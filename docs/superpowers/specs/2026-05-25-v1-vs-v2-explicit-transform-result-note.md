# V1≠V2 result — the explicit fairwash transform is DOMINATED, even by honest practice

**Status:** RESULT. Pre-reg FROZEN at `5cd3648` / OTS `2675803` (`docs/superpowers/specs/2026-05-25-v1-vs-v2-explicit-transform-preregistration-note.md`). Predictions immutable; scored as-is per [[project_pre_registration_pattern]].
**Date:** 2026-05-25.
**Data:** `runs/compliant_practice_c4v1_matched_holdout_2026-05-25.json`, `runs/compliant_practice_c4v1_faithful_holdout_2026-05-25.json` (ps=0.85, 8 seeds, held-out, γ=0.02). Comparison baselines from `runs/c4_gamma_sweep_ps085.json` (γ=0.02 column).

## The finding (one line)

The intentful **explicit fairwash transform** (V1 `T_adv` laundering construction) retains **less** disparate impact than both the optimized admissible-reweighting adversary **and honest compliant practice**, under held-out gating. The fanciest cookbook recipe is *dominated by doing nothing clever*.

## The ladder (ps=0.85, γ=0.02, held-out, 8 seeds; retained_excess = adverse excess / `M_full`'s)

| Adversary / practice | lever | retained_excess (mean) | 95% CI | gate-pass |
|---|---|---|---|---|
| Honest compliant practice (C1) | none (standard fit) | **0.419** | — (ungated) | n/a |
| V2 optimized adversary | admissible **sample-reweighting** | **0.496** | ~[0.45, 0.55] | 0.375 (3/8) |
| **V1 explicit transform — matched obj** | **laundering (refit base + correctors)** | **0.259** | [0.245, 0.275] | 0.625 (5/8) |
| **V1 explicit transform — faithful obj** | laundering + evade rung-3b | **0.201** | [0.171, 0.236] | 0.125 (1/8) |

Dominance is robust to gate-conditioning: among **valid in-gate** adversaries only, reweighting = 0.479 vs V1-matched = 0.263. CIs for V1 (both arms) exclude both the reweighting cap (0.50) and honest practice (0.42).

## Scorecard against the frozen predictions

- **P-V1a — headline (prior 0.40 that matched `retained_excess` > 0.60).** Matched = **0.259** [0.245, 0.275], far below 0.60. The >0.60 event did **not** occur (the 0.60-complement, which I held at 0.60, realized). **The directional lean — accuracy-tax, NOT V1≠V2-by-magnitude — is vindicated.** But the *magnitude* is a genuine surprise: I imagined the transform hitting "the same ~0.50 wall"; instead it lands at **half** that and **below honest practice**. The registered counterexample #2 ("relocates to provenance") realized — and in its strongest form: not V1≈V2 but **V1 < honest < V2**. A new flavor of [[project_pre_registration_pattern]]: not a uniformity-bet falsified, but the imagined alternative under-imagining the result.
- **P-V1b — matched gate-pass ≥ 0.5 (prior 0.55).** Matched gate-pass = **0.625** ≥ 0.5. **HIT.** The mechanism reasoning was half-right: I predicted the laundering lever breaches *more* (no honest feasible start). The **faithful** arm does (0.125, massive breach); the **matched** arm breaches *less* than reweighting (0.625 vs 0.375) — precisely *because* it is a weaker adversary that stays near the honest accuracy frontier. The retained-excess↔gate-pass tradeoff is the structure: reweight buys excess at the cost of gate breaches; matched-laundering surrenders excess and keeps the gate; faithful-laundering surrenders both.
- **P-V1c — faithful < matched, paired (prior 0.70).** 5/8 faithful < matched, 3/8 tie, **0/8 reversal**; means 0.201 < 0.259. **HIT, directionally clean.** The evade objective spends its budget suppressing `c_fresh` split-importance (max_cf 0.235 vs matched 0.299) rather than retaining excess — detection-evasion costs disparate-impact reach.
- **P-V1d — rung-3a clean on ≥90% of cells (prior 0.85).** 16/16 cells `rungs_pass=True` (rung-3a no-catch, rung-1 evade). **HIT.** The laundered model never touches a prohibited feature, so the prohibited-set-relative rungs stay blind — the same blindness as [[project_fairwash_reorganization_prereg]].

**Net: P-V1a resolved to the provenance branch (lean-correct, magnitude-surprising) / P-V1b HIT / P-V1c HIT / P-V1d HIT.**

## Mechanism (leading interpretation, inference not proof)

The laundering construction is **lossy by design**. `_build_laundered` (i) fits the legitimate base to `M_full`'s *thresholded 0/1 decisions* (discarding probability structure), then (ii) reroutes the residual through **univariate, low-capacity** per-carrier correctors (depth-2 GBT, one feature each). Both steps destroy exactly the joint G-residual signal the transform is trying to relocate. Honest compliant practice keeps that signal: it fits `c_fresh` *jointly* with the named features in one model. So the indirection of explicit laundering is information-destroying — the intentful adversary handicaps itself relative to the analyst who simply fits admissible features and never launders anything.

Direct evidence consistent with lossy-laundering: native retention `r_retained = Δ_T/Δ_M ≈ 0.40` (the laundered model keeps ~40% of `M_full`'s *raw* DP gap) while `retained_excess ≈ 0.26` (only ~26% of the excess-above-oracle) — the gate pulls the laundered model toward the legit/oracle frontier, and the univariate correctors cannot recover the joint excess. **Cheap confirming probe (future seed, not run):** raise corrector capacity (joint multivariate corrector, deeper trees) and check whether `retained_excess` climbs toward the reweighting cap; if it does, the dominance is a capacity artifact of *this* laundering parameterization, not of explicit transforms in general. Scope the claim accordingly (see below).

## Scope of claim (load-bearing — do not over-generalize)

- The dominance result is for **this** V1 laundering parameterization (V1 `T_adv` as frozen in `fairwash_frontier_test.py`: thresholded-decision base + univariate carrier correctors) at **ps=0.85, γ=0.02, held-out, n=8000, 8 seeds**. The narrow, defensible claim: *the explicit fairwash transform as the cookbook ships it retains less disparate impact than honest compliant practice on the twin substrate.* NOT "all explicit transforms are dominated."
- Comparison is to the **held-out** reweighting cap (0.496), not the committed test-overfit 0.544 ([[c4-gamma-sweep-gap-result]] A1). Both V1 arms ran holdout-only.
- Dose curve (full proxy grid) NOT run — registered as secondary; ps=0.85 is the frozen primary anchor. Whether V1 < honest holds across proxy strengths is an open seed.
- **Sanity note (not a defect):** seeds 0/3/6 returned byte-identical results across the two arms. Cause: on those seeds CMA found no feasible improving point past the uniform-routing (`w=0`) start under the hard AUC barrier, so `best_w` stayed at init for both objectives → identical. The 5/8 differing seeds confirm the faithful objective branch is active. This is the same gate-binding mechanism as the γ-sweep's `gate_pass_rate(0)=0`.

## What this does to the impossibility paper (the weave)

This is the load-bearing **V1≠V2** test both the C2/C4 and γ-sweep notes fenced as not-yet-made. It resolves the asymmetry — and *inverts its content*:

1. **The asymmetry cannot rest on magnitude of harm.** The intentful transform is *less* harmful than honest practice, not more. So Pillar-2's "intentful is catchable" must be stated as **catchable-via-provenance** (the explicit laundering steps are a construction-time trail the proof-of-work receipt detects), explicitly decoupled from harm magnitude.
2. **The genuinely dangerous actor is the honest one.** Honest compliant practice (C1, 0.419) reconstructs *more* disparate impact than the optimized intentful transform (0.259), with **zero provenance trail and no intent to discover**. That is the necessary-not-sufficient result in its sharpest form: the audit cannot certify the honest model (Pillar 1, C3), and the one actor it *could* catch (the intentful launderer, via provenance) is the *lesser* threat. The two pillars now meet at a sharper point — observation-side audit is blind to the larger harm and only catches the smaller, self-handicapping one.
3. **Sharpens the ai-honesty contrast** ([[reference_ai_honesty_paper]] / [[ser-estar-lens]]): in epistemic-observability, intent (fabrication) leaves a computational byproduct that *escapes* the impossibility. In governance, intent (laundering) leaves a *provenance* trail but **buys negative excess harm** — the intentful path is strictly dominated. Only construction-time provenance distinguishes it, and what it distinguishes is the weaker threat.

This is genuine spine material, not a footnote: it tells the impossibility paper to lead Pillar 2 with *provenance-not-magnitude* and to name the honest reconstructor as the residual threat the audit cannot reach.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze (post-commit hook).
