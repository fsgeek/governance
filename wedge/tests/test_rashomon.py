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
    # All members within epsilon of the best AUC observed in the sweep.
    aucs = [m.holdout_auc for m in members]
    best = max(aucs)
    for auc in aucs:
        assert best - auc <= 0.05 + 1e-9


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
