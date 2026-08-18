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
> direct. All real, reflected in the manuscript with `\E5readytrue`; it supports
> the thesis that applicability reasoning (temporal validity, observer
> knowledge) — not a prompt-level state slot — is where the state matters. Still
> a **single-provider preliminary** test; multi-family, larger natural-text and
> human agreement remain open.

The earlier free-tier attempts (before billing) did **not** complete and were
never used as a result; that history is retained below for provenance. The
current archived `e5_gemini_*.jsonl` are real, audited, complete responses.

## Why this is not usable as a scientific result

- **Only one provider is reachable.** In the execution environment the egress
  policy allows only `generativelanguage.googleapis.com` (Gemini); OpenRouter,
  OpenAI, xAI, Groq and DeepInfra hosts are blocked, so no non-Gemini family
  could be run.
- **Free-tier quota exhausted mid-run.** No model completed all 35 items. After
  two resumable attempts, `gemini-2.5-flash-lite` reached 26--27 successful
  calls per condition, `gemini-2.5-flash` 22--24 and `gemini-3.5-flash` 6--9.
  Coverage remains unequal across categories, so the succeeding items form a
  quota-selected rather than balanced sample.
- **Directions disagree and N is incomplete**, so no situation-on-versus-off
  contrast is claimed.

## What the run *did* establish (kept in the code, not as data)

- The harness makes real, scored calls and archives raw responses/usage/errors.
- Two real bugs were fixed while running: (1) verbose JSON conditions were
  truncated because Gemini "thinking" tokens consumed the 512-token budget —
  fixed with a uniform, larger `--max-tokens` and `thinkingBudget=0` (with a
  400-fallback for models that reject a zero budget); (2) free-tier rate limits
  now trigger exponential backoff instead of error records.

## To obtain the real E5 result

Run with a key that has real quota (paid credits, or after the daily free-tier
reset), then the existing pipeline fills the manuscript automatically:

```bash
export GEMINI_API_KEY=...        # or OPENROUTER_API_KEY if that host is allowed
python code/run_e5.py            # renders sample, runs models, summarizes, builds table
# then flip \E5readytrue in paper/main.tex
```

Until then the manuscript keeps `\E5readyfalse` and the evidence ladder's E5 row
(“needed to claim LLM improvement”) remains the honest status.

`python code/audit_e5.py ...` is the authoritative completion check. The audit
must print `E5 INTEGRITY GATE: PASS` before E5 is enabled in the manuscript.
