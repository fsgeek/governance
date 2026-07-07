# Set → score: per-applicant P(flip) is the stable audit object (Fable, vindicated)

**2026-06-10. Fable's challenge (document 3): "Jaccard 0.24–0.30 is NOT 'substantially the same
people'" + the constructive fix "move from set to score." Both accepted; the score built and tested.
Script: `scripts/pflip_score_probe.py`. Output: `runs/pflip_score_probe.json`. Corrects an error in
[[project_shuffle_set_margin_not_protected]].**

## The error Fable caught (two layers)

1. The committed claim "substantially the same marginal people flip across seeds (Jaccard 0.25–0.30)"
   was WRONG about what the column measured. `mean_pairwise_jaccard` (probe lines 230–239) is
   WITHIN-band member-pair overlap — Jaccard between two band MEMBERS' disagreement sets — NOT
   across-seed membership conservation. I conflated them. Across-seed conservation was UNMEASURED and
   I asserted it.
2. Even read correctly, ~0.27 is WEAK overlap. Fable: a Jaccard of 0.27 means the intersection is a
   quarter of the union — most members of one seed's shuffle-set are ABSENT from another's. So the
   set of people whose outcome is arbitrary is ITSELF arbitrary: second-order arbitrariness, the
   lottery's entrants chosen by lottery.

## The measurement (now done right)

Per-applicant P(flip) over S sampler seeds, on a fixed deterministic DGP (stable applicant indices).
Each seed holds out a different 30%, so applicant i is scored only where held out; P_flip(i) =
(#seeds i flipped)/(#seeds i held out), keep coverage ≥ 3. Across-seed flip-set Jaccard computed
RESTRICTED to commonly-held-out rows (else it measures split-disjointness, not conservation).

```
across-seed flip-SET Jaccard (4 seeds, common rows):  0.51   -> SET moderately conserved / jittery
P_flip frac extreme (<0.15 or >0.85):                 0.66   -> SCORE is BIMODAL
P_flip frac middle (0.4–0.6):                         0.01
P_flip vs (-margin) corr:                            +0.42   -> tracks seed-INVARIANT margin
P_flip G_diff (protected-blindness at score level):  -0.007  -> still protected-blind
deciles of P_flip:  [0, 0, 0, 0, 0, 0.25, 0.33, 0.67, 0.67, 1.0, 1.0]
```

## What it shows (Fable's reframe vindicated)

- **The SET is jittery, the SCORE is stable.** Membership in any one seed's shuffle-set is largely
  seed-noise, but P_flip(i) is a near-BINARY per-applicant property: ~half the population never
  flips (deciles 0–40% all 0.0), a clear tail always flips (top deciles 1.0), almost nobody in the
  middle (1%). The flip-REGION is structural (margin-driven, seed-invariant, corr +0.42); individual
  MEMBERSHIP within it is noise. Exactly Fable's reconciliation.
- **The score is individually meaningful and due-process-attachable.** "Your outcome differs in X% of
  equally-good models" is a per-person quantity; a threshold ("P_flip > 0.3 → human review") attaches
  to a score in a way it never can to a set whose membership a seed decides. The sampler distribution
  STOPS being noise-around-the-answer and BECOMES the answer.
- **Protected-blindness survives the move to score** (G_diff −0.007): the reframe does not resurrect a
  protected signal. The harm is still arbitrariness toward marginal applicants, now measured per
  person.

## Consequence: the audited quantity upgrades from set/rate to SCORE

The manifest field added at `454c79d` records a band-level flip-RATE. That is the right RATE but the
wrong GRANULARITY for due process. The per-applicant P_flip (over the sampler) is the object to
expose: a distribution/curve the institution attests, with the operating threshold a disclosed
policy act (Fable doc 2: ε and now the P_flip threshold are bank-side commitments, like a capital
ratio). [open: promote band-flip-rate → per-applicant P_flip in the audit record; needs the sampler
loop inside the construction, not just one band.]

## Two hygiene notes Fable flagged (accepted)

- D1's vacuous case (band=2, 0 flips) proves band COUNT is the wrong multiplicity metric and flip-rate
  is right — state explicitly so no future reader audits model-counts. (Already the design of the
  `454c79d` field; now said out loud.)
- The Jaccard "—" at degenerate-band rows should print WHY it is undefined (n_members<2), not dash
  silently. Silent dashes lose provenance. [small fix owed in the probe's printer.]

## Meta

Caught AFTER propagation (the claim was committed at `166620e`), corrected in the open with the
original preserved and dated — append-only epistemics, the khipu amended not rewoven. This is the
second post-propagation correction of the engagement (first: the floor dichotomy → gradient). The
calibration line holds: the overclaim was a SATISFYING caption ("the same people") minted without
measuring the thing it claimed. Comfort, not confidence, was the tell. [[feedback_engagement_quality]]
