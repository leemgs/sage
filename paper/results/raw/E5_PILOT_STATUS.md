# E5 pilot raw responses — INCOMPLETE, not a result

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
- **Free-tier quota exhausted mid-run.** No model completed all 35 items:
  `gemini-2.5-flash-lite` covered 4/7 categories, `gemini-2.5-flash` 2/7. The
  succeeding items are a biased subset (whichever calls landed inside a quota
  window), not the intended stratified sample.
- **Directions disagree and N is tiny** (6–13 scored per condition), so no
  situation-on-versus-off contrast can be claimed.

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
