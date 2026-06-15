# Multi-surface release — Orchestration Plan

> **Branch:** `feature/multi-surface-release`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-multi-surface-release`
> **Spec:** `docs/specs/SPEC-multi-surface-release-2026-06-15.md`
> **Version Target:** next craft minor (TBD at release)

## Objective

Make one release verifiably reach every surface craft controls (Code / Homebrew / marketplace) and
print an honest one-time step for Desktop — driven by a context-aware `release:verify-surfaces`
step, plus an aggregator marketplace, cache-prune, and the live rforge drift fix.

## Decisions baked in (from spec D1–D7)

- **D1** context-aware trigger (auto on `.claude-plugin/plugin.json`), `--skip-surfaces` escape only.
- **D2** block on mismatch of craft-controlled legs; **warn** Desktop.
- **D3** print the one-time `claude plugin marketplace add` step; never write Desktop store files.
- **D4** design generically for all Data-Wise plugins (craft, scholar, rforge, himalaya-mcp).
- **D5** one aggregator Data-Wise marketplace (Phase 3).
- **D6** reuse `claude plugin tag` for the plugin.json↔marketplace leg.
- **D7** cache-prune keeps current + 2, reports what it removes.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 0 | rforge drift fix (Item 3, ops — can run standalone) | High | 10m | ✅ done — `update rforge@local-plugins` → 2.13.0 |
| 1 | `release:verify-surfaces` engine (Item 2) | High | 1–2h | ✅ done (commit 9cf08710) |
| 2 | Cache-prune (Item 5) | Medium | 30m | ✅ done |
| 3 | Aggregator Data-Wise marketplace (Item 6) | Medium | 1h | ✅ done (craft-side; aggregator repo = follow-up PR) |
| 4 | Docs & Discoverability (Item 4 + required) | High | 1h | ✅ done |

> **Phase 0 note:** the bare `claude plugin update rforge` errors "not found"; locally-registered
> plugins need the **marketplace-qualified** name (`rforge@local-plugins`). Remediation hints
> updated accordingly.

> Item 1 (Desktop spike) is **already DONE** — see spec. Not a phase.

## Phase 0: rforge drift fix (ops, no craft code)

**Scope:** clear the one real live drift (Code-registered rforge 2.6.0 vs brew 2.13.0).

- [ ] 0.1 Run `claude plugin update rforge` (restart to apply); confirm `installed_plugins.json`
      shows 2.13.0.

**Key files:** none (ops). Can be done outside the worktree anytime.

## Phase 1: `release:verify-surfaces` engine (Item 2)

**Scope:** the core check + report; extend `scripts/post-release-sweep.sh`, slot into the `release`
skill after Step 13.

- [ ] 1.1 Add a `verify-surfaces` routine: auto-runs when `.claude-plugin/plugin.json` is present
      (D1); honors `--skip-surfaces`.
- [ ] 1.2 Reuse `claude plugin tag` (or its validation path) for plugin.json ↔ marketplace entry (D6).
- [ ] 1.3 Add the remaining version legs: git tag `vX.Y.Z` ↔ tap `Formula/<name>.rb` ↔
      brew-installed ↔ Code-registered (`~/.claude/plugins/installed_plugins.json`).
- [ ] 1.4 Behavior (D2): block on any craft-controlled leg mismatch; **warn** on the Desktop leg.
- [ ] 1.5 Emit the ADHD-friendly surfaces report (one line/surface, glyph + version + next action).
- [ ] 1.6 Write/update the `.STATUS` surfaces matrix (plugin × {Code, Desktop} × version).
- [ ] 1.7 Tests: a passing case + a forced-mismatch case proving it blocks (red→green).

**Key files:**

- `scripts/post-release-sweep.sh` (update)
- `skills/release/SKILL.md` (wire the step in)
- `commands/code/release.md` (reference the new step)
- `tests/` (new test for verify-surfaces)

## Phase 2: Cache-prune (Item 5)

**Scope:** GC stale `~/.claude/plugins/cache/local-plugins/<name>/<ver>/` dirs.

- [ ] 2.1 Keep current + 2 most recent per plugin (D7); never silent-delete — print what's removed.
- [ ] 2.2 Make it a release sub-step (and/or standalone); distinct from `claude plugin prune` (deps).
- [ ] 2.3 Test on a fixture dir (don't delete real cache in tests).

**Key files:** `scripts/post-release-sweep.sh` or a new `scripts/cache-prune.sh`; `tests/`.

## Phase 3: Aggregator Data-Wise marketplace (Item 6)

**Scope:** one `marketplace.json` listing all Data-Wise plugins; added once per surface.

- [ ] 3.1 Decide host (Open Q6: reuse `Data-Wise/claude-plugins` vs new `Data-Wise/marketplace`).
- [ ] 3.2 Author the aggregator `marketplace.json` (craft, scholar, rforge, himalaya-mcp entries).
- [ ] 3.3 Wire each plugin's release to update its aggregator entry (single cross-plugin source).
- [ ] 3.4 Make the aggregator entry a leg in `verify-surfaces` (Phase 1) so it can't diverge.

**Key files:** aggregator repo `marketplace.json` (cross-repo — coordinate, may be separate PR);
`scripts/` release wiring.

> **Cross-repo note:** Phase 3 touches a Data-Wise repo outside craft. Keep craft-side wiring here;
> the aggregator repo gets its own change/PR. Don't co-edit unrelated repos from this worktree
> without switching context.

## Phase 4: Documentation & Discoverability (REQUIRED — final phase)

- [ ] 4.1 `docs/guide/desktop-release.md` — add a **plugin-install** section: one-time
      `claude plugin marketplace add Data-Wise/<aggregator>` + the exact in-app click-path
      (confirm once in the Desktop UI — Open Q7).
- [ ] 4.2 Tutorial/help — document `verify-surfaces` + `--skip-surfaces` where release is documented.
- [ ] 4.3 REFCARD — add to relevant command tables.
- [ ] 4.4 Help hub / discovery — verify `/craft:hub` surfaces any new command/flag.
- [ ] 4.5 Website — `mkdocs.yml` nav if new pages; `mkdocs build`.
- [ ] 4.6 Catalog — update `docs/skills-agents.md` if a skill/command changed.
- [ ] 4.7 CHANGELOG `[Unreleased]` + count bumps if any; `./scripts/validate-counts.sh` ✓.
- [ ] 4.8 `./scripts/docs-staleness-check.sh` clean.

## Friction Prevention

- **Context first**: read this ORCHESTRATE file and the spec BEFORE starting.
- **Verify location**: confirm CWD is the worktree (`~/.git-worktrees/craft/feature-multi-surface-release`), not the main repo.
- **No autonomous starts**: after each phase, STOP and confirm before proceeding.
- **Test per phase**: run the suite after each phase.
- **Branch-guard**: new code files are fine here (feature branch); on `dev` they'd be blocked.

## Acceptance Criteria (from spec)

- [ ] Release fails loud on craft-controlled version disagreement; Desktop is warn-only.
- [ ] Surfaces report prints per-surface status; `.STATUS` surfaces matrix updates.
- [ ] rforge reads 2.13.0 in Code (Phase 0).
- [ ] Aggregator marketplace exists and is a verified leg.
- [ ] Cache-prune keeps current + 2 and reports.
- [ ] Desktop step documented with the verified click-path.
- [ ] No craft code writes under `~/Library/Application Support/Claude/**`.
- [ ] Documentation & Discoverability phase complete.

## Commit Strategy

- Phase 0: (ops — no commit)
- Phase 1: `feat(release): verify-surfaces — multi-surface version assert + report`
- Phase 2: `feat(release): cache-prune for stale local-plugins versions`
- Phase 3: `feat(dist): Data-Wise aggregator marketplace + release wiring`
- Phase 4: `docs(release): document verify-surfaces + Desktop plugin install`

## Verification

After each phase:

```bash
python3 tests/test_craft_plugin.py        # unit
python3 -m pytest tests/ -q               # full suite (CI mirror)
./scripts/validate-counts.sh              # counts (if any added)
./scripts/docs-staleness-check.sh         # docs (Phase 4)
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the multi-surface-release feature. The spec at
`docs/specs/SPEC-multi-surface-release-2026-06-15.md` has full design details and Decisions D1–D7.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-multi-surface-release
claude
```

On session start, paste:

> Read `ORCHESTRATE-multi-surface-release.md` and the spec at
> `docs/specs/SPEC-multi-surface-release-2026-06-15.md`. Start Phase 1.
> (Phase 0 is a standalone ops fix — `claude plugin update rforge` — do it whenever.)

### Phase-by-Phase

1. Read the current state of each file listed in the phase.
2. Implement per the spec design + Decisions D1–D7.
3. Run verification after each phase.
4. Commit in logical groups (see Commit Strategy).
5. STOP and confirm before the next phase.
