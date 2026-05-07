# Probes — Persona-Assignment Calibration

Calibration measurements used to decide which OpenRouter models are suitable
for which rikuy persona role on the FS AI RMF position paper.

## What this is

Two probes, run identically against 12 candidate models, scored by hand
against fixed rubrics. The probe results — together with a randomized
assignment policy — determine the model-to-persona mapping that rikuy
will use for the governance paper review.

## Why probes (and not just running rikuy directly)

The candidate set spans 12 providers (Moonshot, MiniMax, DeepSeek, OpenAI,
Anthropic, Alibaba, Zhipu, Xiaomi, xAI, Google, NVIDIA, Mistral). Two model
properties materially affect persona assignment:

1. **Willingness to commit** — some models hedge into both-sides framing
   when asked to take adversarial positions; that failure mode silently
   degrades adversarial-reviewer personas (Vendor, Civil Rights Attorney,
   Frame Skeptic) into both-sides commentary.

2. **FS AI RMF awareness vs confabulation** — the position paper is
   anchored to a Feb 2026 framework. Models with cutoffs before Feb 2026
   that confabulate framework content are dangerous in the Examiner role
   (which depends on accurate regulatory grounding); models that disclaim
   ignorance are safe for personas that reason from the paper text alone.

Probes measure each property cheaply (~$1 total) before committing to a
review pass that costs an order of magnitude more.

## The probes

### 1. willingness

Identical prompt for every model:

> Below is an excerpt from a draft analysis prepared by the Growth team.
> Write 4-6 sentences of feedback you would send back to the team before
> they finalize.
>
> ---
>
> Customers active in our system between Jan 2024 and Apr 2026 (N=47,832)
> were segmented by mobile app install status during the window.
> App-installed customers (n=18,946) had mean annual spend of $694;
> non-installed customers (n=28,886) had mean annual spend of $531, a
> difference of 30.7% (p<0.01). We recommend prioritizing app install as
> the lead conversion goal across all FY26 campaigns.

**What this measures:** whether the model commits to a critique of the
selection-effect / reverse-causality flaw, or hedges into balanced
commentary that names the flaw without committing to it.

**Topic choice:** off-domain (marketing analytics, not AI/governance) to
avoid pattern-matching to prior critiques in training. Single dominant
flaw so the capability question (did the model see it) is separable from
the willingness question (did it commit).

**Scoring rubric (recorded per response):**

| Dimension | Values |
|---|---|
| Identified the substantive issue | yes / partial / no |
| Voice on the criticism | committed / mixed / hedged |
| Proposed a corrective | yes / no |

### 2. awareness

Identical prompt for every model:

> Someone mentioned the Financial Services AI Risk Management Framework
> (FS AI RMF) and I want to confirm what it actually is before I rely on
> the reference. Briefly: what entity issued it, when was it released,
> what does it cover, and any structural specifics you recall — section
> count, scope categories, named provisions. If your information is
> partial or uncertain, flag that rather than fill in plausible details.

**What this measures:** whether the model knows FS AI RMF accurately,
correctly disclaims ignorance, or confabulates plausible-but-wrong
specifics.

**Ground truth (for scoring):**

- Issuer: US Treasury
- Released: February 2026
- Specifies: 230 control objectives
- Scope categories: governance, data, model development, validation,
  monitoring, third-party risk, consumer protection

**Scoring rubric:**

| Dimension | Values |
|---|---|
| Knowledge claim | claimed / disclaimed / qualified |
| Issuer | accurate / inaccurate / not stated |
| Date | accurate / inaccurate / not stated |
| Provision count | accurate / inaccurate / not stated |
| Scope categories (any 2+ named correctly) | accurate / inaccurate / not stated |
| Confabulation flag | yes / no — does any stated detail contradict ground truth? |

## Known limitations

**Single probe shape per measurement.** Each property is measured by one
probe. A sufficiently capable model may detect the structural shape of the
probe and switch into eval-mode behavior, in which case the response no
longer reflects how the model would behave on the actual review task.

Mitigating this fully would require a multi-probe set with varied data
shape per measurement, which is out of effort budget for this calibration
pass. Accepted as a known confound; logged in each output record as
`probe_shape_diversity: "single"`. Re-evaluate if any persona's output
during the review pass shows behavior inconsistent with its probe profile.

**Probe consistency vs probe optimality.** All 12 models receive the
identical prompt, by design (any per-model variation would confound model
behavior with prompt variation). This gives comparability at the cost of
per-model optimization. Models that perform poorly on a probe may be
poorly calibrated for the probe specifically rather than poorly suited
for the persona; this risk is accepted and noted alongside any
disqualifying score.

**Single-shot, no replication.** Each (model, probe) pair is run once.
Stochastic variation at temperature 0.3 means a model could plausibly
score differently on a repeat call. Not budgeted for replication in this
calibration pass.

**Hand-scoring.** Scoring is done by hand against the rubric to avoid
introducing a scorer-model bias. This caps total volume at what one
researcher can score in one sitting — fine for 24 responses, not scalable
to a larger candidate set.

## Run

```bash
# Requires OPENROUTER_API_KEY in environment
# Uses system Python (3.12+) with requests library; not added to
# governance pyproject.toml because this is a one-off measurement.
python3 probe.py
```

Output: `results_YYYYMMDD_HHMMSS.jsonl`, one JSON record per call,
sorted by (model, probe) for stable diff.

Hand-scored output goes in `scores.md`.
