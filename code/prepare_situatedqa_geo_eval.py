#!/usr/bin/env python3
"""Build the pre-registered E9 SituatedQA geographic sample (natural text).

Source: Geographic SituatedQA test split (Zhang & Choi, EMNLP 2021), file
data/qa_data/geo.test.jsonl of https://github.com/mikejqzhang/SituatedQA at
commit 1ef854512fe0f692ca55f92ff2feedf3d7612eda. The repository states no
licence, so question texts are NOT redistributed: the runnable sample goes to
a git-ignored file and a text-free id list is committed for audit.

Sampling (fixed in paper/PREREGISTRATION_E9.md): exact (id, location)
duplicates are dropped (case-insensitive location), then 300 items are drawn
uniformly with seed 20261114.

Usage:
  python code/prepare_situatedqa_geo_eval.py \
    --source /path/to/SituatedQA/data/qa_data/geo.test.jsonl \
    --expect-sha256 097d74586533991f5c1816a9dec4b785dbcfe4512fe2cbbe46b914104103b3b7
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import re
from pathlib import Path


def item_id(row):
    loc = re.sub(r"[^0-9a-z]+", "-", row["location"].casefold()).strip("-")
    return f"sqageo-{row['id']}-{loc}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--out", default="paper/data/local/situatedqa_geo_e9.jsonl")
    p.add_argument("--ids-out", default="paper/data/situatedqa_geo_e9_ids.jsonl")
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--seed", type=int, default=20261114)
    p.add_argument("--expect-sha256")
    a = p.parse_args()
    raw = Path(a.source).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if a.expect_sha256 and digest != a.expect_sha256:
        raise SystemExit(f"source sha256 {digest} != expected {a.expect_sha256}")
    rows = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
    seen, unique = set(), []
    for r in rows:
        k = item_id(r)
        if k not in seen:
            seen.add(k); unique.append(r)
    pool = sorted(unique, key=item_id)
    chosen = random.Random(a.seed).sample(pool, a.n)
    out, ids = Path(a.out), Path(a.ids_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f, ids.open("w") as g:
        for r in chosen:
            iid = item_id(r)
            f.write(json.dumps({"id": iid, "cluster": str(r["id"]), "location": r["location"],
                                "question": r["question"], "edited_question": r["edited_question"],
                                "answers": r["answer"]}, ensure_ascii=False) + "\n")
            g.write(json.dumps({"id": iid, "cluster": str(r["id"]),
                                "location": r["location"]}) + "\n")
    print(f"source sha256 {digest}; {len(rows)} rows, {len(unique)} unique; "
          f"wrote {len(chosen)} items to {out} and ids to {ids}")


if __name__ == "__main__":
    main()
