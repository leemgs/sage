# End-to-end multi-model experiment

This package does not contain invented frontier-model results. Run the frozen
sample with exact model identifiers and archive raw CSV outputs.

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
The only remaining blocker to a real run is OpenRouter credits, not code. The
per-provider commands below remain available for single-model or native-endpoint
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
