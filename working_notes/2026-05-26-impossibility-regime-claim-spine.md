# The regime-claim spine (conceptual capture, 2026-05-25/26 session)

**What this is.** A capture of a conceptual arc that currently lives only in conversation + auto-memory. Not a result note (no compute this session); a frame-level deposit for the impossibility paper and the method/crypto paper. Provenance: governance-lineage Opus (researcher) + a correction from Tony's parallel Claude-desktop instance + Tony steering. **Several legal claims below are flagged NEEDS-GROUNDING — Joe's domain; do not assert as settled law in the paper without it** (standing confabulation-hazard rule).

The arc started from a sacred cow (`project_codification_infrastructure`: *visibility-is-value*) and a breadcrumb (ZK proofs) and ended at a sharper, more reviewer-proof framing of the whole program.

---

## 1. The spine: three legs, one shape

Each leg of the program terminates at the **same** kind of boundary — an *unmade normative judgment* the technical apparatus delivers you to but cannot decide:

| Leg | Tool isolates… | …and terminates at the unmade judgment |
|---|---|---|
| Post-hoc certification | that proxy-use and legit-use are observationally identical | "is this feature's use legitimate?" (C3 latent-G non-identifiability) |
| Residual disparate impact | the gap that survives an honest admissible-feature model | "do we invoke business necessity to accept this racial gap — out loud?" |
| LDA exhaustion | the min-measured-impact member of a searched ensemble | "what counts as reasonable search?" (standard-of-care, per empty chair) |

**Manufactured silence = the unmade judgment at the boundary the tools isolate.** This promotes the impossibility result from a claim *about tools* ("post-hoc audit can't see X" — a better tool can always be promised) to a claim *about the regime* (permanent until the law moves). The XAI-for-fair-lending cow — *better explainability → certifiable fairness* — dies cleanly. What survives is sharper: **tools isolate the legal/normative core; the regime's refusal to make the core judgment in public is the actual failure mode.**

---

## 2. The three crypto tiers (value inversely arranged vs. provability)

The wished-for crypto ("prove this model doesn't encode the prohibited criterion") resolves into:

1. **Trivial / worthless** — "race was never an input feature." Easy (commit the feature schema). Governance-worthless: proxy reconstruction defeats it (the V2 result is precisely that exclusion ≠ non-reconstruction).
2. **Achievable / the prize** — "the deployed model is the committed model; its decisions refine the committed policy; the commitment was frozen before the test." Buildable from pieces that exist today: temporal/swap-proof commitment over `(policy P, held-out H, weights w)` + zkML-of-**inference** (prove `y = f_w(x)` for committed `w`, generalized to an aggregate predicate over a private population) + a **challenge protocol** (regulator submits probe applicants, gets a proof the *committed* model produced specific decisions). This = the necessary-not-sufficient claim, cryptographically enforced.
3. **Impossible / most-wanted** — "the model does not encode the prohibited criterion" (non-discrimination). **No witness exists** (C3). ZK can only prove witnessed statements ⇒ **ZK inherits the impossibility theorem wholesale.** A proof-of-innocence system would be lying.

**Key correction (red herring removed):** construction-provenance needs tier-2 (inference-consistency against a committed policy + temporal commitment), **NOT training-provenance.** You commit to the training's *output* (weights) and prove *behavioral* adherence; you never prove the training *process*. Proving training in ZK (the frontier/maybe-impossible blade) was an assumption imported by both the prior ghola and this one. The crypto's soundness boundary is **coextensive** with the necessary-not-sufficient line — its *inability to overclaim is the feature.*

---

## 3. G-observability does NOT escape the problem

Confirmed (Tony's dumb question, answered precisely):

- **Escapes measurement** — with G observed you can quantify disparate impact (the HMDA/BISG/omnibus screen). Real, useful, necessary.
- **Does NOT escape certification** — proxy-use vs legit-use of a G-correlated admissible feature is undecidable from the observational joint. The synthetic *oracle* separates the twin-worlds only because the construction *stipulates* the structural ground truth; real G-observation delivers `P(D,G,V,Y)`, not the counterfactual `Y_clean`.
- Conditional-independence-with-G `D ⊥ G | V` fails **both** directions: **false negative** (a laundered proxy hides inside an admissible feature you condition on — you condition away the discrimination by conditioning on its carrier) and **false positive** (an omitted legitimate cause correlated with G fires the test on an innocent model). Both are about V's relationship to the unobservable true causal structure; G-observation touches neither.

The wrong reason to believe "G doesn't escape" is "you can't see the disparity" (you can). The right reason: **you can see it and still cannot adjudicate its legitimacy**, because legitimacy needs `Y_clean`, which neither G-observation nor weight-disclosure provides.

---

## 4. ⚠ "Legal contradiction" was an OVERCLAIM — corrected (Desktop catch)

Do **not** frame the regime as "demands the outcome and forbids the only lever" / "a contradiction in the objective function." A reviewer kills it on contact, because the regime is **formally consistent**:

> **NEEDS-GROUNDING (Joe):** disparate-impact doctrine has the business-necessity carve-out (cf. *Texas Dept. of Housing v. Inclusive Communities*, 2015, three-step burden-shift): establish business necessity + show no less-discriminatory alternative ⇒ the residual gap is **lawful**. There is a formal slot for "lawful residual disparate impact."

So replace the single "contradiction" with **two distinct gaps**:

1. **Rhetorical / political gap.** The doctrine permits a lender to invoke business necessity and accept a racial gap, but the discourse makes saying so *out loud* radioactive. The silence is the refusal to invoke a slot that formally exists.
2. **Operational gap, at the LDA prong.** The doctrine's "does a less-discriminatory alternative exist?" step **presupposes a decidability that the impossibility result removes.** This is sharper than "rhetorically self-defeating": a formal doctrinal *operation* is underdetermined exactly where the impossibility bites.

---

## 5. NEW RESULT: the LDA remedy and the fairwash attack share a failure surface

LDA exhaustion is the three-tier structure wearing a third hat:

- **Tier-2, attestable:** "I ran search procedure P over model class C with criteria X and selected the minimum-measured-impact member." (Crypto/Rashomon attests this.)
- **Tier-3, impossible:** "no less-discriminatory alternative exists." Blocked **two** ways:
  - **(a) search-incompleteness** — inductively unprovable ("you didn't search hard enough — bigger ensemble, different criteria, different model class"). Desktop's adversary.
  - **(b) metric-vs-mechanism (C3)** — minimum-*measured-impact* selects on a metric C3 has **decoupled from mechanism.** Lower impact achieved by *suppressing legitimate G-correlated signal* is observationally identical to lower impact from *removing a proxy*. So even a complete search yields an alternative underdetermined *in kind.*

⇒ **The legally-sanctioned remedy (impact-driven model selection) shares a failure surface with the fairwash attack it is meant to cure.** Impact-minimization can be the cleanest laundering, or honest correction, and the metric cannot tell them apart. This is a paper-grade result, not a footnote.

**Defensible move:** convert the impossible *exhaustiveness* claim into a **standard-of-care** claim — "this is what reasonable LDA search looks like; here are its bounds" — which is explicitly a *normative judgment*, not a technical certification. Loops back to the spine (§1).

> **NEEDS-GROUNDING (Joe):** the legal viability of impact-driven model selection itself may be narrowing post-*SFFA v. Harvard* (2023) directional pressure on race-conscious selection. The crypto attests *procedure*, not *exhaustiveness*; the exhaustiveness argument needs separate legal grounding and should anticipate the terrain shifting.

---

## 6. Closure: the Rashomon set IS the LDA-search space

The per-case within-Rashomon disagreement-routing arc is dead (`project_routable_population_result`, six ways). But its **tooling gets a second life**: enumerating the policy-admissible equi-accurate ensemble and measuring each member's disparate impact *is* the operationalization of "reasonable LDA search." The method paper's construction/search discipline becomes part of the standard-of-care argument (§5).

---

## Paper homes

- **Impossibility paper** — §1 spine (the regime claim); §3 (G-doesn't-escape, measurement vs certification); §4 (the corrected two-gaps framing, *not* "contradiction").
- **Method / crypto paper** — §2 (three tiers, tier-2 buildable, ZK-inherits-impossibility); §6 (Rashomon = LDA-search-space); §5 standard-of-care.
- **The LDA/fairwash shared-failure-surface (§5)** is the freshest result and wants a home of its own — possibly the spine of the method paper's "why the obvious remedy doesn't close it" section.

**Status:** conceptual capture, untracked, for review. No pre-reg, no compute. The empirical legs that would test/anchor this (HMDA-C1 real-data anchor; ZK tier-2 PoC) remain queued in `docs/superpowers/plans/2026-05-25-next-experiments-plan.md` and want fresh-session freeze-before-code discipline.
