#!/usr/bin/env python3
"""Runner: did the young-end overcharge actually PAY OFF for the lender?

Loads LC accepted (resolved loans), builds est_age + age bands + realized cashflow fields, runs:
  A           realized return by age band, lawful controls (primary)
  pos-control plant +5pp on 30% of youngest band, assert recovery (anti-confabulation)
  B           net-of-grade (does grade internalize the realized-return economics?)
  C           decompose into interest-collected-rate and loss-rate, per band (the mechanism)
  gradient    Tony's deliberateness instrument: monotonicity + slope + R^2 of profit-by-age

Reads the CSV directly (the cached 13-col parquet lacks cashflow fields); does NOT poison that cache.
All statistics live in the tested module wedge/age_realized_return.py; this script is glue + I/O.
See docs/superpowers/specs/2026-06-23-age-realized-return-design.md for the frozen ledger.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from wedge.age_residual import assign_age_band, band_label, AGE_BANDS  # noqa: E402
from wedge.age_realized_return import (  # noqa: E402
    realized_return, interest_collected_rate, loss_rate,
    fit_band_return, gradient_characterization, inject_return_premium,
    RETURN_CONTROLS,
)

CSV = "data/accepted_2007_to_2018Q4.csv"
OUT_TXT = "runs/lc_age_realized_return_2026-06-23.txt"
OUT_JSON = "runs/lc_age_realized_return_2026-06-23.json"
RESOLVED = {"Fully Paid", "Charged Off"}
USECOLS = ["int_rate", "fico_range_low", "fico_range_high", "dti", "annual_inc",
           "loan_amnt", "funded_amnt", "term", "purpose", "issue_d", "earliest_cr_line",
           "loan_status", "grade",
           "total_pymnt", "recoveries", "total_rec_int", "total_rec_prncp", "out_prncp"]


def load():
    df = pd.read_csv(CSV, usecols=USECOLS, low_memory=False)
    df = df[df["loan_status"].isin(RESOLVED)].copy()
    for c in ["int_rate", "dti", "annual_inc", "loan_amnt", "funded_amnt",
              "total_pymnt", "recoveries", "total_rec_int", "total_rec_prncp", "out_prncp"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["fico_mid"] = (pd.to_numeric(df["fico_range_low"], errors="coerce")
                      + pd.to_numeric(df["fico_range_high"], errors="coerce")) / 2.0
    df["term_months"] = (df["term"].astype(str).str.strip()
                         .str.replace(" months", "", regex=False).astype(float))
    issue = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
    earliest = pd.to_datetime(df["earliest_cr_line"], format="%b-%Y", errors="coerce")
    df["issue_year"] = issue.dt.year
    df["est_age"] = 18.0 + (issue - earliest).dt.days / 365.25
    df = df[(df["est_age"] >= 18) & (df["est_age"] <= 95)]
    need = ["fico_mid", "dti", "annual_inc", "loan_amnt", "funded_amnt", "term_months",
            "purpose", "est_age", "grade", "total_pymnt", "recoveries",
            "total_rec_int", "total_rec_prncp"]
    df = df.dropna(subset=need).copy()
    df = df[df["funded_amnt"] > 0].copy()
    df["age_band"] = df["est_age"].map(assign_age_band)
    df = df[df["age_band"] >= 0].copy()
    # realized outcomes
    df["realized_ret"] = realized_return(df)
    df["int_rate_collected"] = interest_collected_rate(df)
    df["loss"] = loss_rate(df)
    return df


def fmt_band(res, unit="pp"):
    lines = []
    for i in range(len(AGE_BANDS)):
        v = res.band_val.get(i, float("nan"))
        lo, hi = res.band_ci.get(i, (float("nan"), float("nan")))
        n = res.n_per_band.get(i, 0)
        tag = "  <- REF" if i == res.reference_band else ""
        lines.append(f"  {band_label(i):10} n={n:>7}  coef={v:+8.2f} {unit}  "
                     f"CI=[{lo:+8.2f},{hi:+8.2f}]{tag}")
    lines.append(f"  R2={res.r2:.4f}  (reference band = {band_label(res.reference_band)})")
    return "\n".join(lines)


def main():
    df = load()
    n = len(df)
    n_default = int((df["loss"] > 0.01).sum())
    out, payload = [], {"n_total": n, "n_loss_positive": n_default}

    out.append("LC AGE x REALIZED LENDER RETURN — did the young-end overcharge PAY OFF? (2026-06-23)")
    out.append(f"Source: {CSV}, resolved loans only, N={n}. Loss-positive loans: {n_default} "
               f"({100*n_default/n:.1f}%).")
    out.append("realized_return = (total_pymnt + recoveries - funded_amnt) / funded_amnt  "
               "(REALIZED, not modeled).")
    out.append("Lawful controls: " + ", ".join(RETURN_CONTROLS) + ", purpose. Reference band [45,50).")
    out.append("FROZEN LEDGER: Claude = young excess NEGATIVE or ~0 (in [-8,+2]pp), < [25,30); "
               "bias-against-LENDER present.  Tony = lenders PROFIT from the young; the bigger the "
               "profit gradient, the more likely it is DELIBERATE (vs unnoticed).")
    out.append("")

    # ---- out_prncp guard: resolved loans must have ~0 outstanding principal ----
    med_out = float(df["out_prncp"].abs().median())
    out.append(f"[guard] median |out_prncp| = {med_out:.4f} (must be < 1.0 for complete cashflow) "
               f"=> {'PASS' if med_out < 1.0 else 'FAIL — METRIC INVALID'}")
    payload["out_prncp_guard"] = {"median_abs": med_out, "pass": med_out < 1.0}
    out.append("")

    # ---- Cell A (primary): realized return by band ----
    a = fit_band_return(df, outcome="realized_ret")
    out.append("[A] REALIZED RETURN by age band, lawful controls (PRIMARY; pp of funded principal):")
    out.append(fmt_band(a))
    payload["A_realized_return"] = {"band_val": a.band_val, "band_ci": a.band_ci,
                                    "n_per_band": a.n_per_band, "r2": a.r2,
                                    "reference_band": a.reference_band}
    out.append("")

    # ---- positive control: recover a planted +5pp premium on 30% of youngest band ----
    df_pc = inject_return_premium(df, "realized_ret", "age_band", young_band=0,
                                  premium_pp=5.0, frac=0.30, seed=42)
    a_pc = fit_band_return(df_pc, outcome="realized_ret")
    young_base = a.band_val.get(0, float("nan"))
    young_pc = a_pc.band_val.get(0, float("nan"))
    recovered = young_pc - young_base
    out.append("[pos-control] plant +5pp on 30% of [18,25) (expect ~+1.5pp recovery at that band):")
    out.append(f"  young base={young_base:+.2f}pp  ->  with-plant={young_pc:+.2f}pp  "
               f"recovered={recovered:+.2f}pp  =>  "
               f"{'PASS' if 0.8 < recovered < 2.2 else 'CHECK'}")
    payload["pos_control"] = {"young_base": young_base, "young_with_plant": young_pc,
                              "recovered": recovered}
    out.append("")

    # ---- Cell B: net-of-grade ----
    b = fit_band_return(df, outcome="realized_ret", extra_terms="C(grade)")
    young_a = a.band_val.get(0, float("nan"))
    young_b = b.band_val.get(0, float("nan"))
    out.append("[B] NET-OF-GRADE realized return by band (does grade internalize the economics?):")
    out.append(fmt_band(b))
    out.append(f"  young A={young_a:+.2f}pp  ->  net-of-grade={young_b:+.2f}pp  "
               f"(large drop => grade carries the realized-return gradient too)")
    payload["B_net_of_grade"] = {"band_val": b.band_val, "band_ci": b.band_ci,
                                 "young_a": young_a, "young_net": young_b}
    out.append("")

    # ---- Cell C: decompose into interest collected vs loss ----
    c_int = fit_band_return(df, outcome="int_rate_collected")
    c_loss = fit_band_return(df, outcome="loss")
    out.append("[C] DECOMPOSITION — interest collected rate by band (the overcharge, realized):")
    out.append(fmt_band(c_int))
    out.append("[C] DECOMPOSITION — loss rate by band (default severity, realized):")
    out.append(fmt_band(c_loss))
    out.append("  read: realized_return ~= interest_collected - loss. young coef on each tells which wins.")
    payload["C_interest"] = {"band_val": c_int.band_val, "band_ci": c_int.band_ci}
    payload["C_loss"] = {"band_val": c_loss.band_val, "band_ci": c_loss.band_ci}
    out.append("")

    # ---- gradient characterization (Tony's deliberateness instrument) ----
    g = gradient_characterization(a)
    out.append("[gradient] Tony's deliberateness instrument on Cell A (profit-by-age):")
    out.append(f"  slope = {g['slope_pp_per_band']:+.3f} pp/band (negative = profit rises toward young)")
    out.append(f"  slope_R2 = {g['slope_r2']:.3f}  (high => clean monotone => steering, not noise)")
    out.append(f"  monotone = {g['monotone']}")
    out.append(f"  spearman(coef, band_idx) = {g['spearman']:+.3f}")
    payload["gradient"] = g
    out.append("")

    # ---- MATURED-VINTAGE robustness (the load-bearing survivorship test) ----
    # resolved-only pooling enriches young loans for early-defaulters (young default faster ->
    # resolve earlier), biasing realized return DOWN at the young end. 2016-18 vintages are only
    # 11-67% resolved (half the data, worst bias). Restrict to 2011-2014 (>=95% resolved across the
    # full sample) so the in-flight exclusion cannot tilt the young cohort. If young<0 SURVIVES here,
    # survivorship is not the cause and the headline is real; if it collapses, the headline was an artifact.
    MATURED = (2011, 2014)
    dm = df[(df["issue_year"] >= MATURED[0]) & (df["issue_year"] <= MATURED[1])].copy()
    am = fit_band_return(dm, outcome="realized_ret")
    am_int = fit_band_return(dm, outcome="int_rate_collected")
    am_loss = fit_band_return(dm, outcome="loss")
    gm = gradient_characterization(am)
    young_m = am.band_val.get(0, float("nan"))
    out.append(f"[MATURED {MATURED[0]}-{MATURED[1]}] realized return by band (>=95% resolved => "
               f"survivorship-robust; N={len(dm)}):")
    out.append(fmt_band(am))
    out.append(f"  decomposition: young interest={am_int.band_val.get(0,float('nan')):+.2f}pp, "
               f"young loss={am_loss.band_val.get(0,float('nan')):+.2f}pp")
    out.append(f"  gradient: slope_R2={gm['slope_r2']:.3f}, monotone={gm['monotone']}, "
               f"spearman={gm['spearman']:+.3f}")
    out.append(f"  SURVIVORSHIP VERDICT: pooled young={a.band_val.get(0,float('nan')):+.2f}pp, "
               f"matured young={young_m:+.2f}pp => "
               f"{'SURVIVES (headline real)' if young_m < -0.5 else 'COLLAPSES (headline was artifact)' if young_m > -0.5 and young_m < 0.5 else 'INVERTS' if young_m >= 0.5 else 'SURVIVES'}.")
    payload["matured_vintage"] = {
        "years": MATURED, "n": int(len(dm)),
        "A_band_val": am.band_val, "A_band_ci": am.band_ci,
        "interest_band_val": am_int.band_val, "loss_band_val": am_loss.band_val,
        "gradient": gm, "young_pooled": a.band_val.get(0, float("nan")), "young_matured": young_m,
    }
    out.append("")

    # ---- ledger scoring (computed from the data; ledger frozen) ----
    young_ret = a.band_val.get(0, float("nan"))
    young_int = c_int.band_val.get(0, float("nan"))
    young_loss = c_loss.band_val.get(0, float("nan"))
    band2 = a.band_val.get(1, float("nan"))  # [25,30)
    out.append("LEDGER SCORING (ledger frozen above; verdicts computed from this run):")
    claude_sign = "NEGATIVE/~0" if young_ret <= 2.0 else "POSITIVE"
    claude_hit = (-8.0 <= young_ret <= 2.0) and (young_ret < band2)
    out.append(f"  Claude 'young excess NEGATIVE/~0 in [-8,+2]pp, < [25,30)': "
               f"young={young_ret:+.2f}pp, [25,30)={band2:+.2f}pp  => "
               f"{'HELD' if claude_hit else 'FALSIFIED'} (sign {claude_sign}).")
    tony_sign = "PROFIT" if young_ret > 0 else "LOSS"
    out.append(f"  Tony 'lenders PROFIT from the young': young realized return = {young_ret:+.2f}pp "
               f"=> {tony_sign} ({'HELD' if young_ret > 0 else 'FALSIFIED'}).")
    out.append(f"  Tony 'gradient indexes deliberateness': slope_R2={g['slope_r2']:.3f}, "
               f"monotone={g['monotone']} — the cleaner/steeper, the stronger the deliberateness read.")
    out.append(f"  Cell C mechanism: young interest collected={young_int:+.2f}pp, "
               f"young loss={young_loss:+.2f}pp => "
               f"{'interest wins (profit)' if young_int + young_ret*0 > young_loss else 'loss wins'} "
               f"net {young_ret:+.2f}pp.")
    out.append("")
    out.append("CAVEATS: 'age' IS credit tenure (est_age=18+tenure). Survivorship: resolved-only "
               "excludes in-flight loans; if young default FASTER they're over-represented in "
               "resolved-early => realized return biased DOWN at young end (runs WITH a negative "
               "finding => flag). The priced-out-profitable young who never borrowed are in NO file "
               "=> realized return UNDERSTATES the empty-chair harm. Old tail (70+) censored, small n.")

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT} and {OUT_JSON}")


if __name__ == "__main__":
    main()
