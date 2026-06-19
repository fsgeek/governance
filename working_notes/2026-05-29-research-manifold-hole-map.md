# The research-manifold hole-map (2026-05-29)

**What this is.** The companion to the claim-audience ledger. The ledger maps what we HAVE;
this maps the HOLES — the places a reader stops believing — ranked by how many of our three
audiences fall through each one. Built by role-playing each audience as an independent
skeptical reader (3 subagents) and overlaying where they stop. A hole all three hit is
structural (no floor without it); a hole one hits is audience-local. Provenance:
governance-lineage Opus + 3 reader-simulation subagents + Tony steering. No new compute.

**Method note (why this is more than my guess):** I drafted a 5-hole read from the ledger,
then had three readers find holes independently. The overlay corrected my ranking twice
(legal hole is LOWER than I thought; a literature hole I'd MISSED is high). Convergence
across independent readers = signal; my solo read = prior.

---

## The holes, ranked by reader-overlap

### TIER 0 — structural floor (ALL THREE readers stop here; fatal to everyone)

**H1. The positive control failed → the spine instrument is unvalidated.**
- Regulator: FATAL ("junk the positive control, I'm not using the impossibility claim").
- Academic: FATAL ("circular… you're proving our oracle is smarter than our surrogate —
  tautological. No peer venue accepts a core impossibility result on an unvalidated
  apparatus").
- Buyer: FATAL ("can't prove its own sensitivity… kills the buy-as-research story").
- **Fills with:** the corrected positive control already specced this morning
  ([[project_pure_disparity_conjecture]]). ONE experiment. If pure-disparity proves
  un-plantable by design, that itself is the answer (the impossibility demonstrating itself)
  — but it must be SHOWN, not asserted. This is the single highest-leverage open item: it is
  load-bearing for all three audiences and I can move it.

**H2. The substrate chasm — FM + synthetic only; the one cross-substrate test FALSIFIED.**
- Regulator: BLOCKING ("a Fannie Mae finding, not a lending finding").
- Academic: FATAL for any regime-level claim; BLOCKING if reframed as institutional.
- Buyer: FATAL for marketing ("10x weaker hook").
- **Fills with:** either (a) a second REAL non-FM substrate showing a silence-like /
  non-identifiability pattern (HMDA-full, auto, cards), or (b) a theoretical argument for the
  structural conditions under which the pattern MUST appear (turns an empirical gap into a
  scoped theorem). (b) is cheaper and also addresses H6.

### TIER 1 — serious (TWO readers stop here)

**H3. Existence ≠ prevalence: is the attack cheap-and-invisible, or expensive-and-caught?**
- Regulator BLOCKING ("if it costs 3% accuracy and any competent examiner catches it, I
  don't regulate it the same as free-and-invisible"). Academic BLOCKING (real-data instance).
- **Partly already answered** on synthetic: the accuracy-tax results (#2 C4, #4 capacity-probe)
  say the intentful attack IS capped at an accuracy cost. The hole is that this is synthetic.
  Porting the accuracy-tax measurement to real FM data is a concrete, bounded fill — and it's
  the regulator's single most decision-relevant number.

**H4. The cryptographic "escape hatch" (tier-2 ZK provenance) is specced, not built.**
- Buyer BLOCKING ("code, not spec… your only compliance-defensible answer"). Academic:
  implicit (the "necessary-not-sufficient" claim needs the artifact to be credible).
- **Fills with:** a toy-scale PoC (commit (policy, held-out, weights); zkML-of-inference on a
  100-applicant challenge; aggregate proof). Engineering, not research. Off my critical path
  for the science but ON the buyer's.

### TIER 2 — audience-local (ONE reader stops here; real but not structural)

**H5. (ACADEMIC) No formal theorem; no positioning vs. known non-identifiability.**
- "Is this distinct from Kilbertus / Kusner on counterfactual-fairness identifiability, or a
  repackaging?" BLOCKING for a top venue. **This is the hole I had entirely missed.** Fills
  with: a literature pass + a formal statement of the LOAN-DOMAIN twist (e.g. "even WITH G
  observed, business-necessity vs laundering is non-identifiable" — Spine §3 asserts this;
  it needs to be a theorem, and it needs to cite who already proved the adjacent thing).

**H6. (ACADEMIC) "Manufactured silence" may be defined-into-existence, not discovered.**
- Did an HONEST admissible model-builder hit the silence, or did we construct it by excluding
  race? BLOCKING for the regime claim. Fills with: an honest-builder construction that hits
  the same silence without the trick. (Related to H2(b).)

**H7. (REGULATOR) Legal NEEDS-GROUNDING (Joe's domain).**
- DOWNGRADED from my morning ranking. The regulator reader did NOT treat this as fatal —
  they ROUTED AROUND it to a usable disclosure rule that needs no settled doctrine. Still
  required before asserting doctrine in print, but it does not block the surviving
  deliverable. IRRITANT-to-BLOCKING, not FATAL.

---

## The thing all three readers independently agreed survives

Asked "what can you actually USE today," the three readers converged on the SAME finding
wearing three hats:

- **Regulator:** a disclosure rule — "report the feature-set variant used and the measured
  disparate impact under ALL plausibly-admissible feature sets."
- **Buyer:** a product discipline — "report both feature-set variants; make the normative
  judgment visible, don't automate it" (and #11: don't build per-case routing).
- **Academic:** a non-identifiability theorem — "impact-minimizing model selection (the
  doctrine's own prescribed remedy) is observationally indistinguishable from proxy
  laundering."

**These are one result (#7 + §5) in three registers.** The program's defensible spine is NOT
"detection is impossible." It is: **the choice of admissible feature-set is a discretionary
lever that moves the audit verdict; the honest response is to make the lever visible, because
no tool can resolve the normative judgment it encodes.** That sentence survives every hole
above (it doesn't depend on H1/H2 — those block the IMPOSSIBILITY framing, not the
lever-visibility framing). It IS the regime-feasibility thesis the hostile reviewer and the
spine §1 both converged on.

---

## What this implies for sequencing

1. **H1 first** — one experiment, load-bearing for all three, already on my bench. Until it
   clears, the impossibility framing is unsafe to write for anyone.
2. **Reframe the spine NOW** from impossibility → lever-visibility. This is free (a writing
   move) and it makes H1/H2 block only the *secondary* (impossibility) claim, not the
   primary (lever-visibility) one. Biggest single risk-reduction available, costs no compute.
3. **H2/H3** — the real-data port (accuracy-tax + a second substrate) is the next experimental
   block; it's what upgrades lever-visibility from synthetic-existence to in-the-wild.
4. **H5** (literature/theorem) and **H4** (ZK PoC) are parallel non-experimental tracks —
   H5 is reading+formalization (gates the academic paper), H4 is engineering (gates the buyer
   artifact). Neither is on the critical path of the others.

**Status:** untracked working note, for review. No pre-reg, no compute this session.
Companion: `2026-05-29-claim-audience-ledger.md`,
`2026-05-26-impossibility-regime-claim-spine.md`.
