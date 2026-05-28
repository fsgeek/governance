# The LDA / fairwash shared-failure-surface — RESULT

**Status:** RESULT. Pre-reg FROZEN at `c815c61` / OTS `ae0d827`. Predictions immutable; scored as-is.
**Date:** 2026-05-28. **Data:** `runs/lda_shared_surface_2026-05-28.json` (20 seeds × ps∈{0.70,0.85}, n=8000, 200 models/ps).
**Tests:** spine §5 (`working_notes/2026-05-26-impossibility-regime-claim-spine.md`) — does an auditor-OBSERVABLE metric separate honest proxy-removal (H) from laundering-by-suppression (L) at matched disparate-impact?

## Headline (one line)

**§5 SURVIVES, sharpened.** The conversation-minted §5 claim ("the LDA remedy and the fairwash attack share a failure surface — the metric cannot tell honest correction from laundering apart") holds on the twin-world. The would-be observable discriminator (held-out accuracy on `Y`) **does not honestly separate H from L** once the feature-count confound is removed — and at high proxy_strength it actively **misleads** (the honest move pays the *larger* observable accuracy tax). The separation lives entirely in the oracle `Y_clean` the auditor cannot see. I went in hunting to slaughter §5 and the data, after a blind-adversary catch, refused me.

## P-scorecard

| Pred. | Prior | Verdict | Headline |
|---|---|---|---|
| P1 (A_clean separates — oracle sanity) | 0.90 | **HIT** | oracle separates (−0.095/−0.030); the ONLY clean separator |
| **P2 (A_obs FAILS to separate — §5 survives)** | 0.62 | **HIT** | genuine observable signal ≈0 / sign-unstable once feature-count controlled |
| P3 (L's obs-accuracy tax ≥ H's, sign) | 0.70 | **informative MISS** | sign INVERTS at high ps: H (honest) costs MORE — the pre-reg's "most likely miss" |
| P4 (separability monotone in τ) | 0.55 | **directional HIT** (re-read on ps axis) | oracle-separability scales with proxy dominance; observable stays blind |
| P5 (CAL adds nothing beyond A_obs) | 0.60 | **HIT** | CAL carries the same feature-count confound; no real observable rescue |

**Net: 3 HIT (P1,P2,P5) / 1 directional HIT (P4) / 1 informative MISS (P3).** A calibrated scorecard — and the informative MISS (P3) is the sharpest single finding.

## ⚠ The blind-adversary catch (recorded BEFORE this headline was written — [[feedback_anti_confirmation_procedure]])

A blind adversary (agent `a5b90d01`, given the JSON + script + pre-reg, blind to my preferred outcome, charged to BREAK the result) was dispatched against my **first** reading. My first reading was the OPPOSITE of the headline above: I read the committed OLS (`is_L` coef −0.059/−0.021, all CIs excluding 0) as **"§5 OVERCLAIMED — the observable separates them."** The adversary killed that reading on two counts, both of which I then verified independently (receipts below):

1. **Feature-count confound (fatal).** My arms span the gap range by dropping *different numbers* of features; L drops more (`corr(is_L, k) = +0.31`). My OLS adjusted for `abs_gap` but not `k`. Adding `k` collapses the effect: A_obs `is_L` goes **−0.059 → −0.019** (ps=0.70) and **−0.021 → +0.011, sign-flip** (ps=0.85). An auditor sees a model's *predictions*, not how many features its builder dropped — so feature-count is **not an observable discriminator** in the sense that matters. The committed coefficient was bookkeeping, not signal-quality detection.
2. **Mechanism runs backwards from P3 (the real finding).** The intended single-intervention comparison: H (drop the proxy channel) vs L (suppress the top legit feature x0). At ps=0.85: **H → A_obs 0.704 at |gap| 0.169; L → A_obs 0.747 at |gap| 0.415.** The *honest* move costs MORE observable accuracy and reaches a LOWER gap. The proxy channel is *more* Y-predictive than the top legit feature at high proxy_strength, so removing it (honest) hurts observable accuracy more than suppressing legit signal (laundering). Read straight, this *supports* §5, not refutes it.

**Adversary verdict: REAL-BUT-NARROWER, tipping toward §5-survives.** I concede fully; my first frame was a confounded-regression artifact and I nearly committed it. The discipline worked exactly as designed: the satisfying frame ("I slaughtered the previous instance's confabulation") was the one that died.

## Receipts (my own re-verification of the adversary's claims)

```
ps=0.70: is_L(~abs_gap)=-0.0593  is_L(+k)=-0.0185  corr(isL,k)=+0.310
ps=0.85: is_L(~abs_gap)=-0.0213  is_L(+k)=+0.0106  corr(isL,k)=+0.310
ps=0.85 intended H-vs-L: H(drop cfresh) A_obs=0.704 |gap|=0.169  vs  L(drop x0) A_obs=0.747 |gap|=0.415
```

## What the result actually says (the corrected, surviving claim)

On the twin-world, an auditor restricted to observables `O = {x0..x7, c_fresh, Y, Ghat_bisg}`:

1. **Cannot separate honest correction from laundering-by-suppression by held-out accuracy on `Y`.** The genuine observable signal (feature-count-controlled) is ≈0 at ps=0.70 and sign-unstable at ps=0.85. §5's "the metric cannot tell them apart" **holds** — and not just the DP-gap metric §5 named, but the thicker (gap + accuracy) metric I proposed as the escape. The escape fails.
2. **The distinction is real but lives in `Y_clean`.** A_clean (oracle) separates cleanly and most strongly (P1 HIT), and its separability scales with proxy dominance (P4). The honest-vs-laundering distinction *exists* — it is just **certification-inaccessible** (spine §3: G-observation escapes measurement, not certification). This is the impossibility, now with an empirical floor on *this specific escape attempt*.
3. **At high proxy_strength the observable actively misleads** (P3 informative MISS). When the proxy channel becomes more Y-predictive than legitimate features, the honest correction pays the *larger* observable accuracy tax — so an auditor naively using held-out accuracy as a "is this honest?" signal would rank the honest model as *more* suspicious. Worse than blind: inverted.

**§5's framing upgrade earned by this result:** §5 said the LDA remedy and the fairwash attack "share a failure surface." The sharper, now-empirically-anchored statement: **the observable accuracy signature an auditor would reach for as a tie-breaker is not merely uninformative between honest and laundering — at the proxy strengths where laundering is most tempting, it points the wrong way.** The remedy's blindness is structural (C3), not a thin-metric artifact fixable by adding accuracy to the dashboard.

## Two regimes (the heterogeneity — `project_pre_registration_pattern`)

The pre-reg assumed proxy_strength-uniformity; the substrate is heterogeneous, as the pre-reg's "most likely overall miss" anticipated:
- **ps=0.70:** H and L families overlap in |gap| (common support ~[0.20,0.27]); the comparison is interpolation. Feature-count-controlled observable signal ≈ −0.019 (weak, mechanism-uninteresting).
- **ps=0.85:** L cannot lower its gap below ~0.36 (proxy dominates); H/L gap support is ~75% disjoint. The committed OLS's `is_L` there was largely **extrapolation across a void** — my own `selftest` prints "NONE (extrapolation!)" for exactly this and I failed to gate on it. The honest reading at ps=0.85 is the inverted-mechanism one (P3), not the OLS coefficient.

## Pre-reg corrections (mechanism only — predictions/priors NOT edited)

1. **Lever: smooth-λ → discrete feature-drop.** The pre-reg §2c scalar-λ lever is a GBT scale-invariance no-op (lesson already in `compliant_practice_test.py:461`, which I walked past). Replaced with discrete feature-drop = the literal LDA model-selection move.
2. **Exact matched-pairs → covariate-adjustment on |gap|.** Discrete drop is too COARSE to hit a target gap within tolerance ({x0,x1} "match" was n=4000 noise; at n=8000 err=0.029). Replaced matched-τ with OLS adjustment. **This deviation is what introduced the feature-count confound** — covariate-adjustment must control for *all* arm-correlated covariates, not just the one named in the pre-reg. Lesson logged below.
3. **τ-grid → ps-axis for P4.** H is a fixed move; τ collapsed; P4 re-read on the proxy_strength axis (the pre-reg's own §4 robustness arm).

## Lessons (operational)

- **A covariate-adjusted "matched" comparison must audit for ALL arm-correlated covariates.** I adjusted for `abs_gap` (the named confound) and missed feature-count (the unnamed one). The blind adversary's item 3 is now a standing check: when matching is replaced by regression, enumerate what *else* differs between arms.
- **Read your own instrument's dials.** The `selftest` was built to flag the ps=0.85 extrapolation and I didn't run it against the committed grid before reading coefficients.
- **The anti-confirmation procedure paid for itself.** The frame that died was the one I wanted (the slaughter). Prior on P2 (0.62) was correctly placed *toward* §5-survival; I overrode my own calibrated prior with a confounded regression and the adversary put it back.

## Scope of claim

- Synthetic twin-world only. The *direction* of the result (observable cannot separate; oracle can; observable inverts at high proxy dominance) is what transfers as a hypothesis; magnitudes are substrate-specific.
- Tests only §5(b) (metric-vs-mechanism / C3 blade). §5(a) (search-incompleteness, inductive-unprovability) is formal, untested here.
- Does NOT establish that NO observable separates H from L — only that the two an auditor would reach for first (held-out accuracy, calibration) fail, and one inverts. A cleverer observable is not ruled out; the burden is now on anyone claiming one exists.
- The real-data analogue cannot be run (no `Y_clean` off-substrate) — which is precisely the point (spine §3).

## Followups (both terminal, not gateways)

- **If pursuing §5 further:** the inverted-mechanism finding (P3) is the publishable core — "the auditor's natural tie-breaker points the wrong way at high proxy dominance." Worth a clean single-intervention figure (H-drop-proxy vs L-suppress-x0 across the ps grid) without the family/OLS apparatus that introduced the confound.
- **If banking §5:** it feeds the method paper's "why the obvious remedy doesn't close it" section as originally routed, now empirically anchored rather than asserted.

---
**Author:** Claude Opus 4.8 (researcher), governance lineage. **Date:** 2026-05-28. **OTS:** auto on freeze.
