# NMI reviewer-readiness audit

## Editorial significance
- [x] Broad claim is framed as a machine-intelligence problem, not a prompt trick.
- [x] Situation engineering is distinguished from prompt, context and harness engineering.
- [x] A formal evidence-applicability object, maturity model and community research agenda are provided.
- [x] The paper contributes a framework, benchmark taxonomy, executable artifact and falsifiable ablations.
- [x] A bounded neural-model check is reported on synthetic items and a 12-item natural-text smoke test.
- [ ] Multiple independent model families and a larger naturally occurring corpus remain required for a strong general NMI claim.

## Scientific validity
- [x] No fabricated commercial-LLM or human-study results.
- [x] Exact generation seed, item count, methods and item-level outputs included.
- [x] Paired comparison, confidence/calibration reporting and component ablations included.
- [x] Claims restricted to the controlled diagnostic setting.
- [x] Symbolic control and neural sensing are explicitly separated.
- [ ] Independent annotation and external-domain validation are not yet performed.

## Research usefulness
- [x] Prompt/context/harness/situation taxonomy and comparison table.
- [x] SE0-SE4 maturity model.
- [x] Six-part reporting protocol and supplementary checklist.
- [x] Stage-specific evaluation metrics and future benchmark modules.
- [x] Governance, provenance, uncertainty and sensitive-state risks discussed.

## Reproducibility
- [x] One-command experiment.
- [x] Dataset generator and frozen generated dataset.
- [x] Item-level predictions and aggregate tables.
- [x] Data and code availability statements.
- [x] Datasheet and limitations.

## Ethics and transparency
- [x] Synthetic data contain no personal or sensitive records.
- [x] Intended and prohibited uses stated.
- [x] AI-assisted writing and analysis disclosure included.
- [x] Situation-state privacy and authority-bias risks discussed.
- [ ] Author must verify affiliation, institutional approvals and corporate publication clearance.

## Submission packaging
- [x] main.tex entry file and compiled PDF.
- [x] Figures in vector and raster form.
- [x] Supplementary Methods/Results and design guidance file.
- [x] Public repository and MIT licence are stated consistently.
- [ ] Mint and cite an archival DOI if the author creates a repository deposit; do not use a placeholder DOI.

## Author-only submission gate
- [ ] Confirm the author name, ORCID, correspondence email and affiliation exactly as they should appear in the journal system.
- [ ] Confirm that the no-specific-funding and no-competing-interests declarations are accurate.
- [ ] Obtain any institutional or employer publication clearance that applies.
- [ ] Upload `main.pdf` and `supplementary.pdf` as separate files and provide the exact Git commit or release tag reviewed by editors.

## Cross-layer engineering taxonomy
- The manuscript distinguishes prompt, context, retrieval, memory, situation, tool/function-calling, protocol/interface, harness, evaluation, observability/provenance, serving, and guardrail/security engineering.
- Terms are grouped into semantic/cognitive, action/runtime, and measurement/resource planes to avoid presenting overlapping terms as mutually exclusive silos.
- Situation engineering is defined by evidence applicability and active-world-state control, not by ownership of retrieval, memory, tools, or orchestration.
- Supplementary Notes provide typed interfaces, anti-patterns, and a minimum cross-layer reporting standard.
