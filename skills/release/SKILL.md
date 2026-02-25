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
│  9. ✓ Deploy docs site (mkdocs gh-deploy)                   │
│ 10. ✓ Update Homebrew tap formula                           │
│ 11. ✓ Sync dev with main                                    │
│ 12. ✓ Verify CI on main                                     │
│ 13. ✓ Verify downstream (docs, brew, badges)                │
│ 13.5 ✓ Post-release sweep (Tier 2+ drift detection)        │
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
| Step 7 (merge) | User confirms --admin if blocked | Auto-use --admin, log the override |
| Step 8-13 (release, deploy, verify) | Same | Same (deterministic) |
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

When branch protection blocks the merge in Step 7:

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
│ Failed at: Step 7 (Merge Release PR)                        │
│ Error: Branch protection rules not met                      │
│ Retry: Attempted 1 retry, still failing                     │
│ Completed: Steps 1-6                                        │
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

# Apply version bump + count sync across all 13 files
./scripts/bump-version.sh <version>

# Verify consistency
./scripts/bump-version.sh --verify
```

This atomically updates 13 files: `plugin.json`, `marketplace.json`, `package.json`, `CLAUDE.md`, `README.md`, `docs/index.md`, `docs/REFCARD.md`, `mkdocs.yml`, `.STATUS`, `docs/DEPENDENCY-ARCHITECTURE.md`, `docs/reference/configuration.md`, `commands/hub.md`, `docs/commands/hub.md`.

### Step 3b: Semantic Doc Updates

After `bump-version.sh` handles mechanical version substitution, update these files with **release-specific content** (title, summary, changelog entry). The release title comes from Step 1.

| File | What to Update |
|------|---------------|
| `CHANGELOG.md` | Insert new version entry with summary from commit analysis |
| `VERSION-HISTORY.md` | Insert new version section with highlights |
| `README.md` | Update release title line (if present) |
| `docs/index.md` | Update `!!! info` box title and description text |
| `docs/REFCARD.md` | Update summary line ~11 title text (after the version) |
| `mkdocs.yml` | Update `site_description` tagline after "adds" to describe new release |
| `commands/hub.md` | Update version in banner template, test count, skill count |
| `docs/commands/hub.md` | Same updates as `commands/hub.md` (published copy) |

**Key distinction:** Step 3 handles mechanical `X.Y.Z` substitution. Step 3b handles semantic content that requires the release title and human judgment.

For **other project types**, update manually:

| Project Type | Files to Update |
|-------------|-----------------|
| Python | `pyproject.toml`, `__init__.py`, `README.md` |
| Node | `package.json`, `package-lock.json`, `README.md` |
| R package | `DESCRIPTION`, `NEWS.md`, `README.md` |

**Verification** (run after bump):

```bash
# Verify automated files (13 files)
./scripts/bump-version.sh --verify

# Sweep for stale refs in long-tail files (comments, CI, examples, brainstorms)
grep -rn "OLD_VERSION\|OLD_CMD_COUNT commands\|OLD_SKILL_COUNT skills" \
  --include="*.md" --include="*.sh" --include="*.yml" --include="*.py" \
  | grep -v CHANGELOG | grep -v archive/ | grep -v node_modules/
```

Replace `OLD_VERSION`, `OLD_CMD_COUNT`, `OLD_SKILL_COUNT` with the previous release values. Fix any hits before committing.

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

After creating the PR (Step 5) but before merging (Step 7), monitor CI status and auto-fix safe failures.

**Script:** `scripts/ci-monitor.sh`

```bash
# Poll CI status for the release PR
bash scripts/ci-monitor.sh <pr-number>
```

**Behavior:**

1. Poll `gh run list` every 30s (configurable via `.claude/release-config.json`)
2. On **success**: proceed to Step 7 (merge)
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
│ Proceeding to Step 7: Merge PR                              │
└─────────────────────────────────────────────────────────────┘
```

**Autonomous mode:** Auto-fixes are applied without prompts. Ask-before-fix categories abort with a report.

**Timeout:** If CI doesn't complete within `ci_timeout` seconds, report to user and ask whether to wait longer or merge with `--admin`.

### Step 8: Create GitHub Release

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

### Step 9: Post-Release (if applicable)

If the project has a docs site (check for `mkdocs.yml`, `_quarto.yml`, or `docs/` directory):

```bash
mkdocs gh-deploy  # or /craft:site:deploy
```

### Step 10: Update Homebrew Tap (if applicable)

If the project has a Homebrew formula or cask in the `data-wise/tap`, update it with the new version.

#### Distribution Type Detection

Determine whether this is a Formula (CLI tool) or Cask (desktop app) release:

```bash
# 1. Explicit config (highest priority)
if [ -f ".craft/homebrew.json" ]; then
    DIST_TYPE=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json')).get('type', 'formula'))")
    FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])")
    TAP=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['tap'])")

# 2. Tauri project auto-detection
elif [ -f "src-tauri/tauri.conf.json" ]; then
    DIST_TYPE="cask"
    FORMULA_NAME=$(python3 -c "import json; c=json.load(open('src-tauri/tauri.conf.json')); print(c.get('productName', c.get('package', {}).get('productName', 'unknown')).lower())")
    TAP="data-wise/tap"

# 3. Git remote mapping (formula default)
elif git remote get-url origin &>/dev/null; then
    DIST_TYPE="formula"
    REPO_NAME=$(git remote get-url origin | sed 's/\.git$//' | sed 's|.*/||' | tr '[:upper:]' '[:lower:]')
    FORMULA_NAME="$REPO_NAME"
    TAP="data-wise/tap"

# 4. Basename fallback (formula default)
else
    DIST_TYPE="formula"
    FORMULA_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]')
    TAP="data-wise/tap"
fi

# Route to appropriate step
if [ "$DIST_TYPE" = "cask" ]; then
    echo "Detected: Cask distribution (desktop app) → Step 10b"
    # Proceed to Step 10b (Cask release pipeline)
else
    echo "Detected: Formula distribution (CLI tool) → Step 10a"
    # Proceed to Step 10a (existing formula update)
fi
```

#### Step 10a: Update Formula (existing behavior)

For CLI tools distributed as Homebrew Formulas. This is the existing formula update path, unchanged.

##### Formula Name Lookup Chain

Determine the formula name using this priority order:

1. **Config file** — `.craft/homebrew.json` (most reliable)
2. **Git remote** — extract repo name from `origin` URL
3. **Directory basename** — fallback (least reliable)

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

#### Step 10b: Desktop App Cask Release (Tauri)

For desktop apps distributed as Homebrew Casks. Triggered when detection finds `src-tauri/tauri.conf.json` or `.craft/homebrew.json` has `"type": "cask"`.

**Overview:** Build multi-arch DMGs → upload to GitHub release → compute SHA256 from local artifacts → update cask file → push tap.

**Progress display:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 10b: Desktop App Release (Tauri)                        │
├─────────────────────────────────────────────────────────────┤
│  [1/8] Detecting project type ............ Tauri (Scribe)   │
│  [2/8] Checking build environment ........ 6/6 passed       │
│  [3/8] Building aarch64 (native) ......... DONE (2m 14s)    │
│  [4/8] Building x86_64 (cross-compile) ... DONE (4m 31s)    │
│  [5/8] Verifying architectures ........... PASSED            │
│  [6/8] Computing SHA256 .................. DONE              │
│  [7/8] Uploading to GitHub release ....... DONE              │
│  [8/8] Updating cask + pushing tap ....... DONE              │
└─────────────────────────────────────────────────────────────┘
```

##### 10b-1: Read Project Config

```bash
# Read from tauri.conf.json
TAURI_CONF="src-tauri/tauri.conf.json"
PRODUCT_NAME=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('productName', c.get('package', {}).get('productName', 'unknown')))")
VERSION=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('version', 'unknown'))")
IDENTIFIER=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('identifier', c.get('tauri', {}).get('bundle', {}).get('identifier', 'unknown')))")

# Override from .craft/homebrew.json if present
if [ -f ".craft/homebrew.json" ]; then
    FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])")
    TAP=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['tap'])")
    # Read cask-specific overrides
    CASK_CONFIG=$(python3 -c "import json; print(json.dumps(json.load(open('.craft/homebrew.json')).get('cask', {})))")
else
    FORMULA_NAME=$(echo "$PRODUCT_NAME" | tr '[:upper:]' '[:lower:]')
    TAP="data-wise/tap"
fi
```

##### 10b-2: Build Environment Validation

```bash
ERRORS=0

# Check Rust targets
NATIVE_TARGET="aarch64-apple-darwin"
CROSS_TARGET="x86_64-apple-darwin"
for TARGET in "$NATIVE_TARGET" "$CROSS_TARGET"; do
    if ! rustup target list --installed | grep -q "$TARGET"; then
        echo "MISSING: Rust target $TARGET"
        echo "  Fix: rustup target add $TARGET"
        echo "  Or:  Install now and continue? (y/n)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Tauri CLI
if ! npx tauri --version &>/dev/null 2>&1 && ! command -v cargo-tauri &>/dev/null; then
    echo "MISSING: Tauri CLI (fix: cargo install tauri-cli)"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js + node_modules
if ! command -v node &>/dev/null; then
    echo "MISSING: Node.js (fix: brew install node)"
    ERRORS=$((ERRORS + 1))
fi
if [ ! -d "node_modules" ]; then
    echo "MISSING: node_modules (fix: npm install)"
    ERRORS=$((ERRORS + 1))
fi

# Check Xcode SDK
if ! xcrun --show-sdk-path &>/dev/null 2>&1; then
    echo "MISSING: Xcode SDK (fix: xcode-select --install)"
    ERRORS=$((ERRORS + 1))
fi

# Check disk space (>= 2GB free)
FREE_KB=$(df -k . | tail -1 | awk '{print $4}')
if [ "$FREE_KB" -lt 2097152 ]; then
    echo "WARNING: Less than 2GB free disk space"
    ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
    echo "ERROR: $ERRORS pre-build checks failed. Fix and retry."
    exit 1
fi
```

##### 10b-3: Multi-Architecture Build (Serial)

Build native architecture first (fast, catches errors early), then cross-compile:

```bash
# Build 1: Native arch (aarch64 on Apple Silicon)
echo "[3/8] Building aarch64 (native)..."
BUILD_START=$(date +%s)
npx tauri build --target "$NATIVE_TARGET"
BUILD_END=$(date +%s)
echo "  DONE ($((BUILD_END - BUILD_START))s)"

# Locate DMG (primary path with fallback)
DMG_ARM="src-tauri/target/$NATIVE_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_aarch64.dmg"
if [ ! -f "$DMG_ARM" ]; then
    DMG_ARM=$(find "src-tauri/target/$NATIVE_TARGET/release/bundle" -name "*.dmg" -type f | head -1)
fi
if [ ! -f "$DMG_ARM" ]; then
    echo "ERROR: ARM DMG not found after build"
    exit 1
fi

# Build 2: Cross-compile (x86_64)
echo "[4/8] Building x86_64 (cross-compile)..."
BUILD_START=$(date +%s)
npx tauri build --target "$CROSS_TARGET"
BUILD_END=$(date +%s)
echo "  DONE ($((BUILD_END - BUILD_START))s)"

# Locate DMG
DMG_INTEL="src-tauri/target/$CROSS_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_x64.dmg"
if [ ! -f "$DMG_INTEL" ]; then
    DMG_INTEL=$(find "src-tauri/target/$CROSS_TARGET/release/bundle" -name "*.dmg" -type f | head -1)
fi
if [ ! -f "$DMG_INTEL" ]; then
    echo "ERROR: Intel DMG not found after build"
    exit 1
fi
```

##### 10b-4: Architecture Verification

Verify each DMG contains the correct architecture binary:

```bash
echo "[5/8] Verifying architectures..."
verify_arch() {
    local DMG_PATH="$1"
    local EXPECTED="$2"
    local MOUNT_POINT="/Volumes/${PRODUCT_NAME}_verify_$$"

    hdiutil attach "$DMG_PATH" -nobrowse -quiet -mountpoint "$MOUNT_POINT"
    BINARY=$(find "$MOUNT_POINT" -name "$PRODUCT_NAME" -type f -perm +111 | head -1)
    ARCH=$(file "$BINARY" | grep -oE 'arm64|x86_64')
    hdiutil detach "$MOUNT_POINT" -quiet

    if [ "$ARCH" != "$EXPECTED" ]; then
        echo "ERROR: DMG contains $ARCH binary, expected $EXPECTED"
        return 1
    fi
    echo "  ✓ $DMG_PATH → $ARCH"
}

verify_arch "$DMG_ARM" "arm64"
verify_arch "$DMG_INTEL" "x86_64"
```

##### 10b-5: SHA256 Computation (Local Artifacts)

Compute SHA256 from local build artifacts — no network involved:

```bash
echo "[6/8] Computing SHA256..."
SHA256_ARM=$(shasum -a 256 "$DMG_ARM" | cut -d' ' -f1)
SHA256_INTEL=$(shasum -a 256 "$DMG_INTEL" | cut -d' ' -f1)

# Validate both are 64-char hex strings
for SHA in "$SHA256_ARM" "$SHA256_INTEL"; do
    if [ -z "$SHA" ] || [ ${#SHA} -ne 64 ]; then
        echo "ERROR: SHA256 calculation failed. Got: '$SHA'"
        exit 1
    fi
done

echo "  ARM:   $SHA256_ARM"
echo "  Intel: $SHA256_INTEL"
```

**Key design decision:** Computing SHA256 from local artifacts eliminates the race condition where GitHub CDN hasn't propagated uploaded assets yet. This was the root cause of tap conflicts during earlier Scribe releases.

##### 10b-6: Asset Upload to GitHub Release

```bash
echo "[7/8] Uploading to GitHub release..."
REPO=$(git remote get-url origin | sed 's/\.git$//' | sed 's|https://github.com/||')

# Upload DMGs (--clobber handles re-uploads)
gh release upload "v${VERSION}" "$DMG_ARM" "$DMG_INTEL" --clobber

# Generate and upload CHECKSUMS.txt
echo "${SHA256_ARM}  ${PRODUCT_NAME}_${VERSION}_aarch64.dmg" > CHECKSUMS.txt
echo "${SHA256_INTEL}  ${PRODUCT_NAME}_${VERSION}_x64.dmg" >> CHECKSUMS.txt
gh release upload "v${VERSION}" CHECKSUMS.txt --clobber

# Verify upload (check URLs return 200)
for ARCH in "aarch64" "x64"; do
    URL="https://github.com/${REPO}/releases/download/v${VERSION}/${PRODUCT_NAME}_${VERSION}_${ARCH}.dmg"
    STATUS=$(curl -sI -o /dev/null -w "%{http_code}" -L "$URL")
    if [ "$STATUS" != "200" ]; then
        echo "WARNING: Asset URL returned $STATUS (CDN may need propagation time)"
    fi
done
```

##### 10b-7: Cask File Update

Update the cask file with new version, SHA256 hashes, and content:

```bash
echo "[8/8] Updating cask + pushing tap..."

# Locate tap directory
TAP_ORG=$(echo "$TAP" | cut -d/ -f1)
TAP_NAME=$(echo "$TAP" | cut -d/ -f2)
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-${TAP_NAME}"
TAP_BREW="$(brew --repository 2>/dev/null)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}"

if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
elif [ -d "$TAP_BREW" ]; then
    TAP_DIR="$TAP_BREW"
else
    echo "No local tap found — skip tap update (CI workflow handles this)"
    # Skip to Step 11
fi

CASK_FILE="$TAP_DIR/Casks/${FORMULA_NAME}.rb"

if [ -f "$CASK_FILE" ]; then
    # --- Zone 1: Update version and SHA256 ---

    # Update version field
    sed -i '' 's/version ".*"/version "'"$VERSION"'"/' "$CASK_FILE"

    # Update SHA256 in architecture blocks (regex targets block structure)
    python3 -c "
import re, sys
content = open(sys.argv[1]).read()
content = re.sub(
    r'(on_arm do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>$SHA256_ARM\2', content)
content = re.sub(
    r'(on_intel do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>$SHA256_INTEL\2', content)
open(sys.argv[1], 'w').write(content)
" "$CASK_FILE"

    # --- Zone 2: Migrate hardcoded version strings to #{version} ---
    sed -i '' "s/What's New in v[0-9.]*:/What's New in v#{version}:/" "$CASK_FILE"
    sed -i '' "s/New in v[0-9.]*:/New in v#{version}:/" "$CASK_FILE"

    # --- Zone 3: Dynamic content (postflight/caveats bullets) ---
    # Updated by --update-content flag (see Increment 4)
    # During /release, content update runs automatically with preview

    # --- Validate ---
    ruby -c "$CASK_FILE" || { echo "ERROR: Cask has syntax errors after update"; exit 1; }
    echo "  ✓ Version: updated to $VERSION"
    echo "  ✓ SHA256 (on_arm): updated"
    echo "  ✓ SHA256 (on_intel): updated"
    echo "  ✓ ruby -c: PASSED"

else
    echo "Cask file not found at $CASK_FILE"
    echo "Generate a new cask with: /craft:dist:homebrew cask"
    # Skip tap push if no cask file exists
fi
```

##### 10b-8: Tap Push with Conflict Resolution

```bash
if [ -n "$TAP_DIR" ] && [ -f "$CASK_FILE" ]; then
    cd "$TAP_DIR"

    # Pull latest with rebase (avoid merge commits in tap)
    git pull --rebase origin main || {
        echo "Rebase conflict — resolving with ours (fresh SHA256 wins)"
        git checkout --ours "Casks/${FORMULA_NAME}.rb"
        git add "Casks/${FORMULA_NAME}.rb"
        git rebase --continue
    }

    # Commit and push
    git add "Casks/${FORMULA_NAME}.rb"
    git commit -m "${FORMULA_NAME}: update to v${VERSION}"
    git push origin main || {
        echo "Push failed — retrying after pull"
        git pull --rebase origin main
        git push origin main
    }

    echo "  ✓ Tap push: ${TAP}/${FORMULA_NAME} v${VERSION}"
fi
```

> **Conflict resolution strategy:** "Ours" always wins because the local cask has freshly computed SHA256 hashes from local build artifacts. Any remote SHA256 values are stale by definition.

**Skip to Step 11 after Step 10b completes.**

### Step 11: Sync Dev with Main

```bash
git checkout dev && git pull origin main
git push  # sync origin/dev
```

### Step 12: Verify CI on Main (MANDATORY)

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

### Step 13: Verify Downstream Workflows (MANDATORY)

After CI passes on main, verify all downstream workflows and artifacts are correct. This catches silent failures in deploy pipelines, Homebrew distribution, and badge rendering.

#### 13a: Deploy Documentation Workflow

```bash
# Check the latest docs deploy workflow run
gh run list --workflow=docs.yml --limit 1 \
  --json status,conclusion,createdAt --jq '.[0]'
```

If `conclusion` is not `success`, check logs with `gh run view <id> --log-failed`.

#### 13b: Homebrew Release Workflow

```bash
# Check the latest homebrew-release workflow run
gh run list --workflow=homebrew-release.yml --limit 1 \
  --json status,conclusion,createdAt --jq '.[0]'
```

If `conclusion` is not `success`, check with `/craft:ci:status` for diagnosis.

#### 13c: Live Site Version

```bash
# Verify the live docs site shows the new version
curl -sL https://data-wise.github.io/craft/ | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+'
```

Compare the extracted version string against the release version. If stale, the docs workflow may have failed silently.

#### 13d: Formula Content Verification

```bash
# Fetch formula from the tap repo and verify version + SHA
gh api repos/Data-Wise/homebrew-tap/contents/Formula/craft.rb \
  --jq '.content' | base64 -d | grep -E '(version|sha256|desc)'

# Also verify via brew info
brew info data-wise/tap/craft
```

Confirm: version matches release, SHA256 is non-empty and 64 chars, description is present.

#### 13e: Badge Validation

```bash
# Fetch the main CI badge and check for "passing"
curl -sL "https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg" | grep -q "passing" \
  && echo "Badge: PASSING" || echo "Badge: NOT PASSING"
```

If the badge does not show "passing", CI may still be running or may have failed. Wait and re-check.

### Step 13.5: Post-Release Sweep (RECOMMENDED)

After downstream verification passes, run the post-release sweep to catch Tier 2+ drift — secondary version references, stale counts, and content staleness that `bump-version.sh` doesn't manage.

```bash
# Normal mode: auto-fix mechanical items, commit if changes made
./scripts/post-release-sweep.sh --fix
# If fixes were applied:
git add -u && git commit -m "chore: fix post-release drift detected by sweep"
git push
```

**Dry-run mode:** Run report-only (no changes):

```bash
./scripts/post-release-sweep.sh
```

**Autonomous mode:** Same as normal mode — auto-fix is safe for mechanical items (version string replacements in secondary docs).

**What it catches:**

| Tier | Scope | Fix Mode |
|------|-------|----------|
| 1 | Core files (via `bump-version.sh --verify`) | Auto |
| 2 | Secondary docs (REFCARD-RELEASE, guides, etc.) | Auto (`--fix`) |
| 2 | Stale test/command counts in docs | Manual review |
| 3 | Content staleness (CHANGELOG vs index.md) | Manual review |

If `--fix` makes changes, commit them before completing the release.

## Output Format

Display progress using box-drawing:

```
┌─────────────────────────────────────────────────────────────┐
│ /release v2.17.0                                            │
├─────────────────────────────────────────────────────────────┤
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
