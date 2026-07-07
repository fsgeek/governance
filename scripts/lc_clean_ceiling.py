#!/usr/bin/env python3
"""Decisive follow-up: the TRUE LC age-disparity ceiling after removing the circular
feature, with the band genuinely accuracy-tied to the honest best.

Two cells the refutation run was missing:
  (1) honest target (Y), CLEAN pool (no credit_hist_len): build many models, keep those
      within eps of the BEST honest AUC, EXPLICITLY SELECT the max |deny-rate disparity|.
      This is the LDA-faithful steered band: selection is steered, accuracy is held.
  (2) same but report disparity in deny-RATE units (apples-to-apples with HMDA 0.014).
"""
import numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

RNG = 20260612
import importlib.util
spec = importlib.util.spec_from_file_location("base", "scripts/age_steered_lc_refute.py")
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)

CAT = base.CAT_PROXIES
NUM_CLEAN = base.NUM_PROXIES_CLEAN  # no credit_hist_len

df = base.load(40000)
tr, te = train_test_split(df, test_size=0.3, random_state=RNG, stratify=df["Y"])
ytr, yte, Gte = tr["Y"].values, te["Y"].values, te["G"].values

# honest target, CLEAN pool, but build MORE models so eps-band is well populated
mb = base.steered_band(tr, te, ytr, yte, Gte, CAT, NUM_CLEAN, target=ytr, n_models=80)
best = mb[0][0]
print(f"honest best AUC(Y) clean pool = {best:.4f}")
for eps in (0.005, 0.01, 0.02):
    band = [m for m in mb if best - m[0] <= eps]
    rates = np.array([m[1] for m in band]); ranks = np.array([m[2] for m in band])
    steer_rate = max(band, key=lambda m: abs(m[1]))
    print(f"  eps={eps:<5} n={len(band):<3} AUC[{min(m[0] for m in band):.4f},{best:.4f}] "
          f"CEILING_rate={steer_rate[1]:+.4f} (rank={steer_rate[2]:+.4f}) "
          f"spread_rate={rates.max()-rates.min():.4f}")
# absolute disparity (signed already older-minus-younger deny); also report |.|
print("\nTRUE defensible ceiling (honest accuracy, steered SELECTION, no circular feature),")
print("in deny-RATE units, apples-to-apples with HMDA's 0.014 anchor:")
band01 = [m for m in mb if best - m[0] <= 0.01]
ceil01 = max(band01, key=lambda m: abs(m[1]))[1]
print(f"  |ceiling@eps=.01| = {abs(ceil01):.4f}")
