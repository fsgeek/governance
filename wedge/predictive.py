"""Pure metrics for the within-tier forward-predictive test.

Pre-registration: docs/superpowers/specs/2026-05-12-within-tier-predictive-test-preregistration-note.md.

The test asks whether a within-grade refinement model fit on a Cat-2-(pricing)
burst's first quarter, frozen, predicts the burst's second quarter's within-grade
realized default above a label-shuffle null. The slow part (data load, per-grade
logistic fits, freeze-and-evaluate) lives in `scripts/within_tier_predictive_test.py`;
this module holds the shuffle-null AUC and the hit/miss classification.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def _safe_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """AUC, returning 0.5 when it is undefined (one class absent)."""
    y_true = np.asarray(y_true)
    if y_true.min() == y_true.max():
        return 0.5
    return float(roc_auc_score(y_true, scores))


def shuffle_null_auc(
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    n_perm: int,
    percentile: float,
    rng_seed: int,
) -> float:
    """The `percentile`-th percentile of the AUC distribution under permutation
    of `y_true`, with `scores` held fixed.

    This is the chance baseline for "does the frozen model's ranking beat
    random?" — and because it permutes the actual label vector, it respects the
    grade's size and class balance (a 300-loan grade has a much wider null band
    than an 8,000-loan one). Returns 0.5 if the labels are degenerate.
    """
    y_true = np.asarray(y_true)
    scores = np.asarray(scores, dtype=float)
    if y_true.size == 0 or y_true.min() == y_true.max():
        return 0.5
    rng = np.random.default_rng(rng_seed)
    aucs = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        aucs[i] = _safe_auc(rng.permutation(y_true), scores)
    return float(np.percentile(aucs, percentile))


def classify_hit(*, oos_auc: float, null_p95: float, floor: float) -> str:
    """Classify an out-of-sample within-grade AUC per the pre-registered rule.

    - HIT      : oos_auc > null_p95 AND oos_auc >= floor
    - NEAR-HIT : oos_auc > null_p95 but in [0.5, floor)
    - MISS     : oos_auc <= null_p95, or oos_auc < 0.5
    """
    if oos_auc < 0.5:
        return "MISS"
    if oos_auc <= null_p95:
        return "MISS"
    if oos_auc >= floor:
        return "HIT"
    return "NEAR-HIT"
