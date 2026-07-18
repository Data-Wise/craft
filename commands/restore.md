---
description: /restore - Restore Git & Session Context
---

# /restore - Restore Git & Session Context

> **This command is a thin shim.** The canonical behavior lives in two skills:
> git-activity recap (`dev/git` skill, Operation 7) and `.STATUS`-based session
> recap (`adhd-workflow` skill, §2 "Context Restoration"). This file exists to
> give both a single, discoverable combined entry point — see
> [`docs/specs/SPEC-craft-restore-2026-07-17.md`](../docs/specs/SPEC-craft-restore-2026-07-17.md).

## Usage

```bash
/craft:restore              # default mode
/craft:restore detailed     # full verbosity on the git-activity portion
/craft:restore summary      # minimal verbosity on the git-activity portion
```

## When invoked

1. **Session state:** run the `adhd-workflow` skill's §2 "Context Restoration
   (recap)" operation — `.STATUS` state, git activity (last 48h), open PRs/issues,
   planning files, Obsidian flow status. This is single-verbosity; the mode
   argument does not change it.
2. **Git activity:** run the `dev/git` skill's Operation 7 (git activity recap) —
   today's/this week's commits, branch ahead/behind, unpushed work, open PRs —
   using whichever mode (`default` | `detailed` | `summary`) was passed.
3. **De-dupe on presentation, not on source logic:** both operations independently
   surface recent commits and open PRs. Present one combined git-activity block
   (from step 2, mode-aware) rather than printing the same commits/PRs twice.
   Session-only content from step 1 (`.STATUS` next-action/blockers, planning
   files, Obsidian flow status) goes in its own section.
4. Present as one combined, ADHD-friendly summary: git state first, session state
   second, a single "what's next" line last.
5. **Do not reimplement either operation here.** Any change to git-recap logic
   belongs in `dev/git`; any change to session-recap logic belongs in
   `adhd-workflow`. This file is routing only.

## Read-only

`/craft:restore` never writes `.STATUS`, never commits, never syncs anything — it
only reads and reports. There is no `--sync` flag (unlike `savant:restore`, which
optionally applies diff-gated doc updates). If write-back is ever wanted, that is
a separate, explicitly-scoped addition — not part of this command today.

## Relationship to `/craft:finish` and `/craft:next`

`/craft:finish` (session completion) *produces* the `.STATUS` state this command
*consumes*. `/craft:next` suggests the next task from that same state. `/craft:restore`
is the read-only "where did I leave off" opener that precedes both — run it first
when returning to a project after a break.
