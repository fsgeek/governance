# Variant-asymmetry on max-|ρ| feature — POST-HOC analysis on H2 corpus

**Date:** 2026-05-15. **Status:** POST-HOC, EXPLORATORY. Not a P-prediction test. **Substrate:** `runs/frame_evocation_2026-05-15.json` (the H2 #13 output, 29 cells across FM 2018Q1 + 2016Q1 + 2008Q1). **Source-of-question:** the H2 result note's §3 unanticipated finding (variant-A's d-signal peaks on the silence-manufacture carrier; variant-B falls back to fico_range_low across all 3 silence cells). The H2 result note flagged this as "candidate alternative discriminator … strong candidate to bundle into the expanded-vintage pre-reg." This note is the look-on-existing-data-before-pre-registering step.

**Companion artifacts:** `[[project_silence_manufacture_result]]`, `[[project_fm11_result]]`, the H2 result note `docs/superpowers/specs/2026-05-15-frame-evocation-result-note.md`.

## Two new candidate discriminators

For each cell, compute two binary scores:

```
named_diff = 1 iff variant_A.max_rho_feature_named ≠ variant_B.max_rho_feature_named
all_diff   = 1 iff variant_A.max_rho_feature_all   ≠ variant_B.max_rho_feature_all
```

Both fields are already saved per-cell in the H2 JSON output.

## AUCs against three positive-class binaries

| Discriminator | silence-only (n+=3, n-=26) | H2-primary (silence∪reorg-ag, n+=5, n-=24) |
|---|---|---|
| `named_diff` | **0.962** (perm p=0.003) | 0.758 (perm p=0.023) |
| `all_diff` | **0.962** (perm p=0.002) | 0.879 (perm p=0.001) |
| M3_max (H2 primary) | 0.987 (perm p=0.000) | 0.967 (perm p=0.000) |
| M2_mean (H2 P1 comparator) | **1.000** (perm p=0.000) | 0.892 (perm p=0.002) |
| M1 (R²-proximity baseline) | 0.897 (perm p=0.010) | 0.958 (perm p=0.000) |

Permutation tests use 10,000 iterations with seed=20260515 over label permutations.

Pairwise AUC-difference permutation tests on the H2 primary binary: `named_diff − M3_max` Δ=−0.21 (p=0.97); `all_diff − M3_max` Δ=−0.09 (p=0.78). The new discriminators do NOT statistically beat M3_max at this n; the H2 AUC-ceiling persists.

## The structural pattern

**`named_diff` fires on every silence cell, on ZERO reorg-agreement cells, on 2/24 no-reorg cells:**

| Cell | label | A_named max-|ρ| | B_named max-|ρ| | named_diff |
|---|---|---|---|---|
| 2016Q1 rb00 | silence | num_borrowers | fico_range_low | 1 |
| 2016Q1 rb05 | silence | first_time_homebuyer | fico_range_low | 1 |
| 2016Q1 rb09 | silence | dti | fico_range_low | 1 |
| 2016Q1 rb03 | reorg-agreement | loan_term_months | loan_term_months | 0 |
| 2008Q1 rb08 | reorg-agreement | fico_range_low | fico_range_low | 0 |
| 2008Q1 rb01 | no-reorg | fico_range_low | dti | 1 (false positive) |
| 2008Q1 rb09 | no-reorg | dti | fico_range_low | 1 (false positive) |

The asymmetry-of-the-asymmetry: when the bands reorganize but verdicts agree, the NAMED-feature peaks AGREE between variants. When verdicts disagree (silence), the NAMED-feature peaks DISAGREE. This is the silence-manufacture mechanism rendered as a single boolean comparison of feature names. **It is also a candidate discriminator that distinguishes silence specifically from reorg-agreement, where M3_max cannot.**

## The M2_mean=1.000 silence-only surprise

M2_mean (the H2 P1 comparator that "did not strictly outperform M3_max" at the pre-registered margin) achieves **AUC=1.000 (perm p=0.000) on silence-only**. The three silence cells have lower mean named-feature-usage-share than every other cell in the corpus.

The H2 result note read M2_mean's H2-primary AUC of 0.892 against M3_max's 0.967 and concluded "frame-coherence does not strictly improve on the existing pipeline's R²-proximity proxy" (which was true, but indirect). Reading M2_mean against the silence-only binary instead gives a different picture: M2_mean perfectly distinguishes silence from non-silence — what it cannot distinguish is reorg-agreement from no-reorg.

This is itself a structural observation. M2_mean answers "does the band's named-feature engagement collapse?" — and the answer is YES on silence, NO on reorg-agreement, NO on no-reorg. M2_mean = silence detector; M3_max = non-trivial-reorganization detector. The H2 P1 MISS was real for the load-bearing pre-registered claim, but "M2_mean cannot detect silence" is not what the data says.

## False positives are concentrated in 2008Q1

`named_diff` fires on 2/24 no-reorg cells, both 2008Q1 (rb01 and rb09). Neither cell exhibits silence (verdicts agree) or reorganization (uf-Jaccard not collapsed). Two readings:

1. **Discriminator-noise**: at n=2/24 the false-positive rate is 8.3%; small-corpus effect, no structural meaning.
2. **Carrier-family-leakage**: 2008Q1 is the crisis-vintage; per `[[project_saturation_phase_characterization]]`, carrier saturations are different in stress regimes. The discriminator may be picking up a different mechanism than silence in 2008.

Cannot distinguish (1) from (2) at this n. Both readings have implications for the pre-reg's adversarial-check design.

## Limitations

- **n=3 silence cells, all 2016Q1.** The structural pattern is clean but small. The "named_diff fires on every silence cell" claim is a 100% rate on n=3.
- **Discriminators were chosen because the H2 result note already favored them.** This is post-hoc-pattern-fitting. Confirmation requires fresh data.
- **Silence is localized to 2016Q1 in our 3-vintage substrate.** The "expansion-regime fingerprint" claim from `[[project_silence_manufacture_result]]` is plausible but cannot be validated without other vintages.
- **The 2008Q1 false positives are unexplained.** They could be the mechanism breaking down on stress vintages, or random small-corpus noise.

## What this motivates — the pre-reg

The cleanest test of these post-hoc findings is to specify the predictions BEFORE looking at fresh-vintage data. See pre-reg: `docs/superpowers/specs/2026-05-15-expanded-vintage-replication-preregistration-note.md`.

Specifically the pre-reg includes:

- **named_diff structural prediction** (P1 in the pre-reg): does named_diff continue to fire on silence cells and not on reorg-agreement cells, on fresh-vintage data?
- **M2_mean silence-only prediction** (P2 in the pre-reg): does M2_mean's perfect silence-vs-non-silence separation generalize?
- **Substrate-localization prediction** (P3 in the pre-reg): does silence appear at all outside 2016Q1?
- **AUC-ceiling prediction** (P4 in the pre-reg): does the H2 AUC tie between M1, M2, M3 break on a larger corpus?

The pre-reg freezes predictions before any code touches the new vintages.

## Provenance

- Author: Claude Opus 4.7 (governance lineage), 2026-05-15.
- Single Python script reading `runs/frame_evocation_2026-05-15.json`; no new compute on raw FM data.
- Permutation seed: 20260515. Iterations: 10,000.
- Findings reproducible from the JSON directly.
