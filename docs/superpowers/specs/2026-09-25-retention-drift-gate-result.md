# Retention drift gate — result

**Date:** 2026-09-25. **Pre-registration:** `dc12f1a` (+ A1 `9f6c3db`, A2 appended at `1a9be04`).
**Raw outputs:** `1a9be04` (committed before review). **Blind adversarial review:** scientific-integrity-auditor, REJECT (as a FAccT contribution); instrument judged valid.
**Decision (project owner): FAccT '27 is DROPPED.** No salvage submission.

## What the gate found

Mechanical §7 verdict: **WEAK_GO**. The review showed that verdict is uninformative, and I concede
it: WEAK_GO fires on any unloadable archive, and sklearn *documents* that cross-version unpickling
is unsupported. I saw during drafting that WEAK_GO was near-certain and froze the rule anyway. The
gate could not have returned NO-GO. That is the main design lesson.

Read on the study's own premise ("the lender stores everything"), the substantive result is a
**null for attribution drift**:

1. **When the stored model loads and the explainer's arguments are recorded, the Reg B top-4
   adverse-reason sets reproduce exactly across five years of library releases** (2021→2026
   July-1 stacks): TreeSHAP bitwise identical across shap 0.39→0.52; KernelSHAP with pinned
   `l1_reg` and seed identical to ~1e-16; LIME identical despite a ~100× runtime change in its
   dependency stack. Predictions never changed (max |ΔP| = 0 on every loadable pair).
2. **sklearn pickles break across every later vintage** (four mechanisms: node dtype at 1.3,
   `_gb_losses` removal at 1.4, Cython loss symbol 1.5→1.7, `_loss` path at 1.9; 0.24→1.1 loads
   with explicit warnings then fails on predict). This is documented sklearn behavior, and
   **retraining from the stored recipe recovers identical reasons** (verified independently in
   v2025: v2021 and v2024 origins, R = 0.000, 0 denied flips). Not a finding.
3. **The one silent change:** shap 0.48 changed `KernelExplainer`'s default `l1_reg` from
   `"auto"` (AIC here) to `"num_features(10)"`. Calling with defaults changes the reason set for
   3.5–6.5% of denied applicants. The deprecation warning is a `DeprecationWarning`, hidden by
   default. But omitting the argument contradicts the study's premise; a lender who recorded it
   sees no drift. Known class of change (Montandon et al. arXiv:2408.05129).
4. The v2023 SHAP failure (shap 0.41 vs numpy 1.24) is a broken install at a July-1 snapshot,
   not decay; it fails at origin too. The v2026 xgb TreeSHAP "categorical split" failure is an
   artifact of explaining the live model at archive time — the reloaded artifact works (review #6).

## Bets

B1 held (TreeSHAP R_excess < 1%). B2 held but was near-certain from sklearn's docs. B3 held (xgb
JSON loads everywhere). B4 held only via the live-object artifact (review #6) — scored as NOT
supported. B5 failed (no pinned KernelSHAP drift). B6 held (default vs pinned). B7 failed (no LIME
drift).

## Conceded defects (review)

Harness and scorer were not frozen with the pre-reg (first committed with results); origin
explained the live model, contest the deserialized one; A2 wrongly called the 0.24→1.1 load
"silent" (three UserWarnings are in the log); noise floor is zero by construction (seeded), so
"beyond noise" is vacuous; positive control unavailable at three origins and silently dropped; two
R = 0 cells misclassified AMBIGUOUS. None changes the null.

## What this is good for

It is evidence **for** the leverage branch the withdrawn record-sufficiency study failed to test,
this time across a real serialization and process boundary: a record carrying the explainer's
arguments, library versions, training data and recipe is enough to reproduce Reg B reasons across
five years; pickles are not a record. That is a compliance-note-sized result ("record the
explainer arguments; archive recipe + data, not pickles"), usable in the regulator-facing
artifact. It is not a FAccT paper: one substrate, two models, one real event.
