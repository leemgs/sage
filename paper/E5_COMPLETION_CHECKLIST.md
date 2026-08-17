# E5 completion checklist

Work required to complete the E5 (matched multi-model intervention) evidence
rung and reflect it in the manuscript. Infrastructure (driver, table generator,
`\ifE5ready` toggle) is already in place, so most items are run + verify +
integrate. The real gate is Phase 0 (key / network).

Status legend: ☐ todo · ☑ done. Owner: **U** = user action, **A** = agent action.

## Phase 0 — Prerequisites (current blockers)
- ☐ **U** Paid Gemini key (enable billing on the AI Studio project). Sufficient for a single-family (Gemini) completion. Cost to run E5 is < $1.
- ☐ **U** *(multi-family only)* Open the egress policy (admin) for `openrouter.ai` etc. + a paid OpenRouter key. Required only for Phase 4 multi-family.

## Phase 1 — Run E5 to completion (A)
- ☐ Recreate the keyfile in the scratchpad (outside the repo); probe the 3 models' quota.
- ☐ `python code/run_e5.py --provider gemini --models gemini-2.5-flash gemini-2.5-flash-lite gemini-3.5-flash --conditions direct structured situation --data paper/data/situationcatch_llm_pilot35.jsonl --sleep 5` (resumable, managed background).
- ☐ Verify completion: every model 7/7 categories, 35/35 scored per condition, errors ≈ 0.

## Phase 2 — Integrity validation (A)
- ☐ Dedup raw files; confirm no bias / no missing category.
- ☐ Compute per-model situation-vs-baseline Δ (situation − best non-situation condition).
- ☐ Report real numbers verbatim — no fabrication, even if the effect is weak or negative.

The executable integrity gate is now implemented in `code/audit_e5.py` and is
called automatically by `code/run_e5.py` before a manuscript table can be
generated. It joins responses to the frozen item set, prefers the latest real
success when retries are duplicated, requires exact per-condition item and
category coverage, and aggregates accuracy, median latency and provider-
normalized token use. The current archived pilot correctly fails this gate;
therefore the boxes above remain unchecked until a funded run supplies the
missing responses.

Manual audit command:

```bash
python code/audit_e5.py paper/results/raw/e5_gemini_*.jsonl \
  --data paper/data/situationcatch_llm_pilot35.jsonl \
  --conditions direct structured situation
```

## Phase 3 — Reflect in the manuscript (A)
- ☐ `make_e5_table.py`: `multimodel_summary.csv` → `section/tables/e5_multimodel_table.tex`.
- ☐ `paper/main.tex`: flip `\E5readyfalse` → `\E5readytrue`.
- ☐ Rewrite `section/026_results_e5.tex` to the actual scope (single-provider Gemini family, the 3 models used, N = 35 stratified, 3 conditions direct/structured/situation, thinking-off decoding, paid tier). Frame as a *preliminary* empirical rung.
- ☐ Reconcile abstract + evidence ladder: the abstract pre-announces "matched … multi-model tests"; state E5 as preliminary and update the E5 ladder row to "partially met".
- ☐ Update `paper/results/raw/E5_PILOT_STATUS.md` to complete; update `code/experiment_manifest.e5.json` status.
- ☐ Rebuild the PDF to confirm it compiles; commit; push to main.

## Phase 4 — NMI-reviewer-grade strengthening (needed to actually pass review)
- ☐ Multiple model *families* (OpenAI, Anthropic, open-weight ≥ 3 families) — needs egress opened.
- ☐ Natural-language evaluation set (SituatedQA / FreshQA / TDBench-derived), beyond schema-generated text. Repo has `situatedqa_temporal_sample.jsonl` (12 items) to expand.
- ☐ Strong baselines: structured-prompt / RAG / agent controls isolating situation semantics from "more prompt / JSON".
- ☐ Human inter-annotator agreement via `code/annotation_cli.py` (≥ 3 independent annotators) — external validity, the main reviewer attack point.
- ☐ Statistics: clustered / bootstrap CIs over template families; selective-risk and risk–coverage curves; pre-registered hypotheses.
- ☐ Cost / latency accounting for maintaining explicit state and provenance (latency + usage already recorded in raw JSONL — just aggregate).
- ☐ Larger N (35 → full 210+).
- ☐ Archival DOI + license (Zenodo) — pre-acceptance requirement.

## Summary
- **Fill E5 honestly in the paper** = Phase 0 key + Phases 1–3 (~30–60 min agent time, < $1).
- **NMI-accept grade** = additionally Phase 4 (multi-family, natural text, human eval — extra resources/time and egress opening).
