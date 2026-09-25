"""Freeze the lender's archived data frame for the retention-drift gate (pre-reg dc12f1a §4).

Runs once, in the project env. Output is plain .npy + JSON so every vintage (numpy 1.21 .. 2.4)
reads the same bytes. Nothing here depends on a vintage.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 20260925
N_TRAIN, N_EVAL, N_BG = 40000, 1000, 100
FEATURES = ["loan_amnt", "term_months", "annual_inc", "dti", "fico_range_low",
            "credit_age_months", "emp_length_yrs", "home_own_code", "verification_code",
            "purpose_code", "delinq_2yrs", "inq_last_6mths", "open_acc", "pub_rec",
            "revol_bal", "revol_util", "total_acc", "mort_acc", "num_actv_rev_tl", "bc_util",
            "pct_tl_nvr_dlq", "acc_open_past_24mths", "avg_cur_bal", "pub_rec_bankruptcies"]
RAW = ["loan_amnt", "term", "annual_inc", "dti", "fico_range_low", "earliest_cr_line", "issue_d",
       "emp_length", "home_ownership", "verification_status", "purpose", "delinq_2yrs",
       "inq_last_6mths", "open_acc", "pub_rec", "revol_bal", "revol_util", "total_acc", "mort_acc",
       "num_actv_rev_tl", "bc_util", "pct_tl_nvr_dlq", "acc_open_past_24mths", "avg_cur_bal",
       "pub_rec_bankruptcies", "loan_status"]
# Fixed code tables (not pandas category codes, which depend on the sample).
HOME = {"RENT": 0, "MORTGAGE": 1, "OWN": 2}
VERIF = {"Not Verified": 0, "Source Verified": 1, "Verified": 2}
PURPOSES = ["debt_consolidation", "credit_card", "home_improvement", "other", "major_purchase",
            "medical", "small_business", "car", "vacation", "moving", "house", "wedding",
            "renewable_energy", "educational"]


def emp_years(s):
    if not isinstance(s, str):
        return np.nan
    if s.startswith("<"):
        return 0.0
    return float(s.split()[0].rstrip("+"))


def main():
    root = Path(__file__).resolve().parents[2]
    df = pd.read_csv(root / "data/accepted_2007_to_2018Q4.csv", usecols=RAW, low_memory=False)
    df = df[df.loan_status.isin(["Fully Paid", "Charged Off", "Default"])].copy()
    df["y"] = (df.loan_status != "Fully Paid").astype(int)
    df["term_months"] = df.term.astype(str).str.extract(r"(\d+)")[0].astype(float)
    iss = pd.to_datetime(df.issue_d, format="%b-%Y", errors="coerce")
    ecl = pd.to_datetime(df.earliest_cr_line, format="%b-%Y", errors="coerce")
    df["credit_age_months"] = (iss - ecl).dt.days / 30.44
    df["emp_length_yrs"] = df.emp_length.map(emp_years)
    df["home_own_code"] = df.home_ownership.map(HOME)
    df["verification_code"] = df.verification_status.map(VERIF)
    df["purpose_code"] = df.purpose.map({p: i for i, p in enumerate(PURPOSES)})
    df = df.dropna(subset=FEATURES + ["y"])
    df = df.sample(n=N_TRAIN + N_EVAL, random_state=SEED)
    X = df[FEATURES].to_numpy(dtype=np.float64)
    y = df["y"].to_numpy(dtype=np.int64)
    X_eval, X_train, y_train = X[:N_EVAL], X[N_EVAL:], y[N_EVAL:]
    rng = np.random.RandomState(SEED)
    bg = X_train[rng.choice(len(X_train), N_BG, replace=False)]
    bg_alt = X_train[np.random.RandomState(SEED + 1).choice(len(X_train), N_BG, replace=False)]
    out = root / "runs/retention_drift/frame"
    out.mkdir(parents=True, exist_ok=True)
    for name, arr in [("X_train", X_train), ("y_train", y_train), ("X_eval", X_eval),
                      ("background", bg), ("background_alt", bg_alt)]:
        np.save(out / f"{name}.npy", arr)
    json.dump({"features": FEATURES, "seed": SEED, "n_train": len(X_train), "n_eval": len(X_eval),
               "default_rate_train": float(y_train.mean()), "prereg": "dc12f1a"},
              open(out / "frame.json", "w"), indent=2)
    print(f"train {X_train.shape} default {y_train.mean():.3f}; eval {X_eval.shape}")


if __name__ == "__main__":
    main()
