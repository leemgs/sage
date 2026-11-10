# Pre-registration: free-tier replication (E8a) and natural-text temporal study (E8b)

Frozen on 2026-11-10 **before any study call was made**; the git commit that adds this
file is the timestamp. This study has no funding: every call uses OpenRouter's
zero-price (`:free`) endpoints, and the recorded per-call cost is checked to be zero.
Probe calls (two structured items per candidate model, scratch directory, never
analysed) only checked availability, cost and reasoning-token use.

Access and decoding are those of E5/E6: temperature 0, reasoning disabled
(`{"enabled": false}`), 1,024 output tokens, reasoning tokens recorded per call.
Free endpoints have a daily request quota; when it is reached the runner stops
without writing a record (`DailyQuotaExhausted`) and is resumed later. No item is
imputed, substituted or dropped. If a model is withdrawn before its runs complete,
its partial records are reported as incomplete and excluded from every contrast;
no replacement model is added without a dated amendment.

## E8a — free-tier multi-family replication of E5/E6

**Models** (three developers not covered by E5/E6):
`nvidia/nemotron-3-ultra-550b-a55b:free` (NVIDIA),
`dots-studio/dots-3-note-preview:free` (dots / rednote hi lab),
`xingchen-agi/xing4.0-29b-a4b:free` (Xingchen).

**Sample and conditions.** The E5/E6 sample (210 items, 30 per category); direct,
structured and situation prompts, and the no-metadata retrieval condition, with the
unchanged code (`code/run_multimodel_eval.py`). The agent condition and the 12-item
SituatedQA check are not run (quota); E8b replaces the latter.

**H1 (primary).** Within-model paired situation − structured accuracy, 95%
category-clustered bootstrap (3,000 resamples, seed 20260726, `code/e5_stats.py`).
Decision rule as in E6: "improves" only if the interval lies entirely above zero in
at least two of the three models; "harmful" if entirely below zero in at least two;
otherwise "no detectable difference". The primary extractor is the pre-registered
one; `code/sensitivity_rescore.py` is reported as the same labelled post-hoc
sensitivity analysis used for E6.

**H2 (secondary).** Temporal accuracy without metadata < structured temporal
accuracy, in each model (descriptive).

**Integrity.** `code/audit_e5.py` passes for every model; `code/audit_multifamily.py`
certifies at least three developers among the E8a models; every record's
`usage.cost` is 0.

## E8b — natural-text temporal study (SituatedQA)

**Data.** Temporal SituatedQA test split (Zhang & Choi, 2021), commit
`1ef854512fe0f692ca55f92ff2feedf3d7612eda`, file sha256
`4188a381aba574a3c964dfdf9f7a69fad4999c9fc6f9a6534fec6dcc731c66a6`. 300 items, 75 per
`date_type` stratum (orig, start, sampled_year, sampled_date), seed 20261110
(`code/prepare_situatedqa_eval.py`; ids in `paper/data/situatedqa_e8_ids.jsonl`). The
upstream repository states no licence, so question texts are not redistributed:
committed raw records omit the prompt text and keep item ids.

**Models.** `nvidia/nemotron-3-ultra-550b-a55b:free` and
`dots-studio/dots-3-note-preview:free`, run after E8a.

**Conditions.** `direct` (the undated question, direct prompt); `date_context` (the
dated question, same direct prompt); `structured` and `situation` (dated question).
Scoring: the existing word-boundary containment of any gold answer
(`matches` in `code/run_multimodel_eval.py`).

**NL-H1.** Paired situation − structured accuracy, 95% bootstrap clustered on the
upstream question id (`code/e8_nl_stats.py`). Situation prompting is said to improve
on natural text only if the interval lies entirely above zero in both models.

**NL-H2 (availability vs applicability on natural text).** On time-dependent items
(`date_type` ≠ orig), dated − undated accuracy (`date_context` − `direct`) is above
zero (interval above zero) in each model; on static (orig) items the same contrast is
the control and is predicted to include zero.

**Known limitations, stated in advance.** Containment scoring undercounts correct
paraphrases equally across conditions; model knowledge has a cut-off, so recent
dates may be unanswerable from parametric knowledge alone; 300 items and two models
are a bounded natural-text test, not the 1,200-scenario set of Supplementary Note 14.
