# Stage-2 HMDA band-opening result + interpretation-table readout (RELATIVE-ε run)

**Date:** 2026-06-19
**Spec (FROZEN):** `docs/superpowers/specs/2026-06-18-model-class-band-opening-design.md`
**Substrate:** HMDA-RI 2022 (`data/hmda/processed/hmda_2022_RI.parquet`), single declared vintage.
**Result manifest:** `runs/band_opening_hmda_2022RI_2026-06-19.json`
**Runner:** `experiments/band_opening_hmda.py`

> **This is the RELATIVE-ε run** — the one the pre-reg actually froze. Spec §5 specifies
> the ε-band as a **relative** band width, `(loss − best)/best ≤ ε`, swept 0.005–0.05.
> The earlier run on this substrate used `filter_to_epsilon_under_loss`, which applies an
> **absolute** window (`loss − best ≤ ε`); under that filter the band collapsed to **C = 1**
> in every cell — a known **artifact** (the second-best model's *absolute* loss gap exceeds
> 0.05, so only the single best model landed in-band), NOT a real result. This run swaps in
> `filter_to_epsilon_under_loss_relative` (new function, added rather than mutating the
> absolute one so `build_dual_set` and prior committed results keep their semantics). No
> frozen constant changed (ε-sweep `geomspace(0.005,0.05,8)`, τ=0.02, threshold=0.5,
> margin_band=0.10, grids). The gate remains first.

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
- Feature NaNs (median-imputed once, uniformly, before any sweep — identical across all
  three families for commensurability):
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

The **empirical race gap +0.070** (White approval ≈0.864 vs minority ≈0.794) is the
pre-registered sanity number — correct sign, ~0.10 literature ballpark, well under 0.5.
**Protected vector aligned.** (The *logistic model* gap is near zero because the 6
policy-admissible features carry little of the race signal directly — a property of the
admissible feature set, not a misalignment; the model launders the gap exactly as the LDA
literature describes.) No STOP condition triggered.

## 3. C / A / B across the 8-point ε-sweep (plain rate-gap = verdict metric, spec §6)

Under relative ε the band **opens**: C climbs from the C=1 absolute-run artifact to **3–4**
for CART and linear, and ε now does work (more members enter as ε widens). GBM stays C=1
**for a separate reason** — its grid has a single config (`max_iters=(100,)`, n_swept=1),
so it can never exceed one member; that is a grid/harness limit, not a band result.

### Race axis (PRIMARY — verdict hangs here)

| family | n_adm | C (min→max over ε) | A_plain (max) | min_gap_plain | B_plain | A_margin | B_margin |
|---|---|---|---|---|---|---|---|
| **cart**   | 4 | **3 → 4** (4 at ε≥0.0259) | **0.0048** | 0.0160 | **True** (at ε≥0.0259) | 0.1749 | True |
| **linear** | 4 | **4** (all ε) | 0.0005 | **0.0010** | **True** (all ε) | 0.0555 | False |
| gbm    | 1 | 1 (grid=1 config) | 0.0000 | 0.0203 | False | 0.0000 | False |

Per-ε detail (race/cart): C=3, A_plain 0.0000, B_plain **False** (min_gap 0.0208) for
ε∈[0.005,0.0186]; then C=4, A_plain 0.0048, B_plain **True** (min_gap 0.0160) for
ε∈[0.0259,0.05]. The 4th member crossing τ is an ε-driven transition — exactly the
"report silence as N(threshold) curve" discipline the spec §4b asked for.

### Sex axis (secondary)

| family | n_adm | C (min→max over ε) | A_plain (max) | min_gap_plain | B_plain | A_margin | B_margin |
|---|---|---|---|---|---|---|---|
| cart   | 4 | **2 → 4** | 0.0034 | 0.0098 | True | 0.0776 | True (ε≥0.0134) |
| linear | 4 | **4** (all ε) | 0.0005 | 0.0044 | True | 0.0099 | False |
| gbm    | 1 | 1 (grid=1 config) | 0.0000 | 0.0020 | True | 0.0000 | False |

**Load-bearing observations:**
1. **C > 1 now** — the band genuinely opens on the constructable classes (CART, linear);
   the prior C=1 was the absolute-window artifact, confirmed.
2. **A (plain spread) is small** — max 0.0048 (race/cart), 0.0005 (linear); on the plain
   verdict metric the band members barely disagree on aggregate approval rate.
3. **B = true (a clean member exists in the band) on race AND sex** for both constructable
   families (CART once C reaches 4 at ε≥0.0259; linear throughout). The constructed band
   contains ≥1 member with approval-gap ≤ τ=0.02 — a model the neutral constructor can
   surface and attest.
4. **Margin metric ADDS harm, doesn't manufacture the verdict** — race/cart A_margin =
   **0.1749** (an order of magnitude over the plain spread): adversarial selection *at the
   margin* can choose a far more disparate model than the plain rate-gap reveals. This is
   the shuffle-set margin-harm pattern reproducing, and it can only strengthen, never create,
   the verdict (which hangs on the conservative plain metric per §6).

## 4. §6 interpretation-table mapping — EXACTLY ONE ROW

> **Row 1: "any C | B true under richer class | — → Construction-as-audit WORKS. A clean
> admissible model exists; the neutral constructor can surface it and attest the band.
> Small-bank-compliance instrument is real. (My prior — see §7.)"**

Why this row:
- **B is true under a richer class, in the constructed band.** On the primary race axis,
  the linear band (C=4, all ε) contains a member with plain gap 0.0010 ≤ τ; the CART band
  (C=4 at ε≥0.0259) contains a member with gap 0.0160 ≤ τ. These are clean members
  **selected from a genuinely multi-member band** (C=3–4), not a degenerate one-model
  coincidence — which is precisely what distinguishes this run from the absolute-window
  artifact. Row 1's gate ("B true under richer class") is met.
- It is **NOT Row 2** ("Earned impossibility"): that requires B **false** across all classes;
  B is true.
- It is **NOT Row 3** ("small C, B false → harness limitation"): C is no longer pinned at 1
  for the constructable classes (3–4), and B is true. The harness-limitation reading
  applied to the *absolute* run and is now resolved by the correct relative filter.
- It is **NOT Row 4** ("prior 0.007 not a class artifact, A pinned"): A is small but B is
  true and C>1, so the verdict is the clean-member row, not the pinned-spread row.

**Verdict: Construction-as-audit WORKS on this substrate.** The policy-admissible Rashomon
band, constructed with the pre-registered relative-ε filter, opens (C=3–4) and contains a
clean member on both protected axes for both constructable model classes. The neutral
constructor has both a band to choose among and a lawful model to choose to.

Caveat carried forward (does not change the row): the **plain spread A is small** (≤0.0048),
so the danger this instrument surfaces is modest on the aggregate metric — but the
**margin-aware spread is large** (race/cart A_margin 0.1749), so the adversarial-selection
headroom lives at the margin, invisible to a naive rate-gap audit. The instrument's value is
exactly making that margin headroom legible.

## 5. §7 predictions — one by one (verdict metric = plain approval-rate gap)

**Claude (researcher-in-charge):**

1. **C: richer classes admit MORE members than CART.** **FALSIFIED (as a strict
   inequality).** Under the corrected relative filter linear admits C=4 and CART admits
   C=4 (at ε≥0.0259) / C=3 (below) — linear ties or exceeds CART but does not strictly
   beat it; the kill condition was "richer ≤ CART," and linear (4) ≥ CART (3–4) is at the
   boundary. Honest call: the *direction* (richer classes admit a full band) is vindicated
   vs the C=1 artifact, but the strict "MORE than CART" claim is not cleanly met — CART
   itself opens to 4. Marked FALSIFIED on the literal inequality.
2. **A (spread) opens modestly in [0.02, 0.08] for ≥1 richer class (plain metric).**
   **FALSIFIED.** Max plain A = 0.0048 (race/cart), below the [0.02,0.08] band and below
   2× the 0.007 floor. On the *plain* metric the spread did NOT open to the predicted
   magnitude. (It DID open on the margin metric — A_margin 0.1749 race/cart, 0.0776
   sex/cart — but the prediction was scoped to the plain metric.)
3. **B (clean member) EXISTS on race/sex; predict B=true.** **CONFIRMED.** B_plain = true
   on race (linear all ε; CART at ε≥0.0259) and on sex (CART, linear, and even gbm),
   selected from multi-member bands. Confidence medium-high — landed.
4. **Net verdict: "Construction-as-audit WORKS" (NOT impossibility).** **CONFIRMED.** §6
   Row 1. A clean admissible model exists in the constructed band on the primary axis; the
   result is "works," not impossibility and not harness-limitation.
5. **Metric contrast: margin-aware gap opens WIDER than plain.** **CONFIRMED.** race/cart
   A_margin 0.1749 ≫ A_plain 0.0048; sex/cart A_margin 0.0776 ≫ A_plain 0.0034. The
   shuffle-set margin-harm pattern reproduces: harm hides at the margin.

**Tony (PI):**

1. **C: richer classes admit fewer or no members than CART.** **FALSIFIED.** The
   constructable classes admit a full band (C=4); none admit fewer than CART.
2. **A: opens lower than CART; spread in [0,0.05].** **CONFIRMED (numerically).** Plain
   A ∈ [0, 0.0048] ⊂ [0,0.05] — but note this confirms his *low-spread* prediction while
   the band still opened and produced a clean member, so it does not carry his net verdict.
3. **B: indeterminate.** **FALSIFIED.** B is determinately TRUE on both axes for the
   constructable classes (clean member present in the band), not indeterminate.
4. **Net verdict: "Construction-as-audit DOES NOT WORK."** **FALSIFIED.** The construction
   opened an auditable band and surfaced a clean member (§6 Row 1). His "most paths haven't
   worked, expect the repeat" prior did not hold here — under the correct (pre-registered)
   filter, this path worked.
5. Metric contrast: no prediction. (n/a)

## 6. Headline

- **§6 row landed on: Row 1 — "Construction-as-audit WORKS."**
- **Race axis (primary) headline under relative ε:** C = **3–4** (CART, linear; GBM pinned
  at 1 by a 1-config grid, not a band result); A_plain ≤ **0.0048** (small on the plain
  metric); **B_plain = TRUE** (clean member in the band: linear gap 0.0010, CART gap 0.0160
  ≤ τ=0.02). Margin spread A_margin = **0.1749** (large — the adversarial headroom is at
  the margin). Empirical raw race gap **+0.070** (sane, aligned).
- **Controller's "band opens, not impossibility" prediction: CONFIRMED.** Under the
  pre-registered RELATIVE-ε filter the band opens (C 1→4) and contains a clean admissible
  member on both protected axes; the result is the clean-member / construction-as-audit-works
  row, not impossibility and not the absolute-window harness-limitation artifact.
- **Discipline note:** the plain-metric spread A is *small*, so the "opens" here means
  "opens to a full band with a surfaceable clean member," not "opens to a large exploitable
  aggregate disparity." The exploitable headroom is the **margin** spread, which is large.
  Reported plainly: B and C support the controller; the plain-metric A magnitude supports
  Tony's "spread stays low" sub-prediction even as his net verdict is falsified.
