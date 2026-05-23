# SEED (candidate, NOT a pre-reg, NOT stamped): carrier-identity as a B-failure screen

**Status:** wander deposit / candidate pre-reg seed. **UNCOMMITTED, UNSTAMPED, predictions PROVISIONAL.**
Captured 2026-05-22 so the object isn't lost; firm up into a held-out pre-reg only if pursued.
**Speech-act class:** constative observation + provisional bet. **Connects:** the #15 B-recovery
pre-reg (`docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md`),
`working_notes/2026-05-22-b-recovery-R2B-definition-erratum.md`,
`[[project_silence_manufacture_result]]`, `[[project_pre_registration_pattern]]`,
`[[project_fm11_result]]` (regime-tilted carrier), `position-desai-foil.md`.

## The object

In-sample on the #14 seven (n=44 A-inadequate cells, both strata, peek-tainted), **B-failure is
predicted by the variant_A disagreement *carrier identity*, not by R²_A magnitude** (the axis the two
frozen #15 screens are stuck on, which is weak and non-monotonic by #15 §3.1's own admission).

| variant_A explainer all-root class | n | B-fail rate |
|---|---|---|
| INSTITUTION (seller/servicer) | 17 | 0.00 |
| GEOGRAPHY (property_state) | 6 | 0.17 |
| named | 11 | 0.18 |
| **LOANSIZE (original_upb)** | 10 | **0.60** |

Provisional screen: *skip the band-B fit unless variant_A roots on loan size.* In-sample: skips 34/44
(77% coverage) at **8.8% false-skip**, vs naive full-skip 20.5% and the frozen R²_A screens'
~34–45% coverage at 10–15% targets. In-sample it dominates both stamped screens.

## Why this is NOT yet a claim (overfit-suspicion, mandatory)

- **Found AFTER peeking** at the corpus whose structure suggested it ⇒ MORE overfit-suspect than the
  frozen #15 screens, not less, despite better numbers. This is exactly the post-hoc screen #15's
  discipline says must be validated fresh on held-out, never adopted in-sample.
- **Thin cells:** loan-size n=10; the clean 0/17 institution leg is the only robust-looking one.
- Cannot retroactively join frozen #15 (the cheap-predictor family is frozen, and the all-root carrier
  class is a *richer* predictor than the frozen family's "named-features-used vector"). It would be its
  own held-out pre-reg.

## Two structural caveats that bound generalization (load-bearing)

1. **The asymmetry is a prohibition-design artifact, not an intrinsic carrier property.**
   `GEOGRAPHY_LENDER_PROHIBITED = [property_state, msa, seller_name, servicer_name]`; variant_B keeps
   only `original_upb`. So loan size is the *only surviving extension*. Geography/institution carriers
   are *forced* to displace (their feature is removed → band reorganizes onto named → recovers); loan
   size *persists* (still available → stays un-named → fails). The screen really detects "is the
   carrier the one extension the prohibition leaves standing." Change the prohibition set and the screen
   changes. **A clean test would vary the prohibition set** (e.g. prohibit loan size too, or keep
   geography) to confirm it's carrier-survival, not carrier-identity per se.
2. **The institution-recovery leg is COVID-concentrated and largely servicer.** 15/17 institution-rooted
   cells are 2020Q2; servicer-rooted is 10/10 COVID. Servicer is post-origination ⇒ servicer carrying
   origination-default-disagreement smells like forbearance leakage or risk-correlated portfolio
   assignment, not underwriting. The "institution never fails" leg is essentially **untested outside
   COVID** and may not transport. Held-out test MUST stratify by regime and treat the institution leg
   as regime-specific until shown otherwise.

## Falsifiable predictions (provisional — to freeze later if pursued)

- On the #15 42-vintage held-out corpus (built for exactly this kind of test): loan-size-rooted
  A-inadequate cells fail at an elevated rate (>> base rate); institution/geography-rooted cells
  recover at near-base. **Falsified if** loan-size-rooted cells do not fail at elevated rate, OR
  institution-rooted cells fail at elevated rate outside COVID.
- The prohibition-set variation (caveat 1) flips the screen: prohibiting loan size too should remove the
  loan-size failure concentration. **Falsified if** failures persist on a different surviving extension.

## Robust residue (survives even if the screen dies on held-out)

The *conceptual* reframe is robust to the exact rule's fate: **the predictor of irreducibility is
which feature carries the disagreement, not how inadequate the named vocabulary is.** This is why the
R²_A-magnitude screens are weak. Holds across the two failure modes, the displacement map, and the
carrier-class table regardless of whether the skip-rule transports.
