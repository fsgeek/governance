# Pricing-space dual-set analog — LendingClub within-grade stratification (2014Q3 / 2015Q3 / 2015Q4)

**Date:** 2026-05-12.
**Status:** Findings note (canonical for the three LC 36-month runs identified below). The pricing-tier reframe of the Cat 2 question, after the binary-verdict version returned zero Cat 2 across four substrates. Unlike the binary null, the pricing-space mechanism finds Cat 2 structure on every LC vintage tested.
**Authority:** Canonical for these three runs. Not a generalization to other substrates or to a richer feature set / non-thin-demo policy.
**Depends on:**
- `wedge/pricing.py` (the within-grade stratification mechanism).
- `scripts/run_pricing_lc.py` (the LC orchestration).
- `docs/superpowers/specs/2026-05-11-cross-vintage-cat2-yield-comparative-note.md` (the binary null this reframes around).
- Run artifacts:
  - `runs/2026-05-12T00-05-39Z-pricing-lc-2014Q3.{jsonl,…-summary.json}`
  - `runs/2026-05-12T00-04-07Z-pricing-lc-2015Q3.{jsonl,…-summary.json}`
  - `runs/2026-05-12T00-06-37Z-pricing-lc-2015Q4.{jsonl,…-summary.json}`
- `policy/thin_demo_hmda.yaml` (the policy whose named-feature set defines "policy-expressible").
**Invalidated by:** A re-run with a different significance threshold, a different feature set, or a non-thin-demo policy will shift the *counts*; the qualitative finding (Cat 2 structure exists, dominated by DTI on the 2015 vintages, concentrated in the A–D grades) should survive unless the threshold is moved drastically.
**Last reconciled with code:** 2026-05-12.

---

## 1. Why a pricing-space version

The binary mechanism asks "is there a policy-admissible model that recovers the realized verdict on a held-out case?" — and on LC 2014Q3 / 2015Q3 / 2015Q4 and FM 2018Q1 the answer is no (zero Cat 2; see the cross-substrate note). Two confounds in that null: data availability (accepted-loans data has no "denied applicant whose performance we can't observe") and the binary collapse (the grant/deny bit throws away the ordinal risk-tier structure). The pricing-space version addresses the second:

> For each lender-assigned risk tier (`sub_grade`), is there a feature that partitions the tier's loans into sub-populations with significantly different *realized* default rates?

A significant split means the grade conflated loans that the feature distinguishes — the pricing-space Cat 2 analog. It dodges the data-availability confound: the test runs over *granted* loans only, all of which have realized outcomes; the counterfactual ("what if the tier had been finer") is over the same population we observe.

## 2. The construction

Mirrors the dual-set structure:
- **Original construction** = the grade as given: every loan in tier *g* carries the tier's pooled realized default rate.
- **Revised construction** = the grade plus the recovered split: tier *g* refined along the most-discriminating feature.
- **Cat 2 (pricing)** = a significant split on a feature *named by the documented policy* → "a factor in your vocabulary the grade used imperfectly."
- **Cat 2-extension (pricing)** = a significant split, but only on a feature *not* in the policy → "the policy should name this factor."
- **Cat 1 (pricing)** = adequate power, no significant split → "the grade is already as fine as the governed vocabulary allows."
- **underpowered** = fewer than `min_loans_per_grade` loans (set to 300 here).

Statistics: two-sided pooled two-proportion z-test on the default-rate difference per (grade, feature, threshold); thresholds are within-grade deciles of each feature, skipping any where either side falls below `min_loans_per_side` (100); Benjamini-Hochberg FDR control across all tests at `alpha` (0.01). Features tested: the four named by `policy/thin_demo_hmda.yaml` (`fico_range_low`, `dti`, `annual_inc`, `emp_length`) plus nine standard LC underwriting fields not in the thin demo (`revol_util`, `open_acc`, `inq_last_6mths`, `delinq_2yrs`, `total_acc`, `mort_acc`, `loan_amnt`, `revol_bal`, `pub_rec`) — so the policy-expressibility filter is non-vacuous.

## 3. Cross-vintage results

| Vintage | n loans | Cat 2 (pricing) | Cat 2-extension | Cat 1 (pricing) | underpowered | sig. splits | dominant split features |
|---|---|---|---|---|---|---|---|
| 2014Q3 | 40,595 | 2 | 0 | 23 | 10 | 6 | `annual_inc` (4), `dti` (1), `revol_bal` (1) |
| 2015Q3 | 73,567 | 7 | 2 | 15 | 11 | 27 | `dti` (14), `fico_range_low` (5), `loan_amnt` (3), `mort_acc` (2), `open_acc` (2) |
| 2015Q4 | 88,669 | 9 | 3 | 11 | 12 | 39 | `dti` (20), `mort_acc` (5), `fico_range_low` (3), `inq_last_6mths` (3), `annual_inc` (3), `open_acc` (3), `loan_amnt` (2) |

Cat 2/extension grades:
- 2014Q3: A2, B2.
- 2015Q3: A1, A5, B1, B5, C1, C2, C3, C5, D4.
- 2015Q4: A1, A2, A4, A5, B3, B4, B5, C1, C2, C3, C4, D3.

**The pricing-space mechanism finds Cat 2 structure on every LC vintage** — in sharp contrast to the binary mechanism's zero. The reframe was not cosmetic; the ordinal structure is where the signal lives.

Three robust observations and one caveat:

- **The signal scales with sample size.** 40k loans → 2 Cat 2 grades, 6 splits; 74k → 9, 27; 89k → 12, 39. Some of this is real (more loans, more detectable miscalibration) and some is power (the 2014Q3 "only 2" is partly "the smaller sample can't detect the rest"). The *fraction* of testable grades that are Cat 2/extension goes 2/25 → 9/24 → 12/23, so it isn't purely a power artifact — but the count is not directly comparable across vintages of different size.
- **DTI dominates on the 2015 vintages, not on 2014Q3.** On 2015Q3 and 2015Q4, `dti` is the recovered factor in 14/27 and 20/39 splits — the largest single contributor. On 2014Q3 it's `annual_inc` (4/6). LC revised its grading methodology periodically; this is consistent with DTI being under-weighted in the 2015-era grading specifically. "DTI under-used in LC grading" is a 2015 finding, not a universal-LC one.
- **`mort_acc` (count of mortgage trades) is a recurring extension signal.** It appears in 2015Q3 (2 splits) and 2015Q4 (5 splits). `mort_acc` is *not* in the thin demo policy — so this is a Cat 2-extension finding: within several grades, having existing mortgage accounts stratifies default rates, and the policy doesn't name it. The actionable read is "the policy should add `mort_acc` to its vocabulary," not "the grading misused a factor it has."
- **Caveat — threshold-sensitivity.** The *count* of Cat 2 grades depends on `alpha`, `min_loans_per_grade`, and the decile-threshold grid. The high-confidence splits (p ≈ 1e-6 to 1e-8, large n on both sides — the C-grade `dti` and `annual_inc` splits) survive any reasonable tightening; the marginal ones (p ≈ 1e-4) would drop at `alpha` = 1e-3. So the qualitative finding is robust; the precise count is not.

## 4. The DTI finding (2015 vintages)

Worked example, LC 2015Q4, grade C2 (n = 5,382 terminal loans, pooled default rate ≈ 18.5%): split at `dti` ≈ 14 gives default 14.2% (n = 1,367) below vs 19.7% (n = 3,188) above — a 5.5 pp gap, p ≈ 1e-5. Grade C2 treated a DTI-12 borrower and a DTI-18 borrower as the same risk; their realized default rates differ by a third. The same monotone within-grade DTI→default relationship is detected at multiple decile thresholds in C2 (14, 16.6, 19, 21.5, …), and recurs in other C-band grades. DTI is named in the thin demo policy (the `dti_ceiling` node, threshold 43) — the policy *has* DTI; the grading used it coarsely. That makes this a clean "Cat 2 (pricing)": the recovered factor is documentable and already in the vocabulary; the action is "grade more finely on a factor you already named," not "add a new factor."

## 5. What this shows about the mechanism vs the binary null

The binary null and the pricing-space positive are not in tension; they're answers to different questions:
- *Binary:* "would a policy-admissible model have flipped the grant/deny verdict on this case?" → no, because the realized failures (defaults on borrowers everyone graded as good) are not separable in the policy's hypothesis class — the policy is genuinely binding on the *verdict*.
- *Pricing:* "would a policy-expressible factor have made the *risk tier* finer?" → yes, in a minority of tiers, dominated by DTI on the 2015 vintages — the grading left ordinal structure on the table even though the *verdict* was as good as the governed class allows.

So the mechanism distinguishes "the policy binds the decision" (true) from "the tiering saturates the policy vocabulary" (false in ~30–50% of testable grades on the 2015 vintages). That distinction is the governance-actionable output: a bank reading this learns "your approve/deny boundary is defensible, but your pricing tiers in the C band are conflating DTI strata you already commit to in your written policy."

## 6. Caveats and what this does not show

- **Thin demo policy.** "Policy-expressible" here means "named by `thin_demo_hmda.yaml`," which is an illustrative four-feature graph, not a real bank's underwriting policy. A real policy would name more features; the Cat 2 / Cat 2-extension split would shift accordingly.
- **Discrete splits only.** The mechanism tests single-feature binary splits at decile thresholds. It will miss diffuse miscalibration (a continuous, multi-feature mismatch with no clean binary cut). Option (2) — a model-predicted-default-vs-grade-implied-default calibration gap — would catch that; it's the natural follow-on.
- **Default-as-proxy.** Realized default ≠ "should have been priced higher." Default depends on post-origination shocks the lender couldn't price. A within-grade default-rate split is suggestive of miscalibration, not proof of it; the lender's response would be "is this split stable across vintages and not an artifact of the realized macro path?" The cross-vintage recurrence of the C-band DTI signal on 2015Q3 and 2015Q4 is the relevant evidence there — it's not a single-vintage fluke — but two adjacent quarters in the same rate environment is not a strong cross-regime test. FM (decades of vintages, multiple rate environments) is.
- **No causal claim about LC's grading model.** "DTI under-used in 2015-era LC grading" is a statement about the *grade-vs-realized-default relationship*, not about LC's internal model. LC may have used DTI and set coarse tier boundaries; the observable consequence is the same.

## 7. Next tests

- **FM with the continuous rate.** FM hands you the original interest rate directly (column index 7, `ORIG_INTEREST_RATE`) — no grade-tier estimation needed. The pricing-space question there is "is the realized default rate for a (rate-band, vintage) cohort consistent with the rate, or is there an origination-feature signal predicting lower default than the rate priced in?" — and FM's decades of vintages make it the cross-regime test LC can't be. One-line collector addition (`"orig_interest_rate": 7` in `FIELD_POSITIONS`) is on the path.
- **Option (2): model-vs-grade calibration gap.** Train a policy-admissible model to predict P(default); compare to the grade-implied pooled rate per loan; a systematic gap along a feature is a Cat 2-analog the discrete-split version may miss. Runner-up to option (4); natural follow-on.
- **Richer feature set / real policy.** With a real bank policy (more named features) the Cat 2 / Cat 2-extension partition is sharper. With the codification infrastructure (the long-term project) this becomes routine rather than bespoke.

## 8. FM 2018Q1 pilot (rate-band tiers)

The file name says "LendingClub"; this section extends to the Fannie Mae substrate. LC publishes a discrete `sub_grade`; FM hands you the continuous original interest rate. The "tier" analog is the rate-band: `orig_interest_rate`, deciled within the acquisition file. Same mechanism, same Cat 1 / Cat 2 / Cat 2-extension taxonomy, with `policy/thin_demo_fm.yaml`'s named features (`fico_range_low`, `dti`, `ltv`) as the policy-expressible set. Script: `scripts/run_pricing_fm.py`. Run: `runs/2026-05-12T00-31-33Z-pricing-fm-2018Q1.{jsonl,…-summary.json}`.

This is a **pilot**, not the cross-regime test: only FM 2018Q1 is on disk (one acquisition quarter, one rate environment). It validates the rate-band tier construction and confirms the mechanism scales to FM's size (~400k eligible loans, ~0.8% default rate). The cross-regime arm — the thing that makes the result regulator-credible rather than illustrative — needs additional FM quarters spanning pre-crisis / crisis / post-crisis / post-QM.

Results: 401,623 eligible loans; default rate 0.80%; rate range [2.5%, 6.25%]; 9 rate-bands after `qcut` (the 10th collapsed — common rate values like 4.000% create duplicate edges). Band-level default tracks the rate cleanly — rb00 (lowest rate) 0.21% → rb08 (highest) 2.65%, a 12x spread; the rate is doing its job at the coarse level. But **all 9 rate-bands are "Cat 2 (pricing)"**: every band has a significant policy-expressible within-band split. 170 significant splits; feature frequency `fico_range_low` (80), `dti` (64), `ltv` (25), `loan_term_months` (1). Top split: rb08 (highest rate), FICO ≤ 643 defaults 5.64% (n=3,936) vs FICO > 643 2.30% (n=33,407) — 2.4x, p ≈ 5e-35. The biggest within-band gaps are in the high-rate bands rb06–rb08 (more defaults → more detectable variation); the low-rate bands rb00–rb02 (~0.2–0.4% default) are also Cat 2 but with tiny absolute effect sizes.

**Caveat — partly by design, not purely a defect.** FM's rate is set off the LLPA grid, which prices in FICO×CLTV *cells* — intentionally coarse bins. "Residual FICO predicts default within a rate-band" is the observable consequence of the grid's bin coarseness, not necessarily a pricing error. Whether the coarseness is a governance *problem* depends on a follow-up this pilot does not run: do the within-band high-default sub-populations correlate with a protected-class proxy? If yes, the coarseness has disparate impact and is actionable; if no, it is a coarse-but-defensible documented pricing policy. The mechanism flags the coarseness; it does not adjudicate it. So the FM 9/9 Cat 2 count means "the rate-band tier conflates FICO/DTI/LTV strata the policy names" — true — not "FM mispriced these loans" — not established.

**Comparison with LC.** LC: ~30–50% of testable `sub_grade` tiers are Cat 2, DTI-dominated on the 2015 vintages. FM: 100% of rate-bands are Cat 2, FICO-dominated. The difference is partly that the rate-band tier (9 bands) is coarser than LC's `sub_grade` (35 tiers), so within-band heterogeneity is larger; partly that FM's enormous sample (400k loans) gives the test much more power; and partly the FM/LC tiers are different objects (LC's grade is the lender's own composite risk assessment; FM's rate is market + GSE LLPA + lender margin). The qualitative finding — the tiering does not saturate the policy vocabulary — holds on both substrates. The next move is the FM cross-regime run once more FM quarters are on disk; the option (C) refinement (tier = the LLPA grid's own FICO×CLTV cells) would audit the documented pricing artifact directly rather than the rate it produces.
