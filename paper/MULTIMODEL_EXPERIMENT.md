# End-to-end multi-model experiment

This package contains no invented frontier-model results. It archives the raw
JSONL outputs of the completed audited Gemini-family pilot; use the commands
below to reproduce it or extend it to independent model families.

## E5 (situation-intervention) study — turnkey path

The E5 study design is frozen in `code/experiment_manifest.e5.json` (models,
gateway, conditions, sample, cost estimate). One driver runs it end to end:

```bash
# Credit-free harness validation (mock provider; never reported as model evidence)
python code/run_e5.py --provider mock --smoke 5

# Cheap preflight against the paid gateway, then the full run (~6-10 USD)
export OPENROUTER_API_KEY=...
python code/run_e5.py --smoke 3
python code/run_e5.py
```

`run_e5.py` renders the stratified 210-item sample if absent, skips any provider
whose key is missing (reporting it, never fabricating), evaluates every model
with the resumable runner, and writes `paper/results/multimodel_summary.csv`.
The reported Gemini-family run is complete. OpenRouter credits and permitted
egress are still required for the planned independent-family extension.

Before any cross-family result is cited, run the fail-closed matrix audit. It
requires at least three provider families, identical item-condition cells for
every model, no duplicate cells, and rejects the offline mock adapter:

```bash
python code/audit_multifamily.py paper/results/raw_nl/*.jsonl \
  --conditions direct chain_of_thought structured date_context self_reflection situation \
  --out paper/results/multifamily_audit.json
```

Mock records may be used only by automated harness tests; they are never model
evidence and must not be copied into the results directory.
The per-provider commands below remain available for single-model or native-endpoint
runs.

## Native single-provider endpoints

```bash
export OPENAI_API_KEY=...
python code/run_multimodel_eval.py --provider openai --model MODEL_ID --out results/openai_MODEL_ID.csv

export ANTHROPIC_API_KEY=...
python code/run_multimodel_eval.py --provider anthropic --model MODEL_ID --out results/anthropic_MODEL_ID.csv

export GEMINI_API_KEY=...
python code/run_multimodel_eval.py --provider gemini --model MODEL_ID --out results/gemini_MODEL_ID.csv
```

For a publishable experiment, evaluate at least three model families, record the
execution date, exact model snapshot, prompts, temperatures, token budgets,
failed calls and costs. Use a larger licensed SituatedQA split rather than only
the bundled 12-item smoke-test sample. Compare direct question answering,
explicit date context and Situation Engineering under identical model and token
budgets. Do not report results until raw outputs and a frozen manifest are
archived.
