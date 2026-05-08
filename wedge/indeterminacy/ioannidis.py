"""Ioannidis-suspicion indeterminacy species (battery).

Tests for fingerprints of suspicious provenance in the case's data: data that
is too clean, too round, or too neatly aligned with policy thresholds to have
been drawn from a smooth underlying generative process. Named after Ioannidis'
work on detecting fabricated or manipulated research data ("Why Most Published
Research Findings Are False"; subsequent forensics literature on p-curves,
Benford's law, and rounding patterns).

This module is a *battery* — individual tests are emitted as separate
IndeterminacyComponents under Case.case_indeterminacy. Per the
2026-05-08 memo, aggregation is deferred until empirical observation tells us
which combinations are most informative.

Tests implemented in this iteration:
  - round_numbers: detects suspiciously round annual_inc values
  - threshold_hugging: detects DTI values landing exactly on regulatory or
    underwriting policy thresholds

Tests deferred and why:
  - internal_coherence: needs cross-field plausibility checks; with only
    FICO/DTI/income/emp_length the scaffolding is too thin for strong
    detection. Add when broader feature pool is available.
  - benford: fundamentally a corpus-level test; single-value Benford scoring
    is meaningless. Compute as run-level diagnostic in the analysis pass.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from wedge.types import FactorSupportEntry, IndeterminacyComponent


# Common DTI cutoffs in unsecured consumer lending. 30/35/40/45/50 are
# round percentages used as internal underwriting policy lines; 36 is the
# Fannie Mae back-end target; 43 is the QM (Qualified Mortgage) rule
# threshold widely adopted as a soft cap in non-mortgage products too.
DTI_THRESHOLDS: tuple[float, ...] = (30.0, 35.0, 36.0, 40.0, 43.0, 45.0, 50.0)
DTI_THRESHOLD_TOL: float = 0.05  # LC publishes DTI to 2 decimals; this is a tight band

# Round-number tiers for annual_inc, ordered most-to-least suspicious.
# Multiples of 25000 are rare under a smooth income distribution and are a
# strong signal of self-reported rounding; multiples of 1000 are common
# because most people report whole-thousand income but still informative
# at population scale.
INCOME_TIERS: tuple[tuple[int, float], ...] = (
    (25000, 1.0),
    (10000, 0.6),
    (5000, 0.3),
    (1000, 0.1),
)
INCOME_DIVISIBILITY_TOL: float = 0.5  # LC incomes are typically integer; tolerate float noise


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(v):
        return None
    return v


def _is_multiple(value: float, divisor: int, tol: float = INCOME_DIVISIBILITY_TOL) -> bool:
    if divisor <= 0:
        return False
    quotient = round(value / divisor)
    return abs(value - quotient * divisor) < tol


def compute_round_numbers(case_features: dict[str, Any]) -> IndeterminacyComponent:
    """Score annual_inc for round-number suspicion.

    Returns the score corresponding to the largest divisor the income is a
    multiple of; the direction tag identifies which tier fired.
    """
    inc = _safe_float(case_features.get("annual_inc"))
    if inc is None or inc <= 0:
        return IndeterminacyComponent(
            species="ioannidis_round_numbers",
            score=0.0,
            factor_support=[],
            direction="missing",
        )
    for divisor, score in INCOME_TIERS:
        if _is_multiple(inc, divisor):
            return IndeterminacyComponent(
                species="ioannidis_round_numbers",
                score=score,
                factor_support=[FactorSupportEntry(feature="annual_inc", weight=score)],
                direction=f"multiple_of_{divisor}",
            )
    return IndeterminacyComponent(
        species="ioannidis_round_numbers",
        score=0.0,
        factor_support=[],
        direction="irregular",
    )


def compute_threshold_hugging(case_features: dict[str, Any]) -> IndeterminacyComponent:
    """Score DTI for proximity to known regulatory / underwriting thresholds.

    Score is binary: 1.0 if DTI lies within DTI_THRESHOLD_TOL of any
    threshold; 0.0 otherwise. Direction tag identifies which threshold.
    """
    dti = _safe_float(case_features.get("dti"))
    if dti is None:
        return IndeterminacyComponent(
            species="ioannidis_threshold_hugging",
            score=0.0,
            factor_support=[],
            direction="missing",
        )
    for threshold in DTI_THRESHOLDS:
        if abs(dti - threshold) <= DTI_THRESHOLD_TOL:
            return IndeterminacyComponent(
                species="ioannidis_threshold_hugging",
                score=1.0,
                factor_support=[FactorSupportEntry(feature="dti", weight=1.0)],
                direction=f"at_threshold_{threshold:.0f}",
            )
    return IndeterminacyComponent(
        species="ioannidis_threshold_hugging",
        score=0.0,
        factor_support=[],
        direction="off_threshold",
    )


def compute_battery(case_features: dict[str, Any]) -> list[IndeterminacyComponent]:
    """Run the full battery on a case; return one IndeterminacyComponent per test."""
    return [
        compute_round_numbers(case_features),
        compute_threshold_hugging(case_features),
    ]
