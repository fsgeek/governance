# Draft results section — policy-constrained Rashomon audit: binary null vs. pricing reversal

**Date:** 2026-05-12.
**Status:** DRAFT. Voice-neutral, modular results-section block. Not yet assigned to a paper in the stack (candidate homes: Paper 1 position, or Paper 3 examination methodology — see `project_paper_structure`). Distilled from the two findings notes; tightened into paper-prose to fix the framing and surface gaps.
**Depends on:**
- `docs/superpowers/specs/2026-05-11-cross-vintage-cat2-yield-comparative-note.md` (binary null, 4 substrates).
- `docs/superpowers/specs/2026-05-12-pricing-space-within-grade-stratification-note.md` (pricing reversal, 3 LC vintages).
- `docs/superpowers/specs/2026-05-11-target-b-null-cat2-findings-note.md` (the 2015Q4-specific binary null + falsification).
**Open beats:** FM cross-regime arm (pending additional FM quarters); option (2) calibration-gap mechanism; figures (see TODO markers).
**Last reconciled with code:** 2026-05-12.

---

## 1. The audit primitive

A deployed credit-decision system can be audited against the institution's own *documented* policy by constraining the model class to the policy vocabulary — the features the policy names, the monotonicity directions it asserts, the features it prohibits — and asking what a policy-admissible model would have done that the deployed construction did not. We instantiate this as a per-unit classification:

- **Cat 1** — the policy genuinely binds: no policy-admissible alternative recovers the realized outcome. The constraint is doing its job.
- **Cat 2** — the deployed construction left a recoverable, policy-expressible signal on the table: a policy-admissible alternative recovers, and the distinguishing factor is *named by the policy*. Action: "use a factor you already committed to, better."
- **Cat 2-extension** — a policy-admissible alternative recovers, but the distinguishing factor is *not* in the policy vocabulary. Action: "the policy should name this factor."

The unit of classification can be the individual decision (the *verdict* version: grant/deny) or the risk tier (the *pricing* version: which rate band a borrower is assigned). The two versions answer different questions, and the contrast between them is the section's central observation.

## 2. The verdict version: zero Cat 2 across four substrates

Running the policy-constrained dual-set construction on LendingClub 36-month originations (vintages 2014Q3, 2015Q3, 2015Q4) and Fannie Mae first-lien mortgages (2018Q1), under thin-demonstration policies, the verdict-version Cat 2 count is **zero on every substrate**. Out-of-sample failures (cases where the deployed ensemble's verdict disagrees with the realized outcome) are all Cat 1: the surprise-revised set does not recover them either.

This is a real result, not a weak-detector artifact. A per-admissible-model falsification — refit every policy-admissible model on the training data, evaluate each on the Cat 1 subset — shows the maximum single-model recovery is ≤ 1.33% on every LC vintage and **0.0%** on FM (0 of 50 admissible models predict against the dominant outcome on any of the 479 FM Cat 1 cases). No aggregation rule on the policy-admissible space recovers; the admissible space does not contain a model that predicts the realized failures. The policy genuinely binds the *decision*.

(Structural texture, available if needed: the surprise-weighted deny-emphasis loss collapses the corresponding ε-band to a single model on every LC vintage but not on FM, so that asymmetry is a substrate × hypothesis-class artifact, not a mechanism property. And the surprise-weighting step is near-inert on FM because the ~99.2% grant rate flattens the surprise signal — a class-balance precondition for that part of the construction.)

## 3. The pricing version: Cat 2 structure on every LC vintage

The same primitive, applied to risk tiers: for each LendingClub `sub_grade`, test whether a feature partitions the tier's loans into sub-populations with significantly different *realized* default rates (two-proportion test over within-grade deciles, Benjamini-Hochberg FDR control). A significant split on a policy-named feature is Cat 2 (pricing); on a non-policy feature, Cat 2-extension; no significant split with adequate power, Cat 1 (pricing).

Unlike the verdict version, this finds structure on every LC vintage tested:

| Vintage | n loans | Cat 2 (pricing) | Cat 2-extension | Cat 1 (pricing) | underpowered | dominant recovered factor |
|---|---|---|---|---|---|---|
| 2014Q3 | 40,595 | 2 | 0 | 23 | 10 | `annual_inc` |
| 2015Q3 | 73,567 | 7 | 2 | 15 | 11 | `dti` (14/27 splits) |
| 2015Q4 | 88,669 | 9 | 3 | 11 | 12 | `dti` (20/39 splits) |

On the 2015 vintages, ~30–50% of testable sub-grades show recoverable within-tier structure, and the dominant recovered factor is **DTI** — a feature the policy already names (the `dti_ceiling` node). Worked example: LC 2015Q4 grade C2 (≈5,400 loans, pooled default ≈18.5%) splits at DTI ≈ 14 into 14.2% default below (n ≈ 1,367) vs. 19.7% above (n ≈ 3,188), p ≈ 10⁻⁵; the same monotone within-grade DTI→default relationship is detected at multiple decile thresholds and recurs across the C band. The grade treated a DTI-12 and a DTI-18 borrower as the same risk; their realized default rates differ by a third. This is the textbook Cat 2 (pricing): the recovered factor is documentable and already in the vocabulary — "grade more finely on a factor you already named." `mort_acc` (count of mortgage trades), not in the thin demo policy, is a recurring Cat 2-extension signal on the 2015 vintages.

**[TODO figure: LC 2015Q4 grade C2 — within-grade default rate by DTI decile, with the ≈14 split marked. One panel; the running illustration of the pricing reversal.]**

## 4. The diagnostic distinction

The verdict null and the pricing positive are not in tension; they are answers to different questions:

- *Verdict:* would a policy-admissible model have flipped the grant/deny decision on this case? — No: the realized failures (defaults on borrowers everyone graded as good) are not separable in the policy's hypothesis class. The policy binds the decision.
- *Pricing:* would a policy-expressible factor have made the risk tier finer? — Yes, in a minority of tiers, dominated by DTI on the 2015 vintages. The grading left ordinal structure on the table even though the verdict was as good as the governed class allows.

So the primitive distinguishes "the policy binds the decision" (true here) from "the tiering saturates the policy vocabulary" (false in ~30–50% of testable LC grades on the 2015 vintages). That distinction is the governance-actionable output: an institution reading this learns "your approve/deny boundary is defensible, but your C-band pricing tiers conflate DTI strata you commit to in your written policy."

## 5. Caveats

- **Thin-demonstration policy.** "Policy-expressible" here means "named by a four-feature illustrative policy graph," not a real institution's underwriting policy. The constraint is not load-bearing yet — the Cat 2 / Cat 2-extension partition only had teeth because the analysis tested nine standard underwriting fields beyond the four the thin demo names. With a real policy (more named features, richer structure) the partition sharpens; with the codification infrastructure the analysis becomes routine rather than bespoke.
- **Discrete single-feature splits.** The pricing mechanism tests binary cuts at decile thresholds on one feature at a time. It will miss diffuse miscalibration — a continuous, multi-feature mismatch with no clean cut. A model-predicted-default vs. grade-implied-default calibration-gap variant (option 2) catches that; it is the natural follow-on.
- **Default as a proxy.** Realized default ≠ "should have been priced higher." Default depends on post-origination shocks the lender could not price. A within-grade default-rate split is suggestive of miscalibration, not proof; the relevant defense is cross-vintage stability. The C-band DTI signal recurs on 2015Q3 and 2015Q4 (not a single-vintage fluke), but two adjacent quarters in one rate environment is not a cross-regime test — see §6.
- **No causal claim about the deployed grading model.** "DTI under-used in 2015-era LC grading" is a statement about the grade-vs-realized-default relationship, not about LC's internal model; LC may have used DTI with coarse tier boundaries, with the same observable consequence.

## 6. Positioning and the open beat

Each ingredient has a literature: LC grade-vs-default mismatch (a cottage industry in the credit-prediction literature); within-tier risk heterogeneity (standard credit risk); Rashomon multiplicity and variable importance across the set (interpretability theory); disparate-impact-in-pricing (fair-lending enforcement). What does *not* co-occur in any of these is the combination — model class defined by the *governed policy vocabulary*, Rashomon analysis *within the admissible set*, and a *tier-level* Cat 1 / Cat 2 classification — because that combination requires the policy-as-first-class-artifact frame, which is rare precisely because machine-encodable policy is rare. From inside any single literature the move looks like a trivial variation ("models beat the grade — old news"; "a smaller hypothesis class — of course the Rashomon set changes"; "rates correlate with proxies — we know"). The contribution is the lens, not an empirical fact: *the governance question was never asked of this well-mined data*.

The open beat is the cross-regime test. The LC result's binding caveat (§5) is that two adjacent 2015 quarters share a rate environment. Fannie Mae's Single-Family Loan Performance data spans decades and multiple regimes (pre-crisis, crisis, post-crisis, post-QM) and exposes a continuous origination rate; the pricing-version question there is "for a (rate-band, vintage) cohort, is realized default consistent with the rate under the policy vocabulary, or can a policy-expressible factor stratify the cohort?" — with rate-band × vintage playing the role of `sub_grade`. The eventual paper's spine is verdict-null → LC pricing-reversal → FM cross-regime confirmation (or its absence). The first two beats are in hand; the third is the work that makes the result regulator-credible rather than illustrative.
