#!/usr/bin/env bash
# Assemble the files for the Nature Machine Intelligence submission system into
# dist/nmi_submission/ (git-ignored): PDFs, a self-contained LaTeX source archive
# (checked to compile on its own), the cover letter, the reporting-summary draft
# and a SHA-256 manifest. Run from the repository root: bash code/make_submission_bundle.sh
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=dist/nmi_submission
rm -rf "$OUT"; mkdir -p "$OUT"
(cd paper && ./run.sh >/dev/null)
python3 code/audit_submission.py >/dev/null

cp paper/main.pdf "$OUT/Lim_situation_engineering_main.pdf"
cp paper/supplementary.pdf "$OUT/Lim_situation_engineering_SI.pdf"
cp paper/COVER_LETTER.md "$OUT/cover_letter.md"
cp paper/REPORTING_SUMMARY_DRAFT.md "$OUT/reporting_summary_draft.md"

# LaTeX source: only what main.tex and supplementary.tex read.
SRC=$(mktemp -d); trap 'rm -rf "$SRC"' EXIT
mkdir -p "$SRC/src"
(cd paper && cp --parents main.tex supplementary.tex sn-jnl.cls run.sh \
   section/*.tex section/tables/*.tex supplementary/*.tex \
   figures/ablations.pdf figures/accuracy.pdf figures/by_category.pdf "$SRC/src/")
(cd "$SRC/src" && ./run.sh >/dev/null 2>&1) || { echo "source archive does not compile on its own"; exit 1; }
(cd "$SRC/src" && rm -f ./*.aux ./*.log ./*.out ./*.pdf ./*.toc && zip -qr "$OLDPWD/$OUT/Lim_situation_engineering_source.zip" .)

(cd "$OUT" && sha256sum ./* > MANIFEST.sha256)
echo "Wrote $OUT:"; ls -l "$OUT"
