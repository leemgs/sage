#!/usr/bin/env python3
"""Desk-reject checks for the Nature Machine Intelligence manuscript (fails closed).

Checks the built PDFs and the LaTeX sources against the limits used for this
submission (Nature-family guidance; confirm on the journal site before submitting):
abstract <= 150 words; main text (Introduction to Discussion, excluding floats)
<= 3,500 words; Methods <= 3,000 words; <= 6 display items; <= 10 Extended Data
items; <= 50 references, all cited, numbered in order of first citation;
figure legends <= 350 words; no citation in the abstract; required statements
present; no unresolved references or placeholders in the PDFs; every Extended
Data table and Supplementary Note mentioned exists; no text outside the text
block on any page; no overfull boxes in the LaTeX logs.

Usage (after `cd paper && ./run.sh`): python code/check_desk_reject.py
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1] / "paper"
MAIN_SECTIONS = ["010_introduction_nmi", "015_situation_engineering", "025_results_ncs",
                 "026_results_e5", "060_discussion"]
REQUIRED = ["Data availability", "Code availability", "Author Contributions",
            "Competing Interests"]
TEXT_WIDTH = 370.6  # pt, measured text block of sn-jnl


def strip(tex, floats=True):
    tex = re.sub(r"(?m)(?<!\\)%.*$", "", tex)
    if floats:
        tex = re.sub(r"\\begin\{(table\*?|figure\*?)\}.*?\\end\{\1\}", "", tex, flags=re.S)
    tex = re.sub(r"\\(cite|ref|label|input)\{[^}]*\}", "", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?", "", tex)
    return re.sub(r"[{}$\\]", "", tex)


def words(tex, floats=True):
    return len(strip(tex, floats).split())


def expand(name):
    path = PAPER / (name if name.endswith(".tex") else name + ".tex")
    tex = re.sub(r"(?m)(?<!\\)%.*$", "", path.read_text())
    return re.sub(r"\\input\{([^}]+)\}", lambda m: expand(m.group(1).lstrip("./")), tex)


def pdf_lines(pdf):
    out = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    return out.split("<page ")[1:]


def main():
    res, fail = {}, []

    def check(name, value, ok):
        res[name] = value
        if not ok:
            fail.append(name)

    sec = {s: (PAPER / "section" / f"{s}.tex").read_text() for s in MAIN_SECTIONS}
    abstract = (PAPER / "section/006_abstract_nmi.tex").read_text()
    abstract = abstract[abstract.index("{%") + 2:abstract.index("\\keywords")].rsplit("}", 1)[0]
    check("abstract_words", words(abstract), words(abstract) <= 150)
    check("abstract_has_no_citation", "\\cite" not in abstract, "\\cite" not in abstract)
    main_words = sum(words(t) for t in sec.values())
    check("main_text_words", main_words, main_words <= 3500)
    methods = words((PAPER / "section/070_methods.tex").read_text())
    check("methods_words", methods, methods <= 3000)

    # Cross-check with texcount (text + headers), which tokenises differently.
    if subprocess.run(["which", "texcount"], capture_output=True).returncode == 0:
        def tc(files):
            out = subprocess.run(["texcount", "-nosub", "-total", *files], capture_output=True,
                                 text=True, cwd=PAPER).stdout
            return sum(int(n) for n in re.findall(r"Words in (?:text|headers): (\d+)", out))
        tc_main = tc([f"section/{s}.tex" for s in MAIN_SECTIONS])
        tc_methods = tc(["section/070_methods.tex"])
        check("texcount_main_text_words", tc_main, tc_main <= 3500)
        check("texcount_methods_words", tc_methods, tc_methods <= 3000)

    full = expand("main.tex")
    cut = full.index("\\section*{Extended Data}")
    body, ed = full[:cut], full[cut:]
    figs = len(re.findall(r"\\begin\{figure\*?\}", body))
    tabs = len(re.findall(r"\\begin\{table\*?\}", body))
    check("display_items", f"{figs} figures + {tabs} tables", figs + tabs <= 6)
    n_ed = len(re.findall(r"\\begin\{(?:table|figure)\*?\}", ed))
    check("extended_data_items", n_ed, n_ed <= 10)
    legends = [len(strip(c, False).split()) for c in
               re.findall(r"\\caption\{(.*?)\}\s*\\label\{fig", body, re.S)]
    check("figure_legend_words_max", max(legends), max(legends) <= 350)

    bib = re.findall(r"\\bibitem\{([^}]+)\}", (PAPER / "section/095_reference_nature.tex").read_text())
    cited = []
    for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", full):
        for k in (x.strip() for x in m.group(1).split(",")):
            if k not in cited:
                cited.append(k)
    check("references", len(bib), len(bib) <= 50)
    check("references_uncited", [k for k in bib if k not in cited], all(k in cited for k in bib))
    check("citations_missing_from_list", [k for k in cited if k not in bib], all(k in bib for k in cited))
    check("references_in_first_citation_order", cited == bib, cited == bib)

    main_tex = (PAPER / "main.tex").read_text()
    missing = [r for r in REQUIRED if f"\\section*{{{r}}}" not in main_tex]
    check("required_statements_missing", missing, not missing)
    ethics = (PAPER / "section/070_methods.tex").read_text()
    check("ethics_statement", "Ethics" in ethics, "Ethics" in ethics)

    for pdf in ("main.pdf", "supplementary.pdf"):
        text = subprocess.run(["pdftotext", str(PAPER / pdf), "-"], capture_output=True,
                              text=True, check=True).stdout
        bad = re.findall(r"\?\?|\bTODO\b|\bTBD\b|\bXXX\b|\[citation needed\]", text)
        check(f"{pdf}_placeholders", bad, not bad)
        outside = []
        for i, page in enumerate(pdf_lines(PAPER / pdf), 1):
            box = [(float(a), float(b)) for a, b in
                   re.findall(r'<line xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)"', page)]
            if box and max(b for _, b in box) - min(a for a, _ in box) > TEXT_WIDTH + 1:
                outside.append(i)
        check(f"{pdf}_pages_wider_than_text_block", outside, not outside)
        log = (PAPER / pdf.replace(".pdf", ".log")).read_text(errors="replace")
        n = log.count("Overfull \\hbox")
        check(f"{pdf}_overfull_hboxes", n, n == 0)
        if pdf == "main.pdf":
            main_text = text

    # Text inside figures must stay legible after scaling (Nature: 5-7 pt).
    widths = {}
    for m in re.finditer(r"\\includegraphics\[width=([\d.]*)\\linewidth\]\{([^}]+)\}", full):
        widths[m.group(2)] = float(m.group(1) or 1)
    smallest = {}
    for rel, frac in widths.items():
        pdf = PAPER / rel
        page_w = float(re.search(r"Page size:\s+([\d.]+) x", subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout).group(1))
        scale = frac * TEXT_WIDTH / page_w
        boxes = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True,
                               text=True, check=True).stdout
        heights = [float(b) - float(a) for a, b in
                   re.findall(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)"', boxes)]
        if heights:
            smallest[rel] = round(min(heights) / 1.2 * scale, 1)  # glyph box ~ 1.2 x font size
    # TikZ figures have no source image: measure the printed page that carries Fig. 1
    # (conservative: footnote-sized text on that page counts too).
    pages = subprocess.run(["pdftotext", "-layout", str(PAPER / "main.pdf"), "-"],
                           capture_output=True, text=True, check=True).stdout.split("\f")
    for number, page_text in enumerate(pages, 1):
        if re.search(r"\bFig\. 1\b", page_text) and "Failure" in page_text:
            box = subprocess.run(["pdftotext", "-bbox", "-f", str(number), "-l", str(number),
                                  str(PAPER / "main.pdf"), "-"], capture_output=True,
                                 text=True, check=True).stdout
            heights = [float(b) - float(a) for a, b in
                       re.findall(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)"', box)]
            smallest["Fig. 1 (TikZ, printed page)"] = round(min(heights) / 1.2, 1)
            break
    check("figure_text_min_printed_pt", smallest, len(smallest) == 4 and all(v >= 5.0 for v in smallest.values()))

    flat = " ".join(main_text.split())
    mentioned ={int(x) for m in re.finditer(r"Extended Data Tables? ((?:\d+(?:, | and |–))*\d+)", flat)
                 for x in re.findall(r"\d+", m.group(1))}
    check("extended_data_mentioned_but_absent", sorted(x for x in mentioned if x > n_ed),
          all(x <= n_ed for x in mentioned))
    supp = (PAPER / "supplementary.tex").read_text()
    notes = {int(x) for x in re.findall(r"\\section\*\{Supplementary Note (\d+)", supp)}
    refs = {int(x) for x in re.findall(r"Supplementary Notes?~?\s?(\d+)", "".join(
        (PAPER / "section" / f).read_text() for f in [*(s + ".tex" for s in MAIN_SECTIONS),
                                                       "070_methods.tex"]))}
    check("supplementary_notes_mentioned_but_absent", sorted(refs - notes), refs <= notes)

    print(json.dumps(res, indent=1, ensure_ascii=False))
    print("DESK-REJECT CHECK:", "PASS" if not fail else "FAIL " + ", ".join(fail))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
