#!/usr/bin/env python3
"""Turnkey driver for the E5 multi-model situation-intervention study.

One command turns the E5 manifest into a complete run: it renders the
stratified sample if needed, preflight-checks provider credentials, evaluates
every configured model with the resumable runner, and writes the aggregate
summary. It never invents model results; a provider whose key is absent is
skipped and reported, and every raw response is stored verbatim by
``run_multimodel_eval.py`` so successes and failures stay distinguishable.

The study design (models, provider gateway, conditions, sample) is read from
``code/experiment_manifest.e5.json`` so the driver and the archived manifest
cannot drift apart.

Credit-free validation (proves the harness is runnable without spending):
    python3 code/run_e5.py --provider mock --smoke 5

Real run (requires OPENROUTER_API_KEY, ~6-10 USD per the manifest estimate):
    python3 code/run_e5.py

Cheap preflight against the paid gateway before the full run:
    python3 code/run_e5.py --smoke 3
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Resolve paths relative to the repository root (this file lives in code/).
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).resolve().parent / "experiment_manifest.e5.json"

# Provider -> required environment variable. Mirrors ADAPTERS in
# run_multimodel_eval.py; kept here so the driver can preflight before spending.
PROVIDER_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "xai": "XAI_API_KEY",
    "mock": None,
}


def slug(model: str) -> str:
    """Filesystem-safe token for a model identifier (e.g. openai/gpt-5.1)."""
    return re.sub(r"[^A-Za-z0-9]+", "_", model).strip("_").lower()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def manifest_models(m: dict) -> list[str]:
    models = m.get("models", {})
    if isinstance(models, dict):
        ordered: list[str] = []
        for group in ("proprietary", "open_weight", "reasoning"):
            ordered += models.get(group, [])
        # Include any other groups the manifest may add later.
        for key, val in models.items():
            if key not in ("proprietary", "open_weight", "reasoning") and isinstance(val, list):
                ordered += val
        return ordered
    return list(models or [])


def manifest_provider(m: dict) -> str:
    # The manifest records the provider as a human string
    # ("openrouter (single gateway ...)"); take the leading token.
    raw = str(m.get("provider", "openrouter")).strip()
    token = re.split(r"[\s(]", raw, 1)[0]
    return token if token in PROVIDER_ENV else "openrouter"


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    m = load_manifest()
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--provider", default=None,
                   help="Override the manifest provider (e.g. 'mock' for a "
                        "credit-free harness check).")
    p.add_argument("--models", nargs="+", default=None,
                   help="Override the manifest model list.")
    p.add_argument("--data", default=m["data"]["rendered_sample"],
                   help="Rendered evaluation sample (JSONL).")
    p.add_argument("--source", default=m["data"]["source"],
                   help="Benchmark source used to render the sample if missing.")
    p.add_argument("--per-category", type=int, default=30,
                   help="Items per category when rendering the sample.")
    p.add_argument("--seed", type=int, default=20260718)
    p.add_argument("--out-dir", default="paper/results/raw",
                   help="Directory for per-model raw JSONL.")
    p.add_argument("--summary", default="paper/results/multimodel_summary.csv")
    p.add_argument("--conditions", nargs="+", default=m.get("conditions"))
    p.add_argument("--smoke", type=int, default=None,
                   help="Limit to N items per model for a cheap preflight.")
    p.add_argument("--sleep", type=float, default=0.2)
    p.add_argument("--dry-run", action="store_true",
                   help="Print the planned per-model commands and exit.")
    args = p.parse_args()

    provider = args.provider or manifest_provider(m)
    models = args.models or manifest_models(m)
    if provider == "mock" and not args.models:
        models = models[:1] or ["pipeline-check"]
    if not models:
        print("No models configured; set them in the manifest or pass --models.",
              file=sys.stderr)
        return 2
    if provider not in PROVIDER_ENV:
        print(f"Unknown provider '{provider}'. Known: {sorted(PROVIDER_ENV)}",
              file=sys.stderr)
        return 2

    # Preflight: credentials. Skip fabricating anything if the key is missing.
    env_var = PROVIDER_ENV[provider]
    if env_var and not os.environ.get(env_var):
        print(f"Missing {env_var} for provider '{provider}'. No calls were made.\n"
              f"Export the key and re-run, or use --provider mock to validate the "
              f"harness without credits.", file=sys.stderr)
        return 1

    # Ensure the rendered sample exists (idempotent).
    data_path = ROOT / args.data
    if not data_path.exists():
        print(f"Rendered sample {args.data} not found; generating it.")
        rc = run([sys.executable, "code/prepare_llm_eval.py",
                  "--data", args.source, "--out", args.data,
                  "--per-category", str(args.per_category),
                  "--seed", str(args.seed)])
        if rc != 0:
            return rc
    n_items = sum(1 for line in data_path.read_text().splitlines() if line.strip())
    print(f"Sample: {args.data} ({n_items} items); provider={provider}; "
          f"models={len(models)}; conditions={len(args.conditions)}")

    raw_paths: list[str] = []
    ran, skipped = 0, 0
    for model in models:
        out = f"{args.out_dir}/e5_{slug(model)}.jsonl"
        raw_paths.append(out)
        cmd = [sys.executable, "code/run_multimodel_eval.py",
               "--provider", provider, "--model", model,
               "--data", args.data, "--out", out,
               "--conditions", *args.conditions,
               "--sleep", str(args.sleep)]
        if args.smoke:
            cmd += ["--limit", str(args.smoke)]
        if args.dry_run:
            print("+", " ".join(cmd))
            continue
        rc = run(cmd)
        if rc == 0:
            ran += 1
        else:
            skipped += 1
            print(f"  model '{model}' returned exit {rc}; "
                  f"partial/errored records are preserved in {out}.",
                  file=sys.stderr)

    if args.dry_run:
        print("Dry run only; no calls were made.")
        return 0

    existing = [rp for rp in raw_paths if (ROOT / rp).exists()]
    if not existing:
        print("No raw output produced; nothing to summarize.", file=sys.stderr)
        return 1
    print(f"Completed {ran} model run(s), {skipped} with errors. Summarizing.")
    rc = run([sys.executable, "code/summarize_multimodel.py", *existing,
              "--out", args.summary])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
