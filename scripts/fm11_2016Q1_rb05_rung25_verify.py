"""Direct verification of the rb05 rung-2.5 inference (2016Q1).

The result note's §3b infers rung-2.5 on 2016Q1 rb05 from variant-B closure:
variant A R²_named = 0.208, variant B R²_named = 0.688 (with DTI + FTHB carrying
it), suggesting the depth-3 named-only explainer cannot see the DTI-within-state
interaction the variant-A band keys on. That's compelling inference but not
direct evidence. This script tests the depth-as-limiter hypothesis directly:

    Refit the variant-A named-only explainer of d on rb05 at depth in {3, 4, 5, 6}.
    If R²_named at depth >=4 jumps toward variant-B's 0.69, the depth ceiling was
    the limiter on the named-only explainer; the named vocabulary was sufficient
    but the explainer's functional form was not.

Reuses the same 2016Q1 load + same prep + same regime envelope + same rate-band
deciles + same ms=5 band construction as the main run, so the result is
comparable.

Writes runs/fm11_2016Q1_rb05_rung25_verify.json. ~25 min compute (the FM load
dominates; the explainer refits are seconds each).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import KFold, cross_val_score
from sklearn.tree import DecisionTreeRegressor

from policy.encoder import load_policy
from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)
from wedge.routing import consensus_scores, per_borrower_disagreement

from scripts.fm_rich_policy_vocab_adequacy_test import (
    CATEGORICAL,
    DEPTHS,
    EPSILON,
    EX_FOLDS,
    EX_LEAF_MIN,
    HOLDOUT_FRAC,
    LEAF_MINS,
    NAMED_CANDIDATE,
    SEED,
    _dedup_by_used_feature_set,
    _impute_numeric,
    _subset_cols,
    load_vintage,
    prep,
    rate_band_labels,
    usable_features,
    EXTENSION_CANDIDATE,
)


VINTAGE = "2016Q1"
CELL = "rb05"
N_RATE_BANDS = 10
MS = 5
DEPTH_SWEEP = (3, 4, 5, 6, 7)
OUT = Path("runs") / f"fm11_{VINTAGE}_{CELL}_rung25_verify.json"


def main() -> int:
    t0 = time.time()
    feats = load_vintage(VINTAGE, nrows=None)
    df, _ = prep(feats)
    df["s_rate"] = rate_band_labels(df["orig_interest_rate"], N_RATE_BANDS)
    cell = df[df["s_rate"] == CELL].reset_index(drop=True)
    if len(cell) < 50:
        raise SystemExit(f"cell {CELL} has only {len(cell)} loans; bailing")
    named, ext = usable_features(df, drop=["amortization_type", "occupancy_status"])
    cand = named + ext
    print(f"[verify] cell={CELL} n={len(cell)} named({len(named)})+ext({len(ext)})={len(cand)}", flush=True)

    # Build the variant-A band (same params as the main run).
    pc = load_policy("policy/fnma_eligibility_matrix.yaml")
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in named}
    X_all = _impute_numeric(cell[cand], [f for f in cand if f not in CATEGORICAL])
    X_named = _impute_numeric(cell[named], [f for f in named if f not in CATEGORICAL])
    y = (cell["label"].to_numpy() == 0).astype(int)  # 1 = default
    print(f"[verify] y.size={y.size} defaults={int(y.sum())} default_rate={y.mean():.5f}", flush=True)

    band = build_refinement_band(X_all, y, feature_names=cand, monotonic_cst_map=mono_default,
                                 epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS,
                                 holdout_frac=HOLDOUT_FRAC, seed=SEED, max_subset_size=MS)
    distinct = _dedup_by_used_feature_set(band.members)
    refit = [refit_member(m, _subset_cols(X_all, cand, m.feature_subset), y,
                          feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
    used_sets = [sorted(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
    scores = [mdl.predict_proba(_subset_cols(X_all, cand, m.feature_subset))[:, 1]
              for mdl, m in zip(refit, distinct)]
    med_rho, _ = pairwise_ranking_spearman(scores)
    M = np.vstack(scores)
    d = per_borrower_disagreement(M)
    p_bar = consensus_scores(M)
    print(f"[verify] band rebuilt: {len(distinct)} distinct uf-members, "
          f"{len({tuple(u) for u in used_sets})} distinct used-feature-sets, med_rho={med_rho:.3f}", flush=True)
    print(f"[verify] d: min={d.min():.6f} median={float(np.median(d)):.6f} max={d.max():.6f} std={d.std():.6f}", flush=True)

    # Refit the named-only explainer at varying depths.
    result_per_depth: dict = {}
    for depth in DEPTH_SWEEP:
        kf = KFold(n_splits=EX_FOLDS, shuffle=True, random_state=SEED)
        tree = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=EX_LEAF_MIN, random_state=SEED)
        folds = cross_val_score(tree, X_named, d, cv=kf, scoring="r2")
        cv_r2 = float(np.mean(folds))
        full = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=EX_LEAF_MIN, random_state=SEED).fit(X_named, d)
        t = full.tree_
        root = named[int(t.feature[0])] if t.node_count > 0 and int(t.feature[0]) >= 0 else None
        imps = sorted(zip(named, (float(i) for i in full.feature_importances_)), key=lambda kv: -kv[1])
        result_per_depth[depth] = {
            "cv_r2_named": round(cv_r2, 4),
            "cv_r2_folds": [round(float(f), 4) for f in folds],
            "root_feature": root,
            "top_importances": [(nm, round(im, 4)) for nm, im in imps[:5] if im > 0],
            "n_features_used": int(sum(1 for i in full.feature_importances_ if i > 1e-12)),
            "n_internal_nodes": int(sum(1 for i in range(t.node_count) if int(t.feature[i]) >= 0)),
            "n_leaves": int(sum(1 for i in range(t.node_count) if int(t.feature[i]) < 0)),
        }
        print(f"[verify] depth={depth}: R²_named={cv_r2:.4f}, root={root}, n_feat_used={result_per_depth[depth]['n_features_used']}, n_internal={result_per_depth[depth]['n_internal_nodes']}", flush=True)

    out = {
        "test": "rb05 rung-2.5 direct verification — named-explainer depth sweep",
        "vintage": VINTAGE, "cell": CELL,
        "n": int(len(cell)), "default_rate": round(float(y.mean()), 5),
        "named_features": named, "extension_features": ext,
        "band_summary": {
            "n_distinct_uf_members": len(distinct),
            "n_distinct_used_feature_sets": len({tuple(u) for u in used_sets}),
            "median_pairwise_spearman": round(float(med_rho), 4),
            "distinct_used_feature_sets": sorted({tuple(u) for u in used_sets}, key=lambda x: (len(x), x)),
            "d_min": round(float(d.min()), 6),
            "d_median": round(float(np.median(d)), 6),
            "d_max": round(float(d.max()), 6),
            "d_std": round(float(d.std()), 6),
        },
        "explainer_named_depth_sweep": result_per_depth,
        "ms": MS, "epsilon": EPSILON, "explainer_leaf_min": EX_LEAF_MIN, "explainer_cv_folds": EX_FOLDS,
        "reference_2016Q1_main_run": {
            "rb05_variant_A_R2_named_at_depth_3": 0.208,
            "rb05_variant_B_R2_named_at_depth_3": 0.688,
            "note": "main run JSON: runs/fm_rich_policy_vocab_adequacy_2016Q1.json",
        },
        "total_seconds": round(time.time() - t0, 1),
    }
    out_str = json.dumps(out, indent=2, default=lambda v: str(v) if not isinstance(v, (int, float, str, type(None), list, dict, bool)) else v)
    OUT.write_text(out_str)
    print(f"\n[verify] wrote {OUT} ({out['total_seconds']}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
