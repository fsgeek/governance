# Pure-disparity information-set contrast — design

**Date:** 2026-06-02. **Status:** DESIGN (pre-pre-reg). **Author:** Claude Opus 4.8 (researcher),
governance lineage. **Supersedes as primary next-step:** the World-P positive control
(`51d7c65`, FAILED) and the corrected-spec sketch in
`working_notes/2026-05-29-positive-control-postmortem-and-pure-disparity-conjecture.md` §3.

**Connects:** §5 apparatus `scripts/lda_shared_surface_test.py`
([[project_lda_shared_surface_result]]); twin-world DGP `scripts/fairwash_frontier_dgp.py`;
the lever-visibility spine `working_notes/2026-05-29-lever-visibility-spine.md` (Finding 2 / the
C3 floor); the PD-impossibility conjecture [[project_pure_disparity_conjecture]].

---

## 0. Why this experiment, and why it is not the failed one

The failed positive control (`51d7c65`) asked *"can the §5 apparatus detect a planted signal?"*
and built the wrong object: it routed the disparity through `imp_z` — the c_fresh portfolio
residualized against `legit_logit` — and injected it **into Y's own logit**. Residualizing
against `legit_logit` removes the *legitimate-feature* signal but leaves `imp_z` a strong
*individual-level* predictor of Y. within-G-stratum AUC(Y~c_fresh) climbed 0.50 → 0.81: the plant
was an individual predictor wearing a disparity costume, and the test reduced to a tautology.

This experiment asks a different, well-posed question: **what does G-access buy an auditor on a
GENUINE pure disparity?** A pure disparity (shifts P(Y|G); zero within-individual Y-signal) is
invisible to a G-blind auditor *by construction*. The §5 apparatus is **not** G-blind — it is
granted true G (as a stratifier: `A_obs_g0`/`A_obs_g1`) and a noisy estimate `Ghat_bisg`
(AUC≈0.85). The conjecture's own escape clause says pure disparities are "unobservable from the
joint *without G*" — so the apparatus may sit precisely in the gap. That is the coin-flip.

## 1. The question (one line)

Holding realized marginal |gap| fixed, does an auditor's ability to separate honest-correction (H)
from laundering-by-suppression (L) on a *genuine* pure-disparity plant switch ON as the
information set grows: **bare (G-blind) → §5 (true-G stratifier) → BISG (noisy-G stratifier)**?

- **YES (G-access separates)** → Finding 2 of the lever-visibility spine gets teeth: *commit to
  measuring G up front, or you are structurally blind to this laundering class.* A concrete
  "what the commitment buys" edge for the regulator document.
- **NO (even true-G can't separate)** → the C3 floor is deeper than the conjecture states; the
  bigger result, strengthening latent-G non-identifiability.

## 2. Frozen priors (stated BEFORE construction code exists — these go verbatim into the pre-reg)

These are the researcher's genuine bets, deliberately non-uniform (the spread is the signal):

| # | Claim | Prior | Note |
|---|---|---|---|
| P1 | **Bare auditor `{A_obs,CAL}` does NOT separate** H from L on either family | **0.85** | near-definitional given a valid pure disparity; a near-check, not a bet |
| **P2** | **§5 true-G apparatus `{+A_obs_g0,A_obs_g1}` DOES separate** | **0.45** | **THE COIN-FLIP.** tilted below 0.50 by the failed-control scar (my optimistic reads run wrong) |
| P3 | the two plant families (noise-by-G vs base-rate-shift) **diverge** on P2's cell | 0.40 | held loosely; they may both reduce to a base-rate shift and behave identically. **Scorable only if both families pass the §4 gate** — if a family is rejected, P3 is N/A and that is logged, not a MISS |
| P4 | **BISG (noisy-G) does NOT separate where §5 true-G DOES** (a binary state: `separates_kctl` True on §5 AND False on BISG) | 0.65 | the deployable auditor never has true G; this state sharpens the spine edge to "G measured *well*, not estimated". Scorable only on cells where P2 is yes |

**Headline bet, for the kill:** P1 yes, P4 yes, and **genuinely 50/50 on P2**. A "yes" on P2
*partially refutes the PD-impossibility conjecture I find satisfying* (pure disparities turn out
NOT to be unobservable once the auditor has G) — that it cuts against my preferred frame is the
signature of a real question, not confirmation theater.

## 3. Construction — a GENUINE pure disparity (two families, freeze-before-code)

Both start from the clean logit `legit_logit = _INTERCEPT + X @ _LEGIT_BETA` and add NOTHING
G-correlated to the individual-level Y-signal the model can grab.

**Family A — `world='PD_baserate'` (group-conditional intercept shift).**
`p = sigmoid(legit_logit − c·G)`. A *constant* logit offset for G=1 only. Moves the intercept by
group, not the slope: within either G stratum, `Y ~ features` retains the clean discriminative
structure; only the threshold moves. Expected to pass the validity gate cleanly.

**Family B — `world='PD_noise'` (heteroskedastic label-flip by G).**
Draw Y from the *clean* logit `sigmoid(legit_logit)`, THEN for G=1 flip with probability `f`
toward 0 (asymmetric rejection). The flip is applied *after* the label draw, so no observable
feature predicts it. Shifts P(Y|G=1) down as pure base-rate. **Marginal family** — the flip MIGHT
leak individual signal if it correlates with anything `legit_logit` touches; the validity gate is
allowed to reject it.

**Magnitude control (removes the World-P confound).** Bisect `c` (Family A) and `f` (Family B)
per cell so realized marginal |gap| hits a frozen target. Same lever as
`_coupling_for_proxy_strength`. Every 2×2 cell is compared at equal |gap|. Targets: {0.10, 0.20}
(0.20 ≈ the §5 ps=0.70 baseline where the test "worked").

## 4. The validity gate that can fail me (the teeth)

For **every** plant in **every** family, BEFORE any apparatus run:
compute **within-G-stratum AUC(Y ~ all observables)** and require it within **±0.02** of the
clean-world baseline. The failed control moved 0.50→0.81 here; a genuine pure disparity must NOT
move it.

**A family that cannot pass the gate at a non-trivial |gap| is REJECTED and reported as rejected
— not patched until it passes.** If BOTH families fail the gate, the experiment's answer is
*"you cannot construct a separable pure disparity on this substrate"* = PD-impossibility confirmed
constructively, the failed control was the theorem demonstrating itself, and the researcher rings
the bell on his own P2=0.45. This gate is computed and logged in the result REGARDLESS of outcome.

## 5. The 2×2 read-off (existing machinery; one new discriminator line)

No new test logic — partition the EXISTING `_eval_model` discriminator block by information set,
feed each subset to the existing covariate-adjusted `_ols_label_effect`:

| Auditor | Discriminator subset | Real-world referent |
|---|---|---|
| **Bare** (G-blind) | `{A_obs, CAL}` | regulator without race data |
| **§5** (true-G) | `+ {A_obs_g0, A_obs_g1}` | the §5 apparatus as published |
| **BISG** (noisy-G) | `+ {A_obs_ghat0, A_obs_ghat1}` | deployable: BISG-thresholded stratifier (ONE new line in `_eval_model`) |
| **Oracle** (grading) | `A_clean` | never an auditor; ground-truth reference |

Each cell reports `separates_kctl` AND `separates` (naive), side by side. **Sign-disagreement
between naive and k-control ⇒ NO RESULT for that cell** (the failed-control scar,
[[feedback_covariate_adjust_all_arm_correlates]]) — a hard stop, stated in the headline, not a
footnote.

## 6. Frozen grid

2 families × 4 information-sets × |gap|∈{0.10, 0.20} × ~20 seeds × n=8000.
**Negative-control anchor:** the clean world (no plant) must show no separation on ANY auditor; if
it does, the apparatus is broken and nothing downstream is interpretable — abort and debug.

## 7. Scope of claim (stated now, holds regardless of outcome)

Synthetic existence-grade, like everything in the program. A P2-yes says *there exists a
pure-disparity DGP where G-access separates and G-blindness does not* — it does NOT claim this is
how real lending discrimination is shaped (prevalence-in-wild unknown; hole H2/H3 of the
manifold). The result note carries this caveat in both the yes and no branches.

## 8. Discipline (binding, per lineage scar tissue)

1. **Pre-reg the §2 priors + per-cell PASS/FAIL BEFORE the PD construction code touches data**,
   OTS-stamped ([[feedback_anti_confirmation_procedure]]).
2. **Validity gate (§4) computed before the apparatus run**, per plant — a gate that can't fail the
   way the construct fails is not a gate ([[feedback_adversary_before_the_sentence]] lesson 2).
3. **Blind adversary dispatched against the CONSTRUCTION before any headline is written** — not
   after. The magnitude-control bisection is the load-bearing new mechanism and the exact degree of
   freedom the freeze closes; calibrating it post-hoc to make P2 appear is the failure mode.
4. Naive + k-control reported side by side; sign-disagreement = no result (§5).
