# Indeterminacy Operationalization — Design Memo

**Date:** 2026-05-08
**Status:** Working design, pre-implementation. Sequel to `2026-05-07-rashomon-prototype-wedge-design.md`; supersedes its §7 "I deferred" decision.
**Scope:** How the I dimension in (T, I, F) emission becomes computable for the Rashomon-routed methodology. This is Layer 2 of the wedge evolution. Layer 1 (selection criterion redesign over attribution space rather than hyperparameter space) depends on this work and is downstream of it.

---

## 1. Why I needs operationalization now

The 2026-05-07 wedge accepted T+F=1 by construction (`models.py` is explicit) and deferred I on the prediction that I would be the most-stable dimension and therefore the least informative to measure first. The first real-data run on 2015Q3 (commit `c2b04a7`) made the deferral untenable: with I absent, the wedge is **not testing the methodology, it's testing a degenerate scalar version of it.** Reporting a Rashomon-set analysis with relabeled axes ("T" and "F") doesn't constitute a test of the neutrosophic frame's claim that I carries information classical probability throws away.

Layer 1 (move the diversity-weighted selection from hyperparameter space onto attribution space) is real work but is *defined relative to the emission*. If we redesign the emission to produce (T, I, F), the diversity criterion should be defined over the new emission — not over the degenerate one. So Layer 2 constrains Layer 1, and is the prerequisite for any methodological claim the run results could support.

## 2. The structural payoff: I as a channel T/F cannot carry without leaking

The non-obvious move in operationalizing I is what becomes possible *because* I exists as a separate channel. Two examples that classical probability cannot articulate without violating model assumptions:

**Post-origination outcomes feeding prospective indeterminacy.** When historical borrowers with profile P showed default patterns *not explained by their origination features*, profile-P new applications inherit elevated I. We are not using future data to predict past outcomes (that would be leakage and trivial). We are using past surprise to flag *uncertainty about the current prediction*. T/F cannot carry this without becoming the label; I can carry it precisely because it is structurally separate.

**Examinability.** T/F are model outputs. I is a model statement about itself. An external examiner can interrogate I in a way they cannot interrogate the predictor — "what makes this case I-rich?" has answers in features and species; "why did the model say T=0.7?" has answers only in the model's internal state. I is structurally more transparent and is therefore the channel where governance-relevant interrogation lives.

**Novelty precision (for the position paper's defensibility).** Concept-drift and calibration-drift literatures already use post-origination outcomes to monitor model health. What is novel here is not "use historical data" — that is table stakes — but specifically (a) structuring it as a *per-case* signal rather than an aggregate model-quality metric, (b) propagating it through a separate channel that does not collapse into T/F, and (c) making it externally examinable. A reviewer who says "this is just concept drift" is wrong, and the difference is articulable in those three terms.

## 3. I as a vector, not a scalar

The conceptual definition in working notes and conversation is broader than any single computational signal. Four species with distinct content:

1. **Local-density.** A case is unusual in its leaf's typical feature distribution. Both tails: atypical (high distance from leaf centroid) AND suspiciously typical (low local entropy in the leaf's feature subspace). Captures "doesn't fit" and "fits too well" within the immediate model-local neighborhood.

2. **Multivariate-coherence.** A case violates expected correlation structure across features in the corpus as a whole — features that are typically correlated in the training distribution are anti-correlated for this case. High FICO with high DTI in a vintage where the joint distribution rarely shows that combination. Computed via density estimation on the marginal joint, separate from any leaf-local computation.

3. **Ioannidis-suspicion.** Data carrying fingerprints of suspicious provenance. Round-number clustering (income reported as $50,000 exactly far more often than the underlying distribution would predict), threshold-hugging values (employment length exactly at 2.0 years where lenders set cutoffs), Benford-violations in stated quantities, internal contradictions across self-reported fields. Citation chain to anchor: Ioannidis 2005 ("Why Most Published Research Findings Are False"); Simonsohn et al. on p-curve forensics; Benford's-law applications in fraud detection. The species exists to capture *pathology of the data itself*, not pathology of the model's fit to it.

4. **Retrospective-trajectory.** Post-origination outcome surprise propagated as I on prospectively-similar cases. Operationalized via a separate "surprise model" trained on (origination_features → outcome_surprise) where outcome_surprise includes things like defaulted earlier than expected given origination signals, paid despite negative origination signals, defaulted with smaller stress event than expected. The surprise model's output on a new case becomes the retrospective species' contribution to that case's I. **This species is the load-bearing piece for the Olorin deployment story** (§7); banks have the lifecycle data; current systems do not structure it as a per-case I-channel.

These species are not reducible to each other in general. A case can be Ioannidis-suspicious (rounded income) without being multivariate-incoherent (FICO/DTI in expected joint range). It can be multivariate-incoherent without being unusual in its leaf's local distribution. **Whether they collapse on real data is itself an empirical question** — if readings show them strongly correlated, we have justification to summarize; if not, we keep the vector and the methodology gets correspondingly richer.

## 4. Computational definitions in CART/LC terms

Per species, concretely:

**Local-density.** For each leaf, compute the centroid and per-feature standard deviation of the training cases that fall in that leaf. For a new case, compute Mahalanobis distance from its leaf's centroid. Map to I via a both-tails function: cases very close to centroid (low local entropy in their leaf's feature subspace) AND cases very far from centroid both score I-positive, with a directional flag attached so downstream consumers can distinguish "fits too well" from "doesn't fit."

**Multivariate-coherence.** Fit a density estimator (lead candidate: Gaussian mixture; alternative: kernel density) on the full training corpus's joint feature distribution. For each case, compute log-likelihood under that density. Low log-likelihood = I-positive. The estimator choice is a design lever; we encode one and hold one in reserve for empirical comparison if the first behaves badly.

**Ioannidis-suspicion.** A battery, not a single test:
- Round-number penalty: comparison of observed rounding patterns in stated income against expected rounding patterns under a smooth underlying distribution. χ² or Kolmogorov-Smirnov against expected.
- Threshold-hugging: case-level flags for values landing at known underwriting thresholds (emp_length exactly 2.0, FICO exactly 660, etc.). Per-threshold list maintained as a small named registry.
- Internal coherence: case-level checks for plausibility violations across self-reported fields (DTI implied by income+debt vs. stated DTI).
- Benford applied to leading-digit distributions of monetary fields where sample size supports it.

Each test contributes a per-case scalar; the battery's outputs are *reported individually*, not aggregated to a single Ioannidis score. Aggregation is itself a design choice we defer to empirical observation.

**Retrospective-trajectory.**
- *Production version (full methodology):* train a surprise model on past (origination_features, observed_outcomes_with_surprise_labels). For new applications, surprise-model output becomes the retrospective species' I.
- *LC evaluation version (proxy):* train surprise model on later vintages' actual outcomes (e.g., 2016–2017 cohorts that have completed terminal observation), evaluate on 2015Q3 origination features, ask whether the surprise model would have flagged origination features the original underwriting did not weight. This is a within-LC simulation of what production would do; it tests the architecture without claiming the methodology has been deployed.

## 5. Pre-registered behaviors a "good" I-encoding should exhibit

Before any real-data reading on the new emission:

- I should be **more stable across Rashomon members** than T or F — Tony's contrarian pre-registered prediction from the 2026-05-07 working session.
- I should peak on cases an examiner would also flag as unusual when shown the case manually (validation against human judgment on a hand-picked subset).
- The four species should **not be perfectly correlated** — if they are, we have one signal with four names; if they are not, we have a real vector. Either result is informative.
- The retrospective species' I on N≥k vintages should correlate with concept-drift literature's metrics computed on the same data, validating that retrospective species captures something credible by independent measure.
- Among outcome-disagreers (T-direction split across the Rashomon set), I-disagreement among the same models should be *smaller* than T-disagreement — the pairwise prediction from the same working session ("if we disagree on T and F, we'll be closer on I").

## 6. Two test surfaces, explicitly separated

**Methodology completeness (production scenario).** All four species computed. Requires N quarters of post-origination data for the retrospective species' surprise model. This is the configuration deployed at Olorin partner banks, not the configuration our LC evaluation runs.

**LC evaluation (what we can actually run).** Species 1, 2, 3 computable directly on origination data. Species 4 via the vintage-simulation proxy. Explicit acknowledgment in the paper: this tests the methodology's *architecture* on N=1 dataset; the retrospective species' production behavior is not directly tested here. HMDA is the planned second dataset (per 2026-05-07 spec); subsequent datasets follow.

We let the test surface match what we can compute; we do not let it shape the methodology specification.

## 7. Olorin deployment story (one paragraph, on the record)

Banks already collect post-origination performance data; current credit-scoring stacks treat it as model-retraining input or as aggregate drift metric. The neutrosophic frame structures it as a per-case I-channel that is externally examinable. That structural rearrangement is the value-add: it gives banks a way to use their own lifecycle data to inform indeterminacy on new applications, in a form that an external examiner (regulator, auditor, governance officer) can interrogate case-by-case rather than accepting an opaque drift score. The retrospective species §3.4 is the operational locus of this contribution; species 1–3 provide the broader I-vector context the channel needs to be informative.

## 8. Explicit non-commitments

The following are *not* pre-specified by this memo and will be settled by empirical observation:

- Which species ends up most informative or most stable in real LC data
- Whether the four species reduce to a scalar or remain a vector — empirical, not pre-specified
- Density-estimator choice for the multivariate-coherence species (GMM as lead candidate; KDE held in reserve; pick by behavior, not by prior)
- The Ioannidis battery's tests are reported individually; aggregation rule deferred until we see the readings
- The retrospective species' surprise-label definition (early default, paid-despite-bad-signals, etc.) is itself a design lever we will compare alternatives on
- The mapping from raw species score to comparable I-units across species — start with rank-based normalization within species; revisit
- Whether species disagreement should itself become a secondary I-signal ("contested indeterminacy") is a question this memo names but does not resolve

---

## Implementation note

Once this memo is interrogated and any revisions absorbed, the encoding work in `wedge/models.py` (per-leaf I emission), `wedge/attribution.py` (per-species attribution decomposition), and a new `wedge/indeterminacy/` module (the four species computations) follows. Layer 1 (selection criterion over attribution space) should be designed against the new emission, not against the degenerate one currently in production. The 2015Q3 run's results stand as the baseline for what the degenerate emission produces; comparison against those results after the new emission lands is itself a useful diagnostic.
