# HMDA Real-Age Pricing Disparity — Design (frozen pre-reg)

**Date:** 2026-06-23 (same sprint as the LC age arc)
**Branch:** `age-pricing-residual`
**Module:** extend `wedge/collectors/hmda.py` (pricing frame) + reuse `wedge/age_residual.fit_band_residuals`
**Artifact:** `runs/hmda_ri_age_pricing_2026-06-23.txt` (+ JSON)

## Why — removing a model from the light path
Per [[project_instrument_with_model_in_light_path]]: the LC age results all carry ONE big light-path
assumption — **"age" is credit tenure** (est_age = 18 + tenure), not observed age. A hostile expert
attacks that first. HMDA observes **real applicant age** (bands), so porting the pricing disparity to
HMDA REMOVES that assumption. This is not "another substrate for generality" — it is cleaning one
declared model out of the light path and testing whether the disparity survives without it.

## What HMDA CAN and CANNOT do (the honest scope, per Tony's (i) call)
- **CAN:** real-age pricing disparity. HMDA has `applicant_age` (observed bands) + `interest_rate` +
  lawful controls (income, loan_amount, ltv, dti, loan_term). Run the band-residual pricing analysis
  on REAL age.
- **CANNOT:** the risk-decomposition. HMDA has NO realized loan outcome (action_taken is origination,
  not performance; no default/charge-off/loss). The realized-risk benchmark that makes the LC analysis
  an *instrument* (not a groupby) does not exist here. Per Tony: report decomposition **UNAVAILABLE —
  no realized-risk benchmark on this substrate**. Do NOT invent a proxy benchmark (that would be
  theater: a constructed quantity dressed as realized risk — the exact move the instrument exposes).
  So HMDA yields a **disparity-only** result with the decomposition honestly declared absent.

## Design
- Substrate: HMDA-RI 2022, first-lien owner-occupied purchase/refi, ORIGINATED only (rate exists only
  for originated). N≈18,226 complete cases (rate + age + income + loan_amount + ltv; dti kept if present).
- Outcome: `interest_rate` (percent). Lawful controls: applicant_income, loan_amount, ltv, dti,
  loan_term_months. (NB: HMDA has NO credit score — legally-mandated pool only. That is itself a
  declared light-path fact: fewer risk controls than LC, so a surviving disparity is LESS purged of
  risk than LC's, a caveat in the direction of caution.)
- Age bands: HMDA NATIVE bands (`<25, 25-34, 35-44, 45-54, 55-64, 65-74, >74`); reference `45-54`
  (closest to LC's [45,50)). Exclude age codes 8888/9999 (missing).
- Method: OLS of interest_rate on age-band dummies + controls + purpose; per-band bps residual vs
  reference. Reuse the band-residual machinery; report exactly as LC.
- Positive control: plant +30bps on the youngest band, assert recovery (anti-confabulation).

## FROZEN LEDGER (set BEFORE the run)
- **Claude (~60%):** the young (`<25`, `25-34`) pay a POSITIVE rate premium net of lawful controls,
  but ATTENUATED vs LC's +209bps — predicted young (`<25`) excess **+10 to +90 bps**, positive,
  smaller than LC because (a) mortgage pricing is more constrained/competitive than personal-loan
  pricing and (b) real age dilutes the tenure signal that drove LC. If `<25` is NEGATIVE or zero, the
  LC gradient was substantially a tenure artifact and a chunk of the sprint reclassifies.
- **Alternative:** flat/no age gradient on real age ⇒ LC's was tenure, not age. Fully falsifiable.
- **Meta:** the decomposition is correctly reported UNAVAILABLE (no realized outcome on HMDA), not faked.

Scoring on the fresh artifact: (a) sign of `<25` and `25-34` residual, (b) magnitude vs LC's +209,
(c) monotonicity young→old, (d) decomposition correctly declared absent.

## Caveats that travel
- HMDA age is OBSERVED and BANDED (coarser than continuous; `<25` is the young proxy). This is the
  point — it removes the tenure confound, at the cost of coarser resolution.
- Fewer risk controls than LC (no credit score) ⇒ a surviving disparity is LESS risk-purged ⇒
  interpret as an UPPER reading of the lawful-controls-residual, not directly comparable in magnitude
  to LC's grade-inclusive number. Declared, not corrected.
- Single state (RI), single year (2022), originated-only (denied loans have no rate; a separate
  selection question, not this experiment's).
- DISPARITY ONLY. Whether any of it is risk-justified is UNANSWERABLE on HMDA and is reported as such.
