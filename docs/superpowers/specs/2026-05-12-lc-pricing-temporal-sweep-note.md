# LC pricing-space stratification — temporal sweep across vintages

**Date:** 2026-05-12.
**Status:** Findings note (canonical for the run `runs/pricing-lc-sweep-36mo-summary.json`, script `scripts/run_pricing_lc_sweep.py`). Descriptive — no pre-registration; runs the existing `wedge/pricing.py` stratification test on more vintages and looks. Prompted by Tony's question: were the dataset choices (2014–2015 cluster) biased toward periods preceding shocks, and would the within-tier pattern persist in quiet periods / across time?
**Headline:** The within-tier structure (Cat 2 (pricing)) is **episodic and feature-unstable across 2008–2015, not a persistent property of LendingClub's grading.** The DTI-dominated episode that the load-bearing pricing-space positive rests on is essentially **2015H2 alone** (2015Q3–2015Q4); the earlier Cat-2 bursts (2013Q3–2014Q2) are dominated by `annual_inc`, not DTI; long stretches (2008–2012 by lack of power; 2014Q4–2015Q2 with full power) show near-zero Cat 2. So "your C-band tiers conflate DTI strata you committed to" is a statement about **2015H2**, consistent with a lender-behavior episode (LC's scandal-era underwriting loosening), not a stable miscalibration. Tony's "lender-specific / time-specific" hunch is supported — and more so than the macro-shock framing he started from, since the LC vintages' performance windows are themselves calm.
**Authority:** Canonical for the 36-month LC vintages 2008Q1–2015Q4. Not a generalization beyond LC; pre-2012 has no statistical power (low origination volume).
**Depends on:** `wedge/pricing.py`, `scripts/run_pricing_lc_sweep.py`, `data/accepted_2007_to_2018Q4.csv`. Companion: `2026-05-12-pricing-space-within-grade-stratification-note.md` (the original LC-DTI positive this re-examines), `2026-05-12-shap-vs-pricing-result-note.md` (the SHAP head-to-head on that positive).
**Last reconciled with code:** 2026-05-12.

---

## 1. What was run

The within-grade stratification test (`wedge/pricing.GradeStratification.compute` + `classify_grades`) on every LendingClub 36-month vintage 2008Q1–2015Q4, same feature set and policy partition as `scripts/run_pricing_lc.py` (4 thin-demo-policy features — `fico_range_low`, `dti`, `annual_inc`, `emp_length` — plus 9 standard underwriting fields), α=0.01 BH-FDR, min 300 loans/grade, min 100 loans/side. Later vintages excluded: for cohorts that have not matured by the 2018Q4 data cut, the Fully-Paid-/Charged-Off subset over-represents early-terminating loans (a selection bias toward early defaults), so the stratification would run on a non-representative sample.

## 2. The pattern over time

| Vintage | n loans | def rate | testable grades | Cat 2 (pricing) | Cat 2-ext | dominant recovered feature (split count) |
|---|---|---|---|---|---|---|
| 2008Q1–2010Q4 | 503–2,243 | 9–17% | 0 | 0 | 0 | — (all grades underpowered: low LC volume) |
| 2011Q1–2012Q2 | 2,617–8,469 | 9–14% | 1–12 | 0 | 0 | — (testable grades all Cat 1) |
| 2012Q3 | 13,322 | 14.2% | 17 | 1 | 0 | annual_inc (1) |
| 2012Q4 | 15,181 | 12.8% | 19 | 1 | 0 | dti (1) |
| 2013Q1 | 17,988 | 12.6% | 19 | 1 | 0 | dti (3) |
| 2013Q2 | 23,136 | 12.8% | 20 | 0 | 0 | — |
| 2013Q3 | 27,318 | 12.2% | 21 | 5 | 1 | **annual_inc (16)**, mort_acc (1), revol_util (1) |
| 2013Q4 | 31,980 | 11.9% | 20 | 7 | 0 | **annual_inc (15)**, dti (7) |
| 2014Q1 | 34,074 | 12.9% | 21 | 2 | 1 | dti (3), annual_inc (1), mort_acc (1) |
| 2014Q2 | 37,881 | 13.6% | 22 | 9 | 2 | **annual_inc (30)**, dti (11), mort_acc (7), loan_amnt (2), revol_bal (2), emp_length (1) |
| 2014Q3 | 40,595 | 13.6% | 25 | 2 | 0 | annual_inc (4), dti (1), revol_bal (1) |
| 2014Q4 | 50,020 | 14.5% | 23 | **0** | 0 | — |
| 2015Q1 | 56,568 | 14.8% | 23 | 1 | 0 | fico_range_low (1) |
| 2015Q2 | 64,222 | 15.4% | 24 | 1 | 1 | mort_acc (3), dti (1) |
| 2015Q3 | 73,567 | 14.6% | 24 | 7 | 2 | **dti (14)**, fico_range_low (5), loan_amnt (3), open_acc (2), mort_acc (2), total_acc (1) |
| 2015Q4 | 88,669 | 14.8% | 23 | 9 | 3 | **dti (20)**, mort_acc (5), fico_range_low (3), open_acc (3), inq_last_6mths (3), annual_inc (3), loan_amnt (2) |

Cat-2-(pricing) share of testable grades across the 30 vintages with adequate power: min 0%, max 41% (2013Q4), mean 10.5%. The dominant recovered feature is `—` (no significant splits) in 18 of 30 vintages; `annual_inc` in 5; `dti` in 5; `fico_range_low` in 1; `mort_acc` in 1.

## 3. Reading

- **Episodic, not persistent.** Three distinct Cat-2 bursts — 2013Q3–Q4, 2014Q2, 2015Q3–Q4 — separated by near-zero stretches (2014Q4–2015Q2 at full power has zero, one, one). This is not "LC's grading conflates named-factor strata"; it is "LC's grading conflated named-factor strata in three specific windows."
- **Feature-unstable.** The 2013–2014 bursts are `annual_inc`-dominated (16, 15, 30 splits on `annual_inc`); only the 2015H2 burst is `dti`-dominated (14, 20 splits on `dti`). The "C-band conflates DTI strata" finding is specific to 2015H2. A bank running this monitor would see the *factor* it's mis-handling change quarter to quarter — which is what you would expect if the cause is the lender's evolving underwriting practice, not a structural property.
- **The 2015H2 episode lines up with LC's known underwriting loosening.** LC's 2016 loan-quality scandal flagged the 2015–2016 vintages as loosened-underwriting cohorts; the DTI-vs-grade calibration breaking down in exactly 2015H2 is consistent with that. The macro-shock framing (Tony's starting point) doesn't apply — these loans' 36-month performance windows are ~2017–2018, pre-COVID, calm — but the *lender-specific-episode* concern that question pointed at is supported.
- **Caveat: the count is power-sensitive; the feature-identity shift is less so.** Sample size grows ~75% from 2014Q4 (50k) to 2015Q4 (89k), so part of the 0→9 Cat-2 jump is power, not a regime change — some 2015Q4 structure may have been latent (sub-significance) in 2014Q4. But a pure power story predicts the *same* feature dominating throughout as power grows; the observed `annual_inc`→`dti` shift between the 2014H1 and 2015H2 bursts is not what growing power alone produces, so something in *what LC's grading was mishandling* changed. Pre-2012 (volume too low) has no power at all — the 2007–2009 GFC-cohort question is unanswerable on LC (FM has the volume; the FM cross-regime run covers 2006/2008, with the LLPA-grid caveat).

## 4. What this reshapes

- **The load-bearing positive is narrower than stated.** `project_pricing_space_cat2` and the original within-grade note describe "Cat 2 structure on every LC vintage, DTI-dominated on the 2015 ones" — true, but the *cross-vintage* claim (2014Q3 / 2015Q3 / 2015Q4) hides that 2014Q3 is `annual_inc`-thin (2 Cat 2) and the DTI dominance is a 2015H2 phenomenon. The honest statement: *in 2015H2, LC's grading conflated DTI strata in ~30–40% of its C-band tiers* — a real, FDR-controlled finding about a specific lender episode, not a general property of risk-tiering.
- **It does not weaken the diagnostic primitive.** The verdict-null-vs-pricing-positive contrast still holds; what changes is the characterization of the positive — it is *time-localized*, which for the *monitoring* use case is a feature (the test detects *when* miscalibration appears and *which* named factor) and for any *permanence* claim is a limit.
- **It raises the bar for the within-tier predictive test.** The test must now distinguish: (a) *within-episode* generalization (does a refinement fit on 2015Q3 predict 2015Q4's within-grade default?) — expected yes; (b) *across-episode* generalization (does a refinement fit on the 2013Q4 `annual_inc` burst predict 2015Q4's within-grade default?) — expected weak, because the driving factor differs; (c) *latent-structure* (does a refinement fit on the *quiet* 2014Q4 C-band — which flagged nothing — still predict 2015Q4's C-band default? if so, 2015Q4's structure was latent in 2014Q4 and "appeared" via power, not a real change). The pre-registration for that test should pin these three arms.

## 5. Next

- **Within-tier predictive test** (pre-registered, the three-arm grid above) — the central follow-on; it converts "episodic Cat-2 bursts" into either "real, pricer-knowable structure that comes and goes" or "within-vintage noise that the significance bar lets through in high-power vintages."
- **60-month LC sweep** (2010Q1–2013Q4, fully observed) — a longer-horizon view; 5-year loans see more macro environment and the 2010–2011 originations are right after the GFC trough.
- **FM full-archive temporal sweep** — FM has the volume the GFC-era LC lacks; the rate-band Cat-2 picture across all 104 quarters, with the LLPA-grid caveat (it's a robustness/scaling view, not an independent positive).
- **Threshold-sensitivity grid** — re-run a few vintages at varying α / min-loans-per-grade to bound how much of the burst-vs-quiet contrast is the significance threshold near a boundary vs a real difference.
