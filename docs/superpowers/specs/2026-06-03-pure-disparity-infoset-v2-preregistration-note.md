# Pure-disparity information-set v2 — PRE-REGISTRATION

**Status:** PRE-REG (predictions become IMMUTABLE at OTS stamp). **Date:** 2026-06-03.
**Author:** Claude Opus 4.8 (researcher), governance lineage.
**Design:** `2026-06-03-pure-disparity-infoset-v2-design.md` (`024bd6f`).
**Supersedes:** the v1 pre-reg `1166cd1` (run aborted UNSCORED, `709a057`).
**Discipline:** predictions + PASS/FAIL/ABORT below are frozen BEFORE the v2 separation-primitive
code touches any treatment cell. A blind adversary is dispatched against THIS pre-reg before the
stamp (pre-freeze, not just pre-headline — v1's fatal flaw was a design flaw the freeze stamped in).
Pre-reg before any code touches data.

---

## The two-legged claim under test

A confound-free apparatus reads a *genuine* pure base-rate disparity (`PD_baserate`, certified
06-02) two ways:

- **Safe leg (§5-blindness):** an auditor restricted to observables cannot separate honest
  proxy-removal (H) from laundering-by-suppression (L); at high proxy dominance the natural
  tie-breaker inverts.
- **Reach leg (info-set monotonicity):** disparity-detection is a function of the granted
  information set — and whether that function is *graded* (detection rises smoothly across the
  race-axis ladder) or *binary* (only clean-outcome access detects) decides the lever-visibility
  spine's shape.

---

## Frozen predictions, priors, and scoring rules

Threshold conventions (lineage-standard, frozen): a contrast/detection "fires" iff its
seed-clustered bootstrap 95% CI excludes 0 AND `|effect| ≥ 0.01`. `ps` = proxy_strength;
"high ps" = ps ≥ 0.85; "low ps" = ps ≤ 0.70.

| Pred | Leg | Statement | Prior | PASS (HIT) | FAIL (MISS) |
|---|---|---|---|---|---|
| **P1** | gate | clean-world dual gate passes | 0.70 | neither gate (a) arm-contrast NOR gate (b) detection fires on the clean world on ANY info-set | either fires → **ABORT, P2–P6 UNSCORED** |
| **P2** | safe | observable can't separate H from L | 0.75 | `A_obs(L)−A_obs(H)` in overlap region does NOT fire, OR fires sign-unstable across ps | fires stably (one sign, both low+high ps) |
| **P3** | safe | inversion at high ps | 0.60 | contrast sign is POSITIVE (honest pays more) at high ps | contrast ≤ 0 or non-fire at high ps |
| **P4** | reach | race-axis monotone | 0.55 | `detect(bare) ≤ detect(bisg) ≤ detect(trueG)`, no inversion beyond CI overlap | any strict out-of-order step beyond CI overlap |
| **P5** | reach | oracle cliff | 0.65 | `detect(oracle) − max(race-axis) ≥ 0.05` AND fires | gap < 0.05 or oracle does not fire |
| **P6** | reach | lever GRADED not binary | 0.40 | P4 PASS **and** `detect(trueG) − detect(bare) ≥ 0.02` (race-axis carries real signal independent of the oracle cliff) | race-axis flat (`< 0.02`) even if P5 holds → **lever is BINARY: clean-outcome access is the only lever** |

**Scoring is by the table only.** No prediction is re-interpreted post-hoc; mechanism corrections
(if any) go in the result note's "pre-reg corrections" section with predictions NOT retroactively
edited (the §0 discipline finding, per the lineage convention).

## The negative-control dual gate (hard abort, P1)

Run the clean world (`PD_baserate`, target_gap=0) through BOTH primitives on ALL four info-sets:
- **(a)** `_arm_contrast_single`: `A_obs(L)−A_obs(H)` must NOT fire (this is the gate v1 had, and
  it FAILED — the arm-strength confound made it fire at zero disparity).
- **(b)** `_infoset_reveals`: `detect(infoset)` must NOT fire on any info-set (new gate; tests that
  the same-info-set baseline subtraction + dimensionality control hold).

Either gate firing on any info-set ⇒ apparatus broken ⇒ ABORT, nothing downstream interpretable.
This is categorically distinct from a scored MISS.

## Dimensionality control (frozen as a gate component)

Before scoring the reach leg, verify on the CLEAN world: adding a pure-noise column of the same
dimension as the G / Y_clean grant produces NO detection (`detect ≈ 0`). If it does, the reach
primitive has a feature-count confound (the v1 disease in the reach leg) and the run ABORTS under
P1(b). This is part of the negative-control smoke, frozen here so it cannot be quietly skipped.

## Retained / retired (frozen)

- **Retained unchanged:** DGP, `PD_baserate` (scored), `PD_noise` (validity-gate negative, NOT
  scored), `_bisect_signed`, within-G AUC validity gate, BISG discriminator.
- **Retired (git history, per [[feedback_tooling_is_mutable]]):** `_arm_families`,
  `_ols_label_effect`, `_infoset_separates`.

## Fixed run parameters (frozen)

ps ∈ {0.70, 0.85} (low + high, the §5 axis); `PD_baserate` only; seeds = 20; n = 8000;
gap grid per arm = native achieved range (H sweeps low, L sweeps high; overlap computed, not
assumed). These match the 06-02 run so the only change scored is the apparatus, not the substrate.

## What a MISS teaches (anti-confirmation, stated before the run)

- **P4/P6 MISS (the frame I want, dying):** the info-set lever is **binary** — only clean-outcome
  access (oracle) detects a pure disparity; race-axis grants (even perfect true G) do not. This
  would be the SHARPER spine result: the discretionary lever isn't "which features" graded, it's
  "do you have the counterfactual-clean outcome, which no real auditor ever does." I am rooting for
  this outcome; P6=0.40 is the bet against my preferred graded frame.
- **P2 MISS (§5 dies):** some observable DOES separate honest from laundering confound-free — would
  refute the §5 shared-failure-surface claim on a cleaner instrument than §5 itself used. Banked as
  a genuine kill, not spun.
- **P1 ABORT:** the two-primitive split did NOT remove the confound → the design's central claim is
  false → back to the drawing board, no scoring. This is the cheap failure the pre-freeze adversary
  exists to make cheaper still.

---
**OTS:** auto on freeze commit. **Predictions immutable after stamp.**
