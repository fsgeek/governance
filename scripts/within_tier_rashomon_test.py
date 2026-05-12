"""Policy-constrained Rashomon refinement set (within-tier) — orchestration (#6).

Pre-registration: docs/superpowers/specs/2026-05-12-policy-constrained-rashomon-refinement-preregistration-note.md.

For each Cat-2-(pricing) burst, for each sub-grade flagged in the burst's first
quarter V1: build the epsilon-band of policy-admissible refinements
(`wedge.refinement_set.build_refinement_band` over the named features, with the
thin-demo policy's monotonicity directions enforced -- sign-flipped to the
default-prediction convention), and measure
  (1) non-triviality   -- >= 3 distinct band members
  (2) plurality        -- >= 2 distinct used-feature sets AND median pairwise
                          ranking-Spearman among members < 0.9
  (3) forward-prediction -- a majority of members beat the constant on V2's
                          within-grade default (grade-size-aware shuffle null)
  (4) cost of the constraint -- constrained band's best forward-predictive OOS
                          AUC vs an unconstrained band's and a kitchen-sink
                          (named + extension, no monotonicity) tree's.

Bursts: D (2015Q3 -> 2015Q4, dti), A (2013Q3 -> 2013Q4, annual_inc).

Usage:
    PYTHONPATH=. python scripts/within_tier_rashomon_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier

from policy.encoder import load_policy
from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.predictive import classify_hit, shuffle_null_auc
from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
TERM = "36 months"
POLICY_PATH = "policy/thin_demo_hmda.yaml"
SWEEP_SUMMARY = Path("runs/pricing-lc-sweep-36mo-summary.json")

# Named features available in LC accepted data (thin-demo names {fico, dti,
# annual_inc, emp_length, ltv}; LC is unsecured -- no ltv).
NAMED_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
EXTENSION_FEATURES = [
    "revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
    "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec",
]

EPSILON = 0.02
DEPTHS = (1, 2, 3)
LEAF_MINS = (25, 50, 100)
N_PERM = 500
NULL_PERCENTILE = 95
AUC_FLOOR = 0.52
SEED = 0

BURSTS = {
    "D_2015H2_dti": {"v1": "2015Q3", "v2": "2015Q4"},
    "A_2013_14_annual_inc": {"v1": "2013Q3", "v2": "2013Q4"},
}


def _coerce_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip().str.rstrip("%"), errors="coerce")


def _prep(raw: pd.DataFrame, vintage: str) -> pd.DataFrame:
    df = filter_to_vintage(raw.copy(), vintage=vintage, term=TERM)
    if df.empty:
        return df
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    for c in NAMED_FEATURES + EXTENSION_FEATURES:
        if c in df.columns:
            df[c] = _coerce_numeric(df[c])
    df = df.dropna(subset=["label", "sub_grade"]).reset_index(drop=True)
    keep = df["sub_grade"].apply(
        lambda s: isinstance(s, str) and len(s) == 2 and s[0] in "ABCDEFG" and s[1] in "12345"
    )
    return df[keep].reset_index(drop=True)


def _flagged_grades(vintage: str) -> list[str]:
    summ = json.loads(SWEEP_SUMMARY.read_text())
    for row in summ.get("vintages", []):
        if row["vintage"] == vintage:
            return sorted(g for g, c in row["grade_classification"].items()
                          if c == "Cat 2 (pricing)")
    return []


def _grade_xy(df: pd.DataFrame, grade: str, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    sub = df[df["sub_grade"] == grade]
    X = sub[cols].to_numpy(dtype=float)
    y = (sub["label"] == 0).to_numpy(dtype=int)  # 1 = default
    return X, y


def _subset(X: np.ndarray, feature_names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    """Columns of X (aligned to feature_names) for the member's feature subset —
    band members are fit on their subset only, so prediction must subset too."""
    name_to_col = {f: i for i, f in enumerate(feature_names)}
    return X[:, [name_to_col[f] for f in subset]]


def _oos(model, X_v2: np.ndarray, y_v2: np.ndarray, perm_seed: int) -> dict:
    """Out-of-sample within-grade AUC + shuffle-null p95 + hit verdict."""
    if y_v2.min() == y_v2.max():
        return {"oos_auc": None, "null_p95": None, "verdict": "INDETERMINATE"}
    s = model.predict_proba(X_v2)[:, 1]
    auc = float(roc_auc_score(y_v2, s))
    null_p95 = shuffle_null_auc(y_v2, s, n_perm=N_PERM, percentile=NULL_PERCENTILE, rng_seed=perm_seed)
    return {"oos_auc": round(auc, 4), "null_p95": round(null_p95, 4),
            "verdict": classify_hit(oos_auc=auc, null_p95=null_p95, floor=AUC_FLOOR)}


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *NAMED_FEATURES, *EXTENSION_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    pc = load_policy(POLICY_PATH)
    # Encoder states monotonicity w.r.t. GRANT probability; the refinement
    # predicts DEFAULT probability, so negate. Keep only named features that
    # exist in LC.
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in NAMED_FEATURES}
    avail_named = [f for f in NAMED_FEATURES if f in raw.columns]
    avail_all = [f for f in NAMED_FEATURES + EXTENSION_FEATURES if f in raw.columns]
    print(f"  policy '{pc.name}': named features in LC = {avail_named}; "
          f"monotonic_cst (default-convention) = {mono_default}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-policy-constrained-rashomon-refinement-preregistration-note.md",
        "policy": pc.name, "monotonic_cst_default_convention": mono_default,
        "named_features": avail_named, "epsilon": EPSILON,
        "params": {"depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                   "n_perm": N_PERM, "null_percentile": NULL_PERCENTILE, "auc_floor": AUC_FLOOR},
        "bursts": {},
    }

    prepped = {v: _prep(raw, v) for v in sorted({x for b in BURSTS.values() for x in b.values()})}

    for burst_name, b in BURSTS.items():
        v1, v2 = b["v1"], b["v2"]
        df1, df2 = prepped[v1], prepped[v2]
        grades = _flagged_grades(v1)
        print(f"\n{'='*72}\n{burst_name}: build on {v1} ({len(df1)} loans), forward-eval on {v2} ({len(df2)})\n"
              f"  flagged grades: {grades} ({len(grades)})\n{'='*72}", flush=True)
        burst_rec: dict = {"v1": v1, "v2": v2, "flagged_grades": grades, "grades": {}}
        nt = pl = fp = cc = 0  # counts of grades meeting each criterion
        n_eff = 0
        for gi, g in enumerate(grades):
            X1n, y1 = _grade_xy(df1, g, avail_named)
            X2n, y2 = _grade_xy(df2, g, avail_named)
            X1a, _ = _grade_xy(df1, g, avail_all)
            X2a, _ = _grade_xy(df2, g, avail_all)
            if y1.min() == y1.max() or y2.min() == y2.max() or len(y1) < 50:
                print(f"  {g}: INDETERMINATE (degenerate / too few)", flush=True)
                burst_rec["grades"][g] = {"verdict": "INDETERMINATE"}
                continue
            n_eff += 1
            imp_named = SimpleImputer(strategy="median").fit(X1n)
            X1ni, X2ni = imp_named.transform(X1n), imp_named.transform(X2n)
            imp_all = SimpleImputer(strategy="median").fit(X1a)
            X1ai, X2ai = imp_all.transform(X1a), imp_all.transform(X2a)

            band = build_refinement_band(X1ni, y1, feature_names=avail_named,
                                         monotonic_cst_map=mono_default, epsilon=EPSILON,
                                         depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
            band_unc = build_refinement_band(X1ni, y1, feature_names=avail_named,
                                             monotonic_cst_map={}, epsilon=EPSILON,
                                             depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
            distinct = band.distinct_members

            # (1) non-trivial
            non_trivial = len(distinct) >= 3
            # Refit distinct members on full V1 grade-G; collect used-feature sets,
            # V1-ranking score vectors, and V2-forward results. Each member is fit
            # on its own feature subset, so predict on the subsetted X.
            refit = [refit_member(m, _subset(X1ni, avail_named, m.feature_subset), y1,
                                  feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
            used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
            used_sets = [u for u in used_sets if u]  # drop members whose tree didn't split
            n_used_sets = len(set(used_sets))
            v1_scores = [mdl.predict_proba(_subset(X1ni, avail_named, m.feature_subset))[:, 1]
                         for mdl, m in zip(refit, distinct)]
            med_rho, min_rho = pairwise_ranking_spearman(v1_scores)
            # (2) plural
            plural = (n_used_sets >= 2) and (med_rho < 0.9)
            # (3) forward-prediction (per distinct member)
            fwd = [_oos(mdl, _subset(X2ni, avail_named, m.feature_subset), y2, perm_seed=10000 + gi * 100 + i)
                   for i, (mdl, m) in enumerate(zip(refit, distinct))]
            n_fwd_hit = sum(1 for r in fwd if r["verdict"] == "HIT")
            forward_predictive = n_fwd_hit > len(refit) / 2
            best_oos_constrained = max((r["oos_auc"] for r in fwd if r["oos_auc"] is not None), default=None)
            # (4) cost of the constraint
            best_unc = max(band_unc.members, key=lambda m: m.holdout_auc) if band_unc.members else None
            unc_oos = None
            if best_unc is not None:
                unc_model = refit_member(best_unc, _subset(X1ni, avail_named, best_unc.feature_subset), y1,
                                         feature_names=list(best_unc.feature_subset), seed=SEED)
                unc_oos = _oos(unc_model, _subset(X2ni, avail_named, best_unc.feature_subset), y2,
                               perm_seed=20000 + gi)["oos_auc"]
            # kitchen-sink: one depth-3 tree on named + extension, no monotonicity
            ks = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=SEED).fit(X1ai, y1)
            ks_oos = _oos(ks, X2ai, y2, perm_seed=30000 + gi)["oos_auc"]
            constraint_cheap = (best_oos_constrained is not None and unc_oos is not None
                                and best_oos_constrained >= 0.9 * unc_oos)

            nt += non_trivial; pl += plural; fp += forward_predictive; cc += constraint_cheap
            burst_rec["grades"][g] = {
                "n_v1": int(len(y1)), "n_v2": int(len(y2)),
                "default_rate_v1": round(float(y1.mean()), 4), "default_rate_v2": round(float(y2.mean()), 4),
                "n_combos_tried": band.n_combos_tried, "band_members_within_eps": len(band.members),
                "band_distinct_members": len(distinct), "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
                "distinct_used_feature_sets": [sorted(u) for u in sorted(set(used_sets), key=lambda x: (len(x), sorted(x)))],
                "n_distinct_used_feature_sets": n_used_sets,
                "median_pairwise_spearman": round(med_rho, 4), "min_pairwise_spearman": round(min_rho, 4),
                "n_forward_predicting_members": n_fwd_hit, "n_members_evaluated": len(refit),
                "best_oos_auc_constrained_band": best_oos_constrained,
                "best_oos_auc_unconstrained_best_member": unc_oos,
                "oos_auc_kitchen_sink_tree": ks_oos,
                "member_forward_results": [{"subset": list(m.feature_subset), "depth": m.max_depth,
                                            "leaf_min": m.min_samples_leaf, "holdout_auc": round(m.holdout_auc, 4),
                                            **fwd[i]} for i, m in enumerate(distinct)],
                "non_trivial": bool(non_trivial), "plural": bool(plural),
                "forward_predictive": bool(forward_predictive), "constraint_cheap": bool(constraint_cheap),
            }
            print(f"  {g}: n_v1={len(y1):5d}  band={len(band.members)}/{len(distinct)} distinct  "
                  f"used-feat-sets={n_used_sets}  med_rho={med_rho:.3f}  fwd={n_fwd_hit}/{len(refit)} HIT  "
                  f"bestOOS: con={best_oos_constrained} unc={unc_oos} ks={ks_oos}  "
                  f"-> NT={non_trivial} PL={plural} FP={forward_predictive} CC={constraint_cheap}", flush=True)

        burst_rec.update({
            "n_effective_grades": n_eff,
            "non_trivial_count": nt, "plural_count": pl, "forward_predictive_count": fp, "constraint_cheap_count": cc,
            "claim_holds": bool(n_eff > 0 and nt > n_eff / 2 and pl > n_eff / 2 and fp > n_eff / 2),
            "claim_falsified": bool(n_eff > 0 and (nt <= n_eff / 2 or pl <= n_eff / 2 or fp <= n_eff / 2)),
        })
        results["bursts"][burst_name] = burst_rec
        print(f"  -> [{burst_name}] of {n_eff} effective grades: non-trivial={nt} plural={pl} "
              f"forward-predictive={fp} constraint-cheap={cc}  ->  claim_holds={burst_rec['claim_holds']}", flush=True)

    # ---- Verdict ----
    holds = {n: results["bursts"][n]["claim_holds"] for n in BURSTS}
    falsified = {n: results["bursts"][n]["claim_falsified"] for n in BURSTS}
    plural_partial = {n: (results["bursts"][n]["plural_count"] <= results["bursts"][n]["n_effective_grades"] / 2
                          and results["bursts"][n]["non_trivial_count"] > results["bursts"][n]["n_effective_grades"] / 2
                          and results["bursts"][n]["forward_predictive_count"] > results["bursts"][n]["n_effective_grades"] / 2)
                      for n in BURSTS}
    results["verdict"] = {
        "claim_holds_per_burst": holds, "claim_falsified_per_burst": falsified,
        "plurality_is_the_soft_spot_per_burst": plural_partial,
        "summary": (
            "Substantive claim 'the policy-constrained Rashomon refinement set is non-trivial, plural, and "
            "forward-predictively valid' — " +
            (("HOLDS on: " + ", ".join(n for n, h in holds.items() if h)) if any(holds.values()) else "") +
            (("; FALSIFIED on: " + ", ".join(n for n, f in falsified.items() if f)) if any(falsified.values()) else "") +
            (". Plurality is the binding constraint on: " + ", ".join(n for n, p in plural_partial.items() if p)
             if any(plural_partial.values()) else ".")
        ),
    }
    print(f"\n{'#'*72}\nVERDICT: {results['verdict']['summary']}\n{'#'*72}", flush=True)

    out = Path("runs/within_tier_rashomon_test_results.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
