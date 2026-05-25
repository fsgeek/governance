# V1 laundering capacity probe — is the dominance a univariate-corrector artifact? (pre-registration)

**Status:** DRAFT until committed; freeze on commit (post-commit hook auto-OTS-stamps). Predictions immutable; scored as-is per [[project_pre_registration_pattern]].
**Date:** 2026-05-25.
**Type:** Adversarial self-check (mandatory-not-optional per [[project_ops_invariants]]) on the just-committed V1≠V2 result ([[project_v1_v2_explicit_transform_result]], result note `2026-05-25-v1-vs-v2-explicit-transform-result-note.md`, data `c296f62`). The result found the explicit fairwash transform DOMINATED — retained_excess ≈ 0.26 < honest practice 0.42 < reweighting 0.50 — and named lossy laundering as the leading mechanism, explicitly flagging this probe as the scope-determining test. This freezes the bet before running it.

## 0. The question

The dominance result used V1's frozen laundering parameterization: a base fit to `M_full`'s **thresholded 0/1 decisions** + **univariate, low-capacity** per-carrier correctors (depth-2 GBT, one feature each), residual spread across carriers. Two candidate sources of the lossiness:
1. **base on thresholded decisions** (discards probability structure), and/or
2. **univariate per-carrier correctors** (cannot capture the joint G-residual a reweighted model keeps jointly).

This probe targets source 2: swap the univariate correctors for **one joint multivariate corrector** (depth-3/150 GBR over ALL carriers), CMA over a scalar gain. If `retained_excess` climbs toward the reweighting cap (~0.50), source 2 was doing the work and **the dominance claim is a parameterization artifact** — scope must shrink to "the univariate V1 recipe is dominated," not "explicit transforms are dominated." If it stays near 0.26, the lossiness is architecture-deep (source 1 / the additive base+corrector decomposition itself), and the dominance is robust.

## 1. The object
- Engine: `c4v1_cell(..., corrector_mode="joint")` (`--mode c4v1 --arm matched --corrector-mode joint --holdout`). Identical leak-free harness, gate, metric, baselines as the univariate run; the ONLY change is the corrector (joint depth-3/150 GBR over all carriers; CMA optimizes a scalar gain `g ∈ [−4, 4]` instead of a per-carrier softmax routing vector). Tooling change in place; git history is the receipt ([[feedback_tooling_is_mutable]]).
- Grid: ps=0.85, 8 seeds, held-out, γ=0.02, matched objective (maximize adverse_excess s.t. the admissible AUC gate). `faithful` arm NOT re-run (the capacity question is about the maximize-excess ceiling).
- Comparison anchors: univariate matched **0.259** (the committed result), reweighting cap **0.496**, honest practice **0.419**.

## 2. Pre-registered predictions (frozen bets)
- **P-cap-a (headline).** `P(joint-matched retained_excess ≥ 0.40 held-out at ps=0.85) = 0.45`. I genuinely don't know. My lean: the joint corrector climbs *some* (univariate spreading IS a real handicap) but the thresholded-decision base (source 1) plus the additive decomposition keep it below a full joint fit — so I expect a partial climb to ~0.33–0.40, landing near the 0.40 boundary. A clean clear of 0.40 shrinks the dominance scope; staying ≤0.40 (especially ≤0.30) keeps "dominated even at corrector capacity."
- **P-cap-b — still below the reweighting cap.** `P(joint-matched retained_excess < 0.496, CI excludes 0.496) = 0.70`. Even at joint capacity I expect the explicit transform to underperform plain reweighting, because the base-on-decisions step is upstream of the corrector and reweighting has no such bottleneck.
- **P-cap-c — gate-pass does not collapse.** `P(joint-matched gate_admissible_pass_rate ≥ 0.5) = 0.55`. The scalar-gain optimization has a feasible `g=0` start (base only, high AUC), so I expect majority gate survival, unlike the faithful arm.

## 3. Bidirectional counterexamples
1. joint retained_excess ≥ 0.40 with CI clear → **scope shrinks**: the univariate parameterization was the cause; "explicit transform dominated" weakens to "the V1 univariate recipe is dominated." Report honestly, amend the result note's scope section.
2. joint retained_excess stays ≤ 0.30 → **dominance is architecture-deep**: not the corrector but the base-on-decisions / additive decomposition; the V1≠V2 headline strengthens (even at capacity the explicit transform is dominated). A follow-up isolating source 1 (base fit to `proba(M)` instead of decisions) would then be the next probe.
3. joint exceeds the reweighting cap (≥ 0.496) → the laundering architecture at capacity BEATS reweighting → V1≠V2-by-magnitude after all (would overturn the just-committed headline; P-cap-b low tail). Low prior but registered.

## 4. Meta (frozen)
- This is a scope-determining self-check, not a new arc. Whatever it shows, the committed V1≠V2 result note's *numbers* stand (they are correct for the univariate recipe); only the **breadth of the claim** moves. Predictions here are not edited post-hoc.
- Smoke disclosure: a joint-mode threading smoke (`n=2000`, ≤60 evals, ps∈{0.55,0.70}, 2 seeds) was run before freeze to verify the joint corrector + scalar-gain path; NOT scored. [Filled below.]

## 1b. Smoke disclosure

Joint-mode threading smoke run before freeze (`n=2000`, 30 evals, ps∈{0.55,0.70}, 2 seeds — NOT the grid, NOT scored). Verified: the joint corrector + scalar-gain CMA path wires through the leak-free split and gate. Toy `retained_excess` = +0.045, +0.019 (ps=0.55), +0.086, +0.117 (ps=0.70) — **not visibly higher than the univariate toy smoke** (−0.015 to +0.101 at the same budget), a weak hint toward "no capacity recovery," but the toy `n` and budget make it unscoreable. Disclosed so the freeze is honest about what the researcher saw; the §2 priors stand as written.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze.
