# Policy-constrained Rashomon refinement set (within-tier) — pre-registration

**Date:** 2026-05-12.
**Status:** Pre-registration. **No experimental code has been written at the time of this note.** Predictions and hit/miss criteria are recorded before any code touches the held-out quarter. Same discipline as `2026-05-12-within-tier-predictive-test-preregistration-note.md` and `2026-05-12-shap-vs-pricing-preregistration-note.md`. This is follow-on **#6** from the 2026-05-12 option-space exploration.
**Origin:** The project is named *policy-constrained Rashomon*, but to date the only Rashomon result is the verdict-side **null** (`project_cat2_null_cross_vintage`). Every positive — the pricing-space within-tier structure (`project_pricing_space_cat2`), its forward-predictive validation (`2026-05-12-within-tier-predictive-test-result-note.md`) — has been "stratification + a single refinement model," not a Rashomon set. #6 makes the positive a genuine Rashomon result: replace the single refinement with an **ε-band over a within-grade refinement-model class restricted to the policy vocabulary**, and ask whether that set is (a) non-trivial, (b) plural, (c) forward-predictively valid. If it is, "policy-constrained Rashomon" attaches to the positive side and the monitor gains a *set-level* output (plurality awareness) SHAP structurally cannot produce — the regulator-legibility / aggregate-model-risk superiority axis. If it isn't, that is a real and reportable limit, and the partial failure (band collapses / doesn't forward-predict / no member-disagreement) tells us which piece fails and probably why.
**Companion:** result note `docs/superpowers/specs/2026-05-12-policy-constrained-rashomon-refinement-result-note.md` (to be written after the run).

---

## 1. Question

For the Cat-2-(pricing) bursts identified by the temporal sweep, restrict the within-grade refinement-model class to the **policy vocabulary** (the named features `{fico_range_low, dti, annual_inc, emp_length}`, depth-bounded CARTs, with the policy's monotonicity directions enforced), build the ε-band of policy-admissible refinements on the burst's first quarter, and ask:

1. **Non-triviality** — is the ε-band more than one model? (If it collapses to a single model, "set" / "plurality" is empty rhetoric.)
2. **Plurality** — do the band's members use *different* named features / split structures? (Feature-usage diversity across members; member-pair disagreement on within-grade case rankings.)
3. **Forward-predictive validity** — do the band's members predict the burst's *second* quarter's within-grade realized default above chance? (The Rashomon-set version of the forward-predictive test already passed for a single logistic; this asks whether the *set of policy-admissible CARTs* does.)
4. **Cost of the constraint** — how does the policy-constrained band's fit quality and forward-predictive AUC compare to (i) an *unconstrained* refinement (CART over the same named features, no monotonicity) and (ii) a *kitchen-sink* refinement (CART over named + extension features, no monotonicity)? If the constrained band forward-predicts ≈ as well as the unconstrained best, the policy constraint is "free" — interpretability + named-feature guarantee at no predictive cost.

A "yes" on 1–3, with the constraint cheap on 4 → the positive becomes a policy-constrained Rashomon result with a set-level, forward-validated, intrinsically-interpretable output; the superiority-over-SHAP claim earns the regulator-legibility / plurality axis. A "no" on any of 1–3 → reported as a limit; the partial failure is diagnostic.

## 2. Setup

- **Substrate:** LendingClub accepted-loan data, 36-month term. Bursts (same as the within-tier predictive test):
  - **Burst D** (the 2015H2 `dti` burst — the load-bearing one): build on V₁ = **2015Q3**, forward-evaluate on V₂ = **2015Q4**.
  - **Burst A** (the 2013–14 `annual_inc` burst): build on V₁ = **2013Q3**, forward-evaluate on V₂ = **2013Q4**.
  - Flagged grades = the sub-grades classified Cat 2 (pricing) in V₁ (from `runs/pricing-lc-sweep-36mo-summary.json`).
- **The refinement-model class (per flagged grade G, on V₁'s grade-G loans):**
  - Hypothesis space: `DecisionTreeClassifier` over every non-empty subset of `{fico_range_low, dti, annual_inc, emp_length}` (15 subsets) × `max_depth ∈ {1, 2, 3}` × `min_samples_leaf ∈ {25, 50, 100}` — i.e., shallow, intrinsically-interpretable trees. Target: realized default (label == 0 ⇒ 1; "default" is class 1). NaNs median-imputed within the grade (imputer frozen on V₁).
  - **Monotonicity:** for each named feature in the subset that the policy constrains, enforce sklearn `monotonic_cst` *with the sign flipped from the encoder's value* — the encoder states directions relative to grant probability (`dti: negative` = higher DTI never decreases *decline* prob); the refinement predicts *default* probability (class 1 = default), so `dti → +1`, `fico_range_low → −1` (the encoder's `fico_range_low: positive` w.r.t. grant becomes `−1` w.r.t. default), `ltv → +1` (not present in LC data; relevant only if the FM variant is run later). `annual_inc` and `emp_length` are unconstrained in the thin demo.
  - Prohibited features: none in the thin demo.
- **The ε-band:** fit each (subset × depth × leaf) combo on a deterministic 70/30 train/holdout split *within* V₁'s grade-G loans (seed 0); score by holdout AUC (predicting default). The band R(ε) = all combos with holdout AUC ≥ (best holdout AUC) − ε, with **ε = 0.02** (pre-registered). Refit each band member on the *full* V₁ grade-G data before forward-evaluation. (Mirrors `wedge/rashomon.py`'s sweep → ε-filter → refit discipline.)
- **Plurality metrics:**
  - *Feature-usage diversity:* the set of named-feature subsets actually split on by band members (a tree fit on subset S may not split on all of S); how many distinct used-feature sets, and is any single feature in *every* member's used set?
  - *Member disagreement:* for each pair of band members, the Spearman correlation of their within-grade predicted-default rankings on V₁'s grade-G loans; report the median and min over pairs (low = high disagreement). Also: on V₂'s grade-G loans, the fraction of cases where band members disagree on which within-grade decile they fall in.
- **Forward-prediction:** for each band member, apply the (frozen, full-V₁-refit) model to V₂'s grade-G loans; compute within-grade AUC against V₂'s realized default; compare to the **constant model** (= the grade's pooled rate, AUC 0.5) via the same grade-size-aware label-shuffle null (95th percentile, 500 permutations) used in `wedge/predictive.py`. "Band member forward-predicts in G" = OOS AUC > shuffle-null p95 and ≥ 0.52.
- **Baselines:** (i) unconstrained refinement = the same sweep without `monotonic_cst`, ε-banded the same way; (ii) kitchen-sink refinement = the same but feature subsets drawn from named + 9 extension features (sampled, not exhaustive — too many subsets), no monotonicity. Report the best holdout AUC and the best forward-predictive OOS AUC of each baseline alongside the policy-constrained band.

## 3. Hit / miss criteria (pre-registered)

Per (burst, flagged-grade G):
- **Non-trivial band:** R(ε) has ≥ 3 members (after de-duplicating combos that produce identical fitted trees). [If < 3 → "band collapses" — record.]
- **Plural band:** ≥ 2 distinct used-feature sets among band members, AND median pairwise ranking-Spearman among members < 0.9 (some genuine disagreement). [If only 1 used-feature set, or median Spearman ≥ 0.95 → "band not plural" — record.]
- **Forward-predictive band:** a *majority* of band members forward-predict in G (OOS AUC > shuffle-null p95 and ≥ 0.52).
- **Constraint cheap in G:** the policy-constrained band's *best* forward-predictive OOS AUC ≥ 0.9 × the unconstrained refinement's best forward-predictive OOS AUC.

Per burst: the **substantive claim "the policy-constrained Rashomon refinement set is non-trivial, plural, and forward-predictively valid"** holds for that burst iff non-trivial + plural + forward-predictive on a *majority* of the burst's flagged grades. **Falsified** for that burst iff a majority of its flagged grades fail any one of {non-trivial, plural, forward-predictive}.

## 4. Pre-registered predictions

> **Burst D (2015Q3 build → 2015Q4 eval):**
> - *Non-trivial:* YES on a majority of flagged grades — the within-grade refinement space (15 feature subsets × 3 depths × 3 leaf sizes, minus identical trees) over a real signal should leave several combos within 0.02 holdout-AUC of the best.
> - *Plural:* PARTIAL — ≥ 2 used-feature sets on most grades, but the band will be **DTI-heavy** (2015H2's within-tier residual is DTI-dominated), so disagreement among members will be modest (median pairwise Spearman likely in [0.85, 0.95] — near the threshold). I expect a fair number of grades to be "non-trivial but only borderline-plural." If the band turns out genuinely multi-factor (DTI, income, and FICO all represented among members, low Spearman) that's a *better* result than predicted and worth flagging.
> - *Forward-predictive:* YES on a majority — the single logistic already forward-predicted on 7/7; a majority of the policy-constrained CART band should too, with OOS AUCs in roughly [0.52, 0.60] (shallow trees are coarser than logistic; expect slightly lower AUC and a few near-misses on small grades).
> - *Constraint cheap:* YES — the monotonicity directions are the *true* directions of the residual (higher DTI → more default within the tier), so constraining to them shouldn't cost much; expect the constrained band's best OOS AUC ≥ 0.95 × the unconstrained best. The kitchen-sink refinement may beat both (it can use `mort_acc` etc.) — that gap is the "value of naming more features in the policy" measure, not a strike against the constrained band.
>
> **Burst A (2013Q3 build → 2013Q4 eval):**
> - Similar, but the residual is `annual_inc`-dominated, so the band will be **income-heavy** rather than DTI-heavy; `annual_inc` is *unconstrained* in the thin demo, so the monotonicity constraint bites less here — the constrained and unconstrained bands should be nearly identical. Forward-predictive on a majority (the single logistic got 5/5). Smaller grades → noisier; expect a few near-misses.
>
> **Net:** the substantive claim — NOT falsified on either burst (non-trivial + forward-predictive hold; plurality is the soft spot, likely "partial" — present but narrow on 2015H2). If plurality fails outright (median Spearman ≥ 0.95 on a majority of grades), the honest reading is "the within-tier residual is essentially single-factor here, so the Rashomon-set framing adds little *on this episode* — its plurality value would have to come from multi-factor episodes," and that's a real (reportable) limit on the superiority claim, not a refutation of the method.

## 5. Why this is the right test now

The superiority-over-SHAP claim on the pricing side cannot be "Rashomon recovers what SHAP missed" (the SHAP-vs-pricing result showed SHAP-on-a-grading-surrogate *does* recover the within-tier structure). The defensible superiority claim is: the policy-constrained Rashomon set delivers the same finding as a *set of deployable, intrinsically-interpretable, forward-validated policy-admissible refinements with a plurality dimension* — a governance artifact SHAP structurally can't produce. That claim is only as strong as the set is non-trivial, plural, and forward-valid. This test measures all three, on two bursts, against the same chance baseline the predictive test used, with the unconstrained-refinement baseline quantifying what the policy constraint costs. The verdict-side SHAP-silence superiority (`project_shap_non_inferiority_result`) is separate and unaffected.

## 6. Followups (not part of this pre-registration)

- **The disagreement-as-routing signal** — where band members disagree most on a within-grade case, that case is the "indeterminate" one (the `project_rashomon_methodology` within-Rashomon-disagreement idea, instantiated on the pricing side); a follow-on would characterize the high-disagreement sub-population and check whether it has elevated realized default variance.
- **FM variant** — the same construction with the FM thin demo (`fico_range_low, dti, ltv` named; LTV available) on FM rate-bands or LLPA cells; FM has LTV, so the monotonicity constraint bites on a feature LC lacks.
- **Across-burst transfer of the band** — does Burst A's `annual_inc`-heavy band forward-predict Burst D's `dti`-dominated quarter? (Expected weak; quantifies feature-specificity.)
- **The selection-of-diverse-members step** — `wedge/rashomon.select_diverse_members` applied to the refinement band, to produce a *small* presentable set (the artifact a model-risk committee would actually look at) rather than the full ε-band.
