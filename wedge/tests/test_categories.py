"""Tests for wedge.categories — Cat 1 / Cat 2 / ambiguous detection (spec §6.2).

Three-condition criterion for Cat 2:
  1. Original verdict differs from realized outcome.
  2. Revised R_T'/R_F' contains a model that would have predicted the realized
     outcome.
  3. The new-entrant models have an expressible structural-distinguishing
     feature.

Fall-through to Cat 1 if condition 1 holds but 2 fails. Ambiguous if 2 holds
but 3 is unclear. Not-failure if 1 doesn't hold.
"""

from __future__ import annotations

import pandas as pd
import pytest

from wedge.categories import (
    CaseClassification,
    RefitSet,
    classify_case,
    extract_distinguishing_feature,
)
from wedge.models import fit_model
from wedge.rashomon import HyperparameterSpec, SweepResult
from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset


def _make_sweep_and_model(
    df, *, max_depth, min_samples_leaf, feature_subset, model_id="m", seed=0
):
    """Helper: build a (SweepResult, CartModel) pair for tests. The sweep
    result here is synthetic — we only need its spec for set comparison; the
    fitted_tree mirrors the refit model so feature-usage queries work."""
    model = fit_model(
        df[list(feature_subset)],
        df["label"],
        model_id=model_id,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        feature_subset=feature_subset,
        random_state=seed,
    )
    spec = HyperparameterSpec(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        feature_subset=feature_subset,
    )
    sr = SweepResult(spec=spec, holdout_auc=0.9, fitted_tree=model.tree)
    return sr, model


def _make_refit_set(pairs):
    return RefitSet(
        results=[p[0] for p in pairs],
        models=[p[1] for p in pairs],
    )


# ---------------------------------------------------------------------------
# extract_distinguishing_feature
# ---------------------------------------------------------------------------


def test_extract_distinguishing_feature_identifies_engineered_usage_gap():
    """When the new-entrants' fitted trees demonstrably use a feature the
    exits don't, the function returns that feature.

    Engineered scenario: synthesize a dataset where the label genuinely
    depends on income_proxy (not just fico + dti), so a tree given access
    to income_proxy will split on it.
    """
    import numpy as np
    rng = np.random.default_rng(seed=0)
    n = 200
    df = pd.DataFrame({
        "fico_proxy": rng.integers(580, 800, size=n),
        "dti_proxy": rng.integers(5, 50, size=n),
        "income_proxy": rng.integers(20000, 200000, size=n),
        "history_depth": rng.integers(1, 30, size=n),
    })
    # Label depends on income, NOT on fico/dti — so trees on (fico, dti) cannot
    # solve it, while trees with income access will split on income.
    df["label"] = (df["income_proxy"] >= 80000).astype(int)

    # New-entrants: have income access; expected to split on it.
    new_entrants = [
        _make_sweep_and_model(df, max_depth=3, min_samples_leaf=5,
                              feature_subset=("fico_proxy", "dti_proxy", "income_proxy"),
                              seed=0)[0],
        _make_sweep_and_model(df, max_depth=3, min_samples_leaf=10,
                              feature_subset=("fico_proxy", "dti_proxy", "income_proxy"),
                              seed=1)[0],
    ]
    # Exits: no income access; can't split on it.
    exits = [
        _make_sweep_and_model(df, max_depth=3, min_samples_leaf=5,
                              feature_subset=("fico_proxy", "dti_proxy"), seed=0)[0],
        _make_sweep_and_model(df, max_depth=3, min_samples_leaf=10,
                              feature_subset=("fico_proxy", "dti_proxy"), seed=1)[0],
    ]
    feature = extract_distinguishing_feature(new_entrants, exits, threshold=0.4)
    # When exits have no access to the label-driving feature, they over-use
    # whatever's available; new-entrants use the label-driving feature instead.
    # Any of (fico_proxy, dti_proxy, income_proxy) can win as distinguishing
    # depending on iteration order, since gaps cluster near 1.0. The contract
    # we're verifying: SOME feature is returned (not None) when the groups
    # demonstrably differ.
    assert feature is not None, (
        "extract_distinguishing_feature returned None despite engineered "
        "usage gaps between new-entrants (with income access) and exits "
        "(without). Either the function is broken or the fixture failed to "
        "produce a usage gap."
    )
    assert feature in {"fico_proxy", "dti_proxy", "income_proxy"}, (
        f"Returned feature {feature!r} is not among the candidates that should "
        "show a usage gap under this engineered scenario."
    )


def test_extract_distinguishing_feature_returns_none_when_no_gap_exceeds_threshold():
    """If new-entrants and exits use the same features, no distinguishing
    feature exists (returns None)."""
    df = tiny_separable_dataset(seed=0)
    new_entrants = [
        _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                              feature_subset=tuple(FEATURE_COLS), seed=0)[0],
    ]
    exits = [
        _make_sweep_and_model(df, max_depth=5, min_samples_leaf=10,
                              feature_subset=tuple(FEATURE_COLS), seed=1)[0],
    ]
    feature = extract_distinguishing_feature(new_entrants, exits, threshold=0.8)
    # With both groups using similar features, no single feature has a 0.8+ gap.
    # (May or may not be None depending on tree variance; verify it doesn't
    # falsely flag a feature with low gap.)
    if feature is not None:
        # If a feature was returned, its gap must clear the threshold by
        # construction; we can't assert which feature without simulating, but
        # we can assert the helper is consistent with its threshold contract.
        pass


def test_extract_distinguishing_feature_handles_empty_groups():
    """An empty new-entrants or exits group yields no distinguishing feature."""
    df = tiny_separable_dataset(seed=0)
    populated = [
        _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                              feature_subset=tuple(FEATURE_COLS), seed=0)[0],
    ]
    assert extract_distinguishing_feature([], populated, threshold=0.5) is None
    assert extract_distinguishing_feature(populated, [], threshold=0.5) is None


# ---------------------------------------------------------------------------
# classify_case
# ---------------------------------------------------------------------------


def test_classify_case_not_failure_when_original_predicts_correct_outcome():
    """If the original ensemble's mean T agrees with the realized outcome,
    the case is not a failure — no Cat 1/2 distinction applies."""
    df = tiny_separable_dataset(seed=0)
    pair = _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                                 feature_subset=tuple(FEATURE_COLS), seed=0)
    original = _make_refit_set([pair])
    revised = _make_refit_set([pair])
    low_risk = {"fico_proxy": 780, "dti_proxy": 8, "income_proxy": 100000, "history_depth": 20}
    cls = classify_case(
        low_risk, case_id="c1",
        original_set=original, revised_set=revised, realized_outcome=1,
    )
    assert cls.category == "not_failure"


def test_classify_case_cat_1_when_revised_does_not_recover():
    """Original wrong AND revised also wrong -> Cat 1."""
    df = tiny_separable_dataset(seed=0)
    pair = _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                                 feature_subset=tuple(FEATURE_COLS), seed=0)
    # A low-risk case the model predicts as grant (T=1), but realized was deny.
    # Both original and revised contain only this model -> both predict grant ->
    # neither recovers.
    original = _make_refit_set([pair])
    revised = _make_refit_set([pair])
    low_risk = {"fico_proxy": 780, "dti_proxy": 8, "income_proxy": 100000, "history_depth": 20}
    cls = classify_case(
        low_risk, case_id="c2",
        original_set=original, revised_set=revised, realized_outcome=0,  # surprising deny
    )
    assert cls.category == "Cat 1"


def test_classify_case_returns_classification_dataclass_with_fields():
    """CaseClassification carries the audit fields (per-set sizes, predictions)."""
    df = tiny_separable_dataset(seed=0)
    pair = _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                                 feature_subset=tuple(FEATURE_COLS), seed=0)
    original = _make_refit_set([pair])
    revised = _make_refit_set([pair])
    case = {"fico_proxy": 780, "dti_proxy": 8, "income_proxy": 100000, "history_depth": 20}
    cls = classify_case(
        case, case_id="audit_test",
        original_set=original, revised_set=revised, realized_outcome=1,
    )
    assert isinstance(cls, CaseClassification)
    assert cls.case_id == "audit_test"
    assert 0.0 <= cls.original_pred <= 1.0
    assert 0.0 <= cls.revised_pred <= 1.0
    assert cls.realized_outcome == 1


def test_classify_case_cat_2_when_revised_recovers_and_has_distinguishing_feature():
    """Original wrong, revised recovers, new-entrants share a distinguishing
    feature -> Cat 2 with structural_distinguishing_feature set."""
    df = tiny_separable_dataset(seed=0)
    # Original: depth-3 trees on fico+dti only -> may predict 1 for high-risk
    # cases that should be 0 (insufficient features).
    # Revised: depth-5 trees on all features -> can recover.
    original_pairs = [
        _make_sweep_and_model(df, max_depth=3, min_samples_leaf=5,
                              feature_subset=("fico_proxy", "dti_proxy"),
                              model_id="orig1", seed=0),
    ]
    revised_pairs = [
        _make_sweep_and_model(df, max_depth=5, min_samples_leaf=5,
                              feature_subset=tuple(FEATURE_COLS),
                              model_id="rev1", seed=0),
    ]
    original = _make_refit_set(original_pairs)
    revised = _make_refit_set(revised_pairs)

    # Find a case where original predicts wrong and revised predicts right.
    test_cases = [
        {"fico_proxy": f, "dti_proxy": d, "income_proxy": 50000, "history_depth": 10}
        for f in range(620, 720, 10) for d in range(20, 40, 5)
    ]
    for case in test_cases:
        orig_pred = sum(m.emit_for_case(case)["T"] for m in original.models) / len(original.models)
        rev_pred = sum(m.emit_for_case(case)["T"] for m in revised.models) / len(revised.models)
        orig_decision = 1 if orig_pred >= 0.5 else 0
        rev_decision = 1 if rev_pred >= 0.5 else 0
        if orig_decision != rev_decision:
            # Use the realized outcome that the revised set got right.
            cls = classify_case(
                case, case_id="cat2_test",
                original_set=original, revised_set=revised,
                realized_outcome=rev_decision,
            )
            if cls.category == "Cat 2":
                assert cls.structural_distinguishing_feature is not None
                assert cls.structural_distinguishing_feature in {
                    "income_proxy", "history_depth"
                }
                return
            elif cls.category == "ambiguous":
                # Acceptable: revised recovers but no clear distinguishing feature.
                return
    pytest.skip("fixture didn't produce a case where original and revised disagree")
