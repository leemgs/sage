#!/usr/bin/env python3
"""Pre-registered E8b analysis: SituatedQA temporal, natural text.

For every model: accuracy per condition (overall and by date_type) and two
paired contrasts with 95% cluster-bootstrap intervals, clustering on the
upstream question id (one question can appear with several dates):
  * NL-H1  situation - structured, all items;
  * NL-H2  date_context - direct (dated minus undated question, same direct
    prompt), on time-dependent items (date_type != orig), and the same
    contrast on static (orig) items reported as the control.
One success per item and condition is required (fails closed otherwise).

Usage: python code/e8_nl_stats.py RAW... --ids paper/data/situatedqa_e8_ids.jsonl \
          --json-out paper/results/e8_nl_stats.json
"""
from __future__ import annotations
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

SEED, BOOT = 20260726, 3000
CONDS = ("direct", "date_context", "structured", "situation")


def read(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def boot_ci(clusters, stat, rng):
    keys = sorted(clusters)
    vals = []
    for _ in range(BOOT):
        sample = [clusters[rng.choice(keys)] for _ in keys]
        v = stat([x for c in sample for x in c])
        if v is not None:
            vals.append(v)
    vals.sort()
    return [vals[int(.025 * len(vals))], vals[int(.975 * len(vals)) - 1]]


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def analyse(records, ids):
    meta = {r["id"]: r for r in ids}
    got = {}
    for r in records:
        if r.get("error") is None and r["id"] in meta:
            got[(r["id"], r["condition"])] = r["correct"]
    missing = [(i, c) for i in meta for c in CONDS if (i, c) not in got]
    if missing:
        raise SystemExit(f"incomplete: {len(missing)} item/condition pairs missing")
    rows = [{"id": i, "cluster": m["cluster"], "dt": m["date_type"],
             **{c: got[(i, c)] for c in CONDS}} for i, m in meta.items()]
    rng = random.Random(SEED)

    def contrast(sub, a, b):
        cl = defaultdict(list)
        for r in sub:
            cl[r["cluster"]].append(r[a] - r[b])
        est = mean([r[a] - r[b] for r in sub])
        return {"n": len(sub), "estimate_pp": 100 * est,
                "ci_pp": [100 * x for x in boot_ci(cl, mean, rng)]}

    acc = {c: 100 * mean([r[c] for r in rows]) for c in CONDS}
    by_dt = {d: {c: 100 * mean([r[c] for r in rows if r["dt"] == d]) for c in CONDS}
             for d in sorted({r["dt"] for r in rows})}
    timed = [r for r in rows if r["dt"] != "orig"]
    static = [r for r in rows if r["dt"] == "orig"]
    return {"n": len(rows), "clusters": len({r["cluster"] for r in rows}),
            "accuracy_pct": acc, "accuracy_by_date_type_pct": by_dt,
            "nl_h1_situation_minus_structured": contrast(rows, "situation", "structured"),
            "nl_h2_dated_minus_undated_time_dependent": contrast(timed, "date_context", "direct"),
            "nl_h2_dated_minus_undated_static_control": contrast(static, "date_context", "direct")}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--ids", default="paper/data/situatedqa_e8_ids.jsonl")
    p.add_argument("--json-out", default="paper/results/e8_nl_stats.json")
    a = p.parse_args()
    ids = read(a.ids)
    by_model = defaultdict(list)
    for path in a.raw:
        for r in read(path):
            by_model[r["model"]].append(r)
    out = {"seed": SEED, "bootstrap": BOOT, "cluster": "upstream question id",
           "models": {m: analyse(rs, ids) for m, rs in sorted(by_model.items())}}
    Path(a.json_out).write_text(json.dumps(out, indent=2) + "\n")
    for m, s in out["models"].items():
        h1, h2 = s["nl_h1_situation_minus_structured"], s["nl_h2_dated_minus_undated_time_dependent"]
        print(f"{m}: H1 {h1['estimate_pp']:+.1f} {h1['ci_pp']}; H2 {h2['estimate_pp']:+.1f} {h2['ci_pp']}")


if __name__ == "__main__":
    main()
