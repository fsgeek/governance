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

# V18: the cap went back 35% -> 40% somewhere between these dates, undated (source table). No placebo inside it.
UNDATED_INTERVALS = [(date(2017, 3, 9), date(2017, 5, 22)),
                     # month-only tightenings: the whole month is excluded, not just the 1st (2nd review, finding 5)
                     (date(2016, 4, 1), date(2016, 4, 30)), (date(2016, 10, 1), date(2016, 10, 31)),
                     (date(2017, 1, 1), date(2017, 1, 31))]
MIN_PLACEBO = 10     # fewer local placebo dates -> the R test is null (2nd review, finding 3)
MAX_EXCL_SHIFT = 0.05  # excluded-DTI share moving more than this between pre and post -> the R test is null (finding 2)
LOCAL = 365          # placebo dates within +/- a year of each change (adversary finding 2: drift x volume)
MIN_MONTHS = 6       # an A window with fewer usable months fails (finding 9)
CONSTRUCT_MAX = 0.02 # accepted loans at or above the written cap, per regime, above this -> CONSTRUCT_INVALID (finding 5)
A1_FLOOR = 0.02      # finding 6: 0.5% was trivially easy

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


def mean_over(share: pd.Series, start: str, end: str) -> float:
    idx = pd.period_range(start, end, freq="M")
    vals = share.reindex(idx).dropna()
    return float(vals.mean()) if len(vals) >= MIN_MONTHS else float("nan")


def written_cap(d: date) -> float:
    return 30.0 if d < C1 else 35.0 if d < C2 else 40.0 if d < C3 else 35.0


def construct_check(acc: pd.DataFrame) -> dict:
    """Share of accepted loans with dti at or above the written cap, per regime, away from transitions. If the
    accepted dti were the policy's DTI and the cap were enforced, this is about 0. Above CONSTRUCT_MAX in any regime,
    the accepted-file tests can't tell non-governance from a measurement mismatch."""
    regimes = {"C1-C2": ("2012-08", "2014-06"), "C2-C3": ("2014-09", "2016-05"), "post-C3": ("2016-08", "2017-02")}
    out = {}
    for k, (a, b) in regimes.items():
        m = acc[(acc["month"] >= pd.Period(a, "M")) & (acc["month"] <= pd.Period(b, "M"))]
        cap = m["month"].map(lambda p: written_cap(p.to_timestamp().date()))
        out[k] = float((m["dti"] >= cap).mean()) if len(m) else float("nan")
    return out


def accepted_tests(acc: pd.DataFrame) -> dict:
    """Windows skip the change month AND the next (application-to-issue lag, finding 7)."""
    b2, b1 = month_share(acc, (35.0, 40.0)), month_share(acc, (30.0, 35.0))
    a1_post, a1_pre = mean_over(b2, "2014-09", "2016-05"), mean_over(b2, "2012-08", "2014-06")
    a2_post, a2_pre = mean_over(b2, "2016-08", "2017-02"), mean_over(b2, "2015-07", "2016-03")
    a3_post, a3_pre = mean_over(b1, "2012-08", "2013-06"), mean_over(b1, "2011-02", "2012-04")
    ok = lambda *v: all(not math.isnan(x) for x in v)
    ge10 = lambda post, pre: ok(post, pre) and (post >= 10 * pre if pre > 0 else post > 0)
    cc = construct_check(acc)
    return {
        # A1 split (2nd review, finding 1): the ratio can decide DOES_NOT_GOVERN; the floor and missing data can't.
        "A1_ratio": None if not ok(a1_post, a1_pre) else bool(ge10(a1_post, a1_pre)),
        "A1_floor": bool(ok(a1_post) and a1_post >= A1_FLOOR),
        "A1_vals": [a1_pre, a1_post],
        "A2": bool(ok(a2_pre, a2_post) and a2_pre > 0 and a2_post <= a2_pre / 3), "A2_vals": [a2_pre, a2_post],
        "A3": bool(ge10(a3_post, a3_pre)), "A3_vals": [a3_pre, a3_post],
        "construct": cc, "construct_ok": bool(all(not math.isnan(v) and v <= CONSTRUCT_MAX for v in cc.values())),
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


def excl_shift(rej: pd.DataFrame, d: date) -> float:
    """|excluded share post - pre| in the R windows; rows with dti NaN are the excluded ('-1%', junk)."""
    d = pd.Timestamp(d)
    pre = rej[(rej["day"] >= d - pd.Timedelta(days=WIN)) & (rej["day"] <= d - pd.Timedelta(days=1))]
    post = rej[(rej["day"] >= d) & (rej["day"] <= d + pd.Timedelta(days=WIN - 1))]
    rate = lambda x: float(x["dti"].isna().mean()) if len(x) else 0.0
    return abs(rate(post) - rate(pre))


def placebo_dates(start=date(2011, 3, 1), end=date(2017, 12, 15), known=KNOWN_CHANGES, gap=45,
                  intervals=UNDATED_INTERVALS) -> list[date]:
    out, y, m = [], start.year, start.month
    while True:
        for day in (1, 15):
            d = date(y, m, day)
            near_known = any(abs((d - k).days) <= gap for k in known)
            near_interval = any(a - timedelta(days=gap) <= d <= b + timedelta(days=gap) for a, b in intervals)
            if start <= d <= end and not near_known and not near_interval:
                out.append(d)
        if (y, m) >= (end.year, end.month):
            return out
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def local_placebo(d: date, pdates: list[date]) -> list[date]:
    return [p for p in pdates if abs((p - d).days) <= LOCAL]


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
        pl = [effect(rej, p, band)[1] for p in local_placebo(d, pdates)]
        out[k + "_n_placebo"] = len(pl)
        out[k + "_excl_shift"] = excl_shift(rej, d)
        if len(pl) < MIN_PLACEBO:
            out[k], out[k + "_why_null"] = "null", "too_few_placebos"
        elif out[k + "_excl_shift"] > MAX_EXCL_SHIFT:
            out[k], out[k + "_why_null"] = "null", "exclusion_shift"
        else:
            out[k] = r_test(z, pl, sign)
        out[k + "_e"], out[k + "_z"] = e, z
        out[k + "_placebo_z_5_95"] = [float(np.percentile(pl, 5)), float(np.percentile(pl, 95))] if pl else None
    return out


def r_verdict(r: dict) -> str:
    """The rejects-file tests alone; they don't depend on the accepted file's dti."""
    rs = [r["R1"], r["R2"], r["R3"]]
    if "contradict" in rs:
        return "R_CONTRADICTS"
    return "R_GOVERNS" if rs.count("pass") >= 2 else "R_MIXED"


def verdict(a: dict, r: dict) -> str:
    """A lender ignoring its cap and an accepted dti that isn't the policy's DTI look the same on the accepted file,
    so a failed construct check makes the accepted tests uninformative, not a verdict either way. r_verdict is then
    reported beside it."""
    if not a.get("construct_ok", True):
        return "CONSTRUCT_INVALID"
    rs = [r["R1"], r["R2"], r["R3"]]
    if a["A1_ratio"] is False or "contradict" in rs:
        return "DOES_NOT_GOVERN"
    if a["A1_ratio"] and a["A1_floor"] and a["A2"] and a["A3"] and rs.count("pass") >= 2:
        return "GOVERNS"
    return "MIXED"


def load_accepted(path: Path) -> tuple[pd.DataFrame, dict]:
    """CSV, not the parquet: the parquet lacks policy_code, application_type, disbursement_method (finding 1).
    Keep the public program (policy_code 1), individual applications, cash disbursement (direct-pay had a 50% cap)."""
    cols = ["issue_d", "dti", "policy_code", "application_type", "disbursement_method"]
    df = pd.read_csv(path, usecols=cols, low_memory=False)
    counts = {"rows": len(df)}
    keep = ((pd.to_numeric(df["policy_code"], errors="coerce") == 1)
            & (df["application_type"].fillna("Individual") == "Individual")
            & (df["disbursement_method"].fillna("Cash") == "Cash"))
    df = df[keep]
    counts["kept"] = int(keep.sum())
    out = pd.DataFrame({"month": pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("M"),
                        "dti": pd.to_numeric(df["dti"], errors="coerce")}).dropna()
    counts["kept_parsed"] = len(out)
    return out, counts


def load_rejects(path: Path) -> tuple[pd.DataFrame, dict]:
    """Keep Policy Code 0 (code 2 is non-public credit policies, finding 4). '-1%' and junk DTI are excluded and
    counted per month, so the exclusion rate can be checked across each window (finding 11)."""
    parts, counts, excl = [], {"rows": 0, "policy_code_dropped": 0, "excluded_dti": 0}, {}
    cols = ["Application Date", "Debt-To-Income Ratio", "Policy Code"]
    for ch in pd.read_csv(path, usecols=cols, chunksize=2_000_000):
        counts["rows"] += len(ch)
        keep = pd.to_numeric(ch["Policy Code"], errors="coerce") == 0
        counts["policy_code_dropped"] += int((~keep).sum())
        ch = ch[keep]
        day = pd.to_datetime(ch["Application Date"], errors="coerce")
        dti = ch["Debt-To-Income Ratio"].map(parse_pct)
        bad = dti.isna()
        counts["excluded_dti"] += int(bad.sum())
        for m, n in day[bad].dt.to_period("M").value_counts().items():
            excl[str(m)] = excl.get(str(m), 0) + int(n)
        parts.append(pd.DataFrame({"day": day, "dti": dti})[day.notna().values])   # dti NaN kept: excluded rows, counted per window
    counts["excluded_dti_by_month"] = dict(sorted(excl.items()))
    return pd.concat(parts, ignore_index=True), counts


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    acc, acc_counts = load_accepted(root / "data/accepted_2007_to_2018Q4.csv")
    a = accepted_tests(acc)
    rej, counts = load_rejects(root / "data/rejected_2007_to_2018Q4.csv")
    r = rejects_tests(rej)
    print(json.dumps({"accepted": a, "rejects": r, "counts": {"accepted": acc_counts, "rejects": counts}, "verdict": verdict(a, r), "r_verdict": r_verdict(r)}, indent=1, default=str))


if __name__ == "__main__":
    main()
