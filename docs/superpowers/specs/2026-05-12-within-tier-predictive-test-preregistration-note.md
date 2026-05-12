# Within-tier forward-predictive test — pre-registration

**Date:** 2026-05-12.
**Status:** Pre-registration. **No experimental code has been written at the time of this note.** Predictions and hit/miss criteria are recorded *before* any code touches the held-out quarter. Mirrors the discipline of `2026-05-09-v1-v2-predictive-test-pre-registration.md` and `2026-05-12-shap-vs-pricing-preregistration-note.md`.
**Origin:** The temporal sweep (`2026-05-12-lc-pricing-temporal-sweep-note.md`) showed within-tier Cat-2-(pricing) structure is *episodic and feature-unstable* — three bursts (2013Q3–Q4 + 2014Q2 `annual_inc`-dominated; 2015Q3–Q4 `dti`-dominated) separated by near-zero stretches. Tony's reframe: episodicity is not a weakness — a contemporaneous miscalibration monitor *should* be quiet when the grading is calibrated and loud when it isn't; "permanence" was never the right bar. But the stratification test's BH-FDR control is *within-vintage* only, so the load-bearing skeptic's objection becomes: across ~30 quarters × ~25 testable grades × 13 features × 9 thresholds (~10⁵ tests), some bursts are inevitable by chance — was 2015Q3 a real episode or a lucky vintage? **Forward-prediction is the substitute for permanence:** if a refinement fit on burst-quarter-1 predicts burst-quarter-2's within-grade realized default out of sample, the burst is a real, contemporaneously-detectable episode, not a multiple-testing artifact.
**Companion:** result note `docs/superpowers/specs/2026-05-12-within-tier-predictive-test-result-note.md` (to be written after the run).

---

## 1. Question

For each Cat-2-(pricing) burst the temporal sweep identified, is the within-tier structure **forward-predictive** — does a within-grade refinement model fit on the burst's first quarter, *frozen*, predict the burst's second quarter's within-grade realized default better than chance?

- **Yes** (across bursts) → the bursts are real, contemporaneously-detectable episodes of within-tier miscalibration; the monitor's signal is trustworthy; "episodic but real" is the established picture; the 2015H2 DTI finding earns its place in the deliverables as a worked instance of contemporaneous observability catching a time-localized miscalibration the lender's own grading missed.
- **No** (for a given burst) → that burst was a lucky vintage; the within-vintage FDR control is insufficient against cross-vintage multiplicity; the monitor needs a stronger guard. (A burst failing is a specific, useful negative — it tells us which "finding" to retract.)

## 2. Setup

- **Substrate:** LendingClub accepted-loan data, 36-month term, the vintages identified by the temporal sweep. Two bursts:
  - **Burst D (the 2015H2 `dti` burst — the load-bearing one):** train quarter V₁ = **2015Q3**, test quarter V₂ = **2015Q4**.
  - **Burst A (the 2013–2014 `annual_inc` burst):** train quarter V₁ = **2013Q3**, test quarter V₂ = **2013Q4**. (Both quarters are in the same burst and `annual_inc`-dominated per the sweep.)
- **Flagged grades:** for each burst, the sub-grades classified Cat 2 (pricing) **in V₁** by the stratification run (`scripts/run_pricing_lc_sweep.py` output, or a fresh `scripts/run_pricing_lc.py` run on V₁ — same parameters: α=0.01 BH-FDR, min 300 loans/grade, min 100 loans/side, the 4-feature thin-demo policy + 9 underwriting fields). The test is run per flagged grade.
- **Refinement model:** for grade G in V₁, fit a `LogisticRegression` (L2, default C; the policy ethos favors an intrinsically interpretable refinement) on V₁'s grade-G loans using **only the policy-named features** (`fico_range_low`, `dti`, `annual_inc`, `emp_length`; missing values median-imputed within the grade) → realized default (label == 0). Robustness arm: a depth-2 `DecisionTreeClassifier` with the same features. The model is frozen — no re-fit on V₂.
- **Evaluation:** apply the frozen V₁-model to V₂'s grade-G loans; compute the within-grade AUC of its predicted-default scores against V₂'s realized default.
- **Baselines, all computed and reported:**
  - **(a) chance** = 0.5.
  - **(b) shuffle null** = permute V₂'s realized-default labels within grade G, recompute the V₁-model's AUC, ×500; the null is the 95th percentile of that distribution. (Accounts for grade size — small grades have wide null bands.)
  - **(c) V₁ in-sample AUC** — the V₁-model's AUC on V₁'s grade-G loans; an upper bound on what's recoverable from these features in this grade.
  - **(d) V₂-refit AUC** — fit the same model class on V₂'s grade-G loans, evaluate on V₂ (in-sample); the "if you could re-fit on the test quarter" bound; the gap (d) − (V₂-OOS) measures how much the structure shifted between quarters.
- **Independence:** V₂'s labels are never seen during fitting; the shuffle null fixes the model and permutes only the test labels.
- **Latent-structure arm (secondary, reported, not part of the falsification core):** also fit a refinement on the **2014Q4** versions of Burst D's flagged grades — quarters the sweep flagged as Cat 1 (nothing significant) — and evaluate on 2015Q4. If V₂-OOS AUC beats the shuffle null, the 2015Q4 structure was *latent* (sub-significance) in 2014Q4 and "appeared" via the +75% sample-size jump, not a true regime change. If it doesn't, 2015Q4's structure is genuinely new. Either reading is fine under the "episodic is OK" reframe; this just characterizes *how* the burst arose.

## 3. Hit / miss criteria (pre-registered)

For each (burst, flagged-grade G):
- **HIT** (forward-predictive in G): V₂-OOS AUC > the 95th percentile of the shuffle null **AND** V₂-OOS AUC ≥ 0.52 (a minimum effect-size floor — a barely-above-null AUC on a huge grade can clear the percentile bar without being practically meaningful).
- **MISS**: V₂-OOS AUC ≤ the 95th percentile of the shuffle null, or < 0.52.
- **NEAR-HIT**: clears the shuffle-null bar but in [0.50, 0.52) — significant but negligible.

Per burst: **the burst is forward-predictive** iff HIT on a *majority* of its flagged grades. **The "bursts are real, not multiple-testing artifacts" claim is falsified** iff a majority of *both* bursts' flagged grades are MISS. One burst forward-predictive and the other not is the "that burst was a lucky vintage" partial outcome — reported as such, and the non-predictive burst's stratification finding is flagged for retraction.

## 4. Pre-registered predictions

> **Burst D (2015Q3 → 2015Q4):** forward-predictive — HIT on a majority of its flagged grades. The DTI/default relationship within a C-band tier should not vanish in one quarter; adjacent quarters in the same episode. Expect V₂-OOS AUC in roughly [0.55, 0.62] within the flagged grades (within-grade AUC is modest by construction — the grade already absorbed most of the cross-grade signal), comfortably above the shuffle null, with a small (d)−(OOS) gap.
>
> **Burst A (2013Q3 → 2013Q4):** also forward-predictive — HIT on a majority of its flagged grades, on the `annual_inc` signal. If LC's grading was conflating income strata in 2013Q3 it almost certainly still was in 2013Q4. Slightly weaker than Burst D expected (2013 vintages are smaller, ~27k vs ~74–89k, so noisier).
>
> **Net:** "bursts are real, not multiple-testing artifacts" — NOT falsified. Both bursts forward-predictive.
>
> **Latent-structure arm (2014Q4 → 2015Q4):** the 2014Q4-fit refinement *does* beat the shuffle null on 2015Q4 (the within-tier DTI/income relationship was present but sub-significance in 2014Q4) — i.e., the monitor's "0 Cat 2 in 2014Q4" was partly a power miss, not a clean true-negative. If this prediction is wrong (2014Q4-fit refinement ≈ chance on 2015Q4), then 2015Q4's structure is genuinely new and the monitor's 2014Q4 quiet was real.

## 5. Why this is the right test now

Under the "episodic is the design goal" reframe, the only thing standing between "the 2015H2 DTI finding is a real, contemporaneously-detectable miscalibration episode" and "it's a lucky vintage in a 10⁵-test forest" is a forward-prediction check, because the test's multiplicity control is within-vintage. This test supplies it, on two independent bursts, with a chance baseline that respects grade size. It also produces, as a by-product, the worked per-tier "here's what the contemporaneous monitor's output looks like" artifact (the flagged grades, the recovered structure, the forward-validation) that the Olorin briefing and the regulator document both need — and the comparison (d)−(OOS) quantifies how stable the structure is quarter-to-quarter, which is the honest version of "how reliable is the monitor."

## 6. Followups (not part of this pre-registration)

- **Burst-characterization:** does each Cat-2 burst line up with a documentable change in LC's origination mix (volume, mean DTI, mean FICO, grade distribution, the 2015–2016 underwriting-loosening episode)? Tests whether the monitor's *temporal* signal is interpretable — whether a bank reading "your grading started conflating DTI strata in 2015Q3" could connect it to a known practice change. The "decision is visible" point applied to the time axis.
- **Cross-lender control:** does the 2015H2 DTI episode show up in FM 2015 data (rate-band or LLPA-cell tiers)? LC-only → strengthens "lender behavior"; also in FM → something macro/sector-wide.
- **60-month LC:** the same forward-predictive test on 60-month vintages (longer horizon; 2010–2013 originations, GFC-aftermath).
- **The Rashomon-ified version (#6):** replace the single logistic refinement with an ε-band over a within-grade refinement-model class; the forward-predictive test then asks whether *policy-expressible members of the ε-band* beat the constant out of sample — which makes "policy-constrained Rashomon" attach to the positive side.
