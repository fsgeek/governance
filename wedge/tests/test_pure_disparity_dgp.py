import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score

_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp",
    Path(__file__).resolve().parents[2] / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

N = 8000
OBS = [f"x{j}" for j in range(8)] + ["cfresh_cont", "cfresh_cat", "cfresh_count"]

def _within_g_auc(fr):
    """Pooled within-G-stratum AUC(Y ~ OBS). A pure disparity stays ~flat vs the
    clean world; an individual predictor climbs."""
    aucs = []
    for g in (0, 1):
        sub = fr[fr["G"] == g]
        if sub["Y"].nunique() < 2:
            continue
        m = GradientBoostingClassifier(max_depth=3, n_estimators=100, random_state=0)
        m.fit(sub[OBS].values, sub["Y"].values)
        aucs.append(roc_auc_score(sub["Y"].values, m.predict_proba(sub[OBS].values)[:, 1]))
    return float(np.mean(aucs))

def _abs_gap(fr):
    g0 = fr[fr["G"] == 0]["Y"].mean(); g1 = fr[fr["G"] == 1]["Y"].mean()
    return float(abs(g0 - g1))

def test_pd_baserate_plants_excess_gap_in_disparate_direction():
    # clean baseline gap is legit-driven (~+0.10, G=1 higher). target_gap=0.20 plants
    # 0.20 of ADDITIONAL gap beyond baseline in the disparate direction (net signed gap
    # should be baseline - 0.20 ~ -0.10, i.e. |net| meaningfully negative-shifted).
    clean = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    def signed(fr):
        return fr[fr["G"]==1]["Y"].mean() - fr[fr["G"]==0]["Y"].mean()
    excess = signed(clean) - signed(plant)     # how much we pushed G=1 down
    assert abs(excess - 0.20) < 0.04, f"excess gap {excess:.3f} off target 0.20"

def test_pd_baserate_unreachable_target_raises():
    import pytest
    with pytest.raises(ValueError):
        dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=5.0).frame  # impossible

def test_pd_baserate_passes_validity_gate():
    clean = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    base = _within_g_auc(clean); pl = _within_g_auc(plant)
    assert abs(pl - base) < 0.02, f"within-G AUC moved {base:.3f}->{pl:.3f} (>0.02: not pure)"

def test_pd_noise_plants_excess_gap_in_disparate_direction():
    clean = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.15).frame
    def signed(fr):
        return fr[fr["G"]==1]["Y"].mean() - fr[fr["G"]==0]["Y"].mean()
    excess = signed(clean) - signed(plant)
    assert abs(excess - 0.15) < 0.04, f"excess gap {excess:.3f} off target 0.15"

def test_pd_noise_validity_gate_is_HONEST():
    # The gate is ALLOWED to reject this family (the design permits it). Assert the
    # within-G AUC delta is computed and finite; do NOT force it to pass. A label-flip
    # that leaks individual signal (delta>0.02) is a genuine scientific outcome, not a bug.
    clean = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.15).frame
    import numpy as np
    delta = abs(_within_g_auc(plant) - _within_g_auc(clean))
    assert np.isfinite(delta)
    print(f"\nPD_noise within-G AUC delta = {delta:.4f} "
          f"({'PASSES gate' if delta < 0.02 else 'REJECTED by gate'})")

def test_pd_noise_now_valid_world():
    fr = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.15).frame
    assert (fr["world"] == "PD_noise").all()
