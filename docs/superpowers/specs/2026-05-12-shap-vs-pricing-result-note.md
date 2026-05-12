# SHAP vs. policy-constrained stratification — pricing-space non-inferiority RESULT

**Date:** 2026-05-12.
**Status:** Findings note (canonical for the run `runs/shap_vs_pricing_results.json`, script `scripts/shap_vs_pricing.py`, module `wedge/shap_pricing.py`, tests `wedge/tests/test_shap_pricing.py`). Companion to the pre-registration `docs/superpowers/specs/2026-05-12-shap-vs-pricing-preregistration-note.md` — predictions were recorded there *before* any code touched the data.
**Headline:** **H0 ("SHAP non-inferior to the policy-constrained stratification test for recovering the within-grade DTI structure") is NOT falsified.** The pre-registered prediction — that SHAP would be *structurally blind* to the within-grade-realized-default structure — was **wrong**. A TreeSHAP analysis of a grading-model surrogate does recover the structure, and the disambiguation check confirms the recovery is real (it tracks realized default), not an artifact. This is a preserved miss, not a rewritten one.
**Authority:** Canonical for the three LC vintages run (2014Q3 / 2015Q3 / 2015Q4, 36-month). Not a generalization beyond LendingClub or beyond this comparison.
**Depends on:**
- `wedge/pricing.py` and `scripts/run_pricing_lc.py` (the stratification result this compares against; `runs/2026-05-12T00-0{4,5,6}*-pricing-lc-*.{jsonl,summary.json}`).
- `wedge/shap_pricing.py`, `wedge/tests/test_shap_pricing.py`, `scripts/shap_vs_pricing.py`.
- `data/accepted_2007_to_2018Q4.csv`.
**Last reconciled with code:** 2026-05-12.

---

## 1. What was run

For each of LC 2014Q3 / 2015Q3 / 2015Q4 (36-month term, the same vintages and feature set the pricing-space runs used — 4 thin-demo-policy features + 9 standard underwriting fields):

- **Arm 1 — the regulatory default.** Fit `g`, an `xgboost` regressor surrogate for the deployed grading model (`features → sub_grade` ordinal A1=0…G5=34). TreeSHAP on `g`. Score the pre-registered recovery criteria on the sub-grades the pricing run flagged Cat 2 (pricing) with a DTI split (2014Q3 has only one such grade, A2, and is `annual_inc`-thin elsewhere — its single DTI-flagged grade is tested):
  - **C1** — within-grade `std(SHAP_DTI) / population std(SHAP_DTI) ≥ 0.25`.
  - **C2** — `mean |SHAP_DTI|` ranks top-3 among features *within the grade*.
  - **C3** — the global `SHAP_DTI`-vs-`DTI` dependence relationship implies `≥ 1.0` sub-grade-ordinal units of change between `DTI = 10` and `DTI = 20`.
- **Arm 2 — the steelman.** Fit `f`, an `xgboost` classifier predicting realized default. TreeSHAP on `f`. Criterion **C5** — `DTI` ranks `≥ 2` positions higher by global `mean |SHAP|` on `f` than on `g`, *and* within-grade `|SHAP_DTI|` on `f` exceeds that on `g` by `≥ 50%`. (Pre-registered as not counting toward "SHAP non-inferior": `f` *is* the within-grade refinement model the stratification test stands in for.)
- **Disambiguation (post-hoc, not in the pre-reg).** Because C1's firing could be confounded with surrogate fidelity — a partial surrogate over-attributes to its few real signals everywhere, inflating `SHAP_DTI` variance for reasons unrelated to detecting the realized-default miscalibration — for each flagged grade we compare the within-grade realized-default-rate gap obtained by median-splitting borrowers (a) by `SHAP_DTI(g)`, (b) by raw `DTI`, against (c) the pricing mechanism's own recovered split. C1's firing is "real recovery of the consequential structure" iff (a) `≥ 0.5 ×` (b).
- **Cat-1-(pricing) control arm (post-hoc).** The grades the pricing run classified **Cat 1 (pricing)** — adequate power, no significant within-grade split — are the control: there is nothing to recover. Re-score C1 (dispersion) and the disambiguation there. A method with false-positive control is quiet on the control grades; a SHAP-dispersion read has none, so C1 should fire here too.

## 2. Results

| Vintage | n loans | flagged DTI grades | surrogate `g` R²(sub_grade) | C1 fires | C2 fires | C3 fires | C1 tracks default | global rank(DTI): g → f | Cat-1 control: C1 fires / tracks |
|---|---|---|---|---|---|---|---|---|---|
| 2014Q3 | 40,595 | 1 (A2) | 0.545 | 1/1 | 0/1 | 0/1 | 1/1 | 9 → 3 | 23/23 / 13 of 23 |
| 2015Q3 | 73,567 | 6 (A5,B1,C1,C2,C5,D4) | 0.506 | 6/6 | 0/6 | 0/6 | 6/6 | 6 → 3 | 15/15 / 10 of 15 |
| 2015Q4 | 88,669 | 8 (A1,A4,A5,B3,B4,B5,C3,C4) | 0.511 | 8/8 | 0/8 | 0/8 | 8/8 | 6 → 2 | 11/11 / 8 of 11 |

Per-grade within-grade default-rate gaps (selected, 2015Q4): C3 — by SHAP_DTI 0.042, by raw DTI 0.034, pricing-recovered split 0.050; C4 — 0.047 / 0.045 / 0.052; A5 — 0.036 / 0.039 / 0.043. The SHAP-`DTI` ranking and the raw-`DTI` ranking produce essentially the same within-grade default split everywhere; both are a little below the pricing mechanism's optimized-threshold gap (expected — a median split is not the most-discriminating split). Full numbers in `runs/shap_vs_pricing_results.json`.

**C1 fired on every flagged grade on all three vintages, and the disambiguation confirms it tracks realized default on every one.** C2 and C3 — the read-outs a validator most commonly relies on (within-grade feature-importance ranking; the SHAP dependence plot) — **failed everywhere**: `DTI` ranks 6th–9th as a grade driver per the surrogate, and the DTI dependence over `[10, 20]` is 0.25–0.67 sub-grade units, below the 1.0 threshold. C5: the global rank gap fires (`DTI` is relatively more important for realized default than for the grade), but the within-grade magnitude condition fails everywhere (`|SHAP_DTI|` is *smaller* on `f` than on `g` — the partial surrogate inflates `g`'s DTI attribution), and C5 is non-independent anyway.

**Cat-1-(pricing) control arm.** C1 (within-grade `SHAP_DTI` dispersion) fired on **100% of the control grades** — 23/23, 15/15, 11/11 — exactly as it fired on 100% of the flagged grades. As a *binary flag*, C1 has zero discriminating power: it fires in every tier, because the partial surrogate over-attributes to DTI everywhere. The disambiguation (does the SHAP-`DTI` ranking track realized default?) discriminates only *partially*: it "tracks" on 100% of the flagged grades but also on a majority of the control grades (13/23, 10/15, 8/11). Inspecting those control "tracks" cases: they are tiers with a ~2-point median-split DTI/default gradient that the stratification test's BH-FDR-controlled decile test did *not* flag — i.e., the disambiguation criterion (any `≥ 2`-point median-split gap) is more liberal than a controlled significance test, not that the stratification test missed real structure. (The disambiguation criterion was pinned post-hoc and is reported as-is, not re-tuned to sharpen the contrast.)

## 3. Verdict against the pre-registration

**H0 is NOT falsified.** Pre-registered falsification required C1, C2, and C3 all silent on `g` across the DTI-dominated grades on ≥ 2 of 3 vintages, with only C5 firing. Instead C1 fired on all flagged grades on all three vintages. The pre-registered prediction "C1 FAILS — the grade defines its members as risk-equivalent, so within-grade `SHAP_DTI` is compressed" was **wrong**, and the *reasoning* behind it — "SHAP explains the model's output (the grade), not the realized outcome, so it has no channel to within-tier miscalibration" — is **refuted by this experiment**. A tree surrogate fit to the sub-grade learns the population `DTI → grade` relationship; within any tier, `SHAP_DTI` then ranks borrowers by their DTI-driven "grade pressure," and (because `SHAP_DTI` is dominated by DTI's marginal effect) that ranking tracks realized default about as well as raw DTI does. SHAP-on-a-grading-surrogate is *not* blind to the within-grade DTI structure.

What *did* come out as predicted: C2 silent (DTI not a leading grade driver per the surrogate), C3 silent (DTI's mid-range dependence sub-grade-modest), C5 mixed and non-independent.

## 4. What this reshapes — for the Olorin argument and the paper

The pricing finding does **not** support "SHAP is blind to the within-grade DTI coarseness." It supports a narrower, and arguably more defensible, set of claims:

1. **SHAP's recovery here rode entirely on a model surrogate, with a fidelity caveat the stratification test does not carry.** `g` had R² ≈ 0.51 on the sub-grade — a *partial* surrogate (13 features; LC's actual grade uses many more, incl. the full credit report). C1's firing is *inflated* by that imperfection (a partial surrogate scatters attribution onto its few real signals). It happened to track realized default anyway because DTI's marginal effect dominates `SHAP_DTI` — but that is a property of this data, not a guarantee: a *more faithful* surrogate would compress `SHAP_DTI` within tiers (more variance absorbed by other features), a *worse* one would scatter it differently. The stratification test is a direct two-proportion z-test on realized outcomes — no surrogate, no fidelity dependence.
2. **No false-positive control on the SHAP side — confirmed.** C1 fires on a grade because of how the *surrogate* behaves there, not because of realized-outcome significance — and the Cat-1-(pricing) control arm confirms it: C1 fires on 100% of the control grades, exactly as on the flagged ones. As a binary flag it discriminates nothing. The realized-outcome conditioning (the disambiguation) recovers *some* discriminating power, but it is itself the stratification test's core move — "condition default on a ranking and look at the gap" — applied to a SHAP-derived score instead of the raw feature; and even so it stays liberal (it "tracks" on a majority of control grades, on sub-significance gradients). What *cleanly* separates "consequential within-tier DTI structure" from "not" is a BH-FDR-controlled significance test against realized default on a feature the policy *names* — the stratification test's whole apparatus. SHAP supplies "DTI varies here" (everywhere) and, with realized outcomes bolted on, "the variation correlates with default here" (most places); it does not supply the controlled, policy-keyed significance call.
3. **The stratification test states the consequence; SHAP leaves it to the eye.** SHAP gives a validator "`SHAP_DTI` varies within C2"; they must then judge whether that is consequential. The stratification test says "`DTI ≈ 14` splits C2's realized default 14.2% vs 19.7%, p ≈ 10⁻⁵." That is the governance-actionable output, with significance attached.
4. **The stratification test keys to the documented policy vocabulary; SHAP-feature-importance keys to whatever the surrogate used.** The Cat 2 (pricing) label means "you committed to DTI in your written policy and your C-band tiers conflate DTI strata you said you'd distinguish." SHAP makes no such statement.
5. **The "SHAP is silent on something" claim survives — but it is the verdict-side claim, not this one.** The 2026-05-09 head-to-head found four pre-registered SHAP-silence criteria fail to recover the verdict-side T-silent-all population (Jaccard ≈ 0). That result stands; this one does not extend it to the pricing side. In the regulator-facing deliverable: concede SHAP's competence on the within-grade DTI finding (per the project's standing posture — conceding where the alternative is adequate strengthens credibility on the cases where it is not), and locate the argument against a SHAP-only regime in (1)–(4) plus the verdict-side silence.

## 5. Caveats on this result

- **`g` and `f` were fit-and-explained on the same data** (no train/eval split). For C5, which is about *which features a model uses* rather than held-out performance, this is acceptable; a depth-4, 200–300-tree xgboost on 40k–88k rows × 13 features does not memorize per-row noise. A train/eval split would tighten any predictive reading; it is not needed for the attribution claims.
- **Surrogate target.** `g` predicts the `sub_grade` ordinal. Within a vintage+term, `int_rate` is approximately a deterministic function of `sub_grade` (essentially no within-grade price variation), so a price-target surrogate behaves the same; the ordinal target is the cleaner "the grade" object.
- **Single attribution method.** TreeSHAP only. A LIME arm (local linear surrogate, different failure modes) is a separate test; KernelSHAP / interventional-vs-conditional SHAP variants likewise.
- **Threshold-sensitivity.** C1's 0.25, C3's 1.0-sub-grade, C5's rank-delta-2 / 1.5× were pinned in the pre-reg before the run. C1 cleared its bar by a wide margin (0.44–1.21); C2 and C3 missed theirs by a wide margin; so the qualitative verdict is not threshold-fragile.
- **This is a comparison against the *stratification* method, not against a Rashomon construction.** Per the methodological-asymmetry note, `wedge/pricing.py` is not an ε-band over a model class. If follow-on #6 (Rashomon-ify the pricing piece) is done, re-run as literally SHAP-vs-Rashomon on the positive side — and re-check whether SHAP's recovery via C1 survives when the comparator is a model-class ε-band rather than a z-test.

## 6. Next

- **A faithful-surrogate sensitivity arm** — re-fit `g` with the full available LC feature set (a real validator would not restrict to 13 features); if C1's within-grade `SHAP_DTI` variance shrinks, that confirms C1's firing here was partly a partial-surrogate artifact, and tightens point (1) above. The sharpest remaining test.
- **Tighten the disambiguation** — require the SHAP-ranking default gap to be *statistically significant* (the stratification test's bar), not merely `≥ 2` points; the Cat-1 control "tracks" rate should fall toward zero. (Pre-register before running, to avoid the appearance of tuning toward a cleaner story.)
- **LIME arm.**
- **FM rate-band version** — the same comparison with `orig_interest_rate` rate-bands as the tier; subject to the LLPA-grid caveat. (Likely the same story: a SHAP surrogate for the rate encodes FICO→rate, so SHAP recovers the within-band FICO structure too — which would *reinforce* the reshaped argument above.)
- **Per-case adverse-action arm** (SHAP's home turf; the place it should win; conceding that strengthens the population-level argument).
