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


def _retry_delay_seconds(detail):
    """Best-effort parse of a provider-supplied retry delay (e.g. '37s')."""
    m = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', detail)
    if m:
        return float(m.group(1))
    m = re.search(r"retry-after[\"']?\s*[:=]\s*[\"']?(\d+)", detail, re.I)
    return float(m.group(1)) if m else None


def post(url, headers, body, max_retries=6):
    """POST JSON; transparently back off on rate-limit / transient errors.

    Free-tier gateways return 429 (quota) and occasional 503; these are not
    real failures, so retry with the server-suggested delay (capped) before
    surfacing an error. Persistent failures still raise so the caller records
    an error record rather than a synthetic result.
    """
    data = json.dumps(body).encode()
    for attempt in range(max_retries + 1):
        request = urllib.request.Request(
            url, data=data, method="POST",
            headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            transient = exc.code in (429, 500, 502, 503, 504)
            if transient and attempt < max_retries:
                wait = _retry_delay_seconds(detail)
                if wait is None:
                    wait = min(2 ** attempt, 60)
                wait = min(wait + 1, 90)
                print(f"    [{exc.code}] backing off {wait:.0f}s "
                      f"(attempt {attempt + 1}/{max_retries})", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc
        except urllib.error.URLError as exc:
            if attempt < max_retries:
                wait = min(2 ** attempt, 30)
                print(f"    [network] backing off {wait:.0f}s "
                      f"(attempt {attempt + 1}/{max_retries}): {exc.reason}",
                      flush=True)
                time.sleep(wait)
                continue
            raise


def call_openai(model, system, user, key, max_tokens):
    body = {"model": model, "instructions": system, "input": user,
            "temperature": 0, "max_output_tokens": max_tokens}
    data = post("https://api.openai.com/v1/responses",
                {"Authorization": f"Bearer {key}"}, body)
    text = data.get("output_text", "")
    if not text:
        text = " ".join(c.get("text", "") for o in data.get("output", [])
                        for c in o.get("content", []))
    return text.strip(), data.get("usage", {}), data.get("id")


def call_anthropic(model, system, user, key, max_tokens):
    body = {"model": model, "max_tokens": max_tokens, "temperature": 0,
            "system": system, "messages": [{"role": "user", "content": user}]}
    data = post("https://api.anthropic.com/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01"}, body)
    text = " ".join(x.get("text", "") for x in data.get("content", [])
                    if x.get("type") == "text")
    return text.strip(), data.get("usage", {}), data.get("id")


def call_gemini(model, system, user, key, max_tokens):
    model = model.removeprefix("models/")
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{urllib.parse.quote(model, safe='-_.')}:generateContent?key="
           f"{urllib.parse.quote(key, safe='')}")
    base = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}]}
    gen = {"temperature": 0, "maxOutputTokens": max_tokens}
    # Prefer thinking off: Gemini 2.x/3.5 "thinking" tokens are drawn from
    # maxOutputTokens, so pinning the budget to 0 keeps the whole budget for the
    # answer and stops the JSON conditions from truncating (uniform decoding
    # control). Some newer models reject an explicit zero budget (HTTP 400); for
    # those fall back to the default thinking mode with a larger budget so the
    # answer still fits after the reasoning tokens.
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
    return text.strip(), data.get("usageMetadata", {}), data.get("responseId")


def call_chat_completions(base_url, extra_headers=None):
    def call(model, system, user, key, max_tokens):
        body = {"model": model, "temperature": 0, "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}]}
        data = post(f"{base_url}/chat/completions",
                    {"Authorization": f"Bearer {key}", **(extra_headers or {})},
                    body)
        text = " ".join((c.get("message") or {}).get("content") or ""
                        for c in data.get("choices", []))
        return text.strip(), data.get("usage", {}), data.get("id")
    return call


def call_mock(model, system, user, key, max_tokens=None):
    """Offline pipeline-validation control. NOT a language model.

    A deterministic latest-mention text heuristic: it reads only the rendered
    evidence block (never gold labels) and answers with the actor of the most
    recent claim, "yes" for polar questions, or CLARIFY when no claim parses.
    Records produced with this adapter are synthetic controls for exercising
    the harness end-to-end and must never be reported as model evidence.
    """
    claims = re.findall(r"^- \((?:time (\d+))[^)]*\) (.+)$", user, re.M)
    question = (re.search(r"^Question: (.+)$", user, re.M) or [None, ""])[1]
    answer = "CLARIFY"
    if claims:
        latest = max(claims, key=lambda c: int(c[0]))
        if re.match(r"(?i)\b(has|is|are|was|does|do|can|did|will)\b", question):
            answer = "yes"
        else:
            token = re.match(r"(?:In reality, |In the hypothetical scenario, )?"
                             r"(?:The |An? )?([A-Za-z]+)", latest[1])
            answer = token.group(1) if token else "CLARIFY"
    if "JSON" in system:
        raw = json.dumps({"state": {}, "action": "ANSWER" if answer != "CLARIFY"
                          else "CLARIFY", "answer": answer, "confidence": 0.5})
    elif "FINAL" in system:
        raw = f"Considering the latest claim only. FINAL: {answer}"
    else:
        raw = answer
    return raw, {"mock": True}, None


ADAPTERS = {
    "openai": ("OPENAI_API_KEY", call_openai),
    "anthropic": ("ANTHROPIC_API_KEY", call_anthropic),
    "gemini": ("GEMINI_API_KEY", call_gemini),
    "openrouter": ("OPENROUTER_API_KEY",
                   call_chat_completions("https://openrouter.ai/api/v1")),
    "xai": ("XAI_API_KEY",
            call_chat_completions("https://api.x.ai/v1")),
    "mock": (None, call_mock),
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
    p.add_argument("--max-tokens", type=int, default=1024,
                   help="Output-token budget, applied uniformly to every "
                        "condition. Must be large enough that the verbose JSON "
                        "conditions are not truncated.")
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    env, adapter = ADAPTERS[args.provider]
    key = os.environ.get(env) if env else "unused"
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
                          "max_tokens": args.max_tokens,
                          "started_at": started.isoformat()}
                try:
                    raw, usage, request_id = adapter(
                        args.model, system, user, key, args.max_tokens)
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
