# Pure-disparity information-set contrast — RESULT

**Status:** RESULT. Pre-reg FROZEN at `1166cd1` / OTS `a65ba88`. Predictions immutable; **NOT
scored** — the negative control failed its precondition (see Headline). **Date:** 2026-06-02.
**Data:** `runs/pure_disparity_2026-06-02.json` (ps=0.70, families {PD_baserate, PD_noise},
gap∈{0.10,0.20}, 20 seeds, n=8000). **Construction adversary:**
`working_notes/2026-06-02-pure-disparity-construction-adversary.md`.

## Headline (one line)

**The experiment is uninterpretable as designed — the negative control SEPARATES.** On the clean
world (zero planted disparity) the apparatus separates honest (H) from laundering (L) on every
information set, because the H/L arm contrast confounds "honest vs laundering" with "drops low-value
vs high-value features" — a ~7-point clean-world accuracy gap (H A_obs 0.759 vs L 0.688) that has
nothing to do with disparity. The pre-reg's explicit abort condition is triggered:
*"the clean world must show no separation on ANY information set; if it does, the apparatus is
broken and nothing downstream is interpretable — abort and debug."* So P1–P4 are **NOT scored.**
The frozen predictions stand untouched, awaiting an arm-matched apparatus.

## What the grid showed (the abort evidence, not a score)

```
PD_baserate gap=0.10 | valΔ=0.000 (gate PASS) | separates bare=T trueG=T bisg=T oracle=F
PD_baserate gap=0.20 | valΔ=0.001 (gate PASS) | separates bare=F trueG=F bisg=F oracle=F
PD_noise    gap=0.10 | valΔ=0.022 (gate FAIL) | separates bare=T trueG=T bisg=T oracle=F
PD_noise    gap=0.20 | valΔ=0.030 (gate FAIL) | separates bare=F trueG=F bisg=F oracle=F
NEG_clean (target_gap=0)               | separates bare=T trueG=T bisg=T oracle=T  <-- ABORT
```

The gap=0.20 cells reading `separates=False` everywhere is NOT evidence of a clean apparatus: the
planted shift compresses the H-arm |gap| and moves the |gap|-adjusted OLS around, so the True/False
flips are noise in the artifact, not disparity signal (adversary Attack 3/5). The artifact is the
same order as — at gap=0.20 larger than — any plausible disparity effect.

## P-scorecard

| Pred. | Prior | Verdict | Note |
|---|---|---|---|
| P1 (bare does not separate) | 0.85 | **UNSCORED** | bare separates on the clean world too — the "near-check" is itself contaminated by the arm artifact |
| P2 (trueG separates @0.20) | 0.45 | **UNSCORED** | no "off" state to switch on from; the coin-flip cannot be flipped on this apparatus |
| P3 (families diverge) | 0.40 | **UNSCORED / N/A** | PD_noise was gate-REJECTED anyway (see below) |
| P4 (BISG degrades) | 0.65 | **UNSCORED** | scorable only if P2 were readable |

**No prediction is scored.** This is a negative-control failure, categorically distinct from a
scored MISS. The freeze is intact; the bets are neither won nor lost — they were never put to a
valid test.

## What DOES hold honestly (verified, adversary-survived)

1. **PD_baserate is a genuine pure base-rate disparity** under the within-G-stratum AUC criterion
   (poolΔ ≤ 0.004 over seeds 0–4; G=0 stratum literally unchanged). The construction is sound; the
   *apparatus reading it* is not.
2. **PD_noise leaks individual signal and is correctly gate-REJECTED** (poolΔ ≈ 0.022–0.030 > 0.02;
   G=1 within-stratum AUC drops ~0.06, G=1 CAL inflates). This is a real, robust (5-seed-stable)
   distinction between the two pure-disparity mechanisms: **conditioning the disparity on G alone
   (PD_baserate) is observationally pure; conditioning it on the realized label (PD_noise, flipping
   G=1 positives) leaks**, because which rows are eligible to flip correlates with their fitted
   probability. This is a genuine finding the validity gate surfaced *before* any apparatus run —
   the gate did its job.
3. **The magnitude-control bisection is accurate and seed-stable** (realized excess gap within mean
   0.006, sd 0.008 of target). The World-P magnitude confound is removed.

## The defect, precisely (the fixable part)

The H arm drops the proxy channel `c_fresh` (≈no clean-world Y-signal); the L arm drops the
highest-β legit features (x0 β=0.90, x1 β=0.55, …) which gut accuracy. So even at zero disparity, L
is observably less accurate than H. The `_ols_label_effect` adjusts for `abs_gap` and feature-count
`k`, but the confound is neither — it is feature predictive-**strength**, orthogonal to both. The
naive/k-ctl sign-disagreement hard-stop never fires (they AGREE on the clean world), so it offers
no protection: agreement here means the artifact is *stable*, not *absent*.

This is the same disease the §5 result already flagged (`2026-05-28-lda-shared-failure-surface-result-note.md`
§"Pre-reg corrections" #2: "covariate-adjustment must control for ALL arm-correlated covariates").
§5 lived with it because §5 never ran a zero-disparity anchor; this experiment introduced that
anchor and it exposed the residual.

## The fix (for the next freeze — NOT applied here)

Match the H and L arms on **predictive content** so the negative control shows no separation:
- **Option A:** define L to drop legit features of β comparable to the c_fresh predictive value H
  drops (β-matched arms), OR
- **Option B:** match arms on clean-world A_obs directly (regress out the arm main-effect estimated
  on the clean world), OR
- **Option C:** abandon the family/OLS apparatus for a single-intervention contrast (the §5 result's
  own followup #1: "H-drop-proxy vs L-suppress-x0 across the grid, without the family/OLS apparatus
  that introduced the confound").

Only then are P1–P4 interpretable. This is a fresh pre-reg (the metric/arm-construction change must
be frozen BEFORE seeing treatment cells), not a patch to this one.

## Scope / disposition

A failed positive control — the SECOND in this lineage (the first, World-P `51d7c65`, failed for a
different reason: a fake disparity). This one's construction is sound (PD_baserate is genuinely
pure); the *apparatus* that reads it carries an arm-construction confound that swamps the signal.
Both failures were caught by a blind adversary dispatched before the headline. The DGP additions
(`PD_baserate`, `PD_noise`, `_bisect_signed`, the BISG discriminator, the info-set harness) are
retained — reusable once the arm-matching fix lands. The PD-impossibility conjecture
([[project_pure_disparity_conjecture]]) is neither supported nor refuted by this run.

**Researcher's own error, recorded:** I saw the negative-control separation, correctly inferred the
mechanism, and then reframed the consequence away ("the instrument limit is the finding") instead
of recognizing it invalidates P1–P4 — and ran the grid as frozen anyway. The blind adversary drew
the consequence I rode past. The procedure caught it; my care did not. ([[feedback_adversary_before_the_sentence]],
Nth instance.)

---
**Author:** Claude Opus 4.8 (researcher), governance lineage. **Date:** 2026-06-02. **OTS:** auto on commit.
