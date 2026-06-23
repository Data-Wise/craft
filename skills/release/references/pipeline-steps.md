# Pipeline Steps Reference

Detailed implementation for Steps 1–9 and Steps 11–12. Step 10 (Homebrew) is in
`references/homebrew.md`. Steps 13+ are in `references/downstream-verification.md`.

## Table of Contents

- [Step 1: Determine Version](#step-1-determine-version)
- [Step 2: Pre-Flight Checks](#step-2-pre-flight-checks)
- [Step 3: Version Bump](#step-3-version-bump)
- [Step 3b: Semantic Doc Updates](#step-3b-semantic-doc-updates)
- [Step 4: Commit & Push](#step-4-commit--push)
- [Step 5: Create Release PR](#step-5-create-release-pr)
- [Step 6: Monitor CI on PR](#step-6-monitor-ci-on-pr-mandatory)
- [Step 6.5: CI Monitoring](#step-65-ci-monitoring)
- [Step 7: Merge Release PR](#step-7-merge-release-pr)
- [Step 8: Create GitHub Release](#step-8-create-github-release)
- [Step 9: Post-Release](#step-9-post-release-if-applicable)
- [Step 11: Sync Dev with Main](#step-11-sync-dev-with-main)
- [Step 12: Verify CI on Main](#step-12-verify-ci-on-main-mandatory)

## Step 1: Determine Version

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

## Step 2: Pre-Flight Checks

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

## Step 3: Version Bump

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

## Step 3b: Semantic Doc Updates

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

## Step 4: Commit & Push

```bash
git add <changed-files>
git commit -m "chore: bump version to v<version> for release"
git push
```

Use specific file adds — never `git add -A` or `git add .` for release commits.

## Step 5: Create Release PR

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

## Step 6: Monitor CI on PR (MANDATORY)

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

## Step 6.5: CI Monitoring

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

## Step 7: Merge Release PR

```bash
gh pr merge <number> --merge
```

**NEVER use `--delete-branch`** — the head branch is `dev`, which must not be deleted.

If branch protection blocks the merge, use `--admin` only after user confirmation.

**Autonomous mode:** Auto-uses `--admin` if blocked. Logs a **WARNING** for audit trail. See "Autonomous Admin Override" section for safety details.

## Step 8: Create GitHub Release

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

## Step 9: Post-Release (if applicable)

If the project has a docs site (check for `mkdocs.yml`, `_quarto.yml`, or `docs/` directory):

```bash
mkdocs gh-deploy  # or /craft:site:deploy
```

## Step 11: Sync Dev with Main

```bash
git checkout dev && git pull origin main
git push  # sync origin/dev
```

## Step 12: Verify CI on Main (MANDATORY)

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
