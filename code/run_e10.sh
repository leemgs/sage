#!/usr/bin/env bash
# Run (or resume) the pre-registered E10 stronger-baseline study (paper/PREREGISTRATION_E10.md).
# Free endpoints only; on the daily free quota the runner exits without writing a
# record; re-run later to continue.
set -u
cd "$(dirname "$0")/.."
R=paper/results/raw_e10
slug() { printf '%s' "${1##*/}" | tr '.:-' '___'; }
for M in nvidia/nemotron-3-ultra-550b-a55b:free dots-studio/dots-3-note-preview:free recursive/flint-v1.0:free; do
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" \
    --data paper/data/situationcatch_llm_sample.jsonl --out "$R/e10_$(slug "$M").jsonl" \
    --conditions chain_of_thought self_reflection --max-tokens 1024 --sleep 0.5 &
done
wait
echo "E10 finished or paused; re-run to continue."
