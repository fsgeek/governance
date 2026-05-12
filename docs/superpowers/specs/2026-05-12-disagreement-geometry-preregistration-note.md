# The geometry of within-Rashomon disagreement — pre-registration

**Date:** 2026-05-12.
**Status:** Pre-registration. **No experimental code has been written at the time of this note.** Predictions and hit/miss criteria recorded before any code touches the data. Same discipline as the preceding pre-regs in this session-arc. Follow-on to the **disagreement-as-routing** result (`2026-05-12-disagreement-routing-result-note.md`), which itself followed **#6** (`2026-05-12-policy-constrained-rashomon-refinement-result-note.md`).
**Origin.** The disagreement-routing result was *deflated and mildly reversed*: per-borrower disagreement `d(x)` among the policy-constrained refinement-band members does not localize to "the hard cases"; if anything the high-`d` tercile is slightly *more* predictable / better-calibrated. The mechanistic reading I gave (post-hoc): `d(x)` tracks *where the within-tier residual feature is active* — depth-1/2/3 trees over different feature subsets carve an active residual gradient differently (→ spread), while in the tier-interior region the grade has absorbed the risk so every member returns ≈ the base rate (→ no spread). That reading has a sharp, *untested* implication: if `d(x)` is "where the residual is," it should be a **legible, low-dimensional function of the borrower's features** — predictable without ever running the band. This note tests that, and adds the question the disagreement-routing note left open (§6): *what kind of borrower does the band disagree about, and is it the same kind across tiers?* Applying the lesson of `project_pre_registration_pattern` (predictions fail by assuming uniformity), the predictions below **explicitly model the heterogeneity** — P2 is itself a yes/no on cross-tier consistency, not an assumption of it — and P4 is a branch in which a *further* failure (named features don't explain `d`) would partially *un-deflate* the routing result.
**Companion:** result note `docs/superpowers/specs/2026-05-12-disagreement-geometry-result-note.md` (after the run).

---

## 1. Question

For the 5 plural sub-grades of Burst D (#6: A5, B1, C1, C5, D4 — built on V₁ = 2015Q3), with `d(x)` = std over the band's distinct member models of the predicted-default probability on x:

1. **Is `d(x)` well-explained by a small number of the *policy-named* features** (`{fico_range_low, dti, annual_inc, emp_length}`), on a majority of the 5 grades?
2. **Is the dominant disagreement-driver the *same* feature (and the same shape) across a majority** of the 5 grades — and, for Burst D, is it `dti` (the burst's headline residual feature)?
3. **Where in that feature is `d(x)` concentrated** — the tails, near a policy threshold, or monotone?
4. **Does adding the *extension* underwriting features** (`{revol_util, open_acc, inq_last_6mths, delinq_2yrs, total_acc, mort_acc, loan_amnt, revol_bal, pub_rec}`) materially improve the explanation of `d(x)` — i.e. does the band disagree partly about structure the *policy vocabulary cannot name*?

## 2. Setup

- **Substrate:** LC 36-month, Burst D. Bands built on V₁ = 2015Q3 with the identical #6 construction (named features, monotonicity sign-flipped to default-prediction `{fico_range_low: −1, dti: +1}`, depths {1,2,3}, leaf-mins {25,50,100}, ε = 0.02, seed 0, de-dup by tree signature). Distinct members refit on the full V₁ grade-G data (each on its own feature subset), frozen. The 5 plural grades re-derive the #6 way (≥ 2 distinct used-feature sets AND median pairwise ranking-Spearman among members < 0.9). `d(x)` computed on V₁'s grade-G loans (primary) and on V₂ = 2015Q4's grade-G loans (robustness; the band is still the V₁ band, members frozen).
- **Disagreement explainer.** For each plural grade G, fit a shallow regression CART (`max_depth ≤ 3`, `min_samples_leaf = 50`) predicting `d(x)` from (a) the **named** features only, (b) the **named + extension** features. Score by out-of-fold R² (5-fold CV) — the fraction of the *variance of `d`* the features capture. Record the feature at the root split and the top-3 feature importances; record the partial-dependence shape of `d` on the dominant feature (mean `d` in each decile of that feature).
- **Univariate.** For each feature f: Spearman ρ(f, d) over the grade's loans; mean `d` in the top vs bottom decile of f; the ratio.
- **Threshold proximity.** Distance `|dti − 43|` (the thin-demo `dti_ceiling`) and `|fico_range_low − 620|` (the `fico_floor`); Spearman of each with `d`. (Within an interior tier these thresholds are typically not *in* the tier's feature range; the test is whether *proximity* to them still tracks `d`.)
- **Cross-tier consistency.** Across the 5 plural grades: the multiset of root-split features of the named-features explainer; the multiset of top-importance features; whether the dominant feature's PD shape (tails-up / threshold-peak / monotone, classified by a simple rule on the decile means) agrees.

## 3. Metrics & verdict logic (all pre-registered, all reported)

Per plural grade G, on V₁ (primary) and V₂ (robustness):
- `R2_named` = CV R² of the named-features explainer; `R2_all` = CV R² of named+extension; `ΔR2 = R2_all − R2_named`.
- `top_named` = root-split feature of the named explainer (ties → highest importance).
- `|ρ_top|` = |Spearman(top_named, d)|; `tail_ratio` = mean `d` in the top-or-bottom decile of `top_named` / mean `d` in the middle 8 deciles (max of the two tails); `shape ∈ {tails, threshold, monotone, flat}` from the decile-mean profile of `d` on `top_named`.
- `prox_ρ` = max(|Spearman(|dti−43|, d)|, |Spearman(|fico−620|, d)|).

Aggregate over the 5 plural grades; "well-explained" = a grade with `R2_named ≥ 0.3` OR `|ρ_top| ≥ 0.3`.

- **P1 hit** iff `well-explained` on ≥ 3 of 5 grades (V₁).
- **P2 hit** iff `top_named` is the *same single feature* on ≥ 3 of 5 grades (V₁) — and **P2-dti hit** iff that feature is `dti`.
- **P3 hit** iff `shape == "tails"` (tail_ratio ≥ 1.5) on ≥ 3 of 5 grades; **P3-threshold hit** iff instead `shape == "threshold"` on ≥ 3 of 5; (either being a clean directional finding).
- **P4 (rescue branch) hit** iff `ΔR2 ≥ 0.1` on ≥ 3 of 5 grades **AND** `R2_named < 0.3` on ≥ 3 of 5 — i.e. the named features *don't* explain `d` but the extension features *do*. **This is the highest-value surprise**: it means the band disagrees about borrowers the policy vocabulary can't describe, which would be a legitimate "the policy is blind here → route to a human" trigger after all — partially *un-deflating* the disagreement-routing result, on a different and arguably stronger basis than the per-case-uncertainty version that was tested.

**Headline forms:** "`d(x)` is a legible function of [`{top_named}` / a small named set / mostly the extension features], [consistent / idiosyncratic] across the plural tiers, concentrated [in the tails / near the policy thresholds / monotone]; the routing implication is [the residual-tracking reading confirmed, routing stays deflated / the policy-blindness reading, routing partially rescued]."

## 4. Pre-registered predictions

> **P1 — likely yes (~65%).** `d(x)` should be largely a function of the burst's active residual feature; I expect `R2_named ≥ 0.3` (or `|ρ_top| ≥ 0.3`) on a majority of the 5 grades. If `R2_named` is high (≥ 0.5) on most, "you can predict the disagreement from the features without running the band" lands cleanly and the residual-tracking mechanism is confirmed. *(Hedge: the band is small on some grades — 8 distinct members on B1, 16 on D4 — so `d` is a coarse quantity there and R² could be noisy / low for sample-size reasons rather than mechanism reasons; I'll flag low-R² grades by member count.)*
>
> **P2 — genuinely uncertain (~50%, no strong prior — the fun one).** Either the same feature (`dti`, plausibly) drives disagreement on a majority of the plural grades — in which case "policy-admissible refinements disagree about a recognizable population type" is a *named thing* — or each tier disagrees about a different feature, in which case the disagreement is idiosoncratic per tier, which *deepens* the deflation (it's not even a coherent signal across tiers, let alone a routable one). I will not pretend to a prior here; the cross-tier multiset of root-split features is the answer.
>
> **P3 — lean tails (~55%) over threshold (~25%) over monotone (~15%).** I expect `d` to peak in the *tails* of the dominant feature: the band members carve the extreme borrowers (very high DTI within an A-grade, etc.) differently because that's where shallow trees on different feature subsets place their splits, while the middle is where they agree on ≈ base rate. The threshold-peak alternative (disagreement spikes near `dti=43`) would be a *more* interesting finding — it would mean the disagreement is keyed to the *policy boundary itself* — so I'd be happy to be wrong toward it.
>
> **P4 — unlikely (~25–30%), highest-value if it fires.** I expect the named features to do most of the work (P1 yes) and the extension features to add little (`ΔR2 < 0.1` on most grades). But if instead the named features *fail* to explain `d` and the extension features *succeed* — the band's disagreement keys on inquiry counts, revolving utilization, mortgage accounts, things the thin-demo policy never names — then the disagreement-routing idea gets a partial reprieve on a *better* footing than the version I tested: not "the models are confused about this borrower" but "the documented policy is silent about the feature the admissible refinements are fighting over." I assign this ~25–30% and flag it as the result I most want to check.
>
> **Cross-cutting:** consistent with `project_pre_registration_pattern`, my single most likely *miss* is over-confidence in P1's clean version — that `R2_named` will be *high* (≥ 0.5) — when in fact it's modest-but-nonzero (0.2–0.4) on most grades, i.e. `d` is *partly* legible from the features and partly not, and the "not" part is the more interesting residue (→ P4-adjacent territory even if P4's strict criterion doesn't trip). I expect the picture to be "mostly legible, with a stubborn fraction that isn't" rather than either "fully legible" or "opaque."

## 5. Why this is the right test now

The disagreement-routing result handed us a *mechanism claim* (disagreement ≈ where the residual is active) as a post-hoc reading. A post-hoc reading that isn't tested is a story. This test turns it into a falsifiable prediction with a clean structure: if the reading is right, `d` is a low-dim feature function (P1, P3); the open empirical question the reading doesn't settle is cross-tier coherence (P2); and there's a specific way the reading could be *wrong in an interesting direction* (P4 — `d` keyed on un-named structure), which would not just falsify the reading but rebuild a piece of the routing claim on firmer ground. Every branch improves the model: P1+P2-consistent → "disagreement is a named, legible thing"; P2-idiosyncratic → "disagreement is per-tier noise, deflation deepened"; P4 → "the policy-blindness routing trigger, recovered." And it's bounded by what we'd actually want to know to write the regulator-facing account of what within-Rashomon disagreement *is* — which is the near-term deliverable this whole sub-arc feeds.

## 6. Followups (not part of this pre-registration)

- If P4 fires: build the policy-blindness routing test directly — route the borrowers where `d` is high *and* unexplained by the named features; re-run the disagreement-routing metrics with that population.
- The FM variant — does the dominant disagreement-driver on FM's thin-demo bands track *its* active residual feature (FICO, per the FM cross-regime note), confirming the mechanism on a second substrate?
- `wedge.rashomon.select_diverse_members` on the band → the small presentable set, annotated with the tier-level disagreement statistic *and* (from this test) the feature(s) the members fight over — the deliverable form of the surviving aggregate-surveillance claim.
- Burst A geometry — the (mostly non-plural) `annual_inc` burst: where there *is* a little disagreement, is it `annual_inc`-keyed, confirming "disagreement tracks the burst's active feature" generically?
