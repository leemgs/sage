#!/usr/bin/env python3
"""Resumable, auditable multi-provider natural-question evaluation."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DIRECT = "Answer briefly. Return only the answer, or CLARIFY if essential information is missing."
CHAIN_OF_THOUGHT = """Reason step by step about the evidence and query date, then
return a final line in the form FINAL: <answer>. Use CLARIFY if essential
information is missing."""
STRUCTURED = """Identify actor, event, query time, validity, scope, modality,
source status, observer and world before answering. Return strict JSON with
keys analysis and answer."""
SELF_REFLECTION = """Produce a candidate answer, check it for stale time,
incorrect scope, modality, source, observer or hypothetical-world errors, then
return strict JSON with keys candidate, verification and answer."""
SITUATION = """Answer using an explicit query-relative situation state. Resolve
time, modality, scope, source status, observer knowledge and possible-world
identity before answering. Return strict JSON with keys state (an object),
action (ANSWER, CLARIFY, or ABSTAIN), answer, and confidence."""


def post(url, headers, body):
    request = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc


def call_openai(model, system, user, key):
    body = {"model": model, "instructions": system, "input": user,
            "temperature": 0, "max_output_tokens": 512}
    data = post("https://api.openai.com/v1/responses",
                {"Authorization": f"Bearer {key}"}, body)
    text = data.get("output_text", "")
    if not text:
        text = " ".join(c.get("text", "") for o in data.get("output", [])
                        for c in o.get("content", []))
    return text.strip(), data.get("usage", {}), data.get("id")


def call_anthropic(model, system, user, key):
    body = {"model": model, "max_tokens": 512, "temperature": 0,
            "system": system, "messages": [{"role": "user", "content": user}]}
    data = post("https://api.anthropic.com/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01"}, body)
    text = " ".join(x.get("text", "") for x in data.get("content", [])
                    if x.get("type") == "text")
    return text.strip(), data.get("usage", {}), data.get("id")


def call_gemini(model, system, user, key):
    model = model.removeprefix("models/")
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{urllib.parse.quote(model, safe='-_.')}:generateContent?key="
           f"{urllib.parse.quote(key, safe='')}")
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 512}}
    data = post(url, {}, body)
    text = " ".join(p.get("text", "") for c in data.get("candidates", [])
                    for p in c.get("content", {}).get("parts", []))
    return text.strip(), data.get("usageMetadata", {}), data.get("responseId")


def call_chat_completions(base_url, extra_headers=None):
    def call(model, system, user, key):
        body = {"model": model, "temperature": 0, "max_tokens": 512,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}]}
        data = post(f"{base_url}/chat/completions",
                    {"Authorization": f"Bearer {key}", **(extra_headers or {})},
                    body)
        text = " ".join((c.get("message") or {}).get("content") or ""
                        for c in data.get("choices", []))
        return text.strip(), data.get("usage", {}), data.get("id")
    return call


ADAPTERS = {
    "openai": ("OPENAI_API_KEY", call_openai),
    "anthropic": ("ANTHROPIC_API_KEY", call_anthropic),
    "gemini": ("GEMINI_API_KEY", call_gemini),
    "openrouter": ("OPENROUTER_API_KEY",
                   call_chat_completions("https://openrouter.ai/api/v1")),
    "xai": ("XAI_API_KEY",
            call_chat_completions("https://api.x.ai/v1")),
}


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).casefold()).strip()


def matches(gold, answer):
    """Word-boundary containment: gold 'no' must not match 'now closed'."""
    g, a = normalize(gold), normalize(answer)
    return bool(g) and (g == a or f" {g} " in f" {a} ")


def extract_answer(raw, condition):
    if condition in ("direct", "date_context"):
        return raw
    if condition == "chain_of_thought":
        match = re.search(r"FINAL:\s*(.+)$", raw, re.I | re.M)
        return match.group(1).strip() if match else raw
    try:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
        parsed = json.loads(text)
        return str(parsed.get("answer", parsed.get("action", "")))
    except (ValueError, TypeError):
        return raw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="paper/data/situatedqa_temporal_sample.jsonl")
    p.add_argument("--provider", choices=ADAPTERS, required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--conditions", nargs="+",
                   choices=["direct", "chain_of_thought", "structured",
                            "date_context", "self_reflection", "situation"],
                   default=["direct", "chain_of_thought", "structured",
                            "date_context", "self_reflection", "situation"])
    p.add_argument("--sleep", type=float, default=.2)
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    env, adapter = ADAPTERS[args.provider]
    key = os.environ.get(env)
    if not key:
        raise SystemExit(f"Missing {env}; no calls were made.")
    items = [json.loads(x) for x in Path(args.data).read_text().splitlines() if x.strip()]
    if args.limit:
        items = items[:args.limit]
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("error") is None:
                    done.add((r["id"], r["condition"]))
    with out.open("a", encoding="utf-8") as f:
        for item in items:
            for condition in args.conditions:
                if (item["id"], condition) in done:
                    continue
                systems = {
                    "direct": DIRECT, "chain_of_thought": CHAIN_OF_THOUGHT,
                    "structured": STRUCTURED, "date_context": DIRECT,
                    "self_reflection": SELF_REFLECTION, "situation": SITUATION,
                }
                system = systems[condition]
                user = (item["question"] if condition == "direct" else
                        item.get("edited_question", item["question"]))
                started = dt.datetime.now(dt.timezone.utc)
                tic = time.perf_counter()
                record = {"id": item["id"], "provider": args.provider,
                          "model": args.model, "condition": condition,
                          "system_prompt": system, "user_prompt": user,
                          "started_at": started.isoformat()}
                try:
                    raw, usage, request_id = adapter(args.model, system, user, key)
                    answer = extract_answer(raw, condition)
                    gold = item["answers"]
                    record.update(raw_response=raw, normalized_answer=answer,
                                  gold=gold, correct=int(any(
                                      matches(x, answer) for x in gold)),
                                  usage=usage,
                                  request_id=request_id, error=None)
                except Exception as exc:
                    record.update(raw_response=None, normalized_answer=None,
                                  gold=item["answers"], correct=None, usage={},
                                  request_id=None,
                                  error=f"{type(exc).__name__}: {exc}")
                record["latency_ms"] = round((time.perf_counter()-tic)*1000, 2)
                record["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
                f.write(json.dumps(record, ensure_ascii=False) + "\n"); f.flush()
                print(record["id"], condition, record["correct"], record["error"])
                time.sleep(args.sleep)


if __name__ == "__main__":
    main()
