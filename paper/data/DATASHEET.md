# Datasheet for SituationCatch-Bench v0.2

## Motivation
The benchmark isolates failures where all decisive evidence is present but an answer depends on time, scope, modality, source authority, observer knowledge, an omitted premise or a counterfactual world.

## Composition
4,200 synthetic English instances: 600 in each of seven categories. Each JSONL record contains a question, shuffled claims, query time, the user's region when the question states one, required situation variables, gold action and gold answer.

Every category is balanced exactly by item index. Yes/no categories (modality, scope, observer, counterfactual) have 300 items per answer; hidden-premise items are 300 CLARIFY, 150 yes and 150 no; temporal items split 300/300 between queries after the last appointment and queries before the later events; and wherever claim order could decide the answer, the decisive claim is the most recent one in exactly half of the items. No constant answer and no "pick the newest claim" rule can therefore exceed chance on the decisive variable.

## Generation and quality control
Instances are produced by `code/run_diagnostic.py` from auditable templates with deterministic seed 20260717. Invariants are checked by construction, and the repository tests verify that the reference engine answers every item correctly from the gold state. No personal data, copyrighted corpus text or human-subject data are included.

## Intended uses
Diagnostic evaluation, unit testing of temporal/event reasoning, and controlled ablation of situation-state components.

## Out-of-scope uses
The benchmark must not be used to claim general natural-language competence, safety in high-stakes deployment, multilingual robustness or human-level situation awareness.

## Distribution and maintenance
The paper package and public GitHub repository contain the generator and
generated JSONL under the repository MIT licence. Third-party benchmark samples
retain their source licences. A DOI should be cited only if and when an archival
deposit is minted; the Git commit or release tag identifies the reviewed version
in the meantime.

## Version history
- **v0.2** (current): balanced answers and decorrelated claim recency, as above.
- **v0.1**: one fixed answer per category, and the decisive claim was always the
  most recent, so answer priors and recency solved most categories and two
  ablations (source status, world identity) could not fail. v0.1 and every
  result computed on it are archived under `data/v0.1/` and `results/v0.1/`.
