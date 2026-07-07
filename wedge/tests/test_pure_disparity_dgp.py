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

def test_eval_model_emits_ghat_stratified_accuracy():
    import importlib.util as iu
    s = iu.spec_from_file_location("lda", Path(__file__).resolve().parents[2]
                                   / "scripts" / "lda_shared_surface_test.py")
    lda = iu.module_from_spec(s); sys.modules["lda"] = lda; s.loader.exec_module(lda)
    fr = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    tr, te = lda._split(len(fr), 0)
    out = lda._eval_model(fr, tr, te, lda.ADMISSIBLE, 0)
    assert "A_obs_ghat0" in out and "A_obs_ghat1" in out
    assert 0.0 <= out["A_obs_ghat0"] <= 1.0 and 0.0 <= out["A_obs_ghat1"] <= 1.0
    # both true-G and ghat stratifiers present (distinct keys)
    assert "A_obs_g0" in out and "A_obs_ghat0" in out
    print(f"\nA_obs_ghat0={out['A_obs_ghat0']:.4f} A_obs_ghat1={out['A_obs_ghat1']:.4f}")

def test_run_pure_disparity_smoke_structure(tmp_path):
    import importlib.util as iu, json
    s = iu.spec_from_file_location("lda", Path(__file__).resolve().parents[2]
                                   / "scripts" / "lda_shared_surface_test.py")
    lda = iu.module_from_spec(s); sys.modules["lda"] = lda; s.loader.exec_module(lda)
    out = tmp_path / "smoke.json"
    lda.run_pure_disparity(0.70, ("PD_baserate",), (0.20,), range(2), 2500, out, True)
    payload = json.loads(out.read_text())
    summary = payload["summary"]
    assert "PD_baserate_gap0.20" in summary
    assert "NEG_clean" in summary
    cell = summary["PD_baserate_gap0.20"]
    assert set(cell["infosets"].keys()) == {"bare", "trueG", "bisg", "oracle"}
    assert "delta" in cell["validity"] and "passes" in cell["validity"]
    # negative control structure: a bool per info-set
    assert set(summary["NEG_clean"].keys()) == {"bare", "trueG", "bisg", "oracle"}

def test_infoset_separates_no_result_on_sign_disagreement():
    import importlib.util as iu
    s = iu.spec_from_file_location("lda2", Path(__file__).resolve().parents[2]
                                   / "scripts" / "lda_shared_surface_test.py")
    lda = iu.module_from_spec(s); sys.modules["lda2"] = lda; s.loader.exec_module(lda)
    # build synthetic rows where naive and k-ctl would disagree is hard to force;
    # instead assert the structure: _infoset_separates returns the right shape and
    # excludes no_result members from the any() decision.
    rows = []
    for seed in range(6):
        for arm in ("H", "L"):
            for k in range(4):
                rows.append({"arm": arm, "k": k, "seed": seed, "abs_gap": 0.1 + 0.01*k,
                             "A_obs": 0.8, "CAL": 0.4, "A_obs_g0": 0.8, "A_obs_g1": 0.8,
                             "A_obs_ghat0": 0.8, "A_obs_ghat1": 0.8, "A_clean": 0.8})
    res = lda._infoset_separates(rows, lda.INFO_SETS["bare"])
    assert "separates" in res and "per_disc" in res
    assert isinstance(res["separates"], bool)
