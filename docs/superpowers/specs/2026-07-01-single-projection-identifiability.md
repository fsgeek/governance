# Single-projection identifiability geometry — BEFORE any estimator

Date: 2026-07-01. Branch `age-pricing-residual`. Frozen design artifact for the FIRST working
detector (single projection) of the Rashomon-parallax program. NO estimator until this analysis
is committed — the last detector (`fairwash_calibration_floor.py`) was built before its identifiability
was checked, read +50bps in a clean world, and died to its own λ=0 guard. This file is the
adversary-before-the-sentence applied to the DESIGN, not the result.

## The question

On ONE lawful-axis surface — per-loan `(price, default, grade G)`, matured window, NO protected
attribute, NO model — is there a statistic that separates an HONEST coarse grade from a LAUNDERED
coarse grade? For a candidate statistic, what family of laundering DGPs is *observationally identical*
to honest under it? Measure-zero family → build the detector. Fat plausible family → that projection
is non-identifiable; find a different light.

## The two worlds (unprotected cohort in focus)

Latent true risk `R ~ U(0,1)`; protected `P ∈ {0,1}`; realized `default ~ Bernoulli(R)` — depends
ONLY on R (P is not a real risk factor). Coarse grade `G = coarsebin(score)`; `price = base + loading·G`.

- HONEST:    `score = R`.        `G = coarsebin(R)`.
- LAUNDERED: `score = R + λ·P`.  `G = coarsebin(R + λ·P)`. Laundering pushes PROTECTED applicants
  into worse bins; `price` still set off the (contaminated) grade.

## RESULT 1 (proven): unprotected-only footprint is NON-IDENTIFIABLE, measure-one.

For unprotected rows, `P = 0`, so `score = R + λ·0 = R` in BOTH worlds — the laundered and honest
DGPs are LITERALLY THE SAME distribution on the unprotected cohort, for every λ. Therefore ANY
statistic computed on unprotected-only rows (including the orthogonal-component / price-⊥-default
test) is identical across honest and laundered. Non-identifiable by construction, exactly — not a
fat-region approximation.

COROLLARY — why the killed detector failed, geometrically: `GUARD 3` (measure on unprotected-only,
so no protected signal leaks) and the DETECTION GOAL are CONTRADICTORY. You cannot detect laundering
from the cohort the laundering provably does not touch. The +50bps at λ=0 was pure grade-gradient
estimator artifact; the near-flatness across λ was the CORRECT answer to a non-identifiable question
(unprotected data does not depend on λ). The guard caught "broken"; this geometry proves it MUST be.

## RESULT 2 (candidate, identifiable): full-cohort bin-price-vs-bin-realized-default decoupling.

Drop GUARD 3. Laundering moves PROTECTED applicants UP into worse bins → it changes each bin's
COMPOSITION. In the laundered world, bin g gains protected applicants pushed up from lower true-risk
R, so the bin's REALIZED default rate is DILUTED (its new members default less than their bin-mates).
Meanwhile they pay the bin's (high) price. So laundered bins are OVER-PRICED relative to their own
realized default — the SBA over-pricing signature — and this is computable WITHOUT the protected
label (you regress price on G and default on G over EVERYONE; the wedge is price-gradient minus
default-justified-gradient). The signal exists BECAUSE protected applicants were laundered in, but
its detection needs only `(price, default, G)`.

This is the orthogonal-component test on the RIGHT cohort (full, not unprotected-only). It is the
identifiable candidate. Its own identifiability must STILL be checked (below) — being identifiable
vs honest is necessary, not sufficient; it must also separate from the two OTHER single-shadow
confounds.

## The three-subject confound (still open, the real work)

A full-cohort bin-price-⊥-default wedge is consistent with THREE subjects:
  (a) upstream laundering (what we want),
  (b) an ordinary UNPRICED lawful risk factor the lender didn't use (bin default varies for a benign
      reason the price ignores),
  (c) grade COARSENESS alone (within-bin risk heterogeneity mechanically decouples flat bin-price
      from continuous realized default).
Result 2 separates from HONEST but NOT yet from (b)/(c). THIS is where single-projection stays
ill-posed and where MOVING THE LIGHT (Rashomon parallax) or the TRANSFORMATION LAW (drift across
frames) must do the work. Frozen deliverable for the parallax step: does a basis of grades with
non-aligned coarseness kill (c), and does the known frame-transformation of the honest surface kill
(b)?

## Frozen decision (pre-estimator)

1. ABANDON the unprotected-only detector — proven non-identifiable (Result 1). Do not resurrect.
2. BUILD the full-cohort bin-price-vs-bin-realized-default wedge as the single working projection
   (Result 2), with a positive control (plant λ, recover the wedge) and a λ=0 null guard.
3. The (b)/(c) confounds are NOT resolved by this single projection — record honestly; they are the
   parallax/transformation-law deliverables, NOT claimed here.
4. Success for THIS artifact = wedge monotone in λ, λ=0 null clean, positive control recovers a
   planted wedge. That proves ONE projection resolves a planted subject vs honest — the first brick.
   It does NOT prove laundering-vs-(b)/(c); that claim is explicitly deferred.
