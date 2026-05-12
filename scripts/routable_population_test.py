"""Does within-Rashomon refinement-band disagreement *route* on the subprime tiers?

Pre-registration: docs/superpowers/specs/2026-05-12-routable-population-test-preregistration-note.md.

The extension-admitted-band result found that on subprime LC 2015H2 tiers the
per-borrower disagreement d_ext(x) among the policy-constrained refinement band's
members collapses off the documented 4-feature policy vocabulary onto the
extension underwriting features. This test asks whether that means the
disagreement *routes*: rebuild the extension-admitted bands DE-DUPED BY
USED-FEATURE-SET (the band-bloat fix -- the more principled "distinct
refinement"), recompute d_ext, fit a depth-<=3 named-feature CART explainer of
d_ext, form the residual r = d_ext - d_hat_named (the disagreement the policy
vocabulary cannot explain), and run the #6 routing metrics on three bucketings:

  (i)   terciles of r            -- the policy-blind bucketing (primary)
  (ii)  terciles of d_ext        -- raw disagreement (control / baseline)
  (iii) terciles of d_hat_named  -- the explained part (negative control: should
        deflate, replicating the #6 routing null)

plus, within the top d_ext tercile, a policy-blind-half (high r) vs
named-explained-half (low r) consensus-reliability contrast.

V1 = 2015Q3 (build bands, fit explainer), V2 = 2015Q4 (forward routing metrics);
a V1-in-sample arm for robustness. Aggregate over the *plural subprime* grades.
Reuses wedge/refinement_set.py + wedge/routing.py wholesale (no new wedge/ code).

Usage:
    PYTHONPATH=. python scripts/routable_population_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeRegressor

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
    brier_by_tercile,
    calibration_gap_vs_disagreement,
    consensus_scores,
    disagreement_explainer,
    ece,
    feature_space_outlierness,
    grade_routing_verdict,
    operational_lift,
    per_borrower_disagreement,
    tercile_labels,
    within_tercile_member_auc,
)

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
TERM = "36 months"
POLICY_PATH = "policy/thin_demo_hmda.yaml"
SWEEP_SUMMARY = Path("runs/pricing-lc-sweep-36mo-summary.json")
OUT = Path("runs/routable_population_test_results.json")

V1, V2 = "2015Q3", "2015Q4"  # Burst D of #6.

NAMED_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
EXTENSION_FEATURES = ["revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
                      "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec"]

# Subprime grades: well_explained=False in the extension-admitted-band test.
SUBPRIME = {"C1", "C2", "C5", "D4"}

# Band construction (same as #6 / extension-admitted; only de-dup differs).
EPSILON, DEPTHS, LEAF_MINS, SEED = 0.02, (1, 2, 3), (25, 50, 100), 0
PLURALITY_RHO_MAX = 0.9

# Explainer (depth-<=3 CART; comparable to geometry / extension-admitted tests).
EX_MAX_DEPTH, EX_LEAF_MIN, EX_FOLDS = 3, 50, 5
R2_GOOD = 0.30

# Routing metrics.
N_PERM, NULL_PCT, N_DECILE = 500, 95, 10

BUCKETINGS = ("residual_r", "raw_d_ext", "explained_d_hat_named")


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


def _grade_X(df: pd.DataFrame, grade: str, cols: list[str]) -> np.ndarray:
    return df[df["sub_grade"] == grade][cols].to_numpy(dtype=float)


def _grade_y(df: pd.DataFrame, grade: str) -> np.ndarray:
    return (df[df["sub_grade"] == grade]["label"] == 0).to_numpy(dtype=int)  # 1 = default


def _subset(X: np.ndarray, feature_names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    idx = {f: i for i, f in enumerate(feature_names)}
    return X[:, [idx[f] for f in subset]]


def _used_set_from_signature(member) -> frozenset:
    """The features the *train-split* tree splits on, read off the member's
    tree_signature = (subset, ((feat_pos, threshold), ...)) -- feat_pos indexes
    into subset (the tree was fit on X[:, subset])."""
    subset, nodes = member.tree_signature
    return frozenset(subset[i] for (i, _thr) in nodes)


def _dedup_by_used_feature_set(members: list) -> list:
    """One representative per used-feature-set (the highest-holdout-AUC one).
    The empty set (a stump that never split -- the constant model) is kept as one
    representative if present."""
    best: dict = {}
    for m in members:
        u = _used_set_from_signature(m)
        cur = best.get(u)
        if cur is None or m.holdout_auc > cur.holdout_auc:
            best[u] = m
    return list(best.values())


def _safe_auc(y: np.ndarray, s: np.ndarray):
    y = np.asarray(y)
    if y.size == 0 or y.min() == y.max():
        return None
    return float(roc_auc_score(y, np.asarray(s, dtype=float)))


def _brier(p: np.ndarray, y: np.ndarray):
    p, y = np.asarray(p, float), np.asarray(y, float)
    return None if p.size == 0 else float(np.mean((p - y) ** 2))


def _bucketing_arm(M: np.ndarray, y: np.ndarray, p_bar: np.ndarray, X_ref: np.ndarray,
                   X_eval: np.ndarray, bucket_var: np.ndarray, *, rng_seed: int) -> dict:
    """All four routing metrics + the outlier diagnostic + the routing booleans,
    for one (score matrix, labels, consensus, bucketing variable) on one arm."""
    terc = tercile_labels(bucket_var)
    m1 = within_tercile_member_auc(M, y, terc, n_perm=N_PERM, percentile=NULL_PCT, rng_seed=rng_seed)
    m2 = calibration_gap_vs_disagreement(bucket_var, p_bar, y, n_bins=N_DECILE)
    m3 = brier_by_tercile(p_bar, y, terc)
    m4 = operational_lift(p_bar, y, terc, n_bins=N_DECILE)
    out = feature_space_outlierness(X_eval, X_ref, terc)
    verdict = grade_routing_verdict(metric1=m1, metric2=m2, metric3=m3, metric4=m4)
    return {
        "tercile_sizes": {int(t): int((terc == t).sum()) for t in (0, 1, 2)},
        "metric1_tercile_member_auc": m1, "metric2_calibration_gap": m2,
        "metric3_consensus_brier_by_tercile": m3, "metric4_operational_lift": m4,
        "diagnostic_feature_space_outlierness": out, "routing_relevant": verdict,
    }


def _within_top_tercile_contrast(M: np.ndarray, y: np.ndarray, p_bar: np.ndarray,
                                 d_ext: np.ndarray, r: np.ndarray) -> dict:
    """Within the top d_ext tercile: policy-blind half (r above its within-tercile
    median) vs named-explained half (the rest) vs the full complement of the tier.
    Per cell: n, consensus Brier, consensus AUC, ECE, and min-over-members Brier."""
    terc = tercile_labels(d_ext)
    top = terc == 2
    comp = ~top
    out: dict = {"n_top_tercile": int(top.sum()), "n_complement": int(comp.sum())}
    if top.sum() < 4:
        out["note"] = "top tercile too small for the policy-blind / named-explained split"
        out["policy_blind_half"] = out["named_explained_half"] = None
        out["complement"] = _cell(M, y, p_bar, comp)
        out["routing_relevant_blind_worse_than_named"] = None
        return out
    r_top = r[top]
    med = float(np.median(r_top))
    blind_mask_local = r_top > med
    # map local masks back to full indices
    top_idx = np.flatnonzero(top)
    blind_idx = top_idx[blind_mask_local]
    named_idx = top_idx[~blind_mask_local]
    blind_full = np.zeros_like(top); blind_full[blind_idx] = True
    named_full = np.zeros_like(top); named_full[named_idx] = True
    cb = _cell(M, y, p_bar, blind_full)
    cn = _cell(M, y, p_bar, named_full)
    cc = _cell(M, y, p_bar, comp)
    out.update({"within_tercile_r_median": round(med, 6),
                "policy_blind_half": cb, "named_explained_half": cn, "complement": cc})
    bb, nb = cb.get("consensus_brier"), cn.get("consensus_brier")
    out["routing_relevant_blind_worse_than_named"] = (
        None if (bb is None or nb is None) else bool(bb > nb))
    # is a good member being averaged away in the blind half (vs the named half)?
    gap_blind = (None if (cb.get("min_member_brier") is None or bb is None) else round(bb - cb["min_member_brier"], 6))
    gap_named = (None if (cn.get("min_member_brier") is None or nb is None) else round(nb - cn["min_member_brier"], 6))
    out["consensus_minus_best_member_brier"] = {"policy_blind_half": gap_blind, "named_explained_half": gap_named,
        "good_member_more_averaged_away_in_blind_half": (
            None if (gap_blind is None or gap_named is None) else bool(gap_blind > gap_named))}
    return out


def _cell(M: np.ndarray, y: np.ndarray, p_bar: np.ndarray, mask: np.ndarray) -> dict:
    n = int(mask.sum())
    if n == 0:
        return {"n": 0, "consensus_brier": None, "consensus_auc": None, "ece": None,
                "min_member_brier": None, "n_default": 0}
    yy = y[mask]
    mm_brier = [float(np.mean((M[i, mask] - yy) ** 2)) for i in range(M.shape[0])]
    return {"n": n, "n_default": int(yy.sum()),
            "consensus_brier": round(_brier(p_bar[mask], yy), 6),
            "consensus_auc": (lambda a: None if a is None else round(a, 4))(_safe_auc(yy, p_bar[mask])),
            "ece": (lambda e: None if e is None else round(e, 6))(ece(p_bar[mask], yy, n_bins=N_DECILE)),
            "min_member_brier": round(min(mm_brier), 6) if mm_brier else None}


def _tally(grade_recs: dict, grades: list[str], arm: str, bucketing: str, key: str) -> list[int]:
    yes = no = 0
    for g in grades:
        v = (grade_recs.get(g, {}).get("arms", {}).get(arm, {}).get(bucketing, {})
             .get("routing_relevant", {}).get(key))
        if v is True:
            yes += 1
        elif v is False:
            no += 1
    return [yes, no]


def _hash123_yes(grade_recs: dict, grades: list[str], arm: str, bucketing: str) -> int:
    """Count grades where the #6-style m1 AND m2 AND m3 all point routing-relevant."""
    n = 0
    for g in grades:
        rr = (grade_recs.get(g, {}).get("arms", {}).get(arm, {}).get(bucketing, {}).get("routing_relevant", {}))
        if rr.get("m1_tercile_predictability_routing") and rr.get("m2_calibration_gap_routing") and rr.get("m3_brier_routing"):
            n += 1
    return n


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *NAMED_FEATURES, *EXTENSION_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    pc = load_policy(POLICY_PATH)
    avail_named = [f for f in NAMED_FEATURES if f in raw.columns]
    avail_ext = [f for f in EXTENSION_FEATURES if f in raw.columns]
    avail_all = avail_named + avail_ext
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in avail_named}
    print(f"  policy '{pc.name}': named={avail_named} ext={avail_ext} mono(default,named)={mono_default}", flush=True)

    df1, df2 = _prep(raw, V1), _prep(raw, V2)
    flagged = _flagged_grades(V1)
    subprime_flagged = [g for g in flagged if g in SUBPRIME]
    print(f"\n{'='*84}\nBuild on {V1} ({len(df1)} loans); forward routing on {V2} ({len(df2)} loans)\n"
          f"  flagged Cat-2 grades in {V1}: {flagged}\n  subprime among them: {subprime_flagged}\n"
          f"  candidate set = {len(avail_all)} features ({2**len(avail_all)-1} subsets x "
          f"{len(DEPTHS)*len(LEAF_MINS)} hyper-cells per grade)\n{'='*84}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-routable-population-test-preregistration-note.md",
        "burst": "D_2015H2_dti", "v1": V1, "v2": V2, "policy": pc.name,
        "monotonic_cst_default_convention_named_only": mono_default,
        "named_features": avail_named, "extension_features": avail_ext,
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                        "seed": SEED, "plurality_rho_max": PLURALITY_RHO_MAX,
                        "candidate_set": "named + extension", "dedup": "used-feature-set (highest-holdout-AUC representative)"},
        "explainer_params": {"max_depth": EX_MAX_DEPTH, "min_samples_leaf": EX_LEAF_MIN, "cv_folds": EX_FOLDS,
                             "r2_good": R2_GOOD},
        "routing_params": {"n_perm": N_PERM, "null_percentile": NULL_PCT, "n_deciles": N_DECILE},
        "bucketings": list(BUCKETINGS), "subprime_grades_definition": sorted(SUBPRIME),
        "flagged_grades_v1": flagged, "subprime_flagged_v1": subprime_flagged, "grades": {},
    }

    plural_grades: list[str] = []
    for gi, g in enumerate(flagged):
        X1n, X2n = _grade_X(df1, g, avail_named), _grade_X(df2, g, avail_named)
        X1a, X2a = _grade_X(df1, g, avail_all), _grade_X(df2, g, avail_all)
        y1, y2 = _grade_y(df1, g), _grade_y(df2, g)
        if y1.size < 50 or y1.min() == y1.max() or y2.size < 50 or y2.min() == y2.max():
            print(f"  {g}: SKIP (degenerate / too few: n_v1={y1.size} n_v2={y2.size})", flush=True)
            results["grades"][g] = {"verdict": "SKIP"}
            continue
        imp_n = SimpleImputer(strategy="median").fit(X1n)
        imp_a = SimpleImputer(strategy="median").fit(X1a)
        X1ni, X2ni = imp_n.transform(X1n), imp_n.transform(X2n)
        X1ai, X2ai = imp_a.transform(X1a), imp_a.transform(X2a)

        band = build_refinement_band(X1ai, y1, feature_names=avail_all, monotonic_cst_map=mono_default,
                                     epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
        if len(band.members) < 2:
            print(f"  {g}: SKIP (band <2 members within eps)", flush=True)
            results["grades"][g] = {"verdict": "SKIP", "band_members_within_eps": len(band.members)}
            continue
        distinct_uf = _dedup_by_used_feature_set(band.members)
        if len(distinct_uf) < 2:
            print(f"  {g}: SKIP (band <2 distinct-by-used-feature-set members)", flush=True)
            results["grades"][g] = {"verdict": "SKIP", "n_distinct_uf_members": len(distinct_uf)}
            continue

        refit = [refit_member(m, _subset(X1ai, avail_all, m.feature_subset), y1,
                              feature_names=list(m.feature_subset), seed=SEED) for m in distinct_uf]
        used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct_uf)]
        n_used_sets = len({u for u in used_sets if u})
        ext_per_member = [sorted(u & set(avail_ext)) for u in used_sets]
        n_members_using_ext = sum(1 for u in ext_per_member if u)
        ext_used_union = sorted(set().union(*[set(u) for u in ext_per_member]) if ext_per_member else set())

        v1_scores = [mdl.predict_proba(_subset(X1ai, avail_all, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct_uf)]
        v2_scores = [mdl.predict_proba(_subset(X2ai, avail_all, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct_uf)]
        med_rho, min_rho = pairwise_ranking_spearman(v1_scores)
        is_plural = (len(distinct_uf) >= 3) and (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)
        if is_plural:
            plural_grades.append(g)

        M1, M2 = np.vstack(v1_scores), np.vstack(v2_scores)
        d1, d2 = per_borrower_disagreement(M1), per_borrower_disagreement(M2)
        p1, p2 = consensus_scores(M1), consensus_scores(M2)
        tree_named = DecisionTreeRegressor(max_depth=EX_MAX_DEPTH, min_samples_leaf=EX_LEAF_MIN,
                                           random_state=SEED).fit(X1ni, d1)
        dhat1, dhat2 = tree_named.predict(X1ni), tree_named.predict(X2ni)
        r1, r2 = d1 - dhat1, d2 - dhat2

        ex_named = disagreement_explainer(d1, X1ni, avail_named, max_depth=EX_MAX_DEPTH,
                                          min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=SEED)
        ex_all = disagreement_explainer(d1, X1ai, avail_all, max_depth=EX_MAX_DEPTH,
                                        min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=SEED)
        r2_named, r2_all = ex_named.get("cv_r2"), ex_all.get("cv_r2")

        def _bucket_vars(d, dhat, r):
            return {"residual_r": np.asarray(r, float), "raw_d_ext": np.asarray(d, float),
                    "explained_d_hat_named": np.asarray(dhat, float)}
        _BUCKET_SEED_OFFSET = {"residual_r": 1, "raw_d_ext": 2, "explained_d_hat_named": 3}
        arms = {}
        for arm, (M, y, p, Xref, Xeval, bv, base_seed) in {
            "v2_forward": (M2, y2, p2, X1ai, X2ai, _bucket_vars(d2, dhat2, r2), 10_000 + gi * 31),
            "v1_insample": (M1, y1, p1, X1ai, X1ai, _bucket_vars(d1, dhat1, r1), 50_000 + gi * 31),
        }.items():
            arm_rec = {}
            for k, var in bv.items():
                arm_rec[k] = _bucketing_arm(M, y, p, Xref, Xeval, var,
                                            rng_seed=base_seed + 100 * _BUCKET_SEED_OFFSET[k])
            # within-top-d_ext-tercile contrast (uses this arm's d_ext and r)
            arm_rec["within_top_d_ext_tercile_contrast"] = _within_top_tercile_contrast(
                M, y, p, bv["raw_d_ext"], bv["residual_r"])
            # bucketing-variable agreement (how different are the three terciles?)
            tr, td, th = (tercile_labels(bv["residual_r"]), tercile_labels(bv["raw_d_ext"]),
                          tercile_labels(bv["explained_d_hat_named"]))
            def _sp(a, b):
                if np.std(a) == 0 or np.std(b) == 0:
                    return None
                rho = spearmanr(a, b).correlation
                return None if np.isnan(rho) else round(float(rho), 4)
            arm_rec["bucketing_agreement"] = {
                "spearman_r_terciles_vs_d_ext_terciles": _sp(tr, td),
                "spearman_d_hat_terciles_vs_d_ext_terciles": _sp(th, td),
                "spearman_r_vs_d_ext_continuous": _sp(bv["residual_r"], bv["raw_d_ext"]),
                "spearman_d_hat_vs_d_ext_continuous": _sp(bv["explained_d_hat_named"], bv["raw_d_ext"]),
            }
            arms[arm] = arm_rec

        results["grades"][g] = {
            "n_v1": int(y1.size), "n_v2": int(y2.size),
            "default_rate_v1": round(float(y1.mean()), 4), "default_rate_v2": round(float(y2.mean()), 4),
            "band_members_within_eps": len(band.members),
            "band_distinct_by_tree_signature": len(band.distinct_members),
            "n_distinct_uf_members": len(distinct_uf), "n_distinct_used_feature_sets": n_used_sets,
            "distinct_used_feature_sets": [sorted(u) for u in sorted({u for u in used_sets if u},
                                                                     key=lambda x: (len(x), sorted(x)))],
            "uses_extension": bool(n_members_using_ext > 0),
            "n_distinct_members_using_extension": n_members_using_ext, "extension_features_used_union": ext_used_union,
            "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
            "median_pairwise_spearman_v1": round(med_rho, 4), "min_pairwise_spearman_v1": round(min_rho, 4),
            "plural": bool(is_plural), "in_subprime_set": g in SUBPRIME,
            "d_ext_summary_v1": {"min": round(float(d1.min()), 6), "median": round(float(np.median(d1)), 6),
                                 "max": round(float(d1.max()), 6), "std": round(float(d1.std()), 6)},
            "r_summary_v1": {"min": round(float(r1.min()), 6), "median": round(float(np.median(r1)), 6),
                             "max": round(float(r1.max()), 6), "std": round(float(r1.std()), 6)},
            "explainer_named_cv_r2": r2_named, "explainer_named_plus_extension_cv_r2": r2_all,
            "explainer_named_root_feature": ex_named.get("root_feature"),
            "explainer_named_top_importances": ex_named.get("top_importances"),
            "well_explained_by_named": bool((r2_named is not None and r2_named >= R2_GOOD)),
            "arms": arms,
        }
        rr2 = arms["v2_forward"]
        ct = rr2["within_top_d_ext_tercile_contrast"]
        cb = (ct.get("policy_blind_half") or {}).get("consensus_brier")
        cn = (ct.get("named_explained_half") or {}).get("consensus_brier")
        print(f"  {g}: n_v1/v2={y1.size}/{y2.size} band={len(band.members)}->sig{len(band.distinct_members)}->uf{len(distinct_uf)} "
              f"plural={is_plural}(med_rho={med_rho:.3f}) ext_used={ext_used_union} | R2_named={r2_named} R2_all={r2_all} | "
              f"V2 routing booleans: "
              f"r=[m3={rr2['residual_r']['routing_relevant']['m3_brier_routing']},m4={rr2['residual_r']['routing_relevant']['m4_operational_lift_nonneg']}] "
              f"d_ext=[m3={rr2['raw_d_ext']['routing_relevant']['m3_brier_routing']},m4={rr2['raw_d_ext']['routing_relevant']['m4_operational_lift_nonneg']}] "
              f"d_hat=[m3={rr2['explained_d_hat_named']['routing_relevant']['m3_brier_routing']}] | "
              f"top-tercile Brier blind/named={cb}/{cn} -> blind_worse={ct.get('routing_relevant_blind_worse_than_named')}", flush=True)

    # ---------------- Aggregate verdict over the plural subprime grades ----------------
    P = [g for g in plural_grades if g in SUBPRIME]
    prime_flagged = [g for g in flagged if g not in SUBPRIME and isinstance(results["grades"].get(g), dict)
                     and results["grades"][g].get("verdict") != "SKIP"]
    n = len(P)
    maj = n / 2
    arm = "v2_forward"
    # P5: R2_named_ext < 0.3 on the subprime tiers (the quality split survives the used-feature-set de-dup)
    p5_lt = [g for g in P if isinstance(results["grades"][g].get("explainer_named_cv_r2"), (int, float))
             and results["grades"][g]["explainer_named_cv_r2"] < R2_GOOD]
    p5_assessable = [g for g in P if isinstance(results["grades"][g].get("explainer_named_cv_r2"), (int, float))]
    p5_hit = bool(len(p5_lt) > len(p5_assessable) / 2) if p5_assessable else None
    prime_well = {g: results["grades"][g].get("well_explained_by_named") for g in prime_flagged}
    # P1a: r-bucketing m3 AND m4 routing-relevant on > maj of P
    m3_r = _tally(results["grades"], P, arm, "residual_r", "m3_brier_routing")
    m4_r = _tally(results["grades"], P, arm, "residual_r", "m4_operational_lift_nonneg")
    p1a_hit = bool(m3_r[0] > maj and m4_r[0] > maj) if n else None
    # P1b: consensus worse on the policy-blind half on > maj of P
    blind_worse = 0
    for g in P:
        v = (results["grades"][g]["arms"][arm]["within_top_d_ext_tercile_contrast"]
             .get("routing_relevant_blind_worse_than_named"))
        if v is True:
            blind_worse += 1
    p1b_hit = bool(blind_worse > maj) if n else None
    p1_hit = bool(p1a_hit) and bool(p1b_hit) if (p1a_hit is not None and p1b_hit is not None) else None
    # P2: explained-d_hat bucketing does NOT m3-route on > maj of P
    m3_dhat = _tally(results["grades"], P, arm, "explained_d_hat_named", "m3_brier_routing")
    p2_hit = bool(not (m3_dhat[0] > maj)) if n else None
    # P4: r-bucketing #6-style 123-yes count >= raw-d_ext #6-style 123-yes count, on the aggregate
    hash123_r = _hash123_yes(results["grades"], P, arm, "residual_r")
    hash123_d = _hash123_yes(results["grades"], P, arm, "raw_d_ext")
    p4_hit = bool(hash123_r >= hash123_d) if n else None

    results["plural_grades"] = plural_grades
    results["primary_aggregate_plural_subprime"] = P
    results["verdict"] = {
        "arm": arm, "n_plural_subprime": n,
        "P5_dedup_robustness_quality_split_survives": {
            "subprime_R2_named_ext_lt_0.3_grades": p5_lt, "subprime_assessable": p5_assessable,
            "per_grade_R2_named_ext": {g: results["grades"][g].get("explainer_named_cv_r2") for g in P},
            "prime_grades_well_explained_by_named": prime_well, "hit": p5_hit},
        "P1a_policy_blind_disagreement_routes_r_terciles": {
            "m3_brier_routing_yes_no": m3_r, "m4_lift_nonneg_yes_no": m4_r, "hit": p1a_hit},
        "P1b_high_disagreement_routes_only_when_policy_blind": {
            "n_grades_blind_half_worse_than_named_half": blind_worse, "n": n, "hit": p1b_hit},
        "P1_headline_routable_population_exists": {"hit": p1_hit, "note": "P1a AND P1b"},
        "P2_explained_part_deflates_control": {"m3_brier_routing_yes_no_on_d_hat": m3_dhat, "hit": p2_hit},
        "P4_residual_at_least_as_clean_as_raw": {
            "hash123_yes_residual_r": hash123_r, "hash123_yes_raw_d_ext": hash123_d, "hit": p4_hit},
        "comparable_to_six_routing_test": {
            "hash123_yes_counts_v2": {b: _hash123_yes(results["grades"], P, arm, b) for b in BUCKETINGS},
            "note": "the #6 named-only-band routing test deflated: m1/m2/m3 routing on <=2/1/2 of 5 plural grades"},
    }

    p1 = p1_hit
    if p1 is True:
        verdict_phrase = ("ROUTABLE POPULATION EXISTS on the subprime tiers -- the policy-blind part of the "
                          "within-Rashomon disagreement localizes the borrowers on which the band consensus is "
                          "least reliable forward; per-case disagreement-routing is partially un-deflated on a "
                          "'the documented policy is silent about the contested feature' (fair-lending-adjacent) "
                          "footing")
    elif p1 is False:
        if p1a_hit is False and (p1b_hit is False):
            verdict_phrase = ("NO ROUTABLE POPULATION -- per-case disagreement-routing is dead even with the wider "
                              "feature view and the policy-blind decomposition; the extension-admitted finding is "
                              "about observability (the policy's vocabulary is inadequate to the indeterminacy here), "
                              "not triage")
        else:
            verdict_phrase = ("PARTIAL / SPLIT -- one leg of P1 holds and the other does not; the routable population, "
                              "if any, is narrower than 'the subprime tiers' -- report the per-grade picture")
    else:
        verdict_phrase = "INCONCLUSIVE on the aggregate (degenerate inputs on too many of the plural subprime grades)"
    if p2_hit is False:
        verdict_phrase += " [CAVEAT: the explained-part control did NOT deflate -- the residual decomposition may be confounded; see P2]"

    summary = (
        f"Routable-population test, Burst D ({V1}->{V2}), plural subprime grades P={P} (n={n}; "
        f"flagged={flagged}, all-plural={plural_grades}): "
        f"P5 (quality split survives used-feature-set de-dup) {'HIT' if p5_hit else ('MISS' if p5_hit is False else 'N/A')} "
        f"(subprime R2_named<0.3 on {len(p5_lt)}/{len(p5_assessable)}; prime well-explained: {prime_well}); "
        f"P1a (r-terciles route: m3 AND m4 on >maj) {'HIT' if p1a_hit else ('MISS' if p1a_hit is False else 'N/A')} "
        f"(m3 yes/no={m3_r}, m4 yes/no={m4_r}); "
        f"P1b (consensus worse on policy-blind half on >maj) {'HIT' if p1b_hit else ('MISS' if p1b_hit is False else 'N/A')} "
        f"({blind_worse}/{n}); P1 headline = {'HIT' if p1_hit else ('MISS' if p1_hit is False else 'N/A')}; "
        f"P2 (explained part deflates) {'HIT' if p2_hit else ('MISS' if p2_hit is False else 'N/A')} (m3 on d_hat yes/no={m3_dhat}); "
        f"P4 (residual >= raw) {'HIT' if p4_hit else ('MISS' if p4_hit is False else 'N/A')} "
        f"(123-yes r={hash123_r} vs d_ext={hash123_d}). VERDICT: {verdict_phrase}."
    )
    results["summary"] = summary
    print(f"\n{'#'*84}\n{summary}\n{'#'*84}", flush=True)

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
