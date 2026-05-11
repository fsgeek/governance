# Documentation Conventions

Two rules and a marking discipline. Adopted 2026-05-11 after spec drift surfaced four misalignments between prose claims and code reality in one review pass of `docs/superpowers/specs/2026-05-10-mechanism-specification.md`. Lightweight by design — heavier process is the wrong intervention for a 10-day-old research project.

## Rule 1: Cite code or canonical contract for normative claims about current behavior

A claim about *what the code or system currently does* must cite either:
- a specific `file:line` reference in code or tests, OR
- a canonical contract document that itself cites code.

Prose memos describing intent, design rationale, or theory do not satisfy this rule. "The encoder validates X" needs `policy/encoder.py:N`, not "per the encoder memo." This rule would have caught the label-polarity bug at write time: a claim about how the wedge encodes labels needs to cite `wedge/collectors/lendingclub.py:85` and `wedge/collectors/hmda.py:145`, not the `policy/encoder.py` docstring's *assumed* convention.

The rule does not apply to claims about *intent* ("the design wants X") or *future state* ("V2 will support X"). Those are theory, not contract — see the marking discipline below.

## Rule 2: Validity headers on substantive documents

Specs, memos, and findings notes that other documents may depend on carry a header block:

```
**Status:** draft / active / superseded / historical
**Authority:** canonical / supporting / exploratory
**Depends on:** [list of file paths, or "none"]
**Invalidated by:** [list of file paths, or "none yet"]
**Last reconciled with code:** YYYY-MM-DD (or "not yet")
```

The load-bearing field is **Invalidated by**. When a finding contradicts an earlier document's claim, edit the earlier doc to add the invalidation pointer. The 2026-05-09 I-stability falsification (`docs/superpowers/specs/2026-05-09-i-stability-falsification-findings-note.md`) should have added an Invalidated-by entry to `docs/superpowers/specs/2026-05-09-conversation-residue-capture.md` §4's "the current wedge cannot test this" claim, and didn't. The 2026-05-10 mechanism spec then inherited the stale claim. Mechanical fix, real leverage.

**Exemptions.** Conversation-residue captures, retrospective working notes, and exploratory memos do not need the header. The threshold is "do other documents cite this for normative claims about current state?" If yes, header. If no (e.g., a working note nobody depends on), skip.

## Marking discipline within a document

Sections or paragraphs that mix contract / theory / findings claims should mark which is which. The mechanism spec's drift came partly from mixing all three without distinguishing.

- **Contract:** what the code currently guarantees. Cite (Rule 1).
- **Theory:** why the architecture should work; intended behavior; future direction. Cite a memo or working note.
- **Findings:** empirical observations from runs. Cite a findings note.

Plain prose can serve any of the three; the marking is for when the claim type isn't obvious from context. The mechanism spec's `**Caveat:**` and `**V1 default:**` patterns in §2.1 and §2.7 are existing examples of this discipline; the convention here just names what was already happening informally.

## What this is not

Not a governance policy. Not a pre-commit checklist. Not a document hierarchy. Not a five-step process. Two rules and a marking convention. Heavier process trades cycle time for over-formalized claims and is the wrong intervention at this project stage.

## Adoption

Apply to *new* substantive documents from 2026-05-11 forward. Existing documents are not retrospectively required to carry the header — the cost-benefit doesn't justify a sweep. When an existing document is materially edited or when a new finding invalidates one of its claims, add the header at that edit.

The mechanism spec (`docs/superpowers/specs/2026-05-10-mechanism-specification.md`) already carries `Status`, `Authority` (via "Authoritative for") and `Depends on` (via the lineage block) informally; adding `Invalidated by` and `Last reconciled with code` at next edit is the path of least resistance.
