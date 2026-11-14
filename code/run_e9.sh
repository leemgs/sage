#!/usr/bin/env bash
# Run (or resume) the pre-registered E9 geographic study (paper/PREREGISTRATION_E9.md).
# Free endpoints only; on the daily free quota the runner exits without writing
# a record; re-run this script later to continue. Needs the local sample from
# code/prepare_situatedqa_geo_eval.py.
set -u
cd "$(dirname "$0")/.."
R=paper/results/raw_e9/geo_local
slug() { printf '%s' "${1##*/}" | tr '.:-' '___'; }
for M in nvidia/nemotron-3-ultra-550b-a55b:free dots-studio/dots-3-note-preview:free; do
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" \
    --data paper/data/local/situatedqa_geo_e9.jsonl --out "$R/geo_$(slug "$M").jsonl" \
    --conditions direct location_context structured situation --max-tokens 1024 --sleep 0.5 &
done
wait
echo "E9 finished or paused; re-run to continue."
