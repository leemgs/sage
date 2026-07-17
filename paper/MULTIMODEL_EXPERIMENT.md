# End-to-end multi-model experiment

This package does not contain invented frontier-model results. Run the frozen
SituatedQA sample with exact model identifiers and archive raw CSV outputs.

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
