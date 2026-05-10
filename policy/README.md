# Policy graphs and constraint encoding

This directory holds the policy-graph definitions and the constraint encoder
that translates them into restrictions on the Rashomon model class.

## What this is

The methodology constructs the Rashomon set R(ε) from a documented bank
policy graph rather than from a generic interpretable model class. Every
model in R(ε) is, by construction, a refinement of documented policy. The
artifact a regulator audits (the YAML below) is the same artifact that
constrains the model class — that co-identification is the point.

## Files

- `thin_demo_hmda.yaml` — illustrative demonstration policy graph for HMDA
  mortgage decisions. Drafted from public underwriting conventions
  (FHA / conventional QM / CFPB ATR/QM); thresholds are illustrative.
  **Status: demonstration substrate, not anyone's actual policy.**

## What gets encoded as a constraint

A policy graph YAML produces three classes of constraint:

1. **Monotonicity constraints.** `direction: positive` means higher feature
   values never decrease grant probability; trees / GAMs / rule lists in
   R(ε) must respect the sign.
2. **Mandatory-feature constraints.** A model that ignores a mandatory
   feature is excluded from R(ε).
3. **Prohibited-feature constraints.** A model that uses a prohibited
   feature is excluded from R(ε).

Plus structural constraints from the node graph itself:

4. **Predicate constraints.** A model's decision-region predicates must be
   expressible as combinations of policy-node conditions.
5. **Routing constraints.** Cases that the policy graph routes to
   `manual_review` are *not scored* by R(ε) — they are surfaced to a
   human with the policy-node trace identifying why.

## Relationship to `wedge/`

The `wedge/` directory holds the earlier (pre-policy-constraint) prototype
infrastructure: hyperparameter sweep, ε filter, attribution, Jaccard overlap
metric. This `policy/` directory adds the constraint layer on top: the
sweep is restricted to constraint-respecting hyperparameters, R(ε) is
filtered by constraint compliance, attribution is decorated with policy-
node identifiers.

## Status

- 2026-05-09: thin demo graph drafted (`thin_demo_hmda.yaml`).
- Pending: constraint encoder (`encoder.py`), policy-aware Rashomon
  constructor, R(ε) construction over HMDA data under thin demo
  constraints.
