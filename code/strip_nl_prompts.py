#!/usr/bin/env python3
"""Copy E8b raw records without SituatedQA question text (licence unstated).

Drops user_prompt; keeps id, model, condition, raw response, answer, gold,
correctness, usage and timing so every number stays auditable.
Usage: python code/strip_nl_prompts.py paper/results/raw_e8/nl_local/*.jsonl \
          --out-dir paper/results/raw_e8/nl
"""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("raw", nargs="+")
p.add_argument("--out-dir", required=True)
a = p.parse_args()
out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
for path in map(Path, a.raw):
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    for r in rows:
        r.pop("user_prompt", None)
        r["user_prompt_omitted"] = "SituatedQA text not redistributed"
    (out / path.name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"{path.name}: {len(rows)} records")
