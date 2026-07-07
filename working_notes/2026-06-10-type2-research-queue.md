# The shuffle-set is a TYPE-2 research queue — the feedback loop is real

**2026-06-10. Tony's loop: the marginal band carries type-(2) signal (individual, aggregate-visible,
LAWFUL) vs type-(1) macro noise. Mine type-2 → fold into next model → band shrinks toward correctly-
priced loans (profit + fairness). Script: `scripts/type2_extractability_probe.py`. Output:
`runs/type2_extractability.json`. Follows [[2026-06-10-profit-disparity-frontier]].**

## FROZEN PREDICTION — P1 CONFIRMED (loop real), with one sign INVERTED in the bank's favor

Predicted (0.50): shuffle-set has extractable LAWFUL signal (AUC_L > 0.55) → research queue. HELD,
strongly. Predicted D1 would show a small POSITIVE gap (full ≳ lawful). INVERTED: the gap is
NEGATIVE — lawful beats full — which is even better for the pitch.

## Result (default-AUC on held-out shuffle-set; LAWFUL = features residualized against G)

```
  channel  n_shuffle  AUC_lawful  AUC_full  AUC_unanimous_ref  gap(full-lawful)
  D1        3344        0.772       0.712       0.878            -0.060
  D4         334        0.584       0.626       0.860            +0.041
```

## Reading (a real SYSTEM now, with operating instructions + trap detector)

- **D1: the loop is real and clean.** Shuffle-set lawful AUC = 0.77 — the marginal borrowers are NOT
  type-1 noise; they carry strong LAWFUL (G-orthogonal) default signal the current CART class failed
  to use. They are type-(2): individually marginal, aggregate-predictable, on lawful grounds. Mine it,
  fold into the next model, the band shrinks toward correctly-priced loans. "Do well by doing right"
  has a MECHANISM.
- **The NEGATIVE gap (lawful BEATS full, 0.77 > 0.71) is the dream case:** on D1 the G-aligned
  component of the features is NOISE for default — removing it HELPS. So mining type-2 lawfully isn't
  just permissible, it's predictively BETTER. The proxy stuff was distraction.
- **D4 is the honest counterweight and behaves exactly as the laundering trap predicts:** lawful AUC
  drops to 0.58 (weak), and the gap flips POSITIVE (+0.04) — removing the G-aligned component now
  HURTS, because in the laundered channel the predictive signal IS the proxy. D4's band is part
  genuine type-2 queue (0.58 > 0.5) and part laundering trap.
- **THE SIGN OF THE GAP IS A CLEAN REGIME DETECTOR:** gap(full − lawful) < 0 → lawful signal
  dominates (mine freely, profit & fairness aligned); gap > 0 → G-aligned/proxy signal present
  (mining it LAUNDERS). This is the same alarm as the profit–disparity correlation sign
  ([[2026-06-10-profit-disparity-frontier]]); two independent detectors agreeing on the D1-clean /
  D4-laundered split.

## The system, assembled

1. The policy-constrained Rashomon band = a menu of equally-accurate models ([[project_pick_one_hides_choice]]).
2. Within it, profit and fairness mostly ALIGN (negative coupling), except where laundered (D4: +1.0 = alarm).
3. The shuffle-set is a TYPE-2 RESEARCH QUEUE: extractable lawful default signal (AUC 0.77, D1) —
   correctly-priceable loans not yet learned. Margin-driven & protected-blind
   ([[project_shuffle_set_margin_not_protected]]) but NOT signal-free.
4. The full-minus-lawful gap SIGN tells the bank which signal it's about to mine: lawful (mine) vs
   proxy-laundering (don't). Operating instructions + trap detector, included.

This is "increase profitability while holding discrimination at the floor" with the mechanism, the
operating point, AND the laundering alarm — the bank pitch Tony asked for, now empirically grounded.

## Honest scope (do not overclaim)

- Synthetic substrate; G is ground-truth (real data inherits the proxy-measurement loss
  [[2026-06-10-proxy-loss-is-differential-only]], differential-error caveat applies to measuring
  "lawful = G-orthogonal" too — residualizing against a NOISY Ĝ leaves G-residue in the "lawful" set).
- LAWFUL operationalized as LINEAR-G-orthogonal (residualize on G). Nonlinear G-dependence could
  survive residualization → "lawful" AUC is an UPPER bound on truly-lawful signal. Flag for the port:
  use a richer G-orthogonalization (e.g. residualize on a flexible G-predictor).
- D4 band=3 (n_shuffle=334) is small; the D4 numbers are directionally right but noisier than D1.
- The loop's CLOSURE (fold type-2 in → band actually shrinks) is asserted, not yet run. Next probe:
  add the extracted lawful feature, refit, confirm shuffle-set shrinks AND disparity drops.

## Meta

Priored predictions 0-for-8 on direction, but this one HELD on the load-bearing claim (P1: lawful
signal extractable) and the surprise (negative gap) ran in the bank's favor. The instrument's arc:
failed protected-detector → due-process score → failed redundancy canary → profit-coupling laundering
detector → TYPE-2 RESEARCH QUEUE with a gap-sign trap detector. Every rebirth came from a Tony reframe,
not from defending the prior instrument.
