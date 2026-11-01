#!/usr/bin/env python3
"""Draw the stratified 70-item subset used for human inter-annotator agreement.

Samples 10 items per category from SituationCatch-Bench with a fixed seed so
the blinded packets in paper/annotation_packets/ can be regenerated exactly:

  python code/prepare_annotation_subset.py
  python code/annotation_cli.py init \
    --input paper/data/annotation_subset_70.jsonl --out paper/annotation_packets
"""
from __future__ import annotations
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--out", default="paper/data/annotation_subset_70.jsonl")
    p.add_argument("--per-category", type=int, default=10)
    p.add_argument("--seed", type=int, default=20260818)
    args = p.parse_args()
    by_category = defaultdict(list)
    for line in Path(args.data).read_text().splitlines():
        if line.strip():
            item = json.loads(line)
            by_category[item["category"]].append(item)
    rng = random.Random(args.seed)
    chosen = [x for cat in sorted(by_category)
              for x in rng.sample(by_category[cat], args.per_category)]
    Path(args.out).write_text("".join(json.dumps(x) + "\n" for x in chosen))
    print(f"Wrote {len(chosen)} items ({args.per_category} per category, "
          f"seed {args.seed}) to {args.out}")


if __name__ == "__main__":
    main()
