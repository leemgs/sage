# SCQA reproducibility package

Run the complete controlled experiment with:

```bash
python code/run_experiments.py --n-per-category 600 --data data --out results
```

The command deterministically generates 4,200 benchmark instances, evaluates three non-situational baselines and SCQA over five confidence seeds, performs ablations and writes item-level predictions. No network access, proprietary model or hidden dataset is required.

## Scope
This release is a controlled diagnostic implementation. It evaluates whether explicit situation variables and transition rules prevent situation-inconsistent answers. It does **not** establish performance of a trained neural situation extractor on naturally occurring text. That external-validity experiment is specified in the manuscript as future work rather than represented as completed.
