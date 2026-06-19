# The dual-set ε is nearly inert: it pins the band to the argmin tie-set

**Run 2026-06-09 (continuation of the manifest-blindness thread). Scripts:
`scripts/band_n_invariance_probe.py`. Output: `runs/band_n_invariance_probe.json`.
Follows [[project_manifest_blindness_probe]], which surfaced the absolute-loss-ε concern.**

## The question

The manifest-blindness probe found the loss-scored dual-set ε is in absolute loss units. I
predicted the band would DEGENERATE at production scale (n_R shrinks toward 1 as N grows). Tested it.

## FROZEN PREDICTION — WRONG (and the real finding is sharper)

Predicted: `n_R` shrinks toward 1 as N rises at fixed ε=0.02, because loss is a raw case-count sum
on the holdout and the loss-gap scales with N. **Wrong: `n_R_T` was ALREADY ~1 at the smallest N
(1000) and stayed 1-2 all the way to N=100000.** Not scale-degradation — the band is the argmin
tie-set at EVERY N.

```
       N  holdout  n_adm  n_R_T  n_R_F   best_L_T
    1000      300    126      1      9      118.5
    3000      900    126      2      2      388.5
   10000     3000    126      2      2     1354.0
   30000     9000    126      1      1     3883.5
  100000    30000    126      1      1    12826.0
```

## THE VERIFIED FINDING: ε is nearly inert

Loss is an integer count of misclassified holdout cases (`wedge/losses.py`,
`grant_emphasis_loss` = `w_T·missed_grants + missed_denies`, all `.sum()` of indicator counts). So
"within ε of the best loss" with ε < 1 means "ties the best integer loss." ε=0.02 is sub-unit at
every N. **Sweeping ε at fixed N=10000, k=3 confirms it directly:**

```
  abs eps= 0.02: n_R=2     abs eps= 5.0: n_R=3
  abs eps= 0.50: n_R=2     abs eps=20.0: n_R=4
  abs eps= 2.00: n_R=2
```

ε from 0.02 to 2.0 — two orders of magnitude — gives the IDENTICAL band. The parameter does almost
nothing. The band size is **tie-multiplicity at the integer-loss minimum**, governed by the
hypothesis-space loss landscape, not by ε.

This also explains the corpus's `n_R=40-50` runs (`runs/2026-05-11T*-manifest.json`, ε=0.05,
best_L≈1162-2759): those are 40-50 CARTs EXACTLY TIED at the integer argmin — a property of that
sweep's wide hypothesis space generating many models on the same integer loss, NOT of ε admitting a
spread. ε=0.05 vs 0.02 is irrelevant; both are sub-unit.

## THE FIX (demonstrated on disk, not just proposed)

Re-specify ε as a FRACTION OF HOLDOUT SIZE (`(loss - best)/n_holdout ≤ eps_frac`, equivalently
tol = eps_frac·n_holdout). Then the tolerance scales with N and becomes a real knob. Same
N=10000, k=3:

```
  eps_frac=0.0005: tol= 1.5 cases  n_R= 2
  eps_frac=0.001 : tol= 3.0 cases  n_R= 3
  eps_frac=0.005 : tol=15.0 cases  n_R= 4
  eps_frac=0.01  : tol=30.0 cases  n_R= 8
  eps_frac=0.02  : tol=60.0 cases  n_R=16
```

Monotone, controllable, N-invariant in meaning. This is the construction the absolute ε is not.

## What this is (calibrated)

- **Construction-validity finding for Paper 2's centerpiece** [[project_policy_constrained_rashomon]]:
  the policy-constrained Rashomon band's tolerance parameter, as currently coded in `build_dual_set`,
  is nearly inert (pins to the integer-argmin tie-set). The fix is a one-line re-spec to a per-sample
  fraction; the before/after curve is on disk. This does NOT impugn the IDEA — with a normalised ε
  the band is a genuine multi-member set whose size the analyst controls.
- **NOT a degeneracy claim about the corpus results.** The 40-50-member bands are real (exact ties);
  they were not wrong, they were just not ε-controlled. Retraction-resistant: I checked the real
  manifests before and after.
- **NOT chased into the tie-combinatorics.** Why a given hypothesis space yields exactly K ties is
  DGP-specific and does not generalise; stopped at the inert-ε / normalisation-fix result, which does.

## Meta

First-read scorecard for the engagement now 0-for-4 (manifest-catches-it, label-confound,
floor-masking, n_R-shrinks-with-N); procedure 4-for-4. Each prediction was killed by going to disk.
The shrinks-with-N miss was the most useful: chasing WHY it didn't shrink produced the sharper,
truer, fixable finding (ε inert, normalise it) that the original prediction would have buried.
