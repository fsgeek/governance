# Within-tier disagreement as a routing signal — pre-registration

**Date:** 2026-05-12.
**Status:** Pre-registration. **No experimental code has been written at the time of this note.** Predictions and hit/miss criteria recorded before any code touches the held-out quarter. Same discipline as the preceding pre-regs in this session. Follow-on to **#6** (`2026-05-12-policy-constrained-rashomon-refinement-result-note.md`).
**Origin:** #6 showed the policy-constrained Rashomon refinement band on the 2015H2 `dti` burst is *plural* — on grade B1 (2015Q3) the band members rank the tier's borrowers with a median pairwise Spearman of ≈ 0.17, real disagreement — and the project's founding methodological idea (`project_rashomon_methodology`, the README's adversarial-review concept) is *within-Rashomon disagreement as a routing signal*: the cases the policy-admissible models can't agree on are the ones a contemporaneous monitor should route to human review rather than auto-decide. #6 gave us tiers where disagreement is measurable; this test asks whether that disagreement *does* anything — whether high-disagreement borrowers are the ones where no policy-admissible refinement is trustworthy. If yes, "the set is plural" becomes "the set tells you which cases need a human" — the contemporaneous-observability product's actual point, and a SHAP-incapable function. If no, the plurality, even where it exists, carries no actionable routing information — which deflates the plurality-superiority argument (plurality you can't act on isn't much of an advantage), and *that* is a finding too.
**Companion:** result note `docs/superpowers/specs/2026-05-12-disagreement-routing-result-note.md` (after the run).

---

## 1. Question

In the tiers where the policy-constrained Rashomon refinement band is plural (the 5 plural grades of Burst D from #6: A5, B1, C1, C5, D4 on 2015Q3), does **per-borrower disagreement among band members** function as a routing signal — are the high-disagreement borrowers the ones where the band's consensus prediction is least reliable?

## 2. Setup

- **Substrate:** LC 36-month, Burst D — band *built* on V₁ = 2015Q3 (per #6's construction), routing-evaluated on V₂ = 2015Q4. The plural grades from #6: **A5, B1, C1, C5, D4** (median pairwise Spearman < 0.9 in #6; B1 the most disagreeing at 0.167). (Robustness: also report the in-sample version on 2015Q3.)
- **The band:** for each grade G, the policy-constrained refinement band from #6 (named features, depth-bounded CARTs, monotonicity sign-flipped to default-prediction, ε = 0.02), distinct members, each re-fit on the full 2015Q3 grade-G data — *frozen*.
- **Per-borrower disagreement:** for borrower x in V₂'s grade-G loans, `d(x) = std({m.predict_proba(x)[default] : m ∈ band})` — the spread of the band members' predicted-default probabilities on x. (Per-*borrower* disagreement; #6's Spearman was *tier-level*.)
- **Consensus prediction:** `p̄(x) = mean({m.predict_proba(x)[default] : m ∈ band})`.
- **Buckets:** terciles of `d(x)` over V₂'s grade-G loans — high / middle / low disagreement.

## 3. Metrics (all pre-registered, all reported)

For each grade G (on V₂ unless noted):
1. **Tercile predictability.** For each band member, its within-tercile AUC for default in the low-`d` and high-`d` terciles; report the *mean over members* per tercile, against a grade-size-aware label-shuffle null (95th pct, 500 perms, per tercile). Routing-relevant if low-tercile mean AUC > high-tercile mean AUC, with the low above its null and the high weaker.
2. **Disagreement vs consensus calibration gap.** Bin V₂'s grade-G loans into deciles of `d(x)`; per decile compute `|mean(realized default) − mean(p̄)|`; report the Spearman of (decile index, gap). Routing-relevant if positive (consensus is more miscalibrated where the band disagrees).
3. **Disagreement vs consensus Brier.** Per `d`-tercile, the Brier score `mean((p̄ − y)²)`; report high − low. Routing-relevant if positive.
4. **Operational lift.** The band-average's calibration error (e.g., the absolute gap between mean `p̄` and mean realized default, computed within `p̄`-deciles and averaged — an ECE-style number) on *all* of V₂'s grade-G loans vs on the *low + middle* terciles only (i.e., if the high-`d` tercile is routed to manual review and removed from the auto-refined population). Routing-relevant if the auto-refined-population calibration error is meaningfully smaller.

Aggregate over the 5 plural grades: **"disagreement is a valid routing signal"** holds iff metrics 1–3 point the routing-relevant way on a *majority* (≥ 3/5) of the plural grades, with metric 4 showing non-negative operational lift on a majority. **Falsified** iff a majority of the plural grades show metrics 1–3 *not* pointing the routing way (high-`d` tercile as predictable / well-calibrated as the low-`d` tercile).

## 4. Pre-registered predictions

> **Partial validity, weak lift.** I expect the routing signal to be *real but small*: the calibration gap (metric 2) will be modestly increasing in `d` on a majority of the plural grades, and the low-`d` tercile will be modestly more predictable (metric 1) than the high-`d` tercile — because per-borrower disagreement *should* track underdetermination (genuine ambiguity, or extrapolation into sparse feature regions; either way, "the policy-admissible models don't know" is a reasonable route-to-human trigger). But the effect will be small: the within-tier AUCs are 0.53–0.61, so there isn't much predictability to differentiate, and metric 4's operational lift (calibration improvement from routing out the high-`d` tercile) will likely be small in absolute terms (a few tenths of a point). So: **"valid but weak"** — the routing signal exists, the practical lift is modest, the honest framing is "disagreement flags the cases worth a second look, and routing them out modestly tightens the auto-refined population's calibration; it is not a dramatic improvement."
>
> **B1 (the most-disagreeing grade) should show the clearest pattern** — if any grade is "valid and not-weak," it's B1.
>
> **If the routing signal is *not* valid at all** (high-`d` tercile just as predictable, calibration gap flat in `d`) — that is the deflating finding: the plurality, even where it exists, is plurality among equivalent models that doesn't localize to "the hard cases," so it doesn't carry the routing function the methodology promised. The plurality-superiority argument would then have to rest on aggregate-model-risk *surveillance* (the bank sees the full set of admissible refinements) rather than per-case *routing* — a weaker but still real claim. I assign this ≈ 30% probability.
>
> **A possible *positive surprise*:** if disagreement is driven mostly by feature-region sparsity (V₂ borrowers in regions the V₁ band didn't see well), the routing signal could be *strong* — "route the borrowers the admissible models extrapolate on" is a clean, robust trigger — but the *story* would be "extrapolation detection," subtly different from "genuine ambiguity." I'll report which reading the data supports (e.g., by checking whether high-`d` borrowers are feature-space outliers within the tier).

## 5. Why this is the right test now

#6 established the plurality dimension exists on the load-bearing episode but left open whether it *does* anything. The methodology's promise — and the part SHAP structurally can't touch — is that within-Rashomon disagreement *routes*: it tells a contemporaneous monitor which cases to auto-decide and which to hand to a human, with the routing decision itself auditable (it's a property of the documented policy-admissible model class, not a black-box confidence score). This test is the direct check on that promise, on real tiers with a real disagreement signal, with a falsification path (high-`d` cases as predictable as low-`d` ones ⇒ the promise doesn't hold) and an operational metric (does routing-out actually tighten calibration). The verdict either way feeds the regulator-facing document's account of what contemporaneous policy-constrained observability *does* — auto-decide-vs-route is the operational core of that account.

## 6. Followups (not part of this pre-registration)

- **Characterize the high-`d` sub-population** — are they feature-space outliers within the tier (extrapolation), near a policy threshold (the `dti_ceiling` at 43, the `fico_floor` at 620), or genuinely interior-but-ambiguous? Determines whether the routing story is "extrapolation detection" or "genuine indeterminacy."
- **The adversarial-review instantiation** — for a high-`d` borrower, the band members that most disagree are the "advocates"; surface their differing feature emphases as the residual decision a human adjudicator faces (the README's adversarial-review concept, made concrete on one case).
- **FM variant** — disagreement-routing on the FM thin-demo bands (LTV available).
- **Burst A** — the `annual_inc` burst's bands were *not* plural (#6); a sanity check that the routing test correctly finds *no* routing signal there (disagreement near zero everywhere ⇒ nothing to route) — confirms the test isn't manufacturing a signal.
