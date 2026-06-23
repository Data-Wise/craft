# GRILL: /done Command ↔ Skill Consolidation

**Date:** 2026-06-23
**Targets grilled:** `SPEC-done-memory-settings-2026-06-23.md`, `SPEC-v249-issues-sprint-2026-06-23.md`
**Outcome:** 1 branch resolved → [ADR-002](../adr/ADR-002-done-command-skill-consolidation.md) + hybrid refactor shipped.

## Open Questions (deferred from the grill)

These branches were surfaced in the codebase sweep but **not** resolved this session — they belong to the v2.49.x sprint, not this consolidation:

- **verify_caveats.py interface mismatch** — spec body declares `run_all_gates(...)`; agent-findings declare `verify_caveats(...)`. Pick one before PR A.
- **SessionStop vs Stop hook naming** — spec says "SessionStop hook"; agent-2 calls `done-reminder.sh` a "Stop hook". Confirm the actual Claude Code hook event name or the PR-B hook never fires.
- **PR-B hook ships outside the repo** — `~/.claude/hooks/session-facet.sh` lives outside `craft/`, but its tests sit in `craft/tests/`. Resolve the distribution/test story.
- **Check 5 scope creep** — folding #184 (plugin version match) into the homebrew gate may reopen scope the sprint deferred.

## Decision Ledger

| # | Branch (question) | Resolution |
|---|-------------------|------------|
| B1 | Where is /done's canonical body — the deprecated command or the replacement skill, and which do we keep? | Hybrid (Option A). Moved the 1195-line body to skills/workflow/adhd-workflow/references/done.md as the single source of truth. SKILL.md operation 1 and the /craft:workflow:done command shim both route to it. Confirmed by SKILL.md Integration note: both entry paths work until v3.0.0; deleting the command at v3.0.0 would have silently dropped the shipped Steps 1.10.5 (Settings Sync) and 1.12 (Memory Optimize). Rationale recorded in ADR-002-done-command-skill-consolidation.md. |
