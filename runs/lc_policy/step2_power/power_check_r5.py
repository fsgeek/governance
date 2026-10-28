"""Synthetic power check for step 2 r5 (no real data): epsilon* on a LendingClub-shaped follower, and a timing of
reason fidelity at full scale."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts/lc_policy"))
import numpy as np, pvg as V, test_pvg as T

t0 = time.time()
X, y = T.realistic(357000, V.written_rule_declines, seed=11, p_other=0.10 / 0.55, sparse_cell=True)
print("accept share", round(y.mean(), 3), "construct_share", V.construct_share(X, y), flush=True)
res = V.run(X, y, seeds=V.SEEDS[:3], n_trees=V.N_TREES, eps_list=V.EPSILONS, reasons=False)
for s, v in res["seeds"].items():
    print(s, "eps_star", v["eps_star"], "best_tree", v["best_tree"], "pooling_gain_median", v["pooling_gain_median"],
          "by_eps", v["by_eps"], flush=True)
    print("   curve (eps, n, corrected):", [(e, n, round(c, 3)) for e, n, c in v["curve"] if n][::6], flush=True)
print("per_seed", res["per_seed"], "verdict", res["verdict"], "eps_star_median", res["eps_star_median"],
      "minutes", round((time.time() - t0) / 60, 1), flush=True)

# reason-fidelity timing: 20 applicants x the eps=0.01 band of one seed, then extrapolate to 300
sp = V.split(X, y)
Xtr, ytr, Xva, yva, Xte = X[sp["tr"]], y[sp["tr"]], X[sp["va"]], y[sp["va"]], X[sp["te"]]
members = V.sample_trees(Xtr, ytr, Xva, yva, V.SEEDS[0], V.N_TREES)
mono = [m for m in members if not V.monotone_violation(m, Xva, yva)]
best = min(m.val_loss for m in mono)
G = [m for m in mono if m.val_loss <= (1 + V.PRIMARY_EPS) * best]
t1 = time.time()
fid = V.reason_fidelity(G, Xte, n_app=20)
dt = time.time() - t1
print("reason fidelity on 20 applicants x", len(G), "members:", fid, "seconds", round(dt, 1),
      "-> 300 applicants x 5 seeds ~", round(dt * 15 * 5 / 3600, 1), "hours", flush=True)
