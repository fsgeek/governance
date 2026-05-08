# Adversarial Robustness and Examinability — Design Memo

**Date:** 2026-05-08
**Status:** Working design memo. Companion to `2026-05-08-indeterminacy-operationalization-memo.md`.
**Scope:** The structural tension between public examinability and adversarial adaptation, and the methodology-level property that resolves it: at least one detection channel must be grounded in *retrospective surprise* rather than prospective regularity. Carries implications for the species priority ordering, the position paper's structural argument, and the methodology's claim to generalize beyond credit underwriting.

---

## 1. The tension

Examinable governance — the kind the methodology is designed to support — requires the criteria for examination to be public. An external examiner (regulator, auditor, governance officer) must know *what* to look for to interrogate a case responsibly. But public criteria are reverse-engineerable: an adversary who knows what triggers examination can adapt the inputs to evade detection.

This is the core failure mode of any system that pairs transparency with detection. It is not specific to credit underwriting:

- **Tax audits.** Published red flags teach evaders which behaviors to avoid.
- **Anti-money-laundering.** The $10K SAR-reporting threshold spawned an entire structuring industry.
- **Peer-review forensics.** Each new manipulation-detection paper teaches the next round of manipulators what fingerprints to suppress.
- **LLM epistemic observability** (entropy-attention work in progress in the parallel project): publishing high-entropy regions teaches the model (or its operators) to suppress entropy in scrutinized areas, hiding rather than resolving the uncertainty.

The methodology in this repository faces this tension directly. The 2026-05-08 indeterminacy memo argued for I as an externally examinable per-case channel — exactly the property that creates the adversarial vulnerability. If our methodology specifies that round-number incomes get flagged, the very act of publishing the methodology teaches applicants to avoid round-number reporting.

The naive responses to this tension are both wrong:

- **"Don't publish the criteria"** violates the examinability claim that's central to the methodology.
- **"Accept that publication kills the methodology"** abandons the project.

The correct response is structural: design the species mix so that *at least one channel survives publication*. This memo argues that property is achievable, and identifies which species architecture provides it.

## 2. Species ranked by adversarial fragility

The four species defined in the indeterminacy memo inherit different levels of adversarial protection from how they are constructed.

| Species | Gameable how | Insider info needed |
|---|---|---|
| Ioannidis: round-numbers | Trivially — report $51,247.83 instead of $50,000 | None |
| Ioannidis: threshold-hugging | Trivially — avoid DTI exactly at policy cutoffs | None (current data suggests not actively gamed) |
| Multivariate-coherence | Report features in high-density regions of the joint distribution | Full corpus joint distribution |
| Local-density | Report features near the leaf centroid for every Rashomon member | Leaf structure of every model in R(ε) |
| **Retrospective-trajectory** | **Knowing which prospectively-unused features will turn out to predict default for borrowers like the adversary** | **The future** |

The Ioannidis tests, designed to detect *fingerprints of suspicious provenance*, are the most adversarially fragile by construction — their detection logic is essentially "the data looks too clean," and the response "make the data look less clean" is straightforward. Local-density and multivariate-coherence sit in the middle: gameable in principle but only with substantial insider information that would defeat most adversaries. Retrospective-trajectory occupies a structurally different position.

## 3. Why retrospective channels are structurally protected

Retrospective-trajectory I propagates *post-origination outcome surprise* back into prospective indeterminacy on similar profiles. To game it, an adversary would need to know, at application time, which features will turn out to predict default for borrowers like them — features that, by construction, aren't being weighted in the current predictor. They can't know this; the information doesn't yet exist at the moment of action.

What the adversary *can* respond to is yesterday's retrospective findings — features that the system has already incorporated based on past observed surprise. But by the time those findings are public, the methodology has already updated. The arms race favors the system in a specific quantifiable way:

- At time T, the system observes outcomes from cohort T − K (where K = loan term + observation window).
- An adversary applying at time T can only adapt against the system's *published* state as of T − 1, which already incorporates observations from cohort T − K − 1.
- The system is therefore *one observation cycle ahead* of any adversary who observes only the published criteria.

This gives retrospective channels a structural property no prospective channel can have: **signal that survives publication.** Adversaries can adapt to it, but only after the fact, at which point the system has moved on.

## 4. Signal-purpose modulates the stakes

The adversarial concern's severity depends on what the signal feeds. Three cases, with different stake profiles:

1. **Signal feeds the predictor.** I is used as a feature in the credit-decision model. Adversarial adaptation directly improves outcomes for the adversary. **High stakes.**
2. **Signal feeds an examination process.** A regulator or auditor uses I to flag cases for review. Adversarial adaptation reduces examination but doesn't directly change credit outcomes. **Moderate stakes** (governance integrity erodes, individual outcomes do not shift sharply).
3. **Signal feeds applicant-side feedback.** Applicant sees their own I and adapts. The methodology becomes a teaching tool for evasion. **Stake severity depends on whether the species' signal correlates with the underlying construct of interest** (credit risk, in this case).

Existing data from the 2026-05-08 run already informs this:

- **Round-number tiers do not predict default differently from baseline** (13.66% for multiples of 25K vs 14.57% overall, monotonic but small). This means Ioannidis-round-number *evasion* has indirect consequences only — fewer cases get flagged for examination — but not direct ones, since the signal isn't credit-risk-correlated. The species is fragile under publication, but the consequences of its fragility are governance-side, not outcome-side.
- **Threshold-hugging cases default at 17.98% vs 14.57% baseline (n=89, suggestive).** If this effect survives a larger sample, threshold-hugging *is* a credit-risk-correlated signal, and adversarial evasion has direct stakes.

The methodology spec should distinguish, per species, what failure mode adversarial adaptation produces. Not all species fail equally; the position paper should not present them as if they do.

## 5. Generalization across domains

The pattern — *examinable governance survives publication of its criteria specifically when at least one detection channel is grounded in retrospective surprise rather than prospective regularity* — appears across multiple public-examination systems that have survived long-term:

- **Tax audits.** IRS publishes general criteria but keeps specific risk models private. The risk models continuously incorporate prior audits where unexpected violations were found — retrospective surprise. New manipulation patterns get added only after they're detected, but they do get added.
- **AML/SAR.** Reporting thresholds are public; FinCEN-published typology updates incorporate prior reported activity. Each new structuring pattern observed feeds the next round of detection.
- **Peer-review forensics.** Simonsohn's p-curve, Ioannidis' "too perfect" results, GRIM and SPRITE forensics — each generation of detection methodology is grounded in *patterns observed in past detected manipulations* that the next generation of manipulators will adapt around.
- **LLM epistemic observability.** The analogous structural move is a retrospective-attention signal — flagging regions of past responses that turned out to be wrong despite low entropy at generation time. Errors that "shouldn't have happened" given the prospective signal become the next round's attention focus. Identical structural form to retrospective-trajectory I in credit.

In each case the system survives publication of its criteria because the *retrospective component* depends on data the adversary cannot anticipate at the moment of action.

## 6. Implications

**For the methodology spec.** The I-vector should always include at least one species grounded in retrospective surprise, even if its individual signal is weaker than a fragile species's. The vector design naturally supports this — the four species have different adversarial-robustness profiles, and the retrospective species can carry the structural-protection load while the others contribute interpretability and breadth. The retrospective species was already named load-bearing in the indeterminacy memo for the Olorin deployment story; this memo gives it a second, independent load-bearing role. **Two independent reasons for retrospective-trajectory being core, not Phase 2.**

**For the position paper.** A structural section making this argument explicit is worth carrying. Working sentence:

> Examinability and adversarial robustness are jointly achievable specifically when the examination signal includes a retrospective channel that the examined party cannot anticipate at the moment of action.

This sentence does work in the credit-underwriting context, the LLM epistemic-observability context, and the broader public-examination-systems literature. The methodology makes the same structural claim across domains, which strengthens the position-paper argument considerably — the methodology is not "a credit-scoring tool dressed up as governance," it's an *instance of a generalizable governance pattern* with a clean structural defense.

**For position paper §4 (silence-manufacture).** Adversarial adaptation is itself a form of silence-manufacture: adapting inputs to occupy the rhetorical position of "ordinary case" so examination doesn't fire. The structural-defense argument here is silence-manufacture's natural counter — retrospective channels detect what the silence was hiding, after the fact. Worth integrating into §4's structure rather than treating as a separate concern.

**For prioritization.** Multivariate-coherence and Ioannidis are still useful (interpretable, cheap, surface real population-level patterns), but the retrospective species is structurally load-bearing. Implementation order in the indeterminacy memo's Layer 2 work should reflect this: retrospective-trajectory ahead of multivariate-coherence in the next round, with the proviso that retrospective requires either real bank lifecycle data (production) or a within-LC vintage-simulation proxy (evaluation).

## 7. Explicit non-commitments

The following are claims this memo deliberately does *not* make:

- **The species adversarial-robustness ordering** is a first analysis, not a definitive ranking. Empirical evidence may complicate it — multivariate-coherence may turn out harder to game than expected, threshold-hugging may turn out easier in production.
- **The "one observation cycle ahead" argument** assumes adversaries observe only published criteria, not insider information. Insider-equipped adversaries (rogue underwriters, leaked risk models) have different threat profiles not covered here.
- **The generalization across domains** is suggestive, not load-bearing for the methodology's primary claim. The position paper can lean on it lightly without requiring it to be airtight; the credit-underwriting case stands on its own.
- **"At least one retrospective channel"** is a sufficiency claim, not a necessity claim about *which* retrospective channel. The retrospective-trajectory species defined in the indeterminacy memo is one operationalization; others may exist (vintage-aware drift signals, ensemble-of-foils with rotating membership, etc.).
- **The fragile species are not dismissed.** They do real work at the population level, surface interpretable findings (Ioannidis-round-number evidence is unambiguous in our data), and cost little to compute. They just shouldn't be load-bearing alone.

---

## Connection to other working documents

- **2026-05-07 wedge design spec.** This memo doesn't change the spec, but it adds an adversarial-robustness lens the spec's iteration-2 section should incorporate.
- **2026-05-08 indeterminacy operationalization memo.** Companion piece. The species architecture defined there gains a structural-defense argument here. The two memos together constitute the methodology's design rationale: *what* the species are (memo 1) and *why the architecture survives publication* (this memo).
- **Position paper §4 (silence-manufacture).** Adversarial adaptation is silence-manufacture under examination pressure. The retrospective-channel argument is the structural counter. Worth integrating into §4 rather than appending as a §6 or §7.
