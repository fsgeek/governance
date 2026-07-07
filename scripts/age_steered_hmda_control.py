#!/usr/bin/env python3
"""HMDA-RI 2022 CONTROL arm: steered Rashomon band + double-dissociation honesty.

Reproduces the ~0.10 disparity ceiling anchor. Key forensic additions over
age_double_dissociation.py:
  - AUC(Y ~ age_score ALONE) reported explicitly (the HMDA mistake guard).
  - The Rashomon band is STEERED: we EXPLICITLY SELECT the accuracy-tied member
    that MAXIMIZES |age disparity|, and report the disparity CEILING (most-disparate
    member's gap) at eps = 0.005, 0.01, 0.02 -- the key cross-arm quantity.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

RNG = 20260612
np.random.seed(RNG)
PARQUET = "data/hmda/processed/hmda_2022_RI.parquet"

CAT_PROXIES = ["loan_purpose", "occupancy_type", "derived_msa-md"]
NUM_PROXIES = ["loan_term", "income", "property_value", "loan_to_value_ratio",
               "tract_median_age_of_housing_units"]
PROXIES = CAT_PROXIES + NUM_PROXIES
LAWFUL = ["income", "loan_to_value_ratio", "property_value", "loan_term"]


def load():
    df = pd.read_parquet(PARQUET)
    df = df[df["action_taken"].isin([1, 3])].copy()
    df["Y"] = (df["action_taken"] == 1).astype(int)
    df = df[df["applicant_age_above_62"].isin(["Yes", "No"])].copy()
    df["G"] = (df["applicant_age_above_62"] == "Yes").astype(int)
    for c in NUM_PROXIES:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def gbt(**kw):
    d = dict(random_state=RNG, n_estimators=150, max_depth=3, learning_rate=0.08)
    d.update(kw)
    return GradientBoostingClassifier(**d)


def make_pre(cat_f, num_f):
    t = []
    if cat_f:
        t.append(("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                                   ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=20))]), cat_f))
    if num_f:
        t.append(("num", SimpleImputer(strategy="median"), num_f))
    return ColumnTransformer(t)


def auc_cv(df, target, cat, num, factory, n=5):
    X = df[cat + num]; y = df[target].values; aucs = []
    for i in range(n):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=RNG + i, stratify=y)
        pipe = Pipeline([("pre", make_pre(cat, num)), ("clf", factory())]).fit(Xtr, ytr)
        aucs.append(roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1]))
    return float(np.mean(aucs)), float(np.std(aucs))


def main():
    df = load()
    n = len(df)
    bG = df["G"].mean()
    appr = df["Y"].mean()
    ao = df.loc[df.G == 1, "Y"].mean()
    ay = df.loc[df.G == 0, "Y"].mean()
    print(f"N={n}  P(>62)={bG:.3f}  approve={appr:.3f}  >62={ao:.3f}  <=62={ay:.3f}  raw_gap={ay-ao:+.4f}")

    # (1) G reconstruct
    g_auc, g_sd = auc_cv(df, "G", CAT_PROXIES, NUM_PROXIES, gbt)
    print(f"\n(1) AUC(G~proxy) GBT={g_auc:.4f}+/-{g_sd:.4f}")

    # (2) double dissociation -- BUILD age_score, report ALONE + marginal
    Xtr, Xte = train_test_split(df, test_size=0.3, random_state=RNG, stratify=df["Y"])
    Xtr = Xtr.copy(); Xte = Xte.copy()
    age_model = Pipeline([("pre", make_pre(CAT_PROXIES, NUM_PROXIES)), ("clf", gbt())]).fit(Xtr[PROXIES], Xtr["G"])
    Xtr["age_score"] = age_model.predict_proba(Xtr[PROXIES])[:, 1]
    Xte["age_score"] = age_model.predict_proba(Xte[PROXIES])[:, 1]
    g_auc_holdout = roc_auc_score(Xte["G"], Xte["age_score"])

    def yauc(cols):
        pipe = Pipeline([("pre", ColumnTransformer([("num", SimpleImputer(strategy="median"), cols)])),
                         ("clf", gbt())]).fit(Xtr[cols], Xtr["Y"])
        return roc_auc_score(Xte["Y"], pipe.predict_proba(Xte[cols])[:, 1])

    y_lawful = yauc(LAWFUL)
    y_lawful_age = yauc(LAWFUL + ["age_score"])
    y_age_alone = yauc(["age_score"])
    print(f"\n(2) double dissociation:")
    print(f"    AUC(G~age_score) holdout         = {g_auc_holdout:.4f}")
    print(f"    AUC(Y ~ age_score ALONE)         = {y_age_alone:.4f}   <-- HMDA-mistake guard")
    print(f"    AUC(Y ~ lawful)                  = {y_lawful:.4f}")
    print(f"    AUC(Y ~ lawful + age_score)      = {y_lawful_age:.4f}")
    print(f"    age marginal to Y                = {y_lawful_age - y_lawful:+.4f}")
    diss = (abs(y_age_alone - 0.5) < 0.03)
    print(f"    dissociation_real (age alone ~0.5)= {diss}")

    # (4) RFOA control
    dfc = df.dropna(subset=LAWFUL).copy()
    dfc["inc_q"] = pd.qcut(dfc["income"].clip(upper=dfc["income"].quantile(0.99)), 5, labels=False, duplicates="drop")
    dfc["ltv_q"] = pd.qcut(dfc["loan_to_value_ratio"].clip(upper=dfc["loan_to_value_ratio"].quantile(0.99)), 5, labels=False, duplicates="drop")
    dfc["term_q"] = pd.qcut(dfc["loan_term"].rank(method="first"), 3, labels=False, duplicates="drop")
    def adj(strata):
        s = dfc.groupby(strata, observed=True).apply(lambda g: pd.Series({
            "gap": (g.loc[g.G == 0, "Y"].mean() - g.loc[g.G == 1, "Y"].mean()) if (g.G == 0).any() and (g.G == 1).any() else np.nan,
            "w": ((g.G == 0).any() and (g.G == 1).any()) * len(g)}), include_groups=False).dropna(subset=["gap"])
        return float(np.average(s["gap"], weights=s["w"])) if len(s) else np.nan
    raw_gap = ay - ao
    adj_il = adj(["inc_q", "ltv_q"])
    adj_ilt = adj(["inc_q", "ltv_q", "term_q"])
    print(f"\n(4) RFOA control:")
    print(f"    raw gap                          = {raw_gap:+.4f}")
    print(f"    adj (income x LTV)               = {adj_il:+.4f}")
    print(f"    adj (income x LTV x term)        = {adj_ilt:+.4f}   <-- term absorbs?")
    grad = "anti-older" if raw_gap > 0.005 else ("pro-older" if raw_gap < -0.005 else "none")
    print(f"    gradient_direction (lawful)      = {grad}")

    # (3) STEERED band: build many tied models, EXPLICITLY SELECT max |disparity|
    print(f"\n(3) STEERED band (explicitly select max |age disparity| among accuracy-tied):")
    Xtr2, Xte2, ytr2, yte2, Gtr2, Gte2 = train_test_split(
        df[PROXIES], df["Y"].values, df["G"].values, test_size=0.3, random_state=RNG, stratify=df["Y"].values)
    rng = np.random.default_rng(RNG)
    members = []
    for k in range(120):
        m = int(rng.integers(3, len(PROXIES) + 1))
        idx = rng.choice(len(PROXIES), size=m, replace=False)
        feats = [PROXIES[i] for i in idx]
        cat_f = [c for c in feats if c in CAT_PROXIES]
        num_f = [c for c in feats if c in NUM_PROXIES]
        clf = GradientBoostingClassifier(random_state=int(rng.integers(1_000_000)),
                                         n_estimators=int(rng.choice([80, 120, 160])),
                                         max_depth=int(rng.choice([2, 3, 4])),
                                         learning_rate=float(rng.choice([0.05, 0.08, 0.12])))
        pipe = Pipeline([("pre", make_pre(cat_f, num_f)), ("clf", clf)]).fit(Xtr2[feats], ytr2)
        p = pipe.predict_proba(Xte2[feats])[:, 1]
        auc = roc_auc_score(yte2, p)
        thr = np.quantile(p, 1 - yte2.mean())
        decide = (p >= thr).astype(int)
        disp = decide[Gte2 == 0].mean() - decide[Gte2 == 1].mean()  # <=62 minus >62
        members.append((auc, disp, tuple(feats)))
    members.sort(key=lambda t: -t[0])
    best = members[0][0]
    print(f"    {len(members)} models; best AUC(Y)={best:.4f}")
    ceil_01 = None
    for eps in (0.005, 0.01, 0.02):
        band = [mm for mm in members if best - mm[0] <= eps]
        disps = np.array([mm[1] for mm in band])
        # STEERED selection = the member maximizing |disparity|
        steered = max(band, key=lambda mm: abs(mm[1]))
        ceiling = steered[1]
        spread = disps.max() - disps.min()
        if eps == 0.01:
            ceil_01 = ceiling
            spread_01 = spread
        print(f"    eps={eps:<5} band_n={len(band):<3} AUC[{min(mm[0] for mm in band):.4f},{best:.4f}] "
              f"disp[min={disps.min():+.4f} max={disps.max():+.4f}] SPREAD={spread:.4f} "
              f"STEERED_CEILING(|max|)={ceiling:+.4f}")

    print("\n" + "=" * 70)
    print(f"SUMMARY hmda-control:")
    print(f"  auc_g_from_proxy        = {g_auc:.4f}")
    print(f"  auc_y_from_proxy        = {auc_cv(df,'Y',CAT_PROXIES,NUM_PROXIES,gbt)[0]:.4f}")
    print(f"  auc_y_from_agescore_alone = {y_age_alone:.4f}")
    print(f"  age_marginal_to_y       = {y_lawful_age - y_lawful:+.4f}")
    print(f"  dissociation_real       = {diss}")
    print(f"  steered_band_ceiling@.01= {ceil_01:+.4f}")
    print(f"  steered_band_spread@.01 = {spread_01:.4f}")
    print(f"  rfoa_raw_gap            = {raw_gap:+.4f}")
    print(f"  rfoa_adjusted_gap       = {adj_ilt:+.4f}")
    print(f"  rfoa_gradient           = {grad}")


if __name__ == "__main__":
    main()
