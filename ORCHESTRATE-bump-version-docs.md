# Bump-Version Docs Orchestration Plan

> **Branch:** `feature/bump-version-docs`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-bump-version-docs`
> **Spec:** `docs/specs/SPEC-bump-version-docs-2026-02-19.md`

## Objective

Extend bump-version.sh to cover 4 additional doc files (mechanical version substitution), and add release skill Step 3b for semantic doc updates (CHANGELOG, VERSION-HISTORY, README title, index.md info box, REFCARD summary).

## Phase Overview

| Phase | Task | Priority | Status |
|-------|------|----------|--------|
| 1 | Add 4 mechanical files to bump-version.sh | High | Pending |
| 2 | Add 4 files to `--verify` mode | High | Pending |
| 3 | Update release skill with Step 3b | Medium | Pending |
| 4 | Test: dry-run, verify, full bump | High | Pending |
| 5 | Update docs (file count refs, configuration.md) | Low | Pending |

## Phase 1: bump-version.sh — Add Mechanical Files

Add sed replacements for:

1. `docs/DEPENDENCY-ARCHITECTURE.md` — `**Version**: X.Y.Z` footer
2. `docs/reference/configuration.md` — `bump-version.sh X.Y.Z` example
3. `docs/REFCARD.md` lines ~7+11 — version in box + summary line version
4. `docs/index.md` — `!!! info "Latest: vX.Y.Z"` line (version part only)

Also improve existing REFCARD handling — currently updates header but misses the box interior lines.

## Phase 2: --verify Mode

Add drift detection for the 4 new files. Pattern: grep for expected version, report mismatch.

## Phase 3: Release Skill Step 3b

After bump-version.sh runs (Step 3), add Step 3b that uses the release title to:

- Insert CHANGELOG.md entry (from commit analysis)
- Insert VERSION-HISTORY.md section
- Update README.md release title line
- Update docs/index.md info box with title
- Update docs/REFCARD.md summary line with title

This step requires the release title (available from Step 1 of release pipeline).

## Phase 4: Testing

- `./scripts/bump-version.sh X.Y.Z --dry-run` shows all 13 files
- `./scripts/bump-version.sh --verify` catches drift in all 13 files
- Manual test: bump to a test version, verify all files, revert

## Acceptance Criteria

- [ ] bump-version.sh handles 13 files (up from 9)
- [ ] `--verify` detects drift in all 13 files
- [ ] `--dry-run` previews all 13 files
- [ ] Release skill Step 3b documented in SKILL.md
- [ ] Zero manual version edits needed during next release

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-bump-version-docs
claude
```
