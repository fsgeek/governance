# Bin-4 k=5 Case Reading — Findings Note

**Date:** 2026-05-08
**Status:** Findings note from a 20-case hand-reading of bin-4 k=5 cases (2015Q4 vintage). Companion to `2026-05-08-all-atypical-conditional-findings-note.md`; tests its §1 narrative claim and §4 frame interpretation against case-level data.
**Scope:** What the conditional-findings note's "wealthy borrower with traditional bank credit options" reading looks like under case-by-case examination, and what structural claim survives when the narrative does not.

---

## 1. Headline

The conditional-findings note's frame — *bin-4 k=5 cases are wealthy, low-leverage borrowers who came to LC despite having access to traditional bank credit* — **failed** under case-level reading. Of 20 cases sampled (all 9 charged-off bin-4 k=5 cases in 2015Q4 plus 11 randomly-sampled paid cases), 2 fit the frame cleanly; 11 are ambiguous; 7 contradict it.

Pre-registered prediction (recorded in conversation before the reading): 12-15 / 5-8 / 1-3. Realized: 2 / 11 / 7. The pre-registration discipline did its job — it prevents re-describing the result as a calibration miss — and the honest reading is that the frame was *wrong*, not overconfident.

A different frame is available, and the prior frame is now visible as a special case of it. Subgroup A — *frugal borrowers in a high-leverage population* — is what the conditional-findings note's mechanism story actually describes; it is one of at least two distinct mispricing mechanisms the methodology surfaces in bin-4 k=5. §2 argues for two from this reading; the underlying count (4-5 cases per subgroup) does not yet support either *exactly two* or *these specific two*, which §3 and §5 take up.

## 2. The two-mechanism finding

The 11 ambiguous cases sort cleanly into two subgroups with different feature signatures:

### 2.1 Subgroup A — frugal borrower (cases 3, 8, 9, 15, 17)

Modest income ($30-84K), very low DTI (0.29 to 2.06), low-to-moderate revolving utilization (0% to 65%). These are not wealthy borrowers. They are *low-leverage* borrowers in a population (LC's approved set) that skews high-leverage. The frame's "capacity-limit on the sparse tail" mechanism applies cleanly — CART leaves can't be granular enough at the low-DTI corner because most LC borrowers are higher-DTI — but the conditional-findings note's "wealthy" framing does not apply. These borrowers came to LC for small loans (often $3-10K, often home improvement) at modest rates that the trees could not price tightly.

### 2.2 Subgroup B — wealthy but heavily levered on revolving (cases 11, 13, 16, 20)

Very high income ($300-650K), moderate DTI (8-17%), but revolving utilization 76-94%. These cases look "low-leverage" to the wedge — DTI is moderate — but they are *heavily* levered on revolving credit, a fact the wedge cannot see because `revol_util` is not in `ORIGINATION_FEATURE_COLS`. The atypicality consensus correctly fires (the trees cannot price this combination — high income with high revolving leverage is a sparse corner) but the §4 frame's mechanism story attributes the mispricing to "capacity limits at the wealthy/low-leverage corner," which is wrong about *why*. The trees cannot price these because the methodology *did not give them the relevant feature*, not because of intrinsic capacity limits.

### 2.3 The contradicting cases

Of the 7 cases that flatly contradict the frame, 4 are very high DTI (35-40%) wealthy-on-paper borrowers (cases 5, 6, 14, 18, 19); the trees correctly underwrote these as moderate-risk grade-B at 9-11%, and the methodology over-flagged. Case 4 is the cleanest contradiction: $480K income, DTI 21, revol_util 98.6%, charged off — the trees correctly priced this as grade E at 18.2%, and the methodology's "atypical, mis-priced upward" claim is exactly wrong (the trees got it right; the methodology fired anyway).

## 3. The structural finding

The two-mechanism split implies a structural claim worth landing in the methodology spec:

> Indeterminacy species and the interpretive frames built on top of them inherit the predictor's feature pool by default. Pathology detection and capacity-limit attribution have different evidentiary needs than prediction. When a species' direction tag or a frame's mechanism story attributes the underlying score to the wrong axis, the externally examinable explanation is misdirected even when the score itself is correct.

This is the same structural pattern the conditional-findings note's all-atypical-tail finding traces — *the methodology's interpretive labels point at one axis while the actual pathology lives on an adjacent axis*. The case-reading surfaces it in two specific instances:

- **Frame inheritance.** The §4 silence-manufacture frame names "trees average tail populations into bulk leaves." True for Subgroup A (frugal-borrower); incomplete for Subgroup B (wealthy-with-revolving), where the trees can't see revol_util at all. The frame inherited the wedge's feature view of "leverage" (DTI-only).
- **Species direction inheritance.** The Ioannidis-suspicion species fires correctly on cases 2 (Store Manager reporting $850K) and 7 (server reporting $120K) — score 1.0 and 0.6 respectively. But the direction tags (`multiple_of_25000`, `multiple_of_10000`) point at *income roundness*, when the actual pathology is *income-employer incoherence*. The species could not articulate the correct direction because the wedge collector did not load `emp_title`. (See §4 of `2026-05-08-indeterminacy-operationalization-memo.md`, which deferred internal_coherence on the stated grounds that "with only FICO/DTI/income/emp_length the scaffolding is too thin." This was true given the predictor's feature pool — but pathology-detection's evidentiary needs are not the predictor's.)

Both instances are the same structural error: *the species/frame's vocabulary is constrained by the predictor's vocabulary, even though their evidentiary purposes diverge*.

The structural claim has the right shape — there is no obvious reason a species' interpretive vocabulary should be constrained by the predictor's feature pool, and several reasons it should not be — but the evidence here is two specific instances (Subgroup B revol_util, Ioannidis direction tags from cases 2 and 7). That is not a structural law; it is a hypothesis with two suggestive cases. Replication on the remaining 84 bin-4 k=5 cases (and across vintages, and across datasets) would test whether the pattern is structural or whether it reflects two coincidences in this particular wedge. The hypothesis is shaped to survive that test, but stating it as established now would be overreach of exactly the kind §1 just retracted.

## 4. Implications

**For the methodology spec.** The species battery should declare its evidentiary needs *independently* of the predictor's feature requirements. Specifically: the LC collector should load `revol_util`, `emp_title`, `home_ownership`, and `verification_status` for indeterminacy use even if the trees do not consume them. Either as a separate feature pool surfaced to the indeterminacy module, or as an explicit "predictor features" / "examination features" split in the case schema.

**For the conditional-findings note.** The §1 narrative ("wealthy borrowers who came to LC despite having other options") should be revised to acknowledge that bin-4 k=5 is at minimum two distinct subgroups, only one of which is wealthy. The §4 frame should be revised to acknowledge that capacity-limit attribution depends on *which features the model class can see* — the trees' inability to price these cases is not always a capacity limit (Subgroup A) and is sometimes a feature-omission artifact (Subgroup B).

**For the position paper.** The structural-recovery claim ("methodology un-manufactures the silence the model class created") *survives, but conditionalizes*. It does not strengthen — that would mean the new finding adds force to the original claim. What actually happened is two-stage: the original claim narrowed in scope (capacity-limit attribution applies cleanly to Subgroup A; for Subgroup B the mispricing is *feature-omission*, not capacity-limit), and the methodology gained a structural finding about feature-pool inheritance (which itself has thin evidence per §3). The position paper should reflect both moves separately, not collapse them into a single "strengthens" that would obscure what the case reading actually showed. A more honest formulation of the §4 frame: *the methodology surfaces cases the model class mis-prices for any of several reasons; per-case mechanism may or may not be capacity-limited; the methodology's interpretive labels point at one axis of the mispricing while the actual mechanism may live on an adjacent axis the species cannot see*.

**For the next ghola.** Three concrete next moves, in priority order:
1. Modify `wedge/collectors/lendingclub.py` to load an examination feature pool (`revol_util`, `emp_title`, `home_ownership`, `verification_status`) alongside the trainer feature pool. Re-emit jsonl with both pools per case.
2. Implement Ioannidis `internal_coherence` test (income/employer plausibility, income/DTI/loan-amount plausibility) using the broader feature pool.
3. Re-run the bin-4 k=5 analysis with the fuller feature set and check whether Subgroup B remains atypical when revol_util is in the species' view (it should — the methodology's *score* is correct; only the *attribution* is misdirected).

## 5. Explicit non-commitments

The structural finding in §3 applies to *this document*. The case verdicts in §2 are one reader's interpretation against one set of features (the wedge's four origination features plus the CSV enrichment in `bin4_k5_case_sheet.py`). The two-subgroup split in §2.1 / §2.2 is a one-reader pattern, not an observed structural division. Both the headline narrative-failure claim and the two-mechanism replacement rest on the same interpretive act, and a blind second reader would test both at once. What would settle them: an independent F/A/C pass and an independent subgroup attempt by a second reader (Tony, or a third party), with inter-rater agreement computed on both. Lacking that, every claim downstream of §2 should be read as "one reader's pattern" rather than "observed structure." The note is itself a worked instance of the structural finding it argues for — interpretive vocabulary conditioned on the reader's feature pool, attribution potentially misdirected — and that recursion is not a side-issue, it is the central caveat.

Other limitations:

- **N=20 from one vintage.** Sample of the 104-case bin-4 k=5 population in 2015Q4. Replication on the remaining 84 (deterministic seed in `scripts/bin4_k5_case_sheet.py`) would settle whether the two-subgroup split is robust, an artifact of sampling, or actually three subgroups, or one subgroup with two surface presentations. "Exactly two mechanisms" is not yet defensible.
- **Subgroup counts are 4-5 cases each.** The §3 structural claim is built on these counts; the §4 architectural prescriptions cascade from §3. The further out from the 9 cases, the more inferential weight thin counts are asked to carry. The thinness threatens both the empirical instance and the structural generalization, not only the former.
- **The "trees can't see revol_util" claim is testable but not tested.** Fitting trees with revol_util in `ORIGINATION_FEATURE_COLS` and re-running the bin-4 k=5 analysis would show whether the set contracts (frame's feature-omission diagnosis confirmed) or remains stable (some other mechanism).
- **The Ioannidis direction-tag finding rests on 2 cases.** The general structural claim survives small-N if the *shape* is right; the empirical instance is narrow.
- **Pre-prediction discipline is informal.** The 12-15 / 5-8 / 1-3 prediction was recorded in conversation before the reading. It is not a formal pre-registration in any external system; the discipline is self-imposed. A future reader has no independent verification that the prediction was made before the reading.

## 6. Known instability — bin edges across runs

T-bin boundaries used by the conditional-findings analysis are computed from quintile edges of the full real-cases set in each run, but are not recorded anywhere. Every script that wants "bin-4" recomputes from the jsonl. Within-run analyses are deterministic. Cross-run comparisons (e.g., comparing bin-4 in this case-reading against bin-4 in a future re-run with revol_util added) will silently disagree if edges shift, which they will whenever the underlying jsonl changes. A future fix would persist edges in run-meta.json or in a separate edges-reference file declared per analysis. Documented here so the next ghola does not have to rediscover.

## 7. Reproducibility

- `scripts/bin4_k5_case_sheet.py` — pulls the 20-case sample (deterministic, seed=20260508) from `runs/2026-05-08T17-44-39Z.jsonl`, joins to `data/accepted_2007_to_2018Q4.csv` by 6-tuple, prints a hand-readable case sheet. All 20 joined uniquely.
- The case verdicts in §2 were assigned by hand reading of the case sheet output. The full per-case table appears in working notes; the structural findings (§2.1, §2.2, §3) are the load-bearing summary.

## 8. Connection to other working documents

- **`2026-05-08-all-atypical-conditional-findings-note.md` §1 / §4.** This note tests the narrative claim and frame interpretation; the narrative does not survive but the structural claim sharpens. The conditional-findings note's "decompose marginal into conditional" move applies here too: bin-4 k=5 is itself further decomposable into Subgroups A and B with different mechanisms.
- **`2026-05-08-indeterminacy-operationalization-memo.md` §3 / §4.** The species' direction tags inherit the predictor's feature pool. The deferred `internal_coherence` test was deferred on the wrong grounds — not "scaffolding too thin" but "evidentiary scope not declared independently of predictor."
- **`2026-05-07-rashomon-prototype-wedge-design.md` §4.3 / §5.** The case schema has a single `features` dict per case. A "predictor features" / "examination features" split (or a separate `examination_features` field) is the structural fix.
- **Position paper §4 (silence-manufacture).** The methodology surfaces silenced cases via multiple mechanisms; attribution to a single mechanism in the frame's interpretive language is overreach. The structural-recovery claim survives; the mechanism-naming should be plural.
