#!/usr/bin/env python3
"""Fail-closed checks for the journal submission package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
REQUIRED = ["main.tex", "main.pdf", "supplementary.tex", "supplementary.pdf",
            "data/DATASHEET.md", "data/situationcatch_bench.jsonl",
            "results/state_conditions_summary.csv", "results/e5_integrity_audit.json"]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit():
    errors = []
    for relative in REQUIRED:
        path = PAPER / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty required file: paper/{relative}")
    for relative in ("main.pdf", "supplementary.pdf"):
        path = PAPER / relative
        if path.is_file() and not path.read_bytes().startswith(b"%PDF-"):
            errors.append(f"invalid PDF header: paper/{relative}")
    agreement_path = PAPER / "results/simulated_iaa/agreement.json"
    if agreement_path.exists():
        agreement = json.loads(agreement_path.read_text(encoding="utf-8"))
        if agreement.get("synthetic") is not True:
            errors.append("simulated IAA artifact is not marked synthetic")
        if agreement.get("provenance") != "simulated_personas":
            errors.append("simulated IAA artifact has incorrect provenance")
    prospective_path = PAPER / "results/prospective_expected_results.json"
    if prospective_path.exists():
        prospective = json.loads(prospective_path.read_text(encoding="utf-8"))
        if prospective.get("synthetic") is not True:
            errors.append("prospective expected results are not marked synthetic")
        if prospective.get("empirical_evidence") is not False:
            errors.append("prospective expected results are not excluded from evidence")
    checksums = PAPER / "SHA256SUMS.txt"
    lines = [line for line in checksums.read_text().splitlines() if line.strip()]
    for line_number, line in enumerate(lines, 1):
        try:
            expected, relative = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"malformed checksum line {line_number}")
            continue
        path = (PAPER / relative).resolve()
        if not path.is_file():
            errors.append(f"checksum target missing: {relative}")
        elif sha256(path) != expected:
            errors.append(f"checksum mismatch: {relative}")
    return {"schema_version": 1, "status": "PASS" if not errors else "FAIL",
            "required_files": len(REQUIRED), "checksum_entries": len(lines),
            "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    report = audit()
    rendered = json.dumps(report, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
