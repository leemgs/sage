# Human inter-annotator agreement (three volunteer annotators)

**Provenance: human annotations.** Three volunteer annotators, recruited by the author,
each completed one blinded packet of the 70-item stratified subset
(`paper/data/annotation_subset_70.jsonl`, 10 items per category) independently, using the
Excel workbooks from `code/annotation_workbooks.py` (query time shown, evidence as
readable lines, drop-down codebook values) and `paper/annotation_packets/ANNOTATOR_INSTRUCTIONS.md`.
The worked examples shown to annotators are not among the 70 items. Annotators were not
authors, received no compensation, and were asked not to discuss items or view the
manuscript or code; the author confirmed with annotator 2, whose labels match the
reference on every item, that the labels were their own judgement without AI tools,
the manuscript or the code. The author reports that institutional ethics review was not
required (exempt / not applicable). Names are not stored: files are `annotator_1..3.csv`.

**Data handling (before scoring).**
1. Returned workbooks were converted with `code/annotation_workbooks.py to-csv`
   (fixed columns restored from the original packets; ratings taken from the workbook).
2. Codebook rule applied mechanically: annotator 1 chose `action = ABSTAIN` but left
   `answer` blank on `modality-0422` and `temporal-0113`; the codebook says the answer
   repeats the action token, so `answer = ABSTAIN` was filled in.
3. Declared deviation from the pre-specified rule (complete packets only): annotator 1
   left `answer` blank on `source_conflict-0262` with `action = ANSWER`. That item is
   dropped from the `answer` slot only (69 items); every other slot uses all 70 items.

**Reproduce.**
```bash
python code/annotation_cli.py score --annotations paper/results/human_iaa \
  --out paper/results/human_iaa/agreement.json --provenance human_annotations \
  --missing answer:source_conflict-0262
python code/annotation_cli.py adjudicate --annotations paper/results/human_iaa \
  --out paper/results/human_iaa/disagreements.csv --missing answer:source_conflict-0262
python code/human_vs_reference.py --missing answer:source_conflict-0262   # descriptive
```

`disagreements.csv` lists every item and slot without unanimous agreement; it has not
been adjudicated. `vs_reference.json` (descriptive, not pre-specified) compares labels
with the reference labels implied by each item's generated state. Interpretation caveat:
the walkthrough given to annotators summarises which slot usually decides each category
and suggests default values for the others, so agreement with the reference partly
reflects these instructions.
