#!/usr/bin/env python3
"""Run gold-, predicted-, and corrupted-state SCQA evaluation."""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from scqa.engine import corrupt_state, decide, is_correct, predict_state

SLOTS = ("actor", "event", "time", "validity", "scope", "modality",
         "source_status", "observer_knowledge", "world")


def slot_value(claim, slot):
    if slot == "validity":
        return (claim.get("valid_from"), claim.get("valid_to"))
    if slot == "modality":
        return claim.get("status")
    if slot == "source_status":
        return (claim.get("source"), claim.get("status"))
    if slot == "observer_knowledge":
        return tuple(sorted(claim.get("observed_by", [])))
    if slot == "world":
        scope = claim.get("scope")
        return scope if scope in ("reality", "counterfactual") else "unspecified"
    if slot == "scope":
        scope = claim.get("scope")
        if scope in ("global", "reality", "counterfactual"):
            return scope
        return "local"
    return claim.get(slot)


def score_slots(gold_item, predicted_item):
    scores = {slot: [] for slot in SLOTS}
    for gold, pred in zip(gold_item["claims"], predicted_item["claims"]):
        for slot in SLOTS:
            scores[slot].append(int(slot_value(gold, slot) ==
                                    slot_value(pred, slot)))
    return scores


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--out", default="paper/results/state_conditions.csv")
    args = p.parse_args()
    items = [json.loads(s) for s in Path(args.data).read_text().splitlines()
             if s.strip()]
    conditions = {
        "gold_state": lambda x: x,
        "predicted_state": predict_state,
        "corrupted_state": corrupt_state,
    }
    rows = []
    slot_rows = []
    for item in items:
        predicted_item = predict_state(item)
        slot_scores = score_slots(item, predicted_item)
        for slot, values in slot_scores.items():
            slot_rows.append({"id": item["id"], "category": item["category"],
                              "slot": slot, "n_claims": len(values),
                              "correct_claims": sum(values),
                              "accuracy": sum(values)/len(values)})
        for condition, transform in conditions.items():
            pred = decide(transform(item))
            rows.append({
                "id": item["id"], "category": item["category"],
                "condition": condition, "gold_action": item["gold_action"],
                "gold_answer": item["gold_answer"], "pred_action": pred["action"],
                "pred_answer": pred["answer"],
                "correct": int(is_correct(item, pred)),
            })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0])
        w.writeheader()
        w.writerows(rows)
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["condition"]].append(r["correct"])
    summary = []
    for condition, vals in grouped.items():
        summary.append({"condition": condition, "n": len(vals),
                        "accuracy": sum(vals)/len(vals)})
    summary_path = out.with_name("state_conditions_summary.csv")
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary[0])
        w.writeheader()
        w.writerows(summary)
    slot_path = out.with_name("predicted_state_slots.csv")
    with slot_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=slot_rows[0])
        w.writeheader(); w.writerows(slot_rows)
    slot_summary = []
    for slot in SLOTS:
        selected = [r for r in slot_rows if r["slot"] == slot]
        numerator = sum(r["correct_claims"] for r in selected)
        denominator = sum(r["n_claims"] for r in selected)
        slot_summary.append({"slot": slot, "n_claims": denominator,
                             "accuracy": numerator/denominator})
    slot_summary_path = out.with_name("predicted_state_slots_summary.csv")
    with slot_summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=slot_summary[0])
        w.writeheader(); w.writerows(slot_summary)
    gold_correct = sum(r["correct"] for r in rows if r["condition"] == "gold_state")
    pred_correct = sum(r["correct"] for r in rows if r["condition"] == "predicted_state")
    decomposition = {
        "n_items": len(items),
        "sensing_attributed_errors": len(items) - pred_correct,
        "update_policy_errors_under_gold_state": len(items) - gold_correct,
        "generation_errors": 0,
        "note": "Attribution is identifiable only in this deterministic controlled pipeline."
    }
    out.with_name("error_decomposition.json").write_text(
        json.dumps(decomposition, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(json.dumps(slot_summary, indent=2))


if __name__ == "__main__":
    main()
