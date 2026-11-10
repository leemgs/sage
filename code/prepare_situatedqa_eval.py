#!/usr/bin/env python3
"""Build the pre-registered E8b SituatedQA temporal sample (natural text).

Source: Temporal SituatedQA test split (Zhang & Choi, EMNLP 2021), file
data/qa_data/temp.test.jsonl of https://github.com/mikejqzhang/SituatedQA at
commit 1ef854512fe0f692ca55f92ff2feedf3d7612eda. That repository states no
licence, so the question texts are NOT redistributed here: this script reads a
local clone and writes the runnable sample to a git-ignored file, and a
text-free id list (upstream id, date, date_type) is committed for audit.

Sampling (fixed in paper/PREREGISTRATION_E8.md): 75 items from each of the four
date_type strata (orig, start, sampled_year, sampled_date), seed 20261110.

Usage:
  python code/prepare_situatedqa_eval.py \
    --source /path/to/SituatedQA/data/qa_data/temp.test.jsonl \
    --out paper/data/local/situatedqa_e8.jsonl \
    --ids-out paper/data/situatedqa_e8_ids.jsonl
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import re
from pathlib import Path

STRATA = ("orig", "start", "sampled_year", "sampled_date")


def item_id(row):
    date = re.sub(r"[^0-9A-Za-z]+", "-", row["date"]).strip("-")
    return f"sqa-{row['id']}-{date}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--out", default="paper/data/local/situatedqa_e8.jsonl")
    p.add_argument("--ids-out", default="paper/data/situatedqa_e8_ids.jsonl")
    p.add_argument("--per-stratum", type=int, default=75)
    p.add_argument("--seed", type=int, default=20261110)
    p.add_argument("--expect-sha256")
    a = p.parse_args()
    raw = Path(a.source).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if a.expect_sha256 and digest != a.expect_sha256:
        raise SystemExit(f"source sha256 {digest} != expected {a.expect_sha256}")
    rows = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
    seen, unique = set(), []
    for r in rows:                      # drop exact (id, date) duplicates
        k = item_id(r)
        if k not in seen:
            seen.add(k); unique.append(r)
    rng = random.Random(a.seed)
    chosen = []
    for s in STRATA:
        pool = sorted((r for r in unique if r["date_type"] == s), key=item_id)
        chosen += rng.sample(pool, a.per_stratum)
    out, ids = Path(a.out), Path(a.ids_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f, ids.open("w") as g:
        for r in chosen:
            iid = item_id(r)
            f.write(json.dumps({"id": iid, "cluster": str(r["id"]),
                                "date_type": r["date_type"], "date": r["date"],
                                "question": r["question"],
                                "edited_question": r["edited_question"],
                                "answers": r["answer"]}, ensure_ascii=False) + "\n")
            g.write(json.dumps({"id": iid, "cluster": str(r["id"]),
                                "date_type": r["date_type"], "date": r["date"]}) + "\n")
    print(f"source sha256 {digest}; {len(rows)} rows, {len(unique)} unique; "
          f"wrote {len(chosen)} items to {out} and ids to {ids}")


if __name__ == "__main__":
    main()
