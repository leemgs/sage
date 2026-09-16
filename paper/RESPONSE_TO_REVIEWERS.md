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
   implementation satisfies all invariants (100.0%); accuracy falls to 77.9%
   with text-inferred states and 35.1% under targeted corruption, localizing an
   independent *sensing* bottleneck. In a preliminary three-model
   Gemini-family test (n = 210), prompting for an explicit situation state does
   **not** beat matched structured prompting and trails focused retrieval; a
   tool-using agent is weakest. We report this null-to-negative result plainly.

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
effect size. The 85.7% control value is described as a structural consequence of
the equally-weighted categories, not an empirical baseline.

**R2 — "No evidence the intervention helps a real model."**
We ran the intervention (E5) on three Gemini models, n = 210, under matched
evidence/decoding/budget, audited for complete and balanced coverage. The honest
outcome is null-to-negative (paired situation−structured = +1.4, −10.0, +0.0
points; only gemini-2.5-flash-lite's 95% cluster-bootstrap interval excludes
zero, and there it is *worse*). We do not claim improvement. This result is
consistent with, and motivates, the paper's central point: an explicit
"situation" field in a prompt is not situation awareness; the bottleneck is
sensing/validation of the state.

**R3 — "Benchmark–solver circularity; little natural language; baselines."**
We acknowledge the synthetic benchmark shares a schema with the solver and state
this as an external-validity limit. We add (i) a 12-item SituatedQA natural-text
probe (reported honestly as a smoke test, not a result), (ii) a top-3 retrieval
(RAG) baseline, and (iii) a ReAct-style tool-using agent baseline. RAG is
strongest overall; the full-evidence conditions lead only on temporal-validity
and observer-knowledge items, which we mark as exploratory. A larger
natural-text corpus remains future work and is pre-registered in the external
-validity protocol.

**R5 — "Statistical framing; item independence."**
Items within a category share a template family, so we treat categories as the
unit of independence and report 95% cluster-bootstrap intervals (fixed seed,
deterministic), paired for within-model contrasts, plus selective risk and cost.
Category-level differences are labelled exploratory because of multiplicity.

**M-A — "Single model family (Gemini)."**
Acknowledged as the primary external-validity limitation. We do not make a
cross-family claim; `code/audit_multifamily.py` fails closed (requires ≥3
provider families, rejects mock records) and currently reports "found 1", which
we take as the honest status. Extension to independent families is specified in
the protocol and blocked only by provider access, not by design.

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
