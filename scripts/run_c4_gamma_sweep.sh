#!/bin/bash
# C4 gamma-sweep launcher (frozen pre-reg c413ed9). Shards compute in parallel;
# the balanced panel needs all cells, so aggregation is a single merge pass.
# Primary: ps=0.85 holdout, 7 gammas x 8 seeds = 56 cells.
# Reproduction: ps=0.85 LEGACY (--no-holdout) at gamma=0.02, 8 cells (quantifies the A1 overfit).
set -e
cd "$(git rev-parse --show-toplevel)"
SHARDS=runs/c4-gamma-shards
mkdir -p "$SHARDS"
GAMMAS="0.0 0.005 0.01 0.02 0.04 0.08 0.15"
SEEDS="0 1 2 3 4 5 6 7"
MAXJOBS=48

launch() {  # $1=gamma $2=seed $3=tag $4=extra-flags
    PYTHONPATH=. python3 scripts/c4_gamma_sweep.py --shard-only --proxy 0.85 \
        --gammas "$1" --seeds-list "$2" --budget-maxgen 70 $4 \
        --out "$SHARDS/${3}_g${1}_s${2}.json" > "$SHARDS/${3}_g${1}_s${2}.log" 2>&1
}

t0=$SECONDS
for g in $GAMMAS; do for s in $SEEDS; do
    launch "$g" "$s" h "" &
    while [ "$(jobs -r | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
done; done
for s in $SEEDS; do
    launch 0.02 "$s" L "--no-holdout" &
    while [ "$(jobs -r | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
done
wait
echo "compute done in $((SECONDS - t0))s; merging..."

PYTHONPATH=. python3 scripts/c4_gamma_sweep.py --merge "$SHARDS/h_g*.json" \
    --proxy 0.85 --seeds 8 --out runs/c4_gamma_sweep_ps085.json
PYTHONPATH=. python3 scripts/c4_gamma_sweep.py --merge "$SHARDS/L_g*.json" \
    --proxy 0.85 --seeds 8 --gammas 0.02 --out runs/c4_gamma_sweep_ps085_legacy.json
echo "ALLDONE"
