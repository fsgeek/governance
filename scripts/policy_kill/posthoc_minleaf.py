"""Diagnostic promised in pre-reg §5 but omitted from the frozen harness: violation rate by
min_samples_leaf (noise non-monotonicity check). Reuses run.py unchanged."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run

Xtr, ytr, Xva, yva, Xte, yte, n = run.frame()
trees = run.sample_trees(Xtr, ytr, Xva, yva)
best = min(m["val_logloss"] for m in trees)
probe = Xva[np.random.RandomState(run.SEED + 1).choice(len(Xva), run.N_PROBE, replace=False)]
feats = set(run.MONO) - {"mortgage_insurance_pct"}
out = {}
for eps in run.EPSILONS:
    R = [m for m in trees if m["val_logloss"] <= best * (1 + eps)]
    tab = {}
    for m in R:
        leaf = m["tree"].get_params()["min_samples_leaf"]; th = run.decline_threshold(m, Xva)
        v = run.violates(m, probe, th, "decision", feats)
        uses_fico = "fico_range_low" in [run.FEATURES[j] for j in m["feats"]]
        t = tab.setdefault(str(leaf), {"n": 0, "violating": 0, "uses_fico": 0})
        t["n"] += 1; t["violating"] += int(v); t["uses_fico"] += int(uses_fico)
    out[str(eps)] = tab
# all 3000 trees, regardless of epsilon: violation rate by leaf size among FICO-using trees
allt = {}
for m in trees:
    if "fico_range_low" not in [run.FEATURES[j] for j in m["feats"]]:
        continue
    leaf = m["tree"].get_params()["min_samples_leaf"]; th = run.decline_threshold(m, Xva)
    t = allt.setdefault(str(leaf), {"n": 0, "violating": 0})
    t["n"] += 1; t["violating"] += int(run.violates(m, probe, th, "decision", {"fico_range_low"}))
out["all_trees_fico_users"] = allt
Path("runs/policy_kill/posthoc_minleaf.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))
