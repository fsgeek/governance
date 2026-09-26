#!/usr/bin/env bash
# Recompute every archive in its own vintage (noise floor) and in every later vintage (pre-reg dc12f1a §4;
# v2023p per amendment A1 is ordered at 2023 and compared with every vintage of a later year).
# Each cell is a fresh process in the contest vintage's env that reads only the archive directory.
set -u
cd "$(dirname "$0")/../.."
LABELS=(v2021 v2022 v2023 v2023p v2024 v2025 v2026)
year() { echo "${1:1:4}"; }
MAXJ=${MAXJ:-8}
for o in "${LABELS[@]}"; do
  [ -f runs/retention_drift/archive/$o/manifest.json ] || { echo "no archive $o"; continue; }
  for c in "${LABELS[@]}"; do
    oy=$(year $o); cy=$(year $c)
    if [ "$o" != "$c" ] && [ "$cy" -le "$oy" ]; then continue; fi
    out=runs/retention_drift/recompute/${o}_${c}
    [ -f $out/manifest.json ] && continue
    while [ "$(jobs -rp | wc -l)" -ge "$MAXJ" ]; do sleep 5; done
    OMP_NUM_THREADS=4 envs_rd/$c/bin/python scripts/retention_drift/explain.py recompute $c \
      runs/retention_drift/archive/$o $out > runs/retention_drift/logs/recompute_${o}_${c}.log 2>&1 &
  done
done
wait
echo ALL_RECOMPUTE_DONE
