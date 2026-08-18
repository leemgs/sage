#!/usr/bin/env python3
"""Render a retrieval-augmented (RAG) baseline sample for E5.

For each benchmark item this retrieves the top-k claims by lexical overlap with
the question and renders only their plain text (no structured time/status/scope
metadata, no situation instruction). Answering this with the plain `direct`
prompt is a realistic retrieval-augmented baseline: it selects the most
*relevant* evidence, exactly the thing the paper argues is not the same as the
*applicable* evidence. Item ids are matched to an existing rendered sample so
the RAG and situation conditions are compared on the same items.

Usage:
  python code/prepare_rag_eval.py --k 3 \
    --ids-from paper/data/situationcatch_llm_sample.jsonl \
    --out paper/data/situationcatch_rag_sample.jsonl
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(question, claims, k):
    q = tokens(question)
    scored = sorted(claims, key=lambda c: (len(q & tokens(c["text"])), c["time"]),
                    reverse=True)
    top = scored[:k]
    # present retrieved evidence in original temporal order for readability
    return sorted(top, key=lambda c: c["time"])


def render(item, k):
    top = retrieve(item["question"], item["claims"], k)
    lines = [f"Query time: {item['query_time']}.", "Retrieved evidence:"]
    lines += [f"- {c['text']}" for c in top]
    lines.append(f"Question: {item['question']}")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--ids-from", default="paper/data/situationcatch_llm_sample.jsonl")
    p.add_argument("--out", default="paper/data/situationcatch_rag_sample.jsonl")
    p.add_argument("--k", type=int, default=3)
    args = p.parse_args()

    wanted = {json.loads(l)["id"] for l in Path(args.ids_from).read_text().splitlines()
              if l.strip()}
    n = 0
    with Path(args.out).open("w", encoding="utf-8") as f:
        for line in Path(args.data).read_text().splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item["id"] not in wanted:
                continue
            rendered = render(item, args.k)
            answers = ([item["gold_answer"]] if item["gold_action"] == "ANSWER"
                       else [item["gold_action"]])
            f.write(json.dumps({
                "id": item["id"], "category": item["category"],
                "gold_action": item["gold_action"],
                "question": rendered, "edited_question": rendered,
                "answers": answers, "k": args.k,
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"Wrote {n} RAG-rendered items (k={args.k}) to {args.out}")


if __name__ == "__main__":
    raise SystemExit(main())
