# Steering-Detectability of the Gradient Instrument — Design (frozen pre-reg)

**Date:** 2026-06-23 (same session as the realized-return result + its survivorship correction)
**Branch:** `age-pricing-residual`
**Module:** `wedge/steering_detectability.py` (to build) — pure synthetic, no real data
**Artifact:** `runs/steering_detectability_2026-06-23.txt` (+ JSON sidecar)

**Lineage / why now:** the realized-return result ([[project_age_realized_return_result]]) read the real LC
profit-by-age GRADIENT as flat (slope_R²=0.046 on matured vintages) and concluded "un-audited instrument,
NOT deliberate steering" — Tony's "they're not searching their own data" branch. That conclusion is only as
good as the instrument. I validated `gradient_characterization` on synthetic MONOTONE data and synthetic
NOISE, but never on **steering laundered through grade**, which is how real pricing works
([[project_steered_laundering_synthetic_repro]], [[project_pick_one_hides_choice]]). If laundered steering
produces the SAME flat gradient as genuine blindness, the "no intent" verdict is **unfalsifiable** and must
be retracted to "intent unobservable."

## Construction — three synthetic lenders, each assigns a grade then prices off it

Common: N synthetic borrowers, an observed `age_band`, a latent `true_risk` (drives real default), lawful
controls correlated with true_risk but NOT with age (mirror real LC: age ⊥ controls). Realized return is
generated, not modeled, so the same `wedge.age_realized_return` cells apply unchanged.

- **L0 — BLIND (negative control):** grade = g(true_risk) only. Price = f(grade). Young priced exactly as
  their risk warrants. No age signal anywhere. Gradient instrument MUST read flat (else false-positive).
- **L1 — OVERT steering (positive control):** grade = g(true_risk); price = f(grade) + δ·1[young]. The
  surcharge sits in PRICE, visible. Gradient instrument MUST light up (else the instrument is broken and the
  whole realized-return verdict is void).
- **L2 — LAUNDERED steering (the coin):** the young-surcharge is injected into the GRADE assignment
  (grade = g(true_risk) − k·1[young], i.e. young pushed to worse grades beyond their risk), THEN price =
  f(grade) honestly. No explicit age term in price. Engineered so the lender profits from the young (or at
  least over-prices them past risk). This is steering that presents as "grade just rates them worse."

## Outcome metrics (per lender)

Run `fit_band_return` + `gradient_characterization` on each lender's price-by-age AND on net-of-grade
price-by-age. Report, per lender:
- young-band price coefficient (raw and net-of-grade),
- gradient slope_R², spearman, monotone-flag,
- a single **STEERING-DETECTED** boolean = (|young raw coef| materially > 0) AND (gradient reads monotone OR
  high slope_R²). Defined identically across L0/L1/L2 so the instrument is blind to which lender it sees.

## THE COIN (frozen prediction)

Does the instrument distinguish **L2 (laundered) from L0 (blind)**?

- **Claude (frozen, ~65%):** L2 reads CLOSER TO L0 than to L1 — laundered steering is MOSTLY INVISIBLE to the
  gradient, because the gradient reads PRICE-by-age and L2 hides the steering in GRADE-by-age. Net-of-grade
  the L2 signal will largely vanish (grade absorbs it), exactly as the real-data net-of-grade barely moved.
  ⇒ If so, the real-data "flat gradient = no steering" verdict is UNFALSIFIABLE and I must retract
  [[project_age_realized_return_result]]'s "not deliberate" line to "intent unobservable via this instrument."
- **Alternative I'm betting against:** L2 lights up like L1 (laundering leaks into the raw price-gradient
  enough to detect) ⇒ the flat real result genuinely means no steering ⇒ Tony's "not looking" branch is earned.
- **Meta / guardrails:** L0 reads flat (no false positive) and L1 lights up (no false negative) — if EITHER
  control fails, the instrument is broken and L2 is uninterpretable; fix the instrument before reading the coin.

Scoring on the fresh artifact: (a) L0 flat? (b) L1 detected? (c) L2 vs L0 vs L1 placement, raw and
net-of-grade; (d) verdict: is the gradient a valid steering detector, or does laundering defeat it?

## Caveat

Synthetic — establishes only what the instrument CAN detect in principle, not what LC did. A "laundering
defeats it" result does not prove LC laundered; it proves the gradient CANNOT RULE laundering OUT, which is
enough to force the retraction of the "not deliberate" claim to the weaker, honest "unobservable."
