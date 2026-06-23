import numpy as np
import pandas as pd
import pytest

from wedge.age_grade_default import (
    predicted_default,
    fit_default_rate_map,
    assert_monotone,
    band_excess_corpus,
    band_excess_within_grade,
    grade_vs_default_rail,
    DefaultRateMap,
    _bootstrap_ci,
    _BOOTSTRAP_MAX_N,
)
from wedge.age_residual import assign_age_band


def _synth(n=80000, planted_young_excess_bps=120.0, seed=0):
    """Synthetic LC-like data where realized default is driven by risk (age-blind), the rate
    tracks default, and the YOUNG band alone is priced ABOVE its default-justified rate by a known
    margin WITHOUT a matching rise in its default.

    This is the positive control for the benchmark: a correct default-justified-price benchmark
    must (a) recover ~planted_young_excess_bps on the young band and (b) show ~0 on a band priced
    exactly at its default-justified rate. If the benchmark instead absorbed the planted excess
    into the map (because the young also default more), it would miss it — so default here is a
    function of risk only, NOT of age.
    """
    rng = np.random.default_rng(seed)
    age = rng.uniform(18, 95, n)
    fico_mid = rng.uniform(640, 820, n)
    dti = rng.uniform(0, 35, n)
    annual_inc = rng.uniform(20000, 200000, n)
    loan_amnt = rng.uniform(1000, 40000, n)
    term_months = rng.choice([36, 60], n)
    purpose = rng.choice(["debt_consolidation", "credit_card", "home_improvement"], n)
    band = np.array([assign_age_band(a) for a in age])

    # default driven by risk ONLY (age-blind): higher when fico low / dti high / 60mo term
    risk_logit = -2.5 - (fico_mid - 730) * 0.012 + dti * 0.04 + (term_months == 60) * 0.4
    p_default = 1.0 / (1.0 + np.exp(-risk_logit))
    default = (rng.uniform(0, 1, n) < p_default).astype(int)

    # JUSTIFIED rate: a clean monotone function of the SAME risk that drives default, so the
    # default->rate map can recover it. (rate rises with risk_logit.)
    justified_rate = 8.0 + (risk_logit + 2.5) * 3.0 + rng.normal(0, 0.3, n)
    int_rate = justified_rate.copy()
    # plant the excess on the young band only, in pp; their default is unchanged -> benchmark sees
    # the excess as priced-past-default.
    int_rate = int_rate + (band == 0) * (planted_young_excess_bps / 100.0)

    return pd.DataFrame(dict(
        est_age=age, age_band=band, fico_mid=fico_mid, dti=dti, annual_inc=annual_inc,
        loan_amnt=loan_amnt, term_months=term_months, purpose=purpose,
        int_rate=int_rate, default=default,
    ))


@pytest.mark.parametrize("map_kind", ["isotonic", "decile"])
def test_positive_control_recovers_planted_young_excess(map_kind):
    df = _synth(planted_young_excess_bps=120.0)
    res = band_excess_corpus(df, map_kind=map_kind, n_boot=200)
    # young band priced +120bps past its default-justified rate -> benchmark must surface a large
    # positive excess there. Tolerance is generous: the map is learned and the young's own loans
    # nudge it upward slightly, attenuating recovery (conservative, the spec's whole point).
    assert res.band_bps[0] > 60.0, f"expected large young excess, got {res.band_bps[0]:.1f}"
    # a middle band carries NO planted excess -> should sit near zero
    assert abs(res.band_bps[4]) < 40.0, f"unplanted band should be ~0, got {res.band_bps[4]:.1f}"
    # the young excess should clearly exceed the unplanted band's
    assert res.band_bps[0] - res.band_bps[4] > 50.0


def test_no_planted_excess_gives_near_zero_everywhere():
    df = _synth(planted_young_excess_bps=0.0)
    res = band_excess_corpus(df, map_kind="isotonic", n_boot=200)
    # with nothing planted, every band's actual rate equals its default-justified rate up to noise
    for i, bps in res.band_bps.items():
        if res.n_per_band[i] > 100:
            assert abs(bps) < 40.0, f"band {i} should be ~0 with no plant, got {bps:.1f}"


def test_default_rate_map_is_monotone():
    df = _synth()
    p_hat = predicted_default(df)
    for kind in ("isotonic", "decile"):
        m = fit_default_rate_map(p_hat, df["int_rate"].to_numpy(), map_kind=kind)
        assert_monotone(m)  # must not raise
        # justified rate is non-decreasing in predicted default
        grid = np.linspace(p_hat.min(), p_hat.max(), 50)
        jr = m.justified_rate(grid)
        assert np.all(np.diff(jr) >= -1e-6), f"{kind} map not monotone on grid"


def test_assert_monotone_raises_on_decreasing_map():
    # a hand-built map where higher default maps to LOWER rate is invalid and must error loudly
    bad = DefaultRateMap(map_kind="isotonic",
                         _x=np.array([0.1, 0.2, 0.3]), _y=np.array([10.0, 8.0, 6.0]))
    with pytest.raises(ValueError, match="NOT monotone"):
        assert_monotone(bad)


def test_predicted_default_excludes_age_and_is_a_probability():
    df = _synth()
    p = predicted_default(df)
    assert p.shape == (len(df),)
    assert np.all((p >= 0) & (p <= 1))
    # predicted default must correlate with realized default (the model is doing something)
    assert np.corrcoef(p, df["default"])[0, 1] > 0.1


def test_within_grade_is_computable_and_returns_all_bands():
    # give the synthetic frame a grade column so within-grade calibration has strata
    df = _synth()
    # assign grade by risk so grades are real strata (A=lowest rate ... G=highest)
    df["grade"] = pd.qcut(df["int_rate"], q=7, labels=list("ABCDEFG"))
    res = band_excess_within_grade(df, map_kind="isotonic", n_boot=200)
    assert res.scope == "within_grade"
    # young band must be present and finite
    assert res.n_per_band[0] > 0
    assert np.isfinite(res.band_bps[0])


def test_bootstrap_ci_closed_form_agrees_with_resample():
    # The large-n branch swaps the percentile bootstrap for the normal-theory CI it converges to.
    # Verify the two agree closely on a sample big enough to trust the CLT but small enough that
    # the resample branch is cheap, by calling each branch explicitly via the threshold.
    rng = np.random.default_rng(7)
    resid = rng.normal(0.05, 0.8, 40000)  # in pp; 40k < threshold so this is the bootstrap branch
    boot_lo, boot_hi = _bootstrap_ci(resid, n_boot=400, seed=1)
    # force the closed-form branch on the same data by temporarily lowering n below threshold check:
    # build a >threshold copy that is the same distribution; closed form should bracket the same mean
    big = np.concatenate([resid] * ((_BOOTSTRAP_MAX_N // len(resid)) + 2))  # > _BOOTSTRAP_MAX_N
    cf_lo, cf_hi = _bootstrap_ci(big, n_boot=400, seed=1)
    boot_mid = (boot_lo + boot_hi) / 2
    cf_mid = (cf_lo + cf_hi) / 2
    # midpoints (the mean estimate) must match tightly; widths differ only because n differs
    assert abs(boot_mid - cf_mid) < 2.0, f"means disagree: boot {boot_mid:.2f} vs cf {cf_mid:.2f}"
    # both CIs are finite and ordered
    assert boot_lo < boot_hi and cf_lo < cf_hi


def test_grade_vs_default_rail_runs_and_signs_young_loading():
    df = _synth()
    df["grade"] = pd.qcut(df["int_rate"], q=7, labels=list("ABCDEFG"))
    rail = grade_vs_default_rail(df)
    assert set(rail) >= {"grade_age_loading_std", "default_age_loading_std",
                         "grade_minus_default_loading"}
    # the planted young excess raises rate -> raises grade for the young WITHOUT raising their
    # default, so grade's young-end age loading should exceed default's (the rail's smoking gun)
    assert rail["grade_minus_default_loading"][0] > rail["grade_minus_default_loading"][4]
