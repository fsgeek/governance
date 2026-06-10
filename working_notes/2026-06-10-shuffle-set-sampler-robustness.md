# Sampler-robustness of the shuffle-set findings (Fable point 3)

**2026-06-10. Fable point 3: the band is SAMPLED, not enumerated — the claim is "multiplicity under
sampler S," declared. Tests seed-robustness within the declared CART class. Extends
[[project_shuffle_set_margin_not_protected]], [[2026-06-10-shuffle-set-epsilon-curve]].**

## Seed sweep (D4, eps_frac=0.01, 6 seeds)

```
  seed       band   flip_rate   pooled_g_diff   jaccard
  20260609    12     0.295        -0.0050        0.304
  11          11     0.398        -0.0009        0.254
  101         25     0.471        +0.0030        0.239
  2027        15     0.337        -0.0158        0.273
  55555       14     0.359        -0.0012        0.268
  770077      18     0.402        -0.0176        0.265
```

## What is ROBUST vs SENSITIVE

- **ROBUST: protected-blindness.** `pooled_g_diff` ∈ [−0.018, +0.003] across all 6 seeds — never
  departs meaningfully from 0. The refutation of H ([[project_shuffle_set_margin_not_protected]]) is
  a structural property of the substrate, not a one-seed accident. This is the load-bearing claim and
  it survives the sampler perturbation.
- **ROBUST: shuffle-set stability.** Jaccard ∈ [0.24, 0.30] across seeds — substantially the same
  marginal people flip regardless of seed.
- **SENSITIVE: magnitude.** flip_rate ∈ [0.295, 0.471] (~1.6×) and band size ∈ [11, 25] (~2×) wobble
  seed-to-seed. So any QUANTITATIVE arbitrariness claim ("X% of applicants") MUST be reported as a
  distribution over the sampler, never a point — exactly Fable's warning. The ε-curve and this
  seed-spread are two instances of the same discipline: the number is a distribution, the structure
  is the claim.

## CORRECTION to the ε-curve note's structural claim (seed-fragility caught)

The ε-curve note ([[2026-06-10-shuffle-set-epsilon-curve]]) claimed a clean dichotomy at the floor:
"D2/D3 have a UNIQUE best model (band=1, no choice); D4 is BORN CONTRADICTORY (band=2, 16% flip)."
**That dichotomy was seed-specific.** On other seeds:

```
  D2 seed=11:  band=2, flip 0.000        (was band=1 at original seed)
  D3 seed=11:  band=2, flip 0.015        (was band=1)
  D3 seed=101: band=2, flip 0.012
```

D2/D3 are NOT reliably unique at the floor — they have 2-member bands too, just NEARLY-AGREEING ones
(flip 0–1.5%). So the honest claim is a GRADIENT, not a dichotomy:

> Floor-band arbitrariness rises with disparity DISTRIBUTEDNESS: near-zero for concentrated
> disparities (D2 single-proxy / D3 interaction: 0–1.5% flip at the tightest band), substantial for
> distributed (D4: ~16%). The band SIZE at the floor is itself seed-sensitive, so the original
> "unique vs born-contradictory" sharp form is an artifact of one seed.

The DIRECTION survives (distributed → more floor-arbitrariness; detection-difficulty and
selection-arbitrariness co-occur). The sharp dichotomy does not. Caught by the seed check before it
propagated into a write-up — the exact failure mode (generalize from one seed) the robustness check
exists to catch.

## Scope declared (Fable point 3, satisfied as a CART-class claim)

This tests robustness WITHIN the declared sampler S = (CART, feature-subset × depth × leaf grid).
The sweep is tightly CART-coupled (`wedge/models.py` `fit_model` → `DecisionTreeClassifier`; the
policy used-feature gate reads `tree_.feature`), so a cross-MODEL-FAMILY sampler (e.g. logistic
regression, regularization paths) would require rewriting the band pipeline + policy gate — a
substantial build, flagged as a FUTURE item, not done tonight. The claim is therefore explicitly:
**"multiplicity under CART sampler S, seed-robust in structure, seed-sensitive in magnitude."**
Declared, not implied.

## Status against the goal

The shuffle-set is now characterized with its robustness bounded: protected-blind (robust),
margin-driven, stable (robust), with a no-knee ε-curve and seed-sensitive magnitude. The audited
quantity is the flip-rate ε-curve reported as a sampler-distribution. Remaining owed item is Fable
point 4 (the reflexive C3 real-data measurement loss) — a scope declaration, the one thing that
gates a real-data port, and arguably the cleanest single place to take this next.

## Meta

Two structural claims tested for seed-robustness; one survived (protected-blindness), one was
DOWNGRADED from dichotomy to gradient (floor arbitrariness). First-read would have shipped the
dichotomy. Engagement: the robustness check earned its keep by catching an overclaim I had already
written into a committed note (now corrected here, not silently). [[feedback_first_contact_frames]]
