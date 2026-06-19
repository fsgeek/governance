# v2 design — blind-adversary kill + the reframe it surfaced (2026-06-03)

**What this is.** The pre-freeze blind-adversary pass against the v2 two-primitive design
(`024bd6f` design + its pre-reg note), dispatched BEFORE the OTS freeze per the sharpened
discipline (v1's fatal flaw was a *design* flaw the freeze stamped in; catch it while predictions
are mutable). The adversary did not argue — it RAN the negative control + reach metric on the
actual DGP. Both legs broke. This note records the kill and the positive finding buried in it.

## The kill (conceded fully)

- **Safe leg — FATAL.** v2 still compares H (drop c_fresh) vs L (drop x0). That is an arm-level
  A_obs *offset* present at every gap, not a covariate-adjustment artifact. The adversary measured
  v2's exact statistic on the clean world (target_gap=0, 20 seeds, n=8000):
  `ps=0.85 is_L=−0.0117 CI=[−0.0159,−0.0078] FIRES`. **That is a P1 ABORT by the pre-reg's own
  rule** — the identical failure that killed v1. My central claim ("single fixed interventions
  remove the confound") was a MISDIAGNOSIS: the confound lives in *which features H and L drop*
  (strength asymmetry), and no reading-side cleverness fixes a contrast between non-comparable arms.
  The only fix is to match arms on clean-world A_obs (Approach A — which I rejected on a bad reason;
  an *uncalibrated* arm pair is strictly worse, it bakes in a guaranteed offset).

- **Reach leg — FATAL.** `detect = gap_planted − gap_clean` does NOT measure "does this info-set
  reveal the disparity." It measures **how much granting this feature lets the model *act on* the
  planted offset.** Measured (ps=0.85, 8 seeds): bare +0.086 / bisg +0.122 / trueG +0.227 /
  oracle +0.080 / noise +0.086. trueG is largest because G is the cleanest channel TO the planted
  variable (amplification), not because it "detects" best. **P5 (oracle cliff) reads the WRONG SIGN
  (−0.15):** the oracle (Y_clean as a feature) makes decisions track clean structure, so they
  barely move under planting → SMALLEST detect. I had the oracle's causal direction backwards.

- **Gate — SERIOUS.** Gate (b) runs detect on the clean world only, where planted=clean ⇒ detect≈0
  by construction (I half-admitted this). The dimensionality control uses a *noise* column; the real
  confound is a *G-correlated* column, which noise cannot reproduce. Both controls read ~0 and bless
  a planted-world-broken apparatus — the v1 "both agree, both blind" structure exactly.

## The reframe the kill surfaced (the actual finding-in-waiting)

The reach-leg gradient is **not a bug to suppress — it is the lever-visibility result in concrete
terms.** Read it forward, not as "detection":

> The more an auditor's granted feature set lets a model ACT ON race (bare → bisg → trueG), the more
> disparate the decisions become. The oracle (clean-outcome access) is the ONE grant that does NOT
> widen the gap, because it routes prediction through legitimate structure instead of through G.

That is the mechanism the lever-visibility spine ([[project_manifold_hole_map]]) is about, stated as
one monotone curve. The bug was never the gradient; it was (a) calling it "detection" and (b)
predicting the oracle would top it. The substrate was telling me the OPPOSITE of P5, and the
adversary made it say so out loud. Signature lineage pattern: the MISS teaches more than the HIT
([[project_pre_registration_pattern]], [[feedback_adversary_before_the_sentence]]).

**The reshaped question (candidate v3, NOT yet designed, NOT frozen):** drop "detect a pure
disparity" entirely. Ask instead: **as the info-set grants more race-access, how does the
DECISION disparity trade off against LEGITIMATE accuracy?** A model granted trueG can lower its
loss by acting on G (more disparate decisions); a model granted only the clean outcome cannot. The
lever is "who may the model act on G," and granting it moves the verdict — measurable as a
gap-vs-accuracy frontier across the info-set ladder. No oracle *cliff* needed; the oracle is just
the no-G-access endpoint of the same curve. This needs a fresh design + fresh adversary + fresh
freeze; do NOT fast-path it (the same intuition produced two confounded metrics — distrust the
third draft most).

## Disposition

- v2 design `024bd6f` + its pre-reg note: **superseded BEFORE freeze, never stamped as predictions.**
  No frozen-prediction credibility spent. This is the cheap failure the pre-freeze adversary exists
  to produce (v1 cost a full freeze+run+abort; v2 cost one adversary pass).
- **Standing discipline validated + sharpened:** dispatch the blind adversary against the DESIGN
  before the freeze, not only against the result before the headline. The adversary that RUNS the
  negative control on the real DGP beats the adversary that reasons about it. Fold into
  [[project_ops_invariants]] pre-registration discipline.
- Adversary agent id (for follow-up): `a9bc444b24dfbf64d`.
- Open: the v3 frontier-question above. The safe leg's Approach-A arm-matching is a prerequisite if
  any H-vs-L contrast survives into v3; it may not (the frontier framing may dissolve the arm split
  the way the reach reframe dissolves "detection").
