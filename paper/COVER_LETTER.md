# Cover letter

Two versions are provided. **A** is for submitting the current manuscript as an
Article; every claim in it matches the manuscript as it stands. **B** is a
presubmission enquiry if you prefer to ask the editor about fit first. Before
sending, replace the two bracketed fields in A (suggested reviewers and any
excluded reviewers) and state any preprint. Do not include any AI-model
identifier.

---

## Version A — Article submission (current manuscript)

Dear Editor,

I submit the manuscript **"Situation engineering: separating evidence
applicability from availability in AI systems"** for consideration as an Article
in *Nature Machine Intelligence*.

AI systems increasingly answer from retrieved documents, tools and memory, yet a
distinct failure persists: a system retrieves a well-supported fact and applies
it to the wrong time, scope, epistemic state or possible world. I name this
failure **situation blindness** and separate two properties that current
evaluation conflates: whether evidence is *available* and whether it is
*applicable* to the query.

The manuscript contributes (i) a testable failure class and a query-relative
state interface distinct from prompt, context, retrieval, memory and harness
engineering; (ii) **SituationCatch-Bench**, a released 4,200-item diagnostic over
seven applicability axes in which no constant answer or recency rule exceeds
chance, with a deterministic reference system whose seven matched ablations
each produce a failure confined to their category; and (iii) a stress test
showing that accuracy falls from 100.0% with oracle states to 66.5% when states
must be sensed from text by a rule-based sensor and 45.1% under targeted
corruption, consistent with a sensing bottleneck.

I report the neural evidence as it stands. Across nine models from seven
developers (three Gemini models and two pre-registered replications with Meta,
DeepSeek, Qwen, NVIDIA, rednote and Recursive models, n = 210 each), prompting
for an explicit situation state never detectably beats a matched structured
prompt under the pre-registered decision rule, whereas giving the same claims
without timestamps collapses accuracy on time-dependent items for every
developer. On independently written SituatedQA questions, adding the date
(300 temporal questions) or the location (297 geographic questions) raises
accuracy by 22–41 points, while the situation prompt again adds no detectable
benefit. A further pre-registered
study shows that language-model sensors recover most situation cues that a
rule-based sensor misses, but not information absent from the text. I present
the null result plainly because it supports the paper's point: a prompt-level
"situation" field is not situation awareness. Proprietary families beyond
Gemini, natural text beyond temporal questions and human annotation are stated
as limitations and not claimed.

Code, data, generator and item-level outputs are openly available at
https://github.com/leemgs/sage under the MIT licence; an archival DOI will be
minted on acceptance. Use of generative AI tools is documented in Methods. The
work has not been published elsewhere and is not under consideration by another
journal. [If a preprint has been posted, state where.] The work received no
funding and was carried out as an unpaid contribution to the research
community; the author declares no competing interests. I suggest as potential reviewers: [names; areas: temporal
QA, belief-state tracking, RAG evaluation]. I request that [any conflicted
parties, or "no one"] be excluded.

Thank you for your consideration.

Sincerely,
Geunsik Lim, Sungkyunkwan University — leemgs@g.skku.edu

---

## Version B — presubmission enquiry (current bounded evidence)

Dear Editor,

I am writing to ask whether the enclosed work would be of interest to *Nature
Machine Intelligence*, and if so under which article type.

The manuscript introduces **situation engineering**: the claim that evidence
*applicability* (whether a well-supported fact holds for the query's time,
scope, observer and possible world) is a distinct, measurable target that
retrieval- and prompt-based evaluation does not isolate. It contributes a formal
failure class ("situation blindness"), a released diagnostic suite
(SituationCatch-Bench, 4,200 items over seven applicability axes), an executable
reference system with matched ablations, and a set of audited, deliberately
bounded language-model studies.

I want to be transparent about the evidence boundary. The controlled results
are a conformance suite co-designed with the solver. The language-model studies
cover nine models from seven developers, largely pre-registered, and they
are **null for the prompt intervention**: an explicit situation-state
prompt never detectably beats a matched structured prompt, nor chain-of-thought
or self-reflection prompts. The positive signal is consistent across settings:
the applicability variable itself is decisive. Removing timestamps from
otherwise identical evidence collapses accuracy on time-dependent items for
every developer, and on 597 independently written SituatedQA questions, adding
the date or the location raises accuracy by 22–41 points, whereas the date has
no detectable effect on control items whose undated reading already has the
same answer.
Language-model sensors close most of a rule-based sensor's gap (65.7% to
79–87%) but not for information the text does not contain. Human annotation,
proprietary families beyond Gemini and natural text for the five remaining
categories are not yet completed and are stated as limitations.

The work received no funding; every new study used zero-cost model endpoints,
and all code, data, pre-registrations and item-level outputs are openly
released and reproducible with single commands.

Given this, I would value your guidance on whether NMI would consider the work
as an **Analysis** on a missing evaluation axis, or would prefer the human
annotation completed first for an Article. I would rather calibrate the framing
to your editorial expectations than over-claim.

Thank you for your time.

Sincerely,
Geunsik Lim, Sungkyunkwan University — leemgs@g.skku.edu

### Summary for the enquiry form (≤200 words)

AI systems can retrieve a well-supported fact yet apply it to the wrong time,
place, observer or possible world. We call this failure situation blindness and
propose situation engineering: constructing the query-relative state that
decides whether evidence applies. We release SituationCatch-Bench (4,200 items,
seven applicability categories) and a reference system that satisfies every
invariant under oracle states (100%), falls to 66.5% with text-inferred states
and 45.1% under corruption, and whose seven ablations each fail only their own
category. Across nine language models from seven developers, including
pre-registered replications, prompting for an explicit situation state never
detectably beats structured, chain-of-thought or self-reflection prompting.
Instead, the applicability variable itself decides: identical evidence without
timestamps fails on time-dependent items, and on 597 natural SituatedQA
questions, adding the date or location raises accuracy by 22–41 points.
Language-model sensors recover most cues a rule-based sensor misses, but not
information absent from the text. The contribution is an executable evaluation
axis and a bounded, partly null empirical record, not a superior method; human
annotation and natural text for five further categories remain open.
