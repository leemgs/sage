#!/usr/bin/env bash
# Run (or resume) the pre-registered E8 studies (paper/PREREGISTRATION_E8.md).
# Free endpoints only. When the daily free quota is reached the runner exits
# without writing a record; re-run this script later to continue.
# E8b needs a local clone of SituatedQA; see code/prepare_situatedqa_eval.py.
set -u
cd "$(dirname "$0")/.."
R=paper/results/raw_e8
slug() { printf '%s' "${1##*/}" | tr '.:-' '___'; }
run_e8a() {
  M="$1"; S=$(slug "$M")
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/situationcatch_llm_sample.jsonl \
    --out "$R/main/e8_$S.jsonl" --conditions direct structured situation --max-tokens 1024 --sleep 0.5 || return
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/situationcatch_rag_sample.jsonl \
    --out "$R/rag/e8_$S.jsonl" --conditions direct --max-tokens 1024 --sleep 0.5
}
run_e8b() {
  M="$1"; S=$(slug "$M")
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/local/situatedqa_e8.jsonl \
    --out "$R/nl_local/nl_$S.jsonl" --conditions direct date_context structured situation --max-tokens 1024 --sleep 0.5
}
A="nvidia/nemotron-3-ultra-550b-a55b:free dots-studio/dots-3-note-preview:free xingchen-agi/xing4.0-29b-a4b:free"
B="nvidia/nemotron-3-ultra-550b-a55b:free dots-studio/dots-3-note-preview:free"
case "${1:-a}" in
  a) for m in $A; do run_e8a "$m" & done; wait ;;
  b) for m in $B; do run_e8b "$m" & done; wait ;;
esac
echo "E8 stage ${1:-a} finished or paused; re-run to continue."
