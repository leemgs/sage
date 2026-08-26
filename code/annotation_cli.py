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
RATING_SLOTS = SLOTS[:-1]


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


def load_completed_annotations(directory):
    """Load aligned packets and fail closed on invalid comparisons."""
    files = sorted(Path(directory).glob("annotator_*.csv"))
    if len(files) < 3:
        raise SystemExit("Need at least three completed annotator files.")
    packets, expected_ids, questions = [], None, {}
    for path in files:
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        ids = [row.get("item_id", "") for row in rows]
        if len(ids) != len(set(ids)):
            raise SystemExit(f"Duplicate item_id in {path}")
        if expected_ids is None:
            expected_ids = set(ids)
        elif set(ids) != expected_ids:
            raise SystemExit(f"Mismatched item set in {path}")
        for row in rows:
            item_id, question = row["item_id"], row.get("question", "")
            if item_id in questions and questions[item_id] != question:
                raise SystemExit(f"Question changed for {item_id} in {path}")
            questions[item_id] = question
            for slot in RATING_SLOTS:
                if not row.get(slot, "").strip():
                    raise SystemExit(f"Missing {slot} in {path}: {item_id}")
        packets.append((path, rows))
    if not expected_ids:
        raise SystemExit("Annotation packets contain no items.")
    return packets, questions


def score(args):
    packets, _ = load_completed_annotations(args.annotations)
    by_slot = {s: defaultdict(list) for s in RATING_SLOTS}
    for _, rows in packets:
        for row in rows:
            for slot in by_slot:
                value = row[slot].strip()
                by_slot[slot][row["item_id"]].append(value.casefold())
    report = {}
    for slot, items in by_slot.items():
        if any(len(v) != len(packets) for v in items.values()):
            raise SystemExit(f"Incomplete independent ratings for {slot}")
        report[slot] = {"fleiss_kappa": fleiss_kappa(items),
                        "unanimous_rate": sum(len(set(v)) == 1 for v in items.values())/len(items)}
    output = {"schema_version": 1, "provenance": "human_annotations",
              "synthetic": False, "n_annotators": len(packets),
              "n_items": len(next(iter(by_slot.values()))), "slots": report}
    Path(args.out).write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


def adjudicate(args):
    packets, questions = load_completed_annotations(args.annotations)
    ratings = defaultdict(lambda: defaultdict(list))
    for _, rows in packets:
        for row in rows:
            for slot in RATING_SLOTS:
                value = row[slot].strip()
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
