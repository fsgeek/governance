# Fannie Mae cross-regime pricing-space stratification (six vintages, five rate environments)

**Date:** 2026-05-12.
**Status:** Findings note (canonical for the six FM acquisition-quarter runs identified below). The cross-regime arm of the pricing-space result: the within-rate-band Cat 2 (pricing) structure found in the FM 2018Q1 pilot, replicated across vintages spanning pre-crisis boom, crisis trough, post-crisis recovery, low-rate era, and rate-spike. This is a *robustness and scaling* result for the mechanism, not a second independent "we found mispricing" headline — see §6.
**Authority:** Canonical for these six runs. Not a generalization to all of mortgage finance; six vintages from one GSE under one thin-demo policy.
**Depends on:**
- `wedge/pricing.py` (the within-grade/within-band stratification mechanism).
- `scripts/run_pricing_fm.py` (`--vintage`-parameterized FM orchestration).
- `docs/superpowers/specs/2026-05-12-pricing-space-within-grade-stratification-note.md` (the LC pricing reversal this extends; §8 there is the FM 2018Q1 pilot).
- `policy/thin_demo_fm.yaml` (the policy whose named features — `fico_range_low`, `dti`, `ltv` — define "policy-expressible").
- `data/fanniemae/Performance_All.zip` (the full FM SF Loan Performance archive, 2000Q1–2022Q2, 104 quarters, unified 113-column layout — the six vintages here were extracted from it).
- Run artifacts (each `runs/2026-05-12T*-pricing-fm-{vintage}.{jsonl,…-summary.json}`):
  - `…01-40-50Z-pricing-fm-2012Q1`, `…01-51-46Z…2016Q1` (timestamps approximate; see the files), and the 2006Q1 / 2008Q1 / 2022Q1 / 2018Q1 runs.
**Invalidated by:** A re-run at a different significance threshold or with the LLPA-grid cells as the tier (rather than rate-band deciles) will shift the counts; the qualitative finding (within-band Cat 2 structure is regime-robust) should survive.
**Last reconciled with code:** 2026-05-12.

---

## 1. What this establishes

The FM 2018Q1 pilot showed all 9 rate-bands are Cat 2 (pricing) — every band has a significant policy-expressible within-band split — with the caveat that this is partly the consequence of FM's rate being set off the LLPA grid (FICO×CLTV cells, intentionally coarse). The open question the pilot left: is that a feature of one rate environment, or robust? This note answers it by running the same mechanism on six FM acquisition quarters spanning the major regimes.

Mechanism: tier = `orig_interest_rate`, deciled *within each vintage* (so a band index means "this position in this vintage's pricing distribution" — the right comparison when the rate level shifts across regimes); for each band, two-proportion test over within-band feature deciles, BH FDR control at α=0.01; policy-expressible features = `fico_range_low`, `dti`, `ltv` (named by `thin_demo_fm.yaml`); extension feature = `loan_term_months`.

## 2. The vintages and regimes

| Vintage | Regime | Rate range | 24-mo window |
|---|---|---|---|
| 2006Q1 | pre-crisis boom (peak loose underwriting) | [3.00, 8.75] | ~2006–2008, catches the early deterioration |
| 2008Q1 | crisis trough (originated into the teeth) | [4.00, 9.50] | ~2008–2010 |
| 2012Q1 | post-crisis recovery (tight underwriting, low rates) | [2.25, 6.75] | ~2012–2014 |
| 2016Q1 | low-rate era | [2.25, 6.00] | ~2016–2018 |
| 2018Q1 | low-rate era (pilot) | [2.50, 6.25] | ~2018–2020 |
| 2022Q1 | rate-spike onset | [1.65, 5.625] | ~2022–2024 |

## 3. Results

| Vintage | n eligible | default rate | rate-bands | Cat 2 (pricing) | underpowered | sig. splits | split feature freq (fico / dti / ltv / loan_term) |
|---|---|---|---|---|---|---|---|
| 2006Q1 | 222,321 | 1.41% | 9 | **8** | 1 | 179 | 72 / 55 / 47 / 5 |
| 2008Q1 | 331,641 | **5.76%** | 9 | **9** | 0 | 243 | 81 / 81 / 70 / 11 |
| 2012Q1 | 554,489 | **0.20%** | 9 | **9** | 0 | 136 | 72 / 51 / 11 / 2 |
| 2016Q1 | 354,601 | 0.76% | 10 | **10** | 0 | 184 | 88 / 77 / 15 / 4 |
| 2018Q1 | 401,623 | 0.80% | 9 | **9** | 0 | 170 | 80 / 64 / 25 / 1 |
| 2022Q1 | 705,902 | 1.30% | 10 | **10** | 0 | 261 | 90 / 86 / 77 / 8 |

Band-level default tracks the rate cleanly in every vintage (lowest band to highest: 2008Q1 1.1%→17.1%, 2012Q1 0.07%→0.88%, 2018Q1 0.21%→2.65% — a ~12–15x spread per vintage). The rate is doing its job at the coarse level.

## 4. The robust finding

**Every rate-band, on every vintage, is Cat 2 (pricing)** — the one exception being a single underpowered band on 2006Q1 (a `qcut` artifact: lumpy rate values made one decile tiny). Across six vintages spanning ~5 rate/underwriting regimes, and across a default-rate range of **28x** (0.20% in 2012Q1 to 5.76% in 2008Q1), the within-rate-band heterogeneity is universal. FICO is the dominant recovered factor in every vintage; DTI second; LTV third. The structure does not depend on having a high base default rate — the 0.20%-default 2012Q1 vintage (554k loans, ~1,100 total defaults) still shows 9/9 Cat 2 with 136 splits; the enormous sample compensates.

## 5. Texture: LTV tracks regime stress

A clean regime-dependence in the *composition* of the recovered factors: LTV is a major recovered factor in the boom/crisis/rate-spike vintages (47 / 70 / 77 splits in 2006Q1 / 2008Q1 / 2022Q1) and a minor one in the calm low-rate vintages (11 / 15 / 25 in 2012Q1 / 2016Q1 / 2018Q1). This is intuitive — LTV matters most for default when home prices are volatile (the path to underwater is open) — and it is the kind of regime-dependent structure the mechanism should surface: in stress regimes, the rate-band tier conflates not just FICO strata but LTV strata, in proportions that track the macro environment. 2008Q1 is the extreme: 5.76% default, 9/9 Cat 2, 243 splits, with FICO / DTI / LTV all heavily implicated (81 / 81 / 70) — the crisis-cohort's rate did not separate any of the three policy-named risk factors well, exactly the kind of thing a post-mortem of crisis-era underwriting would want flagged.

## 6. The "by design" caveat, restated and sharpened

FM's rate is set off the LLPA grid, which prices in FICO×CLTV *cells* with intentionally coarse bins. So "FICO predicts default within a rate-band, in every regime" is *partly the expected consequence of the grid's bin coarseness*, not a regime-dependent pricing error a black-box model uniquely discovered. This makes the cross-regime result a **robustness and scaling** finding for the mechanism — it works at FM's 200k–700k-loan scale, across rate environments, without modification — and *not* a second independent "FM mispriced these loans" headline alongside the LC DTI finding (where LC's `sub_grade` is the lender's own composite risk assessment, so the within-grade DTI split is a genuine "you used a named factor coarsely" finding).

Two things the cross-regime run *does* establish, beyond robustness:
- **The within-band coarseness is regime-robust.** A future analysis that asks "is the within-band high-default sub-population correlated with a protected-class proxy?" (the governance-significance follow-up the mechanism does not itself run) will not be confounded by "we only looked at one rate environment" — the structure is there in every regime.
- **The grid's bins conflate substantial within-band risk differences, everywhere.** Within FM 2018Q1's highest rate-band, FICO ≤ 643 vs > 643 defaults 5.6% vs 2.3% — a 2.4x difference along a factor the LLPA grid names. Whether bins that coarse are *acceptable* is a policy judgment; the mechanism's job is to flag that the documented pricing artifact conflates a 2.4x risk difference, and it does, in every vintage tested. "By design" is not the same as "fine."

## 7. What this does and does not establish; next

Establishes: the pricing-space mechanism scales to FM and is regime-robust; the within-rate-band Cat 2 structure is universal across six vintages and five regimes; LTV's role in that structure tracks macro stress; the LLPA-grid-derived rate-band tier conflates ~2x+ within-band risk differences along policy-named factors in every regime.

Does not establish: that FM mispriced loans (the within-band signal is partly the grid's intended bin coarseness); that the coarseness has disparate impact (needs the protected-class-proxy follow-up); that the result generalizes beyond Fannie Mae / beyond first-lien owner-occupied purchase-refi / beyond the thin-demo policy vocabulary.

Next:
- **Option (C): tier = the LLPA grid's own FICO×CLTV cells**, not rate-band deciles. This audits the *documented pricing artifact* directly rather than the rate it produces — the worked instance of "policy codification as infrastructure." Needs the era-appropriate LLPA grid encoded (the grid revises over time; for a 2018 vintage, the 2018-era grid). The Cat 2 question becomes "within an LLPA cell, does a policy-expressible factor stratify realized default?" — and a positive answer there is the cleaner "the documented grid is too coarse" finding, free of the rate-as-noisy-proxy concern.
- **The protected-class-proxy follow-up**: do the within-band/within-cell high-default sub-populations correlate with a geographic or other protected-class proxy? That is the step that converts "coarse" into "disparate impact" or rules it out.
- **Full-archive density**: 6 of 104 quarters here. The remaining vintages add density within the regimes already covered; not needed for the cross-regime claim, available if a reviewer wants the dense version.
