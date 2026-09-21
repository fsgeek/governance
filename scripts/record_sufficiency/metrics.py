"""Divergence metrics for record-sufficiency recomputation.

Frozen by the pre-registration at docs/superpowers/specs/
2026-09-18-record-sufficiency-preregistration-note.md (OTS bd47a9d).

PRIMARY (gating):   top-k Jaccard, k=5, reproduce iff mean >= 0.90
SECONDARY (never gating): RBO (p=0.9), L2, cosine

The primary is rank-based on purpose. Hwang et al. (arXiv:2601.12654) show L2
reports stability that rank metrics do not support; an examiner reading an
attribution asks which factors drove the decision, which is a rank question.
Do not promote a secondary metric to gating. If a secondary contradicts the
primary, that contradiction is the finding.
"""

from __future__ import annotations

import numpy as np

PRIMARY_K = 5
PRIMARY_THRESHOLD = 0.90
SUFFICIENCY_FRACTION = 0.95
RBO_P = 0.9

# Sensitivity arms (reported, never gating) -- pre-reg section 4.
SENSITIVITY_K = (3, 5, 10)
SENSITIVITY_THRESHOLD = (0.85, 0.90, 0.95)
SENSITIVITY_FRACTION = (0.90, 0.95, 0.99)


def _topk_indices(attr_row: np.ndarray, k: int) -> set[int]:
    """Indices of the k largest-|attribution| features for one decision.

    Ties are broken by feature index, deterministically. A tie at the k-th
    position is a real source of instability; breaking it by index means we
    measure attribution divergence rather than sort-implementation divergence.
    """
    order = np.lexsort((np.arange(attr_row.shape[0]), -np.abs(attr_row)))
    return set(order[:k].tolist())


def topk_jaccard(a: np.ndarray, b: np.ndarray, k: int = PRIMARY_K) -> np.ndarray:
    """Per-decision top-k Jaccard similarity between two attribution matrices.

    a, b: (n_decisions, n_features). Returns (n_decisions,) in [0, 1].
    """
    _check_shapes(a, b)
    k = min(k, a.shape[1])
    out = np.empty(a.shape[0], dtype=float)
    for i in range(a.shape[0]):
        sa, sb = _topk_indices(a[i], k), _topk_indices(b[i], k)
        union = sa | sb
        out[i] = len(sa & sb) / len(union) if union else 1.0
    return out


def rbo(a: np.ndarray, b: np.ndarray, p: float = RBO_P) -> np.ndarray:
    """Rank-biased overlap over the full ranking, top-weighted by p.

    Secondary metric. Unlike top-k Jaccard this reads the whole ranking, so it
    catches reordering below k that the primary is blind to.

    Uses the EXTRAPOLATED form (Webber et al. 2010, eq. 32). Rankings here are
    finite (n_features long), and the raw truncated sum saturates at 1 - p**n
    rather than at 1.0 -- for n=10, p=0.9 that ceiling is 0.651. Two identical
    rankings would then score 0.651, and, worse, the ceiling MOVES WITH
    n_features, so a truncated RBO is not comparable across substrates with
    different feature counts. The extrapolated form assumes the unseen tail
    continues at the observed agreement, restoring RBO(x, x) == 1.0 and making
    the metric comparable across arms.
    """
    _check_shapes(a, b)
    n_feat = a.shape[1]
    out = np.empty(a.shape[0], dtype=float)
    for i in range(a.shape[0]):
        ra = np.lexsort((np.arange(n_feat), -np.abs(a[i])))
        rb = np.lexsort((np.arange(n_feat), -np.abs(b[i])))
        seen_a: set[int] = set()
        seen_b: set[int] = set()
        total = 0.0
        overlap_at_n = 0
        for d in range(n_feat):
            seen_a.add(int(ra[d]))
            seen_b.add(int(rb[d]))
            overlap_at_n = len(seen_a & seen_b)
            total += (overlap_at_n / (d + 1)) * (p ** d)
        # Extrapolate the unseen tail at the depth-n agreement ratio.
        tail = (overlap_at_n / n_feat) * (p ** n_feat)
        out[i] = (1 - p) * total + tail
    return out


def l2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-decision L2 distance. SECONDARY -- never gating. See module docstring."""
    _check_shapes(a, b)
    return np.linalg.norm(a - b, axis=1)


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-decision cosine similarity. SECONDARY -- never gating."""
    _check_shapes(a, b)
    na = np.linalg.norm(a, axis=1)
    nb = np.linalg.norm(b, axis=1)
    denom = na * nb
    out = np.ones(a.shape[0], dtype=float)
    nz = denom > 0
    out[nz] = np.sum(a[nz] * b[nz], axis=1) / denom[nz]
    return out


def reproduces(a: np.ndarray, b: np.ndarray,
               k: int = PRIMARY_K,
               threshold: float = PRIMARY_THRESHOLD,
               fraction: float = SUFFICIENCY_FRACTION) -> dict:
    """Frozen primary verdict: does recomputation b reproduce original a?

    Pre-reg section 2e/2f: mean top-k Jaccard >= threshold is the per-decision
    reproduce test; a record level is sufficient iff >= `fraction` of decisions
    reproduce. Both numbers are frozen; `k`/`threshold`/`fraction` are
    parameterised only so the section-4 sensitivity arms can be reported.
    """
    j = topk_jaccard(a, b, k=k)
    per_decision = j >= threshold
    frac = float(per_decision.mean())
    return {
        "metric": f"topk_jaccard_k{k}",
        "threshold": threshold,
        "mean_jaccard": float(j.mean()),
        "median_jaccard": float(np.median(j)),
        "min_jaccard": float(j.min()),
        "fraction_reproducing": frac,
        "sufficiency_fraction_required": fraction,
        "SUFFICIENT": bool(frac >= fraction),
        "n_decisions": int(a.shape[0]),
    }


def full_report(a: np.ndarray, b: np.ndarray) -> dict:
    """Primary verdict plus every secondary and sensitivity arm.

    Secondaries are namespaced under `secondary_*` so no downstream consumer can
    read one as the verdict by accident.
    """
    report = {"primary": reproduces(a, b)}

    n_feat = a.shape[1]
    null = random_null_jaccard(n_feat)
    report["chance_correction"] = {
        "n_features": int(n_feat),
        "random_null_jaccard": null,
        "normalized_jaccard": normalized_jaccard(
            report["primary"]["mean_jaccard"], n_feat),
        "note": "normalized = (observed - null)/(1 - null); "
                "ONLY this figure is comparable across substrates",
    }

    report["secondary_rbo"] = _summarize(rbo(a, b))
    report["secondary_l2"] = _summarize(l2(a, b))
    report["secondary_cosine"] = _summarize(cosine(a, b))

    sens = {}
    for k in SENSITIVITY_K:
        j = topk_jaccard(a, b, k=k)
        for t in SENSITIVITY_THRESHOLD:
            frac = float((j >= t).mean())
            for f in SENSITIVITY_FRACTION:
                sens[f"k{k}_thr{t}_frac{f}"] = {
                    "fraction_reproducing": frac,
                    "sufficient": bool(frac >= f),
                }
    report["sensitivity_NON_GATING"] = sens
    return report


def random_null_jaccard(n_features: int, k: int = PRIMARY_K,
                        trials: int = 40000, seed: int = 0) -> float:
    """E[top-k Jaccard] for two INDEPENDENT uniform-random rankings.

    The principled reference point Hwang et al. (arXiv:2601.12654) derive and
    which the R0 surrogate-refit control does not supply. It is not decorative:
    the null is a strong function of feature count --

        n_feat=7 -> 0.568   n_feat=12 -> 0.278   n_feat=50 -> 0.058

    -- because with k=5 of 7 features, two random top-5 sets must overlap
    heavily by construction. A raw Jaccard of 0.85 is therefore NOT comparable
    across substrates with different feature counts, and the study's two arms
    have 7 and 12 features. Report `normalized_jaccard` for any cross-arm
    statement.
    """
    rng = np.random.RandomState(seed)
    k = min(k, n_features)
    a = np.argsort(rng.rand(trials, n_features), axis=1)[:, :k]
    b = np.argsort(rng.rand(trials, n_features), axis=1)[:, :k]
    inter = np.array([len(set(x.tolist()) & set(y.tolist())) for x, y in zip(a, b)])
    return float((inter / (2 * k - inter)).mean())


def normalized_jaccard(observed: float, n_features: int,
                       k: int = PRIMARY_K) -> float:
    """Chance-corrected agreement: (observed - null) / (1 - null).

    0.0 == indistinguishable from random ranking; 1.0 == exact reproduction.
    Negative values mean WORSE than chance. This is the only Jaccard figure
    that may be compared across substrates. The frozen primary verdict in
    `reproduces` is deliberately NOT changed -- it stays on the raw scale the
    pre-registration fixed; this is an additional reported quantity.
    """
    null = random_null_jaccard(n_features, k=k)
    if null >= 1.0:
        return float("nan")
    return (observed - null) / (1.0 - null)


def _summarize(v: np.ndarray) -> dict:
    return {
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "min": float(v.min()),
        "max": float(v.max()),
    }


def _check_shapes(a: np.ndarray, b: np.ndarray) -> None:
    if a.shape != b.shape:
        raise ValueError(f"attribution shape mismatch: {a.shape} vs {b.shape}")
    if a.ndim != 2:
        raise ValueError(f"expected (n_decisions, n_features), got {a.shape}")
