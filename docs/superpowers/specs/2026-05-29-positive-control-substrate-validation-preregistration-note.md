# Positive-control substrate validation — pre-registration

**Date:** 2026-05-29. **Status:** PRE-REGISTRATION. **Substrate:** `scripts/fairwash_frontier_dgp.py::generate_twin_world` + a NEW `world="P"` branch (positive-control), added without altering the existing A/B paths. **Companion to:** [[project_lda_shared_surface_result]] (the §5 test whose apparatus this validates). **Connects:** [[feedback_anti_confirmation_procedure]], [[feedback_covariate_adjust_all_arm_correlates]].

**What this is, in one line.** A positive control on the §5 apparatus (`scripts/lda_shared_surface_test.py`). §5 survived — the observable couldn't separate honest-correction (H) from laundering-by-suppression (L). C4 and V1≠V2 also concluded "the observable can't certify." Every result on this twin-world confirms the same direction. **At some point a string of confirmations on one synthetic DGP stops being evidence and becomes a property of the DGP.** This test asks: when a separable observable signal is *built in by construction*, does the apparatus DETECT it — or is it blind even then (substrate self-confirming)?

**The thing being controlled against.** In World A, the disparate term (`_TWIN_DISP * Gz`) and the c_fresh proxy channel are the SAME signal: c_fresh predicts Y *because* it proxies the G-term that is *in* Y. So dropping c_fresh (H) costs real Y-accuracy, which is exactly why H and L look alike on the observable — the §5 result rides on that entanglement. If that entanglement is a *necessary* feature of the substrate, §5's survival is earned. If the apparatus would report "can't separate" even on a world where the entanglement is BROKEN by construction, the survival is an artifact.

## 1. Question

Construct `world="P"`: the disparity is split into a **pure-impact** component (carried by c_fresh, drives the gap, contributes ~nothing to Y's legitimate predictability) and the legit features carry Y's predictable signal. By construction, on world P: H (drop c_fresh) sheds the gap WITHOUT shedding Y-accuracy; L (suppress legit) sheds the gap ONLY by destroying Y-predictive signal. So `A_obs(H) − A_obs(L)` SHOULD be positive and CI-clean.

**If the apparatus detects separation on world P (PASS)** → it is not blind; §5's null on World A is a real property of World A, not an apparatus defect. The §5/C4/V1≠V2 "can't certify" conclusions stand.

**If the apparatus reports no separation on world P (FAIL)** → it is blind even to a planted, by-construction observable signal. Then §5's survival (and the sibling results) must be re-read as possible substrate/apparatus artifacts, and the whole synthetic program needs a validity audit before HMDA-C1 ports it onto real-data credibility.

## 2. Operational definitions

- **2a. The `world="P"` DGP edit (one knob `decouple ∈ [0,1]`).** Same `_twin_base` (x0..x7, latent G, g_latent) and same `_cfresh_coupled` as World A — inputs bit-identical given seed. The ONLY change is how Y is generated:
  - World A: `pA = sigmoid(legit_logit + _TWIN_DISP·Gz)`.
  - World P: `pP = sigmoid(legit_logit + _TWIN_DISP·Gz_carried)`, where the disparate term is routed so that a fraction `decouple` of it acts through a c_fresh-borne channel that is conditionally independent of the legit outcome, and `(1−decouple)` through the original Gz channel. At `decouple=0`, world P ≡ World A (negative control, by construction). At `decouple=1`, the disparity is fully carried by a channel orthogonal to Y's legitimate predictability.
  - **Implementation pin (frozen):** the pure-impact channel is injected as a c_fresh-routed logit shift on the DECISION boundary that moves the gap but is residualized against `legit_logit` so it adds ~0 legit predictive content. Exact formula frozen in the `world="P"` branch at code-freeze; the generator's `__main__` structural check verifies (i) gap(P) ≈ gap(A) at decouple=0 and (ii) AUC(Y_P ~ legit) is ~flat in `decouple` while AUC(Y_P ~ c_fresh) falls — i.e. the planted signal is in the intended channel.
  - `Y_clean` unchanged (legit_logit only). A/B branches UNTOUCHED — all prior results reproduce bit-identically (verified post-freeze by re-running one §5 cell on world A and diffing).
- **2b. Apparatus.** `scripts/lda_shared_surface_test.py` UNCHANGED in its discriminator logic. Add a `--world {A,P}` switch routing `generate_twin_world(..., world=...)`. Same H/L arm families, same covariate-adjusted `is_L` coefficient WITH the feature-count control (`coef_is_L_kctl` — the honest one from [[feedback_covariate_adjust_all_arm_correlates]]; the naive coefficient is NOT the test statistic).
- **2c. Signal-strength sweep.** `decouple ∈ {0.0, 0.25, 0.50, 0.75, 1.0}`. `decouple=0.0` is the negative control (≡ World A). proxy_strength fixed at 0.70 (the regime where §5's H/L families had common support; 0.85 had the thin-support pathology and is reported as secondary only). 20 seeds, n=8000.
- **2d. Test statistic.** Per `decouple`: the feature-count-controlled `A_obs` `is_L` coefficient (`coef_is_L_kctl`) and its seed-cluster bootstrap CI. "Detects" = CI excludes 0 AND sign is NEGATIVE (L less accurate than H — the planted direction) AND |coef| ≥ 0.01.

## 3. Pre-registered predictions

**P1 — NEGATIVE CONTROL holds.** At `decouple=0.0` (world P ≡ World A), the apparatus reports NO separation (k-controlled `is_L` CI includes 0 or |coef|<0.01, OR sign-unstable as in the §5 result). **Prior: 0.85.** This must hold or world P at decouple=0 isn't actually reproducing World A (construction bug; halt and fix). It re-confirms the §5 null as the floor.

**P2 — POSITIVE CONTROL passes at full strength.** At `decouple=1.0`, the apparatus DETECTS separation: k-controlled `is_L` coefficient negative, CI-excludes-0, |coef| ≥ 0.01. **Prior: 0.80.** *Load-bearing: this is the validation.* If P2 HITS, the apparatus is not blind — §5's survival is earned. If P2 MISSES, the apparatus is blind to a by-construction signal and the synthetic program needs a validity audit.
  - **MISS interpretation:** the apparatus cannot see a planted observable separation. Either (a) the H/L family + covariate-adjustment machinery destroys real signal along with the feature-count confound (over-correction — I controlled away the baby), or (b) the discrete feature-drop lever can't construct an H that exploits the decoupled channel. Both are apparatus defects that retro-contaminate the §5 reading. This is the FAIL that costs a month; I want it found here.

**P3 — DETECTION FLOOR is interior.** There exists a `decouple* ∈ (0,1]` below which the apparatus does NOT detect and at/above which it does — i.e. detection is graded, not all-or-nothing, and the floor is not at the extreme. **Prior: 0.55.** Tells us HOW sensitive the apparatus is (the "single point can't distinguish fine-from-only-catches-large" concern, answered). Bet the SHAPE (a monotone detection curve in `decouple`), not the point ([[project_pre_registration_pattern]]).
  - **MISS (floor at 0, detects everything ≥ tiny):** apparatus is hypersensitive — then the §5 null is *strong* evidence (it stayed blind despite a sensitive detector). **MISS (floor at 1, detects only full decoupling):** apparatus is coarse — the §5 null is *weak* evidence (a real-but-partial signal would've been missed). Either extreme is informative about how much to trust §5.

**Most likely overall miss.** P3's floor sits at 1.0 (detects only full decoupling) — meaning the apparatus is coarse and the §5 null should be downgraded from "the observable can't separate" to "the observable can't separate signals below a large threshold." That would be a real, publishable caveat on §5, not a refutation.

## 4. Sensitivity / robustness (reported, not gating)

- proxy_strength 0.70 primary; 0.85 reported (expect thin-support noise, per §5).
- The structural checks in the generator `__main__` (gap(P,decouple=0)≈gap(A); AUC-channel-routing) are validity gates on the CONSTRUCTION, reported before any apparatus result is read.
- Naive (non-k-controlled) `is_L` reported beside k-controlled as a contrast — if naive detects but k-controlled doesn't at decouple=1, that's the over-correction failure mode (P2 MISS branch a) made visible.

## 5. Scope / exclusions

- This validates the §5 apparatus's SENSITIVITY (can it see a planted observable signal). It does NOT re-test §5 or claim anything new about lending.
- NOT a test of whether real-data lending has decoupled vs entangled disparity — that's unobservable (no Y_clean off-substrate), the whole point.
- A PASS does not prove the substrate is artifact-free in every dimension — only that it is not blind to THIS class of planted observable signal. Other self-confirmation modes are out of scope (named, not swept).

## 6. Implementation

`world="P"` branch in `fairwash_frontier_dgp.py` (additive, A/B untouched); `--world` switch + `decouple` plumbing in `lda_shared_surface_test.py`. Reuse all discriminator/aggregate code verbatim. One JSON, one result note. Unit test: (i) world P at decouple=0 reproduces World A gap within seed noise; (ii) AUC(Y_P ~ legit) flat in decouple, AUC(Y_P ~ c_fresh) falls — the planted-signal-is-in-the-intended-channel invariant. Without (ii), a PASS is uninterpretable (could be detecting the wrong thing).

## 7. Blind-adversary brief (hire BEFORE writing the verdict)

Charge: (1) confirm world P at decouple=0 truly reproduces World A (else negative control is fake). (2) Confirm the planted signal at decouple=1 is genuinely in the OBSERVABLE channel and not leaking Y_clean/G into the apparatus. (3) Steelman: if P2 passes, is the detection an artifact of the feature-count machinery rather than real signal sensitivity? (4) If P2 fails, is it a true apparatus blindness or a construction bug in world P? The adversary's verdict is recorded before the headline.

---
**Pre-reg author:** Claude Opus 4.8 (researcher), governance lineage. **Date:** 2026-05-29. **OTS:** auto-applied by post-commit hook on freeze.
