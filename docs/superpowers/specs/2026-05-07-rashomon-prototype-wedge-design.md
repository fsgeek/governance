# Rashomon Prototype — Wedge Design

**Date:** 2026-05-07
**Status:** Working design, pre-implementation. Subject to revision when contact with data forces revision.
**Scope:** The smallest concrete starting wedge for a Rashomon-routed governance prototype. *Not* a full end-to-end loop (the methodology's strands (A)–(D) all need to survive contact with data before (E) can be specified honestly).

---

## 1. Purpose and what this is not

This wedge tests one empirical claim at the smallest cost: **across a Rashomon set R(ε) of equally-good models, cases with high outcome agreement may have substantially disagreeing factor support.** That is, the models concur on the decision but draw on disjoint evidence to reach it. If the claim holds, the methodology has its first concrete empirical anchor and the structural argument from §4 of `position-section4.md` (silence-manufacture as substitution under suppression) gains a *paper-internal* instance: outcome agreement among model classes is itself a substitute artifact occupying the rhetorical position where reasoning multiplicity should sit.

What this wedge is *not*:

- Not a full (E) loop. (B) reasoning-trace capture, (C) observability surface, (D) adversarial-pair stipulation HITL UX are deferred.
- Not a full (T, I, F) neutrosophic emission. The I component is deferred — Tony's prediction (corrected from earlier) is that I is the most stable dimension across R(ε), so it is the *least informative* dimension to measure first.
- Not a generality claim. Generality requires N≥3 datasets per the project's research-design rule; this wedge is N=1 (LendingClub). HMDA is the planned second dataset; further datasets to follow.
- Not a solution to reject inference. The wedge acknowledges the unobservable counterfactual rather than pretending to close it.

## 2. Primary hypothesis under test

**H_primary.** Among outcome-agreers in R(ε) — cases where all models in the set predict the same direction with closely-spaced T values — the *factor support* of f_T (and separately f_F) varies non-trivially across models.

*Falsification:* if pairwise factor-support overlap among outcome-agreers is consistently high (median Jaccard > 0.7 across model pairs on top-k features), the methodology's structural distinction between outcome agreement and reasoning agreement collapses.

*Confirmation:* a substantial subset of outcome-agreers exhibits low pairwise factor-support overlap (Jaccard < 0.3), AND hand-inspection of these cases reveals genuinely different reasoning paths (not just different feature labels for the same underlying signal).

## 3. Secondary hypothesis (predictive extension)

**H_predictive.** When LendingClub's underwriting policy changes between vintages V₁ and V₂, the factor-support distributions in R(ε) shift in directions *predictable from the documented policy delta*.

*Mechanism:* a policy change (e.g., FICO floor raised) reshapes the surviving population's feature distribution. Factor support that depended on the dropped tail loses discrimination power; factor support of residual features rises to compensate. The methodology *predicts the direction of shift* before R(ε) is fit on V₂.

*Falsification:* pre-register predictions for f_T / f_F factor-support shifts based on the documented V₁ → V₂ policy delta; fit R(ε) on V₂; check predicted versus measured shifts. If predictions are at chance, the methodology's predictive claim falls.

This converts vintage drift from a *confound* (forcing single-vintage restriction to keep the within-vintage signal interpretable) into a *test* (using documented inter-vintage policy changes as a natural experiment for the methodology's predictive content).

## 4. Data architecture: dual collector

The collector layer mirrors the May-6 synthetic/real taxonomy. Two collectors emit into the same downstream interface; each case carries an `origin` tag that the analysis layer never elides.

### 4.1 Real-data collector

- Source: LendingClub historical loan-level data (Kaggle mirror; verify current availability of original platform download).
- Vintage scope: single quarter of 36-month-term originations (target: 2015 Q3, fully observable through 2018 Q4). Choice rationale: pre-policy-shift, fully terminal, large enough for stable model fitting.
- Case = origination-time feature vector. Excludes any post-origination feature (payment history, etc.) — those would leak.
- Label = binary: `charged_off` (1) vs `paid_in_full` (0). Excludes `current`, `late`, `in-grace-period` (no terminal outcome) and any loan whose observation window doesn't extend to loan_term + 6 months.
- Train / eval split: stratified by outcome, 70/30. R(ε) is fit on train only; all measurements happen on eval.

### 4.2 Synthetic-data collector

- Source: a boundary-extension generator calibrated to real-data marginals on observable features, extending into the rejected region using whatever partial reject data is available (LendingClub historically published a `RejectStats` file with limited features — verify current availability).
- Where reject data is unavailable: the generator extends declared inductive priors about the rejected population's composition (lower FICO tail, higher DTI tail, etc.). Priors are documented in the generator's config so they are available for examination.
- Each synthetic case carries `origin: synthetic` and `synthetic_role: hypothetical-scenario` per the May-6 taxonomy.
- *Validity bound:* synthetic cases support claims at the *hypothetical-scenario* validity bar (faithful modeling of the hypothesized condition) — they cannot support back-testing claims (which require real data) or any claim the May-6 taxonomy reserves for real-data corpora.

### 4.3 Per-case schema (jsonl)

```jsonc
{
  "case_id": "<uuid>",
  "origin": "real" | "synthetic",
  "synthetic_role": null | "hypothetical-scenario",
  "vintage": "2015Q3",
  "features": { /* origination-time features */ },
  "label": 0 | 1 | null,    // null for synthetic cases without outcome
  "per_model": [
    {
      "model_id": "tree_1",
      "T": 0.72,             // confidence-in-grant from leaf purity, grant direction
      "F": 0.21,             // concern from leaf purity, deny direction
      // I deferred for the wedge
      "factor_support_T": [
        {"feature": "fico_range_low", "weight": 0.40},
        {"feature": "annual_inc",     "weight": 0.25}
      ],
      "factor_support_F": [
        {"feature": "dti",            "weight": 0.45},
        {"feature": "revol_util",     "weight": 0.30}
      ],
      "path": ["fico_range_low > 680", "annual_inc > 50000", ...],
      "leaf": "leaf_42"
    }
    /* ... per model in R(ε) ... */
  ]
}
```

## 5. Model class: single decomposable tree per R(ε) member

For the wedge, each member of R(ε) is a single CART (Classification and Regression Tree). Five models in R(ε), varied along two axes:

- Hyperparameter choices: `max_depth` ∈ {6, 8, 10}, `min_samples_leaf` ∈ {50, 100, 200}, sampled to give five distinct (depth, leaf-min) combinations.
- Feature-subset randomization: each tree fit on a random 80% subset of available features, with the FICO and DTI features always included (they are operationally non-optional in any realistic underwriting model; excluding them would push a tree out of R(ε) trivially).

*Rationale for single CART, not random forest or GBM:* per-case attribution and (T, F) emission are direct from a single tree (path to leaf, leaf purity). For a forest or GBM, attribution averages over many constituent trees and the per-component decomposition becomes noisy. The wedge prioritizes attribution clarity over predictive performance.

*Acknowledged cost:* a single CART may not hit production-grade AUC. We accept a more permissive ε for the wedge; iteration 2 can move to monotone-constrained GBMs (closer to what Rudin's group publishes) where ε can be tightened.

## 6. R(ε) construction

1. **Fit a hyperparameter sweep of single CARTs on the train set.** Grid: `max_depth` ∈ {4, 6, 8, 10, 12}, `min_samples_leaf` ∈ {25, 50, 100, 200, 400}, `feature_subsample` ∈ {0.6, 0.8, 1.0}. Record AUC on a hold-out from the train set (not the eval set).
2. **Define ε.** Take the best hold-out AUC; ε = best − 0.02. Any tree within ε is a candidate R(ε) member. Tighten in iteration 2.
3. **Sample five members.** Among in-ε candidates, select five that maximize spread on (depth, leaf-min, feature-subset) — explicitly preferring diversity of inductive bias rather than only diversity of data.
4. **Verify.** All five members report eval-set AUC within ε of best. Record per-model AUC in the output for inspection.

## 7. (T, F) emission per model per case

For a CART on a binary classification task:

- For an eval case routed to leaf ℓ in tree h:
  - **T_h(case)** = empirical proportion of paid-in-full training cases at ℓ (model's leaf-level confidence in grant).
  - **F_h(case)** = empirical proportion of charged-off training cases at ℓ.
  - For a single tree on a binary task, T + F = 1 at the leaf (no residual); leaf-level entropy could be encoded as I but is deferred per Section 1.

*Why this is a defensible (T, F) extraction:* the leaf's empirical class proportion is the canonical CART confidence. T and F are then calibration-target separable — a leaf with 80% paid-in-full produces (T, F) = (0.8, 0.2), a leaf with 50/50 produces (0.5, 0.5). The "neutrosophic" framing is honest about the dimensions being orthogonal even when the wedge's specific extraction has them sum-constrained; iteration 2's more sophisticated emission (e.g., T from leaf purity *combined with* training-density evidence; F from leaf purity *combined with* class-conditional density) breaks the sum constraint and produces genuinely independent components.

## 8. Factor-support extraction per component

For each (case, model, component):

1. Walk the path from root to the case's leaf in tree h.
2. For each split on the path, attribute information gain (Δ entropy at the split, weighted by node sample size).
3. Aggregate per-feature information gain across the path. This is the *path-level feature attribution*.
4. **Per-component split.** At each split on the path, the case took one branch and not the other. Compare grant-purity and deny-purity of the chosen branch's subtree against the *unchosen* branch's subtree:
   - If the chosen branch's subtree has higher grant purity than the unchosen branch's, the split's information gain attributes to **factor_support_T**.
   - If higher deny purity, attributes to **factor_support_F**.
   - If both (uncommon but possible if the unchosen branch was mixed), attributes to both.
   - If neither, the split is informational but does not differentiate the two components for this case; attribute to neither.
   This yields genuine per-component differentiation: a feature can be in `factor_support_T` for one case (it routed the case toward grant-confident territory) and in `factor_support_F` for another case (it routed away from grant-confident territory).
5. Top-k features (k = 5 for the wedge, configurable) as the case's factor support for that component under that model.

*Note for honesty:* this is intrinsic, ante-hoc attribution from the model's own structure. It is *not* SHAP, LIME, or any post-hoc method; it does not generate explanations from a separate explainer model. The wedge's attribution discipline is consistent with Rudin's position and with the position paper's argument against post-hoc explanation.

## 9. Comparison metrics

For each eval case:

- **Outcome agreement.** All five models predict the same direction (argmax of T vs F is the same), AND the spread max(T) − min(T) ≤ 0.10. Cases meeting both conditions are *outcome-agreers*.
- **Pairwise factor-support overlap.** For each pair (h_i, h_j) of models on a given case, compute the Jaccard overlap of top-k features in factor_support_T (separately, factor_support_F). Aggregate across all (5 choose 2) = 10 pairs to a per-case mean overlap.
- **Distribution.** Plot the distribution of mean pairwise factor-support overlap across outcome-agreers, separately for T and F.

The methodology earns its empirical anchor if:

- The distribution is bimodal or has a substantial low-overlap tail (cases with mean pairwise overlap < 0.3).
- Hand-inspection of the low-overlap cases shows genuinely distinct reasoning paths — not just synonymous features (e.g., `fico_range_low` and `fico_range_high` are not "different reasoning"; they are the same signal under different feature names).
- The high-overlap and low-overlap cases differ in ways the methodology can articulate (e.g., low-overlap cases concentrate at certain feature-space regions, or among certain demographic slices, or at certain T-value bands).

The methodology fails to earn its anchor if:

- The distribution is unimodal at high overlap (median > 0.7).
- Or low-overlap cases turn out under inspection to be synonyms-of-the-same-signal rather than genuine reasoning multiplicity.

## 10. Predictive extension (V₂ falsification)

Once the V₁ measurement exists, before fitting R(ε) on V₂:

1. Document the policy delta between V₁ and V₂ (LendingClub's published underwriting changes — FICO floor moves, income-verification tightening, DTI ceilings, term-mix shifts).
2. *Pre-register* predicted factor-support shifts in writing, committed to the repo before V₂ data is touched. Predictions structured as: "feature F in factor_support_X should shift by direction D as a result of policy change P, because ⟨mechanism⟩."
3. Fit R(ε) on V₂ using the same hyperparameter sweep procedure.
4. Measure factor-support distributions on V₂ eval set.
5. Compare measured shifts to pre-registered predictions. Report hit rate, near-hit rate, miss rate, with examples of each.

The pre-registration is non-optional. Post-hoc rationalization of observed shifts is exactly the failure mode the methodology critiques in others; the prototype must hold itself to the standard it argues for.

## 11. Output and inspection

- **One jsonl per run** (`runs/<timestamp>-vintage-<v>.jsonl`), one record per case as schemed in §4.3.
- **Run metadata header** in a sibling `runs/<timestamp>-meta.json`: dataset version, vintage, R(ε) members and their hyperparameters, ε used, train/eval split seed, library versions.
- **A notebook** (`notebooks/wedge-inspection.ipynb`) that loads the jsonl, computes outcome-agreer set, plots overlap distribution, surfaces hand-inspection candidates, and runs basic per-component summaries.
- **A small script** (`scripts/run_wedge.py`) that orchestrates collector → R(ε) fit → per-case emission → jsonl write. CLI flags for vintage, ε, k, and seed.

## 12. Explicit limitations and validity bounds

- **Single model class** (CART). The wedge cannot test cross-class robustness of the disagreement signal (H3 from the prior conversation). That is iteration 2.
- **Deferred I component.** The wedge measures only T and F factor support. Whether I is stable across R(ε) (Tony's prediction) is not testable from this wedge alone.
- **Single dataset, single vintage initially; second vintage as predictive test.** No generality claim. Generality requires N≥3 (5+ preferred), planned across LendingClub, HMDA, and at least one out-of-US-lending dataset.
- **Reject inference is partial at best.** The synthetic collector's rejected-region extension is hypothetical-scenario validity-grade; it does not solve the unobservable counterfactual.
- **LendingClub data is conditioned on their own approval.** All claims about R(ε) behavior are conditional on `granted` status. The dual-collector design names this; it does not erase it.
- **Single ε choice.** Sensitivity to ε (does the H_primary signal persist under tightening / loosening?) is not tested in the wedge. Iteration 2 sweeps ε.
- **No HITL surface, no observability layer, no full pipeline.** Per design — these are (D), (C), (E) and are deferred until earlier strands have produced data.

## 13. What this wedge enables next

If H_primary holds (factor-support dispersion present among outcome-agreers):

- (B) reasoning-trace capture becomes the natural next strand — the per-case factor-support records *are* a primitive form of reasoning trace; the next iteration enriches them with consultation patterns and relational weightings per the May-6 §2 pipeline.
- (A)-deepening: cross-class R(ε) (decomposable trees + GAMs + monotone NNs), tighter ε, full (T, I, F) emission with I derived from leverage / OOD distance.
- (C) observability surface: the per-component disagreement scalars are the runtime signal; expose them through a tracing layer.

If H_primary fails:

- The methodology's central distinction (outcome agreement ≠ reasoning agreement) is empirically thin; revise the May-7 note's structural argument before building further on top.
- This is the *good* outcome of falsification — early failure saves later effort, and the position paper's frame survives even if the methodology's specific empirical bet does not.

## 14. Open questions deferred to implementation

- LendingClub data acquisition specifics (Kaggle vs alternative mirrors; current availability of `RejectStats`).
- Synthetic-collector calibration choices (copula vs Gaussian mixture vs simple per-feature marginal sampling). Probably simple-marginal-sampling for the wedge; better calibration is iteration 2.
- Top-k value for factor support (default k=5; sensitivity test once we have data).
- Outcome-agreement threshold (T-spread ≤ 0.10; reasonableness verifiable empirically once distribution is known).

---

*End of wedge design. Subject to revision as data forces revision.*
