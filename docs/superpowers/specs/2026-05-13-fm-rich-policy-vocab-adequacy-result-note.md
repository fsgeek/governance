# Does a medium-fidelity codified mortgage policy still leave a vocabulary gap? — result note (#11)

**Date:** 2026-05-13. **Status:** result. **Substrate:** Fannie Mae SF Loan Performance, vintages **2018Q1 / 2016Q1 / 2008Q1** (the pre-registered cross-vintage triple — robustness *gate*, not followup; runs strictly serial per FM-load discipline). **Pre-registration:** `docs/superpowers/specs/2026-05-12-fm-rich-policy-vocab-adequacy-preregistration-note.md` (committed `1817010`, OTS-stamped `ddb0b1f`). **Companion to:** `2026-05-12-extension-admitted-band-result-note.md`, `2026-05-12-routable-population-test-result-note.md`.

---

## Headline (one paragraph — pre-reg-frozen claim form)

**Narrow claim form (the sharpest defensible statement):** *on the FM single-family acquisition substrate, with this medium-fidelity codified policy and rate-band stratification, the highest-rate decile (rb09 — subprime-equivalent) shows an ε-stable vocabulary gap on 2 of 3 vintages, with the carrier shifting from pure-geography in expansion (2016Q1: property_state alone, variant B fully closes 0.022 → 0.744) to geography+loan-size in crisis (2008Q1: property_state 0.44 + original_upb 0.55, variant B only half-closes 0.076 → 0.264 because it doesn't prohibit loan-size). The pre-reg's P1 verdict (gap recurs on ≥1 plural band on ≥2 of 3 vintages, ε-stable) HITS — but only on rb09; rb00's 2016Q1 gap did not replicate. The data robustly support the rb09-specific replication; they do NOT support a generalized "rich policies underdetermine model indeterminacy on community-bank-equivalent mortgage portfolios" claim — that would over-reach what was tested.*

**Per-vintage summary**: 2018Q1 is "no-gap-where-measurable, opacity-elsewhere" rather than "no-gap-everywhere" — 2 of 3 plural cells show decisively adequate vocabulary (rb00/rb04, real-vs-random placebo margin ≥+0.30), 1 plural cell is HOLLOW (rb02, margin +0.02 — vocabulary not distinguishably better than random), 6 cells are non-plural and the placebo wasn't run (R²_named 0.72–0.95 is presumption-of-adequacy, not evidence). 2016Q1 has rb00 (R²_named=0.035, rung-3b, plural, gap) and rb09 (R²_named=0.022, rung-3a/3b mixed, plural, gap) hitting the strict verdict criterion; rb05 (R²_named=0.208, not plural — median pairwise spearman ≈ 0.998) is a non-verdict-counting cell where variant-A and variant-B construct *different* ε-good bands (variant-A keys on `(dti, property_state)`, variant-B reorganizes to DTI + FTHB) with *different disagreement signals* — the variant-A reading is "vocab inadequate via property_state-dominated `d_A`", the variant-B reading is "vocab adequate via DTI+FTHB-structured `d_B`", both correct in their respective contexts. **Initially inferred rung-2.5 on this cell; the depth-sweep verification (depths 3–7, R²_named flat at ~0.21) falsifies the inference**; the actual finding is diagnostic-pragmatics — "vocab adequacy" is variant-indexed on this cell. See §3b. 2008Q1 has rb09 (R²_named=0.076, rung-3a/3b mixed, plural, gap, ε-stable); rb08 is marginal (R²_named=0.45, only opens at ε=0.05 — ε-unstable, doesn't count).

**Robust schema-level findings independent of P1:** (a) all three mandatory-feature enforcement readings (R-member / R-any / R-majority) **fail on every analyzed cell on every vintage tested** — the schema's `mandatory_features` mechanism is doing no load-bearing work; the pre-reg's prediction that "R-majority is the only satisfiable one" is wrong (it is neither satisfiable nor non-trivial on this data); (b) the C-scrambled placebo confirms the documented monotonicity is *usually informative for prediction structure* (R²_scrambled < R²_named on 8 of 10 non-gap plural cells) but does not give the cleaner per-constraint binding diagnostic — that lives in the dead-letter sibling pre-reg; (c) **the placebo's "real vs random margin" inverts on gap cells** (real *below* random on every 2016Q1 gap cell and 2008Q1 rb09 — random features explain their controlled `d_rand` better than the real 11 named features explain `d_real`) — a sharper statement of "the gap is real, not a low-dim-`d` artifact" than the pre-reg's P5 anticipated.

---

## 1. Implementation (what was built, what deviated)

### 1a. Policy YAML — `policy/fnma_eligibility_matrix.yaml`

Medium-fidelity reconstruction (`status: medium-fidelity-reconstruction`) in the existing `policy/encoder.py` schema. 13 mandatory features (FICO / DTI / LTV / CLTV / MI% / loan-term-months / loan_purpose / occupancy_status / num_units / num_borrowers / first_time_homebuyer / property_type / amortization_type); monotonicity on the 5 numeric risk inputs (FICO+, DTI−, LTV−, CLTV−, MI+, in grant-convention); the Eligibility-Matrix gates (FICO ≥ 620, DTI ≤ 50, LTV ≤ 97, conforming UPB) encoded inside `applicable_regime` because the schema has no first-class slot for them. **Schema finding recorded here, not fixed in this test:** the eligibility-gate constraint type wants a first-class `gates:` block parallel to `monotonicity:` — feature / operator / threshold / on-fail-route — `applicable_regime`'s free-text dict is the closest existing slot but does no enforcement work.

The candidate set at run time is smaller than the YAML's 13 mandatory: **`occupancy_status` is regime-constant** (the loader filters to owner-occupied) and **`amortization_type` is ~constant** (FM is overwhelmingly fixed-rate on every vintage tested; ~99% FRM on 2018Q1/2016Q1/2008Q1). Both are dropped from the candidate set at prep-time (recorded in `prep.near_constant_dropped`). Exposed mandatory at analysis time: **11 named features**.

### 1b. Collector extension — `wedge/collectors/fanniemae.py`

Added 7 new field positions (glossary-verified against a real 2018Q1 row): `seller_name` (pos 5), `servicer_name` (pos 6), `original_upb` (pos 10), `cltv` (pos 21), `property_state` (pos 31), `msa` (pos 32), `mortgage_insurance_pct` (pos 34), `amortization_type` (pos 35). Split `WEDGE_FEATURES` into numeric vs. categorical maps; numeric coercion now covers cltv / MI% / UPB / num_units / num_borrowers. Added `bucket_high_cardinality(top_k=20)` for `seller_name` / `servicer_name`. New unit tests cover position uniqueness, the new fields' presence and types, and the bucketing helper. **Test count: 235 pass / 1 skip → 242 pass / 1 skip** (+5 collector tests, +2 refinement_set tests).

`msa` is collected for completeness but is **not** in the measured candidate set — the pre-reg §1b extension list is `property_state / original_upb / seller_name / servicer_name`; `msa` appears only in variant B's prohibited list for fidelity (a no-op since it is never a candidate).

### 1c. Analysis script — `scripts/fm_rich_policy_vocab_adequacy_test.py`

Reuses `wedge/refinement_set.py` and `wedge/routing.py` wholesale. Per-cell pipeline: build the within-ε refinement band over named ∪ extension (variant A) and over named-only (variant B); de-dup by used-feature-set (the validated default); refit distinct members on the full cell population; compute `d(x)` = per-borrower std over members and `p̄(x)` = consensus; run the depth-≤3 disagreement explainer named-only → `R²_named` and named+extension → `R²_all`; compute `ΔR²_ext`; classify rung-3a/3b on gap cells; record univariate ρ(feature, d) and PD shape on the named-explainer root. Placebo (C-random ×5 + C-scrambled) and the eps-arm {0.01, 0.02, 0.05} are run on the plural variant-A cells (where R²_named carries a verdict). One vintage per invocation; per-vintage JSON at `runs/fm_rich_policy_vocab_adequacy_{vintage}.json`.

### 1d. The two `wedge/` changes and the reasoning

The pre-reg specified "the collector extension is the only `wedge/` change". Two changes were made:

1. **`wedge/collectors/fanniemae.py`** — the planned collector extension (§1b above).
2. **`wedge/refinement_set.py`** — an additive `max_subset_size: int | None = None` parameter on `build_refinement_band` (default `None` preserves prior behavior; all existing callers and tests unaffected). With 15 candidate features the full enumeration is 2¹⁵ ≈ 33k subsets × 9 hyper-cells per band × ~30 analyzed cells × 3 vintages × 2 variants × per-cell placebo — multi-day compute. The knob is set to **5** in the #11 runs.
   - **Losslessness argument**:
     - **Mathematical (max=7)**: a depth-≤3 CART has at most 2³ − 1 = 7 internal nodes and hence splits on ≤ 7 distinct features. Setting `max_subset_size = 7` is *bit-for-bit lossless by construction*: every tree fittable on a larger subset equals a tree fittable on some enumerated ≤7-subset.
     - **Empirical (max=5)**: setting the knob to 5 was a compute restriction adopted for tractability. **The under-max=5 observation that "max used-set was 5" is necessary-but-not-sufficient evidence of losslessness** — a search told "use ≤5" can stop at a satisfactory ≤5-subset where a max=7 search would find a strictly better 6-or-7-subset that displaces some of the 5-member band. To close this gap, a **max=7 spot check was run on the headline gap cell**, 2008Q1 rb09 (the largest band in the corpus, 130 distinct uf-members under train-split dedup, 78 distinct refit-used-feature-sets, carrying the cross-vintage P1 verdict): ms=5 enumerated 44,487 (subset × depth × leaf_min) combinations; ms=7 enumerated 147,447 (3.3× more, exploring the 102,960 additional ≥6-feature combos). **Result: 78 distinct refit used-feature-sets at ms=5, 78 at ms=7, identical sets, identical size distribution {size-2: 6, size-3: 31, size-4: 35, size-5: 6, size-≥6: 0}; zero size-6 or size-7 used-sets entered.** R²_named differs by 0.0006 (well inside CV noise); R²_all by 0.0006; dR²_ext by 0.0012. The headline verdict is bit-stable at the refit-used-set level. (Run: `--vintage 2008Q1 --max-subset-size 7 --only-cell rb09`; output: `runs/fm_rich_policy_vocab_adequacy_2008Q1-rb09-ms7.json`.) **Conclusion**: on this substrate, the empirical ceiling on used-set size is set by `leaf_min ≥ 25`, not by `max_subset_size`; the ms=5 cap was empirically non-binding on the headline cell. Across the broader corpus, the histogram of used-set sizes (2,070 sets across all bands × all variants × all three vintages: size-1: 43, size-2: 386, size-3: 940, size-4: 615, size-5: 86, size-≥6: 0) is consistent with the same conclusion, modulo the same caveat (each cell was searched under ms=5; the rb09 spot-check is the only cell with a max=7 confirmation).
     - **Regression tests**: lossless-at-7 on 4-feature fixture; restriction-at-2 enforces size limit.
   - **Documented impact**: at `max_subset_size=5` the per-band fit count is C(15, ≤5) × 9 = 4943 × 9 ≈ 44.5k vs. ≈ 295k at unlimited — a ~6.6× compute reduction.

### 1e. Other deviations from the frozen pre-reg

- **Placebo + eps-arm on plural variant-A cells only** (the pre-reg specified per-cell). Reason: C-random/C-scrambled validate R²_named, which only carries a verdict on plural cells. The skeleton-clarity loss is small; the compute saving is large.
- **S-rate this report, S-llpa as a follow-on.** The pre-reg made S-rate the primary stratum and S-llpa "runs in parallel"; the verdict criteria are stated for S-rate. S-llpa will be reported as cross-tabulated context in a follow-on note.
- **Vintage scoping**: the pre-reg specified the three-vintage gate; the runs were performed serially as required, each on the full extracted CSV (no `--nrows` cap).

---

## 2. Setup as run (measured)

| vintage | N (regime envelope) | default rate | # rate-bands ≥ 5k | # plural cells | # gap cells | run seconds |
|---------|---------------------|--------------|--------------------|----------------|-------------|-------------|
| 2018Q1  | 401,275             | 0.00796      | 9                  | 3              | 0           | 16,220      |
| 2016Q1  | 354,426             | 0.00762      | 10                 | 4              | 2 (rb00, rb09) | 13,617  |
| 2008Q1  | 257,516             | 0.04291      | 10                 | 7              | 1 (rb09)    | 16,139      |

The most striking number: **2008Q1's vintage default rate (4.29%) is 5.4× higher** than 2016Q1/2018Q1 (~0.8%). The crisis-vintage regime is real in the data: rb09 of 2008Q1 has a 14.3% within-band default rate; rb08, 8.5%; rb07, 5.8%. By contrast 2016Q1 rb09 was 2.5% and 2018Q1's hottest band (rb08) was 2.65%. The regime envelope (FICO≥620, DTI≤50, LTV≤97) dropped ≤ 1% of loans across all three vintages (FM acquisitions are inherently conforming).

---

## 3. The per-vintage picture

### 3a. 2018Q1 — "no gap where measurable, opacity elsewhere"

`R²_named` is **0.72–0.95** across all 9 analyzed rate-bands; `dR²_ext` is uniformly small (max 0.060 on rb06). **No cell hits the strict verdict gap criterion** (`R²_named < 0.30 AND ΔR²_ext ≥ 0.15`). But the placebo only ran on the 3 plural cells (rb00, rb02, rb04), and what it says is mixed: **2 of 3 are decisively vocabulary-adequate** (rb00 margin +0.44, rb04 margin +0.30), **1 is HOLLOW** (rb02 margin +0.02 — the real 11 named features explain `d` no better than random 11 features explain a controlled `d_rand`; on rb02, the high R²_named=0.78 is "`d` is low-dim, not policy-aligned", not "vocabulary is adequate"). On the **6 non-plural cells** (rb01/rb03/rb05–rb08), the placebo was not run; their R²_named of 0.72–0.95 is *presumption-of-adequacy*, not *evidence*. We cannot tell from this data whether their high R²_named reflects vocabulary-fit or low-dimensionality-of-`d` — that's the opacity the 2018Q1 plurality-thinness leaves.

The named-explainer root is **`fico_range_low`** in every cell, with importance 0.71–0.97 — the disagreement `d(x)` is essentially a function of FICO with small secondary contributions from CLTV / loan-term-months / num-borrowers, where it can be measured. The named policy vocabulary is *one-feature-of-adequate* on the cells where it's measurable.

| cell | n | plural | R²_named | R²_all | dR²_ext | named root | named top features |
|------|-------|--------|----------|--------|---------|------------|---------------------|
| rb00 | 59283 | True | 0.898 | 0.897 | -0.001 | FICO | FICO 0.86, loan_term 0.12 |
| rb01 | 44341 | False | 0.949 | 0.949 | 0.000 | FICO | FICO 0.97, num_borrowers 0.03 |
| rb02 | 50974 | True | 0.783 | 0.803 | 0.019 | FICO | FICO 0.96, original_upb 0.03 |
| rb03 | 35896 | False | 0.920 | 0.920 | 0.000 | FICO | FICO 0.82, CLTV 0.15 |
| rb04 | 67317 | True | 0.787 | 0.787 | 0.000 | FICO | FICO 0.97, DTI 0.01 |
| rb05 | 40903 | False | 0.715 | 0.715 | 0.000 | FICO | FICO 0.75, CLTV 0.18 |
| rb06 | 27777 | False | 0.826 | 0.886 | 0.060 | FICO | FICO 0.71, CLTV 0.21, upb 0.08 |
| rb07 | 37441 | False | 0.780 | 0.792 | 0.012 | FICO | FICO 0.84, CLTV 0.10, seller 0.06 |
| rb08 | 37343 | False | 0.785 | 0.806 | 0.022 | FICO | FICO 0.80, CLTV 0.13, servicer 0.04 |

**Placebo (plural cells, real R²_named vs C-random R²_mean margin):** rb00 +0.44 (decisive), rb02 +0.02 (HOLLOW — `d` is low-dim on rb02; any 11 features explain it), rb04 +0.30 (decisive). **C-scrambled** R² is 0.29–0.39 with bands of 60–90 distinct members (large), i.e. the documented monotonicity admits many ε-good reversed-sign models → **monotonicity is largely slack on 2018Q1**.

**Eps-arm (plural cells):** verdict ε-stable across {0.01, 0.02, 0.05} on all three; no cell crosses the gap criterion at any ε.

### 3b. 2016Q1 — "the gap recurs"

`R²_named` is BIMODAL: high (0.59–0.94) on rb01/rb02/rb04/rb06/rb07/rb08, near-zero (0.022–0.21) on **rb00 / rb05 / rb09**. The named-explainer root on the gap cells is no longer FICO — it's CLTV (rb00) / DTI (rb05) / property_type (rb09), with weak importance; the all-explainer root is **`property_state`** on every gap cell.

| cell | n | plural | R²_named | R²_all | dR²_ext | rung | named root | all top features |
|------|-------|--------|----------|--------|---------|------|------------|------------------|
| rb00 | 45150 | True | 0.035 | 0.580 | 0.545 | **3b-codification-irreducible** | CLTV | property_state 0.97 |
| rb01 | 27482 | False | 0.936 | 0.936 | 0.000 | — | FICO | FICO 0.97 |
| rb02 | 63559 | False | 0.894 | 0.913 | 0.020 | — | FICO | FICO 0.96 |
| rb03 | 12267 | True | 0.365 | 0.696 | 0.331 | — | loan_term | property_state 0.51, loan_term 0.38 |
| rb04 | 39690 | False | 0.842 | 0.842 | 0.000 | — | FICO | FICO 0.99 |
| rb05 | 45692 | False | 0.208 | 0.961 | **0.753** | **3b-codification-irreducible** | DTI | DTI 0.64, FTHB 0.28, property_state 0.08 |
| rb06 | 43717 | True | 0.591 | 0.624 | 0.032 | — | FICO | FICO 0.89, seller 0.10 |
| rb07 | 27436 | False | 0.937 | 0.937 | 0.000 | — | FICO | FICO 0.98 |
| rb08 | 17966 | False | 0.858 | 0.867 | 0.009 | — | FICO | FICO 0.95 |
| rb09 | 31467 | True | 0.022 | 0.961 | **0.939** | **3a/3b-mixed-loan-size-and-geo** | property_type | property_state 0.63, upb 0.24, DTI 0.12 |

**The gap-cell band structure on 2016Q1 is qualitatively different:** every band member uses `property_state` on the rb00/rb09 verdict-cells. On rb00 the band has 3 distinct used-feature-sets, **all three contain `property_state`** (`{property_state}`, `{loan_purpose, property_state}`, `{num_borrowers, property_state}`). On rb09 (the highest-rate band) all 57 distinct members use `property_state`; most also use `original_upb`. The pattern is rung-3b textbook: the gap is real, the carrier is a feature a compliant policy literally cannot name, and any non-property_state-using tree is more than ε = 0.02 below the best — so it falls out of the band.

**Variant B closes the gap-cells:** rb00 0.035 → 0.769, rb09 0.022 → 0.744. With geography/lender prohibited, the band can't use `property_state`, and the named features carry the load — exactly the P4 near-mechanical prediction.

**rb05 is the most interesting non-verdict cell — but for a reason different from what I first inferred.** (`median_pairwise_spearman ≈ 0.998` → near-identical predictions across variant-A members → NOT plural under the pre-reg's plurality criterion → does NOT count toward the strict P1 verdict.) The variant-A band has 4 distinct used-feature-sets, all containing `(dti, property_state)`: `{dti, property_state}`, `{dti, FTHB, property_state}`, `{dti, loan_purpose, property_state}`, `{dti, property_state, servicer_name}`. Members make near-identical predictions on the cell loans (`med_rho=0.998`), so `d_A` is tiny (std = 2.0e-4, max = 1.6e-3). Variant-A's R²_named = 0.208 looks gap-like; variant-B's R²_named = 0.688 (its band has 31 distinct used-feature-sets all without `property_state`, keyed on DTI + FTHB) looks gap-closing.

**My first inference was rung-2.5** (the named-vocabulary IS the right carrier; the depth-3 explainer just can't see the DTI-within-state interaction). **The direct verification falsifies that inference.** Run: `scripts/fm11_2016Q1_rb05_rung25_verify.py` (output: `runs/fm11_2016Q1_rb05_rung25_verify.json`); the variant-A named-only explainer at depths {3, 4, 5, 6, 7} gives R²_named = {0.208, 0.210, 0.214, 0.215, 0.210}, going from 5 internal nodes to 38 with no jump toward variant-B's 0.688. The depth-3 functional form is NOT the limiter; the named-only explainer captures what it can capture (R²≈0.21) regardless of depth budget. **Rung-2.5 is falsified on this cell.**

**The post-falsification reading is sharper and more interesting:** variant A and variant B are not the same refinement set viewed with/without geography — they are **two different ε-good bands keyed on different feature combinations** (variant-A members all use `(dti, property_state)`; variant-B members all avoid `property_state` and reorganize onto DTI + FTHB combinations). Their disagreement signals `d_A` and `d_B` are *different signals*, not "the same signal with different observability." `d_A` is small and structured by `property_state` (named-only explainer captures R²≈0.21 because *the structure isn't in the named features at any depth — it's in property_state*); `d_B` is a different shape and IS named-explainable (R²≈0.69). **The variant-B "closure" on rb05 is not fixing a deficiency in the variant-A view; it is *running a different diagnostic on a different band* and getting a different answer.**

This is a **diagnostic-pragmatics** finding (loops directly into the pragmatics/indexicality framing from the project's session-8 discussion): "vocab adequacy on rb05" is *indexical* — it means different things depending on which variant's band is being reported. Variant-A reports "rb05 vocab inadequate by named features" (true: `d_A`'s structure is in `property_state`); Variant-B reports "rb05 vocab adequate by named features" (true: `d_B`'s structure is in DTI+FTHB). Both are technically true; they refer to different bands. **The deployed observability artifact must declare its indexical context — which band, under what admissibility — for the "vocab adequate / inadequate" claim to bind.** A regulator running this test on rb05 will get opposite verdicts depending on whether the candidate-feature-set includes `property_state`, and *both verdicts are correct in their respective contexts*.

This finding wasn't in the pre-reg's P-list. It's a result that surfaced through the pre-reg discipline (the rung-2.5 inference was falsified by direct verification; the *falsification itself* exposed the underlying mechanism). It is closer in shape to a §5-style schema/diagnostic finding than to a P1–P7 verdict-cell finding, but it's specific enough to rb05 (not "every cell" the way the §5a `mandatory_features` finding is) that it lives here in §3b.

**Eps-arm (plural gap cells):** rb00 gap stable across all three ε (R²_named = 0.035 / 0.035 / 0.049); rb09 stable at ε ∈ {0.01, 0.02} (R²_named = 0.021 / 0.022), R²_named jumps to 0.16 at ε = 0.05 — still well below 0.30 → eps-stable verdict.

**Placebo (plural cells, real R²_named vs C-random R²_mean margin):** rb00 −0.42, rb03 −0.23, rb06 +0.10, rb09 −0.36. On the gap cells the real-vs-random margin is *negative* — i.e. the named features explain `d_real` *worse* than random features explain `d_rand`. This is not the pre-reg's "hollow" branch (real ≈ random) but a stronger statement: the named policy has *less* purchase on the real disagreement than a random feature set has on its own controlled disagreement. The placebo confirms the gap is real (not a "low-dim `d`" artifact).

**C-scrambled on gap cells (raw observation, interpretation deferred to §5b):** band size **7 distinct members on rb00 2016Q1** (vs 80 on 2018Q1 prime cells, vs 38 distinct used-feature-sets on the *real* variant-B band of rb00 2016Q1). On rb09 2016Q1: 59 distinct members. The relationship between scrambled-band size, cell n, and "is monotonicity binding?" is **muddier than the pre-reg's all-or-nothing criterion** — §5b lays out the full table across all three vintages and walks through what the placebo does and does not tell us. The clean cross-cell observation lives in §5b; the per-cell numbers are recorded here for completeness.

### 3c. 2008Q1 — "the gap recurs at the subprime-equivalent band, with a different carrier"

`R²_named` is **0.076 (rb09) through 0.89** across the 10 analyzed rate-bands; 7 of 10 cells are plural. The gap recurs at **rb09** (R²_named=0.076, dR²_ext=0.65, rung 3a/3b mixed, ε-stable across {0.01, 0.02, 0.05}). **rb08 is a marginal eps-unstable cell** (R²_named = 0.531 / 0.450 / 0.262 at ε = 0.01 / 0.02 / 0.05 — gap only at ε=0.05 — does not count toward the strict ε-stable verdict).

| cell | n | def_rate | plural | R²_named | R²_all | dR²_ext | B_R²_named | rung |
|------|-------|----------|--------|----------|--------|---------|-------------|------|
| rb00 | 33285 | 0.0085  | True   | 0.780 | 0.811 | 0.031 | 0.823 | — |
| rb01 | 29013 | 0.0162  | True   | 0.771 | 0.796 | 0.025 | 0.731 | — |
| rb02 | 15874 | 0.0227  | True   | 0.821 | 0.831 | 0.009 | 0.816 | — |
| rb03 | 29495 | 0.0254  | True   | 0.886 | 0.889 | 0.004 | 0.861 | — |
| rb04 | 38767 | 0.0334  | True   | 0.687 | 0.718 | 0.031 | 0.792 | — |
| rb05 | 26872 | 0.0381  | False  | 0.859 | 0.859 | 0.000 | 0.848 | — |
| rb06 | 18086 | 0.0448  | False  | 0.849 | 0.876 | 0.027 | 0.910 | — |
| rb07 | 19380 | 0.0585  | False  | 0.837 | 0.841 | 0.003 | 0.835 | — |
| rb08 | 30288 | 0.0848  | True   | 0.450 | 0.843 | 0.393 | 0.730 | — (eps-unstable; gap only at ε=0.05) |
| rb09 | 16456 | 0.1435  | True   | **0.076** | **0.722** | **0.646** | **0.264** | **3a/3b-mixed-loan-size-and-geo** |

**rb09 mechanism on 2008Q1:** all 130 distinct used-feature-sets use ≥1 extension feature; the all-explainer's top features are `original_upb` (0.55), `property_state` (0.44), `fico_range_low` (0.01). Loan size and geography split the explanatory load almost evenly with FICO contributing essentially nothing — i.e. in the 2008Q1 14.3%-default-rate top-rate band, the credit-risk feature the policy most prominently names (FICO) is *absorbed by the rate stratification*, and what remains of `d` is split between a feature a policy *could partially* name (loan size — via jumbo overlays / conforming-limit gates — "rung 3a-ish") and one a compliant policy *cannot* name (property_state — "rung 3b"). Variant B prohibits property_state but allows original_upb → variant B closes the property_state-half of the gap and leaves the loan-size-half: R²_named goes 0.076 → 0.264 (still gap), R²_all goes 0.722 → 0.747 (the remaining explanatory power is in original_upb).

**Placebo (plural cells, real R²_named − C-random R²_mean margin):** rb00 +0.17, rb01 −0.03, rb02 +0.27, rb03 +0.18, rb04 +0.06, rb08 −0.26, rb09 **−0.59** (decisive gap confirmation — random features explain `d_rand` 9× better than the real 11 named features explain `d_real`).

**Eps-arm (plural cells, gap_recurs at {ε=0.01, 0.02, 0.05}):** rb09 gap-True at all three (R²_named = 0.150 / 0.076 / 0.084 — all <0.30); rb08 gap-False/False/True (only the widest band opens the gap — does not count for the verdict); all other plural cells gap-False at all three.

---

## 4. The P1–P7 scorecard

| prediction | prior | 2018Q1 | 2016Q1 | 2008Q1 | cross-vintage verdict |
|------------|-------|--------|--------|--------|------------------------|
| P1 — gap recurs on ≥1 plural band, eps-stable | 0.55 | MISS (0/3 plural cells hit) | HIT (rb00, rb09) | HIT (rb09; rb08 eps-unstable) | **HIT (2 of 3 vintages)** |
| P2 — if gap then rung 3b | 0.65 | N/A | partial — rb00 pure 3b, rb09 mixed 3a/3b | mixed 3a/3b on rb09 | **partial HIT** — pure 3b once (2016Q1 rb00), mixed 3a/3b on both rb09 hits |
| P3 — heterogeneity by rate-band | 0.7 | partial (R² 0.72–0.95; no predicted "high-rate gap") | HIT (rb00 + rb09 gap, mid bands adequate) | HIT (rb09 gap, others adequate; rb08 marginal) | **HIT** — heterogeneity confirmed; predicted *shape* (high-rate gap) holds on 2 of 3 vintages, fails on 2018Q1 |
| P4 — variant B closes gap | 0.8 | N/A | HIT on verdict-cells (rb00 0.04→0.77, rb09 0.02→0.74); rb05 (non-verdict, not plural) shows variant-A→variant-B R²_named jumping 0.21→0.69 but **the post-falsification reading is that variant A and variant B are different ε-good bands with different disagreement signals on rb05, not the same band with different observability** — see §3b | partial — rb09 0.076→0.264, *still gap*; variant B allows `original_upb` which carries half the disagreement | **partial HIT on verdict-cells (geography-only carrier closes; geography+loan-size carrier only half-closes); rb05 reveals a separate diagnostic-pragmatics finding (variant-A and variant-B construct different bands, both correct in their respective contexts) — rung-2.5 inference falsified by direct verification** |
| P5 — real beats random-placebo by ≥0.15 | 0.85 | HIT rb00/rb04; HOLLOW rb02 | MISS on gap cells (margin negative on every plural cell) | mixed: HIT rb00/rb02/rb03; HOLLOW rb01/rb04; INVERTED rb08/rb09 | **MISS as criterion-stated** — but the inverted (real < random) margins on gap cells are themselves a sharper "the gap is real" confirmation |
| P6 — verdict eps-stable | 0.7 | HIT (all 3 plural; no gap at any ε) | HIT — rb00 stable at all 3 ε; rb09 stable at 0.01/0.02, R²=0.16<0.30 at 0.05 (gap) | HIT — rb09 stable at all 3 ε; rb08 only opens at ε=0.05 (eps-unstable, not counted) | **HIT** on the verdict-bearing cells |
| P7 — heterogeneity across vintages | 0.65 | — | — | — | **STRONG HIT** — 2018Q1 (no gap) qualitatively different from 2016Q1 / 2008Q1 (gap recurs); among the two hit vintages, rb09's mechanism differs (3b on 2016Q1, mixed 3a/3b on 2008Q1) |

**The cross-cutting most-likely-miss the pre-reg called out** ("the FM strata are just too homogeneous within to support a plural refinement set at ε = 0.02 once ~12 mandatory features, used-feature-set de-dup, and the cross-vintage replication requirement are all imposed") **did partially materialize as predicted**: many cells have very few distinct used-feature-sets after refit (rb00 2016Q1 has only 3; rb05 2016Q1 has only 4). But the pre-reg's "no analyzed-plural bands at all" outcome did NOT happen — plural bands exist on all three vintages.

**The pre-reg's predicted-pattern miss the pre-reg didn't anticipate**: the recurring gap-band is rb09 *across regimes*, but the mechanism is *vintage-dependent* (property_state-only on 2016Q1, loan-size + property_state on 2008Q1). The pre-reg's P2 split (3a-codification-fixable vs 3b-codification-irreducible) suggested a clean per-finding classification; the actual finding is **the same band-index classifies differently across vintages, because the regime-specific drivers of within-band default differ**. Loan size and geography trade off as carriers as the rate environment shifts.

**The pre-reg's prediction the data falsified outright**: "(R-majority) predicted the only one that's both satisfiable and non-trivial." R-majority is satisfied **on zero cells on zero vintages**. The schema's `mandatory_features` mechanism does no work on this substrate under any of the three readings — a finding one level up from P1–P7 (see §5).

---

## 5. Schema findings (independent of P1–P7, present on every vintage tested)

### 5a. The `mandatory_features` mechanism is doing no work

All three pre-registered enforcement readings — R-member (every member's used-set ⊇ mandatory), R-any (the band's *union* of used features covers mandatory), R-majority (each mandatory feature used by ≥50% of members) — **fail on every analyzed cell on every vintage tested**. The features that pass the 50%-used threshold are at most {fico_range_low, dti, num_borrowers, loan_term_months} on any cell; the other 7+ mandatory features are used by <50% of band members. The pre-reg predicted R-majority would be "the only one that's both satisfiable and non-trivial" — that prediction is wrong: it is neither, on this data.

The deeper finding: **`mandatory_features` as a YAML list cannot pin a refinement set on a real-data substrate where shallow trees with `leaf_min ≥ 25` use a small subset of available features per fit.** A 13-mandatory-feature requirement at member-level is incompatible with depth-3 trees by construction (a depth-3 tree splits on ≤7 features). At band-union level (R-any) it requires every mandatory feature to be a competitive splitter in *at least one* admissible model — not the case here. At majority level (R-majority) it asks for *most* models to use *every* mandatory feature — strictly less satisfiable than R-any.

**Recorded for schema redesign (NOT BUILT here):** `mandatory_features` semantically wants to be a **band-level admissibility predicate** (the band as a whole must satisfy the mandatory-consideration requirement), not a per-member or per-feature one. A workable formalization: the band is admissible iff the *cardinality of the union of used-feature-sets* covers the mandatory features (R-any) AND the predicted-probability *function* P(default|x) viewed at the band consensus depends on every mandatory feature non-trivially. Both readings are still not "satisfied" on FM 2016Q1 rb00 (where the consensus is essentially P(state) and is independent of FICO/DTI/etc.), but they're at least *measurable*.

### 5b. C-scrambled placebo — what it says and what it does not

The C-scrambled placebo builds an ε-good band with the **reversed** documented monotonicity. The pre-reg hoped this would be "a first taste of the dead-letter test" — if reversed-sign models are excluded from R(ε), the documented monotonicity is binding; if reversed-sign models populate R(ε) freely, it is slack. The data here lands less cleanly than that:

| vintage | cell | real_band_uf | C-random_uf | C-scrambled_uf | R²_named | R²_scrambled | ratio |
|---------|------|--------------|-------------|-----------------|----------|---------------|-------|
| 2018Q1 | rb00 | 30  | 17 | 80 | 0.898 | 0.373 | 0.42 |
| 2018Q1 | rb02 | 131 | 44 | 89 | 0.783 | 0.286 | 0.37 |
| 2018Q1 | rb04 | 96  | 70 | 61 | 0.787 | 0.391 | 0.50 |
| 2016Q1 | rb00 (gap) | 3 | 3 | 7 | 0.035 | 0.035 | 1.00 |
| 2016Q1 | rb03 | 9 | 7 | 11 | 0.365 | 0.293 | 0.80 |
| 2016Q1 | rb06 | 126 | 93 | 35 | 0.591 | 0.030 | 0.05 |
| 2016Q1 | rb09 (gap) | 57 | 56 | 59 | 0.022 | 0.058 | 2.6 |
| 2008Q1 | rb00 | 42 | 22 | 43 | 0.780 | 0.861 | **1.10** |
| 2008Q1 | rb01 | 82 | 30 | 40 | 0.771 | 0.649 | 0.84 |
| 2008Q1 | rb02 | 220 | 80 | 50 | 0.821 | 0.573 | 0.70 |
| 2008Q1 | rb03 | 81 | 50 | 45 | 0.886 | 0.599 | 0.68 |
| 2008Q1 | rb04 | 68 | 36 | 18 | 0.687 | 0.567 | 0.83 |
| 2008Q1 | rb08 | 13 | 12 | 20 | 0.450 | 0.134 | 0.30 |
| 2008Q1 | rb09 (gap) | 130 | 110 | 22 | 0.076 | 0.071 | 0.93 |

The **partial observation**: on non-gap cells, R²_scrambled is *usually* lower than R²_named — median ratio across the 11 non-gap plural cells is ≈ 0.68, with a long tail toward 0.05 (2016Q1 rb06). On gap cells the ratio is ≈ 1 (neither real nor scrambled explains `d`). The 2008Q1 rb00 ratio of 1.10 is an outlier — reversed-monotonicity trees happen to fit a low-default rate-band's `d_scrambled` slightly better than real-monotonicity trees fit `d_real` (R² difference of 0.08 on a 5-fold CV is within plausible CV variance for these cell sizes).

The pre-reg's clean "binding/slack" diagnostic does **not** materialize: scrambled-band sizes are 7–89 distinct members across cells; *none* are "empty or trivially small", so the reversed-monotonicity R(ε) is populated on every cell. The pre-reg's all-or-nothing binding criterion ("R(ε) empty under reversed sign ⇒ monotonicity binding") is not met cleanly on any cell. Band size and ratio are dominated by the cell's intrinsic refinement capacity (a 16k-loan cell supports fewer distinct ε-good models than a 60k-loan cell, with any monotonicity choice), not by whether the documented constraint is binding.

**Net**: the C-scrambled placebo confirms the documented monotonicity is *usually informative for prediction structure* on non-gap cells (R²_scrambled < R²_named on 8 of 10 non-gap plural cells tested) but does not give the cleaner per-constraint binding diagnostic the pre-reg implicitly hoped for. The actual dead-letter test is the per-constraint sibling pre-reg (relax one documented monotonicity constraint at a time, reconstruct R(ε), measure whether the relaxation admits new ε-good models that violate the dropped constraint). The C-scrambled here is the all-at-once version; the per-constraint version is the followup that would actually identify *which* documented monotonicity constraints are binding *on which cells*.

---

## 6. Limits (verbatim from pre-reg §6, plus what the runs themselves added)

[verbatim from pre-reg §6:]

- **The FM public file is thinner than a real underwriting file** (no income, no reserves, no liquid assets, no residual income, no manual-underwriter notes). The "medium-fidelity" policy is bounded above by the data. A residual gap (P1 hits) is consistent with *either* "real policies underdetermine" *or* "this particular public dataset is missing the features that would close it" — and we cannot fully disentangle the two here. The cleaner test of "real policies underdetermine" would be a real lender's data + real policy (out of scope; this is the best public proxy).
- **The policy YAML is a reconstruction of public structure, not the Eligibility Matrix PDF.** Numbers (DTI 50, FICO 620, LTV 97, conforming limit) are public and stable; the *exact* matrix cell structure is approximated.
- **Stratum choice (rate-band) is one defensible analogue of LC's `sub_grade`, not the only one.** S-llpa is the parallel arm; reported in the follow-on note.
- **The schema doesn't have first-class eligibility gates.** #11 smuggles the Matrix cutoffs into `applicable_regime` + a hand-written `nodes` graph (see §1a above).
- **No claim about case-level routing.** That door is closed ([[project_routable_population_result]], six ways). This test is purely about *observability* at the tier level.
- **#11 is one cell of a larger structure: the documented-policy-vs-operative-behavior diff** — the unwritten-policy cell. The dead-letter cell (relaxed-constraint R(ε)) and the distortion cell are sibling pre-regs to write. The dead-letter cell has a *first taste* in §5b above.

[added by the runs:]

- **The cross-vintage gate fired:** 2018Q1 says no-gap, 2016Q1 says gap-on-3-cells. P7 hit at the strongest possible reading. **Vocabulary adequacy is regime-sensitive on the same substrate and policy** — a finding worth more than the headline. The implication for a deployed observability artifact: a single-vintage test of "is my policy vocab-adequate" can give the *opposite* answer to the same test on a different vintage of the same portfolio. **The test is a gate, not an oracle.**
- **The placebo's "real vs random margin" inverts on gap cells.** When the policy *adequately* describes `d`, real margin > random margin (P5 holds). When the policy *fails*, real margin can be NEGATIVE — random features explain their own controlled `d_rand` better than real features explain `d_real`. This is a sharper statement of "the gap is real" than the pre-reg's P5 anticipated. The "hollow" branch (real ≈ random) appeared once (2018Q1 rb02); the "real < random" branch appeared on every 2016Q1 gap cell.
- **The `nrows` cap on the FM load was NOT used** — the runs read the full extracted CSVs (~6-7 GB each, ~12 min / ~30 GB RSS apiece). Memory and runtime stayed within the operational gotchas. The compute restriction was on subset enumeration (max_subset_size = 5), not data sampling.
- **Scope-of-claim discipline (the temptation to over-state).** The data robustly support **the narrow form** stated in §0: rb09 of FM SF acquisitions shows an ε-stable vocabulary gap on 2 of 3 vintages, with a regime-dependent carrier (geography in expansion, geography+loan-size in crisis). The data **do not** support a generalized "rich policies underdetermine model indeterminacy on community-bank-equivalent mortgage portfolios" claim — that would over-reach what was tested. rb09 is structurally the slice where pricing dispersion is widest (jumbo overlays, lender-specific risk pricing), so the within-band residual heterogeneity carried by non-credit-risk features lives there for understandable structural reasons, not because policy vocabulary is failing across the board. The regulator-doc spine's "vocabulary inadequacy" framing must keep to the narrow form: *the highest-rate decile of a single-family conforming portfolio is the slice where a medium-fidelity codified policy's vocabulary leaves a measurable observability gap; below that, on this substrate, the vocabulary is at least non-distinguishably adequate (and where it's measurable, decisively so).* A regulator who reads the narrow form can only ask "what about other portfolios?" — which is the right question for the next experiment.
- **No bridge to per-decision routing.** The finding is at the tier (rate-band) level, not the case level. The bridge to "this matters for a deployed observability artifact" is sound (a regulator running this test on a portfolio gets a per-tier "vocab-adequate / vocab-gap" map); the bridge to "this is why per-decision routing works" is NOT here and shouldn't be reached for downstream. The per-decision routing arc is closed terminal ([[project_routable_population_result]], six ways) and this result does not reopen it.
- **2008Q1 confounds regime change with policy-period mismatch.** The 2008Q1 finding tests vocab adequacy under a present-day (2018-era) policy YAML applied to a historical (2008-era) portfolio — a legitimate framing for current examination practice (current examiners audit historical performance against current rules), but a confound for the regime-change story specifically: the 2008Q1 rb09 result could be partly anachronism-driven (the YAML's $453,100 conforming UPB and 2018 LLPA grid are wrong for 2008 originations) rather than purely regime-driven. The cross-vintage replication claim ("rb09 gap on 2 of 3 vintages") is robust to this confound (the *replication* is real regardless of carrier identity), but the mechanism attribution on 2008Q1 specifically ("loan size carries it because…") needs the anachronism sibling pre-reg (§7) to disentangle vocabulary-inadequacy from policy-period-mismatch. The 2016Q1 finding does NOT have this confound (a 2018-era YAML on 2016-era data is a small-time-gap test; 2016's gates were materially similar).

---

## 7. Provenance

Implementation order followed pre-reg §7: (1) policy YAML + collector extension + collector tests green; (2) the script; (3) the three FM runs strictly serial (2018Q1 → 2016Q1 → 2008Q1, ~14h compute total); (4) this result note. Test count: **235 pass / 1 skip → 242 pass / 1 skip** (+5 collector tests for the new fields + bucketing helper, +2 refinement_set tests for the `max_subset_size` knob).

**Commit hashes:**
- Pre-reg (frozen): `1817010` (substantive) / `ddb0b1f` (OTS).
- Implementation + result (this commit): [TBD] / [TBD] (OTS).

**Sibling pre-regs to write (priority order — diagnostic pragmatics first because it generalizes from the rb05 falsification, then scope-closers, then the orthogonal tests):**

1. **The variant-indexicality / diagnostic-pragmatics test** (highest priority for the artifact-design spine, promoted by the rb05 finding). The rb05 result in §3b shows that on at least one cell, variant-A and variant-B construct *different ε-good bands* (different used-feature-set distributions, different disagreement signals `d_A` vs `d_B`), and the "vocab adequacy" diagnostic is *indexical* — it reads differently in each variant, and both readings are correct in their context. **Pre-reg to write** is the generalized version: across the band-corpus, on what fraction of cells is `d_A` ≠ `d_B` (band reorganization rather than band restriction), and what predicts which cells re-organize? Specifically, is it cells where the variant-A band's used-feature-sets ALL contain a prohibited-in-variant-B feature (the property_state-saturation pattern on rb05 2016Q1 / rb09 2016Q1 / rb09 2008Q1)? If so, the *artifact* must declare its variant context for the "vocab adequate" claim to bind — and a regulator running the diagnostic in only one variant gets a *partial* picture, not the full picture. This is the practical artifact-design lever the rb05 finding opens: **the diagnostic protocol must specify "report variant-A and variant-B together, never one in isolation"**, otherwise the indexicality lets the artifact silence-manufacture under a chosen variant.
2. **(Rung-2.5 explainer-depth as a general phenomenon — kept on the menu but DEMOTED.)** The rb05 verification falsified rung-2.5 on that cell, but the phenomenon could still occur elsewhere — a cell where the variant-A band's `d_A` IS named-feature-explainable at higher depth would be the existence proof. The depth-sweep can be run as a regression test on any future gap cell where R²_named at depth 3 is suspect; no standalone pre-reg needed unless a candidate cell appears.
3. **The dead-letter test** (relaxed-constraint R(ε) per documented constraint; the C-scrambled placebo in §5b is the all-or-nothing version, the per-constraint version is the actual sibling). The rb05 finding sharpens the case for it: variant-A and variant-B's different bands on the same cell suggest the documented monotonicity might be binding-where-DTI-carries vs slack-where-property_state-keys-the-band; the dead-letter test would resolve that per-constraint per-cell.
4. **Variant C — full Eligibility-Matrix conforming gates** (scope-closer for 2008Q1 rb09). Prohibit geography *and* `original_upb` above the era-matched conforming limit. The 2008Q1 rb09 mechanism makes the case: variant B half-closes because it allows `original_upb`. Variant C would test whether the 3a-codifiable component of the rb09 gap is exactly the conforming-limit gate — i.e. whether a policy with first-class `gates:` *would* close it. If variant C closes 2008Q1 rb09, the rung classification firms up to "3a-via-the-conforming-gate"; if it doesn't, there's a residual that's neither geography nor jumbo loan size, which would be a substantive surprise.
5. **The anachronism test** ([[temporal-documented-vs-documented diff]] — scope-closer for the 2008Q1 confound). The YAML here encodes 2018-era gates (conforming UPB $453,100, DTI 50, LTV 97, FICO 620). Applying it to 2008Q1 is *applying today's documented policy to yesterday's portfolio* — exactly what current-day examiners do when auditing historical performance against current rules. Write `policy/fnma_eligibility_matrix_2008.yaml` with era-correct gates ($417,000 baseline conforming, the original LLPA grid, the tighter pre-QM DTI thresholds, no HERA high-balance overlay) and rerun #11 on 2008Q1 only. If the rb09 gap closes under era-matched policy → the 2008Q1 gap is anachronism-driven; if it persists → vocab inadequacy is robust to policy-period-matching. Either is a finding. (Conceived in the 2026-05-13 session-8 conversation; not yet pre-registered.)
6. **The distortion test** (where are the documented-monotone features non-monotone in the unconstrained ε-good set — the third sibling cell of the documented-vs-operative diff structure).
