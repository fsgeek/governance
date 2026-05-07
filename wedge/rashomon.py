"""R(ε) construction: hyperparameter sweep, ε filter, diversity-weighted selection.

The wedge fits a sweep of single-CART hyperparameter combinations on a
hold-out from the train set, defines ε = best_holdout_AUC - epsilon_tolerance,
and selects n_members from the within-ε candidates by farthest-point
selection in (depth, leaf_min, feature_subset) space — explicitly preferring
diversity of inductive bias over diversity of data fit.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from wedge.models import CartModel, fit_model


@dataclass(frozen=True)
class HyperparameterSpec:
    max_depth: int
    min_samples_leaf: int
    feature_subset: tuple[str, ...]


@dataclass
class SweepResult:
    spec: HyperparameterSpec
    holdout_auc: float


@dataclass
class SweepConfig:
    max_depths: tuple[int, ...]
    min_samples_leafs: tuple[int, ...]
    feature_subsets: tuple[tuple[str, ...], ...]
    random_state: int = 0
    holdout_fraction: float = 0.3


def hyperparameter_sweep(
    X: pd.DataFrame, y: pd.Series, *, config: SweepConfig
) -> list[SweepResult]:
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
                    )
                )
    return results


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

    # Compute per-dimension scale factors from the candidate pool so that
    # no axis (e.g. min_samples_leaf with span 400) dominates over another
    # (e.g. max_depth with span 8).
    raw = np.array(
        [
            [r.spec.max_depth, r.spec.min_samples_leaf, len(r.spec.feature_subset)]
            for r in candidates
        ],
        dtype=float,
    )
    spans = raw.max(axis=0) - raw.min(axis=0)
    spans = np.where(spans > 0, spans, 1.0)  # avoid divide-by-zero

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


def build_rashomon_set(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    config: SweepConfig,
    epsilon: float,
    n_members: int,
) -> list[SweepResult]:
    """Run the sweep, filter to within-ε of best AUC, select diverse members.

    Returns up to n_members SweepResults whose specs are the ones the caller
    will then re-fit on the full training set for emission.
    """
    sweep = hyperparameter_sweep(X, y, config=config)
    if not sweep:
        return []
    best = max(r.holdout_auc for r in sweep)
    in_epsilon = [r for r in sweep if best - r.holdout_auc <= epsilon + 1e-9]
    return select_diverse_members(in_epsilon, n=n_members)


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
