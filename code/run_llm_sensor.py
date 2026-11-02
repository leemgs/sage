#!/usr/bin/env python3
"""E7: use an LLM as the situation sensor (pre-registered in
paper/PREREGISTRATION_E6_E7.md).

The model receives exactly what the rule-based sensor in scqa.engine receives
-- the query time, the question and the claim texts in benchmark order, with no
metadata -- and returns the state slots the SCQA engine uses. Raw responses are
archived; scoring is done separately by code/score_llm_sensor.py.

Usage:
  python code/run_llm_sensor.py --model google/gemini-2.5-flash \
      --out paper/results/raw_sensor/sensor_gemini_2_5_flash.jsonl
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_multimodel_eval import ADAPTERS  # noqa: E402

SYSTEM = """You extract a structured situation state from evidence claims.
For EVERY claim, in the order given, return an object with these fields:
- event: one of appoint, resign, eligibility, close, not_decided, restructure,
  invite, cancel, online, offline, unknown
- actor: the main entity of the claim (a person, unit, "board" or "company")
- status: one of confirmed, proposed, rumor, assumed
- source: one of official, anonymous, email, organizer, monitor, scenario, reported
- scope: "global" if the claim applies everywhere, "reality" if it describes the
  actual world, "counterfactual" if it describes a hypothetical scenario, or
  otherwise the name of the unit, person or group the claim is limited to
- observed_by: list of the people the text says received or know this
  information; [] if the text names no one
- time: integer time of the claim if the text states it, else null
- valid_to: integer end of validity if the text states it, else null
Also return region: the place the user says they live in, if the question
states it, else null.
Return strict JSON only: {"region": ..., "claims": [ ... ]}."""


def render(item):
    lines = [f"Query time: {item['query_time']}.", f"Question: {item['question']}",
             "Claims:"]
    lines += [f"{i}. {c['text']}" for i, c in enumerate(item["claims"], 1)]
    return "\n".join(lines)


def parse(raw, n_claims):
    """Return the parsed object, or None if it is not a valid n-claim state."""
    text = (raw or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        return None
    try:
        obj = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    claims = obj.get("claims")
    if not isinstance(claims, list) or len(claims) != n_claims:
        return None
    if not all(isinstance(c, dict) for c in claims):
        return None
    return obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--provider", default="openrouter", choices=sorted(ADAPTERS))
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--ids-from", default="paper/data/situationcatch_llm_sample.jsonl")
    p.add_argument("--out", required=True)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--sleep", type=float, default=0.2)
    args = p.parse_args()
    env, call = ADAPTERS[args.provider]
    key = os.environ.get(env)
    if not key:
        raise SystemExit(f"Missing {env}; no calls were made.")
    wanted = [json.loads(l)["id"] for l in Path(args.ids_from).read_text().splitlines()
              if l.strip()]
    bench = {x["id"]: x for x in map(json.loads,
             Path(args.data).read_text().splitlines()) if x["id"] in set(wanted)}
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in out.read_text().splitlines():
            r = json.loads(l)
            if r.get("error") is None:
                done.add(r["id"])
    with out.open("a", encoding="utf-8") as f:
        for item_id in wanted:
            if item_id in done:
                continue
            item = bench[item_id]
            user = render(item)
            rec = {"id": item_id, "provider": args.provider, "model": args.model,
                   "task": "llm_sensor", "user_prompt": user,
                   "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}
            tic = time.perf_counter()
            try:
                # One retry if the output is not a valid state (pre-registered);
                # a second invalid output is kept and scored as a sensing failure.
                attempts = []
                for _ in range(2):
                    raw, usage, request_id = call(args.model, SYSTEM, user, key,
                                                  args.max_tokens)
                    attempts.append({"raw_response": raw, "usage": usage,
                                     "request_id": request_id})
                    state = parse(raw, len(item["claims"]))
                    if state is not None:
                        break
                rec.update(attempts=attempts, state=state, valid=state is not None,
                           error=None)
            except Exception as exc:  # API failure: retried by re-running
                rec.update(error=f"{type(exc).__name__}: {exc}"[:2000])
            rec["latency_ms"] = round((time.perf_counter() - tic) * 1000, 2)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(item_id, "valid" if rec.get("valid") else rec.get("error") or "invalid",
                  flush=True)
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
