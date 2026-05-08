# Vintage Stability — Findings Note

**Date:** 2026-05-08
**Status:** Empirical findings note from a 3-vintage sweep (2014Q3, 2015Q3, 2015Q4) using the wedge as built (local-density + Ioannidis-suspicion species). Companion to the indeterminacy operationalization and adversarial-robustness memos.
**Scope:** What survives across vintages, what doesn't, and the structural axis the split implies. Not a generality claim (N=3 across one dataset is too thin) but a methodological observation about which findings are regime-specific and which are regime-general.

---

## 1. Headline

The 3-vintage sweep produced a structurally informative split: **some findings are robust across vintages; others are sharply vintage-dependent**, and the split is not random — it tracks a meaningful axis (model-driven signal vs applicant-driven signal). Tony's pre-registered prediction ("findings won't hold up, and selection-criteria changes will be at least partly responsible") was partially correct in a sharper way than the binary version of the prediction would have been.

| Finding | 2014Q3 | 2015Q3 | 2015Q4 | Stability |
|---|---|---|---|---|
| Q1−Q4 default rate (quartile-binned atypical-defaults-LESS) | **−0.022** | +0.017 | −0.006 | Vintage-dependent |
| All-atypical extreme default rate | 11.6% (n=362) vs 13.6% baseline | 7.8% (n=77) vs 14.6% | 11.8% (n=586) vs 14.8% | **Robust at the tail** |
| Ioannidis multiple-of-25k % of whole-thousand reporters (null = 4%) | 14.0% | 14.7% | 14.6% | **Robust** |
| Cross-species non-overlap (Ioannidis-flagged that are LD-ordinary) | ~85% | ~85% | ~87% | **Robust** |
| Median pairwise overlap_T among agreers | **0.80** | **0.60** | **0.87** | Highly vintage-dependent |
| Outcome-agreer rate | 96.0% | 82.2% | 98.9% | Highly vintage-dependent |

## 2. The 2015Q3 anomaly

The original wedge run on 2015Q3 produced median pairwise overlap_T = 0.60 among outcome-agreers. We treated this as the methodology's empirical anchor — below the collapse threshold (0.7), striking enough to write up. The vintage sweep shows that **0.60 is a 2015Q3 phenomenon, not a methodology-general one.** Both neighboring vintages produce overlap_T of 0.80 or higher and outcome-agreer rates of 96–99%. The methodology extracted more reasoning-disagreement signal from 2015Q3 than from either neighbor.

What made 2015Q3 different is consistent with Tony's selection-criteria mechanism prediction. 2015Q3 sits in a period when LC's underwriting was in flux: documented industry-wide changes in income verification and FICO weighting were rolling through the unsecured-personal-loan space. A transition vintage will produce a less coherent approved population, which lets equally-good models carve the population in more diverse ways. Stabler regimes (2014Q3, 2015Q4) produce more model convergence because the underlying population is more uniform.

This is consistent with the predictive-extension hypothesis from the 2026-05-07 wedge spec §3 — that factor-support distributions in R(ε) shift in directions predictable from documented policy deltas. We didn't pre-register a prediction about 2015Q3 specifically being a transition vintage, but we now have empirical evidence consistent with the broader claim.

## 3. The vintage-sensitive / vintage-stable axis

The species split observed in the data is not a coincidence. It has a structural interpretation:

- **Vintage-sensitive species** detect *selection-driven signal* — how the underwriting regime carves up the approved population. The species output depends on how the models were fit, which depends on what the population looked like, which depends on selection. Examples in the wedge: factor-support overlap (overlap_T), quartile-binned local-density default-rate gradients.

- **Vintage-stable species** detect *applicant-driven signal* — properties of how applicants behave (round-number reporting, threshold-hugging) or properties of the case-feature geometry (cross-species independence). The species output depends on the applicants and on the structure of the feature space, neither of which is sharply altered by underwriting policy. Examples in the wedge: Ioannidis round-number tier rates, Ioannidis-vs-local-density non-overlap rate.

This split is *useful*, not a defect. A methodology whose species all moved together with the regime would be over-determined by the regime; a methodology whose species all stayed flat would be insensitive to the regime. The vector-of-species design produces both, with the choice of *which species to weight* depending on what claim is being made.

## 4. The all-atypical tail effect

The most empirically robust positive finding from the sweep: **cases that every model in R(ε) flags as locally-atypical default at lower rates than the baseline, and this holds in all three vintages** with effect sizes of 2–7 percentage points and sample sizes of 77 to 586. The middle quartiles of the I distribution show vintage-dependent default-rate behavior; the *all-atypical extreme tail* is consistent.

This rescues the atypical-defaults-LESS finding from the "specific to 2015Q3" worry. The original observation wasn't just an artifact of one vintage — it's a tail behavior that survives across regimes, even though the quartile-binned version of the same observation does not.

Mechanistic interpretation, consistent with the original framing: the all-atypical population includes a meaningful fraction of *unusual-but-strong* borrowers (rare positive feature combinations) that LC's selection process funnels through despite their atypicality. The middle of the I distribution mixes unusual-but-strong with unusual-but-weak in proportions that vary by selection regime; the extreme tail concentrates the "all models agree this is weird" cases, which skew toward the unusual-but-strong direction more consistently.

## 5. Implications

**For the methodology spec.** The species-stability axis should be captured in spec language. Each species' production write-up should declare whether it carries a regime-specific claim or a regime-general claim, and in what circumstances each species' output would or would not generalize. This is a real spec evolution, not just documentation hygiene — it changes what the methodology promises an examiner.

**For the position paper.**
- Claims about reasoning-disagreement (overlap_T) are *regime-specific* claims. The position paper should not lead with "the methodology extracts factor-support disagreement of 0.60 from outcome-agreers"; that's specific to 2015Q3 and may not hold elsewhere.
- Claims about applicant-side detection (Ioannidis round-number signal at 3.5× null, robust across three vintages) are stronger and travel.
- Claims about cross-species independence (~85% non-overlap, robust across vintages) are also stronger.
- The all-atypical tail effect can be claimed across vintages with appropriate sample-size caveats.
- The 2015Q3 transition-vintage effect, *if* documented LC policy-shift evidence corroborates it, is itself a methodological contribution: the methodology surfaces signal precisely when the regime is in flux.

**For the next ghola's priorities.** Retrospective-trajectory remains the next-priority species (two independent load-bearing arguments from the prior memos). The vintage sweep extends but does not replace that priority — implementing retrospective-trajectory will let us test whether *its* output is vintage-sensitive or vintage-stable, which is itself a structurally useful question.

## 6. Explicit non-commitments

- **N=3 across one dataset is not generality.** The project's research-design rule is N≥3 (5+ preferred) *across datasets*. HMDA remains the planned second dataset. This sweep advances the within-LC characterization; it does not advance cross-dataset generality.
- **The transition-vintage interpretation of 2015Q3 is hypothesis, not finding.** It is consistent with the data and with general knowledge of LC's documented shifts, but a tighter test would map LC's actual quarter-by-quarter underwriting changes against the methodology's overlap_T trajectory across all available vintages, which we have not done.
- **The vintage-sensitive / vintage-stable split is observed, not proven.** With three vintages the structural axis is suggestive; with N≥5 we'd be able to argue it more confidently. The current evidence is enough to motivate spec revision but not to claim the axis as a methodology law.
- **The all-atypical tail effect's mechanism is interpretation, not measurement.** Whether the tail concentrates "unusual-but-strong" cases is a hypothesis about the population, not a measurement of it. Stratifying the all-atypical population by T to see whether they have higher predicted-grant confidence than baseline would be the next test.

---

## Connection to other working documents

- **2026-05-07 wedge design spec** §3 (predictive-extension hypothesis): the 2015Q3 transition-vintage observation is consistent with the spec's prediction that policy-delta-driven shifts in factor support are detectable. The sweep doesn't formally test that hypothesis (no documented policy delta was named in advance) but the evidence is in the right shape.
- **2026-05-08 indeterminacy operationalization memo**: the species-stability-axis is a refinement of that memo's vector-of-species argument. The four species don't just detect different things; they have different stability properties, and the methodology's claims need to be calibrated to those properties.
- **2026-05-08 adversarial-robustness memo**: vintage-stable species (Ioannidis, cross-species non-overlap) are also the species *most exposed* to adversarial adaptation under publication, because applicant-side signal is what an adversary can directly modify. Vintage-sensitive species are less adversarially exposed (an applicant cannot change LC's underwriting regime). The two structural axes — vintage stability and adversarial robustness — are roughly orthogonal, and the species architecture happens to span both.
