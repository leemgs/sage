# Cover letter and point-by-point response

This document supports submission of *"Situation engineering: separating
evidence applicability from availability in AI systems."* It (1) states the contribution and
its intended article type, and (2) responds point-by-point to an internal
referee report so the editor and reviewers can see, up front, what is claimed,
what is deliberately bounded, and what is left open. Nothing here is a claim of
results not present in the manuscript.

---

## 1. Cover letter (contribution and scope)

This paper contributes, in order of weight:

1. **A falsifiable problem definition.** We name and operationalize *situation
   blindness* — applying a well-supported fact to the wrong time, scope,
   epistemic state, source status, or possible world — and distinguish
   *evidence availability* from *evidence applicability*.
2. **A reusable diagnostic resource.** SituationCatch-Bench: 4,200 items across
   seven applicability categories, with a deterministic generator, datasheet,
   and item-level outputs.
3. **A bounded, audited empirical finding.** Under oracle states a reference
   implementation satisfies all invariants (100.0%); accuracy falls to 66.5%
   with text-inferred states and 45.1% under targeted corruption, consistent
   with a *sensing* bottleneck for that rule-based sensor. Across six models
   from four families (three Gemini models; a pre-registered replication with
   Meta, DeepSeek and Qwen models; n = 210 each), prompting for an explicit
   situation state does not beat matched structured prompting under the
   pre-registered decision rule; evidence without timestamps fails on
   time-dependent items in every family. Language-model sensors (E7) recover
   most cues the rule-based sensor misses (65.7% → 79.0–87.1%), but not
   information absent from the text. We report these results plainly.

We therefore position the manuscript as a **problem-formulation + resource +
diagnostic** paper, not as a method that claims state-of-the-art performance.
We ask the editor to consider it under the article type that best fits a
resource/analysis contribution. We do not claim that situation prompting
improves language models; the value is the formulation, the benchmark, and the
evidence that current prompt/retrieval/agent interventions do not resolve
applicability.

**Integrity posture.** All reported numbers derive from archived raw responses;
a completion audit gates any manuscript table; a fail-closed multi-family audit
refuses to certify cross-family claims we have not earned; and the
simulated-persona annotation run is labelled synthetic and explicitly *not*
human-subject evidence. Code, data, generator, and checksums are released.

---

## 2. Point-by-point response

**R1 — "The headline oracle result is analytic, not an effect size."**
Agreed, and we now say so explicitly: oracle accuracy is presented as
regression-test coverage of the specified invariants, not as a competitive
effect size. Beyond that, we found that benchmark v0.1 fixed one answer per
category and always made the decisive claim the most recent, so answer priors
and recency solved most categories (the 85.7% control value) and two ablations
could not fail. Benchmark v0.2 balances answers and claim recency in every
category: the controls fall to 47.4-54.3%, and each of the seven ablations now
produces exactly 300 errors, all in its own category. v0.1 and its results are
archived.

**R2 — "No evidence the intervention helps a real model."**
We ran the intervention (E5) on three Gemini models, n = 210, under matched
evidence/decoding/budget, audited for complete and balanced coverage, and re-ran
it in full on benchmark v0.2 with the same models and analysis. The honest
outcome is null-to-negative (paired situation−structured = −2.9, −14.8, −2.9
points; only gemini-2.5-flash-lite's 95% cluster-bootstrap interval excludes
zero, and there it is *worse*). We do not claim improvement. This result is
consistent with, and motivates, the paper's central point: an explicit
"situation" field in a prompt is not situation awareness. A pre-registered
replication (E6; Meta, DeepSeek, Qwen) gives −4.3, +19.5 and −0.5 points; the
decision rule (interval above zero in ≥2 of 3 families) is not met, so we report
no detectable difference. The single positive contrast is an extractor artefact
(prose-wrapped JSON, boolean answers); a post-hoc sensitivity analysis, labelled
as such, gives −1.9 [−7.1, +1.9] for that model and no model above zero.

**R3 — "Benchmark–solver circularity; little natural language; baselines."**
We acknowledge the synthetic benchmark shares a schema with the solver and state
this as an external-validity limit. We add (i) a 12-item SituatedQA natural-text
probe (reported honestly as a smoke test, not a result), (ii) a retrieval
baseline, and (iii) a ReAct-style tool-using agent baseline. Because items have
at most three claims, the retrieval condition receives every claim but without
timestamps or metadata; it is 79.4% overall against 86.3% structured and 79.5%
situation, and fails on temporal items (44.4%). We state that it is a metadata
ablation rather than a test of retrieval over a large corpus. A larger
natural-text corpus remains future work and is pre-registered in the external
-validity protocol.

**R5 — "Statistical framing; item independence."**
Items within a category share a template family, so we treat categories as the
unit of independence and report 95% cluster-bootstrap intervals (fixed seed,
deterministic), paired for within-model contrasts, plus selective risk and cost.
Category-level differences are labelled exploratory because of multiplicity.

**M-A — "Single model family (Gemini)."**
Addressed in part. The pre-registered E6 replication adds Meta, DeepSeek and
Qwen models (3,258 records, no failed calls, no reasoning tokens);
`code/audit_multifamily.py` now certifies four developer families. The planned
Anthropic and OpenAI models were dropped before any outcome was inspected
because API credit ran out (Amendment 1, `paper/PREREGISTRATION_E6_E7.md`), so
no proprietary family beyond Gemini is covered; this is stated as a limitation.

**M-B — "No human inter-annotator agreement."**
Acknowledged. Blinded three-annotator packets over a 70-item stratified subset
are prepared; the scoring/adjudication pipeline is validated end-to-end with
*simulated personas that are explicitly not people and not human evidence*. The
human study is stated as required and not yet completed. [If completed before
submission, replace this paragraph with the measured Fleiss-κ and adjudication
summary.]

**M-C — "Ceiling effects / item difficulty."**
Several synthetic categories reach 100% under full evidence, reflecting that the
diagnostic isolates one invariant per item rather than compounding difficulty.
We report per-category results so this is visible and do not aggregate it into a
single headline number.

**M-D — "Article-type fit given a null core result."**
We agree the contribution is a formulation + resource + diagnostic rather than a
performance advance, and have framed the manuscript accordingly (see cover
letter). We defer to the editor on the appropriate article type.

---

## 3. Outstanding items before final acceptance
- Mint an archival DOI (Zenodo deposit is pre-configured via `.zenodo.json`) and
  insert the version DOI into Data/Code availability.
- Complete the human IAA study (packets and pipeline are ready).
- Add ≥1 independent model family once provider access permits (the audit will
  certify it automatically).
