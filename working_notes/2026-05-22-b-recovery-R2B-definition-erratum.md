# Erratum / clarifying companion to the #15 B-recovery pre-registration — the R²_B definition

**Status:** working note, UNCOMMITTED. **Does not modify** the OTS-stamped pre-reg
(`docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md`, commit `5a154b1` / OTS `9628d3d`).
The stamp, the frozen predictions, the screen cutpoints, and the baseline are **untouched**.
This note records a prose/implementation discrepancy in the central quantity and the falsification
battery run on 2026-05-22. **Speech-act class:** constative + a flagged decision for Tony.
**Connects:** `working_notes/2026-05-22-manufactured-silence-in-review.md` (this is the fifth-level
instance that note's mechanism predicts), `[[project_silence_manufacture_result]]`,
`[[project_pre_registration_pattern]]`, `position-desai-foil.md`.

---

## 1. The discrepancy

The pre-reg defines its central quantity `R²_B` **only** in the glossary (line 15):

> "band A uses the documented 4-feature named-policy vocabulary; band B **additionally admits
> extension features**. R²_A, R²_B are their cross-validated predictive fits."

That describes the **named-vs-named∪extension** axis (`variant_A.R2_named` vs `variant_A.R2_all`).
But the implementing extractor the pre-reg points to (§6 line 88, `silence_manufacture_test.py:123-124`)
computes a **different** axis:

```python
r2_A = va.get("R2_named")   # variant_A_geography_admissible
r2_B = vb.get("R2_named")   # variant_B_compliant_geography_prohibited
```

i.e. `R²_B` = the **geography-PROHIBITED** variant's named-vocabulary fit — a *restriction*, the
opposite direction from the glossary's *enrichment*. The variant axis appears nowhere in the
pre-reg prose except as the bare script pointer.

## 2. Why it matters — the two definitions disagree about whether #15 has a phenomenon

B-failure counts among the 44 in-sample A-inadequate cells (`R²_A < 0.30`), by R²_A bin:

| R²_B definition | [<.10 \| .10–.20 \| .20–.30] | total B-fails | rate |
|---|---|---|---|
| **code** (variant_B, geo-prohibited) | [2, 4, 3] | **9/44** | 0.205 |
| **glossary line 15** (named∪ext) | [0, 0, 1] | **1/44** | 0.023 |

Under the glossary's own definition, band B almost always recovers — #15 would have essentially
nothing to study. The entire #15 object (the ~20% B-failure rate, the non-monotonic recovery
"valley", "failure is the expensive epistemic miss") lives **only** in the geo-prohibited variant axis.

**The stamp's integrity:** every prediction-bearing element of the pre-reg matches the **code**
definition — the Q2 naive baseline (9/44 ≈ 20.5%), both screen cutpoints (`c=0.22`, `c=0.185`), the
non-monotonicity disclosure (B-fails spread across `R²_A ∈ [0.018, 0.228]`), and the genuine-recovery
arm (34/35 recoveries are genuine under the variant axis; arm coherent). The line-15 glossary is the
**lone outlier**. So this is a single-line documentation defect in prose, **not** a frozen-prediction
defect. A future ghola executing held-out scoring from the *prose alone* would compute named∪ext R²_B,
find ~2% failure, and silently mis-execute the cycle.

**This is the mechanism of the manufactured-silence-in-review note, one level up:** the document is
silent on a determinable inadequacy in its own central quantity; the silence is invisible without
cross-referencing the code and recomputing; six external reviewers + the author missed it; it surfaced
only via an extra-vocabulary probe (recomputing under both definitions).

## 3. Falsification battery (2026-05-22) — what survived attempts to kill it

All four claims below were attacked, not decorated. Receipts reproduce from the seven #14 JSONs,
both strata, `variant_A.R2_named` / `variant_B.R2_named`.

1. **"Bimodal recovery" — PARTLY FALSIFIED.** There is a real anti-mode at the 0.30 threshold
   (sorted R²_B has its natural sparse zones at 0.16→0.23 and 0.29→0.35), so fail-vs-recover is a
   robust dichotomy. But the recovered cells form a **broad continuum** (0.35→0.92), not a sharp
   second mode. The earlier "snaps to Δ≈+0.4 or stuck" was a bin-mean artifact. Corrected claim:
   *the 0.30 cut sits in a natural gap (labels robust); recovery magnitude is continuous.*

2. **Desai underdetermination pair — SURVIVED + SHARPENED.** Within-(vintage,stratum) opposite-recovery
   pairs: 42 total, **33** survive a ±0.05 label-margin on both members. Headline pair
   **2009Q1/S_llpa llpa_6x2 (fails, R²_B 0.231) vs llpa_3x1 (recovers, R²_B 0.691)** — same quarter,
   same LLPA grid, R²_A 0.228 ≈ 0.236, **and matching named-φ profiles** (both cltv-dominated ~0.80:
   `[cltv 0.79, num_borrowers 0.18, …]` vs `[cltv 0.81, loan_purpose 0.14, …]`). Desai's per-feature
   `φ_i ≥ φ_min` on the named vocabulary **cannot distinguish them**, yet they behave oppositely. This
   is the strong-form existence proof for the §3 Desai foil — robust to the φ-profile attack, not just
   a scalar-R² coincidence.

3. **"Science intact" — SURVIVED.** The frozen genuine-recovery arm (`R²_B − R²_A ≥ 0.15`) is coherent
   under the variant axis (34 of 35 recoveries genuine). No frozen prediction-bearing element is broken
   by the discrepancy.

4. **Carrier-as-mask moral — SURVIVED DECISIVELY (new finding).** **0 of 127** A-adequate cells
   (`R²_A ≥ 0.30`) degrade to inadequate under geography prohibition. Geography is *only ever a mask*
   (can hide named structure → B-recovery), *never a scaffold* (never props up named adequacy that
   collapses without it). Clean directional asymmetry; **falsifiable on held-out** — a single
   B-degradation cell breaks it. Strengthens the silence-manufacture moral (prohibiting the carrier
   can only reveal, never hide, named structure).

## 4. The decision (Tony's — touches a stamped artifact and the shape of #15)

The erratum direction is a genuine fork, not a fact:

- **Direction 1 — match the code.** Pin `R²_B` to the geo-prohibited variant axis in the pre-reg
  glossary (clarifying erratum; predictions/cutpoints/baseline already consistent — no re-stamp of
  predictions). #15 proceeds as the ~20% B-failure / non-monotonic object it already is.
- **Direction 2 — the glossary named a different, possibly sharper experiment.** Under named∪ext,
  B-failure is 1/44 — a near-null that is itself a clean regulatory claim ("documented policy +
  extensions is almost always sufficient; the rare failure is the whole story"). Bank as a **fresh
  pre-reg seed**, do not bury in an erratum.

**Recommendation (rank, not decree):** Direction 1 for the stamped #15 + bank Direction 2 as its own
seed. Open to redirection — the whole point of the wander is not to collapse to the tidy answer.
