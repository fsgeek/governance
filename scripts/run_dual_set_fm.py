"""Dual-set Target C run on Fannie Mae 2018Q1.

Cross-asset-class test of the LC null-Cat-2 finding. FM has a different
feature space (FICO + DTI + LTV + loan_term, no annual_inc/emp_length)
and a different label semantic (ever-90+DPD-in-24mo, not charge-off).

Caveat: only FM 2018Q1 is on disk, so target and surprise cohorts are
both drawn from 2018Q1 (50/50 row-split). This degrades the
"different-vintage surprise" semantic — the surprise model is trained
on a sibling subset of the same vintage rather than a distinct prior
vintage. The dual-set / Cat-2 mechanics still exercise; the surprise-
weighting interpretation is weaker. Flagged in §0 of the writeup.

Usage:
    PYTHONPATH=. python scripts/run_dual_set_fm.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from policy.encoder import load_policy
from wedge.collectors.fanniemae import (
    derive_origination_and_label,
    filter_eligible,
    read_raw,
    to_feature_frame,
)
from wedge.orchestration import run_dual_set_target_c


FM_CSV = Path("data/fanniemae/2018Q1.csv")
FM_POLICY = Path("policy/thin_demo_fm.yaml")
OUTPUT_DIR = Path("runs")
SEED = 0


def _load_fm_frame() -> pd.DataFrame:
    """Load FM 2018Q1 as a DataFrame with the wedge feature columns + label."""
    raw = read_raw(FM_CSV)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible)
    return feats


def main() -> None:
    frame = _load_fm_frame()
    print(f"FM 2018Q1 eligible rows: {len(frame)}")
    # Numeric features only — drop loan_purpose/occupancy_status/lien_position
    # for the sweep (they're categorical strings and the wedge's sweep is
    # numeric-only).
    feature_cols = ["fico_range_low", "dti", "ltv", "loan_term_months"]
    frame = frame[feature_cols + ["label"]].dropna(subset=feature_cols + ["label"]).reset_index(drop=True)
    print(f"after numeric-feature dropna: {len(frame)} rows; "
          f"grant={int(frame['label'].sum())}, deny={int((1-frame['label']).sum())}")

    # 50/50 row-split into target / surprise cohorts (stratified on label).
    target_df, surprise_df = train_test_split(
        frame, test_size=0.50, random_state=SEED, stratify=frame["label"]
    )
    target_df = target_df.reset_index(drop=True)
    surprise_df = surprise_df.reset_index(drop=True)
    print(f"target={len(target_df)} surprise={len(surprise_df)}")

    policy = load_policy(FM_POLICY)

    summary = run_dual_set_target_c(
        df_target=target_df,
        df_surprise_train=surprise_df,
        feature_cols=feature_cols,
        target_vintage_label="FM-2018Q1-target-half",
        surprise_vintage_label="FM-2018Q1-surprise-half",
        output_dir=OUTPUT_DIR,
        policy_constraints=policy,
        epsilon_T=0.05,
        epsilon_F=0.05,
        w_T=1.5,
        w_F=1.5,
        n_members=5,
        seed=SEED,
    )

    print(f"\nrun_id: {summary['run_id']}")
    print(f"jsonl: {summary['jsonl_path']}")
    print(f"manifest: {summary['manifest_path']}")
    print(f"oos cases: {summary['n_oos_cases']}")
    print(f"admissible={summary['admissible_count']} excluded={summary['excluded_count']}")
    print(
        f"|R_T|={summary['n_R_T']} |R_F|={summary['n_R_F']} "
        f"|R_T'|={summary['n_R_T_prime']} |R_F'|={summary['n_R_F_prime']}"
    )
    print(f"category_counts: {summary['category_counts']}")
    print(f"I_pred > {summary['i_pred_threshold']}: {summary['i_pred_above_threshold']}")
    print(
        f"surprise weight mean={summary['surprise_weight_mean']:.4f} "
        f"max={summary['surprise_weight_max']:.4f}"
    )


if __name__ == "__main__":
    main()
