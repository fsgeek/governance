"""Step 2 (r2): P (compiled written policy) vs G (generic monotone) on LendingClub decisions, 2011-01-06 to 2012-05-31.

Implements docs/superpowers/specs/2026-10-27-lc-step2-policy-vs-generic-prereg-DRAFT.md (r2). r2 rebuilt after the
blind adversary's four blockers: G is trained monotone (not filtered), the policy check is exact on leaf boxes at the
probability level (no decision threshold), the verdict rests on retention, and a reason-fidelity metric is added.
`main()` reads the real files and must not run before the freeze commit.
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
SCORE, DTI, AMT, EMP_ = 0, 1, 2, 3
MONO = {SCORE: +1, DTI: -1, AMT: 0, EMP_: 0}
SUBSETS = [[0, 1], [0, 1, 2], [0, 1, 3], [0, 1, 2, 3]]   # every G tree uses score and DTI (credit priors, no policy numbers)
SEED = 20261027
SEEDS = [SEED + k for k in range(5)]
N_TREES = 4000          # set by the pre-freeze power check (pre-reg §5)
BOOT = 100_000          # bootstrap sample per tree
EPSILONS = [0.005, 0.01, 0.02]
PRIMARY_EPS = 0.01
MIN_G = 200
DEPTHS, LEAVES = (2, 3, 4), (1000, 3000)
RHO = 0.01              # a leaf "accepts" if its P(accept) exceeds this
MIN_MASS = 10           # a violation needs at least this many test applicants inside it
DTI_TOL, SCORE_TOL = 0.5, 5.0
WINDOW = ("2011-01-06", "2012-05-31")
ACC_MONTHS = ("2011-02", "2012-05")


# ---------- the written rule ----------

def written_rule_declines(score, dti, tol_dti=0.0, tol_score=0.0):
    """V5/V6: decline if FICO < 660, or DTI >= 25 with FICO < 720, or DTI >= 30 with FICO >= 720.
    With tolerances, each declined region shrinks inward: DTI by tol_dti, the 720 boundary by tol_score each side."""
    score, dti = np.asarray(score, float), np.asarray(dti, float)
    return ((score < 660) | ((score < 720 - tol_score) & (dti >= 25 + tol_dti))
            | ((score >= 720 + tol_score) & (dti >= 30 + tol_dti)) | ((score >= 660) & (dti >= 30 + tol_dti)))


def floors_declines(score, dti, tol_dti=0.0, tol_score=0.0):
    """Decomposition: the univariate part only (FICO >= 660 and DTI < 30 for everyone)."""
    score, dti = np.asarray(score, float), np.asarray(dti, float)
    return (score < 660) | (dti >= 30 + tol_dti)


def true_reasons(score: float, dti: float) -> set[str]:
    """The written rule's own reasons for a decline. FICO < 720 with DTI in [25, 30): DTI, or score (reaching 720 makes
    it eligible). DTI >= 30: DTI. FICO < 660 (with an eligible DTI): score."""
    r = set()
    if score < 660:
        r.add("score")
    if dti >= 30:
        r.add("dti")
    elif dti >= 25 and score < 720:
        r |= {"dti", "score"}
    return r


# ---------- trees and leaf boxes ----------

def bucket5(x):
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
    depth: int
    leaf: int
    val_loss: float = 0.0


def p_accept(m: Member, X: np.ndarray) -> np.ndarray:
    p = m.tree.predict_proba(X[:, m.cols])
    return p[:, list(m.tree.classes_).index(1)] if 1 in m.tree.classes_ else np.zeros(len(X))


def leaf_boxes(m: Member) -> list[tuple[dict, float]]:
    """Every leaf as ({feature: (lo, hi)} on the FULL feature index, P(accept)). Intervals are (lo, hi]: sklearn
    sends x <= t left."""
    tr = m.tree.tree_
    k1 = list(m.tree.classes_).index(1) if 1 in m.tree.classes_ else None
    out = []

    def walk(node, box):
        if tr.children_left[node] == -1:
            v = tr.value[node][0]
            p = float(v[k1] / v.sum()) if k1 is not None and v.sum() > 0 else 0.0
            out.append((dict(box), p))
            return
        f, t = m.cols[tr.feature[node]], float(tr.threshold[node])
        lo, hi = box.get(f, (-np.inf, np.inf))
        box[f] = (lo, min(hi, t)); walk(tr.children_left[node], box)
        box[f] = (max(lo, t), hi); walk(tr.children_right[node], box)
        box[f] = (lo, hi)

    walk(0, {})
    return out


def in_box(X: np.ndarray, box: dict) -> np.ndarray:
    ok = np.ones(len(X), bool)
    for f, (lo, hi) in box.items():
        ok &= (X[:, f] > lo) & (X[:, f] <= hi)
    return ok


def violation_mass(m: Member, Xmass: np.ndarray, rule=written_rule_declines) -> int:
    """Test applicants inside an accepting leaf (P > RHO) that the rule (with tolerances) declines. Exact over the
    leaf boxes: every amount and employment value is covered, not a median grid (adversary finding 6)."""
    declined = rule(Xmass[:, SCORE], Xmass[:, DTI], DTI_TOL, SCORE_TOL)
    hit = np.zeros(len(Xmass), bool)
    for box, p in leaf_boxes(m):
        if p > RHO:
            hit |= in_box(Xmass, box) & declined
    return int(hit.sum())


def violates(m: Member, Xmass: np.ndarray, rule=written_rule_declines) -> bool:
    return violation_mass(m, Xmass, rule) >= MIN_MASS


def logloss(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def sample_trees(Xtr, ytr, Xva, yva, seed: int, n: int = N_TREES) -> list[Member]:
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        cols = SUBSETS[rng.randint(len(SUBSETS))]
        depth, leaf = int(rng.choice(DEPTHS)), int(rng.choice(LEAVES))
        rows = rng.randint(0, len(Xtr), min(BOOT, len(Xtr)))
        t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, monotonic_cst=[MONO[c] for c in cols],
                                   random_state=(seed * 10_000 + i) % 4_294_967_295)
        t.fit(Xtr[rows][:, cols], ytr[rows])
        m = Member(t, cols, depth, leaf)
        m.val_loss = logloss(yva, p_accept(m, Xva))
        out.append(m)
    return out


def band(members: list[Member], eps: float) -> list[Member]:
    best = min(m.val_loss for m in members)
    return [m for m in members if m.val_loss <= (1 + eps) * best]


# ---------- reason fidelity (secondary) ----------

def first_reason(m: Member, x: np.ndarray) -> str | None:
    """The single feature whose change most raises P(accept) for x: each feature is moved across each of its split
    thresholds (to the float32 just above / at-or-below), others fixed. None if no single change raises it."""
    base = float(p_accept(m, x[None, :])[0])
    tr = m.tree.tree_
    best, best_gain = None, 0.0
    for local, f in enumerate(m.cols):
        ts = {float(tr.threshold[j]) for j in range(tr.node_count) if tr.feature[j] == local}
        gain = 0.0
        for t in ts:
            for v in straddle32(t):
                z = x.copy(); z[f] = v
                gain = max(gain, float(p_accept(m, z[None, :])[0]) - base)
        if gain > best_gain + 1e-12:
            best, best_gain = FEATURES[f], gain
    return best


def straddle32(t: float) -> tuple[float, float]:
    """float32 values at-or-below and just above t (sklearn compares float32 X against t in double)."""
    f = np.float32(t)
    if float(f) <= t:
        lo, hi = f, np.nextafter(f, np.float32(np.inf))
    else:
        lo, hi = np.nextafter(f, np.float32(-np.inf)), f
    return float(lo), float(hi)


def reason_fidelity(P: list[Member], Xte: np.ndarray, n_app: int = 300, seed: int = SEED) -> dict:
    """Over test applicants the written rule declines (no tolerance) and each member of P declines (P <= RHO):
    the share of (applicant, member) pairs whose first reason is outside the rule's own reasons."""
    d = written_rule_declines(Xte[:, SCORE], Xte[:, DTI])
    idx = np.where(d)[0]
    if not len(idx) or not P:
        return {"pairs": 0, "outside_share": float("nan")}
    rng = np.random.RandomState(seed)
    idx = rng.choice(idx, min(n_app, len(idx)), replace=False)
    pairs = outside = none = 0
    for i in idx:
        x = Xte[i]
        truth = true_reasons(x[SCORE], x[DTI])
        for m in P:
            if p_accept(m, x[None, :])[0] > RHO:
                continue
            r = first_reason(m, x)
            pairs += 1
            if r is None:
                none += 1
            elif r not in truth:
                outside += 1
    return {"pairs": pairs, "outside_share": (outside / pairs) if pairs else float("nan"),
            "no_single_reason_share": (none / pairs) if pairs else float("nan")}


# ---------- verdict ----------

def seed_metrics(members, Xte, eps, with_reasons=False) -> dict:
    G = band(members, eps)
    P = [m for m in G if not violates(m, Xte)]
    P1 = [m for m in G if not violates(m, Xte, floors_declines)]
    by = {}
    for m in G:
        k = f"d{m.depth}_l{m.leaf}"
        b = by.setdefault(k, [0, 0]); b[0] += 1; b[1] += int(m in P)
    out = {"n_G": len(G), "n_P": len(P), "n_P1_floors": len(P1), "void": len(G) < MIN_G,
           "retention": (len(P) / len(G)) if G else float("nan"),
           "retention_floors": (len(P1) / len(G)) if G else float("nan"),
           "retention_interaction_given_floors": (sum(m in P for m in P1) / len(P1)) if P1 else float("nan"),
           "retention_by_depth_leaf": {k: [v[0], v[1] / v[0]] for k, v in by.items()}}
    if with_reasons:
        out["reason_fidelity"] = reason_fidelity(P, Xte)
    return out


def seed_verdict(s: dict) -> str:
    if s["void"]:
        return "VOID"
    if s["retention"] >= 0.90:
        return "KILL"
    if s["retention"] <= 0.50:
        return "POLICY_MATTERS"
    return "INCONCLUSIVE"


def overall_verdict(per_seed: list[str]) -> str:
    if sum(v == "VOID" for v in per_seed) > 1:
        return "INCONCLUSIVE"
    for v in ("KILL", "POLICY_MATTERS", "INCONCLUSIVE"):
        if sum(x == v for x in per_seed) >= 4:
            return v
    return "INCONCLUSIVE"


def split(X, y, seed=SEED):
    rng = np.random.RandomState(seed)
    parts = {"tr": [], "va": [], "te": []}
    for c in (0, 1):
        ix = rng.permutation(np.where(y == c)[0])
        a, b = int(0.55 * len(ix)), int(0.77 * len(ix))
        parts["tr"].append(ix[:a]); parts["va"].append(ix[a:b]); parts["te"].append(ix[b:])
    return {k: np.concatenate(v) for k, v in parts.items()}


def run(X, y, seeds=SEEDS, n_trees=N_TREES, eps_list=EPSILONS, reasons=True) -> dict:
    sp = split(X, y)
    Xtr, ytr, Xva, yva, Xte = X[sp["tr"]], y[sp["tr"]], X[sp["va"]], y[sp["va"]], X[sp["te"]]
    res = {"n": int(len(y)), "accept_share": float(y.mean()), "seeds": {}}
    for s in seeds:
        members = sample_trees(Xtr, ytr, Xva, yva, s, n_trees)
        res["seeds"][s] = {str(e): seed_metrics(members, Xte, e, with_reasons=(reasons and e == PRIMARY_EPS))
                           for e in eps_list}
    per = [seed_verdict(res["seeds"][s][str(PRIMARY_EPS)]) for s in seeds]
    res["per_seed_primary"], res["verdict"] = per, overall_verdict(per)
    return res


# ---------- data ----------

def load(root: Path):
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
    mth = pd.to_datetime(a["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("M")
    keep = ((mth >= pd.Period(ACC_MONTHS[0], "M")) & (mth <= pd.Period(ACC_MONTHS[1], "M"))
            & (pd.to_numeric(a["policy_code"], errors="coerce") == 1)
            & (a["application_type"].fillna("Individual") == "Individual")
            & (a["disbursement_method"].fillna("Cash") == "Cash"))
    a = a[keep]
    acc = pd.DataFrame({"score": pd.to_numeric(a["fico_range_low"], errors="coerce"),
                        "dti": pd.to_numeric(a["dti"], errors="coerce"),
                        "amount": pd.to_numeric(a["loan_amnt"], errors="coerce"),
                        "emp": a["emp_length"].map(emp_code), "y": 1})
    df = pd.concat([rej, acc], ignore_index=True)
    counts = {"rejects": len(rej), "accepts": len(acc)}
    before = len(df)
    df = df.dropna(subset=["score", "dti", "amount"])
    counts["excluded_missing_score_dti_or_amount"] = before - len(df)
    df["score"] = bucket5(df["score"].to_numpy())
    return df[FEATURES].to_numpy(dtype=float), df["y"].to_numpy(dtype=int), counts


def main():
    root = Path(__file__).resolve().parents[2]
    X, y, counts = load(root)
    res = run(X, y)
    res["counts"] = counts
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
