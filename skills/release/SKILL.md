---
name: release
description: This skill should be used when the user asks to "release", "create a release", "ship it", "publish a new version", "bump version and release", "cut a release", or mentions releasing to GitHub/npm/PyPI. Orchestrates the full release pipeline from pre-flight checks through GitHub release creation.
---

# Release Pipeline

Orchestrate end-to-end releases with pre-flight validation, version bumping, PR creation, merge, and GitHub release — all in one flow.

## When to Use

- User says "release", "ship it", "cut a release", or similar
- User wants to publish a new version to GitHub/npm/PyPI
- User is ready to merge dev to main and tag a release

## Prerequisites

- Must be on `dev` branch (or have dev up to date)
- All feature work merged to dev via PRs
- Working tree clean (no uncommitted changes)

## Arguments

| Argument | Alias | Description | Default |
|----------|-------|-------------|---------|
| `--dry-run` | `-n` | Preview release plan without executing | `false` |
| `--autonomous` | `--auto` | Run without user prompts, auto-resolve where possible | `false` |

## Dry-Run Mode

When `--dry-run` or `-n` is passed, execute **only** Step 1 (version detection), then display a preview of every remaining step and exit. No mutations occur.

**Risk Level:** HIGH (modifies git history, creates PRs, publishes releases)

### Dry-Run Output

After detecting the current and next version, display:

```text
┌─────────────────────────────────────────────────────────────┐
│ /release --dry-run                                          │
├─────────────────────────────────────────────────────────────┤
│ Current version: v2.17.0                                    │
│ Next version:    v2.18.0 (minor — feat: commits detected)   │
├─────────────────────────────────────────────────────────────┤
│ Actions that WOULD be taken:                                │
│                                                             │
│  1. ✓ /craft:check --for release (full CI mirror)            │
│  2. ✓ Run pre-release-check.sh v2.18.0 (metadata)           │
│  3. ✓ Bump version in plugin.json, CLAUDE.md                │
│  4. ✓ Commit: "chore: bump version to v2.18.0 for release"  │
│  5. ✓ Push to dev                                           │
│  6. ✓ Create PR: dev → main                                 │
│  6.5 ✓ CI monitoring (poll → diagnose → fix → retry)        │
│  7. ✓ Merge PR (--merge, NO --delete-branch)                │
│  8. ✓ Create GitHub release v2.18.0 on main                 │
│  8.5 ✓ Update Homebrew tap formula                          │
│  9. ✓ Deploy docs site (mkdocs gh-deploy)                   │
│ 10. ✓ Sync dev with main                                    │
├─────────────────────────────────────────────────────────────┤
│ ⚠ Risk: HIGH — modifies git history, creates PRs            │
│ ⚠ No changes were made. Run without --dry-run to execute.   │
└─────────────────────────────────────────────────────────────┘
```

### Dry-Run Guarantees

- No commits, tags, or pushes
- No PRs created or merged
- No GitHub releases published
- No docs deployed
- Exit code 0

## Autonomous Mode (--autonomous)

When `--autonomous` or `--auto` is passed, the release pipeline runs without user interaction:

| Step | Normal | Autonomous |
|------|--------|------------|
| Step 1 (version) | AskUserQuestion to confirm | Auto-select from commit analysis, show decision |
| Step 2 (pre-flight) | Same | Same (fail = abort, no retry) |
| Step 3-5 (bump, commit, PR) | Same | Same (deterministic) |
| Step 6 (merge) | User confirms --admin if blocked | Auto-use --admin, log the override |
| Step 7-8 (release, deploy) | Same | Same (deterministic) |
| Errors | Stop and report | Retry once (step-level), then abort with report |

### Autonomous Safety Checks

Before starting, `--autonomous` validates:

- Working tree is clean (no uncommitted changes)
- Current branch is `dev`
- No existing release PR is open

If any check fails, abort with a clear error message. No retries on safety checks.

### Autonomous Version Detection

```bash
# Analyze commits since last release
commits=$(git log $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD --oneline)

# Determine version bump
if echo "$commits" | grep -qi "breaking\|BREAKING"; then
    bump="major"
elif echo "$commits" | grep -q "^.*feat:"; then
    bump="minor"
else
    bump="patch"
fi

# Show decision (but don't ask)
echo "Auto-detected version bump: $bump (from $(echo "$commits" | wc -l | tr -d ' ') commits)"
```

### Autonomous Admin Override

> **WARNING:** This auto-uses `--admin` to bypass branch protection, which skips required status checks. Only use `--autonomous` when CI has already passed on the PR. For safer unattended releases, use `--autonomous --dry-run` first to preview the plan.

When branch protection blocks the merge in Step 6:

1. Log: "**WARNING:** Branch protection blocking merge. Using --admin override."
2. Run: `gh pr merge <number> --merge --admin`
3. Continue pipeline

### Autonomous Error Recovery

On any step failure:

1. Log the error with full output
2. Retry the step once
3. If retry fails, abort with full error report:

```text
┌─────────────────────────────────────────────────────────────┐
│ /release --autonomous ABORTED                                │
├─────────────────────────────────────────────────────────────┤
│ Failed at: Step 6 (Merge Release PR)                        │
│ Error: Branch protection rules not met                      │
│ Retry: Attempted 1 retry, still failing                     │
│ Completed: Steps 1-5                                        │
│ Rollback: PR #71 still open, no release created             │
├─────────────────────────────────────────────────────────────┤
│ Manual fix needed. Resume with: /release (interactive)       │
└─────────────────────────────────────────────────────────────┘
```

### Combining Flags

- `--autonomous --dry-run`: Shows what autonomous mode WOULD do, without executing
- `--autonomous` alone: Full pipeline with no prompts

## Release Pipeline

Execute these steps in order. Stop and report if any step fails.

### Step 1: Determine Version

Detect current version and determine the next version:

```bash
# Detect version (check in priority order, use first match)
cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || \
cat package.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || \
git describe --tags --abbrev=0 2>/dev/null || echo "unknown"
```

If the user specified a version, use it. Otherwise, analyze commits since last release to suggest:

- **patch** (x.y.Z): only `fix:` and `chore:` commits
- **minor** (x.Y.0): any `feat:` commits
- **major** (X.0.0): any breaking changes or user-specified

Ask the user to confirm the version before proceeding.

**Autonomous mode:** Skips this confirmation. Uses auto-detected version and shows the decision in output.

### Step 2: Pre-Flight Checks

Run two complementary validations. **Both must pass** before proceeding.

#### 2a: Full CI Mirror (`/craft:check --for release`)

Run the full test suite, lint, and validation — the same checks CI runs:

```bash
/craft:check --for release
```

This runs: full pytest (unit + integration + e2e), strict lint, security audit, docs validation, and 90% coverage threshold. Catches test failures that would break CI after push.

#### 2b: Release Metadata (`pre-release-check.sh`)

Run release-specific consistency checks:

```bash
# Craft plugin projects
./scripts/pre-release-check.sh <version>

# General projects — skip (covered by 2a)
```

This checks: version consistency across files, command/skill/agent count accuracy, CLAUDE.md version refs, README.md and docs/index.md version refs, clean working tree.

#### 2c: Marketplace Validation (if applicable)

If `.claude-plugin/marketplace.json` exists, validate marketplace distribution:

```bash
# Run Claude plugin validator
claude plugin validate .

# Check version consistency
MARKETPLACE_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['metadata']['version'])")
PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
if [ "$MARKETPLACE_VERSION" != "$PLUGIN_VERSION" ]; then
    echo "ERROR: marketplace.json version ($MARKETPLACE_VERSION) != plugin.json ($PLUGIN_VERSION)"
    exit 1
fi
```

Skip this step if marketplace.json doesn't exist (not all projects use marketplace distribution).

#### If Pre-Flight Fails

Fix issues and re-run from 2a. Common fixes:

- Test failure: fix the test or the code it validates
- Version mismatch: update plugin.json/package.json
- CLAUDE.md version refs: update version string
- Uncommitted changes: commit or stash

### Step 3: Version Bump

For **Craft plugin projects**, use the automated bump script:

```bash
# Preview what will change
./scripts/bump-version.sh <version> --dry-run

# Apply version bump + count sync across all 9 files
./scripts/bump-version.sh <version>

# Verify consistency
./scripts/bump-version.sh --verify
```

This atomically updates: `plugin.json`, `marketplace.json`, `package.json`, `CLAUDE.md`, `README.md`, `docs/index.md`, `docs/REFCARD.md`, `mkdocs.yml`, and `.STATUS`.

For **other project types**, update manually:

| Project Type | Files to Update |
|-------------|-----------------|
| Python | `pyproject.toml`, `__init__.py`, `README.md` |
| Node | `package.json`, `package-lock.json`, `README.md` |
| R package | `DESCRIPTION`, `NEWS.md`, `README.md` |

**Verification** (run after bump):

```bash
./scripts/bump-version.sh --verify
```

### Step 4: Commit & Push

```bash
git add <changed-files>
git commit -m "chore: bump version to v<version> for release"
git push
```

Use specific file adds — never `git add -A` or `git add .` for release commits.

### Step 5: Create Release PR

Create PR from dev to main:

```bash
gh pr create --base main --head dev \
  --title "Release: v<version> — <title>" \
  --body "<release-notes>"
```

**Critical rules for PR body:**

- Avoid literal destructive git commands in the body text (branch guard hooks scan PR creation commands)
- Use descriptive language instead:
  - DO: "Blocks dangerous git operations that discard changes"
  - DON'T: Include the actual command strings that branch guard detects
- Include a test plan checklist with results

### Step 6: Monitor CI on PR (MANDATORY)

**Do NOT skip this step.** After the PR is created, poll CI before merging:

```bash
# Poll until CI completes (max 5 min)
for i in $(seq 1 10); do
    STATUS=$(gh run list --branch dev --limit 1 --json status,conclusion --jq '.[0].status + " " + (.[0].conclusion // "pending")')
    echo "[Poll $i] $STATUS"
    if [[ "$STATUS" == "completed success" ]]; then
        echo "✅ CI passed — proceeding to merge"
        break
    elif [[ "$STATUS" == "completed failure" ]]; then
        echo "❌ CI failed — diagnose before merging"
        gh run view $(gh run list --branch dev --limit 1 --json databaseId --jq '.[0].databaseId') --log-failed 2>&1 | tail -20
        # Ask user before proceeding
        break
    fi
    sleep 30
done
```

**If CI fails:** Diagnose the failure, fix on dev, push, and wait for the new run to pass. Only use `--admin` merge as a last resort after user confirmation.

**If CI takes too long (>5 min):** Ask user whether to wait or merge with `--admin`.

### Step 7: Merge Release PR

```bash
gh pr merge <number> --merge
```

**NEVER use `--delete-branch`** — the head branch is `dev`, which must not be deleted.

If branch protection blocks the merge, use `--admin` only after user confirmation.

**Autonomous mode:** Auto-uses `--admin` if blocked. Logs a **WARNING** for audit trail. See "Autonomous Admin Override" section for safety details.

### Step 6.5: CI Monitoring (NEW in v2.22.0)

After creating the PR (Step 5) but before merging (Step 6), monitor CI status and auto-fix safe failures.

**Script:** `scripts/ci-monitor.sh`

```bash
# Poll CI status for the release PR
bash scripts/ci-monitor.sh <pr-number>
```

**Behavior:**

1. Poll `gh run list` every 30s (configurable via `.claude/release-config.json`)
2. On **success**: proceed to Step 6 (merge)
3. On **failure**: diagnose, categorize, and attempt fix
4. Max 3 retry cycles before reporting to user

**Auto-fix categories** (applied without asking):

| Category | Fix Strategy |
|----------|-------------|
| `version_mismatch` | Run `scripts/version-sync.sh --fix`, update files, commit + push |
| `lint_failure` | Run linter with `--fix` flag, commit + push |
| `changelog_format` | Reformat CHANGELOG entries, commit + push |

**Ask-before-fix categories** (require user approval):

| Category | Why |
|----------|-----|
| `test_failure` | May indicate real bugs, not just formatting |
| `security_audit` | Vulnerability fixes need careful review |
| `build_failure` | Root cause may be complex |

**Configuration:** `.claude/release-config.json`

```json
{
    "ci_timeout": 600,
    "ci_max_retries": 3,
    "ci_poll_interval": 30,
    "ci_auto_fix_categories": ["version_mismatch", "lint_failure", "changelog_format"],
    "ci_ask_before_fix": ["test_failure", "security_audit", "build_failure"]
}
```

**Output format:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 6.5: CI Monitoring                                     │
├─────────────────────────────────────────────────────────────┤
│ Polling CI status for PR #85...                             │
│                                                             │
│ [Poll 1] ⏳ In progress (30s elapsed)                       │
│ [Poll 2] ⏳ In progress (60s elapsed)                       │
│ [Poll 3] ✅ All checks passed (90s elapsed)                  │
│                                                             │
│ Proceeding to Step 6: Merge PR                              │
└─────────────────────────────────────────────────────────────┘
```

**Autonomous mode:** Auto-fixes are applied without prompts. Ask-before-fix categories abort with a report.

**Timeout:** If CI doesn't complete within `ci_timeout` seconds, report to user and ask whether to wait longer or merge with `--admin`.

### Step 7: Create GitHub Release

```bash
git pull origin main

gh release create v<version> --target main \
  --title "v<version> — <title>" \
  --notes "<release-notes>"
```

Generate release notes by analyzing commits since last release (`git log <last-tag>..HEAD --oneline`). Include:

- Highlights section with key features
- List of changes grouped by type
- Test count and stats
- Link to full changelog comparison

### Step 8: Post-Release (if applicable)

If the project has a docs site (check for `mkdocs.yml`, `_quarto.yml`, or `docs/` directory):

```bash
mkdocs gh-deploy  # or /craft:site:deploy
```

### Step 8.5: Update Homebrew Tap (if applicable)

If the project has a Homebrew formula in the `data-wise/tap`, update it with the new version.

#### Formula Name Lookup Chain

Determine the formula name using this priority order:

1. **Config file** — `.craft/homebrew.json` (most reliable)
2. **Git remote** — extract repo name from `origin` URL
3. **Directory basename** — fallback (least reliable)

```bash
# 1. Config file (preferred)
if [ -f ".craft/homebrew.json" ]; then
    FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])")
    TAP=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['tap'])")
# 2. Git remote mapping
elif git remote get-url origin &>/dev/null; then
    REPO_NAME=$(git remote get-url origin | sed 's/\.git$//' | sed 's|.*/||' | tr '[:upper:]' '[:lower:]')
    FORMULA_NAME="$REPO_NAME"
    TAP="data-wise/tap"
# 3. Basename fallback
else
    FORMULA_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]')
    TAP="data-wise/tap"
fi
```

#### `.craft/homebrew.json` Config Format

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `formula_name` | Yes | Name of the Homebrew formula (e.g., `craft`, `aiterm`) |
| `tap` | Yes | Tap in `org/name` format (e.g., `data-wise/tap`) |
| `source_type` | No | `github` (default) or `pypi` |

#### Tap Update Script

```bash
# Locate tap directory
TAP_ORG=$(echo "$TAP" | cut -d/ -f1)
TAP_NAME=$(echo "$TAP" | cut -d/ -f2)
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-${TAP_NAME}"
TAP_BREW="$(brew --repository 2>/dev/null)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}"

if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
    cd "$TAP_DIR" && git pull
elif [ -d "$TAP_BREW" ]; then
    TAP_DIR="$TAP_BREW"
    cd "$TAP_DIR" && git pull
else
    echo "No local tap found — skip tap update (CI workflow handles this)"
fi

if [ -n "$TAP_DIR" ]; then
    FORMULA="$TAP_DIR/Formula/${FORMULA_NAME}.rb"
    if [ -f "$FORMULA" ]; then
        # Calculate SHA256 from GitHub release tarball
        REPO=$(git remote get-url origin | sed 's/\.git$//' | sed 's|https://github.com/||')
        SHA256=$(curl -sL --retry 3 --retry-delay 2 "https://github.com/${REPO}/archive/refs/tags/v${VERSION}.tar.gz" | shasum -a 256 | cut -d' ' -f1)

        # Validate SHA256 is not empty
        if [ -z "$SHA256" ] || [ ${#SHA256} -ne 64 ]; then
            echo "ERROR: SHA256 calculation failed. Got: '$SHA256'"
            exit 1
        fi

        # Update version and sha256 in formula
        sed -i '' "s|/archive/refs/tags/v[0-9.]*\.tar\.gz|/archive/refs/tags/v${VERSION}.tar.gz|" "$FORMULA"
        sed -i '' "s/sha256 \"[a-f0-9]*\"/sha256 \"${SHA256}\"/" "$FORMULA"

        # Syntax check before committing
        ruby -c "$FORMULA" || { echo "ERROR: Formula has syntax errors after update"; exit 1; }

        # Commit and push
        cd "$TAP_DIR"
        git add "Formula/${FORMULA_NAME}.rb"
        git commit -m "${FORMULA_NAME}: update to v${VERSION}"
        git push
        echo "Homebrew tap updated: ${FORMULA_NAME} v${VERSION}"
    fi
fi
```

Skip if no local tap exists — the GitHub Actions workflow (`homebrew-release.yml`) handles tap updates automatically on release trigger.

#### Verify Homebrew Release Workflow

After the GitHub release is created, verify the `homebrew-release` workflow succeeded:

```bash
# Wait for workflow to trigger
sleep 30

# Check homebrew-release workflow status
gh run list --repo Data-Wise/craft --workflow=homebrew-release.yml --limit 1 \
  --json status,conclusion --jq '.[0]'
```

If the workflow failed, check with `/craft:ci:status` for diagnosis.

### Step 9: Sync Dev with Main

```bash
git checkout dev && git pull origin main
git push  # sync origin/dev
```

### Step 10: Verify CI on Main (MANDATORY)

After merge, verify CI passes on main. This catches issues like missing CI dependencies.

```bash
# Wait for CI to start on main
sleep 10

# Poll CI on main
gh run list --branch main --limit 1 --json status,conclusion,databaseId \
  --jq '.[0] | .status + " " + (.conclusion // "pending") + " (run " + (.databaseId|tostring) + ")"'

# If failed, check logs
gh run view <run-id> --log-failed 2>&1 | tail -30
```

**If CI fails on main:** This is critical — the release tag points to broken code. Fix immediately on dev, then merge to main (patch release if needed).

## Output Format

Display progress using box-drawing:

```
┌─────────────────────────────────────────────────────────────┐
│ /release v2.17.0                                            │
├─────────────────────────────────────────────────────────────┤
│ [ 1/11] CI mirror check .................... PASSED          │
│ [ 2/11] Release metadata check ............. PASSED          │
│ [ 3/11] Version bump ....................... DONE             │
│ [ 4/11] Commit & push ..................... DONE              │
│ [ 5/11] Release PR created ................. PR #70          │
│ [ 6/11] CI monitoring ..................... GREEN (90s)       │
│ [ 7/11] PR merged .......................... DONE             │
│ [ 8/11] GitHub release ..................... v2.17.0          │
│ [ 9/11] Docs deployed ..................... DONE              │
│ [10/11] Dev synced ........................ DONE               │
│ [11/11] Verify CI on main ................. PASSED            │
├─────────────────────────────────────────────────────────────┤
│ Release URL: https://github.com/.../releases/tag/v2.17.0   │
└─────────────────────────────────────────────────────────────┘
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Pre-flight fails | Fix issues, re-run check |
| PR body triggers branch guard | Rephrase to avoid literal command strings |
| Branch protection blocks merge | Use `--admin` with user confirmation |
| Tag already exists | Verify correct version, delete stale tag if needed |
| Docs deploy fails | Run `mkdocs build` first to check for errors |

## Additional Resources

### Reference Files

- **`references/release-checklist.md`** — Detailed per-project-type checklists and edge cases
