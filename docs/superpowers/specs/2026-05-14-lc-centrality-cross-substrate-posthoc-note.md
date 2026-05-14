# LC pricing-space centrality cross-substrate replication — POST-HOC characterization

**Date:** 2026-05-14. **Status:** POST-HOC — pre-registration discipline was violated. The author peeked at top-3 saturation and top-5 importance per grade in `runs/extension_admitted_band_test_results.json` before attempting to freeze predictions. This note characterizes the patterns transparently as exploratory; the genuinely-pre-registered confirmation test belongs on different data. **Companion to:** `2026-05-13-variant-indexical-silence-manufacture-result-note.md` (FM #12) and `2026-05-14-p2ext-classifier-centrality-diagnosis-note.md`. **Lineage:** [[project_extension_admitted_band_result]], [[project_routable_population_result]].

---

## Headline

**The centrality-vs-presence asymmetry replicates on LC pricing-space, but the carrier identity is portfolio-shaped — not portfolio-invariant.** On all 3 collapser grades (C2 / C5 / D4 — the genuine collapsers from [[project_routable_population_result]]), the disagreement explainer's root feature is an *extension* feature. On all 3 prime grades (A1 / A5 / B1), the explainer's root feature is a *named* feature. The structural asymmetry — "some features carry the band's disagreement at the root, others appear peripherally" — replicates. The specific carriers differ: FM's codification-irreducible feature was `property_state`; LC's are `loan_amnt` (on C2, C5) and `inq_last_6mths` (on D4). **No single feature is "the" codification-irreducible carrier across substrates; different portfolios have different deeply-irreducible features.**

This is the more surprising of the two possible outcomes I was holding before peeking (carrier-portfolio-invariant vs carrier-portfolio-shaped) — and the one with the bigger implication for Paper 2 schema design: **the codification-irreducibility list is portfolio-parameterized, not a universal subset of features.**

Saturation alone is NOT what distinguishes prime from collapser on LC — prime mean top-sat (0.61) ≈ collapser mean top-sat (0.62). What distinguishes them is *centrality*: which feature sits at the explainer-root, AND whether saturation and centrality AGREE on the same feature.

---

## 1. The data (peeked, then fully analyzed)

| grade | tier | plural | top-by-sat | top-ext-by-importance-v1 | sat×imp agree | explainer root v1 | R²_named | ΔR²_ext |
|-------|------|--------|------------|--------------------------|---------------|-------------------|----------|---------|
| A1 | prime | True | open_acc = 0.88 | inq_last_6mths = 0.14 | ✗ | **fico_range_low** | 0.66 | 0.18 |
| A5 | prime | True | open_acc = 0.43 | open_acc = 0.50 | ✓ | **dti** | 0.42 | 0.26 |
| B1 | prime | True | open_acc = 0.51 | revol_util = 0.40 | ✗ | **annual_inc** | 0.42 | 0.19 |
| C1 | (de-dup-recovered) | True | open_acc = 0.53 | open_acc = 0.39 | ✓ | mort_acc | 0.06 | 0.63 |
| C2 | collapser | True | loan_amnt = 0.73 | loan_amnt = 0.24 | ✓ | **loan_amnt** | 0.11 | 0.25 |
| C5 | collapser | True | loan_amnt = 0.95 | loan_amnt = 0.55 | ✓ | **loan_amnt** | 0.13 | 0.26 |
| D4 | collapser | False | revol_util = 0.19 | inq_last_6mths = 0.38 | ✗ | **inq_last_6mths** | 0.15 | 0.31 |

**Root-is-extension cut:** 3/3 collapsers, 0/3 primes. Cleanly separable.

---

## 2. The three patterns

### 2a. Centrality replicates, presence is degenerate

On FM SF #11/#12, `property_state` had both high saturation (1.00 on the 3 manufactured-silence cells) and high explainer importance (0.97 on rb00 2016Q1). The two signals coincided, so the saturation-based P2 classifier achieved 100% accuracy on the FM corpus.

On LC: **saturation alone does NOT separate prime from collapser** — open_acc reaches saturation 0.88 on A1 (prime) while loan_amnt reaches 0.95 on C5 (collapser). Both are very high. The structural difference lives in *what role the high-saturation feature plays*: on A1, open_acc is widely present but the explainer roots on `fico_range_low` (open_acc's importance is only 0.14 — it's diffuse decorative); on C5, loan_amnt is widely present AND the explainer roots on loan_amnt at importance 0.55. **Presence without centrality is peripheral; presence with centrality is carrier.**

The centrality-vs-presence asymmetry from FM's P2-ext diagnosis is the right reading of the LC data too — but with sharper teeth here: on LC, you CANNOT diagnose codification-irreducibility from saturation alone. The FM result was a special case where the two coincided.

### 2b. Carrier identity is portfolio-shaped, not universal

The 3 collapser grades have *different* top-sat features (C2: loan_amnt, C5: loan_amnt, D4: revol_util) and *different* top-importance extensions (C2: loan_amnt, C5: loan_amnt, D4: inq_last_6mths). C2 and C5 share a carrier (loan_amnt); D4 has a different one entirely.

Compared to FM where `property_state` was the carrier on all 3 manufactured-silence cells: LC's pattern is *not* a single feature with universal carrier-status. Loan size carries the rung-3b residual on two LC subprime sub-grades; recent inquiries carry it on a third; neither carries it on FM (FM's rb09 used loan size as a *secondary* carrier alongside property_state; LC has no geography in its extension set at all).

**The implication:** codification-irreducibility is a *property of the portfolio's residual structure*, not a property of the feature. Loan size carries the residual on LC C2/C5 because the LC sub-grade machinery + extension set leaves loan-size-dependent default heterogeneity unexplained by named features. Geography carries it on FM because the FM rate-band machinery + named feature set leaves geography-dependent default heterogeneity unexplained by named features. There isn't a universal "irreducible feature"; there's a *portfolio-specific list*.

### 2c. The disagreement explainer's root is a sharper centrality measure than top-importance among extensions

On A1: top-extension-by-importance is inq_last_6mths (0.14), but the *explainer's overall root* is fico_range_low (a named feature). The "top extension by importance" framing answered the wrong question — it asked "given that we're looking at extensions, which one is highest"; the right question is "is the explainer's root feature in the named or extension set."

The 3-of-3 vs 0-of-3 root-is-extension cut between collapsers and primes IS the centrality signal, sharper than either saturation or extension-rank-importance. The next pre-reg should use root-is-extension as the centrality discriminator, not the saturation classifier.

---

## 3. Specific things I see beyond what I peeked at

(The peek showed top-3 saturation and top-5 importance per grade. The full analysis added:)

- **Explainer root-feature distribution** by tier (3/3 collapsers extension-rooted, 0/3 primes extension-rooted) — this is the cleanest pattern in the data and I had NOT seen it from the peek.
- **The saturation distribution by tier is degenerate** (means within 0.01 of each other). Saturation alone is uninformative on LC — this is a stronger statement than what I'd have predicted from the peek.
- **Saturation × importance agreement is mid (4/7)** — not the clean ≥5 I would have pre-registered. Agreement fails *systematically on prime grades* (A1, B1) and *on D4* (the non-plural collapser). The 4 agreements are all on bands where one extension feature has both high saturation and high importance.
- **C1's role is anomalous** — labeled "de-dup-recovered" in [[project_routable_population_result]] memory, neither pure prime nor pure collapser. Its explainer roots on mort_acc (extension) but its R²_named is 0.06 (very low), AND it has the clean sat×imp agreement on open_acc. Looks like a *fourth distinct pattern* — collapser-by-R²-named, prime-by-rule-of-dedup recovery. Worth noting that it's plural, agrees on sat×imp, and has extension-rooted explainer. So if the cut were "extension-rooted root" alone, C1 joins the collapsers (4/4 extension-rooted on subprime-default-prone grades).
- **D4 is the most ambiguous cell**: low saturation across all extensions (top is revol_util at 0.19), explainer roots on inq_last_6mths (0.38 importance), R²_named 0.15. The extension carriers are *diffuse and weak* — no single feature dominates either by presence or by centrality. This is consistent with D4 being non-plural under the prediction-similarity criterion (median_pairwise_spearman near 1.0 per [[project_extension_admitted_band_result]]).

---

## 4. What this changes about Paper 2's schema design

#12's result note proposed a `(variant-context-declaration, reorganization-flag, verdict-pair)` tuple as the redesigned `mandatory_features` slot. The LC characterization sharpens the reorganization-flag operationalization:

**Reorganization-flag should be based on EXPLAINER ROOT FEATURE TIER, not saturation.** Specifically: the flag is "true (reorganized / carrier-extension-driven)" iff the disagreement explainer's root feature is in the prohibited set (extension features in LC's framing; geography+lender features in FM's framing). This cuts cleanly on both substrates:

- FM: rb00 2016Q1's all-explainer roots on `property_state` (prohibited extension) → flag-true
- FM: prime cells' explainer roots on fico_range_low (named) → flag-false
- LC: C2 / C5 / D4 explainer-root on loan_amnt / loan_amnt / inq_last_6mths (extensions) → flag-true
- LC: A1 / A5 / B1 explainer-root on fico_range_low / dti / annual_inc (named) → flag-false

**The Jaccard reorganization-flag from #12 also remains valid** — it caught the same FM cells. But the explainer-root-tier operationalization is *substrate-independent* (works without a variant-A/B comparison) and might be more amenable to a single-band deployment artifact (one band built, one flag computed, no need to build two parallel bands for comparison).

This is a real schema-design refinement and probably wants its own Paper 2 §X. Likely formulation: **the codification-irreducibility verdict is a (carrier-feature, carrier-feature-tier) tuple per band; the protocol "the artifact reports the carrier" gives regulators a portfolio-specific list of irreducible features instead of a generic 'vocab inadequate / adequate' boolean.**

---

## 5. The pre-reg discipline violation and what to do about it

I peeked at top-3 saturation and top-5 extension importance per grade before attempting to freeze predictions. That informed me about:
- C2 / C5 both have loan_amnt as top-sat (P4 — "same carrier across collapsers" — partly violated)
- A1 has high open_acc saturation despite being prime (P5 — "primes have peripheral extensions" — looked like it might be violated)
- D4 has weak saturation everywhere (P1 — "top-sat ≥ 60%" — looked like it might miss on D4)

Pre-registering predictions after seeing those data points would have been performance, not honesty. Better to be transparent: **this note articulates the mechanism, doesn't claim the predictions are confirmed.**

**The genuinely pre-registered confirmation test should be on different data.** Concrete options:

1. **Different LC vintage** — LC pricing-space sweep covers many vintages ([[project_pricing_space_cat2]]); pick one not analyzed for centrality. **Cleanest near-term option**; ~few hours of compute if existing scripts apply.
2. **HMDA substrate** — never tested with the extension-admitted-band framework. **Furthest cross-substrate test**; multi-day if it requires new band construction infrastructure.
3. **FM multi-variant followup** (#12 §6 #1) — different question (carrier independence across multiple prohibition profiles on FM) but tests the explainer-root-tier discriminator with a clean pre-reg on FM data we haven't peeked at the multi-variant level on.
4. **LC OTHER bursts** — Burst D was 2015H2_dti; the sibling [[project_disagreement_geometry_result]] tested 4 bursts on LC. The other bursts' centrality structure is unpeeked.

**My pick (where the next pre-reg should land):** option 4 — LC's other bursts (A, B, C from #6, if they have extension-admitted band data). Same substrate, fresh data, cleanest test of "does the explainer-root-tier discriminator replicate within LC." If it doesn't, the LC-Burst-D characterization here is brittle. If it does, the schema design proposal in §4 is supported on multiple LC slices and the next test escalates to HMDA.

Option 3 (FM multi-variant) is the heavy-compute option but tests a different facet (carrier-independence-across-prohibition-profiles); it's a *complement* to the explainer-root-tier story, not a *replication test* of it.

---

## 6. The cleanest single-sentence finding

*On LC pricing-space Burst D (2015H2), the disagreement explainer's root feature is an extension on all 3 subprime collapser grades and a named feature on all 3 prime grades — cleanly replicating the FM-SF centrality structure with portfolio-shaped carrier identity (loan_amnt on C2/C5, inq_last_6mths on D4, vs property_state on FM). The codification-irreducibility list is portfolio-parameterized, not a universal feature subset; the schema slot wants `(carrier-feature, carrier-feature-tier)`, not a generic boolean.*

---

## 7. Provenance

- Script: `scripts/lc_centrality_diagnosis.py`
- Saved output: `runs/lc_centrality_diagnosis_2026-05-14.json`
- Source data: `runs/extension_admitted_band_test_results.json` (committed in [[project_extension_admitted_band_result]] lineage)
- This note: post-hoc, NOT pre-registered. Treat findings as articulation, not confirmation.
- Commits: [TBD] / OTS [TBD]
