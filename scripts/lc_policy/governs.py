"""Step 1 of the reopened experiment: does LendingClub's written DTI policy govern its decisions?

Implements docs/superpowers/specs/2026-10-26-lc-written-policy-governs-prereg-DRAFT.md exactly. Pure functions over
DataFrames, so constructed data can drive every branch. `main()` reads the real files and must not be run before the
freeze commit that contains both this file and the pre-registration.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

C1, C2, C3 = date(2012, 6, 1), date(2014, 7, 25), date(2016, 6, 7)
ABOVE = (40.0, 50.0)   # above every cap ever written (V0-V18); see pre-reg §3 and test_wrong_way_below_band_is_null
WIN = 21
# Effective dates of every dated policy change (source table V5-V18) plus the unquantified 2016-17 tightenings.
KNOWN_CHANGES = [date(2011, 1, 6), date(2012, 4, 10), C1, date(2012, 11, 28), date(2013, 9, 10), date(2014, 4, 3),
                 C2, date(2014, 8, 20), date(2015, 12, 28), date(2016, 4, 1), C3, date(2016, 10, 1),
                 date(2017, 1, 1), date(2017, 3, 9)]

_PCT = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*%?\s*$")


def parse_pct(s) -> float:
    """'35%' -> 35.0; '-1%' and junk -> nan (excluded and counted, per pre-reg §2)."""
    if isinstance(s, (int, float)) and not (isinstance(s, float) and math.isnan(s)):
        v = float(s)
    else:
        m = _PCT.match(str(s))
        if not m:
            return float("nan")
        v = float(m.group(1))
    return float("nan") if v < 0 else v


def in_band(x: pd.Series, band) -> pd.Series:
    lo, hi = band
    return (x >= lo) & (x < hi)          # half-open, per pre-reg §6


def month_share(acc: pd.DataFrame, band) -> pd.Series:
    """acc: columns month (Period[M]) and dti (float). Share of issued loans in band, per month."""
    g = acc.assign(hit=in_band(acc["dti"], band)).groupby("month")["hit"].mean()
    return g


def mean_over(share: pd.Series, start: str, end: str, drop=()) -> float:
    idx = pd.period_range(start, end, freq="M")
    idx = [m for m in idx if m not in {pd.Period(d, "M") for d in drop}]
    vals = share.reindex(idx).dropna()
    return float(vals.mean()) if len(vals) else float("nan")


def accepted_tests(acc: pd.DataFrame) -> dict:
    drop = (C1, C2, C3)
    b2, b1 = month_share(acc, (35.0, 40.0)), month_share(acc, (30.0, 35.0))
    a1_post, a1_pre = mean_over(b2, "2014-08", "2016-05", drop), mean_over(b2, "2012-07", "2014-06", drop)
    a2_post, a2_pre = mean_over(b2, "2016-07", "2017-02", drop), mean_over(b2, "2015-07", "2016-04", drop)
    a3_post, a3_pre = mean_over(b1, "2012-07", "2013-06", drop), mean_over(b1, "2011-02", "2012-04", drop)
    ge10 = lambda post, pre: post >= 10 * pre if pre > 0 else post > 0
    return {
        "A1": bool(a1_post >= 0.005 and ge10(a1_post, a1_pre)), "A1_vals": [a1_pre, a1_post],
        "A2": bool(a2_pre > 0 and a2_post <= a2_pre / 3), "A2_vals": [a2_pre, a2_post],
        "A3": bool(ge10(a3_post, a3_pre)), "A3_vals": [a3_pre, a3_post],
    }


def effect(rej: pd.DataFrame, d: date, band) -> tuple[float, float]:
    """rej: columns day (datetime64) and dti (float). Returns (e, z): e = ln(r_post / r_pre) with
    r = n(band) / n(ABOVE), and z = e / se, se the Poisson standard error of e.

    The reference band sits ABOVE every cap, not below: a below-band control let a boundary that moved the wrong way
    (below the band) read as a pass, because it dilutes the band but not the control. z, not e, is compared with the
    placebo, because reject volume grows about 2000-fold from 2007 to 2018 and raw e is not comparable across years.
    Both were found by constructed tests before freeze."""
    d = pd.Timestamp(d)
    pre = rej[(rej["day"] >= d - pd.Timedelta(days=WIN)) & (rej["day"] <= d - pd.Timedelta(days=1))]
    post = rej[(rej["day"] >= d) & (rej["day"] <= d + pd.Timedelta(days=WIN - 1))]
    def counts(x):
        return in_band(x["dti"], band).sum() + 0.5, in_band(x["dti"], ABOVE).sum() + 0.5   # +0.5: finite when empty
    b0, a0 = counts(pre)
    b1, a1 = counts(post)
    e = math.log((b1 / a1) / (b0 / a0))
    se = math.sqrt(1 / b0 + 1 / a0 + 1 / b1 + 1 / a1)
    return e, e / se


def placebo_dates(start=date(2011, 3, 1), end=date(2017, 12, 15), known=KNOWN_CHANGES, gap=45) -> list[date]:
    out, y, m = [], start.year, start.month
    while True:
        for day in (1, 15):
            d = date(y, m, day)
            if start <= d <= end and all(abs((d - k).days) > gap for k in known):
                out.append(d)
        if (y, m) >= (end.year, end.month):
            return out
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def r_test(z: float, placebo_z: list[float], sign: int) -> str:
    """pass: z beyond the placebo 5th/95th percentile on the predicted side. contradict: |z| > 3 on the opposite side
    AND beyond every placebo z. One contradict decides DOES_NOT_GOVERN, so it gets the stricter bar (a 5% tail read
    'contradict' by noise on a constructed no-break series, pre-freeze)."""
    lo, hi = np.percentile(placebo_z, 5), np.percentile(placebo_z, 95)
    if sign < 0:
        return "pass" if z < lo else ("contradict" if z > 3 and z > max(placebo_z) else "null")
    return "pass" if z > hi else ("contradict" if z < -3 and z < min(placebo_z) else "null")


def rejects_tests(rej: pd.DataFrame, pdates=None) -> dict:
    pdates = placebo_dates() if pdates is None else pdates
    spec = {"R1": (C1, (30.0, 35.0), -1), "R2": (C2, (35.0, 40.0), -1), "R3": (C3, (35.0, 40.0), +1)}
    out = {}
    for k, (d, band, sign) in spec.items():
        e, z = effect(rej, d, band)
        pl = [effect(rej, p, band)[1] for p in pdates]
        out[k] = r_test(z, pl, sign)
        out[k + "_e"], out[k + "_z"] = e, z
        out[k + "_placebo_z_5_95"] = [float(np.percentile(pl, 5)), float(np.percentile(pl, 95))]
    return out


def verdict(a: dict, r: dict) -> str:
    rs = [r["R1"], r["R2"], r["R3"]]
    if not a["A1"] or "contradict" in rs:
        return "DOES_NOT_GOVERN"
    if a["A1"] and a["A2"] and a["A3"] and rs.count("pass") >= 2:
        return "GOVERNS"
    return "MIXED"


def load_accepted(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=["issue_d", "dti", "policy_code", "application_type"])
    df = df[(df["policy_code"] == 1) & (df["application_type"].fillna("Individual") == "Individual")]
    return pd.DataFrame({"month": pd.to_datetime(df["issue_d"], format="%b-%Y").dt.to_period("M"),
                         "dti": pd.to_numeric(df["dti"], errors="coerce")}).dropna()


def load_rejects(path: Path) -> tuple[pd.DataFrame, dict]:
    parts, counts = [], {"rows": 0, "excluded_dti": 0}
    for ch in pd.read_csv(path, usecols=["Application Date", "Debt-To-Income Ratio"], chunksize=2_000_000):
        counts["rows"] += len(ch)
        dti = ch["Debt-To-Income Ratio"].map(parse_pct)
        counts["excluded_dti"] += int(dti.isna().sum())
        parts.append(pd.DataFrame({"day": pd.to_datetime(ch["Application Date"], errors="coerce"), "dti": dti}).dropna())
    return pd.concat(parts, ignore_index=True), counts


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    a = accepted_tests(load_accepted(root / "data/accepted_2007_to_2018Q4.parquet"))
    rej, counts = load_rejects(root / "data/rejected_2007_to_2018Q4.csv")
    r = rejects_tests(rej)
    print(json.dumps({"accepted": a, "rejects": r, "counts": counts, "verdict": verdict(a, r)}, indent=1, default=str))


if __name__ == "__main__":
    main()
