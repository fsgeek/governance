# Within-tier forward-predictive test — RESULT

**Date:** 2026-05-12.
**Status:** Findings note (canonical for the run `runs/within_tier_predictive_test_results.json`, script `scripts/within_tier_predictive_test.py`, module `wedge/predictive.py`, tests `wedge/tests/test_predictive.py`). Companion to the pre-registration `docs/superpowers/specs/2026-05-12-within-tier-predictive-test-preregistration-note.md` — predictions and hit/miss criteria were recorded there before any code touched the held-out quarter.
**Headline:** **"The within-tier Cat-2 bursts are real, not multiple-testing artifacts" — NOT falsified.** Both bursts are forward-predictive: a within-grade refinement fit on the burst's first quarter, frozen, predicts the second quarter's within-grade realized default above a grade-size-aware shuffle null, on *every* flagged grade (logistic; 5/7 and 5/5 with a depth-2 tree). The pre-registered prediction held on both bursts and on the latent-structure arm. **And it sharpens the temporal picture in a way that partly walks back the "episodic / lender-specific" reading**: the 2015Q4 within-tier structure was *predictively present in the "quiet" 2014Q4* too — it just hadn't crossed the within-vintage FDR significance bar at that sample size. So the underlying within-tier residual is roughly persistent and *pricer-knowable at origination*; what is episodic is the *significance* signal, which is sample-size-confounded. This resolves the macro/lender-contamination worry favorably and makes the bank/regulator work item defensible.
**Authority:** Canonical for the three LC vintage-pairs run. Modest within-grade AUCs (0.53–0.61) — the residual is real but thin (the grade already absorbed the cross-grade signal). Not a generalization beyond LC.
**Depends on:** `wedge/pricing.py` (the stratification flags), `wedge/predictive.py`, `scripts/within_tier_predictive_test.py`, `scripts/run_pricing_lc_sweep.py` (the flagged-grade lists), `data/accepted_2007_to_2018Q4.csv`. Companions: `2026-05-12-lc-pricing-temporal-sweep-note.md`, `2026-05-12-pricing-space-within-grade-stratification-note.md`, `2026-05-12-shap-vs-pricing-result-note.md`.
**Last reconciled with code:** 2026-05-12.

---

## 1. What was run

For each Cat-2-(pricing) burst the temporal sweep identified, and for each sub-grade flagged Cat 2 (pricing) in the burst's first quarter V₁: fit a within-grade refinement (`LogisticRegression` over the 4 policy-named features `fico_range_low`, `dti`, `annual_inc`, `emp_length`, median-imputed and standard-scaled, all fit on V₁; robustness arm: depth-2 `DecisionTreeClassifier`) → realized default; freeze it; apply to V₂'s grade-G loans; compute the within-grade AUC of its scores against V₂'s realized default. Baselines, all reported: chance (0.5); a label-shuffle null (95th percentile, 500 permutations of V₂'s labels with the model fixed — respects grade size); V₁ in-sample AUC; V₂-refit AUC. Pre-registered hit rule: **HIT** iff V₂-OOS AUC > shuffle-null p95 **and** ≥ 0.52; a burst is forward-predictive iff HIT on a majority of its flagged grades; the "bursts are real" claim is falsified iff a majority of *both* bursts' flagged grades are MISS.

- **Burst D** (the 2015H2 `dti` burst — the load-bearing one): V₁ = 2015Q3, V₂ = 2015Q4. 7 flagged grades.
- **Burst A** (the 2013–14 `annual_inc` burst): V₁ = 2013Q3, V₂ = 2013Q4. 5 flagged grades.
- **Latent-structure arm** (secondary): fit on **2014Q4** (which the sweep flagged as Cat 1 — nothing significant) the versions of 2015Q4's 9 flagged grades; evaluate on 2015Q4.

## 2. Results (logistic refinement; tree-d2 in parentheses)

| Arm | V₁→V₂ | flagged grades | HITs | OOS AUC range | shuffle-null p95 range | drift gap (refit−OOS) | forward-predictive? |
|---|---|---|---|---|---|---|---|
| D (`dti`) | 2015Q3→2015Q4 | 7 | **7/7** (5/7) | 0.530–0.613 | 0.516–0.542 | ≈ −0.01 to +0.01 | **yes** (yes) |
| A (`annual_inc`) | 2013Q3→2013Q4 | 5 | **5/5** (5/5) | 0.550–0.584 | 0.530–0.537 | ≈ −0.05 to +0.01 | **yes** (yes) |
| latent | 2014Q4→2015Q4 | 9 | **9/9** (6/9) | 0.532–0.622 | 0.516–0.544 | ≈ −0.01 to +0.01 | **yes** (yes) |

- **Burst D:** every flagged grade HIT (logistic). OOS AUC comfortably above the grade-size-aware null on all 7; V₁-in-sample and V₂-refit AUCs sit right next to OOS (the drift gap is ≈0) — the within-tier structure is stable quarter-to-quarter, not a one-vintage fluctuation. The depth-2 tree HITs 5/7; the two misses (C5 n≈3.4k, D4 n≈1.2k) are the smallest grades, where the tree's coarser fit just clips the null.
- **Burst A:** every flagged grade HIT under both models. OOS AUC 0.55–0.58 on the `annual_inc` signal. (B1's V₂-refit AUC 0.64 vs OOS 0.58 — the largest drift gap; the structure was stronger in 2013Q4 than the frozen 2013Q3 model captures, which is fine — drift toward *more* structure doesn't threaten the forward-prediction claim.)
- **Latent arm:** every one of 2015Q4's flagged grades is HIT when the refinement is fit on the *2014Q4* version of that grade (logistic) — i.e., the structure 2015Q4 flagged was *already there, predictively*, in the quarter the monitor scored as "Cat 1, nothing significant." The tree arm HITs 6/9 (misses A1, A2 — n_v1 ≈ 1.8–2.2k — and B5). So the monitor's "0 Cat 2 in 2014Q4" was largely a power miss, not a true negative.
- **Robustness:** scaled vs unscaled logistic differs by ≤ 0.01 AUC everywhere — the refinement-model spec isn't load-bearing. Logistic and depth-2 tree agree on every grade except a handful of small-n ones (tree slightly more conservative there).

## 3. Verdict against the pre-registration

**Both bursts forward-predictive — the "bursts are real, not multiple-testing artifacts" claim is NOT falsified.** Pre-registered predictions: Burst D HIT on a majority of flagged grades (got 7/7 logistic), Burst A HIT on a majority (got 5/5), latent arm fires (got 9/9 logistic). All three held. The within-tier residual the stratification test flags is a real, contemporaneously-detectable, *forward-predictive* property — a model using only origination-time policy features, fit on one quarter, predicts the *next* quarter's within-tier realized default above chance.

## 4. What this establishes — and the honest sharpening of the temporal picture

1. **The pricing-space positive is robust to the macro/lender-contamination worry.** It is not macro-shock noise (it forward-predicts in calm quarters, on the `annual_inc` 2013 burst as well as the `dti` 2015 one). It is not a lucky vintage in the ~10⁵-test forest (it forward-predicts on two independent bursts against a grade-size-aware null). It *is* pricer-knowable at origination (origination-time features, predicting a later quarter). The bank/regulator work item is defensible: "you committed to DTI; your C-band tiers conflate DTI strata; a refinement fit on last quarter's loans predicts this quarter's within-tier defaults, AUC ≈ 0.54–0.61, beating chance."
2. **"Episodic / lender-specific" was partly the *significance* signal, not the *structure*.** The latent arm shows 2014Q4's "quiet" grades had predictively-real within-tier structure too; it just hadn't crossed the within-vintage FDR bar at that sample size. So the underlying within-tier residual is roughly *persistent* — the bursts in the *significance* time series reflect (a) sample size growing through 2014→2015 (more power → more significant splits) as much as any regime change. **But not entirely:** the *dominant recovered feature* shifted (`annual_inc` in the 2013–14 bursts, `dti` in the 2015H2 burst), and a pure power story predicts the *same* feature dominating throughout — so something in *which named factor* LC's grading mishandled did change, plausibly tracking LC's evolving underwriting. The synthesis: a roughly-persistent baseline within-tier residual, plus a real shift in *which factor* it loads on.
3. **Methodological consequence for the monitor (carry this).** The significance-based output (Cat 1 vs Cat 2) is sample-size-confounded — a small lender, or an early quarter, will read "Cat 1, you're fine" on a tier that has a real residual. The forward-predictive output (does last quarter's refinement beat chance on this quarter's within-tier defaults) is the more robust signal. The monitor should report *both* and a bank should weight the predictive signal when its sample is small. This also points at follow-on #6: replace the single logistic refinement with an ε-band over a within-grade refinement-model class and ask whether *policy-expressible members* beat the constant out of sample — which makes "policy-constrained Rashomon" attach to the positive side and gives the monitor a set-level (not single-model) output.
4. **Magnitude honesty.** The within-grade OOS AUCs are 0.53–0.61 — modest by construction (the grade already absorbed the cross-grade signal; what's left is a thin residual). The finding is not "your grading is badly broken"; it is "your grading leaves a small, statistically-real, pricer-knowable residual on the table within these tiers, on a factor you named." Actionable for governance ("grade finer on a named factor"), not a five-alarm fire — and saying so straight is what makes the rest credible.

## 5. Caveats

- **Within-grade refinement only.** The refinement uses the 4 policy-named features; a richer policy (or the extension features) would change the AUCs. The thin-demo-policy caveat from `project_pricing_space_cat2` still applies.
- **Adjacent-quarter transfer.** V₁→V₂ are adjacent quarters in the *same* burst — a one-quarter-ahead test, not a multi-year one. A stronger version: fit on 2013Q3 (the `annual_inc` burst), predict 2015Q4 (the `dti` burst) — expected weak (different driving factor), and it would quantify how far the structure transfers. Not run here; a follow-on.
- **Grade-label drift.** "C2" in V₁ and V₂ are LC's grade labels, which LC re-calibrates over time; the test transfers a refinement across same-labelled tiers without controlling for re-calibration. Generalizing *despite* that is if anything a stronger result, but a default-rate-matched-tier robustness arm would be cleaner.
- **Fit-and-evaluate on the full vintage.** No train/holdout split within V₁; the V₁-in-sample AUC is therefore optimistic as a "what's recoverable" bound. The forward-prediction (V₁-fit → V₂-eval) is the clean part and is unaffected.

## 6. Next

- **Across-burst transfer** (fit 2013Q3 `annual_inc` burst → predict 2015Q4 `dti` burst) — quantifies how feature-specific the structure is.
- **Burst-characterization** — does each Cat-2 burst line up with a documentable change in LC's origination mix (volume, mean DTI/FICO, grade distribution, the 2015–16 underwriting loosening)? The "is the temporal signal interpretable" check; the "decision is visible" point on the time axis.
- **Cross-lender control** — does the 2015H2 DTI residual show up in FM 2015 data (rate-band or LLPA-cell tiers)? LC-only → "lender behavior"; also in FM → something sector-wide.
- **#6 — the Rashomon-ified refinement** — ε-band over a within-grade refinement-model class; forward-predictive test asks whether policy-expressible members beat the constant out of sample. Makes "policy-constrained Rashomon" attach to the positive side; gives the monitor a set-level output.
- **60-month LC** — the same forward-predictive test on 5-year vintages (2010–2013 originations; GFC-aftermath; longer horizon).
