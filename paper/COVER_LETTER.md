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

I report the neural evidence as it stands. Across six models from four
families (three Gemini models and a pre-registered replication with Meta,
DeepSeek and Qwen models, n = 210 each), prompting for an explicit situation
state does not beat a matched structured prompt under the pre-registered
decision rule, whereas giving the same claims without timestamps collapses
accuracy on time-dependent items in every family. A second pre-registered study
shows that language-model sensors recover most situation cues that a
rule-based sensor misses, but not information absent from the text. I present
the null result plainly because it supports the paper's point: a prompt-level
"situation" field is not situation awareness. Proprietary families beyond
Gemini, natural-text evaluation and human annotation are stated as limitations
and not claimed.

Code, data, generator and item-level outputs are openly available at
https://github.com/leemgs/sage under the MIT licence; an archival DOI will be
minted on acceptance. Use of generative AI tools is documented in Methods. The
work has not been published elsewhere and is not under consideration by another
journal. [If a preprint has been posted, state where.] The author declares no
competing interests. I suggest as potential reviewers: [names; areas: temporal
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
*applicability* — whether a supported fact holds for the query's time, scope,
observer and world *now* — is a distinct, measurable target that current
retrieval- and prompt-based evaluation does not isolate. I contribute a formal
failure class ("situation blindness"), a released diagnostic suite
(SituationCatch-Bench, 4,200 items over seven applicability axes), an executable
reference system with matched ablations, and an **audited, deliberately bounded**
neural studies.

I want to be transparent about the evidence boundary up front. The controlled
results are a conformance suite co-designed with the solver. The neural studies
cover six models from four families, partly pre-registered, and are
**null for the prompt intervention**: an explicit situation state never beats a
matched structured prompt. The useful signals are that evidence stripped of
timestamps fails on time-dependent items in every family, and that
language-model sensors close most of a rule-based sensor's gap (65.7% to
79–87%) but not for information the text does not contain. Natural-text and
human-annotated confirmation are specified but not yet run.

Given this, I would value your guidance on whether NMI would consider the work as
a **Perspective/Analysis** on a missing evaluation axis, or whether you would
prefer the confirmatory experiments completed first for an Article. I would
rather calibrate the framing to your editorial expectations than over-claim.

All materials are openly released and reproducible with a single command.

Thank you for your time.

Sincerely,
Geunsik Lim, Sungkyunkwan University — leemgs@g.skku.edu
