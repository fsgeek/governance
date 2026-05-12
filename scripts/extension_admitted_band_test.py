"""Extension-admitted refinement bands and the locus of within-Rashomon disagreement.

Pre-registration: docs/superpowers/specs/2026-05-12-extension-admitted-band-preregistration-note.md.

Repairs the disagreement-geometry P4 (rescue) branch, which was structurally
vacuous: the #6 refinement bands (`scripts/within_tier_rashomon_test.py`) are
built over the policy-NAMED features only, so d(x) -- the per-borrower
disagreement among the distinct band members -- is by construction a pure
function of the named features, and the 9 extension underwriting features add
delta-R^2 ~ 0 trivially.

This test rebuilds the Burst-D refinement epsilon-band with the extension
features ADMITTED into the candidate feature set (the thin-demo policy's
monotonicity directions still enforced on the *named* features; the extension
features unconstrained), recomputes d_ext, and asks:

  A   do the band's distinct members actually use the extension features at all
      (or is the policy vocabulary AUC-sufficient within these tiers at eps=0.02)?
  P4  (headline, rescue) is d_ext still well-explained by the policy-NAMED
      features alone (R2_named_ext >= 0.3) -- or has the locus of disagreement
      moved to structure the policy vocabulary cannot name (R2_named_ext < 0.3 on
      >maj AND named+extension recovers it: delta-R2_ext >= 0.1 on >maj)?
  P4-soft  does the named explainer's grip drop by >= 15 R^2-points relative to
      the #6 (named-only) band on >maj grades (the "partly moved" reading)?
  P5  does admitting the extension features flip which grades are *plural*?

If P4 fires the disagreement-routing deflation is partially un-deflated on a
"the documented policy is blind here" basis (which is ECOA/Reg-B
disparate-impact adjacent). If A misses, the deflation is reinforced.

V1 = 2015Q3 (build the bands, primary arm); V2 = 2015Q4 (band frozen, d_ext
recomputed -- robustness arm). Same #6 band construction otherwise (eps=0.02,
depths {1,2,3}, leaf-mins {25,50,100}, seed 0). The #6 named-only band's
named-explainer R^2 per grade is read from runs/disagreement_geometry_test_results.json
for the delta-R2_band comparison.

Usage:
    PYTHONPATH=. python scripts/extension_admitted_band_test.py
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
GEOMETRY_RESULTS = Path("runs/disagreement_geometry_test_results.json")  # for the #6-band comparison
OUT = Path("runs/extension_admitted_band_test_results.json")

V1, V2 = "2015Q3", "2015Q4"  # Burst D of #6.

NAMED_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
EXTENSION_FEATURES = ["revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
                      "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec"]

# Same band construction as #6 (the only change: candidate set = named + extension).
EPSILON, DEPTHS, LEAF_MINS, SEED = 0.02, (1, 2, 3), (25, 50, 100), 0
PLURALITY_RHO_MAX = 0.9

# Explainer hyperparameters (identical to the geometry test, so R^2 is comparable).
EX_MAX_DEPTH, EX_LEAF_MIN, EX_FOLDS = 3, 50, 5
N_DECILE = 10
R2_GOOD, RHO_GOOD, DELTA_R2 = 0.30, 0.30, 0.10
DELTA_R2_BAND_SOFT = -0.15  # P4-soft: named-explainer R^2 drops by >= 15 pts vs the #6 band
DTI_CEILING, FICO_FLOOR = 43.0, 620.0

SIX_PLURAL = {"A5", "B1", "C1", "C5", "D4"}  # the #6 plural set (geometry result), for the comparison


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


def _six_band_named_r2() -> dict:
    """#6 (named-only) band: named-explainer CV R^2 of d on V1, per grade."""
    try:
        geo = json.loads(GEOMETRY_RESULTS.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    out = {}
    for g, rec in geo.get("grades", {}).items():
        v1 = rec.get("v1") or {}
        en = v1.get("explainer_named") or {}
        if en.get("cv_r2") is not None:
            out[g] = en["cv_r2"]
    return out


def _grade_X(df: pd.DataFrame, grade: str, cols: list[str]) -> np.ndarray:
    return df[df["sub_grade"] == grade][cols].to_numpy(dtype=float)


def _subset(X: np.ndarray, feature_names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    idx = {f: i for i, f in enumerate(feature_names)}
    return X[:, [idx[f] for f in subset]]


def _geometry_arm(d: np.ndarray, X_named_imp: np.ndarray, X_all_imp: np.ndarray,
                  avail_named: list[str], avail_all: list[str], *, seed: int) -> dict:
    """All geometry stats for one (d, named-features, named+extension-features) triple
    -- identical to the geometry test's _geometry_arm (so the numbers are comparable)."""
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
    r2n, r2a = ex_named.get("cv_r2"), ex_all.get("cv_r2")
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


def _roll_up(grades: dict, headline: list[str], arm_key: str, six_named_r2: dict) -> dict:
    """Pre-registered A / P4-strict / P4-soft over the headline-plural grades, one arm ('v1'/'v2')."""
    n = len(headline)
    arms = {g: grades[g][arm_key] for g in headline if arm_key in grades.get(g, {})}
    well = [g for g in headline if arms.get(g, {}).get("well_explained")]
    tops = {g: arms.get(g, {}).get("root_feature") for g in headline}
    shapes = {g: arms.get(g, {}).get("pd_profile_on_root", {}).get("shape") for g in headline}
    cons = cross_tier_consistency(tops, shapes)
    uses_ext = {g: bool(grades[g].get("uses_extension")) for g in headline}
    n_uses_ext = sum(1 for v in uses_ext.values() if v)
    r2n = {g: arms.get(g, {}).get("explainer_named", {}).get("cv_r2") for g in headline}
    r2a = {g: arms.get(g, {}).get("explainer_named_plus_extension", {}).get("cv_r2") for g in headline}
    dr2 = {g: arms.get(g, {}).get("delta_r2") for g in headline}
    # delta-R2_band only meaningful on V1 (the #6 numbers are V1); compute it anyway, report on v1.
    dr2_band = {g: (None if (r2n.get(g) is None or six_named_r2.get(g) is None)
                    else round(r2n[g] - six_named_r2[g], 4)) for g in headline}
    n_dr2_big = sum(1 for v in dr2.values() if v is not None and v >= DELTA_R2)
    n_r2n_small = sum(1 for v in r2n.values() if v is not None and v < R2_GOOD)
    n_dr2band_soft = sum(1 for v in dr2_band.values() if v is not None and v <= DELTA_R2_BAND_SOFT)
    maj = n / 2
    return {
        "n_headline_plural": n, "headline_plural_grades": headline,
        "A_band_uses_extension": {"per_grade": uses_ext, "n_using": n_uses_ext, "hit": bool(n_uses_ext > maj)},
        "P1ish_named_features_explain_d_ext": {"well_explained_grades": well, "n": len(well),
                                               "still_named_legible_on_majority": bool(len(well) > maj)},
        "P2ish_same_dominant_driver": {"per_grade_root": tops, **cons["dominant_feature"]},
        "P3ish_concentration": {"per_grade_shape": shapes, "shape_counts": cons["pd_shape"]["counts"]},
        "P4_strict_rescue": {"per_grade_named_r2": r2n, "per_grade_all_r2": r2a, "per_grade_delta_r2": dr2,
                             "n_delta_r2_ge_0.1": n_dr2_big, "n_named_r2_lt_0.3": n_r2n_small,
                             "hit": bool(n_dr2_big > maj and n_r2n_small > maj)},
        "P4_soft_named_grip_drops_vs_six": {"per_grade_named_r2_six_band": {g: six_named_r2.get(g) for g in headline},
                                            "per_grade_delta_r2_band": dr2_band,
                                            "n_delta_r2_band_le_neg0.15": n_dr2band_soft,
                                            "hit": bool(n_dr2band_soft > maj)},
        "threshold_proximity_max_abs_rho_per_grade": {
            g: arms.get(g, {}).get("threshold_proximity", {}).get("max_abs_rho") for g in headline},
    }


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *NAMED_FEATURES, *EXTENSION_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    pc = load_policy(POLICY_PATH)
    avail_named = [f for f in NAMED_FEATURES if f in raw.columns]
    avail_ext = [f for f in EXTENSION_FEATURES if f in raw.columns]
    avail_all = avail_named + avail_ext
    # Policy states monotonicity w.r.t. GRANT probability; refinements predict DEFAULT, so negate.
    # Only the NAMED features get a direction; the extension features are unconstrained (the
    # documented policy is silent about them) -- missing keys in build_refinement_band => unconstrained.
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in avail_named}
    six_named_r2 = _six_band_named_r2()
    print(f"  policy '{pc.name}': named in LC = {avail_named}; extension in LC = {avail_ext}; "
          f"mono(default, named only) = {mono_default}", flush=True)
    print(f"  #6 named-only band named-explainer R^2 (V1, from {GEOMETRY_RESULTS.name}): {six_named_r2}", flush=True)

    df1, df2 = _prep(raw, V1), _prep(raw, V2)
    flagged = _flagged_grades(V1)
    print(f"\n{'='*82}\nExtension-admitted bands: build on {V1} ({len(df1)} loans); robustness on {V2} "
          f"({len(df2)} loans)\n  flagged Cat-2 grades in {V1}: {flagged} ({len(flagged)})\n"
          f"  candidate set = {len(avail_all)} features ({2**len(avail_all)-1} subsets x "
          f"{len(DEPTHS)*len(LEAF_MINS)} hyper-cells per grade)\n{'='*82}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-extension-admitted-band-preregistration-note.md",
        "burst": "D_2015H2_dti", "v1": V1, "v2": V2, "policy": pc.name,
        "monotonic_cst_default_convention_named_only": mono_default,
        "named_features": avail_named, "extension_features": avail_ext,
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                        "seed": SEED, "plurality_rho_max": PLURALITY_RHO_MAX,
                        "candidate_set": "named + extension"},
        "explainer_params": {"max_depth": EX_MAX_DEPTH, "min_samples_leaf": EX_LEAF_MIN, "cv_folds": EX_FOLDS,
                             "n_deciles": N_DECILE, "r2_good": R2_GOOD, "rho_good": RHO_GOOD,
                             "delta_r2": DELTA_R2, "delta_r2_band_soft": DELTA_R2_BAND_SOFT,
                             "dti_ceiling": DTI_CEILING, "fico_floor": FICO_FLOOR},
        "six_named_only_band_plural_set": sorted(SIX_PLURAL),
        "six_named_only_band_named_explainer_r2_v1": six_named_r2,
        "flagged_grades_v1": flagged, "grades": {},
    }

    plural_ext: list[str] = []
    for g in flagged:
        X1n, X2n = _grade_X(df1, g, avail_named), _grade_X(df2, g, avail_named)
        X1a, X2a = _grade_X(df1, g, avail_all), _grade_X(df2, g, avail_all)
        y1 = (df1[df1["sub_grade"] == g]["label"] == 0).to_numpy(dtype=int)  # 1 = default
        if y1.size < 50 or y1.min() == y1.max():
            print(f"  {g}: SKIP (degenerate / too few)", flush=True)
            results["grades"][g] = {"verdict": "SKIP"}
            continue
        imp_n = SimpleImputer(strategy="median").fit(X1n)
        imp_a = SimpleImputer(strategy="median").fit(X1a)
        X1ni, X2ni = imp_n.transform(X1n), imp_n.transform(X2n)
        X1ai, X2ai = imp_a.transform(X1a), imp_a.transform(X2a)

        # The one change vs the geometry test: candidate set = named + extension.
        band = build_refinement_band(X1ai, y1, feature_names=avail_all, monotonic_cst_map=mono_default,
                                     epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
        distinct = band.distinct_members
        if len(distinct) < 2:
            print(f"  {g}: SKIP (band <2 distinct members)", flush=True)
            results["grades"][g] = {"verdict": "SKIP", "band_distinct_members": len(distinct)}
            continue
        refit = [refit_member(m, _subset(X1ai, avail_all, m.feature_subset), y1,
                              feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
        used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
        n_used_sets = len({u for u in used_sets if u})
        # Extension-usage diagnostic (A).
        ext_per_member = [sorted(u & set(avail_ext)) for u in used_sets]
        ext_used_union = sorted(set().union(*[set(u) for u in ext_per_member]) if ext_per_member else set())
        n_members_using_ext = sum(1 for u in ext_per_member if u)
        ext_feature_member_counts = {f: sum(1 for u in ext_per_member if f in u) for f in avail_ext}
        ext_feature_member_counts = {f: c for f, c in ext_feature_member_counts.items() if c > 0}

        v1_scores = [mdl.predict_proba(_subset(X1ai, avail_all, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct)]
        v2_scores = [mdl.predict_proba(_subset(X2ai, avail_all, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct)]
        med_rho, min_rho = pairwise_ranking_spearman(v1_scores)
        is_plural = (len(distinct) >= 3) and (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)
        if is_plural:
            plural_ext.append(g)

        d1 = per_borrower_disagreement(np.vstack(v1_scores))
        d2 = per_borrower_disagreement(np.vstack(v2_scores))
        arm1 = _geometry_arm(d1, X1ni, X1ai, avail_named, avail_all, seed=SEED)
        arm2 = _geometry_arm(d2, X2ni, X2ai, avail_named, avail_all, seed=SEED)
        results["grades"][g] = {
            "n_v1": int(y1.size), "default_rate_v1": round(float(y1.mean()), 4),
            "n_combos_tried": band.n_combos_tried, "band_members_within_eps": len(band.members),
            "band_distinct_members": len(distinct), "n_distinct_used_feature_sets": n_used_sets,
            "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
            "distinct_used_feature_sets": [sorted(u) for u in sorted({u for u in used_sets if u},
                                                                     key=lambda x: (len(x), sorted(x)))],
            "median_pairwise_spearman_v1": round(med_rho, 4), "min_pairwise_spearman_v1": round(min_rho, 4),
            "uses_extension": bool(n_members_using_ext > 0),
            "extension_features_used_union": ext_used_union,
            "n_distinct_members_using_extension": n_members_using_ext,
            "extension_feature_member_counts": ext_feature_member_counts,
            "in_six_plural_set": g in SIX_PLURAL, "plural": bool(is_plural), "v1": arm1, "v2": arm2,
        }
        en1, ea1 = arm1["explainer_named"], arm1["explainer_named_plus_extension"]
        six_r2 = six_named_r2.get(g)
        print(f"  {g}: n={y1.size:5d} band={len(band.members)}/{len(distinct)} usedsets={n_used_sets} "
              f"plural={is_plural}(med_rho={med_rho:.3f}) | ext_used={ext_used_union} "
              f"({n_members_using_ext}/{len(distinct)} members) | V1 d_ext~feat: root={en1.get('root_feature')} "
              f"R2_named={en1.get('cv_r2')} R2_all={ea1.get('cv_r2')} dR2={arm1['delta_r2']} "
              f"(#6 R2_named={six_r2}) shape={arm1['pd_profile_on_root'].get('shape')} "
              f"well={arm1['well_explained']}", flush=True)

    results["plural_grades_extended_band_v1"] = plural_ext
    headline = sorted(set(plural_ext) & SIX_PLURAL)
    became_plural = sorted(set(plural_ext) - SIX_PLURAL)
    lost_plural = sorted(SIX_PLURAL - set(plural_ext) - {g for g, r in results["grades"].items()
                                                          if isinstance(r, dict) and r.get("verdict") == "SKIP"})
    # P5: did the candidate-set change flip any flagged grade's plurality?
    p5_hit = bool(became_plural or lost_plural)
    results["plurality_comparison"] = {
        "extended_band_plural": plural_ext, "six_named_only_band_plural": sorted(SIX_PLURAL),
        "headline_plural_intersection": headline,
        "became_plural_under_extended_band": became_plural,
        "lost_plurality_under_extended_band": lost_plural,
        "P5_plurality_flipped": p5_hit,
    }

    if not headline:
        results["verdict_v1_primary"] = {"note": "no grade is plural under BOTH the extended band and the #6 band"}
        results["verdict_v2_robustness"] = results["verdict_v1_primary"]
        summary = ("Extension-admitted bands, Burst D: NO grade is plural under both the extended band and the "
                   f"#6 named-only band (extended-plural={plural_ext}, #6-plural={sorted(SIX_PLURAL)}). "
                   "P4 not assessable on a common set; see plurality_comparison.")
        results["summary"] = summary
        print(f"\n{'#'*82}\n{summary}\n{'#'*82}", flush=True)
        OUT.write_text(json.dumps(results, indent=2))
        print(f"\nwrote {OUT}", flush=True)
        return 0

    roll_v1 = _roll_up(results["grades"], headline, "v1", six_named_r2)
    roll_v2 = _roll_up(results["grades"], headline, "v2", six_named_r2)
    results["verdict_v1_primary"] = roll_v1
    results["verdict_v2_robustness"] = roll_v2

    a_hit = roll_v1["A_band_uses_extension"]["hit"]
    p4s = roll_v1["P4_strict_rescue"]["hit"]
    p4soft = roll_v1["P4_soft_named_grip_drops_vs_six"]["hit"]
    still_named = roll_v1["P1ish_named_features_explain_d_ext"]["still_named_legible_on_majority"]
    n_using = roll_v1["A_band_uses_extension"]["n_using"]
    n_h = len(headline)
    if p4s:
        routing = ("P4 fired -> the band's disagreement keys on structure the policy vocabulary cannot name "
                   "-> the disagreement-routing deflation is PARTIALLY UN-DEFLATED on a 'the documented policy "
                   "is blind here' basis (ECOA/Reg-B disparate-impact adjacent)")
    elif not a_hit:
        routing = ("A missed -> the policy-named features are AUC-sufficient within these tiers at eps=0.02; the "
                   "extension features don't enter a competitive refinement -> deflation REINFORCED (and a "
                   "codification-infrastructure counter-instance: the thin demo's 4 features are predictively, "
                   "not just legally, sufficient here)")
    elif p4soft:
        routing = ("P4-strict missed but P4-soft fired -> the locus of disagreement PARTLY moved to un-named "
                   "structure (named-explainer grip dropped vs the #6 band) without fully leaving the policy "
                   "vocabulary -> a weak reprieve for routing; report the per-tier picture")
    else:
        routing = ("P4 missed despite the band using extension features -> the disagreement stays a legible "
                   "function of the policy-NAMED features even with a wider feature view -> the residual-tracking "
                   "reading HARDENS; routing stays deflated")
    summary = (
        f"Extension-admitted bands, Burst D, headline-plural set {headline} "
        f"(= extended-plural {plural_ext} INT #6-plural {sorted(SIX_PLURAL)}; "
        f"became-plural={became_plural}, lost-plurality={lost_plural}; primary arm = V1 {V1}): "
        f"A (band uses extension features) {'HIT' if a_hit else 'MISS'} ({n_using}/{n_h} headline grades); "
        f"d_ext still named-legible on a majority: {still_named} "
        f"({roll_v1['P1ish_named_features_explain_d_ext']['n']}/{n_h}); "
        f"P4-strict (R2_named_ext<0.3 on >maj AND dR2_ext>=0.1 on >maj) {'HIT' if p4s else 'MISS'} "
        f"(n_dR2>=0.1={roll_v1['P4_strict_rescue']['n_delta_r2_ge_0.1']}, "
        f"n_R2_named<0.3={roll_v1['P4_strict_rescue']['n_named_r2_lt_0.3']}); "
        f"P4-soft (dR2_band<=-0.15 vs #6 on >maj) {'HIT' if p4soft else 'MISS'} "
        f"(n={roll_v1['P4_soft_named_grip_drops_vs_six']['n_delta_r2_band_le_neg0.15']}); "
        f"P5 (plurality flipped) {'HIT' if p5_hit else 'MISS'}. "
        f"Routing implication: {routing}."
    )
    results["summary"] = summary
    print(f"\n{'#'*82}\n{summary}\n{'#'*82}", flush=True)

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
