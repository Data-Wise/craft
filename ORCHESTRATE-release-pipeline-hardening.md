# ORCHESTRATE: Release Pipeline Hardening & Post-Release Verification

**Branch:** `feature/release-pipeline-hardening`
**Base:** `dev`
**Worktree:** `~/.git-worktrees/craft/feature-release-pipeline-hardening`

---

## Overview

Harden the release pipeline with concurrency controls, dual-badge layout, expanded pre-release checks, post-release downstream verification, and documentation updates.

**19 files modified** across 8 phases. Estimated 4-6 increments.

---

## Increment 1: GitHub Actions Workflow Fixes (Phase 1)

### 1A. `.github/workflows/docs.yml` — Full hardening

Current state: bare `mkdocs gh-deploy --force`, `python-version: 3.x`, no concurrency, no path filter.

**Changes:**

1. Add concurrency group (queue, don't cancel):

   ```yaml
   concurrency:
     group: deploy-docs
     cancel-in-progress: false
   ```

2. Add path filter to `push` trigger:

   ```yaml
   on:
     push:
       branches: [ main ]
       paths:
         - 'docs/**'
         - 'mkdocs.yml'
         - '.github/workflows/docs.yml'
     workflow_dispatch:
   ```

3. Pin Python to `'3.12'` (replace `3.x`)

4. Replace bare `mkdocs gh-deploy --force` with retry loop:

   ```yaml
   - name: Deploy docs with retry
     run: |
       for attempt in 1 2 3; do
         echo "Attempt $attempt of 3..."
         if mkdocs gh-deploy --force; then
           echo "Deploy succeeded on attempt $attempt"
           exit 0
         fi
         echo "Deploy failed, fetching latest gh-pages and retrying..."
         git fetch origin gh-pages
         sleep 5
       done
       echo "Deploy failed after 3 attempts"
       exit 1
   ```

### 1B. `.github/workflows/ci.yml` — Add concurrency

Add after `on:` block (before `jobs:`):

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

### 1C. `.github/workflows/docs-quality.yml` — Add concurrency

Add after `on:` block (before `jobs:`):

```yaml
concurrency:
  group: docs-quality-${{ github.ref }}
  cancel-in-progress: true
```

### Verification

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/docs.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/docs-quality.yml'))"
```

**Commit:** `fix: harden GitHub Actions workflows with concurrency and retry`

---

## Increment 2: Badge Updates (Phase 2)

### 2A. `docs/index.md` lines 3-5

Replace the existing dev-only CI badges with dual main+dev layout. The new layout has two lines:

- **main:** line with Craft CI `?branch=main` badge and Deploy Docs badge (no branch param, defaults to main)
- **dev:** line with Craft CI `?branch=dev` badge and Documentation Quality `?branch=dev` badge
- Keep the existing Documentation completeness badge on its own line

### 2B. `README.md` lines 3-6

Same dual main+dev badge pattern as 2A. Keep existing Version and Documentation badges.

### Verification

```bash
# Verify both main and dev badges present
grep -c 'branch=main' docs/index.md README.md
grep -c 'branch=dev' docs/index.md README.md
```

**Commit:** `feat: add dual main+dev CI badge layout`

---

## Increment 3: Pre-Release Script Enhancement (Phase 3)

### 3A. `scripts/pre-release-check.sh`

**Update total check count** from `/6` to `/8` in all headers.

**Add Check 7** (after Check 6, before Summary):

```bash
# --------------------------------------------------------------------------
# Check 7: Badge URL branch validation
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[7/8] Badge URL branch validation${NC}"

BADGE_ERRORS=0
for file in README.md docs/index.md; do
    if [ -f "$file" ]; then
        if ! grep -q 'badge.svg?branch=main' "$file"; then
            echo -e "${RED}  ✗ $file missing main branch badge${NC}"
            BADGE_ERRORS=$((BADGE_ERRORS + 1))
        fi
        if ! grep -q 'badge.svg?branch=dev' "$file"; then
            echo -e "${RED}  ✗ $file missing dev branch badge${NC}"
            BADGE_ERRORS=$((BADGE_ERRORS + 1))
        fi
    fi
done

if [ $BADGE_ERRORS -gt 0 ]; then
    echo -e "${RED}  ✗ $BADGE_ERRORS badge URL issues found${NC}"
    echo -e "${YELLOW}    Fix: Add main and dev badges to README.md and docs/index.md${NC}"
    ERRORS=$((ERRORS + BADGE_ERRORS))
else
    echo -e "${GREEN}  ✓ Both main and dev badges present${NC}"
fi
```

**Add Check 8:**

```bash
# --------------------------------------------------------------------------
# Check 8: Homebrew formula desc consistency
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[8/8] Homebrew formula desc consistency${NC}"

FORMULA_PATH=""
for candidate in \
    "$HOME/projects/dev-tools/homebrew-tap/Formula/craft.rb" \
    "$(brew --repository 2>/dev/null)/Library/Taps/data-wise/homebrew-tap/Formula/craft.rb"; do
    if [ -f "$candidate" ]; then
        FORMULA_PATH="$candidate"
        break
    fi
done

if [ -n "$FORMULA_PATH" ]; then
    FORMULA_DESC=$(grep '^  desc ' "$FORMULA_PATH" | head -1 | sed 's/.*desc "\(.*\)"/\1/')
    FORMULA_CMD_COUNT=$(echo "$FORMULA_DESC" | grep -o '[0-9]* commands' | grep -o '[0-9]*' || echo "")
    if [ -n "$FORMULA_CMD_COUNT" ] && [ "$FORMULA_CMD_COUNT" != "$CMD_COUNT" ]; then
        echo -e "${YELLOW}  ! Formula desc says $FORMULA_CMD_COUNT commands, actual is $CMD_COUNT${NC}"
    elif [ -n "$FORMULA_CMD_COUNT" ]; then
        echo -e "${GREEN}  ✓ Formula command count matches: $FORMULA_CMD_COUNT${NC}"
    fi
    echo -e "${GREEN}  ✓ Formula desc: \"$FORMULA_DESC\"${NC}"
else
    echo -e "${YELLOW}  - Homebrew formula not found locally (skipping)${NC}"
fi
```

### Verification

```bash
./scripts/pre-release-check.sh 2.26.0
```

**Commit:** `feat: add badge URL and formula desc checks to pre-release script`

---

## Increment 4: Release Skill and Checklist Updates (Phase 4)

### 4A. `skills/release/SKILL.md`

**Expand Step 10 title** from "Verify CI on Main" to "Verify CI on Main (MANDATORY)".

**Add Step 11: Verify Downstream Workflows (NEW)** after Step 10. This section adds five verification subsections:

- **11a: Deploy Documentation Workflow** — run `gh run list --workflow=docs.yml --limit 1` and check conclusion
- **11b: Homebrew Release Workflow** — run `gh run list --workflow=homebrew-release.yml --limit 1` and check conclusion
- **11c: Live Site Version** — `curl` the docs site and extract version string with grep
- **11d: Formula Content Verification** — use `gh api` to fetch formula from homebrew-tap, plus `brew info`
- **11e: Badge Validation** — `curl` the main CI badge SVG, check for "passing" string

**Update Output Format table** — change step counts from `11/11` to `13/13`:

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

```bash
# Verify step references are consistent
grep -c '/13' skills/release/SKILL.md
grep 'Step 1[1-3]' skills/release/SKILL.md
```

**Commit:** `feat: add post-release downstream verification to release skill`

---

## Increment 5: Command Updates (Phase 5)

### 5A. `commands/ci/status.md` — Add `--post-release` argument

Add to frontmatter `arguments:` section:

```yaml
  - name: post-release
    description: Run post-release verification (downstream workflows, live site, formula)
    required: false
    default: false
```

Add new **Post-Release Mode** section after "Failure Summary". When `--post-release` is passed, run extended verification checking:

1. All release-triggered workflows (ci.yml, docs.yml, homebrew-release.yml)
2. Homebrew tap workflows (Data-Wise/homebrew-tap)
3. Live site version via `curl` the docs site
4. Badge URL validation (main and dev badges resolve)
5. `brew info` output for version confirmation

Use the standard box-drawing output format showing each check with pass/fail status.

### 5B. `commands/check.md` — Add badge/formula checks

Add two rows to the **Context-Specific Check Lists** table (the `--for` flag table):

| Check | `--for commit` | `--for pr` | `--for release` | `--for deploy` |
|-------|---------------|-----------|----------------|---------------|
| Badge URLs | Skip | Skip | Validate both branches | Validate both branches |
| Formula desc | Skip | Skip | Check counts match | Skip |

Add two new documentation sections after "Hook Conflict Audit":

**Badge URL Validation (NEW in v2.27.0)** — validates that CI badge URLs in README.md and docs/index.md include both `?branch=main` and `?branch=dev` variants. Runs for `--for release` and `--for deploy`.

**Homebrew Formula Desc Validation (NEW in v2.27.0)** — checks that the Homebrew formula `desc` field command counts match actual counts. Runs for `--for release`. Severity: warning (not blocking).

### Verification

```bash
python3 -c "
import yaml
with open('commands/ci/status.md') as f:
    content = f.read()
    front = content.split('---')[1]
    yaml.safe_load(front)
    print('ci/status.md frontmatter OK')
"
```

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

Add entry under `## [Unreleased]` or `## [2.27.0]` with these items under `### Added`:

- GitHub Actions concurrency groups and docs deploy retry logic
- Dual main+dev CI badge layout in README.md and docs/index.md
- Pre-release checks 7-8: badge URL validation and formula desc consistency
- Post-release downstream verification (Steps 11-13 in release pipeline)
- `/craft:ci:status --post-release` mode for downstream workflow checks
- Badge URL and formula desc validation in `/craft:check --for release`

### Verification

```bash
# Run unit tests
python3 tests/test_craft_plugin.py

# Run broken link check
python3 tests/test_craft_plugin.py -k "broken_links"

# Validate counts
./scripts/validate-counts.sh
```

**Commit:** `docs: update release pipeline docs for 13-step workflow with downstream verification`

---

## Phase 7: Homebrew Formula Desc Fix (Separate Repo)

### 7A. `~/projects/dev-tools/homebrew-tap/Formula/craft.rb` line 6

Change desc from `"Full-stack developer toolkit for Claude Code with 107 commands"` to `"Full-stack developer toolkit for Claude Code"`.

This removes counts from desc to avoid the 80-char Homebrew limit and count drift. Counts exist elsewhere in the formula (caveats block).

**Note:** This is in a separate repo. Handle via direct edit + commit + push, or defer to next release cycle if preferred.

**Commit (in homebrew-tap repo):** `craft: simplify desc to avoid count drift`

---

## Phase 8: Homebrew Local Upgrade

```bash
brew update && brew upgrade data-wise/tap/craft
```

This is a manual step — not committed. Run after Phase 7 changes are pushed.

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
- [ ] `python3 tests/test_craft_plugin.py` unit tests pass
- [ ] `python3 -m pytest tests/test_plugin_e2e.py -v` e2e tests pass
- [ ] `./scripts/validate-counts.sh` counts match
- [ ] Both `docs/index.md` and `README.md` contain `branch=main` badges
- [ ] Both `docs/index.md` and `README.md` contain `branch=dev` badges

---

## Implementation Order

```text
Increment 1 -> Increment 2 -> Increment 3 -> Increment 4 -> Increment 5 -> Increment 6
    (CI)         (Badges)       (Script)       (Skill)        (Commands)      (Docs)
```

Each increment is independently committable. Phases 7-8 (Homebrew) are separate repo operations to do after the main PR.
