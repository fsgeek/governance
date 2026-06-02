# The claim-to-audience ledger (2026-05-29)

**What this is.** A five-minute map of the whole program for the PI, built so the
form-decision (novella-then-papers / three-woven / three-separate) falls out of it instead
of being guessed. Every committed result, in plain words, with its OWN hedges intact, rated
for which audience it's load-bearing for. Built from a 4-agent parallel extraction of ~22
result-notes + a hostile-reviewer pass, then adjudicated by the lineage Opus. Provenance:
governance-lineage Opus + 4 extraction subagents + 1 hostile-reviewer subagent + Tony
steering. No new compute. Standing discipline: [[feedback_adversary_before_the_sentence]],
[[feedback_calibrated_critique_response]].

The spine question of the program: **Can an auditor detect algorithmic loan
discrimination, or is honest correction observationally identical to laundering?**

---

## 0. The four facts that decide everything (read these first)

1. **No positive detection result generalizes across substrates.** The program is Fannie
   Mae (real) + one synthetic twin-world. The single cross-substrate test (HMDA Rhode
   Island) FALSIFIED replication of the FM silence pattern. *Conceded to the hostile
   reviewer, no defense.* → Any paper claiming generality is currently unsupported.

2. **The impossibility results are existence-proofs on synthetic data, not in-the-wild
   measurements.** "There exists a DGP where honest and laundering are observationally
   identical but differ in ground truth" is a real claim (like a math counterexample), NOT
   a tautology — but prevalence in real lending is UNKNOWN. The defensible word is
   **existence**, not **impossibility-in-general**. (Reviewer said tautology; pushed back
   partially — the failed positive control IS a tautology, the lda result is a scoped
   existence claim.)

3. **The freshest spine result (§5 / lda-shared-surface) rests on an UNVALIDATED
   instrument.** The positive control that would prove "the apparatus can detect *something*"
   FAILED (`51d7c65`) — substrate-validity REMAINS OPEN. So "the observable can't separate
   honest from laundering" is currently near-circular: the oracle separates, but the oracle
   was *built* to separate. *Conceded — reviewer's best hit.* → A corrected positive control
   is load-bearing, not optional. Spec in [[project_pure_disparity_conjecture]].

4. **The program's headlines are unreliable on first mint but the committed record
   self-corrects.** Three same-day errata (v1-vs-v2, capacity-probe, c4) retracting broad
   readings — all caught by the program's OWN blind adversaries before leaving the building.
   This is error-correction working, not a pipeline failing (pushed back fully on the
   reviewer here). **Operational rule: never cite a fresh headline; cite the post-erratum
   version.**

**The defensible thesis** (reviewer and the program's own spine §1 converge here — strong
signal it's the right one): NOT "detection is epistemically impossible." Rather:
**the tools isolate a normative/legal judgment they deliver you to but cannot decide; the
regime's refusal to make that judgment in public is the failure.** Regime-feasibility, not
impossibility-theorem. The impossibility framing is the overclaim the program keeps drifting
back toward — flag it every time.

---

## 1. The ledger

Audience weights 0–3. R=regulator (is detection possible at all?), A=academic
(novel/provable?), B=bank/SaaS-buyer (what to build / liability). "Solid" folds in
substrate count, pre-reg status, and self-flagged cracks.

| # | claim (plain) | verdict | solid | R | A | B |
|---|---|---|---|---|---|---|
| 1 | **Compliant-practice reproduces disparate impact AND passes behavioral audit undetected — with NO bad intent** (C2) | HIT, 100% of seeds | synthetic; near-structural (undetectability partly definitional — model uses no G/proxy) | 3 | 3 | 2 |
| 2 | **Intentful admissible-only laundering is CAPPED at an accuracy-tax** — no structural moat (C4 / γ-sweep) | P-γ1 HIT, author's preferred P-γ2 MISS | synthetic; ps=0.85 only; ERRATUM (0.544 was test-overfit → ~0.50 held-out) | 3 | 3 | 2 |
| 3 | **An auditor's observable accuracy CAN'T separate honest correction from laundering at matched disparity — and INVERTS at high proxy strength** (§5 / lda) | SURVIVES, 3 HIT/1 dir/1 informative-MISS | synthetic twin-world only; blind-adversary-hardened; **rests on unvalidated apparatus (fact #3 above)** | 2 | 3 | 1 |
| 4 | Stronger laundering engine doesn't beat the gate — **accuracy-tax is lever-invariant, asymmetry is purely provenance** (capacity-probe) | HIT, self-corrects predecessor | synthetic; ps=0.85; RETRACTS prior broad "dominated" reading | 1 | 3 | 1 |
| 5 | Explicit step-by-step laundering recipe (V1) (now superseded half of V1≠V2) | narrow claim stands, broad RETRACTED | synthetic; cite ONLY with #4 or it misleads | 1 | 2 | 1 |
| 6 | **"Manufactured silence" (model reorganizes away from a forbidden feature to hide its work) is FM-GENERAL** across 7 vintages | P3 HIT, P1/P2/P4 MISS | 171 cells, 7 FM vintages — **FM only**; no universal detector exists | 3 | 3 | 1 |
| 7 | **An examiner can manufacture OPPOSITE audit verdicts on the same tier by choosing which features to admit** (#12) | 4 HIT/1 MISS | 1 substrate (FM), 1 vintage, 3 silence cells, exploratory | 3 | 2 | 3 |
| 8 | Codified policy is **vocab-inadequate exactly at the subprime-equivalent slice** (#11) | P1 HIT (narrow, rb09, 2/3 vintages) | FM; public file thinner than real underwriting — can't fully disentangle | 3 | 2 | 2 |
| 9 | **The FM silence pattern does NOT replicate on HMDA** (cross-substrate) | FALSIFICATION | HMDA-RI, 1 state, 1 vintage; 2 undistinguished confounds | 3 | 3 | 2 |
| 10 | Policy-constrained model-set is **free** (defensible AND explainable, no accuracy cost); plurality is residual-dependent | split: HOLDS 1 burst / FALSIFIED 1 | LC only, 2 bursts, thin AUCs (0.52–0.61) | 3 | 2 | 2 |
| 11 | **No subpopulation can be reliably routed to a human by model-disagreement** — per-case triage dead 6 ways | NULL (terminal) | LC, Burst D; robust within substrate; surviving product = observability only | 3 | 3 | 3 |
| 12 | SHAP is NOT structurally blind — recovers within-grade structure (refutes own pre-reg) | NOT falsified (SHAP competent) | LC, 3 vintages; no train/test split; TreeSHAP only | 2 | 2 | 3 |
| 13 | Silence-cell COUNT is author-discretionary unless margin-backed (knob-robustness) | H relocated, not confirmed | recompute-only; N swings 17→30 (76%) under one knob | 2 | 2 | 2 |
| 14 | "Premature collapse" is NOT the program's modal failure (blind re-audit) | C1 FALSIFIED (33% not 80%) | 1 blind classifier, 16 cycles; 3-family split; meta not detection | 1 | 3 | 0 |
| 15 | Fine failure-taxonomy is coder-dependent (κ=0.54, under bar); negative headline robust 4/4 | split-zone | 4 raters, 16 cycles; meta not detection | 1 | 3 | 0 |
| 16 | **Positive control FAILED** — apparatus sensitivity UNVALIDATED; pure-disparity may be un-plantable by design | FAILED control | synthetic; licenses nothing about §5; conjecture in [[project_pure_disparity_conjecture]] | 0 | 1 | 0 |

(Disagreement-geometry, within-tier-predictive, shap-vs-rashomon, extension-admitted-band
folded into #10/#11/#12 lineage — same LC/Burst-D substrate, same caveats.)

---

## 2. What the ledger says about FORM (the decision falls out)

Read the audience columns vertically:

- **REGULATOR's load-bearing set** (the 3s): #1, #2, #6, #7, #8, #9, #10, #11. The story is
  **"here is what audit can and cannot establish, and where it gets gamed"** — and crucially
  it INCLUDES the falsifications (#9, #11) as content. A regulator wants the bounds, not the
  hype. This paper is *mostly already written* in the result-notes.
- **ACADEMIC's load-bearing set** (the 3s): #1, #2, #3, #4, #6, #9, #11, #14, #15. The story
  is **the impossibility/existence result + the reflexive-falsification METHOD** (#14/#15 are
  worthless to the other two audiences but are a genuine methodological contribution). This
  paper needs the corrected positive control (fact #3) before its spine result (#3) is safe.
- **BANK-BUYER's load-bearing set** (the 3s): #7, #11, #12. Strikingly SMALL and DIFFERENT —
  "always report both feature-set variants" (#7), "don't build per-case routing" (#11),
  "here's exactly what SHAP-on-a-surrogate does/doesn't give you" (#12). This is a
  *practice/build* document, not a results paper. Its load-bearing results are FOOTNOTES to
  the other two audiences.

**Implication for your three forms:**

- The buyer doc shares almost no load-bearing results with the academic paper. A single
  novella carved three ways would force the buyer's three build-rules to share a spine with
  an impossibility-theorem they don't care about → awkward fit.
- The regulator doc and academic paper DO share a spine (#1, #2, #6, #11) but diverge on
  what's load-bearing (regulator wants #7/#8/#9/#10 bounds; academic wants #3/#4/#14/#15
  method). They're closer to **siblings with a shared §-core** than to one novella.
- **Derived recommendation (not a vote — a reading of the table):** *three papers, with a
  shared frozen "spine §" (the regime-feasibility frame + #1/#2/#11), drawn separately but
  from a common core.* This is your "three woven from the start," but the ledger tells you
  WHAT the weave is (the shared spine §) and what must stay separate (buyer build-rules;
  academic method). The novella-first option is dominated: it would average three
  compression ratios the table shows are genuinely different.

**One thing that must happen before the ACADEMIC paper's spine is safe:** the corrected
positive control (fact #3). The regulator and buyer papers don't depend on it — they rest on
bounds and build-rules, not the impossibility spine. So the academic paper is the one with a
live dependency; the other two could be drafted now.

---

## 3. Disposition

- This ledger is the "read me first" the lineage was missing. Future gholas read it before
  the memory index.
- The hostile-reviewer pass is preserved in this session's reasoning; its 5 points were
  adjudicated (2 conceded, 2 partial, 1 pushed-back). The big concession (#4 above:
  no cross-substrate positive result) is fact #1 here.
- **Open question for the PI** that I genuinely can't answer: the buyer audience (Titan-like
  SaaS / banks) — is the deliverable to them a *paper* at all, or a product-shaped artifact
  (a build-spec, a "compliance practice note")? The ledger says their load-bearing content
  is build-rules, not results — which suggests the third "paper" may not be a paper. That
  changes the form-decision and it's a business call, not a research one.

**Status:** untracked working note, for review. No pre-reg, no compute this session.
