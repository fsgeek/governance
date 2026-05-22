# Result note — Corpus collapse-audit: my frame was confirmation-biased, and the discipline caught it

**Pre-reg (FROZEN, OTS-stamped):** `2026-05-22-corpus-collapse-audit-preregistration-note.md` — commit `5928dc0`.
**Blind classifier:** independent agent, adversarial rubric, no access to my §3 ledger. Coding reproduced in §3 below.
**Date:** 2026-05-22.

## Headline

**C1 (premature-collapse is the modal failure) is FALSIFIED on the blind coding.** I predicted collapse-root on 11/16 cycles (~80% of burned cycles). The blind classifier found premature-collapse in only **4 of 12 burned cycles (~33%)** — a *plurality of one-third*, not a majority. My frame, minted three turns earlier, was a seductive over-fit, and the pre-registered ledger + blind adversary caught it red-handed. This is the best available outcome for "work to falsify it."

## Scorecard against the frozen predictions

- **P1 — modal (≥70%): FALSIFIED.** Blind: premature-collapse = 4/12 burned (33%). The **modal** failure family is **honest-null** (5/12, 42%): the predicted effect simply wasn't there — which is the *already-documented* pre-registration-uniformity pattern. A third family, **substrate-non-transport** (3/12, 25%), is comparably sized. Three roughly-equal families, honest-null largest. (prior 0.70 → decisively wrong)
- **P2 — non-instances exist (≥2): CONFIRMED, emphatically.** Blind found **10** non-collapse cycles (5 honest-null + 3 non-transport + 2 successful-collapse), against my floor of 2. The clean non-instances I'd nominated (shap-vs-rashomon, saturation) held, plus seven more I had wrongly called collapses. (prior 0.80 → confirmed and then some)
- **P3 — margin=receipt: not adjudicated numerically; reframed.** The blind result shows margin only *applies* to the genuine-collapse subset (4 cycles); it is meaningless for honest-nulls (no effect to have margin) and non-transports (the effect is real, it just doesn't travel). Full numeric P3 deferred to a followup, because the population it presupposed turned out to be a minority.
- **P4 — the hunted violation (#14): CONFIRMED, independently.** The blind classifier flagged #14's discriminator AUC = 1.000 as "a textbook hypothesis-layer premature collapse... AUC falls to 0.763" out-of-sample. This is exactly the high-margin-yet-deceptive case: huge margin from a naive 0.5 threshold, worthless out-of-sample. **Naive margin=receipt is wrong as stated; the receipt must be held-out (or vs-placebo) margin.** (prior 0.60 → fired as designed)
- **Meta-commitment honored:** the result is *not* clean. P1 failed, P4 fired. I report the disconfirmation as the finding.

## Where I was wrong (me vs blind)

I over-attributed collapse on ~7 of 16 cycles. The instructive disagreements:
- **disagreement-routing** — I called it "the canonical collapse." Blind: **honest-null** — disagreement tracks *signal*, not *confusion*; there was no reliability structure to discard, the per-case referent simply doesn't exist. The blind call is the sharper one.
- **frame-evocation** — I said collapse; blind: **underpowered honest-null** (all discriminators tie at AUC 0.89–0.97, permutation p≈0.7). No margin to find at n=29.
- **shap-vs-pricing, routable-population** — I said collapse; both are honest-nulls (the predicted absence wasn't there).
- **refinement-#6, hmda-trimodal, fm-#11** — I said collapse; blind: **substrate-non-transport** — a generalization limit, a distinct and well-populated category my frame had no slot for.

## The recursion (the actual finding)

I collapsed the project's heterogeneous error-log — honest-nulls, non-transports, successful reductions, and genuine collapses — into the single label "it's all premature collapse." **That act was itself a premature collapse.** I committed the sin three turns into diagnosing it, and the only reason it's visible is that I froze the ledger and hired an adversary before computing. The lesson is not about collapse; it's that **the frame is most dangerous to its own author at the moment it feels most explanatory**, and the only defense that worked was procedural (freeze + blind adjudication), not introspective.

This *strengthens* the project's real thesis while puncturing my version of it: premature-collapse is a genuine, recurring failure mode (33%, including the load-bearing #14 deceptive spike) — but the honest decomposition is **three comparable families, honest-null modal**, and any single-scalar story about "the" failure mode is exactly the error the project exists to name.

## Followups (four-state)

- **(i)** Re-issue the Paper-1 frame as **three-family**, not monocausal: honest-null (uniformity-assumption), substrate-non-transport, premature-collapse. The premature-collapse strand keeps #14 as its worked deceptive-spike example.
- **(ii)** Numeric P3 on the 4-cycle genuine-collapse subset only, with margin redefined **out-of-sample / vs-placebo** (per #14). Small, well-posed.
- **(iii)** The me-vs-blind disagreement on routing/frame-evocation (collapse vs honest-null) is a real rubric ambiguity — "no signal" vs "signal discarded by the scalar." Worth a sharper operational boundary before either label bears paper weight.
- **(iv)** Honest-null being modal is *already* in the project memory as the pre-registration-uniformity pattern; this audit independently re-derives it via an adversary, which is corroboration, not novelty — and a check on whether that memory was itself over-claimed (it wasn't).
