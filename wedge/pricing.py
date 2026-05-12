"""Pricing-space dual-set analog: within-grade stratification (spec extension).

The binary wedge asks "is there a policy-admissible model that recovers the
realized verdict on a held-out case?" — and on every substrate tried, the
answer is no (zero Cat 2). This module asks the *pricing-tier* version:

    For each lender-assigned risk tier (sub-grade), is there a
    policy-expressible feature that partitions the tier's loans into
    sub-populations with significantly different *realized* default rates?

A significant split means the grade conflated loans that the policy
vocabulary could distinguish — the pricing-space Cat 2 analog. The dual
structure:

  - Original construction = the grade as given: every loan in tier g carries
    the tier's pooled realized default rate.
  - Revised construction = the grade plus the recovered split: tier g is
    refined along the most-discriminating policy-expressible feature.
  - Cat 2 (pricing) = a significant policy-expressible split exists → "a
    factor in the documented vocabulary that the grade should have used."
  - Cat 2-extension (pricing) = a significant split exists but only on a
    feature NOT in the policy vocabulary → "the policy should name this
    factor."
  - Cat 1 (pricing) = adequate power, no significant split → "the grade is
    already as fine as the governed vocabulary allows."
  - underpowered = too few loans in the tier to test.

Why this dodges the binary mechanism's data-availability problem: the test
runs over *granted* loans only, all of which have realized outcomes. There
is no "denied applicant whose performance we can't observe" — the
counterfactual ("what if the tier had been finer") is over the same
population we observe.

Statistics: two-sided pooled two-proportion z-test on the default-rate
difference per (grade, feature, threshold); Benjamini-Hochberg FDR control
across all tests at level `alpha`. Threshold candidates are the within-grade
deciles of each feature; thresholds where either side falls below
`min_loans_per_side` are skipped. Grades below `min_loans_per_grade` are
"underpowered" and not tested.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal, Optional

import numpy as np
import pandas as pd


PricingCategory = Literal[
    "Cat 2 (pricing)",
    "Cat 2-extension (pricing)",
    "Cat 1 (pricing)",
    "underpowered",
]


# ---------------------------------------------------------------------------
# Grade-level pooled default rates
# ---------------------------------------------------------------------------
def grade_default_rates(
    df: pd.DataFrame, *, grade_col: str, label_col: str
) -> dict[str, float]:
    """Pooled realized default rate per grade.

    Label convention is grant-as-positive (1 = paid, 0 = charged off), so
    the default rate of a grade is `mean(label == 0)` over its loans.
    """
    out: dict[str, float] = {}
    for g, sub in df.groupby(grade_col):
        out[str(g)] = float((sub[label_col] == 0).mean())
    return out


# ---------------------------------------------------------------------------
# Two-proportion z-test (no scipy dependency; p-value via math.erfc)
# ---------------------------------------------------------------------------
def _two_proportion_pvalue(
    n1: int, k1: int, n2: int, k2: int
) -> float:
    """Two-sided p-value for H0: p1 == p2, pooled-variance z-test.

    n1, n2: group sizes. k1, k2: "success" counts (here: default counts).
    Returns 1.0 when the pooled rate is 0 or 1 (no variance, no signal).
    """
    if n1 == 0 or n2 == 0:
        return 1.0
    p1 = k1 / n1
    p2 = k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    if p_pool <= 0.0 or p_pool >= 1.0:
        return 1.0
    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return 1.0
    z = (p1 - p2) / se
    # Two-sided: P(|Z| > |z|) = erfc(|z| / sqrt(2)).
    return math.erfc(abs(z) / math.sqrt(2.0))


def _benjamini_hochberg(pvalues: list[float], alpha: float) -> list[bool]:
    """Return a boolean mask of rejections under BH FDR control at `alpha`."""
    m = len(pvalues)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvalues[i])
    reject = [False] * m
    max_k = -1
    for rank, idx in enumerate(order, start=1):
        if pvalues[idx] <= (rank / m) * alpha:
            max_k = rank
    if max_k > 0:
        for rank, idx in enumerate(order, start=1):
            if rank <= max_k:
                reject[idx] = True
    return reject


# ---------------------------------------------------------------------------
# Within-grade splits
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WithinGradeSplit:
    """A significant within-grade default-rate partition along one feature."""

    grade: str
    feature: str
    threshold: float
    n_lo: int  # loans with feature <= threshold
    n_hi: int  # loans with feature > threshold
    default_rate_lo: float
    default_rate_hi: float
    p_value: float
    policy_expressible: bool

    @property
    def gap(self) -> float:
        """Absolute default-rate difference between the two sides."""
        return abs(self.default_rate_hi - self.default_rate_lo)


def _decile_thresholds(values: np.ndarray) -> list[float]:
    """Within-grade decile cut points (10th..90th percentiles), de-duplicated."""
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return []
    qs = np.quantile(finite, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    seen: list[float] = []
    for q in qs:
        qf = float(q)
        if not seen or abs(qf - seen[-1]) > 1e-12:
            seen.append(qf)
    return seen


def find_within_grade_splits(
    df: pd.DataFrame,
    *,
    grade_col: str,
    label_col: str,
    feature_cols: Iterable[str],
    policy_features: set[str],
    alpha: float = 0.01,
    min_loans_per_grade: int = 200,
    min_loans_per_side: int = 100,
) -> list[WithinGradeSplit]:
    """Find statistically significant within-grade default-rate partitions.

    For each grade with at least `min_loans_per_grade` loans, for each feature
    in `feature_cols`, test the default-rate difference across that feature's
    within-grade deciles (skipping thresholds where either side has fewer than
    `min_loans_per_side` loans). Apply Benjamini-Hochberg FDR control at
    `alpha` across all (grade, feature, threshold) tests; return the
    significant splits.

    `policy_features` is the set of feature names the documented policy names;
    each returned split is tagged `policy_expressible` accordingly.
    """
    feature_cols = list(feature_cols)
    candidates: list[dict[str, Any]] = []
    pvals: list[float] = []

    for g, sub in df.groupby(grade_col):
        if len(sub) < min_loans_per_grade:
            continue
        is_default = (sub[label_col] == 0).to_numpy()
        for feat in feature_cols:
            if feat not in sub.columns:
                continue
            vals = pd.to_numeric(sub[feat], errors="coerce").to_numpy()
            for thr in _decile_thresholds(vals):
                lo_mask = np.isfinite(vals) & (vals <= thr)
                hi_mask = np.isfinite(vals) & (vals > thr)
                n_lo = int(lo_mask.sum())
                n_hi = int(hi_mask.sum())
                if n_lo < min_loans_per_side or n_hi < min_loans_per_side:
                    continue
                k_lo = int(is_default[lo_mask].sum())
                k_hi = int(is_default[hi_mask].sum())
                p = _two_proportion_pvalue(n_lo, k_lo, n_hi, k_hi)
                candidates.append(
                    dict(
                        grade=str(g),
                        feature=feat,
                        threshold=float(thr),
                        n_lo=n_lo,
                        n_hi=n_hi,
                        default_rate_lo=k_lo / n_lo,
                        default_rate_hi=k_hi / n_hi,
                        p_value=p,
                        policy_expressible=feat in policy_features,
                    )
                )
                pvals.append(p)

    rejected = _benjamini_hochberg(pvals, alpha)
    return [
        WithinGradeSplit(**c) for c, r in zip(candidates, rejected) if r
    ]


# ---------------------------------------------------------------------------
# Grade stratification bundle + classification
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GradeStratification:
    """Per-grade stratification result: pooled rate, loan count, significant
    splits. The atomic object the pricing-space classification reads.
    """

    grade_loan_counts: dict[str, int]
    grade_default_rate: dict[str, float]
    splits: list[WithinGradeSplit]
    min_loans_per_grade: int
    policy_features: frozenset[str]

    @classmethod
    def compute(
        cls,
        df: pd.DataFrame,
        *,
        grade_col: str,
        label_col: str,
        feature_cols: Iterable[str],
        policy_features: set[str],
        alpha: float = 0.01,
        min_loans_per_grade: int = 200,
        min_loans_per_side: int = 100,
    ) -> "GradeStratification":
        counts = {str(g): int(len(sub)) for g, sub in df.groupby(grade_col)}
        rates = grade_default_rates(df, grade_col=grade_col, label_col=label_col)
        splits = find_within_grade_splits(
            df,
            grade_col=grade_col,
            label_col=label_col,
            feature_cols=feature_cols,
            policy_features=policy_features,
            alpha=alpha,
            min_loans_per_grade=min_loans_per_grade,
            min_loans_per_side=min_loans_per_side,
        )
        return cls(
            grade_loan_counts=counts,
            grade_default_rate=rates,
            splits=splits,
            min_loans_per_grade=min_loans_per_grade,
            policy_features=frozenset(policy_features),
        )

    def splits_for(self, grade: str) -> list[WithinGradeSplit]:
        return [s for s in self.splits if s.grade == grade]


def classify_grades(strat: GradeStratification) -> dict[str, PricingCategory]:
    """Classify each grade per the pricing-space Cat 1 / Cat 2 criterion.

    - "underpowered"             : fewer than `min_loans_per_grade` loans.
    - "Cat 2 (pricing)"          : ≥1 significant split on a policy feature.
    - "Cat 2-extension (pricing)": significant split(s) only on non-policy
                                   features.
    - "Cat 1 (pricing)"          : adequate power, no significant split.
    """
    out: dict[str, PricingCategory] = {}
    for grade, n in strat.grade_loan_counts.items():
        if n < strat.min_loans_per_grade:
            out[grade] = "underpowered"
            continue
        gsplits = strat.splits_for(grade)
        if not gsplits:
            out[grade] = "Cat 1 (pricing)"
        elif any(s.policy_expressible for s in gsplits):
            out[grade] = "Cat 2 (pricing)"
        else:
            out[grade] = "Cat 2-extension (pricing)"
    return out
