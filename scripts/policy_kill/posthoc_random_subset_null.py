"""POST-HOC (not pre-registered): random-subset null for the policy-kill verdict.

Removing ANY members from R mechanically shrinks the P(flip)>0 ambiguous set. This asks whether
the policy-filtered subset differs from a random subset of the same size. Reuses the frozen
harness (run.py at 8f72e4f) unchanged to regenerate the identical tree sample.
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run

def main():
    Xtr, ytr, Xva, yva, Xte, yte, n = run.frame()
    trees = run.sample_trees(Xtr, ytr, Xva, yva)
    best = min(m["val_logloss"] for m in trees)
    probe = Xva[np.random.RandomState(run.SEED + 1).choice(len(Xva), run.N_PROBE, replace=False)]
    D_te = {}
    out = {"note": "POST-HOC random-subset null", "by_eps": {}}
    rng = np.random.RandomState(7)
    for eps in run.EPSILONS:
        R = [m for m in trees if m["val_logloss"] <= best * (1 + eps)]
        thrs = [run.decline_threshold(m, Xva) for m in R]
        D = np.stack([(run.p_default(m, Xte) >= th) for m, th in zip(R, thrs)]).astype(float)
        def stats(idx):
            s = D[idx].mean(axis=0); pf = np.minimum(s, 1 - s); return pf
        pf_R = stats(np.arange(len(R))); amb_R = pf_R > 0
        e = {"n_R": len(R)}
        for vname, (level, feats) in {"decision_noMI": ("decision", set(run.MONO) - {"mortgage_insurance_pct"}),
                                      "prob_noMI": ("prob", set(run.MONO) - {"mortgage_insurance_pct"})}.items():
            keep = [k for k, (m, th) in enumerate(zip(R, thrs)) if not run.violates(m, probe, th, level, feats)]
            if len(keep) < 2:
                e[vname] = {"n_RP": len(keep)}; continue
            def jac(idx):
                a = stats(idx) > 0; u = (a | amb_R).sum(); return (a & amb_R).sum() / u if u else 1.0
            j_pol = jac(np.array(keep))
            nulls = np.array([jac(rng.choice(len(R), len(keep), replace=False)) for _ in range(1000)])
            # which features cause the violations
            viol_by_feat = {}
            for f in feats:
                viol_by_feat[f] = sum(run.violates(m, probe, th, level, {f}) for m, th in zip(R, thrs))
            e[vname] = {"n_RP": len(keep), "jaccard_policy": float(j_pol),
                        "null_jaccard_mean": float(nulls.mean()),
                        "null_jaccard_p05_p50_p95": [float(np.percentile(nulls, q)) for q in (5, 50, 95)],
                        "frac_null_leq_policy": float((nulls <= j_pol).mean()),
                        "violations_by_feature": viol_by_feat}
        out["by_eps"][str(eps)] = e
    Path("runs/policy_kill/posthoc_random_subset_null.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
