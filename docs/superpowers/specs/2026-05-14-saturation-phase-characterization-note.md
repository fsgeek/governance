# FM saturation phase structure & carrier-family asymmetry — post-hoc

**Date:** 2026-05-14. **Status:** POST-HOC characterization, NOT pre-registered. **Substrate:** `runs/silence_manufacture_2026-05-13.json` (#12 saved data). **Script:** `scripts/saturation_phase_characterization.py`. **Output:** `runs/saturation_phase_characterization.json`. **Companion to:** `2026-05-14-root-tier-substrate-independence-addendum.md` (5:50 AM same day, which observed "~50% property_state penetration" in the 2 reorganized-but-agreeing cells). **Connects:** `[[project_silence_manufacture_result]]`, `[[project_pragmatics_linguistics_lens]]`, `[[project_ontology_design_philosophy]]`.

**Why post-hoc, not pre-reg:** the 5:50 AM addendum disclosed the ~0.50 penetration in 2 of the 5 reorganized cells. That contaminates a pre-registered prediction of the continuous saturation→divergence joint. This note characterizes the full distribution honestly, labeled.

---

## 1. Question

Two threads collapsed into one analysis when I started looking at the saved data:

- **(A)** Is the property_state→silence relationship continuous-monotone, knife-edge-thresholded, or something else? (My initial naive expectation, now answered.)
- **(B)** Does `prohibited_3_saturation_A` (union of geographic + 2 institutional carriers) predict silence equivalently to `property_state_saturation_A` alone? (The Paper 2 schema implication: is the prohibition-list slot homogeneous or carrier-family-distinct?)

---

## 2. Finding (A): three-phase structure with gaps, not continuous

Sorting the 29 cells by `property_state_saturation_A`:

| Phase | sat_ps range | n | reorg | silence | cells |
|---|---|---|---|---|---|
| **0** (no reorganization) | `[0.00, 0.45]` | 24 | 0/24 | 0/24 | all three vintages |
| **1** (reorganized, verdict-agrees) | `[0.50, 0.55]` | 2 | 2/2 | 0/2 | 2016Q1 rb03, 2008Q1 rb08 |
| **2** (manufactured silence) | `= 1.00` | 3 | 3/3 | 3/3 | 2016Q1 rb00, rb05, rb09 |

**Sharp gaps:** 0.45 (2008Q1 rb09, the highest non-reorganized cell) → 0.50 (2016Q1 rb03, the lowest reorganized cell). And 0.55 (2008Q1 rb08, the highest agreeing cell) → 1.00 (2016Q1 rb00, the lowest silence cell). No cell lies in the half-saturated-but-not-half regions in between.

**Jaccard tracks the same trimodality:** ~1.0 in phase 0, ~0.33 in phase 1, 0.0 in phase 2. The three phases are *jointly* visible on the saturation axis and the Jaccard axis.

**Implication.** The previous #12 P2 binary classifier with cutpoint at 0.50 captured the phase 0 ↔ phase 1+2 boundary. It missed the phase 1 ↔ phase 2 boundary at 1.00. The silence-manufacture mechanism is not "high saturation" — it is *complete* saturation. Half-saturation reorganizes but does not silence.

**Caveat.** n=2 in phase 1 and n=3 in phase 2. The "sharp gaps" claim rests on the absence of cells in `(0.55, 1.00)` from this 29-cell sample. Replication on additional vintages (or substrates) is the obvious next step before claiming this is a structural property of the mechanism.

---

## 3. Finding (B): institutional carriers (seller/servicer) do not participate

Marginal Spearman ρ with `|R²_A − R²_B|` (verdict-divergence magnitude):

| Predictor | ρ |
|---|---|
| `property_state_saturation_A` | **+0.585** |
| `prohibited_3_saturation_A` | +0.450 |

But the two predictors are themselves highly correlated (ρ = +0.827). After partial-Spearman residualization:

| Conditional ρ | value |
|---|---|
| property_state \| prohibited_3 → r²_gap | **+0.424** |
| prohibited_3 \| property_state → r²_gap | **−0.074** |

Once you control for property_state saturation, prohibited_3 contributes nothing to predicting verdict-divergence. The unconditional 0.450 is leakage from property_state.

**The direct evidence is sharper than the partials.** On all 5 reorganized cells (the 2 agreeing + 3 silenced), `prohibited_3 ≡ property_state` exactly (carrier-gap = 0). The seller_name / servicer_name penetrations contribute *zero* additional saturation on the cells where reorganization happens.

On the 24 non-reorganized cells, seller/servicer can saturate quite high without inducing reorganization:

| Cell | sat_ps | sat_p3 | carrier_gap | r²_gap |
|---|---|---|---|---|
| 2018Q1 rb06 | 0.30 | 0.67 | +0.37 | 0.021 |
| 2018Q1 rb08 | 0.08 | 0.49 | +0.41 | 0.066 |
| 2018Q1 rb03 | 0.00 | 0.40 | +0.40 | 0.026 |
| 2018Q1 rb07 | 0.18 | 0.57 | +0.39 | 0.038 |
| 2008Q1 rb07 | 0.08 | 0.44 | +0.36 | 0.003 |

Seller/servicer saturation in the 0.4-0.7 range produces r²_gaps under 0.07. Property_state saturation at 0.50 produces r²_gap ≈ 0.40. The two carrier families behave asymmetrically under prohibition.

---

## 4. Regime asymmetry

| Vintage | n | property_state ρ vs r²_gap | prohibited_3 ρ vs r²_gap |
|---|---|---|---|
| 2008Q1 (crisis) | 10 | **+0.588** | +0.224 |
| 2016Q1 (expansion) | 10 | **+0.865** | +0.865 |
| 2018Q1 (normal) | 9 | −0.202 | +0.100 |

- **2016Q1**: both predictors equally good, because the high-saturation cells dominate and the two predictors converge there.
- **2008Q1**: property_state strongly beats prohibited_3, because mid-saturation crisis cells separate the two predictors and only property_state's signal is real.
- **2018Q1**: neither predictor works — but 2018Q1 has zero reorganized cells, so there's no silence to predict. The negative ρ for property_state is noise.

All 3 manufactured-silence cells are 2016Q1, replicating the `[[project_silence_manufacture_result]]` finding that manufactured silence is an expansion-regime fingerprint in this corpus. The 2 reorganized-but-agreeing cells split between 2016Q1 and 2008Q1, so the phase-1 phenomenon spans regimes; only phase-2 silence-manufacture is regime-localized in this sample.

---

## 5. Schema implications (Paper 2)

The previous (`[[project_silence_manufacture_result]]`) finding suggested the codification schema needs a `(variant-context, reorganization-flag, verdict-pair)` tuple. This characterization sharpens the reorganization-flag slot:

1. **The reorganization-flag should encode the phase, not a binary.** Three discrete phases (no-reorg, reorg-agreement, reorg-silence) carry different consequences for single-variant artifact reporting:
   - Phase 0: single-variant reporting is adequate.
   - Phase 1: single-variant reporting is *under-explanatory* (the variant choice picks one of several admissible stories) — surface the variant-context.
   - Phase 2: single-variant reporting is *manufacturing silence* — require dual-variant reporting.

2. **The prohibition-list slot is not carrier-family-homogeneous.** Geographic-context carriers (property_state) drive reorganization; institutional-relationship carriers (seller_name, servicer_name) do not, even at moderate saturation. The codification artifact's prohibition list should be annotated with carrier-family, and the silence-manufacture detector should operate carrier-family-by-carrier-family — not on the aggregate prohibition saturation.

3. **The pragmatics analogy (`[[project_pragmatics_linguistics_lens]]`) is empirically reinforced.** Different prohibition slots have different pragmatic indexicality: geographic-context is the indexical that varies under prohibition; institutional-relationship is informationally redundant with named features (and so its prohibition is "censorial" rather than "reorganizational"). The codification layer should formalize this carrier-family distinction.

---

## 6. Limits

- **n = 29 cells, all FM, all 36-month observation.** Three vintages. The trimodal structure could be sampling artifact at this n — but each phase has within-vintage replicates of the structural property (phase 1 spans 2008Q1 and 2016Q1; phase 0 covers all three vintages).
- **Phase boundaries are post-hoc.** The 0.45→0.50 and 0.55→1.00 gaps are not pre-registered cutpoints; they emerge from the empirical distribution. Replication on additional vintages or HMDA/HARP would test whether the gaps survive.
- **Carrier-family asymmetry rests on 5 reorganized cells.** Property_state appears as the lone driver in this sample; another substrate could produce reorganized cells where seller/servicer participate. The claim is about *this corpus*, not about a structural law.
- **Phase 1 vs phase 2 mechanism difference is not characterized here.** Why does sat_ps = 0.50 reorganize without silencing, while sat_ps = 1.00 silences? The natural next investigation: at sat_ps = 0.50, variant-B has an unrestricted half of A's ufs to reconstruct a parallel story; at sat_ps = 1.00, no such reservoir exists. But this story is hand-waving until tested. The root-tier discriminator (5:50 AM addendum) catches the phase-2 boundary cleanly (3/3) and not the phase-1 boundary (0/2) — consistent with this story but not validating it.

---

## 7. Followups (ranked by what would change the picture)

1. **Replicate the trimodal structure on a new substrate or new FM vintages.** If the phase boundaries hold (gaps at ~0.5 and ~1.0), the schema needs the three-state encoding. If the phases blur, the binary reorg flag is fine. Substrates: HMDA-RI 2022 is already preprocessed and untouched.
2. **Carrier-family generalization.** Add `seller_name_saturation_A` and `servicer_name_saturation_A` as separate columns in the silence-manufacture pipeline (a small extension to `silence_manufacture_test.py`), and re-run on a substrate where institutional carriers may dominate. The current 5-cell evidence for property_state-only-participation is from one substrate, one prohibition setup.
3. **Phase 1 mechanism characterization.** What does variant-B's restricted band look like when half of variant-A's ufs use property_state? Is it the unrestricted half, or a genuinely different reconstruction? This is the question that distinguishes "reorganized-but-agreeing" from "censored." Disagreement-explainer trees on rb03 and rb08 would answer it.
4. **Pre-reg a NEW substrate before peeking.** Given the contamination-discipline issue, the next move on this thread should be HMDA — where no one has yet looked at the saturation distribution. Pre-register: HMDA cells with sat_ps ≥ 0.99 should show R²_gap ≥ 0.3; cells with sat_ps < 0.45 should show R²_gap < 0.1.
