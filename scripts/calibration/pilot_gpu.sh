#!/usr/bin/env bash
# Codebook pilot under the ayllu GPU lease (plan §6). Run via:
#   ~/projects/hamutay/deploy/ayllu-gpu run --holder governance --purpose "calibration-study codebook pilot (Phi-4)" \
#       --ttl 3h -- scripts/calibration/pilot_gpu.sh
# Phi-4 Q5_K from microsoft/phi-4-gguf@6edc2ef6 (sha256 1cf76820e5b9..., checked against the repo's LFS oid).
set -euo pipefail
cd "$(dirname "$0")/../.."
MODEL=/home/tony/models/phi-4-gguf/phi-4-Q5_K.gguf
PORT=8090
LOG=runs/calibration/pilot/llama-server.log

/home/tony/src/llama.cpp/build/bin/llama-server -m "$MODEL" -ngl 99 -c 16384 -fa on --jinja \
    --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null; wait "$SERVER" 2>/dev/null || true' EXIT

for _ in $(seq 1 120); do
    curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break
    kill -0 "$SERVER" 2>/dev/null || { echo "llama-server exited; see $LOG" >&2; exit 1; }
    sleep 2
done
curl -sf "http://127.0.0.1:$PORT/health" >/dev/null

uv run python scripts/calibration/pilot_run.py code --url "http://127.0.0.1:$PORT"
