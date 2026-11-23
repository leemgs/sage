#!/usr/bin/env python3
"""Descriptive (not pre-specified): human annotations vs benchmark reference labels.

For every rating slot: each annotator's agreement with the reference label implied by
the item's generated state (annotation_cli.reference_labels), the agreement of the
three-annotator majority (ties count as disagreement), and per-category rates of the
majority. Blank cells declared with --missing are skipped for that slot only.

Usage: python code/human_vs_reference.py --annotations paper/results/human_iaa \
          --missing answer:source_conflict-0262 --out paper/results/human_iaa/vs_reference.json
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import annotation_cli as cli  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", default="paper/results/human_iaa")
    p.add_argument("--bench", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--missing", action="append")
    p.add_argument("--out", default="paper/results/human_iaa/vs_reference.json")
    a = p.parse_args()
    packets, _ = cli.load_completed_annotations(a.annotations, cli.parse_missing(a.missing))
    bench = {r["id"]: r for r in map(json.loads, Path(a.bench).read_text().splitlines())}
    ref = {i: cli.reference_labels(bench[i]) for i in {r["item_id"] for _, rows in packets for r in rows}}
    norm = lambda s, v: cli.normalize_label(s, v) if v else ""
    labels = defaultdict(lambda: defaultdict(list))
    per_annot = {s: [0, 0, 0] for s in cli.RATING_SLOTS}  # not used directly
    annot = {}
    for k, (path, rows) in enumerate(packets, 1):
        hits = {}
        for s in cli.RATING_SLOTS:
            ok = n = 0
            for r in rows:
                v = r[s]
                if not v:
                    continue
                labels[s][r["item_id"]].append(v)
                n += 1
                ok += v == norm(s, ref[r["item_id"]][s])
            hits[s] = round(100 * ok / n, 1)
        annot[f"annotator_{k}"] = hits
    majority, by_cat = {}, defaultdict(dict)
    for s in cli.RATING_SLOTS:
        ok, cats = 0, defaultdict(lambda: [0, 0])
        for item, vals in labels[s].items():
            top, cnt = Counter(vals).most_common(1)[0]
            hit = cnt >= 2 and top == norm(s, ref[item][s])
            ok += hit
            c = bench[item]["category"]
            cats[c][0] += hit; cats[c][1] += 1
        majority[s] = round(100 * ok / len(labels[s]), 1)
        for c, (h, n) in sorted(cats.items()):
            by_cat[s][c] = round(100 * h / n, 1)
    out = {"descriptive": True, "note": "not pre-specified; reference = labels implied by "
           "the generated state (annotation_cli.reference_labels)",
           "per_annotator_pct": annot, "majority_pct": majority, "majority_by_category_pct": by_cat}
    Path(a.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"majority_pct": majority, "per_annotator_pct": annot}, indent=1))


if __name__ == "__main__":
    main()
