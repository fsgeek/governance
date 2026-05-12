"""Geometry of within-Rashomon disagreement -- orchestration.

Pre-registration: docs/superpowers/specs/2026-05-12-disagreement-geometry-preregistration-note.md.

Tests the post-hoc mechanism claim from the disagreement-routing result (`d(x)`
tracks where the within-tier residual feature is active) as a falsifiable claim,
on the 5 plural sub-grades of Burst D (#6: built on V1 = 2015Q3; rederived here,
not hardcoded). For each plural grade G:

  - rebuild the policy-constrained refinement epsilon-band (identical #6
    construction), refit its distinct members on the full V1 grade, compute
    d(x) = std over members of predicted-default prob on each loan;
  - fit a shallow regression CART explaining d from the policy-NAMED features,
    and from NAMED + EXTENSION features (CV R^2; root-split feature; importances);
  - univariate Spearman of each named feature with d; partial-dependence profile
    of d on the named explainer's root feature (shape: tails / threshold /
    monotone / flat); Spearman of |dti - 43| and |fico - 620| with d.

Then roll up the pre-registered predictions over the plural grades:
  P1  named features explain d (CV R^2 >= 0.3 OR |rho_top| >= 0.3) on >= 3/5
  P2  the dominant driver is the same single feature on >= 3/5 (P2-dti: it is dti)
  P3  d concentrates in the tails of that feature on >= 3/5 (P3-threshold: in an
      interior bump instead)
  P4  (rescue branch) extension features add Delta-R^2 >= 0.1 on >= 3/5 AND named
      R^2 < 0.3 on >= 3/5  ->  disagreement keys on un-named structure  ->  the
      routing claim is partially un-deflated on a "the policy is blind here" basis

V1 (2015Q3) is the primary arm; the band is also re-evaluated on V2 (2015Q4) --
members frozen, d recomputed on V2's loans -- as a robustness arm.

Usage:
    PYTHONPATH=. python scripts/disagreement_geometry_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from policy.encoder import load_policy
from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)
from wedge.routing import (
    consensus_scores,
    cross_tier_consistency,
    disagreement_explainer,
    partial_dependence_profile,
    per_borrower_disagreement,
    threshold_proximity_correlation,
    univariate_disagreement_correlations,
)

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
TERM = "36 months"
POLICY_PATH = "policy/thin_demo_hmda.yaml"
SWEEP_SUMMARY = Path("runs/pricing-lc-sweep-36mo-summary.json")
OUT = Path("runs/disagreement_geometry_test_results.json")

V1, V2 = "2015Q3", "2015Q4"  # Burst D of #6.

NAMED_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
EXTENSION_FEATURES = ["revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
                      "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec"]

# Same band construction as #6.
EPSILON, DEPTHS, LEAF_MINS, SEED = 0.02, (1, 2, 3), (25, 50, 100), 0
PLURALITY_RHO_MAX = 0.9

# Explainer hyperparameters (pre-reg §2).
EX_MAX_DEPTH, EX_LEAF_MIN, EX_FOLDS = 3, 50, 5
N_DECILE = 10
R2_GOOD, RHO_GOOD, DELTA_R2 = 0.30, 0.30, 0.10
DTI_CEILING, FICO_FLOOR = 43.0, 620.0


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


def _grade_X(df: pd.DataFrame, grade: str, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    sub = df[df["sub_grade"] == grade]
    X = sub[cols].to_numpy(dtype=float)
    y = (sub["label"] == 0).to_numpy(dtype=int)  # 1 = default (unused here, kept for parity)
    return X, y


def _subset(X: np.ndarray, feature_names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    idx = {f: i for i, f in enumerate(feature_names)}
    return X[:, [idx[f] for f in subset]]


def _disagreement(refit_models: list, members: list, X_named: np.ndarray,
                  feature_names: list[str]) -> np.ndarray:
    rows = [mdl.predict_proba(_subset(X_named, feature_names, m.feature_subset))[:, 1]
            for mdl, m in zip(refit_models, members)]
    return per_borrower_disagreement(np.vstack(rows))


def _geometry_arm(d: np.ndarray, X_named_imp: np.ndarray, X_all_imp: np.ndarray,
                  avail_named: list[str], avail_all: list[str], *, seed: int) -> dict:
    """All geometry stats for one (d, named-features, all-features) triple."""
    ex_named = disagreement_explainer(d, X_named_imp, avail_named, max_depth=EX_MAX_DEPTH,
                                      min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=seed)
    ex_all = disagreement_explainer(d, X_all_imp, avail_all, max_depth=EX_MAX_DEPTH,
                                    min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=seed)
    uni = univariate_disagreement_correlations(d, X_named_imp, avail_named, n_deciles=N_DECILE)
    root = ex_named.get("root_feature")
    if root is not None and root in avail_named:
        prof = partial_dependence_profile(d, X_named_imp[:, avail_named.index(root)], n_deciles=N_DECILE)
    else:
        prof = {"shape": None, "tail_ratio": None, "argmax_bucket": None, "decile_mean_d": [], "n_buckets": 0}
    dti_col = X_named_imp[:, avail_named.index("dti")] if "dti" in avail_named else None
    fico_col = X_named_imp[:, avail_named.index("fico_range_low")] if "fico_range_low" in avail_named else None
    prox = threshold_proximity_correlation(d, dti_col, fico_col, dti_ceiling=DTI_CEILING, fico_floor=FICO_FLOOR)
    r2n = ex_named.get("cv_r2")
    r2a = ex_all.get("cv_r2")
    rho_top = None
    if root is not None and root in uni and uni[root]["spearman_rho"] is not None:
        rho_top = abs(uni[root]["spearman_rho"])
    well_explained = bool((r2n is not None and r2n >= R2_GOOD) or (rho_top is not None and rho_top >= RHO_GOOD))
    delta_r2 = None if (r2n is None or r2a is None) else round(r2a - r2n, 4)
    return {
        "d_summary": {"min": round(float(d.min()), 6), "median": round(float(np.median(d)), 6),
                      "max": round(float(d.max()), 6), "mean": round(float(d.mean()), 6),
                      "std": round(float(d.std()), 6)},
        "explainer_named": ex_named, "explainer_named_plus_extension": ex_all, "delta_r2": delta_r2,
        "root_feature": root, "rho_top_abs": None if rho_top is None else round(rho_top, 4),
        "well_explained": well_explained,
        "pd_profile_on_root": prof, "univariate": uni, "threshold_proximity": prox,
    }


def _roll_up(grades: dict, plural: list[str], arm_key: str) -> dict:
    """Pre-registered P1-P4 over the plural grades for one arm ('v1' / 'v2')."""
    n = len(plural)
    maj = n / 2
    arms = {g: grades[g][arm_key] for g in plural if arm_key in grades.get(g, {})}
    well = [g for g in plural if arms.get(g, {}).get("well_explained")]
    tops = {g: arms.get(g, {}).get("root_feature") for g in plural}
    shapes = {g: arms.get(g, {}).get("pd_profile_on_root", {}).get("shape") for g in plural}
    cons = cross_tier_consistency(tops, shapes)
    p1 = len(well) > maj
    p2 = bool(cons["dominant_feature"]["majority"])
    p2_dti = bool(p2 and cons["dominant_feature"]["modal"] == "dti")
    shape_counts = cons["pd_shape"]["counts"]
    p3_tails = shape_counts.get("tails", 0) > maj
    p3_threshold = shape_counts.get("threshold", 0) > maj
    r2n = {g: arms.get(g, {}).get("explainer_named", {}).get("cv_r2") for g in plural}
    dr2 = {g: arms.get(g, {}).get("delta_r2") for g in plural}
    n_dr2_big = sum(1 for v in dr2.values() if v is not None and v >= DELTA_R2)
    n_r2n_small = sum(1 for v in r2n.values() if v is not None and v < R2_GOOD)
    p4 = (n_dr2_big > maj) and (n_r2n_small > maj)
    return {
        "n_plural": n, "plural_grades": plural,
        "P1_named_features_explain_d": {"well_explained_grades": well, "n": len(well), "hit": bool(p1)},
        "P2_same_dominant_driver": {"per_grade_root": tops, **cons["dominant_feature"], "hit": bool(p2),
                                    "P2_dti_hit": p2_dti},
        "P3_concentration": {"per_grade_shape": shapes, "shape_counts": shape_counts,
                             "P3_tails_hit": bool(p3_tails), "P3_threshold_hit": bool(p3_threshold)},
        "P4_rescue_extension_features": {"per_grade_named_r2": r2n, "per_grade_delta_r2": dr2,
                                         "n_delta_r2_ge_0.1": n_dr2_big, "n_named_r2_lt_0.3": n_r2n_small,
                                         "hit": bool(p4)},
        "threshold_proximity_max_abs_rho_per_grade": {
            g: arms.get(g, {}).get("threshold_proximity", {}).get("max_abs_rho") for g in plural},
    }


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *NAMED_FEATURES, *EXTENSION_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    pc = load_policy(POLICY_PATH)
    avail_named = [f for f in NAMED_FEATURES if f in raw.columns]
    avail_all = [f for f in NAMED_FEATURES + EXTENSION_FEATURES if f in raw.columns]
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in avail_named}
    print(f"  policy '{pc.name}': named in LC = {avail_named}; extension = "
          f"{[f for f in EXTENSION_FEATURES if f in raw.columns]}; mono(default) = {mono_default}", flush=True)

    df1, df2 = _prep(raw, V1), _prep(raw, V2)
    flagged = _flagged_grades(V1)
    print(f"\n{'='*78}\nBurst D geometry: bands on {V1} ({len(df1)} loans); robustness on {V2} "
          f"({len(df2)} loans)\n  flagged Cat-2 grades in {V1}: {flagged}\n{'='*78}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-disagreement-geometry-preregistration-note.md",
        "burst": "D_2015H2_dti", "v1": V1, "v2": V2, "policy": pc.name,
        "monotonic_cst_default_convention": mono_default,
        "named_features": avail_named, "extension_features": [f for f in EXTENSION_FEATURES if f in raw.columns],
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                        "seed": SEED, "plurality_rho_max": PLURALITY_RHO_MAX},
        "explainer_params": {"max_depth": EX_MAX_DEPTH, "min_samples_leaf": EX_LEAF_MIN, "cv_folds": EX_FOLDS,
                             "n_deciles": N_DECILE, "r2_good": R2_GOOD, "rho_good": RHO_GOOD,
                             "delta_r2": DELTA_R2, "dti_ceiling": DTI_CEILING, "fico_floor": FICO_FLOOR},
        "flagged_grades_v1": flagged, "grades": {},
    }

    plural: list[str] = []
    for gi, g in enumerate(flagged):
        X1n, _ = _grade_X(df1, g, avail_named)
        X2n, _ = _grade_X(df2, g, avail_named)
        X1a, _ = _grade_X(df1, g, avail_all)
        X2a, _ = _grade_X(df2, g, avail_all)
        y1 = (df1[df1["sub_grade"] == g]["label"] == 0).to_numpy(dtype=int)
        if y1.size < 50 or y1.min() == y1.max():
            print(f"  {g}: SKIP (degenerate / too few)", flush=True)
            results["grades"][g] = {"verdict": "SKIP"}
            continue
        imp_n = SimpleImputer(strategy="median").fit(X1n)
        imp_a = SimpleImputer(strategy="median").fit(X1a)
        X1ni, X2ni = imp_n.transform(X1n), imp_n.transform(X2n)
        X1ai, X2ai = imp_a.transform(X1a), imp_a.transform(X2a)

        band = build_refinement_band(X1ni, y1, feature_names=avail_named, monotonic_cst_map=mono_default,
                                     epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
        distinct = band.distinct_members
        if len(distinct) < 2:
            print(f"  {g}: SKIP (band <2 distinct members)", flush=True)
            results["grades"][g] = {"verdict": "SKIP", "band_distinct_members": len(distinct)}
            continue
        refit = [refit_member(m, _subset(X1ni, avail_named, m.feature_subset), y1,
                              feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
        used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
        n_used_sets = len({u for u in used_sets if u})
        v1_scores = [mdl.predict_proba(_subset(X1ni, avail_named, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct)]
        med_rho, min_rho = pairwise_ranking_spearman(v1_scores)
        is_plural = (len(distinct) >= 3) and (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)
        if is_plural:
            plural.append(g)

        d1 = per_borrower_disagreement(np.vstack(v1_scores))
        d2 = _disagreement(refit, distinct, X2ni, avail_named)
        arm1 = _geometry_arm(d1, X1ni, X1ai, avail_named, avail_all, seed=SEED)
        arm2 = _geometry_arm(d2, X2ni, X2ai, avail_named, avail_all, seed=SEED)
        results["grades"][g] = {
            "n_v1": int(y1.size), "band_members_within_eps": len(band.members),
            "band_distinct_members": len(distinct), "n_distinct_used_feature_sets": n_used_sets,
            "median_pairwise_spearman_v1": round(med_rho, 4), "min_pairwise_spearman_v1": round(min_rho, 4),
            "plural": bool(is_plural), "v1": arm1, "v2": arm2,
        }
        en1, ea1 = arm1["explainer_named"], arm1["explainer_named_plus_extension"]
        print(f"  {g}: n={y1.size:5d} band={len(band.members)}/{len(distinct)} plural={is_plural} "
              f"(med_rho={med_rho:.3f}) | V1 d~feat: root={en1.get('root_feature')} "
              f"R2_named={en1.get('cv_r2')} R2_all={ea1.get('cv_r2')} dR2={arm1['delta_r2']} "
              f"|rho_top|={arm1['rho_top_abs']} shape={arm1['pd_profile_on_root'].get('shape')} "
              f"well={arm1['well_explained']} prox_rho={arm1['threshold_proximity'].get('max_abs_rho')}", flush=True)

    results["plural_grades"] = plural
    roll_v1 = _roll_up(results["grades"], plural, "v1")
    roll_v2 = _roll_up(results["grades"], plural, "v2")
    results["verdict_v1_primary"] = roll_v1
    results["verdict_v2_robustness"] = roll_v2

    p1, p2 = roll_v1["P1_named_features_explain_d"]["hit"], roll_v1["P2_same_dominant_driver"]["hit"]
    p2dti = roll_v1["P2_same_dominant_driver"]["P2_dti_hit"]
    p3t, p3th = roll_v1["P3_concentration"]["P3_tails_hit"], roll_v1["P3_concentration"]["P3_threshold_hit"]
    p4 = roll_v1["P4_rescue_extension_features"]["hit"]
    modal = roll_v1["P2_same_dominant_driver"]["modal"]
    shape_word = ("tails" if p3t else ("interior threshold bump" if p3th else "no consistent shape"))
    routing_implication = ("P4 fired -> the band disagrees about un-named structure -> the disagreement-routing "
                           "claim is PARTIALLY UN-DEFLATED on a 'the documented policy is blind here' basis"
                           if p4 else
                           "P4 did not fire -> the residual-tracking reading stands, routing stays deflated"
                           if p1 else
                           "P1 failed too -> d is not well-explained by the policy features at all "
                           "(neither residual-tracking confirmed nor a clean policy-blindness signal)")
    summary = (
        f"Disagreement geometry, Burst D, {len(plural)} plural grades {plural} (primary arm = V1 {V1}): "
        f"P1 (named features explain d) {'HIT' if p1 else 'MISS'} "
        f"({roll_v1['P1_named_features_explain_d']['n']}/{len(plural)} well-explained); "
        f"P2 (same dominant driver) {'HIT' if p2 else 'MISS'}"
        f"{f' [modal={modal}]' if modal else ''}{', P2-dti HIT' if p2dti else ''}; "
        f"P3 concentration = {shape_word}; "
        f"P4 (rescue: extension features explain d where named ones don't) {'HIT' if p4 else 'MISS'}. "
        f"Routing implication: {routing_implication}."
    )
    results["summary"] = summary
    print(f"\n{'#'*78}\n{summary}\n{'#'*78}", flush=True)

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
