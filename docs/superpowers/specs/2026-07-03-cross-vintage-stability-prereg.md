# PRE-REGISTRATION — is the honest lawful risk-loading vintage-stable on SBA 7(a)?

Date: 2026-07-03. Branch `age-pricing-residual`. FROZEN BEFORE the estimator, per this lineage's
discipline (three detectors died from building before the identifiability was checked). This is the
load-bearing feasibility test for the cross-vintage identifying restriction named as the leading
bucket-(iv) route in `docs/superpowers/specs/2026-07-03-calibration-floor-resolution.md`.

## Why this test, and why FIRST

The calibration-floor resolution (commit `692438c`) proved item 4a is category B: the declared
price-map `(P0,L)` cannot be self-calibrated (wedge ≡ 0 by OLS algebra), so it needs an EXOGENOUS
identifying restriction. Four candidate restrictions; the most interesting is the CROSS-VINTAGE
STABILITY EXCLUSION:

    "The honest lawful risk-loading L (bps of price per unit of realized default rate) is INVARIANT
     across origination vintages; laundering is what BREAKS that invariance."

If true, this restriction lets a detector calibrate L on a reference vintage and flag deviations on
held-out vintages as candidate laundering — WITHOUT self-calibration and WITHOUT an external rate
sheet. It also welds to the transformation-law deliverable of the parallax program.

But the restriction has a LOAD-BEARING empirical premise that has NEVER been checked: IS the honest L
actually vintage-stable on real data? If L drifts across vintages for a purely lawful reason (macro
credit cycle, changing borrower mix), the restriction imports a confound — I could not tell
laundering-drift from lawful-L-drift, which is Fact B's cousin one level up. Building detector #4 on
an untested stability premise would repeat the exact error that killed #1-#3. So this feasibility
test runs FIRST, and its result GATES whether the cross-vintage route survives at all.

## The known confound, pre-handled

SBA 7(a) is ~79% VARIABLE-rate; the INITIAL interest rate tracks the base-rate environment at
origination (`wedge/collectors/sba.py:159-166`). Therefore the price INTERCEPT P0 (level) is EXPECTED
to drift by `approval_fy` for a lawful reason (the Fed rate path 2010-2016). This is NOT the quantity
under test. The restriction only needs the SLOPE L (price-per-realized-risk) to be stable, not the
level. Two guards against the base-rate confound:
  1. Test L (the risk-loading coefficient), never the raw price level.
  2. Report the test SEPARATELY on FIXED-rate loans (`rate_type == 'F'`), where the base-rate-timing
     confound is weakest, as the cleaner cell. If L is stable on fixed-rate but not variable-rate,
     that localizes the drift to the rate-environment mechanism, not to firm-risk-pricing.

## The map, made estimable

Per the resolution, the honest map is `risk_justified_price(d) = P0 + L*d` where `d` = realized
default RATE. Operationally, per vintage v, estimate L_v as the slope of price on a bounded realized-
risk quantity, net of lawful controls. To keep `d` a bounded [0,1] rate (Fact B discipline — never an
unbounded bin index), I stratify each vintage's loans into fixed quantile bins of predicted/realized
risk and regress bin-mean price on bin-mean realized default rate. L_v = that slope. (Bin-mean
regression, NOT individual-row OLS — the latter is attenuated by the noisy binary default, the second
bug found in the map-design pass. Verified concern, pre-handled.)

## FROZEN PREDICTIONS (falsifiable, scored WIN/LOSE, no hedge)

Vintages = matured approval-FY window FY2010-2016 (the collector's MATURED default; 7 vintages).
Reference-free: I compute L_v for every vintage and test dispersion, NOT deviation from a chosen anchor.

- **P1 (the load-bearing bet, ~55% prior):** the fixed-rate risk-loading L_v is vintage-stable —
  operationally, the coefficient of variation of L_v across the 7 matured vintages is < 0.25 (a
  quarter of the mean), AND no single vintage's L_v 95% CI excludes the pooled-across-vintage L.
  WIN => the cross-vintage restriction is EMPIRICALLY LICENSED (build detector #4 on it).
  LOSE => L drifts; the restriction imports a lawful-drift confound; the cross-vintage route is
  DEAD or needs the drift itself modeled (transformation-law, harder). Either way, recorded.

- **P2 (localization, ~50% prior, conditional read):** IF L drifts (P1 LOSE), the drift is LARGER on
  variable-rate than fixed-rate loans (CoV_variable > CoV_fixed), localizing it to the base-rate
  mechanism rather than to firm-risk-pricing. WIN here would PARTIALLY rescue the route (restrict to
  fixed-rate). LOSE (drift is equal or larger on fixed-rate) means the drift is in the risk-pricing
  itself — the route is more thoroughly dead.

- **P3 (sanity / positive control, must PASS or the estimator is broken):** on a SHUFFLED-vintage
  placebo (randomly reassign each loan's vintage label, destroying any true vintage structure), the
  L_v dispersion COLLAPSES toward zero (CoV_shuffled << CoV_real). If the shuffled placebo shows the
  same dispersion as real, the "drift" is estimator noise, not vintage structure, and P1/P2 are
  uninterpretable. This guards against reading sampling noise as drift.

## What this test does NOT claim
- It does NOT build detector #4. It only tests whether ONE of its candidate identifying restrictions
  is empirically licensed.
- It does NOT touch the (b)/(c) confounds (unpriced lawful risk / coarseness) — out of scope, as in
  the parent specs.
- A stable L (P1 WIN) is NECESSARY, not sufficient, to license the route: it says the honest surface
  CAN serve as an anchor, not that deviations from it are provably laundering (still confounded with
  a vintage-specific lawful shock). That sufficiency question is downstream, flagged not assumed.

## Scoring
P1, P2, P3 each scored explicitly WIN/LOSE/PASS-FAIL against the frozen bet above. The blind
scientific-integrity adversary runs BEFORE any result memo (the result may flatter the "route
survives" prior — that is exactly when self-deception peaks). Numbers with no on-disk artifact do not
count.
