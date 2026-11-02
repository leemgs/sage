# Pre-registration: multi-family E5 replication (E6) and LLM-sensor study (E7)

Frozen on 2026-11-02 **before any call of either study was made**. The git commit that
adds this file is the timestamp. Any later deviation is reported as a deviation, not
silently folded into the design. Probe calls made only to check model availability and
cost (two items, written to a scratch directory, never analysed) are not study data.

Benchmark: SituationCatch-Bench v0.2. Sample: the existing E5 sample
`paper/data/situationcatch_llm_sample.jsonl` (210 items, 30 per category, seed 20260718).
Access: OpenRouter, temperature 0, model reasoning disabled (`{"enabled": false}`; if a
model refuses, `{"effort": "minimal"}`), 1,024 output tokens. Reasoning tokens are
recorded per call.

## E6 — multi-family replication of E5

**Models.** Primary families (the decision rule uses only these):
`anthropic/claude-sonnet-5.5` (Anthropic), `openai/gpt-6.1-sol` (OpenAI),
`meta-llama/llama-4-maverick` (Meta, open weights). Secondary, reported descriptively only:
`deepseek/deepseek-v4.1-flash`, `qwen/qwen3.8-flash`. The three Gemini models of E5
form a fourth family.

**Conditions.** Identical to E5 and run with the identical code: direct, structured,
situation (prompts in `code/run_multimodel_eval.py`); the no-metadata retrieval condition
(`situationcatch_rag_sample.jsonl`, direct prompt); the tool-using agent
(`code/run_agent_eval.py`); the 12-item SituatedQA check.

**Primary contrast (H1).** Within each model, paired situation − structured accuracy,
95% category-clustered bootstrap interval (3,000 resamples, seed 20260726), via
`code/e5_stats.py`.

**Decision rule (from Methods / Supplementary Note 14).** "Explicit situation prompting
improves over structured prompting" is claimed only if the H1 interval lies entirely above
zero in at least two of the three primary families. If it lies entirely below zero in at
least two, we report that situation prompting is harmful. Otherwise we report no
detectable difference. Gemini and secondary models are reported but do not vote.

**Secondary (H2).** In each primary family, no-metadata retrieval accuracy on temporal
items is lower than structured accuracy on temporal items (descriptive; 30 items per
model).

**Integrity.** `code/audit_e5.py` must pass (one successful response per item and
condition) for every model before any number is reported; `code/audit_multifamily.py`
must certify at least three provider families. Failed calls are retried by re-running
the same command; nothing is imputed.

## E7 — LLMs as situation sensors

**Question (referee R4).** The rule-based sensor drops end-to-end accuracy from 100% to
66.5%. Is the sensing gap specific to that sensor, or do LLMs show it too?

**Task.** For each of the 210 sample items, a model receives exactly what the rule-based
sensor receives — the query time, the question and the claim texts, in the benchmark's
claim order, with **no** metadata — and returns, for every claim, the slots the SCQA
engine uses: `event` (fixed vocabulary), `actor`, `status`, `source`, `scope`,
`observed_by`, `time` and `valid_to` (null unless stated in the text), plus the
user's `region` if the question states one. Prompt and vocabulary are fixed in
`code/run_llm_sensor.py` before the run.

**Invalid outputs.** An output that is not valid JSON with one object per claim is
retried once; a second invalid output is kept and scored as a sensing failure (every
slot wrong; the engine receives no claims). API errors are retried by re-running.

**Measures.** (i) Claim-level slot accuracy with the scorer used for the rule sensor
(`score_slots` in `code/run_experiments.py`). (ii) End-to-end accuracy: the predicted
state is passed unchanged to the SCQA engine (`decide`). (iii) The rule-based sensor on
the same 210 items, as the comparison.

**Models.** The three primary E6 models and `google/gemini-2.5-flash`.

**Interpretation rule.** "LLM sensing remains a bottleneck" is supported only if every
model's end-to-end accuracy is below 100% and the shortfall concentrates in slots that
require reading situation cues (status, source, scope, observers, world, region), not
in slots the text cannot reveal (`time`, `valid_from`), which we report separately.
If LLM sensors reach near-100% on cue slots, we report that the sensing gap in this
benchmark is specific to the rule-based sensor.

**Known limitation, stated in advance.** Claim texts contain no timestamps, so no sensor
can recover `time`; temporal items whose answer depends on the query time are therefore
not recoverable from text by design. This is reported, not corrected after the fact.
