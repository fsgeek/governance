"""Does a medium-fidelity codified mortgage policy still leave a vocabulary gap? (#11)

Pre-registration: docs/superpowers/specs/2026-05-12-fm-rich-policy-vocab-adequacy-preregistration-note.md.

Swaps the LC thin demo (3-4 named features) for a medium-fidelity codified FNMA
policy (~13 named Selling-Guide features; policy/fnma_eligibility_matrix.yaml) on
Fannie Mae Single-Family Loan Performance, and re-asks the extension-admitted /
routable-population question: within each pricing stratum cell, is the
per-borrower disagreement d(x) among the policy-constrained refinement band's
members a legible function of the *named* policy features, or does it collapse off
the policy vocabulary onto the available un-named features (geography / lender /
loan size)? -- and if a gap remains, is it rung-3a (codification-fixable: a
credit-risk feature the public file merely lacks) or rung-3b (codification-
irreducible: property a policy shouldn't/can't name)?

One vintage per invocation (`--vintage YYYYQN`); run 2018Q1 -> 2016Q1 -> 2008Q1
STRICTLY SERIAL (FM-load discipline: ~12 min / ~30 GB RSS each, never two in
parallel). Writes runs/fm_rich_policy_vocab_adequacy_{vintage}.json. The
cross-vintage replication verdict (P1-P7) is assembled in the result note from
the three per-vintage files.

Reuses wedge/refinement_set.py + wedge/routing.py wholesale. The one wedge/
change is the additive `max_subset_size` knob on build_refinement_band (a compute
control; lossless at `>= 2**max(depths)-1 == 7` -- a depth-<=3 CART splits on <=7
distinct features, and all <=7-subsets are enumerated, so band membership is
bit-for-bit identical). The collector extension (wedge/collectors/fanniemae.py)
exposes the named-policy + extension features.

Usage:
    PYTHONPATH=. python scripts/fm_rich_policy_vocab_adequacy_test.py --vintage 2018Q1
    PYTHONPATH=. python scripts/fm_rich_policy_vocab_adequacy_test.py --vintage 2018Q1 --probe   # timing probe, one S-rate cell
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from policy.encoder import load_policy
from wedge.collectors.fanniemae import (
    bucket_high_cardinality,
    derive_origination_and_label,
    filter_eligible,
    read_raw,
    to_feature_frame,
)
from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)
from wedge.routing import (
    consensus_scores,
    disagreement_explainer,
    partial_dependence_profile,
    per_borrower_disagreement,
    univariate_disagreement_correlations,
)

FM_DATA_DIR = Path("data/fanniemae")
POLICY_PATH = "policy/fnma_eligibility_matrix.yaml"

# Candidate named-policy features (the YAML's mandatory_features), in collector
# wedge-feature names. occupancy_status is dropped post-load (regime-filtered ->
# ~constant) and amortization_type is dropped if it has no spread (2018Q1 ~FRM).
NAMED_CANDIDATE = [
    "fico_range_low", "dti", "ltv", "cltv", "mortgage_insurance_pct",
    "loan_term_months", "loan_purpose", "num_units", "num_borrowers",
    "first_time_homebuyer", "property_type", "amortization_type", "occupancy_status",
]
# Extension features for the gap measurement (pre-reg §1b): property_state /
# original_upb / seller_name / servicer_name. orig_interest_rate is EXCLUDED (it
# defines the S-rate stratum). msa is collected by the loader but NOT used as a
# measured candidate -- it is a near-duplicate geography proxy of property_state
# and §1b does not list it; it appears only in variant B's prohibited set for
# documentation fidelity (a no-op there since it is never a candidate).
EXTENSION_CANDIDATE = ["property_state", "original_upb", "seller_name", "servicer_name"]
# Extension features the *compliant* policy graph (variant B) prohibits (pre-reg §2).
GEOGRAPHY_LENDER_PROHIBITED = ["property_state", "msa", "seller_name", "servicer_name"]
HIGH_CARDINALITY = ["seller_name", "servicer_name"]
CATEGORICAL = ["loan_purpose", "property_type", "first_time_homebuyer", "amortization_type",
               "occupancy_status", "property_state", "seller_name", "servicer_name"]

# Regime envelope (the Eligibility-Matrix gates; UPB / conforming-limit is
# auto-satisfied -- FM only acquires conforming loans).
FICO_FLOOR, DTI_CEIL, LTV_CEIL = 620.0, 50.0, 97.0

# Band construction (frozen in the pre-reg).
EPSILON, DEPTHS, LEAF_MINS, SEED = 0.02, (1, 2, 3), (25, 50, 100), 0
HOLDOUT_FRAC = 0.3
PLURALITY_RHO_MAX = 0.9
EPS_ARM = (0.01, 0.02, 0.05)

# Explainer (depth-<=3 CART; comparable to geometry / extension-admitted tests).
EX_MAX_DEPTH, EX_LEAF_MIN, EX_FOLDS = 3, 50, 5
R2_GOOD, DR2_EXT_MIN = 0.30, 0.15

# Placebo.
N_RANDOM_DRAWS = 5
SELLER_SERVICER_TOPK = 20
MSA_TOPK = 40

MIN_CELL_LOANS = 5000


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


# ---------------------------------------------------------------------------
# Load + prep
# ---------------------------------------------------------------------------
def load_vintage(vintage: str, *, nrows: int | None) -> pd.DataFrame:
    fm_csv = FM_DATA_DIR / f"{vintage}.csv"
    if not fm_csv.exists():
        raise FileNotFoundError(
            f"{fm_csv} not found -- extract first: "
            f"unzip {FM_DATA_DIR}/Performance_All.zip {vintage}.csv -d {FM_DATA_DIR}/")
    print(f"[{_now_iso()}] loading FM {vintage} from {fm_csv} (~12 min, large perf file)...", flush=True)
    t0 = time.time()
    raw = read_raw(fm_csv, nrows=nrows)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible).copy()
    print(f"[{_now_iso()}] loaded+collapsed in {time.time()-t0:.0f}s; eligible owner-occ purchase/refi rows: {len(feats)}", flush=True)
    return feats


def prep(feats: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply the regime filter, drop NaN keys, fill MI%->0, bucket high-card
    categoricals, integer-encode all categoricals (stable codes over the whole
    vintage). Returns (df, metadata)."""
    meta: dict = {}
    n0 = len(feats)
    df = feats.dropna(subset=["fico_range_low", "dti", "ltv", "orig_interest_rate", "label"]).copy()
    meta["n_after_dropna_keys"] = len(df)
    # UPB / conforming-limit: report, do not filter (FM acquisitions are conforming).
    if "original_upb" in df.columns:
        upb = pd.to_numeric(df["original_upb"], errors="coerce")
        meta["upb_pctiles"] = {p: round(float(np.nanpercentile(upb, p)), 0) for p in (50, 90, 99, 100)}
        meta["frac_upb_over_453100"] = round(float((upb > 453100).mean()), 4)
    # Regime envelope: FICO>=620, DTI<=50, LTV<=97.
    env = (df["fico_range_low"] >= FICO_FLOOR) & (df["dti"] <= DTI_CEIL) & (df["ltv"] <= LTV_CEIL)
    df = df[env].reset_index(drop=True)
    meta["n_in_regime_envelope"] = len(df)
    meta["frac_dropped_by_envelope"] = round(1 - len(df) / max(n0, 1), 4)
    meta["default_rate"] = round(float((df["label"] == 0).mean()), 5)
    # MI%: empty (LTV<=80 / no MI) -> 0 (semantically "no MI"), not median-imputed.
    if "mortgage_insurance_pct" in df.columns:
        df["mortgage_insurance_pct"] = pd.to_numeric(df["mortgage_insurance_pct"], errors="coerce").fillna(0.0)
    # Bucket high-cardinality categoricals.
    bucket_maps: dict[str, list[str]] = {}
    for c in HIGH_CARDINALITY:
        if c in df.columns:
            tk = MSA_TOPK if c == "msa" else SELLER_SERVICER_TOPK
            before = df[c].copy()
            df[c] = bucket_high_cardinality(before.astype("string"), top_k=tk)
            bucket_maps[c] = sorted(set(df[c].dropna().unique()))
    meta["high_cardinality_kept_buckets"] = {k: v for k, v in bucket_maps.items()}
    # Integer-encode categoricals (stable codes; missing -> -1).
    code_maps: dict[str, dict] = {}
    for c in CATEGORICAL:
        if c in df.columns:
            cat = pd.Categorical(df[c].astype("string"))
            code_maps[c] = {str(v): int(i) for i, v in enumerate(cat.categories)}
            codes = cat.codes.astype(float)
            codes[codes < 0] = -1.0
            df[c] = codes
    meta["categorical_code_maps"] = code_maps
    # Numeric features: report spread; flag near-constant for dropping.
    near_constant = []
    for c in ["loan_term_months", "num_units", "num_borrowers", "cltv", "mortgage_insurance_pct",
              "original_upb", "amortization_type", "occupancy_status"]:
        if c in df.columns:
            nun = int(pd.Series(df[c]).nunique(dropna=True))
            if nun <= 1:
                near_constant.append(c)
    meta["near_constant_dropped"] = near_constant
    return df, meta


def usable_features(df: pd.DataFrame, drop: list[str]) -> tuple[list[str], list[str]]:
    named = [f for f in NAMED_CANDIDATE if f in df.columns and f not in drop
             and pd.Series(df[f]).nunique(dropna=True) > 1]
    ext = [f for f in EXTENSION_CANDIDATE if f in df.columns and f not in drop
           and pd.Series(df[f]).nunique(dropna=True) > 1]
    return named, ext


# ---------------------------------------------------------------------------
# Strata
# ---------------------------------------------------------------------------
def rate_band_labels(rate: pd.Series, n_bands: int) -> pd.Series:
    try:
        codes = pd.qcut(rate, q=n_bands, labels=False, duplicates="drop")
    except ValueError:
        codes = pd.Series(np.zeros(len(rate), dtype=int), index=rate.index)
    return codes.map(lambda c: f"rb{int(c):02d}" if pd.notna(c) else None)


_FICO_BUCKETS = [(-np.inf, 660), (660, 680), (680, 700), (700, 720), (720, 740), (740, 760), (760, 780), (780, np.inf)]
_LTV_BUCKETS = [(-np.inf, 60), (60, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, 95), (95, np.inf)]


def _bucket_idx(v: float, buckets: list[tuple[float, float]]) -> int:
    for i, (lo, hi) in enumerate(buckets):
        if lo < v <= hi or (i == 0 and v <= hi):
            return i
    return len(buckets) - 1


def llpa_cell_labels(fico: pd.Series, ltv: pd.Series) -> pd.Series:
    fi = fico.map(lambda v: _bucket_idx(float(v), _FICO_BUCKETS))
    li = ltv.map(lambda v: _bucket_idx(float(v), _LTV_BUCKETS))
    return (fi.astype(str).str.zfill(1) + "x" + li.astype(str).str.zfill(1)).map(lambda s: f"llpa_{s}")


# ---------------------------------------------------------------------------
# One cell x one variant: build band, geometry
# ---------------------------------------------------------------------------
def _used_set_from_signature(member) -> frozenset:
    subset, nodes = member.tree_signature
    return frozenset(subset[i] for (i, _thr) in nodes)


def _dedup_by_used_feature_set(members: list) -> list:
    best: dict = {}
    for m in members:
        u = _used_set_from_signature(m)
        cur = best.get(u)
        if cur is None or m.holdout_auc > cur.holdout_auc:
            best[u] = m
    return list(best.values())


def _subset_cols(X: np.ndarray, names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    idx = {f: i for i, f in enumerate(names)}
    return X[:, [idx[f] for f in subset]]


def _impute_numeric(Xdf: pd.DataFrame, numeric_cols: list[str]) -> np.ndarray:
    """Median-impute the numeric columns; categorical (already int-coded, -1 for
    missing) pass through unchanged."""
    X = Xdf.to_numpy(dtype=float)
    if numeric_cols:
        ncols = [Xdf.columns.get_loc(c) for c in numeric_cols if c in Xdf.columns]
        if ncols:
            imp = SimpleImputer(strategy="median")
            X[:, ncols] = imp.fit_transform(X[:, ncols])
    return X


def build_band_for_cell(cell: pd.DataFrame, named: list[str], ext: list[str],
                        mono_default: dict[str, int], *, epsilon: float,
                        max_subset_size: int | None) -> dict:
    """Build the within-eps refinement band over `named + ext`, de-dup by
    used-feature-set, refit members, compute d / consensus, run the named-only
    and named+ext disagreement explainers. Returns a dict (or {'verdict':'SKIP'})."""
    cand = named + ext
    numeric_named = [f for f in named if f not in CATEGORICAL]
    Xdf = cell[cand]
    X_all = _impute_numeric(Xdf, [f for f in cand if f not in CATEGORICAL])
    X_named = _impute_numeric(cell[named], numeric_named) if named else np.zeros((len(cell), 0))
    y = (cell["label"].to_numpy() == 0).astype(int)  # 1 == default
    if y.size < 50 or y.min() == y.max():
        return {"verdict": "SKIP", "reason": f"degenerate labels (n={y.size}, defaults={int(y.sum())})"}

    band = build_refinement_band(X_all, y, feature_names=cand, monotonic_cst_map=mono_default,
                                 epsilon=epsilon, depths=DEPTHS, leaf_mins=LEAF_MINS,
                                 holdout_frac=HOLDOUT_FRAC, seed=SEED, max_subset_size=max_subset_size)
    if len(band.members) < 2:
        return {"verdict": "SKIP", "reason": "band <2 members within eps",
                "band_members_within_eps": len(band.members), "n_combos_tried": band.n_combos_tried}
    distinct = _dedup_by_used_feature_set(band.members)
    if len(distinct) < 2:
        return {"verdict": "SKIP", "reason": "band <2 distinct-by-used-feature-set members",
                "n_distinct_uf": len(distinct), "band_members_within_eps": len(band.members)}

    refit = [refit_member(m, _subset_cols(X_all, cand, m.feature_subset), y,
                          feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
    used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
    distinct_used_sets = [u for u in used_sets if u]
    n_used_sets = len(set(distinct_used_sets))
    scores = [mdl.predict_proba(_subset_cols(X_all, cand, m.feature_subset))[:, 1]
              for mdl, m in zip(refit, distinct)]
    med_rho, min_rho = pairwise_ranking_spearman(scores)
    is_plural = (len(distinct) >= 3) and (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)

    M = np.vstack(scores)
    d = per_borrower_disagreement(M)
    p_bar = consensus_scores(M)

    ex_named = (disagreement_explainer(d, X_named, named, max_depth=EX_MAX_DEPTH, min_samples_leaf=EX_LEAF_MIN,
                                       n_splits=EX_FOLDS, seed=SEED) if named else {"cv_r2": None})
    ex_all = disagreement_explainer(d, X_all, cand, max_depth=EX_MAX_DEPTH, min_samples_leaf=EX_LEAF_MIN,
                                    n_splits=EX_FOLDS, seed=SEED)
    r2_named, r2_all = ex_named.get("cv_r2"), ex_all.get("cv_r2")
    dr2_ext = None if (r2_named is None or r2_all is None) else round(r2_all - r2_named, 4)

    # Which extension features carry the explainer importance?
    ext_set = set(ext)
    ext_importances = [(nm, im) for nm, im in (ex_all.get("top_importances") or []) if nm in ext_set]
    # rung-3a/3b: 3b iff dominant ext contributors are geography/lender/loan-size.
    rung = None
    if (r2_named is not None and r2_named < R2_GOOD) and (dr2_ext is not None and dr2_ext >= DR2_EXT_MIN):
        carriers = [nm for nm, _ in ext_importances]
        geo_lender = {"property_state", "msa", "seller_name", "servicer_name"}
        if not carriers:
            rung = "3?-gap-but-no-ext-carrier-in-top3"
        elif all(c in geo_lender for c in carriers):
            rung = "3b-codification-irreducible"
        elif "original_upb" in carriers and all(c in (geo_lender | {"original_upb"}) for c in carriers):
            rung = "3a/3b-mixed-loan-size-and-geo" if any(c in geo_lender for c in carriers) else "3a-loan-size"
        else:
            rung = "mixed"
    # PD shape of d on the named-explainer root feature.
    pd_shape = None
    root = ex_named.get("root_feature")
    if root is not None and named and root in named:
        ridx = named.index(root)
        pd_shape = partial_dependence_profile(d, X_named[:, ridx]).get("shape")
    # univariate spearman(feature, d) for all candidates.
    uni = univariate_disagreement_correlations(d, X_all, cand)

    # Mandatory-feature enforcement readings (post-hoc; the geometry above is on
    # the full de-duped band -- consistent with #6 / extension-admitted / routable).
    mand_exposed = named  # all exposed mandatory features (occupancy/amort dropped if constant)
    usage_share = {f: round(sum(1 for u in used_sets if f in u) / len(used_sets), 3) for f in mand_exposed}
    union_used = set().union(*[set(u) for u in used_sets]) if used_sets else set()
    r_member_band = [m for m, u in zip(distinct, used_sets) if set(mand_exposed) <= u]
    enforcement = {
        "R_member_n_qualifying": len(r_member_band),
        "R_any_union_covers_mandatory": bool(set(mand_exposed) <= union_used),
        "R_any_missing_from_union": sorted(set(mand_exposed) - union_used),
        "R_majority_all_mandatory_used_by_ge_half_members": bool(mand_exposed and all(v >= 0.5 for v in usage_share.values())),
        "mandatory_feature_usage_share": usage_share,
        "interpretation": ("R-majority = each exposed mandatory feature used by >=50% of distinct band members; "
                           "geometry reported on the full de-duped within-eps band (the construction)"),
    }

    return {
        "verdict": "ANALYZED",
        "n": int(y.size), "n_default": int(y.sum()), "default_rate": round(float(y.mean()), 5),
        "candidate_named": named, "candidate_extension": ext,
        "band_members_within_eps": len(band.members),
        "band_distinct_by_tree_signature": len(band.distinct_members),
        "n_distinct_uf_members": len(distinct), "n_distinct_used_feature_sets": n_used_sets,
        "distinct_used_feature_sets": [sorted(u) for u in sorted({u for u in distinct_used_sets},
                                                                 key=lambda x: (len(x), sorted(x)))],
        "n_members_using_extension": sum(1 for u in used_sets if u & ext_set),
        "extension_features_used_union": sorted(union_used & ext_set),
        "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
        "median_pairwise_spearman": round(med_rho, 4), "min_pairwise_spearman": round(min_rho, 4),
        "plural": bool(is_plural),
        "d_summary": {"min": round(float(d.min()), 6), "median": round(float(np.median(d)), 6),
                      "max": round(float(d.max()), 6), "std": round(float(d.std()), 6)},
        "R2_named": r2_named, "R2_all": r2_all, "dR2_ext": dr2_ext,
        "explainer_named_root_feature": root, "explainer_named_top_importances": ex_named.get("top_importances"),
        "explainer_all_root_feature": ex_all.get("root_feature"), "explainer_all_top_importances": ex_all.get("top_importances"),
        "extension_importances_in_all_explainer": [(nm, round(im, 4)) for nm, im in ext_importances],
        "rung_classification": rung, "pd_shape_d_on_named_root": pd_shape,
        "well_explained_by_named": bool(r2_named is not None and r2_named >= R2_GOOD),
        "gap_recurs": bool((r2_named is not None and r2_named < R2_GOOD) and (dr2_ext is not None and dr2_ext >= DR2_EXT_MIN)),
        "univariate_spearman_d": uni,
        "mandatory_feature_enforcement": enforcement,
        "n_combos_tried": band.n_combos_tried,
    }


def placebo_for_cell(cell: pd.DataFrame, named: list[str], ext: list[str], *,
                     max_subset_size: int | None, rng_seed: int) -> dict:
    """C-random: build an unconstrained (no monotonicity) band over named+ext ->
    d_rand; for N_RANDOM_DRAWS random |named|-subsets of the candidate, R2 of
    d_rand explained by that subset. C-scrambled: build a band over named+ext
    with the real numeric-named monotonicity REVERSED -> d_scram; R2 of d_scram
    explained by the named set, plus the scrambled band size (binding check)."""
    cand = named + ext
    X_all = _impute_numeric(cell[cand], [f for f in cand if f not in CATEGORICAL])
    y = (cell["label"].to_numpy() == 0).astype(int)
    if y.size < 50 or y.min() == y.max():
        return {"verdict": "SKIP"}
    out: dict = {}
    # C-random: unconstrained band.
    band_r = build_refinement_band(X_all, y, feature_names=cand, monotonic_cst_map={},
                                   epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS,
                                   holdout_frac=HOLDOUT_FRAC, seed=SEED, max_subset_size=max_subset_size)
    if len(band_r.members) >= 2:
        distinct_r = _dedup_by_used_feature_set(band_r.members)
        refit_r = [refit_member(m, _subset_cols(X_all, cand, m.feature_subset), y,
                                feature_names=list(m.feature_subset), seed=SEED) for m in distinct_r]
        Mr = np.vstack([mdl.predict_proba(_subset_cols(X_all, cand, m.feature_subset))[:, 1]
                        for mdl, m in zip(refit_r, distinct_r)])
        d_rand = per_borrower_disagreement(Mr)
        rng = np.random.default_rng(rng_seed)
        k = len(named)
        rand_r2 = []
        for _ in range(N_RANDOM_DRAWS):
            pick = sorted(rng.choice(len(cand), size=min(k, len(cand)), replace=False).tolist())
            sub_names = [cand[i] for i in pick]
            sub_X = _impute_numeric(cell[sub_names], [f for f in sub_names if f not in CATEGORICAL])
            ex = disagreement_explainer(d_rand, sub_X, sub_names, max_depth=EX_MAX_DEPTH,
                                        min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=SEED)
            rand_r2.append(ex.get("cv_r2"))
        vals = [v for v in rand_r2 if v is not None]
        out["C_random"] = {"d_rand_band_distinct_uf": len(distinct_r),
                           "R2_random_named_per_draw": rand_r2,
                           "R2_random_named_mean": round(float(np.mean(vals)), 4) if vals else None,
                           "R2_random_named_std": round(float(np.std(vals)), 4) if vals else None}
    else:
        out["C_random"] = {"verdict": "SKIP (unconstrained band <2 members)"}
    # C-scrambled: reversed monotonicity on the numeric named features.
    pc = load_policy(POLICY_PATH)
    # default-prediction convention is -grant-convention; scrambled = + grant-convention (i.e. flip sign vs the real default-conv).
    scrambled_mono = {f: pc.monotonicity_map[f] for f in named if f in pc.monotonicity_map}  # = grant-conv = -(default-conv); the "wrong" sign
    band_s = build_refinement_band(X_all, y, feature_names=cand, monotonic_cst_map=scrambled_mono,
                                   epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS,
                                   holdout_frac=HOLDOUT_FRAC, seed=SEED, max_subset_size=max_subset_size)
    if len(band_s.members) >= 2:
        distinct_s = _dedup_by_used_feature_set(band_s.members)
        if len(distinct_s) >= 2:
            refit_s = [refit_member(m, _subset_cols(X_all, cand, m.feature_subset), y,
                                    feature_names=list(m.feature_subset), seed=SEED) for m in distinct_s]
            Ms = np.vstack([mdl.predict_proba(_subset_cols(X_all, cand, m.feature_subset))[:, 1]
                            for mdl, m in zip(refit_s, distinct_s)])
            d_scram = per_borrower_disagreement(Ms)
            X_named = _impute_numeric(cell[named], [f for f in named if f not in CATEGORICAL])
            ex = disagreement_explainer(d_scram, X_named, named, max_depth=EX_MAX_DEPTH,
                                        min_samples_leaf=EX_LEAF_MIN, n_splits=EX_FOLDS, seed=SEED)
            out["C_scrambled"] = {"band_members_within_eps": len(band_s.members),
                                  "band_distinct_uf": len(distinct_s),
                                  "R2_scrambled_named": ex.get("cv_r2"),
                                  "scrambled_monotonicity_grant_conv": scrambled_mono}
        else:
            out["C_scrambled"] = {"band_members_within_eps": len(band_s.members), "band_distinct_uf": len(distinct_s),
                                  "note": "scrambled band <2 distinct-uf members (monotonicity binding)"}
    else:
        out["C_scrambled"] = {"band_members_within_eps": len(band_s.members),
                              "note": "scrambled band <2 members within eps (monotonicity binding)"}
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_stratum(df: pd.DataFrame, *, stratum: str, cell_col: str, named: list[str], ext: list[str],
                mono_default_A: dict[str, int], max_subset_size: int | None, min_cell_loans: int,
                do_placebo: bool, do_eps_arm: bool, probe: bool, only_cell: str | None = None) -> dict:
    cells = df[cell_col].value_counts().sort_index()
    analyzed = [c for c, n in cells.items() if n >= min_cell_loans]
    if only_cell is not None:
        if only_cell not in analyzed:
            raise ValueError(f"--only-cell {only_cell!r} not in analyzable cells for {stratum}: {analyzed}")
        analyzed = [only_cell]
    elif probe and analyzed:
        analyzed = [analyzed[len(analyzed) // 2]]  # one mid cell
    print(f"[{_now_iso()}] stratum {stratum}: {len(cells)} cells, {len(analyzed)} >= {min_cell_loans} loans"
          f"{' (PROBE: one cell)' if probe else ''}: {analyzed}", flush=True)
    pc = load_policy(POLICY_PATH)
    prohibited_B = set(GEOGRAPHY_LENDER_PROHIBITED)
    named_B = named  # the 4 ext are prohibited; named stays
    ext_B = [f for f in ext if f not in prohibited_B]  # original_upb may survive
    mono_default_B = {f: v for f, v in mono_default_A.items() if f in named_B}

    out: dict = {"stratum": stratum, "cell_col": cell_col, "cell_loan_counts": {str(k): int(v) for k, v in cells.items()},
                 "analyzed_cells": analyzed, "min_cell_loans": min_cell_loans, "cells": {}}
    plural_A: list[str] = []
    for ci, cell_id in enumerate(analyzed):
        cell = df[df[cell_col] == cell_id].reset_index(drop=True)
        t0 = time.time()
        recA = build_band_for_cell(cell, named, ext, mono_default_A, epsilon=EPSILON, max_subset_size=max_subset_size)
        recB = build_band_for_cell(cell, named_B, ext_B, mono_default_B, epsilon=EPSILON, max_subset_size=max_subset_size)
        cell_rec = {"n": int(len(cell)), "variant_A_geography_admissible": recA, "variant_B_compliant_geography_prohibited": recB,
                    "seconds": round(time.time() - t0, 1)}
        if recA.get("plural"):
            plural_A.append(cell_id)
        out["cells"][cell_id] = cell_rec
        a = recA
        msg = (f"  {cell_id}: n={len(cell)} A:[{a.get('verdict')}"
               + (f" plural={a.get('plural')} R2_named={a.get('R2_named')} R2_all={a.get('R2_all')} "
                  f"dR2_ext={a.get('dR2_ext')} rung={a.get('rung_classification')} uf={a.get('n_distinct_uf_members')}"
                  if a.get('verdict') == 'ANALYZED' else f" {a.get('reason','')}")
               + f"] B:[{recB.get('verdict')}"
               + (f" R2_named={recB.get('R2_named')} R2_all={recB.get('R2_all')}" if recB.get('verdict') == 'ANALYZED' else "")
               + f"] ({cell_rec['seconds']}s)")
        print(msg, flush=True)
    out["plural_cells_variant_A"] = plural_A

    # Placebo / scrambled-policy baselines: on the PLURAL variant-A cells only
    # (where R2_named carries a verdict; the pre-reg specifies per-analyzed-cell
    # but the controls only validate R2_named where there is a band to disagree).
    if do_placebo and not probe and plural_A:
        for pi, cell_id in enumerate(plural_A):
            cell = df[df[cell_col] == cell_id].reset_index(drop=True)
            t0 = time.time()
            out["cells"][cell_id]["placebo"] = placebo_for_cell(cell, named, ext,
                                                                max_subset_size=max_subset_size,
                                                                rng_seed=100_000 + pi * 31)
            pb = out["cells"][cell_id]["placebo"]
            print(f"  [placebo] {cell_id}: C-random R2_mean={pb.get('C_random', {}).get('R2_random_named_mean')} "
                  f"C-scrambled R2={pb.get('C_scrambled', {}).get('R2_scrambled_named')} "
                  f"scrambled_band_uf={pb.get('C_scrambled', {}).get('band_distinct_uf')} ({time.time()-t0:.0f}s)", flush=True)

    # eps arm: re-run construction at {0.01, 0.05} on the plural analyzed cells (variant A, primary).
    if do_eps_arm and not probe and plural_A:
        eps_out: dict = {}
        for cell_id in plural_A:
            cell = df[df[cell_col] == cell_id].reset_index(drop=True)
            per_eps = {}
            for eps in EPS_ARM:
                if eps == EPSILON and cell_id in out["cells"]:
                    rec = out["cells"][cell_id]["variant_A_geography_admissible"]
                else:
                    rec = build_band_for_cell(cell, named, ext, mono_default_A, epsilon=eps, max_subset_size=max_subset_size)
                per_eps[str(eps)] = {"verdict": rec.get("verdict"), "plural": rec.get("plural"),
                                     "R2_named": rec.get("R2_named"), "R2_all": rec.get("R2_all"),
                                     "dR2_ext": rec.get("dR2_ext"), "gap_recurs": rec.get("gap_recurs"),
                                     "n_distinct_uf": rec.get("n_distinct_uf_members")}
            gaps = {e: v.get("gap_recurs") for e, v in per_eps.items() if v.get("verdict") == "ANALYZED"}
            per_eps["verdict_stable_across_eps"] = (len(set(gaps.values())) <= 1) if gaps else None
            eps_out[cell_id] = per_eps
            print(f"  [eps-arm] {cell_id}: " + ", ".join(f"eps={e}:gap={v.get('gap_recurs')},R2n={v.get('R2_named')}"
                  for e, v in eps_out[cell_id].items() if isinstance(v, dict) and 'gap_recurs' in v), flush=True)
        out["eps_arm_on_plural_variant_A"] = eps_out
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="#11 FM rich-policy vocabulary-adequacy test (one vintage).")
    ap.add_argument("--vintage", default="2018Q1", help="FM acquisition quarter; reads data/fanniemae/{vintage}.csv")
    ap.add_argument("--n-rate-bands", type=int, default=10)
    ap.add_argument("--min-cell-loans", type=int, default=MIN_CELL_LOANS)
    ap.add_argument("--max-subset-size", type=int, default=7,
                    help="cap on feature-subset size in build_refinement_band; 7 is lossless for depth<=3")
    ap.add_argument("--strata", default="rate,llpa", help="comma list of {rate,llpa}")
    ap.add_argument("--no-placebo", action="store_true")
    ap.add_argument("--no-eps-arm", action="store_true")
    ap.add_argument("--probe", action="store_true", help="timing probe: one S-rate cell only, no placebo/eps-arm")
    ap.add_argument("--only-cell", default=None, help="restrict S-rate to one specific cell id (e.g. rb09); skip S-llpa")
    ap.add_argument("--nrows", type=int, default=None, help="cap on raw monthly rows read (testing/sampling)")
    ap.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = ap.parse_args()

    strata = [s.strip() for s in args.strata.split(",") if s.strip()]
    do_placebo = not args.no_placebo and not args.probe
    do_eps_arm = not args.no_eps_arm and not args.probe

    t_start = time.time()
    feats = load_vintage(args.vintage, nrows=args.nrows)
    df, prep_meta = prep(feats)
    drop = list(prep_meta.get("near_constant_dropped", [])) + ["occupancy_status"]
    named, ext = usable_features(df, drop)
    print(f"[{_now_iso()}] usable named ({len(named)}): {named}\n  usable extension ({len(ext)}): {ext}\n"
          f"  dropped: {sorted(set(drop))}\n  candidate set size {len(named)+len(ext)} -> "
          f"<= sum_C(n,1..{args.max_subset_size}) subsets x {len(DEPTHS)*len(LEAF_MINS)} hyper-cells per band", flush=True)
    pc = load_policy(POLICY_PATH)
    # Convert encoder's grant-convention monotonicity to default-prediction convention (negate), keep only exposed named.
    mono_default_A = {f: -v for f, v in pc.monotonicity_map.items() if f in named}
    print(f"  policy '{pc.name}' v{pc.version}: mandatory(exposed)={named}; mono(default-conv)={mono_default_A}", flush=True)

    # Strata labels.
    if "rate" in strata:
        df["s_rate"] = rate_band_labels(df["orig_interest_rate"], args.n_rate_bands)
    if "llpa" in strata:
        df["s_llpa"] = llpa_cell_labels(df["fico_range_low"], df["ltv"])

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-fm-rich-policy-vocab-adequacy-preregistration-note.md",
        "test": "fm-rich-policy-vocab-adequacy-#11", "substrate": f"FM-{args.vintage}",
        "run_at": _now_iso(), "policy": pc.name, "policy_version": pc.version, "policy_status": pc.status,
        "regime_envelope": {"fico_floor": FICO_FLOOR, "dti_ceiling": DTI_CEIL, "ltv_ceiling": LTV_CEIL,
                            "conforming_upb": "auto-satisfied (FM acquisitions are conforming)"},
        "prep": prep_meta, "named_features_exposed": named, "extension_features_exposed": ext,
        "dropped_features": sorted(set(drop)),
        "monotonic_cst_default_convention": mono_default_A,
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                        "seed": SEED, "holdout_frac": HOLDOUT_FRAC, "plurality_rho_max": PLURALITY_RHO_MAX,
                        "max_subset_size": args.max_subset_size, "dedup": "used-feature-set (highest-holdout-AUC representative)",
                        "candidate_set": "named-policy features UNION extension features (orig_interest_rate excluded -- defines the rate stratum)"},
        "explainer_params": {"max_depth": EX_MAX_DEPTH, "min_samples_leaf": EX_LEAF_MIN, "cv_folds": EX_FOLDS,
                             "r2_good": R2_GOOD, "dr2_ext_min": DR2_EXT_MIN},
        "placebo_params": {"n_random_draws": N_RANDOM_DRAWS, "seller_servicer_topk": SELLER_SERVICER_TOPK, "msa_topk": MSA_TOPK},
        "eps_arm": list(EPS_ARM), "min_cell_loans": args.min_cell_loans, "probe": bool(args.probe),
        "strata": {},
    }
    if "rate" in strata:
        results["strata"]["S_rate"] = run_stratum(df, stratum="S-rate (orig_interest_rate deciles)", cell_col="s_rate",
                                                  named=named, ext=ext, mono_default_A=mono_default_A,
                                                  max_subset_size=args.max_subset_size, min_cell_loans=args.min_cell_loans,
                                                  do_placebo=do_placebo, do_eps_arm=do_eps_arm, probe=args.probe,
                                                  only_cell=args.only_cell)
    if "llpa" in strata and not args.probe and args.only_cell is None:
        results["strata"]["S_llpa"] = run_stratum(df, stratum="S-llpa (FICO x LTV grid cells)", cell_col="s_llpa",
                                                  named=named, ext=ext, mono_default_A=mono_default_A,
                                                  max_subset_size=args.max_subset_size, min_cell_loans=args.min_cell_loans,
                                                  do_placebo=do_placebo, do_eps_arm=False, probe=False)
    results["total_seconds"] = round(time.time() - t_start, 1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.probe:
        suffix = "-probe"
    elif args.only_cell is not None:
        suffix = f"-{args.only_cell}-ms{args.max_subset_size}"
    else:
        suffix = ""
    out_path = args.output_dir / f"fm_rich_policy_vocab_adequacy_{args.vintage}{suffix}.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n[{_now_iso()}] wrote {out_path} ({results['total_seconds']}s total)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
