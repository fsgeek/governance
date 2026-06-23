#!/usr/bin/env python3
"""Arm A (the real falsification test) — does the LC age-graded pricing-past-default gradient
appear on Fannie Mae single-family, with age proxied by LTV cohort?

Frozen pre-reg: docs/superpowers/specs/2026-06-23-cross-substrate-falsification-prereg.md
H0 (Tony): LC is an outlier, the gradient will NOT appear here. This run tries to FALSIFY H0.

Age proxy = LTV cohort. Equity maps to life-stage: HIGH LTV (thin equity) ~ YOUNG; LOW LTV
(equity-rich) ~ OLD. LTV deciles ascending => band 0 = lowest LTV = OLD-analog; band 9 = highest
LTV = YOUNG-analog. The LC falsifier would be a band-9 (young-analog) overcharge with a monotone
gradient toward band 0 (old-analog subsidy).

THE TAUTOLOGY BREAK (load-bearing): LTV is INCLUDED in the predicted-default model, so the
default-justified yardstick already prices LTV's risk. A surviving high-LTV-cohort excess therefore
cannot be LTV-risk rerouted — it is the FM analog of the LC +134. (Parallel to LC putting FICO/DTI
in the yardstick and still finding the gradient. Arm C's P2 showed banded continuous fields CAN
carry real residual signal, so this control is the whole test, not optional.)

Reuses the tested wedge/age_grade_default.py benchmark with LTV-cohort bands in place of age bands.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from wedge.collectors.fanniemae import load_collapsed_cached  # noqa: E402
from wedge.age_grade_default import (  # noqa: E402
    band_excess_corpus, fit_default_rate_map, assert_monotone,
)

FM_VINTAGE_CSV = "data/fanniemae/2015Q1.csv"  # post-crisis, fully seasoned for 24mo label
OUT_TXT = "runs/fm_age_ltv_default_2026-06-23.txt"
OUT_JSON = "runs/fm_age_ltv_default_2026-06-23.json"
# LTV is heavily spiked at round values (95 appears 50k+ times, 90 ~20k) so equal-frequency
# qcut collapses to <10 non-empty bins and leaves the top band EMPTY. Use fixed mortgage-meaningful
# LTV cutpoints instead — interpretable cohorts (the 80 PMI line, the 90/95/97 high-LTV tiers) and
# every band populated. Band 0 = lowest LTV (OLD/equity-rich analog) ... top band = highest LTV
# (YOUNG/thin-equity analog), preserving the band-0=old, top=young convention the scorer expects.
LTV_CUTPOINTS = [0, 60, 70, 75, 80, 85, 90, 95, 100]  # 8 cohorts; right-edge inclusive top
N_COHORTS = len(LTV_CUTPOINTS) - 1
FALSIFIER_BPS = 25.0  # frozen: young-analog (high-LTV) excess > this, CI excludes 0 = falsifies H0

# FM risk controls (no annual_inc — FM doesn't release it). LTV IS HERE: the tautology break.
FM_RISK_NUMERIC = ["fico_range_low", "dti", "ltv", "loan_term_months"]


def build_modeling_frame() -> tuple[pd.DataFrame, str]:
    feats, source = load_collapsed_cached(FM_VINTAGE_CSV)
    df = feats.copy()
    df["default"] = 1 - df["label"].astype(int)  # label=1 is clean (grant-positive)
    df["int_rate"] = pd.to_numeric(df["orig_interest_rate"], errors="coerce")
    df["purpose"] = df["loan_purpose"].astype(str)
    need = ["int_rate", "fico_range_low", "dti", "ltv", "loan_term_months", "purpose", "default"]
    df = df.dropna(subset=need).copy()
    df = df[(df["int_rate"] > 0) & (df["ltv"] > 0) & (df["ltv"] <= 100)].copy()
    # Fixed LTV cutpoints (NOT quantiles — LTV is spiked at round values). Band 0 = lowest LTV
    # (OLD/equity-rich analog) ... top band = highest LTV (YOUNG/thin-equity analog).
    df["age_band"] = pd.cut(df["ltv"], bins=LTV_CUTPOINTS, labels=False,
                            include_lowest=True, right=True).astype("Int64")
    df = df.dropna(subset=["age_band"]).copy()
    df["age_band"] = df["age_band"].astype(int)
    return df, source


def predicted_default_fm(df: pd.DataFrame) -> np.ndarray:
    """Predicted default on FM risk controls INCLUDING LTV (the tautology break). Mirrors
    wedge.age_grade_default.predicted_default but uses FM_RISK_NUMERIC (no income)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    X_num = StandardScaler().fit_transform(df[FM_RISK_NUMERIC].astype(float).to_numpy())
    dummies = pd.get_dummies(df["purpose"], prefix="purpose", drop_first=True)
    X = np.hstack([X_num, dummies.to_numpy(dtype=float)]) if dummies.shape[1] else X_num
    clf = LogisticRegression(max_iter=1000, C=1e6)
    clf.fit(X, df["default"].astype(int).to_numpy())
    return clf.predict_proba(X)[:, 1]


def k_a1_collinearity_void(df: pd.DataFrame, p_hat: np.ndarray) -> tuple[bool, float]:
    """K-A1: if LTV-cohort and predicted-default are so collinear the LTV-aware yardstick can't
    separate cohort from its own risk, Arm A is VOID for tautology (not scored as a result).
    Diagnostic: correlation between cohort rank and predicted default. |corr| ~ 1 => degenerate."""
    corr = float(np.corrcoef(df["age_band"].astype(float), p_hat)[0, 1])
    void = abs(corr) > 0.95
    return void, corr


def fmt(res):
    lines = []
    for i in range(N_COHORTS):
        if i not in res.band_bps:
            continue
        bps = res.band_bps[i]
        lo, hi = res.band_ci.get(i, (float("nan"), float("nan")))
        n = res.n_per_band.get(i, 0)
        role = "OLD-analog (low LTV)" if i == 0 else ("YOUNG-analog (high LTV)" if i == N_COHORTS - 1 else "")
        sign = "PAST default" if bps > 0 else "SUBSIDIZED"
        x0 = "" if (lo > 0 or hi < 0) else "  (CI crosses 0)"
        lines.append(f"  LTV-band {i:>2} n={n:>7}  excess={bps:+8.1f} bps  CI=[{lo:+8.1f},{hi:+8.1f}]  "
                     f"{sign}{x0}  {role}")
    return "\n".join(lines)


def main():
    df, source = build_modeling_frame()
    p_hat = predicted_default_fm(df)
    out, payload = [], {"n_total": int(len(df)), "source": source,
                        "n_default": int(df["default"].sum())}

    out.append("FM ARM A — does the LC age/pricing-past-default gradient appear on Fannie Mae? "
               "(LTV-cohort age proxy, 2026-06-23)")
    out.append(f"Source: {FM_VINTAGE_CSV} ({source}), eligible loans N={len(df)}, "
               f"defaults={int(df['default'].sum())} ({100*df['default'].mean():.2f}%).")
    out.append("H0 (Tony, frozen): LC is an outlier; gradient will NOT appear. This run tries to falsify it.")
    out.append("Age proxy = LTV cohort: band 0 = LOW LTV (OLD-analog), band 9 = HIGH LTV (YOUNG-analog).")
    out.append("Tautology break: LTV is IN the predicted-default yardstick, so a surviving high-LTV "
               "excess is NOT LTV-risk rerouted. Risk controls: " + ", ".join(FM_RISK_NUMERIC) +
               ", purpose (no income — FM doesn't release it).")
    out.append(f"FROZEN falsifier: YOUNG-analog (band 9) excess > +{FALSIFIER_BPS} bps, CI excludes 0, "
               "AND monotone decline toward band 0. H0 survives if band-9 excess ~ 0.")
    out.append("")

    # ---- K-A1 collinearity void check ----
    void, corr = k_a1_collinearity_void(df, p_hat)
    out.append(f"[K-A1] corr(LTV-cohort, predicted-default) = {corr:+.3f}  "
               f"=> {'VOID for tautology (|corr|>0.95)' if void else 'OK, cohort separable from its risk'}")
    payload["k_a1_corr"] = corr
    payload["k_a1_void"] = bool(void)
    out.append("")
    if void:
        out.append("ARM A VOID — LTV-cohort and its own predicted default are rank-degenerate; the "
                   "LTV-aware yardstick cannot separate cohort from risk. Not scored as survive/falsify. "
                   "(This is the failure mode the prior HMDA session hit; reported honestly.)")
        payload["verdict"] = "VOID_K_A1"
        with open(OUT_TXT, "w") as fh:
            fh.write("\n".join(out) + "\n")
        with open(OUT_JSON, "w") as fh:
            json.dump(payload, fh, indent=2, default=float)
        print("\n".join(out)); print(f"\nWrote {OUT_TXT} (VOID)"); return

    # ---- the benchmark, both maps ----
    results = {}
    for kind in ("isotonic", "decile"):
        m = fit_default_rate_map(p_hat, df["int_rate"].to_numpy(), map_kind=kind)
        assert_monotone(m)  # K-A2
        res = band_excess_corpus(df, map_kind=kind, p_hat=p_hat)
        results[kind] = res
        out.append(f"=== MAP = {kind.upper()} ===  (LTV-cohort excess over default-justified rate)")
        out.append(fmt(res))
        out.append("")
        payload[f"map_{kind}"] = {"band_bps": res.band_bps, "band_ci": res.band_ci,
                                  "n_per_band": res.n_per_band}

    # ---- score H0 (isotonic primary) ----
    iso = results["isotonic"]
    young = iso.band_bps.get(N_COHORTS - 1, float("nan"))  # band 9 = high LTV = young-analog
    ylo, yhi = iso.band_ci.get(N_COHORTS - 1, (float("nan"), float("nan")))
    old = iso.band_bps.get(0, float("nan"))
    # monotone decline from young-analog (band 9) to old-analog (band 0)?
    seq = [iso.band_bps[i] for i in range(N_COHORTS) if i in iso.band_bps]
    monotone_up_with_ltv = all(seq[i] <= seq[i + 1] + 5 for i in range(len(seq) - 1))  # rises with LTV
    falsifies = (young > FALSIFIER_BPS) and (ylo > 0) and monotone_up_with_ltv
    out.append("H0 SCORING (frozen pre-reg; isotonic primary):")
    out.append(f"  YOUNG-analog (band 9, high LTV) excess = {young:+.1f} bps, CI=[{ylo:+.1f},{yhi:+.1f}]")
    out.append(f"  OLD-analog (band 0, low LTV) excess = {old:+.1f} bps")
    out.append(f"  rises-with-LTV (young>old, monotone): {monotone_up_with_ltv}")
    if falsifies:
        out.append(f"  => H0 FALSIFIED: high-LTV cohort priced +{young:.0f} bps PAST LTV-aware default-"
                   "justified rate, gradient mirrors LC. The discrimination is NOT an LC outlier.")
    else:
        out.append(f"  => H0 SURVIVES: high-LTV cohort excess {young:+.0f} bps does not clear the frozen "
                   f"falsifier (+{FALSIFIER_BPS} bps, CI-excludes-0, monotone). On FM-via-LTV the LC "
                   "gradient does NOT reproduce. (A null here is about the LTV proxy on FM, not proof "
                   "LC is artifactual — Arm C already showed the LC machinery is sound.)")
    payload["verdict"] = "H0_FALSIFIED" if falsifies else "H0_SURVIVES"
    payload["young_analog_bps"] = young
    payload["old_analog_bps"] = old
    out.append("")
    out.append("CAVEATS: FM 'age' is LTV-cohort, a weaker/different proxy than LC credit-tenure. "
               "No income control (FM gap). Pricing = FM note rate. A null does not prove LC "
               "artifactual; it shows the LTV proxy doesn't carry the gradient on this FM vintage.")

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT}, {OUT_JSON}  (verdict={payload['verdict']})")


if __name__ == "__main__":
    main()
