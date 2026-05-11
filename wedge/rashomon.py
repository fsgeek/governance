"""Three-phase R(ε) construction: sweep → policy evaluation → ε-filter → selection.

Pipeline per spec §3 (set construction) and §2.7 OD-9b/OD-12 (mandatory-feature
enforcement):

  1. hyperparameter_sweep(X, y, config)
        Fit a sweep of single-CART hyperparameter combinations on a hold-out
        from the train set. Each SweepResult retains its fitted tree so later
        stages can inspect the used-feature set.

  2. evaluate_policy(sweep_results, policy_constraints)
        Partition swept results into a PolicyAdmissibleSet:
          - admissible: feature subset and fitted tree both satisfy the policy
          - excluded:   ExclusionRecord per failure with a structured reason
        With policy_constraints=None, all results are admissible.

  3. filter_to_epsilon(policy_admissible_set, epsilon)
        Within the admissible set, partition by holdout-AUC distance from the
        admissible best:
          - within_epsilon: AUC within ε of admissible_best (the R(ε) candidates)
          - out_of_epsilon: admissible but suboptimal
        Note: ε is measured against the best AUC among admissible models, not
        against the global sweep best. The unconstrained case behaves identically
        because all results are admissible.

  4. select_diverse_members(within_epsilon_results, n)
        Farthest-point selection in spec space; picks n members for diversity.

Each intermediate set is a first-class object (auditable; carries the data
that feeds the construction manifest per spec §3.6). The decomposition matches
the spec's natural seams: admissibility (categorical) is distinct from
near-optimality (gradational), which is distinct from diversity selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from policy.encoder import PolicyConstraints
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
    """

    spec: HyperparameterSpec
    holdout_auc: float
    fitted_tree: Optional[DecisionTreeClassifier] = None


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
    """Output of phase 3 (filter_to_epsilon).

    `within_epsilon` is the R(ε) candidate set: admissible models with
    holdout_auc within `epsilon` of `global_best_auc`. `global_best_auc` is the
    best AUC among admissible models (not among all swept results). When the
    admissible set is empty, `global_best_auc` is NaN and both partitions are
    empty.
    """

    within_epsilon: list[SweepResult]
    out_of_epsilon: list[SweepResult]
    global_best_auc: float
    epsilon: float


# ---------------------------------------------------------------------------
# Phase 1: hyperparameter sweep
# ---------------------------------------------------------------------------


def hyperparameter_sweep(
    X: pd.DataFrame, y: pd.Series, *, config: SweepConfig
) -> list[SweepResult]:
    """Fit every (max_depth, min_samples_leaf, feature_subset) combination on a
    hold-out and return per-combo SweepResult with the fitted tree retained.
    """
    X_fit, X_holdout, y_fit, y_holdout = train_test_split(
        X, y, test_size=config.holdout_fraction, random_state=config.random_state, stratify=y
    )
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
                results.append(
                    SweepResult(
                        spec=HyperparameterSpec(
                            max_depth=depth,
                            min_samples_leaf=leaf_min,
                            feature_subset=subset,
                        ),
                        holdout_auc=auc,
                        fitted_tree=model.tree,
                    )
                )
    return results


# ---------------------------------------------------------------------------
# Phase 2: policy evaluation
# ---------------------------------------------------------------------------


def _used_features(fitted_tree: DecisionTreeClassifier, feature_names: list[str]) -> set[str]:
    """Return the set of feature names a fitted tree actually splits on.

    sklearn's `tree_.feature` is an int array of length `n_nodes`; non-leaf
    nodes carry the feature index used at the split, leaves carry -2 (the
    sentinel `TREE_UNDEFINED`). Index into `feature_names` accordingly.
    """
    feature_idx = fitted_tree.tree_.feature
    return {feature_names[i] for i in feature_idx if i >= 0}


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
    """Phase 3: partition the admissible set by AUC distance from the admissible
    best.

    `epsilon` is the tolerance: a model is in `within_epsilon` iff its
    holdout_auc is within `epsilon` of `global_best_auc` (the admissible-best
    AUC). When the admissible set is empty, both partitions are empty and
    `global_best_auc` is NaN.
    """
    if not admissible_set.admissible:
        return EpsilonAdmissibleSet(
            within_epsilon=[],
            out_of_epsilon=[],
            global_best_auc=float("nan"),
            epsilon=epsilon,
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
        global_best_auc=best,
        epsilon=epsilon,
    )


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
