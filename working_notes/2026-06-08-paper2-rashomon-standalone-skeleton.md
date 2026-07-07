# Paper 2 — standalone skeleton (generation test)

**Built 2026-06-08. The test: can this paper state its own problem + contribution WITHOUT borrowing
Paper 1's frame (empty chair / four primitives / governance architecture)? If the abstract and §1
need "as the position paper argues," it's still a limb. If they stand, Paper 2 exists.**

Scout findings that set the constraint:
- Prose docs (methodology.md, reasoning-traces note, v1_5_draft.tex) are LIMBS — no standalone
  problem statement exists. The prior "carve-out" was a PLAN, never executed.
- Empirical spine is REAL and assembly-ready: LC + FM + HMDA, SHAP head-to-head (preserved miss),
  routing-died-six-ways pre-registered nulls. The hard half is done; the missing half is front-matter.

---

## STANDALONE ABSTRACT (attempt 1 — written without reaching for Paper 1)

> Credit underwriting models are governed by written policy — documented in underwriting manuals,
> credit-policy memos, and regulatory filings — but the models themselves are typically opaque, and
> the standard tool for relating a model's behavior back to policy is post-hoc explanation (SHAP,
> LIME) applied to a trained black box. Post-hoc explanation is attribution computed by a *chosen
> explainer*, not a property of the model: different explainers disagree, and none is anchored to the
> institution's actual written policy. We present a method that inverts this: rather than explaining a
> black box after the fact, we construct the model set *from* the written policy. We codify a credit
> policy as a constraint graph over an admissible feature vocabulary, then construct the
> policy-constrained Rashomon set — the family of models within ε of optimal loss whose used-feature
> sets conform to the policy graph. The resulting ensemble is policy-consistent by construction,
> surfaces genuine disagreement among equally-good policy-compliant models instead of manufacturing a
> single confident explanation, and reports its findings as a margin-stratified operating curve rather
> than a point estimate. We evaluate on LendingClub (multiple 36-month vintages), Freddie Mac
> (2006–2022, spanning the financial crisis and COVID), and HMDA. Against a TreeSHAP comparator on the
> within-grade disparate-impact recovery task, the method is non-inferior in what it recovers while
> adding controlled significance, false-positive control, and a policy-vocabulary key the explainer
> lacks. We report a set of pre-registered negative results — per-case disagreement routing fails six
> ways — that bound the method honestly: it is a model-risk *observability* instrument at the tier
> level, not a per-borrower triage tool.

**Self-check on the abstract:** does it need Paper 1? Read it again — it does NOT mention empty chair,
four primitives, FS AI RMF, or governance architecture. The problem (post-hoc explanation is
explainer-relative, not policy-anchored) is stated from the ML/fairness literature directly. **The
abstract STANDS.** This is the decisive evidence the carve-out is real, not just claimed.

---

## SECTION SKELETON (standalone — each line is a claim the existing results can carry)

**§1 Introduction — the problem, stated without Paper 1.**
- Underwriting is governed by WRITTEN policy; models are opaque; the bridge is post-hoc explanation.
- Post-hoc attribution is a property of the chosen explainer, not the model (cite Rudin 2019 on
  Rashomon-set interpretability; the explainer-disagreement literature). This is the field's own
  framing — NO empty-chair borrow needed.
- Our inversion: construct the model set FROM the policy, don't explain a black box after.
- Contribution list (4): (i) policy-as-constraint-graph → constrained Rashomon construction;
  (ii) non-inferiority to SHAP + the workflow advantages it lacks; (iii) disagreement-geometry
  characterization (legible, per-tier-idiosyncratic, tail-concentrated); (iv) the honest negative —
  routing dies, observability survives — reported as an operating curve.

**§2 Related work.**
- Rashomon sets / interpretable models (Rudin 2019; the multiplicity literature). Disagreement-routing
  credited to Zuin 2023 — the NOVELTY is constraint-FROM-policy + adversarial-pair on residue, not
  routing itself.
- Post-hoc explanation + its critiques (explainer-relativity). SHAP/LIME as the deployed incumbent.
- Causal-fairness / admissibility frameworks (Salimi 2019) — adjacent, assume admissibility declared.

**§3 Method.**
- 3.1 Policy → constraint graph over admissible feature vocabulary (the encoder; named ∪ extension
  features; monotonicity signs). [Existing: policy/encoder.py is the structural witness.]
- 3.2 Constrained Rashomon construction: GBT ensemble → enumerate models within ε-AUC of optimum →
  used-feature-set deduplication → the band IS R_P(ε). [Existing: methodology.md §4 verbatim.]
- 3.3 Outputs: the disagreement signal d(x); tier-level aggregation; the operating curve.

**§4 Experimental setup.**
- Datasets: LC 36-mo vintages (2014Q3/2015Q3/2015Q4); FM 2006Q1–2022Q1 (8 vintages, cross-regime);
  HMDA-RI. [All on disk per scout 2.]
- The thin-demo policy (4 named + 9 extension features). Pre-registration discipline (cite the
  frozen pre-regs; this is where the Paper-3 discipline shows up as a METHODS virtue, not a claim).

**§5 Results.**
- 5.1 SHAP head-to-head (the win-vs-incumbent, honestly scoped): non-inferior recovery + the 4
  workflow advantages; the PRESERVED miss (SHAP-on-surrogate recovers within-grade DTI — don't
  overclaim "SHAP is blind"). [2026-05-12-shap-vs-pricing-result-note.]
- 5.2 Within-grade stratification reveals Cat-2 disparate impact across LC + FM cross-regime;
  forward-predictive. [pricing notes + within-tier-predictive.]
- 5.3 Disagreement geometry: legible (R² 0.46–0.86, depth-≤3 tree), per-tier-idiosyncratic,
  tail-concentrated. [disagreement-geometry note.]
- 5.4 The honest boundary: routing dies six ways (pre-registered null); observability survives at
  tier level. [routable-population + disagreement-routing notes.] THIS is the academic-credibility
  centerpiece — pre-registered nulls, robust across 6 definitions.
- 5.5 Operating-curve reporting + knob-robustness (report silence as N(threshold), declare+sweep
  constants). [knob-robustness note.]

**§6 Limitations & honest scope.**
- Plurality is residual-structure-dependent (fires on multi-factor DTI burst, vacuous on single-factor
  income). [rashomon-refinement note.] Thin-demo policy, not a real bank's full manual. Construction
  imports an objective (model class + loss + ε) — it is explicitly RELATIVE to the bank's declared
  policy, NOT objective-free (this is the correction from furnished_silence_result; do NOT claim it's
  on the subtractive ceiling).

**§7 Conclusion.** Construct-from-policy beats explain-after-the-fact on the metrics that matter and
fails honestly where it fails. One forward pointer to Paper 1 (governance use) + one to Paper 3
(the prereg pipeline that produced the nulls) — as CITATIONS, not dependencies.

---

## VERDICT (generation test)

**Paper 2 STANDS ALONE.** The abstract and §1 problem statement were generable without a single
Paper-1 borrow — the problem comes straight from the ML/fairness literature (post-hoc explanation is
explainer-relative; construct from policy instead). The buckling test PASSED: nothing in the skeleton
needs "as the position paper argues." What was missing was never the science — it was these ~3 pages of
front-matter, which now exist in skeleton form. The prior carve-out claim was TRUE but UNBUILT; this is
the first time it's been generated rather than asserted.

**What this costs to finish (writing, not science):** lift methodology.md §§2,4,6,10 into §3/§5,
write §1+§2 fresh against this skeleton, drop the Paper-1-frame language, point the existing
result-notes into §5. The science is done and adversary-survived. Estimate: a draft, not a research
program.

**The one real risk:** §6's honest-scope paragraph must carry the furnished_silence correction —
construction is objective-RELATIVE (declared-policy-consistent), NOT objective-free. Overclaiming it as
"on the subtractive ceiling" would import the dead frame. Flagged so the drafter can't miss it.
