#!/usr/bin/env node
// Build the one-page SAGE academic poster (A0 landscape) -> ppt/sage-poster.pptx
// Run from the repository root: node ppt/build_poster.js
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const LOGO = path.join(ROOT, "assets", "sage-logo.png");

// Sage Calm palette
const DARK = "2C3E44"; // near-black slate (text, dark cards)
const SLATE = "50808E"; // primary accent
const SAGE = "84B59F"; // secondary accent
const EUCA = "69A297"; // tertiary
const LIGHT = "EEF4F2"; // light sage tint for cards
const MUTED = "5B6B70"; // muted body text

const pres = new pptxgen();
pres.defineLayout({ name: "A0L", width: 46.8, height: 33.1 });
pres.layout = "A0L";

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

const F = "Arial";

// ---------------------------------------------------------------- header
slide.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: 46.8, h: 4.6, fill: { color: DARK }, line: { type: "none" },
});
slide.addImage({ path: LOGO, x: 0.9, y: 0.55, w: 3.5, h: 3.5 });
slide.addText("Situation Engineering for Evidence-Applicable Artificial Intelligence", {
  x: 4.9, y: 0.75, w: 40.9, h: 1.7, margin: 0,
  fontFace: F, fontSize: 66, bold: true, color: "FFFFFF",
});
slide.addText(
  "Situation blindness, SCQA and SituationCatch-Bench: a controlled diagnostic for whether available evidence actually applies",
  { x: 4.9, y: 2.45, w: 40.9, h: 0.9, margin: 0, fontFace: F, fontSize: 26, color: "CFE3DC" });
slide.addText([
  { text: "Geunsik Lim", options: { bold: true } },
  { text: "   ·   Sungkyunkwan University   ·   github.com/leemgs/sage", options: {} },
], { x: 4.9, y: 3.4, w: 40.9, h: 0.8, margin: 0, fontFace: F, fontSize: 24, color: "FFFFFF" });

// ---------------------------------------------------------------- helpers
const COLX = [1.0, 12.45, 23.9, 35.35]; // 4 columns
const CW = 10.45; // column width
const TOP = 5.5;

function sectionHeader(x, y, text) {
  slide.addText(text, {
    x, y, w: CW, h: 1.0, margin: 0, fontFace: F, fontSize: 32, bold: true, color: DARK,
  });
}

function card(x, y, w, h, fillColor) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.16,
    fill: { color: fillColor }, line: { type: "none" },
  });
}

// ================================================================ column 1
let x = COLX[0];
sectionHeader(x, TOP, "The problem: situation blindness");

card(x, TOP + 1.1, CW, 4.2, LIGHT);
slide.addText(
  "An answer supported by at least one available claim, yet inconsistent with the time, scope, modality, observer knowledge or possible world the query requires. The decisive evidence is already present — its applicability is wrong.",
  { x: x + 0.35, y: TOP + 1.4, w: CW - 0.7, h: 3.6, margin: 0, fontFace: F, fontSize: 22, color: DARK, valign: "top" });

const failures = [
  ["T", "Stale time", "names the resigned coordinator as the current one"],
  ["M", "Modality", "turns a proposal into a decision that was never made"],
  ["S", "Scope", "extends a local policy to the whole organization"],
  ["W", "Observer / world", "answers from facts the observer cannot know, or from the wrong (hypothetical) world"],
];
let fy = TOP + 6.0;
for (const [letter, label, desc] of failures) {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y: fy + 0.12, w: 0.95, h: 0.95, fill: { color: SLATE }, line: { type: "none" },
  });
  slide.addText(letter, {
    x, y: fy + 0.12, w: 0.95, h: 0.95, margin: 0, align: "center", valign: "middle",
    fontFace: F, fontSize: 28, bold: true, color: "FFFFFF",
  });
  slide.addText([
    { text: label + " — ", options: { bold: true, color: DARK } },
    { text: desc, options: { color: MUTED } },
  ], { x: x + 1.25, y: fy, w: CW - 1.25, h: 2.1, margin: 0, fontFace: F, fontSize: 21, valign: "top" });
  fy += 2.25;
}

card(x, fy + 0.4, CW, 3.6, LIGHT);
slide.addText("16.5%", {
  x: x + 0.35, y: fy + 0.65, w: 4.4, h: 3.1, margin: 0,
  fontFace: F, fontSize: 64, bold: true, color: SLATE, valign: "middle",
});
slide.addText(
  "of sampled NQ-Open questions depend on time or place, and updated evidence does not remove the gap (SituatedQA).",
  { x: x + 4.9, y: fy + 0.7, w: CW - 5.25, h: 3.0, margin: 0, fontFace: F, fontSize: 20, color: DARK, valign: "middle" });

card(x, fy + 4.5, CW, 2.5, DARK);
slide.addText("“Relevance is not applicability.”", {
  x: x + 0.3, y: fy + 4.5, w: CW - 0.6, h: 2.5, margin: 0, align: "center", valign: "middle",
  fontFace: F, fontSize: 30, italic: true, bold: true, color: "FFFFFF",
});
slide.addText(
  "Conventional factuality checks mark the supporting claim as true — while missing that it is true in the wrong situation.",
  { x, y: fy + 7.5, w: CW, h: 1.8, margin: 0, fontFace: F, fontSize: 20, color: MUTED });

// ================================================================ column 2
x = COLX[1];
sectionHeader(x, TOP, "Situation engineering: the interface");

card(x, TOP + 1.1, CW, 4.2, LIGHT);
slide.addText("S(q, E) = { A, V, T, P, M, K, W, U }", {
  x: x + 0.35, y: TOP + 1.35, w: CW - 0.7, h: 0.9, margin: 0,
  fontFace: "Courier New", fontSize: 26, bold: true, color: DARK,
});
slide.addText(
  "actors · events · valid time · scope · modality & source · observer knowledge · possible world · unresolved variables",
  { x: x + 0.35, y: TOP + 2.3, w: CW - 0.7, h: 1.0, margin: 0, fontFace: F, fontSize: 18, color: MUTED });
slide.addText("π(S) ∈ {Answer · Clarify · Retrieve · Abstain · Act}", {
  x: x + 0.35, y: TOP + 3.5, w: CW - 0.7, h: 0.9, margin: 0,
  fontFace: "Courier New", fontSize: 20, bold: true, color: SLATE,
});

// pipeline diagram (vertical)
const boxes = [
  "Query, evidence, memory and tools",
  "Situation sensing",
  "Provenance-linked candidate states",
  "Applicability validation",
  "Answer, retrieve, clarify or abstain",
];
const BW = 7.6, BH = 1.7, BX = x + 0.7, GAP = 1.05;
let by = TOP + 6.0;
const boxY = [];
for (let i = 0; i < boxes.length; i++) {
  boxY.push(by);
  const isLast = i === boxes.length - 1;
  card(BX, by, BW, BH, isLast ? SLATE : "FFFFFF");
  if (!isLast) {
    slide.addShape(pres.ShapeType.roundRect, {
      x: BX, y: by, w: BW, h: BH, rectRadius: 0.14,
      fill: { type: "none" }, line: { color: SLATE, width: 2.5 },
    });
  }
  slide.addText(boxes[i], {
    x: BX + 0.2, y: by, w: BW - 0.4, h: BH, margin: 0, align: "center", valign: "middle",
    fontFace: F, fontSize: 21, bold: true, color: isLast ? "FFFFFF" : DARK,
  });
  if (!isLast) {
    slide.addShape(pres.ShapeType.line, {
      x: BX + BW / 2, y: by + BH, w: 0, h: GAP,
      line: { color: DARK, width: 3, endArrowType: "triangle" },
    });
  }
  by += BH + GAP;
}
// dashed "missing variable" return arrow (validation -> sensing), right side
slide.addShape(pres.ShapeType.line, {
  x: BX + BW + 0.35, y: boxY[1] + BH / 2, w: 0, h: boxY[3] - boxY[1],
  line: { color: MUTED, width: 2.5, dashType: "dash",
          beginArrowType: "triangle", endArrowType: "none" },
});
slide.addText("missing variable", {
  x: BX + BW + 0.55, y: (boxY[1] + boxY[3]) / 2 - 0.4, w: 2.0, h: 1.6, margin: 0,
  fontFace: F, fontSize: 16, italic: true, color: MUTED, valign: "middle",
});

const opsY = by + 0.3;
card(x, opsY, CW, 3.6, LIGHT);
slide.addText([
  { text: "Six operations. ", options: { bold: true, color: DARK } },
  { text: "sensing · assembly · updating · validation · policy · observability.  ", options: { color: DARK } },
  { text: "The layer consumes retrieval, memory, tool and harness outputs and returns applicability decisions and unresolved-state signals — it replaces none of those disciplines.", options: { color: MUTED } },
], { x: x + 0.35, y: opsY + 0.3, w: CW - 0.7, h: 3.0, margin: 0, fontFace: F, fontSize: 20, valign: "top" });

// ================================================================ column 3
x = COLX[2];
sectionHeader(x, TOP, "SCQA & SituationCatch-Bench");

const tiles = [["4,200", "generated items"], ["7", "failure categories"], ["0", "learned parameters"]];
const TW = (CW - 0.6) / 3;
tiles.forEach(([num, label], i) => {
  const tx = x + i * (TW + 0.3);
  card(tx, TOP + 1.1, TW, 2.7, LIGHT);
  slide.addText(num, {
    x: tx, y: TOP + 1.25, w: TW, h: 1.4, margin: 0, align: "center",
    fontFace: F, fontSize: 44, bold: true, color: SLATE,
  });
  slide.addText(label, {
    x: tx + 0.1, y: TOP + 2.65, w: TW - 0.2, h: 1.0, margin: 0, align: "center",
    fontFace: F, fontSize: 17, color: MUTED,
  });
});

const cats = ["temporal", "hidden premise", "source conflict", "modality", "scope", "observer", "counterfactual"];
const chipW = (CW - 0.3) / 2, chipH = 0.95;
let cy = TOP + 4.3;
cats.forEach((c, i) => {
  const cx = x + (i % 2) * (chipW + 0.3);
  const rowY = cy + Math.floor(i / 2) * (chipH + 0.25);
  card(cx, rowY, chipW, chipH, i === 6 ? SAGE : "FFFFFF");
  if (i !== 6) {
    slide.addShape(pres.ShapeType.roundRect, {
      x: cx, y: rowY, w: chipW, h: chipH, rectRadius: 0.12,
      fill: { type: "none" }, line: { color: SAGE, width: 2 },
    });
  }
  slide.addText(c, {
    x: cx, y: rowY, w: chipW, h: chipH, margin: 0, align: "center", valign: "middle",
    fontFace: F, fontSize: 19, bold: true, color: i === 6 ? "FFFFFF" : DARK,
  });
});
cy = cy + 4 * (chipH + 0.25) + 0.35;

slide.addText("Oracle-state accuracy by method (%)", {
  x, y: cy, w: CW, h: 0.7, margin: 0, fontFace: F, fontSize: 22, bold: true, color: DARK,
});
slide.addChart(pres.ChartType.bar, [{
  name: "Exact action-and-answer accuracy",
  labels: ["Lexical-RAG", "Recency-RAG", "Latest-mention", "SCQA"],
  values: [70.0, 71.4, 85.7, 100.0],
}], {
  x, y: cy + 0.8, w: CW, h: 5.6, barDir: "bar",
  chartColors: [SLATE], showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 16,
  dataLabelFormatCode: "0.0",
  dataLabelColor: DARK, dataLabelFontFace: F,
  catAxisLabelFontSize: 17, catAxisLabelColor: DARK, catAxisLabelFontFace: F,
  valAxisLabelFontSize: 14, valAxisLabelColor: MUTED, valAxisLabelFontFace: F,
  valAxisMaxVal: 100, valAxisMinVal: 0,
  valGridLine: { color: "DDE7E4", size: 1 }, catGridLine: { style: "none" },
});

const abY = cy + 6.7;
card(x, abY, CW, 4.4, LIGHT);
slide.addText([
  { text: "Causal ablations. ", options: { bold: true, color: DARK } },
  { text: "Removing one state variable selectively damages exactly its matching category (time → 93.5%, modality / scope / observer / missing → 85.7%). Behaviour changes because the specific required variable disappears — not because of a generic instruction to be cautious. Benchmark and solver share one schema, so results are a protocol conformance suite, not natural-language performance.", options: { color: MUTED } },
], { x: x + 0.35, y: abY + 0.3, w: CW - 0.7, h: 3.8, margin: 0, fontFace: F, fontSize: 20, valign: "top" });

// ================================================================ column 4
x = COLX[3];
sectionHeader(x, TOP, "Results: sensing is the bottleneck");

const nums = [["100.0%", "gold state", SAGE], ["77.9%", "predicted state", SLATE], ["35.1%", "corrupted state", DARK]];
nums.forEach(([num, label, color], i) => {
  const tx = x + i * (TW + 0.3);
  card(tx, TOP + 1.1, TW, 2.7, LIGHT);
  slide.addText(num, {
    x: tx, y: TOP + 1.25, w: TW, h: 1.4, margin: 0, align: "center",
    fontFace: F, fontSize: 34, bold: true, color,
  });
  slide.addText(label, {
    x: tx + 0.1, y: TOP + 2.65, w: TW - 0.2, h: 1.0, margin: 0, align: "center",
    fontFace: F, fontSize: 17, color: MUTED,
  });
});

slide.addChart(pres.ChartType.bar, [{
  name: "Accuracy under state conditions",
  labels: ["Gold", "Predicted", "Corrupted"],
  values: [100.0, 77.9, 35.1],
}], {
  x, y: TOP + 4.3, w: CW, h: 5.2, barDir: "col",
  chartColors: [SAGE, SLATE, DARK], chartColorsOpacity: 100,
  showLegend: false, showTitle: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 17,
  dataLabelFormatCode: "0.0", dataLabelColor: DARK, dataLabelFontFace: F,
  catAxisLabelFontSize: 17, catAxisLabelColor: DARK, catAxisLabelFontFace: F,
  valAxisLabelFontSize: 14, valAxisLabelColor: MUTED, valAxisLabelFontFace: F,
  valAxisMaxVal: 100, valAxisMinVal: 0,
  valGridLine: { color: "DDE7E4", size: 1 }, catGridLine: { style: "none" },
  barGapWidthPct: 60,
});

const snY = TOP + 10.0;
card(x, snY, CW, 3.7, LIGHT);
slide.addText([
  { text: "Deterministic text sensor (claim level). ", options: { bold: true, color: DARK } },
  { text: "Time 0% · Validity 0% · Actor 30.8% · Scope 61.5% · Event 92.3% · Modality 100%. All 927 final errors are attributable to sensing; update and policy are exact under gold state.", options: { color: MUTED } },
], { x: x + 0.35, y: snY + 0.3, w: CW - 0.7, h: 3.1, margin: 0, fontFace: F, fontSize: 20, valign: "top" });

const elY = snY + 4.0;
slide.addText("Evidence ladder: established vs open", {
  x, y: elY, w: CW, h: 0.7, margin: 0, fontFace: F, fontSize: 22, bold: true, color: DARK,
});
const ladder = [
  ["E1", "Formal definition — failure class is testable", true],
  ["E2", "Oracle unit tests — invariants executable, causally separable", true],
  ["E3", "Natural prevalence — independent QA literature", true],
  ["E4", "Predicted-state control — sensing errors reduce accuracy", true],
  ["E5", "Multi-model intervention — harness released, run pending", false],
  ["E6", "Deployment / human study — not completed", false],
];
let ly = elY + 0.85;
for (const [tag, text, done] of ladder) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y: ly + 0.05, w: 1.0, h: 0.72, rectRadius: 0.1,
    fill: { color: done ? SAGE : "C9CFCE" }, line: { type: "none" },
  });
  slide.addText(tag, {
    x, y: ly + 0.05, w: 1.0, h: 0.72, margin: 0, align: "center", valign: "middle",
    fontFace: F, fontSize: 18, bold: true, color: done ? "FFFFFF" : DARK,
  });
  slide.addText(text, {
    x: x + 1.25, y: ly, w: CW - 1.25, h: 0.85, margin: 0, valign: "middle",
    fontFace: F, fontSize: 17, color: done ? DARK : MUTED,
  });
  ly += 0.92;
}

card(x, ly + 0.25, CW, 3.2, DARK);
slide.addText([
  { text: "Takeaway.  ", options: { bold: true, color: "FFFFFF" } },
  { text: "A falsifiable problem definition, a modular evaluation decomposition and a reproducible scaffold for measuring where sensing, state update, policy and generation fail.  ", options: { color: "E4EEEA" } },
  { text: "github.com/leemgs/sage", options: { bold: true, color: SAGE } },
], { x: x + 0.35, y: ly + 0.5, w: CW - 0.7, h: 2.6, margin: 0, fontFace: F, fontSize: 20, valign: "top" });

pres.writeFile({ fileName: path.join(__dirname, "sage-poster.pptx") })
  .then(() => console.log("Wrote ppt/sage-poster.pptx"));
