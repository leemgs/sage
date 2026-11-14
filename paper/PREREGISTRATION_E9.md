# Pre-registration: natural-text geographic-scope study (E9)

Frozen on 2026-11-14 **before any study call was made**; the git commit that adds this
file is the timestamp. Like E8, this study has no funding: every call uses OpenRouter's
zero-price (`:free`) endpoints and the recorded per-call cost is checked to be zero.

**Purpose.** E8b tested natural text only for the temporal category. E9 extends the
natural-text evidence to the *scope* category with the geographic split of the same
independently authored dataset, using the identical design. Only these two SituatedQA
splits are available to this unfunded study without new data access; observer
knowledge, counterfactual worlds, source conflict, modality and hidden premises remain
untested on natural text, and this is stated as a limitation.

**Data.** Geographic SituatedQA test split (Zhang & Choi, 2021), commit
`1ef854512fe0f692ca55f92ff2feedf3d7612eda`, file `data/qa_data/geo.test.jsonl`, sha256
`097d74586533991f5c1816a9dec4b785dbcfe4512fe2cbbe46b914104103b3b7` (506 rows; 501 after
removing exact (question id, location) duplicates, location compared case-insensitively).
300 items drawn uniformly, seed 20261114 (`code/prepare_situatedqa_geo_eval.py`; ids in
`paper/data/situatedqa_geo_e9_ids.jsonl`; 125 upstream questions). The upstream repository
states no licence, so question texts are not redistributed; committed raw records omit
the prompt text.

**Models.** `nvidia/nemotron-3-ultra-550b-a55b:free` and
`dots-studio/dots-3-note-preview:free` (the E8b models), reasoning disabled,
temperature 0, 1,024 output tokens.

**Conditions** (`code/run_multimodel_eval.py`, unchanged prompts): `direct` (the
unlocated question, direct prompt); `location_context` (the located question, same
direct prompt); `structured` and `situation` (located question). Scoring: word-boundary
containment of any gold answer for that location (`matches`).

**GEO-H1.** Paired situation − structured accuracy, 95% bootstrap clustered on the
upstream question id (3,000 resamples, seed 20260726, `code/e9_geo_stats.py`). Situation
prompting is said to improve only if the interval lies entirely above zero in both models.

**GEO-H2.** Located − unlocated accuracy (`location_context` − `direct`) is above zero
(interval entirely above zero) in each model. Unlike E8b there is no control stratum:
every item's unlocated question is ambiguous across locations by construction. A split
into items located in the United States versus elsewhere is reported descriptively only
(NQ questions often presuppose a US reading), not as a test.

**Operation and integrity.** As in E8: the runner stops without writing a record when the
daily free quota is reached and is resumed on later days; transient errors are retried
until each item and condition has one success; no item is imputed, substituted or
dropped; a model withdrawn before completion is reported as incomplete and excluded,
and no replacement is added without a dated amendment. Responses that reach the output
limit are counted and reported per condition (`code/e8_truncation.py` logic).

**Known limitations, stated in advance.** Many gold answers are long or numeric
(e.g. exchange rates), so containment scoring undercounts correct answers in every
condition alike and absolute accuracy will be low; paired contrasts are the quantities
of interest. Two models and 300 items are a bounded test of one further category.
