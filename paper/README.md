# Situation Engineering / SCQA - NMI research package

## Target venue
- **Primary submission target: Nature Machine Intelligence (NMI)**, Springer
  Nature (`sn-jnl.cls`, Numbered/Nature reference style). The NMI framing is
  controlled by the `\ifNMIframing` toggle in `main.tex` (default: on).
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

## Main measured result
SCQA achieved 100.0% exact action-and-answer accuracy in the structured diagnostic setting. The strongest non-situational control achieved 85.7%. This is explicitly reported as a constructive upper bound, not as evidence that a neural model can extract situation states from arbitrary natural language.
The deterministic text sensor achieved 77.9%, and its deliberately corrupted
state achieved 35.1%; these are controlled sensing diagnostics.

## Submission-critical limitation
A competitive Nature Machine Intelligence submission would be substantially stronger with independent natural-text and frontier/open-model evaluation, human annotation agreement, multilingual and multimodal stress tests and a public archival DOI. Those experiments are proposed but not fabricated in this package.

## Build
`./run.sh` builds `main.pdf`. Run `pdflatex supplementary.tex` twice to build `supplementary.pdf`.

## Natural-language and frontier-model extension

`data/situatedqa_temporal_sample.jsonl` is a 12-item smoke-test sample derived
from the public SituatedQA temporal development split. `code/run_multimodel_eval.py`
contains provider adapters and matched prompt conditions. No frontier-model
result is included unless produced by an actual API call and stored as raw CSV.
See `MULTIMODEL_EXPERIMENT.md`.
