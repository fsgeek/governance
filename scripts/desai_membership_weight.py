"""Desai foil — membership-weighted feature-usage in the 2008Q1 S_rate rb01 band.

The #11 JSON stores the 45 *distinct* used-feature-sets but not how many of the
2517 epsilon-band members instantiate each set. The Desai (2025) phi_i >= phi_min
refutation needs the membership weight: of the admissible (feature-subset x depth x
leaf_min) configurations within the AUC band, what fraction NEVER split on `dti`
(phi_dti identically 0)? Distinct-set count says 31/45 are dti-free; weighting by
member count weights by hyperparameter robustness (a dti-free config admissible
across many depth/leaf_min settings is a robust alternative, not a knife-edge corner).

Reproduces the exact band via the test module's own helpers + frozen constants, and
SELF-VERIFIES against the stored invariants (band_members_within_eps=2517,
n_distinct_used_feature_sets=45, best_holdout_auc=0.7469) before reporting any count.
If the parquet load diverges from the CSV path, the invariant check fails loudly.

Run from repo root:  PYTHONPATH=. python3 scripts/desai_membership_weight.py
"""
from __future__ import annotations
import json, os, sys, time
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import fm_rich_policy_vocab_adequacy_test as fm  # noqa: E402

VINTAGE = "2008Q1"
CELL = "rb01"
MAX_SUBSET_SIZE = 5  # the stored run's band_params value (NOT the arg default of 7)
N_RATE_BANDS = 10
COLLAPSED_PARQUET = Path("data/fanniemae/parquet") / f"{VINTAGE}_h24.collapsed.parquet"

# Stored invariants for 2008Q1 S_rate rb01 variant_A (geography admissible).
EXPECT = {"band_members_within_eps": 2517, "n_distinct_used_feature_sets": 45,
          "best_holdout_auc": 0.7469}


def load_feats() -> pd.DataFrame:
    if COLLAPSED_PARQUET.exists():
        print(f"[load] FM {VINTAGE} from collapsed parquet {COLLAPSED_PARQUET}", flush=True)
        return pd.read_parquet(COLLAPSED_PARQUET)
    print(f"[load] parquet cache absent; CSV fallback via load_vintage", flush=True)
    return fm.load_vintage(VINTAGE, nrows=None)


def main() -> int:
    t0 = time.time()
    feats = load_feats()
    df, _meta = fm.prep(feats)
    drop = list(_meta.get("near_constant_dropped", [])) + ["occupancy_status"]
    named, ext = fm.usable_features(df, drop)
    pc = fm.load_policy(fm.POLICY_PATH)
    mono_default_A = {f: -v for f, v in pc.monotonicity_map.items() if f in named}
    df["s_rate"] = fm.rate_band_labels(df["orig_interest_rate"], N_RATE_BANDS)

    cell = df[df["s_rate"] == CELL].reset_index(drop=True)
    print(f"[cell] {CELL}: n={len(cell)} loans; candidates named={len(named)} ext={len(ext)}", flush=True)

    cand = named + ext
    X_all = fm._impute_numeric(cell[cand], [f for f in cand if f not in fm.CATEGORICAL])
    y = (cell["label"].to_numpy() == 0).astype(int)  # 1 == default

    band = fm.build_refinement_band(
        X_all, y, feature_names=cand, monotonic_cst_map=mono_default_A,
        epsilon=fm.EPSILON, depths=fm.DEPTHS, leaf_mins=fm.LEAF_MINS,
        holdout_frac=fm.HOLDOUT_FRAC, seed=fm.SEED, max_subset_size=MAX_SUBSET_SIZE)

    members = band.members
    n = len(members)

    def refit_used_set(m) -> frozenset:
        """Features the DEPLOYED model splits on: refit on full (X, y), as the
        production pipeline does (refit_member docstring: 'the member you deploy
        is re-fit on everything'). phi is a property of the deployed model."""
        mdl = fm.refit_member(m, fm._subset_cols(X_all, cand, m.feature_subset), y,
                              feature_names=list(m.feature_subset), seed=fm.SEED)
        return frozenset(fm.used_feature_set(mdl, m.feature_subset))

    # Membership-weighted (the bet): refit every one of the 2517 admissible members.
    print(f"[refit] deployed-model usage over {n} members...", flush=True)
    refit_used = [refit_used_set(m) for m in members]

    # Anchor against the stored 45/14: mirror the production dedup-then-refit pipeline
    # (dedup by train-split used-set -> 82 reps -> refit -> distinct deployed used-sets).
    distinct_reps = fm._dedup_by_used_feature_set(members)
    rep_refit = [refit_used_set(m) for m in distinct_reps]
    distinct_refit_sets = {u for u in rep_refit if u}
    anchor_n_distinct = len(distinct_refit_sets)                                # expect 45
    anchor_dti_distinct = sum(1 for u in distinct_refit_sets if "dti" in u)     # expect 14

    got = {"band_members_within_eps": n,
           "n_distinct_used_feature_sets": anchor_n_distinct,
           "best_holdout_auc": round(band.best_holdout_auc, 4)}
    ok = (got["band_members_within_eps"] == EXPECT["band_members_within_eps"]
          and got["n_distinct_used_feature_sets"] == EXPECT["n_distinct_used_feature_sets"]
          and abs(got["best_holdout_auc"] - EXPECT["best_holdout_auc"]) < 1e-4)
    print(f"[verify] got {got}  expect {EXPECT}  ->  {'MATCH' if ok else 'MISMATCH'}", flush=True)
    print(f"[anchor] distinct deployed used-sets containing dti: {anchor_dti_distinct}/{anchor_n_distinct} (expect 14/45)", flush=True)

    # The bet quantity: fraction of deployed admissible models that never split on
    # dti (phi_dti identically 0). Empty used-set (degenerate stump) counts dti-free.
    dti_free_members = sum(1 for u in refit_used if "dti" not in u)
    dti_free_member_frac = dti_free_members / n
    distinct_nonempty = {u for u in refit_used if u}
    dti_free_distinct = sum(1 for u in distinct_nonempty if "dti" not in u)

    # Per-feature membership share (context: which features carry the band).
    feat_member_count: Counter = Counter()
    for u in refit_used:
        for f in u:
            feat_member_count[f] += 1
    feat_member_share = {f: round(c / n, 4) for f, c in feat_member_count.most_common()}

    result = {
        "test": "desai-membership-weight",
        "substrate": f"FM-{VINTAGE}", "stratum": "S_rate", "cell": CELL,
        "variant": "A_geography_admissible",
        "source": "collapsed_parquet" if COLLAPSED_PARQUET.exists() else "csv",
        "invariant_check": {"expected": EXPECT, "got": got, "match": ok},
        "anchor_distinct_deployed_used_sets": anchor_n_distinct,
        "anchor_dti_in_distinct_sets": f"{anchor_dti_distinct}/{anchor_n_distinct}",
        "band_members_within_eps": n,
        "n_distinct_deployed_used_sets_all_members": len(distinct_nonempty),
        "dti": {
            "free_members": dti_free_members,
            "free_member_fraction": round(dti_free_member_frac, 4),
            "using_members": n - dti_free_members,
            "free_distinct_sets": dti_free_distinct,
            "using_distinct_sets": len(distinct_nonempty) - dti_free_distinct,
        },
        "feature_member_share": feat_member_share,
        "recorded_bet": "membership-weighted dti-free fraction in [0.20, 0.35]; "
                        "<0.05 vindicates Desai (corner), >0.50 obliterates it",
        "seconds": round(time.time() - t0, 1),
    }
    outp = Path("runs") / f"desai_membership_weight_{VINTAGE}_{CELL}.json"
    outp.write_text(json.dumps(result, indent=2))
    print(f"\n[RESULT] dti-free membership fraction = {dti_free_member_frac:.3f} "
          f"({dti_free_members}/{n} members)   distinct dti-free sets = {dti_free_distinct}/{len(distinct_nonempty)}")
    print(f"[RESULT] top feature shares: {dict(list(feat_member_share.items())[:8])}")
    print(f"[RESULT] -> {outp}  ({result['seconds']}s)  invariant {'OK' if ok else 'FAILED'}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
