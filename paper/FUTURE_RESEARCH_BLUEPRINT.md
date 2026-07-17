# Situation Engineering research blueprint

## Core research questions

- How frequently do supported-but-inapplicable answers occur across model families and domains?
- Which situation variables are most difficult to sense from natural language and multimodal evidence?
- Does an explicit state improve accuracy beyond matched prompt, context, RAG and harness baselines?
- When should an AI retrieve, clarify, abstain or act?
- How should uncertainty over competing situations be calibrated and audited?
- What are the latency, cost, privacy and security costs of state maintenance?

## Minimal end-to-end benchmark record

Each item should contain query time, actors, events, valid-time intervals, observation time, scope, modality, source/provenance, observer knowledge, possible-world identifier, unresolved variables, gold action and answer aliases.

## Required experimental matrix

- Model: at least three proprietary and three open-weight families.
- Intervention: direct, structured prompt, date/context, RAG, temporal/event RAG, verification agent, Situation Engineering.
- State: gold, model-predicted, corrupted/adversarial.
- Data: controlled, semi-synthetic and naturally occurring.
- Generalization: unseen schemas, longer chains, nested beliefs, multilingual and multimodal.

## Required metrics

Situation-slot F1; temporal relation and interval accuracy; scope/modality/source/observer/world classification; final answer accuracy; claim-level applicability; clarification utility; abstention precision and recall; selective risk and coverage; latency; tokens; monetary and energy cost.

## Reproducibility contract

Archive prompts, evidence, raw responses, model identifiers, execution dates, tool traces, state objects, normalization code, annotation guidelines, adjudication logs, seeds, dependency locks, costs and checksums.
