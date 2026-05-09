# V₁ → V₂ Predictive Test — Pre-Registration

**Date:** 2026-05-09.
**Status:** Pre-registration. Predictions committed to git (and OTS-stamped) *before* the comparison test is run. The comparison is to be executed separately, against this document as the prediction record. Any post-hoc reinterpretation of predictions found here is exactly the discipline failure this document exists to prevent.
**Scope:** Predicted shifts in per-feature factor-support distributions across the Rashomon set R(ε) between LendingClub vintages V₁ = 2014Q3 and V₂ = 2015Q4, with mechanisms tied to claimed LC underwriting changes during that period.
**Anchoring:** Memo-internal claims about LC's 2014-2015 underwriting trajectory (`2026-05-08-vintage-stability-findings-note.md` §2) plus general knowledge of the LC platform's underwriting evolution. **External documentation verification (LC 10-Ks, industry coverage from the period) is owed before the comparison test is fully credible.** The pre-registration discipline operates regardless; the credibility of the *anchoring* is what's bounded.

---

## 1. Why this exists

The 2026-05-07 wedge design spec §3 named V₁ → V₂ predictive testing as the methodology's central predictive falsification: the methodology should be able to predict the *direction* of factor-support shifts in R(ε) when underwriting policy changes between vintages. The spec §10 specified pre-registration as non-optional: "Post-hoc rationalization of observed shifts is exactly the failure mode the methodology critiques in others; the prototype must hold itself to the standard it argues for."

This test has been named since 2026-05-07 and has not been executed. The vintages exist (`runs/`); the predictions have not been written. This document writes the predictions, anchored to what's known now, so the test can be run against a committed record rather than against memory.

The bin-4 case-reading note (2026-05-08) is a worked instance of the discipline. The pre-prediction (12-15 fits / 5-8 ambiguous / 1-3 contradicts) landed at (2 / 11 / 7); the frame failed; the discipline made the failure honest rather than rationalizable. The same discipline is being applied here.

## 2. Vintages and rationale

- **V₁ = 2014Q3** — earliest vintage available in committed `runs/` (`2026-05-08T17-43-21Z.jsonl`). Pre-2015 underwriting regime.
- **V₂ = 2015Q4** — latest vintage available (`2026-05-08T17-44-39Z.jsonl`). Post-mid-2015 changes; per the vintage-stability note, downstream of the 2015Q3 transition period.

The 2014Q3 → 2015Q4 gap is the largest available in committed data. It crosses the documented 2015 transition window. This maximizes the signal a directional test could detect.

A secondary comparison (2014Q3 → 2015Q3) is also informative because 2015Q3 is the *transition vintage*; predictions about transition behavior can be tested separately. The primary test is V₁=2014Q3 / V₂=2015Q4; the secondary is V₁=2014Q3 / V₂=2015Q3 to characterize the trajectory.

## 3. Anchoring claims (LC policy changes 2014 → 2015)

Each predicted shift below depends on one or more of these claimed underwriting changes. The claims are stated here so the comparison phase can verify them against external sources (LC 10-Ks for FY2014 and FY2015, FinTech industry coverage of unsecured-consumer-lending shifts in the period).

- **C1. Income verification tightening.** Per `2026-05-08-vintage-stability-findings-note.md` §2: "documented industry-wide changes in income verification and FICO weighting were rolling through the unsecured-personal-loan space" in 2015. Direction: more loans had verified income in V₂ than in V₁.
- **C2. FICO floor adjustment.** General knowledge of LC's underwriting trajectory: FICO minimums tightened over 2014-2015 as the platform moved upmarket. Direction: fewer subprime borrowers in V₂ than V₁; the surviving population's FICO range narrows from below.
- **C3. DTI ceiling tightening.** Similar trajectory; DTI maximums tightened. Direction: fewer high-DTI borrowers in V₂ than V₁.
- **C4. Term-mix shift toward 60-month loans.** The wedge filters to 36-month loans only, so this shift affects who *opts into* 36-month financing in V₂. Direction: 36-month borrowers in V₂ may skew toward different employment/income profiles than V₁ if more conservative profiles migrate to 60-month products.

**External verification owed:** specific dates, magnitudes, and policy texts for each of C1-C4. The comparison phase should not run before this verification, or should run with explicit acknowledgment that the anchoring is internal-only at the time of running.

## 4. Predictions

Each prediction has the form: *which feature* shifts in *which direction* in factor-support distribution across R(ε) between V₁ and V₂, attributable to *which anchoring claim*, via *which mechanism*. Hit criteria are in §5.

### Prediction P1 — annual_inc factor support increases (V₂ > V₁)

- **Anchoring:** C1 (income verification tightening).
- **Mechanism:** When income is verified, the trees can treat it as a higher-signal feature; unverified income is noisier and discount-able. Tighter verification raises annual_inc's signal-to-noise, which raises its information gain at splits, which raises its weight in path-level factor support.
- **Direction:** Mean factor_support_T weight on annual_inc across R(ε) members should be *higher* in V₂ than V₁. Same for factor_support_F.
- **Confidence:** Moderate-high. C1 is the most clearly directional of the anchoring claims, and the mechanism (verification → signal reliability → information gain) is direct.

### Prediction P2 — fico_range_low factor support decreases (V₂ < V₁)

- **Anchoring:** C2 (FICO floor adjustment).
- **Mechanism:** When the FICO floor rises, the surviving population's FICO range compresses from below. CART splits on fico_range_low have less remaining variance to exploit. Information gain at FICO splits decreases because the splits operate in a narrower range. The split count on fico_range_low may stay the same (CART will still use it where it can), but the per-split information gain — and therefore the path-level attribution weight — shrinks.
- **Direction:** Mean factor_support_T weight on fico_range_low across R(ε) members should be *lower* in V₂ than V₁. Same for factor_support_F.
- **Confidence:** Moderate. The mechanism is well-understood (range compression → information gain reduction) but the *magnitude* depends on how much the FICO floor actually moved, which is owed to external verification.

### Prediction P3 — dti factor support decreases (V₂ < V₁)

- **Anchoring:** C3 (DTI ceiling tightening).
- **Mechanism:** Same shape as P2. Tighter DTI ceiling compresses the population's DTI range from above; trees have less DTI variance to exploit; information gain at DTI splits decreases; path-level factor support on DTI decreases.
- **Direction:** Mean factor_support weight on dti across R(ε) members should be *lower* in V₂ than V₁.
- **Confidence:** Moderate. Lower than P2 because DTI ceilings in unsecured personal lending are softer caps than FICO floors (lenders sometimes accept high-DTI applicants with offsetting strength elsewhere); the directional prediction may be diluted.

### Prediction P4 — emp_length factor support shifts in V₂ (direction less certain)

- **Anchoring:** C4 (term-mix shift) + indirect employment-stability correlations.
- **Mechanism:** If more conservative borrowers (longer employment, more stable income) migrate to 60-month products in V₂, the 36-month V₂ population may have *less* employment-length variance at the high end. Information gain on emp_length splits could increase (if the shift makes emp_length more discriminative within the residual 36-month population) or decrease (if it removes the high-end tail that previously carried discriminative signal).
- **Direction:** *Indeterminate* in advance. Recorded as a prediction-of-uncertainty: emp_length should *shift*, but I do not pre-commit to a direction.
- **Confidence:** Low on direction; moderate on shift-occurring.

### Prediction P5 — overall factor-support stability decreases (V₁ → V₂)

- **Anchoring:** C1+C2+C3 collectively (multiple simultaneous policy changes).
- **Mechanism:** When multiple features experience underwriting changes simultaneously, the surviving population's joint feature distribution shifts in ways that affect the trees' splits unevenly across R(ε) members. Different members of R(ε) — with different feature subsets and hyperparameters — will adapt differently to the new distribution. Pairwise factor-support overlap across R(ε) members should *decrease* in V₂ relative to V₁.
- **Direction:** Median pairwise factor-support overlap among R(ε) members should be *lower* in V₂ (i.e., more reasoning-disagreement) than V₁.
- **Confidence:** Moderate. This connects to the vintage-stability finding that 2015Q3 (transition vintage) had overlap_T = 0.60 vs ~0.85 for stable-regime vintages; if the 2015Q4 vintage has only partially settled into the new regime, its overlap should be *between* 2014Q3 and 2015Q3.
- **Note:** This prediction is at a higher-order than P1-P4 and is the methodology's most distinctive claim — that *reasoning-disagreement* tracks *underwriting-flux*.

## 5. Hit criteria

For P1-P3 (directional predictions on individual features):

- **Hit:** Mean factor support on the named feature shifts in the predicted direction, with effect size ≥ 5% of V₁ baseline.
- **Near-hit:** Predicted direction observed but effect size < 5% of V₁ baseline.
- **Miss:** Opposite direction observed (effect size doesn't matter; direction is the load-bearing claim).
- **Indeterminate:** R(ε) members shift in mixed directions (no clear central tendency).

For P4 (predicted-shift, undirected):

- **Hit:** Mean factor support on emp_length shifts in either direction with effect size ≥ 5% of V₁ baseline.
- **Miss:** No detectable shift (effect size < 5% in either direction).

For P5 (overall reasoning-disagreement):

- **Hit:** Median pairwise factor_support overlap across R(ε) members in V₂ is *lower* than in V₁ by at least 0.05 (overlap is a 0-1 quantity; a 0.05 absolute change is meaningful given vintage-stability findings showed overlap_T spanning 0.60-0.87).
- **Near-hit:** Lower by 0.01-0.05.
- **Miss:** Higher in V₂ than V₁.

For each prediction, the comparison phase reports: hit/near-hit/miss/indeterminate, plus the actual measured shift, plus a one-sentence interpretation. No prediction may be reinterpreted after the comparison runs.

## 6. Comparison protocol

1. Reuse existing committed jsonl runs:
   - V₁: `runs/2026-05-08T17-43-21Z.jsonl` (2014Q3)
   - V₂: `runs/2026-05-08T17-44-39Z.jsonl` (2015Q4)
   - Optional secondary: `runs/2026-05-08T16-26-41Z.jsonl` (2015Q3) for trajectory characterization
2. Compute per-feature factor-support summary across R(ε) per vintage. For each case, average factor_support_T weight on each feature across the 5 R(ε) members; aggregate across cases (mean and quartiles); compute the cross-R(ε)-member variance (which feeds P5).
3. For each prediction P1-P5, compute the comparison statistic; classify against §5 hit criteria; report hit/near-hit/miss/indeterminate.
4. Write findings note: hit rate, miss rate, examples of each, methodology interpretation.
5. **No prediction may be reinterpreted post-hoc.** If a prediction misses, that is the result. The methodology either has predictive content per this test or it doesn't.

## 7. Honest caveats

- **External verification of anchoring claims (C1-C4) is owed.** The comparison test should not be run before this verification, or should be run with explicit acknowledgment that anchoring is internal-only. The pre-registration discipline still works either way; what's bounded is the credibility of the link between LC's actual policy changes and the predictions.
- **N=2 vintages is thin.** Even a clean hit on P1-P5 would not establish methodology-general predictive content; only its presence on this dataset between these vintages. Replication across additional vintages and across datasets (HMDA is the planned second) is owed for any general claim.
- **Pre-registration is informal.** Committed to git + OTS-stamped, but not registered with any external pre-registration platform (OSF, etc.). The OTS stamp provides time-anchoring; external registration would provide additional credibility, but the OTS chain is acceptable for in-project work.
- **Predictions are constrained to the wedge's current feature pool** (fico_range_low, dti, annual_inc, emp_length). Documented LC changes that affect features outside this pool — revolving credit policy, debt verification, employment verification specifics — cannot be predicted here. The species/feature-pool inheritance finding from `2026-05-08-bin4-k5-case-reading-findings-note.md` suggests this is a real limitation, not just a sampling artifact: the wedge's view of "leverage" is DTI-only, so policy changes to revolving credit underwriting are invisible to the test.
- **Mechanism articulation is the single-reader work** of an Opus 4.7 instance under heavy scaffolding, late in a long session. The same instance acknowledged contracted ceiling in conversation immediately before writing this. A fresh instance might articulate sharper mechanisms; a thin-prompt instance might predict differently. The pre-registration discipline does not require optimal predictions, only honest ones, but the limitation is worth flagging.

## 8. What this document does NOT do

- Does not run the comparison. The comparison is the next step, to be executed by the same or a different instance against this committed record.
- Does not commit to a date for running the comparison. The comparison should run after external verification of anchoring claims (or with explicit acknowledgment of the anchoring's limits).
- Does not pre-commit to which vintages will be compared *additionally* if the primary comparison hits/misses interestingly. Follow-on comparisons (2015Q3 trajectory, future vintages) are open.
- Does not commit to a follow-up prediction structure. If P1-P5 produce informative results, the next round of predictions (e.g., for 2016+ vintages, or for HMDA) will be designed at that point, not pre-committed here.

## 9. Connection to other working documents

- **`2026-05-07-rashomon-prototype-wedge-design.md` §3 + §10.** The spec named this test as the methodology's central predictive falsification and required pre-registration. This document discharges that requirement.
- **`2026-05-08-vintage-stability-findings-note.md` §2.** The transition-vintage observation about 2015Q3 is the empirical bridge to P5 (predicting that 2015Q4 has only partially-settled overlap).
- **`2026-05-08-bin4-k5-case-reading-findings-note.md` §3.** The species/feature-pool inheritance finding bounds what can be predicted in §7.
- **`2026-05-09-conversation-residue-capture.md` §4.** The I-stability experiment is named there as a separate pending test. This document does not address that experiment; it addresses the orthogonal predictive-content test from the wedge spec §3. Both can be run; neither blocks the other.
