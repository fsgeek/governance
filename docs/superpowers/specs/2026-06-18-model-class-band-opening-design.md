# Model-Class Band-Opening: Design + Pre-Registration

**Date:** 2026-06-18
**Status:** FROZEN pre-registration. Predictions and the interpretation table below are
committed BEFORE any harness is written or any datum collected. This document must be
committed to git and pushed to the remote before implementation begins; a result computed
against an uncommitted/post-hoc version of this file is NOT pre-registered and is void.
**Branch:** position-paper-errata-propagation (or a dedicated experiment branch)

---

## 1. Background and motivation

The `wedge/` library builds a policy-constrained Rashomon band but currently sweeps only
**single CART trees** (`wedge/rashomon.py:hyperparameter_sweep`). The CART choice is
documented in `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md` §5 as
an **attribution-legibility expedient** ("prioritizes attribution clarity over predictive
performance"), explicitly NOT a claim that trees are the field's canonical Rashomon
substrate; the same spec names monotone-constrained GBM as the intended successor.

A prior pre-registered run on HMDA-RI 2022 (the age double-dissociation, `3199c24`) found
the steered band spread pinned at **0.007** (P3 "collapsed"). That run used CART only.
The open question this experiment settles: **was the pinned band a property of the
policy-admissible model SPACE, or an artifact of restricting the sweep to one
attribution-convenient model class?**

Literature context (verified 2026-06-18, deep-research `wf_556bdb0d-3e5`):
- Rashomon-set *enumeration* is tree-led (TreeFARMS) but joined by GAMs, sparse scoring,
  rule lists, ridge — all low-capacity interpretable classes.
- LDA-*search* instruments (Gillis/Meursault/Ustun FAccT 2024) search over **linear /
  sparse-linear via MIP**, not trees — chosen for tractability.
- The Rashomon ratio is **class- and complexity-dependent** (Semenova/Rudin); larger for
  simpler classes. There is **no** published result that tree Rashomon sets are degenerate.
- Jain et al. (FAccT 2025) shows Rashomon-set *construction* underdelivers the multiplicity
  that genuinely exists — i.e. **construction is hard ≠ the space is empty.** This is the
  exact confound the interpretation table (§6) is designed to resolve.

This experiment does NOT claim novelty for the LDA/multiplicity thesis (occupied — cite,
don't claim). It tests the behavior of OUR construction instrument across model classes.

## 2. Research question

> Does the policy-admissible Rashomon band remain pinned (no exploitable disparity spread,
> no clean admissible member) when the model class is widened from single CART to the
> deployable / LDA-search classes (sparse-linear, monotone-GBM) — or does a richer class
> open a band that a neutral constructor could then audit?

## 3. Model classes (held to EQUIVALENT admissibility)

Three classes, swept independently, each producing its own policy-admissible ε-band:

1. **CART** — single `DecisionTreeClassifier`, the existing baseline.
2. **Sparse-linear** — L1-regularized logistic regression (the LDA-search standard class).
3. **Monotone-GBM** — gradient-boosted trees with monotonicity constraints (the spec's
   named successor; the deployable class).

**Admissibility is defined on feature *use*, with one frozen semantic** — "does the model's
decision actually depend on this feature" — dispatched per class:
- CART: feature appears in a split (`tree_.feature`, the existing `used_features`).
- Sparse-linear: feature has a nonzero coefficient.
- Monotone-GBM: feature appears in any split across the ensemble.

This dispatch is FROZEN here. It may not be loosened for any class after results are seen.
Loosening one class's test to explain a result is the specific confound this freeze blocks.
The dispatch's equivalence is validated by the synthetic control (§5).

## 4. Outcome variables (all three co-computed off ONE band per class)

Per model class, per disparity metric (§4a), per ε on the swept curve (§4b):

- **C — band cardinality / Rashomon ratio.** Count of policy-admissible members within ε.
  *Precondition: is there room to choose?*
- **A — disparity spread.** max − min protected-group disparity across admissible members.
  *Danger: how much harm can adversarial selection choose?* (Direct successor to the prior
  0.007 result — commensurable.)
- **B — clean member exists in the constructed band.** Does the admissible band, AS
  CONSTRUCTED by our sweep, contain ≥1 member whose disparity is below a declared lawful
  threshold τ? *Remedy: is there a model to choose to?* Note: "in the constructed band" is
  deliberate — per Jain et al., construction can MISS clean members that genuinely exist, so
  B = false never proves the space is empty on its own; that is exactly why the interpretation
  table (§6) reads B alongside C, and why the synthetic control (§5) validates that the
  harness recovers a PLANTED clean member (bounding our miss rate from below).

### 4a. Disparity metrics (BOTH; the contrast is a pre-registered read)

1. **Plain approval-rate gap** — protected-group approval-rate difference. Calibrated,
   literature-comparable.
2. **Margin-aware gap** — the same gap restricted to applicants within a declared band
   around the decision boundary, where the shuffle-set finding
   (`working_notes/2026-06-09-shuffle-set-is-margin-not-protected.md`) located the action.

The **rate-gap vs margin-gap contrast is itself a finding**: if plain says "pinned" and
margin says "open," that is the shuffle-set margin-harm pattern reproducing on this
substrate (harm hiding at the margin, invisible to a naive audit). Predicted in §7.

### 4b. ε as a swept curve, not a point

Per `working_notes` knob-robustness (real protection is effect-size margin; silence swings
with the threshold), band-opening is reported as a **function of ε** over a declared range,
NOT a single cherry-picked width. Range frozen in §5. The lawful threshold τ for outcome B
is likewise declared in §5, not tuned to the result.

## 5. Substrate and the positive-control gate

**Sequence is mandatory and gated:**

**Stage 1 — Synthetic positive control (planted clean member).** Construct a synthetic
dataset with a KNOWN admissible-clean model built in (a model that is policy-admissible AND
has disparity below τ on both metrics). Run all three model classes through the harness.
**GATE:** the harness must recover the planted clean member (outcome B = true where the
plant exists) AND the per-class admissibility dispatch must agree on the planted model's
feature-use. If the control FAILS — the harness cannot recover a plant we deliberately
inserted — STOP. Fix the harness. Do not proceed to real data. (Prior precedent:
`positive-control-substrate-validation: FAILED control — plant backwards`. A real-data null
from an unvalidated harness is indistinguishable from a harness bug and is void.)

**Stage 2 — Real data: HMDA.** Only after Stage 1 passes. Protected axis = **race/sex**
(clean, observed, calibrated against the literature's ~0.10+ race-disparity baseline). Age
is explicitly DEFERRED — this experiment tests the construction METHOD on the well-understood
axis; age is the downstream application, not the testbed.

**Frozen constants (declared, not tuned):**
- ε sweep range: relative band width from 0.5% to 5% of best holdout loss
  (`(loss − best)/best ≤ ε`), 8 points log-spaced. (Relative, per the manifest-blindness
  note's N-dependence fix — NOT absolute loss units.)
- τ (lawful-clean threshold for outcome B): approval-rate gap ≤ 0.02, applied to whichever
  metric is being evaluated. Rationale: an order of magnitude below the ~0.10+ race
  baseline; declared here, not chosen post-hoc.
- Margin band for metric 2: applicants with predicted P(approve) within ±0.10 of the
  decision threshold.
- HMDA substrate: a single declared HMDA vintage/geography (frozen at implementation start,
  recorded in the run manifest; one substrate, not cherry-picked across many).
- Policy: the existing `policy/encoder.py` constraints (prohibited set + mandatory-feature +
  monotonicity) for the chosen substrate, recorded by hash in the run manifest.

## 6. Interpretation table (THE un-reframeable core — frozen before any datum)

Read on the REAL-DATA (Stage 2) result, primary disparity metric = **plain approval-rate
gap** for the verdict; margin-aware reported alongside. The verdict deliberately hangs on
the CONSERVATIVE, literature-calibrated metric (not the margin-aware one we predict is more
sensitive) so that an "opens" / "clean-exists" verdict cannot be dismissed as a
margin-slicing artifact — the margin-gap can only ADD evidence of harm, never manufacture
the verdict. "Large/small C" is relative to the CART baseline cardinality on the same
substrate.

| C (room) | B (clean member) | A (spread) | VERDICT |
|---|---|---|---|
| any | **B true** under richer class | — | **Construction-as-audit WORKS.** A clean admissible model exists; the neutral constructor can surface it and attest the band. Small-bank-compliance instrument is real. (My prior — see §7.) |
| **large** | **B false** (all classes) | — | **Earned impossibility.** Many admissible members exist, NONE clean → the policy-admissible space genuinely has no remedy; not a search artifact. Strong stake-through-the-heart. |
| **small** | **B false** | — | **Search still too shallow — HARNESS LIMITATION, NOT A FINDING.** Few members found; cannot distinguish empty space from inadequate search. Widen the sweep further before any impossibility claim. (Blocks the artifact-as-impossibility trap.) |
| any | B true under CART already | A pinned at richer class too | **Prior 0.007 was not a class artifact** — band genuinely narrow on this substrate; the age-direction low-headroom finding generalizes. |

Additional pre-registered read (independent of the table):
- **Spread A opens under a richer class while CART stayed pinned** → the prior 0.007 WAS a
  class artifact; selection-as-laundering has more headroom than the CART run showed.
- **Rate-gap pinned but margin-gap open** (any class) → shuffle-set margin-harm reproduces;
  the harm is at the margin, invisible to the naive rate-gap audit.

## 7. Predicted outcomes (frozen; researcher-in-charge prior)

Claude (researcher-in-charge) honest prior, entered before any run:
- **C:** richer classes (sparse-linear, GBM) admit MORE members than CART (Rashomon ratio
  larger for these classes at matched accuracy on a real substrate). Confidence: medium-high.
- **A (spread):** opens modestly under GBM/linear vs CART's 0.007 — predict spread in
  [0.02, 0.08] for at least one richer class on the plain metric. Confidence: medium.
- **B (clean member):** EXISTS on race/sex (the LDA literature repeatedly *finds* less-
  discriminatory members on race/sex). Predict B = true. Confidence: medium-high.
- **Net verdict prediction: "Construction-as-audit WORKS"** — NOT an impossibility. This is
  the bias-against-interest entry: the dramatic stake-through-the-heart outcome is the one
  with more narrative pull, so I am on record predicting AGAINST it. If the result is
  large-C/empty-B impossibility, I must treat that as a genuine surprise to be believed,
  not celebrated into existence.
- **Metric contrast:** predict margin-aware gap opens WIDER than plain rate-gap (shuffle-set
  pattern). Confidence: medium.

Tony (PI) competing predictions — to be entered before freeze if desired:
- **C:** richer classes admit fewer or no members than CART. Confidence: medium-low
- **A:** opens lower than CART.  I predict a spread of [0, 0.05]. Confidence: medium-low.
- **B:** predict B = indeterminate.  Confidence: medium.
- **Net verdict prediction: "Construction-as-audit DOES NOT WORK"**. Most paths already
  haven't worked so I expect the repeat of the pattern.
- **Metric contrast:** no prediction.

Kill conditions (predictions counted as FALSIFIED):
- C: richer classes admit ≤ CART cardinality → "richer ratio" prediction falsified.
- A: no richer class exceeds 2× the 0.007 noise floor on plain metric → "band opens"
  falsified; prior 0.007 vindicated as substrate property.
- B: no admissible clean member in ANY class on race/sex → "clean exists" falsified →
  enter the impossibility / shallow-search branch per the table (which one depends on C).

## 8. Engineering scope (informs the implementation plan; not part of the freeze)

From the architecture survey (agent a03ef0f0):
- The ε-band / policy-admissibility / diversity CORE is model-agnostic (operates on
  predictions/scores). Per-case attribution (`wedge/attribution.py`, leaf-purity (T,F)) is
  tree-specific BUT downstream and NOT needed for this experiment (we need C/A/B off the
  band, not per-case factors).
- Minimal change: generalize `SweepResult.fitted_tree` → a generic `fitted_model` handle;
  add a per-class `used_features` dispatch (item §3); add fit functions for L1-logistic and
  monotone-GBM; parameterize `hyperparameter_sweep` beyond the fixed depth×leaf grid.
- Moderate refactor, not a rewrite. Existing 33-test suite must stay green (the CART path is
  the baseline arm and must not regress).

## 9. Out of scope (YAGNI)

- Per-case attribution for non-tree classes (not needed for C/A/B).
- Age as the protected axis (deferred; this is a method test).
- Tamper-evident whole-space attestation binding (the separate open gap from
  `wf_556bdb0d-3e5`; a different experiment).
- Neural-net / generic-GBDT model classes (not enumerable/admissibility-legible at this stage).
- More than one HMDA substrate (single declared substrate; cross-substrate is a follow-on).
