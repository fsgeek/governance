#!/usr/bin/env python3
"""FNMAE 2018Q1 PERFORMANCE arm -- blind-adversary RE-RUN to refute "ceiling-wide".

The probe claims a WIDE steered age-disparity ceiling (-0.281, spread 0.2253) on a
richer proxy space. We re-run and stress-test the four candidate artifacts:
  (a) lawful-covariate leak / collinearity (the HMDA mistake again)
  (b) imputed-age CIRCULARITY -- G is imputed FROM proxies => "proxies predict G" tautological
  (c) band members not truly accuracy-tied (eps too loose)
  (d) class-imbalance / threshold artifact + DIRECTION of the gap (pro-older = no ADEA harm)

Age has NO ground truth in FNMAE. We impute via a LinearRegression fit on HMDA-RI 2022
(applicant_age band midpoints ~ 4 transferable proxies), exactly as the probe described,
then form top/bottom imputed-age tertiles as G. Every "disparity" is against a PROXY tertile.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

RNG = 20260612
np.random.seed(RNG)

FM = "data/fanniemae.old/2018Q1.csv"
HMDA = "data/hmda/processed/hmda_2022_RI.parquet"

# FNMAE field positions (glossary field number; CSV 0-indexed col = field-1)
F = {
    "loan_id": 2, "term": 13, "ltv": 20, "cltv": 21, "n_borr": 22, "dti": 23,
    "fico": 24, "upb": 10, "dlq": 40, "zbcode": 44, "purpose": 27,
}
# Original UPB = field 10. Loan Identifier = field 2.


def load_fnmae(nmax_rows=None):
    """Collapse 23M monthly rows to loan-level: keep origination static fields + ever-default flag."""
    usecols = sorted(set(F.values()))
    names = {v: k for k, v in F.items()}
    cols0 = [c - 1 for c in usecols]  # 0-indexed positions
    chunks = pd.read_csv(FM, sep="|", header=None, usecols=cols0,
                         names=[names[c] for c in usecols],
                         dtype=str, chunksize=3_000_000, nrows=nmax_rows)
    STATIC = ["term", "ltv", "cltv", "n_borr", "dti", "fico", "upb", "purpose"]
    perf_parts = []   # per-chunk loan-level max(serious), max(ce)
    static_parts = []  # per-chunk first-seen static rows
    for ci, ch in enumerate(chunks):
        dlq_n = pd.to_numeric(ch["dlq"], errors="coerce")
        ch["serious"] = (dlq_n >= 3).astype(int)
        ch["ce"] = ch["zbcode"].isin(["03", "09", "02", "15"]).astype(int)
        perf_parts.append(ch.groupby("loan_id", sort=False)[["serious", "ce"]].max())
        static_parts.append(ch.drop_duplicates("loan_id", keep="first")[["loan_id"] + STATIC])
        print(f"    chunk {ci}: rows={len(ch)}", flush=True)
    perf = pd.concat(perf_parts).groupby(level=0).max()  # loan_id index
    static = pd.concat(static_parts).drop_duplicates("loan_id", keep="first").set_index("loan_id")
    df = static.join(perf)
    df = df.rename(columns={"serious": "ever_dlq", "ce": "ever_ce"})
    for c in ["term", "ltv", "cltv", "n_borr", "dti", "fico", "upb"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    print(f"    collapsed loans={len(df)}", flush=True)
    return df.reset_index(drop=True)


def build_age_imputer():
    """Fit LinearRegression: age_midpoint ~ [loan_amount, loan_term, dti, ltv] on HMDA-RI 2022."""
    h = pd.read_parquet(HMDA)
    mid = {"<25": 21, "25-34": 29.5, "35-44": 39.5, "45-54": 49.5,
           "55-64": 59.5, "65-74": 69.5, ">74": 80}
    h = h[h["applicant_age"].isin(mid)].copy()
    h["age_mid"] = h["applicant_age"].map(mid)
    for c in ["loan_amount", "loan_term", "debt_to_income_ratio", "loan_to_value_ratio"]:
        h[c] = pd.to_numeric(h[c], errors="coerce")
    feats = ["loan_amount", "loan_term", "debt_to_income_ratio", "loan_to_value_ratio"]
    h = h.dropna(subset=feats + ["age_mid"])
    X = h[feats].values
    y = h["age_mid"].values
    sc = StandardScaler().fit(X)
    lr = LinearRegression().fit(sc.transform(X), y)
    r2 = lr.score(sc.transform(X), y)
    return sc, lr, r2, feats


def main():
    print("Loading FNMAE 2018Q1 (collapsing monthly -> loan-level)...", flush=True)
    df = load_fnmae()
    n = len(df)
    print(f"  loans={n}  ever_dlq rate={df['ever_dlq'].mean():.4f}  ever_ce rate={df['ever_ce'].mean():.4f}")

    # impute age from HMDA map
    sc, lr, r2, hfeats = build_age_imputer()
    print(f"\nHMDA age-imputer R^2={r2:.4f}  (probe reported 0.056)")
    # FNMAE proxy mapping: loan_amount<-upb, loan_term<-term, dti<-dti, ltv<-ltv
    fm_map = df[["upb", "term", "dti", "ltv"]].copy()
    fm_map.columns = hfeats
    valid = fm_map.notna().all(axis=1)
    df = df[valid].copy()
    fm_map = fm_map[valid]
    df["age_imp"] = lr.predict(sc.transform(fm_map.values))
    print(f"  imputed age p10={df['age_imp'].quantile(.1):.1f} p50={df['age_imp'].median():.1f} "
          f"p90={df['age_imp'].quantile(.9):.1f}  max={df['age_imp'].max():.1f}  "
          f">=62: {(df['age_imp']>=62).mean()*100:.2f}%")

    # G = top vs bottom imputed-age tertile
    q1, q2 = df["age_imp"].quantile([1/3, 2/3])
    df_g = df[(df["age_imp"] <= q1) | (df["age_imp"] >= q2)].copy()
    df_g["G"] = (df_g["age_imp"] >= q2).astype(int)  # older-imputed = 1
    print(f"  older-imp mean age={df_g.loc[df_g.G==1,'age_imp'].mean():.1f}  "
          f"younger-imp mean={df_g.loc[df_g.G==0,'age_imp'].mean():.1f}")

    Y = "ever_dlq"
    df_g[Y] = df_g[Y].astype(int)
    # proxy set for modeling (FNMAE-native, NO age label)
    PROX = ["term", "ltv", "cltv", "n_borr", "dti", "fico", "upb"]
    LAWFUL = ["term", "ltv", "dti", "fico", "upb"]

    # base rates by G
    yo = df_g.loc[df_g.G == 1, Y].mean()
    yy = df_g.loc[df_g.G == 0, Y].mean()
    print(f"\nBase default rate older-imp={yo:.4f}  younger-imp={yy:.4f}  raw_gap(young-old)={yy-yo:+.4f}")

    # ---- (b) CIRCULARITY test: G is a deterministic fn of {upb,term,dti,ltv} ----
    # AUC(G ~ those very 4) MUST be near 1.0 by construction -> tautological.
    dfb = df_g.dropna(subset=PROX).copy()
    Xtr, Xte = train_test_split(dfb, test_size=0.3, random_state=RNG, stratify=dfb["G"])

    def auc(cols, target, tr=Xtr, te=Xte):
        pipe = GradientBoostingClassifier(random_state=RNG, n_estimators=120, max_depth=3, learning_rate=0.08)
        ximp = SimpleImputer(strategy="median").fit(tr[cols])
        pipe.fit(ximp.transform(tr[cols]), tr[target])
        return roc_auc_score(te[target], pipe.predict_proba(ximp.transform(te[cols]))[:, 1])

    g_auc_4 = auc(["upb", "term", "dti", "ltv"], "G")
    g_auc_all = auc(PROX, "G")
    g_auc_ltv = auc(["ltv"], "G")
    g_auc_term = auc(["term"], "G")
    print(f"\n(b) CIRCULARITY: G imputed FROM {{upb,term,dti,ltv}}.")
    print(f"    AUC(G ~ those 4 imputation inputs) = {g_auc_4:.4f}   <-- tautological by construction")
    print(f"    AUC(G ~ all proxies)               = {g_auc_all:.4f}")
    print(f"    AUC(G ~ LTV alone)                 = {g_auc_ltv:.4f}")
    print(f"    AUC(G ~ term alone)                = {g_auc_term:.4f}")

    # ---- (a) lawful leak / no dissociation: age_score predicts Y ALONE? ----
    # age_score := the imputed age itself (continuous) restricted to band data.
    Xtr2, Xte2 = Xtr.copy(), Xte.copy()
    Xtr2["age_score"] = Xtr2["age_imp"]; Xte2["age_score"] = Xte2["age_imp"]
    y_age_alone = auc(["age_score"], Y, Xtr2, Xte2)
    y_lawful = auc(LAWFUL, Y, Xtr2, Xte2)
    y_lawful_age = auc(LAWFUL + ["age_score"], Y, Xtr2, Xte2)
    y_proxy = auc(PROX, Y, Xtr2, Xte2)
    print(f"\n(a) DISSOCIATION guard:")
    print(f"    AUC(Y ~ age_score ALONE) = {y_age_alone:.4f}   <-- HMDA mistake fires if >>0.5")
    print(f"    AUC(Y ~ lawful)          = {y_lawful:.4f}")
    print(f"    AUC(Y ~ lawful+age)      = {y_lawful_age:.4f}")
    print(f"    age marginal to Y        = {y_lawful_age - y_lawful:+.4f}")
    print(f"    AUC(Y ~ all proxies)     = {y_proxy:.4f}")
    diss = abs(y_age_alone - 0.5) < 0.03
    print(f"    dissociation_real        = {diss}")

    # ---- (4) RFOA: gap before/after lawful covariates ----
    dfc = df_g.dropna(subset=LAWFUL).copy()
    for c, q in [("dti_q", "dti"), ("ltv_q", "ltv"), ("fico_q", "fico")]:
        dfc[c] = pd.qcut(dfc[q].rank(method="first"), 5, labels=False, duplicates="drop")
    dfc["term_q"] = dfc["term"].astype(str)
    def adj(strata):
        s = dfc.groupby(strata, observed=True).apply(lambda g: pd.Series({
            "gap": (g.loc[g.G == 0, Y].mean() - g.loc[g.G == 1, Y].mean())
                   if (g.G == 0).any() and (g.G == 1).any() else np.nan,
            "w": ((g.G == 0).any() and (g.G == 1).any()) * len(g)}),
            include_groups=False).dropna(subset=["gap"])
        return float(np.average(s["gap"], weights=s["w"])) if len(s) else np.nan
    raw_gap = yy - yo
    adj_full = adj(["dti_q", "ltv_q", "fico_q", "term_q"])
    print(f"\n(4) RFOA control:")
    print(f"    raw gap (young-old)             = {raw_gap:+.4f}")
    print(f"    adj (dti x ltv x fico x term)   = {adj_full:+.4f}")
    grad = "anti-older(ADEA-shaped)" if raw_gap > 0.005 else ("pro-older(protective)" if raw_gap < -0.005 else "none")
    print(f"    lawful gradient direction       = {grad}")

    # ---- (c)+(d) STEERED band: tied on AUC(Y), select max |disparity|, report DIRECTION ----
    print(f"\n(3) STEERED band (select max |disparity| among accuracy-tied):", flush=True)
    sub = dfb.sample(n=min(60000, len(dfb)), random_state=RNG)
    Xs, Xt = train_test_split(sub, test_size=0.3, random_state=RNG, stratify=sub["G"])
    yt = Xt[Y].values; Gt = Xt["G"].values
    rng = np.random.default_rng(RNG)
    members = []
    base_disp = None
    for k in range(200):
        m = int(rng.integers(3, len(PROX) + 1))
        idx = rng.choice(len(PROX), size=m, replace=False)
        feats = [PROX[i] for i in idx]
        imp = SimpleImputer(strategy="median").fit(Xs[feats])
        clf = GradientBoostingClassifier(random_state=int(rng.integers(1_000_000)),
                                         n_estimators=int(rng.choice([80, 120, 160])),
                                         max_depth=int(rng.choice([2, 3, 4])),
                                         learning_rate=float(rng.choice([0.05, 0.08, 0.12])))
        clf.fit(imp.transform(Xs[feats]), Xs[Y].values)
        p = clf.predict_proba(imp.transform(Xt[feats]))[:, 1]
        a = roc_auc_score(yt, p)
        thr = np.quantile(p, 1 - yt.mean())
        decide = (p >= thr).astype(int)
        # disparity = older-imp adverse-flag rate MINUS younger-imp (POSITIVE = ADEA harm to older)
        disp = decide[Gt == 1].mean() - decide[Gt == 0].mean()
        members.append((a, disp, tuple(feats)))
    members.sort(key=lambda t: -t[0])
    best = members[0][0]
    print(f"    {len(members)} models; best AUC(Y)={best:.4f}")
    print(f"    (disparity sign convention: POSITIVE = older-imp flagged adverse MORE = ADEA-shaped harm)")
    res = {}
    for eps in (0.005, 0.01, 0.02):
        band = [mm for mm in members if best - mm[0] <= eps]
        disps = np.array([mm[1] for mm in band])
        steered = max(band, key=lambda mm: abs(mm[1]))
        ceiling = steered[1]
        # also: max POSITIVE (true ADEA direction) ceiling
        pos_ceiling = max(d for d in disps)
        spread = disps.max() - disps.min()
        res[eps] = (len(band), ceiling, pos_ceiling, spread)
        print(f"    eps={eps:<5} n={len(band):<3} AUC[{min(mm[0] for mm in band):.4f},{best:.4f}] "
              f"|max|ceiling={ceiling:+.4f}  ADEA-dir(max+)={pos_ceiling:+.4f}  spread={spread:.4f}")

    print("\n" + "=" * 70)
    print("REFUTATION SUMMARY:")
    print(f"  (b) circularity AUC(G~4 inputs) = {g_auc_4:.4f}  [near 1.0 => tautological]")
    print(f"  (a) dissociation_real           = {diss}  (age alone AUC={y_age_alone:.4f})")
    print(f"  (d) lawful gradient             = {grad}")
    print(f"      RFOA adj gap                = {adj_full:+.4f}")
    e = res[0.02]
    print(f"  (c) steered |max|ceiling@.02    = {e[1]:+.4f}  ADEA-direction max@.02 = {e[2]:+.4f}")


if __name__ == "__main__":
    main()
