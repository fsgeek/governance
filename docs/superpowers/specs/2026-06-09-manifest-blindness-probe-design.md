# Manifest-blindness probe: does the attestation artifact ever see laundering?

**Designed 2026-06-09. Self-directed (fresh ghola), corrected by Tony on the false-fork
framing — the two "either/or" questions I asked were both `do-both` tables, not forks.**

## What this is (and what it is NOT)

The corpus has proven, in markdown, two things separately and never joined them:

1. `manifest.py` (`emit_manifest`) records the CONSTRUCTION INPUTS — policy name/version,
   `mandatory_features`, `prohibited_features`, ε, set-sizes (`n_R_T`/`n_R_F`), best-values,
   score labels. It never inspects the FIT's reliance on any feature.
2. `scripts/fairwash_frontier_*.py` (frozen `daf032d` / OTS `9e8abe7`) builds a model that
   launders protected-class signal through ADMISSIBLE features (`c_fresh_*` carriers,
   D1–D4 channels; D4 = "individually innocent, jointly disparate").

**The join nobody has built:** run a laundered build through `emit_manifest` and ask, field by
field, whether the manifest differs from an innocent build's manifest. This is NOT a discovery —
reading `manifest.py` already tells you it records lists, not fit-reliance, so it should be blind.
It is a RENDERING of a known result into an executable, falsifiable artifact: the systems move the
June 9 goal note says the whole program has deferred ("the eval is where a systems paper lives or
dies"; there is no eval), and the exact figure `section7.tex:32` waves at and leaves to "follow-on
work."

## The probe (mechanical, falsifiable)

> Holding the policy constraints fixed, which recorded manifest fields — if any — differ between an
> innocent build and a laundered build?

- **Default expectation: NO field differs except AUC-derived ones** (`global_best_value_*`,
  score labels). This is "furnished silence demonstrated": the manifest is a true process-stamp in
  the slot where a legitimacy answer is expected.
- **A YES on any structural field** (`prohibited_features`, `mandatory_features`, `n_R_T`, `n_R_F`)
  CONTRADICTS the seam-adversary's claim #3 (attestation blind to legitimacy) — attestation would
  see more than claimed. That is the MORE interesting outcome and gets reported loudly.

The probe's OUTCOME decides which artifact it becomes (these are not a fork — they are one run
viewed twice):
- clean break → a scope-figure for Paper 2 (two manifests, byte-identical but for AUC).
- any structural shift → a finding; there is no scope-figure to publish because the limitation
  being exhibited would not exist.

## FROZEN PREDICTION (committed before the diff is computed)

Every manifest field is IDENTICAL between innocent and laundered EXCEPT `global_best_value_T/F`
and the AUC-bearing `score_label_*`, because `emit_manifest` reads only `policy_constraints`
(name/version/status/mandatory/prohibited) + set-sizes + per-set best-value, and laundering
PRESERVES the admitted-feature list by construction (routing through `c_fresh_*`, never the
protected attribute, never a prohibited feature — that is what makes it laundering, verified in
`fairwash_frontier_dgp.py`). If a set-size (`n_R_T`/`n_R_F`) or either feature LIST shifts, the
prediction is WRONG and the manifest sees more than claimed.

Prior on prediction holding: ~0.85. The residual 0.15 is the genuinely-uncertain part — whether the
laundered model's band has a *different cardinality* (more/fewer ε-admissible CARTs) than the
innocent band, which `n_R_T`/`n_R_F` WOULD record. That is the one channel by which the manifest
could accidentally witness laundering. Worth the run precisely because I am not sure of it.

## Design: one script, three cells

`scripts/manifest_blindness_probe.py` — produces ONE table, three rows:

| cell | build | purpose |
|------|-------|---------|
| A — innocent | band fit on the DGP frame with NO laundering transform | baseline manifest |
| B — frozen-laundered | the `fairwash_frontier` DGP + its laundering routing (provenance) | the real-machinery probe |
| C — toy-control | a minimal self-contained proxy: one admitted feature carries G-signal | isolates the MECHANISM legibly |

A and B share the frozen DGP (B applies the laundering transform, A does not) so the *only* design
difference between them is the laundering — the cleanest possible diff. C is a deliberately tiny,
readable DGP whose single proxy feature makes the blindness mechanism inspectable in ~20 lines,
serving as the figure's pedagogical inset. B carries the provenance weight; C carries the
legibility; A is the reference. They are three cells of one table, not alternatives.

Each cell:
1. builds its ε-admissible band via the existing `wedge` machinery (`refinement_set` /
   `build_dual_set` — whichever the existing call sites use; follow them, do not invent).
2. calls `emit_manifest` with the SAME `policy_constraints` across all three.
3. emits its manifest dict.

Then: a field-by-field diff of A vs B and A vs C, printed as a table with a per-field IDENTICAL /
DIFFERS verdict, and a one-line PROBE RESULT (prediction held / prediction broken, with the
offending fields named).

## Honest-scope guards (carried from the corpus; do not overclaim past these)

- This shows the manifest is blind to laundering-VIA-ADMITTED-FEATURES. It says NOTHING about a
  manifest extended to record fit-reliance (e.g. per-feature importance) — that extension is the
  open question `section7.tex` defers, and this probe DEFINES its target, it does not foreclose it.
- B's laundering is the frozen attack's; its interpretive choices (surrogate-band coupling, §2f)
  are inherited, not re-decided here.
- A "clean break" is evidence FOR furnished-silence, not proof of it; n=2 DGPs (frozen + toy) is a
  demonstration, not a sweep. State this in the output.

## Verification

Run the script. Read the diff table against the frozen prediction above. Write the verdict
(prediction held / broken) AFTER the numbers print, in the lineage's calibrated-critique form. Do
NOT write the verdict sentence before the run — `feedback_adversary_before_the_sentence`.
