# RESULT — the honest lawful risk-loading is NOT vintage-stable on SBA 7(a); cross-vintage calibration route is DEAD

Date: 2026-07-03. Branch `age-pricing-residual`. Answers the frozen pre-reg
`docs/superpowers/specs/2026-07-03-cross-vintage-stability-prereg.md`. Estimator:
`scripts/cross_vintage_stability.py`. Artifacts: `runs/cross_vintage_stability_2026-07-03.{json,txt}`.
Blind scientific-integrity adversary run BEFORE this memo (result flatters the discipline-conforming
"I checked before building" narrative — exactly when self-deception peaks). Adversary ran 5
independent checks against the real data; the finding SURVIVED all five. Two adversary corrections
folded in.

## Scoring vs the frozen bet

| Prediction | Bet | Outcome |
|---|---|---|
| **P1** fixed-rate L_v stable (CoV < 0.25, no vintage CI excludes pooled) | ~55% | **LOSE.** Fixed-rate CoV = 0.428; all-rate 0.330. Far above threshold. |
| **P2** drift larger on variable- than fixed-rate (localizes to base-rate mechanism) | ~50% | **LOSE.** Drift is NOT larger on variable (CoV 0.34) than fixed (CoV 0.43) — if anything larger on fixed. Drift is in the risk-pricing itself, not the base-rate environment. |
| **P3** shuffled-vintage placebo dispersion collapses (noise guard) | must pass | **PASS.** Placebo CoV = 0.069 vs real 0.33-0.43. The drift is REAL vintage structure, not estimator noise. |

Two of three frozen sign-bets fell. The load-bearing one (P1) fell decisively.

## The finding (adversary-confirmed 5 ways)

The honest lawful risk-loading L — percentage POINTS of price per unit of realized default rate, net
of lawful controls (loan size, term, guaranteed share, jobs) — is **NOT constant across matured
origination vintages FY2010-2016**. It sits at **~0.28-0.31 pp for FY2010-2013, then steps up to
~0.48-0.64 pp for FY2014-2016** — a near-DOUBLING, and a STEP (at 2013->2014), not a smooth trend.

Confirmed independently by, per the blind adversary:
1. bin-mean regression (the pre-reg estimator): early ~0.29 -> late ~0.51;
2. raw individual-level OLS (no binning): early 0.28 -> late 0.65 (rules out binning-on-X circularity);
3. joint interacted OLS `interest_rate ~ controls + C(fy) + C(fy):defaulted`: slope-equality
   Wald F=50, **p ~ 6e-62**; the 2013->2014 contrast p ~ 8e-08;
4. maturity-EQUALIZED fixed-K-year charge-off horizon (kills the survivorship-edge alternative — and
   it was the strongest one, refuted by SIGN: incomplete late-vintage resolution would ATTENUATE L,
   not inflate it; the jump persists at K=3,5,7yr, K=7: early 0.35 -> late 0.72);
5. invariant across 4 control specs (+NAICS sector, +rate_type, +firm-age FE); fixed-rate-only
   SHARPENS the split (CoV 0.40).

## Two corrections folded in (recorded against interest)

1. **Unit label was wrong.** L is in percentage POINTS, not basis points (the number and CoV are
   correct; only the word was wrong). Fixed in `scripts/cross_vintage_stability.py` docstring.
2. **The `any_vintage_ci_excludes_pooled` clause is under-powered and reads misleadingly.** It shows
   False ("looks stable") while the standard interacted OLS rejects slope-equality at p~6e-62. The
   CoV is the load-bearing evidence; that clause if anything UNDERSTATES the instability. Caveat
   added in-code so no future reader mistakes False there for stability.

## What it means (the un-flattering read, which is the true one)

1. **The cross-vintage identifying restriction is empirically DEAD** in its simple form. You cannot
   calibrate the honest L on a reference vintage and flag deviations on held-out vintages as candidate
   laundering — because the honest L itself moves ~70% across vintages for a LAWFUL reason (credit-
   cycle repricing of realized risk). A detector #4 built on this restriction would flag the
   2013->2014 macro regime shift AS laundering — a false positive baked into the calibration, the
   exact confound shape that killed detectors #1-#3.

2. **This TIGHTENS the category-B calibration-floor verdict** ([[project-calibration-floor-resolution]],
   commit `692438c`). That verdict said `(P0,L)` needs an EXOGENOUS declared restriction. This result
   shows the MOST NATURAL such restriction — "the honest rule is time-stable" — is FALSE on real data.
   The declaration cannot borrow stability from the world; it must be genuinely exogenous (a stated
   rate sheet / policy), because the empirical honest surface is non-stationary across the credit cycle.

3. **It makes the transformation-law rescue LESS available, not more.** The parallax program's
   deliverable 3 wanted to model drift as a known group action and SUBTRACT it. But the drift is a
   STEP (structural break at 2013->2014), not a smooth trend — a break is much harder to subtract as a
   clean change-of-frame group action than a gradient. The seductive "the drift IS the transformation
   law" move (flagged in [[detector-design-theory-rashomon-set-as-parallax-rig-for-a-hidden-subject-frame-cautions]]
   as the session's most seductive frame) is therefore WEAKER here, not a save. Recorded before it
   could be reached for.

## What this does NOT claim
- It does not prove the drift's CAUSE is "lawful macro credit cycle" vs some other omitted mechanism.
  But that cut goes AGAINST the calibration route regardless of cause: whatever moves honest L, it is
  not vintage-invariant, so the restriction imports a confound either way.
- It does not kill detector #4 outright — it kills ONE of its four candidate identifying restrictions.
  The remaining live routes (bucket iv): a genuinely external declared rate sheet, or a NONLINEAR
  declared curve whose SHAPE (not level) is asserted stable — the latter untested and now the
  natural next feasibility question, since the LEVEL/slope is shown non-stationary.

## NEXT (earned, not momentum)
The clean surviving question: is the SHAPE of the honest price-risk curve (its convexity/monotonicity)
vintage-stable even though its SLOPE is not? A restriction on curve SHAPE rather than curve LEVEL is a
weaker, possibly-licensed exogenous assumption. That is the next feasibility test — freeze it before
the estimator, same discipline. If shape is also non-stationary, bucket (iv) collapses to "external
rate sheet only," which is a real (if less elegant) resolution and should be stated as such.
