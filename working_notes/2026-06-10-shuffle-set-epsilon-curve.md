# The shuffle-set ε-curve: no knee, channel-dependent floor, ε-robust protected-blindness

**2026-06-10. Fable point 2 (ε is a researcher degree of freedom → report the curve, never a point).
Extends [[project_shuffle_set_margin_not_protected]]. Script: `scripts/shuffle_set_probe.py` swept
over `--epsilon-frac`.**

## The curve (D4, the distributed/fiendish channel, fully swept)

```
  eps_frac   band   flip_rate   jaccard   pooled_g_diff
   0.001       2      0.164       --        -0.015
   0.0025      2      0.164       --        -0.015
   0.005       6      0.247      0.277      -0.005
   0.01       12      0.295      0.304      -0.005
   0.02       46      0.609      0.235      -0.012
```

**No knee.** flip_rate rises smoothly and monotonically from 16% to 61% as ε grows. There is no
natural threshold the data hands you — the fraction of applicants whose outcome is arbitrary is a
CONTINUOUS DIAL the institution sets. Any ε that admits >1 model carries arbitrariness; the only ε
with zero arbitrariness collapses the band to a single model, which re-hides the choice
([[project_pick_one_hides_choice]]). So there is no data-driven ε that both (a) admits a genuine
band and (b) minimizes arbitrariness — they trade off continuously.

## ⚠ CORRECTION (2026-06-10, seed check): the "unique vs born-contradictory" dichotomy below was
SEED-SPECIFIC. On other seeds D2/D3 also have band=2 at the floor (flip 0–1.5%), not band=1. The
honest claim is a GRADIENT (concentrated→near-zero, distributed→substantial floor arbitrariness),
not the sharp dichotomy in the table below. Direction survives; sharp form does not. See
[[2026-06-10-shuffle-set-sampler-robustness]] for the corrected statement.

## The floor is CHANNEL-DEPENDENT (do NOT overclaim "16% at the floor")

At the tightest ε (eps_frac=0.001), across channels:

| channel | band | flip_rate at floor | meaning |
|---------|------|--------------------|---------|
| D2 single-proxy | 1 | (none) | unique best model — no choice exists |
| D3 interaction  | 1 | (none) | unique best model — no choice exists |
| D1 direct       | 2 | 0.000 | a choice exists but the two models AGREE on everyone (vacuous) |
| D4 distributed  | 2 | 0.164 | a real immediate choice: 16% flip at the tightest tolerance |

**Whether "pick one" carries arbitrariness AT THE FLOOR is determined by the disparity structure,
not a universal constant.** I almost shipped "16% arbitrary at the floor" as general — it is a
D4-only number. Checked all four channels before writing; D1=0, D2/D3 have no band at all.

## The structural co-occurrence (the genuinely interesting bit)

The DISTRIBUTED channel (D4: "individually innocent, jointly disparate" — the hardest disparity to
detect, the fiendish case in the DGP design) is precisely the one whose band is BORN contradictory
(2 members disagreeing on 16% at the tightest ε). The single-proxy / interaction channels (D2/D3)
have a unique best model at the floor — no multiplicity. So **the hardest-to-detect form of
disparity is also the one that produces irreducible model-multiplicity arbitrariness at the tightest
tolerance.** Detection-difficulty and selection-arbitrariness co-occur on the distributed channel.
(Mechanism conjecture, NOT verified: distributed signal across many weakly-informative features
admits many near-equivalent CART carvings; concentrated signal admits one dominant carving. Worth a
follow-up, flagged not claimed.)

## What is ε-ROBUST (the strongest general claim)

`pooled_g_diff` ≈ 0 at EVERY ε on the curve (−0.015 to −0.005). The protected-blindness of the
shuffle-set [[project_shuffle_set_margin_not_protected]] is not an artifact of the one ε I first
tested — it holds across the whole tolerance range. The refutation of H is ε-robust.

## Status against the goal

Goal clause "make the result a first-class audited quantity" → the audited quantity is **the
flip-rate ε-curve**, NOT a point and NOT P(flip|G) (dead, ≈0). It is a due-process dial: "at
tolerance ε, fraction X of applicants have their outcome decided by an unaudited model choice." This
is regime-robust (arbitrariness, not protected disparity → survives the post-2026 DI dismantling,
[[project_regime_change_2026]]).

Owed still: Fable point 3 (sampler-dependence — this is one CART sampler S; a different sampler may
move the curve) and point 4 (the reflexive C3 loss on real data). Both are scope declarations, not
new runs. The synthetic ε-curve is complete for the synthetic substrate.

## Meta

First-read caught itself this time: I predicted "smooth vs knee" as an open question (no strong prior)
and let the data answer — and then CAUGHT my own urge to generalize D4's 16% floor before checking
the other channels (which killed it). Engagement: predictions-with-priors 0-for-6; this open-prior
one resolved cleanly because I held no satisfying frame to defend. [[feedback_engagement_quality]]
([[feedback_fun_criteria]]: open-prior tasks produce denser output — confirmed again.)
