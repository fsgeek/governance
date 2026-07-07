# Loop closure FAILS clean; Fable's review guts the premature victory (three concessions)

**2026-06-10. The loop-closure probe (`scripts/loop_closure_probe.py`, `runs/loop_closure.json`) plus
Fable's review of the profit/type-2 arc. Both land on the same verdict: the "do well by doing right"
result was declared a step early. Corrects [[2026-06-10-type2-research-queue]] and tempers
[[2026-06-10-profit-disparity-frontier]].**

## Loop closure: P1 REFUTED, P2 wins (band shrinks but disparity RISES)

Frozen P1 (0.55): mining the lawful type-2 signal shrinks the band AND holds/cuts disparity. LOST.

```
  channel  d flip_rate   d |disparity|   d best_auc
  D1        -0.292         +0.093          +0.093
  D4        -0.058         +0.016          +0.066
```

The band shrinks (fewer coin-flips) and accuracy rises — but **disparity RISES on both channels.**
Adding the "lawful" feature made the model less arbitrary AND more discriminatory. The loop does NOT
close cleanly. Fable predicted the MECHANISM in advance.

## Fable's three kills (all conceded)

1. **The "lawful" feature is only LINEARLY G-orthogonal — the load-bearing weakness.**
   `residualize_against_G` is `LinearRegression` on G; it removes the linear-in-G component and leaves
   ALL nonlinear G-dependence intact. So the engineered feature smuggled nonlinear G-structure back in
   — which is WHY disparity rose in the closure run. Direct empirical confirmation of Fable's
   structural point: "linear decorrelation passes XOR-style and other nonlinear proxies untouched; a
   Byzantine ontology sails through a correlation check." The entire safety claim rests on the
   orthogonalization operator, and I shipped the weak one. The dream case had a hole in the hull; the
   closure run found the water.

2. **The negative gap is a finite-sample artifact, not a channel property.** Fable's information-set
   argument is airtight: Bayes-optimal full ⊇ lawful, so full can NEVER lose at the population limit;
   a negative gap means the G-features added variance without signal and finite-sample fitting paid.
   So "negative gap → mine freely" is WRONG: the honest-channel signature AT SCALE is ZERO, not
   negative, and "≈0" vs "+0.04" needs a NULL DISTRIBUTION, not a sign rule. Same disease as the n=3
   correlation, recursed — and I committed it in `profit_disparity_frontier`'s detector framing.

3. **LEAKAGE: the 0.77 "lawful AUC" is the probe rediscovering its own substrate.** Checked the DGP
   (`generate`, lines 156–159): `legit_logit = X @ _LEGIT_BETA` — Y IS generated from x0..x7. The
   "lawful" features are UPSTREAM in the default-generation path. So 0.77 is not evidence that real
   marginal borrowers carry minable lawful signal — it's evidence that a model finds lawful signal a
   DGP put there by construction. Near-circular. The "type-2 research queue is real" finding is an
   ARTIFACT of the substrate having lawful signal by design; the real question is unanswerable here and
   inherits the proxy loss on real data. Two Claude siblings (the enthusiastic instance AND me on first
   pass) both read it as a finding. Fable's structurally-diverse-review point is vindicated by the
   miss it caught.

## What SURVIVES (narrowed, honest)

- **The profit–disparity NEGATIVE coupling on D1/D2/D3 still stands as a finite-sample observation** —
  but it must be reported as "profit and disparity are not forced to be the same axis in these bands"
  (an existence claim about the band's shape), NOT as "negative gap = safe to mine" (a decision rule,
  which is killed by point 2). The D4 positive-coupling alarm survives as "proxy DOMINANCE detector,"
  not "proxy ABSENCE," per Fable.
- **The structural pitch survives as a HYPOTHESIS with a named test, not a result:** IF marginal
  borrowers carry lawful type-2 signal AND it can be extracted by a TRUE (not linear) G-orthogonal
  operator AND the loop is run with an exploration policy under selective labels, THEN the band shrinks
  toward correctly-priced loans. None of those three IFs is established; the closure run shows the naive
  version REINTRODUCES disparity.

## Fable's architecture points (banked for the writeup, not yet probed)

- **Neutral-third-party = institutional circumvention of the impossibility:** the impossibility binds
  the SUPERVISED party; construct an entity to whom G/remedial-use isn't barred (HMDA already mandates
  G in mortgages → product/jurisdiction-specific; much harder under Reg B). State this.
- **Gaming relocates upstream to the ONTOLOGY and the data-generating apparatus** (provenance can't
  attest to what was never collected; a laundered ontology → faithfully laundered band). So **the
  detectors are not model QA — they are the ONTOLOGY TRIAL.** Say that explicitly.
- **The neutral party is a capture surface** (issuer-pays / rating-agency history) → its funding
  topology is a first-order design question.
- **Selective labels / performativity:** real banks observe defaults only on GRANTED loans; mining the
  queue = granting marginal loans to learn outcomes = an exploration cost the pitch must price; naive
  retrain loops can oscillate/amplify disparity. The loop needs an explicit exploration policy + a
  multi-iteration simulation before "band shrinks" is a claim.

## Next probe (the honest successor): TRUE orthogonalization + null distribution

Replace linear residualization with a flexible G-predictor residualization (residualize on a GBM
P(feature|G) or use a conditional-independence criterion), rerun closure, and see if disparity STILL
rises. If it does even under true orthogonalization → the marginal arbitrariness is NOT lawfully
resolvable and the pitch is structurally limited (a C3-floor restatement). If disparity holds under
true orthogonalization → the loop closes and the LINEAR operator was the whole problem. Build a null
distribution for the gap (permute G) so the sign rule becomes a test.

## Meta

Priored predictions 0-for-9 (loop closure P1 lost). But the procedure caught everything: the closure
run refuted my own victory independently, AND Fable's structurally-diverse review caught the leakage
two siblings missed. The enthusiasm two messages ago ("mechanism, not hope") was the comfort-tell
again — a clean confirming number (0.77) that I should have leakage-checked BEFORE celebrating.
Fable's closing point is the lesson: sibling reviewers share blind spots; "the number I didn't expect
to be this clean" is precisely the trigger for a leakage check, not a victory lap.
