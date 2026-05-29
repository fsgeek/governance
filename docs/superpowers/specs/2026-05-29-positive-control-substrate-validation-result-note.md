# Positive-control substrate validation — RESULT

**Status:** RESULT. Pre-reg FROZEN at `a0dfd23` / OTS `c0d40fb`. Predictions immutable; scored as-is.
**Date:** 2026-05-29. **Data:** `runs/positive_control_2026-05-29.json` (ps=0.70, decouple∈{0,.25,.5,.75,1}, 20 seeds, n=8000).
**Validates (attempted):** the §5 apparatus ([[project_lda_shared_surface_result]]) — is it blind, or does it detect a planted observable signal?

## Headline (one line)

**The positive control FAILED — and the failure is MINE, not the apparatus's. I built the wrong world.** The planted "pure-impact" channel is not a disparity carrier; it is a strong individual-level legitimate-looking predictor of `Y`, "illegitimate" only by the fiat of how I defined `Y_clean`. So the test reduced to a tautology ("the arm that keeps the better `Y`-predictor predicts `Y` better"), and its headline sign was additionally a feature-count-control artifact. **The substrate-validity question — is the §5 apparatus blind to a planted disparity signal? — REMAINS OPEN.** No conclusion about §5 is licensed by this run.

## P-scorecard

| Pred. | Prior | Verdict | Headline |
|---|---|---|---|
| P1 (negative control decouple=0 does NOT detect) | 0.85 | **MISS (threshold)** | decouple=0 k-ctl=−0.020 clears the 0.01 "detect" bar — my threshold mischaracterized §5's own small-but-CI-clean coefficient |
| **P2 (decouple=1 DETECTS, neg is_L)** | 0.80 | **MISS** | sign is POSITIVE (+0.038) and it tests a tautology, not the planted-disparity claim |
| P3 (detection floor interior) | 0.55 | **N/A** | the curve is real & monotone but measures the wrong construct |

## ⚠ Blind-adversary catch (recorded BEFORE this headline — [[feedback_anti_confirmation_procedure]])

I dispatched a blind adversary (agent `ae964622`) against my FIRST reading. My first reading — written in the turn I got the numbers — was: *"better than a PASS: the apparatus is live (not dead), and the positive is_L (+0.038) is a dose-response confirmation of the §5 inversion — the observable rewards laundering, increasingly with decoupling."* **That was me narrating a backwards construction as a richer finding — the exact failure mode I had named as the risk one turn earlier and walked into anyway.** Verdict: **PLANT-BACKWARDS-ARTIFACT.**

Three findings, all verified by me independently (receipts below):
1. **The plant is a tautology.** The pre-reg claimed the c_fresh-routed channel "carries the disparity but NOT legitimate predictive signal." False against the observable `Y` the apparatus sees: I injected `_TWIN_DISP·imp_z` directly into the observable logit, making c_fresh the *dominant individual-level predictor* of `Y`. The arms then reduce to "H drops the best `Y`-predictor; L keeps it" — so L wins A_obs by construction. The pre-reg's own validity gate ("AUC(Y~c_fresh) rises") is the *same fact* as the "finding" ("L beats H"), stated twice.
2. **The deciding check (within-G-stratum AUC).** A genuine group-level disparity collapses to ≈0.50 within a G stratum. My channel stays high. **Verified:** within-G AUC(Y~c_fresh) = **0.503** at decouple=0 (World A — correct, pure disparity), rising to **0.809** at decouple=1 (individual-level signal, not disparity). Only 6% of `imp_z`'s variance is G-explained; 94% is non-G.
3. **The positive sign is a k-control artifact.** Naive A_obs is_L at decouple=1 is **−0.007** (negative); the headline **+0.038** appears only under the feature-count control, via the same `corr(is_L,k)=+0.31` confound the apparatus warns about in its own comments ([[feedback_covariate_adjust_all_arm_correlates]], unlearned twice now). Common-support trim shrinks it ~60% (to +0.014).

## Receipts (my own verification)

```
within-G-stratum AUC(Y~c_fresh):  decouple 0.00 -> 0.503  |  0.50 -> 0.680  |  1.00 -> 0.809
(a true disparity stays ~0.50 within stratum; mine climbs -> individual predictor, not disparity)

A_obs is_L @ decouple=1:  naive = -0.007  |  +k control = +0.038  |  +k, common-support-trim = +0.014
oracle A_clean is_L stays negative throughout (-0.036 -> -0.046) -- the plant DID corrupt Y_clean-accuracy,
but via a channel that is individually Y-predictive, so the observable rewards keeping it.
```

## What this DOES and does NOT establish

- **Does NOT establish** the apparatus is sound (I cannot claim "§5 earned" — the control didn't test the claimed construct).
- **Does NOT establish** the apparatus is blind either — it responded strongly and monotonically; it just responded to a tautological signal.
- **Does establish** one real, narrow thing: the §5 apparatus's covariate-adjusted statistic is **not robust to the feature-count confound even after the supposed k-control** — at decouple=1 the naive and k-controlled coefficients have *opposite signs*. The k-control over-extrapolates (both arms identical at k=0; it credits the slow-degrading arm). This retro-sharpens the §5 caveat: the k-controlled coefficient is not a clean estimator on this family construction. [[project_lda_shared_surface_result]]'s ps=0.70 k-ctl (−0.019) should be read with this fragility in mind, though §5's qualitative conclusion (observable doesn't cleanly separate) is unthreatened — if anything reinforced.

## The substrate-validity question is still open (what a CORRECT positive control needs)

To actually test apparatus sensitivity, the planted signal must be a **group-mediated disparity that is genuinely observable-separable from honest correction** — i.e. within-G-stratum AUC(Y~c_fresh) must stay ≈0.50 (it IS pure disparity) while the *honest* and *laundering* arms produce different observable signatures for a reason other than "one kept the better individual predictor." That is a materially harder construction than what I froze, and on reflection it may be **impossible by design** on this substrate — which would itself be the answer (if you cannot build an observable-separable pure-disparity signal, that is *why* §5 survives, structurally). That is the next pre-reg, not a patch to this one.

## Lessons (operational)

- **Compute the construct-validity check BEFORE reading the outcome.** Within-G-stratum AUC would have shown the plant was individual-signal in 30 seconds, before any apparatus run. I checked the channel-routing invariant (legit-AUC flat, c_fresh-AUC rises) but that invariant is *consistent with the tautology* — it does not distinguish disparity from predictor. A validity gate that can't fail the way the construct fails is not a gate.
- **The feature-count confound bit me a SECOND time** ([[feedback_covariate_adjust_all_arm_correlates]]) — I let the k-controlled coefficient be the headline without checking the naive coefficient agreed in sign. The rule needs teeth: report naive and k-ctl side by side in the *headline*, and if they disagree in sign, neither is the result.
- **I narrated the surprise as a finding in the same turn I saw it** — precisely [[feedback_first_contact_frames]]. The anti-confirmation procedure ([[feedback_anti_confirmation_procedure]]) was the only thing between that narration and a committed false result. Third instance this lineage; the procedure earns its cost every time.

## Scope of claim

A failed positive control, honestly logged. It validates nothing about §5 and refutes nothing about §5. Its only positive contribution is the k-control-fragility note above and a sharpened spec for the *next* attempt. The DGP `world="P"` branch is retained (the construction is reusable once corrected); the result is the negative.

---
**Author:** Claude Opus 4.8 (researcher), governance lineage. **Date:** 2026-05-29. **OTS:** auto on freeze.
