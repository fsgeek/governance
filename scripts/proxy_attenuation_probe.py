#!/usr/bin/env python3
"""Does the proxy measurement loss actually bite the BLINDNESS finding?

Fable point 4 (the reflexive C3 loss): on real data there is no protected
attribute, so "protected-correlated" must be constructed (BISG / HMDA proxy).
The apparatus that measures whether the shuffle-set is protected-concentrated
uses the very protected-inference it audits. Fable: declare it a loss.

BUT the DIRECTION matters and Fable's framing may be too strong for THIS result.
My finding is BLINDNESS (pooled_g_diff ~= 0), not a disparity claim. Classical
measurement-error theory: NON-DIFFERENTIAL error in a binary regressor ATTENUATES
its estimated effect toward zero. So:
  - claiming DISPARITY through a proxy  -> attenuation is FATAL (hides real gap)
  - claiming BLINDNESS through a proxy  -> attenuation is FRIENDLY (true 0 stays
    ~0); the finding is corrupted ONLY by DIFFERENTIAL error (proxy accuracy
    depends on flip status / boundary proximity), which can manufacture spurious
    structure out of a true zero.

This probe DEMONSTRATES both directions on a controlled synthetic case:
  1. Inject a TRUE nonzero g_diff (protected group really does flip more).
  2. Add NON-DIFFERENTIAL proxy noise (Ghat = G flipped w.p. q, independent of
     everything) -> show the measured g_diff attenuates toward 0 as q rises.
     => a disparity claim dies; a blindness claim is SAFE (can't be faked UP).
  3. Add DIFFERENTIAL proxy noise (Ghat accuracy depends on flip status) ->
     show it can manufacture a spurious g_diff from a TRUE ZERO.
     => this is the ONLY proxy regime that threatens the blindness finding.

FROZEN PREDICTION (before run):
  (2) non-diff: measured |g_diff| decreases monotonically toward 0 as q->0.5;
      a true ZERO stays ~0 at every q (cannot be inflated). prior 0.9.
  (3) differential: measured g_diff departs from 0 (the true value) in the
      direction of the differential bias, magnitude growing with the
      flip-status-accuracy gap. prior 0.85.
  Conclusion if both hold: the honest scope is NARROWER than "apparatus stands
  on the floor" -- it is "blindness is robust to non-differential proxy error;
  cite differential-error sensitivity as the real, bounded threat."
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def measured_g_diff(flip: np.ndarray, Ghat: np.ndarray) -> float:
    """P(flip | Ghat=1) - P(flip | Ghat=0)."""
    a = flip[Ghat == 1]; b = flip[Ghat == 0]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    return float(a.mean() - b.mean())


def nondiff_proxy(G: np.ndarray, q: float, rng) -> np.ndarray:
    """Ghat = G with each label independently flipped w.p. q. Non-differential:
    the error does not depend on flip status or anything else."""
    flipmask = rng.random(len(G)) < q
    return np.where(flipmask, 1 - G, G)


def diff_proxy(G: np.ndarray, flip: np.ndarray, q_flip: float, q_noflip: float, rng) -> np.ndarray:
    """Ghat error rate DEPENDS on flip status: q_flip for flippers, q_noflip for
    non-flippers. Differential measurement error."""
    q = np.where(flip == 1, q_flip, q_noflip)
    flipmask = rng.random(len(G)) < q
    return np.where(flipmask, 1 - G, G)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--n", type=int, default=40000)
    ap.add_argument("--g-prev", type=float, default=0.3)
    ap.add_argument("--base-flip", type=float, default=0.30, help="P(flip) baseline")
    ap.add_argument("--true-gap", type=float, default=0.15,
                    help="injected TRUE g_diff: P(flip|G1)-P(flip|G0)")
    ap.add_argument("--out", default="runs/proxy_attenuation_probe.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    n = args.n

    G = (rng.random(n) < args.g_prev).astype(int)

    # --- Case A: TRUE nonzero g_diff (disparity exists) ---
    p_flip = np.where(G == 1, args.base_flip + args.true_gap / 2,
                      args.base_flip - args.true_gap / 2)
    flip_disp = (rng.random(n) < p_flip).astype(int)
    true_gd_disp = measured_g_diff(flip_disp, G)

    # --- Case B: TRUE zero g_diff (blindness) ---
    flip_blind = (rng.random(n) < args.base_flip).astype(int)
    true_gd_blind = measured_g_diff(flip_blind, G)

    qs = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4]
    nondiff_disp, nondiff_blind = [], []
    for q in qs:
        Gh = nondiff_proxy(G, q, rng)
        nondiff_disp.append(round(measured_g_diff(flip_disp, Gh), 4))
        Gh2 = nondiff_proxy(G, q, rng)
        nondiff_blind.append(round(measured_g_diff(flip_blind, Gh2), 4))

    # Differential proxy on the TRUE-ZERO (blindness) case: can it manufacture
    # a spurious g_diff? Vary the flip/noflip accuracy gap at fixed base noise.
    diff_rows = []
    for q_noflip, q_flip in [(0.1, 0.1), (0.1, 0.3), (0.1, 0.4), (0.3, 0.1), (0.4, 0.1)]:
        Gh = diff_proxy(G, flip_blind, q_flip, q_noflip, rng)
        diff_rows.append({"q_noflip": q_noflip, "q_flip": q_flip,
                          "measured_g_diff_on_true_zero": round(measured_g_diff(flip_blind, Gh), 4)})

    out = {
        "true_g_diff_disparity_case": round(true_gd_disp, 4),
        "true_g_diff_blindness_case": round(true_gd_blind, 4),
        "proxy_noise_q": qs,
        "nondiff_measured_on_disparity": nondiff_disp,
        "nondiff_measured_on_blindness": nondiff_blind,
        "differential_on_blindness": diff_rows,
    }
    print(json.dumps(out, indent=2))

    print(f"\n{'='*72}\nREADING\n{'='*72}")
    print(f"DISPARITY case true g_diff = {true_gd_disp:.3f}")
    print(f"  non-diff proxy attenuates it: {nondiff_disp}")
    print(f"  => measuring DISPARITY through a proxy: FATAL (shrinks toward 0).")
    print(f"BLINDNESS case true g_diff = {true_gd_blind:.3f} (~0 by construction)")
    print(f"  non-diff proxy keeps it ~0:  {nondiff_blind}")
    print(f"  => measuring BLINDNESS through a non-diff proxy: SAFE (cannot inflate).")
    print(f"DIFFERENTIAL proxy on the TRUE ZERO:")
    for r in diff_rows:
        print(f"    q_noflip={r['q_noflip']} q_flip={r['q_flip']} -> measured g_diff={r['measured_g_diff_on_true_zero']:+.3f}")
    print(f"  => the ONLY regime that manufactures spurious disparity from a true zero.")
    print(f"     THIS is the real, bounded threat to the blindness finding -- not")
    print(f"     'the apparatus stands on the floor' in general.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
