# SIMULATED PIPELINE-VALIDATION RECORDS — NOT MODEL EVIDENCE

`pipeline_validation.jsonl` was produced by the offline `mock` provider in
`code/run_multimodel_eval.py`: a deterministic latest-mention text heuristic
that reads only the rendered evidence block (never gold labels). Its purpose
is to exercise the full E5 harness — prompt rendering, all three answer-
extraction paths (plain / FINAL / JSON), word-boundary scoring, resumability
and aggregation — at zero API cost.

These records are synthetic software controls. They must never be cited,
plotted or summarized as language-model results, and they are excluded from
every claim in the manuscript. Real E5 evidence requires executed API calls
recorded with provider usage metadata (see `code/experiment_manifest.e5.json`).
