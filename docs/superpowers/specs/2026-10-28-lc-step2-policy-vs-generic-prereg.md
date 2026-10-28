# Pre-registration (FROZEN): does compiling LendingClub's written policy change the set of good models? (step 2, P vs G)

**Status: FROZEN (r5)** in this file's first commit (its OTS stamp is the freeze), together with the harness at:
- `scripts/lc_policy/pvg.py` sha256 `7a5638a4882ffc7969f97e86ba0b0870287967494fbe57736af93866f9b2d18b`
- `scripts/lc_policy/test_pvg.py` sha256 `70ad19bc70097a9062893e9d5f7fc498ab9b068620d3a5d959bc7e78d1817ef9` (23 constructed tests, passing at freeze)

Three blind adversary passes were run before the freeze, and the stop rule was not triggered at pass 3. **No model has
been fit on real data** before this commit. Seen so far: column names; window counts; step 1's result. The run is
`uv run python scripts/lc_policy/pvg.py`, unmodified, and its output is committed as the result. Sections §3–§6 and §8
are the operative r5 text. The sections at the end are the dated design history (r1–r5) and are kept as the record.

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
  `policy_code == 1`, Individual, Cash, `issue_d` 2011-03 to 2012-05. Starting at 2011-03 means issue months can't
  predate applications made before the 2011-01-06 rule. Label: accepted = 1.
- **Features, common to both files:**
  - score: rejects `Risk_Score`; accepts `fico_range_low`. Both are put in 5-point buckets. FICO throughout, since the
    Vantage switch is 2013-11-05.
  - DTI (percent; rejects parsed by step 1's `parse_pct`, "-1%" excluded);
  - amount requested / `loan_amnt`;
  - employment length (both files use the same text categories, mapped to 0–10, "n/a" = −1).
  - No state, no date: the rule doesn't use them.
- Rows missing score, DTI or amount are excluded and counted. Employment coded −1 (n/a, missing, unmapped) is
  reported as a share per file, since a coding difference between files would let `emp` mark the file of origin.
- Split 55/22/23 train/validation/test, stratified by label, seed 20261027.

## 3. Arms (r5)

- **G (generic monotone):** unconstrained CART classifiers predicting acceptance that pass an **exact leaf-box
  monotonicity check** (accept non-decreasing in score, non-increasing in DTI). The check uses held-out validation
  leaf estimates (k+0.5)/(n+1), ignores leaves with fewer than 100 held-out rows, and tolerates max(0.02, 3 SE) per
  leaf pair.
  - Every tree uses score and DTI; amount and employment length are added at random.
  - Depth ∈ {2, 3, 4}; min leaf ∈ {1000, 3000}; a 100,000-row bootstrap per tree; 4,000 trees per seed.
  - Not sklearn's `monotonic_cst`: its midpoint bounds can't represent the 720 interaction, which is monotone.
  - No policy numbers are used.
- **P (compiled policy) = each G member gated:** P(accept) := 0 wherever the written rule declines, with tolerances of
  0.5 DTI points and one score bucket at 720. So DTI exactly at 25.00, or a 715 bucket, isn't gated. Log loss clips P
  to [10⁻⁶, 1 − 10⁻⁶], so an accepted row inside the gate costs 13.8 nats; the construct check guards against that.

## 4. Checks

- **Construct check (frozen, decides CONSTRUCT_INVALID):** accepts inside the gate, as a share of accepts in the
  window. Above 0.05%, the gate would measure mismatch between the files, not model misstatement. Step 1 never
  checked these cells for 2011–12, so this can't be assumed.
- **Material change:** for a tree, a paired test over validation rows of the per-row loss difference (tree − gated
  tree). Material if |z| > 3 **and** |gain| > 0.001 × best loss. The gain is reported split into reject-row savings and
  accept-row penalty.
- Every verdict branch is shown reachable on constructed lenders: KILL, POLICY_MATTERS and CONSTRUCT_INVALID end to
  end; DEPENDS_ON_EPSILON on the LendingClub-shaped follower (§6).

## 5. Primary quantity: ε\*

The band excess of a tree is val_loss / best − 1. For each grid value e (60 log-spaced values from 10⁻⁴ to 0.05), the
band is the trees with excess ≤ e. **ε\* = the smallest e at which the band has ≥ 200 members and more than half of
them are materially corrected by the gate.** ε\* is infinite if that never happens. The full curve (e, n, share
corrected) is reported, along with the median gain of corrected trees.

## 6. Verdict (per seed; 5 seeds; ≥ 4 of 5 non-VOID must agree)

- **KILL:** ε\* > 0.02. Rule-misstating models sit outside any reasonable band, so compiling adds nothing.
- **POLICY_MATTERS:** ε\* < 0.005. Even tight bands are dominated by models the record corrects.
- **DEPENDS_ON_EPSILON:** otherwise, reported with ε\*. Whether the record matters depends on how much fit an analyst
  will trade, and ε\* says exactly how much.
- **VOID** if fewer than 200 monotone trees have excess ≤ 0.05. **CONSTRUCT_INVALID** before everything else, per §4:
  accepts inside the gate are above **0.5%** of accepts (0.05% was about 17 loans). This also carries "the record
  disagrees with the decisions". CONTRADICTS is removed because it couldn't fire first (adversary 3).
- **Capacity check (adversary 3, finding 1):** 3 more seeds sample trees of depth {5, 6}. If their ε\* falls in a
  different region from the primary verdict, the verdict becomes **CAPACITY_DEPENDENT** and both are reported.
  Every verdict sentence below is about **trees of depth ≤ 4**.
- **Seeds share one train/validation/test split**, so they repeat the tree sampling only, and 4-of-5 agreement is
  close to automatic. The ε\* range across seeds is reported.
- **Sensitivity (reported):** ε\* under a floors-only gate (FICO 660 / DTI 30, so how much of ε\* comes from the 720
  interaction itself), and at 25% and 75% dominance. Accepts inside the gate are excluded from the materiality test
  and counted.

**Synthetic expectation, recorded before any fit.** A LendingClub-shaped follower (357,000 rows, 10% accepts, 3 seeds)
gave ε\* = 0.0103 in every seed. The curve is a step: share corrected 0 up to 0.83%, then 0.74 at 1.6%. The best tree is
never changed by the gate, and the construct share is 0. So a follower like the synthetic one reads DEPENDS_ON_EPSILON.
Real decisions may put ε\* anywhere. ε\* is a measurement of the real model landscape, not a consequence of the design:
r1–r4 failed on exactly that point.

**What each verdict claims (widener's sentences, written before the result):**
- **KILL:** the record adds no constraint on near-optimal depth-≤4 tree models of this lender's decisions; its value
  is dating and attesting the rule.
- **POLICY_MATTERS:** depth-≤4 tree models within 0.5% of the best are mostly corrected by the record, so a model fit
  to the decisions isn't evidence of what the rule was.
- **DEPENDS_ON_EPSILON:** the same claim, true beyond a stated fit cost ε\*.
- **CAPACITY_DEPENDENT:** the answer depends on tree size, so no claim about the record.
- **CONSTRUCT_INVALID:** the two public files disagree with the written rule (or with each other) too much for the
  gate to measure models. This is reported as a data finding.

All of these are N = 1: one lender, one rule.

**Secondary, reported, not in the verdict:** reason fidelity over the ε = 0.01 band (about 0.7 hours at full scale), and
by-ε shares at 0.005, 0.01 and 0.02.

## 7. Demonstration, not a test: out-of-time across 2014-07-25

Fit G on 2014-01-01 to 2014-07-24 (features DTI, amount, employment length; no score, since Vantage and FICO are mixed
after 2013-11-05). Predict 2014-08-01 to 2014-12-31. Report the share of test applicants with DTI in [35, 40) that G
declines and LendingClub accepted, against P with the dated cap. **Documented behavior predicts P wins** (step 1
already showed decisions changed on the date), so this is reported as a demonstration that a dated written record
carries information historical data lacks. It doesn't enter the verdict.

## 8. Forecasts (owner, before any fit)

| ID | p |
|---|---|
| Verdict KILL | 0.20 |
| Verdict POLICY_MATTERS | 0.20 |
| Verdict DEPENDS_ON_EPSILON | 0.45 |
| Verdict CONSTRUCT_INVALID | 0.10 |
| Verdict CAPACITY_DEPENDENT or INCONCLUSIVE | 0.05 |
| ε\* (median over seeds) in [0.005, 0.02] | 0.50 |
| At least 4 of 5 seeds non-VOID | 0.70 |
| Reason fidelity: outside-truth share ≥ 0.10 | 0.40 |

(Revised at r5 before any fit. The synthetic follower gives DEPENDS_ON_EPSILON with ε\* ≈ 0.0103; real decisions
with structure outside the rule, such as amount, push ε\* down, as the adversary showed with 0.0017. CONSTRUCT_INVALID
is plausible on real data, because accepted DTI is post-verification and rejects' DTI is at application.)

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

## r4 → r5 (2026-10-28): r4 not freezable; one more design, under a written stop rule

**The second blind adversary pass found r4 not freezable** (two blockers, both accepted in full).
1. **Accept-row penalty.** The gate sets P to 0, clipped to 1e-6, so a single accepted validation row the rule declines
   costs 13.8 nats. About 2 such rows push a rule-embodying tree into "worsened", and about 9 cancel a pooling tree's
   gain. Step 1 never checked accepts in the 2011–12 interaction cells: its construct check began 2012-08, and A3 only
   measured [30, 35). So §6's "step 1 found no accepted loan the rule declines" was unsupported for this window. It is
   withdrawn.
2. **POLICY_MATTERS is what a follower produces.** On the LendingClub-shaped follower, the best trees embody the rule
   (ε = 0.005: corrected ≈ 0), and at ε = 0.01 "material" means a gain between 0.1·E and E. That is r3's ε-relative bar
   under another name. So r4's verdict can't distinguish a follower.

**What r1–r4 were circling.** For a lender that follows a threshold rule, the best trees embody it, and models that
misstate it cost a roughly fixed amount of fit, g. They are "near-optimal" exactly when ε > g/best. A verdict at a
fixed ε is decided by that inequality. **The ε-free quantity is ε\* = g / best loss**: how much worse than the best a
tree model must be before it misstates the written rule.

**r5 (to build):** estimate ε\* per seed (the smallest relative log-loss excess, over sampled monotone trees, at which a
tree's gating gain is material), with a CI across seeds. Verdict regions, fixed now:
- **KILL** if ε\* > 0.02. Rule-misstating models sit outside any reasonable band, so compiling adds nothing.
- **POLICY_MATTERS** if ε\* < 0.005. Even tight bands contain them.
- **DEPENDS_ON_EPSILON** otherwise, reported with the value.
- **CONTRADICTS** if the best trees themselves are worsened by gating.
- **CONSTRUCT_INVALID** if accepts that the rule declines exceed 0.05% of accepts in the window. This is a frozen
  construct check, adversary 2 finding 1.

Also: gate with the diagnostic tolerances; accepts from 2011-03; report gain split into reject-row savings and
accept-row penalty; state the 1e-6 clip; (k+0.5)/(n+1) leaf estimates with n ≥ 100; node-id lookup for held-out stats;
report unmapped employment values per file; time reason fidelity before freeze; fix the stale text.

**Stop rule (written before building r5):** if r5's blind adversary finds another blocker of the same kind (a verdict
fixed by construction or by an ε-relative bar), **step 2 closes as "not decidable on this substrate"** and the program
records that as its result. There is no r6. Bugs and text fixes don't count against the rule; a design that can't
discriminate does.
