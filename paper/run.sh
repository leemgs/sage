#!/usr/bin/env bash
set -euo pipefail
# References are embedded with thebibliography, so three pdflatex passes resolve
# citations, cross-references, contents and PDF bookmarks without BibTeX.
# Fixed timestamps and PDF ID make the build reproducible: the same sources give
# byte-identical PDFs, so SHA256SUMS.txt stays valid after a rebuild.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1794700800}"  # 2026-11-15 00:00 UTC
export FORCE_SOURCE_DATE=1
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{main.tex}"
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{main.tex}"
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{main.tex}"
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{supplementary.tex}"
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{supplementary.tex}"
pdflatex -interaction=nonstopmode -halt-on-error "\pdftrailerid{}\input{supplementary.tex}"
