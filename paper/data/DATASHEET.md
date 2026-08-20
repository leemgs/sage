# Datasheet for SituationCatch-Bench v0.1

## Motivation
The benchmark isolates failures where all decisive evidence is present but an answer depends on time, scope, modality, source authority, observer knowledge, an omitted premise or a counterfactual world.

## Composition
4,200 synthetic English instances: 600 in each of seven categories. Each JSONL record contains a question, shuffled claims, query time, required situation variables, gold action and gold answer.

## Generation and quality control
Instances are produced from auditable templates with deterministic seed 20260717. Invariants are checked by construction. No personal data, copyrighted corpus text or human-subject data are included.

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
