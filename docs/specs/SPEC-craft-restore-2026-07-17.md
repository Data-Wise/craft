# Spec: `/craft:restore`

**Date:** 2026-07-17
**Status:** DRAFT — awaiting review
**Supersedes:** `git-recap` and `recap` (both deleted 2026-07-09, PR #279)

## Objective

Give craft a single, read-only "restore my context" entry point that combines:

1. **Git-activity recap** — today/this-week commits, branch ahead/behind, unpushed
   work, open PRs (`gh pr list --author @me`). Currently lives undocumented-as-a-command
   in `skills/dev/git/SKILL.md` Operation 7.
2. **`.STATUS`-based session recap** — "what was I doing, what's next" — currently
   lives in the `adhd-workflow` skill.

Today a user has to know to ask for "git recap" and separately for a status/session
recap. `/craft:restore` merges both into one combined output, mirroring the framing
already established by `savant:restore` ("Restore context on a research project").
Success looks like: after a break (new session, new day, context switch back to
this project), one command/one natural-language ask answers "where did I leave off
and what's the state of the repo."

**Explicitly out of scope** (see Boundaries): a cross-plugin `/restore` dispatcher
that would route to `savant:restore` for research projects and `craft:restore` for
dev-tools projects. Investigated this session and confirmed structurally blocked —
craft's `/do`/`/hub` routers cannot dispatch into another plugin's namespace
(`docs/specs/SPEC-craft-native-first-breakup-2026-07-09.md`). That idea would need
its own spec and likely an MCP-level capability, not a craft command.

## Commands

No new build/test tooling — this is a markdown command file plus (if needed) a
small reference doc under an existing skill. Existing repo commands apply:

```
Unit tests:   python3 -m pytest tests/test_craft_plugin.py
Full tests:   python3 -m pytest tests/
Validate counts: ./scripts/validate-counts.sh
Docs staleness:  ./scripts/docs-staleness-check.sh
```

## Project Structure

```
commands/restore.md                          → NEW. Thin-shim root command (this spec's deliverable)
skills/dev/git/SKILL.md                      → Operation 7 (git activity recap) — canonical git-side logic, unchanged
skills/dev/git/references/                   → if the combined output needs new reference detail, add here
skills/workflow/adhd-workflow/                → canonical .STATUS/session recap logic, unchanged
docs/specs/SPEC-craft-restore-2026-07-17.md  → this file
```

No new directories. `commands/restore.md` is the only new file this spec produces.

## Code Style

Follow the existing thin-shim convention exactly — `commands/done.md` is the
template (not `commands/next.md`, which predates the shim pattern and still carries
full inline logic):

```markdown
---
description: /restore - Restore Git & Session Context
---

# /restore - Restore Git & Session Context

> **This command is a thin shim.** The canonical behavior lives in two skills:
> git-activity recap (`dev/git` skill, Operation 7) and `.STATUS`-based session
> recap (`adhd-workflow` skill). This file exists only to preserve an explicit
> `/craft:restore` slash entry point, combining both into one command.

## When invoked

1. Run the `adhd-workflow` skill's §2 "Context Restoration (recap)" operation:
   `.STATUS` state, git activity (last 48h), open PRs/issues, planning files,
   Obsidian flow status.
2. Run the `dev/git` skill's Operation 7 (git activity recap) for the mode-aware
   git slice: today/week commits, branch ahead/behind, unpushed work, open PRs.
   **Known overlap:** both sources independently surface recent git activity and
   open PRs — the shim de-dupes on presentation (one git-activity block, not two),
   it does not run either source's git-fetching logic twice.
3. Present as one combined, ADHD-friendly summary — git state first (mode-aware),
   then session state (single-verbosity), then a single "what's next" line.
4. **Do not reimplement either operation here.** Changes to git-recap logic go in
   `dev/git`; changes to session-recap logic go in `adhd-workflow`.

## Modes

`default` | `detailed` | `summary` apply to the **git-activity portion only**
(`skills/dev/git/SKILL.md` Operation 7, which already implements them).
`adhd-workflow`'s recap operation (§2 "Context Restoration") has no mode support
today — verified 2026-07-17, not assumed — so its output stays single-verbosity
regardless of the mode passed. Adding modes to adhd-workflow's side is explicitly
deferred (see Open Questions).
```

No `deprecated`/`replaced-by` frontmatter — this is a net-new command name, not a
migration shim for a name that already existed.

## Testing Strategy

Docs-only change (a command markdown file, no executable logic of its own) — per
`pre-pr-testing.md`'s tier table, the minimum bar is lint + count/staleness
validators, not the full suite:

- `./scripts/validate-counts.sh` — new root command shifts root-command count; confirm
  it's picked up correctly (root-level commands aren't counted by `_cmd_cat()`, so this
  should be a no-op, but verify).
- `./scripts/docs-staleness-check.sh` — confirm no stale cross-references are introduced.
- Manual dogfood: run `/craft:restore` (and `/craft:restore detailed`, `/craft:restore
  summary`) in this repo and confirm real output — git state + `.STATUS` state — comes
  back correctly for both modes. This is the E2E evidence required before PR per
  `e2e-before-pr.md` (prose-skill / command-routing change: trace real invocations,
  quote the transcript).
- Sweep `commands/hub.md` and `docs/commands/hub.md` for stale "git recap"
  phrasing (at least 3 known lines from this session's earlier REFCARD audit) and
  point them at `/craft:restore` instead.

## Boundaries

- **Always do:** keep all logic in the two source skills; the command file is
  routing only. Run the doc-staleness/count validators before PR.
- **Ask first:** any decision to eventually deprecate/redirect `skills/dev/git/SKILL.md`
  Operation 7's own direct invocation path in favor of routing everything through
  `/craft:restore`; any decision to add a `--sync` flag later (explicitly deferred,
  see Open Questions).
- **Never do:** implement the cross-plugin `/restore` → `savant:restore` dispatcher
  as part of this work (confirmed out of scope, needs its own spec); add write/sync
  behavior to this command (it is read-only by design, per the grill decision below).

## Success Criteria

- `/craft:restore` (default mode) runs and prints a combined git-activity +
  `.STATUS`-session summary in one output, in this repo.
- `detailed` and `summary` modes both work and visibly differ in verbosity.
- No `--sync` or any write behavior exists on this command.
- `commands/hub.md` / `docs/commands/hub.md` no longer reference the deleted
  `git-recap`/`recap` commands.
- `validate-counts.sh` and `docs-staleness-check.sh` both pass clean after the change.

## Locked Decisions (from grill, 2026-07-17)

1. **Scope:** combine BOTH git-activity recap and `.STATUS`-based session recap into
   one command with one combined output (not two separate sub-outputs a user has to
   mentally merge).
2. **`--sync` flag:** NOT included. Read-only only, matching `savant:restore`'s
   default (non-`--sync`) behavior, not its optional write path.
3. **Output modes:** keep the existing `default` / `detailed` / `summary` 3-mode
   shape already defined in `skills/dev/git/SKILL.md` Operation 7 — no new modes.

## Open Questions

- Should a future `--sync` mode (mirroring `savant:restore --sync`'s diff-gated,
  no-commit doc-sync behavior) ever be added to `craft:restore`? Deferred — no
  current use case identified; revisit if one emerges.
- Should the cross-plugin dispatcher idea (`/restore` routing to `savant:restore` vs
  `craft:restore` by project kind) get its own spec later? Not this spec's job to
  decide — flagged for a future, separate proposal if the user wants to pursue it.
