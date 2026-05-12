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
from sklearn.model_selection import KFold, cross_val_score
from sklearn.tree import DecisionTreeRegressor


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


# ===========================================================================
# Geometry of the disagreement: is d(x) a legible function of the features?
# (pre-reg: docs/superpowers/specs/2026-05-12-disagreement-geometry-preregistration-note.md)
#
# The disagreement-routing result deflated; the post-hoc reading was "d(x)
# tracks where the within-tier residual feature is active". These helpers test
# that as a falsifiable claim: explain d from the policy-named features (and
# from the extension features), find the dominant driver, classify where d
# concentrates, and check cross-tier consistency.
# ===========================================================================
def disagreement_explainer(d: np.ndarray, X: np.ndarray, feature_names: list[str], *,
                           max_depth: int = 3, min_samples_leaf: int = 50,
                           n_splits: int = 5, seed: int = 0) -> dict:
    """Fit a shallow regression CART predicting per-borrower disagreement `d`
    from the features `X` (aligned to `feature_names`). Report the out-of-fold
    R^2 (k-fold CV; the fraction of var(d) the features capture), and -- from a
    fit on all the data -- the root-split feature and the top-3 feature
    importances. Degenerate cases (n too small, d ~ constant) -> cv_r2 None.

    Returns {"cv_r2", "cv_r2_folds", "root_feature", "top_importances",
    "n", "n_features"}.
    """
    d = np.asarray(d, dtype=float).ravel()
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    names = list(feature_names)
    if n != d.size or p != len(names):
        raise ValueError("X / d / feature_names shape mismatch")
    base = {"n": int(n), "n_features": int(p), "root_feature": None,
            "top_importances": [], "cv_r2": None, "cv_r2_folds": []}
    if n < max(2 * n_splits, 20) or float(np.std(d)) < 1e-12:
        return base
    tree = DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples_leaf,
                                 random_state=seed)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = cross_val_score(tree, X, d, cv=kf, scoring="r2")
    full = DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples_leaf,
                                 random_state=seed).fit(X, d)
    t = full.tree_
    root_feat = names[int(t.feature[0])] if t.node_count > 0 and int(t.feature[0]) >= 0 else None
    imps = sorted(zip(names, (float(i) for i in full.feature_importances_)),
                  key=lambda kv: -kv[1])
    base.update({"cv_r2": round(float(np.mean(folds)), 4),
                 "cv_r2_folds": [round(float(f), 4) for f in folds],
                 "root_feature": root_feat,
                 "top_importances": [(nm, round(im, 4)) for nm, im in imps[:3] if im > 0]})
    return base


def _decile_means(values: np.ndarray, d: np.ndarray, n_deciles: int = 10) -> np.ndarray:
    """Mean of `d` within each rank-quantile bucket of `values` (equal-sized,
    `quantile_bin_labels` convention)."""
    bins = quantile_bin_labels(np.asarray(values, dtype=float), n_deciles)
    d = np.asarray(d, dtype=float)
    out = []
    for b in range(int(bins.max()) + 1 if bins.size else 0):
        m = bins == b
        if m.any():
            out.append(float(d[m].mean()))
    return np.asarray(out, dtype=float)


def partial_dependence_profile(d: np.ndarray, feature_values: np.ndarray, *,
                               n_deciles: int = 10) -> dict:
    """Profile of mean disagreement `d` across deciles of one feature, plus a
    coarse shape label:

      flat      : the decile-mean spread is small relative to the overall level
      tails     : the max decile-mean sits in an end bucket and the larger tail
                  is >= 1.5x the middle-8 mean (U-shaped or one-tailed)
      threshold : the max sits in an interior bucket and is >= 1.3x the middle
                  mean (a bump -- candidate "near a policy threshold")
      monotone  : |Spearman(decile index, decile mean)| >= 0.8 and not flat
      mixed     : none of the above

    Returns {"decile_mean_d", "n_buckets", "shape", "tail_ratio", "argmax_bucket"}.
    """
    m = _decile_means(feature_values, d, n_deciles)
    if m.size < 3:
        return {"decile_mean_d": [round(float(x), 6) for x in m], "n_buckets": int(m.size),
                "shape": "flat", "tail_ratio": None, "argmax_bucket": None}
    overall = float(np.mean(m))
    spread = float(m.max() - m.min())
    mid = float(np.mean(m[1:-1])) if m.size >= 3 else overall
    tail = max(float(m[0]), float(m[-1]))
    tail_ratio = (tail / mid) if mid > 1e-12 else None
    argmax = int(np.argmax(m))
    end_buckets = {0, m.size - 1}
    idx = np.arange(m.size, dtype=float)
    rho_idx = spearmanr(idx, m).correlation
    monotone = rho_idx is not None and not np.isnan(rho_idx) and abs(rho_idx) >= 0.8
    if overall > 1e-12 and spread / overall < 0.20:
        shape = "flat"                                   # decile means barely move
    elif monotone:
        shape = "monotone"                               # one-sided ramp (incl. a single-tail rise)
    elif argmax in end_buckets and tail_ratio is not None and tail_ratio >= 1.5:
        shape = "tails"                                  # U-shape: both ends elevated, middle low
    elif (argmax not in end_buckets) and mid > 1e-12 and (float(m[argmax]) / mid) >= 1.3:
        shape = "threshold"                              # interior bump (candidate "near a policy threshold")
    else:
        shape = "mixed"
    return {"decile_mean_d": [round(float(x), 6) for x in m], "n_buckets": int(m.size),
            "shape": shape, "tail_ratio": None if tail_ratio is None else round(tail_ratio, 3),
            "argmax_bucket": argmax}


def univariate_disagreement_correlations(d: np.ndarray, X: np.ndarray,
                                         feature_names: list[str], *,
                                         n_deciles: int = 10) -> dict:
    """Per feature: Spearman of (feature value, `d`) with its p-value, the mean
    `d` in the feature's top and bottom decile, and the larger-tail / middle-8
    ratio. Returns {feature: {...}}."""
    d = np.asarray(d, dtype=float).ravel()
    X = np.asarray(X, dtype=float)
    out: dict = {}
    for j, nm in enumerate(feature_names):
        col = X[:, j]
        if float(np.std(col)) < 1e-12 or float(np.std(d)) < 1e-12:
            out[nm] = {"spearman_rho": None, "spearman_p": None, "mean_d_top_decile": None,
                       "mean_d_bottom_decile": None, "tail_over_mid": None}
            continue
        sr = spearmanr(col, d)
        m = _decile_means(col, d, n_deciles)
        mid = float(np.mean(m[1:-1])) if m.size >= 3 else float(np.mean(m))
        tail = max(float(m[0]), float(m[-1])) if m.size else None
        out[nm] = {"spearman_rho": None if np.isnan(sr.correlation) else round(float(sr.correlation), 4),
                   "spearman_p": None if np.isnan(sr.pvalue) else round(float(sr.pvalue), 4),
                   "mean_d_top_decile": round(float(m[-1]), 6) if m.size else None,
                   "mean_d_bottom_decile": round(float(m[0]), 6) if m.size else None,
                   "tail_over_mid": None if (tail is None or mid <= 1e-12) else round(tail / mid, 3)}
    return out


def threshold_proximity_correlation(d: np.ndarray, dti_values: np.ndarray,
                                    fico_values: np.ndarray, *, dti_ceiling: float = 43.0,
                                    fico_floor: float = 620.0) -> dict:
    """Spearman of |dti - dti_ceiling| with `d` and of |fico - fico_floor| with
    `d` -- does *proximity to the documented policy thresholds* track the
    disagreement? Reports both and the max |rho|. Missing feature -> None."""
    d = np.asarray(d, dtype=float).ravel()
    def one(vals):
        if vals is None:
            return {"spearman_rho": None, "spearman_p": None}
        v = np.asarray(vals, dtype=float)
        if v.size != d.size or float(np.std(v)) < 1e-12 or float(np.std(d)) < 1e-12:
            return {"spearman_rho": None, "spearman_p": None}
        sr = spearmanr(v, d)
        return {"spearman_rho": None if np.isnan(sr.correlation) else round(float(sr.correlation), 4),
                "spearman_p": None if np.isnan(sr.pvalue) else round(float(sr.pvalue), 4)}
    dti_prox = one(None if dti_values is None else np.abs(np.asarray(dti_values, float) - dti_ceiling))
    fico_prox = one(None if fico_values is None else np.abs(np.asarray(fico_values, float) - fico_floor))
    cands = [abs(x["spearman_rho"]) for x in (dti_prox, fico_prox) if x["spearman_rho"] is not None]
    return {"dti_ceiling": dti_ceiling, "fico_floor": fico_floor,
            "dti_proximity": dti_prox, "fico_proximity": fico_prox,
            "max_abs_rho": round(max(cands), 4) if cands else None}


def cross_tier_consistency(per_grade_top_features: dict, per_grade_shapes: dict) -> dict:
    """Across the plural grades: the multiset of dominant disagreement-driver
    features and of PD shapes, the modal value of each and whether it covers a
    strict majority of the grades. Returns the counts + the booleans."""
    def summarize(mapping: dict) -> dict:
        vals = [v for v in mapping.values() if v is not None]
        n = len(vals)
        counts: dict = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        modal, modal_n = (None, 0)
        for v, c in sorted(counts.items(), key=lambda kv: -kv[1]):
            modal, modal_n = v, c
            break
        return {"n": n, "counts": counts, "modal": modal, "modal_count": modal_n,
                "majority": bool(n > 0 and modal_n > n / 2)}
    return {"dominant_feature": summarize(per_grade_top_features),
            "pd_shape": summarize(per_grade_shapes)}
