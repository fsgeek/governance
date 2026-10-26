"""Constructed violators for every branch of the decision rule (pre-reg §6). No real data is read."""
import math
import sys
from datetime import date
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


def written_cap(d):
    return 30 if d < G.C1 else 35 if d < G.C2 else 40 if d < G.C3 else 35


def test_accepted_follow_written_policy_passes_A1_A2_A3():
    a = G.accepted_tests(synth_accepted(written_cap))
    assert a["A1"] and a["A2"] and a["A3"]


def test_accepted_ignoring_policy_fails_A1():
    a = G.accepted_tests(synth_accepted(lambda d: 40))      # constant 40% cap all along: no response to C2
    assert not a["A1"]


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
    return G.placebo_dates()[::4]   # thinned for speed; full list in the real run


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
    good_a = {"A1": True, "A2": True, "A3": True}
    assert G.verdict(good_a, {"R1": "pass", "R2": "pass", "R3": "null"}) == "GOVERNS"
    assert G.verdict(good_a, {"R1": "pass", "R2": "null", "R3": "null"}) == "MIXED"
    assert G.verdict(good_a, {"R1": "pass", "R2": "pass", "R3": "contradict"}) == "DOES_NOT_GOVERN"
    assert G.verdict({**good_a, "A1": False}, {"R1": "pass", "R2": "pass", "R3": "pass"}) == "DOES_NOT_GOVERN"
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


def test_placebo_dates_avoid_known_changes():
    ds = G.placebo_dates()
    assert ds and all(abs((d - k).days) > 45 for d in ds for k in G.KNOWN_CHANGES)
    assert G.C2 not in ds


def test_empty_band_is_finite():
    rej = pd.DataFrame({"day": pd.to_datetime(["2014-07-20", "2014-07-30"]), "dti": [15.0, 15.0]})
    assert all(math.isfinite(v) for v in G.effect(rej, G.C2, (35.0, 40.0)))
