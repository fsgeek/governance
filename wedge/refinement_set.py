"""Within-grade policy-constrained refinement epsilon-band (follow-on #6).

Pre-registration: docs/superpowers/specs/2026-05-12-policy-constrained-rashomon-refinement-preregistration-note.md.

Given the loans in one lender risk-tier and a binary "did it default" label, build
the epsilon-band of policy-admissible *refinements* — shallow CARTs over subsets
of the policy's named features, with the policy's monotonicity directions
enforced (passed in already sign-flipped for default-prediction: the policy
encoder states directions relative to grant probability; this module's models
predict default probability, so the caller negates). The band is the within-tier
analog of the verdict-side R(epsilon) in `wedge/rashomon.py`, scoped to the
documented policy vocabulary.

The slow data load and the per-burst orchestration live in
`scripts/within_tier_rashomon_test.py`; this module builds one tier's band and
provides the plurality metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RefinementMember:
    """One refinement in (or out of) the epsilon-band: a (feature subset, depth,
    leaf-min) combo with its holdout AUC and a structural signature of the tree
    fitted on the train split (used for de-duplication)."""
    feature_subset: tuple[str, ...]
    max_depth: int
    min_samples_leaf: int
    monotonic_cst: tuple[int, ...]
    holdout_auc: float
    tree_signature: tuple


@dataclass
class RefinementBand:
    members: list[RefinementMember]              # all combos within epsilon
    distinct_members: list[RefinementMember]     # de-duplicated by tree_signature
    best_holdout_auc: Optional[float]
    epsilon: float
    n_combos_tried: int
    feature_names: tuple[str, ...]


# ---------------------------------------------------------------------------
def _tree_signature(tree: DecisionTreeClassifier, subset: tuple[str, ...]) -> tuple:
    """A hashable structural signature: the subset + the (feature, threshold)
    sequence of internal nodes (rounded), so two combos that fit the same tree
    de-dup to one. Leaves carry feature index -2 in sklearn; we keep only splits."""
    t = tree.tree_
    nodes = []
    for i in range(t.node_count):
        f = int(t.feature[i])
        if f >= 0:
            nodes.append((f, round(float(t.threshold[i]), 6)))
    return (subset, tuple(nodes))


def used_feature_set(tree: DecisionTreeClassifier, subset: tuple[str, ...]) -> set[str]:
    """Names of the features the fitted tree actually splits on (subset positions
    mapped back to names)."""
    t = tree.tree_
    used = {int(f) for f in t.feature if int(f) >= 0}
    return {subset[i] for i in used if i < len(subset)}


def _fit_one(X_sub: np.ndarray, y: np.ndarray, *, max_depth: int, min_samples_leaf: int,
             monotonic_cst: tuple[int, ...], seed: int) -> Optional[DecisionTreeClassifier]:
    if y.min() == y.max():
        return None
    kwargs = dict(max_depth=max_depth, min_samples_leaf=min_samples_leaf, random_state=seed)
    if any(c != 0 for c in monotonic_cst):
        kwargs["monotonic_cst"] = np.asarray(monotonic_cst, dtype=np.int8)
    m = DecisionTreeClassifier(**kwargs)
    m.fit(X_sub, y)
    return m


def build_refinement_band(
    X: np.ndarray,
    y: np.ndarray,
    *,
    feature_names: list[str],
    monotonic_cst_map: dict[str, int],
    epsilon: float = 0.02,
    depths: Iterable[int] = (1, 2, 3),
    leaf_mins: Iterable[int] = (25, 50, 100),
    holdout_frac: float = 0.3,
    seed: int = 0,
) -> RefinementBand:
    """Build the epsilon-band of policy-admissible refinements for one tier.

    X is (n, p) aligned to `feature_names`; y is (n,) with 1 == default. For each
    non-empty subset of `feature_names` x depth x leaf_min, fit a CART on a
    deterministic train split (with the subset's monotonicity constraints from
    `monotonic_cst_map`, missing entries unconstrained), score by holdout AUC for
    default. The band = combos with holdout AUC >= best - epsilon.
    `monotonic_cst_map` values must already be in the *default-prediction*
    convention (caller negates the policy encoder's grant-convention values).
    An empty map gives the unconstrained band.
    """
    feature_names = list(feature_names)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    name_to_col = {f: i for i, f in enumerate(feature_names)}

    if y.size < 8 or y.min() == y.max():
        return RefinementBand([], [], None, epsilon, 0, tuple(feature_names))

    Xtr, Xho, ytr, yho = train_test_split(X, y, test_size=holdout_frac, random_state=seed,
                                          stratify=y if min(np.bincount(y)) >= 2 else None)
    if yho.min() == yho.max() or ytr.min() == ytr.max():
        return RefinementBand([], [], None, epsilon, 0, tuple(feature_names))

    all_subsets = []
    for k in range(1, len(feature_names) + 1):
        all_subsets.extend(combinations(feature_names, k))

    scored: list[tuple[float, RefinementMember]] = []
    n_tried = 0
    for subset in all_subsets:
        cols = [name_to_col[f] for f in subset]
        mono = tuple(int(monotonic_cst_map.get(f, 0)) for f in subset)
        Xtr_s, Xho_s = Xtr[:, cols], Xho[:, cols]
        for d in depths:
            for lm in leaf_mins:
                n_tried += 1
                tree = _fit_one(Xtr_s, ytr, max_depth=d, min_samples_leaf=lm,
                                monotonic_cst=mono, seed=seed)
                if tree is None:
                    continue
                ho_pred = tree.predict_proba(Xho_s)[:, 1]
                try:
                    auc = float(roc_auc_score(yho, ho_pred))
                except ValueError:
                    continue
                scored.append((auc, RefinementMember(
                    feature_subset=tuple(subset), max_depth=int(d), min_samples_leaf=int(lm),
                    monotonic_cst=mono, holdout_auc=auc,
                    tree_signature=_tree_signature(tree, tuple(subset)),
                )))

    if not scored:
        return RefinementBand([], [], None, epsilon, n_tried, tuple(feature_names))

    best = max(a for a, _ in scored)
    members = [m for a, m in scored if a >= best - epsilon - 1e-12]
    # De-dup by tree signature, keeping the highest-AUC representative.
    by_sig: dict[tuple, RefinementMember] = {}
    for m in sorted(members, key=lambda mm: -mm.holdout_auc):
        if m.tree_signature not in by_sig:
            by_sig[m.tree_signature] = m
    distinct = list(by_sig.values())
    return RefinementBand(members=members, distinct_members=distinct, best_holdout_auc=best,
                          epsilon=epsilon, n_combos_tried=n_tried, feature_names=tuple(feature_names))


def refit_member(member: RefinementMember, X: np.ndarray, y: np.ndarray, *,
                 feature_names: list[str], seed: int = 0) -> DecisionTreeClassifier:
    """Re-fit a band member on the full (X, y) — used before forward evaluation.

    Mirrors `wedge/rashomon.refit_members`: the band is selected on the train/
    holdout split; the member you deploy/evaluate is re-fit on everything.
    """
    name_to_col = {f: i for i, f in enumerate(feature_names)}
    cols = [name_to_col[f] for f in member.feature_subset]
    m = _fit_one(np.asarray(X, float)[:, cols], np.asarray(y, int),
                 max_depth=member.max_depth, min_samples_leaf=member.min_samples_leaf,
                 monotonic_cst=member.monotonic_cst, seed=seed)
    if m is None:
        raise ValueError("cannot refit member: degenerate labels")
    return m


def pairwise_ranking_spearman(score_vectors: list[np.ndarray]) -> tuple[float, float]:
    """Median and minimum pairwise Spearman correlation among a set of score
    vectors (each a model's predicted-default scores on the same loans).

    High median ~ the band members rank the tier's borrowers nearly identically
    (low plurality of *outputs*); low ~ they disagree (the disagreement /
    indeterminacy signal). A single vector returns (1.0, 1.0).
    """
    if len(score_vectors) < 2:
        return 1.0, 1.0
    ranks = [pd.Series(np.asarray(v, dtype=float)).rank(method="average").to_numpy()
             for v in score_vectors]
    rhos = []
    for a, b in combinations(ranks, 2):
        if np.std(a) == 0 or np.std(b) == 0:
            rhos.append(0.0)
            continue
        rho = float(np.corrcoef(a, b)[0, 1])
        rhos.append(0.0 if np.isnan(rho) else rho)
    rhos = np.asarray(rhos)
    return float(np.median(rhos)), float(np.min(rhos))
