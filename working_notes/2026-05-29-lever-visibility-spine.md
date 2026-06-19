# The lever-visibility spine (2026-05-29) — supersedes the impossibility framing

**What this is.** The reframed spine of the program, built to be the SKELETON of the
regulator-facing draft document (task #6), not an internal capture. Supersedes
`2026-05-26-impossibility-regime-claim-spine.md` (kept as lineage — the thinking as of
05-26). The promotion: what was buried in that note's §1-last-line and §2-tiers becomes the
lead; the "impossibility theorem" language is demoted to a scoped secondary claim that three
independent skeptical readers said gets killed on contact. Provenance: governance-lineage
Opus + reader-simulation subagents + Tony steering across the 2026-05-29 session. Standing
rule retained: legal claims flagged **NEEDS-GROUNDING (Joe)** — do not assert as settled law.

**The one-sentence spine.** *The choice of which features count as admissible is a
discretionary lever that moves the audit verdict; no post-hoc tool can resolve the normative
judgment that lever encodes; therefore the only defensible posture is to make the lever — and
the commitment behind it — visible and tamper-evident.* (NOT "detection is impossible." That
framing is the overclaim the lineage keeps drifting back to; every skeptical reader rejects
it. See `2026-05-29-research-manifold-hole-map.md`.)

---

## 1. Two findings, one asset (the offense/defense pairing)

The program is **two findings**, and the regulator document's force comes from holding them
together — neither alone is the asset.

**Finding 1 — the attack (offense / the threat model).** You can construct a model whose
disparate impact is invisible to a SHAP/LIME audit *as those audits are actually run*, because
the post-hoc explanation reports feature attribution and leaves legitimacy — the normative
question — out of scope. Exclusion of the protected attribute does NOT prevent its
reconstruction (the V2 result). This makes the industry-standard explainability stack unfit
for the certification purpose it is used for. Responsibly disclosed TO the regulator as
evidence, not wielded as a how-to.

**Finding 2 — Rashomon does NOT escape the floor (defense / the honest boundary).** The
natural hope — "use a policy-constrained Rashomon set to detect the laundering SHAP/LIME
hides" — fails. There is a floor (C3 latent-G non-identifiability): honest correction and
laundering are observationally identical. Rashomon's value is therefore NOT detection. It is
**pre-commitment + auditability** — a property post-hoc tools structurally cannot offer:
freeze the policy and the held-out set *before* the outcome, and the audit trail is real
because it cannot be backfilled.

**Why the pairing is the asset, not either half:** Finding 1 makes the incumbent stack a
liability; Finding 2 offers the defensible alternative AND is honest about what it cannot do.
The honesty (the floor) is what separates Finding 2 from every vendor who over-claims
detection — and over-claiming is exactly what makes SR-26-2 regulators uncomfortable. A tool
that under-claims in precisely the right place is the differentiated, credible asset.

---

## 2. The three tiers (what can be proven, inversely arranged vs. what is wanted)

The wished-for crypto ("prove this model doesn't encode the prohibited criterion") resolves
into three tiers — and the tiers ARE the offense/defense story stated cryptographically:

1. **Trivial / worthless** — "race was never an input feature." Easy to attest; governance-
   worthless because proxy reconstruction defeats it. *This is essentially what SHAP/LIME
   attests, and Finding 1 is the proof it is worthless.*
2. **Achievable / the prize** — "the deployed model is the committed model; its decisions
   refine the committed policy; the commitment was frozen before the test." Buildable from
   pieces that exist today: temporal/swap-proof commitment over `(policy P, held-out H,
   weights w)` + zkML-of-**inference** + a regulator **challenge protocol**. *This is
   Finding 2's pre-commitment/auditability, cryptographically enforced — the
   necessary-not-sufficient line.*
3. **Impossible / most-wanted** — "the model does not encode the prohibited criterion." No
   witness exists (C3); ZK can only prove witnessed statements ⇒ ZK inherits the floor
   wholesale. A proof-of-innocence system would be lying. *This is the floor, and a tool
   honestly refusing to claim it is the proof-of-non-capture.*

The crypto's inability to overclaim is **coextensive** with the necessary-not-sufficient
line — *that the system cannot prove tier-3 is the feature, not the bug.*

**Key correction (retained from 05-26):** construction-provenance needs tier-2 (inference-
consistency against a committed policy + temporal commitment), NOT training-provenance. You
commit to the training's *output* (weights) and prove *behavioral* adherence; you never prove
the training *process*.

---

## 3. The causal loop (why this is a strategic asset, not just a paper)

The regulator document and the strategic value are not parallel — they are causal and
circular **on purpose** (Tony's framing, 2026-05-29):

- The regulator document shapes what a supervisor believes is unsafe (post-hoc/launderable)
  and what counts as adequate (pre-committed/auditable).
- That belief makes the incumbent stack a liability and pre-commitment a requirement.
- The requirement IS the moat — and it exists *only because* the regulator now cares about
  the distinction the document taught them to care about.
- So the asset is not a product; it is **the chance to shape the standard a product already
  satisfies**, while the window is open (SR-26-2 = uncomfortable-but-not-decided; harder in
  six months).

**The integrity constraint this imposes:** the regulator document CANNOT read as captured. A
captured document claims its tool detects discrimination. This one says "nothing detects it
post-hoc, ours included — here is the boundary — *therefore* pre-commitment is the only
defensible posture." The floor (tier-3) is not humility decoration; it is the **load-bearing
strut**, because it is what makes a regulator adopt the frame rather than suspect it. The
honesty IS the strategy.

---

## 4. Where the impossibility framing goes (demoted, not deleted)

"Detection is impossible" survives ONLY as a scoped, secondary, technically-careful claim:
- It is an **existence result on synthetic data** ("there exists a DGP where honest and
  laundering are observationally identical but differ in ground truth"), NOT an
  in-the-wild measurement. Prevalence in real lending is unknown (hole H2/H3).
- It needs the corrected positive control (H1) before even the synthetic existence claim is
  safe — the apparatus's basic sensitivity is currently unvalidated.
- It must be positioned against known non-identifiability (Kilbertus/Kusner) or it risks
  re-deriving them (hole H5).

So in the regulator document the floor appears as **finding 2's honest boundary** (which needs
none of the above to be useful), NOT as a headline impossibility theorem (which needs all of
the above and is the academic paper's burden, not the regulator document's).

---

## 5. Document skeleton this spine dictates (for task #6)

1. **Threat model** — Finding 1, the SHAP/LIME construction, responsibly disclosed as
   evidence that post-hoc explainability is unfit for certification.
2. **Why no better post-hoc tool rescues it** — the floor, stated as a boundary (Finding 2's
   "no"), at the depth a regulator needs (not the full theorem).
3. **The defensible posture** — pre-commitment + auditability (Finding 2's "yes" / tier-2).
4. **The honest limit** — tier-3, explicitly, as proof this is not a sales document.
5. **The open questions** — the TITAN holes, visibly flagged as comment-invitations:
   which second substrate (H2/H3 reduced), legal grounding (H7/Joe), ZK-build funding (H4 /
   the sponsorship ask), academic trajectory (H5 / worth formalizing?).

**Status:** untracked working note, for review. Supersedes the 05-26 spine. No compute this
session. Next: task #2 (corrected positive control, freeze-before-code, fresh window).
