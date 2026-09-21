# Record sufficiency for post-hoc attribution recomputation — result note

**Date:** 2026-09-21. **Status:** RESULT (draft, pre-adversarial-review).
**Pre-registration:** `docs/superpowers/specs/2026-09-18-record-sufficiency-preregistration-note.md`, OTS `bd47a9d`. Frozen before any attribution ran.
**Artifacts:** `runs/record_sufficiency/*.json`. **Code:** `scripts/record_sufficiency/`.
**Commits:** `403bb2e` (Arm B), `873b0a9` (Arm G), `c6f89c0` (chance correction + methods).

---

## 1. What was asked

Which fields must a decision-time binding record carry for a later recomputation
of a post-hoc attribution to land within a stated tolerance of the original, and
are there conditions under which no achievable record suffices?

Record levels R0 (outcome only) through R5 (adds seed), nested, crossed against
divergence conditions (i) same process, (ii) fresh process, (iii) library minor
version, (iv) thread/BLAS path. Frozen primary: mean top-5 Jaccard ≥ 0.90 for
≥95% of decisions. Rank-based, not magnitude-based, because Hwang et al.
(arXiv:2601.12654) show magnitude metrics report stability that rank metrics do
not support.

## 2. Verdicts against the frozen predictions

| | Claim | Prior | Outcome |
|---|---|---|---|
| **P1** | R3 NOT sufficient under library drift | 0.70 | **FALSIFIED** |
| **P2** | R5 sufficient under (i)–(iv) | 0.65 | **HELD** |
| **P3** | Stochasticity dominates systems nondeterminism | 0.60 | **HELD, and stronger than stated** |
| **P4** | L2 would declare sufficiency ≥1 level weaker | 0.75 | **HELD** |
| **P5** | R0 not sufficient (negative control) | 0.99 | **HELD, narrowly** |

**P1 falsified.** TreeSHAP reproduces exactly (Jaccard 1.0000, L2 0.0000) at R2
and above across shap 0.48.0 → 0.49.1, fresh processes, and single-threaded
execution. Environment pinning (R4: library versions, OS, hardware class, thread
count) changes nothing in either arm. The prediction that environment would
matter was wrong, and wrong in the direction that makes the policy ask smaller.

**P3 held in a stronger form than registered.** The prediction was that method
stochasticity would *dominate* systems nondeterminism. Systems nondeterminism was
not merely dominated; it was **absent** — every deterministic cell was
bit-identical across all four conditions.

**P5 held narrowly, and the margin is itself a result.** R0 forces a surrogate
refit. Mean Jaccard 0.869 with only 61.5% of decisions reproducing — rejected on
the *fraction* gate, not on collapsed similarity. Two tree ensembles fit on the
same data largely agree about which features dominate. Had the pre-registration
gated on mean Jaccard alone, R0 would have come within 0.03 of "reproducing."

## 3. The result

**Sufficiency is method-indexed. There is no single minimum sufficient record.**

| Method | Sufficient at | Field that closes it |
|---|---|---|
| TreeSHAP | **R2** | model parameters (deterministic thereafter) |
| KernelSHAP | **R3** | `n_samples` — *not* the seed |
| SamplingSHAP | **R5** | seed |
| LIME | **R5** | seed |

KernelSHAP's coalition set is fully determined by the sample count, so pinning
`n_samples` removes the stochasticity without a seed. An institution cannot
write one policy ("record the seed") and be done: what suffices depends on which
explainer ran, which is a property of the method rather than of institutional
diligence.

**Record cost.** R1 = 170 bytes, R5 = 819 bytes per decision. The entire distance
between a useless record and a sufficient one is ≈650 bytes. At 100,000
decisions/year that is ~65 MB — the number the policy argument needs.

**Chance correction.** Raw top-k Jaccard is not comparable across substrates: the
random-null value is a strong function of feature count (0.568 at n=7, 0.278 at
n=12, 0.058 at n=50). Arm B has 12 features, Arm G has 7. Normalized
`(observed − null)/(1 − null)` is the only cross-arm-comparable figure. Sufficient
cells are unaffected; failures move materially (Arm G R1 retention: 0.855 raw →
**0.665** normalized). The valid cross-arm comparison **reverses** the raw
reading: the retention gap is larger on real lending data (0.665) than on
synthetic (0.776).

## 4. Three failure modes the record cannot fix

1. **Retention.** R1 (model id + version, no parameters) resolves to whatever
   currently answers to that name. Normalized 0.665 (Arm G) / 0.776 (Arm B),
   both insufficient. A pointer to a version nobody kept is not a record.
2. **Ambient seed.** `shap.SamplingExplainer.__init__` is
   `(self, model, data, **kwargs)` — it has **no seed parameter**. Passing one is
   silently swallowed; the RNG consumed is the *global* numpy state. An
   institution intending to record "the seed" has nothing method-local to record,
   and an examiner who sets one on recomputation gets no error and no effect.
3. **Toolchain rot.** shap 0.48.0 **and** 0.49.1 both fail on xgboost 3.2.0
   models: `ValueError: could not convert string to float: '[1.98975E-1]'`
   (xgboost serializes `base_score` as a bracketed vector; shap's loader parses a
   scalar). **A record pinning model version, config, method, and method version
   would be fully sufficient on paper and still not recomputable, because no
   available explainer can read the model.** Record sufficiency presupposes a
   working toolchain and the record cannot record that. Not anticipated in
   pre-reg §9. **Currently n=1 — an anecdote until a second instance is found.**

## 5. The limitation that must not be left for a reviewer

Recording a seed makes an explanation **reproducible, not right**. A different
seed yields a different, equally valid explanation; the record locks in an
arbitrary member of the multiplicity set. Hwang et al. are asking whether the
explanation is *determined*; this study asks whether the one that was produced is
*recoverable*. These are different questions and the second does not answer the
first. Structurally identical to this project's own "pick one hides the choice"
result.

## 6. Threats to validity

- **Stochastic methods n=4**, single substrate for KernelSHAP/LIME, single
  condition (i). Conditions (ii)–(iv) not run for those two.
- **No neural / GPU case.** This is where P2's collapse branch is most likely to
  fire and is the single most likely thing to overturn the headline. Tree models
  on CPU may be the easy case.
- **One dataset per arm**, against this project's own N≥3 standard.
- **k=5 of 7 features (Arm G)** puts the null at 0.568, leaving little dynamic
  range. Arm G should be re-run with a wider feature set.
- **The harness was wrong three times in four days** — truncated RBO ceiling
  moving with feature count; the swallowed seed; a watcher testing file count
  rather than JSON validity. Each was caught by a loud failure, not by
  inspection. A study about whether recomputation is trustworthy should report
  that its own recomputation harness required three corrections.

## 7. What would change the verdict

- A neural model with GPU nondeterminism showing R5 insufficient → P2's collapse
  branch, and the paper's conclusion inverts to "artifacts must be stored."
- A second toolchain-rot instance → failure mode 3 becomes a class rather than
  an anecdote.
- A method whose stochasticity is not closed by any recordable field → there is
  no sufficient record for that method, which is the strongest version of the
  negative result.

---

**NEXT STEP (pre-reg §7, mandatory): blind adversarial review before the result
is OTS-stamped as final.** Supply the prior-art context (Hwang et al.) and
withhold the verdict.
