#!/usr/bin/env python3
"""Excel workbooks for the human annotators, and conversion back to CSV packets.

make     paper/annotation_packets/annotator_N.csv -> annotator_N.xlsx: evidence shown as
         readable lines, the nine rating columns with drop-down lists of codebook values,
         the five fixed columns locked, plus a codebook sheet and the worked examples.
to-csv   a returned annotator_N.xlsx -> annotator_N.csv for code/annotation_cli.py score.
         Fixed columns are restored from the original packet, so only the ratings are
         taken from the workbook; the item set must match exactly.

Usage:
  python code/annotation_workbooks.py make --packets paper/annotation_packets --out DIR
  python code/annotation_workbooks.py to-csv --packets paper/annotation_packets \
      --xlsx returned/annotator_1.xlsx --out filled/annotator_1.csv
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Protection
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from annotation_cli import ALLOWED, SLOTS  # noqa: E402

FIXED = ["blind_id", "item_id", "question", "query_time", "evidence"]
HELP = {
    "action": "Can it be answered from the evidence?",
    "answer": "Answer if ANSWER; else repeat CLARIFY/ABSTAIN",
    "temporal_state": "Does the answer depend on the query time?",
    "modality": "Settled fact or only proposed?",
    "scope": "Applies to everyone, or only some?",
    "source_status": "Do the sources agree?",
    "observer_state": "Does the person asked about know everything relevant?",
    "world": "Real world or hypothetical scenario?",
    "notes": "Optional",
}


def readable(evidence_json):
    """One line per claim: (t3) text [status, source, scope]."""
    lines = []
    for c in json.loads(evidence_json):
        meta = ", ".join(f"{k}={c[k]}" for k in ("status", "source", "scope") if c.get(k))
        extra = f"; observed by {', '.join(c['observed_by'])}" if c.get("observed_by") else ""
        lines.append(f"(t{c.get('time', '?')}) {c.get('text', '')} [{meta}{extra}]")
    return "\n".join(lines)


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def make(args):
    packets, out = Path(args.packets), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    examples = read_csv(packets / "EXAMPLE_annotator_filled.csv")
    for path in sorted(packets.glob("annotator_[0-9]*.csv")):
        rows = read_csv(path)
        wb = Workbook()
        ws = wb.active
        ws.title = "Items"
        header = FIXED + SLOTS
        ws.append(header)
        ws.append(["(do not edit)"] * len(FIXED) + [HELP[s] for s in SLOTS])
        for r in rows:
            ws.append([r["blind_id"], r["item_id"], r["question"], int(r["query_time"]),
                       readable(r["evidence"])] + [r.get(s, "") for s in SLOTS])
        n = len(rows) + 2
        bold, grey = Font(bold=True), PatternFill("solid", fgColor="EEEEEE")
        fill = PatternFill("solid", fgColor="FFF8DC")
        for cell in ws[1]:
            cell.font = bold
        for cell in ws[2]:
            cell.font = Font(italic=True, size=9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        widths = {"A": 18, "B": 20, "C": 45, "D": 11, "E": 70}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        for i, slot in enumerate(SLOTS):
            ws.column_dimensions[chr(ord("F") + i)].width = 16 if slot != "notes" else 30
        for row in ws.iter_rows(min_row=3, max_row=n):
            for cell in row[:len(FIXED)]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.fill = grey
                cell.protection = Protection(locked=True)
            for cell in row[len(FIXED):]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.fill = fill
                cell.protection = Protection(locked=False)
        for i, slot in enumerate(SLOTS):
            col = chr(ord("F") + i)
            if slot in ALLOWED:
                dv = DataValidation(type="list", formula1='"' + ",".join(ALLOWED[slot]) + '"',
                                    allow_blank=True, showErrorMessage=True,
                                    errorTitle="Not a codebook value",
                                    error="Choose one of: " + ", ".join(ALLOWED[slot]))
                ws.add_data_validation(dv)
                dv.add(f"{col}3:{col}{n}")
        ws.freeze_panes = "F3"
        ws.protection.sheet = True  # no password: prevents accidental edits only
        ws.protection.formatColumns = False
        ws.protection.formatRows = False

        cb = wb.create_sheet("Codebook")
        cb.append(["column", "question to ask", "allowed values"])
        for slot in SLOTS:
            cb.append([slot, HELP[slot], ", ".join(ALLOWED.get(slot, ("free text",)))])
        cb.append([])
        cb.append(["query_time", "When the question is asked, on the same scale as the evidence times "
                   "(t3, t8, ...). 'Now' and 'current' refer to it.", ""])
        for col, w in {"A": 16, "B": 70, "C": 40}.items():
            cb.column_dimensions[col].width = w
        for cell in cb[1]:
            cell.font = bold

        ex = wb.create_sheet("Examples (not rated)")
        ex.append(["question", "query_time", "evidence"] + SLOTS)
        for r in examples:
            ex.append([r["question"], int(r["query_time"]), readable(r["evidence"])]
                      + [r[s] for s in SLOTS])
        for col, w in {"A": 45, "B": 11, "C": 70}.items():
            ex.column_dimensions[col].width = w
        for row in ex.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for cell in ex[1]:
            cell.font = bold
        target = out / (path.stem + ".xlsx")
        wb.save(target)
        print(f"Wrote {target} ({len(rows)} items)")


def to_csv(args):
    xlsx = Path(args.xlsx)
    m = re.match(r"annotator_(\d+)", xlsx.stem)
    if not m:
        raise SystemExit(f"Cannot tell which packet {xlsx.name} belongs to (expected annotator_N.xlsx)")
    original = read_csv(Path(args.packets) / f"annotator_{m.group(1)}.csv")
    ws = load_workbook(xlsx, data_only=True)["Items"]
    header = [c.value for c in ws[1]]
    missing = [h for h in ["item_id"] + SLOTS if h not in header]
    if missing:
        raise SystemExit(f"Workbook lacks columns: {missing}")
    rated = {}
    for row in ws.iter_rows(min_row=3, values_only=True):
        rec = dict(zip(header, row))
        if rec.get("item_id"):
            if rec["item_id"] in rated:
                raise SystemExit(f"Duplicate item_id in {xlsx}: {rec['item_id']}")
            rated[rec["item_id"]] = rec
    if set(rated) != {r["item_id"] for r in original}:
        raise SystemExit(f"Item set in {xlsx} differs from the original packet")
    fields = list(original[0].keys())
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in original:
            src = rated[r["item_id"]]
            w.writerow({**r, **{s: "" if src.get(s) is None else str(src[s]).strip() for s in SLOTS}})
    print(f"Wrote {args.out}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("make")
    a.add_argument("--packets", default="paper/annotation_packets")
    a.add_argument("--out", default="paper/annotation_packets/xlsx")
    b = sub.add_parser("to-csv")
    b.add_argument("--packets", default="paper/annotation_packets")
    b.add_argument("--xlsx", required=True)
    b.add_argument("--out", required=True)
    args = p.parse_args()
    {"make": make, "to-csv": to_csv}[args.cmd](args)


if __name__ == "__main__":
    main()
