# "Pick one from the explainable set" is the silence-manufacturing move

**2026-06-09. Tony's probe: "if ε is inert, building explainable Rashomon ensembles is easy —
'here, pick one from the explainable set,' done, right??" Answer: NO — and the why sharpens the
whole project. Composes [[project_band_epsilon_inert]] with the corpus's within-band disagreement
data (`runs/within_tier_rashomon_test_results.json`).**

## The reasoning that makes "pick one" seem obvious

ε inert → band = argmin tie-set → all members tied on loss → interchangeable on accuracy →
"pick any explainable one, you're done." Rudin's existence claim satisfied for free.

## Why it's false (on real corpus data, not a toy)

Tied-on-loss ≠ interchangeable. Two models can post the IDENTICAL holdout loss and disagree about
WHICH borrowers — different splits, different features, opposite verdicts on the same person.

The corpus already measured this. `within_tier_rashomon_test_results.json`, 12 real grade-bands
(LC 2015H2 dti burst + 2013-14 annual_inc), ε=0.02:

```
burst           grade  distinct  feat_sets  med_rho  min_rho
D_2015H2_dti    A5     17        8           0.626   -0.061
D_2015H2_dti    C1     42        12          0.743   -0.077
D_2015H2_dti    C5     48        9           0.564    0.070
A_2013_14_annu  B1     5         3           0.768    0.023
... (12 bands)
median band_distinct_members = 14 (max 48)
median of min_pairwise_spearman = 0.123;  8 of 12 bands have min_rho < 0.3
```

`min_pairwise_spearman` is the per-borrower rank correlation between the two MOST-disagreeing
members of the band. In the majority of real bands it is near zero (several slightly negative).
**Two tied-on-loss, policy-admissible, explainable models rank borrowers almost INDEPENDENTLY of
each other.** The band is a real Rashomon set (median 14 distinct members, up to 8 distinct feature
sets), not a degenerate singleton.

(My own toy DGP produced a degenerate 2-member "tie-set" with 0% per-borrower disagreement —
identical decision vectors — which would have falsely supported "pick one." The real corpus bands
are the load-bearing evidence; the toy is too small to contain genuine alternatives. Checked the
real data before believing either position.)

## The synthesis (the actual finding)

**ε being inert does not make the construction trivial — it RELOCATES the entire difficulty into
model SELECTION within the band, which is exactly where manufactured silence lives.**

- The band is easy to build and frequently large.
- Its members frequently CONTRADICT each other per-borrower (min_rho ≈ 0).
- Every member is equally defensible on EVERY recorded metric: loss (tied by construction), AUC,
  policy-compliance, explainability. So the choice among them — the choice that decides who gets the
  loan — is **unconstrained by anything the manifest or the audit records.**
- Therefore "pick an explainable one" is an UNAUDITED DISCRETIONARY CHOICE dressed as a technical
  formality. It is the silence-manufacture pattern ([[project_silence_manufacture_result]],
  [[project_furnished_silence_result]]) in the selection step: the picker's discretion is total and
  invisible.

This is NOT a defect in Rudin's existence claim — the interpretable model does exist in the band.
It is that **"use it instead of a black box" is UNDERDETERMINED**: the band contains many
interpretable models that disagree about people, and which one ships is a free, unrecorded choice.

## The systems claim this forces (empty-chair, with teeth)

The honest contribution is NOT "we hand you an explainable model." It is:

> The policy admits N mutually-contradicting explainable models for this borrower; the system
> EXPOSES that, and forces the selection among them to be justified rather than hidden.

That inverts "pick one, you're done" into "you cannot pick one silently." The breadth/depth eval the
goal note wants ([[project_primary_goal_systems_contribution]],
[[project_goodhart_resistance_plural_objectives]]) has a natural home here: within-band
per-borrower disagreement = the measure of how much "pick one" HIDES.

## Revives two deflated results

- [[project_disagreement_routing_result]] / [[project_disagreement_geometry_result]]: deflated as a
  per-CASE routing signal (disagreement doesn't localize to hard cases; survives only as aggregate
  surveillance). Re-read under THIS frame, within-band disagreement is not trying to be a routing
  signal — it is the **audit quantity for selection discretion.** A different job, not the failed one.
  min_pairwise_spearman per band = "how much does the choice of band member matter for this
  population." That is a live metric, not a dead routing knob.

## Status

Composed from on-disk data; no new run needed to establish it (the disagreement numbers already
exist). The new thing is the COMPOSITION: ε-inert (band = tie-set) + within-band min_rho≈0
(tie-set members contradict) ⇒ "pick one" = furnished silence in the selection step. Worth a Paper-2
section: the construction is the easy half; making the SELECTION non-silent is the contribution.
