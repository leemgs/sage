#!/usr/bin/env python3
"""Aggregate only successful raw multi-model records."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("inputs", nargs="+")
p.add_argument("--out", default="paper/results/multimodel_summary.csv")
a = p.parse_args()
groups = defaultdict(list)
errors = defaultdict(int)
for name in a.inputs:
    for line in Path(name).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = (r["provider"], r["model"], r["condition"])
        if r["correct"] is None:
            errors[key] += 1
        else:
            groups[key].append(r["correct"])
rows = [{"provider": k[0], "model": k[1], "condition": k[2],
         "n_success": len(v), "n_error": errors[k], "accuracy": sum(v)/len(v)}
        for k, v in sorted(groups.items())]
if not rows:
    raise SystemExit("No successful model responses to summarize.")
out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
print(json.dumps(rows, indent=2))
