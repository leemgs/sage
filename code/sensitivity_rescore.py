#!/usr/bin/env python3
"""Post-hoc SENSITIVITY rescoring (not pre-registered; reported as such).

The pre-registered extractor (run_multimodel_eval.extract_answer) parses a JSON
condition only when the whole response is JSON, and never maps a boolean
answer to yes/no. Some models write prose before a JSON block, or answer
`"answer": false`, so a correct answer can be scored wrong. This script applies
one more robust extractor to every record of every model and condition alike:
  * if the response is not JSON, the last {...} block in it is parsed;
  * a boolean answer true/false becomes "yes"/"no".
Archived raw files are never modified; rescored copies go to --out-dir.

Usage: python code/sensitivity_rescore.py RAW... --out-dir paper/results/sensitivity/e6
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_multimodel_eval import extract_answer, matches  # noqa: E402


def last_json_object(text):
    """Parse the last balanced {...} block in text, or return None."""
    ends = [i for i, ch in enumerate(text) if ch == "}"]
    for end in reversed(ends):
        depth = 0
        for start in range(end, -1, -1):
            depth += {"}": 1, "{": -1}.get(text[start], 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:end + 1])
                    if isinstance(obj, dict):
                        return obj
                except ValueError:
                    pass
                break
    return None


def robust_extract(raw, condition):
    if condition in ("direct", "date_context", "chain_of_thought"):
        return extract_answer(raw, condition)
    obj = last_json_object(raw or "")
    if obj is None:
        return extract_answer(raw, condition)
    action = str(obj.get("action", "")).strip().upper()
    if action in ("CLARIFY", "ABSTAIN"):
        return action
    ans = obj.get("answer", obj.get("action", ""))
    if isinstance(ans, bool):
        return "yes" if ans else "no"
    return str(ans)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    for path in map(Path, args.raw):
        changed = flipped_up = flipped_down = 0
        lines = []
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r.get("error") is None and r.get("raw_response") is not None:
                ans = robust_extract(r["raw_response"], r["condition"])
                ok = int(any(matches(g, ans) for g in r["gold"]))
                if ok != r.get("correct"):
                    changed += 1
                    flipped_up += ok > (r.get("correct") or 0)
                    flipped_down += ok < (r.get("correct") or 0)
                r = {**r, "normalized_answer": ans, "correct": ok,
                     "sensitivity_rescored": True}
            lines.append(json.dumps(r, ensure_ascii=False))
        (out / path.name).write_text("\n".join(lines) + "\n")
        print(f"{path.name}: {changed} records changed "
              f"({flipped_up} wrong->right, {flipped_down} right->wrong)")


if __name__ == "__main__":
    main()
