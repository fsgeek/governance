"""Policy-vs-epsilon kill test (pre-reg docs/superpowers/specs/2026-09-28-policy-kill-test-preregistration.md).

Does restricting a sampled Rashomon set of shallow trees by the (reconstructed) Fannie Mae policy's
monotonicity constraints change the admissible set materially, versus epsilon alone?
Frozen together with the pre-reg; any later change is an amendment.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from wedge.collectors.fanniemae import load_collapsed_cached  # noqa: E402

SEED = 20260928
N_TREES = 3000
EPSILONS = [0.005, 0.01, 0.02]
PRIMARY_EPS = 0.01
DECLINE_SHARE = 0.20
N_PROBE = 1000
# Policy monotonicity, restated for P(default): grant-positive => default-negative.
MONO = {"fico_range_low": -1, "dti": +1, "ltv": +1, "cltv": +1, "mortgage_insurance_pct": -1}
FEATURES = ["fico_range_low", "dti", "ltv", "cltv", "mortgage_insurance_pct", "loan_term_months",
            "purpose_code", "num_units", "num_borrowers", "fthb", "prop_code"]


def frame():
    f, _ = load_collapsed_cached("data/fanniemae/2015Q1.csv")
    df = f.copy()
    # Policy regime envelope (population gate, applied to BOTH arms).
    df = df[(df.lien_position == 1) & (df.occupancy_status == "P") & (df.fico_range_low >= 620)
            & (df.dti <= 50) & (df.ltv <= 97) & (df.original_upb <= 453100)]
    df["default"] = 1 - df["label"].astype(int)
    df["purpose_code"] = df.loan_purpose.map({"P": 0, "R": 1, "C": 2}).astype(float)
    df["fthb"] = (df.first_time_homebuyer == "Y").astype(float)
    df["prop_code"] = df.property_type.map({"SF": 0, "PU": 1, "CO": 2, "MH": 3, "CP": 4}).astype(float)
    df["mortgage_insurance_pct"] = df.mortgage_insurance_pct.fillna(0.0)
    df = df.dropna(subset=FEATURES + ["default"])
    df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    n = len(df)
    tr, va = int(0.55 * n), int(0.77 * n)
    X = df[FEATURES].to_numpy(float); y = df["default"].to_numpy(int)
    return X[:tr], y[:tr], X[tr:va], y[tr:va], X[va:], y[va:], n


def sample_trees(Xtr, ytr, Xva, yva):
    rng = np.random.RandomState(SEED)
    out = []
    for i in range(N_TREES):
        k = rng.randint(3, 7)
        feats = np.sort(rng.choice(len(FEATURES), k, replace=False))
        depth = int(rng.choice([2, 3, 4]))
        leaf = int(rng.choice([200, 1000, 3000]))
        idx = rng.choice(len(Xtr), len(Xtr), replace=True)  # bootstrap: different fits per subset
        t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=i)
        t.fit(Xtr[idx][:, feats], ytr[idx])
        p = t.predict_proba(Xva[:, feats])[:, 1] if t.n_classes_ == 2 else np.zeros(len(Xva))
        out.append({"i": i, "feats": feats, "tree": t,
                    "val_logloss": float(log_loss(yva, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1]))})
    return out


def p_default(m, X):
    t = m["tree"]
    return t.predict_proba(X[:, m["feats"]])[:, 1] if t.n_classes_ == 2 else np.zeros(len(X))


def decline_threshold(m, Xref):
    return np.quantile(p_default(m, Xref), 1 - DECLINE_SHARE)


def violates(m, Xprobe, thr, level, features):
    """Exact-at-thresholds monotonicity check on a probe set.
    level='prob': P(default) must move in the policy direction as the feature moves.
    level='decision': the decline decision (p >= thr) must not move against policy."""
    t = m["tree"].tree_
    used = {FEATURES[m["feats"][j]]: j for j in range(len(m["feats"]))}
    for fname, sign in MONO.items():
        if fname not in used or fname not in features:
            continue
        j = used[fname]
        cuts = np.unique(t.threshold[t.feature == j])
        if len(cuts) == 0:
            continue
        grid = np.concatenate([[cuts.min() - 1.0], cuts + 1e-6])  # one value per region, ascending
        Z = np.repeat(Xprobe, len(grid), axis=0)
        col = m["feats"][j]
        Z[:, col] = np.tile(grid, len(Xprobe))
        p = p_default(m, Z).reshape(len(Xprobe), len(grid))
        v = p if level == "prob" else (p >= thr).astype(float)
        d = np.diff(v, axis=1) * sign  # must be >= 0 (moving up the feature moves default in `sign`)
        if (d < -1e-12).any():
            return True
    return False


def pflip(members, Xte, thrs):
    D = np.stack([(p_default(m, Xte) >= th) for m, th in zip(members, thrs)]).astype(float)
    share = D.mean(axis=0)
    return np.minimum(share, 1 - share)


def main():
    t0 = time.time()
    Xtr, ytr, Xva, yva, Xte, yte, n = frame()
    trees = sample_trees(Xtr, ytr, Xva, yva)
    best = min(m["val_logloss"] for m in trees)
    probe = Xva[np.random.RandomState(SEED + 1).choice(len(Xva), N_PROBE, replace=False)]
    res = {"prereg": "see commit", "n_envelope": n, "default_rate": float(np.concatenate([ytr, yva, yte]).mean()),
           "best_val_logloss": best, "by_eps": {}}
    variants = {"decision_all5": ("decision", set(MONO)),
                "decision_noMI": ("decision", set(MONO) - {"mortgage_insurance_pct"}),
                "prob_all5": ("prob", set(MONO)),
                "prob_noMI": ("prob", set(MONO) - {"mortgage_insurance_pct"})}
    for eps in EPSILONS:
        R = [m for m in trees if m["val_logloss"] <= best * (1 + eps)]
        thrs = [decline_threshold(m, Xva) for m in R]
        pf_R = pflip(R, Xte, thrs)
        amb_R = set(np.where(pf_R > 0)[0].tolist())
        e = {"n_R": len(R), "mean_pflip_R": float(pf_R.mean()), "n_ambiguous_R": len(amb_R), "variants": {}}
        for vname, (level, feats) in variants.items():
            keep = [k for k, (m, th) in enumerate(zip(R, thrs)) if not violates(m, probe, th, level, feats)]
            RP = [R[k] for k in keep]
            v = {"n_RP": len(RP), "retention": len(RP) / max(1, len(R))}
            if len(RP) >= 2:
                pf_P = pflip(RP, Xte, [thrs[k] for k in keep])
                amb_P = set(np.where(pf_P > 0)[0].tolist())
                u = amb_R | amb_P
                v.update({"mean_pflip_RP": float(pf_P.mean()),
                          "delta_mean_pflip": float(pf_P.mean() - pf_R.mean()),
                          "n_ambiguous_RP": len(amb_P),
                          "ambiguous_jaccard": (len(amb_R & amb_P) / len(u)) if u else 1.0,
                          "mean_abs_pflip_change": float(np.abs(pf_P - pf_R).mean())})
            e["variants"][vname] = v
        res["by_eps"][str(eps)] = e
    res["verdict"] = verdict(res)
    res["secs"] = round(time.time() - t0, 1)
    out = ROOT / "runs/policy_kill"; out.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out / "results.json", "w"), indent=2)
    print(json.dumps(res, indent=1))


def verdict(res):
    """Pre-reg §5, at PRIMARY_EPS on the decision-level, MI-excluded variant (primary)."""
    e = res["by_eps"][str(PRIMARY_EPS)]
    v = e["variants"]["decision_noMI"]
    if e["n_R"] < 30:
        return {"verdict": "VOID", "why": f"n_R={e['n_R']} < 30"}
    if v["n_RP"] < 2:
        return {"verdict": "POLICY_MATTERS", "why": "policy leaves < 2 members", "detail": v}
    kill = (v["retention"] >= 0.90 and abs(v["delta_mean_pflip"]) < 0.01 and v["ambiguous_jaccard"] >= 0.90)
    matters = (v["retention"] <= 0.50 or v["ambiguous_jaccard"] <= 0.70)
    return {"verdict": "KILL" if kill else ("POLICY_MATTERS" if matters else "INCONCLUSIVE"), "detail": v}


if __name__ == "__main__":
    main()
