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
PERSONAS = [
    {"id": "context_specialist", "focus": "time, scope, and world state"},
    {"id": "evidence_auditor", "focus": "source status and modality"},
    {"id": "pragmatic_reader", "focus": "answerability and observer knowledge"},
]


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


def simulate_personas(args):
    """Create deterministic synthetic ratings for pipeline validation only."""
    if not 0 <= args.disagreement_rate <= 1:
        raise SystemExit("--disagreement-rate must be between 0 and 1.")
    items = load_jsonl(args.input)
    if not items:
        raise SystemExit("Input contains no items.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "synthetic": True,
                "provenance": "simulated_personas", "seed": args.seed,
                "warning": "NOT HUMAN-SUBJECT EVIDENCE",
                "personas": PERSONAS}
    (out / "SIMULATION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    fields = ["blind_id", "item_id", "question", "evidence", *SLOTS]
    for index, persona in enumerate(PERSONAS, 1):
        rng = random.Random(f"{args.seed}:{persona['id']}")
        rows = []
        for item in items:
            category = item["category"]
            labels = {
                "action": item["gold_action"], "answer": item["gold_answer"],
                "temporal_state": "relevant" if category == "temporal" else "stable",
                "modality": "proposed" if category == "modality" else "confirmed",
                "scope": "limited" if category in {"scope", "hidden_premise"} else "global",
                "source_status": "conflict" if category == "source_conflict" else "reliable",
                "observer_state": "partial" if category == "observer" else "shared",
                "world": "counterfactual" if category == "counterfactual" else "actual",
                "notes": f"SIMULATED persona={persona['id']}; not a human rating",
            }
            # Each persona has a small, seeded interpretation difference.  This
            # prevents the validation set from manufacturing perfect agreement.
            if rng.random() < args.disagreement_rate:
                slot = rng.choice(RATING_SLOTS[2:])
                labels[slot] = f"alternate_{slot}"
            rows.append({
                "blind_id": hashlib.sha256(
                    f"{args.seed}:{persona['id']}:{item['id']}".encode()).hexdigest()[:16],
                "item_id": item["id"], "question": item["question"],
                "evidence": json.dumps(item.get("claims", item.get("evidence", []))),
                **labels,
            })
        rng.shuffle(rows)
        with (out / f"annotator_{index}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)
    print(f"Created {len(PERSONAS)} simulated-persona packets in {out}")


def score(args):
    packets, _ = load_completed_annotations(args.annotations)
    manifest_path = Path(args.annotations) / "SIMULATION_MANIFEST.json"
    simulation = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
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
    output = {"schema_version": 1,
              "provenance": "simulated_personas" if simulation else "human_annotations",
              "synthetic": bool(simulation), "n_annotators": len(packets),
              "n_items": len(next(iter(by_slot.values()))), "slots": report}
    if simulation:
        output["warning"] = "NOT HUMAN-SUBJECT EVIDENCE"
        output["personas"] = simulation["personas"]
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
    q = sub.add_parser("simulate-personas")
    q.add_argument("--input", required=True); q.add_argument("--out", required=True)
    q.add_argument("--seed", type=int, default=20260828)
    q.add_argument("--disagreement-rate", type=float, default=0.12)
    q.set_defaults(fn=simulate_personas)
    q = sub.add_parser("adjudicate")
    q.add_argument("--annotations", required=True)
    q.add_argument("--out", default="annotation_adjudication.csv")
    q.set_defaults(fn=adjudicate)
    args = p.parse_args(); args.fn(args)


if __name__ == "__main__":
    main()
