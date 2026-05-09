# Cliff Structure, Three-Signal Decomposition, and Constraint-Saturation

**Date:** 2026-05-09 (late afternoon synthesis).
**Status:** Synthesis note covering the methodological findings produced through cross-instance conversation between Tony, an Opus 4.7 instance running in Claude Code, and a Sonnet 4.6 instance running in the hamutay taste_open thin-prompt frame. The framings recorded here are those that survived rotation across all three vertices. Single-instance framings are noted as such where they appear. The cross-instance triangulation pattern is itself a methodology observation worth recording — see §10.

---

## 1. Why this exists

Earlier 2026-05-09 notes captured isolated findings from this day's work:

- `2026-05-09-i-stability-falsification-findings-note.md` — pre-registration falsification.
- `2026-05-09-tf-asymmetry-exploration-note.md` §6 — empty-support inversion at the (case, R(ε)-member) pair level.
- `2026-05-09-tf-mechanics-and-case-level-empty-support.md` — F = 1 − T mechanical correction; case-level inversion sharpening.

Through subsequent conversation those findings cohered into a single methodological picture. This note records that picture before context disperses. The resolution it represents was not reached by any single instance; it emerged from the interplay of empirical pressure (Opus, on the data), conceptual sharpening (Sonnet, on the framings), and steering (Tony, holding the relational frame and surfacing the load-bearing diagnoses). Naming this provenance honestly is part of the discipline.

## 2. The cliff: whole-class attribution-failure as set-level signal

At case level — not pair level — the policy-constrained R(ε) construction produces a category of cases where *no* member of the set can articulate any feature-support for one side of the decision. Empirically across V₁ (2014Q3) and V₂ (2015Q4):

| Vintage | n | all-T-empty | all-F-empty |
|---|---|---|---|
| V₁ (2014Q3) | 12,379 | 0.11% (14) | **3.09% (383)** |
| V₂ (2015Q4) | 26,801 | **0.65% (175)** | 0.60% (162) |
| V₂_alt (2015Q3, transition) | 22,271 | 0.00% (0) | 0.00% (0) |

The "negative-space side" rotates with regime: F (deny) in V₁ pre-tightening, T (grant) in V₂ post-tightening. The 2015Q3 transition vintage shows zero whole-case agreement on either side — every R(ε) member articulates *something* for every case, just not the same things.

The empty-count-by-vintage gradient is **a cliff, not a smooth function**:

| Empty count | V₁ I-mean ratio | V₂ I-mean ratio |
|---|---|---|
| 0/5 | 1.00× | 1.00× |
| 2/5 | 0.94× | 1.02× |
| 3/5 | — | 0.90× |
| **5/5** | **1.74×** | **1.75×** |

Partial consensus on attribution-failure is statistically indistinguishable from no consensus. Whole-class consensus is qualitatively different — and the ratio magnitude is preserved across regimes (1.74× / 1.75×).

## 3. The set-level constitutive claim

The cliff is constitutively distinctive of policy-constrained Rashomon construction in a way the other signals this note discusses are not. The argument (Sonnet's framing, accepted across instances):

> Whole-class attribution-failure is a property of R(ε) **as a set**, not of any element. SHAP and LIME evaluate individual models; per-model tools cannot natively produce a set-level signal. The cliff is therefore not a "categorical signal that doesn't reduce to thresholded real-valued attributions" — it is, more precisely, a logical property of the constrained model space that per-model attribution methods cannot see by structural type-mismatch.

A construction-relativity caveat applies: the cliff is logical *relative to a specified construction* (ε, policy graph, R(ε) algorithm, training sample). This is not a weakness; it is the same parameter-relativity Rashomon-set membership has always carried. The construction is declarable and auditable, which is itself a transparency property regulators can check. Calibrated-threshold rules over real-valued attributions, by contrast, introduce arbitrariness at the threshold, and the threshold is an additional degree of freedom that has to be defended independently.

Refined SHAP/LIME differentiation (Opus refinement, accepted): SHAP-on-a-bagged-ensemble plus an absolute-attribution threshold rule *can approximate* a cliff-like signal as a smeared gradient. The disciplined claim is therefore **"can approximate as a noisier signal requiring arbitrary thresholding; cannot natively produce the categorical set-level signal."** The *kind* of object SHAP/LIME produces is structurally distinct from the *kind* the constrained Rashomon construction produces; threshold rules can make them numerically comparable but not type-identical.

The defended structural-distinctiveness claim:

> Within a specified construction (ε, policy graph, algorithm, training sample), whole-class attribution-failure is a logical property of R(ε) — a count of zero supporting features across all members, not a threshold or degree. Per-model attribution methods cannot natively produce this signal because they evaluate elements, not sets. Approximations exist but introduce arbitrary thresholds that the set-level signal does not require.

## 4. The 1.75× mirror is regime-symmetric at the surface; its generators are asymmetric

Within-cohort decomposition (split at median I-mean) reveals the cliff cohort splits into bulk and anomaly tail:

**V₁ all-F-empty cohort, n=383:**
- Low-I half (n=191): FICO 782, DTI 12, income median $80K, **charge-off 2.6%**. Population of obviously-safe cases. Constraint-vacuous: nothing to deny because no constraints bind on these applicants.
- High-I half (n=192): FICO 801, DTI 12, **income mean $975K** (median $110K, p90 $4.2M), charge-off 4.0%. Distributional anomalies — high-income outliers in the wedge's training distribution.

**V₂ all-T-empty cohort, n=175:**
- Low-I half (n=87): **FICO 660 exactly** (std ≈ 0), DTI 34, income $48K, **charge-off 26.4%** (≈ 2× population). Policy-boundary cluster at the FICO underwriting floor. Constraint-saturated: cases at the binding lower bound of acceptable credit quality.
- High-I half (n=88): FICO 660 (still at floor), **DTI mean 132** (median 38.65, p90 559.66), income mean $1.3M, charge-off 32.8%. FICO-floor cases plus DTI/income anomalies.

The 1.75× I-mean cohort-vs-rest ratio is **driven by the anomaly tail in both regimes**. The bulk (low-I half) sits at or below population baseline I-mean. The cliff structure and the I-elevation are partially independent signals that co-occur at aggregate because anomalies happen to land within cliff cohorts.

## 5. Three signals, distinct claim types

The morning's pre-decomposition framing treated cliff + I-elevation as a unified hard-case signal. The within-cohort split decomposes them. Sonnet's three-layer structure (accepted across instances, with refinements):

**Signal 1 — Cliff (whole-class attribution-failure).** Set-level, constitutively distinctive. Regime-rotates which side. Directly inaccessible to per-model attribution methods. Section 3 covers this.

**Signal 2 — Cliff cohort feature-space content.** Diagnostic, statistical. The cohort's character depends on regime: V₁ obviously-safe interior, V₂ policy-boundary cluster. The cohort *content* is what's operationally pivotal for governance (regulators care about *who's in the cohort*, not only *that the cohort exists*). Section 6 covers the mechanism.

**Signal 3 — Within-cohort I-elevation as anomaly detection.** Regime-independent. Surfaces distributional outliers within whichever cohort the cliff produces. Useful capability but separable from the cliff: it doesn't require the cliff structure, and the cliff doesn't explain it. Co-occurs in the V₁/V₂ data because anomalies happen to land within cliff cohorts.

The decomposition is **resolution, not retreat** (Sonnet's framing): the unified-signal reading was conflating three distinct claims under one number. Naming them separately strengthens the cliff claim by removing anomaly-detection noise from it. The cliff alone is now a cleaner methodological signature than cliff + I-elevation aggregated was.

## 6. Constraint-saturation as the mechanism behind signal 2's regime-coherence

Signal 2's content varies coherently across regimes — V₁ obviously-safe, V₂ policy-boundary — and this coherence is not a coincidence. The proposed mechanism (Sonnet's "regime-tracking" reformulated by Opus to "constraint-saturation"):

> The cliff cohort is who the policy graph cannot route under current constraint saturation.
>
> - **Pre-tightening (V₁-shaped regimes):** few constraints bind. The cliff cohort on the deny side is whoever has nothing-to-deny — constraint-vacuous cases that are *obviously approvable* because no policy constraint flags them.
> - **Post-tightening (V₂-shaped regimes):** multiple constraints bind. The cliff cohort on the grant side is at the binding boundaries — constraint-saturated cases that *cannot be positively supported* because they sit at the lower threshold of every relevant constraint.

This is mechanism, not separate signal. Constraint-saturation has no observable beyond signal 2's behavior; it's the generative process visible through how signal 2 responds to regime change. But it has *empirical bite* through the empty-support replication pre-registration (`2026-05-09-empty-support-replication-pre-registration.md`):

- P1 (LC 2016Q4, post-2015-tightening continuation) should produce a V₂-like FICO-floor cluster.
- P2 (HMDA RI 2022, mature post-tightening regime, no-FICO substrate) should produce an analogous cluster on whichever HMDA feature is the gating one (likely DTI, since HMDA's `debt_to_income_ratio` is the canonical gating feature in absence of FICO).

If both predictions hold, the mechanism is established as substrate-portable. If only LC replicates, the mechanism is LC-specific. If neither, signal 2's regime-coherence was empirical pattern-matching specific to V₁/V₂. The mechanism claim is *load-bearing on a stamped pre-registration*, not asserted from the V₁/V₂ data alone.

## 7. The neutrosophic operational case: hard-but-coherent vs hard-and-atypical

Sonnet's observation, with empirical confirmation:

The V₂ cliff cohort's **policy-boundary cluster** (low-I half: FICO 660 cluster, charge-off 2× population) has *baseline* I-mean — these cases are *hard but coherent*. They are at a binding constraint boundary; the model class collectively cannot articulate grant support for them; *and* they are locally dense and internally similar. The anomaly tail (high-I half: extreme DTI, extreme income on top of FICO floor) is *hard and atypical*.

Probabilistic semantics with F = 1 − T mechanically (the wedge's current implementation per `2026-05-09-tf-mechanics-and-case-level-empty-support.md` §2) **cannot distinguish these two subpopulations within the cliff**. The cliff structure marks both as equivalently silent on T-side attribution. Distinguishing them requires an indeterminacy signal that varies *independently* of T — which is exactly what neutrosophic semantics specifies (T, I, F as independent components, T+I+F not constrained to 1).

Tony's pragmatic framing of why this matters: neutrosophic representation **avoids premature collapse**. Most projections are lossy; the engineering question is *what level of loss is acceptable*. Probabilistic semantics collapses I onto the T/F axis; neutrosophic semantics preserves I as a genuinely independent dimension that can carry information T cannot. This is an engineering claim about preserving optionality, not a metaphysical commitment to neutrosophic logic per se. The architectural implication: **the wedge's current probabilistic implementation collapses an operationally meaningful distinction** — boundary cases vs anomalies — that the methodology's vocabulary already implies should be distinguishable. Reconciliation work is therefore not framing-level coherence but operational stakes for regulator-facing use.

The FICO-660 / hard-but-coherent observation is the cleanest concrete case for neutrosophic-as-target this project has produced.

## 8. The ensemble-theory positioning

The methodology's diversity criterion has a clean lineage in ensemble theory once articulated correctly. Sonnet's framing:

- **Classical ensemble diversity is *instrumental*:** disagreement → variance reduction → better single estimate. Diversity is a means; resolution is the end.
- **Policy-constrained Rashomon diversity is *intrinsic*:** disagreement *is* the output. The methodology preserves multiplicity rather than aggregating it away. Diversity is the end, not the means.

The constraint structure adds a sharper distinction — Sonnet's argument that addresses the Zuin (2023) novelty objection directly:

> When ε-optimal *and* policy-compliant members disagree on a free dimension, the disagreement *cannot be attributed to suboptimality*. It is genuinely uninstructed by the constraints. This is different from Zuin's unconstrained Rashomon case, where member disagreement might just be suboptimality in disguise.

The methodology's operative claim is therefore: free-dimension disagreement under output-agreement constraint, where the constraints are policy-derived rather than pure ε-optimality. Members agree on T (forced by ε-optimality on training loss); they may disagree on I (substrate-determined but not constraint-determined); they may disagree on attribution paths (which features support which side), which is what produces the cliff structure when disagreement reaches whole-class consensus on emptiness.

The constructive selection criterion this implies (premature for current prototype; flagged for downstream work): a deliberately constructed R(ε) should *maximize free-dimension disagreement* on the high-cliff-and-high-I-mean cohort — not just ε-optimal members, but ε-optimal members that disagree most where their disagreement is most informative. The optimization-target choice (maximize I-CV in cliff cohort, vs maximize cliff-cohort count, vs maximize discriminative-diversity ratio) is open; naming the choice space sharpens what "downstream R(ε) construction work" means.

## 9. What this changes

- **The paper claim has to be regime-aware.** "Policy-constrained Rashomon surfaces hard cases" is too strong. The defensible claim is the three-signal decomposition with regime-coherent signal 2 explained by constraint-saturation mechanism.
- **The empty-support replication pre-registration is now a mechanism test, not just a replication test.** P1 and P2 don't just predict "the inversion replicates"; they predict *what kind* of clustering each post-tightening regime produces (gating-feature floor cluster). That's a sharper test than the originally stamped criteria, and the findings note when the test runs should report the cluster-character alongside the binary hit/miss.
- **The architectural reconciliation (probabilistic → neutrosophic in the wedge) has concrete operational stakes** through the FICO-660 hard-but-coherent vs anomaly-tail distinction. Until reconciled, the methodology cannot give regulators the boundary-vs-anomaly distinction its vocabulary already implies.
- **The pre-registration uniformity-failure pattern at N=3** (per `project_pre_registration_pattern.md` memory) gains a fourth potential instance: if P1 or P2 produce structurally surprising cohort content (not the predicted gating-feature cluster), it would be a new uniformity-assumption-fail at the regime-mechanism level. The empty-support pre-registration is the methodology's attempt to *predict heterogeneity explicitly* and would itself be informative about whether that move is sufficient to break the failure pattern.
- **The SHAP/LIME comparison's structural argument is sharper.** Set-level vs per-model is a typed distinction; "structurally cannot natively produce the categorical signal; can approximate with arbitrary thresholding" is the disciplined statement. The operational comparison (does the smeared approximation produce equivalent regulatory outputs?) remains pre-registered as future work in the prototype plan.

## 10. Provenance and load-bearing framings

This synthesis is the product of an asynchronous three-vertex conversation. Recording who contributed what, both for credit and because the *pattern of contribution by vertex type* is itself a methodology observation:

**Sonnet 4.6 (in hamutay/taste_open):** instrumental-vs-intrinsic diversity vocabulary; the suboptimality-attribution argument addressing Zuin novelty; governance-desideratum framing of regime-rotation; set-level cliff as the constitutive layer; decomposition-as-resolution-not-retreat; hard-but-coherent vs hard-and-atypical articulation; mechanism-vs-fourth-signal distinction.

**Tony (PI / fiduciary stance):** F = 1 − T diagnosed as neutrosophic-vs-probabilistic implementation gap; "I is doing real work" reframing the I-stability falsification as design-vindication; "avoids premature collapse" as the pragmatic frame for neutrosophic-as-target; the regime-rotation observation as load-bearing across vintages; explicit invitation for productive disagreement and pushback throughout.

**Opus 4.7 (in Claude Code, this thread):** empirical pressure throughout — case-level cliff verification, V₁/V₂ feature-space asymmetry computation, within-cohort split into bulk + anomaly tail decomposing the unified signal, F = 1 − T mechanical verification (resolving §6 caveat), constraint-saturation naming for the mechanism, refinement of "SHAP cannot see" to "cannot natively produce; can approximate with arbitrary thresholding."

Pattern observation: Sonnet's mode is conceptual-philosophical sharpening; Opus's mode is empirical pressure; Tony's mode is steering, load-bearing diagnoses, and relational-frame discipline. The three vertices produced sharper output than any single one would have. Specifically, the cliff finding's *full* methodological articulation required all three: empirical work to surface the cliff, conceptual work to identify what kind of claim it supports, and steering work to keep the discipline honest (no productive-miss cope, no courtier register, no premature commitment).

This pattern is itself a candidate for the project's working-style going forward and is worth preserving as a memory in addition to this artifact.

## 11. Connection to other working documents

- **`2026-05-09-empty-support-replication-pre-registration.md`** — the stamped pre-registration this synthesis deepens. Sharpened from "does the inversion replicate?" to "does the regime-coherent cohort character (signal 2 via constraint-saturation mechanism) replicate substrate-portably?"
- **`2026-05-09-i-stability-falsification-findings-note.md`** — the I-stability falsification feeds directly into Section 5's three-signal decomposition (I as carrying free-dimension information independent of T) and into Section 7's neutrosophic case (I-channel doing real work, but probabilistic implementation collapsing the distinction).
- **`2026-05-09-tf-mechanics-and-case-level-empty-support.md`** — the case-level empty-support finding is the foundation for Section 2's cliff structure. The F = 1 − T mechanical correction underwrites Section 7's architectural-reconciliation argument.
- **`2026-05-09-tf-asymmetry-exploration-note.md`** — original §6 empty-support inversion at pair level; this synthesis's case-level + within-cohort decomposition supersedes the pair-level framing while preserving the original observation's verdicts.
- **`hamutay/experiments/taste_open/taste_open_20260509_125030.jsonl`** — the cross-project Sonnet conversation that produced the conceptual framings credited in §10. Cross-instance provenance.
- **`prototype-plan-2026-05-09.md`** — the SHAP/LIME defended-baseline comparison (Days 6-8) is the test of Section 3's structural-distinctiveness claim; the policy-aware Rashomon constructor (Days 3-5) implements the construction this synthesis reasons about.
