#!/usr/bin/env python3
"""Clustered-bootstrap statistics, selective risk and cost for the E5 pilot.

Reads the audited raw responses, resolves one success per item/condition
(latest success wins, matching audit_e5.py), and reports for every model:
  * per-condition accuracy with a 95% cluster-bootstrap CI (categories are the
    clusters, because items within a category share a template family, so item
    counts overstate independence -- reviewer concern R5);
  * the paired within-model contrast delta = situation - structured and
    delta = situation - direct, with paired cluster-bootstrap CIs (the pairing
    uses the same resampled items for both conditions);
  * selective-risk figures where a condition emits an ANSWER/CLARIFY/ABSTAIN
    action (coverage = fraction answered, risk = error rate among answered);
  * cost: median latency and mean total tokens per condition.

No fabrication: every number derives from archived responses. Emits a JSON
report and a LaTeX table for the manuscript.
"""
from __future__ import annotations
import argparse
import json
import random
import re
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SEED = 20260726


def read_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def token_total(usage):
    for k in ("totalTokenCount", "total_tokens"):
        if usage.get(k) is not None:
            return int(usage[k])
    return sum(int(usage.get(k, 0) or 0) for k in
               ("prompt_tokens", "completion_tokens", "input_tokens", "output_tokens"))


def choose(records, conditions):
    """One record per (id, condition): latest success, else latest attempt."""
    grouped = defaultdict(list)
    for r in records:
        if r["condition"] in conditions:
            grouped[(r["id"], r["condition"])].append(r)
    chosen = {}
    for key, attempts in grouped.items():
        succ = [r for r in attempts if r.get("correct") is not None]
        chosen[key] = max(succ or attempts, key=lambda r: (r.get("completed_at") or ""))
    return chosen


def category_of(item_id):
    return item_id.rsplit("-", 1)[0]


def cluster_bootstrap(by_cat_values, reducer, n=2000):
    """95% CI by resampling categories, then items within each category."""
    # A local RNG and sorted keys make every interval reproducible and prevent
    # unrelated extra models or input-file ordering from changing the result.
    rng = random.Random(BOOTSTRAP_SEED)
    cats = sorted(by_cat_values)
    if not cats:
        return (None, None)
    stats = []
    for _ in range(n):
        pooled = []
        for _ in range(len(cats)):
            c = rng.choice(cats)
            vals = by_cat_values[c]
            if vals:
                pooled.extend(rng.choice(vals) for _ in vals)
        if pooled:
            stats.append(reducer(pooled))
    stats.sort()
    lo = stats[int(0.025 * len(stats))]
    hi = stats[int(0.975 * len(stats))]
    return (lo, hi)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def parse_action(record):
    """Extract ANSWER/CLARIFY/ABSTAIN from a JSON-emitting condition, if any."""
    raw = (record.get("raw_response") or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        obj = json.loads(raw)
        act = str(obj.get("action", "")).upper()
        if act in ("ANSWER", "CLARIFY", "ABSTAIN"):
            return act
    except (ValueError, TypeError):
        pass
    norm = (record.get("normalized_answer") or "").strip().upper()
    if norm in ("CLARIFY", "ABSTAIN"):
        return norm
    return "ANSWER"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--data", required=True)
    p.add_argument("--conditions", nargs="+", required=True)
    p.add_argument("--json-out", default="paper/results/e5_stats.json")
    p.add_argument("--tex-out", default="paper/section/tables/e5_stats_table.tex")
    p.add_argument("--boot", type=int, default=2000)
    args = p.parse_args()

    items = read_jsonl(args.data)
    n_items = len(items)
    by_model_records = defaultdict(list)
    for path in args.raw:
        for r in read_jsonl(path):
            by_model_records[r["model"]].append(r)

    report = {"data": args.data, "n_items": n_items, "conditions": args.conditions,
              "bootstrap": args.boot, "models": {}}
    for model, records in sorted(by_model_records.items()):
        chosen = choose(records, set(args.conditions))
        # correctness per condition, grouped by category (only scored records)
        cond_cat = {c: defaultdict(list) for c in args.conditions}
        cond_lat = defaultdict(list)
        cond_tok = defaultdict(list)
        cond_action = defaultdict(list)  # (action, correct)
        for (item_id, cond), r in chosen.items():
            if r.get("correct") is None:
                continue
            cat = category_of(item_id)
            cond_cat[cond][cat].append(int(r["correct"]))
            cond_lat[cond].append(float(r.get("latency_ms", 0)))
            cond_tok[cond].append(token_total(r.get("usage") or {}))
            cond_action[cond].append((parse_action(r), int(r["correct"])))

        model_out = {"conditions": {}, "contrasts": {}}
        for cond in args.conditions:
            vals = [v for cat in cond_cat[cond].values() for v in cat]
            acc = mean(vals)
            lo, hi = cluster_bootstrap(cond_cat[cond], mean, args.boot)
            # selective risk
            actions = cond_action[cond]
            answered = [c for a, c in actions if a == "ANSWER"]
            abstained = sum(1 for a, _ in actions if a != "ANSWER")
            coverage = len(answered) / len(actions) if actions else None
            risk = 1 - mean(answered) if answered else None
            model_out["conditions"][cond] = {
                "n": len(vals), "accuracy": acc, "ci95": [lo, hi],
                "median_latency_ms": statistics.median(cond_lat[cond]) if cond_lat[cond] else None,
                "mean_tokens": mean(cond_tok[cond]),
                "coverage": coverage, "selective_risk": risk,
                "n_abstain_or_clarify": abstained,
            }
        # paired contrasts vs structured and direct
        for base in ("structured", "direct"):
            if base not in args.conditions or "situation" not in args.conditions:
                continue
            # paired per category: align items present in both conditions
            paired_by_cat = defaultdict(list)
            sit = {i: r for (i, c), r in chosen.items()
                   if c == "situation" and r.get("correct") is not None}
            bas = {i: r for (i, c), r in chosen.items()
                   if c == base and r.get("correct") is not None}
            for i in set(sit) & set(bas):
                paired_by_cat[category_of(i)].append(
                    int(sit[i]["correct"]) - int(bas[i]["correct"]))
            all_d = [d for v in paired_by_cat.values() for d in v]
            delta = mean(all_d)
            lo, hi = cluster_bootstrap(paired_by_cat, mean, args.boot)
            model_out["contrasts"][f"situation_minus_{base}"] = {
                "n_pairs": len(all_d), "delta": delta, "ci95": [lo, hi],
                "interval_excludes_zero": (lo is not None and (lo > 0 or hi < 0)),
            }
        report["models"][model] = model_out

    Path(ROOT / args.json_out).parent.mkdir(parents=True, exist_ok=True)
    Path(ROOT / args.json_out).write_text(json.dumps(report, indent=2) + "\n")

    # LaTeX table: accuracy (CI) per condition + situation-vs-structured delta (CI)
    def pct(x):
        return f"{100*x:.1f}" if x is not None else r"\textemdash"

    lines = [
        r"% E5 statistics -- generated by code/e5_stats.py. Do not edit by hand.",
        r"\begin{table}[t]",
        r"\caption{Gemini-family E5 accuracy with 95\% cluster-bootstrap confidence intervals "
        r"(categories as clusters; " + str(args.boot) + r" resamples), the paired "
        r"situation$-$structured contrast, and cost. CIs that exclude zero are the "
        r"are flagged as directional estimates only within this bounded analysis.}",
        r"\label{tab:e5-stats}",
        r"\centering\scriptsize\setlength{\tabcolsep}{0pt}%",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Model & Direct & Structured & Situation & $\Delta_{\text{sit-str}}$ "
        r"(95\% CI) & Sit.\ tok. \\",
        r"\midrule",
    ]
    for model in sorted(report["models"]):
        mo = report["models"][model]
        c = mo["conditions"]

        def cell(cond):
            d = c.get(cond)
            if not d:
                return r"\textemdash"
            lo, hi = d["ci95"]
            return f"{pct(d['accuracy'])} ({pct(lo)}--{pct(hi)})"
        con = mo["contrasts"].get("situation_minus_structured", {})
        if con:
            lo, hi = con["ci95"]
            dstr = f"{100*con['delta']:+.1f} ({100*lo:+.1f},{100*hi:+.1f})"
        else:
            dstr = r"\textemdash"
        tok = c.get("situation", {}).get("mean_tokens")
        safe = model.removeprefix("gemini-").replace("-flash-lite", " Flash Lite")
        safe = safe.replace("-flash", " Flash").replace("_", r"\_")
        lines.append(f"{safe} & {cell('direct')} & {cell('structured')} & "
                     f"{cell('situation')} & {dstr} & {tok:.0f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    Path(ROOT / args.tex_out).parent.mkdir(parents=True, exist_ok=True)
    Path(ROOT / args.tex_out).write_text("\n".join(lines))
    print(json.dumps(report, indent=2))
    print(f"Wrote {args.json_out} and {args.tex_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
