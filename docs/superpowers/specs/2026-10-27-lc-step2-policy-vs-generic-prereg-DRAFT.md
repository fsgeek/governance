# Pre-registration (DRAFT, not frozen): does compiling LendingClub's written policy change the set of good models? (step 2, P vs G)

**Status: DRAFT.** It freezes as a new file, with its harness (`scripts/lc_policy/pvg.py` and tests), in one stamped
commit, after a blind adversary and a widener, and after the harness passes on constructed violators. **No model is
fit on real data before that commit.** Seen so far: column names; sample counts for the window (322,366 Policy-Code-0
rejects, 1.3% missing risk score; 35,047 accepts); step 1's result.

**Program context.** This is the one experiment the closing note's 10-26 addendum reopened. Step 1 (GOVERNS) showed the
written DTI cap is the operative one. The design note (`2026-10-26-lc-step2-design-note.md`, retraction section) records
why the earlier conformance-audit proposal was withdrawn.

## 1. Question

If near-optimal models of LendingClub's *decisions* already respect its written policy, compiling the policy into the
model space is decoration (**KILL**, the closing note's kill). If the policy excludes many near-optimal models, or
changes which applicants are ambiguous, compiling it adds something the data alone doesn't give (**POLICY_MATTERS**).

The test is the only quantified policy content beyond sign constraints that the public declines can check: the
**V5/V6 interaction rule**, 2011-01-06 to 2012-05-31 (source table, rows V5–V6):
- FICO ≥ 660;
- DTI (excluding mortgage) below **25% if FICO < 720**, below **30% if FICO ≥ 720**.

## 2. Data

- **Applications, 2011-01-06 to 2012-05-31.** Rejects: `Policy Code == 0` by `Application Date`. Accepts:
  `policy_code == 1`, Individual, Cash, `issue_d` 2011-02 to 2012-05 (issue month, so the first window month is
  dropped for the lag). Label: accepted = 1.
- **Features, common to both files:**
  - score: rejects `Risk_Score`; accepts `fico_range_low`. Both are put in 5-point buckets. FICO throughout, since the
    Vantage switch is 2013-11-05.
  - DTI (percent; rejects parsed by step 1's `parse_pct`, "-1%" excluded);
  - amount requested / `loan_amnt`;
  - employment length (both files use the same text categories, mapped to 0–10, "n/a" = −1).
  - No state, no date: the rule doesn't use them.
- Rows missing score or DTI are excluded and counted.
- Split 55/22/23 train/validation/test, stratified by label, seed 20261027.

## 3. Arms

- **R(ε):** a sampled Rashomon set of CART classifiers predicting acceptance. Feature subsets of size 2–4 drawn from the
  4 features; depth ∈ {2, 3, 4}; **min leaf ∈ {1000, 3000}** (closing note: ≥ 1000); rows bootstrapped. The set is the
  trees with validation log loss ≤ (1+ε)·best, ε ∈ {0.005, **0.01 (primary)**, 0.02}. Each tree's decision is "accept
  iff P(accept) ≥ that tree's validation quantile matching the observed acceptance share".
- **G (generic monotone, fixed without the policy's numbers):** members of R(ε) whose decisions are monotone:
  non-decreasing in score and non-increasing in DTI. The owner has read the policy, so G can't be fixed *before*
  reading it. Instead, G is fixed **without using any policy threshold**: it is sign constraints only, the standard
  credit priors.
- **P (compiled policy):** members of G that never accept an applicant the written rule declines, on the probe set
  (§4). P = G ∩ {respects the FICO floor and the FICO-conditional DTI caps}.

## 4. Checks (with the policy-kill lessons applied)

- **Probe set:** 2,000 validation rows plus a constructed grid: score buckets 640–800 by 5 × DTI 0–35 by 0.5, with
  amount and employment length at their medians.
- **Monotonicity (G):** for each constrained feature a tree uses, the decision is checked at the two **float32** values
  that straddle each split threshold t (`straddle32`). sklearn casts X to float32 and compares it in double against
  t, so a float64 `np.nextafter` can round back to the wrong side. That is the policy-kill bug class. A constructed
  test shows float64 `nextafter` misjudges a real tree; the guard is mutation-checked.
- **Policy respect (P):** a tree violates if it accepts any probe point with FICO < 660, or DTI ≥ 25.5 with FICO < 720,
  or DTI ≥ 30.5 with FICO ≥ 720. That is the written rule with a **0.5-point DTI tolerance**, so a learned cutoff at
  25.02 instead of 25.00 isn't a violation: noise near the threshold was the policy-kill confound. Score is bucketed
  by 5, so it needs no tolerance.
- Every check is tested on constructed violators before freeze.

## 5. Metrics (closing-note definitions, P vs G)

- **retention = |P| / |G|.**
- **Per-applicant P(flip)** = min(share accepting, share declining) over members, on the test set.
- **Ambiguous set** = test applicants with P(flip) > 0. **Jaccard(ambiguous_G, ambiguous_P)**.
- |Δ mean P(flip)|.
- **Decomposition (diagnostic, not in the verdict):** P1 = G ∩ {FICO ≥ 660 and DTI < 30.5 for everyone}, the floors
  alone. The report gives retention(P1 | G) and retention(P | P1). The second is the share the 720 interaction adds on
  top of the floors. If P is small mainly because trees ignore score and break the FICO floor, the decomposition shows
  it, and the write-up must not credit the interaction for it.
- **Stability (closing note):** the run is repeated over **5 sampler seeds**. A seed is **VOID** if |G| < 200
  (n_R ≥ 200). A verdict counts only if at least 4 of 5 seeds are non-VOID and agree.

## 6. Verdict (primary: ε = 0.01; each seed, then across seeds)

- **KILL:** retention ≥ 0.90 AND ambiguous Jaccard ≥ 0.90 AND |Δ mean P(flip)| < 0.01.
- **POLICY_MATTERS:** retention ≤ 0.50 OR ambiguous Jaccard ≤ 0.70.
- **INCONCLUSIVE:** otherwise, or if the seeds don't agree (fewer than 4 of 5 the same), or if more than 1 seed is VOID.

**Documented behavior that would trigger each branch:**
- KILL: LendingClub enforced the rule exactly (step 1's pattern), so trees fit on its decisions learn the cutoffs,
  including the 720 conditional, and respect them.
- POLICY_MATTERS: the FICO ≥ 720 × DTI [25, 30) cell is small; with min leaf ≥ 1000, trees can't resolve the
  conditional and smooth across it, so many accept FICO < 720 applicants at DTI 25–30 (or decline FICO ≥ 720 ones).
  Only the second is allowed by the written rule, and it doesn't count as a violation.
- INCONCLUSIVE: noise in leaves near the cutoffs, or sampler instability.

**Why this one can come out either way:** the KILL path needs trees to resolve a conditional in a small cell under a
leaf-size floor; the POLICY_MATTERS path needs them to fail. Neither is documented behavior of the lender. It is a
property of models of its decisions, which is the question.

## 7. Demonstration, not a test: out-of-time across 2014-07-25

Fit G on 2014-01-01 to 2014-07-24 (features DTI, amount, employment length; no score, since Vantage and FICO are mixed
after 2013-11-05). Predict 2014-08-01 to 2014-12-31. Report the share of test applicants with DTI in [35, 40) that G
declines and LendingClub accepted, against P with the dated cap. **Documented behavior predicts P wins** (step 1
already showed decisions changed on the date), so this is reported as a demonstration that a dated written record
carries information historical data lacks. It doesn't enter the verdict.

## 8. Forecasts (owner, before any fit)

| ID | p |
|---|---|
| Verdict KILL | 0.40 |
| Verdict POLICY_MATTERS | 0.30 |
| Verdict INCONCLUSIVE | 0.30 |
| At least 4 of 5 seeds non-VOID | 0.75 |
| retention (primary, median over seeds) ≥ 0.90 | 0.45 |

## 9. What each verdict means for the program

- **KILL:** compiling LendingClub's written policy adds nothing a model of its decisions doesn't already contain, on
  the one quantified interaction available. The reopened experiment closes with a kill. The program's record says so.
- **POLICY_MATTERS:** the written policy excludes near-optimal models of the lender's own decisions. A record of the
  rule carries constraints that data-fit models violate. This is the open contribution the closing note named.
  Generality is still N = 1 (one lender, one rule).
- **INCONCLUSIVE:** reported as such. No second attempt on this window.

## r2 work-in-progress note (2026-10-27): not freezable; r3 decided

The first blind adversary raised 4 blocking findings: a plateau threshold (the coin-flip again); the monotonicity
filter discarding the very trees that learned the interaction; VOID likely; POLICY_MATTERS meaning "coarse models
break the rule". r2 rebuilt the harness (`pvg.py` r2): G trained with `monotonic_cst`, the policy checked exactly on
leaf boxes at probability level (P(accept) > 0.01 in a declined region holding ≥ 10 test applicants), the verdict on
retention, and reason fidelity added (widener).

**Constructed test result that blocks r2:** a depth-4 monotone tree fit to a lender that follows the rule *exactly*
(realistic imbalance) has a leaf "score > 657.5, DTI > 19.71" with P(accept) = 0.116. CART's greedy split lands at
19.7, not at the 25% cap, and pools eligible with ineligible applicants. So under r2, KILL is close to unreachable for
coarse trees *even for a lender that follows its rule*. That makes it a gate the model class satisfies, which is not a
test.

**r3 (decided):** "compiling" the policy = gating each G member with the written rule (P(accept) := 0 where the rule
declines). POLICY_MATTERS if gating improves the median member's validation log loss by more than ε·best (the policy
moves models across the Rashomon boundary). KILL if it improves by less than 0.1·ε·best for ≥ 90% of members. Both
thresholds are tied to ε, already fixed. Constructed tests must show **KILL is reachable** (a follower with trees fine
enough to find the cap) and POLICY_MATTERS reachable (a follower with coarse trees, or a lender ignoring the
conditional). Reason fidelity stays as a secondary metric. A power check on realistic synthetic data sets N_TREES.
