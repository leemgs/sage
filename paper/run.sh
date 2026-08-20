#!/usr/bin/env bash
set -euo pipefail
# References are embedded with thebibliography, so three pdflatex passes resolve
# citations, cross-references, contents and PDF bookmarks without BibTeX.
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error supplementary.tex
pdflatex -interaction=nonstopmode -halt-on-error supplementary.tex
pdflatex -interaction=nonstopmode -halt-on-error supplementary.tex
