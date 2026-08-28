# Simulated-persona IAA — pipeline validation only

These files are a deterministic validation run over the 70-item annotation
subset. `context_specialist`, `evidence_auditor`, and `pragmatic_reader` are
software personas, **not people**. Their labels and the resulting agreement
statistics must not be represented as human inter-annotator agreement or used
as human-subject evidence.

Reproduce the run from the repository root:

```bash
python code/annotation_cli.py simulate-personas \
  --input paper/data/annotation_subset_70.jsonl \
  --out paper/results/simulated_iaa/packets \
  --seed 20260828 --disagreement-rate 0.12
python code/annotation_cli.py score \
  --annotations paper/results/simulated_iaa/packets \
  --out paper/results/simulated_iaa/agreement.json
python code/annotation_cli.py adjudicate \
  --annotations paper/results/simulated_iaa/packets \
  --out paper/results/simulated_iaa/adjudication.csv
```

The manifest and score output carry machine-readable provenance and synthetic
flags. The disagreement sheet is intentionally left unadjudicated because no
human adjudication occurred.
