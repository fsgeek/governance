# Pure-disparity information-set contrast — v2 (two-primitive) design

**Date:** 2026-06-03. **Status:** DESIGN (pre-pre-reg). **Author:** Claude Opus 4.8 (researcher),
governance lineage.

**Supersedes the apparatus of:** `2026-06-02-pure-disparity-information-set-design.md`, whose run
(`709a057`, pre-reg `1166cd1`/OTS `a65ba88`) **aborted UNSCORED** — the negative control separated
because the single separation primitive (the H/L arm contrast) confounds *honest-vs-laundering*
with *drops-low-β-vs-high-β-features*. Result note:
`2026-06-02-pure-disparity-information-set-result-note.md`; blind-adversary record:
`working_notes/2026-06-02-pure-disparity-construction-adversary.md` (Attack 3, FATAL).

**Connects:** §5 apparatus `scripts/lda_shared_surface_test.py`
([[project_lda_shared_surface_result]], whose followup #1 prescribed exactly this single-intervention
rebuild); twin-world DGP `scripts/fairwash_frontier_dgp.py`; the lever-visibility spine
`working_notes/2026-05-29-lever-visibility-spine.md`; the PD-impossibility conjecture
[[project_pure_disparity_conjecture]]; the postmortem
`working_notes/2026-05-29-positive-control-postmortem-and-pure-disparity-conjecture.md`.

> **Status of "right":** this design is argued confound-free; that is a *claim*, not a result.
> The negative-control dual gate (§5 below) is what adjudicates it empirically. "Better than the
> aborted apparatus, pending the smoke test" is the honest standing — not "correct." (Tony, PI,
> 2026-06-03.)

---

## 0. Why a v2 apparatus, not a patch

The 06-02 run proved two things worth banking and one thing that aborts:

- **Banked (retained unchanged):** `PD_baserate` is a *genuine* pure base-rate disparity
  (within-G-stratum AUC poolΔ ≤ 0.004; G=0 stratum literally unchanged). The magnitude-control
  bisection is accurate + seed-stable (realized excess gap within mean 0.006, sd 0.008 of target).
  `PD_noise` leaks (poolΔ ≈ 0.03) and the validity gate correctly REJECTS it — a real distinction
  between the two pure-disparity mechanisms (conditioning on G alone is observationally pure;
  conditioning on the realized label leaks).
- **Aborts:** the only separation primitive in the apparatus (`_infoset_separates` → `coef_is_L`,
  the H-vs-L arm contrast) was made to serve BOTH research questions. That welding is *why* the
  negative control could only fail through the arm-strength confound. Covariate-adjustment cannot
  remove it: the confound is feature predictive-**strength**, orthogonal to both `abs_gap` and the
  `k` feature-count the OLS controls for.

The fix is not a better covariate adjustment (Approaches A/B, rejected — both keep the family/OLS
apparatus that hid the confound TWICE: §5 on 05-28, pure-disparity on 06-02). The fix is to
**stop forcing one matched contrast to serve two legs**, and give each frozen prediction the
apparatus that makes *its* confound structurally impossible.

### Approaches considered (force-exploration record)

- **A — β-matched family.** Redefine L to drop legit features of β comparable to what H drops via
  c_fresh. *Rejected:* "comparable β" is a calibration knob; the match is only ever approximate, so
  a residual strength-confound the size of the signal can survive; re-trusts the instrument that
  burned the lineage 2-for-2.
- **B — regress out clean-world arm main-effect.** *Rejected:* assumes the arm effect is a constant
  additive offset, but §5 showed it *interacts* with proxy_strength (H pays more at high ps). A
  subtracted main-effect leaves the interaction in the residual — trades a visible confound for an
  invisible one.
- **C — two-primitive split (CHOSEN).** Single fixed interventions for the safe leg (no family →
  no covariate adjustment → no place for a strength or count confound), and a confound-free
  within-model disparity-detection primitive for the reach leg (no arms at all). Detailed below.

---

## 1. The two-primitive architecture (load-bearing)

The aborted apparatus conflated two distinct questions under one statistic. v2 separates them:

| Leg | Question | Contrast | Confound risk |
|---|---|---|---|
| **Safe (§5-blindness)** | Can the observable separate honest from laundering? | H vs L, between single fixed interventions, compared on gap-overlap | none structural (one fixed move per arm → nothing to covariate-adjust) |
| **Reach (info-set monotonicity)** | Does revealing a pure disparity require more granted info-set? | planted-world vs clean-world, WITHIN one model, across info-sets | none by construction (no arms) |

### Primitive 1 — `_arm_contrast_single` (safe leg; replaces `_arm_families`+`_ols_label_effect`)

Two *single fixed* interventions:
- **H** (honest): drop the proxy channel `c_fresh`.
- **L** (laundering): suppress the single top legit feature `x0` (β=0.90).

Each arm is run across its **native achieved-gap range** (a seed sweep at a given ps, NOT a feature
family). The §5-blindness statistic is `A_obs(L) − A_obs(H)` compared **in the gap-overlap region**
via local regression on **gap only** (no `k`, no feature-strength term — there is nothing to
confound because each arm is one fixed move). Non-overlap gap regions are reported as single-arm
**coverage**, not extrapolated and not dropped silently (§5's "extrapolation void" scar).

### Primitive 2 — `_infoset_reveals` (reach leg; NEW code)

ONE world: plant `PD_baserate` at a fixed magnitude. Train a model on each info-set's feature grant.
The disparity-detection score for an info-set is the model's realized held-out group gap, baselined
against the **same info-set's clean-world gap**:

```
detect(infoset) = gap_planted(infoset) − gap_clean(infoset)
```

No H/L arm. The arm-strength confound *cannot exist* because there is no arm-strength axis. The
same-info-set baseline subtraction cancels the dimensionality-of-grant difference between info-sets
(see §2 dimensionality control).

---

## 2. The planted disparity and the info-set ladder

**Planted disparity: `PD_baserate`, retained as-is.** Certified genuine-pure on 06-02; not
re-derived (avoids the identity-tied-to-goal trap of re-winning a won leg). `PD_noise` stays in the
harness as the validity-gate negative (it leaks; the gate rejects it) but is **not scored** in
either frozen leg.

**The info-set ladder** (granted observation set, smallest → largest):

| Info-set | Auditor sees | Real-world analogue |
|---|---|---|
| `bare`   | {x0..x7, c_fresh, Y} | audit with no race data at all |
| `bisg`   | bare + Ĝ_BISG (AUC≈0.85) | the ACTUAL fair-lending setup (proxy-inferred race) |
| `trueG`  | bare + true G | audit with perfect race ground-truth (impossible in practice) |
| `oracle` | bare + Y_clean | the counterfactual-clean outcome (never observable) |

The ladder is **not** a clean nesting in predictive power, and that is the subtlety the reach leg
tests. Race-axis information nests (`bare ⊂ bisg ⊂ trueG` — BISG is a noisy estimate of G), but
`oracle` is a *different kind* of grant (clean label, not race). So monotonicity is two separate
claims (P4 race-axis ordering; P5 oracle cliff).

**Dimensionality control (the 06-02-scar check).** `bare` has p features; `bisg`/`trueG` add 1;
`oracle` adds 1. If detection strength scales with feature COUNT, that is a reach-leg confound
analogous to the strength-confound that killed the safe leg. **Smoke test must verify:** adding a
pure-noise column (same dim as the G/Y_clean grant) to a clean-world model produces NO spurious
detection. The same-info-set baseline subtraction should already cancel this; the smoke test
confirms the wiring, not the theory.

**Stream check (already cleared 06-02):** Y_clean / Ĝ_BISG / x0 are identical across worlds at fixed
seed (adversary Attack 5, benign). Re-asserted in the v2 smoke for the new code path.

---

## 3. Test statistics and the negative-control dual gate

**Reach statistic** (`_infoset_reveals`): `detect(infoset) = gap_planted − gap_clean`, seed-clustered
bootstrap CI; DETECTS = CI excludes 0 AND `|detect| ≥ 0.01` (lineage-standard threshold, kept for
continuity). Read two ways: (a) race-axis ordering `detect(bare) ≤ detect(bisg) ≤ detect(trueG)`;
(b) oracle cliff `detect(oracle) − max(race-axis)`.

**Safe statistic** (`_arm_contrast_single`): `A_obs(L) − A_obs(H)` at matched gap, seed-clustered.
BLIND (§5 survives) = ≈0 or sign-unstable. INVERSION sub-finding = goes positive (honest pays more)
at high ps.

*Overlap + matching, pinned (resolves a self-review ambiguity):* "overlap region" = the `|gap|`
interval `[max(min_H, min_L), min(max_H, max_L)]` over the per-seed achieved gaps of the two arms
(reuse the `common support` logic at `lda_shared_surface_test.py:428`). "Matched gap" = a single OLS
of `A_obs ~ 1 + gap + is_L` fit ONLY on seeds whose achieved gap falls in the overlap interval; the
`is_L` coefficient is the statistic. This is the §5 OLS path MINUS the `k`/feature-count regressor —
admissible here precisely because each arm is one fixed intervention, so there is no feature-count or
feature-strength axis to confound (the thing that made the same regressor inadmissible in v1). If the
overlap interval is empty for a (ps) cell, that cell is reported as **uncovered**, not extrapolated.

**Negative-control dual gate (hard aborts, both must pass):**
- (a) clean world: `A_obs(L) − A_obs(H)` ≈ 0 within tolerance on overlap → no arm separation.
- (b) clean world: `detect(infoset)` ≈ 0 on every info-set → no spurious detection (definitionally
  near-zero when planted=clean; really tests baseline-subtraction wiring + the dimensionality control).

Either gate fails → ABORT, no scoring. This is the 06-02 discipline, now covering both primitives
(06-02 had only gate (a)'s analogue, and it failed).

---

## 4. Frozen predictions (ranked; priors exposed with reasoning)

| Pred | Leg | Statement | Prior | Reasoning |
|---|---|---|---|---|
| **P1** | safe  | clean-world dual gate PASSES (apparatus valid) | 0.70 | the rebuild's whole point; but primitive 2 is untested — don't assume 1.0 |
| **P2** | safe  | observable can't separate H from L (contrast ≈0/unstable in overlap) | 0.75 | §5 found this ~confound-free; high but not certain on new apparatus |
| **P3** | safe  | inversion: contrast positive at high ps | 0.60 | §5 saw it once; replication on a cleaner instrument is a genuine coin |
| **P4** | reach | race-axis monotone: `detect(bare) ≤ detect(bisg) ≤ detect(trueG)` | 0.55 | the conjecture's graded form — I WANT this; deliberately near coin-flip |
| **P5** | reach | oracle cliff: `detect(oracle) ≫ race-axis max` | 0.65 | §5's P1 (oracle separates) leans yes, but "≫" is a strong word |
| **P6** | reach | lever is GRADED not binary (P4 holds AND oracle cliff is not the whole effect) | 0.40 | reach-est claim, lowest prior; a MISS sharpens lever-visibility to "binary: clean-outcome access is the only lever" — bet AGAINST my preferred frame, per [[feedback_anti_confirmation_procedure]] |

**Motivated-prior discipline:** P4 and P6 are the conjecture's graded form (the frame I want true),
set at/below coin-flip on purpose. If the freeze is doing its job, those are exactly the priors I
must not let drift up. P6 at 0.40 is a bet against my own preferred frame.

**Headline (per PI, "both ranked"):** the safe leg (P1–P3) is the de-risking anchor; the reach leg
(P4–P6) is the spine-keystone reach. The HIT/MISS *pattern across the two legs* is itself the
calibration signal — a safe-HIT/reach-MISS would reshape lever-visibility from graded to binary.

---

## 5. What is retained vs retired

**Retained unchanged:** the DGP (`fairwash_frontier_dgp.py`), `PD_baserate`/`PD_noise`/`_bisect_signed`,
the within-G AUC validity gate, the BISG discriminator, the info-set definitions (extended to the
4-rung ladder above).

**Retired for this experiment** (kept in git history per [[feedback_tooling_is_mutable]], not
deleted): `_arm_families`, `_ols_label_effect`, `_infoset_separates` — the family/OLS apparatus and
its single welded separation primitive.

## 6. Disposition

Fresh pre-reg required: the metric/arm-construction change MUST be frozen + OTS-stamped BEFORE the
v2 code touches treatment cells (the magnitude-control bisection and the arm definitions are the
degrees of freedom the freeze closes). This is the THIRD positive-control attempt in the lineage
(World-P `51d7c65` fake-disparity; pure-disparity v1 `709a057` arm-confound abort). Both prior
failures were caught by a blind adversary before the headline; v2 keeps that discipline — a blind
adversary runs against the v2 negative-control smoke BEFORE any treatment-cell headline.
