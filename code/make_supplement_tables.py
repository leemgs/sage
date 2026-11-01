#!/usr/bin/env python3
"""Write the Supplementary Notes 2-4 tables from the diagnostic result CSVs.

Run after code/run_diagnostic.py (repository root):
    python code/make_supplement_tables.py
"""
import csv
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent / "paper"
RES, OUT = PAPER / "results", PAPER / "supplementary"


def rows(name):
    with open(RES / name, newline="") as fh:
        return list(csv.DictReader(fh))


def esc(text):
    return text.replace("_", r"\_")


def results_table():
    body = [f"{r['method']} & {float(r['accuracy']):.3f} & {float(r['SCHR']):.3f} & "
            f"{float(r['ECE']):.3f}\\\\" for r in rows("summary.csv")]
    return ("\\begin{table}[!ht]\\centering\\begin{tabular}{lrrr}\\toprule "
            "Method & Accuracy & SCHR & ECE\\\\\\midrule\n" + "\n".join(body) +
            "\n\\bottomrule\\end{tabular}\\end{table}\n")


def category_table():
    data = rows("by_category.csv")
    methods = [k for k in data[0] if k != "category"]
    lines = ["\\begin{tabular}{l" + "r" * len(methods) + "}", "\\toprule",
             "category & " + " & ".join(methods) + " \\\\", "\\midrule"]
    lines += [esc(r["category"]) + " & " +
              " & ".join(f"{float(r[m]):.3f}" for m in methods) + " \\\\" for r in data]
    return "\n".join(lines + ["\\bottomrule", "\\end{tabular}", ""])


def ablation_table():
    lines = ["\\begin{tabular}{lrr}", "\\toprule", "ablation & accuracy & errors \\\\",
             "\\midrule"]
    lines += [f"{r['ablation']} & {float(r['accuracy']):.3f} & {r['errors']} \\\\"
              for r in rows("ablations.csv")]
    return "\n".join(lines + ["\\bottomrule", "\\end{tabular}", ""])


if __name__ == "__main__":
    (OUT / "results_table.tex").write_text(results_table())
    (OUT / "category_table.tex").write_text(category_table())
    (OUT / "ablation_table.tex").write_text(ablation_table())
    print(f"Wrote supplementary tables to {OUT}")
