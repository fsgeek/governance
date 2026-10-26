"""Step 2: P (compiled written policy) vs G (generic monotone) on LendingClub decisions, 2011-01-06 to 2012-05-31.

Implements docs/superpowers/specs/2026-10-27-lc-step2-policy-vs-generic-prereg-DRAFT.md. Pure functions over arrays so
constructed data can drive every branch. `main()` reads the real files and must not run before the freeze commit.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from governs import parse_pct  # noqa: E402  (step 1's frozen parser)

FEATURES = ["score", "dti", "amount", "emp"]
SCORE, DTI = 0, 1
SEED = 20261027
SEEDS = [SEED + k for k in range(5)]
N_TREES = 3000
EPSILONS = [0.005, 0.01, 0.02]
PRIMARY_EPS = 0.01
MIN_G = 200
DEPTHS, LEAVES = (2, 3, 4), (1000, 3000)
WINDOW = ("2011-01-06", "2012-05-31")
ACC_MONTHS = ("2011-02", "2012-05")


DTI_TOL = 0.5   # a tree violates only if it accepts DTI at least this far inside a declined region (pre-reg §4)


def written_rule_declines(score: np.ndarray, dti: np.ndarray, tol: float = 0.0) -> np.ndarray:
    """V5/V6: decline if FICO < 660, or DTI >= 25 with FICO < 720, or DTI >= 30 with FICO >= 720.
    With tol, the DTI boundaries move inward by tol (score is bucketed, so it needs none)."""
    return (score < 660) | ((score < 720) & (dti >= 25 + tol)) | ((score >= 720) & (dti >= 30 + tol))


def floors_declines(score: np.ndarray, dti: np.ndarray, tol: float = 0.0) -> np.ndarray:
    """Decomposition (pre-reg §5): the univariate part only, FICO >= 660 and DTI < 30 for everyone."""
    return (score < 660) | (dti >= 30 + tol)


def bucket5(x: np.ndarray) -> np.ndarray:
    return np.floor(np.asarray(x, dtype=float) / 5.0) * 5.0


EMP = {"< 1 year": 0, "1 year": 1, "10+ years": 10, "n/a": -1}
EMP.update({f"{k} years": k for k in range(2, 10)})


def emp_code(s) -> float:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return -1.0
    return float(EMP.get(str(s).strip(), -1))


@dataclass
class Member:
    tree: DecisionTreeClassifier
    cols: list[int]
    thr: float          # accept iff P(accept) >= thr
    val_loss: float


def predict_accept_proba(m: Member, X: np.ndarray) -> np.ndarray:
    p = m.tree.predict_proba(X[:, m.cols])
    return p[:, list(m.tree.classes_).index(1)] if 1 in m.tree.classes_ else np.zeros(len(X))


def decide(m: Member, X: np.ndarray) -> np.ndarray:
    return predict_accept_proba(m, X) >= m.thr


def logloss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def sample_trees(Xtr, ytr, Xva, yva, seed: int, n: int = N_TREES) -> list[Member]:
    rng = np.random.RandomState(seed)
    share = float(np.mean(yva))
    out = []
    for i in range(n):
        k = rng.randint(2, len(FEATURES) + 1)
        cols = sorted(rng.choice(len(FEATURES), size=k, replace=False).tolist())
        depth, leaf = int(rng.choice(DEPTHS)), int(rng.choice(LEAVES))
        rows = rng.randint(0, len(Xtr), len(Xtr))
        t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=(seed * 10_000 + i) % 4_294_967_295)
        t.fit(Xtr[rows][:, cols], ytr[rows])
        m = Member(t, cols, 0.0, 0.0)
        pva = predict_accept_proba(m, Xva)
        m.thr = float(np.quantile(pva, 1 - share))       # decision matches the observed acceptance share
        m.val_loss = logloss(yva, pva)
        out.append(m)
    return out


def rashomon(members: list[Member], eps: float) -> list[Member]:
    best = min(m.val_loss for m in members)
    return [m for m in members if m.val_loss <= (1 + eps) * best]


def split_thresholds(m: Member, feature: int) -> list[float]:
    if feature not in m.cols:
        return []
    local = m.cols.index(feature)
    tr = m.tree.tree_
    return sorted({float(tr.threshold[j]) for j in range(tr.node_count) if tr.feature[j] == local})


def straddle32(t: float) -> tuple[float, float]:
    """The float32 values just at-or-below and just above threshold t. sklearn casts X to float32 and tests
    x <= t, so a float64 nextafter can round back to the wrong side (the policy-kill bug class)."""
    f = np.float32(t)
    if float(f) <= t:
        lo, hi = f, np.nextafter(f, np.float32(np.inf))
    else:
        lo, hi = np.nextafter(f, np.float32(-np.inf)), f
    return float(lo), float(hi)


def violates_monotone(m: Member, probe: np.ndarray) -> bool:
    """Accept must be non-decreasing in score and non-increasing in DTI. Checked on the two float32 values that
    straddle every split threshold of that feature."""
    for f, sign in ((SCORE, +1), (DTI, -1)):
        for t in split_thresholds(m, f):
            lo, hi = probe.copy(), probe.copy()
            lo[:, f], hi[:, f] = straddle32(t)
            dlo, dhi = decide(m, lo), decide(m, hi)
            if sign > 0 and np.any(dlo & ~dhi):
                return True
            if sign < 0 and np.any(~dlo & dhi):
                return True
    return False


def violates_policy(m: Member, probe: np.ndarray, rule=written_rule_declines) -> bool:
    return bool(np.any(decide(m, probe) & rule(probe[:, SCORE], probe[:, DTI], DTI_TOL)))


def policy_grid(med_amount: float, med_emp: float) -> np.ndarray:
    s, d = np.meshgrid(np.arange(640, 805, 5.0), np.arange(0, 35.5, 0.5))
    g = np.column_stack([s.ravel(), d.ravel(), np.full(s.size, med_amount), np.full(s.size, med_emp)])
    return g


def pflip(members: list[Member], X: np.ndarray) -> np.ndarray:
    if not members:
        return np.zeros(len(X))
    share = np.mean([decide(m, X) for m in members], axis=0)
    return np.minimum(share, 1 - share)


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    u = np.sum(a | b)
    return 1.0 if u == 0 else float(np.sum(a & b) / u)


def seed_metrics(members: list[Member], probe_mono, probe_pol, Xte, eps: float) -> dict:
    R = rashomon(members, eps)
    G = [m for m in R if not violates_monotone(m, probe_mono)]
    P = [m for m in G if not violates_policy(m, probe_pol)]
    P1 = [m for m in G if not violates_policy(m, probe_pol, floors_declines)]
    out = {"n_R": len(R), "n_G": len(G), "n_P1_floors": len(P1), "n_P": len(P), "void": len(G) < MIN_G,
           # decomposition: how much the floors alone exclude, and how much the 720 interaction adds on top
           "retention_floors": (len(P1) / len(G)) if G else float("nan"),
           "retention_interaction_given_floors": (len([m for m in P1 if m in P]) / len(P1)) if P1 else float("nan")}
    if out["void"] or not P:
        out.update({"retention": (len(P) / len(G)) if G else float("nan"), "jaccard": float("nan"), "dpflip": float("nan")})
        return out
    fg, fp = pflip(G, Xte), pflip(P, Xte)
    out.update({"retention": len(P) / len(G), "jaccard": jaccard(fg > 0, fp > 0),
                "dpflip": float(abs(fg.mean() - fp.mean()))})
    return out


def seed_verdict(s: dict) -> str:
    if s["void"]:
        return "VOID"
    if s["n_P"] == 0 or s["retention"] <= 0.50 or (not math.isnan(s["jaccard"]) and s["jaccard"] <= 0.70):
        return "POLICY_MATTERS"
    if s["retention"] >= 0.90 and s["jaccard"] >= 0.90 and s["dpflip"] < 0.01:
        return "KILL"
    return "INCONCLUSIVE"


def overall_verdict(per_seed: list[str]) -> str:
    """At least 4 of 5 seeds non-VOID and agreeing; more than 1 VOID -> INCONCLUSIVE."""
    if sum(v == "VOID" for v in per_seed) > 1:
        return "INCONCLUSIVE"
    for v in ("KILL", "POLICY_MATTERS", "INCONCLUSIVE"):
        if sum(x == v for x in per_seed) >= 4:
            return v
    return "INCONCLUSIVE"


def split(X, y, seed=SEED):
    rng = np.random.RandomState(seed)
    idx = {c: rng.permutation(np.where(y == c)[0]) for c in (0, 1)}
    parts = {"tr": [], "va": [], "te": []}
    for c, ix in idx.items():
        a, b = int(0.55 * len(ix)), int(0.77 * len(ix))
        parts["tr"].append(ix[:a]); parts["va"].append(ix[a:b]); parts["te"].append(ix[b:])
    return {k: np.concatenate(v) for k, v in parts.items()}


def run(X: np.ndarray, y: np.ndarray, seeds=SEEDS, n_trees=N_TREES, eps_list=EPSILONS) -> dict:
    sp = split(X, y)
    Xtr, ytr, Xva, yva, Xte = X[sp["tr"]], y[sp["tr"]], X[sp["va"]], y[sp["va"]], X[sp["te"]]
    rng = np.random.RandomState(SEED + 1)
    probe_rows = Xva[rng.choice(len(Xva), min(2000, len(Xva)), replace=False)]
    grid = policy_grid(float(np.median(X[:, 2])), float(np.median(X[:, 3])))
    probe_pol = np.vstack([probe_rows, grid])
    res = {"n": int(len(y)), "accept_share": float(y.mean()), "seeds": {}}
    for s in seeds:
        members = sample_trees(Xtr, ytr, Xva, yva, s, n_trees)
        res["seeds"][s] = {str(e): seed_metrics(members, probe_rows, probe_pol, Xte, e) for e in eps_list}
    per = [seed_verdict(res["seeds"][s][str(PRIMARY_EPS)]) for s in seeds]
    res["per_seed_primary"] = per
    res["verdict"] = overall_verdict(per)
    return res


def load(root: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    counts = {}
    parts = []
    for ch in pd.read_csv(root / "data/rejected_2007_to_2018Q4.csv", chunksize=2_000_000,
                          usecols=["Application Date", "Risk_Score", "Debt-To-Income Ratio", "Amount Requested",
                                   "Employment Length", "Policy Code"]):
        d = pd.to_datetime(ch["Application Date"], errors="coerce")
        ch = ch[(d >= WINDOW[0]) & (d <= WINDOW[1]) & (pd.to_numeric(ch["Policy Code"], errors="coerce") == 0)]
        parts.append(pd.DataFrame({"score": pd.to_numeric(ch["Risk_Score"], errors="coerce"),
                                   "dti": ch["Debt-To-Income Ratio"].map(parse_pct),
                                   "amount": pd.to_numeric(ch["Amount Requested"], errors="coerce"),
                                   "emp": ch["Employment Length"].map(emp_code), "y": 0}))
    rej = pd.concat(parts, ignore_index=True)
    a = pd.read_csv(root / "data/accepted_2007_to_2018Q4.csv", low_memory=False,
                    usecols=["issue_d", "fico_range_low", "dti", "loan_amnt", "emp_length", "policy_code",
                             "application_type", "disbursement_method"])
    m = pd.to_datetime(a["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("M")
    keep = ((m >= pd.Period(ACC_MONTHS[0], "M")) & (m <= pd.Period(ACC_MONTHS[1], "M"))
            & (pd.to_numeric(a["policy_code"], errors="coerce") == 1)
            & (a["application_type"].fillna("Individual") == "Individual")
            & (a["disbursement_method"].fillna("Cash") == "Cash"))
    a = a[keep]
    acc = pd.DataFrame({"score": pd.to_numeric(a["fico_range_low"], errors="coerce"),
                        "dti": pd.to_numeric(a["dti"], errors="coerce"),
                        "amount": pd.to_numeric(a["loan_amnt"], errors="coerce"),
                        "emp": a["emp_length"].map(emp_code), "y": 1})
    df = pd.concat([rej, acc], ignore_index=True)
    counts.update({"rejects": len(rej), "accepts": len(acc)})
    before = len(df)
    df = df.dropna(subset=["score", "dti", "amount"])
    counts["excluded_missing"] = before - len(df)
    df["score"] = bucket5(df["score"].to_numpy())
    X = df[FEATURES].to_numpy(dtype=float)
    return X, df["y"].to_numpy(dtype=int), counts


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    X, y, counts = load(root)
    res = run(X, y)
    res["counts"] = counts
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
