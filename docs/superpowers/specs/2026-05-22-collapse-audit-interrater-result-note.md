# Result note — Inter-rater reliability: the fine taxonomy is coder-dependent, the negative headline is rock-solid

**Pre-reg (FROZEN, OTS-stamped):** `2026-05-22-collapse-audit-interrater-preregistration-note.md` — commit `8ea285e`.
**Raters:** A (original, `runs/corpus_collapse_audit_blind_2026-05-22.md`) + B, C, D (3 new, identical frozen rubric, mutually blind). Codings preserved in `runs/corpus_collapse_audit_interrater_2026-05-22.md`.
**Date:** 2026-05-22.

## Headline

The three-family taxonomy **half-blew-up, in the informative half.** The *negative* claim — premature-collapse is NOT the modal failure — **replicated 4/4 independently** (every rater put premature-collapse at 3–6 of 16 and honest-null as the largest or tied bucket). But the *fine-grained per-cycle family labels* are **coder-dependent**: 5-way Fleiss κ = 0.537, binary κ = 0.546, both below the bars I froze. So: the robust finding is the negative one; a crisp per-cycle taxonomy cannot bear paper weight.

## Scorecard against frozen predictions

- **P1 — 5-way replicates (κ≥0.6 AND pairwise≥70%): FAILED.** κ=0.537, pairwise 64.6%. (prior 0.40 — I doubted it; doubt confirmed.)
- **P2 — binary replicates (κ≥0.6 AND ≥85%): FAILED, narrowly.** κ=0.546, pairwise 82.3%. Even collapse-vs-not is only *moderate* agreement, under the bar. (prior 0.55.)
- **P3 — disagreement localizes to my named set: FALSIFIED.** Only 3/9 contested cycles were in my named set {routing, frame13, routable, refine6, within}. I named **routable and within as contested — both came back UNANIMOUS** — and missed the real scatter cells (dis-geometry, ext-band, fm11, silence12). I could not predict where coders disagree. (prior 0.60.)
- **P4 — dissolution (κ<0.4 AND binary<75%): NOT triggered.** κ≈0.54, binary 82.3%. The taxonomy is fuzzy, not dissolved.

We landed in the pre-registered **"split" zone**: binary moderate (not solid), 5-way boundary-fuzzy → needs a sharper operational boundary before any per-cycle label is paper-usable; the robust contribution is the *method* + the negative claim.

## What the disagreement IS (not noise — structure)

The 8 cells that replicated unanimously (5-way or near): i-stability, v1v2, within-tier, shap-pricing, routable, hmda, expanded#14, plus near-unanimous saturation/frame13 — are the **single-outcome** cycles. The cells that scattered — **disagreement-geometry, extension-admitted, fm#11, variant-silence#12** — are precisely the **multi-leg experiments** (P1-HIT/P2-MISS/P4-MISS, A-HIT/P4-strict-MISS, mixed scorecards). The rubric forced ONE dominant root-cause; reality is multi-causal; **the inter-rater disagreement is the multi-causality leaking through the single-label demand.**

So the unreliability is itself a finding, and it is the project's own frame turned one level deeper: **forcing a multi-causal failure into one root-cause label is itself a premature collapse.** The categories scatter exactly where the failures are genuinely plural — which is most of the interesting ones.

## What this means for Paper 1 (the question that prompted this)

- **Safe to claim (4/4 replication):** the project has **no single modal failure mode**; premature-collapse is one of several recurring modes (~25–37%), honest-null/uniformity is at least as common, substrate-non-transport is a third. Heterogeneity is the texture.
- **NOT safe to claim:** the crisp 33/42/25 split or any per-cycle family assignment — these are coder-dependent.
- **The robust contribution is the method:** reflexive pre-registered falsification, with blind + multi-rater adjudication, caught (a) the author's confirmation bias and (b) the limit of its own taxonomy. That is paper-ready and does not depend on the fragile labels.

**Verdict on the original fork:** do NOT reframe Paper 1 around a clean three-family taxonomy — it doesn't replicate. DO, if anything, write the *method* (reflexive falsification as the contribution) and state failure-heterogeneity as a qualitative claim, not a quantitative partition.

## Followups (four-state)

- **(i)** Write the method/reflexivity strand as the paper-ready piece (the blog-spine from session start), backed by this two-experiment cascade.
- **(ii)** If a taxonomy is wanted, allow **multi-label** root-cause coding (not forced-single) and re-measure agreement; predict κ rises because the scatter was the single-label demand.
- **(iii)** The unanimous cells (8/16) are a reliable sub-corpus; any quantitative claim should be restricted to them, with the multi-leg cells reported as "multi-causal, unclassified."
- **(iv)** Honest-null modality is now triple-corroborated (parent audit + 4-rater replication + the existing [[project_pre_registration_pattern]] memory) — the most robust single fact in this cascade.
