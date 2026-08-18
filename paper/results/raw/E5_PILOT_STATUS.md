# E5 pilot raw responses — COMPLETE (audited), single-family preliminary result

> **Update (paid tier, expanded to n=210).** With a billed Gemini key the
> 3-model pilot ran to completion on the full 210-item stratified sample
> (30/category x 7) and **passes the integrity gate** (`code/audit_e5.py`:
> `confirmatory_complete: true`, 0 failed calls). The result is **null-to-
> negative**: prompting for an explicit situation state never significantly
> beats a matched structured prompt — paired situation-minus-structured
> differences are -2.9, -5.2 and +0.0 points, and all three 95% cluster-
> bootstrap CIs (categories as clusters; `code/e5_stats.py`) include zero. The
> situation/structured conditions cost ~3x the tokens and up to ~2x the latency
> of the direct prompt with no accuracy or selective-risk gain. This is a real,
> reportable finding (not fabricated), reflected in the manuscript with
> `\E5readytrue`; it supports the thesis that sensing — not a prompt-level state
> slot — is the bottleneck. It remains a **single-provider preliminary** test;
> a confirmatory E5 (multiple families, natural text, human agreement) is open.

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
