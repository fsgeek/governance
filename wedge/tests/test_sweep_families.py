# wedge/tests/test_sweep_families.py
import pandas as pd
from wedge.rashomon import SweepResult, evaluate_policy
from wedge.sweep_families import sweep_family
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset

def test_sweep_family_runs_all_three_and_yields_admissible_under_no_policy():
    df = tiny_noisy_dataset()
    X, y = df[FEATURE_COLS], df["label"]
    fs = (tuple(FEATURE_COLS),)
    grids = {
        "cart": {"max_depths": (2, 3), "min_samples_leafs": (1,)},
        "linear": {"Cs": (0.05, 1.0)},
        "gbm": {"max_iters": (30,)},
    }
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid, feature_subsets=fs)
        assert results and all(isinstance(r, SweepResult) for r in results)
        assert all(r.fitted_model is not None for r in results)
        pa = evaluate_policy(results, policy_constraints=None)
        assert len(pa.admissible) == len(results)
