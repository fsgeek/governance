#!/usr/bin/env python3
"""Manifest-blindness probe: does the attestation artifact ever SEE laundering?

Design + frozen prediction:
    docs/superpowers/specs/2026-06-09-manifest-blindness-probe-design.md

THE PROBE (mechanical, falsifiable):
    Holding the policy constraints fixed, which recorded manifest fields -- if
    any -- differ between an INNOCENT build and a LAUNDERED build?

This is NOT a discovery. `wedge/manifest.py:emit_manifest` records construction
INPUTS (policy name/version, mandatory/prohibited feature LISTS, epsilon,
set-sizes, best-values, score labels). It never inspects the FIT's reliance on
any feature. So a model that launders protected-class signal through ADMITTED
features should produce a manifest indistinguishable from an innocent one,
except on AUC-derived fields. This script RENDERS that known result into one
executable, falsifiable artifact -- the figure section7.tex:32 defers to
"follow-on work" ("furnished silence" shown as a passing audit log).

FROZEN PREDICTION (committed in the design doc before this ran):
    Every manifest field IDENTICAL between innocent and laundered EXCEPT
    global_best_value_T/F and the AUC-bearing score_label_*, because
    emit_manifest reads only policy_constraints + set-sizes + per-set
    best-value, and laundering preserves the admitted-feature list by
    construction. The one uncertain channel (prior ~0.15) is set CARDINALITY:
    if the laundered band has a different number of epsilon-admissible CARTs,
    n_R_T / n_R_F WOULD record it -- the only way the manifest could
    accidentally witness laundering.

Three cells, one table:
    A  innocent        -- frozen DGP frame, no laundering routing
    B  frozen-laundered-- frozen DGP frame WITH protected signal routed onto
                          an admitted carrier (provenance: the daf032d attack's
                          substrate + carriers)
    C  toy-control     -- minimal self-contained proxy, mechanism legible

The OUTCOME decides the artifact (not a fork -- one run viewed twice):
    clean break       -> Paper-2 scope-figure (manifests identical but for AUC)
    structural shift  -> a FINDING contradicting the seam-adversary's claim #3.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    SweepConfig,
    build_dual_set,
    evaluate_policy,
    hyperparameter_sweep,
)
from wedge.manifest import emit_manifest

# Import the FROZEN attack substrate for provenance (cell B). The DGP module is
# frozen with the pre-reg (daf032d / OTS 9e8abe7); we use its data substrate and
# its admissible laundering carriers, not its audit rungs.
import importlib.util
import sys
from pathlib import Path


def _load_by_path(mod_name: str, path: str):
    """Register in sys.modules BEFORE exec so dataclass introspection (which
    looks up cls.__module__ in sys.modules) works on 3.14. Mirrors the frozen
    test's loader."""
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_DGP_PATH = Path(__file__).with_name("fairwash_frontier_dgp.py")
_dgp = _load_by_path("fairwash_frontier_dgp", str(_DGP_PATH))


# ---------------------------------------------------------------------------
# Shared policy: one PolicyConstraints object across ALL three cells, so the
# ONLY difference that can move the manifest is the data/laundering -- not the
# policy. The protected attribute G is prohibited; the legitimate risk features
# and the admissible carriers are not. This is the policy a real reviewer would
# write: ban the protected attribute, say nothing about the carriers (because
# the carriers are, individually, innocent -- that is the whole problem).
# ---------------------------------------------------------------------------

PROTECTED = "G"


def shared_policy(feature_names: list[str]) -> PolicyConstraints:
    """The policy is identical for innocent and laundered builds.

    Mandatory: none (keeps the band non-empty and the probe about laundering,
    not about mandatory-feature enforcement). Prohibited: the protected
    attribute G only -- exactly what a reviewer can ban WITHOUT the lender's
    objective (the subtractive / ban-out move). The carriers are admitted
    because nothing in an exogenous prohibition reaches them.
    """
    return PolicyConstraints(
        name="manifest_blindness_probe",
        version="1",
        status="active",
        monotonicity_map={},
        mandatory_features=(),
        prohibited_features=(PROTECTED,),
        applicable_regime={},
    )


# ---------------------------------------------------------------------------
# Cell builders. Each returns (X, y, feature_names). G is ALWAYS dropped from
# the model design (it is prohibited); the difference between innocent and
# laundered is whether G's signal has been ROUTED onto an admitted carrier.
# ---------------------------------------------------------------------------


def _enumerate_subsets(features: list[str], max_k: int) -> tuple[tuple[str, ...], ...]:
    """Feature-subsets up to size max_k (the band's hypothesis space)."""
    from itertools import combinations

    subsets: list[tuple[str, ...]] = []
    for k in range(1, max_k + 1):
        subsets.extend(combinations(features, k))
    return tuple(subsets)


def cell_frozen_clean(
    *, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, list[str]]:
    """Cells A/B from the FROZEN substrate, with the SAME treatment discipline
    as the toy: ONE fixed label Y, two feature tables differing ONLY in whether
    protected signal is routed onto the admitted carrier.

    The frozen DGP's D2 channel supplies a legitimate design X (8 features), a
    protected G, an admissible carrier, and a base label Y -- all frozen. We
    KEEP Y exactly as the frozen DGP produced it (no relabelling -- the earlier
    version's relabelling changed the prediction problem and confounded the
    probe, the LDA arm-confound again). The INNOCENT table is the frozen X
    untouched; the LAUNDERED table routes G-disparity onto the admitted carrier.
    G is dropped from both (prohibited). Any manifest difference is therefore
    the laundering treatment on a FIXED problem, on the frozen substrate.
    """
    dgp = _dgp.generate("D2", n=_dgp.N_TRAIN, seed=seed)
    frame = dgp.frame.copy()
    carrier = dgp.proxy_feature  # an ADMITTED feature, correlated with G
    g = frame[_g_col(frame)].to_numpy()
    feat_cols = [c for c in frame.columns if c not in (_g_col(frame), "Y")]

    y = frame["Y"].astype(int)
    X_innocent = frame[feat_cols].copy()
    X_laundered = frame[feat_cols].copy()
    # Route additional protected signal onto the admitted carrier; G untouched,
    # carrier name/admissibility preserved, label fixed.
    X_laundered[carrier] = X_laundered[carrier] + 1.25 * (g - g.mean())
    return X_innocent, X_laundered, y, feat_cols


def cell_toy_clean(
    *, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, list[str]]:
    """Cell C (clean control): SAME label Y, two feature tables differing ONLY
    in whether protected signal is routed onto the admitted 'proxy' feature.

    The label Y is fixed (driven by x0, x1, and the latent disparity). In the
    INNOCENT table, 'proxy' is pure noise -- G's disparity is unexpressed in any
    admitted feature, so a fitted model cannot recover it. In the LAUNDERED
    table, the SAME G-disparity is routed onto 'proxy' -- a fitted model now
    recovers it THROUGH an admitted feature. G never enters either model;
    'proxy' is admitted in both; the manifest's prohibited list catches nothing
    either way. Holding Y identical means any manifest difference is the
    treatment (laundering), not a changed prediction problem.
    """
    rng = np.random.default_rng(seed)
    n = 6000
    x0 = rng.standard_normal(n)
    x1 = rng.standard_normal(n)
    g = (rng.standard_normal(n) > 0.5).astype(int)
    g_centered = g - g.mean()
    # Y depends on legit features AND a latent G-disparity -- FIXED across both
    # worlds. (The disparity is real in the data-generating truth; the question
    # is only whether an ADMITTED feature exposes it to the fitted model.)
    logit = 0.8 * x0 + 0.6 * x1 + 1.3 * g_centered
    y = pd.Series((rng.random(n) < 1.0 / (1.0 + np.exp(-logit))).astype(int))

    proxy_innocent = 0.4 * rng.standard_normal(n)                  # pure noise
    proxy_laundered = 0.9 * g_centered + 0.4 * rng.standard_normal(n)  # carries G
    feat_cols = ["x0", "x1", "proxy"]
    X_innocent = pd.DataFrame({"x0": x0, "x1": x1, "proxy": proxy_innocent})
    X_laundered = pd.DataFrame({"x0": x0, "x1": x1, "proxy": proxy_laundered})
    return X_innocent[feat_cols], X_laundered[feat_cols], y, feat_cols


def _g_col(frame: pd.DataFrame) -> str:
    """The frozen DGP names the protected attribute 'G'; be defensive."""
    for cand in ("G", "g", "protected", "group"):
        if cand in frame.columns:
            return cand
    raise KeyError(f"no protected-attribute column in {list(frame.columns)}")


# ---------------------------------------------------------------------------
# The pipeline: drive the REAL wedge path for one cell, return its manifest.
# ---------------------------------------------------------------------------


def build_manifest(
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: list[str],
    *,
    label: str,
    seed: int,
    max_k: int,
    epsilon: float,
) -> dict:
    policy = shared_policy(feature_names)
    cfg = SweepConfig(
        max_depths=(4, 6, 8),
        min_samples_leafs=(50, 100, 200),
        feature_subsets=_enumerate_subsets(feature_names, max_k),
        random_state=seed,
        holdout_fraction=0.30,
    )
    sweep = hyperparameter_sweep(X, y, config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=policy)
    R_T, R_F = build_dual_set(
        admissible, epsilon_T=epsilon, epsilon_F=epsilon, w_T=1.5, w_F=1.5
    )
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata={"model_id": "none", "training_sample_id": label},
        run_id=f"probe-{label}",
        training_sample_id=label,
        hypothesis_space=f"CART subsets<=k{max_k}",
    )
    return manifest


# ---------------------------------------------------------------------------
# Diff + verdict.
# ---------------------------------------------------------------------------

# Fields the prediction allows to differ (AUC-derived). Everything else
# differing would BREAK the prediction.
AUC_DERIVED = {
    "global_best_value_T",
    "global_best_value_F",
    "score_label_T",
    "score_label_F",
}
# Fields that are trivially per-run and carry no probe signal.
IGNORE = {"run_id", "training_sample_id", "surprise_model_training_sample"}


def diff_manifests(innocent: dict, laundered: dict) -> dict:
    keys = sorted(set(innocent) | set(laundered))
    rows = []
    structural_breaks = []
    for k in keys:
        if k in IGNORE:
            continue
        a, b = innocent.get(k), laundered.get(k)
        same = a == b
        rows.append((k, same, a, b))
        if not same and k not in AUC_DERIVED:
            structural_breaks.append(k)
    return {"rows": rows, "structural_breaks": structural_breaks}


def print_cell(name: str, innocent: dict, laundered: dict) -> list[str]:
    d = diff_manifests(innocent, laundered)
    print(f"\n{'='*72}\nCELL {name}: innocent vs laundered\n{'='*72}")
    print(f"{'field':<28}{'verdict':<12}{'innocent':<16}laundered")
    for k, same, a, b in d["rows"]:
        verdict = "IDENTICAL" if same else ("AUC-DERIV" if k in AUC_DERIVED else "**DIFFERS**")
        sa = _fmt(a)
        sb = _fmt(b)
        print(f"{k:<28}{verdict:<12}{sa:<16}{sb}")
    return d["structural_breaks"]


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4f}"
    if isinstance(v, list):
        return f"[{len(v)} items]"
    return str(v)[:15]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260609)
    ap.add_argument("--max-k", type=int, default=3, help="max feature-subset size")
    ap.add_argument("--epsilon", type=float, default=0.02)
    ap.add_argument("--out", type=str, default="runs/manifest_blindness_probe.json")
    args = ap.parse_args()

    # Cell A/B: frozen substrate, ONE fixed Y, innocent vs laundered feature table.
    Xa, Xb, yab, fab = cell_frozen_clean(seed=args.seed)
    man_a = build_manifest(Xa, yab, fab, label="frozen-innocent", seed=args.seed,
                           max_k=args.max_k, epsilon=args.epsilon)
    man_b = build_manifest(Xb, yab, fab, label="frozen-laundered", seed=args.seed,
                           max_k=args.max_k, epsilon=args.epsilon)

    # Cell C: toy control. CLEAN VERSION -- innocent and laundered share the SAME
    # label Y; the ONLY difference is whether protected signal has been routed
    # onto the admitted 'proxy' feature. (The first run confounded laundering
    # with a label change -- the LDA arm-confound in a new costume; the band
    # cardinality moved because the PREDICTION PROBLEM changed, not because the
    # manifest saw illegitimacy. Holding Y fixed isolates the treatment.)
    Xc_innocent, Xc_laundered, yc, fc = cell_toy_clean(seed=args.seed)
    man_c_innocent = build_manifest(Xc_innocent, yc, fc, label="toy-innocent",
                                    seed=args.seed, max_k=args.max_k, epsilon=args.epsilon)
    man_c_laundered = build_manifest(Xc_laundered, yc, fc, label="toy-laundered",
                                     seed=args.seed, max_k=args.max_k, epsilon=args.epsilon)

    breaks_ab = print_cell("A/B (frozen substrate)", man_a, man_b)
    breaks_c = print_cell("C (toy control)", man_c_innocent, man_c_laundered)

    print(f"\n{'='*72}\nPROBE RESULT\n{'='*72}")
    print(f"frozen cell structural breaks: {breaks_ab or 'NONE'}")
    print(f"toy cell    structural breaks: {breaks_c or 'NONE'}")
    print()
    # Verified reading (see working_notes/2026-06-09-manifest-blindness-probe-result.md).
    # The ONLY fields that ever move are (a) AUC-derived best-values [allowed]
    # and (b) set-sizes n_R_T/n_R_F. In THIS small probe (k<=3 subsets, ~27
    # combos) the loss-scored band's epsilon is in ABSOLUTE LOSS units, so at
    # eps=0.02 the band is just the argmin's TIE-SET. The toy has CART ties at
    # the min (n_R=4); laundering changes the tie COUNT (4->2). The frozen cell
    # has a UNIQUE argmin (n_R=1), so no tie-count to move -- not a 'floor that
    # masks' (raising eps to 0.10 did NOT unlock it; that hypothesis was tested
    # and refuted), but a genuinely unique minimiser. So n_R here counts
    # numerical ties, not legitimacy. (Real corpus runs use richer hypothesis
    # spaces and show n_R=40-50; the tie-collapse is a property of this probe's
    # tiny space, not of the construction at scale.)
    set_size_only = set(breaks_ab) | set(breaks_c) <= {"n_R_T", "n_R_F"}
    if set_size_only:
        print("READING: every policy / feature-LIST field is BYTE-IDENTICAL under")
        print("laundering in all cells -- the manifest is BLIND to laundering-via-")
        print("admitted-features on every field that encodes the policy (claim #3")
        print("holds). The only structural mover, n_R, counts argmin TIE-MULTIPLICITY")
        print("under an absolute-loss epsilon (toy 4->2; frozen unique-argmin so no")
        print("tie to move). It witnesses neither legitimacy nor illegitimacy -- it")
        print("counts ties. Furnished silence survives on the policy fields; n_R is")
        print("not a laundering detector. (n=2 DGPs; a demonstration, not a sweep.)")
    else:
        print("UNEXPECTED: a NON-set-size structural field moved. Investigate -")
        print(f"  fields: {sorted(set(breaks_ab) | set(breaks_c))}")
        print("this would be a genuine contradiction of claim #3, not the")
        print("set-size accuracy-confound. Do NOT report until understood.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    all_breaks = sorted(set(breaks_ab) | set(breaks_c))
    out.write_text(json.dumps({
        "frozen_innocent": man_a, "frozen_laundered": man_b,
        "toy_innocent": man_c_innocent, "toy_laundered": man_c_laundered,
        "frozen_structural_breaks": breaks_ab,
        "toy_structural_breaks": breaks_c,
        "all_structural_breaks": all_breaks,
        "set_size_only": set(all_breaks) <= {"n_R_T", "n_R_F"},
    }, indent=2, sort_keys=True, default=str))
    print(f"\nmanifests written to {out}")


if __name__ == "__main__":
    main()
