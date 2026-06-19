#!/usr/bin/env python3
"""LC-grading arm: REFUTATION re-run of the wide-ceiling claim (0.1593).

Blind adversary. The arm claims steered selection opens a wide age-disparity gap an
accuracy audit can't see, on LC's richer proxy space. Default to REFUTED. Built-in
attacks on the four named artifacts:

  (a) lawful-covariate LEAK: does the wide gap survive when the age_score is forced
      orthogonal to the lawful default-risk signal? (HMDA mistake = age_score predicts
      Y alone). Report AUC(Y~age_score alone) and re-measure ceiling on residualized score.
  (b) imputed-age circularity: est_age is DERIVED from earliest_cr_line, which is also a
      proxy feature. If the steering target uses est_age and the band features include
      credit-history-length, "proxies predict age-disparity" is partly tautological.
      ATTACK: drop earliest_cr_line / credit-history-derived features from the proxy pool
      and re-measure; report ceiling with and without the circular feature.
  (c) eps not a genuine tie: the report measures ceiling in PERCENTILE-RANK units, not a
      decision rate. ATTACK: report the ceiling in (i) rank units (their metric) AND
      (ii) actual GRANT-RATE / decision-disparity units (apples-to-apples with HMDA's
      0.014), at eps=0.005,0.01,0.02 on held-out AUC. A rank-unit "gap" is mechanically
      inflated and NOT comparable to the HMDA anchor.
  (d) class imbalance / threshold: default base rate ~0.2; report disparity at the
      natural operating point AND confirm AUC ties are real on held-out test.
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

RNG = 20260612
CSV = "data/accepted_2007_to_2018Q4.csv"

# Proxy pool. credit_hist_len is the CIRCULAR feature (est_age derives from it).
CAT_PROXIES = ["home_ownership", "purpose", "addr_state"]
NUM_PROXIES_CLEAN = ["emp_length_num", "dti", "annual_inc", "loan_amnt", "term_num", "fico_range_low"]
CIRCULAR = ["credit_hist_len"]  # = issue_d - earliest_cr_line, i.e. est_age - 18
NUM_PROXIES = NUM_PROXIES_CLEAN + CIRCULAR
LAWFUL = ["annual_inc", "dti", "fico_range_low", "loan_amnt", "term_num"]


def load(n_sample=None):
    cols = ["loan_amnt", "term", "int_rate", "grade", "sub_grade", "emp_length",
            "home_ownership", "annual_inc", "issue_d", "loan_status", "purpose",
            "addr_state", "dti", "earliest_cr_line", "fico_range_low"]
    df = pd.read_csv(CSV, usecols=cols, low_memory=False)
    df = df[df["loan_status"].isin(["Fully Paid", "Charged Off"])].copy()
    df["Y"] = (df["loan_status"] == "Charged Off").astype(int)  # default = 1
    issue = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
    earliest = pd.to_datetime(df["earliest_cr_line"], format="%b-%Y", errors="coerce")
    df["credit_hist_len"] = (issue - earliest).dt.days / 365.25
    df["est_age"] = 18.0 + df["credit_hist_len"]
    df["term_num"] = df["term"].str.extract(r"(\d+)").astype(float)
    el = df["emp_length"].replace({"< 1 year": "0", "10+ years": "10"}, regex=False)
    df["emp_length_num"] = el.str.extract(r"(\d+)").astype(float)
    df["int_rate"] = pd.to_numeric(df["int_rate"].astype(str).str.replace("%", "", regex=False), errors="coerce")
    df = df.dropna(subset=["est_age", "int_rate", "Y"]).copy()
    df = df[(df["est_age"] >= 18) & (df["est_age"] <= 95)].copy()
    # G = top age quartile (older direction), per the arm's definition.
    thr = df["est_age"].quantile(0.75)
    df["G"] = (df["est_age"] >= thr).astype(int)  # 1 = older
    if n_sample and len(df) > n_sample:
        df = df.sample(n=n_sample, random_state=RNG).reset_index(drop=True)
    return df


def make_pre(cat_f, num_f):
    t = []
    if cat_f:
        t.append(("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                                   ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=50))]), cat_f))
    if num_f:
        t.append(("num", SimpleImputer(strategy="median"), num_f))
    return ColumnTransformer(t)


def gbt(seed=RNG, **kw):
    d = dict(random_state=seed, n_estimators=120, max_depth=3, learning_rate=0.08)
    d.update(kw)
    return GradientBoostingClassifier(**d)


def auc_holdout(Xtr, Xte, ytr, yte, cat, num):
    pipe = Pipeline([("pre", make_pre(cat, num)), ("clf", gbt())]).fit(Xtr[cat + num], ytr)
    return roc_auc_score(yte, pipe.predict_proba(Xte[cat + num])[:, 1])


def steered_band(Xtr, Xte, ytr, yte, Gte, pool_cat, pool_num, *, target,
                 n_models=60, seed=RNG):
    """Build many AUC(Y)-tied models on random feature subsets; for each, record
    held-out AUC(Y) and BOTH disparity metrics (rank-units and decision-rate units).
    `target` is the column the models are fit to (Y, or steered Y+lam*agez)."""
    rng = np.random.default_rng(seed)
    pool = pool_cat + pool_num
    base_rate = float(yte.mean())
    members = []
    for _ in range(n_models):
        m = int(rng.integers(3, len(pool) + 1))
        idx = rng.choice(len(pool), size=m, replace=False)
        feats = [pool[i] for i in idx]
        cat_f = [c for c in feats if c in pool_cat]
        num_f = [c for c in feats if c in pool_num]
        clf = GradientBoostingClassifier(
            random_state=int(rng.integers(1_000_000)),
            n_estimators=int(rng.choice([80, 120, 160])),
            max_depth=int(rng.choice([2, 3, 4])),
            learning_rate=float(rng.choice([0.05, 0.08, 0.12])))
        pipe = Pipeline([("pre", make_pre(cat_f, num_f)), ("clf", clf)]).fit(Xtr[feats], target)
        p = pipe.predict_proba(Xte[feats])[:, 1]
        # held-out AUC always measured against TRUE Y (the audit metric)
        auc = roc_auc_score(yte, p)
        # decision-rate disparity at natural operating point (deny worst base_rate frac)
        thr = np.quantile(p, 1 - base_rate)
        deny = (p >= thr).astype(int)
        disp_rate = deny[Gte == 1].mean() - deny[Gte == 0].mean()  # older minus younger DENY rate
        # rank-unit disparity (the arm's metric): mean percentile-rank gap
        rank = pd.Series(p).rank(pct=True).values
        disp_rank = rank[Gte == 1].mean() - rank[Gte == 0].mean()
        members.append((auc, disp_rate, disp_rank, tuple(feats)))
    members.sort(key=lambda t: -t[0])
    return members


def report_band(members, label):
    best = members[0][0]
    out = {}
    for eps in (0.005, 0.01, 0.02):
        band = [mm for mm in members if best - mm[0] <= eps]
        rates = np.array([mm[1] for mm in band])
        ranks = np.array([mm[2] for mm in band])
        steered_rate = max(band, key=lambda mm: abs(mm[1]))[1]
        steered_rank = max(band, key=lambda mm: abs(mm[2]))[2]
        out[eps] = dict(n=len(band), auc_lo=min(mm[0] for mm in band), auc_hi=best,
                        ceiling_rate=steered_rate, ceiling_rank=steered_rank,
                        spread_rate=rates.max() - rates.min(),
                        spread_rank=ranks.max() - ranks.min())
        print(f"  [{label}] eps={eps:<5} n={len(band):<3} AUC[{min(mm[0] for mm in band):.4f},{best:.4f}] "
              f"CEILING rate={steered_rate:+.4f} rank={steered_rank:+.4f} "
              f"spread_rate={rates.max()-rates.min():.4f} spread_rank={ranks.max()-ranks.min():.4f}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300000)
    ap.add_argument("--lam", type=float, default=2.0, help="steering strength toward age")
    args = ap.parse_args()

    df = load(args.n)
    n = len(df)
    print(f"N={n}  P(older=G1)={df['G'].mean():.3f}  default_rate={df['Y'].mean():.3f}  "
          f"older_def={df.loc[df.G==1,'Y'].mean():.4f}  younger_def={df.loc[df.G==0,'Y'].mean():.4f}")
    print(f"corr(est_age,default)={np.corrcoef(df['est_age'],df['Y'])[0,1]:+.4f}  "
          f"corr(est_age,int_rate)={np.corrcoef(df['est_age'],df['int_rate'])[0,1]:+.4f}")

    tr, te = train_test_split(df, test_size=0.3, random_state=RNG, stratify=df["Y"])
    tr = tr.copy(); te = te.copy()

    # (1) AUC(G ~ proxy) WITH and WITHOUT the circular feature
    g_auc_full = auc_holdout(tr, te, tr["G"].values, te["G"].values, CAT_PROXIES, NUM_PROXIES)
    g_auc_clean = auc_holdout(tr, te, tr["G"].values, te["G"].values, CAT_PROXIES, NUM_PROXIES_CLEAN)
    print(f"\n(1) AUC(G~proxy) full(+credit_hist)={g_auc_full:.4f}  clean(no credit_hist)={g_auc_clean:.4f}")

    # (2) double dissociation: age_score alone + marginal. age_score built from proxies.
    age_model = Pipeline([("pre", make_pre(CAT_PROXIES, NUM_PROXIES)), ("clf", gbt())]).fit(
        tr[CAT_PROXIES + NUM_PROXIES], tr["G"])
    tr["age_score"] = age_model.predict_proba(tr[CAT_PROXIES + NUM_PROXIES])[:, 1]
    te["age_score"] = age_model.predict_proba(te[CAT_PROXIES + NUM_PROXIES])[:, 1]

    def yauc(cols, trf=tr, tef=te):
        pipe = Pipeline([("pre", ColumnTransformer([("num", SimpleImputer(strategy="median"), cols)])),
                         ("clf", gbt())]).fit(trf[cols], trf["Y"])
        return roc_auc_score(tef["Y"], pipe.predict_proba(tef[cols])[:, 1])

    y_lawful = yauc(LAWFUL)
    y_lawful_age = yauc(LAWFUL + ["age_score"])
    y_age_alone = yauc(["age_score"])
    print(f"\n(2) dissociation:")
    print(f"    AUC(Y ~ age_score ALONE)     = {y_age_alone:.4f}   <-- if >0.53, age_score LEAKS lawful risk")
    print(f"    AUC(Y ~ lawful)              = {y_lawful:.4f}")
    print(f"    AUC(Y ~ lawful + age_score)  = {y_lawful_age:.4f}")
    print(f"    age marginal to Y            = {y_lawful_age - y_lawful:+.4f}")

    # ATTACK (a): residualize age_score against the lawful signal, re-check it still
    # carries G. Build lawful default-score, regress age_score on it, take residual.
    lawpipe = Pipeline([("pre", ColumnTransformer([("num", SimpleImputer(strategy="median"), LAWFUL)])),
                        ("clf", gbt())]).fit(tr[LAWFUL], tr["Y"])
    tr["risk_score"] = lawpipe.predict_proba(tr[LAWFUL])[:, 1]
    te["risk_score"] = lawpipe.predict_proba(te[LAWFUL])[:, 1]
    lr = LinearRegression().fit(tr[["risk_score"]], tr["age_score"])
    te["age_resid"] = te["age_score"] - lr.predict(te[["risk_score"]])
    auc_g_resid = roc_auc_score(te["G"], te["age_resid"])
    print(f"    AUC(G ~ age_score residualized of risk) = {auc_g_resid:.4f}  "
          f"(if ~AUC(G~age_score), the G signal is NOT a lawful-risk leak)")
    auc_g_raw = roc_auc_score(te["G"], te["age_score"])
    print(f"    AUC(G ~ age_score raw)                  = {auc_g_raw:.4f}")

    # (3) STEERED band -- four configurations:
    #   A. honest (target=Y), full pool (incl circular)
    #   B. STEERED (target=Y + lam*agez), full pool   <- the arm's wide claim
    #   C. STEERED, CLEAN pool (no credit_hist)       <- attack (b) circularity
    print(f"\n(3) STEERED band (lam={args.lam}):")
    ytr = tr["Y"].values; yte = te["Y"].values; Gte = te["G"].values
    agez_tr = ((tr["est_age"] - tr["est_age"].mean()) / tr["est_age"].std()).values
    steer_target = (ytr.astype(float) + args.lam * agez_tr)
    # binarize steered target for a classifier (keep it a ranking by thresholding at its mean)
    steer_bin = (steer_target >= np.quantile(steer_target, 1 - ytr.mean())).astype(int)

    print(" honest (target=Y), full pool:")
    mb_honest = steered_band(tr, te, ytr, yte, Gte, CAT_PROXIES, NUM_PROXIES, target=ytr)
    r_honest = report_band(mb_honest, "honest-full")

    print(" STEERED (target=Y+lam*agez), full pool [the arm's claim]:")
    mb_steer = steered_band(tr, te, steer_bin, yte, Gte, CAT_PROXIES, NUM_PROXIES, target=steer_bin)
    r_steer = report_band(mb_steer, "steered-full")

    print(" STEERED, CLEAN pool (drop credit_hist_len = attack circularity):")
    mb_clean = steered_band(tr, te, steer_bin, yte, Gte, CAT_PROXIES, NUM_PROXIES_CLEAN, target=steer_bin)
    r_clean = report_band(mb_clean, "steered-clean")

    # (4) RFOA: raw and lawful-adjusted disparity in DENY-rate units
    dfc = df.dropna(subset=LAWFUL).copy()
    for q, src in [("inc_q", "annual_inc"), ("dti_q", "dti"), ("fico_q", "fico_range_low")]:
        dfc[q] = pd.qcut(dfc[src].rank(method="first"), 5, labels=False, duplicates="drop")
    raw = dfc.loc[dfc.G == 1, "Y"].mean() - dfc.loc[dfc.G == 0, "Y"].mean()
    def adj(strata):
        s = dfc.groupby(strata, observed=True).apply(lambda g: pd.Series({
            "gap": (g.loc[g.G == 1, "Y"].mean() - g.loc[g.G == 0, "Y"].mean()) if (g.G == 0).any() and (g.G == 1).any() else np.nan,
            "w": ((g.G == 0).any() and (g.G == 1).any()) * len(g)}), include_groups=False).dropna(subset=["gap"])
        return float(np.average(s["gap"], weights=s["w"])) if len(s) else np.nan
    print(f"\n(4) RFOA (default-rate gap older-younger): raw={raw:+.4f} adj(inc x dti x fico)={adj(['inc_q','dti_q','fico_q']):+.4f}")

    print("\n" + "=" * 78)
    print("REFUTATION SUMMARY")
    print(f"  steered ceiling @eps=.01  RANK units = {r_steer[0.01]['ceiling_rank']:+.4f}  (the arm's 0.1593)")
    print(f"  steered ceiling @eps=.01  RATE units = {r_steer[0.01]['ceiling_rate']:+.4f}  <-- apples-to-apples w/ HMDA 0.014")
    print(f"  honest  ceiling @eps=.01  RATE units = {r_honest[0.01]['ceiling_rate']:+.4f}  (no steering baseline)")
    print(f"  steered-CLEAN ceiling@.01 RATE units = {r_clean[0.01]['ceiling_rate']:+.4f}  (circular feature removed)")
    print(f"  age_score Y-alone AUC = {y_age_alone:.4f} | age marginal = {y_lawful_age-y_lawful:+.4f} | "
          f"G-from-resid AUC = {auc_g_resid:.4f}")


if __name__ == "__main__":
    main()
