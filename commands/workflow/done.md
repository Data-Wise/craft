---
description: /done - Session Completion & Context Capture
category: workflow
deprecated: true
replaced-by: "skills/workflow/adhd-workflow/"
---

# /done - Session Completion & Context Capture

> **This command is a thin shim.** The canonical behavior lives in the
> `adhd-workflow` skill's Session Completion operation. This file exists only to
> preserve the explicit `/craft:workflow:done` slash entry point through the
> v2.34.0 → v3.0.0 migration (see
> [ADR-002](../../docs/adr/ADR-002-done-command-skill-consolidation.md)).

## When invoked

1. **Load the canonical procedure:** read
   [`skills/workflow/adhd-workflow/references/done.md`](../../skills/workflow/adhd-workflow/references/done.md)
   and follow it exactly. That reference is the single source of truth for the
   full session-completion flow — CLAUDE.md sync (Step 1.10), **Settings Sync
   (Step 1.10.5)**, Memory Capture (Step 1.11), **Memory Optimize (Step 1.12)**,
   Insights Capture (Step 1.13), Worktree Status (Step 1.14), the interactive
   summary (Step 2), and auto-git (Step 3.5).

2. **Do not reimplement here.** Any change to `/done` behavior must be made in
   the reference file, never duplicated into this shim. Keeping the body in one
   place is the entire point of [ADR-002](../../docs/adr/ADR-002-done-command-skill-consolidation.md).

## Why this is a shim

`/done` is one of seven `commands/workflow/*.md` commands being consolidated into
the `adhd-workflow` skill. Both entry paths — the explicit `/craft:workflow:done`
slash command and the skill's natural-language match ("wrap up", "I'm done") —
now route to the same reference file. At v3.0.0 this shim may be retired; the
canonical body in the skill survives.
