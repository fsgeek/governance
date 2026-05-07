"""Boundary-extending synthetic collector.

For the wedge, the simplest realization of the synthetic-data pipeline:
sample each feature independently from the real-data marginal extended
into the rejected region by a configurable factor on the lower tail of
risk-relevant features. Real-data marginals preserve overall shape;
the lower-tail extension produces synthetic cases that look like
plausibly-rejected applicants.

This is *demonstration / hypothetical-scenario* validity-grade per the
May-6 synthetic/real-data taxonomy. It cannot support back-testing claims
or any claim that requires real outcome data. Each case is tagged
origin="synthetic", synthetic_role="hypothetical-scenario".

Better calibration (copulas, joint distribution preservation) is iteration 2.
"""

from __future__ import annotations

import uuid

import numpy as np
import pandas as pd

from wedge.types import Case


# Features for which we extend the lower tail (more risk-shaped values
# downward). For other features we sample from the real marginal directly.
# Both fixture names (fico_proxy, dti_proxy) and real LendingClub column
# names (fico_range_low, dti) are included so the extension fires on both
# test data and real LC data without any caller-side configuration.
RISK_FEATURES_LOWER_EXTENSION = ("fico_proxy", "fico_range_low")
RISK_FEATURES_UPPER_EXTENSION = ("dti_proxy", "dti")
DEFAULT_LOWER_EXTENSION_PCT = 0.10  # extend by 10% of feature range below real min
DEFAULT_UPPER_EXTENSION_PCT = 0.10  # extend by 10% above real max


def _extended_uniform(
    rng: np.random.Generator,
    n: int,
    real_min: float,
    real_max: float,
    *,
    lower_extension_pct: float = 0.0,
    upper_extension_pct: float = 0.0,
) -> np.ndarray:
    span = real_max - real_min
    lo = real_min - span * lower_extension_pct
    hi = real_max + span * upper_extension_pct
    return rng.uniform(lo, hi, size=n)


def generate_boundary_cases(
    real: pd.DataFrame,
    *,
    n: int,
    vintage: str,
    seed: int = 0,
    lower_extension_pct: float = DEFAULT_LOWER_EXTENSION_PCT,
    upper_extension_pct: float = DEFAULT_UPPER_EXTENSION_PCT,
    lower_extension_features: tuple[str, ...] = RISK_FEATURES_LOWER_EXTENSION,
    upper_extension_features: tuple[str, ...] = RISK_FEATURES_UPPER_EXTENSION,
) -> list[Case]:
    """Generate `n` synthetic cases calibrated to real's marginals, extending
    the lower tail of lower_extension_features and the upper tail of
    upper_extension_features.

    Parameters
    ----------
    real : the real-data DataFrame whose marginals we sample from.
    n    : number of synthetic cases to generate.
    vintage : vintage tag attached to each synthetic case (matches the real
              dataset's vintage; we are extending the same vintage's
              hypothetical population, not generating cross-vintage data).
    seed : RNG seed for reproducibility. Note: results are reproducible
           only when `real` has the same column order across calls; the
           per-column loop consumes RNG state in column order.
    lower_extension_pct : fraction of the feature range to extend below
           the real-data minimum for columns listed in lower_extension_features.
    upper_extension_pct : fraction of the feature range to extend above
           the real-data maximum for columns listed in upper_extension_features.
    lower_extension_features : columns to extend into the lower tail. Defaults
           to RISK_FEATURES_LOWER_EXTENSION, which covers both the test fixture
           name ('fico_proxy') and the real LC schema name ('fico_range_low').
    upper_extension_features : columns to extend into the upper tail. Defaults
           to RISK_FEATURES_UPPER_EXTENSION, which covers both the test fixture
           name ('dti_proxy') and the real LC schema name ('dti').
    """
    if real.empty:
        raise ValueError(
            "generate_boundary_cases: real DataFrame is empty; "
            "cannot estimate marginals with no rows."
        )
    rng = np.random.default_rng(seed)
    feature_cols = [c for c in real.columns if c != "label"]
    samples = {}
    for col in feature_cols:
        real_col = real[col].astype(float)
        lower_pct = lower_extension_pct if col in lower_extension_features else 0.0
        upper_pct = upper_extension_pct if col in upper_extension_features else 0.0
        samples[col] = _extended_uniform(
            rng,
            n,
            real_min=float(real_col.min()),
            real_max=float(real_col.max()),
            lower_extension_pct=lower_pct,
            upper_extension_pct=upper_pct,
        )
    cases: list[Case] = []
    for i in range(n):
        features = {col: float(samples[col][i]) for col in feature_cols}
        cases.append(
            Case(
                case_id=str(uuid.uuid4()),
                origin="synthetic",
                synthetic_role="hypothetical-scenario",
                vintage=vintage,
                features=features,
                label=None,
                per_model=[],
            )
        )
    return cases
