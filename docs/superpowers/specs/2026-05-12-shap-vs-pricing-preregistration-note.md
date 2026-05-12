# SHAP vs. policy-constrained stratification — pricing-space non-inferiority pre-registration

**Date:** 2026-05-12.
**Status:** Pre-registration. **No experimental code has been written at the time of this note.** Predictions and recovery criteria are recorded *before* the experiment runs so the result is load-bearing rather than reportable. Mirrors the verdict-side pre-reg `docs/superpowers/specs/2026-05-09-shap-vs-rashomon-preregistration-note.md`.
**Origin:** Follow-on #9 from the 2026-05-12 option-space exploration. The pricing-space mechanism (`wedge/pricing.py`) produced the project's load-bearing *positive* result — within several LendingClub sub-grades, a policy-named feature (DTI on the 2015 vintages) separates realized default at high significance; the grade conflates DTI strata it could have distinguished. The project is positioned against SHAP/LIME as the regulator-legible default; the verdict-side comparison was run, the pricing-side was not. The Olorin-facing argument to *not* simply use SHAP needs the head-to-head on the positive result, not just the null.
**Companion:** result note `docs/superpowers/specs/2026-05-12-shap-vs-pricing-result-note.md` (to be written after the run).

---

## 0. Naming honesty

The pricing-side comparator is **not a Rashomon construction.** `wedge/pricing.py` is policy-constrained *stratification testing* — two-proportion z-tests over within-grade feature deciles, Benjamini-Hochberg FDR-controlled — not an ε-band over a model class. So this is "SHAP vs. the policy-constrained stratification method," not "SHAP vs. Rashomon." The *spirit* is identical to the verdict-side pre-reg — post-hoc single-model explainer vs. the governance-constrained structured method — and that is what the falsification is about. (If follow-on #6 is done — Rashomon-ify the pricing piece — the comparison becomes literally SHAP-vs-Rashomon on the positive side too; a separate pre-reg would cover that.)

## 1. Hypothesis

**H0 (the claim we try to falsify):** SHAP, applied the standard way to the deployed grading model, is **non-inferior** to the policy-constrained stratification test for recovering the within-grade DTI structure — a model validator using SHAP would surface "this grade conflates DTI strata with materially different realized default" just as the pricing mechanism does.

- **H0 not falsified** (SHAP non-inferior; the pricing mechanism added nothing) → the Olorin/regulator argument cannot lean on "SHAP misses the pricing-coarseness finding"; it has to lean on other load-bearing arguments (codification-as-infrastructure, contemporaneous capture, the verdict-side null).
- **H0 falsified** (SHAP is silent/inferior on this) → the pricing mechanism surfaces something a SHAP-equipped validator would not, and the head-to-head earns its place in the regulator-facing deliverable and the paper.

## 2. Setup

- **Substrate:** LendingClub accepted-loan data, vintages **2014Q3, 2015Q3, 2015Q4**, 36-month term — the same three vintages the pricing runs used (`runs/2026-05-12T00-0{4,5,6}*-pricing-lc-*.{jsonl,summary.json}`). N=3 for the replication; the 2015 vintages are DTI-dominated, 2014Q3 is `annual_inc`-dominated with only ~2 Cat-2 splits (a thinner test there — if DTI is not a flagged feature on 2014Q3 the 2014Q3 arm tests whichever feature *is* flagged, by the same logic).
- **The "deployed grading model" surrogate `g`:** LendingClub's internal grading model is not published. Build the validator's surrogate — an `xgboost` regressor predicting **`sub_grade`-ordinal** (A1=0 … G5=34) from the borrower features (the same feature set the pricing run used: 4 thin-demo-policy features + 9 standard underwriting fields). Robustness arm: the same with target `int_rate`. Note in advance: within a vintage+term, `int_rate` is approximately a deterministic function of `sub_grade` — there is essentially **no within-grade price variation** — which is itself the structural point (the price *is* the grade; SHAP on the price cannot see within-grade structure because there is none in the thing being explained).
- **The realized-default model `f` (steelman arm):** an `xgboost` classifier predicting realized default (label==0) from the same features, isotonic-calibrated — identical construction to the verdict-side pre-reg's "deployed model." This is *not* the deployed grading model; it is what a more sophisticated validator builds when SHAP-on-the-grade comes up empty.
- **Attribution method:** TreeSHAP (apples-to-apples with the tree models; standard practitioner choice). LIME is a follow-on.
- **Independence:** `g` and `f` are trained independently of `wedge/pricing.py`; the comparison is not rigged in either direction.

## 3. Recovery criteria (pre-registered, all reported)

"SHAP recovered the within-grade DTI structure **in grade G**" is operationalized as **any** of the following firing, where G ranges over the sub-grades flagged Cat 2 (pricing) with a DTI split on that vintage (analogously for the dominant feature on 2014Q3 if not DTI):

**Arm 1 — on the grading surrogate `g` (the regulatory-default use of SHAP):**

- **C1 — within-grade SHAP-DTI dispersion.** Among grade-G borrowers, `std(SHAP_DTI | G) ≥ 0.25 × std(SHAP_DTI | all borrowers)`. (The explainer attributes meaningfully varied DTI-contributions to borrowers *within* the grade — a validator might notice "the grade isn't treating DTI uniformly here.")
- **C2 — within-grade SHAP-DTI prominence.** Among grade-G borrowers, `mean |SHAP_DTI|` ranks in the **top 3** features by within-grade `mean |SHAP|`. ("DTI is a leading driver of the grade, within this tier.")
- **C3 — SHAP-dependence materiality across the grade's DTI span.** The global SHAP-`DTI` dependence relationship on `g` (bin-means of `SHAP_DTI` vs `DTI`), evaluated between `DTI = 10` and `DTI = 20` (the neighborhood of the recovered C2 split at ≈14), implies a change of `≥ 1.0` sub-grade-ordinal unit. (If a validator sees "DTI 10→20 is worth a full sub-grade" *and* sees DTI-10 and DTI-20 borrowers sharing grade C2, that is a flaggable contradiction.)

**Arm 1 — structural negative, pre-registered explicitly (not a "criterion that fails"):** there is **no** SHAP operation on `g` that references realized default. The pricing finding — a within-grade *realized-default-rate* gap — lives in the relationship `grade → realized outcome`, which `g` does not model. SHAP, being a decomposition of `g`'s output, has no term for it. We state this in advance so a post-hoc "but you could have looked at X" cannot be retrofitted.

**Arm 2 — on the realized-default model `f` (the steelman):**

- **C5 — SHAP-attribution-gap.** The rank of `DTI` by `mean |SHAP|` on `f` is **≥ 2 positions higher** than its rank on `g`, **and** within `≥ half` of the DTI-dominated grades the within-grade `mean |SHAP_DTI|` on `f` exceeds that on `g` by `≥ 50%`. ("DTI drives realized default more than it drives the grade → the grade underuses DTI.")
  - **Independence caveat, pre-registered:** `f` — a realized-default model on the borrower features — *is* the within-grade refinement model the pricing-mechanism's stratification test is a nonparametric stand-in for. So C5 firing establishes "if you build the refinement model, a SHAP-diff on it also surfaces the structure" — it does **not** establish that SHAP-on-the-deployed-system is non-inferior. C5 is reported, but a "SHAP non-inferior" verdict cannot rest on C5 alone.

## 4. Pre-registered predictions

> **C1 (within-grade SHAP-DTI dispersion on `g`):** FAILS on the DTI-dominated grades — within-grade `std(SHAP_DTI)` is `< 0.25×` the pooled spread. The grade *defines* its members as risk-equivalent; the cross-grade DTI variation is what `g` spent to assign the grade, so the within-grade DTI residual gets little attribution. (It will be `> 0` — feature interactions and imperfect surrogate fit guarantee that — but compressed.)
>
> **C2 (within-grade SHAP-DTI prominence on `g`):** AMBIGUOUS / vintage-dependent. DTI may rank top-3 in within-grade grade-attribution if LC weights DTI heavily in grading; if so, C2 fires *mechanically* — but ranking high in *what drives the grade* is not the same as *the grade is too coarse on it*, so a C2 hit does not on its own make a validator reach the pricing finding. Reported, weighed accordingly.
>
> **C3 (SHAP-dependence materiality on `g`):** FAILS — the global `SHAP_DTI`-vs-`DTI` slope, localized to the `[10, 20]` interval, implies `< 1.0` sub-grade units. Most of DTI's grade-effect (such as it is) sits at the distribution tails and is entangled with FICO; the mid-range residual is, by the grading model's lights, immaterial.
>
> **Arm 1 net:** silent on the pricing-coarseness finding across the DTI-dominated grades (C1, C3 fail; C2 if it fires is not coarseness-detection).
>
> **C5 (SHAP-attribution-gap, `f` vs `g`):** FIRES — `DTI` ranks materially higher on `f` than on `g`, and within most DTI-dominated grades `|SHAP_DTI|` on `f` exceeds that on `g`. But this is the non-independent route: it requires `f`, which is the refinement model the pricing test stands in for.
>
> **Cross-vintage replication:** the Arm-1-silent / C5-fires-but-non-independent pattern holds on all three vintages (2014Q3 with whichever feature is its dominant flagged one, if not DTI).

## 5. Falsification criterion

> **H0 ("SHAP non-inferior") is NOT falsified IF:** C1, C2, **or** C3 fires on `g` for **≥ half** the DTI-dominated grades on **≥ 2 of the 3 vintages** — i.e., a validator using SHAP-on-the-grading-model the standard way would have been led to the pricing-coarseness finding. (C5 firing does **not** count toward non-inferiority — it is not independent of building the refinement model; see §3 C5 caveat.)
>
> **H0 IS falsified IF:** C1, C2, and C3 are all silent on `g` across the DTI-dominated grades on **≥ 2 of the 3 vintages**, and the only recovery signal is C5 on `f`. Verdict: the policy-constrained stratification test surfaces within-grade-realized-default structure that SHAP-on-the-deployed-grading-model is structurally blind to; the only SHAP route that reaches it requires first building the very model the stratification test stands in for. SHAP is incidental to the finding, not a substitute for the method.
>
> **Partial outcome:** if C2 (only) fires broadly while C1 and C3 stay silent — report as "SHAP-on-the-grade surfaces that DTI is a grade driver, but not that the grade is too coarse on it; the coarseness claim is the stratification test's, not SHAP's." This is the most likely partial result and it still favors keeping the head-to-head in the deliverable.

## 6. Why this is the right test now

The pricing finding currently reads as "the policy-constrained stratification test found within-grade DTI heterogeneity." It does *not* yet read as "a SHAP-equipped validator would have missed it" — and under the FS AI RMF / SR-style language, interpretability *and* benchmarking-to-alternatives are both named tools, so SHAP is the default a bank reaches for. The Olorin-facing argument to do something *other* than SHAP needs to show what SHAP-on-the-deployed-model can't see. The structural reason it can't — SHAP decomposes the model's output, and the pricing finding lives in the model's *miscalibration against realized outcomes within a tier*, which the output decomposition has no term for — is the kind of claim that is much stronger demonstrated on real data than asserted. This experiment demonstrates it (or refutes it).

## 7. Followups (not part of this pre-registration)

- **LIME arm** — model-agnostic local surrogate; different failure modes; a separate pre-reg would add a LIME variant of each criterion.
- **The Rashomon-ified pricing piece (#6)** — once `wedge/pricing.py` has an ε-band-over-a-model-class variant, re-run as literally SHAP-vs-Rashomon on the positive side.
- **FM rate-band version** — the same comparison with `orig_interest_rate` rate-bands as the tier; subject to the "FM rate is LLPA-grid-driven" caveat from the FM cross-regime note.
- **Per-case adverse-action arm** — SHAP's structural home (ECOA/Reg B per-case reason codes) is *not* what this tests; a separate test scoring SHAP's most-confident per-case attributions against realized outcomes is where SHAP should *win*, and conceding that loss strengthens the credibility of the population-level argument.
