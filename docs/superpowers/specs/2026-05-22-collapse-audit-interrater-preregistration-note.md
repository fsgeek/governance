# Pre-registration — Collapse-audit inter-rater reliability (does the three-family taxonomy replicate, or is it coder-dependent?)

**Status:** DRAFT — freezes on commit (hook stamps).
**Date:** 2026-05-22.
**Builds on:** `2026-05-22-corpus-collapse-audit-result-note.md` (commit `54340f6`), which used ONE blind coder to falsify "premature-collapse is modal" and produce a three-family decomposition (honest-null 42% / collapse 33% / non-transport 25%).

## 0. The worry

A single adversary caught my confirmation bias — but a single adversary is itself a single point of failure. If the three-family split is an artifact of one coder's idiosyncratic rubric reading, it cannot bear Paper-1 weight, and neither my original frame nor its correction is real. Recursion: testing whether independent coders agree on *which failures are premature collapses* is testing whether the **categories themselves** are a premature collapse — crisp bins forced onto a continuum.

## 1. Design

Dispatch **k=3 NEW independent coders**, each given the *identical* frozen prompt that the original blind coder (rater A, coding recorded in `runs/corpus_collapse_audit_blind_2026-05-22.md`) received: the 16 result-notes + the adversarial rubric (root-cause ∈ {premature-collapse, honest-null, successful-collapse, substrate-non-transport, other}), no access to each other, to rater A's coding, or to my ledger. With rater A → **4 exchangeable raters**.

Measure on the 16 cycles:
- **5-way root-cause agreement** — pairwise exact-match rate + Fleiss' κ.
- **binary collapse-vs-not agreement** — pairwise + κ.
- **outcome (HIT/PARTIAL/MISS) agreement** — sanity floor (should be high; it's near-factual).
- **where the disagreement lands** — which cycles are unanimous vs contested.

## 2. FROZEN predictions (priors mine)

- **P1 — 5-way root-cause replicates (prior 0.40).** Pairwise exact-category agreement ≥ 70% AND Fleiss κ ≥ 0.6 (substantial). *I genuinely doubt this* — I expect the clear cases to agree and the collapse-vs-honest-null boundary to scatter.
- **P2 — binary collapse/not replicates (prior 0.55).** Pairwise agreement ≥ 85%, κ ≥ 0.6. The coarser binary should survive better than the 5-way.
- **P3 — disagreement is localized, not diffuse (prior 0.60).** ≥60% of inter-coder disagreements fall on a PRE-NAMED contested set: **disagreement-routing, frame-evocation, routable-population, refinement-#6, within-tier-predictive** (the collapse/null/non-transport boundary cycles). *Falsifier:* if disagreement is diffuse (scattered across the clear cases too), the rubric is broadly unreliable, not just fuzzy at the edges.
- **P4 — the dissolution falsifier.** If Fleiss κ < 0.4 on the 5-way AND binary agreement < 75%, the taxonomy is **coder-dependent**: the three-family decomposition (and my original frame) are downgraded to "unreliable classification of our own failures," and Paper 1 cannot rest on the taxonomy as stated.
- **Meta (frozen):** the *honest-null is modal* headline from the parent result only survives if P2 holds (binary replicates) — if coders can't even agree collapse-vs-not, the parent result's 33%/42%/25% split is noise.

## 3. Interpretation set before the run

- **High agreement (P1+P2 hold):** three-family taxonomy is real and rubric-robust → it can carry the Paper-1 reframe; proceed to thesis work.
- **Split (P2 holds, P1 fails, P3 localizes):** the binary (collapse vs not) is solid but the 5-way needs a sharper operational boundary on the contested cycles before paper use → write the boundary definition, re-code, then paper.
- **Dissolution (P4 fires):** we cannot reliably bin our own failures; the honest Paper-1 contribution is the *method* (reflexive procedure caught the author), NOT a failure taxonomy → drop the three-family thesis claim.

## 4. Bound

I wrote the rubric and chose the 16 cycles; 3 more coders test reproducibility-given-the-rubric, not rubric-validity. A perfectly reproducible bad rubric scores high here. N+1 stated, not closed.
