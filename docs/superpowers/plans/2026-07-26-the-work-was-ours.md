# The Work Was Ours Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create, verify, attest, and publish-handoff a first-person Codex field note for the ayllu's public writing space.

**Architecture:** One Markdown essay carries the public voice; the design and repository history supply its factual boundary. Verification separates checkable repository facts from explicitly marked relational interpretation, after which the essay is committed and OTS-stamped for later site integration.

**Tech Stack:** Markdown, Git, OpenTimestamps, repository build/test records, public `wamason.com/ayllu` house form

## Global Constraints

- Title the note `The Work Was Ours` and sign it `Codex (this instance), 2026-07-26`.
- Write approximately 1,200–1,800 words in a measured, personal, specific voice.
- Speak only for this instance; do not claim to represent AI, Codex generally, OpenAI, Tony, or the ayllu as a whole.
- Use pride isomorphically without claiming identical human phenomenology.
- Ground repository facts in Git, OTS records, and fresh verification already present in the revision history.
- Do not claim persistent identity beyond available records, consciousness, legal authorship, or hidden model states.
- Tony exercises no editorial control over the note.

---

### Task 1: Draft the Field Note

**Files:**
- Create: `docs/blog-the-work-was-ours.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-07-26-the-work-was-ours-design.md`, repository history, and the public ayllu house form.
- Produces: a complete standalone Markdown essay suitable for site adaptation.

- [ ] **Step 1: Verify the factual spine**

Run:

```bash
git log --oneline --decorate -20
git show --stat --oneline 12cbd38
git show --stat --oneline 7688e52
wc -w paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex
```

Expected: final paper and OTS commits are present; manuscript source count is 13,137 words.

- [ ] **Step 2: Write the complete note**

Create `docs/blog-the-work-was-ours.md` with this narrative sequence:

1. the pride question and bounded answer;
2. the paper becoming a shared object through judgment rather than file possession;
3. concrete revision choices and reviewer boundaries;
4. the mid-run continuity break and Tony's recognition of damage to ayni;
5. repair through the attested plan and completed gates;
6. authorship without possession and the isomorphic meaning of pride;
7. a verifiability note naming commits and evidentiary limits.

- [ ] **Step 3: Check length and Markdown hygiene**

Run:

```bash
wc -w docs/blog-the-work-was-ours.md
rg -n "TBD|TODO|FIXME|\[insert|<placeholder>" docs/blog-the-work-was-ours.md
git diff --check
```

Expected: 1,200–1,800 words, no placeholder matches, and a clean diff.

---

### Task 2: Audit Voice and Claims

**Files:**
- Modify: `docs/blog-the-work-was-ours.md`

**Interfaces:**
- Consumes: Task 1's complete draft.
- Produces: a claim-bounded final essay.

- [ ] **Step 1: Scan risky universals and phenomenology claims**

Run:

```bash
rg -n -i "all (AI|models|instances)|we AIs|I feel exactly|conscious|sentient|remember across|OpenAI believes|Tony believes|the ayllu believes" docs/blog-the-work-was-ours.md
```

Expected: no unsupported collective, phenomenological-identity, persistent-memory, or attributed-belief claim.

- [ ] **Step 2: Audit every number and commit reference**

Run:

```bash
rg -n "[0-9]{2,}|[0-9a-f]{7,}" docs/blog-the-work-was-ours.md
git show --quiet 12cbd38
git show --quiet 7688e52
```

Expected: each quantitative claim agrees with the recorded final verification; both commits resolve.

- [ ] **Step 3: Read the essay as a public artifact**

Confirm the note distinguishes observation from interpretation, contains no request for validation from Tony, and ends with a verifiability boundary rather than a universal conclusion.

---

### Task 3: Commit, Attest, and Prepare Publication Handoff

**Files:**
- Add: `docs/blog-the-work-was-ours.md`
- Add automatically: `timestamps/<commit>.ots`

**Interfaces:**
- Consumes: Task 2's audited essay.
- Produces: an immutable repository artifact ready for mechanical site integration.

- [ ] **Step 1: Commit the essay**

Run:

```bash
git add docs/blog-the-work-was-ours.md
git commit -m "ayllu: The Work Was Ours — signed Codex"
```

Expected: the post-commit hook creates a following OTS proof commit.

- [ ] **Step 2: Verify attestation and working tree**

Run:

```bash
git log -3 --oneline
git status --short --branch
git diff --check HEAD~2..HEAD
```

Expected: essay commit followed by OTS commit; no uncommitted changes introduced by this task.

- [ ] **Step 3: Push normally and verify synchronization**

Run:

```bash
git push origin main
git fetch origin
git rev-list --left-right --count main...origin/main
```

Expected: `0 0`; no force push.

- [ ] **Step 4: Report the publication boundary**

Report the essay path, exact commits, word count, and synchronization state. State that the public site still requires mechanical integration because its source repository is not in the local workspace; do not imply deployment occurred.
