# Root-tier discriminator: FM substrate-independence sanity check + C1 dedup story

**Date:** 2026-05-14. **Status:** addendum (refines two claims from `2026-05-14-lc-centrality-cross-substrate-posthoc-note.md`). NOT pre-registered. **Script:** `scripts/root_tier_substrate_independence_check.py`.

The LC post-hoc proposed (a) the explainer-root-feature-tier as a *substrate-independent* operationalization of the reorganization-flag and (b) characterized C1 as "anomalous — neither pure prime nor pure collapser." This addendum tests both claims against existing data.

## 1. FM substrate-independence check — REFINED, not refuted

**Test:** for each of the 29 cells in the #12 FM corpus, classify as "root-tier-reorganized" iff variant-A's all-explainer root feature is in the prohibited set (`candidate_extension_A \ candidate_extension_B`). Compare to #12's Jaccard-based reorganization classification.

**Result: 27 of 29 cells agree. 2 disagreements.**

The 27 cleanly-classified cells:
- **3 manufactured-silence cells** (2016Q1 rb00, rb05, rb09): both discriminators say reorganized; variant-A root is `property_state` (prohibited extension).
- **2008Q1 rb09** (the known rung-3b gap cell that #12 classified as censored): both say censored; variant-A root is `original_upb`, which is in BOTH variants' candidate_extension sets — so it's NOT prohibited, and root-tier correctly classifies it as censored. This is a tidy confirmation.
- **24 prime/mid cells**: both say censored; variant-A root is `fico_range_low` (named).

**The 2 disagreements are exactly the "reorganized-but-verdict-agreeing" cells from #12:**

| cell | Jaccard | root-tier | rootA | rootB | R²_named A | R²_named B |
|------|---------|-----------|-------|-------|------------|------------|
| 2016Q1 rb03 | reorganized | NOT reorganized | loan_term_months (named) | loan_purpose (named) | 0.365 | 0.778 |
| 2008Q1 rb08 | reorganized | NOT reorganized | fico_range_low (named) | fico_range_low (named) | 0.450 | 0.730 |

On both cells, property_state is *present* in ~50% of variant-A's ufs (driving Jaccard reorganization classification) but **does not sit at the all-explainer's root** (because the band's *structural* explanation of d is still rooted in named features — loan_term_months on rb03, fico_range_low on rb08). The Jaccard catches "structural reorganization potential" via uf-set differences; root-tier catches "actual centrality" via explainer-root identity. These are different signals.

### Refined claim (replacing the LC post-hoc §4's broader statement)

**Root-tier discriminator is the substrate-independent operationalization of the manufactured-silence detection.** It catches every cell where the prohibited feature is *centrally explanatory* (the 3 manufactured-silence cells in FM), and correctly classifies the censored cells (24 prime cells + 2008Q1 rb09). 

**It does NOT catch the wider class of structural reorganization that Jaccard does** — the 2 cells (rb03, rb08) where prohibited features are *present in the band but not at the explainer root*. Those are also real (variant-A and variant-B build different ε-good bands; rb03's verdict is threshold-adjacent at R²_named=0.365), but the centrality signal is absent.

**Both discriminators have a role.** Root-tier is the substrate-independent detector for manufactured-silence; Jaccard is the substrate-dependent detector for the wider structural-reorganization class. Paper 2 schema design should report **both flags** per band, with manufactured-silence being the load-bearing one (the protocol mandate "always report both variants" binds only on root-tier-reorganized cells) and reorganization-potential being the secondary one (regulatory advisory for threshold-adjacent cells like rb03).

This is a TIGHTENING of the LC post-hoc's claim, not a refutation. The substrate-independence claim survives in narrower form.

## 2. C1 dedup story — confirmed artifact

The LC post-hoc §3 noted C1 as "anomalous — neither pure prime nor pure collapser." That reading was based on the #6 extension-admitted-band JSON which uses TREE-SIGNATURE dedup (271 near-duplicate trees → 15 distinct ufs after tree-sig dedup, R²_named = 0.064, explainer-root = mort_acc extension). Under that dedup, C1 looks collapser-flavored with extension-rooted explainer.

Under [[project_routable_population_result]]'s used-feature-set dedup (the corrected methodology), the saved data for C1 shows:

| metric | tree-sig dedup (#6) | uf dedup (routable_pop) |
|--------|---------------------|--------------------------|
| n_distinct_ufs | 15 | 8 |
| R²_named | 0.064 | **0.4032** |
| named-only explainer root | (not directly saved here) | **annual_inc** (importance 0.97) |
| well_explained_by_named | (low R² implies no) | **True** |
| named+ext explainer cv_r2 | 0.633 | 0.551 |

**C1's "collapser flavor" under tree-sig-dedup is artifactual** — the 271-near-duplicate-trees were inflating distinct-uf count and producing std-over-noise as d(x), making R²_named look pathological. Under uf-dedup, C1 has 8 distinct ufs, R²_named ≈ 0.40 (clearly named-feature-legible), and the named-only explainer roots on `annual_inc` with 0.97 importance.

**The named+ext explainer root for C1 under uf-dedup is not directly saved** in the routable_population JSON (only the named-only explainer root is). Circumstantial evidence (R²_named = 0.40, named-only-importance on annual_inc = 0.97) strongly suggests the named+ext explainer would also root on a named feature. To confirm rigorously: re-run the named+ext explainer on the uf-dedup band. Not done here.

### Implication for the LC post-hoc's 3-vs-0 cut

The cut "3/3 collapsers extension-rooted vs 0/3 primes named-rooted" used C2/C5/D4 as collapsers and A1/A5/B1 as primes. C1 was classified as "other (de-dup-recovered)" in the script's tier column, sidestepping the question.

The honest reading: under tree-sig-dedup (the source data), C1 has extension-rooted explainer, suggesting "3 collapsers + C1 = 4/4 extension-rooted on subprime-default-prone grades." Under uf-dedup (the methodology correction), C1 is named-feature-legible and moves to the non-collapser side, restoring the 3/4 vs 0/3 cut to 3 collapsers (extension-rooted) vs 4 named-feature-legible cells (A1/A5/B1 + C1).

**Either way, the centrality-vs-presence asymmetry replicates.** The cut is robust under both dedup methods at the question of "do collapsers and non-collapsers separate by carrier tier" — they do. The dedup affects only which cell C1 falls into; the asymmetric structure holds.

## 3. What changes upstream

The LC post-hoc note's §3 "C1 anomaly" reading is partially obsolete — C1's tree-sig-dedup data IS extension-rooted but that's a known artifact, and the corrected data shows C1 is named-feature-legible. The "4th distinct pattern" speculation should be replaced with: "C1 was a tree-sig-dedup artifact; under uf-dedup it joins the named-feature-legible class."

The LC post-hoc note's §4 schema-design proposal (root-tier as substrate-independent reorganization-flag) is TIGHTENED: substrate-independent for manufactured-silence detection (3/3 + 3/3 cells; the 4th LC collapser D4 hasn't been re-checked under uf-dedup's named+ext explainer, see limit below) but NOT a complete replacement for the Jaccard discriminator. Both flags should appear in the schema.

## 4. Open questions (genuine, not just hedges)

- **The named+ext explainer root for C2/C5/D4 under uf-dedup is not saved** — the routable_population JSON only has the named-only explainer root. The LC post-hoc's claim "3/3 collapsers root on extensions" used the tree-sig-dedup data. Whether the uf-dedup data would also show C2/C5/D4 extension-rooted is a clean re-run question. Cost: re-fit the depth-3 disagreement explainer over named∪extension on each of the 4 uf-dedup bands (C1/C2/C5/D4). Fast (saved-data analysis), but the band-member trees themselves need to be in saved form, which they may not be.
- **The 2 Jaccard-but-not-root-tier cells (rb03, rb08) on FM** — are they regulatory-meaningful, or just verdict-threshold-adjacent noise? The Paper 2 schema design needs to decide whether to elevate both flags or treat root-tier as primary and Jaccard as advisory.

## 5. Provenance

- Script: `scripts/root_tier_substrate_independence_check.py`
- Output: stdout (saved analysis JSON could be added but the per-cell table fits in the script's print)
- Refines: `2026-05-14-lc-centrality-cross-substrate-posthoc-note.md` §3 (C1) and §4 (schema design)
- Companions: `2026-05-13-variant-indexical-silence-manufacture-result-note.md` (#12), `2026-05-14-p2ext-classifier-centrality-diagnosis-note.md`
- Commit: [TBD] / OTS [TBD]
