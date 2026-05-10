# Experiment Preregistration Template

**Title:**  
**Date:**  
**Status:** Pre-registration  
**Linked hypothesis ID:**  

## 1. Motivation

Why this experiment exists now, and what question it is supposed to resolve.

## 2. Substrate / Dataset

- Primary dataset or corpus:
- Secondary dataset or comparison set:
- Model class or workflow surface:
- Version / run artifacts already on disk:

## 3. Exact Measurements

List the precise measurements, proxies, and summary statistics the experiment
will use.

Required details:

- unit of analysis
- feature or case filters
- thresholds
- aggregation rules
- any ranking or normalization choices

## 4. Inclusion / Exclusion Criteria

State exactly which cases, runs, models, or records are in scope and which are
excluded.

## 5. Heterogeneity Assumptions

State what asymmetries, subgroup behavior, or regime differences are expected.

If the experiment assumes symmetry or uniformity, say so explicitly.

## 6. Primary Predictions

List each prediction separately.

For each:

- prediction ID
- expected direction or relationship
- expected magnitude if known
- confidence level if useful
- mechanism story, if the mechanism is part of the claim

## 7. Alternative Outcomes That Count as Failure

State the results that would falsify the claim.

Do not write only "opposite direction." Be concrete about:

- null results
- mixed results
- subgroup reversals
- baseline parity outcomes
- degenerate or non-informative measurement behavior

## 8. Comparison Baseline

If the experiment is comparative, name the exact baseline and why it is the
fair comparator.

Examples:

- SHAP on a single calibrated model
- bagging variance
- current bank process
- raw human handoff

## 9. Analysis Plan

Describe the computation and classification plan.

Include:

- scripts or code paths to use
- ordering of computations
- how hit / near-hit / miss will be assigned if relevant
- what gets reported no matter the outcome

## 10. Decision Rule / Kill Criteria

State what result would kill the current claim or force a downgrade in the
research program.

This is the section most likely to be weakened post hoc if not written clearly.

## 11. Known Limitations Before Running

List limitations that are already known before the experiment runs.

Examples:

- anchoring claims not yet externally verified
- feature-pool limitations
- current model class mismatch
- weak sample size
- measurement degeneracy risk

## 12. Output Links

Fill what exists now and update with links after the run:

- script:
- prereg artifact:
- expected findings-note location:
- expected run-output location:

## 13. Notes on What This Experiment Does Not Decide

State explicitly which broader claims remain open even if this experiment hits
or misses.
