# SPEC: Fix Dead `/craft:dist:marketplace` References (6 Files)

**Date:** 2026-07-29 · **Status:** DEFERRED — verified but not implemented in this pass
**Repo:** `craft`
**Precedent:** commit `0aef1ca71` (`docs: fix remaining stale command references and workflow: legacy namespace`) — fixed the equivalent `/craft:dist:curl-install` and `/craft:dist:pypi` dead references. `docs/commands/dist.md` lines 14-19 carry that fix's disclaimer as the literal template for this SPEC.

## Problem

`/craft:dist:marketplace` was folded into the `dist-extras` skill during the v4 consolidation (Phase 3.5, 2026-07-12 — see `skills/distribution/dist-extras/SKILL.md` line 20). It no longer exists as a real slash command. A prior background session was tasked with applying the same fix already done for `/craft:dist:curl-install`/`/craft:dist:pypi`, but was killed before making any changes — confirmed via `git status` (zero uncommitted diff) and `git log` (no related commit). Six files still contain live, unannotated references to the dead command.

## Part 1 Findings — Adversarial Verification

**Verdict: CONFIRMED** — straightforward annotation/rename fix, same shape as the curl-install/pypi precedent. No content beyond command-syntax is stale.

Evidence:

1. **Real command list has no `dist:marketplace`.** `find commands/dist -name '*.md'` returns only `homebrew.md` and `surfaces.md`. No `marketplace.md` command file exists.

2. **`dist-extras` skill genuinely covers marketplace functionality — not an assumption error.** `skills/distribution/dist-extras/SKILL.md`:
   - Frontmatter `description` (line 3) explicitly lists "publish to Claude Code marketplace", "create marketplace.json", "private plugin", "plugin drift", "pin refresh" as trigger phrases.
   - A full `## Claude Code marketplace` section (lines 109-280) covers subcommand-equivalents (`init`/`validate`/`test`/`publish`, mirrored 1:1 from the dead command), the `marketplace.json` schema, the no-build-step limitation, public/private mode, the SSH-vs-HTTPS upstream bug, and post-release pin-refresh/drift-doctor logic — all genuine, non-trivial content, not a stub.
   - This is materially deeper coverage than a passing mention; the skill is the real successor.

3. **Reference content is technically accurate as workflow documentation; only the invocation syntax is dead — and leaving it as-is matches the already-accepted precedent.** `skills/distribution/dist-extras/references/marketplace.md` is written throughout (18 occurrences) in the old `/craft:dist:marketplace [subcommand]` framing (headers, Quick Start, execution steps, example output boxes). This looks stale at first glance, but checking the precedent file `skills/distribution/dist-extras/references/curl-install.md` shows the **same pattern was left untouched** by commit `0aef1ca71` (10 occurrences of `/craft:dist:curl-install`, still present, unannotated) — confirmed by `git show 0aef1ca71 --stat`, which only touched `docs/commands/dist.md` and other top-of-file-disclaimer targets, not the `references/*.md` internal skill docs. **Conclusion: `references/marketplace.md` and `references/curl-install.md` are internal skill knowledge-base files, not user-facing command docs — the established convention is to leave their command-syntax framing as historical/internal shorthand and NOT to annotate them.** This file needs no edit to stay consistent with precedent.

4. **`commands/dist/homebrew.md` and `commands/dist/surfaces.md` are single "See Also"/"Integration" table-row mentions — cheap fix, not deep integration.**
   - `commands/dist/homebrew.md` line 1692: one "See Also" bullet: `` `/craft:dist:marketplace` - Claude Code marketplace distribution - init, validate, test, and publish``. The line directly above it (1691) already carries the curl-install fix in the exact target format: ``curl-based install scripts - ask "generate an install script" (`dist-extras` skill, moved from `/craft:dist:curl-install` in the v4 consolidation)``.
   - `commands/dist/surfaces.md`: two one-line table/bullet mentions — Integration table row (line 168: `` `/craft:dist:marketplace` | Marketplace distribution (Code surface) ``) and a "See Also" bullet (line 178: `` `/craft:dist:marketplace` — marketplace distribution``). Both are shallow cross-references, not embedded workflow logic. (Lines 29/36/144/149 in the same file mention "marketplace" as a channel/surface noun, not the command — no fix needed there.)

## Part 2 — Fix Plan (Deferred, Not Implemented)

**No files were modified in this pass except this SPEC.** A future session should apply exactly this plan.

### 1. `docs/commands/dist.md` — whole-page disclaimer + table + section rename (deepest fix)

This file is built around `/craft:dist:marketplace` as one of its 4 headline commands (TL;DR line 9-10, Commands Overview table row 27, full `## /craft:dist:marketplace - Marketplace Distribution` section lines 34-135 with Quick Start/Subcommands/Init/Validate/Test/Publish subsections, Common Workflows references).

- Extend the existing v4-consolidation disclaimer block (lines 14-19) to also cover marketplace:
  add a sentence: `` `/craft:dist:marketplace` also no longer exists as a slash command — moved to the same `dist-extras` skill. Ask naturally ("publish to Claude Code marketplace", "create marketplace.json") instead. ``
- TL;DR (line 9): change ``Use `/craft:dist:marketplace` for Claude Code plugins`` to naturally-phrased guidance, e.g. ``Ask to "publish to Claude Code marketplace" (dist-extras skill) for Claude Code plugins``.
- Commands Overview table (line 27): change row to match the PyPI/curl-install rows' pattern (line 29-30): `` | Marketplace distribution (moved to `dist-extras` skill, v4) | Claude Code marketplace distribution | All platforms | ``
- Section header (line 34): rename `## /craft:dist:marketplace - Marketplace Distribution` to `## Marketplace Distribution (moved to \`dist-extras\` skill, v4 consolidation — formerly \`/craft:dist:marketplace\`)`, matching the exact pattern already used for the PyPI section header (line 361) and Universal Installer section header (line 464).
- Body content within that section (Quick Start code fences using `/craft:dist:marketplace ...`, subcommand table) — reframe the intro sentence to "Ask naturally... instead of the `/craft:dist:marketplace` subcommands shown below" (matching lines 363/466), then leave the illustrative subcommand walkthrough as-is (documents behavior, not living syntax) — same treatment already applied to the PyPI and curl-install sections below it.
- Common Workflows section (lines 534-553): `/craft:dist:homebrew setup` / `/craft:dist:pypi setup` / `/craft:dist:curl-install --add-readme` block already mixes real+moved commands without inline annotation (relies on the section-level disclaimers above) — add `/craft:dist:marketplace` mentions there under the same convention (no per-line fix needed, covered by the earlier disclaimer note).

### 2. `commands/dist/homebrew.md` — inline "See Also" bullet (cheap fix)

Line 1692. Replace:

```
- `/craft:dist:marketplace` - Claude Code marketplace distribution - init, validate, test, and publish
```

with (matching line 1691's exact style):

```
- Claude Code marketplace distribution - ask "publish to Claude Code marketplace" (`dist-extras` skill, moved from `/craft:dist:marketplace` in the v4 consolidation)
```

### 3. `commands/dist/surfaces.md` — two inline table/bullet mentions (cheap fix)

- Line 168 (Integration table row): replace `` `/craft:dist:marketplace` | Marketplace distribution (Code surface) `` with `` `dist-extras` skill (ask "publish to Claude Code marketplace") | Marketplace distribution (Code surface) — moved from `/craft:dist:marketplace` in the v4 consolidation ``.
- Line 178 (See Also bullet): replace `` `/craft:dist:marketplace` — marketplace distribution`` with `` `dist-extras` skill — marketplace distribution (ask naturally; moved from `/craft:dist:marketplace` in the v4 consolidation)``.
- No other line in this file needs a fix (lines 29/36/144/149 use "marketplace" as a plain noun for the distribution channel/surface, not as the dead command).

### 4. `skills/distribution/dist-extras/references/marketplace.md` — NO CHANGE

Per Part 1 finding 3: this is an internal skill reference file. The precedent commit (`0aef1ca71`) deliberately left the sibling `references/curl-install.md` (and presumably `references/pypi.md`) with their old command-syntax framing intact, unannotated. Applying a different treatment to `marketplace.md` alone would be an inconsistency, not a fix. **Leave as-is.**

### 5. `skills/distribution/dist-extras/references/curl-install.md` — NO CHANGE

Listed in the task's file set but out of scope for this SPEC's marketplace fix — it's the PyPI/curl-install precedent file itself (already the accepted end-state per commit `0aef1ca71`), not a marketplace reference. Confirmed no `marketplace` dead-reference content in it. **Leave as-is.**

### 6. `skills/distribution/dist-extras/SKILL.md` — NO CHANGE

All `/craft:dist:marketplace` mentions in this file (lines 114) are of the form "Subcommands (mirrors `/craft:dist:marketplace`)" — explicitly documenting the skill's own lineage from the dead command, which is accurate historical context, not a dead-reference bug. Same treatment as the analogous "mirrors `/craft:dist:pypi`" (line 36) and "mirrors `/craft:dist:curl-install`" (line 75) lines already present and left unannotated. **Leave as-is.**

## Summary Table

| File | Fix type | Action |
|---|---|---|
| `docs/commands/dist.md` | Whole-page disclaimer + table + section rename | Apply (deepest fix, ~5 edit points) |
| `commands/dist/homebrew.md` | Inline "See Also" bullet | Apply (1 line) |
| `commands/dist/surfaces.md` | Inline table row + bullet | Apply (2 lines) |
| `skills/distribution/dist-extras/references/marketplace.md` | N/A | No change (matches curl-install.md precedent) |
| `skills/distribution/dist-extras/references/curl-install.md` | N/A | No change (not a marketplace file; already the accepted precedent) |
| `skills/distribution/dist-extras/SKILL.md` | N/A | No change (accurate lineage note, same as pypi/curl-install lines) |

## Deferred

**This SPEC is deferred — no implementation happened in this pass.** A future session (or `/craft:orch:drive` against this SPEC) should:

1. Apply the 3 real edits (`docs/commands/dist.md`, `commands/dist/homebrew.md`, `commands/dist/surfaces.md`) per section 1-3 above.
2. Skip the 3 "no change" files (do not touch them — touching them would break parity with the accepted pypi/curl-install precedent).
3. Run the docs-only pre-PR tier (lint + link/count validators — this is a docs/prose-only change per `pre-pr-testing.md`'s tier table).
4. Grep the whole repo for `dist:marketplace` and `/craft:dist:marketplace` one more time after editing to confirm no other stray mentions were missed outside the 6 files originally scoped.
