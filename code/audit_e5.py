#!/usr/bin/env python3
"""Audit an E5 run before any result can enter the manuscript.

The audit joins raw responses to the frozen evaluation set, resolves repeated
attempts deterministically (latest successful record wins), checks balanced
item/category coverage, and reports accuracy, latency and token use.  It exits
non-zero unless every requested model/condition has exactly one successful
response for every frozen item.  This makes ``\\E5readytrue`` a data-dependent
gate rather than a manual judgement.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()
            if line.strip()]


def token_total(usage: dict) -> int:
    """Normalize token totals emitted by Gemini/OpenAI-style providers."""
    for key in ("totalTokenCount", "total_tokens"):
        if usage.get(key) is not None:
            return int(usage[key])
    return sum(int(usage.get(k, 0) or 0) for k in
               ("prompt_tokens", "completion_tokens", "input_tokens",
                "output_tokens"))


def choose_records(records: list[dict]) -> tuple[dict[tuple[str, str], dict], int]:
    """Choose one record per item/condition, preferring the latest success."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        grouped[(record["id"], record["condition"])].append(record)
    chosen = {}
    duplicates = 0
    for key, attempts in grouped.items():
        duplicates += max(0, len(attempts) - 1)
        successes = [r for r in attempts if r.get("correct") is not None]
        pool = successes or attempts
        chosen[key] = max(pool, key=lambda r: (r.get("completed_at") or ""))
    return chosen, duplicates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", nargs="+", type=Path)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--conditions", nargs="+", required=True)
    parser.add_argument("--json-out", type=Path,
                        default=Path("paper/results/e5_integrity_audit.json"))
    parser.add_argument("--csv-out", type=Path,
                        default=Path("paper/results/e5_audited_summary.csv"))
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="Write a diagnostic report but return success.")
    args = parser.parse_args()

    items = read_jsonl(args.data)
    item_category = {item["id"]: item["category"] for item in items}
    expected_ids = set(item_category)
    expected_categories = Counter(item_category.values())
    reports, rows = [], []

    for raw_path in args.raw:
        records = read_jsonl(raw_path)
        if not records:
            reports.append({"file": str(raw_path), "complete": False,
                            "reason": "empty raw file"})
            continue
        model = records[0].get("model", raw_path.stem)
        provider = records[0].get("provider", "unknown")
        chosen, duplicates = choose_records(records)
        condition_reports = []
        file_complete = True
        for condition in args.conditions:
            selected = {item_id: record for (item_id, cond), record in chosen.items()
                        if cond == condition and item_id in expected_ids}
            successful = {i: r for i, r in selected.items()
                          if r.get("correct") is not None}
            missing = sorted(expected_ids - successful.keys())
            unexpected = sorted({i for (i, c) in chosen
                                 if c == condition and i not in expected_ids})
            coverage = Counter(item_category[i] for i in successful)
            balanced = coverage == expected_categories
            complete = not missing and not unexpected and balanced
            file_complete &= complete
            accuracy = (sum(int(r["correct"]) for r in successful.values()) /
                        len(successful)) if successful else None
            latencies = [float(r.get("latency_ms", 0)) for r in successful.values()]
            tokens = sum(token_total(r.get("usage") or {})
                         for r in successful.values())
            condition_reports.append({
                "condition": condition, "n_success": len(successful),
                "n_expected": len(expected_ids), "accuracy": accuracy,
                "missing_ids": missing, "unexpected_ids": unexpected,
                "category_coverage": dict(sorted(coverage.items())),
                "balanced": balanced, "median_latency_ms":
                statistics.median(latencies) if latencies else None,
                "total_tokens": tokens, "complete": complete,
            })
            rows.append({"provider": provider, "model": model,
                         "condition": condition, "n_success": len(successful),
                         "n_expected": len(expected_ids), "accuracy": accuracy,
                         "median_latency_ms": statistics.median(latencies)
                         if latencies else None, "total_tokens": tokens,
                         "complete": int(complete)})
        reports.append({"file": str(raw_path), "provider": provider,
                        "model": model, "raw_records": len(records),
                        "duplicate_attempts": duplicates,
                        "conditions": condition_reports,
                        "complete": file_complete})

    complete = bool(reports) and all(r.get("complete", False) for r in reports)
    audit = {"data": str(args.data), "n_items": len(items),
             "expected_category_coverage": dict(sorted(expected_categories.items())),
             "conditions": args.conditions, "models": reports,
             "confirmatory_complete": complete}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(audit, indent=2) + "\n")
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else
                                ["provider", "model", "condition"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(audit, indent=2))
    if complete:
        print("E5 INTEGRITY GATE: PASS")
        return 0
    print("E5 INTEGRITY GATE: FAIL (incomplete or unbalanced real responses)")
    return 0 if args.allow_incomplete else 1


if __name__ == "__main__":
    raise SystemExit(main())
