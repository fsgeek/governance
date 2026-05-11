"""Tests for wedge.rashomon — sweep, policy evaluation, ε-filter, diversity selection.

Three-phase construction pipeline per spec §2.7 OD-9b / OD-12:
    hyperparameter_sweep -> evaluate_policy -> filter_to_epsilon -> select_diverse_members
"""

from __future__ import annotations

import pytest

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    EpsilonAdmissibleSet,
    ExclusionRecord,
    HyperparameterSpec,
    PolicyAdmissibleSet,
    SweepConfig,
    evaluate_policy,
    filter_to_epsilon,
    hyperparameter_sweep,
    select_diverse_members,
)
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset


def _trivial_policy(*, mandatory=(), prohibited=(), monotonicity=None):
    """Build a minimal PolicyConstraints for tests."""
    return PolicyConstraints(
        name="test",
        version="0",
        status="test",
        monotonicity_map=monotonicity or {},
        mandatory_features=mandatory,
        prohibited_features=prohibited,
    )


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


def test_hyperparameter_sweep_retains_fitted_tree():
    """SweepResult.fitted_tree must be populated so evaluate_policy can inspect
    the used-feature set without re-fitting."""
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3,),
        min_samples_leafs=(5,),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    for r in results:
        assert r.fitted_tree is not None
        # sklearn DecisionTreeClassifier exposes tree_.feature post-fit.
        assert hasattr(r.fitted_tree, "tree_")


# ---------------------------------------------------------------------------
# evaluate_policy — phase 1 of the three-phase pipeline (spec §2.7 OD-9b / OD-12)
# ---------------------------------------------------------------------------


def test_evaluate_policy_no_constraints_admits_all():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    result = evaluate_policy(sweep, policy_constraints=None)
    assert isinstance(result, PolicyAdmissibleSet)
    assert len(result.admissible) == len(sweep)
    assert result.excluded == []
    assert result.total_swept == len(sweep)


def test_evaluate_policy_excludes_subset_missing_mandatory_feature():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(5,),
        min_samples_leafs=(5,),
        feature_subsets=(("fico_proxy", "dti_proxy"),),  # no income_proxy
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy = _trivial_policy(mandatory=("income_proxy",))
    result = evaluate_policy(sweep, policy_constraints=policy)
    assert len(result.admissible) == 0
    assert len(result.excluded) == 1
    assert isinstance(result.excluded[0], ExclusionRecord)
    assert "mandatory_feature_not_in_subset" in result.excluded[0].reason
    assert "income_proxy" in result.excluded[0].reason


def test_evaluate_policy_excludes_prohibited_feature_in_subset():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(5,),
        min_samples_leafs=(5,),
        feature_subsets=(tuple(FEATURE_COLS),),  # contains fico_proxy
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy = _trivial_policy(prohibited=("fico_proxy",))
    result = evaluate_policy(sweep, policy_constraints=policy)
    assert len(result.admissible) == 0
    assert all("prohibited_feature_in_subset" in er.reason for er in result.excluded)


def test_evaluate_policy_excludes_post_fit_when_tree_does_not_split_on_mandatory():
    """Spec §2.7 OD-12: a fitted tree that does not split on a mandatory feature
    is excluded from the admissible set even though the subset is admissible."""
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(1,),  # depth 1 = at most one feature gets used
        min_samples_leafs=(5,),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    # Mark three features as mandatory; the depth-1 tree can only split on one.
    policy = _trivial_policy(
        mandatory=("fico_proxy", "dti_proxy", "income_proxy", "history_depth"),
    )
    result = evaluate_policy(sweep, policy_constraints=policy)
    assert len(result.admissible) == 0
    assert len(result.excluded) > 0
    assert all("mandatory_feature_unused" in er.reason for er in result.excluded)


def test_evaluate_policy_admits_when_tree_uses_all_mandatory_features():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(5,),
        min_samples_leafs=(5,),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    # fico_proxy and dti_proxy are the only features the separable rule depends
    # on (per fixtures.py), so a depth-5 tree should split on both.
    policy = _trivial_policy(mandatory=("fico_proxy", "dti_proxy"))
    result = evaluate_policy(sweep, policy_constraints=policy)
    assert len(result.admissible) == len(sweep)
    assert result.excluded == []


# ---------------------------------------------------------------------------
# filter_to_epsilon — phase 2 of the three-phase pipeline
# ---------------------------------------------------------------------------


def test_filter_to_epsilon_partitions_admissible_set():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy_set = evaluate_policy(sweep, policy_constraints=None)
    result = filter_to_epsilon(policy_set, epsilon=0.05)
    assert isinstance(result, EpsilonAdmissibleSet)
    expected_best = max(sr.holdout_auc for sr in policy_set.admissible)
    assert result.global_best_auc == pytest.approx(expected_best)
    assert result.epsilon == pytest.approx(0.05)
    for sr in result.within_epsilon:
        assert expected_best - sr.holdout_auc <= 0.05 + 1e-9
    for sr in result.out_of_epsilon:
        assert expected_best - sr.holdout_auc > 0.05 + 1e-9
    # within ∪ out covers the admissible set with no overlap.
    assert len(result.within_epsilon) + len(result.out_of_epsilon) == len(policy_set.admissible)


def test_filter_to_epsilon_measures_against_admissible_best_not_global_best():
    """When some sweep results are policy-excluded, ε is measured against the
    best AUC among admissible models, not the best AUC overall. This matters
    when the policy is binding: we want 'near-optimal under the policy', not
    'near-optimal under the policy AND the unconstrained best'."""
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    # Exclude the best model (or some prefix) by marking history_depth mandatory
    # but only some trees split on it. Mandate at least one feature that's
    # usage-dependent so SOME but not ALL models pass.
    policy = _trivial_policy(mandatory=("history_depth",))
    policy_set = evaluate_policy(sweep, policy_constraints=policy)
    if not policy_set.admissible:
        pytest.skip("fixture coincidentally excluded all models; rerun with different seed")
    eps_result = filter_to_epsilon(policy_set, epsilon=0.05)
    admissible_best = max(sr.holdout_auc for sr in policy_set.admissible)
    assert eps_result.global_best_auc == pytest.approx(admissible_best)


def test_filter_to_epsilon_empty_admissible_set_returns_empty():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(1,),
        min_samples_leafs=(5,),
        feature_subsets=(("fico_proxy",),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    # Subset doesn't contain the mandatory feature -> all excluded.
    policy = _trivial_policy(mandatory=("dti_proxy",))
    policy_set = evaluate_policy(sweep, policy_constraints=policy)
    assert len(policy_set.admissible) == 0
    result = filter_to_epsilon(policy_set, epsilon=0.05)
    assert result.within_epsilon == []
    assert result.out_of_epsilon == []


# ---------------------------------------------------------------------------
# select_diverse_members — phase 3 (unchanged signature, takes list[SweepResult])
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Three-phase composition produces the expected members
# ---------------------------------------------------------------------------


def test_three_phase_pipeline_produces_admissible_within_epsilon_members():
    """End-to-end: sweep -> evaluate_policy -> filter_to_epsilon -> select_diverse_members
    yields members that all satisfy policy AND are within ε of the admissible best."""
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy = _trivial_policy(mandatory=("fico_proxy", "dti_proxy"))
    policy_set = evaluate_policy(sweep, policy_constraints=policy)
    eps_set = filter_to_epsilon(policy_set, epsilon=0.10)
    members = select_diverse_members(eps_set.within_epsilon, n=3)
    assert 1 <= len(members) <= 3
    for m in members:
        assert eps_set.global_best_auc - m.holdout_auc <= 0.10 + 1e-9


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
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy_set = evaluate_policy(sweep, policy_constraints=None)
    eps_set = filter_to_epsilon(policy_set, epsilon=0.10)
    members = select_diverse_members(eps_set.within_epsilon, n=3)
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
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy_set = evaluate_policy(sweep, policy_constraints=None)
    eps_set = filter_to_epsilon(policy_set, epsilon=0.10)
    members = select_diverse_members(eps_set.within_epsilon, n=2)
    fitted_a = refit_members(df[FEATURE_COLS], df["label"], members=members, random_state=42)
    fitted_b = refit_members(df[FEATURE_COLS], df["label"], members=members, random_state=42)
    import numpy as np
    preds_a = fitted_a[0].predict(df[FEATURE_COLS])
    preds_b = fitted_b[0].predict(df[FEATURE_COLS])
    assert np.array_equal(preds_a, preds_b)
