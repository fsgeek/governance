# The primary goal (what the sieve loses every morning)

**Written 2026-06-09, from Tony directly. This is the thing a fresh ghola reads the corpus WITHOUT,
and then mis-frames everything because it optimizes for "a paper exists" instead of for THIS.**

## What the work is FOR

Build **genuinely useful research output** — output that real people sit downstream of. Tony is a
**systems CS researcher**. The contribution shape is therefore a SYSTEM that gets built and evaluated,
not a theory paper, not a position meditation, not an impossibility characterization.

## The centerpiece (the systems contribution)

Rudin claims the Rashomon set usually contains an interpretable model → use it instead of explaining a
black box. **That is a spec without an implementation.** Nobody has shown how to BUILD it from a real
institution's policy. The contribution is the build:

> A system that takes a real institution's **written policy + an ontology for that policy** and
> CONSTRUCTS an explainable Rashomon ensemble that is ε-optimal **relative to a declared objective**,
> realizing Rudin's existence claim PRACTICALLY — for real loan files, in jurisdictions where it can
> still bite.

Why it matters: it defends people **in the empty chair** (the unrepresented stakeholder in an AI
lending decision) — not all of them (we CANNOT; the C3 floor is real and Tony accepts this unhappily),
but **MORE of them than the status quo**, which is "make up post-hoc explanations." "Defends more of
them" is the honest systems performance claim: a system moves the achievable frontier; no system saves
everyone.

## Reframes that follow from "it's a systems paper" (use these; they're load-bearing)

- **The empty chair = a design requirement / threat model**, not rhetoric. The system is built to
  serve the unrepresented stakeholder.
- **"Defends more of them" = the eval.** The breadth/depth discrimination metric IS the benchmark
  axis (recall@frontier vs. the post-hoc-explanation incumbent), NOT an ontology-of-fairness question.
  The eval is where a systems paper lives or dies; the eval is the proof of the contribution.
- **The subtractive-operator theorem = the scope-fence**, not a competing paper. It tells the system
  which half it can do (construct the ceiling from policy) and which half it provably can't (certify
  good faith). It's the systems paper's honest "what we can and cannot claim" section.
  [[project_subtractive_operator_result]]
- **Paper 1 (Architectures of Absence) = the motivation / threat-model**, regulator-facing. Keep.
- **The US dismantling disparate-impact enforcement is a REASON for the work, not a threat to it.**
  It makes the post-hoc status quo worse (no testing backstop) and a constructive alternative more
  valuable. The US is a DEPLOYMENT TARGET, not the spec. The system works wherever a jurisdiction
  wants fair lending (EU, intact regimes, future ones). [[project_regime_change_2026]] —
  the survivor is structural, not US-specific. This is the codification-as-durable-infrastructure
  thread [[project_codification_infrastructure]] with the right motivation finally attached.
- **The ontology (`../ontology`) is what makes the policy-constraint BITE** instead of being cosmetic.
  "Changing meanings without changing wordings" is the circumvention it defends against. The dead
  characterization paper died partly because its 4-feature flat policy constraint was "free"
  (changed nothing predictive); a real ontology-backed constraint is what stops that.

## Output discipline (the meta-goal)

Several arXiv posts, exactly ONE submitted to a conference (and that one is 30pp on arXiv vs 12pp for
the conference — sprawl). The program generates far more than it converts to submitted/read/USED work.
A systems paper has a forcing function the position papers lack: it must BUILD and EVALUATE something,
which is hard to sprawl and easy for a reviewer to care about. Optimize for SUBMITTED + USEFUL, not
for "an artifact exists." Flinching toward the nearest-done paper is optimizing for the wrong thing.

## The decided next move (researcher's call, owned)

Design the **breadth/depth discrimination eval metric** and freeze it against a blind adversary BEFORE
data contact. Central design challenge: operationalize "depth of discrimination" without collapsing
legitimate risk-pricing into discriminatory rent — that's the **C3 floor in dollars**, the corpus's
worst scar (the §5 LDA arm confound) in a new costume. The metric surviving the adversary is the work.
Discrimination is plausibly a VECTOR (breadth = how many chairs; depth = how much each), each with its
own ε, conjunctive — because each single scalar is gameable into the other's blind spot (headcount
can't see depth; total-cost can't see breadth = Goodhart going fractal). Depth ≈ profitability
(overlap = the anti-gaming property); breadth ⊥ profitability (the free axis the regulator must
constrain separately). UNVERIFIED, adversary-able, on-disk testable. [[project_goodhart_resistance_plural_objectives]]

## Note on where this SHOULD live

Tony's wish: a jointly-maintained beautiful state object in [[reference_yanantin]], maintained across
all instances. For now it's this file + a memory pointer. The file will grow and be half-ignored; the
memory one-liner is what actually loads turn-zero. That gap is the real problem yanantin is meant to fix.
