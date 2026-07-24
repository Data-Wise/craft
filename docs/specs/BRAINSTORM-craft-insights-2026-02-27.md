# BRAINSTORM: Craft Insights-Driven Improvements

**Date:** 2026-02-27
**Source:** Insights analysis (327 sessions, 6 weeks)
**Scope:** Brainstorm only — no specs committed yet
**Craft Version:** v2.31.0

---

## Priority Ranking

| # | Feature | Project | Impact | Effort | Priority |
|---|---------|---------|--------|--------|----------|
| 1 | Version Sync Drift Prevention (3 layers) | Craft | High — #1 CI failure cause | ~1.5h total | **P1** |
| 2 | Worktree Pre-flight Validation | Craft | High — prevents 40+ git friction events | ~2h | **P1** |
| 3 | Release Pipeline Enhancements | Craft | Medium — already 13-step, incremental gains | ~3h | **P2** |
| 4 | Headless Doc Sync Automation | Craft | Medium — saves ~45 doc update sessions | ~2h | **P3** |
| 5 | Parallel Doc Agent Orchestration | Both | Low — experimental, Scholar/Craft share pattern | ~4h | **P4** |

---

## 1. Version Sync Drift Prevention

**Problem:** 48 wrong_approach events + multiple CI failures from version strings drifting out of sync across 13+ files per project.

**Solution:** Three-layer defense-in-depth.

### Layer 1: Pre-commit Hook (Prevention)

```bash
# .claude/hooks/pre-commit-version-check.sh
# Triggers on commits touching version-bearing files
# Greps for OLD version string in all known locations
# Warns + aborts if drift detected
```

**Trigger files:** `package.json`, `plugin.json`, `mkdocs.yml`, `CLAUDE.md`, `README.md`
**Action:** Extract version from `package.json`, grep all 13 sync files, abort if any mismatch
**Effort:** ~15 min
**Limitation:** Bypassed with `--no-verify`, doesn't help CI-only workflows

### Layer 2: CI Check (Enforcement)

```yaml
# .github/workflows/ci.yml addition
- name: Version consistency check
  run: ./scripts/pre-release-check.sh --verify-only
```

**Already partially exists:** Scholar CI validates `package.json` vs `plugin.json` vs `mkdocs.yml`. Craft has `pre-release-check.sh` with 9 checks.
**Gap:** Neither checks ALL 13 files on every PR — only during release pre-flight.
**Fix:** Extract version check from release pre-flight into standalone CI step.
**Effort:** ~30 min

### Layer 3: Slash Command (Repair)

```bash
/craft:code:version-sync
# Scans all known version locations
# Shows diff of current vs expected
# Offers --fix to auto-update all files
# Handles both Craft (bump-version.sh) and Scholar (version-sync.js) patterns
```

**Cross-repo:** Detects project type (Craft vs Scholar vs generic) and uses appropriate sync tool.
**Effort:** ~30 min

### Dependencies

- Layer 1 depends on hook infrastructure (already exists in both projects)
- Layer 2 depends on CI workflow access
- Layer 3 is independent

---

## 2. Worktree Pre-flight Validation

**Problem:** Worktrees created without committed specs, APFS case-sensitivity collisions, Bash CWD invalidation after deletion, branch naming conflicts.

**Solution:** Pre-flight validation before `git worktree add`.

### Validation Checks

| Check | What | Why |
|-------|------|-----|
| Spec committed | Verify ORCHESTRATE/SPEC files are committed to feature branch | Prevents orphaned planning artifacts |
| No naming collision | Case-insensitive branch name comparison (APFS) | Prevents `Feature/Auth` vs `feature/auth` collisions |
| Target dir clean | Verify `~/.git-worktrees/<project>/<name>` doesn't exist | Prevents clobbering existing worktree |
| Source branch valid | Confirm creating from `dev` (not `main` or stale branch) | Enforces branch architecture |
| No overlapping edits | Compare ORCHESTRATE files across active worktrees for file overlap | Prevents merge conflicts |

### Integration with `/craft:git:worktree`

Craft's worktree command already has a `validate` action. Extend it:

```bash
# Current
/craft:git:worktree validate   # Verify CWD matches expected worktree

# Extended
/craft:git:worktree create feature/my-feature
  → Pre-flight: 5 checks above
  → If all pass: proceed with create
  → If any fail: show specific error + suggested fix
```

### Scope

- **In scope:** Pre-flight validation only (checks before create)
- **Out of scope:** Conflict detection during development, progress tracking, graceful teardown (future spec)

### Effort

~2 hours (5 check functions + integration with existing `create` action)

---

## 3. Release Pipeline Enhancements

**Problem:** Craft already has a mature 13-step pipeline. Insights suggest incremental improvements around CI failure diagnosis and Homebrew automation.

### 3a. CI Failure Auto-Diagnosis

**Current:** Step 6.5 monitors CI and auto-fixes "safe" categories (lint, version mismatch, changelog). Asks before fixing test/security failures.

**Enhancement:** Add pattern matching for known failure modes from insights:

| Failure Pattern | Auto-Fix | Category |
|-----------------|----------|----------|
| `--experimental-vm-modules` missing | Add to test runner config | Safe |
| CHANGELOG MD053 lint | Fix link refs at bottom | Safe |
| Version constant drift | Run bump-version.sh | Safe |
| Branch protection block | Switch to `--admin` | Ask first |
| Homebrew formula SHA mismatch | Recalculate + update | Safe |
| Test count mismatch | Update mkdocs.yml count | Safe |

**Effort:** ~1.5h (pattern dictionary + match logic)

### 3b. Homebrew SHA Auto-Update

**Current:** Formula URL updated, but SHA256 requires manual calculation + edit.

**Enhancement:** After GitHub release, auto-download tarball → compute SHA256 → update formula → `ruby -c` syntax check → commit + push.

**Effort:** ~1h (script extension to existing Homebrew step)

### 3c. Post-Release Sweep --fix Mode

**Current:** Detects Tier 2 stale references. Reports only.

**Enhancement:** Add `--fix` flag that auto-updates detected stale refs (with diff preview before applying).

**Effort:** ~30 min

---

## 4. Headless Doc Sync Automation

**Problem:** 45 documentation_update sessions in 6 weeks, many are predictable post-merge sync operations.

**Solution:** Headless Claude Code script for post-merge doc syncs.

### Trigger

```bash
# Post-merge hook or CI step
claude -p "Sync all documentation to match current version and command counts. \
  Run markdownlint on changed docs. Commit with 'docs: sync references to vX.Y.Z'" \
  --allowedTools "Read,Edit,Write,Bash,Grep,Glob"
```

### What It Syncs

| Target | Source | Tool |
|--------|--------|------|
| Version refs in ~30 doc files | `package.json` | `version-sync.js` |
| Command counts | `find commands/` | `validate-counts.sh` |
| Test counts | `npm test -- --json` | Parse test runner output |
| CHANGELOG | Git log since last tag | Auto-format |
| mkdocs.yml nav | File listing | `nav-update` command |

### Limitations

- Can't update semantic content (release highlights, tutorials)
- Requires Claude Code headless mode (available but not widely used)
- Needs careful `--allowedTools` scoping to prevent unintended changes

### Effort

~2h (script + testing + CI integration)

---

## 5. Parallel Doc Agent Orchestration

**Problem:** Bulk doc updates touch 15-26+ files sequentially, causing fatigue-related lint errors.

**Solution:** Spawn parallel agents by doc category.

### Agent Partition

| Agent | Files | Category |
|-------|-------|----------|
| Agent 1 | `docs/tutorials/**/*.md` | Tutorials |
| Agent 2 | `docs/reference/**/*.md` | Reference docs |
| Agent 3 | `README.md`, `CHANGELOG.md`, `mkdocs.yml` | Root + config |
| Agent 4 | `docs/commands/**/*.md` | Command docs |

### Reconciliation

After all agents complete:

1. Run `markdownlint docs/` on combined changes
2. Run `markdown-link-check` for cross-reference integrity
3. Commit all changes together

### Risks

- **Merge conflicts:** Two agents editing overlapping files (mitigated by strict partition)
- **Inconsistency:** Agents may use different phrasing for same version/count
- **Complexity:** Orchestration overhead may exceed sequential time for small updates

### Effort

~4h (agent prompts + partition logic + reconciliation)

---

## Dependencies Between Ideas

```
[1. Version Sync] ──→ [3. Release Pipeline] (sync is a release pre-req)
         │
         └──→ [4. Headless Doc Sync] (sync is one of the doc tasks)

[2. Worktree Pre-flight] ──→ independent (no deps)

[5. Parallel Doc Agents] ──→ [4. Headless Doc Sync] (agents could be headless)
```

---

## Recommended Sequence

1. **Version Sync Drift Prevention (P1)** — Immediate ROI, prevents #1 CI failure cause. Start with Layer 3 (command), then Layer 2 (CI), then Layer 1 (hook).

2. **Worktree Pre-flight Validation (P1)** — Independent of #1, can be done in parallel. Prevents recurring git friction.

3. **Release Pipeline Enhancements (P2)** — After #1, leverage version sync in the pipeline. CI failure patterns are incremental improvements.

4. **Headless Doc Sync (P3)** — After #1 is stable, automate the predictable doc sync workflows.

5. **Parallel Doc Agents (P4)** — Experimental. Try after #4 proves headless doc sync works. May not be worth the complexity.

---

## Craft Versions

| Feature | Target Version | Depends On |
|---------|---------------|------------|
| Version sync command | v2.32.0 | Nothing |
| Worktree pre-flight | v2.32.0 | Nothing |
| CI failure patterns | v2.33.0 | Version sync |
| Homebrew SHA auto-update | v2.33.0 | Nothing |
| Headless doc sync | v2.34.0 | Version sync |
| Parallel doc agents | v2.35.0+ | Headless doc sync |

---

## Not Included (Out of Scope)

- **Self-healing release pipelines** — Too ambitious for initial spec. Requires autonomous retry loops, rollback logic, and failure classification. Defer to future brainstorm.
- **Friction-aware test generation for Craft** — Craft's test suite (112 tests) is smaller than Scholar's (3,092). The dogfood pipeline is Scholar-specific for now.
- **Custom /release skill** — Craft already has a comprehensive `/release` skill (47 KB spec). Improvements should extend the existing skill, not create a new one.
