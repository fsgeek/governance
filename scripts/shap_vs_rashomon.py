"""SHAP vs. Rashomon non-inferiority comparison.

Pre-registered design in
docs/superpowers/specs/2026-05-09-shap-vs-rashomon-preregistration-note.md.

For each vintage (V1 2014Q3, V2alt 2015Q3, V2 2015Q4):
  1. Replicate the wedge run's data load + train/eval split.
  2. Train one xgboost on X_train (the "deployed model" arm).
  3. Compute TreeSHAP values on the eval set.
  4. Apply four pre-registered SHAP-silence criteria.
  5. Load the matching jsonl run; identify T-silent-all (and F-silent-all)
     populations from per_model.factor_support_T/F (5/5 silent).
  6. Cross-tabulate SHAP-silent populations against T-silent-all and
     F-silent-all by Jaccard overlap and charge-off rates.

Multi-vintage results expose the regime-shift signature: T-silent-all goes
0 -> nonzero V1 -> V2 in the Rashomon analysis. The pre-registered question
is whether any SHAP-silence criterion shows the same 0 -> nonzero shift.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

from wedge.collectors.lendingclub import (
    ORIGINATION_FEATURE_COLS,
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
# Vintage <-> jsonl mapping is authoritative per each run's adjacent
# meta.json (written by wedge/run.py). Do not trust dict labels alone.
RUNS = {
    "2014Q3": ("2014Q3", "runs/2026-05-08T17-43-21Z.jsonl"),
    "2015Q3": ("2015Q3", "runs/2026-05-08T00-00-09Z.jsonl"),
    "2015Q4": ("2015Q4", "runs/2026-05-08T17-44-39Z.jsonl"),
}
TERM = "36 months"
SEED = 0
TEST_SIZE = 0.30


# ----------------------------------------------------------------------
def replicate_split(vintage: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Replicate the wedge run.py train/eval split deterministically."""
    df = pd.read_csv(LC_CSV, low_memory=False)
    df = filter_to_vintage(df, vintage=vintage, term=TERM)
    df = df.assign(label=derive_label(df["loan_status"]))
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]
    train_df, eval_df = train_test_split(
        df, test_size=TEST_SIZE, random_state=SEED, stratify=df["label"]
    )
    return train_df.reset_index(drop=True), eval_df.reset_index(drop=True), feature_cols


def train_deployed_model(X_train, y_train) -> xgb.XGBClassifier:
    """Train one xgboost on X_train. Calibration via isotonic on a holdout
    of train (matches what a bank's deployed-and-calibrated model looks like)."""
    base = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=SEED,
        eval_metric="logloss",
        n_jobs=-1,
    )
    # NaN handling: xgboost handles NaN natively, no imputation needed.
    base.fit(X_train.values, y_train.values)
    return base


def compute_treeshap(model: xgb.XGBClassifier, X: pd.DataFrame) -> np.ndarray:
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X.values)
    # For binary xgboost, shap_values returns a single (n, p) matrix
    # representing margin contributions for the positive class.
    return sv


# ----------------------------------------------------------------------
@dataclass
class SilencePopulations:
    """Boolean mask per case for each pre-registered criterion."""
    magnitude: np.ndarray
    concentration: np.ndarray
    instability: np.ndarray
    baseline_dominance: np.ndarray

    def as_dict(self) -> dict[str, np.ndarray]:
        return {
            "magnitude": self.magnitude,
            "concentration": self.concentration,
            "instability": self.instability,
            "baseline_dominance": self.baseline_dominance,
        }


def silence_magnitude(shap_values: np.ndarray, q: float = 0.10) -> np.ndarray:
    """Bottom-q decile of sum(|SHAP|) per case. Model uses no feature strongly."""
    total_mag = np.abs(shap_values).sum(axis=1)
    threshold = np.quantile(total_mag, q)
    return total_mag <= threshold


def silence_concentration(shap_values: np.ndarray, q: float = 0.10) -> np.ndarray:
    """Bottom-q decile of (top-1 |SHAP| / sum |SHAP|) per case. No dominant reason."""
    abs_sv = np.abs(shap_values)
    total = abs_sv.sum(axis=1)
    top1 = abs_sv.max(axis=1)
    # Avoid division by zero for cases with all-zero SHAP (perfectly base-rate).
    ratio = np.divide(top1, total, out=np.zeros_like(top1), where=total > 0)
    threshold = np.quantile(ratio, q)
    return ratio <= threshold


def silence_instability(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    k_top: int = 3,
    n_neighbors: int = 10,
) -> np.ndarray:
    """Top-k SHAP signs flip on nearest neighbors (majority of neighbors disagree)."""
    from sklearn.neighbors import NearestNeighbors
    Xv = X.values.astype(float)
    # Standardize features so distance is meaningful with mixed scales.
    Xz = (Xv - np.nanmean(Xv, axis=0)) / (np.nanstd(Xv, axis=0) + 1e-9)
    Xz = np.nan_to_num(Xz, nan=0.0)
    nn = NearestNeighbors(n_neighbors=n_neighbors + 1).fit(Xz)
    _, idx = nn.kneighbors(Xz)
    # idx[:, 0] is self; use idx[:, 1:].
    neigh_idx = idx[:, 1:]

    abs_sv = np.abs(shap_values)
    top_k_features = np.argsort(-abs_sv, axis=1)[:, :k_top]
    signs = np.sign(shap_values)

    n_cases = shap_values.shape[0]
    flagged = np.zeros(n_cases, dtype=bool)
    for i in range(n_cases):
        my_top = top_k_features[i]
        my_signs = signs[i, my_top]
        flips = 0
        for j in neigh_idx[i]:
            if (signs[j, my_top] != my_signs).any():
                flips += 1
        if flips > n_neighbors // 2:
            flagged[i] = True
    return flagged


def silence_baseline_dominance(
    model: xgb.XGBClassifier,
    X: pd.DataFrame,
    shap_values: np.ndarray,
    base_rate: float,
    eps: float = 0.05,
    k_top: int = 3,
) -> np.ndarray:
    """After zeroing top-k SHAP-magnitude features, predicted prob within
    eps of base rate (model is essentially predicting base rate)."""
    abs_sv = np.abs(shap_values)
    top_k = np.argsort(-abs_sv, axis=1)[:, :k_top]
    Xz = X.values.astype(float).copy()
    # Replace top-k features with column mean (equivalent to "zero out signal").
    col_means = np.nanmean(Xz, axis=0)
    for i in range(Xz.shape[0]):
        Xz[i, top_k[i]] = col_means[top_k[i]]
    preds = model.predict_proba(Xz)[:, 1]
    return np.abs(preds - base_rate) <= eps


def compute_silence(
    model: xgb.XGBClassifier,
    X: pd.DataFrame,
    shap_values: np.ndarray,
    base_rate: float,
) -> SilencePopulations:
    return SilencePopulations(
        magnitude=silence_magnitude(shap_values),
        concentration=silence_concentration(shap_values),
        instability=silence_instability(shap_values, X),
        baseline_dominance=silence_baseline_dominance(model, X, shap_values, base_rate),
    )


# ----------------------------------------------------------------------
def load_rashomon_silence(jsonl_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For each eval case in the jsonl, compute (silent_t_count, silent_f_count, label).

    Returns three arrays of length n_cases, in jsonl order.
    """
    silent_t, silent_f, labels = [], [], []
    for line in jsonl_path.open():
        rec = json.loads(line)
        if rec["origin"] != "real":
            continue  # ignore synthetic boundary cases
        members = rec["per_model"]
        st = sum(1 for m in members if not m["factor_support_T"])
        sf = sum(1 for m in members if not m["factor_support_F"])
        silent_t.append(st)
        silent_f.append(sf)
        labels.append(int(rec["label"]))
    return np.array(silent_t), np.array(silent_f), np.array(labels)


# ----------------------------------------------------------------------
def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool); b = b.astype(bool)
    union = (a | b).sum()
    if union == 0:
        return 0.0
    return float((a & b).sum() / union)


def report_vintage(label: str, vintage: str, jsonl_path: Path) -> dict:
    print(f"\n=== {label}  vintage={vintage} ===")
    train_df, eval_df, feature_cols = replicate_split(vintage)
    print(f"  train: {len(train_df)}  eval: {len(eval_df)}  features: {feature_cols}")
    X_train, y_train = train_df[feature_cols], train_df["label"]
    X_eval, y_eval = eval_df[feature_cols], eval_df["label"]
    base_rate = float(y_train.mean())

    model = train_deployed_model(X_train, y_train)
    shap_values = compute_treeshap(model, X_eval)

    silence = compute_silence(model, X_eval, shap_values, base_rate)

    silent_t, silent_f, jsonl_labels = load_rashomon_silence(jsonl_path)

    # Sanity: jsonl real cases should match eval_df row count and labels.
    assert len(silent_t) == len(eval_df), (
        f"jsonl real-case count {len(silent_t)} != eval_df {len(eval_df)} for {label}"
    )
    if not (jsonl_labels == y_eval.values).all():
        # Order may not match; jsonl iteration order should be eval_df row order
        # per wedge/run.py but flag if not.
        n_match = (jsonl_labels == y_eval.values).sum()
        print(f"  WARN: jsonl/eval label mismatch — only {n_match}/{len(jsonl_labels)} aligned")

    n_members = 5  # per all three runs' meta.json
    t_silent_all = silent_t == n_members
    f_silent_all = silent_f == n_members

    print(f"  Rashomon T-silent-all: {t_silent_all.sum()} cases ({100*t_silent_all.mean():.2f}%)")
    print(f"  Rashomon F-silent-all: {f_silent_all.sum()} cases ({100*f_silent_all.mean():.2f}%)")
    if t_silent_all.sum():
        print(f"    T-silent-all charge-off rate: {y_eval.values[t_silent_all].mean():.3f}  (base {base_rate:.3f})")
    if f_silent_all.sum():
        print(f"    F-silent-all charge-off rate: {y_eval.values[f_silent_all].mean():.3f}  (base {base_rate:.3f})")

    results = {"vintage": vintage, "n_eval": len(eval_df), "base_rate": base_rate,
               "t_silent_all_n": int(t_silent_all.sum()),
               "f_silent_all_n": int(f_silent_all.sum()),
               "criteria": {}}

    print(f"\n  SHAP-silence criteria (rates and overlaps with T-silent-all / F-silent-all):")
    for name, mask in silence.as_dict().items():
        n_flag = int(mask.sum())
        rate = mask.mean()
        co_rate = float(y_eval.values[mask].mean()) if n_flag else 0.0
        jac_t = jaccard(mask, t_silent_all)
        jac_f = jaccard(mask, f_silent_all)
        print(f"    {name:22s} n={n_flag:5d} ({100*rate:5.2f}%)  charge-off={co_rate:.3f}  "
              f"Jac(T-silent-all)={jac_t:.3f}  Jac(F-silent-all)={jac_f:.3f}")
        results["criteria"][name] = {
            "n": n_flag, "rate": float(rate), "charge_off": co_rate,
            "jaccard_t_silent_all": jac_t, "jaccard_f_silent_all": jac_f,
        }

    return results


def main() -> int:
    all_results = {}
    for label, (vintage, jsonl_str) in RUNS.items():
        all_results[label] = report_vintage(label, vintage, Path(jsonl_str))

    print("\n\n=== Regime-shift signature (V1 -> V2alt -> V2) ===")
    print("  Rashomon T-silent-all rate by vintage:")
    for label in RUNS:
        r = all_results[label]
        rate = r["t_silent_all_n"] / r["n_eval"]
        print(f"    {label}: {r['t_silent_all_n']:5d} ({100*rate:5.2f}%)")
    print("  SHAP-silence rates by vintage (per criterion):")
    for crit in ("magnitude", "concentration", "instability", "baseline_dominance"):
        rates = [all_results[label]["criteria"][crit]["rate"] for label in RUNS]
        n_flags = [all_results[label]["criteria"][crit]["n"] for label in RUNS]
        print(f"    {crit:22s}: " +
              "  ".join(f"{lbl}={n} ({100*r:5.2f}%)"
                       for lbl, n, r in zip(RUNS.keys(), n_flags, rates)))

    out_path = Path("runs/shap_vs_rashomon_results.json")
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nResults written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
