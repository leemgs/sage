#!/usr/bin/env python3
"""Pre-registered E9 analysis: SituatedQA geographic split, natural text.

For every model: accuracy per condition and two paired contrasts with 95%
bootstrap intervals clustered on the upstream question id (each question
appears with several locations):
  * GEO-H1  situation - structured (located question);
  * GEO-H2  location_context - direct (located minus unlocated question,
    same direct prompt).
Descriptive only (not a test): GEO-H2 split into items located in the United
States (location string in US_NAMES) and elsewhere. One success per item and
condition is required (fails closed otherwise).

Usage: python code/e9_geo_stats.py RAW... --ids paper/data/situatedqa_geo_e9_ids.jsonl \
          --json-out paper/results/e9_geo_stats.json
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e8_nl_stats import BOOT, SEED, boot_ci, mean, read  # noqa: E402

CONDS = ("direct", "location_context", "structured", "situation")
US_NAMES = {"united states", "us", "usa", "the united states", "america",
            "united states of america", "the us", "u.s.", "the usa"}


def analyse(records, ids):
    meta = {r["id"]: r for r in ids}
    got = {}
    for r in records:
        if r.get("error") is None and r["id"] in meta:
            got[(r["id"], r["condition"])] = r["correct"]
    missing = [(i, c) for i in meta for c in CONDS if (i, c) not in got]
    if missing:
        raise SystemExit(f"incomplete: {len(missing)} item/condition pairs missing")
    rows = [{"cluster": m["cluster"], "us": m["location"].strip().casefold() in US_NAMES,
             **{c: got[(i, c)] for c in CONDS}} for i, m in meta.items()]
    rng = random.Random(SEED)

    def contrast(sub, a, b):
        cl = defaultdict(list)
        for r in sub:
            cl[r["cluster"]].append(r[a] - r[b])
        return {"n": len(sub), "estimate_pp": 100 * mean([r[a] - r[b] for r in sub]),
                "ci_pp": [100 * x for x in boot_ci(cl, mean, rng)]}

    return {"n": len(rows), "clusters": len({r["cluster"] for r in rows}),
            "accuracy_pct": {c: 100 * mean([r[c] for r in rows]) for c in CONDS},
            "geo_h1_situation_minus_structured": contrast(rows, "situation", "structured"),
            "geo_h2_located_minus_unlocated": contrast(rows, "location_context", "direct"),
            "descriptive_h2_us_located": contrast([r for r in rows if r["us"]], "location_context", "direct"),
            "descriptive_h2_elsewhere": contrast([r for r in rows if not r["us"]], "location_context", "direct")}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--ids", default="paper/data/situatedqa_geo_e9_ids.jsonl")
    p.add_argument("--json-out", default="paper/results/e9_geo_stats.json")
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
        h1, h2 = s["geo_h1_situation_minus_structured"], s["geo_h2_located_minus_unlocated"]
        print(f"{m}: H1 {h1['estimate_pp']:+.1f} {h1['ci_pp']}; H2 {h2['estimate_pp']:+.1f} {h2['ci_pp']}")


if __name__ == "__main__":
    main()
