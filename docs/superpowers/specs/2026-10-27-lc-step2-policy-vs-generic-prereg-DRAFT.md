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

## 3. Arms (r3)

- **G (generic monotone):** unconstrained CART classifiers predicting acceptance that **pass an exact monotonicity
  check on their leaf boxes**: accept probability non-decreasing in score and non-increasing in DTI, to within
  δ = 0.02. **Not sklearn's `monotonic_cst`.** Its midpoint bounds are sufficient for monotonicity but not necessary,
  and they forbid the 720 interaction leaf the written rule needs, even though the rule is monotone. On a constructed
  follower, a `monotonic_cst` tree gains 0.08 from gating and an unconstrained one gains 0.0. Built on it, the verdict
  would be POLICY_MATTERS for any lender. This is guarded by a test. Every tree uses score and DTI, the standard credit priors, with no policy numbers; amount and
  employment length are added at random. Depth ∈ {2, 3, 4}; min leaf ∈ {1000, 3000}; a 100,000-row bootstrap per tree.
  G(ε) = trees with validation log loss ≤ (1+ε)·best, ε ∈ {0.005, **0.01 (primary)**, 0.02}.
- **P (compiled policy) = each G member gated by the written rule:** P(accept) := 0 wherever the rule, as written,
  declines. "Compiling the policy" means exactly this. The question is whether the gate changes near-optimal models
  materially.

The owner has read the policy, so G can't be fixed *before* reading it. Instead, G uses no policy threshold: it is
sign constraints only.

## 4. Checks (policy-kill lessons, and the r1/r2 adversary findings)

- **Monotonicity: exact leaf-box check at the probability level, with leaf probabilities estimated on the held-out
  validation rows.** A violation is a pair of leaves A, B where some point of B dominates some point of A (score ≥,
  DTI ≤, other features overlapping) and p(A) − p(B) > max(δ = 0.02, 3 standard errors of the difference). Held-out,
  because CART chooses splits to maximise leaf differences: on pure noise a depth-3 tree showed a 3.8-SE gap in its
  training leaves. Scaled by SE, because at min leaf 1000–3000 a fixed δ alone flags leaf noise. The r1 filter checked decisions at a plateau threshold, so leaf noise at the 717.5 split failed it
  (r1 finding 2). Probabilities with δ don't have that problem. Tested: a reversed tree fails; a flat-rate noise tree
  passes; the rule's own staircase passes.
- **No decision threshold:** the verdict works on probabilities and log loss, so there's no plateau cut to land on (r1
  finding 1).
- **Diagnostics (not in the verdict):** the share of G members with an exact leaf-box violation (a leaf with
  P(accept) > 0.01 intersecting the declined region, with 0.5-point DTI and one-score-bucket tolerance, holding ≥ 10
  test applicants), for the full rule and for the floors alone; the gain by depth and min leaf.
- `straddle32` (float32 probes at split thresholds) is used for reason fidelity, where thresholds are crossed.
- Every branch is shown reachable on constructed lenders (§6).

## 5. Metrics

- **gain(m)** = validation log loss of m − validation log loss of gated m. Positive means the policy helps.
- **E = ε · best**, the Rashomon band width.
- Per seed: median gain over G(ε), the share of members with gain < 0.1·E, the share with gain > E, and how many
  sampled trees fall inside the band after gating.
- **Reason fidelity (secondary, pre-registered):** for up to 300 test applicants the written rule declines, and each
  member of G(ε), the *first reason* is the single feature whose change across one of the tree's split thresholds
  most raises P(accept). Reported: the share of (applicant, member) pairs whose first reason is outside the rule's
  own reasons. The rule's own reasons are DTI when DTI ≥ 30; DTI *or* score when FICO < 720 and DTI is in [25, 30),
  since reaching 720 makes the applicant eligible; and score when FICO < 660. This is the Reg B adverse-action
  question with a known true reason (widener).
- **Stability:** 5 sampler seeds. The train/validation/test split is fixed (seed 20261027), so the seeds test sampler
  stability only, not split stability (r1 finding 9). A seed is VOID if |G(ε)| < 200. n_G is reported at every ε,
  because the band width is near the log-loss standard error (r1 finding 10).

## 6. Verdict (r4; primary ε = 0.01; each seed, then across seeds)

**Primary quantity: the share of G(ε) that the written record materially changes.** For each member, a paired test
over validation rows of the per-row log-loss difference (member − gated member). The change is **material if |z| > 3
and |gain| > 0.001 × best loss**, both required. The magnitude floor is there because with about 78,000 validation
rows the paired test found 2.5 × 10⁻⁶ nats "significant": 40% of the ε = 0.005 band was counted as corrected with a
median gain of 0.0000025. On the constructed follower the two populations sit about three orders of magnitude apart
(0.0000025 vs 0.0016 nats), so any floor between about 10⁻⁵ and 10⁻³ classifies them the same way. Sensitivity is
reported at floors of 0.0001 × and 0.003 × best, together with the share significant at any size.
- **share_corrected** = the share with z > 3 (gating materially improves the fit).
- **share_worsened** = the share with z < −3 (gating materially worsens it).

Verdicts:
- **CONTRADICTS:** share_worsened > 0.5. The record disagrees with the decisions.
- **POLICY_MATTERS:** share_corrected > 0.5. Most near-optimal models misstate the rule, and the record corrects them.
- **KILL:** share_corrected + share_worsened < 0.10. The near-optimal models already embody the rule.
- **INCONCLUSIVE:** otherwise.
- **Across seeds:** at least 4 of 5 non-VOID seeds must agree; more than 1 VOID gives INCONCLUSIVE.
- **Reported at every ε** as a curve (share_corrected against ε), since the band's composition changes with ε.

**Why r3's ε-relative bars were dropped.** On a LendingClub-shaped constructed follower (357,000 rows, 10% accepts),
the band holds two populations: the best trees embody the rule (gain ≈ 0.0000025), and slightly worse trees pool
across the cap (gain ≈ 0.0016 nats). Because E = ε·best scales with ε and the pooling gain doesn't, the r3 verdict went
KILL (ε = 0.005) → INCONCLUSIVE (0.01) → KILL (0.02). That's a knife-edge produced by comparing a fixed quantity with an
ε-relative bar. r4's paired test asks of each model whether the record changes it beyond its own noise, which doesn't
scale with ε. The r3 power-check output is kept in the run directory with the result.

**This is the last redesign before freeze.** Each revision so far (r1–r4) was driven by constructed lenders the owner
built, before any real fit. That's legitimate, and it's also how a design drifts toward what synthetic data rewards.
r4 goes to a second blind adversary with the power curve attached. Whatever survives is frozen, INCONCLUSIVE
included.

**Both branches are reachable, shown on constructed lenders before freeze:**
- a follower whose trees can find the staircase gives KILL;
- a lender that ignores the 720 conditional gives CONTRADICTS;
- a follower with models too coarse to hold the rule (depth 1) gives POLICY_MATTERS.

(All three were re-verified under r4.)

So the verdict on real data depends on what LendingClub's decisions look like to near-optimal monotone trees. That
is the empirical question.

**What POLICY_MATTERS would mean, stated honestly (r1 finding 4):** step 1 found no accepted loan the rule declines.
So POLICY_MATTERS can't mean the data lacks the rule. It means **near-optimal coarse models of a lender that followed
its rule misstate that rule**, and the written record corrects them by more than the models differ among themselves.
That is a property of the models, and it is the record-versus-model claim. N = 1.

## 7. Demonstration, not a test: out-of-time across 2014-07-25

Fit G on 2014-01-01 to 2014-07-24 (features DTI, amount, employment length; no score, since Vantage and FICO are mixed
after 2013-11-05). Predict 2014-08-01 to 2014-12-31. Report the share of test applicants with DTI in [35, 40) that G
declines and LendingClub accepted, against P with the dated cap. **Documented behavior predicts P wins** (step 1
already showed decisions changed on the date), so this is reported as a demonstration that a dated written record
carries information historical data lacks. It doesn't enter the verdict.

## 8. Forecasts (owner, before any fit)

| ID | p |
|---|---|
| Verdict KILL | 0.25 |
| Verdict POLICY_MATTERS | 0.55 |
| Verdict INCONCLUSIVE | 0.15 |
| Verdict CONTRADICTS | 0.05 |
| At least 4 of 5 seeds non-VOID | 0.70 |
| Reason fidelity: outside-truth share ≥ 0.10 | 0.40 |

(Revised at r3 and r4, before any fit. A LendingClub-shaped constructed follower gives POLICY_MATTERS at ε = 0.01:
81% of the band is corrected by the record. So POLICY_MATTERS is the expected branch *if* real decisions look like the
synthetic follower. Real reject composition may differ: if near-optimal trees on real data find the staircase, KILL.
The constructed expectation is recorded so the real result can be read against it, not fitted to it.)

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
