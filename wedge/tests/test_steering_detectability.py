"""The three synthetic lenders validate the gradient/price instrument against LAUNDERED steering.

Locked signatures (n=120000, seed=1, canonical [45,50) reference):
  L0 blind   : young price ~0 (no false positive)
  L1 overt   : young price large, SURVIVES net-of-grade (steering is in price)
  L2 launder : young price large, COLLAPSES net-of-grade (steering is in grade — the fingerprint)
The L2 collapse-net-of-grade is the discriminant; real LC's +209->+27bps matches it.
"""
import numpy as np

from wedge.steering_detectability import build_lender, evaluate_lender


def test_blind_no_false_positive():
    """L0: grade=g(risk) only, no age signal. Young price coef ~0."""
    ev = evaluate_lender(build_lender("blind", n=120000, seed=1))
    assert abs(ev["young_raw_bps"]) < 25, f"blind false positive: {ev['young_raw_bps']:.1f}bps"
    assert ev["laundering_signature"] is False


def test_overt_detected_and_survives_net_of_grade():
    """L1: +4pp explicit young surcharge in PRICE. Detected, and SURVIVES net-of-grade (it's not
    in grade, so controlling for grade doesn't remove it). NOT a laundering signature."""
    ev = evaluate_lender(build_lender("overt", n=120000, seed=1, overt_delta_pp=4.0))
    assert ev["young_raw_bps"] > 300, f"overt not detected: {ev['young_raw_bps']:.1f}bps"
    assert ev["collapse_ratio"] > 0.7, f"overt should survive net-of-grade: ratio={ev['collapse_ratio']:.2f}"
    assert ev["laundering_signature"] is False


def test_launder_detected_and_collapses_net_of_grade():
    """L2: young pushed to worse GRADES beyond risk; price honest off grade. The discriminant:
    large raw young price that COLLAPSES net-of-grade -> the laundering fingerprint. This is the
    case my pre-reg bet would be invisible; it is NOT — it's caught, by the collapse signature."""
    ev = evaluate_lender(build_lender("launder", n=120000, seed=1, launder_grade_shift=0.30))
    assert ev["young_raw_bps"] > 300, f"launder not detected in raw: {ev['young_raw_bps']:.1f}bps"
    assert ev["collapse_ratio"] < 0.3, f"launder should collapse net-of-grade: ratio={ev['collapse_ratio']:.2f}"
    assert ev["laundering_signature"] is True


def test_only_launderer_shows_laundering_signature():
    """The signature must be SPECIFIC: exactly L2 trips it, not L0 or L1."""
    sigs = {k: evaluate_lender(build_lender(k, n=120000, seed=1))["laundering_signature"]
            for k in ["blind", "overt", "launder"]}
    assert sigs == {"blind": False, "overt": False, "launder": True}, sigs


def test_explicit_fit_matches_raw_band_means():
    """Guard against the fit_band_return Categorical instability: the explicit band-0 coefficient must
    match the raw band0-vs-band5 mean price difference (within noise). This is why evaluate_lender uses
    the explicit fit — verified, not trusted."""
    from wedge.steering_detectability import _explicit_band_fit
    df = build_lender("blind", n=120000, seed=1)
    d = df[df["age_band"] != 9].copy()
    raw = _explicit_band_fit(d, "int_rate")
    coef_bps = raw.band_val[0] * 100.0
    mean_diff_bps = (d[d.age_band == 0]["int_rate"].mean()
                     - d[d.age_band == 5]["int_rate"].mean()) * 100.0
    # explicit coef is control-adjusted; raw mean diff is not, but on blind data (age ⊥ everything)
    # they must agree within a few bps. If they diverge by >50bps the harness is lying.
    assert abs(coef_bps - mean_diff_bps) < 50, f"coef {coef_bps:.1f} vs raw mean {mean_diff_bps:.1f}"


def test_l3_honest_risk_collapses_like_launder():
    """L3 (young genuinely riskier, grade honest): price side is INDISTINGUISHABLE from L2 launder —
    both collapse net-of-grade and trip the laundering signature. This is the whole point: the
    net-of-grade fingerprint ALONE cannot separate honest risk-grading from laundering."""
    l2 = evaluate_lender(build_lender("launder", n=120000, seed=1))
    l3 = evaluate_lender(build_lender("honest_risk", n=120000, seed=1))
    assert l3["laundering_signature"] is True, "honest-risk should ALSO trip the price fingerprint"
    assert l3["collapse_ratio"] < 0.3, "honest-risk young price should collapse net-of-grade like launder"
    # the price side cannot tell them apart:
    assert abs(l2["young_net_bps"] - l3["young_net_bps"]) < 10


def test_l2_l3_separated_only_by_realized_return_sign():
    """The discriminant the price gradient can't supply: realized-return SIGN. L2 laundered PROFITS
    on the young (over-priced, not actually riskier); L3 honest LOSES (genuinely riskier). Opposite
    signs, robustly. NB: real LC's young show NEGATIVE realized return -> the L3 (honest) side, which
    is why the 'bias against interest' reading is confounded by latent risk (see the L3 run note)."""
    l2 = evaluate_lender(build_lender("launder", n=120000, seed=1))
    l3 = evaluate_lender(build_lender("honest_risk", n=120000, seed=1))
    assert l2["young_realized_return_pp"] > 2.0, "laundered should profit on the young"
    assert l3["young_realized_return_pp"] < -5.0, "honest-risk should lose on the genuinely-riskier young"


def test_construction_age_orthogonal_to_risk():
    """Guard: true_risk ~ independent of age in the NON-honest lenders (else 'excess' is real risk,
    not steering). honest_risk is EXCLUDED — there the young ARE riskier by design."""
    for kind in ["blind", "overt", "launder"]:
        df = build_lender(kind, n=40000, seed=7)
        c = np.corrcoef(df["true_risk"].astype(float), df["age"].astype(float))[0, 1]
        assert abs(c) < 0.05, f"{kind}: true_risk correlated with age ({c:.3f})"
