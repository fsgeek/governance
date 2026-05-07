# Rashomon Prototype Wedge

Smallest concrete starting cut of the Rashomon-routed governance prototype.

**Spec:** `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md`
**Plan:** `docs/superpowers/plans/2026-05-07-rashomon-prototype-wedge.md`

## What this tests

The primary hypothesis: among outcome-agreers in R(ε), factor-support
varies non-trivially across models. Same outcome reached via different
feature paths.

Falsification: if pairwise Jaccard overlap among outcome-agreers is
consistently high (median > 0.7), the methodology's distinction between
outcome agreement and reasoning agreement collapses.

## Layout

- `types.py` — Case, PerModelOutput, FactorSupportEntry dataclasses
- `collectors/lendingclub.py` — LendingClub real-data loader
- `collectors/synthetic.py` — boundary-extending synthetic generator
- `models.py` — CART wrapper with T/F leaf-purity emission
- `attribution.py` — path walk, per-component split attribution
- `rashomon.py` — hyperparameter sweep, ε filter, diversity-weighted selection
- `metrics.py` — outcome-agreer detection, Jaccard overlap
- `output.py` — jsonl writer with metadata sidecar
- `run.py` — CLI orchestration
- `notebooks/inspection.ipynb` — interactive analysis
- `tests/` — unit tests; run with `pytest wedge/tests/`

## How to run

```bash
# 1. Place a LendingClub CSV at <path>. The wedge expects the standard
#    LendingClub schema with at least: issue_d, term, loan_status,
#    fico_range_low, dti, annual_inc, emp_length.
python -m wedge.run \
    --csv <path-to-lc.csv> \
    --vintage 2015Q3 \
    --term '36 months' \
    --epsilon 0.02 \
    --n-members 5 \
    --top-k 5 \
    --synthetic-n 200 \
    --output-dir runs/

# 2. Open notebooks/inspection.ipynb, set RUN_JSONL to the produced jsonl,
#    run all cells. Hand-inspect the low-overlap and high-overlap tails.
```

## Limitations

Single dataset, single vintage, single model class, deferred I, partial
reject inference, demonstration-grade synthetic data only. See spec §12.

The validity bound on synthetic-collector output is *hypothetical-scenario*;
it cannot support back-testing or any claim that requires real-data outcomes.
