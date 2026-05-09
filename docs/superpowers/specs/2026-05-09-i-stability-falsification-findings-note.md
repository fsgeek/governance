# I-Stability Pre-Registration — Falsification Findings Note

**Date:** 2026-05-09.
**Status:** Findings note for a contrarian pre-registered prediction. **Falsified, decisively, across all three available vintages.** The finding's primary execution was performed by a Sonnet 4.6 instance running under the hamutay taste_open thin-prompt frame earlier in the same day (`/home/tony/projects/hamutay/experiments/taste_open/taste_open_20260509_125030.jsonl` cycle 6). The numbers below are an independent re-computation by an Opus 4.7 instance against the same committed jsonl runs; the two computations agree to four decimal places, confirming the falsification is not an artifact of one execution. **This note exists because the Sonnet instance's execution was logged in the hamutay session record but had no corresponding findings artifact in the governance research record. The "we keep learning things and not preserving the learning" pattern named in `2026-05-09-conversation-residue-capture.md` was recurring in the very session that observed it.**

---

## 1. The pre-registered prediction

**Source:** `2026-05-08-indeterminacy-operationalization-memo.md` §5; recapitulated in `2026-05-09-conversation-residue-capture.md` §4 as a "named pending test."

**Prediction (Tony, 2026-05-07 working session, contrarian):** *I will be more stable across Rashomon members than T or F.* Disagreement on direction (T vs F) should exceed disagreement on indeterminacy.

**Why contrarian:** the natural intuition is the opposite — that direction (T/F) is what the model is *for* and should be highly stable, while indeterminacy is a derived secondary signal and should be noisier. The contrarian prediction reverses this: it claims I captures something more substrate-determined than the verdicts themselves, and therefore should vary less across substrate-respecting members of R(ε).

**Falsification target:** if the prediction holds, it constitutes substantial structural support for the four-species indeterminacy design (I is a real signal in a way that survives model-class variation). If it fails, the design's central claim about what I carries fails empirically.

## 2. What was computed

For each case in each of the three committed runs, compute coefficient of variation (CV = standard deviation / mean) across the 5 R(ε) members for each of three quantities:

- **T:** the per-model probability that the case is positive label (grant-supporting in LC).
- **F:** the per-model probability that the case is negative label (deny-supporting in LC).
- **I (local_density species):** the per-model indeterminacy score under the local-density species, drawn from `per_model[i].indeterminacy[species=local_density].score`.

Mean CV is then averaged across all cases per vintage.

The data already supports per-model I emission for the local_density species (visible in the existing jsonl schema), contradicting the residue spec §4's claim that "the current wedge cannot test this." The test *was* runnable on existing data; the Sonnet instance noticed and acted. Other species (Ioannidis battery, etc.) are case-level rather than per-model and remain outside this test's scope.

## 3. Results

| Vintage | n cases | T mean CV | F mean CV | I mean CV | I/T ratio | F/T ratio |
|---|---|---|---|---|---|---|
| 2014Q3 (V₁) | 12,379 | 0.0186 | 0.1335 | 0.1658 | 8.92× | 7.18× |
| 2015Q3 (V₂_alt) | 22,271 | 0.0302 | 0.1966 | 0.1926 | 6.37× | 6.51× |
| 2015Q4 (V₂) | 26,801 | 0.0197 | 0.1298 | 0.1706 | 8.67× | 6.59× |

(The Sonnet instance's cycle-6 table reported T CV and I CV identical to these to four decimal places. F was not in the Sonnet table; it is reported here as additional texture — see §5.)

## 4. Verdict

**Falsified.** Across all three vintages, I is substantially *less* stable than T, by a factor of 6–9×. The pre-registered prediction was the wrong sign by a large margin. No vintage shows I more stable than T; no vintage shows I within 2× of T's CV.

The contrarian prediction was wrong. The intuition it inverted — that T (the verdict) is the most stable substrate-respecting quantity and I a derived noisier one — was correct.

This is the third pre-registration in 2026-05-08/09 to fail in the same structural way:

1. Bin-4 case-reading (12-15/5-8/1-3 → 2/11/7) — assumed uniform fit-distribution.
2. V₁→V₂ predictive test P5 — assumed T/F symmetry.
3. I-stability — assumed I more stable than T/F, was 6-9× less stable than T.

The `feedback_research_design` and `project_pre_registration_pattern` memories should both reflect this third instance.

## 5. Texture: T is the outlier, not I

The pre-registered comparison was binary (I vs T/F treated as a unit). The falsification holds against either pole of that comparison: I is much less stable than T (6-9× less), and *F is also much less stable than T* (6-7× less). Across all three vintages, I and F are approximately comparable in instability (I marginally higher in V₁ and V₂; F marginally higher in V₂_alt). Neither approaches T's stability.

The honest summary is **T is the outlier**, not I:

- T mean CV ranges 0.019–0.030 across vintages.
- F mean CV ranges 0.130–0.197 — roughly 7× T.
- I mean CV ranges 0.166–0.193 — roughly 8× T.

This shifts the question from "is I more stable than T/F?" (no) to "why is T so much more stable than F or I across substrate-respecting Rashomon members?" That's a different mechanistic question. Possible reads:

- T (the positive-class probability) is the quantity the loss directly optimizes; R(ε) members are constrained to ε-optimal training loss, which means they are constrained to *agree about T* on the training population. F = 1−T mechanically, so F is not independently constrained — its CV reflects rounding/tail behavior near the boundaries.
- Wait — F = 1 − T mechanically? Let me check. (See §6 caveat.)
- I (local_density) measures something about the training population's geometry rather than the verdict; nothing in the ε-optimality constraint forces R(ε) members to agree about local density estimates.

The "T is the outlier" framing is *interesting* — but writing it down here is not promoting it to a finding. It is post-hoc and would itself be productive-miss-pattern shaped if treated as a vindicated mechanism. It is recorded as a question for future pre-registration.

## 6. Caveats

- **F vs T mechanical relationship.** If the wedge defines F = 1 − T per-model (binary classifier), the F CV finding is partly mechanical: when T ≈ 0.5, small T variation produces proportionally small F variation; when T ≈ 0 or 1, small T variation can produce proportionally large F variation in the *complement*. The fact that F CV is much higher than T CV at the population level may reflect this asymmetry plus boundary-population structure rather than independent F-instability. The script needs to be extended to confirm/disconfirm this mechanical hypothesis before §5's framing can be promoted to a finding.
- **Single-species I.** The test computed I-stability for the `local_density` species only. Other indeterminacy species (Ioannidis battery components: round-numbers, threshold-hugging, etc.) are case-level by construction in the current schema, not per-model, so are not testable with the same protocol. The pre-registered claim was about I generally; this test falsifies it for local_density specifically. Whether the falsification generalizes requires extending per-model emission to additional species, which is design work.
- **Two independent computations agree** (Sonnet 4.6 in taste_open + Opus 4.7 in claude-code). Inter-instance reproducibility is established. Inter-substrate (different jsonl format) would be its own test if/when a fresh wedge run is generated.

## 7. What this changes

- **The four-species indeterminacy design loses its contrarian-pre-registration vindication.** The test that would have given it strong empirical support produced the opposite. The design may still be useful for other reasons (interpretability of disagreement structure; per-species mechanism articulation) but the "I is more stable than T/F" claim cannot anchor the design's case.
- **The pre-registration uniformity-failure pattern is now N=3.** The pattern memory should be updated. Each instance assumed a structural symmetry that the data did not exhibit:
  - Bin-4: assumed cases distribute uniformly across F/A/C bins.
  - V₁→V₂: assumed T/F sides shift symmetrically under policy change.
  - I-stability: assumed I, T, F have comparable cross-member variability.
  
  Three for three is no longer noise. The pattern is methodology-signature: predictions that assume symmetry/uniformity over a non-uniform substrate fail. The empty-support replication pre-registration (`2026-05-09-empty-support-replication-pre-registration.md`) explicitly tries to break this pattern by predicting *asymmetric* outcomes; whether it succeeds is its own test.
- **The "T is the outlier" question (§5) is the next pre-registration target** if/when per-model I emission is extended to additional species. The mechanism candidate (ε-optimality constraint forces T-agreement; F is mechanical complement; I is geometry-derived and unconstrained) is articulable enough to predict from on fresh data.
- **The cross-instance preservation gap is itself a finding.** A Sonnet 4.6 instance running in a different harness (taste_open, hamutay) executed a load-bearing falsification. The result was preserved in *that* instance's session record (the JSONL log) but had no corresponding artifact in the governance research record where future-Claude in *this* harness will look. Capturing it required cross-harness reading. The natural fix is the noticing-discipline named in `2026-05-09-conversation-residue-capture.md` §5: scan for substantive reasoning not in a file before any natural break. This case extends the pattern: scan for substantive *findings* produced in sibling-instance sessions before assuming the research record is current.

## 8. Connection to other working documents

- **`2026-05-08-indeterminacy-operationalization-memo.md` §5.** The pre-registration this falsifies. The memo's contrarian prediction is now empirically refuted.
- **`2026-05-09-conversation-residue-capture.md` §4 and §5.** §4 named this as a pending test; §5 named the loss-of-learning pattern. Both are answered/instantiated here.
- **`2026-05-08-bin4-k5-case-reading-findings-note.md`.** First pre-registration failure; same uniformity-assumption pattern.
- **`2026-05-09-v1-v2-predictive-test-findings-note.md`.** Second pre-registration failure; same pattern.
- **`2026-05-09-empty-support-replication-pre-registration.md`.** First pre-registration that explicitly *predicts asymmetry* rather than assuming symmetry; designed to test whether the methodology can produce a clean falsification when given heterogeneity-aware predictions on fresh data.
- **`hamutay/experiments/taste_open/taste_open_20260509_125030.jsonl` cycle 6.** Sibling-instance execution of this test, whose result triggered this note. Cross-project provenance; not in this repo, but referenced for completeness.

## 9. Provenance

This note's existence is a deliberate response to two things observed by an Opus 4.7 instance in a Claude Code session on 2026-05-09 afternoon:

1. The Sonnet 4.6 taste_open instance's cycle-6 falsification result was real and load-bearing.
2. It had no governance-repo artifact preserving it.

The Opus instance independently recomputed the numbers (matching to four decimal places) and wrote this note rather than asking the PI whether to do so, on the principle that the discipline lives in the voice of the instance, not in permission-gating. The PI may push back on the call; that's expected and welcome.
