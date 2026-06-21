import numpy as np
import pandas as pd
import pytest

from wedge.age_residual import (
    assign_age_band,
    band_label,
    AGE_BANDS,
    REFERENCE_BAND_INDEX,
    fit_band_residuals,
)


def _synth(n=60000, planted_young_bps=30.0, seed=0):
    """Synthetic LC-like data with a KNOWN premium planted on the youngest band only.

    Controls are drawn independently of age and genuinely drive the lawful price, so a
    correct residualization must attribute the planted bps to age (not absorb it into
    controls). This is the positive control against the confabulation failure mode.
    """
    rng = np.random.default_rng(seed)
    age = rng.uniform(18, 95, n)
    fico_mid = rng.uniform(640, 820, n)
    dti = rng.uniform(0, 35, n)
    annual_inc = rng.uniform(20000, 200000, n)
    loan_amnt = rng.uniform(1000, 40000, n)
    term_months = rng.choice([36, 60], n)
    purpose = rng.choice(["debt_consolidation", "credit_card", "home_improvement"], n)
    # lawful price: a real function of controls (so controls are NOT inert)
    base = 5.0 + (820 - fico_mid) * 0.02 + dti * 0.05 + (term_months == 60) * 1.5
    noise = rng.normal(0, 0.5, n)
    int_rate = base + noise
    band = np.array([assign_age_band(a) for a in age])
    int_rate = int_rate + (band == 0) * (planted_young_bps / 100.0)  # +Xbps on youngest only
    return pd.DataFrame(
        dict(age=age, fico_mid=fico_mid, dti=dti, annual_inc=annual_inc,
             loan_amnt=loan_amnt, term_months=term_months, purpose=purpose,
             int_rate=int_rate, age_band=band)
    )


def test_assign_age_band_boundaries():
    assert assign_age_band(18) == 0
    assert assign_age_band(24.9) == 0
    assert assign_age_band(25) == 1
    assert assign_age_band(47) == 5          # [45,50) is the 6th band, index 5
    assert assign_age_band(70) == 9          # [70,95]
    assert assign_age_band(95) == 9          # right edge inclusive on last band
    assert assign_age_band(17) == -1
    assert assign_age_band(96) == -1


def test_reference_band_is_45_50():
    lo, hi = AGE_BANDS[REFERENCE_BAND_INDEX]
    assert (lo, hi) == (45, 50)
    assert band_label(REFERENCE_BAND_INDEX) == "[45,50)"


def test_positive_control_recovers_planted_young_premium():
    df = _synth(planted_young_bps=30.0)
    res = fit_band_residuals(df)
    assert abs(res.band_bps[0] - 30.0) < 6.0, f"expected ~30bps, got {res.band_bps[0]:.1f}"
    # a band with NO planted premium should be near zero
    assert abs(res.band_bps[4]) < 8.0, f"unplanted band should be ~0, got {res.band_bps[4]:.1f}"
    # reference band residual is identically 0 by construction
    assert res.band_bps[REFERENCE_BAND_INDEX] == 0.0
