#!/usr/bin/env python3
"""Score E7 LLM-sensor outputs against the gold state (pre-registered in
paper/PREREGISTRATION_E6_E7.md) and compare with the rule-based sensor on the
same items, using one scorer for both.

Usage:
  PYTHONPATH=code python code/score_llm_sensor.py \
      paper/results/raw_sensor/sensor_*.jsonl --out paper/results/llm_sensor_summary.json
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scqa.engine import decide, is_correct, predict_state  # noqa: E402
from run_experiments import SLOTS, slot_value  # noqa: E402

# Slots the claim text can reveal, versus slots it cannot (no timestamps in text).
CUE_SLOTS = ("actor", "event", "scope", "modality", "source_status",
             "observer_knowledge", "world")
TEXT_UNRECOVERABLE = ("time", "validity")


def norm(v):
    return v.strip().casefold() if isinstance(v, str) else v


def slot_equal(slot, gold, pred):
    """Pre-registered comparison: strings case-insensitive and trimmed; an actor
    is correct if the gold name occurs as a whole word in the predicted actor."""
    g, p = slot_value(gold, slot), slot_value(pred, slot)
    if slot == "actor":
        g, p = norm(g) or "", norm(p) or ""
        return bool(g) and re.search(rf"\b{re.escape(g)}\b", p) is not None
    if isinstance(g, tuple):
        return tuple(norm(x) for x in g) == tuple(norm(x) for x in p)
    return norm(g) == norm(p)


def to_claim(text, raw):
    """Map one LLM claim object onto the engine's claim schema."""
    c = {"text": text}
    t = raw.get("time")
    c["time"] = int(t) if isinstance(t, (int, float)) else 0
    c["valid_from"] = int(t) if isinstance(t, (int, float)) else None
    if isinstance(raw.get("valid_to"), (int, float)):
        c["valid_to"] = int(raw["valid_to"])
    for k in ("event", "actor", "status", "source", "scope"):
        c[k] = str(raw.get(k) or "").strip()
    c["event"] = c["event"].lower(); c["status"] = c["status"].lower()
    c["source"] = c["source"].lower()
    if c["scope"].lower() in ("global", "reality", "counterfactual"):
        c["scope"] = c["scope"].lower()
    obs = raw.get("observed_by") or []
    if obs:
        c["observed_by"] = [str(x).strip() for x in obs]
    return c


def predicted_item(item, state):
    x = {k: v for k, v in item.items() if k != "claims"}
    if state is None:   # invalid output: no usable claims (pre-registered)
        x["claims"], x["user_region"] = [], None
        return x
    x["claims"] = [to_claim(g["text"], r) for g, r in zip(item["claims"], state["claims"])]
    region = state.get("region")
    x["user_region"] = str(region).strip() if region else None
    return x


def score(items, predicted):
    slots = {s: [0, 0] for s in SLOTS}
    cats = defaultdict(list)
    for item in items:
        pred = predicted[item["id"]]
        cats[item["category"]].append(int(is_correct(item, decide(pred))))
        pc = pred["claims"] or [{} for _ in item["claims"]]
        for gold, p in zip(item["claims"], pc):
            for s in SLOTS:
                slots[s][0] += int(bool(p) and slot_equal(s, gold, p))
                slots[s][1] += 1
    acc = sum(sum(v) for v in cats.values()) / len(items)
    return {"end_to_end_accuracy": acc,
            "by_category": {k: sum(v) / len(v) for k, v in sorted(cats.items())},
            "slot_accuracy": {s: a / n for s, (a, n) in slots.items()},
            "cue_slot_accuracy": sum(slots[s][0] for s in CUE_SLOTS) /
                                 sum(slots[s][1] for s in CUE_SLOTS)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--ids-from", default="paper/data/situationcatch_llm_sample.jsonl")
    p.add_argument("--out", default="paper/results/llm_sensor_summary.json")
    args = p.parse_args()
    ids = [json.loads(l)["id"] for l in Path(args.ids_from).read_text().splitlines() if l.strip()]
    bench = {x["id"]: x for x in map(json.loads, Path(args.data).read_text().splitlines())}
    items = [bench[i] for i in ids]
    report = {"n_items": len(items), "scorer": "pre-registered (case-insensitive; actor by whole-word match)",
              "rule_sensor": score(items, {x["id"]: predict_state(x) for x in items}),
              "models": {}}
    for path in args.raw:
        recs = {}
        for l in Path(path).read_text().splitlines():
            r = json.loads(l)
            if r.get("error") is None:
                recs[r["id"]] = r          # latest successful record wins
        missing = [i for i in ids if i not in recs]
        if missing:
            raise SystemExit(f"{path}: {len(missing)} items without a successful call; re-run first.")
        model = next(iter(recs.values()))["model"]
        res = score(items, {i: predicted_item(bench[i], recs[i]["state"]) for i in ids})
        res["invalid_outputs"] = sum(1 for i in ids if not recs[i]["valid"])
        res["reasoning_tokens"] = sum(int(((a.get("usage") or {}).get("completion_tokens_details") or {})
                                          .get("reasoning_tokens") or 0)
                                      for i in ids for a in recs[i]["attempts"])
        report["models"][model] = res
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"rule_sensor": report["rule_sensor"]["end_to_end_accuracy"],
                      **{m: v["end_to_end_accuracy"] for m, v in report["models"].items()}}, indent=2))


if __name__ == "__main__":
    main()
