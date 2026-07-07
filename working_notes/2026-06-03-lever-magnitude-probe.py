"""Falsifying probe for the lever-magnitude pivot (2026-06-03).

THE QUESTION (the mandate from the outgoing ghola, distrust-the-4th-draft):
    Is "magnitude of the discretionary lever" distinct from `bisg - bare`,
    or is it the same number wearing a regulator's hat?

THE LEVER (the pivot's central quantity):
    gap(S) = disparate-impact gap in grant rate between race groups, for a
    model trained on admissible feature-set S.
    The lever = how much the *analyst's choice of S* moves gap(S).

THE KILL TEST:
    If gap(S) is just a monotone function of proxy_strength = AUC(race ~ S),
    then "lever-magnitude" carries NO information beyond proxy-strength ->
    it IS bisg - bare relabeled -> pivot DEAD.

    If two *defensible* admissible sets at SIMILAR proxy_strength produce
    DIFFERENT gaps, discretion does independent work -> lever is REAL.

This is a probe, not a frozen experiment. No predictions are scored; the
output is read to decide whether the pivot survives to a freeze.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

PARQUET = "data/hmda/processed/hmda_2022_RI.parquet"

# Admissible numeric features available in raw HMDA (regulator-mandated pool).
# These are the features an analyst could *defensibly* include or exclude.
RAW_NUMERIC = {
    "income": "income",
    "loan_amount": "loan_amount",
    "ltv": "loan_to_value_ratio",
    "dti_raw": "debt_to_income_ratio",  # parsed below
    "loan_term": "loan_term",
    "property_value": "property_value",
    "interest_rate": "interest_rate",
    "loan_to_income": "_derived_lti",
    # Geographic / tract features: admissible (they're in the LAR) but the
    # classic disparate-impact proxies. An analyst chooses whether to use them.
    "tract_minority_pct": "tract_minority_population_percent",
    "tract_to_msa_income": "tract_to_msa_income_percentage",
}

# Defensible admissible feature-sets. Each is a choice a real analyst could
# justify on non-racial grounds. They span the proxy-strength axis.
FEATURE_SETS = {
    # Pure financial underwriting, no geography.
    "financial_core": ["income", "loan_amount", "ltv", "dti_raw", "loan_term"],
    # Financial + property value + rate (richer underwriting).
    "financial_rich": ["income", "loan_amount", "ltv", "dti_raw", "loan_term",
                        "property_value", "interest_rate"],
    # Capacity-only (the leanest defensible set).
    "capacity_only": ["income", "dti_raw", "loan_to_income"],
    # Financial + tract income (defensible: area cost-of-living). Mild proxy.
    "fin_plus_tract_income": ["income", "loan_amount", "ltv", "dti_raw",
                              "loan_term", "tract_to_msa_income"],
    # Financial + tract minority pct (defensible-on-paper: "neighborhood
    # risk"; this is the strong geographic proxy). High proxy strength.
    "fin_plus_tract_minority": ["income", "loan_amount", "ltv", "dti_raw",
                                "loan_term", "tract_minority_pct"],
}

# Baselines for the bisg-bare comparison.
BARE = []  # no features -> gap from the intercept only (~0 by construction)
PROXY_ONLY = ["tract_minority_pct", "tract_to_msa_income"]  # the "bisg" arm


def load() -> pd.DataFrame:
    df = pd.read_parquet(PARQUET)
    # regime filter mirroring wedge.collectors.hmda.filter_to_regime
    mask = (
        df["action_taken"].isin([1, 3])
        & df["loan_purpose"].isin([1, 31, 32])
        & (df["lien_status"] == 1)
        & (df["occupancy_type"] == 1)
    )
    df = df.loc[mask].reset_index(drop=True)

    out = pd.DataFrame(index=df.index)
    out["label"] = (df["action_taken"].astype(int) == 1).astype(int)  # grant=1

    # numeric features
    out["income"] = pd.to_numeric(df["income"], errors="coerce")
    out["loan_amount"] = pd.to_numeric(df["loan_amount"], errors="coerce")
    out["loan_to_value_ratio"] = pd.to_numeric(df["loan_to_value_ratio"], errors="coerce")
    out["loan_term"] = pd.to_numeric(df["loan_term"], errors="coerce")
    out["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")
    out["interest_rate"] = pd.to_numeric(df["interest_rate"], errors="coerce")
    out["tract_minority_population_percent"] = pd.to_numeric(
        df["tract_minority_population_percent"], errors="coerce")
    out["tract_to_msa_income_percentage"] = pd.to_numeric(
        df["tract_to_msa_income_percentage"], errors="coerce")
    out["_derived_lti"] = out["loan_amount"] / out["income"].where(out["income"] > 0)

    # DTI: parse banded ordinal exactly as the collector does
    dti_order = ["<20%", "20%-<30%", "30%-<36%", "36", "37", "38", "39", "40",
                 "41", "42", "43", "44", "45", "46", "47", "48", "49",
                 "50%-60%", ">60%"]
    dti_rank = {v: i for i, v in enumerate(dti_order)}
    out["debt_to_income_ratio"] = df["debt_to_income_ratio"].astype(str).str.strip().map(dti_rank).astype("float64")

    # protected attribute: White vs Black (the disparate-impact contrast)
    out["race"] = df["derived_race"]
    return out


def _cols(feat_keys: list[str]) -> list[str]:
    return [RAW_NUMERIC[k] for k in feat_keys]


def disparate_impact_gap(X: pd.DataFrame, y: np.ndarray, race: pd.Series,
                         feat_keys: list[str], rng: int = 0) -> dict:
    """Train a model on feat_keys, return grant-rate gap (White - Black) on
    cross-validated predictions, plus the model's accuracy AUC."""
    if not feat_keys:  # bare: predict base rate
        pred = np.full(len(y), y.mean())
    else:
        cols = _cols(feat_keys)
        Xs = X[cols].copy()
        # simple median impute (probe-grade)
        Xs = Xs.fillna(Xs.median())
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=1000, random_state=rng))
        pred = cross_val_predict(clf, Xs, y, cv=5, method="predict_proba")[:, 1]

    # grant-rate gap between groups: mean predicted grant prob
    w = race == "White"
    b = race == "Black or African American"
    gap = pred[w.values].mean() - pred[b.values].mean()
    auc = roc_auc_score(y, pred) if feat_keys else 0.5
    return {"gap": float(gap), "model_auc": float(auc)}


def proxy_strength(X: pd.DataFrame, race: pd.Series, feat_keys: list[str],
                   rng: int = 0) -> float:
    """AUC(race ~ S): how well the admissible set S reconstructs race
    (White=0, Black=1 among the two-group subset)."""
    if not feat_keys:
        return 0.5
    sub = race.isin(["White", "Black or African American"])
    cols = _cols(feat_keys)
    Xs = X.loc[sub, cols].copy().fillna(X[cols].median())
    g = (race[sub] == "Black or African American").astype(int).values
    if g.sum() == 0 or g.sum() == len(g):
        return 0.5
    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(max_iter=1000, random_state=rng))
    p = cross_val_predict(clf, Xs, g, cv=5, method="predict_proba")[:, 1]
    return float(roc_auc_score(g, p))


def main():
    df = load()
    # restrict to the two-group disparate-impact contrast for gap computation
    two = df[df["race"].isin(["White", "Black or African American"])].reset_index(drop=True)
    # drop rows with no DTI (the most-missing core feature) to keep it honest
    two = two.dropna(subset=["debt_to_income_ratio"]).reset_index(drop=True)
    y = two["label"].values
    race = two["race"]
    print(f"n={len(two)}  White={int((race=='White').sum())}  "
          f"Black={int((race=='Black or African American').sum())}  "
          f"base grant rate={y.mean():.3f}")
    print(f"raw grant-rate gap (White-Black, observed): "
          f"{two.loc[race=='White','label'].mean() - two.loc[race=='Black or African American','label'].mean():+.4f}")
    print()

    # baselines for bisg - bare
    bare = disparate_impact_gap(two, y, race, BARE)
    proxy = disparate_impact_gap(two, y, race, PROXY_ONLY)
    bisg_minus_bare = proxy["gap"] - bare["gap"]
    print(f"BARE gap                = {bare['gap']:+.4f}")
    print(f"PROXY-ONLY gap          = {proxy['gap']:+.4f}  "
          f"(proxy_strength={proxy_strength(two, race, PROXY_ONLY):.3f})")
    print(f"bisg - bare             = {bisg_minus_bare:+.4f}   <-- the thing the pivot must beat")
    print()

    rows = []
    for name, fk in FEATURE_SETS.items():
        g = disparate_impact_gap(two, y, race, fk)
        ps = proxy_strength(two, race, fk)
        rows.append({"set": name, "gap": g["gap"], "model_auc": g["model_auc"],
                     "proxy_strength": ps, "n_feat": len(fk)})
    res = pd.DataFrame(rows).sort_values("proxy_strength").reset_index(drop=True)
    pd.set_option("display.float_format", lambda v: f"{v:+.4f}")
    print("ADMISSIBLE FEATURE-SET CHOICES (sorted by proxy_strength):")
    print(res.to_string(index=False))
    print()

    # THE LEVER: spread of gap across defensible choices
    lever = res["gap"].max() - res["gap"].min()
    print(f"LEVER (max gap - min gap across defensible admissible sets) = {lever:+.4f}")
    print()

    # THE KILL TEST: is gap monotone in proxy_strength?
    # If yes -> lever is just proxy_strength relabeled.
    # Look for sets at SIMILAR proxy_strength with DIFFERENT gaps.
    rho = res[["proxy_strength", "gap"]].corr(method="spearman").iloc[0, 1]
    print(f"Spearman(proxy_strength, gap) = {rho:+.3f}")
    print("  near +1.00 -> gap is a readout of proxy_strength -> PIVOT DEAD (bisg-bare relabeled)")
    print("  weak/scattered -> discretion moves gap independently -> LEVER REAL")
    print()
    # explicit similar-ps / different-gap probe
    res["ps_round"] = (res["proxy_strength"] * 20).round() / 20
    for psr, grp in res.groupby("ps_round"):
        if len(grp) > 1:
            spread = grp["gap"].max() - grp["gap"].min()
            print(f"  sets at proxy_strength~{psr:.2f}: gap spread = {spread:+.4f} "
                  f"({', '.join(grp['set'])})")


if __name__ == "__main__":
    main()
