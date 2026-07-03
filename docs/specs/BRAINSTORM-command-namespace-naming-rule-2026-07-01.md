# BRAINSTORM: Command-Namespace Naming Rule — Worth Doing?

**Date:** 2026-07-01 · **Depth:** default · **Focus:** arch
**Backlog item:** `.STATUS` — "Command-namespace naming rule" (`namespace:command --flags`).
**User asked:** "now that we're refactoring, do the naming rule; what do you think?"

---

## My verdict (up front)

**Don't do the plugin-wide rename. Codify the *principle* instead, and apply it opportunistically.**

The rename is churn for near-zero benefit: craft is already ~90% consistent, there's no deep-nesting
sprawl to fix, and (per this session's bloat grill) renaming doesn't cut resting tokens unless it
cuts command *count* — which only a few genuine variant-collapses do.

---

## Grounding (measured)

- **craft is already flat & consistent:** 80 commands are `namespace:command` (depth-2), 9 are bare
  (depth-1). **No depth-3 sprawl** to flatten. The backlog's "depth-2 but inconsistent" framing
  overstated the problem.
- **The real inconsistency is tiny:** a handful of commands mix colon-subcommands with *positional
  sub-verbs* — `orchestrate` (status/timeline/abort), `dist/{pypi,marketplace,homebrew}`. That's
  ~4–5 commands, not a plugin-wide issue.

## The principle that IS right (and worth keeping)

The proposed `namespace:command --flags` is really a CLI-design question, and the correct rule is:

> **Subcommand (colon) when it's a distinct operation with its own contract; flag when it's a
> variant/modifier of the same operation.**

- `git:worktree`, `git:sync`, `git:status` = **distinct operations** → correctly colons. Collapsing
  them into `git --worktree --sync` would be a terrible fat mega-command.
- `orchestrate:plan --output orchestrate-only|worktree|dispatch` = **variants of one operation** →
  correctly a flag. (Grill branch 2 of the dispatch-mode design already endorsed exactly this.)

## Why blanket `namespace:command --flags` is wrong

`★ Insight ─────────────────────────────────────`

- **Fat mega-commands.** Collapsing distinct operations into one command's flags means one huge body
  parsing all flag combos + validation logic — the exact anti-pattern the orchestrate-family audit
  is removing.
- **Lost per-command frontmatter.** Each command carries its own `description`, `argument-hint`,
  model routing, allowed-tools. Flags can't hold those — you'd lose per-operation config.
- **Discoverability.** Claude Code discovers by *file → command name*; flags aren't tab-completed or
  listed the way command names are. Fewer named commands = harder to find capability.

`─────────────────────────────────────────────────`

## Token reality (from this session's bloat grill)

Renaming a command changes its *name string*, not the resting cost meaningfully. Resting cost is
description count × length. A rename that DOESN'T cut command count saves ~0 tokens. Only a genuine
*variant-collapse* (4 commands → 1 + flags) cuts count — and there are only a few such candidates
(the orchestrate family, already being handled via `--output`).

## What to actually do

### Quick Win (< 30 min)

1. **Codify the verb-vs-flag principle** as a one-paragraph convention (governance rule or a
   CLAUDE.md line): distinct operation → subcommand; variant → flag. Cheap, durable, guides all
   future authoring without touching a single existing command.

### Medium (opportunistic, not a project)

- [ ] **Apply the principle only when already touching a namespace.** The orchestrate-family wave-1
  already collapses variants via `--output` — that's the pattern, applied where it pays. Don't open
  a standalone rename project.

### Explicitly NOT doing

- ❌ Plugin-wide rename of all 89 commands — churn, ~30-file count cascade per change,
  discoverability loss, ~0 token benefit.
- ❌ Collapsing distinct operations into flags — fat mega-commands.

## Risks of doing the rename anyway

- **Count cascade × N** — every renamed command re-triggers the ~30-file count/doc sweep.
- **Reference rot** — the consolidation audit already showed every command name is referenced in
  hub/routing/docs; renames break all of them.
- **Muscle-memory break** — users' existing `/craft:git:status` habits.

## Recommended Next Step

→ **Adopt the one-paragraph verb-vs-flag convention; skip the rename.** If you want it enforced,
add it as a governance rule (advisory) so new commands follow it. The only "refactor" worth doing
here is the orchestrate-family `--output` collapse you're already planning — everything else is
churn. This is the *fourth* time this session that measuring beat the intuition to refactor.
