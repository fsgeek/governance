# Empty-Support Inversion — Replication Pre-Registration

**Date:** 2026-05-09.
**Status:** Pre-registration. Predictions and pre-committed interpretations committed to git (and OTS-stamped) *before* the replication runs are generated. Any post-hoc reinterpretation is exactly the discipline failure this document exists to test against.
**Scope:** Replication of the empty-support inversion observed in `2026-05-09-tf-asymmetry-exploration-note.md` §6 across (a) a fresh LendingClub vintage (same substrate, fresh time period) and (b) the HMDA RI 2022 dataset already loaded but not yet run through the wedge (cross substrate). The 2×2 of (same-substrate-replicates, cross-substrate-replicates) is the informative output.
**Anchoring:** The §6 finding from the asymmetry note plus the procedural mechanism story articulated in this conversation: post-tightening regimes systematically lose articulable approval reasons because grant becomes the negative space (absence of risk flags) rather than a positively-attributed condition.

---

## 1. Why this exists

The 2026-05-09 V₁→V₂ predictive test missed P5 on its headline factor_support_T side. The companion T/F asymmetry exploration note found a richer mechanism (appearance × intensity decomposition) and incidentally surfaced a separate finding in §6: the empty-support inversion (V₁ T-empty 1.1% → V₂ T-empty 4.2%; V₁ F-empty 8.2% → V₂ F-empty 2.2%). The note flagged it as worth a fresh-vintage pre-registration but did not develop one.

The repeated pattern across pre-registrations so far (bin-4 case-reading; V₁→V₂ predictive test) is **miss → richer mechanism on the same dataset**. That pattern is either evidence of methodology-finding-capacity (the substrate is genuinely heterogeneous and each failed prediction sharpens the next) or of productive-miss bias (every observation gets framed into a flattering story). The two read identically on a single dataset; they diverge on replication.

This document writes a pre-registration **specifically designed to be losable**. The hit criteria are sharp; the pre-committed interpretations explicitly name what each miss-shape means; the same-substrate and cross-substrate predictions are independent enough that selective replication has a forced interpretation.

If P1, P2, and P3 all hit, the methodology has earned the productive-miss-pattern reading. If P1 misses, the V₁→V₂ empty-support read was vintage-specific cope. If P2 misses, the inversion is LC-specific and the substrate-independence claim fails. If P3 misses, the T/F asymmetry mechanism doesn't replicate as a structural property.

## 2. Vintages and datasets

- **V_fresh (LC) = 2016Q4.** One full year past V₂ (2015Q4), enough separation that any V₂-specific transition residue should have settled. LC public-loan-data goes through 2018Q4; 2016Q4 is mature post-tightening regime.
- **HMDA RI 2022.** Already loaded per `prototype-plan-2026-05-09.md` Days 1–2 (22,481 cases). Not yet run through the wedge. Cross-substrate test: HMDA's feature structure differs from LC, but the procedural-mechanism story predicts the inversion is a property of post-tightening regimes generally, not of LC specifically.

Neither dataset has been run through the wedge at the time of this pre-registration. The runs to be generated are net-new.

## 3. Anchoring claims

- **A1. The V₁→V₂ inversion was real and not a measurement artifact.** The asymmetry note's §6 numbers are correct; rerunning the empty-support computation on the existing V₁ and V₂ jsonl files reproduces (T₁=1.1%, F₁=8.2%, T₂=4.2%, F₂=2.2%) within rounding. *Verification owed before running the new runs:* re-execute the empty-support computation on existing data and confirm.
- **A2. Procedural mechanism: post-tightening regimes lose articulable approval reasons.** Tighter underwriting selects survivors who mostly look fine; what differentiates them is risk flags, not approval flags; trees articulate "DTI > X → deny-supports" sharply but increasingly leave grant-side leaves empty because grant is the absence-of-flags rather than a positive condition.
- **A3. The mechanism is not LC-specific.** It depends on (post-tightening selection of survivors) + (tree-based attribution that can return categorical absence). HMDA 2022 is post a sequence of tightenings (Dodd-Frank QM, post-2018 ATR refinements, post-COVID forbearance reset); RI 2022 is mature regime. The same substrate-structure (CART-derived factor support with both T and F leaves) applies once HMDA features are wedge-encoded.

## 4. Predictions

Each prediction has the form: *which quantity* shifts in *which direction* with *which magnitude threshold* on *which dataset*. Hit criteria are in §5.

### P1 — Empty-support inversion replicates same-substrate (LC 2016Q4)

- **Anchoring:** A2 (procedural mechanism). If the mechanism is real and the post-2015 regime is mature, V_fresh should exhibit the same inversion direction as V₂.
- **Prediction:** In LC 2016Q4, the T-side empty rate is **≥ 2.2%** (i.e., at least 2× V₁'s 1.1% baseline) AND the F-side empty rate is **≤ 4.1%** (i.e., at most 1/2 V₁'s 8.2% baseline). **Both legs must hold for hit.**
- **Confidence:** Moderate-high if the mechanism is correct. The 2× / 0.5× thresholds are deliberately weaker than V₂ values (4.2% / 2.2%) to allow for regression to the mean while still requiring the inversion-direction.
- **Mechanism-coherent stronger version (not the official prediction):** V_fresh T-empty between 2.2% and 8% (allowing for some growth but capping unbounded drift); V_fresh F-empty between 1% and 4.1%.

### P2 — Empty-support inversion appears cross-substrate (HMDA RI 2022)

- **Anchoring:** A3 (mechanism is not LC-specific).
- **Prediction:** In HMDA RI 2022 wedge run, the T-side empty rate **exceeds** the F-side empty rate by **≥ 1 percentage point** in absolute terms.
- **Confidence:** Moderate. HMDA features differ structurally from LC (no FICO directly, different income/DTI handling); the policy-tightening trajectory is also different. The prediction is the weaker structural claim — that any mature post-tightening regime exhibits *some* T > F empty-rate gap, not a specific magnitude.
- **Note on weakness:** This prediction is weaker than P1 by design because we cannot anchor to a within-HMDA prior baseline (no committed earlier-vintage HMDA run to compare against). A future pre-registration with two HMDA vintages would be a sharper test.

### P3 — T/F asymmetry replicates same-substrate (LC 2016Q4 vs LC 2015Q4)

- **Anchoring:** A2 + the asymmetry note's revised H2 (grant attribution responds to "how confidently a feature supports approval given the surviving distribution"; deny attribution responds to "how reliably a feature flags risk within the surviving distribution"; these are not symmetric channels).
- **Prediction:** For ≥ 2 of {dti, fico_range_low, annual_inc, emp_length}, the V₂ → V_fresh shift exhibits T/F asymmetry where asymmetry = (T-side and F-side shifts have opposite signs) OR (T-side and F-side shifts differ in magnitude by ≥ 2×).
- **Confidence:** Moderate. The mechanism predicts the asymmetry is structural; if so, it should appear across vintages within the same substrate. The 2-of-4 threshold is deliberately loose to test whether *any* of the headline features replicate, not whether all do.

## 5. Hit criteria

- **P1 hit:** Both legs hold (T-empty ≥ 2.2% AND F-empty ≤ 4.1%).
- **P1 partial-hit:** Exactly one leg holds. (Reported separately; does NOT count as a full hit.)
- **P1 miss:** Neither leg holds.
- **P2 hit:** T-empty − F-empty ≥ 1 percentage point in HMDA RI 2022.
- **P2 miss:** T-empty − F-empty < 1 percentage point (including negative values).
- **P3 hit:** Asymmetry holds for ≥ 2 of the 4 features.
- **P3 partial-hit:** Asymmetry holds for exactly 1 feature.
- **P3 miss:** Asymmetry holds for 0 features.

For each prediction, the comparison phase reports: hit/partial/miss, plus the actual measured numbers, plus a one-sentence interpretation drawn from §6 (no novel post-hoc interpretation permitted).

## 6. Pre-committed interpretations

This is the discipline addition relative to prior pre-registrations. Each (P1, P2, P3) outcome combination has a pre-committed interpretation that the findings note must use. **No post-hoc reinterpretation is permitted.** This forecloses the productive-miss-pattern by removing interpretive degrees of freedom.

| P1 | P2 | P3 | Pre-committed interpretation |
|---|---|---|---|
| Hit | Hit | Hit | Empty-support inversion is methodology-real: vintage-stable AND substrate-independent AND mechanistically reproducible. Productive-miss read on the V₁→V₂ note was earned. |
| Hit | Hit | Miss | Empty-support inversion replicates structurally but the T/F-asymmetry-on-features story does not. The asymmetry note's §3 mechanism was over-fit to V₁/V₂; only the §6 finding is methodology-real. |
| Hit | Miss | Hit | Empty-support is LC-stable but LC-specific. Substrate-independence claim fails; the methodology produces vintage-stable findings within a substrate but does not generalize. |
| Hit | Miss | Miss | Same as above; LC-specific finding only. |
| Miss | Hit | Hit | V₁→V₂ empty-support reading was vintage-specific (2015Q4 captured an unusual transition residue not present in 2016Q4) but the mechanism appears in HMDA. The V₁→V₂ productive-miss read was over-fit. |
| Miss | Hit | Miss | Same as above; the only surviving claim is HMDA-specific. |
| Miss | Miss | Hit | Empty-support inversion was V₁→V₂-specific cope. The T/F-asymmetry-on-features story replicates within LC but the headline §6 finding does not. |
| Miss | Miss | Miss | Empty-support inversion was V₁→V₂-specific cope; T/F asymmetry was V₁→V₂-specific; both productive-miss reads were over-fit. The methodology has not earned the productive-miss-pattern reading on this evidence. |

The (Hit, Hit, Hit) outcome is the only one that vindicates the productive-miss-pattern reading. Five of the eight outcomes constitute substantive disconfirmation of one or more prior claims.

## 7. Comparison protocol

1. **Pre-flight:** Re-execute the asymmetry note's §6 empty-support computation on `runs/2026-05-08T17-43-21Z.jsonl` (V₁) and `runs/2026-05-08T17-44-39Z.jsonl` (V₂). Confirm reproducibility of (1.1%, 8.2%, 4.2%, 2.2%) within ± 0.5 percentage points. If pre-flight fails, halt and re-examine A1.
2. **Generate V_fresh run:** Run the wedge on LC 2016Q4 with the same configuration as V₁/V₂ runs (same R(ε) construction, same feature pool, same hyperparameters). Commit the resulting jsonl + meta.json to `runs/`.
3. **Generate HMDA run:** Run the wedge on HMDA RI 2022 with the policy-encoder and feature mapping per `policy/encoder.py`. Commit the resulting jsonl + meta.json to `runs/`.
4. **Compute empty-support rates:** For V_fresh, compute T-empty and F-empty fractions at the (case, R(ε)-member) pair level. For HMDA, same. For V₂ → V_fresh, compute the appearance × intensity decomposition for the four headline features (replicating the asymmetry note's §3 method).
5. **Classify:** Apply §5 hit criteria; identify the 8-row §6 outcome row; copy the pre-committed interpretation verbatim into the findings note.
6. **Findings note:** State outcome row, numbers, pre-committed interpretation. No additional novel interpretation. Reference any unexpected sideways findings as "exploratory follow-up candidates" without promoting them to interpretation of P1/P2/P3.

## 8. Honest caveats

- **Pre-flight verification of A1 is owed.** The (1.1, 8.2, 4.2, 2.2) numbers come from the asymmetry note. If that note's computation had a bug, the entire baseline structure is wrong. Pre-flight is the cheap fix.
- **HMDA wedge encoding is itself novel.** The wedge has not been run on HMDA before (per plan-doc Day 1–2). The first HMDA run is therefore a methodology-development step as well as a prediction test. If the encoder produces obviously broken factor-support outputs (e.g., one R(ε) member contributes zero attributions across all cases), the run is invalid and P2 cannot be classified. *Encoder-validity check is part of the comparison protocol.*
- **Mechanism A2 is not externally verified.** The procedural-mechanism story (grant becomes negative space because survivors look fine) is a hypothesis derived from this conversation, not from the explanation literature. A clean (Hit, Hit, Hit) outcome is consistent with A2 but does not establish A2 as the mechanism — alternative mechanisms (CART tree depth interactions; class-imbalance-shift artifacts; species/feature-pool drift across vintages) would also produce the inversion.
- **N=1 fresh vintage and N=1 cross-substrate dataset are still thin.** Even (Hit, Hit, Hit) does not establish methodology-general predictive content; only its presence on these specific runs. Replication across additional vintages (LC 2017Q4, 2018Q2) and additional cross-substrate datasets (Fannie Mae once available) is owed for any general claim.
- **The pre-committed-interpretation table is itself a discipline experiment.** Prior pre-registrations did not pre-commit interpretations. Whether this stronger form is wise (forecloses real surprises) or unwise (forecloses productive-miss cope) is itself an open question this document instances.

## 9. What this document does NOT do

- Does not run the comparison. The comparison is the next step.
- Does not commit to dates. The runs require new wedge invocations and HMDA encoder validation; both are bounded but not pre-scheduled.
- Does not pre-commit to follow-on predictions if (Hit, Hit, Hit) lands. Follow-on predictions (cross-Fannie-Mae, multi-vintage HMDA) would be designed at that point.
- Does not address the SHAP/LIME-non-inferior null. That is a separate test (Null A or Null B from the conversation residue); this pre-registration is about whether the empty-support finding is real before it is worth comparing against SHAP/LIME at all.

## 10. Connection to other working documents

- **`2026-05-09-tf-asymmetry-exploration-note.md` §6.** The empty-support inversion finding this document tests for replication. Verdicts of that note remain unchanged regardless of this test's outcome (per pre-registration discipline; that note's findings are about V₁/V₂ specifically).
- **`2026-05-09-v1-v2-predictive-test-pre-registration.md` and `-findings-note.md`.** The pre-registration discipline pattern this document inherits and extends (with pre-committed interpretations, a stronger form).
- **`2026-05-08-bin4-k5-case-reading-findings-note.md`.** The earlier instance of the discipline pattern. The pre-prediction (12-15 / 5-8 / 1-3) → observed (2 / 11 / 7) failure is the worked precedent for "the prediction was the prediction; the discipline made the failure honest."
- **`prototype-plan-2026-05-09.md` Days 3–5 and beyond.** This pre-registration's runs feed the policy-aware Rashomon constructor work; if (Hit, Hit, Hit) lands, the empty-support metric becomes a methodology-output worth showing in the Olorin briefing.
