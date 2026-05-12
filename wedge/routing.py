"""Within-tier disagreement as a routing signal (follow-on to #6).

Pre-registration: docs/superpowers/specs/2026-05-12-disagreement-routing-preregistration-note.md.

#6 (`wedge/refinement_set.py`) built, for one lender risk-tier, the epsilon-band
of policy-admissible *refinements* and showed it can be plural -- on the
load-bearing 2015H2 `dti` burst, grade B1's band members rank the tier's
borrowers with a median pairwise Spearman of ~0.17. This module asks whether that
disagreement *does* anything: given the band's distinct member models (each
fitted on its own feature subset) and a held-out quarter's loans for the tier,
it computes the *per-borrower* disagreement among members, the band's consensus
prediction, and the pre-registered routing metrics -- does disagreement localize
to the cases where the consensus is least reliable? If yes, "the set is plural"
becomes "the set tells you which cases need a human" (a SHAP-incapable function);
if no, the plurality carries no actionable routing information (a deflating, but
real, finding).

The slow data load and the per-grade band rebuilds live in
`scripts/disagreement_routing_test.py`; this module is pure metrics.
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score


# ---------------------------------------------------------------------------
# Member scores, disagreement, consensus
# ---------------------------------------------------------------------------
def member_score_matrix(predict_fns: list[Callable[[np.ndarray], np.ndarray]],
                        X: np.ndarray) -> np.ndarray:
    """Stack each member's predicted-default scores into an (n_members, n_rows)
    matrix. `predict_fns[i](X)` must return P(default) for every row of `X`
    (the caller subsets `X` to the member's feature columns inside the closure)."""
    X = np.asarray(X, dtype=float)
    rows = [np.asarray(fn(X), dtype=float).ravel() for fn in predict_fns]
    if not rows:
        raise ValueError("no member predict functions")
    M = np.vstack(rows)
    if M.shape[1] != X.shape[0]:
        raise ValueError(f"member scores have {M.shape[1]} cols, expected {X.shape[0]} rows")
    return M


def per_borrower_disagreement(score_matrix: np.ndarray) -> np.ndarray:
    """`d(x)` = std (population, ddof=0) of the band members' predicted-default
    probabilities on `x`. One value per row (borrower). With a single member,
    disagreement is identically zero."""
    M = np.asarray(score_matrix, dtype=float)
    if M.ndim != 2 or M.shape[0] == 0:
        raise ValueError("score_matrix must be (n_members, n_rows) with >=1 member")
    if M.shape[0] == 1:
        return np.zeros(M.shape[1], dtype=float)
    return M.std(axis=0, ddof=0)


def consensus_scores(score_matrix: np.ndarray) -> np.ndarray:
    """`p_bar(x)` = mean of the band members' predicted-default probabilities."""
    M = np.asarray(score_matrix, dtype=float)
    if M.ndim != 2 or M.shape[0] == 0:
        raise ValueError("score_matrix must be (n_members, n_rows) with >=1 member")
    return M.mean(axis=0)


# ---------------------------------------------------------------------------
# Bucketing
# ---------------------------------------------------------------------------
def tercile_labels(values: np.ndarray) -> np.ndarray:
    """Assign each row to a tercile of `values`: 0 = low, 1 = middle, 2 = high.

    Rank-based so the three buckets are as equal-sized as integer division
    allows, even with heavy ties (ties broken by a stable sort, i.e. by original
    order). For n not divisible by 3 the low bucket gets the extra one or two."""
    v = np.asarray(values, dtype=float)
    n = v.size
    if n == 0:
        return np.empty(0, dtype=int)
    if n < 3:
        return np.zeros(n, dtype=int)
    order = np.argsort(v, kind="stable")
    rank = np.empty(n, dtype=int)
    rank[order] = np.arange(n)
    return np.minimum(rank * 3 // n, 2).astype(int)


def quantile_bin_labels(values: np.ndarray, n_bins: int) -> np.ndarray:
    """Rank-based `n_bins`-quantile bucket index in [0, n_bins-1] for each row of
    `values` (same equal-size-by-rank convention as `tercile_labels`)."""
    v = np.asarray(values, dtype=float)
    n = v.size
    if n == 0:
        return np.empty(0, dtype=int)
    nb = max(1, int(n_bins))
    if n < nb:
        nb = n
    order = np.argsort(v, kind="stable")
    rank = np.empty(n, dtype=int)
    rank[order] = np.arange(n)
    return np.minimum(rank * nb // n, nb - 1).astype(int)


# ---------------------------------------------------------------------------
# Metric 1: tercile predictability
# ---------------------------------------------------------------------------
def _safe_auc(y: np.ndarray, s: np.ndarray) -> Optional[float]:
    y = np.asarray(y)
    if y.size == 0 or y.min() == y.max():
        return None
    return float(roc_auc_score(y, np.asarray(s, dtype=float)))


def _shuffle_null_auc(y: np.ndarray, s: np.ndarray, *, n_perm: int, percentile: float,
                      rng_seed: int) -> Optional[float]:
    y = np.asarray(y)
    if y.size == 0 or y.min() == y.max():
        return None
    s = np.asarray(s, dtype=float)
    rng = np.random.default_rng(rng_seed)
    aucs = np.fromiter((roc_auc_score(rng.permutation(y), s) for _ in range(n_perm)),
                       dtype=float, count=n_perm)
    return float(np.percentile(aucs, percentile))


def within_tercile_member_auc(score_matrix: np.ndarray, y: np.ndarray,
                              terciles: np.ndarray, *, n_perm: int = 500,
                              percentile: float = 95, rng_seed: int = 0) -> dict:
    """Per disagreement-tercile: the mean over band members of that member's
    within-tercile AUC for realized default, and a grade-size-aware label-shuffle
    null (the `percentile`-th pct of the AUC distribution under permuting `y`
    within the tercile, scores held fixed -- score-vector-independent up to ties,
    so computed once per tercile off the first member).

    Returns {0|1|2: {"mean_member_auc", "null_pXX", "n", "n_default",
    "per_member_auc": [...]}}. A tercile with degenerate labels gets None AUCs.
    Routing-relevant pattern: mean_member_auc(low) > mean_member_auc(high), with
    low above its null and high weaker.
    """
    M = np.asarray(score_matrix, dtype=float)
    y = np.asarray(y)
    terc = np.asarray(terciles, dtype=int)
    out: dict = {}
    for t in (0, 1, 2):
        mask = terc == t
        yt = y[mask]
        n, ndef = int(mask.sum()), int(yt.sum()) if mask.any() else 0
        if not mask.any() or yt.size == 0 or yt.min() == yt.max():
            out[t] = {"mean_member_auc": None, f"null_p{int(percentile)}": None,
                      "n": n, "n_default": ndef, "per_member_auc": []}
            continue
        per_member = [_safe_auc(yt, M[i, mask]) for i in range(M.shape[0])]
        per_member = [a for a in per_member if a is not None]
        null = _shuffle_null_auc(yt, M[0, mask], n_perm=n_perm, percentile=percentile,
                                 rng_seed=rng_seed + 1000 * t)
        out[t] = {"mean_member_auc": float(np.mean(per_member)) if per_member else None,
                  f"null_p{int(percentile)}": None if null is None else round(null, 4),
                  "n": n, "n_default": ndef,
                  "per_member_auc": [round(a, 4) for a in per_member]}
    return out


# ---------------------------------------------------------------------------
# Metric 2: disagreement vs consensus calibration gap
# ---------------------------------------------------------------------------
def calibration_gap_vs_disagreement(disagreement: np.ndarray, consensus: np.ndarray,
                                    y: np.ndarray, *, n_bins: int = 10) -> dict:
    """Bin rows into `n_bins` quantile buckets of `disagreement`; per bucket the
    calibration gap `|mean(realized default) - mean(consensus)|`; report the
    Spearman correlation between (bucket index, gap). Routing-relevant if
    positive (the consensus is more miscalibrated where the band disagrees more).

    Returns {"spearman_rho", "spearman_p", "n_bins_used", "per_bin": [{"bin",
    "n", "mean_consensus", "mean_default", "abs_gap"}]}.
    """
    d = np.asarray(disagreement, dtype=float)
    p = np.asarray(consensus, dtype=float)
    y = np.asarray(y, dtype=float)
    bins = quantile_bin_labels(d, n_bins)
    rows = []
    for b in sorted(set(bins.tolist())):
        m = bins == b
        mc, md = float(p[m].mean()), float(y[m].mean())
        rows.append({"bin": int(b), "n": int(m.sum()), "mean_consensus": round(mc, 5),
                     "mean_default": round(md, 5), "abs_gap": round(abs(md - mc), 5)})
    if len(rows) < 3:
        return {"spearman_rho": None, "spearman_p": None, "n_bins_used": len(rows),
                "per_bin": rows}
    idx = np.array([r["bin"] for r in rows], dtype=float)
    gap = np.array([r["abs_gap"] for r in rows], dtype=float)
    rho, pval = spearmanr(idx, gap)
    return {"spearman_rho": None if np.isnan(rho) else round(float(rho), 4),
            "spearman_p": None if np.isnan(pval) else round(float(pval), 4),
            "n_bins_used": len(rows), "per_bin": rows}


# ---------------------------------------------------------------------------
# Metric 3: disagreement vs consensus Brier
# ---------------------------------------------------------------------------
def brier_by_tercile(consensus: np.ndarray, y: np.ndarray, terciles: np.ndarray) -> dict:
    """Per disagreement-tercile, the consensus Brier score mean((p_bar - y)^2),
    plus `high_minus_low`. Routing-relevant if positive (consensus is worse on
    the high-disagreement tercile)."""
    p = np.asarray(consensus, dtype=float)
    y = np.asarray(y, dtype=float)
    terc = np.asarray(terciles, dtype=int)
    per = {}
    for t in (0, 1, 2):
        m = terc == t
        per[t] = None if not m.any() else round(float(np.mean((p[m] - y[m]) ** 2)), 6)
    hi, lo = per[2], per[0]
    return {"brier_by_tercile": per,
            "high_minus_low": None if (hi is None or lo is None) else round(hi - lo, 6)}


# ---------------------------------------------------------------------------
# Metric 4: operational lift (routing the high-disagreement tercile to manual)
# ---------------------------------------------------------------------------
def ece(consensus: np.ndarray, y: np.ndarray, *, n_bins: int = 10) -> Optional[float]:
    """Expected calibration error: bin rows into `n_bins` quantile buckets of the
    consensus score, take `|mean(consensus) - mean(default)|` per bucket, average
    weighted by bucket size. None if there are no rows."""
    p = np.asarray(consensus, dtype=float)
    y = np.asarray(y, dtype=float)
    n = p.size
    if n == 0:
        return None
    bins = quantile_bin_labels(p, n_bins)
    err = 0.0
    for b in set(bins.tolist()):
        m = bins == b
        err += m.sum() / n * abs(float(p[m].mean()) - float(y[m].mean()))
    return float(err)


def operational_lift(consensus: np.ndarray, y: np.ndarray, terciles: np.ndarray,
                     *, n_bins: int = 10) -> dict:
    """Calibration error (`ece`) on all of the tier's held-out loans vs. on the
    low+middle disagreement terciles only (i.e. if the high-disagreement tercile
    is routed to manual review and removed from the auto-refined population).
    `lift = ece_all - ece_auto_kept`; routing-relevant if non-negative (routing
    out the high-disagreement cases tightens the auto-refined population's
    calibration). Also reports the count routed out."""
    p = np.asarray(consensus, dtype=float)
    y = np.asarray(y, dtype=float)
    terc = np.asarray(terciles, dtype=int)
    keep = terc != 2
    e_all = ece(p, y, n_bins=n_bins)
    e_keep = ece(p[keep], y[keep], n_bins=n_bins) if keep.any() else None
    lift = None if (e_all is None or e_keep is None) else round(e_all - e_keep, 6)
    return {"ece_all": None if e_all is None else round(e_all, 6),
            "ece_auto_kept": None if e_keep is None else round(e_keep, 6),
            "lift": lift, "n_total": int(p.size), "n_routed_out": int((~keep).sum())}


# ---------------------------------------------------------------------------
# Diagnostic: are the high-disagreement borrowers feature-space outliers?
# ---------------------------------------------------------------------------
def feature_space_outlierness(X_eval: np.ndarray, X_reference: np.ndarray,
                              terciles: np.ndarray) -> dict:
    """Mean Mahalanobis distance (under the *reference* tier's mean and
    covariance -- the data the band was fit on) of the eval rows in each
    disagreement-tercile. If the high-disagreement tercile sits much farther out
    than the low one, the routing signal is reading "the admissible models are
    extrapolating here" (extrapolation detection) rather than "interior-but-
    genuinely-ambiguous". Uses a pinv of the covariance for robustness.

    Returns {"mean_mahalanobis_by_tercile": {0,1,2: float}, "high_over_low": ratio}.
    """
    Xe = np.asarray(X_eval, dtype=float)
    Xr = np.asarray(X_reference, dtype=float)
    terc = np.asarray(terciles, dtype=int)
    mu = Xr.mean(axis=0)
    cov = np.cov(Xr, rowvar=False)
    cov = np.atleast_2d(cov)
    vi = np.linalg.pinv(cov)
    diff = Xe - mu
    md = np.einsum("ij,jk,ik->i", diff, vi, diff)
    md = np.sqrt(np.clip(md, 0.0, None))
    per = {}
    for t in (0, 1, 2):
        m = terc == t
        per[t] = None if not m.any() else round(float(md[m].mean()), 4)
    hi, lo = per[2], per[0]
    ratio = None if (hi is None or lo is None or lo == 0) else round(hi / lo, 3)
    return {"mean_mahalanobis_by_tercile": per, "high_over_low": ratio}


# ---------------------------------------------------------------------------
# Per-grade verdict roll-up
# ---------------------------------------------------------------------------
def grade_routing_verdict(*, metric1: dict, metric2: dict, metric3: dict,
                          metric4: dict) -> dict:
    """Collapse the four metrics for one grade into the pre-registered
    routing-relevant booleans:

      m1_routing : mean_member_auc(low) > mean_member_auc(high), with low above
                   its null and high <= its null OR < low (weaker)
      m2_routing : calibration-gap Spearman > 0
      m3_routing : Brier high - low > 0
      m4_lift_ok : operational lift >= 0

    Any metric whose inputs were degenerate is recorded as None (does not count
    either way in the aggregate)."""
    pkey = next((k for k in metric1.get(0, {}) if k.startswith("null_p")), "null_p95")
    lo, hi = metric1.get(0, {}), metric1.get(2, {})
    a_lo, a_hi = lo.get("mean_member_auc"), hi.get("mean_member_auc")
    n_lo, n_hi = lo.get(pkey), hi.get(pkey)
    if a_lo is None or a_hi is None or n_lo is None or n_hi is None:
        m1 = None
    else:
        m1 = bool(a_lo > a_hi and a_lo > n_lo and (a_hi <= n_hi or a_hi < a_lo))
    rho = metric2.get("spearman_rho")
    m2 = None if rho is None else bool(rho > 0)
    hml = metric3.get("high_minus_low")
    m3 = None if hml is None else bool(hml > 0)
    lift = metric4.get("lift")
    m4 = None if lift is None else bool(lift >= 0)
    return {"m1_tercile_predictability_routing": m1, "m2_calibration_gap_routing": m2,
            "m3_brier_routing": m3, "m4_operational_lift_nonneg": m4}
