#!/usr/bin/env python3
"""Collapse FNMAE 2018Q1 monthly rows -> loan-level, cache to parquet. Run once."""
import pandas as pd, numpy as np, time

FM = "data/fanniemae.old/2018Q1.csv"
OUT = "data/fanniemae.old/2018Q1_loanlevel.parquet"
# glossary field N -> 0-indexed col N-1
COLS = {"loan_id": 2, "term": 13, "ltv": 20, "cltv": 21, "n_borr": 22,
        "dti": 23, "fico": 24, "upb": 10, "dlq": 40, "zbcode": 44, "purpose": 27}
names = {v - 1: k for k, v in COLS.items()}
usecols = sorted(names)

t0 = time.time()
parts = []
rdr = pd.read_csv(FM, sep="|", header=None, usecols=usecols,
                  names=[names[c] for c in usecols], dtype=str,
                  engine="c", chunksize=4_000_000)
for i, ch in enumerate(rdr):
    dlq_n = pd.to_numeric(ch["dlq"], errors="coerce")
    ch["serious"] = (dlq_n >= 3).astype("int8")
    ch["ce"] = ch["zbcode"].isin(["02", "03", "09", "15"]).astype("int8")
    parts.append(ch[["loan_id", "term", "ltv", "cltv", "n_borr", "dti", "fico",
                     "upb", "purpose", "serious", "ce"]])
    print(f"  chunk {i} rows={len(ch)} t={time.time()-t0:.0f}s", flush=True)

big = pd.concat(parts, ignore_index=True)
print(f"concat rows={len(big)} t={time.time()-t0:.0f}s", flush=True)
agg = big.groupby("loan_id", sort=False).agg(
    term=("term", "first"), ltv=("ltv", "first"), cltv=("cltv", "first"),
    n_borr=("n_borr", "first"), dti=("dti", "first"), fico=("fico", "first"),
    upb=("upb", "first"), purpose=("purpose", "first"),
    ever_dlq=("serious", "max"), ever_ce=("ce", "max"),
).reset_index()
for c in ["term", "ltv", "cltv", "n_borr", "dti", "fico", "upb"]:
    agg[c] = pd.to_numeric(agg[c], errors="coerce")
agg.to_parquet(OUT)
print(f"DONE loans={len(agg)} dlq_rate={agg.ever_dlq.mean():.4f} "
      f"ce_rate={agg.ever_ce.mean():.4f} t={time.time()-t0:.0f}s -> {OUT}", flush=True)
