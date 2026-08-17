# E5 pilot raw responses — INCOMPLETE, not a result

> **Update (second attempt, after a daily free-tier quota reset).** Re-running
> the 3-model Gemini pilot with a multi-pass, resumable, backoff-driven driver
> still did not complete: the daily free-tier quota was exhausted again before
> any model reached 7/7 categories × 35 items (best: gemini-2.5-flash-lite and
> gemini-2.5-flash at 6/7 categories, ~26/35 and ~24/35 scored; gemini-3.5-flash
> 3/7). Directions are inconsistent across models and N is uneven, so the data
> remain scientifically invalid as an E5 result. **Conclusion: the free tier is
> demonstrably insufficient for even a single-family pilot; a funded key (or an
> account with real quota) is required.** The manuscript stays at \E5readyfalse.

The `e5_gemini_*.jsonl` files in this directory are **real** Gemini API
responses (archived verbatim, successes and errors distinguishable), but they
are an **incomplete free-tier pilot** and must **not** be read as the E5
result. They exist to (a) prove the harness produces real, scored responses
end to end and (b) preserve what was collected before the free-tier quota ran
out.

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
