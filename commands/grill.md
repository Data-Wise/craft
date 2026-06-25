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
  - name: refine
    description: "Refine the topic via prompt-refiner BEFORE grilling. Default-ON for a quoted/bare topic; SKIPPED when the argument is a path (a spec/plan file — nothing to refine). --no-refine to disable."
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

When the argument is a quoted/bare topic, run prompt-refiner on it first (default-on; `--no-refine` skips). When the argument is a path, skip refine entirely.

Before asking anything, read repo evidence (`.STATUS`, `git log`, `docs/specs/*`, `commands/`,
`~/.claude/settings.json` when relevant) and PRE-ANSWER every branch you can. Each pre-answer
becomes the **Recommended:** line on its question — shown, never silently skipped, so the user
can override.

### Step 3: The grill loop (deliberate, one question at a time)

Ask **one question per AskUserQuestion call** (NOT 4-question batches — one branch at a time
preserves decision-tree fidelity). For EACH question:

- option[0] is the **Recommended** answer, labelled and reasoned;
- EVERY option carries a one-line **consequence** of choosing it;
- the implicit "Other" free-text path stays open for answers off the menu.

Each answer reshapes the next question. **Halt** on `/done` or empty-enter. `--bound N` stops after
N branches. `--yes` / `--non-interactive`: emit ZERO AskUserQuestion calls — auto-pick every
Recommended, log each pick, and proceed straight to capture. `--yes` cascades: the
prompt-refiner auto-accepts AND the interactive loop is suppressed — one flag, fully headless.

**Milestone checkpoints (ADHD-friendly):** every 5 resolved branches, pause with an
AskUserQuestion: "keep going / wrap up now / show ledger so far" (reuses brainstorm's milestone
pattern).

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
