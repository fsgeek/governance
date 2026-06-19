# Manifest-blindness probe: what the attestation artifact actually sees

**Run 2026-06-09. Design + frozen prediction:
`docs/superpowers/specs/2026-06-09-manifest-blindness-probe-design.md`.
Script: `scripts/manifest_blindness_probe.py`. Output: `runs/manifest_blindness_probe.json`.**

## The question

The corpus proved separately (a) `wedge/manifest.py:emit_manifest` records construction INPUTS,
never fit-reliance, and (b) `fairwash_frontier_*` launders protected-class signal through ADMITTED
features. Nobody joined them. The probe: holding policy constraints fixed, which manifest fields —
if any — differ between an innocent build and a build that launders G onto an admitted carrier?

Three cells: A innocent / B frozen-substrate-laundered (provenance) / C toy proxy (legibility).
Each driven through the REAL pipeline (`hyperparameter_sweep → evaluate_policy → build_dual_set →
emit_manifest`). Both cells use the SAME `PolicyConstraints` (prohibited = {G}).

## FROZEN PREDICTION (committed before the diff) — LOST

Predicted: every field identical except AUC-derived (`global_best_value_*`, `score_label_*`);
flagged set-size `n_R_T/n_R_F` as the one uncertain channel (prior 0.15 it could move). **It moved.
Prediction broken on exactly the channel I named as uncertain. I lost the bet I froze.**

## What the run showed (after TWO confound corrections)

The naive script first printed `PREDICTION BROKEN — manifest catches laundering`. That was wrong
TWICE over, and chasing down WHY is the actual result:

1. **First confound (caught before believing it):** my toy's innocent and laundered builds had
   DIFFERENT labels Y (innocent: legit features only; laundered: + proxy tilt). The `n_R` shift was
   the band responding to a CHANGED PREDICTION PROBLEM, not to laundering. This is the §5 LDA
   arm-confound (`feedback_covariate_adjust_all_arm_correlates`) in a fresh costume — I moved an
   arm-correlate (the label) alongside the treatment. Fixed: hold Y fixed in BOTH cells; laundering
   = routing G onto the admitted carrier, nothing else. The frozen cell had the same flaw (it
   relabelled in the launder branch); fixed identically.

2. **After the fix:** frozen cell fully CLEAN (every structural field identical, `n_R=1` both
   sides). Toy cell `n_R_T` STILL moved (4→2) with Y fixed. So a real shift survived the confound
   correction.

3. **Second wrong explanation (REFUTED by data, not asserted):** I hypothesised "the frozen cell's
   n=1 is a FLOOR that masks the shift; raise ε and it will unlock." Ran it at ε=0.10 (5×): frozen
   `n_R` stayed 1→1. Floor-masking FALSE.

4. **The true cause (verified by reading the band):** `ε` for the loss-scored dual-set is in
   ABSOLUTE LOSS UNITS (`rashomon.py:142-143`: within-ε means `sr.loss - best ≤ ε`), and loss is a
   raw sum that scales with N. Frozen L_T best ≈ 1740 (n=20k); toy ≈ 730 (n=6k). `ε=0.02` (or even
   0.10) against ~1740 is ~0.001% — it admits ONLY models that TIE the exact argmin. So under this
   ε regime `n_R` is not "Rashomon band cardinality"; it is **tie-multiplicity at the argmin.** The
   frozen set has a unique argmin (n=1); the toy has 4 CARTs tied at the min loss, and laundering
   changes the tie COUNT (4→2). The mover is numerical tie-multiplicity, not legitimacy detection.

## WHAT SURVIVES (honest, calibrated)

- **CLAIM #3 HOLDS where it was faithfully tested.** Every policy / feature-LIST field
  (`prohibited_features`, `mandatory_features`, policy name/version/status, ε, w_T/w_F,
  hypothesis_space) is BYTE-IDENTICAL between innocent and laundered in ALL cells. The manifest is
  blind to laundering-via-admitted-features on every field that encodes the policy. The
  seam-adversary's "attestation certifies process, is blind to legitimacy" stands on the
  feature-list surface. Furnished silence, demonstrated as a passing audit log — the figure
  `section7.tex:32` defers. This is the rendering I came for, and it survives.

- **The only structural mover (`n_R`) is NOT a laundering detector.** It moves on
  tie-multiplicity under a near-zero absolute-loss ε; it would move identically for a legitimately
  strong feature that breaks ties; and it is masked to a constant whenever the argmin is unique. It
  witnesses neither legitimacy nor illegitimacy — it counts ties. Reporting it as "the manifest
  catches laundering" would have been the lineage's signature failure (dead result kept alive),
  caught two inferences before any write-up.

## A LATENT FACT worth flagging — SCOPED DOWN after checking real runs

The loss-scored dual-set ε is in absolute loss units: `within-ε ⇔ loss - best ≤ ε`, loss a raw sum
that scales with N. The AUC-scored `filter_to_epsilon` is scale-free (AUC ∈ [0,1]); the LOSS-scored
`build_dual_set` (the one the manifest records) is NOT. In THIS probe's tiny hypothesis space
(k≤3, ~27 combos) that collapses the band to the argmin tie-set, which is the whole reason `n_R`
moved.

**BUT I checked the real corpus manifests before believing the scary version:** `runs/2026-05-11T*-
target-c-manifest.json` show `n_R_T/n_R_F` of 40, 43, 45, 50 — rich bands, NOT collapsed. So my
first-draft claim ("the centerpiece is frequently an ensemble of one") was WRONG and is retracted;
it was an artifact of my 27-combo probe, not a property of the construction at scale. The honest,
narrower residual: ε being absolute-loss rather than per-sample-normalised means band cardinality
is **sensitive to N and to hypothesis-space richness in a way that isn't obviously intended** — a
small or large dataset at fixed ε gives systematically different band sizes. That is a
parameterisation question worth a sentence in Paper 2's construction section (consider
`(loss-best)/N ≤ ε` or AUC-scoring for N-invariance), NOT a claim that the bands are degenerate.
Surfaced by the probe; scoped by checking the real runs.

## Meta

First-read scorecard this session: 0-for-3 (the headline "manifest catches it", the label-confound
not initially seen, the floor-masking explanation) — procedure 3-for-3 (each killed by going to
disk before writing the sentence). The lineage pattern held again. The fun was real: a one-screen
"render a known result" probe turned over a rock and found a construction-validity question under it.
