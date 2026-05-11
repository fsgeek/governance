"""Tests for wedge.rashomon — sweep, policy evaluation, ε-filter, diversity selection.

Three-phase construction pipeline per spec §2.7 OD-9b / OD-12:
    hyperparameter_sweep -> evaluate_policy -> filter_to_epsilon -> select_diverse_members
"""

from __future__ import annotations

import pytest

from policy.encoder import PolicyConstraints
from wedge.losses import deny_emphasis_loss, grant_emphasis_loss
from wedge.rashomon import (
    EpsilonAdmissibleSet,
    ExclusionRecord,
    HyperparameterSpec,
    PolicyAdmissibleSet,
    SweepConfig,
    build_dual_set,
    evaluate_policy,
    filter_to_epsilon,
    filter_to_epsilon_under_loss,
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


def test_hyperparameter_sweep_retains_holdout_predictions():
    """SweepResult must retain holdout_y_true and holdout_y_pred so dual-set
    construction can evaluate cost-asymmetric losses without re-fitting."""
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
        assert r.holdout_y_true is not None
        assert r.holdout_y_pred is not None
        assert r.holdout_y_true.shape == r.holdout_y_pred.shape
        # Holdout fraction was 0.3 over 100 rows; pandas train_test_split with
        # stratify rounds, but shape should be in a plausible range.
        assert 20 <= r.holdout_y_true.shape[0] <= 40
    # All SweepResults from one sweep share the same holdout split.
    import numpy as np
    first_y_true = results[0].holdout_y_true
    for r in results[1:]:
        assert np.array_equal(r.holdout_y_true, first_y_true)


# ---------------------------------------------------------------------------
# filter_to_epsilon_under_loss — Phase 3 under cost-asymmetric losses (§3.2/§3.3)
# ---------------------------------------------------------------------------


def test_filter_to_epsilon_under_loss_uses_grant_emphasis():
    """L_T-based ε-band: members are within ε of the L_T-minimal admissible model."""
    from functools import partial

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    loss_fn = partial(grant_emphasis_loss, w_T=1.5)
    result = filter_to_epsilon_under_loss(
        admissible, loss_fn=loss_fn, loss_label="L_T(w_T=1.5)", epsilon=2.0
    )
    assert isinstance(result, EpsilonAdmissibleSet)
    assert result.score_label == "L_T(w_T=1.5)"
    # The best L_T value among admissible members:
    losses = [loss_fn(sr.holdout_y_true, sr.holdout_y_pred) for sr in admissible.admissible]
    best_loss = min(losses)
    assert result.global_best_value == pytest.approx(best_loss)
    # Within-ε members all satisfy: loss - best_loss <= ε.
    for sr in result.within_epsilon:
        sr_loss = loss_fn(sr.holdout_y_true, sr.holdout_y_pred)
        assert sr_loss - best_loss <= 2.0 + 1e-9


def test_filter_to_epsilon_under_loss_uses_deny_emphasis():
    from functools import partial

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    loss_fn = partial(deny_emphasis_loss, w_F=1.5)
    result = filter_to_epsilon_under_loss(
        admissible, loss_fn=loss_fn, loss_label="L_F(w_F=1.5)", epsilon=2.0
    )
    assert result.score_label == "L_F(w_F=1.5)"
    losses = [loss_fn(sr.holdout_y_true, sr.holdout_y_pred) for sr in admissible.admissible]
    best_loss = min(losses)
    assert result.global_best_value == pytest.approx(best_loss)


def test_filter_to_epsilon_under_loss_empty_admissible_returns_empty():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(1,),
        min_samples_leafs=(5,),
        feature_subsets=(("fico_proxy",),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    policy = _trivial_policy(mandatory=("dti_proxy",))
    admissible = evaluate_policy(sweep, policy_constraints=policy)
    assert len(admissible.admissible) == 0

    from functools import partial
    result = filter_to_epsilon_under_loss(
        admissible,
        loss_fn=partial(grant_emphasis_loss, w_T=1.5),
        loss_label="L_T(w_T=1.5)",
        epsilon=2.0,
    )
    assert result.within_epsilon == []
    assert result.out_of_epsilon == []


# ---------------------------------------------------------------------------
# build_dual_set — R_T(ε_T) and R_F(ε_F) per spec §3.2 / §3.3
# ---------------------------------------------------------------------------


def test_build_dual_set_returns_two_epsilon_admissible_sets():
    """Dual-set construction yields R_T (grant-emphasis) and R_F (deny-emphasis),
    both filtered by policy admissibility and their respective ε-bands."""
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    R_T, R_F = build_dual_set(
        admissible, epsilon_T=2.0, epsilon_F=2.0, w_T=1.5, w_F=1.5
    )
    assert isinstance(R_T, EpsilonAdmissibleSet)
    assert isinstance(R_F, EpsilonAdmissibleSet)
    assert R_T.score_label.startswith("L_T")
    assert R_F.score_label.startswith("L_F")
    assert len(R_T.within_epsilon) > 0
    assert len(R_F.within_epsilon) > 0


def test_build_dual_set_revised_under_surprise_weights():
    """When sample_weights are provided, build_dual_set uses the weighted
    losses (L_T' / L_F'); score_label carries a prime marker."""
    import numpy as np

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    # All admissible SweepResults share the same holdout_y_true; build a
    # weight vector of matching shape.
    holdout_n = admissible.admissible[0].holdout_y_true.shape[0]
    rng = np.random.default_rng(seed=0)
    weights = rng.uniform(0.5, 2.0, size=holdout_n)

    R_T_prime, R_F_prime = build_dual_set(
        admissible,
        epsilon_T=2.0,
        epsilon_F=2.0,
        w_T=1.5,
        w_F=1.5,
        sample_weights=weights,
    )
    assert R_T_prime.score_label.startswith("L_T'")
    assert R_F_prime.score_label.startswith("L_F'")
    assert "weighted" in R_T_prime.score_label
    assert "weighted" in R_F_prime.score_label
    assert len(R_T_prime.within_epsilon) > 0


def test_build_dual_set_revised_uses_weighted_loss_implementation():
    """Surprise-weighted L_T' / L_F' produce different per-model loss values
    than the unweighted variants on any model with non-zero misses. (The best
    model may have zero misses → both losses are 0; tested at the per-model
    level rather than at the best-loss level to keep the test fixture-robust.)"""
    import numpy as np

    from wedge.losses import grant_emphasis_loss, grant_emphasis_loss_weighted

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    holdout_n = admissible.admissible[0].holdout_y_true.shape[0]
    weights = np.ones(holdout_n)
    weights[: holdout_n // 2] = 5.0

    # Per-model: weighted loss should equal unweighted loss only when the model
    # has zero misses in the up-weighted region. At least some non-best model
    # has misses there, so the values must differ for that model.
    differences = []
    for sr in admissible.admissible:
        unweighted = grant_emphasis_loss(sr.holdout_y_true, sr.holdout_y_pred, w_T=1.5)
        weighted = grant_emphasis_loss_weighted(
            sr.holdout_y_true, sr.holdout_y_pred, w_T=1.5, sample_weights=weights
        )
        differences.append(abs(weighted - unweighted))
    assert any(d > 1e-9 for d in differences), (
        "No admissible model has differing weighted vs unweighted L_T; weights "
        "effectively uniform or losses miscomputed."
    )

    # And: the build_dual_set wrapper produces a non-empty surprise-weighted set.
    R_T_prime, _ = build_dual_set(
        admissible, epsilon_T=2.0, epsilon_F=2.0, sample_weights=weights
    )
    assert len(R_T_prime.within_epsilon) > 0


def test_build_dual_set_loss_values_distinguish_admissible_models():
    """For build_dual_set to be meaningful, L_T and L_F must produce different
    rankings on at least some admissible models. Whether R_T and R_F end up
    with literally different membership is data-dependent (small fixtures with
    integer-grained losses often tie); the algorithmic property we can assert
    is that the per-model L_T and L_F values differ for at least one admissible
    model whose predictions are imperfect."""
    from functools import partial

    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=None)
    L_T = partial(grant_emphasis_loss, w_T=5.0)
    L_F = partial(deny_emphasis_loss, w_F=5.0)
    differences = [
        L_T(sr.holdout_y_true, sr.holdout_y_pred)
        - L_F(sr.holdout_y_true, sr.holdout_y_pred)
        for sr in admissible.admissible
    ]
    # At least one model has L_T != L_F (i.e. its missed-grant count differs
    # from its missed-deny count).
    assert any(abs(d) > 1e-9 for d in differences), (
        "All admissible models have L_T == L_F; cost-asymmetric losses cannot "
        "distinguish them. Check loss implementation or use a larger fixture."
    )


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
    assert result.global_best_value == pytest.approx(expected_best)
    assert result.score_label == "auc"
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
    assert eps_result.global_best_value == pytest.approx(admissible_best)


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
        assert eps_set.global_best_value - m.holdout_auc <= 0.10 + 1e-9


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
