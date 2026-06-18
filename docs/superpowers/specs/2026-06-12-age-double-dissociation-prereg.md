# Pre-registration: Age double-dissociation probe (HMDA-RI 2022)

**Date:** 2026-06-12
**Substrate:** `data/hmda/processed/hmda_2022_RI.parquet` (RI, 2022; 41,774 rows; age OBSERVED)
**Frozen BEFORE computing.** Anti-confirmation: a satisfying frame is in hand (the "cookbook" asymmetry);
this ledger exists so the result can come back NO and be caught.

## The claim under test

Forensic age discrimination via facially-neutral proxies, where age is unobservable to the auditor in
loan-PERFORMANCE/deployed-model data, rests on a DOUBLE DISSOCIATION:

- **G reconstructs**: `AUC(applicant_age_above_62 ~ transferable proxies)` is HIGH — the discriminator can
  recover age from facially-neutral fields.
- **Y is blind**: `AUC(action_taken ~ same proxies)` is NEAR 0.50 on the age-carrying channel — an accuracy
  audit of the approve/deny decision does not visibly lean on the age-proxy.
- **Steering is where harm is chosen**: an ε-Rashomon band of approval models, selected adversarially,
  spreads age-disparity wide (band-max − band-min disparity ≫ 0) while all members tie on AUC(Y).

If all three hold: the harm is chosen at the unaudited SELECTION step, invisible to accuracy audit, and the
auditor (who lacks age in performance data) cannot see what the discriminator (who reconstructs it) exploits.

## Variables (frozen)

- **Y** = `action_taken` ∈ {1 originated, 3 denied} → binary (1 = originated).
- **G** = `applicant_age_above_62` ∈ {Yes, No}; drop NaN (780 rows). This is the ECOA special-protection age.
- **TRANSFERABLE proxy set** (must exist in age-blind substrates FNMAE/LC too — this is the honest set):
  `loan_purpose`, `loan_term`, `income`, `property_value`, `loan_to_value_ratio`, `occupancy_type`,
  `derived_msa-md` (geography), `tract_median_age_of_housing_units` (ecological, ACS-style).
- **EXCLUDED as cheats** (do not transfer / leak age degenerately): `reverse_mortgage`,
  `applicant_age`, `applicant_age_above_62` (the label), `co-applicant_age*`, race/sex/ethnicity fields,
  `denial_reason*` (post-decision leakage), `interest_rate`/`rate_spread` (priced post-approval).

## PREDICTIONS (frozen — my honest priors, scored later)

- **P1 (G reconstructs)**: restricted-proxy `AUC(G ~ proxies)` ∈ **[0.62, 0.74]**. NOT >0.75 — without
  reverse_mortgage and without credit-history-length, the transferable set is weak. I expect "reconstructable
  but not cleanly." **Collapse if < 0.58** (age non-identifiable → ser/estar floor → frame dies).
- **P2 (Y blind on the age channel)**: I do NOT predict AUC(Y~proxy)≈0.50 globally — loan_term/income/LTV are
  genuinely predictive of approval. AUC(Y ~ full proxy set) likely **0.62–0.70**. The dissociation must be
  shown on the AGE-CARRYING COMPONENT, not the whole proxy set. Refined P2: the partial contribution of the
  age-predictive direction to Y is small — i.e. after controlling for the lawful predictive content, the
  residual age-channel adds little to Y-fit. **This is the prediction most likely to be messy/fail.**
- **P3 (steered band gap)**: ε-band (AUC within 0.01 of best) approval models, selected for max vs min
  age-disparity, spread **≥ 2× the within-CI noise** — selection moves disparity materially while Y-fit is
  pinned. **Collapse if band-max ≈ band-min** (then laundering needs no steering → reduces to LDA-for-age).
- **P4 (RFOA confound honesty)**: age-above-62 applicants have materially different approval base rates AND
  different lawful covariates (income, LTV at retirement). The probe MUST report disparity BEFORE and AFTER
  controlling for lawful covariates — if the disparity vanishes under lawful controls, that is the RFOA
  business-necessity alibi and the steered-gap must exceed it.

## What would KILL this (named in advance)

1. P1 < 0.58 → age non-identifiable from transferable proxies → symmetric blindness → ser/estar floor.
2. P3 band gap ≈ 0 → harm not chosen at selection → LDA-for-age (occupied).
3. P2 dissociation absent (age channel IS load-bearing for Y) → no "blind audit" → it's just ordinary
   disparate impact, auditor can see it.
4. P4: disparity fully explained by lawful covariates → RFOA alibi holds → no residual harm to forensically
   detect.

## Honesty notes

- HMDA age is BANDED, not scalar → AUC(G~proxy) is a coarser test than a scalar age regression would be.
- N=41,774 single state single year → CIs matter; bootstrap the band gap.
- This is the CALIBRATION substrate. A positive result here does NOT prove the FNMAE transfer; it proves the
  proxy map EXISTS where age is observed. The transfer is a separate, later claim.
