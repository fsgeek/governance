# Risk-justified-price MAP — a dimensionally-coherent wedge, BEFORE detector #4

Date: 2026-07-01. Branch `age-pricing-residual`. Frozen design artifact, produced per the FROZEN
NEXT note in `c1c0a1e` (detector #3's failure commit): detector #3 failed GUARD A because its
"declared risk price" was a single scalar (bps per unit realized-default, fit by
`price ~ default` OLS on the honest world) applied to a `price_gap` that scales with bin INDEX
RANGE while `def_gap` is a bounded [0,1] probability difference. Not a confound — a malformed,
unit-incommensurable statistic. This document is the adversary-before-the-sentence pass on the
REPLACEMENT statistic, before any estimator is built on it. No Python was run to build a detector;
the numerical checks below are diagnostic-only, run to verify the map's construction, not to
produce a result.

## Recap: what exactly broke, verified against primary sources

Read directly: `docs/superpowers/specs/2026-07-01-single-projection-identifiability.md`,
`scripts/single_projection_detector.py`, `git show c1c0a1e`, `runs/single_projection_detector_2026-07-01.txt`.

The killed wedge was `wedge_g = price_gap_g - def_gap_g * just_per_default`, where:
- `price_gap_g = price_mean(g) - price_mean(ref_g)`. Because `price = base + loading*G` (a step
  function of bin INDEX, not of any bounded quantity), `price_gap` scales with the INDEX RANGE
  spanned by non-reference bins — which grows every time you cut the same population into more
  bins (more bins = wider index range for the same total price range... in fact in the detector's
  own DGP price range itself scales with bin count, since `loading` is fixed per index step).
- `def_gap_g = default_mean(g) - default_mean(ref_g)`, a difference of two quantities each bounded
  in [0,1], hence itself bounded in [-1,1] regardless of bin count.
- `just_per_default` is a SINGLE scalar (bps per unit default probability), estimated once by
  `OLS(price ~ default)` on the lambda=0 honest world at 5 bins, then reused unchanged at every
  bin count.

Empirically reproduced here (diagnostic-only) on the exact killed-detector DGP: at bins=5,
`price_gap` ranges [-60, +180]; at bins=100, `price_gap` ranges roughly 20x wider, while `def_gap`'s
range is materially stable (~[-0.35, +0.62] at every bin count, since it is pinned to the true
`R -> default` relationship). A single scalar slope calibrated at one granularity cannot track a
target whose scale is a moving function of bin count. That is the whole failure — confirmed by
reproducing the honest-world wedge at bins=5 and watching `price_gap`'s span balloon.

**Second, independent mechanism found during this design pass (not previously recorded):**
`OLS(price ~ default)` fit on INDIVIDUAL-LEVEL rows (not bin means) suffers severe attenuation
bias. Diagnostic run: true honest DGP `price = base + loading*R` with `loading=300`; individual-row
`OLS(price ~ default)` recovers a slope of **95.5** — nearly identical to the killed detector's
95.6, and nowhere near the true 300. `default` is a noisy Bernoulli(R) draw, not R itself; regressing
a downstream variable on a noisy binary realization of the true driver attenuates the coefficient
toward zero by a factor governed by Var(R)/Var(default-as-continuous-proxy). This means detector #3's
"declared" price was not merely applied at the wrong granularity — it was ALSO a structurally biased
estimate of the true price-per-risk relationship, estimated by regressing on the wrong (noisy,
binary) variable instead of the latent quantity or its unbiased bin-level estimate. Two distinct
bugs stacked in one scalar.

## Part 1 — the dimensionally-coherent map

**Definition.** Declare a full pricing CURVE, not a scalar:

```
risk_justified_price(d) = P0 + L * d,           d in [0,1]
```

where `d` is a REALIZED DEFAULT RATE (a bounded [0,1] quantity — either an individual probability
estimate or, operationally, a bin's realized default frequency, which is a consistent estimator of
the bin's mean latent risk), and `(P0, L)` are DECLARED constants representing a lender's stated
(or regulator-hypothesized) price-per-unit-of-realized-risk schedule: `P0` = the price charged to a
zero-risk borrower, `L` = bps charged per unit of default probability. This is dimensionally a
price-per-probability slope over a BOUNDED domain — the same kind of object a real underwriting
policy would state ("we charge X bps per point of expected loss"), not a regression coefficient
backed into from binned, index-scaled data.

The per-bin wedge is then:

```
wedge_g = price_mean(g) - risk_justified_price(default_mean(g))
        = price_mean(g) - (P0 + L * default_mean(g))
```

and the footprint is the population-weighted mean of `wedge_g` over bins (or, better — see Part 3 —
computed at the INDIVIDUAL level and only aggregated for reporting, not estimated from bin means).

**Why this fixes the incommensurability, concretely — what changed vs the killed scalar-slope
approach:**

1. **The right-hand side is now a function of a BOUNDED input (`d in [0,1]`), evaluated pointwise**,
   not a fixed scalar multiplied against an unbounded bin-index gap. `price_gap` (LHS, unbounded
   with bin count in the old construction) is replaced entirely — there is no `price_gap` term.
   `price_mean(g)` is compared directly against `risk_justified_price` EVALUATED AT `default_mean(g)`,
   not against a step multiplied by an index difference. The map absorbs the "which bin" question
   into ITS ARGUMENT (`d`), and `d` does not grow with bin count — it is confined to [0,1] by
   construction, regardless of how many bins you cut.
2. **`(P0, L)` are declared once, at the finest resolution the domain admits (the individual level,
   or equivalently the R-continuum) and applied UNCHANGED at every coarser aggregation**, rather
   than re-estimated per bin-count run. Because `d` is comparable across granularities (it is always
   a [0,1] rate), the SAME map is valid input-for-input at any bin count — there is no re-calibration
   step that could reintroduce a granularity dependence.
3. **`(P0, L)` must be obtained from a source that is NOT attenuated by the noisy binary `default`
   outcome.** The killed detector's fatal error (per the second mechanism found above) was fitting
   `price ~ default` on raw individual rows. The fix: calibrate `(P0, L)` against `default_mean`
   computed at a FIXED, sufficiently fine partition (bin-level realized-frequency, which is a
   consistent, asymptotically unbiased estimator of the bin's mean latent risk as bin population
   grows) — not against the raw per-row binary indicator. This is a bias-of-estimation fix,
   independent of and in addition to the dimensional fix in points 1-2.

**Diagnostic verification (not a detector run — sanity-checking the construction only).** Built a
throwaway honest-world generator with a genuinely continuous underlying price rule
(`price` set from the bin-mean of a continuous score, `base=500, loading=300`), and evaluated the
map `risk_justified_price(d) = 500 + 300*d` against bin means at bins = 5, 10, 20, 50:

```
bins   pop-weighted mean wedge (lambda=0, honest)
  5    -0.365
 10    -0.365 (bin-level values differ by bin but pop-weighted mean stable)
 20    -0.365
 50    -0.365
```

Population-weighted mean wedge is **stable to 3 decimals across a 10x change in bin count** — a
sharp contrast with the killed statistic's 102 -> 2952 explosion over the same kind of sweep. The
small residual (-0.365, not exactly 0) is attributable to finite-sample noise in bin-level
`default_mean` as an estimator of bin-mean-R (verified: it does not grow with bin count, consistent
with sampling noise rather than a structural pedestal). Re-run with lambda in {0, 0.1, 0.2, 0.4} at
bins in {5, 20}: pop-weighted wedge is IDENTICAL across bin counts at each fixed lambda (8.658 at
lambda=0.1 for both 5 and 20 bins; 17.681 at lambda=0.2 for both; 35.727 at lambda=0.4 for both) and
monotonically increasing in lambda. This is the qualitative signature detector #3 was supposed to
have and did not.

## Part 2 — is the honest-world wedge EXACTLY zero by construction, or only empirically small?

**Claim (weaker than "proof," stated honestly): the wedge is zero BY CONSTRUCTION only under a
calibration assumption that must be stated as a modeling choice, not derived from data. It is NOT a
theorem-grade zero the way Result 1 in the identifiability spec is a theorem-grade non-identifiability.**

Walk-through of what "zero by construction" would require and where it actually comes from:

- If `(P0, L)` are declared to EXACTLY match the honest world's TRUE price-generating rule
  (`price = P0 + L * R`, and `default_mean(g)` is used as a stand-in for `R`), then in the limit of
  infinite bin population, `default_mean(g) -> R_mean(g)` (law of large numbers on the Bernoulli
  draws within a bin) and `price_mean(g) -> P0 + L*R_mean(g)` exactly (if price is generated at the
  bin level from bin-mean R, as in the diagnostic construction above) or converges to it under mild
  conditions (if price is generated per-row from individual R and then bin-averaged — the diagnostic
  check above used the former). Under those conditions the wedge -> 0 as bin population -> infinity,
  AT ANY BIN COUNT, because the argument `d` and the true generator both track the SAME bounded
  latent, up to finite-sample noise that does not accumulate with bin count (it shrinks or stays flat
  as bins get finer and each bin's population shrinks — this is the OPPOSITE scaling of the killed
  statistic, and is worth flagging as a DIFFERENT risk: with more bins, EACH bin has fewer
  observations, so per-bin noise in `default_mean(g)` GROWS per bin even as the pop-weighted
  aggregate stays flat. This is a bias-variance question for detector #4, not resolved here).

- This is exactly the same epistemic status as detector #3's original intent ("declare `just_per_default`
  from the honest world, then it should be near-zero at lambda=0") — the FIX is not "now it's a
  theorem," the fix is "the declared quantity is now dimensionally capable of being zero at every
  granularity, where before it was mathematically guaranteed NOT to be, because of the index-vs-rate
  mismatch." Zero-at-construction here means: IF you declare `(P0, L)` to equal the true honest-world
  generating parameters, THEN the wedge's only departure from 0 is finite-sample noise in
  `default_mean` as an R-estimator — a noise source that is bounded, does not systematically grow
  with bin count (verified numerically above, in contrast to the killed statistic which does), and
  is a STANDARD estimation-noise problem with known asymptotics (shrinks with bin population,
  standard bootstrap CIs apply) rather than a structural, ever-growing pedestal.

**What is NOT proven, stated honestly:**
1. This is conditional on `(P0, L)` being declared correctly (equal, or asymptotically consistent
   with, the true honest-world price rule). In a REAL detector run on field data, the true honest
   rule is unknown — `(P0, L)` would have to come from the lender's STATED pricing policy (a
   regulatory artifact, e.g. a rate sheet) or from some other external, non-circular source. If the
   declared `(P0, L)` is wrong even under an honest world, the wedge will NOT be zero — it will be a
   confound of "declared policy != actual (honest) policy," which is a real, expected, and
   detectable-but-different failure mode, not the incommensurability bug. This is analogous to
   Result 2's own caveat in the parent spec (identifiable vs honest is necessary, not sufficient —
   still confounded with (b)/(c)); here the analogous caveat is "zero under correct calibration is
   necessary, not sufficient — miscalibration is a live, EXPECTED-nonzero risk that detector #4 must
   guard against separately from the incommensurability bug this document fixes."
2. This document does NOT prove the wedge is zero as a mathematical identity independent of
   assumptions, the way Result 1 in the parent spec is a genuine non-identifiability THEOREM (a
   distributional equality holding for every lambda by pure algebra: `score = R` under both worlds
   when `P=0`). What IS shown here is weaker and empirical/constructive: given a correctly specified
   map, the wedge's departure from zero is finite-sample noise with the RIGHT asymptotic behavior
   (does not explode with bin count), not a structural bias term. That is a materially different,
   and materially weaker, claim than a proof. Calling it a proof would repeat exactly the overclaim
   pattern this project's discipline exists to catch.

## Part 3 — adversarial self-check: at least 2 failure modes attempted against this design

**Attempt 1 — does calibrating `(P0, L)` from bin-level regression reintroduce the SAME attenuation
bug detector #3 had, just moved one level up?**

Tried: instead of declaring `(P0, L)` from known truth, estimate them by
`OLS(price_mean(g) ~ default_mean(g))` across bins — i.e., regress BIN MEANS against each other
rather than individual rows. This is a real candidate for how a detector #4 would have to calibrate
`(P0, L)` on FIELD data, where the true honest rule is unknown. Diagnostic check on the continuous
honest-world DGP (`base=500, loading=300`, `n_bins=5`): individual-row `OLS(price~default)` recovers
95.5 bps (severely attenuated). Bin-mean regression was not separately re-run in this design pass
(the direct-declaration approach above was validated instead), but the mechanism is inferable: for a
FIXED bin count, bin-mean regression averages out the individual-row Bernoulli noise BEFORE
regressing, which should sharply reduce attenuation relative to individual-row OLS (that's exactly
why using `default_mean(g)` as the map's ARGUMENT, rather than raw `default`, is the second fix in
Part 1). **This survives as a design choice** but is flagged, not verified numerically here, as a
gap: detector #4 must empirically confirm bin-mean-regression-calibrated `(P0, L)` converges to the
true parameters as bin population grows, and must check whether this reintroduces a NEW granularity
dependence (regressing bin means against each other, where the number of bins IS the sample size for
that regression, could behave differently at bins=5 (n=5 points) vs bins=100 (n=100 points) —
untested here, real risk for detector #4, not resolved).

**Attempt 2 — does the "population-weighted mean of a linear-in-d map" hide a granularity artifact
the way `price_gap` did, just one derivative down?**

Tried: check whether AGGREGATING wedge_g (computed per-bin) via population-weighting can itself
reintroduce a bin-count dependence, even though each individual `wedge_g` is well-posed. Concern:
if the map `risk_justified_price` is LINEAR in `d` (as declared: `P0 + L*d`), then
`E_g[wedge_g] = E_g[price_mean(g)] - P0 - L*E_g[default_mean(g)]`, and by linearity this equals
`price_pop_mean - risk_justified_price(default_pop_mean)` — i.e., the population-weighted aggregate
of per-bin wedges collapses to a SINGLE population-level wedge regardless of how the population was
partitioned into bins, AS LONG AS the map is linear. This is a genuinely reassuring finding — it
means the aggregate footprint statistic is provably invariant to the CHOICE of bin count (not just
empirically stable, as shown in Part 1's diagnostic, but a direct algebraic consequence of linearity
in `d` plus population-weighted averaging). **However this reveals a real cost, not a false alarm
survived**: if the linear map collapses to depending only on the POPULATION MEANS of price and
default (not on the bin structure at all), then a population-level footprint statistic loses ALL
per-bin resolution — it cannot distinguish "laundering concentrated in one bin, offset elsewhere" from
"no laundering," because the linear map's aggregate is a function only of the marginal means. A
NONLINEAR declared map (if the true honest pricing curve is nonlinear in risk, which is realistic —
real rate cards are often convex in risk) would NOT collapse this way, and would retain bin-level
resolution as a genuine feature, not just noise. **This did not "survive" cleanly** — it exposed a
real tension: the SAME property that guarantees bin-count invariance (linearity) also guarantees the
aggregate statistic is blind to within-population reallocation of laundering across bins, which is
arguably the MAIN signature Result 2 in the parent spec was trying to capture (laundering moves
protected people INTO specific worse bins). A linear map may be dimensionally sound but could throw
away the very signal the design is meant to detect. Recorded honestly as unresolved: detector #4
needs to decide whether to (a) accept this and report only a population-level, bin-count-invariant
number (weaker but well-posed), or (b) use a nonlinear declared map / retain and report per-bin
wedges rather than the population aggregate (potentially strong signal, but then EACH per-bin wedge's
individual-noise behavior, not just the aggregate, needs its own bin-count-stability check — not done
here).

**Attempt 3 (brief, not fully worked) — does `default_mean(g)` used as BOTH the map's argument and
(implicitly, via calibration) an input to `(P0,L)` create a new circularity, distinct from the old
individual-level attenuation bug?**

Flagged, not resolved: if `(P0, L)` are calibrated FROM the same data the wedge is later computed
on (as opposed to genuinely external/declared from a rate sheet), the map is fit-then-applied on the
same sample — a version of the same in-sample circularity that killed detector #1
(`fairwash_calibration_floor.py`, `ae7af3d`). The linear-collapse result in Attempt 2 makes this
sharper: if `(P0, L)` are fit by OLS on population means and the wedge is then evaluated using those
same population means, the population-level wedge is provably 0 by algebraic tautology (regressing
X on Y then evaluating the fit at the mean of Y reproduces the mean of X exactly) — a real risk of
manufacturing a fake "GUARD A passes" result that is actually circular, not evidence the map is
correct out of sample. This is the single most dangerous failure mode found in this pass and is NOT
resolved here: it means `(P0, L)` calibration MUST come from a source independent of the sample the
footprint is later measured on (a held-out honest reference sample, a genuinely external declared
rate sheet, or cross-validation across time/vintage), or GUARD A will pass trivially and
uninformatively. Flagging this explicitly rather than building past it.

## Frozen decision (pre-estimator)

1. ADOPT the dimensionally-coherent map `risk_justified_price(d) = P0 + L*d` (or a nonlinear
   generalization, per Attempt 2's finding) as the replacement for the killed scalar
   `just_per_default`. The old scalar-times-bin-index construction is ABANDONED — proven
   unit-incommensurable (parent commit `c1c0a1e`), and this document reproduces the mechanism
   independently.
2. A detector #4 built on this map MAY claim: the population-weighted footprint is invariant to bin
   count UNDER a LINEAR declared map (algebraic consequence, not just empirical — verified in Attempt
   2), and the honest-world wedge is small and bin-count-STABLE (not exploding, unlike the killed
   statistic) under a correctly- and NON-CIRCULARLY-calibrated map (verified diagnostically in Part 1
   for one synthetic DGP).
3. A detector #4 built on this map MAY NOT claim: that the honest-world wedge is a mathematical
   ZERO by theorem (Part 2 — it is zero only conditional on correct, non-circular calibration of
   `(P0, L)`, with residual finite-sample noise whose asymptotics were checked in one synthetic case,
   not proven in general). It also MAY NOT claim per-bin (as opposed to population-aggregate)
   resolution unless it uses a nonlinear map and separately validates per-bin wedge stability — the
   linear map's bin-count invariance was shown to come AT THE COST of collapsing to a population-mean
   statistic that cannot localize where in the bin structure laundering occurred (Attempt 2).
4. EXPLICITLY DEFERRED / UNRESOLVED, must be addressed before or during detector #4, not assumed
   away:
   a. How `(P0, L)` are calibrated on FIELD data without circularity (Attempt 3 — the most serious
      open risk; a naive in-sample fit can make GUARD A pass tautologically, reproducing the shape of
      detector #1's failure one level up the stack).
   b. Whether bin-mean-level calibration of `(P0, L)` (as opposed to individual-row OLS, which is
      confirmed attenuated) itself carries a bin-count-dependent bias — inferred plausible but NOT
      numerically verified here (Attempt 1).
   c. The choice between a linear map (bin-count-invariant aggregate, no localization) and a
      nonlinear map (potential localization, bin-count-invariance not yet shown) is UNMADE — this is
      a design fork for detector #4, not resolved by this document.
   d. Per Part 2's per-bin noise remark: finer bins shrink each bin's population, which could grow
      per-bin (not pop-aggregate) variance — a bias-variance tradeoff for CI construction in
      detector #4, untouched here.
   e. As in the parent spec: confounds (b) unpriced lawful risk factor and (c) grade coarseness alone
      remain COMPLETELY OUT OF SCOPE for this document, unchanged from the parent spec's deferral.
      This document only repairs the WEDGE'S DIMENSIONAL WELL-POSEDNESS; it does not touch, and does
      not claim to touch, the three-subject confound the parent spec left open.
5. Before detector #4 is built, item 4(a) (non-circular calibration source for `(P0, L)`) must be
   resolved on paper — it is the single highest-risk unresolved item, and it is the SAME SHAPE of
   error (in-sample circularity) that killed detector #1. Building past it now would be exactly the
   "momentum" this project's discipline exists to interrupt.
