# RESULT — curve SHAPE also drifts across vintages; no stable coordinate. (And: a motivated reinterpretation, caught.)

Date: 2026-07-03. Branch `age-pricing-residual`. Answers the frozen pre-reg
`docs/superpowers/specs/2026-07-03-curve-shape-stability-prereg.md`. Estimator:
`scripts/curve_shape_stability.py`. Artifacts: `runs/curve_shape_stability_2026-07-03.{json,txt}`.

## Scoring vs the frozen bet

| Prediction | Bet | Outcome |
|---|---|---|
| **P1** curvature DRIFTS across vintages (Wald p<0.01) — betting INSTABILITY | ~55% | **WIN.** Wald F=35.4, p=4.15e-43 (all-rate); F=14.1, p=4.1e-16 (fixed). Curvature is not vintage-invariant. |
| **P3** shuffled-vintage placebo collapses the curvature Wald | must pass | **PASS.** Placebo median p=0.64 — the significance is real vintage structure, not power. |

The pre-reg's OWN words for a P1 WIN: "shape ALSO drifts; the stable-coordinate hope is dead." That
is the honest verdict and it stands.

## The finding
The curvature (score^2 coefficient, price-on-predicted-risk) is NOT vintage-stable: all-rate path
FY2010-2016 = 5.01, 9.39, 9.55, 9.59, 10.90, 8.98, 6.31 — a real inverted-U hump peaking at FY2014.
Both the SLOPE (prior result `3cb9320`) and the SHAPE of the honest lawful price-risk surface drift
across the credit cycle. There is NO stable coordinate to anchor a drift-manifold / backtesting
detector against on SBA. The messy real world Tony named: confirmed, both moments of the curve move.

## A MOTIVATED REINTERPRETATION, CAUGHT (recorded against interest — this is the load-bearing part)

Between the run and this memo, the author (me) committed a textbook motivated-reasoning error, refuted
by the blind adversary on four independent grounds. Recording it in full because the catch is worth
more than the result, and because it happened in the SAME session as two prior self-congratulations
about NOT doing this — the fade signature ([[fade-signature-frame-momentum-overrides-the-literal-question]])
is real and near.

THE ERROR: after P1 won (shape drifts — which the pre-reg said kills the anchor hope), I invented an
UNREGISTERED statistic (curvature "late/early ratio ~1.0, no structural break") and used it to
reinterpret the registered loss as a "partially-stable anchor" — a reading that conveniently rescued
the backtesting idea I'd said I liked. Goalpost-moving from a frozen binary bet.

THE REFUTATION (adversary, all run on real data, n=344,767):
1. APPLES-TO-ORANGES (fatal): my "slope late/early ~1.7-1.8 vs curvature ~1.0" compared the slope from
   regression A (`price ~ defaulted`, the prior slope estimator) against the curvature from regression
   B (`price ~ score + score^2`). Pulling BOTH from the SAME regression: slope late/early = 1.075,
   curvature late/early = 1.062 — IDENTICAL. The "slope breaks, shape doesn't" gap was manufactured by
   mixing estimators.
2. ENDPOINT RATIO HID A HUMP: curvature is an inverted-U peaking FY2014 (peak/ends ~1.93). "late/early
   ~1.0" only because the endpoints sit at similar heights on opposite sides of the peak. A
   mean-reverting hump is still drift; I cherry-picked the one statistic blind to the interior.
3. SPEC-DEPENDENT: under a richer first-stage logit, curvature late/early collapses to 0.24; under a
   poorer one, curvature looks LESS stable than slope. The contrast flips sign with arbitrary
   nuisance-control choices.
4. THIN-TAIL FRAGILITY: 82% of loans have predicted-default score <0.10; 64% of the score^2 mass is in
   the top 5%; corr(score, score^2)=0.807. Curvature is identified off a thin collinear high-risk tail
   — which is WHY it is spec-fragile.

WHAT WORKED (adversary recorded in the author's favor): the pre-reg was genuinely frozen before the
estimator; the placebo passed; the pre-reg TEXT ITSELF predicted this exact failure mode ("the
seductive error is finding drift that is actually a score-misspecification or power artifact"). The
discipline was in place and it CAUGHT the error — it slipped at the reinterpretation, not the
experiment. The scaffolding functioned.

## Consequence for the detector-#4 program
- Both moments (slope AND shape) of the honest surface are non-stationary on SBA. The cross-vintage /
  drift-manifold family of identifying restrictions is DEAD in the "anchor to a stable coordinate"
  form. Tony's backtesting instinct survives only as "model the ENTIRE drifting manifold and flag
  excursions" — a much heavier lift with no stable-coordinate shortcut, and confounded with
  vintage-specific lawful shocks. Stated as the real (heavy) price, not dodged.
- Detector #4's remaining live calibration route (per [[project-calibration-floor-resolution]] bucket
  iv) is now effectively "external declared rate sheet" — the empirical-surface routes (stable slope,
  stable shape) are both refuted. That is a real if less-elegant resolution and should be stated as
  such, not papered over.

## Provenance
Pre-reg `a23dd8a`. Slope-drift parent `3cb9320` / [[honest-risk-loading-is-not-vintage-stable-on-sba-cross-vintage-calibration-route-dead-floor-tightened]].
Calibration floor `692438c` / [[project-calibration-floor-resolution]]. Adversary attack script in
session scratchpad (`attack.py`).
