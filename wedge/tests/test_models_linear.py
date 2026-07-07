import pandas as pd
from wedge.models import FittedModel
from wedge.models_linear import fit_sparse_linear

def test_sparse_linear_satisfies_protocol_and_used_features_drops_noise():
    # f0 perfectly separates; f1, f2 are pure noise. Strong L1 should zero them.
    X = pd.DataFrame({
        "f0": [0, 0, 0, 1, 1, 1, 0, 1] * 4,
        "f1": [0, 1, 0, 1, 0, 1, 1, 0] * 4,
        "f2": [1, 0, 1, 0, 1, 0, 0, 1] * 4,
    })
    y = pd.Series([0, 0, 0, 1, 1, 1, 0, 1] * 4)
    m = fit_sparse_linear(X, y, model_id="lin", C=0.5,
                          feature_subset=("f0", "f1", "f2"))
    assert isinstance(m, FittedModel)
    used = m.used_features()
    assert "f0" in used            # signal feature retained
    assert used.issubset({"f0", "f1", "f2"})
    proba = m.predict_proba(X)
    assert proba.shape == (len(X), 2)
