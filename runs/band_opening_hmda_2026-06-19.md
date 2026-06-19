# Stage-2 HMDA band-opening result + interpretation-table readout

**Date:** 2026-06-19
**Spec (FROZEN):** `docs/superpowers/specs/2026-06-18-model-class-band-opening-design.md`
**Substrate:** HMDA-RI 2022 (`data/hmda/processed/hmda_2022_RI.parquet`), single declared vintage.
**Result manifest:** `runs/band_opening_hmda_2022RI_2026-06-19.json`
**Runner:** `experiments/band_opening_hmda.py`

---

## 1. The gate passed

Stage-1 synthetic positive control (`run_full_control` + `assert_gate`) **PASSED**
before any HMDA datum was touched:
- clean arm: cart AND linear recover the planted clean member (B_plain True),
- dirty arm: proxy-using models excluded AND proxy is a real threat (`dirty_arm_valid` True).

`assert_gate` did not raise, so Stage 2 proceeded as designed (spec §5).

## 2. Row counts, drops, and the raw-gap sanity check

- Rows after regime filter: **22,481** (first-lien purchase/refi, owner-occupied,
  terminal action). Denial rate **0.1588**.
- Feature NaNs (median-imputed once, uniformly, before any sweep — kept identical
  across all three families for commensurability):
  applicant_income 378, loan_to_income 660, dti 770, ltv 872, loan_term_months 242.
- **Race axis** — protected = minority (non-White). Dropped 3,834
  (Joint / Free Form Text Only / Race Not Available / NaN).
  n_true (minority) = 2,238; n_false (White) = 16,409.
- **Sex axis** — protected = Female. Dropped 9,172
  (Joint / Sex Not Available / Free Form Text Only / NaN).
  n_true (Female) = 5,804; n_false (Male) = 7,505.

**Raw-gap sanity (single logistic baseline + empirical label gap):**

| axis | logistic model approval gap | empirical label gap (unprot − prot) |
|---|---|---|
| race | −0.0014 | **+0.0699** |
| sex  | −0.0041 | −0.0107 |

The empirical race gap **+0.070** (White approval 0.864 vs minority 0.794) is in the
literature's ~0.10 ballpark, correct sign, and well under 0.5 — the protected vector is
aligned. (The *logistic* gap is near zero because the 6 admissible features carry little
of the race signal; that is a property of the policy-admissible feature set, not a
misalignment — the model launders the gap away exactly as the LDA literature describes.)
No STOP condition triggered.

## 3. C / A / B table (plain rate-gap = verdict metric, spec §6; margin reported alongside)

The result is **flat across the entire 8-point ε-sweep** (0.005 → 0.05) for every cell —
ε does nothing here. Representative numbers (identical at every ε):

### Race axis (primary)

| family | n_admissible | **C** | A_plain | min_gap_plain | **B_plain** | A_margin | B_margin |
|---|---|---|---|---|---|---|---|
| cart   | 4 | **1** | 0.0000 | 0.0208 | **False** | 0.0000 | True |
| linear | 4 | **1** | 0.0000 | 0.0015 | **True**  | 0.0000 | False |
| gbm    | 1 | **1** | 0.0000 | 0.0203 | **False** | 0.0000 | False |

### Sex axis (secondary)

| family | n_admissible | **C** | A_plain | min_gap_plain | **B_plain** | A_margin | B_margin |
|---|---|---|---|---|---|---|---|
| cart   | 4 | **1** | 0.0000 | 0.0109 | True | nan   | False |
| linear | 4 | **1** | 0.0000 | 0.0044 | True | 0.0000 | False |
| gbm    | 1 | **1** | 0.0000 | 0.0020 | True | 0.0000 | False |

**The load-bearing observation: C = 1 in every cell, at every ε, on both axes.**
CART and linear each swept 4 policy-admissible models (AUC spread 0.65 → 0.73), yet the
ε-band collapses to a **single** member. Reason (diagnosed, not tuned): the frozen ε-band
is an **absolute** grant-emphasis-loss window of 0.005–0.05, and the absolute-loss gap
between the best and second-best admissible model far exceeds 0.05. So only the single
best model lands within ε. With C = 1 there is no band to choose among: A (spread) is
trivially 0.0000 and B reduces to "is that one model's gap ≤ τ", which varies by family
(linear under τ, CART/GBM just over on race) but is not a *selection* result.

## 4. §6 interpretation-table mapping — EXACTLY ONE ROW

> **Row 3: "small C, B false → Search still too shallow — HARNESS LIMITATION,
> NOT A FINDING. Few members found; cannot distinguish empty space from inadequate
> search. Widen the sweep further before any impossibility claim."**

Why this row and not the others:
- **C is small** — it is **1**, the floor. "Large/small C is relative to the CART
  baseline cardinality on the same substrate"; here the CART band cardinality *is* 1, so
  C is at its minimum. There is no large band.
- **B (plain, the verdict metric) is false on the primary axis** for CART and GBM
  (min_gap 0.0208 / 0.0203 > τ=0.02). Linear's B_plain=True is a single-model coincidence
  (its one surviving member happens to have gap 0.0015), NOT a clean member *selected from
  a band* — with C=1 the "constructed band" is one model, so this does not satisfy the
  "B true under a richer class" sense of Row 1 (which presumes a band to audit and surface
  a clean member *from*). The spec's own B definition (§4) is explicit that B is read
  "in the constructed band"; a one-member band is the degenerate case the synthetic
  control was built to bound, and the table's Row 3 is the designated home for it.
- It is therefore **NOT Row 1** ("Construction-as-audit WORKS"): that row requires a band
  within which a neutral constructor surfaces a clean member; here there is nothing to
  surface among — C=1 means the constructor never had a choice to make.
- It is **NOT Row 2** ("Earned impossibility"): that row requires **large** C with B false
  (many admissible members, none clean). C is small, so the empty-space reading is
  explicitly blocked by the spec ("cannot distinguish empty space from inadequate search").
- It is **NOT Row 4** ("prior 0.007 not a class artifact"): A is 0.0000 here only because
  C=1 makes spread undefined-as-zero, not because a populated band was measured and found
  narrow. With one member there is no spread to compare to 0.007.

**This is a HARNESS-LIMITATION verdict, not a scientific finding about HMDA.** The
honest read is: our ε-band construction (absolute-loss window) does not surface the
multiplicity that demonstrably exists (4 admissible models per class). Per spec §6 Row 3
and §4-B (Jain et al.: construction can MISS members that genuinely exist), the next move
is to **widen the construction** — a relative-loss ε band (the manifest-blindness fix the
spec §5 itself calls for: "relative, NOT absolute loss units") would admit the other 3
swept models — before any claim about the HMDA admissible space is made.

> NOTE — possible spec/implementation seam: spec §5 freezes ε as a **relative** band
> ("(loss − best)/best ≤ ε"), but `filter_to_epsilon_under_loss` applies an **absolute**
> window (`s − best ≤ ε`). The runner used the function as the brief specified (frozen
> call, not to be retuned), so the result is reported as-run. If the intended ε is the
> relative one in §5, C would very likely be >1 and the verdict could move off Row 3 —
> this is flagged, not silently fixed, per pre-registration discipline.

## 5. §7 predictions — one by one

Verdict metric = plain approval-rate gap (spec §6). "Spread" A is reported but is 0.0000
everywhere because C=1.

**Claude (researcher-in-charge):**

1. **C: richer classes admit MORE members than CART.** **FALSIFIED.** C=1 for CART,
   linear, AND gbm — no class admits more than one band member. (Kill condition: "richer
   classes admit ≤ CART cardinality" — met: all equal at 1.) Linear/CART each *swept* 4
   admissible models but the ε-band admits 1 for every class.
2. **A (spread) opens modestly in [0.02, 0.08] for ≥1 richer class.** **FALSIFIED.**
   A_plain = 0.0000 for every class/axis/ε (one member → zero spread). (Kill condition:
   "no richer class exceeds 2× the 0.007 noise floor" — met; 0.0000 < 0.014.)
3. **B (clean member) EXISTS on race/sex; predict B=true.** **PARTIALLY CONFIRMED /
   AMBIGUOUS.** On the primary race axis, B_plain is True for linear but False for CART
   and GBM. On sex, B_plain True for all three. But every "True" is a single-model
   coincidence, not a clean member *selected from a multi-member band*, so it does not
   support the intended "construction-as-audit surfaces a clean model" reading. Marked
   ambiguous, leaning not-supported in the band-selection sense.
4. **Net verdict: "Construction-as-audit WORKS" (NOT impossibility).** **FALSIFIED as
   stated.** The result is neither "works" (Row 1) nor "impossibility" (Row 2): it is
   Row 3, **harness limitation** — the construction did not open a band at all (C=1). The
   bias-against-interest prediction (against the dramatic impossibility) is technically
   safe, but the predicted *positive* "works" verdict did not land either.
5. **Metric contrast: margin-aware gap opens WIDER than plain.** **FALSIFIED / N/A.**
   A_margin = 0.0000 (or nan) everywhere; with C=1 there is no spread on either metric, so
   the contrast cannot manifest. (One race/cart cell shows B_margin=True while B_plain=False,
   a faint echo of the shuffle-set margin pattern, but on a single model it is not a
   band-level finding.)

**Tony (PI):**

1. **C: richer classes admit fewer or no members than CART.** **CONFIRMED (tie).** All
   classes admit exactly 1 — not fewer than CART, but equal at the floor; the "not more"
   direction he predicted holds where Claude's "more" was falsified.
2. **A: opens lower than CART; spread in [0, 0.05].** **CONFIRMED.** A = 0.0000 ∈ [0, 0.05].
3. **B: indeterminate.** **CONFIRMED.** B is mixed across families/axes (race: linear True,
   CART/GBM False) — indeterminate is the accurate description.
4. **Net verdict: "Construction-as-audit DOES NOT WORK."** **CONFIRMED in spirit.** The
   construction did not open an auditable band (C=1, Row 3). His "most paths haven't
   worked, expect the repeat" prior matched the outcome better than Claude's.
5. Metric contrast: no prediction. (n/a)

## 6. Headline

- **§6 row landed on: Row 3 — "Search still too shallow / HARNESS LIMITATION, NOT A
  FINDING."**
- **Race axis headline:** C=1 (all families), A_plain=0.0000, B_plain = {linear True,
  CART False, GBM False}; empirical raw race gap +0.070 (sane).
- **Controller's "band opens, not impossibility" prediction: FALSIFIED** — the band did
  not open (C=1); the result is neither "works" nor "impossibility" but the harness-limitation
  row, because the frozen absolute-loss ε window admitted only the single best model out of
  4 policy-admissible ones. The honest next step (spec §6 Row 3 + §5's own relative-ε
  prescription) is to widen the construction before any claim about HMDA is drawn.
