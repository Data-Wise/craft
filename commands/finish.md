---
description: /finish - Session Completion & Context Capture
---

# /finish - Session Completion & Context Capture

> **This command is a thin shim.** The canonical behavior lives in the
> `adhd-workflow` skill's Session Completion operation. This file exists only to
> preserve the explicit `/craft:finish` slash entry point (renamed from
> `/craft:done` on 2026-07-17 — see
> [ADR-006](../docs/adr/ADR-006-done-renamed-to-finish.md), which supersedes
> [ADR-002](../docs/adr/ADR-002-done-command-skill-consolidation.md) on
> naming only; ADR-002's shim-vs-skill rationale is unchanged).

## When invoked

1. **Load the canonical procedure:** read
   `${CLAUDE_PLUGIN_ROOT:-.}/skills/workflow/adhd-workflow/references/done.md`
   and follow it exactly. That reference is the single source of truth for the
   full session-completion flow — CLAUDE.md sync (Step 1.10), **Settings Sync
   (Step 1.10.5)**, Memory Capture (Step 1.11), **Memory Optimize (Step 1.12)**,
   Insights Capture (Step 1.13), Worktree Status (Step 1.14), the interactive
   summary (Step 2), and auto-git (Step 3.5).

2. **Do not reimplement here.** Any change to `/finish` behavior must be made in
   the reference file, never duplicated into this shim. Keeping the body in one
   place is the entire point of [ADR-002](../docs/adr/ADR-002-done-command-skill-consolidation.md).

## Why this is a shim

`/finish` (renamed from `/done`) routes to the `adhd-workflow` skill's Session
Completion operation. Both entry paths — the explicit `/craft:finish` slash
command and the skill's natural-language match ("wrap up", "I'm done") — route
to the same reference file.
