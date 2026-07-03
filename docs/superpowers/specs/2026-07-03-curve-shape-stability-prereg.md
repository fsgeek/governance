# PRE-REGISTRATION — is the SHAPE of the honest price-risk curve vintage-stable, even though its SLOPE is not?

Date: 2026-07-03. Branch `age-pricing-residual`. FROZEN BEFORE the estimator. Follow-on to
`docs/superpowers/specs/2026-07-03-cross-vintage-stability-result.md` (commit `3cb9320`), which
established that the honest risk-loading SLOPE L is NOT vintage-stable on SBA 7(a) (near-doubling,
structural step 2013->2014, adversary-confirmed 5 ways).

## Why this test, and why it comes NOW (not parked)

The slope-drift result killed the "calibrate L on a reference vintage" route. But it does NOT kill the
weaker question that Tony's backtesting instinct points at: even if the LEVEL/slope of honest pricing
moves across the credit cycle, is there a STABLE COORDINATE in the honest surface — specifically, is
the SHAPE of the price-vs-realized-risk curve (its curvature / convexity, independent of its overall
slope) invariant across vintages? A restriction on curve SHAPE is strictly WEAKER than a restriction
on curve LEVEL, and might survive where the level restriction died.

This is the PREREQUISITE for the larger drift-manifold / backtesting idea, not a parked afterthought:
that idea (laundering = drift that doesn't match the honest drift-shape) only has legs if there is a
stable something for excursions to be measured against. If SHAPE is stable while slope drifts, that
stable coordinate is the anchor the backtesting frame needs. If SHAPE is ALSO non-stationary, the
drift-manifold needs a much richer model and bucket-(iv) collapses toward "external rate sheet only."
Either answer advances the detector-#4 program.

## The estimator constraint I must respect (found by reading the prior run's SEs, not its headline)

The prior run's per-vintage bin-mean L_v estimates carry SEs of 0.18-0.51 — as large as the point
estimates. A CoV of 7 noisy points is itself noisy (the placebo guard is what made the slope-drift
finding trustworthy, not the bin-mean CoV magnitude). A per-vintage CURVATURE estimate off the same
10 bins would be hopelessly under-powered — second-order terms are noisier than first-order. Therefore
this test MUST use the high-power INTERACTED INDIVIDUAL-LEVEL OLS the blind adversary used to confirm
the slope drift (p~6e-62), NOT a per-vintage bin regression. Curvature enters as an explicit
polynomial (or spline) term in realized risk, interacted with vintage.

## Design

Individual-level OLS on the matured window FY2010-2016, all rate types (fixed-rate cell reported
separately as the base-rate-confound-weakest check, per the prior pre-reg):

    interest_rate ~ lawful_controls + f(risk) + C(fy) + C(fy):f(risk)

where `f(risk)` captures BOTH slope and curvature. Two operationalizations, both run:
  (A) POLYNOMIAL: f(risk) = defaulted + I(defaulted^2)-analog. Since `defaulted` is 0/1 at the
      individual level, curvature can't come from a single loan; use a per-loan CONTINUOUS risk
      score = the net-of-controls predicted default (from a first-stage logit of defaulted on lawful
      controls), then enter score + score^2, each interacted with C(fy). The vintage-varying
      coefficient on score = slope L_v (drift already established); the coefficient on score^2 =
      CURVATURE k_v. SHAPE-stability = is k_v vintage-invariant?
  (B) NORMALIZED-SHAPE: within each vintage, standardize the fitted price-risk curve to unit slope
      (divide by L_v), then compare the standardized curves' second-derivative across vintages. This
      separates "shape" from "level/slope" explicitly — a curve can drift in slope but keep its shape.

## FROZEN PREDICTIONS (falsifiable, scored WIN/LOSE, no hedge)

Prior recalibrated DOWN from the slope test: Tony's stated prior is that lawful discrimination drifts
because nobody optimizes to hold it still, and the slope test confirmed drift. So I do NOT bet shape
is stable by default. Honest split prior:

- **P1 (curvature drift, ~55% — note: betting shape is NON-stable, the OPPOSITE default from last
  time, because the slope result + Tony's moving-target prior both point at pervasive drift):** the
  curvature term k_v is NOT vintage-invariant — a joint Wald test of `C(fy):score^2` equality across
  vintages REJECTS at p < 0.01. WIN => shape ALSO drifts; the stable-coordinate hope is dead; the
  drift-manifold needs a richer model. LOSE (curvature IS stable, Wald p > 0.01) => a genuinely
  surprising and USEFUL result: a stable shape coordinate exists under a drifting slope — the anchor
  the backtesting frame needs.

- **P2 (relative magnitude, descriptive):** the curvature's coefficient of variation across vintages
  is compared to the slope's CoV (0.33-0.43). Report whether shape drifts MORE or LESS than slope,
  regardless of the significance verdict. No bet; characterization.

- **P3 (placebo, must PASS):** shuffled-vintage labels collapse the curvature-drift Wald statistic
  toward its null distribution (the interaction becomes non-significant under shuffle). Guards
  reading power-driven significance (millions of rows make tiny effects significant) as real drift.
  If the shuffle ALSO rejects, the "drift" is a spec artifact and P1 is uninterpretable.

## What this does NOT claim
- A stable shape (P1 LOSE) is NECESSARY, not sufficient, for the backtesting/drift-manifold route: it
  says a stable coordinate EXISTS, not that off-shape excursions are provably laundering (still
  confounded with vintage-specific lawful shocks to shape). Sufficiency is downstream, flagged.
- Continuous risk score from a first-stage logit is a DECLARED construction (goes in the light path);
  its misspecification is a confound this test does not resolve. Declared, not hidden.

## Scoring
P1/P2/P3 scored explicitly against the frozen bet. Blind adversary BEFORE the memo — and this time
the specific self-deception to guard is the OPPOSITE of last time: last time I over-bet stability;
here I've bet INSTABILITY, so the seductive error is finding drift that is actually a
score-misspecification or power artifact. The adversary must attack in that direction.
