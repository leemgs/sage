# SCQA reference implementation

This directory is the executable source of the paper.

```bash
python code/run_experiments.py
python code/annotation_cli.py init \
  --input paper/data/situatedqa_temporal_sample.jsonl --out annotations
python code/run_e5.py --provider mock --smoke 5   # credit-free E5 harness check
python code/run_e5.py --dry-run                    # inspect frozen plan; no key needed
python code/run_e5.py                             # pilot rerun (needs GEMINI_API_KEY)
python code/run_multimodel_eval.py --help
PYTHONPATH=code python -m pytest code/tests
```

`run_e5.py` is the turnkey driver for the E5 multi-model intervention study. It
reads `code/experiment_manifest.e5.json`, renders the stratified sample if it is
missing, preflight-checks the provider key (no key -> no calls), evaluates every
configured model with the resumable runner, and writes
`paper/results/multimodel_summary.csv`. Use `--provider mock` to validate the
harness without spending credits, `--smoke N` for a cheap preflight, and
`--dry-run` to print the exact per-model commands. It never fabricates results.

`run_experiments.py` evaluates the complete situation engine in three settings:
gold structured state, state predicted from claim text, and deliberately
corrupted predicted state. Outputs are written to `paper/results/`.

The annotation tool creates blinded, independently writable packets. Agreement
and adjudication are computed only from actual annotator files; missing ratings
cause a non-zero exit rather than synthetic labels.

For reproducible **software validation only**, it can also generate three named
simulated personas and score their deliberately imperfect labels. The generated
manifest and agreement report are always marked `synthetic: true` and
`NOT HUMAN-SUBJECT EVIDENCE`:

```bash
python code/annotation_cli.py simulate-personas \
  --input paper/data/annotation_subset_70.jsonl \
  --out paper/results/simulated_iaa/packets
python code/annotation_cli.py score \
  --annotations paper/results/simulated_iaa/packets \
  --out paper/results/simulated_iaa/agreement.json
```

The multi-model runner never invents responses. It records the exact provider,
model identifier, prompt, raw response, timestamps, latency, usage and errors in
JSONL, and can resume an interrupted run.

Matched prompt conditions include direct, chain-of-thought, structured,
date-aware, self-reflection and explicit situation-state prompting. Provider
credentials and immutable model identifiers must be supplied by the researcher.
Successful responses and failed requests remain distinguishable in raw JSONL.
