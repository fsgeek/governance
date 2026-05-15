# Pre-registration template

**When to use.** Running an experimental test (Rashomon-band construction, vocab-adequacy probe, silence-manufacture audit, routing test, replication) and want the standard pre-reg/result discipline: predictions frozen *before* code touches data, OTS-stamped, scored by a companion result note. Drafted from 6+ pre-regs in `docs/superpowers/specs/` (2026-05-09 → 2026-05-14). Save as `docs/superpowers/specs/YYYY-MM-DD-<topic>-preregistration-note.md`. Cut sections that don't apply.

---

# <Topic> — pre-registration

**Date:** YYYY-MM-DD. **Status:** PRE-REGISTRATION. **Substrate:** `<path>` (rows × cols; provenance / untouched-or-not). **Companion to:** `<related notes, [[wiki]] links>`. **Connects:** `[[project_X]]`.

**Pre-registration discipline.** Name what's been inspected (schema, dtypes, row counts) and what has *not* (joint distributions on any variable in §3). State the OTS stamp freezes the predictions.

## 1. Question

Frame the question; end *if YES then ... ; if NO then ...* . If a replication or follow-on, name the originating finding.

*Example: "Does the trimodal phase structure replicate on HMDA-RI 2022 (different outcome, different feature inventory)?"*

## 2. Operational definitions

Sub-headed (2a, 2b, ...). Use what applies:

- **2a. Outcome.** Encoding, censoring, threshold.
- **2b. Scope / corpus.** Filter rules with code-level criteria.
- **2c. Stratification.** Stratifier (e.g. `loan_purpose × income_decile`); in-scope rule (e.g. ≥100 rows, ≥10/class); fallback + trigger.
- **2d. Feature partition.** Named (policy) / Extension (admissible beyond policy) / Prohibited (variant-A includes, variant-B excludes). *Example: named = `{fico_range_low, dti, annual_inc, emp_length}`; prohibited geographic = `{tract_minority_population_percent, census_tract, county_code}`.*
- **2e. Band construction.** Variants; ε-band (e.g. **0.02 AUC**); model class (e.g. depth-≤3 CART, leaf-min ∈ {25, 50, 100}, used-feature-set de-dup); seed; monotonicity.
- **2f. Discriminators.** Saturation, Jaccard, R²_named, verdict-divergence — each with exact formula.
- **2g. Missing values.** Parsing, sentinel→NaN, drop rule. Pre-registered, not per-cell.

## 3. Pre-registered predictions

One sub-section per **P1...Pn**. For each:

- **Claim** — one declarative sentence, quantitative where possible.
- **Prior** in [0, 1]. *Example: "Prior: 0.40."*
- **MISS interpretation** — what each failure mode would mean (partial replication, mechanism-bound, threshold-sensitive). Informative MISSes require naming the readings up front.

Mark **load-bearing** predictions (e.g. "P5 is load-bearing for SHAP-killer Line A") and **conditional** ones ("conditional on P1, P2 says ...").

Optional **"Most likely overall miss"** — best guess at how this fails. *Example: "the Jaccard metric is wrong; member-weighted version pre-registered as sensitivity."*

## 4. Sensitivity / robustness pre-specs

Arms reported alongside but **not gating** the primary verdict: ε-band at ε ∈ {0.01, 0.02, 0.03}; Jaccard at J ∈ {0.3, 0.4, 0.5}; adequacy threshold; fallback stratification trigger. Anything that would change the verdict if tuned post-hoc — pre-register or commit not to tune.

## 5. Scope / exclusions ("what this is NOT testing")

Explicit list. *Example: "Not testing SHAP-on-surrogate fairwashing — that's Line A from [[shap_killer_seed]]. Not testing per-decision routing — [[routable_population_result]] remains terminal."*

## 6. Implementation

Result-side script (`scripts/<topic>_test.py`); reused `wedge/` modules; new surface (one script, one JSON, one result note); expected runtime; unit tests for new discriminators.

## 7. Followups (regardless of verdicts)

Conditional menu: "If P1 fires ... ; if P1 fails ...". Both branches terminal — not a gateway to test #N+1.

---

**Pre-reg author:** Claude Opus 4.7 (ghola), governance lineage. **Date:** YYYY-MM-DD. **OTS:** auto-applied by post-commit hook.

---

## Scoring conventions (companion result note)

Result notes open with a **P-scorecard table**: `| Pred. | Prior | Verdict | Headline |`.

Verdicts:

- **HIT** — fired positive at primary thresholds.
- **HIT at floor** — at the minimum threshold; note the margin.
- **HIT (strong)** — well above threshold or clean separator (e.g. ratio ∞); note caveats.
- **MISS** — fired negative.
- **partial MISS** — multi-part criterion `(a) AND (b) AND (c)` had some parts pass; itemize.
- **informative MISS** — failed the binary but the failure pattern is itself a finding (e.g. "manufactured-silence class bounded to one vintage"). Cite the pre-reg's MISS-interpretation.
- **N/A** — conditional predecessor didn't fire.
- **directional HIT, threshold MISS** — sign agrees, magnitude doesn't clear (HMDA P3).

Mixed scorecards (e.g. "4 HITs, 1 informative MISS"; "0/5 HITs, 3 N/A") are the calibration sweet spot — uniform HITs/MISSes suggest miscalibrated priors.

**Scope-of-claim discipline.** State what the verdicts let you claim *and where the claim ends*. *Example: "Trimodal claim tightens to 'FM-substrate-validated', not universal."* Apply [[project_pre_registration_pattern]]: uniformity-assumption failures get explicit heterogeneity next time.

**Pre-reg corrections at result time.** Typos, code-language slips, feature-leak fixes go in a "Pre-reg corrections" sub-section of the result note. Predictions, priors, thresholds are **not** retroactively edited; the OTS-stamped pre-reg is the artifact.

---

## Commit message form

Pre-reg commit:

```
<topic>: pre-registration

PRE-REGISTRATION (NOT post-hoc). Predictions frozen before any code touches
data on <substrate>. Post-commit OTS hook stamps this commit.

<2-3 line summary + P1-Pn list with priors>
```

Result commit:

```
<topic>: RESULT (<scorecard, e.g. "P-scorecard MISS" or "4 HITs / 1 informative MISS">)

<2-3 line headline + load-bearing finding + what tightens or falsifies>
```

OTS stamp lands on the next commit as `ots: stamp <hash>`.
