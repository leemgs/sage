#!/usr/bin/env python3
"""Fail-closed audit for a balanced, real multi-family evaluation matrix."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def audit_records(records, expected_conditions, min_families=3):
    successful = [r for r in records if r.get("error") is None]
    if any(r.get("provider") == "mock" or r.get("usage", {}).get("mock")
           for r in successful):
        raise ValueError("synthetic/mock records cannot support multi-family evidence")
    models = {(r.get("provider"), r.get("model")) for r in successful}
    providers = {provider for provider, _ in models}
    if len(providers) < min_families:
        raise ValueError(f"need >= {min_families} provider families; found {len(providers)}")
    cells = defaultdict(Counter)
    for record in successful:
        cells[(record.get("provider"), record.get("model"))][
            (record.get("id"), record.get("condition"))] += 1
    reference = None
    for model, counts in sorted(cells.items()):
        duplicates = [cell for cell, count in counts.items() if count != 1]
        if duplicates:
            raise ValueError(f"duplicate cells for {model}: {duplicates[:3]}")
        missing = set(expected_conditions) - {condition for _, condition in counts}
        if missing:
            raise ValueError(f"missing conditions for {model}: {sorted(missing)}")
        matrix = set(counts)
        if reference is None:
            reference = matrix
        elif matrix != reference:
            raise ValueError(f"unbalanced item-condition matrix for {model}")
    return {"schema_version": 1, "synthetic": False,
            "provider_families": sorted(providers), "n_families": len(providers),
            "n_models": len(models), "n_cells_per_model": len(reference or ())}


def audit(paths, expected_conditions, min_families=3):
    records = []
    for path in paths:
        records.extend(json.loads(line) for line in Path(path).read_text().splitlines()
                       if line.strip())
    return audit_records(records, expected_conditions, min_families)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--conditions", nargs="+", required=True)
    parser.add_argument("--min-families", type=int, default=3)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        report = audit(args.inputs, args.conditions, args.min_families)
    except ValueError as exc:
        raise SystemExit(f"AUDIT FAILED: {exc}") from exc
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
