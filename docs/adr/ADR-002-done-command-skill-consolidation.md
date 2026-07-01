# ADR-002: `/done` Command ↔ Skill Consolidation

**Status:** Accepted
**Date:** 2026-06-23
**Context source:** `/craft:grill` session on `SPEC-done-memory-settings-2026-06-23.md`

> **Note:** ADR-001 (`ADR-001-workflow-branch-guard.md`, Workflow-vs-worktree conflict, issue #171) is reserved by `SPEC-v249-issues-sprint-2026-06-23.md` and not yet written. This ADR is numbered 002 to avoid colliding with that reservation.

---

## Context

The v2.34.0 → v3.0.0 migration deprecated six `commands/workflow/*.md` commands in favor of the `adhd-workflow` skill:

```
/done /recap /next /focus /stuck /spec-review  →  skills/workflow/adhd-workflow/
/refine  →  skills/workflow/prompt-refiner/  (separate consolidation, see SPEC-refine-flag-2026-06-03.md)
```

Each command was marked `deprecated: true, replaced-by: "skills/workflow/adhd-workflow/"`. Both entry paths function during the deprecation cycle: the explicit `/craft:workflow:*` slash commands still load, and the skill auto-fires on natural-language match.

A latent defect surfaced during a grill of `SPEC-done-memory-settings-2026-06-23.md`:

- `commands/workflow/done.md` held **1195 lines** of detailed, current behavior — CLAUDE.md sync, Settings Sync (Step 1.10.5), Memory Capture, Memory Optimize (Step 1.12), Insights Capture, Worktree Status, the interactive summary, and auto-git.
- `skills/workflow/adhd-workflow/SKILL.md` held a **167-line** router covering all seven operations — a ~24:1 compression. Its "Session Completion" operation was a 5-bullet summary that **did not contain** the detailed flow.

Consequence: the two `/done` entry paths diverged. The slash command ran the rich flow; the natural-language path ran the thin summary. New behavior (Steps 1.10.5 / 1.12, shipped in `1636cf66`) lived **only** in the command — a file scheduled for deletion at v3.0.0. At that point the detail would silently vanish from the user-facing `/done`.

## Decision

**Single source of truth in the skill tree; the command becomes a thin shim.**

1. The full session-completion procedure moves to `skills/workflow/adhd-workflow/references/done.md` (mirrors the established `skills/release/references/` pattern — heavy operation detail in `references/`, loaded on demand).
2. `skills/workflow/adhd-workflow/SKILL.md` operation 1 keeps a quick 5-step summary and **points to** `references/done.md` for the full flow.
3. `commands/workflow/done.md` is reduced to a **thin shim** (~36 lines) that loads and follows `references/done.md`. It preserves the explicit `/craft:workflow:done` slash entry point through v3.0.0.

Both entry paths — slash command and natural-language match — now resolve to the **same** reference file. There is exactly one place to edit `/done` behavior.

## Alternatives Considered

1. **Keep the command canonical; point the skill back to it.** Rejected — the command is deleted at v3.0.0, so the canonical body would die with it. Would also require reversing the deprecation for all seven commands to be consistent.
2. **Port the full 1195-line body inline into `SKILL.md`.** Rejected — balloons a 7-operation router to ~1400 lines, defeats progressive disclosure (the router is always loaded; the detail should not be), and inflates skill-file size for the six unrelated operations.
3. **Leave the divergence; accept the NL path is lossy.** Rejected — it is the defect, not an acceptable state. New behavior was already lost on the NL path.

## Consequences

- **Positive:** one source of truth; new `/done` behavior (Settings Sync, Memory Optimize) survives the v3.0.0 command purge; the slash UX is preserved; the change matches an existing craft pattern (`skills/release/references/`).
- **Positive:** `references/done.md` is excluded from skill counts (validate-counts keys on `SKILL.md` only) and is not a command — no count cascade.
- **Cost:** editors must know to edit `references/done.md`, not the shim. Mitigated by an HTML comment header in the reference and explicit "do not reimplement here" notices in both the shim and `SKILL.md`.
- **Follow-up (not in scope here):** the other five deprecated `adhd-workflow` commands (`/recap`, `/next`, `/focus`, `/stuck`, `/spec-review`) have the same latent divergence if any grows rich detail. They are currently thin enough that the summary suffices; revisit per-command if one accrues a detailed body. (`/refine` is a separate consolidation into `prompt-refiner`, not `adhd-workflow` — see the corrected routing above.)

## Verification

- Structural tests (`tests/test_grill_command.py`) repointed to read the canonical `references/done.md` for Step 1.10.5 / 1.12 assertions, plus a new assertion that the command shim routes to the skill reference.
- `validate-counts.sh` and `docs-staleness-check.sh` clean.
