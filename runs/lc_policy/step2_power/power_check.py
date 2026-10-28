import sys, json, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3] / "scripts/lc_policy"))
import numpy as np, pvg as V, test_pvg as T
t0 = time.time()
# about the real window's size and accept share (35k accepts of ~357k); a follower with other-reason declines
X, y = T.realistic(357000, V.written_rule_declines, seed=11, p_other=0.10 / 0.55, sparse_cell=True)
print("accept share", round(y.mean(), 3), flush=True)
res = V.run(X, y, seeds=V.SEEDS[:2], n_trees=V.N_TREES, eps_list=V.EPSILONS, reasons=False)
for s, v in res["seeds"].items():
    for e, m in v.items():
        print(s, e, {k: m.get(k) for k in ("n_G", "share_corrected", "share_worsened", "share_significant_any_size", "sensitivity_corrected_worsened", "gain_median")}, flush=True)
print("per-seed", res["per_seed_primary"], "minutes", round((time.time() - t0) / 60, 1))
