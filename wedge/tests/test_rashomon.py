"""Tests for wedge.rashomon — sweep, ε-filter, member sampling."""

from __future__ import annotations

import pandas as pd

from wedge.rashomon import (
    HyperparameterSpec,
    SweepConfig,
    build_rashomon_set,
    hyperparameter_sweep,
    select_diverse_members,
)
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset


def test_hyperparameter_sweep_returns_one_record_per_combo():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    assert len(results) == 4  # 2 depths * 2 leaf-mins * 1 subset
    for r in results:
        assert 0.0 <= r.holdout_auc <= 1.0
        assert isinstance(r.spec, HyperparameterSpec)


def test_build_rashomon_set_respects_epsilon():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    members = build_rashomon_set(
        df[FEATURE_COLS], df["label"], config=cfg, epsilon=0.05, n_members=5
    )
    assert len(members) <= 5
    assert len(members) >= 1
    # All members within epsilon of the GLOBAL sweep best, not the in-set best.
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    global_best = max(r.holdout_auc for r in sweep)
    for m in members:
        assert global_best - m.holdout_auc <= 0.05 + 1e-9


def test_select_diverse_members_picks_distinct_specs():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep_results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    diverse = select_diverse_members(sweep_results, n=3)
    assert len(diverse) == 3
    specs = {(d.spec.max_depth, d.spec.min_samples_leaf, d.spec.feature_subset) for d in diverse}
    assert len(specs) == 3  # all distinct


def test_refit_members_returns_one_cartmodel_per_member_with_correct_ids():
    from wedge.models import CartModel
    from wedge.rashomon import refit_members

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    members = build_rashomon_set(
        df[FEATURE_COLS], df["label"], config=cfg, epsilon=0.10, n_members=3
    )
    fitted = refit_members(df[FEATURE_COLS], df["label"], members=members, random_state=0)
    assert len(fitted) == len(members)
    expected_ids = [f"tree_{i+1}" for i in range(len(members))]
    assert [m.model_id for m in fitted] == expected_ids
    for f, m in zip(fitted, members):
        assert isinstance(f, CartModel)
        assert tuple(f.feature_subset) == m.spec.feature_subset


def test_refit_members_deterministic_with_random_state():
    from wedge.rashomon import refit_members

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    members = build_rashomon_set(
        df[FEATURE_COLS], df["label"], config=cfg, epsilon=0.10, n_members=2
    )
    fitted_a = refit_members(df[FEATURE_COLS], df["label"], members=members, random_state=42)
    fitted_b = refit_members(df[FEATURE_COLS], df["label"], members=members, random_state=42)
    # Same random_state -> same predictions on the training data.
    import numpy as np
    preds_a = fitted_a[0].predict(df[FEATURE_COLS])
    preds_b = fitted_b[0].predict(df[FEATURE_COLS])
    assert np.array_equal(preds_a, preds_b)
