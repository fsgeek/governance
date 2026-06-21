import numpy as np
import pandas as pd
import pytest

from wedge.age_residual import (
    assign_age_band,
    band_label,
    AGE_BANDS,
    REFERENCE_BAND_INDEX,
    fit_band_residuals,
    fit_poly_age,
    within_tenure_residuals,
    collinearity_diagnostics,
    orthogonalized_age_residual,
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


def test_poly_age_runs_and_returns_finite_bps():
    df = _synth(planted_young_bps=30.0)
    df["est_age"] = df["age"]
    out = fit_poly_age(df)
    # A single planted band is not a true parabola; we only assert the quadratic model RUNS
    # and returns finite coefficients. Curvature is read in the artifact, not unit-asserted.
    assert np.isfinite(out["est_age_coef_bps"])
    assert np.isfinite(out["est_age_sq_coef_bps"])
    assert 0.0 <= out["r2"] <= 1.0


def test_within_tenure_returns_a_result_per_bin():
    df = _synth(planted_young_bps=30.0)
    df["est_age"] = df["age"]
    bins = within_tenure_residuals(df, n_tenure_bins=4)
    # qcut with duplicates="drop" may yield fewer than n_tenure_bins if tenure has ties at
    # quantile boundaries; assert we get multiple strata, each a usable BandResult.
    assert len(bins) >= 2
    for r in bins.values():
        assert hasattr(r, "band_bps")
        assert hasattr(r, "reference_band")


def test_collinearity_reports_vif_and_corr():
    df = _synth()
    df["est_age"] = df["age"]
    diag = collinearity_diagnostics(df)
    assert set(diag["vif"]).issuperset({"fico_mid", "dti"})
    assert "fico_mid" in diag["corr_with_est_age"]
    # synthetic controls are independent of age -> low corr
    assert abs(diag["corr_with_est_age"]["fico_mid"]) < 0.1


def test_orthogonalized_age_recovers_planted_young_premium():
    # Cell C: residualize est_age on controls, then price-on-age-residual by band.
    # With age independent of controls (synthetic), orthogonalization changes little and the
    # planted +30bps on the young band must still surface.
    df = _synth(planted_young_bps=30.0)
    df["est_age"] = df["age"]
    res = orthogonalized_age_residual(df)
    assert abs(res.band_bps[0] - 30.0) < 8.0, f"expected ~30bps, got {res.band_bps[0]:.1f}"
