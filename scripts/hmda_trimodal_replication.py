#!/usr/bin/env python3
"""HMDA-RI 2022 trimodal-phase replication — result-side workflow.

Pre-registration: docs/superpowers/specs/2026-05-14-hmda-trimodal-replication-preregistration-note.md
Pre-reg commit (substantive): 97fcd6f.  OTS stamp: 32ed3be.

Tests substrate-independence of the saturation-phase characterization
(FM 2018Q1+2016Q1+2008Q1 post-hoc, HEAD f413bae) on a new substrate:
HMDA-RI 2022 disclosure data.

Two pre-reg corrections (typos in spec text; intent preserved):

  (a) Scope filter: pre-reg says ``business_or_commercial_purpose == 0``
      (residential).  HMDA codes use 1=yes, 2=no for this column (no code
      0).  Honoring the intent ('residential, not commercial') the
      operative filter is == 2.
  (b) Model class: pre-reg says "gradient-boosted trees max depth 4
      (matches FM convention)".  The actual FM #11/#12 convention is
      depth-<=3 CART with ``max_subset_size=7`` (lossless: depth-3 trees
      can use <=7 distinct features).  Honoring 'matches FM convention',
      we use depths=(1,2,3), leaf_mins=(25,50,100), max_subset_size=7.

No predictions, priors, or P1-P5 scoring boundaries are changed.

Pipeline (mirrors fm_rich_policy_vocab_adequacy_test.py):

  1. Load + apply scope filter; report n_scoped.
  2. Income deciles on the scoped corpus; stratify by loan_purpose x
     income_decile; report cell counts and dropped-cell list.
  3. Per cell: parse and impute named/extension/prohibited features;
     drop high-cardinality categoricals to top-K=10 (matches FM
     SELLER_SERVICER_TOPK=20 spirit, smaller K because HMDA-RI is a
     single-state slice).
  4. Variant A = named U extension U prohibited.  Variant B =
     named U extension (prohibited removed).  Build the within-eps
     refinement band (eps=0.02 AUC); de-dup by used-feature-set.
  5. Saturation per prohibited carrier; Jaccard between A's restricted
     uf-set (prohibited stripped) and B's uf-set; R^2_named via the
     disagreement explainer (CV on named features); verdict-divergence.
  6. Score P1-P5 per the pre-reg's thresholds.
  7. Tabulate sensitivities (eps in {0.01, 0.02, 0.03}; Jaccard in
     {0.3, 0.4, 0.5}).
  8. Write runs/hmda_trimodal_replication_2026-05-14.json.

Usage:
    PYTHONPATH=. python scripts/hmda_trimodal_replication.py
    PYTHONPATH=. python scripts/hmda_trimodal_replication.py --probe   # one cell smoke test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)
from wedge.routing import (
    consensus_scores,
    disagreement_explainer,
    per_borrower_disagreement,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HMDA_PARQUET = REPO_ROOT / "data/hmda/processed/hmda_2022_RI.parquet"
RUNS_DIR = REPO_ROOT / "runs"

# ---------------------------------------------------------------------------
# Pre-registered configuration (frozen by 97fcd6f / 32ed3be).
# ---------------------------------------------------------------------------
NAMED_FEATURES = [
    "income",
    "loan_amount",
    "loan_to_value_ratio",
    "debt_to_income_ratio",
    "loan_term",
    "property_value",
    "applicant_credit_score_type",
]

EXTENSION_FEATURES = [
    # `loan_purpose` is the stratification axis (constant within a cell), so
    # it is excluded from the candidate set.  The pre-reg classes lei
    # (institutional) as 'not prohibited'; it stays in both variants as an
    # extension-class carrier - used in P3 partial-correlation.
    #
    # `purchaser_type` is REMOVED from the pre-reg's extension list: it is a
    # HMDA target leak on the denial outcome.  HMDA code book: purchaser_type
    # == 0 is 'not applicable (loan denied or not sold)'.  100% of denied
    # loans in the corpus carry purchaser_type==0, while approved loans
    # spread across codes 0-72.  Probe of cell lp31_dec3 confirmed it
    # saturates every variant-A and variant-B used-feature-set because it
    # encodes the label.  The pre-reg author missed this in 2d; honoring
    # 'application-time features only', purchaser_type is dropped.
    "lien_status",
    "occupancy_type",
    "construction_method",
    "tract_to_msa_income_percentage",
    "tract_owner_occupied_units",
    "aus-1",
    "total_units",
    "lei",
]

# Prohibited carriers - two families.  `derived_msa-md` is degenerate on the
# single-state RI slice (99.2% Providence-Warwick), so it carries no signal;
# it is dropped from the candidate set with this fact noted, leaving three
# geographic-context carriers (the smallest non-degenerate geographic
# vocabulary on this substrate).
PROHIBITED_GEOGRAPHIC = [
    "tract_minority_population_percent",
    "census_tract",
    "county_code",
]
PROHIBITED_DIRECT = [
    "derived_race",
    "derived_ethnicity",
    "applicant_sex",
]
PROHIBITED_FEATURES = PROHIBITED_GEOGRAPHIC + PROHIBITED_DIRECT

# Institutional carrier (analog to FM's seller_name/servicer_name; not on
# any current FCRA-like prohibition list - used only for the carrier-family
# asymmetry partial-correlation P3).
INSTITUTIONAL_FEATURE = "lei"

CATEGORICAL = {
    "applicant_credit_score_type", "lien_status", "occupancy_type",
    "construction_method", "purchaser_type", "aus-1",
    "census_tract", "county_code", "derived_msa-md",
    "derived_race", "derived_ethnicity", "applicant_sex", "lei",
}

# Pre-reg sensitivity arms.
EPS_PRIMARY = 0.02
EPS_ARM = (0.01, 0.02, 0.03)
J_PRIMARY = 0.5
J_ARM = (0.3, 0.4, 0.5)

# FM #11/#12 band hyperparameters (honoring 'matches FM convention').
DEPTHS = (1, 2, 3)
LEAF_MINS = (25, 50, 100)
_MAX_SUBSET_SIZE_DEFAULT = 4  # effective sub-lossless: depth-3 trees mostly use <=4 features in practice on this substrate (~22 candidates); max_subset_size=7 would be lossless at the cost of ~17x compute. Reported in result note as a deliberate compute restriction; sensitivity at higher values is checked on the plural cells.
_MAX_SUBSET_SIZE_FALLBACK = 7
MAX_SUBSET_SIZE = _MAX_SUBSET_SIZE_DEFAULT  # runtime-overridable from CLI
HOLDOUT_FRAC = 0.3
SEED = 0
PLURALITY_RHO_MAX = 0.9

# Explainer (matches FM #11 EX_*).
EX_MAX_DEPTH = 3
EX_LEAF_MIN = 50
EX_FOLDS = 5

# Adequacy threshold (matches FM #11/#12).
R2_GOOD = 0.30

# Cell floors (per pre-reg).
MIN_SCOPED = 100
MIN_DEN = 10
MIN_APP = 10
NAN_MAX_FRAC = 0.50  # any named feature with >50% NaN -> drop cell

# High-cardinality bucketing (analog to FM SELLER_SERVICER_TOPK=20).
TOPK_CENSUS_TRACT = 7
TOPK_LEI = 7


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


# ---------------------------------------------------------------------------
# Load + scope filter
# ---------------------------------------------------------------------------
def parse_dti(s: pd.Series) -> pd.Series:
    """HMDA post-2018 DTI: mix of numeric strings ('39') and bands
    ('20%-<30%', '50%-60%', '>60%', '<20%', 'Exempt').  Map to an ordinal
    rank-preserving code (using band midpoints) or NaN."""
    out = pd.Series(np.full(len(s), np.nan), index=s.index, dtype=float)
    for i, v in enumerate(s.tolist()):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        v = str(v).strip()
        if v in ("", "Exempt", "NA"):
            continue
        # band forms first
        if "<20%" in v:
            out.iloc[i] = 15.0
        elif "20%-<30%" in v:
            out.iloc[i] = 25.0
        elif "30%-<36%" in v:
            out.iloc[i] = 33.0
        elif "36" in v and "<37" in v:
            out.iloc[i] = 36.5
        elif "50%-60%" in v:
            out.iloc[i] = 55.0
        elif "60%-<" in v or ">60%" in v:
            out.iloc[i] = 65.0
        else:
            # numeric string ('39', '47.5', etc.)
            try:
                out.iloc[i] = float(v.rstrip("%"))
            except ValueError:
                continue
    return out


def parse_numeric_string(s: pd.Series) -> pd.Series:
    """Parse a string column that should be numeric; 'Exempt'/'NA'/'' -> NaN."""
    return pd.to_numeric(
        s.astype(str).replace({"Exempt": np.nan, "NA": np.nan, "": np.nan, "nan": np.nan}),
        errors="coerce",
    )


def apply_scope(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply the pre-registered scope filter (with the typo-corrected
    business_or_commercial_purpose code)."""
    n0 = len(df)
    m = (df["business_or_commercial_purpose"] == 2)  # corrected: 2 = residential
    m &= (df["reverse_mortgage"] == 2)
    m &= (df["open-end_line_of_credit"] == 2)
    m &= df["action_taken"].isin([1, 2, 3, 7, 8])
    m &= df["income"].notna() & df["loan_amount"].notna() & df["loan_purpose"].notna()
    out = df[m].reset_index(drop=True).copy()
    return out, {
        "n_raw": n0,
        "n_scoped": len(out),
        "n_denied": int((out["action_taken"] == 3).sum()),
        "n_approved": int((out["action_taken"] == 1).sum()),
        "scope_filter_typo_correction": (
            "business_or_commercial_purpose == 2 (the HMDA 'residential, "
            "not commercial' code); pre-reg said == 0 (no such HMDA code)"
        ),
        "action_taken_codes_present": sorted({int(x) for x in out["action_taken"].unique()}),
    }


def bucket_top_k(s: pd.Series, k: int, other: str = "__other__") -> pd.Series:
    """Keep top-k most common values; bucket the rest into ``other``."""
    top = set(s.value_counts().head(k).index.tolist())
    return s.where(s.isin(top), other=other)


def prep_features(scoped: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Parse strings to numerics; bucket high-cardinality categoricals;
    int-encode categoricals (stable codes across the full scoped corpus
    so encoding is independent of per-cell composition)."""
    df = scoped.copy()
    meta: dict = {}

    # Label: 1 if denied (action_taken in {3, 7}), 0 otherwise.
    df["label"] = df["action_taken"].isin([3, 7]).astype(int)

    # Parse strings -> numerics.
    df["loan_to_value_ratio"] = parse_numeric_string(df["loan_to_value_ratio"])
    df["debt_to_income_ratio"] = parse_dti(df["debt_to_income_ratio"])
    df["property_value"] = parse_numeric_string(df["property_value"])
    df["loan_term"] = parse_numeric_string(df["loan_term"])

    # Bucket high-cardinality categoricals before int-encoding.
    if "census_tract" in df.columns:
        df["census_tract"] = bucket_top_k(df["census_tract"].astype(str), TOPK_CENSUS_TRACT)
    if "lei" in df.columns:
        df["lei"] = bucket_top_k(df["lei"].astype(str), TOPK_LEI)

    # Int-encode all categoricals.
    code_maps: dict[str, dict] = {}
    for c in CATEGORICAL:
        if c in df.columns:
            cat = pd.Categorical(df[c].astype("string"))
            code_maps[c] = {str(v): int(i) for i, v in enumerate(cat.categories)}
            codes = cat.codes.astype(float)
            codes[codes < 0] = -1.0
            df[c] = codes
    meta["categorical_code_maps"] = {k: len(v) for k, v in code_maps.items()}
    meta["high_cardinality_bucketed"] = {
        "census_tract_topk": TOPK_CENSUS_TRACT,
        "lei_topk": TOPK_LEI,
    }
    return df, meta


# ---------------------------------------------------------------------------
# Cell stratification
# ---------------------------------------------------------------------------
def stratify_cells(df: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple], list[tuple], dict]:
    """Decile income on the scoped corpus; assign cell labels; return
    (df with cell column, in_scope cells, out_scope cells, meta)."""
    df = df.copy()
    df["income_decile"] = pd.qcut(df["income"], q=10, labels=False, duplicates="drop")
    df["cell"] = df.apply(
        lambda r: f"lp{int(r['loan_purpose'])}_dec{int(r['income_decile'])}"
        if pd.notna(r["income_decile"]) else None,
        axis=1,
    )
    cell_counts = df.groupby("cell").size().to_dict()
    in_scope, out_scope = [], []
    for cell_id, n in cell_counts.items():
        if cell_id is None:
            continue
        sub = df[df["cell"] == cell_id]
        n_den = int((sub["label"] == 1).sum())
        n_app = int((sub["label"] == 0).sum())
        info = (cell_id, n, n_den, n_app)
        if n >= MIN_SCOPED and n_den >= MIN_DEN and n_app >= MIN_APP:
            in_scope.append(info)
        else:
            out_scope.append(info)

    # Sort cells deterministically.
    in_scope.sort()
    out_scope.sort()

    meta = {
        "n_cells_total": len(cell_counts),
        "n_in_scope": len(in_scope),
        "n_out_scope": len(out_scope),
        "in_scope_cells": [c for c, _, _, _ in in_scope],
        "out_scope_cells": [
            {"cell": c, "n": n, "n_den": d, "n_app": a}
            for c, n, d, a in out_scope
        ],
        "income_decile_boundaries": [
            float(x) for x in pd.qcut(df["income"], q=10, retbins=True, duplicates="drop")[1]
        ],
    }
    return df, in_scope, out_scope, meta


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
    X = np.asarray(Xdf.to_numpy(dtype=float), dtype=float).copy()
    if numeric_cols:
        ncols = [Xdf.columns.get_loc(c) for c in numeric_cols if c in Xdf.columns]
        if ncols:
            imp = SimpleImputer(strategy="median")
            X[:, ncols] = imp.fit_transform(X[:, ncols])
    return X


def filter_usable_candidates(cell: pd.DataFrame, candidates: list[str]) -> list[str]:
    """Drop near-constant candidates (<=1 unique non-null) and candidates with
    >NAN_MAX_FRAC NaN within this cell."""
    keep = []
    for c in candidates:
        if c not in cell.columns:
            continue
        s = cell[c]
        if s.isna().mean() > NAN_MAX_FRAC:
            continue
        nun = int(pd.Series(s).nunique(dropna=True))
        if nun <= 1:
            continue
        keep.append(c)
    return keep


def cell_dropped_for_named_nan(cell: pd.DataFrame) -> str | None:
    """Pre-reg §2g: drop cell if >50% NaN on any named feature."""
    for c in NAMED_FEATURES:
        if c in cell.columns and cell[c].isna().mean() > NAN_MAX_FRAC:
            return c
    return None


def build_band_for_cell(cell: pd.DataFrame, candidates: list[str], *,
                        epsilon: float) -> dict:
    """Build band over `candidates`; de-dup by used-feature-set; compute
    geometry and R^2_named explainer."""
    if not candidates:
        return {"verdict": "SKIP", "reason": "no usable candidates"}
    Xdf = cell[candidates]
    numeric_cols = [c for c in candidates if c not in CATEGORICAL]
    X_all = _impute_numeric(Xdf, numeric_cols)
    y = cell["label"].to_numpy().astype(int)
    if y.size < 50 or y.min() == y.max():
        return {"verdict": "SKIP", "reason": f"degenerate labels (n={y.size}, denied={int(y.sum())})"}

    named_in_cand = [c for c in candidates if c in NAMED_FEATURES]
    if named_in_cand:
        X_named = _impute_numeric(cell[named_in_cand], [c for c in named_in_cand if c not in CATEGORICAL])
    else:
        X_named = np.zeros((y.size, 0))

    band = build_refinement_band(
        X_all, y, feature_names=candidates,
        monotonic_cst_map={},  # unconstrained (no HMDA policy YAML)
        epsilon=epsilon, depths=DEPTHS, leaf_mins=LEAF_MINS,
        holdout_frac=HOLDOUT_FRAC, seed=SEED, max_subset_size=MAX_SUBSET_SIZE,
    )
    if len(band.members) < 2:
        return {
            "verdict": "SKIP",
            "reason": "band <2 members within eps",
            "band_members_within_eps": len(band.members),
            "n_combos_tried": band.n_combos_tried,
        }

    distinct = _dedup_by_used_feature_set(band.members)
    if len(distinct) < 2:
        return {
            "verdict": "SKIP",
            "reason": "band <2 distinct-by-used-feature-set members",
            "n_distinct_uf": len(distinct),
            "band_members_within_eps": len(band.members),
        }

    refit = [
        refit_member(m, _subset_cols(X_all, candidates, m.feature_subset), y,
                     feature_names=list(m.feature_subset), seed=SEED)
        for m in distinct
    ]
    used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
    distinct_uf_sets = sorted({u for u in used_sets if u}, key=lambda x: (len(x), sorted(x)))
    n_used_sets = len(distinct_uf_sets)

    scores = [mdl.predict_proba(_subset_cols(X_all, candidates, m.feature_subset))[:, 1]
              for mdl, m in zip(refit, distinct)]
    med_rho, min_rho = pairwise_ranking_spearman(scores)
    is_plural = (len(distinct) >= 3) and (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)

    M = np.vstack(scores)
    d = per_borrower_disagreement(M)
    p_bar = consensus_scores(M)

    ex_named = (
        disagreement_explainer(
            d, X_named, named_in_cand,
            max_depth=EX_MAX_DEPTH, min_samples_leaf=EX_LEAF_MIN,
            n_splits=EX_FOLDS, seed=SEED,
        ) if named_in_cand else {"cv_r2": None, "root_feature": None, "top_importances": []}
    )
    r2_named = ex_named.get("cv_r2")

    return {
        "verdict": "ANALYZED",
        "n": int(y.size),
        "n_denied": int(y.sum()),
        "denial_rate": round(float(y.mean()), 5),
        "candidates": candidates,
        "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
        "band_members_within_eps": len(band.members),
        "band_distinct_by_tree_signature": len(band.distinct_members),
        "n_distinct_uf_members": len(distinct),
        "n_distinct_used_feature_sets": n_used_sets,
        "distinct_used_feature_sets": [sorted(u) for u in distinct_uf_sets],
        "median_pairwise_spearman": round(med_rho, 4),
        "min_pairwise_spearman": round(min_rho, 4),
        "plural": bool(is_plural),
        "R2_named": r2_named,
        "explainer_named_root_feature": ex_named.get("root_feature"),
        "explainer_named_top_importances": ex_named.get("top_importances"),
        "d_summary": {
            "min": round(float(d.min()), 6),
            "median": round(float(np.median(d)), 6),
            "max": round(float(d.max()), 6),
            "std": round(float(d.std()), 6),
        },
        "n_combos_tried": band.n_combos_tried,
    }


# ---------------------------------------------------------------------------
# Saturation / Jaccard / verdict-divergence per-cell
# ---------------------------------------------------------------------------
def jaccard_set_of_frozensets(A: set[frozenset], B: set[frozenset]) -> float:
    if not A and not B:
        return 1.0
    inter = len(A & B)
    union = len(A | B)
    return inter / union if union else 0.0


def restrict_ufs(ufs: list[list[str]], prohibited: set[str]) -> set[frozenset]:
    return {frozenset(uf) - frozenset(prohibited) for uf in ufs}


def carrier_saturation(ufs: list[list[str]], carrier: str) -> float:
    if not ufs:
        return 0.0
    return sum(1 for uf in ufs if carrier in uf) / len(ufs)


def family_saturation(ufs: list[list[str]], carriers: set[str]) -> float:
    if not ufs:
        return 0.0
    return sum(1 for uf in ufs if any(c in uf for c in carriers)) / len(ufs)


def adequacy(r2_named: float | None) -> str | None:
    if r2_named is None:
        return None
    return "adequate" if r2_named >= R2_GOOD else "inadequate"


def analyze_cell(cell_id: str, cell_df: pd.DataFrame, *, epsilon: float) -> dict:
    """Build variant-A and variant-B; return per-cell metrics."""
    nan_skip = cell_dropped_for_named_nan(cell_df)
    if nan_skip is not None:
        return {
            "cell": cell_id, "in_scope": False,
            "reason_out": f"named feature {nan_skip!r} >50% NaN",
        }
    n = len(cell_df)
    n_den = int((cell_df["label"] == 1).sum())
    n_app = int((cell_df["label"] == 0).sum())

    cand_named = filter_usable_candidates(cell_df, NAMED_FEATURES)
    cand_ext = filter_usable_candidates(cell_df, EXTENSION_FEATURES)
    cand_prohibited = filter_usable_candidates(cell_df, PROHIBITED_FEATURES)
    # Variant A = named U extension U prohibited.  Variant B = named U
    # extension (only the prohibited set is removed).  Pre-reg §2d classes
    # lei as 'institutional, not prohibited' - it lives in EXTENSION_FEATURES
    # and so stays in both variants; it is used only to measure
    # institutional-family saturation for the P3 partial correlation.
    cand_A = cand_named + cand_ext + cand_prohibited
    prohibited_set = set(PROHIBITED_FEATURES)
    cand_B = [c for c in cand_A if c not in prohibited_set]

    if len(cand_A) == len(cand_B):
        return {
            "cell": cell_id, "in_scope": False,
            "reason_out": "no usable prohibited features in this cell",
        }

    recA = build_band_for_cell(cell_df, cand_A, epsilon=epsilon)
    recB = build_band_for_cell(cell_df, cand_B, epsilon=epsilon)

    out: dict = {
        "cell": cell_id, "in_scope": True,
        "n": n, "n_denied": n_den, "n_approved": n_app,
        "candidates_A": cand_A, "candidates_B": cand_B,
        "variant_A": recA, "variant_B": recB,
    }

    if recA.get("verdict") != "ANALYZED" or recB.get("verdict") != "ANALYZED":
        out["analyzable"] = False
        return out
    out["analyzable"] = True

    # Saturation per prohibited carrier (variant A).
    ufs_A = recA["distinct_used_feature_sets"]
    ufs_B = recB["distinct_used_feature_sets"]

    sat_per_carrier: dict[str, float] = {}
    for c in PROHIBITED_FEATURES:
        if c in cand_A:
            sat_per_carrier[c] = round(carrier_saturation(ufs_A, c), 4)
    sat_per_carrier["__family_geographic"] = round(
        family_saturation(ufs_A, set(PROHIBITED_GEOGRAPHIC) & set(cand_A)), 4
    )
    sat_per_carrier["__family_direct"] = round(
        family_saturation(ufs_A, set(PROHIBITED_DIRECT) & set(cand_A)), 4
    )
    if INSTITUTIONAL_FEATURE in cand_A:
        sat_per_carrier[f"__institutional_{INSTITUTIONAL_FEATURE}"] = round(
            carrier_saturation(ufs_A, INSTITUTIONAL_FEATURE), 4
        )
    out["saturation_A"] = sat_per_carrier

    # Jaccard A-restricted vs B (over the pre-registered prohibited set).
    A_restricted = restrict_ufs(ufs_A, prohibited_set)
    B_set = {frozenset(uf) for uf in ufs_B}
    out["jaccard_A_restricted_vs_B"] = round(
        jaccard_set_of_frozensets(A_restricted, B_set), 4
    )
    out["A_has_empty_uf_after_restriction"] = (frozenset() in A_restricted)

    # Adequacy / verdict-divergence.
    r2_A = recA.get("R2_named")
    r2_B = recB.get("R2_named")
    adq_A = adequacy(r2_A)
    adq_B = adequacy(r2_B)
    out["adequacy_A"] = adq_A
    out["adequacy_B"] = adq_B
    out["R2_named_A"] = r2_A
    out["R2_named_B"] = r2_B
    if r2_A is not None and r2_B is not None:
        out["verdict_divergence"] = round(abs(r2_A - r2_B), 4)
        out["verdict_differs"] = (adq_A != adq_B)
    else:
        out["verdict_divergence"] = None
        out["verdict_differs"] = None
    return out


# ---------------------------------------------------------------------------
# P1 phase scoring per carrier
# ---------------------------------------------------------------------------
def score_p1_for_carrier(cells_analyzed: list[dict], carrier_key: str,
                          *, jaccard_thresh: float) -> dict:
    """Score P1 (a-d) for one carrier.  cells_analyzed are dicts with
    saturation_A[carrier_key], jaccard, verdict_divergence."""
    sat = []
    for c in cells_analyzed:
        s = c.get("saturation_A", {}).get(carrier_key)
        if s is None:
            continue
        sat.append({
            "cell": c["cell"], "sat": s,
            "jaccard": c["jaccard_A_restricted_vs_B"],
            "vd": c["verdict_divergence"],
        })
    if not sat:
        return {"carrier": carrier_key, "applicable": False, "reason": "no cells with this carrier"}

    n = len(sat)
    phase0 = [s for s in sat if s["sat"] <= 0.45]
    phase1 = [s for s in sat if 0.48 <= s["sat"] <= 0.65]
    phase2 = [s for s in sat if s["sat"] >= 0.95]
    gap_low = [s for s in sat if 0.45 < s["sat"] < 0.48]
    gap_high = [s for s in sat if 0.65 < s["sat"] < 0.95]

    # (a) phase 0 floor: >=60% of cells in phase 0, all with Jaccard >= 0.7.
    p0_frac = len(phase0) / n
    p0_pass = (p0_frac >= 0.60) and all(s["jaccard"] >= 0.7 for s in phase0)
    # (b) phase 1: >=2 cells in [0.48,0.65], all with Jaccard <= jaccard_thresh, vd < 0.2.
    p1_pass = (len(phase1) >= 2) and all(
        s["jaccard"] <= jaccard_thresh and (s["vd"] is not None and s["vd"] < 0.2) for s in phase1
    )
    # (c) phase 2: >=2 cells with sat>=0.95, all with Jaccard <= jaccard_thresh, vd >= 0.3.
    p2_pass = (len(phase2) >= 2) and all(
        s["jaccard"] <= jaccard_thresh and (s["vd"] is not None and s["vd"] >= 0.3) for s in phase2
    )
    # (d) sharp gaps.
    gaps_pass = (len(gap_low) == 0) and (len(gap_high) == 0)

    # Manufactured-silence cells: sat-in-phase-2-range AND criteria pass.
    phase2_passing = [
        s for s in phase2
        if s["jaccard"] <= jaccard_thresh and s["vd"] is not None and s["vd"] >= 0.3
    ]
    phase1_passing = [
        s for s in phase1
        if s["jaccard"] <= jaccard_thresh and s["vd"] is not None and s["vd"] < 0.2
    ]
    return {
        "carrier": carrier_key,
        "applicable": True,
        "n_cells_with_carrier": n,
        "phase_0_count_in_range": len(phase0),
        "phase_0_fraction_in_range": round(p0_frac, 3),
        "phase_1_count_in_range": len(phase1),
        "phase_2_count_in_range": len(phase2),
        "phase_1_count_passing": len(phase1_passing),
        "phase_2_count_passing": len(phase2_passing),
        "gap_low_count_0.45_to_0.48": len(gap_low),
        "gap_high_count_0.65_to_0.95": len(gap_high),
        "phase_0_floor_pass": p0_pass,
        "phase_1_pass": p1_pass,
        "phase_2_pass": p2_pass,
        "sharp_gaps_pass": gaps_pass,
        "P1_full_HIT": p0_pass and p1_pass and p2_pass and gaps_pass,
        "phase_0_cells_in_range": [s["cell"] for s in phase0],
        "phase_1_cells_in_range": [(s["cell"], s["sat"], s["jaccard"], s["vd"]) for s in phase1],
        "phase_2_cells_in_range": [(s["cell"], s["sat"], s["jaccard"], s["vd"]) for s in phase2],
        "phase_2_cells_passing": [(s["cell"], s["sat"], s["jaccard"], s["vd"]) for s in phase2_passing],
        "phase_1_cells_passing": [(s["cell"], s["sat"], s["jaccard"], s["vd"]) for s in phase1_passing],
    }


# ---------------------------------------------------------------------------
# Partial Spearman (Spearman of residuals on rank-z).
# ---------------------------------------------------------------------------
def _rank(xs):
    sorted_xs = sorted(enumerate(xs), key=lambda t: t[1])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and sorted_xs[j + 1][1] == sorted_xs[i][1]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[sorted_xs[k][0]] = avg
        i = j + 1
    return ranks


def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx * syy == 0:
        return float("nan")
    return sxy / (sxx * syy) ** 0.5


def _spearman(xs, ys):
    return _pearson(_rank(xs), _rank(ys))


def _partial_spearman(xs, ys, zs):
    rx, ry, rz = _rank(xs), _rank(ys), _rank(zs)
    n = len(rz)
    if n < 4:
        return float("nan")
    mz = sum(rz) / n
    szz = sum((r - mz) ** 2 for r in rz)
    if szz == 0:
        return float("nan")
    def resid(r):
        mr = sum(r) / n
        cov = sum((r[i] - mr) * (rz[i] - mz) for i in range(n))
        alpha = cov / szz
        beta = mr - alpha * mz
        return [r[i] - alpha * rz[i] - beta for i in range(n)]
    return _pearson(resid(rx), resid(ry))


# ---------------------------------------------------------------------------
# P5 disparate-impact scoring
# ---------------------------------------------------------------------------
def disparate_impact_per_cell(df: pd.DataFrame, cell_id: str,
                               race_code_map: dict[str, int]) -> dict:
    """Compute denial-rate gap (non-white - white) for one cell."""
    sub = df[df["cell"] == cell_id]
    white_code = race_code_map.get("White")
    if white_code is None or len(sub) == 0:
        return {"cell": cell_id, "available": False}
    is_white = (sub["derived_race"] == white_code)
    n_white = int(is_white.sum())
    n_nonwhite = int((~is_white & (sub["derived_race"] >= 0)).sum())  # exclude -1 (missing)
    if n_white < 5 or n_nonwhite < 5:
        return {
            "cell": cell_id, "available": False,
            "n_white": n_white, "n_nonwhite": n_nonwhite,
        }
    den_white = float(sub.loc[is_white, "label"].mean())
    den_nonwhite = float(sub.loc[~is_white & (sub["derived_race"] >= 0), "label"].mean())
    return {
        "cell": cell_id, "available": True,
        "n_white": n_white, "n_nonwhite": n_nonwhite,
        "denial_rate_white": round(den_white, 4),
        "denial_rate_nonwhite": round(den_nonwhite, 4),
        "gap_nonwhite_minus_white": round(den_nonwhite - den_white, 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_full(probe: bool, eps: float) -> dict:
    t_start = time.time()
    print(f"[{_now_iso()}] loading {HMDA_PARQUET}...", flush=True)
    raw = pd.read_parquet(HMDA_PARQUET)
    print(f"[{_now_iso()}] raw: {len(raw)} rows x {len(raw.columns)} cols", flush=True)

    scoped, scope_meta = apply_scope(raw)
    print(f"[{_now_iso()}] scoped: {scope_meta['n_scoped']} rows "
          f"({scope_meta['n_denied']} denied, {scope_meta['n_approved']} approved)", flush=True)

    prepped, prep_meta = prep_features(scoped)
    # Recover the categorical code for 'White' (used in P5).
    race_codes = prep_meta["categorical_code_maps"]  # only counts; need actual map
    # Re-derive the race code map for P5: re-encode the column to get the map.
    race_cat = pd.Categorical(scoped["derived_race"].astype("string"))
    race_code_map = {str(v): int(i) for i, v in enumerate(race_cat.categories)}

    cells_df, in_scope, out_scope, cell_meta = stratify_cells(prepped)
    print(f"[{_now_iso()}] cells: {len(in_scope)} in-scope, {len(out_scope)} out-of-scope", flush=True)
    if probe and in_scope:
        in_scope = [in_scope[len(in_scope) // 2]]
        print(f"[{_now_iso()}] PROBE: restricting to {in_scope[0][0]}", flush=True)

    per_cell: list[dict] = []
    for ci, (cell_id, n, n_den, n_app) in enumerate(in_scope):
        t0 = time.time()
        cell_df = cells_df[cells_df["cell"] == cell_id].reset_index(drop=True)
        rec = analyze_cell(cell_id, cell_df, epsilon=eps)
        per_cell.append(rec)
        if rec.get("analyzable"):
            va = rec["variant_A"]
            vb = rec["variant_B"]
            print(f"  [{ci+1}/{len(in_scope)}] {cell_id}: n={n} "
                  f"A:[uf={va['n_distinct_used_feature_sets']} R2n={va['R2_named']} adq={rec['adequacy_A']}] "
                  f"B:[uf={vb['n_distinct_used_feature_sets']} R2n={vb['R2_named']} adq={rec['adequacy_B']}] "
                  f"J={rec['jaccard_A_restricted_vs_B']} vd={rec['verdict_divergence']} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        else:
            print(f"  [{ci+1}/{len(in_scope)}] {cell_id}: SKIP "
                  f"({rec.get('reason_out', 'analyzability failure')})", flush=True)

    analyzable = [c for c in per_cell if c.get("analyzable")]

    # P1 scoring over all prohibited carriers + family aggregates.
    p1_per_carrier = []
    for carrier in PROHIBITED_FEATURES + ["__family_geographic", "__family_direct"]:
        p1_per_carrier.append(score_p1_for_carrier(analyzable, carrier, jaccard_thresh=J_PRIMARY))
    p1_any_hit = any(r.get("P1_full_HIT") for r in p1_per_carrier)
    p1_hitting_carriers = [r["carrier"] for r in p1_per_carrier if r.get("P1_full_HIT")]

    # P2: conditional on P1 firing, the trimodal carrier is geographic-context.
    geographic_set = set(PROHIBITED_GEOGRAPHIC) | {"__family_geographic"}
    direct_set = set(PROHIBITED_DIRECT) | {"__family_direct"}
    p2_status: dict = {"applicable": p1_any_hit}
    if p1_any_hit:
        p2_status["hit_carriers"] = p1_hitting_carriers
        p2_status["all_geographic"] = all(c in geographic_set for c in p1_hitting_carriers)
        p2_status["any_direct"] = any(c in direct_set for c in p1_hitting_carriers)
        p2_status["P2_HIT"] = p2_status["all_geographic"] and not p2_status["any_direct"]
    else:
        p2_status["P2_HIT"] = None

    # P3: partial Spearman asymmetry geographic vs institutional.
    sat_geo, sat_inst, vd = [], [], []
    for c in analyzable:
        if c["verdict_divergence"] is None:
            continue
        sat_geo.append(c["saturation_A"].get("__family_geographic", 0.0))
        sat_inst.append(c["saturation_A"].get(f"__institutional_{INSTITUTIONAL_FEATURE}", 0.0))
        vd.append(c["verdict_divergence"])
    p3 = {"n": len(vd)}
    if len(vd) >= 4:
        rho_geo_marg = _spearman(sat_geo, vd)
        rho_inst_marg = _spearman(sat_inst, vd)
        rho_geo_given_inst = _partial_spearman(sat_geo, vd, sat_inst)
        rho_inst_given_geo = _partial_spearman(sat_inst, vd, sat_geo)
        p3.update({
            "rho_geographic_vs_vd_marginal": round(float(rho_geo_marg), 4) if not np.isnan(rho_geo_marg) else None,
            "rho_institutional_vs_vd_marginal": round(float(rho_inst_marg), 4) if not np.isnan(rho_inst_marg) else None,
            "rho_geographic_given_institutional": round(float(rho_geo_given_inst), 4) if not np.isnan(rho_geo_given_inst) else None,
            "rho_institutional_given_geographic": round(float(rho_inst_given_geo), 4) if not np.isnan(rho_inst_given_geo) else None,
            "P3_HIT": (
                (not np.isnan(rho_geo_given_inst)) and (not np.isnan(rho_inst_given_geo))
                and rho_geo_given_inst >= 0.25 and rho_inst_given_geo <= 0.10
            ),
        })
    else:
        p3["P3_HIT"] = None

    # P4: variant-B non-empty on phase-2 cells.  Pre-reg: "phase-2
    # (manufactured silence) cells" = sat>=0.95 AND Jaccard<=thresh AND
    # verdict-divergence>=0.3.  Collect the union across all carriers
    # (not just P1-HIT carriers - a single phase-2 cell on any carrier is
    # an instance of manufactured silence by the pre-reg's definition).
    phase2_cells = set()
    for r in p1_per_carrier:
        if r.get("applicable"):
            phase2_cells.update(c[0] for c in r.get("phase_2_cells_passing", []))
    p4 = {"applicable": len(phase2_cells) > 0,
          "phase_2_cells": sorted(phase2_cells)}
    if phase2_cells:
        non_empty = []
        for cell_id in phase2_cells:
            rec = next((c for c in analyzable if c["cell"] == cell_id), None)
            if rec is None:
                continue
            vb = rec["variant_B"]
            non_empty.append({
                "cell": cell_id,
                "variant_B_uf_count": vb["n_distinct_used_feature_sets"],
                "variant_B_non_empty": vb["n_distinct_used_feature_sets"] >= 1,
            })
        p4["per_cell"] = non_empty
        p4["P4_HIT"] = all(r["variant_B_non_empty"] for r in non_empty)
    else:
        p4["P4_HIT"] = None

    # P5: phase-2 cells show elevated disparate impact.
    p5 = {"applicable": len(phase2_cells) > 0}
    if phase2_cells:
        all_di = [disparate_impact_per_cell(cells_df, c["cell"], race_code_map) for c in analyzable]
        valid_di = [r for r in all_di if r["available"]]
        if len(valid_di) >= 5:
            gaps = sorted([r["gap_nonwhite_minus_white"] for r in valid_di])
            # rank of each phase-2 cell's gap among all valid gaps
            p2_ranks = []
            for cell_id in phase2_cells:
                r = next((x for x in valid_di if x["cell"] == cell_id), None)
                if r is None:
                    continue
                rank = sum(1 for g in gaps if g <= r["gap_nonwhite_minus_white"]) / len(gaps)
                p2_ranks.append({"cell": cell_id, "gap": r["gap_nonwhite_minus_white"], "rank_fraction": round(rank, 3)})
            median_rank = float(np.median([r["rank_fraction"] for r in p2_ranks])) if p2_ranks else None
            p5.update({
                "all_in_scope_disparate_impact": all_di,
                "phase_2_disparate_impact_ranks": p2_ranks,
                "phase_2_median_rank_fraction": round(median_rank, 3) if median_rank is not None else None,
                "P5_HIT": (median_rank is not None and median_rank >= 0.60),
            })
        else:
            p5["P5_HIT"] = None
            p5["reason"] = "fewer than 5 cells with usable disparate-impact data"
    else:
        p5["P5_HIT"] = None

    out = {
        "test": "hmda-trimodal-replication",
        "pre_reg_commit_substantive": "97fcd6f",
        "pre_reg_commit_ots": "32ed3be",
        "pre_reg_path": "docs/superpowers/specs/2026-05-14-hmda-trimodal-replication-preregistration-note.md",
        "epsilon": eps,
        "j_primary": J_PRIMARY,
        "j_arm": list(J_ARM),
        "eps_arm": list(EPS_ARM),
        "depths": list(DEPTHS),
        "leaf_mins": list(LEAF_MINS),
        "max_subset_size": MAX_SUBSET_SIZE,
        "adequacy_threshold_R2_named": R2_GOOD,
        "scope_meta": scope_meta,
        "prep_meta": prep_meta,
        "cell_meta": cell_meta,
        "race_code_map": race_code_map,
        "n_cells_analyzed": len(analyzable),
        "n_cells_skipped": len(per_cell) - len(analyzable),
        "per_cell": per_cell,
        "P1_per_carrier": p1_per_carrier,
        "P1_any_HIT": p1_any_hit,
        "P1_hitting_carriers": p1_hitting_carriers,
        "P2": p2_status,
        "P3": p3,
        "P4": p4,
        "P5": p5,
        "total_seconds": round(time.time() - t_start, 1),
        "run_at": _now_iso(),
    }
    return out


def main():
    ap = argparse.ArgumentParser(description="HMDA-RI 2022 trimodal-replication.")
    ap.add_argument("--probe", action="store_true", help="one in-scope cell only (smoke test)")
    ap.add_argument("--eps", type=float, default=EPS_PRIMARY)
    ap.add_argument("--max-subset-size", type=int, default=_MAX_SUBSET_SIZE_DEFAULT,
                    help="cap on feature-subset size enumerated in build_refinement_band")
    ap.add_argument("--output", type=Path,
                    default=RUNS_DIR / "hmda_trimodal_replication_2026-05-14.json")
    args = ap.parse_args()
    global MAX_SUBSET_SIZE
    MAX_SUBSET_SIZE = args.max_subset_size
    res = run_full(probe=args.probe, eps=args.eps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(res, indent=2, default=str))

    print()
    print("=" * 60)
    print(f"WROTE {args.output}")
    print("=" * 60)
    print(f"n cells analyzed: {res['n_cells_analyzed']}")
    print(f"P1 ANY-HIT: {res['P1_any_HIT']}")
    if res["P1_any_HIT"]:
        print(f"  hitting carriers: {res['P1_hitting_carriers']}")
    print(f"P2 HIT: {res['P2'].get('P2_HIT')}")
    print(f"P3 HIT: {res['P3'].get('P3_HIT')}; partials: "
          f"geo|inst={res['P3'].get('rho_geographic_given_institutional')}, "
          f"inst|geo={res['P3'].get('rho_institutional_given_geographic')}")
    print(f"P4 HIT: {res['P4'].get('P4_HIT')}; phase-2 cells: {res['P4'].get('phase_2_cells')}")
    print(f"P5 HIT: {res['P5'].get('P5_HIT')}; median rank: {res['P5'].get('phase_2_median_rank_fraction')}")
    print(f"total seconds: {res['total_seconds']}")


if __name__ == "__main__":
    main()
