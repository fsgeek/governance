# Record sufficiency for post-hoc attribution recomputation — pre-registration

**Date:** 2026-09-18. **Status:** PRE-REGISTRATION.
**Target:** ACM FAccT 2027 (abstract 2026-10-27 MANDATORY GATE; paper 2026-11-03; archival).
**Connects:** [[project-current-anchor]], `docs/recomputability-boundary-draft_1.md`, `section6.tex` ~L170-190, `section7.tex` ~L34-48.

**Pre-registration discipline.** Nothing in §3 has been computed. No attribution
has been run on any substrate for this study. The metric and tolerance in §2e are
frozen BEFORE any divergence number exists, because the published result that
motivates this study ([Hwang et al. 2026], §1) shows that metric choice alone
determines whether attributions look stable — so choosing a metric after seeing
results is not a judgment call, it is the whole finding. The OTS stamp on this
commit freezes §2 and §3.

**Inspected:** the LC/FM/SBA schemas, row counts, and the existing `wedge/`
model-construction path (prior work, this lineage). The public benchmark
datasets are standard and their schemas are known from the literature.
**NOT inspected:** any attribution output, any divergence measurement, any
cross-environment comparison. Zero.

---

## 1. Question

The foundation paper (*Architectures of Absence*, SSRN) argues that feature
attributions, local approximations, and internal-state observations are "in
principle recomputable later," while the **binding** — which model version and
configuration, under which policy, produced this decision on this file — is not.
The policy consequence drawn from this is that one small decision-time record
converts several otherwise-unreachable evidentiary objects into reachable ones.

That argument has an unexamined empirical premise: **that recomputation given a
preserved binding actually returns the same evidence.**

Hwang, Lee, Rosenblatt, Stoyanovich & Whang, "Explanation Multiplicity in SHAP"
(arXiv:2601.12654, Jan 2026) hold the trained model FIXED and re-run SHAP,
varying only explainer stochasticity and background resampling. They find
explainer-induced multiplicity dominates on large data, and — load-bearing for
this study — **L2 distance makes attributions look stable while rank-based
metrics (top-k Jaccard, RBO) show disagreement approaching a randomized
baseline.** They do not vary library version, hardware, or floating-point
environment.

This study asks the record-design question their result opens:

> **Which fields must a decision-time binding record carry for a later
> recomputation of a post-hoc attribution to land within a stated tolerance of
> the original — and are there conditions under which no achievable record
> suffices?**

*If SOME achievable field set suffices* → the minimum sufficient record is
specifiable, and the foundation paper's policy claim survives with the record
spec as its concrete content.
*If NO achievable field set suffices* → the binding record does NOT rescue
Class A, the artifacts themselves must be preserved, and the foundation paper's
leverage argument is materially weakened. **This branch is publishable and is
the one this pre-reg expects** (see §3, P1).

## 2. Operational definitions

**2a. The record under test.** A *binding record* is a set of fields captured at
decision time. We test nested field sets, weakest to strongest:

- **R0 (outcome only):** case id, decision, timestamp. *(Negative control — must fail.)*
- **R1 (model identity):** R0 + model identifier + version string.
- **R2 (model state):** R1 + serialized parameters/weights hash + config hash.
- **R3 (+ method construction):** R2 + attribution method, its version, value
  function, background/reference dataset identity + size, sampling parameters.
- **R4 (+ execution environment):** R3 + library versions (attribution lib, BLAS,
  numpy/sklearn), OS, hardware class, thread count.
- **R5 (+ seed):** R4 + RNG seed(s) for any stochastic component.

**2b. Recomputation.** Given a record R, reconstruct the attribution using ONLY
the fields in R plus the preserved input, in a fresh process. Fields absent from
R are resolved as a later examiner would resolve them: by taking the
then-current default (current library version, current hardware, unseeded RNG,
default background).

**2c. Divergence conditions.** Crossed against each record level:
(i) same process, re-run; (ii) fresh process, same machine; (iii) different
library minor version; (iv) different thread count / BLAS path; (v) different
hardware class (CPU vs GPU where applicable). Condition (v) is
*report-if-available*, not gating.

**2d. Substrates (BOTH arms — see §6 for the cut rule).**
- **Arm B (benchmark):** standard public tabular datasets used by the
  explanation-stability literature, for direct comparability with Hwang et al.
- **Arm G (governance):** this project's own lending substrate (LC/FM/SBA) with
  policy-constrained models, where the record-design claim has its motivating
  application.

**2e. THE TOLERANCE — FROZEN.**

Primary metric is **rank-based**, not magnitude-based:

> **Top-k Jaccard similarity on the k highest-|attribution| features, k = 5,
> averaged over the evaluation set.**
>
> **A recomputation REPRODUCES iff mean top-k Jaccard ≥ 0.90.**

Rationale, stated in advance: an L2 or cosine criterion would report stability
that the rank metric does not support, per Hwang et al. In a governance setting
the operative question is "would an examiner reading this attribution reach the
same conclusion about which factors drove the decision," which is a question
about ranks, not magnitudes. **L2 and rank-biased overlap (RBO, p=0.9) are
reported alongside as SECONDARY and are explicitly NON-GATING.**

Adverse-action context makes k=5 the principled choice, not a tuned one:
Regulation B implementations commonly disclose up to four principal reasons;
k=5 sits just above that boundary.

**2f. Sufficiency.** Record level R is *sufficient under condition C* iff
recomputation from R under C reproduces (2e) for **≥95% of evaluated decisions**.
The **minimum sufficient record** is the weakest R sufficient under all gating
conditions (i)-(iv).

## 3. Pre-registered predictions

**P1 — LOAD-BEARING.** R3 (model state + method construction, no environment
pinning) is **NOT sufficient** under condition (iii), library version drift.
**Prior: 0.70.**
*MISS reading:* if R3 IS sufficient, attributions are more robust to environment
than the reproducibility literature suggests, Hwang et al.'s instability is
confined to sampling/background choices that R3 already pins, and the foundation
paper's leverage argument is STRENGTHENED. That is a clean positive result and
must be reported as such, not buried.

**P2.** R5 (everything including seed) IS sufficient under conditions (i)-(iv)
for tree-based models on tabular data. **Prior: 0.65.**
*MISS reading:* if even R5 fails, no achievable record suffices, and the honest
policy conclusion is that Class A artifacts must be STORED, not recomputed.
That is the collapse branch and it is publishable.

**P3.** The gap between R3 and R5 is driven predominantly by the **seed /
sampling** component rather than by library or hardware differences — i.e.
attribution-method stochasticity dominates systems nondeterminism.
**Prior: 0.60.** *(Directional; consistent with Hwang et al. but not implied
by them, since they did not vary environment.)*

**P4.** The L2 criterion would report sufficiency at a record level at least one
step weaker than the rank criterion does — i.e. choosing L2 post hoc would have
produced a falsely reassuring record spec. **Prior: 0.75.**
*This is a methodological finding about record design and is reported regardless
of P1-P3.*

**P5 — negative control.** R0 is not sufficient under any condition.
**Prior: 0.99.** If R0 "reproduces," the harness is broken and no other result
counts.

**Most likely overall miss:** that sufficiency is not a clean step function in R
but varies by model class and dataset size, so "the minimum sufficient record"
is not well-defined globally and the honest output is a conditional table rather
than a single spec. Pre-registered as the expected complication; a conditional
table is an acceptable primary result.

## 4. Sensitivity / robustness (reported, NOT gating)

- k ∈ {3, 5, 10} for top-k Jaccard.
- Jaccard threshold ∈ {0.85, 0.90, 0.95}.
- Sufficiency fraction ∈ {90%, 95%, 99%}.
- RBO p ∈ {0.8, 0.9}.
- L2 and cosine, reported for every cell, never gating.

**Commitment:** none of these will be tuned to move a verdict. The §2e primary
is fixed. If a sensitivity arm contradicts the primary, that contradiction is
the reported finding.

## 5. Scope — what this is NOT testing

- Not whether attributions are *faithful*, *correct*, or *good explanations*.
  Only whether recomputation returns the same object.
- Not model-induced multiplicity (retraining). The model is FIXED throughout.
  That is Hwang et al.'s other arm and we do not duplicate it.
- Not the human-review half of the record. The foundation paper's §6 already
  states that decision-time context and reviewer records have no recomputable
  substitute; this study cannot speak to them.
- Not a claim that any regulator should require any record.
- Not establishing novelty of the governance framing without the literature
  review already begun (prior-art sweep 2026-09-18).

## 6. Implementation and the two-arm cut rule

Result-side script `scripts/record_sufficiency_test.py`; one JSON per
(arm × record-level × condition) cell; one result note.

**Cut rule, pre-committed:** Arm B (benchmark) is PRIMARY and must complete.
Arm G (governance substrate) is the paper's motivating application and is
SECONDARY. If by **2026-10-20** Arm B is not complete, Arm G is cut to a single
worked substrate and reported as illustrative rather than as a second arm.
Deciding this now prevents a deadline-driven post-hoc rationalization about
which arm "was really the point."

## 7. Followups (both branches terminal)

- **If P1 fires and P2 holds:** the paper is "the minimum sufficient record is
  R5, here is the field spec, here is what it costs" — a constructive record-design
  result. Feeds the foundation paper's §6 and the retention corollary in
  `docs/recomputability-boundary-draft_1.md`.
- **If P2 fails (collapse branch):** the paper is "no achievable record suffices;
  recomputation is not a substitute for preservation," which INVERTS the
  recomputability draft's central claim and materially weakens the foundation
  paper's leverage argument. Report it plainly. This lineage's validation has
  repeatedly come from disciplining its own headline down.

Neither branch is a gateway to a further test.

---

**Adversarial step (mandatory, per [[project-ops-invariants]]):** the result note
goes to a blind external reviewer BEFORE the OTS stamp on the result, with the
prior-art context (Hwang et al.) supplied but the verdict withheld.
