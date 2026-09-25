#!/usr/bin/env bash
# Recompute every archive in its own vintage (noise floor) and in every later vintage (pre-reg dc12f1a §4).
# Each cell is a fresh process in the contest vintage's env that reads only the archive directory.
set -u
cd "$(dirname "$0")/../.."
YEARS=(2021 2022 2023 2024 2025 2026)
MAXJ=${MAXJ:-8}
for o in "${YEARS[@]}"; do
  for c in "${YEARS[@]}"; do
    [ "$c" -lt "$o" ] && continue
    out=runs/retention_drift/recompute/v${o}_v${c}
    [ -f $out/manifest.json ] && continue
    while [ "$(jobs -rp | wc -l)" -ge "$MAXJ" ]; do sleep 5; done
    OMP_NUM_THREADS=4 envs_rd/v$c/bin/python scripts/retention_drift/explain.py recompute v$c \
      runs/retention_drift/archive/v$o $out > runs/retention_drift/logs/recompute_v${o}_v${c}.log 2>&1 &
  done
done
wait
echo ALL_RECOMPUTE_DONE
