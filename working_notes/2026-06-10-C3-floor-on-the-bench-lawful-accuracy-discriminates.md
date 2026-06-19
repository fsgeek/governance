# The C3 floor, demonstrated: a G-blind lawful score STILL discriminates because base rates differ

**2026-06-10. The keystone. Diagnoses WHY loop-closure raised disparity
([[2026-06-10-loop-closure-and-fable-corrections]]). Script: `scripts/lawful_leak_diagnosis.py`.
Output: `runs/lawful_leak_diagnosis.json`. Frozen P2 (0.35) WON — the deep finding, not the leak.**

## The question

Loop closure shrank the band but RAISED disparity. Two explanations: (LEAK) the "lawful" feature
secretly predicts G via the joint/nonlinear path; (C3) the rise is not a leak but the structural
fact that any accurate lawful model discriminates in OUTCOMES when base rates differ by group.

## Result — unambiguous, all 4 channels, lands on C3

```
  channel  AUC(G~lawful_score)  base_default_rate_gap(G1-G0)  grant_disparity_from_pure_lawful_threshold
  D1        0.348                 -0.170                        +0.201
  D2        0.413                 -0.130                        +0.108
  D3        0.407                 -0.133                        +0.095
  D4        0.409                 -0.129                        +0.125
```

- **The lawful score does NOT predict G** (AUC 0.35–0.41 — at/below 0.5, genuinely G-blind; NOT a
  leak). With binary G, linear residualization removes the full E[feature|G], so Fable's
  linear-orthogonalization worry — correct in general — is NOT what raised disparity here.
- **Yet a pure G-blind lawful-score threshold creates 10–20% grant disparity** — because **base
  default rates differ by group** (G1 defaults LESS, gap −0.13 to −0.17). A genuinely lawful,
  accurate risk model denies the higher-risk group more, and risk correlates with G for LAWFUL reasons
  (the DGP entangles G with x0, a legitimate risk factor). **Accuracy itself produces group disparity.**

## THE FINDING (C3 floor as an operational theorem)

> You cannot "increase profitability while holding discrimination at the floor" by mining lawful
> signal, because the more accurate the lawful model, the more it sorts on real risk, and when real
> risk differs by group, accurate lawful sorting PRODUCES group disparity. Profit (accuracy) and
> group-disparity are coupled THROUGH THE BASE-RATE DIFFERENCE ITSELF — not through any proxy, leak,
> or laundering. In the loop-closure run, adding the lawful feature raised disparity BECAUSE IT WORKED.

This is the C3 non-identifiability the whole project orbits, shown operationally: a G-blind score
still discriminates in OUTCOMES because the world's risk is G-correlated. It is NOT fixable by better
features, better orthogonalization, or a neutral third party. It is the disparate-impact /
business-necessity tension in irreducible form.

## What this does to Tony's pitch (narrows it to the TRUE, defensible form)

- **DEAD: "do well by doing right for FREE."** Profit-increase at zero disparity-cost is forbidden
  when base rates differ by group — by structure, not by tooling. The earlier "negative coupling →
  mine freely" reading ([[2026-06-10-profit-disparity-frontier]], already softened by Fable's
  finite-sample point) is now fully killed: that negative coupling was within a FIXED band at fixed
  accuracy; the moment you INCREASE accuracy by mining, you climb the base-rate-driven disparity.
- **ALIVE, and stronger for being honest: the band makes the accuracy–disparity FRONTIER visible and
  attestable.** The bank cannot escape the frontier, but it can SEE it and CHOOSE its operating point
  on it — disclosed, like a capital ratio. The contribution is not "free fairness"; it is "the
  trade-off you were making implicitly is now an explicit, attested, auditable institutional choice."
  The empty chair is defended not by erasing the trade-off (impossible) but by making the bank OWN it
  in the open.

## Honest scope

- Synthetic; the base-rate gap is DGP-built (G entangled with x0 by design). On real data the base-rate
  gap is an empirical fact subject to the proxy-measurement loss
  ([[2026-06-10-proxy-loss-is-differential-only]]); the STRUCTURE (accuracy×base-rate-gap → outcome
  disparity) is substrate-independent and is just the standard impossibility (Chouldechova/Kleinberg:
  can't have calibration + equal grant rates when base rates differ). This probe RE-DERIVES that on the
  Rashomon bench and ties it to the profit pitch — the contribution is the TIE, not the impossibility
  (which is known).
- The frontier-visibility claim (band exposes the accuracy-disparity menu) is asserted from the
  profit-disparity result; a clean frontier plot (sweep operating points, show the Pareto front) is the
  honest next artifact.

## Meta

Priored predictions: this one I called P2 at 0.35 and it WON — my second priored hit of the engagement
(after the proxy attenuation theorem), and again because it was a structural/theorem claim (base-rate
impossibility) not a narrative. Fable's review forced the leak-vs-C3 diagnosis that surfaced it; the
enthusiastic-instance victory lap would have shipped "do well by doing right" over a buried C3 floor.
The arc: failed protected-detector → due-process score → failed canary → profit frontier → C3 floor
on the bench. Every reframe truer and narrower than the last.
