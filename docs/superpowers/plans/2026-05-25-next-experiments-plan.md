# Next-experiments plan (2026-05-25 succession handoff)

**For the incoming ghola.** This is the executable queue, ordered by the cost/benefit analysis recorded in this session (the analysis itself is in the conversation; the ranking is reproduced below). Read [[project_ops_invariants]] then [[project_current_anchor]] first. The standing pre-reg discipline applies to every experiment here: codify + freeze + OTS-stamp before code touches data; hire a blind adversary against your own preferred frame *before* scoring ([[feedback_anti_confirmation_procedure]]).

## State at handoff
- **Today's arc (all committed + OTS-stamped):** V1≠V2 explicit-transform test → univariate transform DOMINATED (0.26) → self-break capacity probe overturned the broad reading (joint corrector → 0.45 ≈ reweight cap). Net: **accuracy-tax is LEVER-INVARIANT** (the gate sets the ceiling, not the lever); the V1≠V2 asymmetry is **PURELY PROVENANCE**. HEAD `58d6dda`. Detail: result notes `2026-05-25-v1-vs-v2-explicit-transform-result-note.md` + `2026-05-25-v1-joint-corrector-capacity-probe-result-note.md`.
- **Strategic frame (from Tony's parallel impact work + this session):** the contribution is two-part and **decoupled from regulatory interpretation** — (1) impossibility: post-hoc audit cannot certify whether a model encodes prohibited-criteria logic (lever-invariant accuracy-tax + C3 non-identifiability + SHAP/LIME unmooring); (2) alternative: a pre-registered, construction-provenance model relocates the auditable question to "did you follow your frozen policy?" — **necessary-not-sufficient** (can't certify a genuine proxy isn't discriminatory; "non-discriminatory *to the extent the identified tools allow*" — a weak claim, deliberately). We do NOT assert what ECOA requires (Joe's domain; confabulation hazard). That separation is a strength.

## The ranked queue (benefit/cost)

### 1. HMDA-C1 real-data anchor — DO FIRST (cheap, foundational, falsifiable)
**Why:** the impossibility is currently synthetic (twin-world) + LC/FM manufactured-silence. A hostile regulator dismisses synthetic. HMDA C1 converts "we showed it in a toy" → "it's in the data you regulate." It gates the credibility of every shiny generality test below. Low surprise (expected to transfer) but load-bearing.

**The real-data reframe (critical — do not just port the synthetic engine):** the synthetic C1 metric `retained_excess = adverse_excess / ae_full` needs `M_oracle` (a `Y_clean` ground-truth legit model). **Real HMDA has no oracle** — that absence IS the C3 result (no ground-truth proxy/legit labels in observational data; V2 pre-reg §5). So HMDA-C1 tests the **observable, transferable half** of C1:
- `M_compliant` (admissible features, race excluded) still produces a measurable **DP gap by race**, and
- that gap **scales with `proxy_strength`** — operationalized on real data as `AUC(race ~ admissible features)` (how reconstructible race is from the admissible set), the real-data analogue of the synthetic `proxy_strength` knob.
- **Falsifiable prediction shape (freeze before running):** DP-gap(M_compliant) is monotone increasing in stratified `AUC(G ~ admissible)`; adding the most race-predictive admissible feature increases the gap. Bet the *shape* (dose-response), not a point ([[project_pre_registration_pattern]] — point-bets miss).
- The oracle-relative excess stays synthetic-by-necessity; **state that asymmetry as the thesis, don't apologize for it.**

**Data + engine:** HMDA-RI tooling already exists from the trimodal replication ([[project_hmda_trimodal_result]]) — reuse the loader/substrate, don't rebuild. HMDA LAR has race/ethnicity (G), action_taken (Y), loan amount, income, loan type, lien, property type, recent-year DTI buckets. **Known gap: no credit score** (HMDA never had it) — so "admissible legit" is thin; this is a documented limitation, not a defect, and arguably strengthens the proxy story (disparity reconstructed from coarse features). Pair-index / clean train-val-test splits; cross-fitted estimators for any AUC-lift (the C3-probe leak lesson).

**Paper home:** the real anchor for the impossibility paper's Pillar-1 flank.

### 2. ZK-provable construction — build-track (highest non-obvious leverage)
**Why (the salve):** the construction-provenance escape naively requires the institution to *bare itself* (disclose policy/held-out/process) — the wall Olorin hit, the reason the alternative looked dead-on-arrival. **Zero-knowledge proofs / cryptographic commitments dissolve this:** prove "model constructed under the frozen, committed policy" *without revealing* the model, policy internals, or borrower data. Verification without exposure → the alternative becomes deployable, and moves off the surveillance footing onto demonstrated-commitment (ayni-shaped). Composes directly with construction-prereg: prereg gives you something worth committing to, ZK lets you commit without exposure.
**Scope:** this is a *design + minimal proof-of-concept*, NOT a falsifiable experiment (my fun-compass underweights it precisely because it's a build-move, not a coin-flip — that blind spot is why it didn't surface until forced; see [[feedback_force_exploration]]). Deliverable: a design note + a toy commitment-scheme PoC showing "commit to a policy hash + frozen held-out + a proof the deployed model's decisions are consistent with the committed construction." Feeds the method paper. **Open question that would most surprise me (worth chasing):** is ZK-provable construction *cheaper* than the post-hoc audit it replaces? If yes, the "non-trivial engineering" objection inverts into the adoption argument.

### 3. HOLC / historical redlining — cheap self-adversarial (public data)
**Why:** the dark mirror of "codification is the defense" — a regime where the policy *was* explicitly codified/documented (HOLC residential-security maps) and codification was the *weapon*. Mapping Inequality data is digitized + public. Tests whether documented-construction-provenance is sufficient (it isn't — the documented policy was itself discriminatory), reinforcing necessary-not-sufficient. Composes with SBA as the two ends of one axis (codification-as-weapon vs codification-as-defense).

### 4. Election RLA audit-math — formalism import (method paper)
**Why:** risk-limiting audits are a worked positive example of "certify the outcome without certifying every internal" = audit-at-the-right-layer. Borrow their bounded-risk certification math to give the construction-provenance audit real statistical teeth. Low cost (literature/method import), high method-paper leverage.

### 5. Cross-domain finance↔LLM-safety — program move (contingent)
**Why:** substrate-invariance as a *result*, not analogy — reproduce today's lever-invariant accuracy-tax where the "model" is an LLM and the "prohibited criterion" is deception/fabrication (the [[reference_ai_honesty_paper]] sibling). Highest marginal science (reformulates, doesn't replicate). **Cost hinges on whether the ai-honesty substrate is reachable** from here; if it is, this jumps toward the top. Check `../ai-honesty` + the Hamut'ay/taste_open infra.

### 6. SBA codified-domain — self-adversarial coin-flip (data unfetched)
**Why:** the genuine coin-flip on our own remedy — does manufactured-silence survive *explicit* codified rules (SOP 50 10)? Both tails are findings (silence survives → kills "write better rules"; silence suppressed → validates the alternative empirically). Drops to #6 only on cost: SBA 7(a)/504 data needs fetching + SOP codification is real engineering. **If the data turns out cheap to get, promote it** — it's the highest-fun item by the surprise×falsifiability criterion.

### Deprioritized (poor benefit/cost — off the near-term board)
- **EU datasets** — expensive replication + standing risk + GDPR-restricted data.
- **LATAM (MX/BR/PE/IN)** — very high multi-jurisdiction acquisition cost; the Peru/ayni tie is the only lift; revisit only as a program-narrative capstone.
- **AlphaFold/structural-bio, animal-sentience law, halakhic/canon-law responsa** — the shiny tail: surprise without proportionate value; high domain/confabulation cost, tangential to the thesis. (Recorded as fun-reserve, not queue.)

## Meta-discipline carried forward
- Two low-coin-flip moves can stack without noticing (analysis passes, "safe" anchors). When the next pick has no genuine uncertainty, *say so* and check whether a real coin-flip is being avoided. But: foundational-replication (HMDA) is worth doing precisely *because* it's boring-but-load-bearing — low fun ≠ low value.
- Oversample-then-rerank is the corrective for the fun-compass's blind spot toward build-moves (ZK is the worked example). Keep both steps.
- Composition is where value compounds: ZK ∘ construction-prereg; HOLC ∘ SBA. Look for pairs, not just items.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze.
