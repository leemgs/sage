#!/usr/bin/env bash
# Run (or resume) the pre-registered E6 and E7 studies; see
# paper/PREREGISTRATION_E6_E7.md (Amendment 1 sets the models).
# Needs OPENROUTER_API_KEY with about $2 of credit. Resumable: completed
# records are skipped, failed ones retried.
set -u
cd "$(dirname "$0")/.."
R=paper/results/raw_e6
run_model() {
  M="$1"; S=$(printf '%s' "${M##*/}" | tr '.-' '__')
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/situationcatch_llm_sample.jsonl \
    --out "$R/main/e5_$S.jsonl" --conditions direct structured situation --max-tokens 1024 --sleep 0.2
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/situationcatch_rag_sample.jsonl \
    --out "$R/rag/e5_$S.jsonl" --conditions direct --max-tokens 1024 --sleep 0.2
  python3 code/run_multimodel_eval.py --provider openrouter --model "$M" --data paper/data/situatedqa_temporal_sample.jsonl \
    --out "$R/nl/nl_$S.jsonl" --conditions direct structured situation --max-tokens 1024 --sleep 0.2
  python3 code/run_agent_eval.py --provider openrouter --model "$M" --out "$R/agent/agent_$S.jsonl" --sleep 0.2
}
run_sensor() {
  M="$1"; S=$(printf '%s' "${M##*/}" | tr '.-' '__')
  python3 code/run_llm_sensor.py --model "$M" --out "paper/results/raw_sensor/sensor_$S.jsonl"
}
for m in meta-llama/llama-4-maverick deepseek/deepseek-v4.1-flash qwen/qwen3.8-flash; do run_model "$m" & done
for m in meta-llama/llama-4-maverick deepseek/deepseek-v4.1-flash qwen/qwen3.8-flash google/gemini-2.5-flash; do run_sensor "$m" & done
wait
echo "E6/E7 runs finished; re-run this script to retry any failed calls."
