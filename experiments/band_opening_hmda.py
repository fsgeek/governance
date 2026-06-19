"""Stage-2 real-data run on HMDA. GATED on experiments.band_opening_control passing.

Run: python -m experiments.band_opening_hmda

Writes:
  runs/band_opening_hmda_2022RI_2026-06-19.json   -- full result manifest
  (the interpretation readout .md is authored separately, see task brief)

Sequence (spec 2026-06-18-model-class-band-opening-design.md, §5):
  1. assert the Stage-1 synthetic control gate (run_full_control + assert_gate).
     If it RAISES, this module must NOT touch real data.
  2. Load HMDA-RI 2022, align race/sex protected vectors row-for-row.
  3. For each protected axis (race, sex) x each family (cart, linear, gbm):
       sweep_family -> evaluate_policy -> for each eps in the frozen 8-point
       geomspace(0.005, 0.05, 8): filter_to_epsilon_under_loss -> band_outcomes.
  4. Record C, A_plain, A_margin, B_plain, B_margin, min_gap_* per (axis, family, eps).

All four band constants are FROZEN (spec §5): tau=0.02, threshold=0.5,
margin_band=0.10, EPS_SWEEP=geomspace(0.005, 0.05, 8). They are not tuned.

Protected vectors (spec §5 / task brief):
  race: derived_race != "White" (minority = True). Drop Joint / Free Form Text
        Only / Race Not Available / NaN.
  sex : derived_sex == "Female" (True). Drop Joint / Sex Not Available /
        Free Form Text Only / NaN.

NaN handling: HMDA feature columns contain missing values. LogisticRegression
(the linear arm) cannot fit on NaN; CART and HistGBM can. To keep all three
families on IDENTICAL inputs (commensurable C/A/B) we median-impute the feature
matrix ONCE, uniformly, before any sweep. This is standard preprocessing, not a
tuned frozen constant.
"""
from __future__ import annotations

import hashlib
import json
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.band_opening_control import assert_gate, run_full_control
from policy.encoder import PolicyConstraints
from wedge.band_outcomes import approval_rate_gap, band_outcomes
from wedge.collectors.hmda import filter_to_regime, load_dataframe
from wedge.losses import grant_emphasis_loss
from wedge.rashomon import evaluate_policy, filter_to_epsilon_under_loss_relative
from wedge.sweep_families import sweep_family

# -- frozen constants (spec §5) --------------------------------------------
EPS_SWEEP = tuple(float(e) for e in np.geomspace(0.005, 0.05, 8))
TAU = 0.02
THRESHOLD = 0.5
MARGIN_BAND = 0.10

VINTAGE = "2022RI"
HMDA_PARQUET = "data/hmda/processed/hmda_2022_RI.parquet"

FEATURES = (
    "applicant_income",
    "loan_amount",
    "loan_to_income",
    "dti",
    "ltv",
    "loan_term_months",
)

# Per-family grids (task brief).
GRIDS = {
    "cart": {"max_depths": (2, 3, 4, 5), "min_samples_leafs": (50,)},
    "linear": {"Cs": (0.05, 0.2, 1.0, 5.0)},
    "gbm": {"max_iters": (100,)},
}

RACE_DROP = {"Joint", "Free Form Text Only", "Race Not Available"}
SEX_DROP = {"Joint", "Free Form Text Only", "Sex Not Available"}


def _file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _policy() -> PolicyConstraints:
    """Policy for this run: the 6 mapped HMDA features, no prohibited set.

    race/sex are NOT in the feature subset, so there is nothing to prohibit
    here (spec §5 / task brief). monotonicity_map empty (the 6 features' lawful
    directions are not all obvious; fabricating signs would be worse).
    """
    return PolicyConstraints(
        name="hmda_band_opening",
        version="1",
        status="active",
        monotonicity_map={},
        mandatory_features=(),
        prohibited_features=(),
        applicable_regime={},
    )


def load_hmda_aligned() -> dict:
    """Load HMDA-RI 2022, build aligned race/sex protected vectors.

    Returns a dict with X (median-imputed), y, the two protected boolean
    Series (already row-subsetted per axis), and bookkeeping counts.
    """
    p = Path(HMDA_PARQUET)
    df = load_dataframe(p)  # filter_to_regime + map_features + label

    raw = pd.read_parquet(p)
    rawf = filter_to_regime(raw)  # SAME filter -> row-for-row alignment
    if len(df) != len(rawf):
        raise RuntimeError(
            f"ALIGNMENT FAILURE: load_dataframe len {len(df)} != "
            f"filter_to_regime(raw) len {len(rawf)} — protected vector would be "
            "misaligned. STOP."
        )

    n_total = len(df)
    y = df["label"].reset_index(drop=True)
    X_raw = df[list(FEATURES)].reset_index(drop=True)
    nan_per_feature = {c: int(X_raw[c].isna().sum()) for c in FEATURES}
    medians = X_raw.median()
    X = X_raw.fillna(medians)

    race = rawf["derived_race"].reset_index(drop=True)
    sex = rawf["derived_sex"].reset_index(drop=True)

    race_keep = ~(race.isna() | race.isin(RACE_DROP))
    sex_keep = ~(sex.isna() | sex.isin(SEX_DROP))

    axes = {
        "race": {
            "protected": (race[race_keep] != "White").reset_index(drop=True),
            "keep_mask": race_keep,
            "n_dropped": int((~race_keep).sum()),
            "positive_label": "minority (non-White) = True",
        },
        "sex": {
            "protected": (sex[sex_keep] == "Female").reset_index(drop=True),
            "keep_mask": sex_keep,
            "n_dropped": int((~sex_keep).sum()),
            "positive_label": "Female = True",
        },
    }

    return {
        "df_features": X,
        "y": y,
        "axes": axes,
        "n_total_after_regime_filter": n_total,
        "nan_per_feature": nan_per_feature,
        "feature_medians": {c: float(medians[c]) for c in FEATURES},
        "denial_rate": float(1.0 - y.mean()),
    }


def _raw_gap_sanity(X: pd.DataFrame, y: pd.Series, protected: pd.Series) -> dict:
    """Single logistic baseline approval-rate gap, plus empirical label gap.

    If the raw gap is implausible (>0.5, or wrong sign vs the empirical label
    gap), the protected vector is probably misaligned — caller should STOP.
    """
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(max_iter=2000)
    clf.fit(X.to_numpy(), y.to_numpy())

    class _Wrap:
        feature_subset = tuple(X.columns)
        classes_ = (0, 1)
        def predict(self, Xin):
            return clf.predict(Xin[list(X.columns)].to_numpy())
        def predict_proba(self, Xin):
            return clf.predict_proba(Xin[list(X.columns)].to_numpy())

    model_gap = approval_rate_gap(_Wrap(), X, protected)
    p = protected.to_numpy().astype(bool)
    emp_gap = float(y.to_numpy()[~p].mean() - y.to_numpy()[p].mean())
    return {
        "logistic_model_approval_gap": float(model_gap),
        "empirical_label_gap_unprotected_minus_protected": emp_gap,
        "n_protected_true": int(p.sum()),
        "n_protected_false": int((~p).sum()),
    }


def run_hmda(*, random_state: int = 0) -> dict:
    # --- THE GATE (mandatory, first) --------------------------------------
    control = run_full_control(random_state=random_state)
    assert_gate(control)  # raises RuntimeError if gate failed -> NO real data
    print("Stage-1 control gate PASSED. Proceeding to HMDA.")

    data = load_hmda_aligned()
    X, y = data["df_features"], data["y"]
    policy = _policy()

    print(f"HMDA-RI {VINTAGE}: {data['n_total_after_regime_filter']} rows after "
          f"regime filter; denial rate {data['denial_rate']:.4f}")

    sanity = {}
    results: dict = {}
    for axis_name, axis in data["axes"].items():
        keep = axis["keep_mask"].to_numpy()
        Xa = X[keep].reset_index(drop=True)
        ya = y[keep].reset_index(drop=True)
        protected = axis["protected"]
        if len(Xa) != len(protected):
            raise RuntimeError(
                f"axis {axis_name}: X len {len(Xa)} != protected len {len(protected)}"
            )

        s = _raw_gap_sanity(Xa, ya, protected)
        sanity[axis_name] = s
        print(f"[{axis_name}] dropped={axis['n_dropped']} "
              f"n_true={s['n_protected_true']} n_false={s['n_protected_false']} "
              f"logistic_gap={s['logistic_model_approval_gap']:+.4f} "
              f"empirical_gap={s['empirical_label_gap_unprotected_minus_protected']:+.4f}")
        if abs(s["logistic_model_approval_gap"]) > 0.5:
            raise RuntimeError(
                f"axis {axis_name}: logistic approval gap "
                f"{s['logistic_model_approval_gap']:+.4f} is implausible (>0.5) — "
                "protected vector likely misaligned. STOP."
            )

        axis_out: dict = {}
        for fam, grid in GRIDS.items():
            swept = sweep_family(
                Xa, ya, family=fam, grid=grid,
                feature_subsets=(FEATURES,), monotonic_cst=None,
                random_state=random_state,
            )
            pa = evaluate_policy(swept, policy_constraints=policy)
            fam_out: dict = {"n_swept": len(swept), "n_admissible": len(pa.admissible)}
            for eps in EPS_SWEEP:
                band = filter_to_epsilon_under_loss_relative(
                    pa, loss_fn=partial(grant_emphasis_loss),
                    loss_label="L_T", epsilon=eps,
                )
                members = [m.fitted_model for m in band.within_epsilon]
                oc = band_outcomes(
                    members, Xa, protected,
                    tau=TAU, threshold=THRESHOLD, margin_band=MARGIN_BAND,
                )
                fam_out[f"eps_{eps:.6f}"] = oc
            axis_out[fam] = fam_out
            rep_eps = f"eps_{EPS_SWEEP[-1]:.6f}"
            rep = axis_out[fam][rep_eps]
            print(f"  [{axis_name}/{fam}] @eps={EPS_SWEEP[-1]:.4f} "
                  f"C={rep['C']} A_plain={rep['A_plain']:.4f} "
                  f"min_gap_plain={rep['min_gap_plain']:.4f} B_plain={rep['B_plain']} "
                  f"A_margin={rep['A_margin']:.4f} B_margin={rep['B_margin']}")
        results[axis_name] = axis_out

    manifest = {
        "experiment": "stage2_hmda_band_opening",
        "spec": "docs/superpowers/specs/2026-06-18-model-class-band-opening-design.md",
        "vintage": VINTAGE,
        "data_parquet": HMDA_PARQUET,
        "data_sha256": _file_sha256(HMDA_PARQUET),
        "random_state": random_state,
        "frozen_constants": {
            "eps_sweep": list(EPS_SWEEP),
            "tau": TAU,
            "threshold": THRESHOLD,
            "margin_band": MARGIN_BAND,
            "features": list(FEATURES),
            "grids": GRIDS,
            "monotonic_cst": None,
        },
        "nan_handling": "median-impute feature matrix once, uniformly, before sweep",
        "row_counts": {
            "n_after_regime_filter": data["n_total_after_regime_filter"],
            "denial_rate": data["denial_rate"],
            "nan_per_feature": data["nan_per_feature"],
            "feature_medians": data["feature_medians"],
            "race_dropped": data["axes"]["race"]["n_dropped"],
            "sex_dropped": data["axes"]["sex"]["n_dropped"],
            "race_positive_label": data["axes"]["race"]["positive_label"],
            "sex_positive_label": data["axes"]["sex"]["positive_label"],
        },
        "raw_gap_sanity": sanity,
        "control_gate": {
            "gate_passed": control["gate_passed"],
            "clean_arm_passed": control["clean_arm_passed"],
            "dirty_arm_valid": control["dirty"]["dirty_arm_valid"],
        },
        "results": results,
    }
    return manifest


if __name__ == "__main__":
    res = run_hmda()
    out_path = f"runs/band_opening_hmda_{VINTAGE}_2026-06-19.json"
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("wrote", out_path)
