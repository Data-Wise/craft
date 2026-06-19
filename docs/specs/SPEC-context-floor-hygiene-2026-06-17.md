# SPEC: Context-Floor Hygiene via `/done` (Skeleton)

**Status:** draft — skeleton (sequenced after `SPEC-orchestrate-token-efficiency-2026-06-17.md`)
**Created:** 2026-06-17
**From Brainstorm:** interactive `/workflow:refine` session — follow-on to orchestrate
token-efficiency; "bake CLAUDE.md + memory optimize/sync into the done workflow"
**Author:** dt + Claude

---

## Overview

Lever A in the token-efficiency spec is a **point fix with a leak**: trimming the
~5,200-token context floor (root `CLAUDE.md` + `craft/CLAUDE.md` + `MEMORY.md`) is undone
over time because `MEMORY.md` grows every session by design (105 entries today, +1–3 per
session). This spec converts the one-time trim into a **sustained floor** by wiring
optimize/sync into session completion (`/craft:workflow:done`).

Because the floor is inherited by **every subagent in every orchestrate run**, holding it
down is the single biggest *long-term* token lever — but it must be done safely.

### Core principle: advisory, not automatic; split by risk

`CLAUDE.md` and memory are two systems with opposite risk profiles:

- **CLAUDE.md** — craft already ships deterministic tooling (`claude_md_sync.py`,
  `claude_md_optimizer.py`, `claude-md-budget-check.sh`) with a budget config. Safe to
  wire in.
- **Memory** — has **no optimizer**; the memory rules deliberately require human curation
  ("check for duplicates, delete ones that turn out wrong"). Auto-pruning is unsafe — an
  optimizer cannot judge which of 105 entries is now stale, and recalled memories reflect
  what was true when written.

---

## Primary User Story

**As a** craft user finishing a session,
**I want** `/done` to keep the context floor lean — syncing CLAUDE.md and surfacing memory
cleanup candidates — without silently rewriting files or deleting learnings,
**so that** orchestrate's per-subagent context tax doesn't creep back up over time.

---

## Scope (skeleton — to be detailed when this spec is activated)

### CLAUDE.md — safe to wire into `/done`

- Detect budget overage + drift via the existing `claude_md_*` tooling.
- **Detect-and-offer** mode: `/done` reports overage/drift and offers to sync, or only
  auto-syncs behind an explicit `--sync` flag. **Not** a silent per-session commit.

### Memory — surface, do not prune

- Flag *candidates* for human confirmation: duplicate slugs, entries older than N months,
  entries whose named file/flag no longer exists (dangling refs).
- **Never auto-delete.** Output is a review list, not an edit.

### Non-goals

- No automatic memory deletion.
- No silent CLAUDE.md commits on every `/done`.
- No coupling that makes `/done` fail when the optimizer errors (advisory only).

---

## Dependencies

- **Depends on** `SPEC-orchestrate-token-efficiency-2026-06-17.md` Phase 0 — the token
  report is used to **trend floor size over sessions** and confirm `/done` holds the line.
- Reuses existing craft utilities: `claude_md_sync.py`, `claude_md_optimizer.py`,
  `claude-md-budget-check.sh`; budget config in `.claude-plugin/config.json`.

---

## Open Questions (resolve at activation)

- Default behavior: advisory-offer vs. `--sync`-gated — which is the `/done` default?
- Memory staleness threshold (N months) and how to detect dangling file/flag refs cheaply.
- Whether the memory candidate list lives in `/done` output or a separate
  `/craft:docs:claude-md:*`-style command.
