# SCQA reference implementation

This directory is the executable source of the paper.

```bash
python code/run_experiments.py
python code/annotation_cli.py init \
  --input paper/data/situatedqa_temporal_sample.jsonl --out annotations
python code/run_multimodel_eval.py --help
python -m pytest code/tests
```

`run_experiments.py` evaluates the complete situation engine in three settings:
gold structured state, state predicted from claim text, and deliberately
corrupted predicted state. Outputs are written to `paper/results/`.

The annotation tool creates blinded, independently writable packets. Agreement
and adjudication are computed only from actual annotator files; missing ratings
cause a non-zero exit rather than synthetic labels.

The multi-model runner never invents responses. It records the exact provider,
model identifier, prompt, raw response, timestamps, latency, usage and errors in
JSONL, and can resume an interrupted run.

Matched prompt conditions include direct, chain-of-thought, structured,
date-aware, self-reflection and explicit situation-state prompting. Provider
credentials and immutable model identifiers must be supplied by the researcher.
Successful responses and failed requests remain distinguishable in raw JSONL.
