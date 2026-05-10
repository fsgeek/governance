# Preregistration Records

This directory holds experiment-level preregistration records for the research
track.

## Purpose

Each file here fixes the structure of one concrete experiment before the result
is known. The goal is not bureaucracy. The goal is to prevent retrospective
editing of what the project said it expected.

Git history plus the repository's OTS-backed commit hooks provide the
timestamping substrate. These files provide the human-readable scientific
structure on top of that substrate.

## Naming

Use:

`YYYY-MM-DD-short-slug.md`

Examples:

- `2026-05-10-shap-vs-rashomon-absolute-threshold-rerun.md`
- `2026-05-12-fnmae-indeterminacy-characterization.md`

## Lifecycle Rules

- One prereg file per concrete experiment.
- A prereg file is the prediction and design record for that experiment.
- Once committed, the scientific content of a prereg file should be treated as
  immutable.
- Interpretation, exceptions, and hindsight belong in a later findings note or
  amendment record, not in a silent rewrite of the original file.

## Amendments

If an amendment is unavoidable:

- do not rewrite the original prediction record
- create a new dated amendment file
- link it to the original prereg and explain exactly what changed and why

Suggested amendment naming:

`YYYY-MM-DD-short-slug-amendment-01.md`

## Relationship to the Other Research Docs

- `../program.md` explains when a topic is mature enough to become a formal
  hypothesis and experiment.
- `../hypothesis-register.md` is the canonical index of hypothesis status.
- Findings notes may live elsewhere in the repository, but each prereg record
  should link forward to the resulting note once it exists.

## Minimum Discipline

Every prereg file should:

- name the linked hypothesis ID
- specify the substrate or dataset
- state the exact measurements
- name the comparison baseline
- define failure conditions
- state what would count as a kill result

If those fields cannot be filled honestly, the topic should remain in
characterization or operationalization rather than being promoted to a prereg.
