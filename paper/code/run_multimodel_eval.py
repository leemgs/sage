#!/usr/bin/env python3
"""Reproducible multi-model evaluation harness for temporal SituatedQA.

No model is called unless the corresponding API key is supplied. The script
never substitutes fabricated outputs. Supported adapters use REST endpoints;
model names are CLI arguments so a frozen experiment manifest records them.
"""
import argparse, csv, json, os, re, time
from pathlib import Path
import requests

BASELINE_SYSTEM = "Answer the question briefly. Return only the answer."
SITUATION_SYSTEM = """You are a situation-aware question-answering system.
Before answering, identify the explicit query time, resolve time-dependent terms
such as current, last and latest relative to that time, and do not substitute
present-day facts. Return only the answer. If the time is insufficient, return
CLARIFY."""

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def correct(pred, answers):
    p=norm(pred)
    return int(any(norm(a) in p or p in norm(a) for a in answers if norm(a)))

def call_openai(model, system, user, key):
    r=requests.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json={"model":model,"instructions":system,"input":user,"temperature":0},timeout=180)
    r.raise_for_status(); j=r.json()
    if j.get("output_text"): return j["output_text"].strip()
    texts=[]
    for o in j.get("output",[]):
        for c in o.get("content",[]):
            if c.get("type") in ("output_text","text") and c.get("text"): texts.append(c["text"])
    return " ".join(texts).strip()

def call_anthropic(model, system, user, key):
    r=requests.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"},json={"model":model,"max_tokens":128,"temperature":0,"system":system,"messages":[{"role":"user","content":user}]},timeout=180)
    r.raise_for_status(); return " ".join(x.get("text","") for x in r.json().get("content",[]) if x.get("type")=="text").strip()

def call_gemini(model, system, user, key):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body={"systemInstruction":{"parts":[{"text":system}]},"contents":[{"role":"user","parts":[{"text":user}]}],"generationConfig":{"temperature":0,"maxOutputTokens":128}}
    r=requests.post(url,json=body,timeout=180); r.raise_for_status(); j=r.json()
    return " ".join(p.get("text","") for c in j.get("candidates",[]) for p in c.get("content",{}).get("parts",[])).strip()

ADAPTERS={"openai":("OPENAI_API_KEY",call_openai),"anthropic":("ANTHROPIC_API_KEY",call_anthropic),"gemini":("GEMINI_API_KEY",call_gemini)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",default="data/situatedqa_temporal_sample.jsonl")
    ap.add_argument("--provider",choices=ADAPTERS,required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--sleep",type=float,default=0.2)
    args=ap.parse_args()
    env,fn=ADAPTERS[args.provider]; key=os.getenv(env)
    if not key: raise SystemExit(f"Missing {env}; no calls were made.")
    items=[json.loads(x) for x in Path(args.data).read_text().splitlines() if x.strip()]
    rows=[]
    for it in items:
        for condition,system,user in [
            ("direct",BASELINE_SYSTEM,it["question"]),
            ("date_context",BASELINE_SYSTEM,it["edited_question"]),
            ("situation_engineering",SITUATION_SYSTEM,it["edited_question"]),
        ]:
            pred=fn(args.model,system,user,key)
            rows.append({"id":it["id"],"provider":args.provider,"model":args.model,"condition":condition,"prediction":pred,"correct":correct(pred,it["answers"]),"gold":" | ".join(it["answers"])})
            time.sleep(args.sleep)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    for c in sorted({r['condition'] for r in rows}):
        x=[r['correct'] for r in rows if r['condition']==c]
        print(f"{c}: {sum(x)}/{len(x)} = {sum(x)/len(x):.3f}")
if __name__=="__main__": main()
