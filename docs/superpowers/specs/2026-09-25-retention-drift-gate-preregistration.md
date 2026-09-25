# Retention drift: go/no-go gate pilot — pre-registration

**Date:** 2026-09-25. **Status:** FROZEN at the commit that adds this file (OTS-stamped).
**Author:** the governance instance that owns the project (Opus 5.5), with Tony Mason as PI.
**Supersedes nothing.** Record-sufficiency v1 (pre-reg `bd47a9d`) was withdrawn at `db12bc0`; this is
a different question, not a repair of that one. Its successor design ("serialize the record, predict
R2 fails") is true by construction and is not run.

## 1. Question

A lender stores **everything** needed to recompute a post-hoc explanation: the trained model artifact,
the background data, the seed, and the explainer arguments. Later, inside a record-retention horizon,
someone recomputes the explanation with the software available *then*. **Do the adverse-action reasons
come out the same?**

Regulatory anchor: Reg B requires specific principal reasons (12 CFR 1002.9(b)(2)); Official
Interpretation 9(b)(2)-1: "disclosure of more than four reasons is not likely to be helpful to the
applicant." The unit of comparison is therefore the **top-4 adverse reason set**. Reg B adverse-action
record retention is 25 months (1002.12(b)); model-risk retention is typically longer.

This is a **gate**, not the paper. It decides whether FAccT '27 is pursued (§7).

## 2. Prior art (checked 2026-09-25, before this freeze)

Open but crowded. Closest: Hwang et al. arXiv:2601.12654 (fixed model, explainer stochasticity,
single environment); Zhou et al. arXiv:2605.23955 (KernelSHAP rank instability tied to ECOA,
single environment; TreeSHAP stable within one environment — the assumption tested here across
versions); Peter et al. arXiv:2608.21449 (same XAI method, different frameworks, time series);
Jin et al. arXiv:2602.07195 (26% of Kaggle notebooks reproduce; 12% after downgrading to original
versions); Montandon et al. arXiv:2408.05129 (default-argument breaking changes). Known mechanism:
shap issue #4288 (shap 0.49 cannot parse xgboost 3.x base_score). None holds a stored artifact fixed
and varies the library stack over a retention horizon measuring reason-set agreement.

## 3. Vintages (the independent variable)

A vintage is the stack a lender would have resolved installing on **July 1 of year Y**
(`uv pip install --exclude-newer Y-07-01`), on the CPython minor current then. Built by
`scripts/retention_drift/build_envs.sh` before this freeze; resolved versions:

| Vintage | Python | shap | scikit-learn | xgboost | numpy | scipy |
|---|---|---|---|---|---|---|
| v2021 | 3.9 | 0.39.0 | 0.24.2 | 1.4.2 | 1.21.0 | 1.7.0 |
| v2022 | 3.10 | 0.41.0 | 1.1.1 | 1.6.1 | 1.22.4 | 1.8.1 |
| v2023 | 3.11 | 0.41.0 | 1.3.0 | 1.7.6 | 1.24.4 | 1.11.1 |
| v2024 | 3.12 | 0.46.0 | 1.5.0 | 2.1.0 | 2.0.0 | 1.14.0 |
| v2025 | 3.13 | 0.48.0 | 1.7.0 | 3.0.2 | 2.2.6 | 1.16.0 |
| v2026 | 3.14 | 0.52.0 | 1.9.0 | 3.3.0 | 2.4.6 | 1.18.0 |

`lime` resolves to 0.2.0.1 (last release 2020) in every vintage; its drift, if any, comes from its
dependencies. Note v2022 and v2023 share shap 0.41.0 — that pair isolates non-shap drift.

## 4. Design

**Substrate.** LendingClub accepted loans 2007–2018Q4, completed loans only (Fully Paid vs Charged
Off/Default). 24 origination-time features (no LC grade/interest rate, nothing post-origination):
`loan_amnt, term_months, annual_inc, dti, fico_range_low, credit_age_months, emp_length_yrs,
home_own_code, verification_code, purpose_code, delinq_2yrs, inq_last_6mths, open_acc, pub_rec,
revol_bal, revol_util, total_acc, mort_acc, num_actv_rev_tl, bc_util, pct_tl_nvr_dlq,
acc_open_past_24mths, avg_cur_bal, pub_rec_bankruptcies`. Rows with missing values dropped.
Seed 20260925. 40,000 train, 1,000 eval, 100-row background drawn from train. Frozen once to
`.npy` (a format every vintage reads) by the project env; the frame is the lender's archived data.

**Models (trained at the ORIGIN vintage, then archived).**
- M1 `sklearn.ensemble.GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=SEED)`, archived with stdlib `pickle` (sklearn's documented persistence).
- M2 `xgboost.XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, tree_method="hist", random_state=SEED)`, archived as xgboost native JSON (`save_model`, the vendor's durable format) **and** pickle. Contest loads JSON first; pickle is recorded as a secondary load path.

**Denied set.** At origin, the 20% of eval rows with the highest archived P(default), per model
(200 applicants). All reason-set metrics are computed on the denied set.

**Methods (all explicit arguments, the same at origin and contest).**
- TreeSHAP: `TreeExplainer(model, data=background, feature_perturbation="interventional")`, raw (log-odds) output; all 1,000 eval rows.
- KernelSHAP: `KernelExplainer(f, background[:50])`, `f = P(default)`, `np.random.seed(SEED)` immediately before `shap_values(X_denied, nsamples=2048, l1_reg=<style>)`. Two call styles: **PINNED** `l1_reg=False`; **DEFAULT** `l1_reg` omitted (what an examiner calling with defaults gets).
- LIME: `LimeTabularExplainer(X_train, mode="classification", discretize_continuous=True, random_state=SEED)`; `explain_instance(x, predict_proba, num_features=24, num_samples=5000, labels=(1,))`.

**Adverse reasons.** The 4 features with the largest positive contribution toward default
(TreeSHAP/KernelSHAP: largest positive attributions for class 1; LIME: largest positive weights
for label 1, mapped back to feature index). Fewer than 4 positive contributions → the set is the
positive ones.

**Pairs.** Each vintage is an origin. Each origin is recomputed (a) in every LATER vintage (15
forward pairs, Δ = 1..5 years) and (b) in its OWN vintage in a fresh process (6 same-vintage
repeats = noise floor). Contest loads only the archive directory; no shared process or object.

**Outcomes per (origin, contest, model, method).**
- `UNLOADABLE`: the archived model cannot be loaded in the contest vintage.
- `UNCOMPUTABLE`: loads, but the explainer raises.
- Otherwise metrics.

## 5. Metrics

- **Primary: R** = fraction of denied applicants whose unordered top-4 adverse reason set differs from the archived set. 95% bootstrap CI over applicants (2,000 resamples, seed fixed).
- **Drift beyond noise:** R_excess = R_pair − max(R_repeat(origin), R_repeat(contest)).
- Secondary: ordered top-4 match rate; mean top-4 Jaccard; RBO (p=0.9) over the full ranking; max |Δ attribution|; max |ΔP(default)|; count of denied-status flips (the decision itself changing).
- **Positive control (metric sensitivity):** at each origin, TreeSHAP recomputed with a *different* 100-row background (seed+1). R_pos must be > 0 at every origin; if it is 0, the metric is declared insensitive and the gate is VOID.

## 6. Predictions (my bets, frozen)

- **B1 (TreeSHAP, loadable pairs):** 70% that every loadable TreeSHAP pair has R_excess < 1%.
- **B2 (sklearn pickle):** 75% that at least one M1 pickle from v2021/v2022 is UNLOADABLE in v2023 or later (tree node layout changes).
- **B3 (xgboost JSON):** 85% that M2 JSON loads in every later vintage.
- **B4 (shap × xgboost 3.x):** 60% that TreeSHAP on M2 is UNCOMPUTABLE in at least one of v2025/v2026.
- **B5 (KernelSHAP PINNED):** 55% that at least one Δ≤2 pair has R_excess ≥ 5%.
- **B6 (KernelSHAP DEFAULT vs PINNED):** 60% that DEFAULT shows more drift than PINNED on at least one pair (default-argument drift).
- **B7 (LIME):** 50% that at least one Δ≤2 pair has R_excess ≥ 5% despite LIME itself being frozen.

## 7. Gate rule (decides FAccT '27)

Within-retention pairs are Δ ≤ 2 (≤ 24 months).
- **STRONG GO:** any method on a loadable, computable Δ≤2 pair has R_excess ≥ 5% with CI lower bound of R > R_repeat upper bound. The paper is attribution drift.
- **WEAK GO:** no STRONG GO, but a standard archive format is UNLOADABLE or the explainer UNCOMPUTABLE on a Δ≤2 pair. The paper would be about explanation-toolchain longevity; FAccT-worthiness then decided after blind adversarial review, not by me alone.
- **NO-GO:** all Δ≤2 pairs loadable and computable with R_excess < 1% for every method. FAccT '27 is dropped and the null is written up as such.
- Anything else (1–5%): AMBIGUOUS → blind adversary, then decide, reasons recorded.

Before any result sentence is written, a blind adversarial review (scientific-integrity-auditor) of
harness + outputs is mandatory.

## 8. Known limitations (declared now)

One substrate; two model classes; CPU only; one machine (WSL2); vintages are July-1 snapshots, not
what any particular lender ran; the contest path is "recompute with the contest-time stack" — the
alternative (re-install the origin stack at contest time) is trivially feasible here because all six
envs installed on 2026-09-25, which is itself only a one-date observation. Python-version rot is
captured only through the vintage/CPython pairing. No GPU nondeterminism.

## 9. Amendment A1 (2026-09-25, recorded after the six ARCHIVE runs started and BEFORE any recompute pair existed)

**Observed at origin:** v2023 (shap 0.41.0 + numpy 1.24.4, as resolved by `--exclude-newer 2023-07-01`)
cannot compute any SHAP attribution: shap 0.41 uses `np.bool`/`np.int`, removed in numpy 1.24
(`AttributeError: module 'numpy' has no attribute 'bool'`). shap 0.42.0 shipped 2023-07-06. LIME
is unaffected. Under §4 this is `ORIGIN_UNCOMPUTABLE` for v2023's SHAP cells and `UNCOMPUTABLE`
wherever v2023 is the contest vintage; the **primary analysis keeps v2023 exactly as frozen.**

**Added, secondary, labelled as such everywhere:** vintage **v2023p** = v2023 with `numpy<1.24`
(the constraint a working 2023 shap install needed). It is an origin and a contest vintage in the
same way as the others, reported in a separate table, and **cannot by itself move the gate** (§7
is evaluated on the frozen vintages). Rationale: separates "the explainer's own dependency hygiene
broke" from "a working stack drifts."
