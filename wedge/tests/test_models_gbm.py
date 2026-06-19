# wedge/tests/test_models_gbm.py
import pandas as pd
from wedge.models import FittedModel
from wedge.models_gbm import fit_monotone_gbm

def test_monotone_gbm_satisfies_protocol_and_respects_monotone_sign():
    # y increases with f0; enforce +1 monotonicity on f0.
    X = pd.DataFrame({
        "f0": [0, 1, 2, 3, 4, 5, 6, 7] * 6,
        "f1": [3, 1, 4, 1, 5, 9, 2, 6] * 6,
    })
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1] * 6)
    m = fit_monotone_gbm(X, y, model_id="gbm", feature_subset=("f0", "f1"),
                         monotonic_cst={"f0": 1, "f1": 0}, max_iter=50)
    assert isinstance(m, FittedModel)
    used = m.used_features()
    assert "f0" in used
    assert used.issubset({"f0", "f1"})
    # monotone +1 on f0: increasing f0 (others fixed) must not DECREASE P(approve)
    lo = pd.DataFrame({"f0": [0], "f1": [4]})
    hi = pd.DataFrame({"f0": [7], "f1": [4]})
    p_lo = m.predict_proba(lo)[0, list(m.classes_).index(1)]
    p_hi = m.predict_proba(hi)[0, list(m.classes_).index(1)]
    assert p_hi >= p_lo - 1e-9
