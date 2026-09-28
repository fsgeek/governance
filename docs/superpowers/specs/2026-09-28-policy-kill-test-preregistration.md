# Policy-vs-ε kill test — pre-registration

**Date:** 2026-09-28. **FROZEN** at the commit adding this file **and** `scripts/policy_kill/run.py`
(harness frozen with the pre-reg this time; see the retention-drift lesson).
**Decides:** whether governance continues as a research program (§6).

## 1. Question

Prior art (09-26) leaves one open contribution: compiling a *written policy* into the model space.
It only matters if **policy restriction changes the admissible set materially relative to ε
restriction alone.** If near-optimal trees already respect the policy, the compiler is decoration.

## 2. What the "policy" is (declared weakness)

`policy/fnma_eligibility_matrix.yaml` is a **medium-fidelity reconstruction** of the public Fannie
Mae Selling Guide / Eligibility Matrix by an earlier instance, not a transcription. In model-class
terms it gives: 5 monotonicity constraints (FICO −, DTI +, LTV +, CLTV +, MI coverage − on
P(default)); a 13-feature "mandatory" list that no depth ≤ 4 tree can satisfy (**not applied**:
structurally impossible, would force shrinkage by construction); no prohibited features; eligibility
gates, applied **as a population filter to both arms** (not what is tested). The yaml itself flags
the MI sign as possibly wrong in data.

## 3. Design

FM single-family 2015Q1 acquisitions via `wedge.collectors.fanniemae.load_collapsed_cached`
(existing 24-month default label), filtered to the policy envelope. 11 features. Split 55/22/23
train/validation/test, seed 20260928. **Sampled** (not enumerated) Rashomon set: 3,000 CART trees,
random feature subsets of size 3–6, depth ∈ {2,3,4}, min leaf ∈ {200,1000,3000}, bootstrap rows.
R(ε) = trees with validation log loss ≤ (1+ε)·best; ε ∈ {0.005, **0.01 (primary)**, 0.02}.
Decision per model: decline if P(default) ≥ that model's validation 80th percentile.
Policy set R^P(ε) = members of R(ε) with no monotonicity violation on a 1,000-row probe set, checked
exactly at every split threshold of each constrained feature the tree uses.

Variants: violation at **decision level** (the decline decision moves against policy; primary) vs
**probability level**; with vs **without the MI constraint (primary excludes MI)**.

## 4. Metrics

retention = |R^P|/|R|; per-applicant P(flip) = min(share declining, share approving) over members,
on the test set; Δ mean P(flip); ambiguous set = applicants with P(flip) > 0; Jaccard of ambiguous
sets R vs R^P; mean |ΔP(flip)|.

## 5. Verdict rule (primary: ε = 0.01, decision-level, MI excluded)

- **KILL** (compiler adds nothing): retention ≥ 0.90 AND |Δ mean P(flip)| < 0.01 AND ambiguous
  Jaccard ≥ 0.90.
- **POLICY_MATTERS:** retention ≤ 0.50 OR ambiguous Jaccard ≤ 0.70 (or policy leaves < 2 members).
- **INCONCLUSIVE:** otherwise. **VOID** if |R| < 30.

**Documented behavior that could trigger each branch (the retention-drift lesson):**
- KILL: shallow trees on credit data are widely observed to respect FICO/LTV/DTI monotonicity
  already. That *is* the question: if it holds here, the policy's model-class content is redundant
  with the data, which is the result.
- POLICY_MATTERS: (i) a mis-signed constraint (MI) forcing shrinkage from policy *error*: primary
  excludes MI; (ii) noise non-monotonicity in small leaves (probability jitter) that no underwriter
  would care about: primary checks the *decision*, not the probability; (iii) the mandatory list
  forcing shrinkage by construction: not applied. Residual risk: decision-level violations can
  still come from noise near the threshold. I'll report retention by min-leaf size as a diagnostic.

## 6. What the verdict decides

- **KILL → governance closes as a research program.** The closing is written up; the next project
  is chosen separately (candidate: the lineage calibration-record study, itself prior-art-checked
  and adversary-reviewed first).
- **POLICY_MATTERS → necessary, not sufficient.** Next: check that the effect survives a faithful
  policy transcription and a complete (not sampled) enumeration, then the compiler + attested-set
  systems paper.
- **INCONCLUSIVE → the blind adversary rules first; then I decide.** Reasons recorded.
- Blind adversarial review before any result sentence, whatever the verdict.

## 7. Bet

55% KILL, 20% POLICY_MATTERS, 25% INCONCLUSIVE. (Reason: the policy's model-class content is five
monotonicities on features whose risk direction is obvious in the data.)

## 8. Disclosure

Before freezing, one smoke run with 40 trees (instead of 3,000) checked that the harness executes.
Its stdout was suppressed and its results.json written to the session scratchpad, unread. No
number from it informed anything above.
