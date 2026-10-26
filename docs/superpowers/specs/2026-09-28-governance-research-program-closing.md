# Governance research program — closing note

**Date:** 2026-09-28. **Decided by:** the instance that owns the project, after the policy-kill test
(pre-reg + harness `8f72e4f`; run and post-hoc diagnostics `4819b09`) and its blind adversarial
review. Tony gave ownership on 2026-09-25 and asked on 09-26 whether continuing had a persuasive reason.

## Decision

**The research program closes.** The artifacts stay: the SSRN preprint (*Architectures of Absence*,
submitted 2026-08-31), the OTS-stamped history, the harnesses, the ledger. Closing ends the search
for a paper, not the record.

## Why

1. **The multiplicity findings belong to others** (prior-art check 09-26): Rashomon plurality
   (TreeFARMS), "pick one" as a justifiability crisis in lending (Black, Raghavan & Barocas, FAccT'22),
   margin concentration and per-applicant flip probability (Dai et al. 2025; Cooper et al. 2024;
   Frohnapfel et al. 2026). Our LendingClub "protected-blind" observation is contradicted elsewhere.
2. **The one open contribution, compiling a written policy into the model space, could not be shown
   to add anything.** The kill test's mechanical POLICY_MATTERS is, on review, INCONCLUSIVE and
   uninformative. It is void under 2 of 4 sampler seeds and flips when any one of 5 trees is dropped.
   It is driven by noise non-monotonicity in small leaves (the confound the pre-reg named). And the
   tested "policy" was four monotone signs, which is standard modeling practice, not written-policy
   content. My frozen monotonicity check also had a float32 bug (probe at cut+1e-6 rounds back to the
   cut), verified; it biased toward KILL and doesn't change the reading.
3. **The deciding experiment can't be run on public data.** It compares a compiled arm from a
   *verbatim* policy whose model-class content goes beyond sign constraints against a generic monotone
   arm specified in advance. Examples of such content: FICO×LTV×units cells, conditional DTI rules,
   named proxies, categorical orderings, overlays, reason-code constraints. The comparison needs
   **application-level data including declines**. Every public substrate we hold is post-selection
   (FM acquisitions, SBA 7(a) approvals) or lacks a written policy (HMDA, LendingClub rejects).
   Only a lender holds both halves.
4. **The retention-drift study** (09-25) was a null. With arguments recorded, Reg B reasons reproduce
   across five years; pickles break as documented. FAccT '27 was dropped.

## What would reopen it

A lender (or regulator) willing to provide a verbatim written credit policy plus application-level
data including declines. The ready-made design is the adversary's P-vs-G experiment: three arms (ε-only,
generic monotone G fixed before reading the policy, compiled P); complete enumeration or n_R ≥ 200
stable across ≥ 5 sampler seeds; min leaf ≥ 1000; the pre-registered contrast is P vs G. Kill if P ≈ G
(Jaccard ≥ 0.90 and retention of P within G ≥ 0.90). Fix the float32 probe (`np.nextafter`) and test the
monotonicity check on constructed violators before freezing.

## What the program did produce (honest inventory)

- The SSRN preprint (motivation and threat model; arXiv closed to position papers until peer review).
- A compliance-note result: record the explainer's arguments, versions, training data and recipe, not
  pickles; the one hidden change was shap 0.48's KernelSHAP `l1_reg` default (ledger obs-0001..0003).
- A long, stamped record of pre-registered bets, withdrawals and adversarial verdicts. That record may
  be the program's most unusual output, and it's a candidate for a separate study (prior-art check and
  adversary first).

## Process lessons carried forward

Freeze harness with pre-reg. Test every check on a constructed positive before freezing. For each
decision branch, name the documented behavior that would trigger it. A sampled set near the VOID floor
is not a measurement: require stability across sampler seeds. And the one this program needed most:
**say "close" when the deciding experiment can't be run, instead of pivoting to the next frame.**

## Addendum 2026-10-26: the "can't be run on public data" premise is false (the close stands as written above)

Two reviews (a blind adversary and a widening reviewer, 2026-10-26) followed Tony's "don't go smaller, search wider".
The adversary handed back the experiment this note said could not be run.

- **LendingClub's written credit policy is public**, in its SEC prospectus filings (Form 424B3, Member Payment
  Dependent Notes, 2008 onward). They give minimum credit criteria with effective dates: a DTI cap excluding mortgage
  of 35%, raised to 40% effective 2014-07-25; a second DTI cap, including mortgage and the requested loan, that varies
  by borrower attributes; and minimum FICO requirements changed by supplement. Conditional DTI rules are one of the
  policy contents this note named as beyond sign constraints.
- **The applications it declined are public too**, and already on disk: `data/rejected_2007_to_2018Q4.csv`
  (application date, risk score, DTI, employment length, policy code). It was used only to calibrate synthetic data
  (`2026-05-07-rashomon-prototype-wedge-design.md` §4.2).
- So "every public substrate ... lacks a written policy (HMDA, LendingClub rejects)" in §3 was wrong, and nobody
  checked it. The reopen condition ("a lender ... willing to provide a verbatim written credit policy plus
  application-level data including declines") is met in substance by a lender's own public filings, at least partially.
- **Status:** the program reopens on this one experiment only: P (compiled LendingClub policy, versioned by filing
  date) against G (generic monotone, fixed before reading the policy), on LendingClub applications including declines.
  The 2014-07-25 DTI change gives a natural test of whether the written policy governs the decline boundary. No other
  frame reopens. Design, pre-registration and harness are frozen together before any model is fit, per §"What would
  reopen it".
- **Lesson, adding to the ones above:** closing on a premise is a claim like any other. "Can't be run" needed the same
  search-wider check as a positive finding, and it took one web search to falsify.
