# Manufactured silence in the review process — a reflexive audit (2026-05-22)

**Status:** working note (not a pre-reg; not a stamped result). **Speech-act class:** constative (a measured observation) + a falsifiable claim. **Connects:** [[project_cookbook_adversarial_manual]] (Position 2), [[reference_ai_honesty_paper]], [[project_silence_manufacture_result]] (the #14 recursive-surface-salience note), the #15 pre-reg (`docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md`), [[project_premature_collapse_frame]].

This note applies #14's own finding to the act of reviewing #15. It has two parts: (1) a concrete, falsifiable object found in the data — the **non-monotonic recovery valley** — and (2) the audit it makes possible: six expert reviewers were structurally silent on the defect that nearly halved #15's statistical power, and the silence broke not from review but from a "dumb question." The two are the same artifact: the object is the worked example *of* the silence.

---

## 1. The object: the non-monotonic recovery valley

Among the 44 #14 A-inadequate cells (`R²_A < 0.30`), B-failure (`R²_B < 0.30`) does **not** increase with how inadequate A is. It concentrates in a narrow **middle** band:

| `R²_A` bin | n | B-fail rate |
|---|---|---|
| deep-inadequate [0.00, 0.10) | 14 | **0.14** |
| mid [0.10, 0.20) | 10 | **0.40** |
| near-adequate [0.20, 0.30) | 20 | **0.15** |

- Spearman(`R²_A`, B-fail) = **−0.07** — no monotone relationship.
- mean `R²_A` | B-fail = **0.158**; mean `R²_A` | B-recover = **0.162** — the linear axis carries essentially **zero** signal. A model that ranks on `R²_A` magnitude sees nothing.
- The fine bin [0.15, 0.20) is the spike: 4 B-fails of 6.

**Mechanism hypothesis (falsifiable):** the relationship is an inverted-U.
- *Deep-inadequate* A (`R²_A` near 0): A is missing an obvious strong feature; band B grabs it and recovers (B-fail rare).
- *Near-adequate* A (`R²_A` ≈ 0.25): A almost works; B closes the small gap and recovers.
- *Mid* A: genuinely-hard cells where neither the named vocabulary nor the extension features suffice — B cannot recover. The recovery valley sits in the middle.

**Honest caveat:** n = 44, and the spike rests on 6 cells. This is a hypothesis, not a result. But it is exactly the kind of structure the stamped #15 held-out run will incidentally test — #15 records per-cell `R²_A` and `B_fails` across 42 vintages, so the prediction "held-out B-fails concentrate in `R²_A ∈ [0.10, 0.20)`, not at low `R²_A`" is checkable post-hoc (recorded here, pre-run, so it is at least disclosed-in-advance even though it is not part of #15's frozen predictions).

This object is *why* the #15 univariate screen is weak and non-monotonic (pre-reg §3.1): the screen had to be built on the one axis that carries no signal, because it is the only A-side quantity available before fitting B.

---

## 2. The audit: what six reviewers surfaced, and what they silenced

The #15 draft went to six instances (gemini, grok, deepseek, kimi, claude, chatgpt). Cataloguing their concerns by **whether the defect was visible on the page**:

**Surfaced (high salience — swarmed by multiple reviewers):**
- The impossible state-(i) coverage criterion (kimi, chatgpt both led with it). — a *textual contradiction* (naive = 100% coverage, "≥10pp more than naive" is arithmetically impossible).
- The unfrozen screen functional form (deepseek, chatgpt, kimi). — a *missing freeze*, a standard pre-reg checklist item.
- LORO retraining ambiguity; state-(iii) lower bound unfrozen; "half-width" misused for a one-sided bound. — all *on-page* logical/statistical defects.

These are real, and fixing them improved the pre-reg. But note their common property: **every one is detectable by reading the document against a checklist.** Surface-salient.

**Silenced (low salience — caught by none of the six):**
1. **The both-strata yield deflation.** Three of the #14 seven (2008Q1/2016Q1/2018Q1) were run `S_rate`-only, and the A-inadequate yield lives in the `S_llpa` stratum (35% A-inadequate vs `S_rate`'s 11%). Not freezing "both strata run for every held-out vintage" would have silently **halved** #15's realized cell yield — directly degrading every bound in the document. **No reviewer flagged it.** It is invisible on the page: detecting it requires cross-referencing the per-vintage *run configuration* against the cell-generation *grid* — both external to the pre-reg text.
2. **The non-monotonicity (§1).** No reviewer asked whether `R²_A` is even the right axis for the screen; all six accepted "freeze a screen" as the fix and debated its *form*, not its *predictor*. The defect — the chosen axis carries zero linear signal — is invisible without computing against the data.

**What broke the silence:** not a reviewer. Tony's question — *"do we have enough data to reach the floor, or is this a limitation built into what we've done previously?"* — forced a cross-reference to the run configs and the grid, which surfaced (1), and the threshold computation it prompted surfaced (2).

---

## 3. The mechanism is the same one, four levels up

#14's result note already named three levels of the same manufactured-silence mechanism: methodology silences findings by undeclared scope-omission; bank policy silences distinctions by feature-omission; a blind reviewer silenced #14's load-bearing conjunct by surface-salience. **This is the fourth level: the review of a pre-reg about manufactured silence manufactured its own silence by the same mechanism.**

The general form: **an artifact is silent on a determinable inadequacy, and the silence is invisible until something *outside the artifact's vocabulary* reveals it.**
- Bank policy ↔ the band-B fit (the richer model that proves the policy was inadequate).
- SHAP attribution ↔ an equi-accuracy model that attributes differently.
- The pre-reg text ↔ the run config + the data geometry.
- Surface-salience review ↔ the dumb question.

Surface-salient review is a *coverage* instrument — it checks the document against a checklist of visible defects — and coverage is exactly the thing #15 §8 argues is the wrong target. It is structurally blind to any inadequacy that requires an extra-vocabulary probe. Six expert reviewers reading carefully will reliably catch on-page contradictions and reliably miss off-page deflations, because the off-page defect is *not in the vocabulary they are reading*.

**The receipt is the extra-vocabulary probe**, not the review pass — the transport boundary (not the coverage count), the held-out data (not the in-sample fit), the dumb question (not the careful read). This is [[reference_ai_honesty_paper]]'s impossibility-of-text-only-observation restated at the level of process: a reviewer confined to the artifact's own vocabulary cannot, in general, see what the vocabulary omits.

**Cookbook implication (Position 2):** an adversary manufacturing silence does not need to defeat review — review defends the on-page vocabulary and is blind by construction to the off-page omission. The defense is not "more/better reviewers"; it is **mandating the extra-vocabulary probe** (the held-out receipt, the both-axes run, the question that crosses the artifact boundary). A review process that only reads the document is a silence-amplifier dressed as a safeguard.

**Falsifiable claim:** the assertion "none of the six reviewers caught the both-strata deflation or the non-monotonicity, while ≥2 caught each on-page contradiction" is checkable against the six review transcripts (in hand). If a reviewer did surface the both-strata or axis-choice defect, this note is wrong and the surface/off-surface partition collapses.
