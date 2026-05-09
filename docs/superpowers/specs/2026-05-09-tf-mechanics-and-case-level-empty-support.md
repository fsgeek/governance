# Two Followups: T+F Mechanical Identity and Case-Level Empty Support

**Date:** 2026-05-09 (later same day).
**Status:** Successor note to two previously-committed-and-stamped findings notes (`2026-05-09-i-stability-falsification-findings-note.md` and `2026-05-09-tf-asymmetry-exploration-note.md`). Both predecessors had explicit caveats this note resolves. Resolution direction: one caveat sharpens a finding, the other corrects an artifact-shaped framing.

---

## 1. Why this exists

The I-stability findings note §5 framed T as stable and "F and I as comparably unstable" — flagging in §6 that the F-instability could be a mechanical complement-of-T artifact and recommending a check before §5's framing could be promoted. The check: does T + F = 1 per (case, member) row?

The asymmetry note §6 reported the empty-support inversion at the (case, R(ε)-member) pair level — fraction of pairs where `factor_support_T` (or `_F`) is empty. A case has 5 R(ε) members in this configuration; a finding that holds at the pair level may or may not hold at the case level. The question: does the inversion replicate when restricted to whole-case agreement (all 5 members empty on a side)?

Both checks were 30-second computations against existing committed jsonl files. The answers shift the framing of the findings, so they get their own note rather than living in conversation residue.

## 2. Finding A: F = 1 − T exactly

**Computation.** For every (case, R(ε)-member) row in V₁ (`runs/2026-05-08T17-43-21Z.jsonl`, n=61,895), compute |T + F − 1|.

**Result.** Mean = 0.0. Max = 0.0. Not "small floating-point noise" small — exactly zero. Across all rows.

**Implication.** F is mechanically the complement of T per the wedge's current definition. The "F mean CV ≈ 0.13–0.20" finding from the I-stability note §3 is therefore not an independent measure of R(ε)-member disagreement on F. It is a deterministic transform of T-CV through the asymmetric-relative-variation effect: small absolute T variation produces proportionally larger relative variation in (1 − T) when T is far from 0.5 (i.e., when the case is confidently classified). The population's T-distribution is heavily skewed toward 1 in this LC data (most cases are non-default), so T-mean is high and F-mean is low; same absolute spread produces higher CV on F by construction.

**Correction to I-stability findings §5.** The framing "T is the outlier, F and I are comparably unstable" overstates F's role. The corrected framing is:

> T is stable across R(ε) members. I (local_density) is 6-9× more variable than T. F = 1 − T mechanically and carries no independent information about member agreement; its higher CV is an artifact of relative-variation asymmetry on a skewed population.

The mechanistic question raised in §5 — "why is T so much more stable than F or I?" — reduces to "why is T so much more stable than I?" That's a tighter question with a cleaner mechanism candidate (ε-optimality directly constrains T-agreement on training population; nothing comparable constrains local-density estimates).

**The reframed methodological reading.** The I-stability pre-registration was binary (I more or less stable than T/F). Falsification reads, on its surface, as a defeat for the four-species design. But once F is set aside as mechanical, the remaining structure is sharper than either pole of the original prediction:

> The wedge's per-model output carries two independent quantities per (case, member): **T** (the verdict) and **I** (the indeterminacy / local-density score). T is heavily stable across R(ε) members because ε-optimality on training loss directly constrains it. I is 6-9× more variable because nothing in the ε-optimality constraint pins down local-density estimates. The instability of I is not noise — **it is exactly the within-Rashomon-disagreement signal the methodology is supposed to surface**, on a quantity that varies independently of the verdicts the members agree about.

That is, the design rationale that I carries information T does not is *more* clearly vindicated by the falsification than it would have been by a hit. A hit would have meant "I is also stable" — a redundant signal. The miss means "I varies on a substrate that constrains T" — an independent signal. The methodology has two channels per member, with structurally different stability properties under the same ε-optimality constraint.

(This reframing came from Tony in conversation, not from this instance: "F has no value independent of T, so I is doing real work." Recorded here verbatim because the framing is load-bearing for how the I-stability finding should be presented in subsequent papers.)

**No retroactive edit to the I-stability note.** The note is OTS-stamped at its original hash; editing would break time-anchoring. This note serves as the corrective successor and the I-stability note's §5 should be read with §6's caveat in mind, then with this resolution in mind.

## 3. Finding B: Case-level empty support sharpens the inversion

**Computation.** For each vintage, compute four quantities per case:
- `all-T-empty`: every R(ε) member has empty `factor_support_T`.
- `all-F-empty`: every R(ε) member has empty `factor_support_F`.
- `any-T-empty`: at least one member has empty `factor_support_T`.
- `any-F-empty`: at least one member.

Pair-level fractions from the asymmetry note §6 are equivalent to "expected empties per member × 1/n_members" averaged across cases — a different statistic.

**Results.**

| Vintage | n cases | all-T-empty | any-T-empty | all-F-empty | any-F-empty |
|---|---|---|---|---|---|
| V₁ (2014Q3) | 12,379 | 0.11% (14) | 1.60% | **3.09% (383)** | 15.74% |
| V₂_alt (2015Q3) | 22,271 | 0.00% (0) | 5.78% | 0.00% (0) | 5.40% |
| V₂ (2015Q4) | 26,801 | **0.65% (175)** | 9.00% | 0.60% (162) | 3.78% |

**Reading the table.**

- **V₁ → V₂ all-F-empty: 3.09% → 0.60%** (5.1× collapse). 383 of V₁'s 12,379 cases had no R(ε) member able to articulate *any* deny-supporting reasoning. By V₂, only 162 of 26,801 cases share that property. The post-2015 regime articulates deny-supporting reasoning for nearly every case.
- **V₁ → V₂ all-T-empty: 0.11% → 0.65%** (6× growth). 175 of V₂'s 26,801 cases have no R(ε) member able to articulate *any* grant-supporting reasoning. The model class collectively cannot say *why* these cases should be granted, even when they are.
- **V₂_alt (transition) is striking: zero whole-case empty agreement on either side.** Every R(ε) member finds *something* to attribute on every case — but as the asymmetry note shows, they don't agree on what. Mid-transition, the substrate forces every member to articulate, just incoherently across members. The post-transition vintage (V₂) re-introduces whole-case attribution failures, but asymmetrically — concentrated on the T side.

**Implication for the empty-support mechanism story.** The case-level result strengthens the procedural-mechanism reading from the asymmetry note §6 and this morning's conversation. At the pair level, "T-empty rate triples" could be rationalized as "individual members occasionally fail to find grant reasons." At the case level, **175 cases in V₂ have unanimous failure to articulate any grant support across all 5 R(ε) members**. That is not individual-member idiosyncrasy. The model class as a whole, under ε-optimality on the V₂ data, contains no member that can articulate why these cases should be granted. That is the clean version of "grant becomes the negative space."

**Implication for the empty-support replication pre-registration.** The pre-registration P1 was set in pair-level units (T-empty ≥ 2.2% and F-empty ≤ 4.1% in LC 2016Q4). The case-level analog is a sharper test of the same mechanism. When the empty-support pre-registration runs against LC 2016Q4 and HMDA RI 2022, the findings note should report *both* pair-level and case-level statistics. The case-level results don't *retroactively* tighten the pre-registered hit criteria (those are what they are), but they constitute additional evidence for or against the mechanism. A case-level inversion that holds in V_fresh would substantially strengthen a P1 hit; a pair-level hit without case-level support would reveal P1 as picking up a weaker effect than the mechanism predicts.

**Implication for the SHAP/LIME comparison.** Whole-case attribution failure is even harder for SHAP/LIME to surface than pair-level rate shifts. SHAP attributions are real-valued per feature; "all attributions are zero on the grant-supporting half" is not a category SHAP natively reports. Discovering that 175 cases in V₂ have whole-class grant-attribution failure requires either (a) the policy-constrained Rashomon construction with explicit T/F leaves, or (b) an *ad hoc* threshold on absolute SHAP values plus a "no feature exceeds threshold" rule with an arbitrary cutoff. The former is native; the latter is a structural workaround. Null B (the structural-finding null from this morning's conversation) gains specificity: it isn't just "regime shift in fraction-with-no-articulable-grant-reason" but "175-out-of-26801 specific cases where the *entire* policy-constrained model class fails to articulate grant support."

## 4. What does NOT change

- The I-stability falsification (the central finding of the predecessor note) is unaffected. T is stable; I is 6-9× more variable than T. F's mechanical-complement status doesn't soften this.
- The asymmetry note's §3 appearance × intensity decomposition stands. The decomposition was per-feature, not on T+F sums; F's mechanical relationship to T is orthogonal.
- The empty-support replication pre-registration's hit criteria are not modified. Pair-level units in §5 of that document remain the binding criteria. This note adds case-level reporting as an additional standard for the eventual findings note, not as a pre-registration amendment.
- The pre-registration uniformity-failure pattern (N=3) is unaffected. The I-stability falsification still counts; the F-mechanical correction is about §5's framing of T-vs-F-vs-I, not about whether I is more stable than T.

## 5. Provenance and protocol note

These two checks were prompted by an open question in this morning's conversation about what's "pulling" — both items existed as flagged caveats in already-committed notes, and following the caveats was lower-cost than letting them compound. The 30-second computation budget for both is small enough that "check the caveat now" is essentially always the right call when the caveat is data-resolvable.

The pattern: when a committed findings note carries an explicit "this could be artifactual, needs further check" caveat, the cost of resolving the caveat in a successor note is low and the cost of leaving it unresolved is path-dependent (future-instances see the §6 caveat without knowing whether it was ever addressed). The successor-note pattern preserves the OTS time-anchoring of the original while letting the research record evolve.

## 6. Connection to other working documents

- **`2026-05-09-i-stability-falsification-findings-note.md` §5 and §6.** This note resolves §6's F-mechanical caveat and corrects §5's framing.
- **`2026-05-09-tf-asymmetry-exploration-note.md` §6.** This note sharpens the empty-support inversion finding from pair level to case level.
- **`2026-05-09-empty-support-replication-pre-registration.md`.** Case-level reporting standard added for the eventual findings note; pre-registered hit criteria unchanged.
- **Conversation residue (this session, 2026-05-09 afternoon).** The "what's pulling at me" frame is the trigger; the §6 caveats are the targets.
