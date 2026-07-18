#!/usr/bin/env python3
"""Regenerate the main-text figures from results/*.csv.

Monochrome (print-safe) styling: grayscale fills plus hatch patterns so the
figures remain readable on black-and-white printers. Writes both PDF (used by
the LaTeX sources) and PNG previews into paper/figures/.

Usage: python3 code/make_figures.py   (run from the repository root)
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER_DIR = Path(__file__).resolve().parent.parent / "paper"
RESULTS = PAPER_DIR / "results"
FIGURES = PAPER_DIR / "figures"

plt.rcParams.update({
    "font.size": 9,
    "axes.edgecolor": "black",
    "savefig.bbox": "tight",
})

# Grayscale fill + hatch per method (legend order matches the manuscript).
METHOD_STYLE = {
    "Latest-mention": {"color": "white", "hatch": ""},
    "Lexical-RAG": {"color": "0.85", "hatch": "///"},
    "Recency-RAG": {"color": "0.55", "hatch": "..."},
    "SCQA": {"color": "0.25", "hatch": ""},
}
SINGLE_BAR = {"color": "0.6", "edgecolor": "black", "linewidth": 0.8}


def read_rows(name):
    with open(RESULTS / name, newline="") as fh:
        return list(csv.DictReader(fh))


def save(fig, stem):
    fig.savefig(FIGURES / f"{stem}.pdf")
    fig.savefig(FIGURES / f"{stem}.png", dpi=200)
    plt.close(fig)


def fig_accuracy():
    rows = read_rows("summary.csv")
    rows.sort(key=lambda r: float(r["accuracy"]))  # barh plots bottom-up
    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    ax.barh([r["method"] for r in rows], [float(r["accuracy"]) for r in rows],
            **SINGLE_BAR)
    ax.set_xlabel("Exact action-and-answer accuracy")
    ax.set_xlim(0, 1.05)
    save(fig, "accuracy")


def fig_by_category():
    rows = read_rows("by_category.csv")
    categories = [r["category"] for r in rows]
    methods = list(METHOD_STYLE)
    width = 0.2
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i, method in enumerate(methods):
        offsets = [x + (i - (len(methods) - 1) / 2) * width
                   for x in range(len(categories))]
        style = METHOD_STYLE[method]
        ax.bar(offsets, [float(r[method]) for r in rows], width,
               label=method, color=style["color"], hatch=style["hatch"],
               edgecolor="black", linewidth=0.6)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=20, ha="right")
    ax.set_xlabel("Situation category")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              fontsize=8, frameon=False)
    save(fig, "by_category")


def fig_ablations():
    rows = read_rows("ablations.csv")
    rows.sort(key=lambda r: (float(r["accuracy"]), r["ablation"]))
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    ax.barh([r["ablation"] for r in rows], [float(r["accuracy"]) for r in rows],
            **SINGLE_BAR)
    ax.set_xlabel("SCQA accuracy")
    ax.set_xlim(0, 1.05)
    save(fig, "ablations")


if __name__ == "__main__":
    fig_accuracy()
    fig_by_category()
    fig_ablations()
    print(f"Figures written to {FIGURES}")
