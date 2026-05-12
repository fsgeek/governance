"""Within-tier forward-predictive test.

Pre-registration: docs/superpowers/specs/2026-05-12-within-tier-predictive-test-preregistration-note.md.

For each Cat-2-(pricing) burst identified by the temporal sweep, for each
sub-grade flagged Cat 2 (pricing) in the burst's first quarter V1:
  - fit a refinement model on V1's grade-G loans using only the policy-named
    features (fico_range_low, dti, annual_inc, emp_length) -> realized default;
  - FREEZE it;
  - apply to V2's grade-G loans; compute the within-grade AUC of its scores
    against V2's realized default;
  - compare to a label-shuffle null (95th percentile, 500 permutations), to the
    chance line (0.5), to V1's in-sample AUC, and to a V2-refit AUC.

A grade is a HIT (forward-predictive) iff V2-OOS AUC > the shuffle-null p95 AND
>= 0.52. A burst is forward-predictive iff a majority of its flagged grades are
HITs. The "bursts are real, not multiple-testing artifacts" claim is falsified
iff a majority of BOTH bursts' flagged grades are MISSes.

Bursts:
  D (the 2015H2 dti burst): V1 = 2015Q3, V2 = 2015Q4.
  A (the 2013-14 annual_inc burst): V1 = 2013Q3, V2 = 2013Q4.
Latent-structure arm (secondary): fit on 2014Q4's versions of 2015Q4's flagged
grades (2014Q4 flagged nothing) and evaluate on 2015Q4.

Models: LogisticRegression (primary, interpretable), DecisionTreeClassifier
depth 2 (robustness).

Usage:
    PYTHONPATH=. python scripts/within_tier_predictive_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.pricing import GradeStratification, classify_grades
from wedge.predictive import classify_hit, shuffle_null_auc

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
TERM = "36 months"
POLICY_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
EXTENSION_FEATURES = [
    "revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
    "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec",
]
SWEEP_SUMMARY = Path("runs/pricing-lc-sweep-36mo-summary.json")

# Stratification params (must match scripts/run_pricing_lc_sweep.py).
ALPHA = 0.01
MIN_LOANS_PER_GRADE = 300
MIN_LOANS_PER_SIDE = 100

# Pre-registered evaluation params.
N_PERM = 500
NULL_PERCENTILE = 95
AUC_FLOOR = 0.52

BURSTS = {
    "D_2015H2_dti": {"v1": "2015Q3", "v2": "2015Q4"},
    "A_2013_14_annual_inc": {"v1": "2013Q3", "v2": "2013Q4"},
}
LATENT_ARM = {"name": "latent_2014Q4_to_2015Q4", "fit_vintage": "2014Q4", "eval_vintage": "2015Q4",
              "grades_from": "2015Q4"}


def _coerce_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip().str.rstrip("%"), errors="coerce")


def _prep(raw: pd.DataFrame, vintage: str) -> pd.DataFrame:
    df = filter_to_vintage(raw.copy(), vintage=vintage, term=TERM)
    if df.empty:
        return df
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    for c in POLICY_FEATURES + EXTENSION_FEATURES:
        if c in df.columns:
            df[c] = _coerce_numeric(df[c])
    df = df.dropna(subset=["label", "sub_grade"]).reset_index(drop=True)
    keep = df["sub_grade"].apply(
        lambda s: isinstance(s, str) and len(s) == 2 and s[0] in "ABCDEFG" and s[1] in "12345"
    )
    return df[keep].reset_index(drop=True)


def _flagged_grades_from_sweep(vintage: str) -> list[str] | None:
    if not SWEEP_SUMMARY.exists():
        return None
    summ = json.loads(SWEEP_SUMMARY.read_text())
    for row in summ.get("vintages", []):
        if row["vintage"] == vintage:
            return sorted(g for g, c in row["grade_classification"].items()
                          if c == "Cat 2 (pricing)")
    return None


def _flagged_grades(raw: pd.DataFrame, vintage: str) -> list[str]:
    cached = _flagged_grades_from_sweep(vintage)
    if cached is not None:
        return cached
    # Fall back to a fresh stratification run.
    df = _prep(raw, vintage)
    feature_cols = [c for c in POLICY_FEATURES + EXTENSION_FEATURES if c in df.columns]
    strat = GradeStratification.compute(
        df, grade_col="sub_grade", label_col="label", feature_cols=feature_cols,
        policy_features=set(POLICY_FEATURES), alpha=ALPHA,
        min_loans_per_grade=MIN_LOANS_PER_GRADE, min_loans_per_side=MIN_LOANS_PER_SIDE)
    classes = classify_grades(strat)
    return sorted(g for g, c in classes.items() if c == "Cat 2 (pricing)")


def _xy(df: pd.DataFrame, grade: str) -> tuple[np.ndarray, np.ndarray]:
    sub = df[df["sub_grade"] == grade]
    X = sub[POLICY_FEATURES].to_numpy(dtype=float)
    y = (sub["label"] == 0).to_numpy(dtype=int)  # 1 = charged off
    return X, y


def _eval_grade(df_v1: pd.DataFrame, df_v2: pd.DataFrame, grade: str,
                model_kind: str, perm_seed: int) -> dict:
    X1, y1 = _xy(df_v1, grade)
    X2, y2 = _xy(df_v2, grade)
    imp = SimpleImputer(strategy="median").fit(X1)  # frozen on V1
    X1i, X2i = imp.transform(X1), imp.transform(X2)

    def _fit(kind, X, y):
        if y.min() == y.max():
            return None
        if kind == "logistic":
            # Scale (the 4 policy features span very different magnitudes) so the
            # L2 penalty is even-handed; scaler + model both frozen on V1.
            m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=1.0))
        else:
            m = DecisionTreeClassifier(max_depth=2, random_state=0)
        m.fit(X, y)
        return m

    m1 = _fit(model_kind, X1i, y1)
    out = {"grade": grade, "model": model_kind, "n_v1": int(len(y1)), "n_v2": int(len(y2)),
           "default_rate_v1": round(float(y1.mean()), 4), "default_rate_v2": round(float(y2.mean()), 4)}
    if m1 is None or y2.min() == y2.max():
        out.update({"v1_insample_auc": None, "v2_oos_auc": None, "v2_refit_auc": None,
                    "shuffle_null_p95": None, "verdict": "INDETERMINATE"})
        return out
    s1 = m1.predict_proba(X1i)[:, 1]
    s2 = m1.predict_proba(X2i)[:, 1]
    v1_auc = float(roc_auc_score(y1, s1))
    v2_oos = float(roc_auc_score(y2, s2))
    m2 = _fit(model_kind, X2i, y2)
    v2_refit = float(roc_auc_score(y2, m2.predict_proba(X2i)[:, 1])) if m2 is not None else None
    null_p95 = shuffle_null_auc(y2, s2, n_perm=N_PERM, percentile=NULL_PERCENTILE, rng_seed=perm_seed)
    verdict = classify_hit(oos_auc=v2_oos, null_p95=null_p95, floor=AUC_FLOOR)
    out.update({
        "v1_insample_auc": round(v1_auc, 4), "v2_oos_auc": round(v2_oos, 4),
        "v2_refit_auc": round(v2_refit, 4) if v2_refit is not None else None,
        "shuffle_null_p95": round(null_p95, 4),
        "drift_gap_refit_minus_oos": round(v2_refit - v2_oos, 4) if v2_refit is not None else None,
        "verdict": verdict,
    })
    return out


def _run_arm(name: str, df_fit: pd.DataFrame, df_eval: pd.DataFrame, grades: list[str],
             results: dict) -> None:
    print(f"\n{'='*70}\n{name}  (fit on {len(df_fit)} loans, eval on {len(df_eval)})\n"
          f"  flagged grades: {grades} ({len(grades)})\n{'='*70}", flush=True)
    arm = {"fit_n": len(df_fit), "eval_n": len(df_eval), "flagged_grades": grades, "grades": {}}
    for model_kind in ("logistic", "tree_d2"):
        hits = nears = misses = indet = 0
        per_grade = {}
        for i, g in enumerate(grades):
            r = _eval_grade(df_fit, df_eval, g, model_kind, perm_seed=1000 + i)
            per_grade[g] = r
            v = r["verdict"]
            hits += v == "HIT"; nears += v == "NEAR-HIT"; misses += v == "MISS"; indet += v == "INDETERMINATE"
            auc_str = f"{r['v2_oos_auc']}" if r["v2_oos_auc"] is not None else "  -  "
            null_str = f"{r['shuffle_null_p95']}" if r["shuffle_null_p95"] is not None else "  -  "
            print(f"  [{model_kind:8s}] {g}: n_v1={r['n_v1']:5d} n_v2={r['n_v2']:5d}  "
                  f"OOS_AUC={auc_str}  null_p95={null_str}  "
                  f"v1_insample={r['v1_insample_auc']}  v2_refit={r['v2_refit_auc']}  -> {v}", flush=True)
        n_eff = len(grades) - indet
        forward_pred = n_eff > 0 and hits > n_eff / 2
        arm["grades"][model_kind] = {
            "per_grade": per_grade, "hits": hits, "near_hits": nears, "misses": misses,
            "indeterminate": indet, "n_effective": n_eff, "forward_predictive": bool(forward_pred),
        }
        print(f"  -> [{model_kind}] HIT={hits} NEAR={nears} MISS={misses} INDET={indet}  "
              f"forward_predictive={forward_pred} (majority of {n_eff} effective)", flush=True)
    results[name] = arm


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *POLICY_FEATURES, *EXTENSION_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-within-tier-predictive-test-preregistration-note.md",
        "params": {"n_perm": N_PERM, "null_percentile": NULL_PERCENTILE, "auc_floor": AUC_FLOOR,
                   "policy_features": POLICY_FEATURES, "term": TERM},
        "arms": {},
    }
    arms: dict = {}

    # Prep all vintages we need once.
    vintages_needed = set()
    for b in BURSTS.values():
        vintages_needed |= {b["v1"], b["v2"]}
    vintages_needed |= {LATENT_ARM["fit_vintage"], LATENT_ARM["eval_vintage"]}
    prepped = {v: _prep(raw, v) for v in sorted(vintages_needed)}

    for burst_name, b in BURSTS.items():
        grades = _flagged_grades(raw, b["v1"])
        _run_arm(burst_name, prepped[b["v1"]], prepped[b["v2"]], grades, arms)

    # Latent-structure arm.
    latent_grades = _flagged_grades(raw, LATENT_ARM["grades_from"])
    _run_arm(LATENT_ARM["name"], prepped[LATENT_ARM["fit_vintage"]],
             prepped[LATENT_ARM["eval_vintage"]], latent_grades, arms)

    results["arms"] = arms

    # ---- Verdict (logistic primary) ----
    burst_fp = {name: arms[name]["grades"]["logistic"]["forward_predictive"] for name in BURSTS}
    all_miss = all(not fp for fp in burst_fp.values())
    results["verdict"] = {
        "burst_forward_predictive_logistic": burst_fp,
        "claim_bursts_are_real_falsified": bool(all_miss),
        "latent_2014Q4_predicts_2015Q4_logistic": arms[LATENT_ARM["name"]]["grades"]["logistic"]["forward_predictive"],
        "summary": (
            ("'bursts are real, not multiple-testing artifacts' — FALSIFIED: a majority of both bursts' "
             "flagged grades are MISS; the within-vintage FDR control is insufficient against cross-vintage "
             "multiplicity.") if all_miss else
            ("'bursts are real' — NOT falsified for: " + ", ".join(n for n, fp in burst_fp.items() if fp) +
             ("; FALSIFIED for: " + ", ".join(n for n, fp in burst_fp.items() if not fp) if not all(burst_fp.values())
              else "; both bursts forward-predictive."))
        ),
    }
    print(f"\n{'#'*70}\nVERDICT: {results['verdict']['summary']}\n"
          f"latent arm (2014Q4-fit refinement predicts 2015Q4 within-grade default): "
          f"{results['verdict']['latent_2014Q4_predicts_2015Q4_logistic']}\n{'#'*70}", flush=True)

    out = Path("runs/within_tier_predictive_test_results.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
