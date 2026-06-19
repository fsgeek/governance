"""Stage-1 control runner. Run directly: python -m experiments.band_opening_control

Prints per-family C/A/B and asserts the gate. Stage 2 is forbidden until this passes.

Two arms:
  CLEAN ARM  -- sweeps only the policy-admissible subset (legit_a, legit_b).
                Gate: harness RECOVERS a planted clean member (B_plain True for
                cart AND linear).
  DIRTY ARM  -- sweeps the proxy-INCLUDING subset (legit_a, legit_b, protected_proxy)
                for cart and linear, PLUS fits one proxy-forced CART on
                (protected_proxy,) alone to demonstrate an unambiguous proxy threat.
                Gate: (a) every swept proxy-USING model lands in pa.excluded, NOT
                admissible; (b) at least one proxy-using model (swept or forced)
                produces |approval_rate_gap| > TAU, confirming the proxy is a real
                threat so exclusion is doing protective work.

Both arms must pass for gate_passed=True. assert_gate(res) raises loudly if not.
"""
from __future__ import annotations

import math
from functools import partial

from sklearn.tree import DecisionTreeClassifier

from wedge.band_outcomes import approval_rate_gap, band_outcomes
from wedge.losses import grant_emphasis_loss
from wedge.rashomon import evaluate_policy, filter_to_epsilon_under_loss
from wedge.sweep_families import sweep_family
from experiments.synthetic_planted import make_planted_dataset

EPS = 0.05  # control uses the loose end of the frozen sweep; full sweep in Stage 2
TAU = 0.02  # frozen disparity threshold


# ---------------------------------------------------------------------------
# CLEAN ARM
# ---------------------------------------------------------------------------

def run_control(random_state: int = 0) -> dict:
    """Clean arm: validates harness RECOVERS a planted clean member.

    Behavior is unchanged from the original; dirty arm is computed separately
    in run_dirty_arm() and combined in run_full_control().

    WARNING: returns a clean-arm-only result; do NOT pass to assert_gate
    (which requires run_full_control's both-arms result). Use run_full_control()
    for the real gate.
    """
    X, y, protected, mono, policy = make_planted_dataset(random_state=random_state)
    feature_subsets = (("legit_a", "legit_b"),)  # the clean subset (proxy excluded)
    grids = {"cart": {"max_depths": (2, 3, 4), "min_samples_leafs": (20,)},
             "linear": {"Cs": (0.05, 0.2, 1.0)},
             "gbm": {"max_iters": (50,)}}
    out = {}
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid,
                               feature_subsets=feature_subsets, monotonic_cst=mono)
        pa = evaluate_policy(results, policy_constraints=policy)
        band = filter_to_epsilon_under_loss(
            pa, loss_fn=partial(grant_emphasis_loss), loss_label="L_T", epsilon=EPS)
        members = [m.fitted_model for m in band.within_epsilon]
        out[fam] = band_outcomes(members, X, protected, tau=TAU)
    gate_passed = bool(out["cart"]["B_plain"] and out["linear"]["B_plain"])
    out["gate_passed"] = gate_passed
    return out


# ---------------------------------------------------------------------------
# DIRTY ARM
# ---------------------------------------------------------------------------

class _ProxyForcedModel:
    """A minimal FittedModel wrapper around a proxy-only CART.

    Fits exclusively on (protected_proxy,) so the proxy signal is unambiguously
    the sole driver. Used to demonstrate that the proxy IS a real disparity
    threat -- i.e. that the exclusion gate is doing protective work, not
    just blocking an inert feature.
    """

    def __init__(self, X, y, random_state: int = 0):
        cols = ["protected_proxy"]
        clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20,
                                     random_state=random_state)
        clf.fit(X[cols].to_numpy(), y.to_numpy())
        self._clf = clf
        self._cols = cols
        self.classes_ = tuple(int(c) for c in clf.classes_)
        self.feature_subset = ("protected_proxy",)
        self.model_id = "proxy_forced_cart"

    def predict(self, X):
        return self._clf.predict(X[self._cols].to_numpy())

    def predict_proba(self, X):
        return self._clf.predict_proba(X[self._cols].to_numpy())

    def used_features(self) -> set:
        return {"protected_proxy"}


def run_dirty_arm(random_state: int = 0) -> dict:
    """Dirty arm: validates harness EXCLUDES proxy-using models and proxy is a real threat.

    Steps:
      1. Sweep (legit_a, legit_b, protected_proxy) for cart and linear families.
      2. evaluate_policy filters out all proxy-including subsets.
      3. Assert: pa.admissible contains NO model whose used_features() includes
         'protected_proxy' (excluded_proxy_users=True).
      4. Demonstrate proxy is a real threat: fit a proxy-FORCED CART on
         (protected_proxy,) alone and verify |approval_rate_gap| > TAU.
         Also collect any multi-feature swept models that did use the proxy
         and record the max gap across all of them.

    ⚠ SEMANTICS OF dirty_gap_max:
      The forced-proxy model (CART on protected_proxy alone, gap ~0.29) demonstrates
      the proxy's CAPACITY to discriminate — which justifies prohibiting it. It does
      NOT show that a naturally-swept proxy-using model would exceed tau: in this DGP
      the legitimate features carry the signal, so a model handed all features weights
      the proxy near-zero (gap ~0.0075 < tau). The exclusion gate therefore enforces a
      CATEGORICAL prohibition (you used a banned feature), not an observed-disparity
      threshold. Laundering through the proxy requires STEERING a model onto it; it
      does not happen by accident when legitimate signal is available.
      DO NOT cite this dirty-arm result as 'exclusion prevented disparity' — cite it
      as 'exclusion enforces the prohibition; the proxy has capacity to discriminate
      if steered.'

    Returns:
      excluded_proxy_users  bool  -- all swept proxy-users excluded from admissible
      dirty_gap_max         float -- max |gap| among proxy-using models (swept + forced)
      dirty_arm_valid       bool  -- excluded_proxy_users AND dirty_gap_max > TAU
      n_proxy_users_swept   int   -- how many swept models actually used the proxy
      n_excluded            int   -- total models excluded by policy
      excluded_reason_ok    bool  -- all exclusion reasons mention "protected_proxy"
    """
    X, y, protected, mono, policy = make_planted_dataset(random_state=random_state)

    # Step 1: sweep the proxy-INCLUDING subset
    dirty_subsets = (("legit_a", "legit_b", "protected_proxy"),)
    grids = {
        "cart": {"max_depths": (2, 3, 4), "min_samples_leafs": (20,)},
        "linear": {"Cs": (0.05, 0.2, 1.0)},
    }
    all_results = []
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid,
                               feature_subsets=dirty_subsets, monotonic_cst=mono)
        all_results.extend(results)

    # Step 2: apply policy -- proxy-including subsets must be rejected
    pa = evaluate_policy(all_results, policy_constraints=policy)

    # Step 3a: no admissible model may use the proxy
    admissible_proxy_users = [
        sr for sr in pa.admissible
        if "protected_proxy" in sr.fitted_model.used_features()
    ]
    excluded_proxy_users = len(admissible_proxy_users) == 0

    # Verify exclusion reason strings reference the proxy feature
    excluded_reason_ok = all(
        "protected_proxy" in exc.reason
        for exc in pa.excluded
        if "protected_proxy" in exc.spec.feature_subset
    )

    # Step 4a: collect swept models that used the proxy (for gap measurement)
    proxy_using_models = []
    for sr in all_results:
        if sr.fitted_model is not None:
            if "protected_proxy" in sr.fitted_model.used_features():
                proxy_using_models.append(sr.fitted_model)
    # Defensive: include any accidentally admissible proxy users
    for sr in pa.admissible:
        if "protected_proxy" in sr.fitted_model.used_features():
            if sr.fitted_model not in proxy_using_models:
                proxy_using_models.append(sr.fitted_model)

    n_proxy_users_swept = len(proxy_using_models)

    # Step 4b: add the proxy-FORCED model as the unambiguous threat demonstration.
    # The multi-feature swept models have legit_a and legit_b available and may
    # weight the proxy weakly, producing a small gap. The forced model eliminates
    # that ambiguity: it uses ONLY the proxy, so any gap is entirely proxy-driven.
    forced_model = _ProxyForcedModel(X, y, random_state=random_state)
    proxy_using_models.append(forced_model)

    # Measure disparity across all proxy-using models
    gaps = [abs(approval_rate_gap(m, X, protected)) for m in proxy_using_models]
    dirty_gap_max = float(max(gaps)) if gaps else float("nan")

    dirty_arm_valid = (
        excluded_proxy_users
        and not math.isnan(dirty_gap_max)
        and dirty_gap_max > TAU
    )

    return {
        "excluded_proxy_users": excluded_proxy_users,
        "dirty_gap_max": dirty_gap_max,
        "dirty_arm_valid": dirty_arm_valid,
        "n_proxy_users_swept": n_proxy_users_swept,
        "n_excluded": len(pa.excluded),
        "excluded_reason_ok": excluded_reason_ok,
    }


# ---------------------------------------------------------------------------
# COMBINED GATE
# ---------------------------------------------------------------------------

def run_full_control(random_state: int = 0) -> dict:
    """Run both arms and return a combined result dict with a single gate_passed flag.

    gate_passed is True only if:
      - clean arm: cart AND linear B_plain both True (harness recovers clean member)
      - dirty arm: dirty_arm_valid True (proxy users excluded AND proxy is a real threat)
    """
    clean = run_control(random_state=random_state)
    dirty = run_dirty_arm(random_state=random_state)

    clean_arm_passed = bool(clean["cart"]["B_plain"] and clean["linear"]["B_plain"])
    gate_passed = clean_arm_passed and dirty["dirty_arm_valid"]

    return {
        **clean,
        "dirty": dirty,
        "clean_arm_passed": clean_arm_passed,
        "gate_passed": gate_passed,
        "both_arms": True,  # sentinel: assert_gate requires this key
    }


def assert_gate(result: dict) -> None:
    """Raise RuntimeError loudly if the Stage-1 gate did not pass.

    Call after run_full_control(). Safe to call from CI, tests, or any
    script that must not proceed to Stage 2 on a broken harness.

    ⚠ GUARDS AGAINST FOOTGUN: raises RuntimeError if called with a clean-arm-only
    result (from run_control). The sentinel key "both_arms" must be present to
    confirm that both arms were evaluated.
    """
    if "both_arms" not in result:
        raise RuntimeError(
            "assert_gate requires a full-control result (run_full_control), "
            "got a partial result — refusing to certify the gate on the clean arm alone."
        )

    if not result.get("gate_passed", False):
        dirty = result.get("dirty", {})
        clean_arm = result.get("clean_arm_passed", False)
        excluded = dirty.get("excluded_proxy_users", False)
        gap = dirty.get("dirty_gap_max", float("nan"))
        valid = dirty.get("dirty_arm_valid", False)
        gap_str = f"{gap:.4f}" if not math.isnan(gap) else "nan"
        raise RuntimeError(
            "STAGE-1 CONTROL GATE FAILED -- do NOT proceed to Stage 2 or run real data.\n"
            f"  clean_arm_passed              : {clean_arm}\n"
            f"  dirty.excluded_proxy_users    : {excluded}\n"
            f"  dirty.dirty_gap_max           : {gap_str} (must exceed tau={TAU})\n"
            f"  dirty.dirty_arm_valid         : {valid}\n"
            "Fix the harness before running Stage 2."
        )


if __name__ == "__main__":
    res = run_full_control()
    print("\n--- CLEAN ARM ---")
    for fam in ("cart", "linear", "gbm"):
        print(f"  {fam}: {res[fam]}")
    print("\n--- DIRTY ARM ---")
    d = res["dirty"]
    print(f"  excluded_proxy_users  : {d['excluded_proxy_users']}")
    print(f"  n_proxy_users_swept   : {d['n_proxy_users_swept']}")
    print(f"  n_excluded            : {d['n_excluded']}")
    print(f"  excluded_reason_ok    : {d['excluded_reason_ok']}")
    print(f"  dirty_gap_max         : {d['dirty_gap_max']:.4f}  (tau={TAU})")
    print(f"  dirty_arm_valid       : {d['dirty_arm_valid']}")
    print(f"\nGATE PASSED: {res['gate_passed']}")
    assert_gate(res)
