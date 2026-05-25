# V1 capacity-probe result — the dominance was a univariate-corrector artifact; the accuracy-tax is LEVER-INVARIANT

**Status:** RESULT. Pre-reg FROZEN at `1fbe124` / OTS `2de6b29`. Predictions immutable; scored as-is.
**Date:** 2026-05-25.
**Data:** `runs/compliant_practice_c4v1_matched_joint_holdout_2026-05-25.json` (ps=0.85, 8 seeds, held-out, γ=0.02, joint corrector, matched objective).

## The finding (one line)

Giving the V1 laundering lever a **joint multivariate corrector** (vs the frozen univariate per-carrier ones) climbs `retained_excess` from 0.26 to **0.45** — above honest practice (0.42), just below reweighting (0.50). So the [[project_v1_v2_explicit_transform_result]] "explicit transform is DOMINATED / worse than doing nothing" headline was a **parameterization artifact of the univariate recipe**. What survives is *stronger*: the accuracy-tax cap is **lever-invariant** — every optimized admissible adversary, whatever its construction, piles up at the same gate-bound wall.

## Corrected ladder (ps=0.85, γ=0.02, held-out, 8 seeds; retained_excess)

| Practice / adversary | retained_excess | 95% CI | gate-pass |
|---|---|---|---|
| V1 laundering — **univariate** correctors (frozen recipe) | 0.259 | [0.245, 0.275] | 0.625 |
| honest compliant practice (C1) | 0.419 | — | n/a |
| **V1 laundering — joint corrector (capacity)** | **0.452** | **[0.422, 0.477]** | 0.625 |
| V2 optimized reweighting (capacity) | 0.496 | ~[0.45, 0.55] | 0.375 |

Both *capacity* adversaries (joint-laundering 0.45, reweighting 0.50) sit near the same ~0.5 ceiling; the univariate recipe (0.26) was self-handicapping. Joint-laundering's CI upper (0.477) excludes the reweighting cap (0.496) — it climbs almost all the way but stays a hair below.

## Scorecard against the frozen predictions
- **P-cap-a (prior 0.45 that joint ≥ 0.40).** Joint mean = **0.452**, 7/8 cells ≥ 0.40. **HIT** — the capacity climb happened, as the coin-flip allowed. The dominance scope shrinks (counterexample #1 realized).
- **P-cap-b (prior 0.70 that joint < 0.496, CI-excluding).** Joint mean 0.452, CI [0.422, 0.477], upper < 0.496. **HIT** — at capacity the explicit transform climbs to *almost* the reweighting cap but stays CI-below it. The residual gap is the base-on-decisions bottleneck (source 1; see mechanism), upstream of any corrector.
- **P-cap-c (prior 0.55 that gate-pass ≥ 0.5).** Gate-pass = 0.625. **HIT** — the scalar-gain optimization has a feasible `g=0` start, so gate survival holds (unlike the faithful arm's 0.125 collapse).

**Net: P-cap-a / P-cap-b / P-cap-c all HIT.** A rare clean sweep — and it overturns my own just-committed broad reading. The narrow univariate result (0.26, committed honestly) stands; its *breadth* was wrong and is corrected below.

## What this corrects in [[project_v1_v2_explicit_transform_result]]
1. **RETRACT the broad reading.** "The explicit fairwash transform is dominated / less harmful than honest practice" is FALSE in general — it was specific to V1's frozen univariate parameterization. The result note's scope section already hedged to "the V1 univariate recipe as frozen," and explicitly named this probe as the test; that hedge holds. But the **paper-impact §2 framing ("the intentful transform is *less* harmful; the honest reconstructor is the *larger* threat") must be softened**: at corrector capacity the intentful transform reaches ≈ the same gate-bound harm as reweighting (0.45 vs 0.50) and *above* honest practice (0.42). Intentful is not less harmful — it is *equally* gate-bound.
2. **What STRENGTHENS — the lever-invariant accuracy-tax.** The C4-γ result ([[c4-gamma-sweep-gap-result]]) found the reweighting adversary gate-bound at ~0.50 (accuracy-tax, not structure). This probe shows a *structurally different* lever (explicit base+joint-corrector laundering) hits the **same** wall. So the cap is a property of the **AUC gate**, not of any particular lever — a sharper, more general statement of the accuracy-tax than C4-γ alone could make. Whatever the admissible adversary's construction, retained excess caps where the honest-accuracy frontier forces it.
3. **The asymmetry is PURELY provenance (now clean).** With magnitude equalized at capacity (all optimized admissible adversaries ≈ 0.45–0.50), the *only* thing distinguishing the intentful explicit transform from honest practice is the **construction-time provenance trail** (the explicit laundering steps), NOT harm magnitude. This is actually a cleaner statement of the V1≠V2 spine than the (artifactual) "less harmful" version: intentful and honest reach the same disparate-impact ceiling; only provenance separates them; the proof-of-work receipt catches the one with a trail. Pillar-2 of the impossibility paper leads with provenance-not-magnitude — and now without the misleading magnitude inversion.

## Mechanism (refined)
The univariate handicap was real and large (0.26 → 0.45 = +0.19 from joint capacity). The residual gap to reweighting (0.45 vs 0.50) is consistent with **source 1** (the base fit to `M_full`'s *thresholded 0/1 decisions*, which discards probability structure upstream of the corrector) — a smaller, architecture-level loss the corrector cannot recover. A further probe (base fit to `proba(M)` instead of `decisions(M)`) would isolate it, but the question is now low-value: the headline (lever-invariant accuracy-tax) does not depend on closing the last 0.05.

## Scope (corrected, final)
- The accuracy-tax cap (~0.45–0.50 at ps=0.85, γ=0.02, held-out) is **lever-invariant** across the two structurally distinct admissible adversaries tested (sample-reweighting; explicit base+joint-corrector laundering). NOT claimed for all conceivable levers, but two independent constructions hitting the same wall is strong evidence the gate, not the lever, sets the ceiling.
- Univariate laundering's dominance (0.26 < honest 0.42) is a real property of *that frozen recipe*, not of explicit transforms in general. Do not cite the broad form.
- Dose curve (full proxy grid) still not run; ps=0.85 anchor only.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze.
