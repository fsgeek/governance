# P2-extended classifier accuracy drop — post-hoc diagnosis (centrality vs presence)

**Date:** 2026-05-14. **Status:** post-hoc diagnosis (NOT pre-registered). **Companion to:** `2026-05-13-variant-indexical-silence-manufacture-result-note.md` §3a. **Script:** `scripts/p2ext_diagnosis.py`. **Note:** this is exploratory follow-up to a surprising finding, not a frozen-prediction test. Reading it as confirmation evidence would be circular; reading it as mechanism-articulation is appropriate.

---

## The question

In #12 the property_state-saturation classifier achieved 100% accuracy on the 29-cell corpus, but extending the saturation measure to {property_state, seller_name, servicer_name} dropped accuracy to 72.4%. The result note attributed this to seller_name and servicer_name being "partially absorbed by underwriting-vocabulary features." Tony's 2026-05-14 followup: *is it seller_name, servicer_name, or both? What's the pattern in the failed classifications?*

## The data

8 false positives (cells where P2-ext predicts reorganized but they're actually censored), 0 false negatives.

**Driver attribution** (which feature pushes each cell over the 0.5 saturation threshold):

| driver | count | cells |
|--------|-------|-------|
| seller_name alone (servicer doesn't) | 2 | 2008Q1 rb02, 2018Q1 rb02 |
| servicer_name alone (seller doesn't) | 1 | 2018Q1 rb06 |
| either alone pushes | 1 | 2008Q1 rb09 |
| only the combination pushes (interaction) | 4 | 2018Q1 rb07, 2008Q1 rb00, 2016Q1 rb08, 2008Q1 rb06 |

**The pattern is the combination, not either feature.** Half the false positives need both features summed to clear the 0.5 threshold; only 3 of 8 are driven by a single feature. So Tony's intuition was right: neither alone is the culprit; their *joint presence* in a band's ufs is what makes the classifier fire incorrectly.

## The mechanism (centrality vs presence)

Look at the uf structure in the false-positive cells.

**False-positive ufs containing seller_name or servicer_name** are uniformly **FICO-rooted with the lender-identity feature appearing as a peripheral splitter**:

- `[fico, seller_name]`
- `[dti, fico, seller_name]`
- `[fico, num_borrowers, seller_name]`
- `[cltv, fico, servicer_name]`
- `[fico, ltv, servicer_name]`

When restriction drops seller_name/servicer_name, the residual uf is `{fico}`, `{dti, fico}`, `{fico, num_borrowers}`, `{cltv, fico}`, etc. — all FICO-rooted, all matching variant-B's FICO-rooted band ufs directly. Jaccard stays high → cell stays censored.

**By contrast, property_state-saturated ufs in the 3 manufactured-silence cells (2016Q1 rb00, rb05, rb09) are property_state-rooted** with the named feature (when present at all) as a secondary splitter:

- 2016Q1 rb00 ufs: `[property_state]`, `[loan_purpose, property_state]`, `[num_borrowers, property_state]`
- 2016Q1 rb05 ufs: `[dti, property_state]`, `[dti, FTHB, property_state]`, `[dti, loan_purpose, property_state]`, `[dti, property_state, servicer_name]`

Cross-check from #11 §3b: the all-explainer's feature importance on rb00 2016Q1 has property_state at **0.97**; on rb09 2016Q1 at **0.63**. These are root-level importances, not peripheral. When restriction drops property_state, the residual ufs become `{}`, `{loan_purpose}`, `{num_borrowers}` — losing the structural skeleton. Jaccard collapses → cell reorganizes.

## The asymmetry sharpened

The result note said "seller_name and servicer_name are partially absorbed by underwriting-vocabulary features." The post-hoc diagnosis sharpens this:

**property_state appears as ROOT when present** — high feature importance, primary splitter, removing it destroys the uf's structural skeleton.

**seller_name and servicer_name appear as PERIPHERAL SPLITS when present** — secondary/tertiary in the tree, supplementing rather than carrying the band structure. Removing them leaves the underlying FICO-rooted skeleton intact, which variant B's ufs also have.

The saturation metric counts **presence**; the reorganization mechanism turns on **centrality**. The two coincide for property_state (presence ≈ centrality) and diverge for seller_name/servicer_name (presence happens often, centrality rarely).

## Why structurally

A plausible mechanistic story (testable on saved tree-level data if pursued, but not done here):

- **property_state** captures geographic structural heterogeneity (regional housing-price cycles, local labor markets, state-specific foreclosure law). It provides high-information-gain splits that **compete with FICO at the root** because the geographic signal is partially orthogonal to credit-quality.
- **seller_name** and **servicer_name** capture lender-identity effects that are **highly correlated with FICO/LTV/loan_purpose mix** (different lenders specialize in different segments — e.g., a subprime lender's portfolio looks different on FICO before lender-identity adds anything). After FICO is split on, the *marginal* information in seller/servicer is small — they show up as decorative late-splits, not roots.

If true, this is one mechanism by which **rung-3b carriers are NOT homogeneous in their codification-irreducibility**. property_state is deeply codification-irreducible (its information content is not absorbed by the policy vocabulary). seller_name/servicer_name are *shallowly* codification-irreducible (their information IS mostly absorbed by the policy vocabulary; the residual appears in trees but doesn't drive band structure).

## Implication for the schema design from #12 §4a

The (variant-context, reorganization-flag, verdict-pair) tuple-slot proposal in the result note needs a fourth slot OR a refinement of the reorganization-flag: **carrier centrality**, not just carrier presence. Two readings:

**(a) Sufficient as-is.** The Jaccard-based reorganization-flag already implicitly captures centrality — peripheral seller/servicer presence produces high post-restriction Jaccard (correctly classified as censored), while central property_state presence produces low post-restriction Jaccard (correctly classified as reorganized). The discriminator works; the saturation classifier was a *proxy* for it that turns out to be less precise. Don't add a centrality slot to the schema; rely on the Jaccard.

**(b) Make the centrality explicit.** Add a slot for "carrier centrality per prohibited feature" — e.g., for each prohibited feature, the band's mean feature-importance on that feature across member trees. Lets a regulator read off "property_state is at importance 0.85 on this band; seller_name is at importance 0.07 — the band reorganization risk lives with property_state." Richer artifact, costs more to compute and report.

**My read:** (a) is sufficient for the current design. The Jaccard already does the work. The centrality story is a *mechanism explanation* for why the Jaccard works, not an additional slot to bolt on. If we ever want to make schema robustness across multiple prohibited features explicit (the multi-variant followup from #12 §6 #1), then (b) becomes worth the cost.

## What this changes about the headline finding

Nothing material. The headline of #12 was "manufactured silence is real, bounded, expansion-regime rung-3b-specific." The post-hoc diagnosis confirms the *why*: property_state is the asymmetric reorganization driver because it appears as a root in variant-A bands and removing it forces structural reorganization. seller/servicer don't drive reorganization because they're peripheral when present.

What it *does* change: the result note's parenthetical claim about seller/servicer being "partially absorbed" was directionally right but vague. The sharper claim is: **lender-identity features appear as peripheral splits because their information is largely absorbed by FICO before they get a chance to be roots.** That's testable, and the result-note phrasing should be tightened in any Paper 2 derivative.

## Limits

- **Post-hoc, not pre-registered.** Don't read this as a confirmatory test.
- **Centrality story is mechanism-articulation, not measurement.** I infer from uf structure that seller/servicer appear peripherally and property_state appears as root; the actual tree-level feature importances per band-member tree would directly confirm. Saved JSONs have explainer-level importances (#11 records the all-explainer's top importances), not band-member-tree importances.
- **One substrate (FM SF).** The asymmetry between property_state and seller/servicer is consistent across all 3 vintages tested, but whether seller/servicer remain peripheral on LC pricing-space or HMDA is not known from this analysis.
- **Sample is 8 false positives.** Statistical inference would be over-confident; this is mechanism articulation on a small case set.

## Provenance

- Script: `scripts/p2ext_diagnosis.py`
- Output: printed to stdout (no saved JSON; trivial to re-derive)
- Commits this addendum: [TBD] / OTS [TBD]
- Triggered by Tony's 2026-05-14 followup question on the #12 result.
