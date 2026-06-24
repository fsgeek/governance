import numpy as np
import pandas as pd
import pytest

from wedge.age_residual import assign_age_band
from wedge.age_realized_return import (
    realized_return,
    interest_collected_rate,
    loss_rate,
    fit_band_return,
    gradient_characterization,
    inject_return_premium,
    RETURN_CONTROLS,
)


def _synth(n=60000, planted_young_pp=0.0, seed=0):
    """Synthetic LC-like cashflow data. Controls drive a lawful realized return; an optional
    return premium is planted on the youngest band only (the positive control)."""
    rng = np.random.default_rng(seed)
    age = rng.uniform(18, 95, n)
    fico_mid = rng.uniform(640, 820, n)
    dti = rng.uniform(0, 35, n)
    annual_inc = rng.uniform(20000, 200000, n)
    funded_amnt = rng.uniform(1000, 40000, n)
    term_months = rng.choice([36, 60], n)
    purpose = rng.choice(["debt_consolidation", "credit_card", "home_improvement"], n)
    band = np.array([assign_age_band(a) for a in age])
    # lawful realized return: a real function of controls (better FICO -> higher return)
    base_ret = 0.05 + (fico_mid - 640) * 0.0005 - dti * 0.001
    noise = rng.normal(0, 0.01, n)
    ret = base_ret + noise + (band == 0) * (planted_young_pp / 100.0)
    # back out cashflow fields consistent with realized_return = (total_pymnt+rec-funded)/funded
    total_pymnt = funded_amnt * (1.0 + ret)
    recoveries = np.zeros(n)
    return pd.DataFrame(
        dict(age=age, fico_mid=fico_mid, dti=dti, annual_inc=annual_inc,
             loan_amnt=funded_amnt, funded_amnt=funded_amnt, term_months=term_months,
             purpose=purpose, total_pymnt=total_pymnt, recoveries=recoveries,
             realized_ret=ret, age_band=band),
    )


def test_realized_return_formula():
    df = pd.DataFrame(dict(total_pymnt=[11000.0], recoveries=[0.0], funded_amnt=[10000.0]))
    assert realized_return(df).iloc[0] == pytest.approx(0.10)


def test_realized_return_with_recovery_and_loss():
    # paid back 6000, recovered 1000 on a 10000 loan -> net -0.30
    df = pd.DataFrame(dict(total_pymnt=[6000.0], recoveries=[1000.0], funded_amnt=[10000.0]))
    assert realized_return(df).iloc[0] == pytest.approx(-0.30)


def test_loss_rate_full_repayment_is_zero():
    df = pd.DataFrame(dict(funded_amnt=[10000.0], total_rec_prncp=[10000.0], recoveries=[0.0]))
    assert loss_rate(df).iloc[0] == pytest.approx(0.0)


def test_loss_rate_total_default_is_one():
    df = pd.DataFrame(dict(funded_amnt=[10000.0], total_rec_prncp=[0.0], recoveries=[0.0]))
    assert loss_rate(df).iloc[0] == pytest.approx(1.0)


def test_interest_collected_rate():
    df = pd.DataFrame(dict(total_rec_int=[1500.0], funded_amnt=[10000.0]))
    assert interest_collected_rate(df).iloc[0] == pytest.approx(0.15)


def test_decomposition_identity():
    """realized_return == interest_collected_rate - loss_rate, exactly, when total_pymnt =
    principal-repaid + interest-collected (the LC accounting identity on resolved loans)."""
    df = pd.DataFrame(dict(
        funded_amnt=[10000.0], total_rec_prncp=[8000.0], total_rec_int=[1200.0],
        recoveries=[500.0],
        total_pymnt=[8000.0 + 1200.0],  # principal + interest the borrower paid
    ))
    ret = realized_return(df).iloc[0]
    icr = interest_collected_rate(df).iloc[0]
    lr = loss_rate(df).iloc[0]
    assert ret == pytest.approx(icr - lr)


def test_positive_control_recovers_planted_premium():
    """THE anti-confabulation guard: plant a +5pp return premium on a random 30% of the youngest
    band, assert Cell A recovers a positive young-band coefficient. Without the plant the synthetic
    young band is at parity (~0), so any recovered positive must come from the plant."""
    df = _synth(planted_young_pp=0.0, seed=1)
    df = inject_return_premium(df, "realized_ret", "age_band", young_band=0,
                               premium_pp=5.0, frac=0.30, seed=2)
    res = fit_band_return(df, outcome="realized_ret", controls=RETURN_CONTROLS)
    young = res.band_val[0]
    # 30% of band gets +5pp -> expected mean shift ~+1.5pp at the young band, vs ref ~0
    assert young > 0.5, f"planted premium not recovered: young={young:.3f}pp"


def test_no_plant_no_young_effect():
    """Negative control: with NO plant the young band must be ~0 (no spurious gradient)."""
    df = _synth(planted_young_pp=0.0, seed=3)
    res = fit_band_return(df, outcome="realized_ret", controls=RETURN_CONTROLS)
    young = res.band_val[0]
    assert abs(young) < 0.5, f"spurious young effect with no plant: young={young:.3f}pp"


def test_gradient_monotone_detection():
    """gradient_characterization flags a clean monotone young->old decline (Tony's deliberateness
    instrument). Build a BandReturn-like object with a perfect descending gradient."""
    from wedge.age_realized_return import BandReturn
    vals = {i: float(10 - i) for i in range(10)}  # 10,9,8,...,1 — descending young->old
    br = BandReturn(band_val=vals, band_ci={i: (0.0, 0.0) for i in vals},
                    n_per_band={i: 1000 for i in vals}, r2=0.9, reference_band=5)
    g = gradient_characterization(br)
    assert g["monotone"] == "monotone_decreasing_young_to_old"
    assert g["slope_pp_per_band"] < 0
    assert g["slope_r2"] == pytest.approx(1.0)
    assert g["spearman"] == pytest.approx(-1.0)


def test_gradient_non_monotone_detection():
    """A noisy non-monotone gradient = 'they're not steering'. Must NOT be flagged monotone."""
    from wedge.age_realized_return import BandReturn
    vals = {0: 5.0, 1: -2.0, 2: 4.0, 3: -1.0, 4: 3.0, 5: 0.0, 6: -3.0, 7: 2.0, 8: -4.0, 9: 1.0}
    br = BandReturn(band_val=vals, band_ci={i: (0.0, 0.0) for i in vals},
                    n_per_band={i: 1000 for i in vals}, r2=0.1, reference_band=5)
    g = gradient_characterization(br)
    assert g["monotone"] == "non_monotone"
    assert abs(g["spearman"]) < 0.8
