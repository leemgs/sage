#!/usr/bin/env python3
"""Re-score archived responses in place with the current scoring functions.

No API calls: for every record that has a stored raw_response and no error,
re-derive normalized_answer via extract_answer() and correct via matches(),
then rewrite the file. Use after a scoring/extraction fix so the archived data
reflect the corrected, deterministic scoring without re-querying any model.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_multimodel_eval import extract_answer, matches  # noqa: E402


def rescore_file(path: Path) -> tuple[int, int]:
    changed = 0
    records = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("error") is None and r.get("raw_response") is not None:
            ans = extract_answer(r["raw_response"], r["condition"])
            gold = r.get("gold") or []
            correct = int(any(matches(g, ans) for g in gold))
            if r.get("normalized_answer") != ans or r.get("correct") != correct:
                changed += 1
            r["normalized_answer"] = ans
            r["correct"] = correct
        records.append(r)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")
    return changed, len(records)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: rescore.py <raw.jsonl> [...]", file=sys.stderr)
        return 2
    total_changed = 0
    for arg in sys.argv[1:]:
        changed, n = rescore_file(Path(arg))
        total_changed += changed
        print(f"{arg}: rescored {n} records, {changed} changed")
    print(f"total changed: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
