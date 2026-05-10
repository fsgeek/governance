# T/F Asymmetry — Exploratory Analysis

**Date:** 2026-05-09.
**Status:** Post-hoc exploratory analysis on the same V₁/V₂ data the predictive test ran on. **Findings here are not promoted to predictions of the methodology.** They explain *why* the pre-registered test had the T/F split it had, and they sharpen the mechanistic story for future pre-registrations on fresh data. Per the pre-registration discipline, exploratory analysis on the same dataset cannot retroactively rescore the predictions, only inform what comes next.
**Origin:** the V₁→V₂ predictive-test findings note (`2026-05-09-v1-v2-predictive-test-findings-note.md`) revealed that grant-supporting (T-side) directional predictions held 4/5 while deny-supporting (F-side) predictions failed 4/5. The pre-registration assumed grant/deny symmetry. This note tests three candidate explanations against the data on disk.
**Script:** `scripts/tf_asymmetry_explore.py`. Inputs: same three jsonl runs the predictive test used.

---

## 1. Headline

The T/F asymmetry is **not** an artifact of label imbalance. Charged-off rates are nearly identical across vintages (V₁=0.136, V₂=0.148, V₂_alt=0.146). H1 rejected.

The asymmetry lives in **attribution intensity** — how much weight a feature carries *when it is used* — not in which features get used. Decomposing each headline factor-support weight as `appearance_rate × weight_when_present` reveals that grant-side and deny-side respond to policy changes through different channels.

## 2. Decomposition of headline shifts

The V₁→V₂ predictive-test note reported aggregate factor support means. These decompose as follows:

### T side (grant-supporting)

| feature | V₁ appearance | V₂ appearance | V₁ weight-when-present | V₂ weight-when-present |
|---|---|---|---|---|
| fico_range_low | 0.592 | 0.704 | 0.002872 | 0.001702 |
| dti | 0.798 | 0.722 | 0.000657 | 0.000687 |
| annual_inc | 0.684 | 0.801 | 0.000337 | 0.000326 |
| emp_length | 0.098 | 0.099 | 0.000063 | 0.000058 |

### F side (deny-supporting)

| feature | V₁ appearance | V₂ appearance | V₁ weight-when-present | V₂ weight-when-present |
|---|---|---|---|---|
| fico_range_low | 0.854 | 0.900 | 0.002183 | 0.002160 |
| dti | 0.476 | 0.541 | 0.000340 | 0.000614 |
| annual_inc | 0.518 | 0.349 | 0.000270 | 0.000157 |
| emp_length | 0.091 | 0.059 | 0.000065 | 0.000046 |

## 3. Mechanistic interpretation

Reading the decompositions per feature:

- **FICO.** T-side: appearance up (+19%), weight-when-present down (−41%). Net headline T-weight down −29% (matches the predictive note). F-side: appearance up (+5%), weight-when-present essentially flat (−1%). Net F-weight up +4%. **Interpretation:** the FICO-floor mechanism (C2 in pre-registration) compresses the surviving population's FICO range from below; trees still use FICO but each split contributes less information for grant-supporting attribution. Deny-supporting FICO weight is unaffected because deny attribution operates on the *bad* end of the surviving range, which the floor doesn't compress.

- **DTI.** T-side: appearance down (−10%), weight-when-present flat (+5%). Net T-weight down −5% (matches). F-side: appearance up (+14%), weight-when-present **up +80%**. Net F-weight up +105% (matches and is dramatic). **Interpretation:** DTI ceiling tightening (C3) does not weaken DTI's grant-side signal as the pre-registration assumed; it *strengthens* DTI's deny-side signal. Above-ceiling DTI in V₂ is a much sharper indicator of charge-off because the surviving population is more selected. The pre-registration had the right mechanism applied to the wrong side of the prediction.

- **annual_inc.** T-side: appearance up (+17%), weight-when-present flat (−3%). Net T-weight up +13% (matches). F-side: appearance down (−33%), weight-when-present down (−42%). Net F-weight down −61% (matches and is dramatic). **Interpretation:** income verification tightening (C1) makes annual_inc more useful as a *grant* signal (verified income → confident grant attribution) and dramatically *less* useful as a *deny* signal. When income is reliably documented, it stops being a useful predictor of charge-off — defaults among verified-income borrowers depend on other factors (DTI, FICO). The pre-registration's "verification raises signal-to-noise" mechanism was correct for grants but predicted wrong direction for denies.

- **emp_length.** T-side: barely used in V₁ (9.8%), still barely used in V₂ (9.9%). F-side: used at similar low rate, dropped to 5.9% in V₂. Weight-when-present small and stable on both sides. **Interpretation:** consistent with the bin-4 species/feature-pool finding that the wedge's view of the world barely uses emp_length to begin with. The undirected P4 prediction hit because *any* shift counts, but the magnitude is small in absolute terms.

## 4. Decision-asymmetry hypothesis (revised statement)

The mechanistic pattern across all four features supports a sharper version of the original H2:

> **Grant decisions and deny decisions reweight features differently under policy tightening because they extract different evidence from the same features.** Grant attribution responds to *how confidently a feature supports approval given the surviving distribution*; deny attribution responds to *how reliably a feature flags risk within the surviving distribution*. These are not symmetric channels. Tightening a policy threshold compresses the grant-supporting variance (less room for attribution) while sharpening the deny-supporting signal (above-threshold cases become more discriminative).

This is a refinement of the pre-registration's mechanistic story, not a replacement. The original anchoring claims (C1–C4) were directionally correct *for the grant side*; their predicted shifts on the deny side were derived from a symmetry assumption that does not hold.

## 5. Transition-vintage instability

The 2015Q3 vintage (V₂_alt) shows striking feature-appearance instability:

- annual_inc T appearance: V₁ 0.684 → V₂_alt **0.462** → V₂ 0.801 (drops to 46%, climbs to 80%).
- emp_length T appearance: V₁ 0.098 → V₂_alt **0.567** → V₂ 0.099 (jumps to 57% mid-transition, then collapses).
- dti F appearance: V₁ 0.476 → V₂_alt 0.660 → V₂ 0.541 (peaks mid-transition).

V₂_alt is also the vintage with the lowest factor_support_T overlap (0.600, vs V₁ 0.800 and V₂ 0.867). Trees in mid-transition genuinely cannot agree on which features matter. By V₂ they have partially re-stabilized but to a *different* pattern than V₁ — emp_length usage collapses back; annual_inc usage settles higher than V₁; FICO appearance settles higher than V₁.

This is consistent with the prior `2026-05-08-vintage-stability-findings-note.md` observation about 2015Q3 turbulence but gives it a finer-grained mechanism: the turbulence is *which features the trees rely on*, not just how diversely they reason about a stable feature set.

## 6. Empty-support rate inversion

A separate structural shift not captured by the predictive test:

| run | frac empty factor_support_T | frac empty factor_support_F |
|---|---|---|
| V₁ (2014Q3) | 0.011 | 0.082 |
| V₂_alt (2015Q3) | 0.027 | 0.021 |
| V₂ (2015Q4) | 0.042 | 0.022 |

In V₁, 8.2% of (case, member) pairs had no F-side attribution at all (model: "no feature here supports denying this case"). In V₂ this drops to 2.2%. Meanwhile T-side empty rate rises from 1.1% to 4.2%. **Models in V₂ almost always articulate deny-supporting reasons but increasingly fail to articulate grant-supporting reasons.** This is the opposite of what one would naively expect from a tighter-policy regime ("more confident grants, less confident denies") and is worth a future pre-registered prediction on a fresh vintage.

## 7. What this changes

- **The methodology's mechanistic story becomes sharper.** The grant/deny asymmetry is real and articulable; future pre-registrations on fresh data should predict T-side and F-side shifts separately, with explicit per-feature mechanisms tied to compression-of-grant-variance vs sharpening-of-deny-signal. Repeating a symmetry-assumption pre-registration on a new dataset would be repeating the same disciplinary failure.
- **The P5 miss on T-side overlap is consistent with the decomposition.** Models in V₂ rely on a more concentrated feature pool for grants (annual_inc + FICO appearance both up; emp_length stays out) — that produces *more* agreement among R(ε) members about which features support grants, hence higher T-side overlap. The pre-registration predicted lower T-side overlap based on a "policy turbulence → reasoning divergence" intuition that did not match the actual mechanism.
- **The Olorin briefing gains an additional honest finding.** Even the methodology's missed prediction surfaced a real empirical pattern worth showing — that the decomposition into appearance × intensity, separated by T/F, reveals mechanism. SHAP/LIME on a single black-box would not have produced this; the Rashomon-set substrate did. (The bagging-variance baseline would also produce something here; what makes the Rashomon framing earn its keep is the constraint-respecting model class plus the per-side decomposition.)
- **No retroactive rescoring.** The predictive-test findings note stands as written. This note explains the texture; it does not change the verdicts.

## 8. What it does NOT change

- **P5 still missed on T.** The headline "reasoning-disagreement tracks underwriting-flux" claim is not vindicated by this analysis. If anything the deeper mechanism (variance compression vs signal sharpening) explains why it was the wrong-shape prediction, but the prediction was the prediction.
- **Anchoring of C1–C4 still owed.** External verification of LC's actual 2014–2015 underwriting changes is still outstanding. The mechanistic interpretations in §3 are conditional on C1–C4 being approximately accurate.
- **N=2 vintages still thin.** The decomposition's mechanistic story would benefit from replication across additional vintages and across datasets (mortgage data via HMDA or Fannie Mae) before any general claim.

## 9. Connection to other working documents

- **`2026-05-09-v1-v2-predictive-test-findings-note.md`** — the predictive-test verdicts this note explores. Verdicts unchanged.
- **`2026-05-09-v1-v2-predictive-test-pre-registration.md`** — the pre-registered predictions and mechanisms. The "Same for factor_support_F" symmetry assumption appearing in P1, P2, P3 is the specific commitment that this note's findings recommend revising for future pre-registrations.
- **`2026-05-08-vintage-stability-findings-note.md` §2** — the 2015Q3 turbulence observation that this note refines (turbulence is in feature *choice*, not just diversity).
- **`2026-05-08-bin4-k5-case-reading-findings-note.md`** — earlier instance of the same discipline pattern. The species/feature-pool inheritance there is consistent with emp_length's small role here.
