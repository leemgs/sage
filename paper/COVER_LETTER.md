# Cover letter — draft

Two versions are provided. Use **A** for a full Article submission only if the
Tier-1 confirmatory experiments (see `NMI_SUBMISSION_ASSESSMENT.md` §6) are done;
use **B** for a presubmission enquiry / Perspective route with the current bounded
evidence. Fill in bracketed fields. Do not include any AI-model identifier.

---

## Version A — full submission (after Tier-1 experiments)

Dear Editor,

We submit our manuscript, **"Situation engineering: separating evidence
applicability from availability in AI systems,"** for consideration as an Article
in *Nature Machine Intelligence*.

AI systems increasingly answer from retrieved documents, tools and memory, yet a
distinct failure persists: a system retrieves a well-supported fact and applies
it to the wrong time, scope, epistemic state or possible world. We name this
failure **situation blindness** and separate two properties that current
evaluation conflates — whether evidence is *available* versus whether it is
*applicable* to the query now. We formalise the query-relative state that governs
applicability, release **SituationCatch-Bench** (4,200 diagnostic items across
seven applicability axes) and a deterministic reference system, and — crucially —
show across [N] model families and [M] independently-authored natural benchmarks
that the operative bottleneck is *applicability sensing*, not retrieval relevance
or the presence of a situation prompt.

The advance is threefold: (i) a testable failure class and a systems-level
applicability interface distinct from prompt, context, retrieval, memory and
harness engineering; (ii) an executable, ablatable diagnostic that localises
failures to sensing, update, policy or generation; and (iii) evidence that a
prompt-level "situation" field is not situation awareness — the gains appear only
where applicability, not similarity, decides the answer. We believe this reframes
how the community should evaluate evidence-grounded and agentic systems, and is
of broad interest to readers working on hallucination, RAG and agents.

All code, data, frozen manifests and item-level outputs are released under an MIT
licence and archived at [DOI]. The work has not been published elsewhere and is
not under consideration by another journal. The author declares no competing
interests. We suggest as potential reviewers: [names/areas: temporal QA,
belief-state tracking, RAG evaluation]. We request that [any conflicted parties]
be excluded.

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
neural pilot.

I want to be transparent about the evidence boundary up front. The controlled
results are a conformance suite co-designed with the solver, and the neural pilot
is single-family (Gemini, n = 210) and **null-to-negative**: prompting for an
explicit situation state does not beat a matched structured prompt and trails
focused retrieval overall. The scientifically useful signal is that accuracy
collapses once the state must be *sensed* from text (100% → 77.9%), consistent
with *sensing*, not a prompt slot, being the bottleneck. A multi-family,
natural-benchmark, human-annotated confirmation is specified but not yet run.

Given this, I would value your guidance on whether NMI would consider the work as
a **Perspective/Analysis** on a missing evaluation axis, or whether you would
prefer the confirmatory experiments completed first for an Article. I would
rather calibrate the framing to your editorial expectations than over-claim.

All materials are openly released and reproducible with a single command.

Thank you for your time.

Sincerely,
Geunsik Lim, Sungkyunkwan University — leemgs@g.skku.edu
