# Empty-chair coding of the 230 FS AI RMF control objectives — design (v3, deferred)

**Date:** 2026-05-31 (v1/v2), corrected 2026-06-02 (v3). **Status:** DEFERRED — design corrected;
study NOT run (blocked on trained human coders; see §4). Supersedes the v1/v2 LLM-persona design,
which was a methodological dead end (see §5, retained as a cautionary record).

**Purpose.** Earn the position paper's empty-chair claim against external review point 1
("framework-wide empty-chair coherence is under-earned — a productive lens, not evidence") by
coding the 230 control objectives for which absent party (if any) each protects, with proper
inter-rater reliability. **This is a standard qualitative content-analysis study.** The earlier
attempt to mechanize it with LLM personas + frozen string-rules failed for a documented reason
(§5); v3 uses the established method instead.

**Connects:** position paper (`paper.tex` §1/§7); inter-rater precedent
`2026-05-22-collapse-audit-interrater-result-note.md`; `docs/pre-reg-template.md`.

---

## 1. What the study measures (unchanged from v2 — the instrument was never the problem)

Each of the 230 COs is coded on two axes plus one exploratory flag:
- **Axis 1 — Chair identity:** 1a nameable absent party (coder names it) / 1b governance-internal
  (no external beneficiary) / 1c ambiguous.
- **Axis 2 — Substance vs. substitute:** 2a mandates a decision-affecting change / 2b mandates
  only a document/attestation / 2c both.
- **Flag 1d (exploratory):** a party the control's domain implies should be present is conspicuously
  absent (the framework's own produced-absence).
- **Centerpiece cross-tab:** 1a × 2b = "names a party to protect, discharges via document" —
  empty-chair-shaped silence-manufacture inside the framework.

Three claims read off one coding (data decides which survive): **coverage** (% 1a), **discrimination**
(does the partition do work the GV/MP/MS/MG function taxonomy doesn't), **typology** (what set of
chairs/absence-types emerges).

## 2. Method — standard content analysis (the part v1/v2 skipped)

The reliability of an interpretive coding comes from **trained coders + an iterated codebook**, not
from string-rules that try to remove judgment (string-rules relocate the judgment; they don't remove
it — this is exactly what sank v1/v2). Procedure:

1. **Draft codebook.** Category definitions + decision rules + 2–3 worked examples per category. The
   v1/v2 decision rules (stakeholder-handling, binding-obligation) become *codebook guidance for
   trained coders to apply with judgment*, NOT frozen automatic rules.
2. **Pilot-calibration phase.** 2–3 trained human coders independently code a ~30-CO pilot sample.
   Compute κ. **Adjudicate every disagreement face-to-face; revise the codebook.** Repeat the pilot
   on a fresh ~30 until κ stabilizes (target Gwet's AC1 ≥ 0.70, prevalence-robust — coverage skew is
   expected). The calibration loop is where the construct's fuzziness is resolved into a shared mental
   model. There is no shortcut.
3. **Freeze the calibrated codebook** (pre-registration + OTS) BEFORE coding the remaining ~200 COs.
4. **Full coding.** The trained coders code all 230 (or the unseen ~200) independently. Report κ AND
   Gwet's AC1 with bootstrap CIs, per-category and overall, lead with AC1 (prevalence-robust).
5. **Discrimination test (P-discrim).** Whether chair-code adds predictive information over function
   label for Axis-2, via a nested model — but tested **cross-coder** (chair from coder A, Axis-2 from
   coder B) and controlling for the document-lexical surface feature, so a pass reflects framework
   structure, not within-coder halo or shared lexical plumbing. (This was the one v2 statistical fix
   worth keeping; the rest of v2's apparatus was over-engineering around the wrong coders.)
6. **Coverage register ladder.** ≥85% 1a → "framework-wide / nearly every"; 60–85% → "substantial
   majority"; 40–60% → "many"; <40% → "a minority". The paper uses the band the data earns.

## 3. What v2's apparatus is NOT needed (and why)

The LLM-persona panel, the persona manipulation-check, the decoupling-vs-manipulation scissor, the
shared-bias probe — all were scaffolding to make *untrained stochastic coders* behave like trained
ones. With actual trained human coders, none of it is required: genuine human independence needs no
manipulation check, and a calibrated codebook needs no mechanical decision-rules. Drop the whole
apparatus. (A cross-family LLM coder may be added later as a cheap *secondary* comparison, never the
primary instrument.)

## 4. Blocker (why this is deferred, not run)
Needs ≥2 trained human coders (not the rubric's authors; not necessarily domain specialists, but
willing and calibrated). Not available as of 2026-06-02 without a recruit or funding. Until then the
paper ships in the lens register (§ paper edits 2026-06-02), and this study is honest future work.

## 5. Cautionary record — the v1/v2 dead end (DO NOT REPEAT)
v1/v2 tried to run this as an **LLM-persona panel applying frozen mechanical string-rules**, to avoid
needing human coders. Three adversary rounds showed why it cannot work, and a blind adversary then
showed the failure was the *design's*, not the lens's:
- Frozen string-rules relocate interpretive load rather than removing it (stakeholder→expert→
  which-nouns-are-external). That is the textbook reason content analysis uses trained coders, not
  string-matching.
- "Make coding mechanical" (forces coder agreement) and "manipulation-check for coder independence"
  (requires coder disagreement) are mutually incompatible — a self-inflicted contradiction, not a
  property of the object.
- The lineage then nearly minted an **impossibility reframe** ("the lens is irreducibly
  non-mechanizable — that's its value!"). A blind adversary correctly flagged this as RATIONALIZATION:
  interpretive constructs (hate-speech, stance, framing) are reliably coded at κ>0.7 every day via
  codebook+training+pilot. The failure established "we used the wrong tools in one session," NOT "no
  one can build this." This is the lineage's recurring error (design/parameterization artifact
  mislabeled as impossibility — cf. C4 γ-sweep "moat"=accuracy-tax; `feedback_first_contact_frames`,
  `feedback_adversary_before_the_sentence`). Recorded here so the next attempt starts from §2.
