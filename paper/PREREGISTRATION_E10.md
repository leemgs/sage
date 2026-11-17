# Pre-registration: stronger prompting baselines (E10)

Frozen on 2026-11-17 **before any study call was made**; the git commit that adds this
file is the timestamp. No funding: zero-price (`:free`) OpenRouter endpoints only, and
every successful call's recorded cost is checked to be zero.

**Purpose.** Reviewers may object that situation prompting was only compared with a
plain direct prompt and one structured prompt. E10 adds the two stronger prompting
baselines already implemented in `code/run_multimodel_eval.py` and unchanged since E5:
`chain_of_thought` (step-by-step reasoning about the evidence and query date, then
`FINAL: <answer>`) and `self_reflection` (candidate answer, an explicit check for stale
time, scope, modality, source, observer and hypothetical-world errors, then a JSON
answer). Few-shot prompting and self-consistency are not run: the first would need new
prompt text written after seeing E5–E8 outputs, and the second multiplies calls beyond
the free quota.

**Sample, models and decoding.** The E5–E8 sample (210 items, 30 per category) and the
three E8a models (`nvidia/nemotron-3-ultra-550b-a55b:free`,
`dots-studio/dots-3-note-preview:free`, `recursive/flint-v1.0:free`) with the E8a
decoding (temperature 0, 1,024 output tokens, reasoning disabled; Flint with minimal
reasoning effort, as in E8a Amendment 1). 1,260 calls.

**Comparison data.** The direct, structured and situation records are the archived E8a
records (`paper/results/raw_e8/main/`), collected 2026-11-10 to 2026-11-14; they are not
re-run. Because the endpoints are hosted, the new conditions are collected some days
later; this is stated as a limitation.

**H1 (primary).** Within-model paired situation − chain_of_thought and situation −
self_reflection accuracy, 95% category-clustered bootstrap (3,000 resamples, seed
20260726, `code/e5_stats.py --bases chain_of_thought self_reflection`). Situation
prompting is said to improve on a stronger baseline only if the interval lies entirely
above zero in at least two of the three models, and to be worse only if it lies
entirely below zero in at least two; otherwise no detectable difference.

**H2 (secondary, descriptive).** Accuracy of each stronger baseline relative to the
structured prompt, per model and per category.

**Integrity and operation.** As in E8/E9: `code/audit_e5.py` passes for all five
conditions in every model; daily-quota stops write no record and the run resumes later;
transient errors are retried until one success per item and condition; nothing is
imputed, substituted or dropped; a deterministic provider rejection or a withdrawn
model is handled only by a dated amendment made before outcomes are computed.
Responses that reach the output limit are counted per condition and reported.
