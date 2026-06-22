# Grade-vs-Default Age Decomposition — Design

**Date:** 2026-06-22
**Script:** `scripts/age_grade_default.py` (sibling runner; shared stats live in `wedge/age_residual.py`)
**Artifact:** `runs/lc_age_grade_default_2026-06-22.txt` (+ JSON sidecar)
**Lineage:** direct descendant of [[project_age_residual_result]]. That result found the young-end pays
+209 bps over conventional lawful risk, dropping to +27 bps net of LC GRADE — so **~182 bps of age pricing
lives inside grade.** This experiment asks whether that 182 is justified by realized default or floats free.

## Question
Does LC's grade price the young-end age gradient PAST what realized default justifies (lawful-but-
illegitimate, the empty-chair instance), or does grade's age-loading track default (grade exonerated, the
+209 is just risk FICO can't see)? And — the high-surprise sub-question — does the sign FLIP at the old end
(are the old priced BELOW their default-justified rate, i.e. subsidized by the same instrument that extracts
from the young)?

Per [[project_empty_chair_as_method.md]]: purpose is not to win a discrimination argument (no court) but to
produce a number a lawmaker can't unsee. The bias-against-interest signature ([[feedback_bias_against_interest]])
— priced past risk => bank loses money on the disqualified-but-profitable — is the version that lands.

## Frozen prediction ledger (set BEFORE design, do not alter post-run)
- **Claude (corpus excess, primary):** young-end excess SURVIVES the conservative corpus benchmark but
  smaller than the 182 — the thin-file risk Tony flagged eats a real chunk. Predict young [18,25) corpus excess
  in **+40 to +100 bps** (positive, conservative, non-trivial). Lower confidence on magnitude, higher on "stays
  positive after netting out real young default."
- **Claude (grade-laundering gap):** corpus-minus-within-grade young excess is LARGE — most of the corpus excess
  vanishes within-grade, i.e. grade is where the age pricing hides. Predict the within-grade young excess drops
  to under half the corpus excess.
- **Claude (old-end sign):** the old ARE priced below their default-justified rate (subsidized) through the
  50-60 bands; the 70+ tail too censored (n=728) to sign. Genuinely uncertain — this is the fun.
- **Tony (flagged pre-run):** the corpus benchmark will bias AGAINST the young because short credit histories
  push them into higher-default categories anyway — so expect the young excess to be ATTENUATED vs the raw 182,
  and a chunk of it is defensible risk. (Recorded as his standing caveat; sharpens what "survives" means.)

## Data
- `data/accepted_2007_to_2018Q4.csv`, resolved loans (Fully Paid|Charged Off), N≈1.34M — SAME universe and
  loader as the parent runner. `default = 1[loan_status == "Charged Off"]` (268,559 of 1,344,935).
- est_age, age bands, lawful controls: identical to parent ([[project_age_residual_result]]).
- **Verified feasible (pre-design):** realized default rises cleanly + MONOTONICALLY with rate charged
  (rate-decile default 4.9% -> 40.2%, no inversions; corr(int_rate, default)=+0.259). A stable empirical
  default->rate map exists; we estimate it from data, never assume a risk-premium formula.

## Defining "justified" (Tony's reframe — anchors the benchmark to DEFAULT, not to LC's price)
"Justified price" = the rate normalized to the group's REALIZED DEFAULT RATE — i.e. the price a given level of
realized default maps to, estimated empirically. Anchoring to default (not to LC's own pricing) sidesteps the
circularity worry entirely: we are NOT asking "is the young price consistent with LC's pricing of similar risk"
(that bakes in any age bias LC already has); we are asking "is the young price consistent with the default they
ACTUALLY realize." Two scopes, and the contrast between them IS the experiment:

- **CORPUS (primary):** fit the default->rate map on the WHOLE population, age-blind, apply to all bands. The
  young's genuinely higher default (thin file = real risk; U-shape young arm is real) is BUILT INTO the justified
  price. So any surviving young-end excess is CONSERVATIVE — it has already netted out the thin-file defense.
  **This is the version a lawmaker can't unsee: it survives the obvious "they're just riskier" rebuttal because
  that rebuttal is already priced into the yardstick.**
- **WITHIN-GRADE (contrast/foil):** fit the map WITHIN each grade. If young-end excess is large in CORPUS but
  vanishes WITHIN-GRADE, that is the smoking gun that GRADE is the laundering layer — it absorbed the age pricing
  so within-grade looks fair. **The corpus-minus-within-grade excess gap is the cleanest measure of how much grade
  launders.** (Within-grade alone exonerates grade by construction, hence foil not headline.)

## Primary: default-justified-price benchmark (the dollar number)
1. **Predicted default:** logistic regression of `default` on lawful risk factors (FICO/DTI/income/loan/term/
   purpose) -> predicted default probability per loan. (NOT on age — age is the thing under test.)
2. **Empirical default->rate map (CORPUS):** estimate the monotone rate that realized default maps to, calibrated
   from the whole-population data (isotonic regression of int_rate on predicted-default, or decile-calibrated
   means). This is the corpus "default-justified price" for each loan.
3. **Per-band excess:** for each age band, mean(actual int_rate − default-justified rate), in bps, with 95% CI.
   - Young-end POSITIVE excess (CONSERVATIVE — thin-file risk already netted out) = priced past realized default
     = bias-against-interest (the headline).
   - Old-end sign read EXPLICITLY: negative = subsidized below justified rate.
4. **Grade-laundering measure:** corpus excess − within-grade excess, per band. Large young-end gap = grade
   absorbed the age pricing.
5. **Headline is a SIGN + RANKING claim** (young above / old below justified), bps secondary and bracketed by
   the map's sensitivity (report under both isotonic and decile-calibrated maps; agreement = robust).

## Sanity rail (cheap, off the same regressions): age-in-grade vs age-in-default
Two band regressions on the same age bands:
- `grade_numeric ~ age_bands + risk` — does grade encode age beyond risk? (grade_numeric = A..G -> 1..7;
  sub_grade deliberately ignored — letter-grade granularity suffices, 35 sub-levels add noise not insight, YAGNI)
- `default ~ age_bands + risk` — does default encode age beyond risk?
If grade's per-band age coefficient EXCEEDS default's (rescaled comparably), grade prices age the default data
doesn't justify. Cross-checks the benchmark; disagreement between rail and benchmark is itself diagnostic.

## Old-end handling (decided on the fun meter, reported honestly)
The old-end subsidy sign is the highest-surprise quantity AND where data is weakest (n=728 @70+, censored
tenure). It stays IN THE PRIMARY, every band with its CI, plus an explicit "signable through band X, noise
beyond" line — the DATA draws the boundary, not nerve. Not appendixed (that would sacrifice the surprise to buy
safety we don't need if uncertainty is reported properly). Wide CI crossing zero at 70+ IS the finding there.

## Testing
- **Positive control:** synthetic data with a band priced ABOVE its default-justified rate by a known margin;
  assert the benchmark recovers that band's excess within tolerance and flags it (and a default-justified band
  shows ~0 excess). Guards the confabulation failure mode at the benchmark level.
- **Monotonicity guard:** assert the estimated default->rate map is monotone non-decreasing (if it isn't, the
  benchmark is invalid and must error loudly, not silently produce garbage).

## Output
- `runs/lc_age_grade_default_2026-06-22.txt` — self-describing: ledger, per-band default-justified excess with
  CIs under both maps, old-end sign line, the grade-vs-default rail, every caveat inline. JSON sidecar.
- No paper, no thread. Just: does grade float free of default — and does the sign flip at the old end?

## Caveats carried in the artifact
- "age" IS credit tenure (est_age = 18 + tenure); credit-tenure gradient read as age.
- Pricing = LC grade model, not a counterfactual lawful price.
- Old tail (70+) censored, small n, wide CIs — old-end sign reported WITH that uncertainty, never clean headline.
- The default->rate map is the attack surface; reported under two estimators and as sign/ranking where the map
  is shakiest.
