# Reviewer response and revision map

## Editorial positioning

The manuscript has been revised from a broad claim of a completed solution for reliable AI to a bounded research article and scaffold on evidence applicability. The new title is **Situation engineering for evidence-applicable artificial intelligence**. The controlled benchmark is labelled an oracle-state conformance test, not an LLM benchmark.

## Major comment 1: Claims exceeded the experiment

**Action.** Rewrote the title, abstract, introduction, Results and Discussion. Added an evidence ladder separating established, supported and proposed claims. Removed the paired P value and calibration result from headline claims. Added an explicit statement that no frontier-model efficacy is established.

## Major comment 2: Generator-solver circularity

**Action.** Reframed SituationCatch-Bench as an intentionally co-designed software conformance suite. Added the end-to-end decomposition `sense -> update -> policy -> generation`; identified sensing as untested; specified hidden-generator, clustered-family, natural and adversarial benchmark extensions.

## Major comment 3: No actual LLM evaluation

**Action.** Retained no invented results. Added a matched confirmatory protocol, immutable model reporting, raw-output archiving and gold/predicted/corrupted-state conditions. The manuscript states that the adapter is executable but the experiment is incomplete.

## Major comment 4: Weak baselines

**Action.** Renamed current methods software controls. Specified required future baselines: direct and structured prompting, chain-of-thought, standard and temporal RAG, event/graph retrieval, reflection/verification agents and Situation Engineering under matched evidence and budgets.

## Major comment 5: Novelty relative to established fields

**Action.** Added a dedicated Related conceptual foundations section and comparison table covering situation semantics, situation/event calculus, belief revision, truth maintenance, POMDPs, dialogue-state tracking, temporal knowledge graphs and bitemporal databases. The contribution is stated as a systems-level applicability contract, not a new universal logic.

## Major comment 6: Calibration was not meaningful

**Action.** Removed rule-derived calibration from Results. Methods now states that it is not neural calibration and specifies proper future metrics: Brier score, ECE, selective risk, risk-coverage area, clarification utility and abstention precision/recall.

## Major comment 7: Statistical overstatement

**Action.** Removed the P value and item-bootstrap confidence intervals as primary scientific evidence. Added the dependence limitation and requirement for scenario/template-clustered bootstrap and pre-specified outcomes in natural studies.

## Major comment 8: Two manuscripts were mixed

**Action.** Shortened and refocused the Results and Discussion. Taxonomy remains as a bounded systems framework; long-term claims are explicitly labelled a staged research programme. The empirical contribution is described as a conformance scaffold.

## Minor comments

- Replaced “human-level reliability” with “epistemically regulated AI” except where explicitly describing a future human comparison.
- Strengthened limitations and security/privacy risks.
- Clarified Data and Code Availability without pretending a DOI exists.
- Expanded the AI-use disclosure.
- Added a research reporting protocol and machine-readable manifest recommendation.

## Remaining work before a strong NMI Article submission

1. Execute the multi-model natural-language study with immutable snapshots and raw outputs.
2. Construct an independently annotated natural benchmark and report agreement.
3. Add learned situation sensing and gold/predicted/corrupted-state comparisons.
4. Use strong RAG and agent baselines under matched budgets.
5. Evaluate OOD composition, multilingual data, cost, latency and human clarification.
6. Archive code/data in an immutable public release with DOI and licence.
