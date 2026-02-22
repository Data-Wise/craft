# ORCHESTRATE: Release Pipeline Hardening and Post-Release Verification

**Branch:** `feature/release-pipeline-hardening`
**Base:** `dev`
**Worktree:** `~/.git-worktrees/craft/feature-release-pipeline-hardening`

---

## Overview

Harden the release pipeline with concurrency controls, dual-badge layout, expanded pre-release checks, post-release downstream verification, and documentation updates.

**19 files modified** across 8 phases. Estimated 4-6 increments.

---

## Increment 1: GitHub Actions Workflow Fixes (Phase 1)

### 1A. `.github/workflows/docs.yml` -- Full hardening

Current state: bare `mkdocs gh-deploy --force`, `python-version: 3.x`, no concurrency, no path filter.

**Change 1:** Add concurrency group (queue, don't cancel) -- `group: deploy-docs`, `cancel-in-progress: false`

**Change 2:** Add path filter to `push` trigger -- `paths: ['docs/**', 'mkdocs.yml', '.github/workflows/docs.yml']`

**Change 3:** Pin Python to `'3.12'` (replace `3.x`)

**Change 4:** Replace bare `mkdocs gh-deploy --force` with bash retry loop: 3 attempts, `git fetch origin gh-pages` + sleep 5 between retries, exit 0 on success, exit 1 after 3 failures.

### 1B. `.github/workflows/ci.yml` -- Add concurrency

Add after `on:` block (before `jobs:`): `concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }`

### 1C. `.github/workflows/docs-quality.yml` -- Add concurrency

Add after `on:` block (before `jobs:`): `concurrency: { group: docs-quality-${{ github.ref }}, cancel-in-progress: true }`

### Verification

Validate YAML syntax with `python3 -c "import yaml; yaml.safe_load(open(...))"` for all three files.

**Commit:** `fix: harden GitHub Actions workflows with concurrency and retry`

---

## Increment 2: Badge Updates (Phase 2)

### 2A. `docs/index.md` lines 3-5

Replace current dev-only badges with dual main+dev layout:

- **main:** CI badge (`?branch=main`) + Deploy Docs badge (`docs.yml/badge.svg`)
- **dev:** CI badge (`?branch=dev`) + Documentation Quality badge (`?branch=dev`)
- Keep existing Documentation completeness badge

### 2B. `README.md` lines 3-6

Same dual main+dev badge pattern. Keep existing Version and Documentation badges.

### Verification

Verify both files contain `badge.svg?branch=main` and `badge.svg?branch=dev`.

**Commit:** `feat: add dual main+dev CI badge layout`

---

## Increment 3: Pre-Release Script Enhancement (Phase 3)

### 3A. `scripts/pre-release-check.sh`

**Update total check count** from `/6` to `/8` in all headers.

**Add Check 7: Badge URL branch validation** (after Check 6, before Summary)

- For both `README.md` and `docs/index.md`:
  - Verify contains `badge.svg?branch=main`
  - Verify contains `badge.svg?branch=dev`
- Fail (increment ERRORS) if either is missing

**Add Check 8: Homebrew formula desc consistency**

- Locate formula locally (`~/projects/dev-tools/homebrew-tap/Formula/craft.rb` or brew tap path)
- Extract `desc` field, check command count vs actual `CMD_COUNT`
- Warn (not fail) if agents/skills not mentioned
- Skip gracefully if formula not found locally

**Update Summary** counts line to include check count.

### Verification

Run `./scripts/pre-release-check.sh 2.26.0` -- should show 8 checks.

**Commit:** `feat: add badge URL and formula desc checks to pre-release script`

---

## Increment 4: Release Skill and Checklist Updates (Phase 4)

### 4A. `skills/release/SKILL.md`

**Expand Step 10 title** from "Verify CI on Main" to "Verify CI on Main (MANDATORY)".

**Add Step 11: Verify Downstream Workflows (NEW)** after Step 10, with five subsections:

- **11a: Deploy Documentation Workflow** -- `gh run list --workflow=docs.yml --limit 1`
- **11b: Homebrew Release Workflow** -- `gh run list --workflow=homebrew-release.yml --limit 1`
- **11c: Live Site Version** -- `curl` the docs site, extract version string
- **11d: Formula Content Verification** -- `gh api` for formula content + `brew info`
- **11e: Badge Validation** -- `curl` main CI badge SVG, check for "passing"

**Update Output Format table** -- change `11/11` to `13/13`:

```text
│ [ 1/13] CI mirror check .................... PASSED          │
│ [ 2/13] Release metadata check ............. PASSED          │
│ [ 3/13] Version bump ....................... DONE             │
│ [ 4/13] Commit and push ................... DONE              │
│ [ 5/13] Release PR created ................. PR #70          │
│ [ 6/13] CI monitoring ..................... GREEN (90s)       │
│ [ 7/13] PR merged .......................... DONE             │
│ [ 8/13] GitHub release ..................... v2.17.0          │
│ [ 9/13] Docs deployed ..................... DONE              │
│ [10/13] Homebrew tap updated .............. DONE              │
│ [11/13] Dev synced ........................ DONE               │
│ [12/13] Verify CI on main ................. PASSED            │
│ [13/13] Downstream verification ........... ALL GREEN         │
```

**Update Dry-Run Output** to show 13 steps with new downstream verification steps.

**Update step numbering** throughout to reflect the new count:

- Old Step 7 (Merge) stays Step 7
- Old Step 7 (Create Release) becomes Step 8
- Old Step 8 (Post-Release/docs) becomes Step 9
- Old Step 8.5 (Homebrew) becomes Step 10
- Old Step 9 (Sync dev) becomes Step 11
- Old Step 10 (Verify CI) becomes Step 12
- New Step 13: Downstream verification

### 4B. `skills/release/references/release-checklist.md`

Add to **Post-Release** section (after existing items):

- CI passes on main
- Deploy Documentation workflow succeeds
- Homebrew Release workflow succeeds
- Live site shows new version
- Formula content verified (version, SHA, desc counts)
- `brew info` shows new version
- Main and dev CI badges show passing

### Verification

Verify step references are consistent: `grep -c '/13' skills/release/SKILL.md`

**Commit:** `feat: add post-release downstream verification to release skill`

---

## Increment 5: Command Updates (Phase 5)

### 5A. `commands/ci/status.md` -- Add `--post-release` argument

Add to frontmatter `arguments:` section: `name: post-release`, `description: Run post-release verification`, `required: false`, `default: false`.

Add new section after "Failure Summary" -- **Post-Release Mode (--post-release)**:

When `--post-release` is passed, run extended verification:

1. All release-triggered workflows: ci.yml, docs.yml, homebrew-release.yml
2. Homebrew tap workflows: Data-Wise/homebrew-tap
3. Live site version: `curl` the docs site and verify version string
4. Badge URL validation: Verify main and dev badges resolve
5. Brew info: Verify `brew info data-wise/tap/craft` shows new version

Include output format with box-drawing characters showing post-release status.

### 5B. `commands/check.md` -- Add badge/formula checks

Add two rows to the **Context-Specific Check Lists** table:

| Check | commit | pr | release | deploy |
|-------|--------|-----|---------|--------|
| Badge URLs | Skip | Skip | Validate both branches | Validate both branches |
| Formula desc | Skip | Skip | Check counts match | Skip |

Add documentation sections:

- **Badge URL Validation (NEW in v2.27.0)** -- validates `?branch=main` and `?branch=dev` in both files
- **Homebrew Formula Desc Validation (NEW in v2.27.0)** -- checks formula desc counts match actual

### Verification

Validate frontmatter YAML for `commands/ci/status.md`.

**Commit:** `feat: add post-release mode and badge/formula checks to commands`

---

## Increment 6: Documentation Updates (Phase 6)

### 6A. `commands/hub.md`

- Update release pipeline display from "10 steps" to "13 steps"
- Add mention of post-release downstream verification
- Update `ci:status` description to include `--post-release` mode

### 6B. `docs/workflows/release-workflow.md`

Add a **"Post-Release Verification"** section with Steps 11-13 description, including downstream workflow checks, live site verification, and formula content verification.

### 6C. `docs/tutorials/TUTORIAL-release-pipeline.md`

Update the step table from 10 to 13 steps. Add downstream verification rows.

### 6D. `docs/guide/badge-management.md`

- Update badge examples to show dual main+dev layout
- Document the new pre-release badge URL validation check

### 6E. `docs/guide/homebrew-automation.md`

- Document formula desc validation check
- Add section on ensuring formula desc stays consistent

### 6F. `docs/REFCARD.md`

- Update release pipeline reference to show 13 steps
- Add downstream verification to the checklist

### 6G. `docs/API-REFERENCE-COMMANDS.md` (if ci:status or check entries exist)

Check for entries, update with new arguments if present.

### 6H. `CHANGELOG.md`

Add entry under `## [Unreleased]` or `## [2.27.0]`:

- GitHub Actions concurrency groups and docs deploy retry logic
- Dual main+dev CI badge layout in README.md and docs/index.md
- Pre-release checks 7-8: badge URL validation and formula desc consistency
- Post-release downstream verification (Steps 11-13 in release pipeline)
- `/craft:ci:status --post-release` mode for downstream workflow checks
- Badge URL and formula desc validation in `/craft:check --for release`

### Verification

```bash
python3 tests/test_craft_plugin.py
python3 tests/test_craft_plugin.py -k "broken_links"
./scripts/validate-counts.sh
```

**Commit:** `docs: update release pipeline docs for 13-step workflow with downstream verification`

---

## Phase 7: Homebrew Formula Desc Fix (Separate Repo)

### 7A. `~/projects/dev-tools/homebrew-tap/Formula/craft.rb` line 6

Change `desc "Full-stack developer toolkit for Claude Code with 107 commands"` to `desc "Full-stack developer toolkit for Claude Code"`.

This removes counts from desc to avoid the 80-char Homebrew limit and count drift. Counts exist elsewhere in the formula (caveats block).

**Note:** This is in a separate repo. Handle via direct edit + commit + push, or defer to next release cycle if preferred.

**Commit (in homebrew-tap repo):** `craft: simplify desc to avoid count drift`

---

## Phase 8: Homebrew Local Upgrade

Run `brew update && brew upgrade data-wise/tap/craft` after Phase 7 changes are pushed. This is a manual step, not committed.

---

## File Change Summary

| # | File | Phase | Change Type |
|---|------|-------|-------------|
| 1 | `.github/workflows/docs.yml` | 1A | Concurrency, path filter, retry, Python 3.12 |
| 2 | `.github/workflows/ci.yml` | 1B | Concurrency group |
| 3 | `.github/workflows/docs-quality.yml` | 1C | Concurrency group |
| 4 | `docs/index.md` | 2A | Dual main+dev badges |
| 5 | `README.md` | 2B | Dual main+dev badges |
| 6 | `scripts/pre-release-check.sh` | 3A | Checks 7-8: badge URLs, formula desc |
| 7 | `skills/release/SKILL.md` | 4A | Steps 11-13: downstream verification |
| 8 | `skills/release/references/release-checklist.md` | 4B | Post-release items |
| 9 | `commands/ci/status.md` | 5A | `--post-release` argument |
| 10 | `commands/check.md` | 5B | Badge + formula validation |
| 11 | `commands/hub.md` | 6A | Release pipeline 13 steps |
| 12 | `docs/workflows/release-workflow.md` | 6B | Post-release verification section |
| 13 | `docs/tutorials/TUTORIAL-release-pipeline.md` | 6C | 13-step table |
| 14 | `docs/guide/badge-management.md` | 6D | Dual-badge pattern |
| 15 | `docs/guide/homebrew-automation.md` | 6E | Formula desc sync |
| 16 | `docs/REFCARD.md` | 6F | Release pipeline reference |
| 17 | `docs/API-REFERENCE-COMMANDS.md` | 6G | ci:status and check updates (if present) |
| 18 | `CHANGELOG.md` | 6H | New entry |
| 19 | `homebrew-tap/Formula/craft.rb` | 7A | Desc field cleanup (separate repo) |

---

## Verification Checklist

- [ ] YAML valid for all 3 workflow files
- [ ] `./scripts/pre-release-check.sh 2.26.0` shows 8 checks
- [ ] `python3 tests/test_craft_plugin.py` -- unit tests pass
- [ ] `python3 -m pytest tests/test_plugin_e2e.py -v` -- e2e tests pass
- [ ] `./scripts/validate-counts.sh` -- counts match
- [ ] Both files have `branch=main` and `branch=dev` badges

---

## Implementation Order

```text
Increment 1 -> Increment 2 -> Increment 3 -> Increment 4 -> Increment 5 -> Increment 6
    (CI)         (Badges)       (Script)       (Skill)        (Commands)      (Docs)
```

Each increment is independently committable. Phases 7-8 (Homebrew) are separate repo operations to do after the main PR.
