# E5 pilot raw responses — COMPLETE (audited), single-family preliminary result

> **Update (paid tier, n=210, rescored + RAG baseline).** With a billed Gemini
> key the 3-model pilot ran to completion on the full 210-item stratified sample
> and **passes the integrity gate** (`code/audit_e5.py`, 0 failed calls). After
> a fair-scoring fix (JSON CLARIFY/ABSTAIN actions credited like the plain
> prompt's token; archived responses rescored deterministically by
> `code/rescore.py`, no re-calling), the result is **null-to-negative**:
> paired situation-minus-structured = +1.4, -10.0, +0.0 points; the only CI that
> excludes zero is gemini-2.5-flash-lite, where situation is significantly
> *worse*. A retrieval-augmented baseline (top-3 lexical claims,
> `prepare_rag_eval.py`) is the strongest condition overall (RAG 91.3% vs
> structured 83.5% vs situation 80.6%), **except** on the two applicability-heavy
> categories — temporal (+8.9) and observer (+5.6) — where the full-state
> situation condition beats RAG. Cost: situation ~3x tokens / ~2x latency of
> direct. All real, reflected in the manuscript with `\EFivereadytrue`; it supports
> the thesis that applicability reasoning (temporal validity, observer
> knowledge) — not a prompt-level state slot — is where the state matters. Still
> a **single-provider preliminary** test; multi-family, larger natural-text and
> human agreement remain open.

The earlier free-tier attempts (before billing) did **not** complete and were
never used as a result; that history is retained below for provenance. The
current archived `e5_gemini_*.jsonl` are real, audited, complete responses.

## Scientific scope and remaining submission risks

- The completed run is usable as a bounded pilot: all 1,890 requested calls
  succeeded and the audit confirms balanced 30-item coverage in each category.
- It is not a multi-family confirmation. All three models use the Gemini API,
  and the 12-item natural-language evaluation is only a smoke test.
- Independent natural-text annotation, human agreement, competitive temporal
  retrieval and verification-agent baselines remain necessary for a broad
  end-to-end efficacy claim. The manuscript states these limits explicitly.

## Exact integrity check

```bash
python code/audit_e5.py \
  paper/results/raw/e5_gemini_2_5_flash.jsonl \
  paper/results/raw/e5_gemini_2_5_flash_lite.jsonl \
  paper/results/raw/e5_gemini_3_5_flash.jsonl \
  --data paper/data/situationcatch_llm_sample.jsonl \
  --conditions direct structured situation
```

This command checks 210 unique items per condition for each model, including
30 items in every category, and must print `E5 INTEGRITY GATE: PASS`. The
separate `raw_rag/` and `raw_nl/` records support the RAG comparison and
natural-text smoke test, respectively; they are not silently pooled into this
matched three-condition audit.
