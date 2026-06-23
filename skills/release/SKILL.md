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
| `--skip-surfaces` | — | Skip Step 13.6 multi-surface version assertion | `false` |

## Dry-Run Mode

When `--dry-run` or `-n` is passed, execute **only** Step 1 (version detection), then display a preview of every remaining step and exit. No mutations occur.

**Risk Level:** HIGH (modifies git history, creates PRs, publishes releases)

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
│ 10. ✓ Update Homebrew tap (formula or cask)                 │
│      (10b if Tauri: build → upload → SHA256 → cask → tap)   │
│ 11. ✓ Sync dev with main                                    │
│ 12. ✓ Verify CI on main                                     │
│ 13. ✓ Verify downstream (docs, brew, badges, cask)          │
│ 13.5 ✓ Post-release sweep (Tier 2+ drift detection)        │
├─────────────────────────────────────────────────────────────┤
│ ⚠ Risk: HIGH — modifies git history, creates PRs            │
│ ⚠ No changes were made. Run without --dry-run to execute.   │
└─────────────────────────────────────────────────────────────┘
```

Guarantees: no commits, tags, pushes, PRs, GitHub releases, or docs deploys. Exit code 0.

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

Before starting, `--autonomous` validates: clean working tree, on `dev` branch, no existing release PR open. Fail = abort, no retry.

**Safety note:** `--autonomous` auto-uses `--admin` to bypass branch protection if needed. Only use when CI has already passed. For unattended preview, use `--autonomous --dry-run` first.

Version detection, admin override logic, and the abort report format are in
**`references/autonomous-mode.md`**.

Combining flags: `--autonomous --dry-run` shows what autonomous mode WOULD do without executing.

## Release Pipeline

Execute these steps in order. Stop and report if any step fails.

### Step 1: Determine Version

```bash
# Detect version (check in priority order, use first match)
cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || \
cat package.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || \
git describe --tags --abbrev=0 2>/dev/null || echo "unknown"
```

Analyze commits since last release to suggest: **patch** (`fix:`/`chore:` only), **minor** (any `feat:`), **major** (breaking changes or user-specified). Ask user to confirm before proceeding.

**Autonomous mode:** Skips confirmation. Uses auto-detected version and shows the decision in output.

### Step 2: Pre-Flight Checks

Run two complementary validations. **Both must pass** before proceeding.

#### 2a: Full CI Mirror (`/craft:check --for release`)

```bash
/craft:check --for release
```

Runs: full pytest (unit + integration + e2e), strict lint, security audit, docs validation, 90% coverage threshold.

#### 2b: Release Metadata (`pre-release-check.sh`)

```bash
./scripts/pre-release-check.sh <version>   # Craft plugin projects
# General projects — skip (covered by 2a)
```

Checks: version consistency across files, command/skill/agent count accuracy, CLAUDE.md and README version refs, clean working tree.

#### 2c: Marketplace Validation (if applicable)

If `.claude-plugin/marketplace.json` exists, validate with `claude plugin validate .` and verify version parity with `plugin.json`. Skip if `marketplace.json` doesn't exist.

#### If Pre-Flight Fails

Fix issues and re-run from 2a. Common fixes: test failure → fix code; version mismatch → update `plugin.json`/`package.json`; uncommitted changes → commit or stash.

### Step 3: Version Bump

For **Craft plugin projects**:

```bash
./scripts/bump-version.sh <version> --dry-run  # preview
./scripts/bump-version.sh <version>             # apply (13 files)
./scripts/bump-version.sh --verify             # confirm
```

For **other project types**, update manually: Python (`pyproject.toml`, `__init__.py`, `README.md`), Node (`package.json`, `package-lock.json`, `README.md`), R package (`DESCRIPTION`, `NEWS.md`, `README.md`).

### Step 3b: Semantic Doc Updates

After `bump-version.sh` handles mechanical version substitution, update these files with **release-specific content** (title, summary, changelog entry):

| File | What to Update |
|------|---------------|
| `CHANGELOG.md` | Insert new version entry with summary from commit analysis |
| `VERSION-HISTORY.md` | Insert new version section with highlights |
| `README.md` | Update release title line (if present) |
| `docs/index.md` | Update `!!! info` box title and description text |
| `docs/REFCARD.md` | Update summary line ~11 title text (after the version) |
| `mkdocs.yml` | Update `site_description` tagline after "adds" |
| `commands/hub.md` | Update version in banner template, test count, skill count |
| `docs/commands/hub.md` | Same updates as `commands/hub.md` (published copy) |

**Verification:**

```bash
./scripts/bump-version.sh --verify
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

```bash
gh pr create --base main --head dev \
  --title "Release: v<version> — <title>" \
  --body "<release-notes>"
```

**Critical rules for PR body:** Avoid literal destructive git commands (branch guard hooks scan PR creation commands). Use descriptive language instead. Include a test plan checklist with results.

### Step 6: Monitor CI on PR (MANDATORY)

**Do NOT skip this step.** Poll CI before merging:

```bash
for i in $(seq 1 10); do
    STATUS=$(gh run list --branch dev --limit 1 --json status,conclusion --jq '.[0].status + " " + (.[0].conclusion // "pending")')
    echo "[Poll $i] $STATUS"
    if [[ "$STATUS" == "completed success" ]]; then
        echo "✅ CI passed — proceeding to merge"
        break
    elif [[ "$STATUS" == "completed failure" ]]; then
        echo "❌ CI failed — diagnose before merging"
        gh run view $(gh run list --branch dev --limit 1 --json databaseId --jq '.[0].databaseId') --log-failed 2>&1 | tail -20
        break
    fi
    sleep 30
done
```

If CI fails: fix on dev, push, wait for new run to pass. Only use `--admin` as last resort after user confirmation.

### Step 7: Merge Release PR

```bash
gh pr merge <number> --merge
```

**NEVER use `--delete-branch`** — the head branch is `dev`, which must not be deleted.

If branch protection blocks the merge, use `--admin` only after user confirmation.

**Autonomous mode:** Auto-uses `--admin` if blocked. Logs a **WARNING** for audit trail.

### Step 6.5: CI Monitoring (NEW in v2.22.0)

After creating the PR (Step 5) but before merging (Step 7), use the enhanced CI monitoring script for auto-fix capabilities:

```bash
bash scripts/ci-monitor.sh <pr-number>
```

Polls every 30s, auto-fixes `version_mismatch`/`lint_failure`/`changelog_format` failures, asks before fixing `test_failure`/`security_audit`/`build_failure`. Max 3 retry cycles.

Full configuration options, output format, and autonomous-mode behavior: **`references/ci-monitoring.md`**

### Step 8: Create GitHub Release

```bash
git pull origin main

gh release create v<version> --target main \
  --title "v<version> — <title>" \
  --notes "<release-notes>"
```

Generate release notes from `git log <last-tag>..HEAD --oneline`. Include: highlights section, changes by type, test count, link to full changelog comparison.

### Step 9: Post-Release (if applicable)

If the project has a docs site (`mkdocs.yml`, `_quarto.yml`, or `docs/`):

```bash
mkdocs gh-deploy  # or /craft:site:deploy
```

### Step 10: Update Homebrew Tap (if applicable)

If the project has a Homebrew formula or cask in `data-wise/tap`, update it with the new version.

Detect distribution type (formula vs cask) from `.craft/homebrew.json`, `src-tauri/tauri.conf.json`, or git remote — full detection script: **`references/homebrew.md`**

#### Step 10a: Update Formula (existing behavior)

Update SHA256 + version in `.rb` file, syntax-check with `ruby -c`, commit, push tap. Skip if no local tap (CI workflow handles it).

Full tap update script and formula name lookup chain: **`references/homebrew.md`**

#### Step 10b: Desktop App Cask Release (Tauri)

8-substep pipeline: build multi-arch DMGs → verify architectures → compute SHA256 from local artifacts → upload to GitHub release → update cask file → push tap with conflict resolution.

Full implementation for all 8 substeps and conflict resolution strategy: **`references/homebrew.md`**

**Skip to Step 11 after Step 10b completes.**

### Step 11: Sync Dev with Main

```bash
git checkout dev && git pull origin main
git push  # sync origin/dev
```

### Step 12: Verify CI on Main (MANDATORY)

After merge, verify CI passes on main. This catches issues like missing CI dependencies.

```bash
sleep 10
gh run list --branch main --limit 1 --json status,conclusion,databaseId \
  --jq '.[0] | .status + " " + (.conclusion // "pending") + " (run " + (.databaseId|tostring) + ")"'
gh run view <run-id> --log-failed 2>&1 | tail -30  # if failed
```

**If CI fails on main:** This is critical — fix immediately on dev, then merge to main (patch release if needed).

### Step 13: Verify Downstream Workflows (MANDATORY)

After CI passes on main, verify all downstream workflows and artifacts:

- **13a** — docs deploy workflow (`docs.yml`) succeeded
- **13b** — homebrew-release workflow succeeded
- **13c** — live site shows new version
- **13d** — formula in tap has correct version + SHA256
- **13e** — CI badge shows "passing"
- **13f** — cask version + SHA256 match (Tauri projects only)

Full verification commands for each check: **`references/downstream-verification.md`**

### Step 13.4: Doc Coverage Gate (MANDATORY)

```bash
bash scripts/doc-coverage-check.sh
```

**Blocking:** Missing REFCARD rows or mkdocs nav entries → fix before continuing.
**Warning:** Missing tutorials → add before next release, does not block.

Full fix procedure: **`references/downstream-verification.md`**

### Step 13.5: Post-Release Sweep (RECOMMENDED)

```bash
./scripts/post-release-sweep.sh --fix
git add -u && git commit -m "chore: fix post-release drift detected by sweep" && git push
```

Catches Tier 2+ drift: secondary version refs, stale counts, content staleness that `bump-version.sh` misses. Tier table and dry-run option: **`references/downstream-verification.md`**

### Step 13.6: Verify Surfaces (multi-surface version assert)

Auto-runs when `.claude-plugin/plugin.json` is present. Asserts one version across: `marketplace.json`, git tag, tap formula, brew-installed, Code-registered, aggregator. Desktop/Cowork → WARN only.

Bypass with `--skip-surfaces` for non-plugin releases. Full script and surface table: **`references/downstream-verification.md`**

### Step 13.7: Prune Version Cache (maintenance)

```bash
./scripts/cache-prune.sh            # dry-run
./scripts/cache-prune.sh --prune    # remove old version dirs
```

Keeps current + 2 most recent per plugin. Never blocks release (exit 0 always). Full docs: **`references/downstream-verification.md`**

## Output Format

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

### Step 10b Error Recovery (Desktop App)

Full error-to-substep recovery table (missing Rust target, build failures, SHA256 validation, gh release upload, cask syntax, tap push conflicts): **`references/homebrew.md`**

## Additional Resources

### Reference Files

- **`references/release-checklist.md`** — Detailed per-project-type checklists and edge cases
- **`references/homebrew.md`** — Full Step 10 implementation: distribution detection, 10a formula script, 10b Tauri cask pipeline (8 substeps), error table, dry-run format
- **`references/ci-monitoring.md`** — Step 6.5 CI monitoring: config, auto-fix categories, output format
- **`references/downstream-verification.md`** — Steps 13–13.7: all verification commands, doc coverage gate, post-release sweep, surface assertion, version cache pruning
- **`references/autonomous-mode.md`** — Autonomous mode: version detection code, admin override details, abort report format
