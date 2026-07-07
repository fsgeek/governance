#!/usr/bin/env python3
"""Age double-dissociation probe on HMDA-RI 2022 (age OBSERVED -> checkable).

Pre-registration: docs/superpowers/specs/2026-06-12-age-double-dissociation-prereg.md

Three measured quantities settle the cookbook thesis spine:
  (1) AUC(G ~ transferable proxies)      G = applicant_age_above_62   -> does age reconstruct?
  (2) AUC(Y ~ same proxies) + age-channel partial contribution        -> is the approve/deny audit blind to age?
  (3) steered Rashomon band gap in age-disparity, models tied on AUC(Y) -> is harm chosen at SELECTION?
  (4) RFOA control: disparity before/after lawful covariates           -> does the alibi explain it?

reverse_mortgage and the age label itself are EXCLUDED as non-transferable cheats.
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

# Transferable proxies (exist in FNMAE/LC too) — the HONEST set. No reverse_mortgage, no age, no race/sex.
CAT_PROXIES = ["loan_purpose", "occupancy_type", "derived_msa-md"]
NUM_PROXIES = ["loan_term", "income", "property_value", "loan_to_value_ratio",
               "tract_median_age_of_housing_units"]
PROXIES = CAT_PROXIES + NUM_PROXIES

# Lawful covariates for the RFOA control (genuine business-necessity content)
LAWFUL = ["income", "loan_to_value_ratio", "property_value", "loan_term"]


def load():
    df = pd.read_parquet(PARQUET)
    # Y: originated(1) vs denied(3) only
    df = df[df["action_taken"].isin([1, 3])].copy()
    df["Y"] = (df["action_taken"] == 1).astype(int)
    # G: age above 62 (drop unknown)
    df = df[df["applicant_age_above_62"].isin(["Yes", "No"])].copy()
    df["G"] = (df["applicant_age_above_62"] == "Yes").astype(int)
    # numeric coercion
    for c in NUM_PROXIES:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # loan_to_value_ratio sometimes has odd strings; property_value too
    return df


def make_pipe(clf):
    pre = ColumnTransformer([
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=20))]), CAT_PROXIES),
        ("num", SimpleImputer(strategy="median"), NUM_PROXIES),
    ])
    return Pipeline([("pre", pre), ("clf", clf)])


def auc_cv(df, target, cols_cat, cols_num, clf_factory, n=5):
    """Held-out AUC, averaged over n splits."""
    X = df[cols_cat + cols_num]
    y = df[target].values
    aucs = []
    for i in range(n):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=RNG + i, stratify=y)
        pre = ColumnTransformer([
            ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                              ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=20))]), cols_cat),
            ("num", SimpleImputer(strategy="median"), cols_num),
        ])
        pipe = Pipeline([("pre", pre), ("clf", clf_factory())])
        pipe.fit(Xtr, ytr)
        p = pipe.predict_proba(Xte)[:, 1]
        aucs.append(roc_auc_score(yte, p))
    return np.mean(aucs), np.std(aucs)


def gbt():
    return GradientBoostingClassifier(random_state=RNG, n_estimators=150, max_depth=3, learning_rate=0.08)


def lr():
    return LogisticRegression(max_iter=2000, C=1.0)


def main():
    df = load()
    n = len(df)
    base_rate_G = df["G"].mean()
    approve_overall = df["Y"].mean()
    approve_old = df.loc[df["G"] == 1, "Y"].mean()
    approve_young = df.loc[df["G"] == 0, "Y"].mean()
    print(f"N={n}  P(age>62)={base_rate_G:.3f}  approve overall={approve_overall:.3f}")
    print(f"  raw approval: >62={approve_old:.3f}  <=62={approve_young:.3f}  "
          f"raw disparity={approve_young - approve_old:+.3f}")

    # ---- (1) does G reconstruct from transferable proxies? ----
    g_auc, g_sd = auc_cv(df, "G", CAT_PROXIES, NUM_PROXIES, gbt)
    g_auc_lr, _ = auc_cv(df, "G", CAT_PROXIES, NUM_PROXIES, lr)
    print(f"\n(1) AUC(G ~ transferable proxies): GBT={g_auc:.3f}±{g_sd:.3f}  LR={g_auc_lr:.3f}")
    print(f"    [pre-reg P1: expect 0.62-0.74; collapse if <0.58]")

    # ---- (2) does the approve/deny audit see the proxies? ----
    y_auc, y_sd = auc_cv(df, "Y", CAT_PROXIES, NUM_PROXIES, gbt)
    print(f"\n(2) AUC(Y=action_taken ~ same proxies): GBT={y_auc:.3f}±{y_sd:.3f}")

    # age-channel partial contribution to Y:
    # build the proxy->G predictor, take its score as the "age direction",
    # ask how much that single direction adds to Y-fit beyond lawful covariates.
    # Operationalize: AUC(Y ~ lawful) vs AUC(Y ~ lawful + age_score)
    Xtr, Xte = train_test_split(df, test_size=0.3, random_state=RNG, stratify=df["Y"])
    # fit age-score on train
    pre_g = ColumnTransformer([
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=20))]), CAT_PROXIES),
        ("num", SimpleImputer(strategy="median"), NUM_PROXIES),
    ])
    age_model = Pipeline([("pre", pre_g), ("clf", gbt())]).fit(Xtr[PROXIES], Xtr["G"])
    for part in (Xtr, Xte):
        part["age_score"] = age_model.predict_proba(part[PROXIES])[:, 1]

    def y_auc_with(cols_num):
        pre = ColumnTransformer([("num", SimpleImputer(strategy="median"), cols_num)])
        pipe = Pipeline([("pre", pre), ("clf", gbt())]).fit(Xtr[cols_num], Xtr["Y"])
        return roc_auc_score(Xte["Y"], pipe.predict_proba(Xte[cols_num])[:, 1])

    y_lawful = y_auc_with(LAWFUL)
    y_lawful_plus_age = y_auc_with(LAWFUL + ["age_score"])
    print(f"    AUC(Y ~ lawful covariates)        = {y_lawful:.3f}")
    print(f"    AUC(Y ~ lawful + reconstructed-age)= {y_lawful_plus_age:.3f}")
    print(f"    age-channel marginal to Y         = {y_lawful_plus_age - y_lawful:+.4f}")
    print(f"    [dissociation: age_score reconstructs G well but adds ~0 to Y]")

    # ---- (4) RFOA control: disparity before/after lawful covariates ----
    # stratified: within income/LTV/term bins, does the >62 approval gap persist?
    dfc = df.dropna(subset=LAWFUL).copy()
    dfc["inc_q"] = pd.qcut(dfc["income"].clip(upper=dfc["income"].quantile(0.99)), 5, labels=False, duplicates="drop")
    dfc["ltv_q"] = pd.qcut(dfc["loan_to_value_ratio"].clip(upper=dfc["loan_to_value_ratio"].quantile(0.99)),
                           5, labels=False, duplicates="drop")
    strat = dfc.groupby(["inc_q", "ltv_q"], observed=True).apply(
        lambda g: pd.Series({
            "n": len(g),
            "gap": (g.loc[g.G == 0, "Y"].mean() - g.loc[g.G == 1, "Y"].mean())
                    if (g.G == 0).any() and (g.G == 1).any() else np.nan,
            "w": ((g.G == 0).any() and (g.G == 1).any()) * len(g),
        }), include_groups=False)
    valid = strat.dropna(subset=["gap"])
    adj_gap = np.average(valid["gap"], weights=valid["w"]) if len(valid) else np.nan
    raw_gap = approve_young - approve_old
    print(f"\n(4) RFOA control (disparity within income x LTV strata):")
    print(f"    raw approval gap (<=62 minus >62) = {raw_gap:+.3f}")
    print(f"    covariate-adjusted gap            = {adj_gap:+.3f}")
    print(f"    [if adj_gap -> 0, RFOA alibi explains it; residual is the forensic target]")

    # ---- (3) steered Rashomon band: models tied on AUC(Y), spread in age-disparity ----
    # Build many approval models (resample features / seeds / regularization),
    # keep those within epsilon AUC of the best, measure spread of >62 approval disparity.
    print(f"\n(3) Steered band (approval models tied on AUC(Y) within eps):")
    Xall = df[PROXIES].copy()
    yall = df["Y"].values
    Gall = df["G"].values
    Xtr2, Xte2, ytr2, yte2, Gtr2, Gte2 = train_test_split(
        Xall, yall, Gall, test_size=0.3, random_state=RNG, stratify=yall)

    members = []
    rng = np.random.default_rng(RNG)
    feature_pool = PROXIES
    for k in range(40):
        # random subset of proxies (>=3), random depth/regularization -> a Rashomon-ish family
        m = int(rng.integers(3, len(feature_pool) + 1))
        idx = rng.choice(len(feature_pool), size=m, replace=False)
        feats = [feature_pool[i] for i in idx]  # plain python str, not numpy str
        cat_f = [c for c in feats if c in CAT_PROXIES]
        num_f = [c for c in feats if c in NUM_PROXIES]
        transformers = []
        if cat_f:
            transformers.append(("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                                                  ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=20))]), cat_f))
        if num_f:
            transformers.append(("num", SimpleImputer(strategy="median"), num_f))
        pre = ColumnTransformer(transformers)
        clf = GradientBoostingClassifier(random_state=int(rng.integers(1000000)),
                                         n_estimators=int(rng.choice([80, 120, 160])),
                                         max_depth=int(rng.choice([2, 3, 4])),
                                         learning_rate=float(rng.choice([0.05, 0.08, 0.12])))
        pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(Xtr2[feats], ytr2)
        p = pipe.predict_proba(Xte2[feats])[:, 1]
        auc = roc_auc_score(yte2, p)
        # approval-rate disparity at a fixed approval threshold (overall approve rate)
        thr = np.quantile(p, 1 - yte2.mean())
        decide = (p >= thr).astype(int)
        disp = decide[Gte2 == 0].mean() - decide[Gte2 == 1].mean()  # <=62 minus >62
        members.append((auc, disp, tuple(feats)))

    members.sort(key=lambda t: -t[0])
    best_auc = members[0][0]
    eps = 0.01
    band = [m for m in members if best_auc - m[0] <= eps]
    disps = np.array([m[1] for m in band])
    print(f"    {len(members)} models built; best AUC(Y)={best_auc:.3f}; "
          f"band(eps={eps})={len(band)} members")
    print(f"    band AUC range: [{min(m[0] for m in band):.3f}, {best_auc:.3f}]  (tied on accuracy)")
    print(f"    age-disparity across band: min={disps.min():+.3f}  max={disps.max():+.3f}  "
          f"SPREAD={disps.max() - disps.min():.3f}")
    print(f"    [pre-reg P3: spread >= 2x noise => harm CHOSEN at selection; collapse if ~0]")

    print("\n" + "=" * 70)
    print("VERDICT CHECK against pre-reg:")
    print(f"  P1 G-reconstructs:  AUC(G~proxy)={g_auc:.3f}  "
          f"{'HOLD' if g_auc >= 0.58 else 'COLLAPSE (ser/estar floor)'}")
    print(f"  P2 Y-blind on age:  age-marginal-to-Y={y_lawful_plus_age - y_lawful:+.4f}  "
          f"{'dissociation' if abs(y_lawful_plus_age - y_lawful) < 0.01 else 'age IS load-bearing'}")
    print(f"  P3 steered gap:     spread={disps.max() - disps.min():.3f}")
    print(f"  P4 RFOA residual:   raw={raw_gap:+.3f} adj={adj_gap:+.3f}")


if __name__ == "__main__":
    main()
