"""Constructed violators for every branch of the decision rule (pre-reg §6). No real data is read."""
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import governs as G


@pytest.mark.parametrize("s,v", [("35%", 35.0), ("35.0%", 35.0), (" 12.5 % ", 12.5), ("-1%", float("nan")),
                                 ("abc", float("nan")), ("", float("nan")), (40, 40.0)])
def test_parse_pct(s, v):
    out = G.parse_pct(s)
    assert (math.isnan(out) and math.isnan(v)) or out == v


def test_band_edges_half_open():
    x = pd.Series([34.999, 35.0, 39.999, 40.0])
    assert G.in_band(x, (35.0, 40.0)).tolist() == [False, True, True, False]


def synth_accepted(cap_fn, n=400, seed=0):
    """Monthly loans 2011-01..2017-12; dti uniform under the cap that cap_fn gives for that month."""
    rng = np.random.default_rng(seed)
    rows = []
    for m in pd.period_range("2011-01", "2017-12", freq="M"):
        cap = cap_fn(m.to_timestamp().date())
        rows.append(pd.DataFrame({"month": m, "dti": rng.uniform(0, cap, n)}))
    return pd.concat(rows, ignore_index=True)


written_cap = G.written_cap


def test_accepted_follow_written_policy_passes_A1_A2_A3():
    a = G.accepted_tests(synth_accepted(written_cap))
    assert a["A1_ratio"] and a["A1_floor"] and a["A2"] and a["A3"] and a["construct_ok"]


def test_accepted_ignoring_policy_is_construct_invalid_not_a_verdict():
    """A constant 40% boundary: no response to C2, and loans above the written cap. On the accepted file this is
    indistinguishable from a dti mismatch, so the verdict is CONSTRUCT_INVALID and R decides separately."""
    a = G.accepted_tests(synth_accepted(lambda d: 40))
    assert a["A1_ratio"] is False and not a["construct_ok"]
    assert G.verdict(a, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "CONSTRUCT_INVALID"


def test_A2_failure_no_drop_at_C3_gives_mixed():
    cap = lambda d: 30 if d < G.C1 else 35 if d < G.C2 else 40          # never comes back down
    a = G.accepted_tests(synth_accepted(cap))
    assert a["A1_ratio"] and not a["A2"]
    assert G.verdict({**a, "construct_ok": True}, {"R1": "pass", "R2": "pass", "R3": "null"}) == "MIXED"


def test_A3_failure_no_rise_at_C1_gives_mixed():
    cap = lambda d: 35 if d < G.C2 else 40 if d < G.C3 else 35          # already 35 before C1
    a = G.accepted_tests(synth_accepted(cap))
    assert a["A1_ratio"] and not a["A3"]
    assert G.verdict({**a, "construct_ok": True}, {"R1": "null", "R2": "pass", "R3": "pass"}) == "MIXED"


def test_missing_window_fails_rather_than_passing():
    acc = synth_accepted(written_cap)
    acc = acc[acc["month"] >= pd.Period("2012-07", "M")]                # A3's pre window is gone
    a = G.accepted_tests(acc)
    assert a["A3"] is False


def test_accepted_loader_filters_programs(tmp_path):
    f = tmp_path / "acc.csv"
    f.write_text("issue_d,dti,policy_code,application_type,disbursement_method,other\n"
                 "Dec-2015,38.0,1,Individual,Cash,x\n"
                 "Dec-2015,45.0,1,Individual,DirectPay,x\n"
                 "Dec-2015,33.0,1,Joint App,Cash,x\n"
                 "Dec-2015,20.0,2,Individual,Cash,x\n"
                 "Mar-2012,22.0,1,Individual,,x\n")
    df, counts = G.load_accepted(f)
    assert sorted(df["dti"].tolist()) == [22.0, 38.0] and counts["rows"] == 5 and counts["kept"] == 2


def test_hump_shaped_dti_under_floor_is_mixed_not_does_not_govern():
    """2nd review, finding 1: a governing lender whose DTI is hump-shaped can sit under the 2% floor in [35, 40)."""
    rng = np.random.default_rng(5)
    rows = []
    for m in pd.period_range("2011-01", "2017-12", freq="M"):
        cap = G.written_cap(m.to_timestamp().date())
        x = rng.normal(15, 6, 4000)
        rows.append(pd.DataFrame({"month": m, "dti": x[(x >= 0) & (x < cap)]}))
    a = G.accepted_tests(pd.concat(rows, ignore_index=True))
    assert a["A1_ratio"] and not a["A1_floor"]
    assert G.verdict(a, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "MIXED"


def test_missing_A1_window_is_mixed():
    acc = synth_accepted(written_cap)
    acc = acc[(acc["month"] < pd.Period("2012-08", "M")) | (acc["month"] > pd.Period("2014-06", "M"))]
    a = G.accepted_tests(acc)
    assert a["A1_ratio"] is None
    assert G.verdict({**a, "construct_ok": True}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "MIXED"


def test_exclusion_shift_makes_r_test_null(pdates):
    rej = synth_rejects(written_cap, per_day=300)
    post = (rej["day"] >= pd.Timestamp(G.C2)) & (rej["day"] <= pd.Timestamp(G.C2) + pd.Timedelta(days=20))
    junk = rej[post].sample(frac=0.3, random_state=0).assign(dti=np.nan)    # excluded rows jump after C2
    r = G.rejects_tests(pd.concat([rej, junk], ignore_index=True), pdates)
    assert r["R2"] == "null" and r["R2_why_null"] == "exclusion_shift"


def test_too_few_placebos_makes_r_test_null():
    r = G.rejects_tests(synth_rejects(written_cap, per_day=200), G.placebo_dates()[:3])
    assert r["R2"] == "null" and r["R2_why_null"] == "too_few_placebos"


def test_month_only_tightenings_exclude_the_whole_month():
    ds = G.placebo_dates()
    assert date(2016, 10, 15) not in ds and date(2017, 1, 15) not in ds


def test_rejects_loader_keeps_policy_code_0_and_counts_exclusions(tmp_path):
    f = tmp_path / "rej.csv"
    f.write_text("Amount Requested,Application Date,Loan Title,Risk_Score,Debt-To-Income Ratio,Zip Code,State,Employment Length,Policy Code\n"
                 "1000,2014-07-20,a,700,36%,1xx,NY,1 year,0\n"
                 "1000,2014-07-21,a,700,-1%,1xx,NY,1 year,0\n"
                 "1000,2014-07-22,a,700,37%,1xx,NY,1 year,2\n")
    df, counts = G.load_rejects(f)
    assert df["dti"].dropna().tolist() == [36.0] and len(df) == 2       # the '-1%' row is kept as excluded (NaN)
    assert counts["policy_code_dropped"] == 1 and counts["excluded_dti"] == 1
    assert counts["excluded_dti_by_month"] == {"2014-07": 1}


def synth_rejects(boundary_fn, per_day=600, seed=1, start="2011-01-01", end="2017-12-31"):
    """Declines: a uniform background over 0-50 plus extra declines above the operative boundary on each day."""
    rng = np.random.default_rng(seed)
    rows = []
    for day in pd.date_range(start, end, freq="D"):
        b = boundary_fn(day.date())
        bg = rng.uniform(0, 50, per_day)
        over = rng.uniform(b, 50, per_day)
        rows.append(pd.DataFrame({"day": day, "dti": np.concatenate([bg, over])}))
    return pd.concat(rows, ignore_index=True)


@pytest.fixture(scope="module")
def pdates():
    return G.placebo_dates()        # full list: thinning would fall under MIN_PLACEBO


def test_rejects_follow_written_policy_pass(pdates):
    r = G.rejects_tests(synth_rejects(written_cap), pdates)
    assert [r["R1"], r["R2"], r["R3"]] == ["pass", "pass", "pass"]


def test_rejects_no_break_never_contradicts_and_rarely_passes(pdates):
    """No break, five seeds: a contradict (which alone decides DOES_NOT_GOVERN) must never appear by noise,
    and a pass (5% tail) at most rarely."""
    res = []
    for seed in range(5):
        r = G.rejects_tests(synth_rejects(lambda d: 35, per_day=300, seed=seed), pdates)
        res += [r["R1"], r["R2"], r["R3"]]
    assert res.count("contradict") == 0
    assert res.count("pass") <= 3


def test_rejects_reversed_break_contradicts(pdates):
    reversed_cap = lambda d: 30 if d < G.C1 else 40 if d < G.C2 else 35 if d < G.C3 else 40   # crosses the band the wrong way at C2 and C3
    r = G.rejects_tests(synth_rejects(reversed_cap), pdates)
    assert r["R2"] == "contradict" and r["R3"] == "contradict"


def test_wrong_way_below_band_is_null(pdates):
    """The boundary falls 30 -> 25 at C2: wrong direction, but below [35, 40). It must not read as a pass.
    (With a below-band control it did; that's why the reference band is above every cap.)"""
    below = lambda d: 30 if d < G.C2 else 25
    r = G.rejects_tests(synth_rejects(below), pdates)
    assert r["R2"] != "pass"


def test_verdict_branches():
    good_a = {"A1_ratio": True, "A1_floor": True, "A2": True, "A3": True, "construct_ok": True}
    assert G.verdict(good_a, {"R1": "pass", "R2": "pass", "R3": "null"}) == "GOVERNS"
    assert G.verdict(good_a, {"R1": "pass", "R2": "null", "R3": "null"}) == "MIXED"
    assert G.verdict(good_a, {"R1": "pass", "R2": "pass", "R3": "contradict"}) == "DOES_NOT_GOVERN"
    assert G.verdict({**good_a, "A1_ratio": False}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "DOES_NOT_GOVERN"
    # the floor and missing data never decide DOES_NOT_GOVERN (2nd review, findings 1 and 9)
    assert G.verdict({**good_a, "A1_floor": False}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "MIXED"
    assert G.verdict({**good_a, "A1_ratio": None}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "MIXED"
    assert G.verdict({**good_a, "A2": False}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "MIXED"


def test_volume_growth_does_not_fake_a_contradict(pdates):
    """Low volume early, high volume late (as in the real file): a no-break series must not contradict at C1."""
    rng = np.random.default_rng(7)
    rows = []
    for day in pd.date_range("2011-01-01", "2017-12-31", freq="D"):
        n = int(20 + 2000 * (day.year - 2011) / 6)
        rows.append(pd.DataFrame({"day": day, "dti": np.concatenate([rng.uniform(0, 50, n), rng.uniform(35, 50, n)])}))
    r = G.rejects_tests(pd.concat(rows, ignore_index=True), pdates)
    assert "contradict" not in [r["R1"], r["R2"], r["R3"]]


def test_placebo_dates_avoid_known_changes_and_the_undated_2017_reversion():
    ds = G.placebo_dates()
    assert ds and all(abs((d - k).days) > 45 for d in ds for k in G.KNOWN_CHANGES)
    assert G.C2 not in ds
    assert not [d for d in ds if date(2017, 1, 23) <= d <= date(2017, 7, 6)]


def test_local_placebo_is_within_a_year():
    for d in (G.C1, G.C2, G.C3):
        loc = G.local_placebo(d, G.placebo_dates())
        assert len(loc) >= 10 and all(abs((p - d).days) <= 365 for p in loc)


def test_drift_plus_volume_growth_does_not_contradict():
    """Finding 2: a slow random walk in the share of declines falling in [35, 40), plus volume growth, no break.
    Poisson z inflates with volume under drift; local placebos must keep that from producing a contradict."""
    rng = np.random.default_rng(11)
    walk = 0.25
    rows = []
    for day in pd.date_range("2011-01-01", "2017-12-31", freq="D"):
        walk = min(0.45, max(0.05, walk + rng.normal(0, 0.004)))
        n = int(30 + 3000 * (day.year - 2011) / 6)
        k = rng.binomial(n, walk)
        rows.append(pd.DataFrame({"day": day, "dti": np.concatenate([rng.uniform(35, 40, k), rng.uniform(40, 50, n - k),
                                                                     rng.uniform(0, 35, n)])}))
    r = G.rejects_tests(pd.concat(rows, ignore_index=True))       # full placebo list
    assert "contradict" not in [r["R1"], r["R2"], r["R3"]]


def test_late_drift_does_not_mask_an_early_break():
    """Finding 2, demonstrated: no drift 2011-14, heavy drift 2015-17 at higher volume, and a real break at C1.
    With placebo dates from all years the late tails swamp R1 (null on this seed); with local placebos it passes.
    Breaks when LOCAL is made global (mutation-checked pre-freeze)."""
    rng = np.random.default_rng(1)
    rows, walk = [], 0.25
    for day in pd.date_range("2011-01-01", "2017-12-31", freq="D"):
        late = day.year >= 2015
        if late:
            walk = min(0.6, max(0.05, walk + rng.normal(0, 0.03)))
        n = 1500 if late else 400
        k = rng.binomial(n, walk if late else 0.25)
        bg = np.concatenate([rng.uniform(30, 35, k), rng.uniform(40, 50, n), rng.uniform(0, 30, n)])
        over = rng.uniform(G.written_cap(day.date()), 40, 120)
        rows.append(pd.DataFrame({"day": day, "dti": np.concatenate([bg, over])}))
    r = G.rejects_tests(pd.concat(rows, ignore_index=True))
    assert r["R1"] == "pass"


def test_break_lagged_14_days_never_contradicts(pdates):
    lagged = lambda d: G.written_cap(d - pd.Timedelta(days=14).to_pytimedelta())
    r = G.rejects_tests(synth_rejects(lagged), pdates)
    assert "contradict" not in [r["R1"], r["R2"], r["R3"]]


def test_full_placebo_list_still_passes_written_policy():
    r = G.rejects_tests(synth_rejects(written_cap, per_day=300, seed=3))
    assert [r["R1"], r["R2"], r["R3"]].count("pass") >= 2 and "contradict" not in [r["R1"], r["R2"], r["R3"]]


def test_empty_band_is_finite():
    rej = pd.DataFrame({"day": pd.to_datetime(["2014-07-20", "2014-07-30"]), "dti": [15.0, 15.0]})
    assert all(math.isfinite(v) for v in G.effect(rej, G.C2, (35.0, 40.0)))
