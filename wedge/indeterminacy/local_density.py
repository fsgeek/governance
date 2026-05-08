"""Local-density indeterminacy species.

For each case landing in a leaf, compute the case's deviation from that leaf's
training-set centroid. Per-feature z-scores (using leaf-train-set mean and
population std) are computed; the case's I_local_density score is the maximum
absolute z-score across features used by the model.

Conceptual scope and limitation:
  The memo's local-density concept covered both tails — "doesn't fit"
  (atypical) and "fits too well" (suspiciously typical). A single case sitting
  near its leaf centroid is not structurally distinguishable from an ordinary
  central case without a set-level null model (the "fits too well" tail is a
  property of distributions of cases, not of single cases). This implementation
  captures only the atypical tail. The suspicious-typicality detection is
  deferred to a separate species or a set-level analysis pass.

Direction tag:
  - "atypical": max |z| > Z_ATYPICAL (case is far from leaf centroid in at
    least one feature)
  - "ordinary": max |z| <= Z_ATYPICAL
  - "unknown": no usable features (all NaN, or leaf statistics unavailable)

Factor support:
  Features sorted by |z| descending. weight = |z|. This identifies which
  features make the case unusual within its leaf.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from wedge.models import CartModel
from wedge.types import FactorSupportEntry, IndeterminacyComponent


Z_ATYPICAL = 2.0  # |z| above this threshold flags the case as atypical
Z_CAP = 10.0  # cap on per-feature |z| to prevent zero-variance dominance


@dataclass
class LeafStatistics:
    """Per-leaf feature mean and std for one fitted CartModel.

    Built once per model after refit on full training data. Queried per case
    via compute_local_density.
    """

    feature_names: tuple[str, ...]
    # leaf_id -> {feature -> (mean, std)}; std is population std (ddof=0)
    stats: dict[int, dict[str, tuple[float, float]]]
    # leaf_id -> training-sample count
    leaf_n: dict[int, int]

    @classmethod
    def fit(cls, model: CartModel, X_train: pd.DataFrame) -> "LeafStatistics":
        feature_names = tuple(model.feature_subset)
        sub = X_train[list(feature_names)].copy()
        leaf_ids = model.tree.apply(sub.to_numpy())
        stats: dict[int, dict[str, tuple[float, float]]] = {}
        leaf_n: dict[int, int] = {}
        for leaf_id in np.unique(leaf_ids):
            mask = leaf_ids == leaf_id
            leaf_sub = sub.loc[mask]
            leaf_n[int(leaf_id)] = int(mask.sum())
            per_feature: dict[str, tuple[float, float]] = {}
            for f in feature_names:
                col = leaf_sub[f].dropna()
                if len(col) == 0:
                    per_feature[f] = (float("nan"), 0.0)
                else:
                    mu = float(col.mean())
                    # ddof=0 (population) — for single-row leaves std is 0 anyway,
                    # and the leaf-train-set is treated as the population for the
                    # purpose of measuring "what's typical here".
                    sigma = float(col.std(ddof=0))
                    per_feature[f] = (mu, sigma)
            stats[int(leaf_id)] = per_feature
        return cls(feature_names=feature_names, stats=stats, leaf_n=leaf_n)


def compute_local_density(
    case_features: dict[str, Any],
    leaf_id: int,
    leaf_stats: LeafStatistics,
) -> IndeterminacyComponent:
    """Compute the local_density I component for one case landing in leaf_id."""
    leaf = leaf_stats.stats.get(leaf_id)
    if leaf is None:
        return IndeterminacyComponent(
            species="local_density",
            score=0.0,
            factor_support=[],
            direction="unknown",
        )

    z_scores: list[tuple[str, float]] = []
    for f in leaf_stats.feature_names:
        val = case_features.get(f)
        if val is None:
            continue
        try:
            v = float(val)
        except (TypeError, ValueError):
            continue
        if np.isnan(v):
            continue
        mu, sigma = leaf[f]
        if np.isnan(mu):
            continue
        if sigma < 1e-9:
            # zero-variance feature in this leaf: case is at the value or far from it
            z = 0.0 if abs(v - mu) < 1e-9 else Z_CAP
        else:
            z = (v - mu) / sigma
        z_abs = min(abs(z), Z_CAP)
        z_scores.append((f, z_abs))

    if not z_scores:
        return IndeterminacyComponent(
            species="local_density",
            score=0.0,
            factor_support=[],
            direction="unknown",
        )

    z_scores.sort(key=lambda x: x[1], reverse=True)
    max_z = z_scores[0][1]
    direction = "atypical" if max_z > Z_ATYPICAL else "ordinary"

    factor_support = [
        FactorSupportEntry(feature=f, weight=float(z))
        for f, z in z_scores
        if z > 0
    ]

    return IndeterminacyComponent(
        species="local_density",
        score=float(max_z),
        factor_support=factor_support,
        direction=direction,
    )
