# E5 completion checklist

Work required to complete the E5 (matched multi-model intervention) evidence
rung and reflect it in the manuscript. Infrastructure (driver, table generator,
`\ifEFiveready` toggle) is already in place, so most items are run + verify +
integrate. The real gate is Phase 0 (key / network).

Status legend: ☐ todo · ☑ done. Owner: **U** = user action, **A** = agent action.

## Phase 0 — Prerequisites (current blockers)
- ☑ **U** Paid Gemini key (billing enabled on the AI Studio project). Done — paid tier verified (20 rapid calls, 0 rate limits). Actual E5 spend ≈ cents.
- ☐ **U** *(multi-family only)* Open the egress policy (admin) for `openrouter.ai` etc. + a paid OpenRouter key. Required only for Phase 4 multi-family.

## Phase 1 — Run E5 to completion (A) — DONE
- ☑ Recreate the keyfile in the scratchpad (outside the repo); probe the 3 models' quota.
- ☑ `python code/run_e5.py --provider gemini --models gemini-2.5-flash gemini-2.5-flash-lite gemini-3.5-flash --conditions direct structured situation --data paper/data/situationcatch_llm_sample.jsonl` (resumable).
- ☑ Verify completion: every model 7/7 categories, 210/210 scored per condition (30/category).

## Phase 2 — Integrity validation (A) — DONE
- ☑ Audit gate passes (`code/audit_e5.py`: `confirmatory_complete: true`); no missing/unbalanced category.
- ☑ Per-model situation-vs-baseline Δ: gemini-2.5-flash +1.4, gemini-2.5-flash-lite −10.0, gemini-3.5-flash +0.0.
- ☑ Report real numbers verbatim — the result is null-to-negative and is reported as such (no fabrication).

The executable integrity gate is implemented in `code/audit_e5.py` and is called
automatically by `code/run_e5.py` before a manuscript table can be generated. It
joins responses to the frozen item set, prefers the latest real success when
retries are duplicated, requires exact per-condition item and category coverage,
and aggregates accuracy, median latency and provider-normalized token use. The
completed paid-tier pilot **passes** this gate, so the manuscript table was
generated and `\EFivereadytrue` was enabled.

Manual audit command:

```bash
python code/audit_e5.py paper/results/raw/e5_gemini_*.jsonl \
  --data paper/data/situationcatch_llm_sample.jsonl \
  --conditions direct structured situation
```

## Phase 3 — Reflect in the manuscript (A) — DONE
- ☑ `make_e5_table.py`: `multimodel_summary.csv` → `section/tables/e5_multimodel_table.tex` (now renders only the conditions actually run).
- ☑ `paper/main.tex`: flipped `\EFivereadyfalse` → `\EFivereadytrue`.
- ☑ Rewrote `section/026_results_e5.tex` to the actual scope (single-provider Gemini family, 3 models, N = 210 stratified, 3 prompt conditions plus RAG, thinking-off decoding, paid tier) and reports the null-to-negative result honestly.
- ☑ Reconciled abstract (preliminary-finding clause) and the E5 evidence-ladder row.
- ☑ Updated `paper/results/raw/E5_PILOT_STATUS.md` and `code/experiment_manifest.e5.json` status.
- ☑ Rebuilt the PDF from the committed sources with `cd paper && ./run.sh`;
  three-pass `pdflatex` completed without errors and refreshed `main.pdf`.

## Phase 4 — NMI-reviewer-grade strengthening (needed to actually pass review)
- 🔒 Multiple model *families* (OpenAI, Anthropic, open-weight ≥ 3 families) — BLOCKED: egress policy allows only Gemini in this environment; needs admin to open it.
- ☑ Natural-language check (SituatedQA, n=12): situation−structured = −17/+0/+0; corroborates the synthetic null. Raw in `paper/results/raw_nl/`. Expanding beyond 12 needs the licensed full split.
- ☑ Strong baselines: structured-prompt ✓, RAG ✓ (`prepare_rag_eval.py`, top-3 lexical retrieval), and agentic/tool-use ✓ (`run_agent_eval.py`, ReAct search-then-answer). Overall RAG 91.3% > structured 83.5% > situation 80.6% > agent 77.5%; full-evidence conditions lead on temporal/observer. No prompt-, retrieval-, or tool-based intervention wins overall.
- 🔒 Human inter-annotator agreement via `code/annotation_cli.py` (≥ 3 independent annotators) — BLOCKED: requires real annotators. The scorer now rejects blank fields, duplicate or mismatched item sets, and changed questions before reporting per-slot Fleiss' kappa and unanimity; synthetic ideal values exist only in the test suite and are not evidence.
- ☐ Run `code/audit_multifamily.py` before reporting Phase 4: it requires ≥3 provider families with an identical, duplicate-free item-condition matrix and rejects mock records.
- ☑ Statistics: clustered/bootstrap CIs over template families + selective-risk/coverage — `code/e5_stats.py`; two situation−structured 95% CIs include zero and one excludes zero in the negative direction (n=210).
- ☑ Cost / latency accounting — aggregated per condition in `code/e5_stats.py` / `e5_audited_summary.csv` (situation ≈ 3× tokens, ≈ 2× latency vs direct).
- ☑ Larger N (35 → full 210). Done: 30/category × 7 = 210, audited, 0 failed calls.
- 🔒 Archival DOI (Zenodo) — needs the user's Zenodo deposit. The MIT
  `LICENSE` is complete; only the account-bound DOI deposit remains.

## Summary
- **Fill E5 honestly in the paper** = Phase 0 key + Phases 1–3 (~30–60 min agent time, < $1).
- **NMI-accept grade** = additionally Phase 4 (multi-family, natural text, human eval — extra resources/time and egress opening).
