# Step 2 design note: replace P-vs-G with a conformance audit (proposal, not frozen)

**Status:** owner's design decision, open to a blind adversary and a widener before any pre-registration. No data
has been looked at for anything below.

## Why P vs G is close to uninformative on LendingClub data

The closing note's P-vs-G experiment compiles the written policy into the model space and compares its Rashomon set
with a generic monotone G fixed in advance. Step 1 (`runs/lc_policy/2026-10-26-step1-result-note.md`) found the
quantified DTI rule enforced *exactly*: 0.0% of accepted loans at or above the cap in every regime. A decision model
trained on accepts and declines will learn an exactly enforced threshold from data, so G recovers it and P ≈ G is
close to guaranteed. LendingClub's unquantified rules ("acceptable" DTI including mortgage; the April and October
2016 and January 2017 tightenings) give P nothing to compile. On this substrate, the kill condition (P ≈ G) can't tell
"the written policy adds nothing" from "the written policy is already in the data". This is the same flaw as a gate
that documented behavior satisfies.

## Proposal: conformance audit of every quantitative claim in the filings

The written policy's value in step 1 was a checkable commitment, not a better model. That is the paper's thesis
(contemporaneous written records as accountability artifacts), so step 2 tests it across everything the record claims:

1. **Threshold conformance**, accepted file, each dated version (source: `docs/research/lc-policy/`):
   - FICO floor 640 → 660 (2008-11-25), via `fico_range_low`;
   - the inquiry caps (10 → 8 → ≤3 below 740 → 6 → 5 excluding mortgage and auto), via `inq_last_6mths`;
   - credit history 12 → 36 months, via `earliest_cr_line` against `issue_d`;
   - revolving utilization 100% → 98% (2012), via `revol_util`;
   - the DTI caps, already done in step 1.
2. **Volume-claim conformance**: the FY2016 10-K says the April, June and October 2016 actions "eliminated
   approximately 11% of total loan volume on an annualized basis", and January 2017 "approximately 5%". These are
   checkable against accepts plus declines, even though no threshold is published.
3. **Each check is a positive control except where the record is vague.** The construct check from step 1 (share of
   loans violating the written rule, per regime) carries over, with tolerance for the documented exceptions only.

**Owner's prior, to be registered properly in the pre-reg:** most thresholds conform. The likeliest divergences are the
inquiry rules (the "or recently opened accounts" clause; `inq_last_6mths` may count inquiries differently) and the
volume claims (their annualized baseline is undefined).

## Questions for the adversary and the widener

- Is the P-vs-G objection right, or is there a version of P vs G that this data *can* decide?
- Does a conformance audit say anything beyond "a regulated lender followed its prospectus"? Who would care, and what
  result would surprise them?
- What did the closing note's P-vs-G framing capture that a conformance audit loses?
