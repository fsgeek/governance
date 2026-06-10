# The reflexive C3 loss bites BLINDNESS only through DIFFERENTIAL proxy error

**2026-06-10. Interrogates Fable point 4 (the reflexive measurement loss) instead of just banking it.
Script: `scripts/proxy_attenuation_probe.py`. Output: `runs/proxy_attenuation_probe.json`.
Composes with — and NARROWS — [[project_shuffle_set_margin_not_protected]].**

## Fable's point 4 (as banked)

Real FM/LC data has no protected attribute, so "protected-correlated" must be CONSTRUCTED (BISG /
HMDA proxy). The apparatus that measures whether the shuffle-set is protected-concentrated uses the
protected-inference it audits → "the apparatus stands on the floor; declare it a loss." Fable called
it the paper's most honest paragraph. Correct that it's a loss — but the DIRECTION matters, and the
general framing is too strong for THIS result.

## The direction the loss actually runs (measurement-error theory + demonstration)

My finding is BLINDNESS (pooled_g_diff ≈ 0), not a disparity claim. Classical result:
NON-DIFFERENTIAL error in a binary regressor ATTENUATES its estimated effect toward zero. So the
proxy loss runs in OPPOSITE directions for the two claim types:

- **Claiming DISPARITY through a proxy → FATAL.** Demonstrated: true g_diff=0.155 attenuates to
  0.018 as non-diff proxy noise q→0.4 (88% shrink). A real gap is hidden by proxy noise.
- **Claiming BLINDNESS through a non-diff proxy → SAFE.** Demonstrated: true g_diff≈0 stays in
  [−0.003,+0.005] at EVERY noise level q∈{0,…,0.4}. Non-differential error **cannot manufacture** a
  spurious disparity from a true zero — it can only shrink toward the zero that's already there.

```
  true disparity 0.155  --nondiff proxy q-->  [0.155, 0.131, 0.116, 0.082, 0.055, 0.018]
  true blindness 0.000  --nondiff proxy q-->  [-0.003,-0.000,-0.003,-0.001,-0.003,+0.005]
```

## The ONE regime that threatens blindness: DIFFERENTIAL error

The blindness finding is corrupted only if proxy accuracy DEPENDS on flip status (differential
error). Demonstrated on the true-zero case:

```
  q_noflip=0.1 q_flip=0.1  -> measured g_diff -0.005   (symmetric: stays ~0)
  q_noflip=0.1 q_flip=0.3  -> measured g_diff +0.071   (manufactured FROM a true zero)
  q_noflip=0.1 q_flip=0.4  -> measured g_diff +0.109
  q_noflip=0.4 q_flip=0.1  -> measured g_diff -0.111
```

So differential proxy error — and ONLY differential — can fabricate a ±0.11 g_diff out of nothing.

## The honest, NARROWED scope (the contribution)

NOT "the apparatus stands on the floor, declare a loss." Instead, precisely:

> The protected-blindness of the shuffle-set is ROBUST to non-differential proxy error (the dominant,
> well-characterised BISG error mode) and threatened ONLY by proxy error that is DIFFERENTIAL in flip
> status — i.e., only if BISG/HMDA accuracy systematically differs for borrowers near vs far from the
> lender's model-disagreement boundary. That is a specific, checkable, bounded condition. There is no
> obvious mechanism for it: BISG error is driven by surname/geography, which have no evident reason to
> correlate with a particular lender's between-model disagreement boundary. The burden it imposes is
> "show your proxy's error is not differential in flip status," not "abandon the claim."

This converts Fable's hand-waved reflexive-impossibility into a measurement-error analysis with a
NAMED, FALSIFIABLE failure condition. It does NOT dissolve the loss (differential error is a real
threat and BISG error CAN be differential in protected status itself, which interacts) — it LOCATES
it. Most honest paragraph AND most precise.

## Caveats on this rebuttal (do not over-rebut)

- BISG error is known to be differential in TRUE RACE (worse for some groups). That is differential
  in G, not directly in flip-status — but if flip-status correlates with G-subgroups, the two couple.
  The clean separation above assumes flip ⟂ (the axis BISG errs on); that assumption is itself
  checkable, not free. Flagged, not resolved.
- This is on the synthetic substrate with a SIMULATED proxy. It establishes the DIRECTION and the
  named threat; it does not certify any real BISG instance is non-differential. That certification is
  the empirical work a real-data port still owes.

## Status against the goal

The shuffle-set characterization is now COMPLETE with its real-data measurement loss located, not
just declared: protected-blind (robust to non-diff proxy), margin-driven, stable, no-knee ε-curve,
seed-robust in structure. The remaining real-data work is bounded to one falsifiable question
(is the proxy differential in flip status?), which is a clean place to hand to a real-data phase.

## Meta

Two frozen predictions, BOTH held (non-diff safe for blindness; differential is the sole threat) —
the first priored predictions to land this engagement, because the claim was a measurement-error
THEOREM (attenuation) with a known sign, not a satisfying narrative. Interrogating Fable's strongest
point instead of banking it turned a conceded loss into a sharpened, falsifiable scope. The adversary
was right that it's a loss; wrong that it's general.
