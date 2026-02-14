# Marketplace Distribution Orchestration Plan

> **Branch:** `feature/marketplace-distribution`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-marketplace-distribution`
> **Spec:** `docs/specs/SPEC-github-marketplace-distribution-2026-02-14.md`

## Objective

Add Claude Code marketplace distribution as a first-class channel: create marketplace.json, new `/craft:dist:marketplace` command, update release skill with marketplace + tap auto-update, fix Homebrew templates for `brew audit --strict`.

## Phase Overview

| Phase | Task | Agent | Priority | Status |
| ----- | ---- | ----- | -------- | ------ |
| 1a | Create `.claude-plugin/marketplace.json` | Agent 1 | High | Pending |
| 1b | Create `commands/dist/marketplace.md` | Agent 2 | High | Pending |
| 1c | Fix Homebrew templates in `commands/dist/homebrew.md` (plugin type auto-detect) | Agent 3 | High | Pending |
| 2a | Update `skills/release/SKILL.md` (Steps 2c, 3, 8.5) | Agent 4 | High | Pending |
| 2b | Update `scripts/pre-release-check.sh` (marketplace validation) | Agent 5 | Medium | Pending |
| 3 | Update docs (README install section, homebrew-installation.md) | Agent 6 | Medium | Pending |

## Parallel Execution Groups

### Group 1 (fully parallel — no dependencies)

These three tasks have zero overlap in files:

- **Agent 1:** Create `.claude-plugin/marketplace.json`
  - Read: `.claude-plugin/plugin.json`, git remote
  - Write: `.claude-plugin/marketplace.json`
  - Validate: `claude plugin validate .` (if available)

- **Agent 2:** Create `commands/dist/marketplace.md`
  - Read: spec file, existing `commands/dist/homebrew.md` for patterns
  - Write: `commands/dist/marketplace.md`
  - 4 subcommands: init, validate, test, publish

- **Agent 3:** Update Homebrew templates in `commands/dist/homebrew.md`
  - Focus: Add Claude Code Plugin as first-class formula type in auto-detection table
  - The validate auto-fix section and plugin template were already updated in the previous commit
  - Read: current `commands/dist/homebrew.md`
  - Write: `commands/dist/homebrew.md` (add auto-detection section)

### Group 2 (depends on Group 1 for context)

- **Agent 4:** Update release skill
  - Read: `skills/release/SKILL.md`, spec
  - Write: `skills/release/SKILL.md`
  - Changes: Step 2c (marketplace validate), Step 3 (marketplace.json bump), Step 8.5 (tap auto-update)

- **Agent 5:** Update pre-release-check.sh
  - Read: `scripts/pre-release-check.sh`
  - Write: `scripts/pre-release-check.sh`
  - Changes: Add marketplace.json version consistency check

### Group 3 (depends on Groups 1+2)

- **Agent 6:** Update documentation
  - Read: `README.md`, `docs/guide/homebrew-installation.md`
  - Write: Both files — add marketplace as recommended install path

## Acceptance Criteria

- [ ] `marketplace.json` valid (passes `claude plugin validate .` if available)
- [ ] `/craft:dist:marketplace` command has all 4 subcommands documented
- [ ] Homebrew auto-detects `.claude-plugin/` as plugin formula type
- [ ] Release skill includes marketplace.json bump + tap update steps
- [ ] pre-release-check.sh validates marketplace.json version
- [ ] README recommends marketplace install for new users
- [ ] All markdown passes lint (`npx markdownlint-cli2`)

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-marketplace-distribution
claude
# Then: /craft:orchestrate (references this file)
```
