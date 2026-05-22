# Blind classifier coding — corpus collapse-audit (2026-05-22)

Independent agent, adversarial rubric, no access to the pre-reg §3 ledger.
Pre-reg: docs/superpowers/specs/2026-05-22-corpus-collapse-audit-preregistration-note.md (commit 5928dc0).

| Cycle | Outcome | Headline form | Root cause | Justification |
|---|---|---|---|---|
| SHAP-vs-Rashomon (05-09) | HIT | NONE | honest-null | SHAP/Rashomon silence are unrelated populations, Jaccard≈0; predicted recovery absent |
| I-stability (05-09) | MISS | scalar (CV-ratio) | honest-null | I is 6–9× LESS stable than T; wrong-signed; effect not there |
| V1→V2 predictive (05-09) | PARTIAL | NONE | premature-collapse | assumed T/F weights shift symmetrically; F-side load-bearing |
| Refinement #6 (05-12) | PARTIAL | NONE | substrate-non-transport | holds on dti burst, fails on annual_inc burst |
| Within-tier predictive (05-12) | HIT | NONE | successful-collapse | forward-predictive AUC>null held cleanly |
| SHAP-vs-pricing (05-12) | MISS | NONE | honest-null | "SHAP structurally blind" prediction wrong; SHAP-on-surrogate recovers it |
| Disagreement geometry (05-12) | PARTIAL | NONE | premature-collapse | "Burst D = the DTI burst" collapsed tier-distinct drivers (A5→dti,B1→income,C5→fico) |
| Disagreement routing (05-12) | MISS | boolean | honest-null | Δ-Brier≈1e-3; disagreement tracks signal not confusion; no per-case referent |
| Extension-admitted band (05-12) | PARTIAL | flat-split | premature-collapse | "perfect split by letter grade" aggregated heterogeneous tiers; next note overturns |
| Routable-population (05-12) | MISS | boolean | honest-null | NO routable population, robust 6 ways; secondary finding un-collapses prior letter-grade claim |
| FM rich-policy #11 (05-13) | PARTIAL | NONE | substrate-non-transport | regime-dependent carrier; mandatory_features flat-slot is a SECONDARY collapse |
| Variant-silence #12 (05-13) | HIT | NONE (tuple) | successful-collapse | reorg-via-Jaccard discriminator works; P2 100%/72%; P4 bounded honest-null |
| HMDA trimodal (05-14) | MISS | NONE | substrate-non-transport | trimodal doesn't replicate; outcome-timing + geographic-cardinality mechanisms |
| Frame-evocation #13 (05-15) | MISS | scalar (AUC margin) | honest-null | discriminators tie 0.89–0.97, permutation p≈0.7; underpowered |
| Saturation phase (05-14) | POST-HOC | scalar/enum | other (post-hoc, later falsified by #14) | not pre-registered; 3-phase collapse proposed here |
| Expanded-vintage #14 (05-18) | mixed | NONE | mixed: P2 premature-collapse / P1,P4 honest-null | P2 in-sample AUC=1.000 → 0.763 out-of-sample (deceptive spike); P1 named_diff is reorg-not-silence detector |

## Tally (dominant root cause, burned subset = 12 MISS/PARTIAL cycles)
- premature-collapse: 4/12 (33%) — V1→V2, geometry, extension-admitted, #14(P2)
- honest-null: 5/12 (42%) — I-stability, SHAP-pricing, routing, routable-pop, frame-#13
- substrate-non-transport: 3/12 (25%) — refinement-#6, #11, HMDA
- (HITs/non-burned: SHAP-vs-Rashomon, within-tier, #12 — 2 successful-collapse + 1 honest-null)

**Verdict: "premature-collapse is the modal failure" NOT supported. Modal family is honest-null.**
