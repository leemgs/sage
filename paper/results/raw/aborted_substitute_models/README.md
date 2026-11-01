# Aborted v0.2 runs with substitute models (excluded from all results)

On 2026-10-31 the native Gemini API refused `gemini-2.5-flash` and
`gemini-2.5-flash-lite` for this project ("no longer available to new users"),
so a run was started with substitute models (`gemini-3.5-flash-lite`,
`gemini-3.8-flash`). It was stopped after a few items because the original
models were reachable through OpenRouter, which allows the v0.2 study to use
exactly the v0.1 model set. These partial files are kept for transparency
only; they enter no table, figure or statistic.

`e5_gemini_3_5_flash_native_free_tier.jsonl` holds 20 records from the native
Gemini API, stopped when the project's free-tier quota (20 requests per day for
this model) was reached. To keep one access route per model, gemini-3.5-flash
was then run in full through OpenRouter like the other two models; these 20
records are excluded from every result.
