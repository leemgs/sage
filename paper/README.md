# Situation Engineering / SCQA - NMI research package

## Target venue
- **Primary submission target: Nature Machine Intelligence (NMI)**, Springer
  Nature (`sn-jnl.cls`, Numbered/Nature reference style). `main.tex` directly
  includes the submission title, abstract and introduction; there is no stale
  fallback manuscript path.
- Fallback candidates under consideration: Artificial Intelligence (AIJ),
  JAIR, TACL, TMLR.

## Repository layout contract
- `../code/` - the only home of the executable implementation (engine,
  experiments, evaluation harness, figure generation). Do not keep code
  copies under `paper/`.
- `paper/` - LaTeX sources, data, results and reviewer documents.
- `../ppt/` - presentation and poster materials.

## Entry points
- Manuscript: `main.tex`
- Supplement: `supplementary.tex`
- Experiment (repository root): `PYTHONPATH=code python code/run_experiments.py`

## Central research proposition
Prompt engineering designs instructions, context engineering designs the information payload, and harness engineering designs the runtime around an AI agent. Situation engineering designs and validates the active world state that determines which available facts apply to the current query or action. The paper formalizes this as an independent, complementary reliability layer rather than a synonym for longer context.

## Included conceptual contributions
- Formal definition of situation blindness and evidence applicability.
- Six situation-engineering operations: sensing, assembly, updating, validation, policy and observability.
- SE0-SE4 maturity model.
- Reporting protocol and reviewer checklist.
- Research agenda connecting RAG, temporal reasoning, knowledge graphs, agent memory, calibration, human-AI interaction and safety.

## Included empirical work
- SituationCatch-Bench v0.1: 4,200 controlled diagnostic instances, seven categories.
- Executable SCQA symbolic control layer.
- Lexical-RAG, Recency-RAG and Latest-mention controls.
- Item-level predictions and seven mechanistic ablations. Legacy item-level
  bootstrap, sign-flip and rule-confidence outputs are regression diagnostics,
  not primary scientific evidence.
- Gold-, text-predicted- and deliberately corrupted-state evaluation over all 4,200 items.
- Vector/raster figures, datasheet and reviewer-readiness audit.
- Audited E5 pilot: three Gemini-family models on 210 stratified items under
  direct, structured and explicit-situation prompts, with item-level raw
  responses, category-clustered bootstrap intervals, latency and token use.
- Focused top-3 lexical-retrieval baseline and a 12-item SituatedQA temporal
  smoke test. These are preliminary single-provider checks, not cross-family
  confirmation.

## Main measured result
SCQA achieved 100.0% exact action-and-answer accuracy in the structured diagnostic setting. The strongest non-situational control achieved 85.7%. This is explicitly reported as a constructive upper bound, not as evidence that a neural model can extract situation states from arbitrary natural language.
The deterministic text sensor achieved 77.9%, and its deliberately corrupted
state achieved 35.1%; these are controlled sensing diagnostics.

## Submission-critical limitation
A competitive Nature Machine Intelligence submission would be substantially
stronger with multiple independent model families, a larger independently
authored natural-text evaluation, human annotation agreement, and multilingual
and multimodal stress tests. These experiments require external resources and
are not fabricated in this package. The public GitHub repository and MIT
licence are present; a DOI must be cited only after an archive deposit is minted.

## Build
`./run.sh` builds both `main.pdf` and `supplementary.pdf` with three LaTeX
passes each.

## Natural-language and frontier-model extension

`data/situatedqa_temporal_sample.jsonl` is a 12-item smoke-test sample derived
from the public SituatedQA temporal development split. `code/run_multimodel_eval.py`
contains provider adapters and matched prompt conditions. Frontier-model
results are included only when produced by actual API calls, retained as raw
JSONL and admitted by the completion audit.
See `MULTIMODEL_EXPERIMENT.md`.
