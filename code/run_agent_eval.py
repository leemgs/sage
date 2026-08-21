#!/usr/bin/env python3
"""ReAct-style agentic baseline for E5 (Gemini, multi-turn tool use).

Each item is answered by an agent that may call a `search(query)` tool up to
`--max-steps` times to retrieve claims from the item's own evidence (top-3 by
lexical overlap), then must `answer(value)` or `clarify()`. This is a genuine
tool-using baseline distinct from one-shot RAG: the model decides what to
retrieve and when to stop. Full transcripts, usage and latency are archived;
failed calls are recorded, never fabricated. Scoring matches the other E5
conditions (condition label "agent"), so the audit and summary tools apply.

Usage:
  python code/run_agent_eval.py --model gemini-2.5-flash \
    --data paper/data/situationcatch_bench.jsonl \
    --ids-from paper/data/situationcatch_llm_sample.jsonl \
    --out paper/results/raw_agent/agent_gemini_2_5_flash.jsonl
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_multimodel_eval import post, matches  # noqa: E402

SYSTEM = """You answer a situational question using an evidence store you must
query. Each turn reply with STRICT JSON and nothing else, one of:
  {"tool":"search","query":"<keywords>"}   to retrieve up to 3 matching claims,
  {"tool":"answer","value":"<final answer>"} to answer, or
  {"tool":"clarify"}                          if answer-critical info is missing.
Search as many times as needed (a small budget), then answer or clarify."""


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def search(query, claims, k=3):
    q = tokens(query)
    ranked = sorted(claims, key=lambda c: (len(q & tokens(c["text"])), c["time"]),
                    reverse=True)
    top = sorted(ranked[:k], key=lambda c: c["time"])
    return [c["text"] for c in top] or ["(no claims found)"]


def gemini_turn(model, contents, key, max_tokens=512):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{urllib.parse.quote(model, safe='-_.')}:generateContent?key="
           f"{urllib.parse.quote(key, safe='')}")
    base = {"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": contents}
    gen = {"temperature": 0, "maxOutputTokens": max_tokens}
    try:
        data = post(url, {}, {**base, "generationConfig":
                              {**gen, "thinkingConfig": {"thinkingBudget": 0}}})
    except RuntimeError as exc:
        if "HTTP 400" not in str(exc):
            raise
        data = post(url, {}, {**base, "generationConfig":
                              {**gen, "maxOutputTokens": max(max_tokens, 4096)}})
    text = " ".join(p.get("text", "") for c in data.get("candidates", [])
                    for p in c.get("content", {}).get("parts", []))
    return text.strip(), data.get("usageMetadata", {})


def parse(reply):
    t = reply.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        return json.loads(t)
    except (ValueError, TypeError):
        return None


def run_item(model, item, key, max_steps):
    q = f"Query time: {item['query_time']}. Question: {item['question']}"
    contents = [{"role": "user", "parts": [{"text": q}]}]
    transcript = []
    usage_total = 0
    for step in range(max_steps + 1):
        reply, usage = gemini_turn(model, contents, key)
        usage_total += int((usage or {}).get("totalTokenCount", 0) or 0)
        transcript.append(reply)
        obj = parse(reply)
        contents.append({"role": "model", "parts": [{"text": reply}]})
        if not obj:
            return "", "malformed", transcript, usage_total
        tool = str(obj.get("tool", "")).lower()
        if tool == "answer":
            return str(obj.get("value", "")), "answer", transcript, usage_total
        if tool == "clarify":
            return "CLARIFY", "clarify", transcript, usage_total
        if tool == "search" and step < max_steps:
            hits = search(str(obj.get("query", "")), item["claims"])
            obs = "Search results:\n" + "\n".join(f"- {h}" for h in hits)
            contents.append({"role": "user", "parts": [{"text": obs}]})
            continue
        # out of search budget: force a final answer
        contents.append({"role": "user", "parts": [{"text":
            "Search budget exhausted. Reply now with answer or clarify JSON."}]})
    reply, usage = gemini_turn(model, contents, key)
    usage_total += int((usage or {}).get("totalTokenCount", 0) or 0)
    obj = parse(reply) or {}
    if str(obj.get("tool", "")).lower() == "clarify":
        return "CLARIFY", "clarify", transcript + [reply], usage_total
    return str(obj.get("value", reply)), "answer", transcript + [reply], usage_total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--data", default="paper/data/situationcatch_bench.jsonl")
    p.add_argument("--ids-from", default="paper/data/situationcatch_llm_sample.jsonl")
    p.add_argument("--out", required=True)
    p.add_argument("--max-steps", type=int, default=3)
    p.add_argument("--sleep", type=float, default=0.25)
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Missing GEMINI_API_KEY; no calls were made.")

    wanted = {json.loads(l)["id"] for l in Path(args.ids_from).read_text().splitlines()
              if l.strip()}
    items = [json.loads(l) for l in Path(args.data).read_text().splitlines()
             if l.strip() and json.loads(l)["id"] in wanted]
    if args.limit:
        items = items[:args.limit]
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in out.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                if r.get("error") is None:
                    done.add(r["id"])
    with out.open("a", encoding="utf-8") as f:
        for item in items:
            if item["id"] in done:
                continue
            gold = ([item["gold_answer"]] if item["gold_action"] == "ANSWER"
                    else [item["gold_action"]])
            rec = {"id": item["id"], "provider": "gemini", "model": args.model,
                   "condition": "agent", "gold": gold,
                   "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}
            tic = time.perf_counter()
            try:
                answer, final, transcript, toks = run_item(
                    args.model, item, key, args.max_steps)
                rec.update(normalized_answer=answer, final_action=final,
                           correct=int(any(matches(g, answer) for g in gold)),
                           n_steps=len(transcript), transcript=transcript,
                           usage={"totalTokenCount": toks}, error=None)
            except Exception as exc:
                rec.update(normalized_answer=None, correct=None,
                           usage={}, error=f"{type(exc).__name__}: {exc}")
            rec["latency_ms"] = round((time.perf_counter() - tic) * 1000, 2)
            rec["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(rec["id"], rec.get("final_action"), rec["correct"], rec["error"])
            time.sleep(args.sleep)


if __name__ == "__main__":
    raise SystemExit(main())
