---
description: Adversarially interrogate a plan, spec, or topic one question at a time — convergent counterpart to brainstorm
arguments:
  - name: target
    description: "Spec/plan path, a topic in quotes, or empty to detect from context"
    required: false
  - name: bound
    description: "Limit interrogation to N decision branches (used by orchestrate Step 0.5 for a quick gate)"
    required: false
    default: null
  - name: no-capture
    description: "Skip writing a GRILL spec file; return decisions inline (used by embedded callers like orchestrate Step 0.5)"
    required: false
    default: false
  - name: yes
    description: "Non-interactive: auto-accept every Recommended answer, emit zero AskUserQuestion prompts (alias --non-interactive)"
    required: false
---

# /craft:grill — Interrogate Before Building

Convergent counterpart to `/craft:workflow:brainstorm`. brainstorm is **divergent** — it
GENERATES options and expands the space. grill is **convergent** — it INTERROGATES a position
to find gaps, contradictions, and unresolved dependencies before you implement.

Use grill to stress-test a spec/plan (or a bare topic) until every branch of the design tree is
resolved, then capture the locked decisions as a durable ledger that feeds `/craft:plan` → `/do`.

## When Invoked

### Step 1: Resolve the target

- **Path argument** → load that artifact (spec/plan/ORCHESTRATE/diff) and interrogate it.
- **Quoted topic** → sketch a 3–5 bullet skeleton, show it, then interrogate the skeleton.
- **Empty** → detect from `.STATUS`, branch name, and recent commits; confirm the target before grilling.

### Step 2: Codebase-first sweep (read-then-confirm)

Before asking anything, read repo evidence (`.STATUS`, `git log`, `docs/specs/*`, `commands/`,
`~/.claude/settings.json` when relevant) and PRE-ANSWER every branch you can. Each pre-answer
becomes the **Recommended:** line on its question — shown, never silently skipped, so the user
can override.

### Step 3: The grill loop (deliberate, one question at a time)

Follow the grill-me directives:

> Interview the user relentlessly about every aspect until shared understanding. Walk each branch
> of the design tree, resolving dependencies one-by-one. For EACH question provide a
> **Recommended:** answer. Ask **one question at a time**. If a question can be answered by
> exploring the codebase, explore the codebase instead.

**Why one-at-a-time free-text and NOT AskUserQuestion batches:** decision-tree fidelity is the
point — each answer reshapes the next question. This is a deliberate exception to craft's
AskUserQuestion-batch convention; do not "fix" it to batches.

**Halt:** the user enters the sentinel `/done` (or empty-enter) at any question → go to Step 4.
Do NOT use the bare word "stop" — it can be a legitimate answer. If `--bound N` was given, stop
after N resolved branches. Otherwise continue until every branch resolves.

**Milestone checkpoints (ADHD-friendly):** every 5 resolved branches, pause with an
AskUserQuestion: "keep going / wrap up now / show ledger so far" (reuses brainstorm's milestone
pattern). This is the ONE place embedded AskUserQuestion is allowed inside the otherwise
free-text loop — for progress, not for the questions themselves.

**After each resolved branch:** append it to the ledger immediately (Step 4 helper) so a
crash/compaction never loses decisions.

### Step 4: Capture (durable, own file, cross-linked)

**If `--no-capture`** (embedded callers like orchestrate Step 0.5): skip all file writes; return
the locked decisions inline to the caller. No `GRILL-*` file is created.

Otherwise grill writes its own file and never rewrites a brainstorm SPEC body:

```python
from commands.utils.grill_ledger import (
    resolve_ledger_path, spec_crosslink, add_backlink, append_decision)
path = resolve_ledger_path(topic, date, "docs/specs")   # GRILL-<topic>-<date>.md
link = spec_crosslink(topic, "docs/specs")              # latest brainstorm SPEC for this slug, or None
# write the GRILL header (include `link` if present), the decision ledger, and an ## Open Questions section
if link:
    add_backlink(os.path.join("docs/specs", link), os.path.basename(path))  # idempotent, atomic
```

Each resolved branch is appended live via `append_decision`. The brainstorm SPEC, if any, is only
ever touched by the single idempotent back-link.

### Step 5: Handoff

Offer (one-directional into the planning spine):
`/craft:plan` tier 4 (plan-orchestrator) → `ORCHESTRATE-*.md` → `/craft:do` / `/craft:orchestrate`.
grill never executes — it interrogates and hands the locked artifact forward.
