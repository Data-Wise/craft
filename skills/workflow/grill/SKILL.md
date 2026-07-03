---
name: grill
description: This skill should be used when the user asks to "grill", "interrogate", "stress-test a spec/plan", "adversarially review a proposal", or invokes /craft:grill. Convergent counterpart to brainstorm — interrogates a spec/plan/topic one question at a time to surface gaps, contradictions, and unresolved dependencies before implementation, then captures a durable GRILL-*.md decision ledger that feeds /craft:plan → /do. For GENERATING options (divergent ideation), use the brainstorm skill instead.
---

# Grill — Interrogate Before Building

Convergent counterpart to `brainstorm`. Brainstorm is **divergent** — it GENERATES options and
expands the space. Grill is **convergent** — it INTERROGATES a position to find gaps,
contradictions, and unresolved dependencies before you implement.

Use grill to stress-test a spec/plan (or a bare topic) until every load-bearing branch of the
design tree is resolved, then capture the locked decisions as a durable ledger that feeds
`/craft:plan` → `/do`.

## Boundary With Adjacent Skills

| Skill | Role |
|-------|------|
| **grill** (this) | Convergent — interrogates a position, captures a `GRILL-*.md` decision ledger |
| `brainstorm` | Divergent — generates options, captures a `BRAINSTORM`/`SPEC` |
| `prompt-refiner` | Sharpens a bare/quoted topic before grilling (default-on for topics) |
| `plan-orchestrator` / `--orch` | Turns the locked ledger + spec into an ORCHESTRATE artifact |

## Inputs (flags owned by the `commands/grill.md` shim)

- **target** — spec/plan path, a quoted topic, or empty (detect from context).
- **--bound N** — stop after N decision branches (quick gate; used by orchestrate Step 0.5).
- **--no-capture** — skip writing a `GRILL-*` file; return decisions inline (embedded callers).
- **--yes / --non-interactive** — auto-accept every Recommended answer, zero AskUserQuestion prompts.
- **--refine / --no-refine** — refine a topic via `prompt-refiner` before grilling (default-on for topics; skipped for a path).
- **--no-tests / --no-docs** — suppress the auto-emitted test-plan / Documentation sections.

## Procedure

### Step 1: Resolve the target

- **Path argument** → load that artifact (spec/plan/ORCHESTRATE/diff) and interrogate it.
- **Quoted topic** → sketch a 3–5 bullet skeleton, show it, then interrogate the skeleton.
- **Empty** → detect from `.STATUS`, branch name, and recent commits; confirm the target before grilling.

### Step 2: Codebase-first sweep (read-then-confirm)

When the argument is a quoted/bare topic, run `prompt-refiner` on it first (default-on;
`--no-refine` skips). When the argument is a path, skip refine entirely.

Before asking anything, explore the codebase — read repo evidence (`.STATUS`, `git log`,
`docs/specs/*`, `commands/`, `~/.claude/settings.json` when relevant) — and PRE-ANSWER every
branch you can. Each pre-answer becomes the **Recommended:** line on its question — shown, never
silently skipped, so the user can override.

### Step 3: Select attack angles (what to interrogate)

Grill is adversarial: interrogate the position's *weaknesses*, not its surface. Consider these
generic angles and attack the ones that apply to THIS target, hardest first:

1. **Weakest recommendation** — the call that looks worst in hindsight; name the cheaper/safer alternative.
2. **Riskiest assumption** — the load-bearing belief that breaks the plan if false. Prioritise **silent** failures (behavior lost, not errors thrown).
3. **Implementation regret** — the step you'd curse mid-build. **Source project-specific traps at runtime from the target project's `CLAUDE.md` / ADRs / memory when a `CLAUDE.md` is present in the target tree** — do NOT hardcode any one project's gotchas here (that would poison grills of other projects).
4. **Benefit honesty** — is any claimed benefit (perf, token, time saved) measured or merely asserted? Separate real levers from wishful ones.
5. **Workflow discipline** — does execution respect the project's *documented* workflow (branch model, test command, verify-before-merge) as stated in its `CLAUDE.md`?
6. **Blast radius** — does the change silently alter a convention or require a doc/drift sweep? Scoped or hidden?
7. **Reversibility & scope creep** — anything irreversible or ballooning past stated scope? Hold vs. proceed?

Angles are **guidance for choosing branches, not a mandatory sweep** — grill stays lightweight.

- **`--bound N`:** pick the **N highest-value angles for this specific target**; a `--bound 2` gate still asks only 2 questions.
- **Unbounded:** stop when the load-bearing branches are resolved — target roughly **5 branches**, not an exhaustive tree. Milestone checkpoints (Step 4) let the user extend.

### Step 4: The grill loop (deliberate, one question at a time)

Ask **one question per AskUserQuestion call** — one-at-a-time fidelity is the point; each answer
reshapes the next question. This is a deliberate exception to craft's AskUserQuestion-batch
convention (NOT 4-question batches). For EACH question:

- option[0] is the **Recommended** answer, labelled and reasoned;
- EVERY option carries a one-line **consequence** of choosing it;
- the implicit "Other" free-text path stays open for answers off the menu.

**Halt** on `/done` or empty-enter. `--bound N` stops after N branches. `--yes` /
`--non-interactive`: emit ZERO AskUserQuestion calls — auto-pick every Recommended, log each
pick, and proceed straight to capture. `--yes` cascades: the prompt-refiner auto-accepts AND the
interactive loop is suppressed — one flag, fully headless.

**Milestone checkpoints (ADHD-friendly):** every 5 resolved branches, pause with an
AskUserQuestion: "keep going / wrap up now / show ledger so far" (reuses brainstorm's milestone
pattern).

**After each resolved branch:** append it to the ledger immediately (Step 5 helper) so a
crash/compaction never loses decisions.

### Step 5: Capture (durable, own file, cross-linked)

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

### Step 6: Handoff

Offer (one-directional into the planning spine):
`/craft:plan` tier 4 (plan-orchestrator) → `ORCHESTRATE-*.md` → `/craft:do` / `/craft:orchestrate`.
Grill never executes — it interrogates and hands the locked artifact forward.

## Do Not

- Reimplement grill logic in the `commands/grill.md` shim — this skill is the single source of truth.
- Hardcode any project's specific gotchas into the attack angles (Step 3) — read the target's
  `CLAUDE.md` at runtime instead.
- Rewrite a brainstorm SPEC's body — only the single idempotent back-link is permitted.
