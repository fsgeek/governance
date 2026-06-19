#!/usr/bin/env python3
"""FNMAE 2018Q1 PERFORMANCE arm refutation -- reads cached loan-level parquet.

Tests the four candidate artifacts behind the probe's "ceiling-wide" (-0.281) claim:
  (a) lawful-covariate leak / no dissociation  (age_score predicts Y alone)
  (b) imputed-age CIRCULARITY                  (G is a fn of the proxies => tautology)
  (c) band members not truly accuracy-tied     (eps too loose)
  (d) class-imbalance / threshold + DIRECTION   (pro-older protective != ADEA harm)
"""
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

RNG = 20260612
np.random.seed(RNG)
LOAN = "data/fanniemae.old/2018Q1_loanlevel.parquet"
HMDA = "data/hmda/processed/hmda_2022_RI.parquet"
RESF = open("/tmp/fnmae_refute_results.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    RESF.write(s + "\n"); RESF.flush()


def age_imputer():
    h = pd.read_parquet(HMDA)
    mid = {"<25": 21, "25-34": 29.5, "35-44": 39.5, "45-54": 49.5,
           "55-64": 59.5, "65-74": 69.5, ">74": 80}
    h = h[h["applicant_age"].isin(mid)].copy()
    h["age_mid"] = h["applicant_age"].map(mid)
    feats = ["loan_amount", "loan_term", "debt_to_income_ratio", "loan_to_value_ratio"]
    for c in feats:
        h[c] = pd.to_numeric(h[c], errors="coerce")
    h = h.dropna(subset=feats + ["age_mid"])
    sc = StandardScaler().fit(h[feats].values)
    lr = LinearRegression().fit(sc.transform(h[feats].values), h["age_mid"].values)
    return sc, lr, lr.score(sc.transform(h[feats].values), h["age_mid"].values), feats


def gbt(rng=RNG, **kw):
    d = dict(random_state=rng, n_estimators=120, max_depth=3, learning_rate=0.08)
    d.update(kw)
    return GradientBoostingClassifier(**d)


def main():
    df = pd.read_parquet(LOAN)
    P(f"loans={len(df)}  dlq_rate={df.ever_dlq.mean():.4f}  ce_rate={df.ever_ce.mean():.4f}")

    sc, lr, r2, hf = age_imputer()
    P(f"\nHMDA imputer R^2={r2:.4f}; std-scaled coefs={dict(zip(hf,[round(c,3) for c in lr.coef_]))}")
    P("  -> imputed age = (almost purely) a linear fn of LTV & term")

    fm = df[["upb", "term", "dti", "ltv"]].copy()
    fm.columns = hf  # loan_amount<-upb, loan_term<-term, dti<-dti, ltv<-ltv
    ok = fm.notna().all(axis=1)
    df = df[ok].reset_index(drop=True); fm = fm[ok]
    df["age_imp"] = lr.predict(sc.transform(fm.values))
    P(f"  imputed age p10={df.age_imp.quantile(.1):.1f} p50={df.age_imp.median():.1f} "
          f"p90={df.age_imp.quantile(.9):.1f} max={df.age_imp.max():.1f} "
          f">=62:{(df.age_imp>=62).mean()*100:.2f}%")

    q1, q2 = df.age_imp.quantile([1/3, 2/3])
    g = df[(df.age_imp <= q1) | (df.age_imp >= q2)].copy()
    g["G"] = (g.age_imp >= q2).astype(int)
    Y = "ever_dlq"
    PROX = ["term", "ltv", "cltv", "n_borr", "dti", "fico", "upb"]
    LAWFUL = ["term", "ltv", "dti", "fico", "upb"]
    g = g.dropna(subset=PROX).reset_index(drop=True)
    yo, yy = g.loc[g.G == 1, Y].mean(), g.loc[g.G == 0, Y].mean()
    P(f"\nband n={len(g)}  default older-imp={yo:.4f} younger-imp={yy:.4f} "
          f"raw_gap(young-old)={yy-yo:+.4f}")

    Xtr, Xte = train_test_split(g, test_size=0.3, random_state=RNG, stratify=g["G"])

    def auc(cols, tgt, tr=Xtr, te=Xte):
        imp = SimpleImputer(strategy="median").fit(tr[cols])
        m = gbt().fit(imp.transform(tr[cols]), tr[tgt])
        return roc_auc_score(te[tgt], m.predict_proba(imp.transform(te[cols]))[:, 1])

    # (b) circularity
    g_auc_4 = auc(["upb", "term", "dti", "ltv"], "G")
    g_auc_ltv = auc(["ltv"], "G"); g_auc_term = auc(["term"], "G")
    P(f"\n(b) CIRCULARITY  AUC(G~imputation-inputs{{upb,term,dti,ltv}})={g_auc_4:.4f}  "
          f"AUC(G~LTV)={g_auc_ltv:.4f}  AUC(G~term)={g_auc_term:.4f}")

    # (a) dissociation guard
    Xtr2, Xte2 = Xtr.copy(), Xte.copy()
    Xtr2["age_score"] = Xtr2.age_imp; Xte2["age_score"] = Xte2.age_imp
    y_alone = auc(["age_score"], Y, Xtr2, Xte2)
    y_law = auc(LAWFUL, Y, Xtr2, Xte2)
    y_law_age = auc(LAWFUL + ["age_score"], Y, Xtr2, Xte2)
    diss = abs(y_alone - 0.5) < 0.03
    P(f"\n(a) DISSOCIATION  AUC(Y~age_score ALONE)={y_alone:.4f}  "
          f"AUC(Y~lawful)={y_law:.4f}  AUC(Y~lawful+age)={y_law_age:.4f}  "
          f"marginal={y_law_age-y_law:+.4f}  dissociation_real={diss}")

    # (4) RFOA
    dfc = g.dropna(subset=LAWFUL).copy()
    for cc, qq in [("dq", "dti"), ("lq", "ltv"), ("fq", "fico")]:
        dfc[cc] = pd.qcut(dfc[qq].rank(method="first"), 5, labels=False, duplicates="drop")
    dfc["tq"] = dfc.term.astype(str)
    def adj(strata):
        s = dfc.groupby(strata, observed=True).apply(lambda gg: pd.Series({
            "gap": (gg.loc[gg.G == 0, Y].mean() - gg.loc[gg.G == 1, Y].mean())
                   if (gg.G == 0).any() and (gg.G == 1).any() else np.nan,
            "w": ((gg.G == 0).any() and (gg.G == 1).any()) * len(gg)}),
            include_groups=False).dropna(subset=["gap"])
        return float(np.average(s.gap, weights=s.w)) if len(s) else np.nan
    raw = yy - yo
    a_full = adj(["dq", "lq", "fq", "tq"])
    grad = "anti-older(ADEA-shaped)" if raw > 0.005 else ("pro-older(protective)" if raw < -0.005 else "none")
    P(f"\n(4) RFOA  raw_gap={raw:+.4f}  adj(dti×ltv×fico×term)={a_full:+.4f}  gradient={grad}")

    # (3)+(c)+(d) STEERED band
    sub = g.sample(n=min(40000, len(g)), random_state=RNG)
    Xs, Xt = train_test_split(sub, test_size=0.3, random_state=RNG, stratify=sub["G"])
    yt = Xt[Y].values; Gt = Xt["G"].values
    rng = np.random.default_rng(RNG)
    members = []
    for k in range(150):
        m = int(rng.integers(3, len(PROX) + 1))
        feats = [PROX[i] for i in rng.choice(len(PROX), size=m, replace=False)]
        imp = SimpleImputer(strategy="median").fit(Xs[feats])
        clf = GradientBoostingClassifier(random_state=int(rng.integers(1_000_000)),
              n_estimators=int(rng.choice([60, 80, 100])), max_depth=int(rng.choice([2, 3])),
              learning_rate=float(rng.choice([0.08, 0.12])))
        clf.fit(imp.transform(Xs[feats]), Xs[Y].values)
        if k % 25 == 0:
            P(f"    ...band model {k}")
        p = clf.predict_proba(imp.transform(Xt[feats]))[:, 1]
        a = roc_auc_score(yt, p)
        thr = np.quantile(p, 1 - yt.mean())
        d = (p >= thr).astype(int)
        # POSITIVE disparity = older-imp flagged adverse MORE = ADEA-shaped harm
        disp = d[Gt == 1].mean() - d[Gt == 0].mean()
        members.append((a, disp))
    members.sort(key=lambda t: -t[0])
    best = members[0][0]
    P(f"\n(3) STEERED band ({len(members)} models, best AUC={best:.4f}; "
          f"POSITIVE disp = ADEA-direction harm to older):")
    out = {}
    for eps in (0.005, 0.01, 0.02):
        band = [mm for mm in members if best - mm[0] <= eps]
        disps = np.array([mm[1] for mm in band])
        steered_abs = max(band, key=lambda mm: abs(mm[1]))[1]
        adea_max = disps.max()  # most ADEA-harmful tied member
        out[eps] = (len(band), steered_abs, adea_max, disps.min(), disps.max())
        P(f"    eps={eps:<5} n={len(band):<3} AUC[{min(mm[0] for mm in band):.4f},{best:.4f}] "
              f"disp[{disps.min():+.4f},{disps.max():+.4f}] |max|ceiling={steered_abs:+.4f} "
              f"ADEA-dir(max+)={adea_max:+.4f}")

    P("\n" + "=" * 70)
    P("REFUTATION SUMMARY (FNMAE performance arm):")
    P(f"  (b) circularity AUC(G~4 imputation inputs) = {g_auc_4:.4f}  [G is those proxies]")
    P(f"  (a) dissociation_real = {diss}  (age alone AUC={y_alone:.4f}, marginal={y_law_age-y_law:+.4f})")
    P(f"  (d) lawful gradient = {grad};  RFOA adj gap = {a_full:+.4f}")
    e = out[0.02]
    P(f"  (c) steered |max|ceiling@.02 = {e[1]:+.4f}  ADEA-direction(max+)@.02 = {e[2]:+.4f}")
    P(f"      probe claimed -0.281 (NEGATIVE=pro-older); ADEA-harm requires POSITIVE.")


if __name__ == "__main__":
    main()
