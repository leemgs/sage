#!/usr/bin/env python3
"""POST-HOC check (not pre-registered; reported as such): output-limit truncation in E8a.

A response that reaches the 1,024-token output limit (completion_tokens >= 1,020)
is cut off; when it is not valid JSON, the pre-registered extractor falls back to
the raw text, so containment scoring can credit a gold string that merely occurs
in the restated evidence, and a real answer can be lost. For every model this
reports, per condition, the number of truncated responses, and the paired
situation - structured contrast on the items where neither response was
truncated (same category-clustered bootstrap as code/e5_stats.py).

Usage: python code/e8_truncation.py paper/results/raw_e8/main/*.jsonl \
          --json-out paper/results/e8_truncation.json
"""
from __future__ import annotations
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

LIMIT, SEED, BOOT = 1020, 20260726, 3000


def truncated(r):
    return (r.get("usage") or {}).get("completion_tokens", 0) >= LIMIT


def analyse(records):
    d = {}
    for r in records:
        if r.get("error") is None:
            d[(r["id"], r["condition"])] = r
    ids = sorted({i for i, _ in d})
    conds = sorted({c for _, c in d})
    out = {"truncated": {c: sum(truncated(d[(i, c)]) for i in ids) for c in conds},
           "n_items": len(ids)}
    keep = [i for i in ids if not truncated(d[(i, "structured")]) and not truncated(d[(i, "situation")])]
    clusters = defaultdict(list)
    for i in keep:
        clusters[i.rsplit("-", 1)[0]].append(d[(i, "situation")]["correct"] - d[(i, "structured")]["correct"])
    rng, keys, vals = random.Random(SEED), sorted(clusters), []
    for _ in range(BOOT):
        s = [x for k in (rng.choice(keys) for _ in keys) for x in clusters[k]]
        vals.append(100 * sum(s) / len(s))
    vals.sort()
    flat = [x for k in keys for x in clusters[k]]
    out["situation_minus_structured_untruncated"] = {
        "n_pairs": len(keep), "estimate_pp": 100 * sum(flat) / len(flat) if flat else None,
        "ci_pp": [vals[int(.025 * BOOT)], vals[int(.975 * BOOT) - 1]] if flat else None}
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--json-out", default="paper/results/e8_truncation.json")
    a = p.parse_args()
    by_model = defaultdict(list)
    for path in a.raw:
        for line in Path(path).read_text().splitlines():
            if line.strip():
                r = json.loads(line); by_model[r["model"]].append(r)
    res = {"post_hoc": True, "limit_completion_tokens": LIMIT, "seed": SEED, "bootstrap": BOOT,
           "models": {m: analyse(rs) for m, rs in sorted(by_model.items())}}
    Path(a.json_out).write_text(json.dumps(res, indent=2) + "\n")
    for m, s in res["models"].items():
        c = s["situation_minus_structured_untruncated"]
        print(m, s["truncated"], c["n_pairs"], c["estimate_pp"], c["ci_pp"])


if __name__ == "__main__":
    main()
