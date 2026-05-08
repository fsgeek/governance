# All-Atypical Effect: Conditional Structure — Findings Note

**Date:** 2026-05-08
**Status:** Findings note from a within-vintage-run analysis using the wedge as built (the three 2026-05-08 jsonl runs across 2014Q3, 2015Q3, 2015Q4). Companion to the vintage-stability and adversarial-robustness memos.
**Scope:** What survives when the marginal "all-atypical defaults less" claim is decomposed by T (mean predicted-grant probability across R(ε) members) and by disagreer identity. Methodology-level claims sharpen as a result.

---

## 1. Headline

The vintage-stability findings note presents the all-atypical defaults-LESS effect as a marginal robust-across-vintages result. **Decomposing by T quintile reveals the effect is not uniform** — it concentrates in T-bin 4 (moderate-to-upper predicted-grant probability) and is absent at low T. The methodology's claim should be conditional on T, not marginal.

Three findings, each tightening the previous:

1. **The k buckets are not a graded consensus signal.** Default-rate-by-k is non-monotonic noise across k=1..4 with a sharp downward break at k=5. Disagreer identity at k=4 tracks feature-subset and hyperparameter idiosyncrasy: the lone abstainer is consistently the model with a distinct feature subset (or extreme hyperparameters). k=1..4 are Boolean encodings of which idiosyncratic model fired; only k=5 is structurally special.

2. **The k=5 defaults-LESS effect is T-conditional.** Pooled across three vintages (n=60,851), within T-quintiles:

   | T bin | range | k=0 rate (n) | k=5 rate (n) | gap |
   |---|---|---|---|---|
   | 1 (low) | [0.632, 0.807] | 21.91% (10,732) | 22.05% (195) | +0.14 pp |
   | 2 | [0.807, 0.846] | 17.86% (11,094) | 14.85% (101) | −3.01 pp |
   | 3 | [0.846, 0.870] | 14.48% (10,769) | 16.00% (150) | +1.52 pp |
   | 4 | [0.870, 0.906] | 11.54% (10,791) | **7.11% (211)** | **−4.43 pp** |
   | 5 (high) | [0.906, 0.979] | 6.77% (10,292) | 5.43% (368) | −1.34 pp |

   Bin-4 Wilson 95% upper bound on k=5 (11.40%) sits below the k=0 point estimate (11.54%). Bin 1 shows no effect. Bin 5 hits a ceiling.

3. **Bin-4 k=5 cases are wealthy, low-leverage borrowers.** 2015Q4 k=5 median annual_inc is $166,500 vs $65,000 for k=0; mean $237K vs $75K; p75 $381K vs $95K. DTI lower by ~5 points (9.34 vs 15.20). FICO marginally higher. Identifiable population: borrowers who came to LC despite having access to traditional bank credit. **Bin-1 k=5 cases also include high-income borrowers** (2015Q4 median $141K) — but with high DTI (mean 36.87 vs 26.80), which the trees correctly weight as risk. The methodology fires only where the trees were under-pricing creditworthiness, not where they were already correct.

## 2. The mechanism, hypothesized

CART `min_samples_leaf` constraints (200-400 across R(ε)) cap leaf granularity exactly at sparse feature-space corners. The high-income + low-DTI corner of LC's distribution is sparse — most LC borrowers are mid-income — so the trees can't populate granular leaves there. T saturates near the leaf-averaged repayment rate, which mixes wealthy borrowers with less-strong neighbors. The atypicality consensus identifies this under-prediction because each model in R(ε) computes density per its own leaves, and sparsely-populated regions yield "atypical" regardless of the model's specific feature subset or depth.

This is testable. Rerun with a richer model class (gradient boosting, depth-unconstrained CART). If the bin-4 k=5 effect attenuates, the mechanism is model-capacity. If it persists, the methodology has a wider claim than this note grants.

## 3. The disagreer-identity finding

For each vintage, the lone-abstainer (model that says "ordinary" when 4 of 5 say "atypical") concentrates on 1-2 specific models, and the dominant abstainer maps to the model with a distinct feature subset or extreme hyperparameters:

| Vintage | Dominant lone-abstainer(s) | Distinguishing property |
|---|---|---|
| 2014Q3 | tree_3 (42%) + tree_4 (48%) = 89% | tree_3 deepest (12) with largest leaves (400); tree_4 has smallest leaves (25) |
| 2015Q3 | tree_2 (83%) | only model in R(ε) without `annual_inc` |
| 2015Q4 | tree_1 (42%) + tree_5 (53%) = 95% | only models in R(ε) without `emp_length` |

What this preserves: **k=5's structural specialness is genuine.** Unanimity requires agreement across heterogeneous feature subsets and hyperparameter regimes that would not naturally agree, which is the property the methodology rests on.

What this changes: **the gradient interpretation is wrong.** Position-paper or spec language that says "the more R(ε) members agree, the stronger the signal" is not supported by the data. Language that says "all R(ε) members, despite their dispersion, agree" is. The k=1..4 buckets carry information about *which* idiosyncratic model fired, not *how strong* a graded consensus is.

## 4. The sharpened methodology claim

Replacing "consensus on atypicality detects unusual-but-strong borrowers":

> **Consensus on atypicality across R(ε) members identifies cases the trained model class systematically mis-prices in the direction of capacity limits relative to the tail of the population distribution.** The signal is informative conditional on T: it refines T-based predictions in the moderate-to-upper T range where the model class under-predicts creditworthiness; it is silent at low T where the model class is already correct.

This is bounded, falsifiable, and connects to position paper §4's silence-manufacture frame: simpler model classes manufacture silence on tail populations by averaging them into bulk-population leaves; atypicality consensus un-manufactures that silence. The methodology becomes a structural recovery of the silenced part of the model's own implicit reasoning rather than an outsider critique. (The frame is interpretation; the data shows the conditional structure.)

## 5. Implications

**For the methodology spec.** Species output should distinguish (k, T-region) signal pairs from raw k counts. The unconditional "all-atypical" claim should be rewritten as conditional. Add the disagreer-identity caveat — k=1..4 are not graded consensus — to species documentation.

**For the position paper.** The vintage-stability findings note's section 5 paper-language ("robust at the tail, 2-7 pp gap") is true marginally but masks the conditional structure. The conditional version is sharper and more defensible: bounded claims survive examination per the adversarial-robustness memo's argument.

**For the next ghola.** Three concrete next moves, in priority order:
1. Rerun with a richer model class to test the model-capacity-limit mechanism. If the bin-4 k=5 effect attenuates, the methodology is correcting for known model-class deficiencies; if it persists, the methodology has a wider claim.
2. Verify the local_density species computes atypicality from per-tree leaves rather than from a shared density substrate. If shared, the unanimity-across-heterogeneous-models claim weakens and the structural read needs revision.
3. Pull twenty bin-4 k=5 cases by hand and read them. The "wealthy borrower who came to LC despite having other options" narrative needs verification beyond aggregate statistics.

## 6. Explicit non-commitments

- **Single dataset.** N≥3 rule applies *across datasets*. HMDA remains the planned second.
- **Mechanism is hypothesized, not measured.** "CART capacity limits at sparse corners" is consistent with the bin-1/bin-4 asymmetry but not directly verified. The richer-model-class test would falsify or confirm.
- **The silence-manufacture connection is interpretation.** The data shows the conditional structure; the structural-recovery framing is a reading that the position paper may or may not adopt.
- **Twenty-by-hand verification not done.** The "kind of person" claim rests on aggregate statistics; narrative coherence has not been checked against actual case files.
- **Per-vintage statistical strength is mixed.** 2014Q3 bin-4 reaches significance (k=5 [1.89%, 9.86%] does not overlap k=0 11.43%, n=114). 2015Q4 bin-4 is suggestive but its CI overlaps k=0 (n=104). 2015Q3 bin-4 has only n=11 k=5 cases. The pooled effect is the load-bearing one.
- **The disagreer-identity → feature-outlier mapping** is clean for 2015Q3 and 2015Q4 (single feature distinguishes the abstainer from the rest of R(ε)). It is fuzzier for 2014Q3, where hyperparameter idiosyncrasy carries the disagreement. The general claim "lone-abstainer is the most-distinct-by-some-axis model" holds; the cleaner "lone-abstainer is the feature-subset outlier" claim does not generalize across all three vintages.

## 7. Connection to other working documents

- **2026-05-08 vintage-stability findings note.** This note refines that note's all-atypical-tail-effect claim from marginal to conditional. The two should be read together; if forced to keep only one finding, the conditional version is the more defensible.
- **2026-05-08 adversarial-robustness memo.** The bounded "capacity-limit-correction" framing strengthens the methodology's adversarial-robustness profile: a small, specific, falsifiable claim survives publication better than a broad one.
- **2026-05-08 indeterminacy operationalization memo.** The species-stability axis (vintage-sensitive vs vintage-stable) gains a conditional sister: even within vintage-stable findings, conditioning on T is required to interpret what the species detects.
- **Position paper §4 (silence-manufacture).** Atypicality-consensus as un-manufacturing of model-class silence on tail populations is a candidate frame for §4. Interpretation, not data.

## 8. Reproducibility

Four scripts in `scripts/`, run against the three 2026-05-08 jsonl runs in `runs/`:

- `all_atypical_gradient.py` — k-bucketed default rates with Wilson intervals, per vintage. Establishes finding (1).
- `all_atypical_t_stratified.py` — T-quintile stratification of k=5 vs k=0 default rates, per vintage and pooled. Establishes finding (2).
- `bin4_k5_features.py` — feature distributions at bins 1 and 4, k=5 vs k=0, per vintage. Establishes finding (3) and the bin-1/bin-4 asymmetry.
- `disagreer_identity.py` — lone-flagger (k=1) and lone-abstainer (k=4) model identity, per vintage. Establishes the k=1..4-as-Boolean-encoding interpretation.

All four print to stdout. None mutate state outside `scripts/`.
