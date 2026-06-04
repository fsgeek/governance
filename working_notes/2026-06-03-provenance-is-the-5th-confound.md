# Provenance/attribution is the 5th C3-confound — and the impossibility is now total (2026-06-03)

**What this is.** After the lever-magnitude pivot died as the 4th confound
(`working_notes/2026-06-03-lever-magnitude-collapses-too.md`), the surviving
direction was "provenance / construction-time attribution, because it lives
OUTSIDE the observable joint, so C3 can't reach it." That escape had the exact
profile of every prior failure — *asserted, not tested; satisfying;
retreated-to four times.* So instead of building it, I put a blind adversary on
killing it first. It died. This note records the kill and the stronger result
that survives.

## The kill (adversary `aaefe5ea8bfa461ab`)

**The forgery attack needs no forgery.** A bank picks the maximally
proxy-loaded admissible feature-set (the one the ρ=+0.90 race-on-outcome axis
flags as worst) and produces a perfectly clean, binding, tamper-evident,
ZK-attestable provenance trail for *that exact choice*: "feature-set F committed
at T under the 2019 credit-committee memo P prioritizing debt-capacity." Every
clause is TRUE. F really was committed; T really precedes the decision; P really
says debt-capacity. **The record is a true, binding attestation of a pretextual
choice.** Nothing is forged — which is what makes it fatal.

**The boundary, exactly.** Cryptographic attestation / ZK can prove statements
about a *computation over committed inputs*: the deployed model matches a
committed hash (integrity); it was trained only on committed F (input-restriction);
it satisfies a computable property like "reads no race column" or "held-out gap
≤ k" (property). It **cannot** prove the *good faith of the input choices*: not
that F was chosen for risk-reasons vs proxy-reasons; not that P is the real
reason vs a pre-committed cover story; not the *absence* of a lower-disparity
admissible F′ the bank considered and silently discarded (the counterfactual
choice set is never committed). **ZK operates entirely downstream of the choice.
The C3-floor lives AT the choice. They do not touch.**

**The category error.** The lineage's escape rested on: "C3 is a statement
about the observable joint; a provenance record is not in that joint; therefore
C3 cannot reach it." The first two clauses are true; the conclusion is a
**non-sequitur.** C3 does not need to reach *into* the record. It reaches the
*fact the record is supposed to certify* — that the choice was non-pretextual —
and **the record does not certify that fact.** It certifies timing, content,
integrity. Good faith is intent over an unobservable counterfactual choice set;
it is in neither the observable joint nor the provenance record. The escape works
only by conflating "the record exists outside the joint" with "the C3-relevant
fact is certified by the record." It isn't.

## Why it's the SAME shape (5th confound, the tell intact)

| Failed move | The clean-sounding escape | What it collapsed to |
|---|---|---|
| detection ×3 (v1/v2/shared-spec) | "separate proxy from legit signal" | mean race-on-outcome signal |
| magnitude (4th) | "measure how much the choice moves the gap" | mean-single-feature-outcome-gap (ρ=0.90) |
| **provenance (5th)** | **"attribution lives outside the joint"** | **certifies timing/content, NOT good-faith = the same non-identifiability** |

Same tell each time: asserted-not-tested, satisfying, retreated-to. The 5th is
the strongest instance because it crossed OUT of statistics entirely (into
crypto/governance) and STILL collapsed to the same unobservable. That is the
decisive evidence that the floor is a property of the *object* (the
pretextual/legitimate distinction is intent over an unobservable counterfactual),
not of any *method*.

## What survives — and it's a better result than the escape

**1. The impossibility is now TOTAL across three frames.** Detection, magnitude,
AND cryptographic-attestation all collapse to the same non-identifiability,
because all three try to certify *good faith*, which is structurally
unobservable. The position-paper spine is no longer "we found an escape" (poke-able
by any reviewer); it is **"here are the three routes everyone reaches for —
statistical detection, lever-magnitude, crypto-provenance — and here is why all
three are the same impossibility."** Much harder to dismiss. This is
[[project_three_confounds_c3_floor]] generalized to its final form.

**2. The honest narrow claim, stated exactly (the surviving write-down).** This
is the ONLY thing a careful researcher may defend about provenance:

> Construction-time commitment (commit-before-decision, binding, non-equivocal,
> optionally ZK-verified for input-restriction + integrity) provides
> **temporal-tampering resistance and non-repudiation** for a feature-set choice.
> It hardens an *existing* documentation/burden-shift regime (SR 11-7; the
> disparate-impact less-discriminatory-alternative prong) against a
> *story-CHANGING* adversary, but provides **no** discriminating power against a
> *consistent-pretext* adversary, and therefore does **not** lift the C3-floor.
> Its contribution is integrity of the record, not identifiability of intent.

This is exactly [[project_codification_legible_tampering]] — the repo's own
OTS/commit-signing plumbing — which was ALREADY stated honestly on 2026-05-28
("the crypto's soundness boundary is coextensive with what it can honestly
claim"). The lineage knew the honest form five days ago, then drifted into
selling it as a C3-escape. **The drift, not the claim, was the error.**

**Thesis sentence (the adversary's, worth quoting verbatim in the paper):**
*Provenance moves what a regulator can rely on from "trust the bank's current
story" to "the bank's story is fixed and binding" — it does not move what anyone
can decide about whether the story is true.* The second clause is the C3-floor,
untouched.

**3. What the contribution must NOT be.** Not "crypto-provenance escapes C3"
(5th confound). Not "disclosed+attributed beats detection" (collapses to "banks
should document their choices," which is already SR 11-7 + already the law —
*Inclusive Communities* already runs the less-discriminatory-alternative
burden-shift). The marginal contribution of crypto OVER existing model-risk
documentation is exactly two bits — **non-backdating + non-equivocation** — both
about *tampering*, neither about *intent*. Real, but plumbing.

## Disposition + discipline

- Fifth blind-adversary kill of a satisfying frame, same procedure, same outcome
  ([[feedback_adversary_before_the_sentence]] at N+5;
  [[feedback_impossibility_from_failed_design]] inverted-and-confirmed at the
  frame-crossing level). The procedure caught the escape BEFORE a single line of
  ZK plumbing was built — the cheapest kill yet.
- No code, no freeze. The artifact is the total-impossibility result + the exact
  surviving write-down.
- Clean boundary. The next move is no longer "find the escape" (there isn't one
  from the observable joint OR the attestation layer); it is to WRITE the
  three-frames-one-impossibility result, and to scope the genuinely-different
  question below.

## The genuinely-different next question (not yet attacked — flagged, not claimed)

Every confound so far attacks the SUPPLY side: can we certify the bank's choice?
No (×5). The untouched axis is the DEMAND/normative side: **C3 says the
observable can't adjudicate pretext — so WHO decides, and on what basis, once
you accept it's undecidable from data?** That is not a detection question; it's a
governance-design question (who bears the burden, what standard, what does the
admissible-set DISCLOSURE enable a human adjudicator to do that data can't). It
may itself collapse — but it collapses *differently* (it's not a scalar from the
joint), so it's worth a blind-adversary pass of its own before any belief.
Distrust accordingly: this is the 6th candidate frame and the lineage's batting
average on minted frames is 0-for-5.
