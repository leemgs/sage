# Plan (draft, not a pre-registration): proprietary model families (P0-1b)

Status: **draft for the author's decision.** Nothing here has been run. If the author
funds the calls, this plan is frozen as `paper/PREREGISTRATION_E11.md` and committed
before the first call, as for E6–E10.

## Why
Reviewers will note that Gemini is the only proprietary family. Adding one Anthropic and
one OpenAI model closes that gap for the paper's central claim (situation prompting vs
structured prompting) with the unchanged protocol.

## Models (prices on OpenRouter, checked 2026-11-19, USD per million tokens, input/output)
| Model | Price | Note |
|---|---|---|
| `anthropic/claude-sonnet-5.5` | 2 / 10 | planned in E6, dropped for lack of credit |
| `openai/gpt-6.1-sol` | 2 / 10 | planned in E6, dropped for lack of credit |
| `anthropic/claude-haiku-5.5` | 0.1 / 0.5 | low-cost alternative (smaller model) |

Whether each endpoint accepts `reasoning: {enabled: false}` must be checked with two probe
calls (as in E8); if not, the E8 fallback (minimal reasoning effort) applies and the
reasoning tokens are reported, because they share the 1,024-token budget (see Flint).

## Options and cost estimates (per model)
Token use per call is taken from the archived E8a/E10 records of non-reasoning models:
about 100–155 input tokens, and 15 (direct), 130–220 (structured/situation) and 30–120
(chain-of-thought/self-reflection) output tokens. "Typical" assumes 200 input and 400
output tokens per call; "ceiling" assumes every response uses the full 1,024 tokens.

| Option | Calls per model | Typical | Ceiling |
|---|---|---|---|
| A. Core claim only: direct, structured, situation on 210 items | 630 | ≈ $2.8 | ≈ $6.7 |
| B. A + no-metadata retrieval (H2) | 840 | ≈ $3.7 | ≈ $8.9 |
| C. B + chain-of-thought and self-reflection (E10) | 1,260 | ≈ $5.5 | ≈ $13.4 |
| D. C + SituatedQA temporal and geographic (E8b, E9) | 3,660 | ≈ $16 | ≈ $39 |

For the two flagship models (Sonnet 5.5, GPT-6.1-sol): **A ≈ $6, B ≈ $7, C ≈ $11,
D ≈ $32 (typical)**; ceilings roughly 2.5× higher. Haiku 5.5 costs about 1/20 of these.
The earlier E6 attempt ran out at about $5, consistent with these figures.

**Recommendation:** option B for both flagship models (≈ $7 typical, ≤ $18 ceiling). It
answers the reviewer's question on the primary contrast and the metadata result without
spending on secondary analyses.

## Decision rule and analysis (unchanged)
Within-model paired situation − structured accuracy, 95% category-clustered bootstrap
(3,000 resamples, seed 20260726); "improves" only if the interval lies entirely above zero
in both proprietary models; integrity gate `code/audit_e5.py`; every call's cost recorded;
sensitivity rescoring reported as post hoc.

## What the author needs to do
1. Add credit on OpenRouter (≈ $10–20 for option B).
2. Give the key to the session through the environment's secure credential settings —
   not by pasting it into the chat.
3. Tell Claude which option to run; Claude freezes the pre-registration, pushes it, then runs.
