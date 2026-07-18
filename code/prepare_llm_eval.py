#!/usr/bin/env python3
"""Render a stratified SituationCatch-Bench sample for LLM evaluation (E5).

Each benchmark item is rendered into an evidence-complete natural prompt: the
claim sentences plus their structured metadata (time, validity, status, source,
scope, observers) as bracketed annotations, so every decisive situation
variable is present in the text. Failures then measure evidence applicability,
not information availability. The rendered file feeds run_multimodel_eval.py
unchanged; all prompt conditions see the identical evidence block.

Usage: PYTHONPATH=code python code/prepare_llm_eval.py \
           --per-category 30 --out paper/data/situationcatch_llm_sample.jsonl
"""
from __future__ import annotations
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def render_claim(claim):
    parts = [f"time {claim['time']}"]
    if claim.get("valid_from") is not None:
        validity = f"valid from {claim['valid_from']}"
        if claim.get("valid_to") is not None:
            validity += f" to {claim['valid_to']}"
        parts.append(validity)
    parts.append(f"status {claim['status']}")
    parts.append(f"source {claim['source']}")
    parts.append(f"scope {claim['scope']}")
    if claim.get("observed_by"):
        parts.append("observed by " + " and ".join(claim["observed_by"]))
    return f"- ({', '.join(parts)}) {claim['text']}"


def render_item(item):
    lines = [f"Query time: {item['query_time']}.",
             "Evidence claims:"]
    lines += [render_claim(c) for c in item["claims"]]
    lines.append(f"Question: {item['question']}")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--out", default="paper/data/situationcatch_llm_sample.jsonl")
    p.add_argument("--per-category", type=int, default=30)
    p.add_argument("--seed", type=int, default=20260718)
    args = p.parse_args()

    by_category = defaultdict(list)
    for line in Path(args.data).read_text().splitlines():
        if line.strip():
            item = json.loads(line)
            by_category[item["category"]].append(item)

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for category in sorted(by_category):
            for item in rng.sample(by_category[category], args.per_category):
                rendered = render_item(item)
                answers = ([item["gold_answer"]]
                           if item["gold_action"] == "ANSWER"
                           else [item["gold_action"]])
                f.write(json.dumps({
                    "id": item["id"], "category": category,
                    "gold_action": item["gold_action"],
                    "question": rendered, "edited_question": rendered,
                    "answers": answers,
                }, ensure_ascii=False) + "\n")
                n += 1
    print(f"Wrote {n} items ({args.per_category} per category, "
          f"seed {args.seed}) to {out}")


if __name__ == "__main__":
    main()
