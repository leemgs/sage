# Nature Machine Intelligence — submission-readiness assessment

Co-author review of the current manuscript (branch `claude/paper-references-nmi-submission-avazrf`).
This is an internal working document, not part of the submission package.

---

## 1. One-line verdict

**Not yet submittable to *Nature Machine Intelligence* (NMI) as a research
Article.** The manuscript is honest, well-scaffolded and reproducible, but its
strongest empirical result is (a) on a benchmark co-designed with the solver and
(b) a *null-to-negative* neural finding on a **single** model family (Gemini,
n = 210). That combination will very likely be **desk-rejected** at NMI, whose
Articles need a novel, externally-valid, positively-demonstrated advance. The
manuscript's own go/no-go note (`REVIEWER_READINESS.md`) reaches the same
conclusion — "does **not** satisfy the stronger empirical claim of a broadly
validated neural intervention."

This is a *positioning and evidence* gap, not a quality gap. The writing,
transparency and reproducibility are already at or above journal standard.

---

## 2. How NMI actually evaluates a submission

NMI desk-rejects the large majority of submissions before review. The editorial
filter is roughly:

1. **Advance in machine intelligence** — a new capability, method or
   understanding, not primarily a re-framing of known ideas.
2. **Evidence that supports the claims** — results that are strong, novel and
   *externally valid* (generalise beyond the authors' own artefact).
3. **Breadth of interest** — matters to the wider ML community, not one niche.
4. **Rigor and reproducibility** — increasingly a *necessary* but never a
   *sufficient* condition.

The current manuscript scores well on (1-conceptual), (3) and (4), and honestly
concedes it does not yet meet (2).

| NMI criterion | Current manuscript | Gap to close |
|---|---|---|
| Conceptual novelty | Strong — "situation blindness", evidence *applicability* vs *availability*, the situation-engineering interface | Framing risk: reviewers in belief-revision / temporal-QA / dialogue-state may see it as re-packaging (the paper pre-empts this in Related work, but a positive empirical hook is what disarms it) |
| Empirical advance | Weak — synthetic conformance suite (100→77.9→35.1%) + a **null** Gemini pilot | The decisive missing piece. Needs a *positive*, generalising result |
| External validity | Low — one synthetic generator, one model family, no human data | Multi-family + independent natural benchmark + human IAA |
| Breadth of interest | Good — evidence use / hallucination / agents are central topics | Preserved once the result generalises |
| Rigor / reproducibility | Excellent — one-command runs, frozen manifests, integrity audits, honest limitations | Already a strength; keep it |

---

## 3. What is genuinely strong (keep and lead with)

- **A crisp, teachable thesis**: *relevance is not applicability*. This is the
  paper's best asset and should headline the title, abstract and cover letter.
- **The evidence ladder (E1–E6)** is exemplary scientific hygiene and exactly
  the kind of honesty NMI editors respond well to.
- **The sensing bottleneck finding** — accuracy collapses (100→77.9%) once the
  state must be *sensed* from text rather than supplied, and the null prompt
  result is consistent with sensing (not a prompt slot) being the real
  bottleneck. This is a real, defensible, interesting claim. It is currently
  *under-sold* relative to the framework material.
- **Reproducibility infrastructure**: fail-closed audits, no fabricated LLM/human
  numbers, synthetic-persona runs explicitly excluded. This is rare and valuable.

## 4. What blocks acceptance (in priority order)

1. **No positive, generalising empirical result.** The neural evidence is one
   family and null-to-negative. NMI will not run a bounded-null single-family
   pilot as a primary Article.
2. **Benchmark–solver circularity.** The headline controlled numbers are unit
   tests of a co-designed schema. Honest, but not an external finding.
3. **No human evaluation / IAA.** Only simulated personas exist (correctly
   excluded). NMI expects real agreement data for any human-facing claim.
4. **Single author on a "reliable AI" framing.** Not disqualifying, but the
   scope/evidence/authorship mismatch amplifies desk-rejection risk.
5. **Model-identity verification.** `gemini-3.5-flash` appears in the manifest,
   raw responses and tables. **Confirm this is a real, dated provider snapshot**
   with archived API metadata before submission — an unverifiable model name is
   the single fastest path to a reject-with-integrity-concern.
6. **Title/claim hygiene** (partially fixed in this revision): the previous
   title implied a delivered "reliability" improvement the data do not show.

---

## 5. Three strategic options

### Option A — Reposition now, submit to a *fitting* venue (fastest)
Submit the manuscript **as-is (with the honest bounded framing)** but not to NMI
as an Article. Realistic homes for a rigorous framework + conformance-suite +
honest null pilot:
- **NMI as a *Perspective/Analysis*** (reframed away from "we validated X" toward
  "here is a missing evaluation axis and why current interventions miss it").
  Still a high bar and often editor-invited, but the honest-null becomes a
  *feature*, not a defect. Consider a **presubmission enquiry** first.
- **TMLR** (Transactions on Machine Learning Research) — explicitly rewards
  correctness and clarity over positive-result novelty; a null, well-audited
  result is publishable. Strong fit, fast, no impact-factor gatekeeping.
- **A top NLP/ML venue** (ACL/EMNLP/NeurIPS D&B track) — the benchmark +
  diagnostic framing lands well; the D&B track values exactly this artefact.

### Option B — Do the confirmatory experiments, then target NMI (highest ceiling)
Execute the multi-family + natural-benchmark + human-IAA program in §6. If the
*sensing-bottleneck* result holds across families and on an independent natural
benchmark, the paper becomes a genuine NMI Article candidate — the story flips
from "prompting doesn't help" to "we localise *why* evidence-grounded systems
still err, and show the bottleneck is applicability sensing, not retrieval or
prompting." That is a positive, general, high-interest result.

### Option C — Presubmission enquiry to NMI now (cheap information)
Send the editor a 1-paragraph enquiry with the honest framing and ask whether
they would consider it as a Perspective/Analysis or want the confirmatory
experiments first. Costs a week, saves a likely desk-reject and tells you which
of A/B to pursue. **Recommended as the immediate next step, in parallel with
starting the Option-B experiments.**

**Recommendation:** run **C now**, start **B in parallel**, and keep **A** (TMLR /
D&B track) as the guaranteed-publication fallback so the work is never stranded.

---

## 6. Experimental roadmap — what turns this into an NMI Article

Ordered by *evidence unlocked per unit effort*. Each item lists what claim it
promotes on the E1–E6 ladder.

### Tier 1 — closes the fatal gaps (required for any NMI Article attempt)
1. **Cross-family confirmation of the sensing bottleneck (E5→E5✓).**
   Repeat the n=210 matched protocol on ≥2 proprietary + ≥2 open-weight families
   (e.g. GPT, Claude, Gemini, Llama/Qwen). Pre-register the primary contrast
   (*same model + same evidence + same budget*, situation off vs on) and the
   direction. Even if still null on *prompting*, a **consistent cross-family
   sensing collapse** is the positive result.
2. **Independent natural benchmark with frozen scoring (E4/E5→real).**
   Move beyond the 12-item SituatedQA smoke test to a full evaluation on ≥1
   independently-authored benchmark (SituatedQA / FreshQA / ChronoQA / TimeQA),
   with frozen item inclusion and a scoring script. This is what breaks the
   circularity objection.
3. **Real human inter-annotator agreement (E6 partial).**
   Recruit ≥3 independent annotators, blinded to method, on a natural sample.
   Report Fleiss' κ on state slots + action + answer, with an ethics
   exemption/approval statement. The blinded-packet pipeline already exists —
   it just needs real annotators. Replace the simulated-persona placeholder.

### Tier 2 — strengthens the mechanism story (raises the ceiling)
4. **Learned situation sensor.** Add a trained/LLM-based sensor (not only the
   rule sensor) and repeat gold/predicted/corrupted-state comparison. Shows the
   bottleneck is not an artefact of a weak deterministic parser.
5. **Stronger, matched baselines.** Add temporal/event-aware RAG,
   self-consistency, self-refinement/Self-RAG, and a verification agent under
   *matched* token/latency/cost budgets. The current top-3 lexical RAG and
   single agent are honest but easy to attack as weak comparators.
6. **Full cost/selective-risk reporting per condition.** Latency, input/output
   tokens, retrieval/tool calls, monetary cost, clarification overhead,
   risk–coverage. Ties the accuracy story to the efficiency story NMI expects.

### Tier 3 — external validity and durability
7. **OOD / compositional splits** at scenario-grammar level; longer event chains,
   nested scope, multiple observers, multilingual items, adversarial stale
   evidence.
8. **Archival deposit + DOI.** Deposit the MIT-licensed code/data (Zenodo — the
   `.zenodo.json` is already staged) and cite the minted DOI. Do **not** print a
   placeholder DOI until it is actually minted.
9. **Optional deployment probe.** State drift, invalidation latency, recovery
   after contradiction — only if pursuing the agent-safety angle.

---

## 7. Manuscript edits already applied in this revision (no new data)

- **Title de-risked** in `section/001_title.tex`, `main.tex` (`pdftitle`) and
  `supplementary.tex`: replaced "for reliable evidence use in artificial
  intelligence" / "is a missing layer for reliable artificial intelligence" with
  the demonstrated claim, "separating evidence applicability from availability in
  AI systems." Also removes a main/supplementary title inconsistency. Reversible
  if Tier-1 experiments later justify a reliability claim.

## 8. Author-only actions before any submission (cannot be done in-repo)

- [ ] **Verify `gemini-3.5-flash`** is a real, dated snapshot; archive request
      metadata proving the calls were made (see §4.5).
- [ ] Confirm name, ORCID, correspondence email, affiliation exactly as they
      should appear.
- [ ] Obtain institutional/employer publication clearance if applicable.
- [ ] Confirm the no-funding / no-competing-interest declarations.
- [ ] Rebuild `main.pdf` and `supplementary.pdf` locally (`./run.sh`) after the
      title change — no `pdflatex` is available in this environment.
- [ ] Reconcile NMI's current word / display-item / reference limits against the
      compiled PDF and pick the manuscript type in the portal.
- [ ] Mint the Zenodo DOI and cite it in Data/Code availability.
- [ ] If pursuing NMI: send the presubmission enquiry (Option C) first.
