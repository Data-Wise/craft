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
│  1. ✓ Run pre-release-check.sh v2.18.0                      │
│  2. ✓ Bump version in plugin.json, CLAUDE.md                │
│  3. ✓ Commit: "chore: bump version to v2.18.0 for release"  │
│  4. ✓ Push to dev                                           │
│  5. ✓ Create PR: dev → main                                 │
│  6. ✓ Merge PR (--merge, NO --delete-branch)                │
│  7. ✓ Create GitHub release v2.18.0 on main                 │
│  8. ✓ Deploy docs site (mkdocs gh-deploy)                   │
│  9. ✓ Sync dev with main                                    │
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

### Step 2: Pre-Flight Checks

Run the project's pre-release validation:

```bash
# Craft plugin projects
./scripts/pre-release-check.sh <version>

# General projects — run test suite
python3 -m pytest tests/ || python3 tests/test_*.py || npm test || R CMD check .
```

If pre-flight fails, fix the issues and re-run. Common fixes:

- Version mismatch: update plugin.json/package.json
- CLAUDE.md version refs: update version string
- Uncommitted changes: commit or stash

### Step 3: Version Bump

Update version in all relevant files. Project-type-specific:

| Project Type | Files to Update |
|-------------|-----------------|
| Craft plugin | `.claude-plugin/plugin.json`, `CLAUDE.md` |
| Python | `pyproject.toml`, `__init__.py` |
| Node | `package.json`, `package-lock.json` |
| R package | `DESCRIPTION`, `NEWS.md` |

Also update any hardcoded version references, test counts, and date strings in CLAUDE.md.

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

### Step 6: Merge Release PR

```bash
gh pr merge <number> --merge
```

**NEVER use `--delete-branch`** — the head branch is `dev`, which must not be deleted.

If branch protection blocks the merge, use `--admin` only after user confirmation.

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

Sync dev with main:

```bash
git checkout dev && git pull origin main
```

## Output Format

Display progress using box-drawing:

```
┌─────────────────────────────────────────────────────────────┐
│ /release v2.17.0                                            │
├─────────────────────────────────────────────────────────────┤
│ [1/8] Pre-flight checks ..................... PASSED         │
│ [2/8] Version bump ......................... DONE            │
│ [3/8] Commit & push ....................... DONE             │
│ [4/8] Release PR created .................. PR #70           │
│ [5/8] PR merged ........................... DONE             │
│ [6/8] GitHub release ....................... v2.17.0          │
│ [7/8] Docs deployed ....................... DONE              │
│ [8/8] Dev synced .......................... DONE              │
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
