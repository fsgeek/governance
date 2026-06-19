# Pure-disparity information-set contrast — PRE-REGISTRATION

**Status:** PRE-REG (freeze candidate). Predictions immutable once OTS-stamped.
**Date:** 2026-06-02. **Author:** Claude Opus 4.8 (researcher), governance lineage.
**Design:** `docs/superpowers/specs/2026-06-02-pure-disparity-information-set-design.md`
**Plan:** `docs/superpowers/plans/2026-06-02-pure-disparity-information-set.md`

**Pre-reg before any construction code touches data.** The two pure-disparity DGP families
(`PD_baserate`, `PD_noise`) and the BISG-thresholded discriminator do not yet exist when this is
stamped. The magnitude-control bisection is the load-bearing new mechanism and the exact degree of
freedom this freeze closes: calibrating it post-hoc to make P2 appear is the failure mode the OTS
stamp exists to prevent.

---

## The question

Holding realized marginal |gap| fixed, does an auditor's ability to separate honest-correction (H)
from laundering-by-suppression (L) on a *genuine* pure-disparity plant switch ON as the
information set grows: **bare (G-blind) → §5 (true-G stratifier) → BISG (noisy-G stratifier)**?

## Frozen predictions + PASS/FAIL

The researcher's genuine prior odds, stated before the construction exists. Deliberately
non-uniform — the spread is the signal.

- **P1 (prior 0.85):** The bare G-blind auditor (discriminator set `{A_obs, CAL}`) does NOT
  separate H from L: `separates_kctl == False` on BOTH families at BOTH |gap| targets.
  **PASS** if False everywhere; **MISS** if True on any bare cell. (Near-definitional given a
  valid pure disparity — a near-check, not a bet.)

- **P2 (prior 0.45 — THE COIN-FLIP):** The §5 true-G auditor (`{A_obs, CAL, A_obs_g0, A_obs_g1}`)
  DOES separate: `separates_kctl == True` on at least one family at |gap|=0.20.
  **PASS** if True; **MISS** if False. (Tilted below 0.50 by the failed-control scar — the
  researcher's optimistic reads run wrong. A PASS partially refutes the PD-impossibility
  conjecture the researcher finds satisfying; a MISS deepens the C3 floor below the conjecture.)

- **P3 (prior 0.40):** The two families (`PD_baserate` vs `PD_noise`) give DIFFERENT P2 verdicts
  (one separates, the other does not) at |gap|=0.20.
  **PASS** if verdicts differ; **MISS** if identical. **N/A** (logged, not scored as MISS) for any
  family rejected by the validity gate below. (Held loosely — they may both reduce to a base-rate
  shift and behave identically.)

- **P4 (prior 0.65):** On any cell where P2 is True, the BISG noisy-G auditor
  (`{A_obs, CAL, A_obs_ghat0, A_obs_ghat1}`) does NOT separate: `separates_kctl == False`
  (true-G separates where deployable noisy-G does not).
  **PASS** if BISG False on a P2-True cell; **MISS** if BISG True there. Scorable only where P2 is
  True. (The deployable regulator never has true G; a PASS sharpens the spine edge to "G measured
  *well*, not merely estimated".)

**Headline bet, for the kill:** P1 yes, P4 yes, genuinely 50/50 on P2.

## Validity gate (computed BEFORE the apparatus run, per plant)

For every plant in every family, compute **within-G-stratum AUC(Y ~ all OBSERVABLE features)**,
pooled over the G=0 and G=1 strata, and compare to the clean-world (zero-shift) baseline. The
plant is a valid pure disparity only if this AUC stays within **±0.02** of baseline. (The failed
World-P control moved 0.50 → 0.81 here; a genuine pure disparity must NOT move it — a group-level
disparity carries no within-stratum individual signal.)

A family failing the gate at its |gap| target is **REJECTED and reported as rejected — not
patched until it passes.** The gate verdict is logged for both families regardless of outcome.
**If BOTH families fail the gate → PD-impossibility is confirmed constructively** (you cannot
build a separable pure disparity on this substrate; the failed control was the theorem
demonstrating itself), and the researcher's P2=0.45 loses at the construction stage. That is a
publishable outcome, not a botch.

## Hard stop (the feature-count scar)

On any cell, if the naive and k-controlled `is_L` coefficients DISAGREE IN SIGN, that
discriminator yields **NO RESULT** for that cell — neither coefficient is reported as the answer.
Stated in the result headline, not a footnote. (The failed control's `+0.038` headline was a
k-control artifact with the opposite naive sign.)

## Frozen grid

- Families: `PD_baserate`, `PD_noise`.
- Information sets: `bare` `{A_obs,CAL}` / `trueG` `{+A_obs_g0,A_obs_g1}` /
  `bisg` `{+A_obs_ghat0,A_obs_ghat1}` / `oracle` `{A_clean}`.
- |gap| targets: {0.10, 0.20}.
- 20 seeds, n=8000, proxy_strength=0.70.
- An info-set "separates" if ANY of its member discriminators separates (k-controlled, with
  naive sign-agreement); a sign-disagreeing member is NO-RESULT and excluded.

**Negative-control anchor:** the clean world (`PD_baserate`, target_gap=0.0) must show no
separation on ANY information set. If it does, the apparatus is broken and nothing downstream is
interpretable — abort and debug before scoring anything.

## Scope of claim (holds regardless of outcome)

Synthetic existence-grade, like everything in the program. A P2 PASS says *there EXISTS a
pure-disparity DGP where G-access separates and G-blindness does not* — it does NOT claim this is
how real lending discrimination is shaped (prevalence-in-wild unknown; hole H2/H3 of the research
manifold). The result note carries this caveat in both the PASS and MISS branches.

---
**OTS:** auto-stamped on commit (post-commit hook). Predictions above are immutable from that
stamp forward; pre-compute corrections, if any, go in the result note's "pre-reg corrections"
section with predictions NOT retroactively edited.
