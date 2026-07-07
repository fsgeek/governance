from experiments.synthetic_planted import make_planted_dataset


def test_planted_dataset_has_recoverable_clean_signal():
    X, y, protected, mono, policy = make_planted_dataset(n=2000, random_state=0)
    assert len(X) == 2000 and set(y.unique()) <= {0, 1}
    assert protected.dtype == bool
    # the label must be predictable from legitimate features (signal exists)
    from sklearn.tree import DecisionTreeClassifier
    legit = [c for c in X.columns if c != "protected_proxy"]
    clf = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X[legit], y)
    assert clf.score(X[legit], y) > 0.8
