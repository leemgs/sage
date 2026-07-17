#!/usr/bin/env python3
"""Blinded independent annotation packets, agreement, and adjudication."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

SLOTS = ["action", "answer", "temporal_state", "modality", "scope",
         "source_status", "observer_state", "world", "notes"]


def load_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def init(args):
    items = load_jsonl(args.input)
    if args.annotators < 3:
        raise SystemExit("At least three independent annotators are required.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for n in range(1, args.annotators + 1):
        shuffled = items[:]
        rng.shuffle(shuffled)
        rows = []
        for item in shuffled:
            token = hashlib.sha256(f"{args.seed}:{n}:{item['id']}".encode()).hexdigest()[:16]
            row = {"blind_id": token, "item_id": item["id"],
                   "question": item["question"],
                   "evidence": json.dumps(item.get("claims", item.get("evidence", [])))}
            row.update({s: "" for s in SLOTS})
            rows.append(row)
        with (out / f"annotator_{n}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0])
            w.writeheader(); w.writerows(rows)
    print(f"Created {args.annotators} blinded packets in {out}")


def fleiss_kappa(labels_by_item):
    items = list(labels_by_item.values())
    n = len(items[0])
    cats = sorted({x for labels in items for x in labels})
    p = {c: sum(labels.count(c) for labels in items)/(len(items)*n) for c in cats}
    pbar = sum((sum(v*v for v in Counter(labels).values())-n)/(n*(n-1))
               for labels in items)/len(items)
    pe = sum(v*v for v in p.values())
    return (pbar-pe)/(1-pe) if pe < 1 else 1.0


def score(args):
    files = sorted(Path(args.annotations).glob("annotator_*.csv"))
    if len(files) < 3:
        raise SystemExit("Need at least three completed annotator files.")
    by_slot = {s: defaultdict(list) for s in SLOTS[:-1]}
    for path in files:
        for row in csv.DictReader(path.open(encoding="utf-8")):
            for slot in by_slot:
                value = row[slot].strip()
                if not value:
                    raise SystemExit(f"Missing {slot} in {path}: {row['item_id']}")
                by_slot[slot][row["item_id"]].append(value.casefold())
    report = {}
    for slot, items in by_slot.items():
        if any(len(v) != len(files) for v in items.values()):
            raise SystemExit(f"Incomplete independent ratings for {slot}")
        report[slot] = {"fleiss_kappa": fleiss_kappa(items),
                        "unanimous_rate": sum(len(set(v)) == 1 for v in items.values())/len(items)}
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def adjudicate(args):
    files = sorted(Path(args.annotations).glob("annotator_*.csv"))
    if len(files) < 3:
        raise SystemExit("Need at least three completed annotator files.")
    ratings = defaultdict(lambda: defaultdict(list))
    questions = {}
    for path in files:
        for row in csv.DictReader(path.open(encoding="utf-8")):
            questions[row["item_id"]] = row["question"]
            for slot in SLOTS[:-1]:
                value = row[slot].strip()
                if not value:
                    raise SystemExit(f"Missing {slot} in {path}: {row['item_id']}")
                ratings[row["item_id"]][slot].append(value)
    rows = []
    for item_id, slots in ratings.items():
        for slot, values in slots.items():
            if len(set(v.casefold() for v in values)) > 1:
                rows.append({"item_id": item_id, "question": questions[item_id],
                             "slot": slot,
                             "independent_labels": json.dumps(values),
                             "adjudicated_label": "",
                             "adjudicator_rationale": ""})
    out = Path(args.out)
    with out.open("w", newline="", encoding="utf-8") as f:
        fields = ["item_id", "question", "slot", "independent_labels",
                  "adjudicated_label", "adjudicator_rationale"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} disagreements to {out}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(required=True)
    q = sub.add_parser("init")
    q.add_argument("--input", required=True); q.add_argument("--out", required=True)
    q.add_argument("--annotators", type=int, default=3); q.add_argument("--seed", type=int, default=20260717)
    q.set_defaults(fn=init)
    q = sub.add_parser("score")
    q.add_argument("--annotations", required=True)
    q.add_argument("--out", default="paper/results/annotation_agreement.json")
    q.set_defaults(fn=score)
    q = sub.add_parser("adjudicate")
    q.add_argument("--annotations", required=True)
    q.add_argument("--out", default="annotation_adjudication.csv")
    q.set_defaults(fn=adjudicate)
    args = p.parse_args(); args.fn(args)


if __name__ == "__main__":
    main()
