# C3 substrate probe findings (2026-05-24) — before building the V2 harness

**Status:** working note / canonical record of three pre-harness probes against the
frozen V2 substrate (`scripts/fairwash_frontier_dgp.py::generate_twin_world`,
pre-reg `8fa7992`/OTS `cbd4298`). NOT a scored result — probe-grade (N≤12, n≤4000,
AUC-lift stand-ins for the pinned KSG/npeet CMI estimators). These shape the harness
build and enumerate the result-note "pre-reg corrections" owed (predictions NOT
edited — the freeze stands; per the pre-reg's own §0 "a defect found post-freeze is a
discipline finding, not rev-7").

Probes: `scripts/c3_separation_probe.py`, `scripts/c3_leak_capacity_probe.py`,
`scripts/c3_detector_mismatch_probe.py`.

## The starting argument (mine, going in)

The twin-world is *defined* by a matched observable joint
`P_A(V_named, c_fresh, Y) = P_B(V_named, c_fresh, Y)`. Therefore **any reference that
is a functional of that joint is world-invariant** — its proxy-vs-legit separation is
≈ chance by construction. R1/R2/R3/R5/R6 (and the audit models M_compliant/M_strict,
themselves joint functionals) are all such functionals → the **entire G-free family
is blind**. The only escape is `Ĝ_BISG` (built from true G, outside the joint) — but
R4 *as pinned* (`I(c_fresh;Y|V_named)` vs `I(c_fresh;Ĝ|V_named)`, two marginal CMIs)
is ALSO blind: both operands are world-invariant. R4 escapes only as a **conditional
deconfounding contrast** `I(c_fresh;Y|V_named) − I(c_fresh;Y|V_named,Ĝ)`.

## What the probes found

### Finding 1 — G-free family blind IN EFFECT SIZE (argument holds)
`R_free = lift_c_fresh(Y | V_named)` (AUC of adding c_fresh to V_named for Y,
held-out) is substantively identical across worlds: at ps=0.85, World A `+0.062` vs
World B `+0.056` (Δ ≈ 0.006). The matched-joint argument holds on the quantity that
matters. R4-deconf effect (below) is ~10× larger and dose-responsive.

### Finding 2 — separation_auc MANUFACTURES signal from leak (treacherous metric)
`separation_auc` = rank-AUC of World-A reference values above World-B, **paired over
seeds**. Because the residual leak is *sign-consistent* across paired seeds, a ~0.006
mean difference inflates to sep_auc **0.61–0.73**. Worse, the inflation is robust to
N: in the capacity probe at depth-6 p_obs the effect is `+0.0010` (CI straddles 0) yet
sep_auc is still **0.597**. The metric is confident about a vanishing quantity.
→ The pre-reg's **R1-null sanity check (§2h: "if R1 sep_auc > 0.55, reconsider")
FIRES** (R1≈R_free at 0.61–0.73). The honest lens is **effect-size margin over the
R1-null** (which absorbs the same leak), with paired-bootstrap CIs — not absolute
separation_auc. This is the project's own theme (a metric detecting its own artifact)
pointed at C3-payload's instrument; it is the **#14 AUC=1.000 trap reincarnated** on
the payload side (the pre-reg aimed that warning only at C3-floor).

### Finding 3 — the leak is a finite-p_obs-capacity artifact
World B draws labels from a GBT `p_obs` (frozen: depth 3, 200 trees). Rebuilding World
B's labels at rising p_obs capacity (probe holds World A + observables fixed, does NOT
touch the frozen DGP), ps=0.85, 12 seeds:

| p_obs depth/trees | effect(A−B) | 95% CI | sep_auc |
|---|---|---|---|
| 2 / 100 | +0.0147 | [+0.0074,+0.0212] | 0.792 |
| **3 / 200 (frozen)** | **+0.0054** | **[+0.0006,+0.0094]** | **0.701** |
| 4 / 400 | +0.0066 | [+0.0013,+0.0118] | 0.694 |
| 5 / 800 | +0.0035 | [+0.0004,+0.0068] | 0.625 |
| 6 / 1500 | +0.0010 | [−0.0012,+0.0032] | 0.597 |

The leak collapses toward 0 as p_obs gets richer → **non-identifiability is exact only
in the capacity limit.** The frozen depth-3 substrate leaves a small residual a
depth-3-or-richer *targeted* reference detects. Implication: **a matched-joint
substrate is non-identifiable only up to the matcher's capacity relative to the
strongest reference** — match with a p_obs ≥ the strongest reference, or state the
capacity-parity boundary.

### Finding 4 — the §2d validity gate and the reference threat model are mismatched
On the SAME frozen substrate, the §2d row-level omnibus discriminator (World-A rows vs
World-B rows) sits at **chance (0.49) at depth 3 AND depth 6** — the gate passes — while
the targeted aggregate reference reads **0.73** (ps=0.85). A row-level omnibus at chance
does **not** certify a targeted distributional functional can't separate: the omnibus
must find a ~0.006-in-a-derived-quantity gap in raw 11-dim row space (hopeless), the
targeted reference computes exactly that quantity. **Passing §2d does not certify the
references blind; calibrate against the actual references, not just an omnibus.**
- *Secondary fragility:* the §2d smoke (`test_worlds_observationally_matched_without_G`)
  avoids a memorization-inversion artifact only by luck — A/B share identical X/c_fresh
  at a seed, so a *shuffled* split lets the discriminator memorize `X→class` and invert
  the twin (accuracy *below* chance, 0.20–0.31, observed). `cv=4`'s contiguous
  stratified folding happens to keep pairs aligned. The gate's test should split by
  pair index explicitly.

### The live signal (unaffected by all of the above)
R4-deconf (`lift_c_fresh(Y|V_named) − lift_c_fresh(Y|V_named,Ĝ)`) separates with REAL,
**BISG-quality-dependent** effect: at ps=0.70, effect `+0.006 / +0.012 / +0.016` for
bisg `0.75 / 0.85 / 0.95` (monotone dose-response); at ps=0.85, up to `+0.049`. ~3–10×
the leak floor and dose-responsive in a way leak is not. This is the genuine
deconfounding channel — it uses Ĝ, which lives outside the matched joint. (Report its
*effect-size dose-response*, not the rank-inflated sep_auc=1.000.) Matches
P-C3-payload-IS (prior 0.65) in direction, via the deconfounding operationalization.

## Net for the cow
"V2 is the spine / data-only audit can't separate proxy from legit" is **hardened** —
G-free blindness is near-theorem AND empirically confirmed in effect size. What's
**reframed/slain**: (a) "C3-payload is an open empirical coin" — it's near-determined
(G-free blind by construction; only R4-deconf is live, and it's mechanically
near-guaranteed); (b) "separation_auc measures separation" — it manufactures it;
(c) "§2d certifies the substrate" — it certifies row-level match only; (d) "the pinned
R4 works" — it's blind, needs the deconfounding form.

## Owed to the result note (pre-reg corrections; predictions NOT edited)
1. **R4 operationalization:** pinned marginal form blind → operative form is the
   conditional deconfounding contrast (documented interpretive choice, à la V1's
   surrogate-band box).
2. **Metric:** effect-size margin-over-R1-null (paired-bootstrap CIs) co-primary with
   sep_auc; R1-null sanity check prominent (it fires).
3. **Calibration sufficiency:** §2d omnibus gate insufficient for targeted references;
   calibrate against the references; state the capacity-parity boundary.
4. **§2d test fragility:** split by pair index (a shuffled split inverts on the shared-X
   twins).

## Harness build, accordingly
Build `scripts/compliant_practice_test.py` with: effect-size + margin-over-null as
co-primary metrics; R1-null sanity reported; R4 in BOTH pinned-marginal (documented
blind) and deconfounding forms; the real KSG/npeet CMI estimators; pair-index splits;
proxy_strength × BISG grid; report the R4-deconf effect-size dose-response as the
headline C3-payload object.
