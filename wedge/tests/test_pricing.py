"""Tests for the pricing-space dual-set analog (within-grade stratification).

The mechanism: for each lender-assigned risk tier (sub_grade), test whether a
policy-expressible feature partitions the tier's loans into sub-populations
with significantly different *realized* default rates. A significant split
means the grade conflated loans that the policy vocabulary could distinguish
— the pricing-space Cat 2 analog. No significant split (with adequate power)
means the grade is as fine as the governed vocabulary allows — Cat 1.

These tests use a synthetic graded fixture with a *planted* within-grade
split, so we can check the mechanism recovers a known signal and does not
fabricate one where there is none.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from wedge.pricing import (
    GradeStratification,
    WithinGradeSplit,
    classify_grades,
    find_within_grade_splits,
    grade_default_rates,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _planted_split_dataset(seed: int = 0) -> pd.DataFrame:
    """Two sub-grades. Grade 'B2' is homogeneous (no within-grade structure).
    Grade 'C3' is conflated: loans with dti <= 25 default at ~5%, loans with
    dti > 25 default at ~20% — a feature the grade should have separated.

    Label convention: grant-as-positive (1 = fully paid, 0 = charged off);
    default rate = mean(label == 0).
    """
    rng = np.random.default_rng(seed)
    rows = []
    # Grade B2: 2000 loans, uniform 8% default, dti spread but uncorrelated.
    for _ in range(2000):
        dti = rng.uniform(5, 40)
        fico = rng.integers(680, 740)
        label = 0 if rng.random() < 0.08 else 1
        rows.append(dict(sub_grade="B2", dti=dti, fico_range_low=fico, label=label))
    # Grade C3: 2000 loans, default rate depends on dti (planted split at 25).
    for _ in range(2000):
        dti = rng.uniform(5, 40)
        fico = rng.integers(640, 700)
        p_default = 0.05 if dti <= 25 else 0.20
        label = 0 if rng.random() < p_default else 1
        rows.append(dict(sub_grade="C3", dti=dti, fico_range_low=fico, label=label))
    return pd.DataFrame(rows)


def _homogeneous_dataset(seed: int = 0) -> pd.DataFrame:
    """One sub-grade, 3000 loans, uniform 10% default, no feature structure."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(3000):
        rows.append(
            dict(
                sub_grade="A4",
                dti=rng.uniform(5, 40),
                fico_range_low=rng.integers(720, 800),
                label=0 if rng.random() < 0.10 else 1,
            )
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# grade_default_rates
# ---------------------------------------------------------------------------
def test_grade_default_rates_basic():
    df = _planted_split_dataset(seed=1)
    rates = grade_default_rates(df, grade_col="sub_grade", label_col="label")
    assert set(rates.keys()) == {"B2", "C3"}
    # B2 ≈ 8%, C3 ≈ 12.5% (average of 5% and 20%).
    assert 0.05 < rates["B2"] < 0.12
    assert 0.09 < rates["C3"] < 0.18


# ---------------------------------------------------------------------------
# find_within_grade_splits — recovers the planted signal
# ---------------------------------------------------------------------------
def test_finds_planted_split():
    df = _planted_split_dataset(seed=2)
    splits = find_within_grade_splits(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"dti", "fico_range_low"},
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    # There must be at least one significant split, on dti, in grade C3.
    c3_dti_splits = [s for s in splits if s.grade == "C3" and s.feature == "dti"]
    assert c3_dti_splits, "mechanism failed to recover the planted dti split in C3"
    best = max(c3_dti_splits, key=lambda s: abs(s.default_rate_hi - s.default_rate_lo))
    assert best.policy_expressible is True
    # The recovered split should land near the planted threshold (25).
    assert 18 <= best.threshold <= 32
    # And the default-rate gap should be substantial (planted 5% vs 20%).
    assert abs(best.default_rate_hi - best.default_rate_lo) > 0.08


def test_no_split_in_homogeneous_grade():
    """A grade with no within-grade structure yields no significant splits."""
    df = _homogeneous_dataset(seed=3)
    splits = find_within_grade_splits(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"dti", "fico_range_low"},
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    assert splits == [], f"fabricated splits in a homogeneous grade: {splits}"


def test_b2_grade_has_no_split_but_c3_does():
    """In the planted dataset, B2 is clean and C3 is conflated."""
    df = _planted_split_dataset(seed=4)
    splits = find_within_grade_splits(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"dti", "fico_range_low"},
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    grades_with_splits = {s.grade for s in splits}
    assert "C3" in grades_with_splits
    assert "B2" not in grades_with_splits


# ---------------------------------------------------------------------------
# policy-expressibility filter
# ---------------------------------------------------------------------------
def test_policy_expressibility_flag():
    """A split on a feature not in the policy vocabulary is flagged
    policy_expressible=False (a Cat-2-extension signal: the policy should
    name this feature)."""
    df = _planted_split_dataset(seed=5)
    splits = find_within_grade_splits(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"fico_range_low"},  # dti is NOT in the policy here
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    c3_dti = [s for s in splits if s.grade == "C3" and s.feature == "dti"]
    assert c3_dti
    assert all(s.policy_expressible is False for s in c3_dti)


# ---------------------------------------------------------------------------
# classify_grades — Cat 1 / Cat 2 (pricing)
# ---------------------------------------------------------------------------
def test_classify_grades_cat2_and_cat1():
    df = _planted_split_dataset(seed=6)
    strat = GradeStratification.compute(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"dti", "fico_range_low"},
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    classes = classify_grades(strat)
    # C3 is conflated along a policy feature -> "Cat 2 (pricing)".
    assert classes["C3"] == "Cat 2 (pricing)"
    # B2 has no significant split with adequate power -> "Cat 1 (pricing)".
    assert classes["B2"] == "Cat 1 (pricing)"


def test_classify_underpowered_grade():
    """A grade with too few loans is 'underpowered', not Cat 1."""
    rng = np.random.default_rng(7)
    rows = [
        dict(sub_grade="G5", dti=rng.uniform(5, 40), fico_range_low=620, label=int(rng.random() > 0.3))
        for _ in range(50)
    ]
    df = pd.DataFrame(rows)
    strat = GradeStratification.compute(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"dti", "fico_range_low"},
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    classes = classify_grades(strat)
    assert classes["G5"] == "underpowered"


def test_classify_cat2_extension_when_only_nonpolicy_feature_splits():
    """If the only significant split is on a non-policy feature, the grade is
    'Cat 2-extension (pricing)' — the recovered factor isn't in the policy
    vocabulary, so the action is 'amend the policy', not 'use the policy
    better'."""
    df = _planted_split_dataset(seed=8)
    strat = GradeStratification.compute(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=["dti", "fico_range_low"],
        policy_features={"fico_range_low"},  # dti not in policy
        alpha=0.01,
        min_loans_per_grade=200,
        min_loans_per_side=100,
    )
    classes = classify_grades(strat)
    assert classes["C3"] == "Cat 2-extension (pricing)"
