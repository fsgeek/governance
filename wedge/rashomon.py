"""Three-phase R(ε) construction with single and dual-set variants.

Pipeline per spec §3 (set construction) and §2.7 OD-9b/OD-12 (mandatory-feature
enforcement):

  1. hyperparameter_sweep(X, y, config)
        Fit a sweep of single-CART hyperparameter combinations on a hold-out
        from the train set. Each SweepResult retains its fitted tree (for the
        post-fit policy gate) AND its holdout_y_true / holdout_y_pred arrays
        (so cost-asymmetric losses can be evaluated without re-fitting).

  2. evaluate_policy(sweep_results, policy_constraints)
        Partition swept results into a PolicyAdmissibleSet:
          - admissible: feature subset and fitted tree both satisfy the policy
          - excluded:   ExclusionRecord per failure with a structured reason
        With policy_constraints=None, all results are admissible.

  3a. filter_to_epsilon(policy_admissible_set, epsilon)
        Single-set ε-filter under holdout AUC (higher = better). The R(ε) of
        spec §1, before the dual-set generalization.

  3b. filter_to_epsilon_under_loss(admissible_set, *, loss_fn, loss_label, epsilon)
        Loss-based ε-filter (lower = better). Used by build_dual_set to
        construct R_T and R_F under cost-asymmetric losses L_T and L_F
        (spec §3.2 / §3.3).

  3c. build_dual_set(admissible_set, *, epsilon_T, epsilon_F, w_T, w_F)
        Dual-set construction: returns (R_T, R_F) as a pair of
        EpsilonAdmissibleSet objects under L_T (grant-emphasis) and L_F
        (deny-emphasis) respectively.

  4. select_diverse_members(within_epsilon_results, n)
        Farthest-point selection in spec space; picks n members for diversity.

Each intermediate set is a first-class object (auditable; carries the data
that feeds the construction manifest per spec §3.6). The decomposition matches
the spec's natural seams: admissibility (categorical) is distinct from
near-optimality (gradational), which is distinct from diversity selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from policy.encoder import PolicyConstraints
from wedge.losses import (
    deny_emphasis_loss,
    deny_emphasis_loss_weighted,
    grant_emphasis_loss,
    grant_emphasis_loss_weighted,
)
from wedge.models import CartModel, fit_model


@dataclass(frozen=True)
class HyperparameterSpec:
    max_depth: int
    min_samples_leaf: int
    feature_subset: tuple[str, ...]


@dataclass
class SweepResult:
    """One hyperparameter combo with its fit outcome.

    `fitted_tree` is populated by `hyperparameter_sweep` so downstream phases
    (policy evaluation, post-fit inspection) can read `tree_.feature` without
    re-fitting. The wedge re-fits selected members on the full training set
    in `refit_members`; the sweep's tree is for inspection only.

    `holdout_y_true` and `holdout_y_pred` retain the model's holdout-set
    predictions and true labels so cost-asymmetric losses (L_T, L_F) can be
    evaluated for dual-set construction without re-fitting. Each SweepResult
    from a given sweep carries the same `holdout_y_true` (the shared
    train_test_split outcome); this is redundant across the list but keeps
    the API surface flat.
    """

    spec: HyperparameterSpec
    holdout_auc: float
    fitted_tree: Optional[DecisionTreeClassifier] = None
    holdout_y_true: Optional[np.ndarray] = None
    holdout_y_pred: Optional[np.ndarray] = None


@dataclass
class SweepConfig:
    max_depths: tuple[int, ...]
    min_samples_leafs: tuple[int, ...]
    feature_subsets: tuple[tuple[str, ...], ...]
    random_state: int = 0
    holdout_fraction: float = 0.3


@dataclass(frozen=True)
class ExclusionRecord:
    """A swept hyperparameter combo excluded by policy with a structured reason.

    The `reason` field is a short label followed by the offending feature(s),
    e.g. "mandatory_feature_unused: ['fico_range_low']". Audit consumers parse
    this; the construction manifest (§3.6) aggregates counts per reason label.
    """

    spec: HyperparameterSpec
    reason: str


@dataclass(frozen=True)
class PolicyAdmissibleSet:
    """Output of phase 2 (evaluate_policy).

    `admissible` are swept results satisfying the policy at both the feature-
    subset gate (mandatory present, prohibited absent) AND the post-fit gate
    (fitted tree splits on every mandatory feature). `excluded` records each
    failure with its reason. `total_swept` is `len(admissible) + len(excluded)`.
    """

    admissible: list[SweepResult]
    excluded: list[ExclusionRecord]
    total_swept: int


@dataclass(frozen=True)
class EpsilonAdmissibleSet:
    """Output of phase 3 (filter_to_epsilon or filter_to_epsilon_under_loss).

    `within_epsilon` is the R(ε) candidate set: admissible models within
    `epsilon` of `global_best_value` under the score function indicated by
    `score_label`.

    Score conventions:
      - "auc"           : `global_best_value` is the max AUC among admissible
                          models; within-ε means `best - sr.holdout_auc ≤ ε`.
      - "L_T(...)"      : `global_best_value` is the min L_T loss; within-ε
                          means `sr.loss - best ≤ ε`.
      - "L_F(...)"      : analogous to L_T.

    When the admissible set is empty, `global_best_value` is NaN and both
    partitions are empty.
    """

    within_epsilon: list[SweepResult]
    out_of_epsilon: list[SweepResult]
    global_best_value: float
    epsilon: float
    score_label: str


# ---------------------------------------------------------------------------
# Phase 1: hyperparameter sweep
# ---------------------------------------------------------------------------


def inner_split(
    X: pd.DataFrame, y: pd.Series, *, config: SweepConfig
):
    """Deterministic train/holdout split used by `hyperparameter_sweep`.

    Exposed so callers that need to align downstream computations to the
    same holdout (e.g. surprise-weight construction for `build_dual_set`)
    can recover the exact (X_fit, X_holdout, y_fit, y_holdout) tuple
    without re-implementing the split. Refactor target: any change to
    sweep's internal split discipline lands here and propagates.
    """
    return train_test_split(
        X, y, test_size=config.holdout_fraction, random_state=config.random_state, stratify=y
    )


def hyperparameter_sweep(
    X: pd.DataFrame, y: pd.Series, *, config: SweepConfig
) -> list[SweepResult]:
    """Fit every (max_depth, min_samples_leaf, feature_subset) combination on a
    hold-out and return per-combo SweepResult with the fitted tree retained.
    """
    X_fit, X_holdout, y_fit, y_holdout = inner_split(X, y, config=config)
    results: list[SweepResult] = []
    for depth in config.max_depths:
        for leaf_min in config.min_samples_leafs:
            for si, subset in enumerate(config.feature_subsets):
                model = fit_model(
                    X_fit,
                    y_fit,
                    model_id=f"sweep_d{depth}_l{leaf_min}_s{si}",
                    max_depth=depth,
                    min_samples_leaf=leaf_min,
                    feature_subset=subset,
                    random_state=config.random_state,
                )
                proba = model.predict_proba(X_holdout)[:, list(model.classes_).index(1)]
                auc = float(roc_auc_score(y_holdout, proba))
                y_pred = model.predict(X_holdout)
                y_true = np.asarray(y_holdout)
                results.append(
                    SweepResult(
                        spec=HyperparameterSpec(
                            max_depth=depth,
                            min_samples_leaf=leaf_min,
                            feature_subset=subset,
                        ),
                        holdout_auc=auc,
                        fitted_tree=model.tree,
                        holdout_y_true=y_true,
                        holdout_y_pred=y_pred,
                    )
                )
    return results


# ---------------------------------------------------------------------------
# Phase 2: policy evaluation
# ---------------------------------------------------------------------------


def used_features(fitted_tree: DecisionTreeClassifier, feature_names: list[str]) -> set[str]:
    """Return the set of feature names a fitted tree actually splits on.

    sklearn's `tree_.feature` is an int array of length `n_nodes`; non-leaf
    nodes carry the feature index used at the split, leaves carry -2 (the
    sentinel `TREE_UNDEFINED`). Index into `feature_names` accordingly.

    Public API: also used by wedge.categories for the structural-distinguishing
    feature extraction (spec §6.2 condition 3).
    """
    feature_idx = fitted_tree.tree_.feature
    return {feature_names[i] for i in feature_idx if i >= 0}


# Backwards-compat alias; some internal call sites may still reference the
# underscore-prefixed name.
_used_features = used_features


def evaluate_policy(
    sweep_results: list[SweepResult],
    *,
    policy_constraints: PolicyConstraints | None,
) -> PolicyAdmissibleSet:
    """Phase 2: partition sweep results by policy admissibility.

    Two gates applied in order:

      1. Subset gate (pre-fit, structural): every mandatory feature must be
         in `spec.feature_subset`; no prohibited feature may be in it.
      2. Used-feature gate (post-fit, behavioral; spec §2.7 OD-12): every
         mandatory feature must appear in the fitted tree's `tree_.feature`
         set; no prohibited feature may appear there. (The prohibited-used
         check is redundant given the subset gate, but kept defensively in
         case future sweeps relax the subset construction.)

    With `policy_constraints=None`, every swept result is admissible.
    """
    if policy_constraints is None:
        return PolicyAdmissibleSet(
            admissible=list(sweep_results),
            excluded=[],
            total_swept=len(sweep_results),
        )

    admissible: list[SweepResult] = []
    excluded: list[ExclusionRecord] = []

    for sr in sweep_results:
        feature_names = list(sr.spec.feature_subset)
        subset_set = set(feature_names)

        # Gate 1a: mandatory features present in subset.
        missing_from_subset = [
            f for f in policy_constraints.mandatory_features if f not in subset_set
        ]
        if missing_from_subset:
            excluded.append(
                ExclusionRecord(
                    spec=sr.spec,
                    reason=f"mandatory_feature_not_in_subset: {missing_from_subset}",
                )
            )
            continue

        # Gate 1b: prohibited features absent from subset.
        prohibited_in_subset = [
            f for f in policy_constraints.prohibited_features if f in subset_set
        ]
        if prohibited_in_subset:
            excluded.append(
                ExclusionRecord(
                    spec=sr.spec,
                    reason=f"prohibited_feature_in_subset: {prohibited_in_subset}",
                )
            )
            continue

        # Gate 2 requires the fitted tree.
        if sr.fitted_tree is None:
            raise ValueError(
                "evaluate_policy with non-None policy_constraints requires "
                "SweepResult.fitted_tree to be populated. Did hyperparameter_sweep "
                "run successfully?"
            )

        used = _used_features(sr.fitted_tree, feature_names)

        # Gate 2a: every mandatory feature actually split on (spec §2.7 OD-12).
        unused_mandatory = [
            f for f in policy_constraints.mandatory_features if f not in used
        ]
        if unused_mandatory:
            excluded.append(
                ExclusionRecord(
                    spec=sr.spec,
                    reason=f"mandatory_feature_unused: {unused_mandatory}",
                )
            )
            continue

        # Gate 2b: no prohibited feature split on (defensive; subset gate
        # should have caught this already).
        prohibited_used = [
            f for f in policy_constraints.prohibited_features if f in used
        ]
        if prohibited_used:
            excluded.append(
                ExclusionRecord(
                    spec=sr.spec,
                    reason=f"prohibited_feature_used: {prohibited_used}",
                )
            )
            continue

        admissible.append(sr)

    return PolicyAdmissibleSet(
        admissible=admissible,
        excluded=excluded,
        total_swept=len(sweep_results),
    )


# ---------------------------------------------------------------------------
# Phase 3: ε-filter against the admissible best
# ---------------------------------------------------------------------------


def filter_to_epsilon(
    admissible_set: PolicyAdmissibleSet,
    *,
    epsilon: float,
) -> EpsilonAdmissibleSet:
    """Phase 3a (single-set, AUC): partition the admissible set by holdout-AUC
    distance from the admissible best (higher AUC = better).

    A model is in `within_epsilon` iff `admissible_best - sr.holdout_auc ≤ ε`.
    When the admissible set is empty, both partitions are empty and
    `global_best_value` is NaN.
    """
    if not admissible_set.admissible:
        return EpsilonAdmissibleSet(
            within_epsilon=[],
            out_of_epsilon=[],
            global_best_value=float("nan"),
            epsilon=epsilon,
            score_label="auc",
        )

    best = max(sr.holdout_auc for sr in admissible_set.admissible)
    tol = epsilon + 1e-9
    within: list[SweepResult] = []
    out: list[SweepResult] = []
    for sr in admissible_set.admissible:
        if best - sr.holdout_auc <= tol:
            within.append(sr)
        else:
            out.append(sr)
    return EpsilonAdmissibleSet(
        within_epsilon=within,
        out_of_epsilon=out,
        global_best_value=best,
        epsilon=epsilon,
        score_label="auc",
    )


def filter_to_epsilon_under_loss(
    admissible_set: PolicyAdmissibleSet,
    *,
    loss_fn: Callable[[np.ndarray, np.ndarray], float],
    loss_label: str,
    epsilon: float,
) -> EpsilonAdmissibleSet:
    """Phase 3b (loss-based): partition the admissible set by `loss_fn` distance
    from the admissible best (lower loss = better).

    `loss_fn(y_true, y_pred) -> float` is evaluated on each admissible model's
    stored holdout predictions. A model is in `within_epsilon` iff
    `sr.loss - admissible_best ≤ ε`.

    Used by `build_dual_set` to construct R_T and R_F under cost-asymmetric
    losses (spec §3.2 / §3.3). Requires that SweepResults have
    `holdout_y_true` and `holdout_y_pred` populated (default for results from
    `hyperparameter_sweep`).
    """
    if not admissible_set.admissible:
        return EpsilonAdmissibleSet(
            within_epsilon=[],
            out_of_epsilon=[],
            global_best_value=float("nan"),
            epsilon=epsilon,
            score_label=loss_label,
        )

    # Score each admissible model under the loss; surface missing holdout data
    # eagerly rather than silently NaN-ing.
    scored: list[tuple[SweepResult, float]] = []
    for sr in admissible_set.admissible:
        if sr.holdout_y_true is None or sr.holdout_y_pred is None:
            raise ValueError(
                "filter_to_epsilon_under_loss requires SweepResult.holdout_y_true "
                "and holdout_y_pred to be populated. Did hyperparameter_sweep run "
                "successfully?"
            )
        scored.append((sr, float(loss_fn(sr.holdout_y_true, sr.holdout_y_pred))))

    best = min(s for _, s in scored)
    tol = epsilon + 1e-9
    within: list[SweepResult] = []
    out: list[SweepResult] = []
    for sr, s in scored:
        if s - best <= tol:
            within.append(sr)
        else:
            out.append(sr)
    return EpsilonAdmissibleSet(
        within_epsilon=within,
        out_of_epsilon=out,
        global_best_value=best,
        epsilon=epsilon,
        score_label=loss_label,
    )


def build_dual_set(
    admissible_set: PolicyAdmissibleSet,
    *,
    epsilon_T: float,
    epsilon_F: float,
    w_T: float = 1.5,
    w_F: float = 1.5,
    sample_weights: Optional[np.ndarray] = None,
) -> tuple[EpsilonAdmissibleSet, EpsilonAdmissibleSet]:
    """Phase 3c: construct (R_T(ε_T), R_F(ε_F)) per spec §3.2 / §3.3.

    R_T = ε-band of policy-admissible models under L_T (grant-emphasis loss
          weighting missed grants by `w_T`).
    R_F = ε-band of policy-admissible models under L_F (deny-emphasis loss
          weighting missed denies by `w_F`).

    When `sample_weights` is provided (shape must match each SweepResult's
    `holdout_y_true`), the loss functions become the surprise-weighted
    variants L_T' and L_F' per spec §5 — set revision under surprise-weighted
    loss. `score_label` carries a prime marker ("L_T'(...)") to make the
    distinction visible in audit output.

    Both returned sets are `EpsilonAdmissibleSet` objects with `score_label`
    set to a parameterized loss identifier so the construction manifest (§3.6)
    records which loss produced each set.
    """
    if sample_weights is None:
        loss_T = partial(grant_emphasis_loss, w_T=w_T)
        loss_F = partial(deny_emphasis_loss, w_F=w_F)
        label_T = f"L_T(w_T={w_T})"
        label_F = f"L_F(w_F={w_F})"
    else:
        def loss_T(y, yh):
            return grant_emphasis_loss_weighted(
                y, yh, w_T=w_T, sample_weights=sample_weights
            )

        def loss_F(y, yh):
            return deny_emphasis_loss_weighted(
                y, yh, w_F=w_F, sample_weights=sample_weights
            )

        label_T = f"L_T'(w_T={w_T}, weighted)"
        label_F = f"L_F'(w_F={w_F}, weighted)"

    R_T = filter_to_epsilon_under_loss(
        admissible_set, loss_fn=loss_T, loss_label=label_T, epsilon=epsilon_T,
    )
    R_F = filter_to_epsilon_under_loss(
        admissible_set, loss_fn=loss_F, loss_label=label_F, epsilon=epsilon_F,
    )
    return R_T, R_F


# ---------------------------------------------------------------------------
# Phase 4: diversity selection
# ---------------------------------------------------------------------------


def select_diverse_members(
    sweep_results: list[SweepResult], *, n: int
) -> list[SweepResult]:
    """Greedy farthest-point selection in spec space.

    Encodes each spec as a numeric vector (max_depth, min_samples_leaf,
    len(feature_subset)). Each dimension is rescaled by its observed range
    across the candidate pool so that no axis dominates. Picks members
    iteratively: start with the highest-AUC candidate, then repeatedly
    add the candidate maximizing minimum L2 distance (in normalized space)
    to already-selected specs. Ties broken by AUC.
    """
    if n <= 0 or not sweep_results:
        return []
    candidates = sorted(sweep_results, key=lambda r: r.holdout_auc, reverse=True)

    raw = np.array(
        [
            [r.spec.max_depth, r.spec.min_samples_leaf, len(r.spec.feature_subset)]
            for r in candidates
        ],
        dtype=float,
    )
    spans = raw.max(axis=0) - raw.min(axis=0)
    spans = np.where(spans > 0, spans, 1.0)

    def _vec(r: SweepResult) -> np.ndarray:
        return np.array(
            [r.spec.max_depth, r.spec.min_samples_leaf, len(r.spec.feature_subset)],
            dtype=float,
        ) / spans

    selected = [candidates[0]]
    remaining = candidates[1:]
    while len(selected) < n and remaining:
        best_idx = None
        best_score = -1.0
        for i, cand in enumerate(remaining):
            min_dist = min(np.linalg.norm(_vec(cand) - _vec(s)) for s in selected)
            if min_dist > best_score or (
                abs(min_dist - best_score) < 1e-12
                and (best_idx is None or cand.holdout_auc > remaining[best_idx].holdout_auc)
            ):
                best_score = min_dist
                best_idx = i
        if best_idx is None:
            break
        selected.append(remaining.pop(best_idx))
    return selected


# ---------------------------------------------------------------------------
# Phase 5: refit selected members on the full training set
# ---------------------------------------------------------------------------


def refit_members(
    X: pd.DataFrame, y: pd.Series, *, members: list[SweepResult], random_state: int = 0
) -> list[CartModel]:
    """Re-fit each selected member on the full (X, y), assigning final model_ids."""
    out: list[CartModel] = []
    for i, m in enumerate(members):
        out.append(
            fit_model(
                X,
                y,
                model_id=f"tree_{i+1}",
                max_depth=m.spec.max_depth,
                min_samples_leaf=m.spec.min_samples_leaf,
                feature_subset=m.spec.feature_subset,
                random_state=random_state,
            )
        )
    return out
