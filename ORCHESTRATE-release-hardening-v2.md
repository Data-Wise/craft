# ORCHESTRATE: Release Pipeline Hardening v2

**Branch:** `feature/release-hardening-v2`
**Base:** `dev`
**Spec:** `docs/specs/SPEC-release-hardening-v2-2026-02-23.md`
**Created:** 2026-02-23

---

## Increment 1: Post-Release Sweep Script (Core)

**Goal:** Create `scripts/post-release-sweep.sh` with Tier 1+2 drift detection and auto-fix.

### Steps

1. **Create `scripts/post-release-sweep.sh`**
   - Source `scripts/formatting.sh` for terminal output
   - Parse args: `--fix`, `--dry-run` (default), `--version X.Y.Z`, `--json`
   - Read current version from `plugin.json` (same pattern as `bump-version.sh`)

2. **Phase 1: Tier 1 check**
   - Run `./scripts/bump-version.sh --verify`
   - Capture exit code — if 1, report Tier 1 drift

3. **Phase 2: Tier 2 version refs**
   - Define `TIER2_VERSION_FILES` array
   - For each file: grep for old version strings (`v$PREV_VERSION`, `$PREV_VERSION`)
   - If `--fix`: sed substitution (same patterns as bump-version.sh)
   - Report results with file:line format

4. **Phase 3: Tier 2 date/count refs**
   - Check test files for hardcoded dates older than release date
   - Check docs for stale count strings
   - If `--fix`: update counts (dates need manual review)

5. **Phase 4: Tier 3 content staleness**
   - Compare `docs/index.md` info box against CHANGELOG latest version
   - Compare `README.md` feature list against recent changes
   - Always report (never auto-fix — needs human judgment)

6. **Phase 5: Summary**
   - Count auto-fixable vs needs-review vs clean
   - Exit 0 (clean) or 1 (drift found)

7. **Make executable:** `chmod +x scripts/post-release-sweep.sh`

### Tests

- Create `tests/test_post_release_sweep.sh`
- Test: clean repo returns exit 0
- Test: stale version in .STATUS returns exit 1
- Test: `--fix` corrects mechanical items
- Test: `--dry-run` doesn't modify files
- Test: `--json` produces valid JSON

### Commit

```
feat: add post-release sweep script for Tier 2+ drift detection

Catches secondary version references, stale dates/counts, and content
staleness that bump-version.sh doesn't cover. Supports --fix for
auto-correction and --dry-run (default) for safe reporting.
```

---

## Increment 2: Branch Guard ORCHESTRATE Block

**Goal:** Hard-block ORCHESTRATE files from being committed on `dev`.

### Steps

1. **Edit `scripts/branch-guard.sh`**
   - Add new section (Section 9 or equivalent) after smart-mode checks
   - On `dev`/`develop` branch:
     - If `Write`/`Edit` tool targets `ORCHESTRATE-*.md`: hard block
     - If `Bash` tool contains `git add.*ORCHESTRATE`: hard block
   - Use `_box` helper for teaching message
   - No session counting — always block (not smart-mode behavior)

2. **Update tests**
   - `tests/test_branch_guard.sh`: Add test case for ORCHESTRATE block on dev
   - `tests/test_branch_guard.sh`: Add test case for ORCHESTRATE allowed on feature/*
   - `tests/test_branch_guard_dogfood.py`: Add dogfood test

### Commit

```
feat: block ORCHESTRATE files on dev branch via branch guard

ORCHESTRATE files are working artifacts that belong on feature branches.
Hard block prevents them from leaking to dev via accidental commits.
```

---

## Increment 3: `/craft:git:clean` Auto-Remove

**Goal:** Upgrade ORCHESTRATE file handling from warn to auto-remove.

### Steps

1. **Edit `commands/git/clean.md`**
   - In the cleanup flow section, change "warn" to "auto-remove"
   - Add `git rm ORCHESTRATE-*.md` + commit step
   - Keep the informational message about why they're being removed

2. **Harden `/craft:git:worktree finish` Step 2.5**
   - Edit `commands/git/worktree.md`
   - Ensure Step 2.5 doesn't silently fail if no ORCHESTRATE files found
   - Add explicit error handling for `git rm` failure

### Commit

```
feat: auto-remove ORCHESTRATE files in git clean and harden worktree finish
```

---

## Increment 4: Release Skill Step 13.5

**Goal:** Add post-release sweep as Step 13.5 in the release pipeline.

### Steps

1. **Edit `skills/release/SKILL.md`**
   - Add Step 13.5 after Step 13 (downstream verification)
   - In normal mode: run `post-release-sweep.sh --fix`, commit if fixes applied
   - In autonomous mode: same behavior (auto-fix is safe)
   - In dry-run mode: run `post-release-sweep.sh` (report only)
   - Update step numbering if needed
   - Update dry-run preview table

2. **Update docs**
   - `docs/reference/REFCARD-RELEASE.md`: Add Step 13.5 to pipeline reference

### Commit

```
feat: add Step 13.5 post-release sweep to release pipeline
```

---

## Increment 5: docs:sync Version Drift Integration

**Goal:** Make `/craft:docs:sync` detect version drift and flag stale index/README content.

### Steps

1. **Edit `commands/docs/sync.md`**
   - Add "Version Drift" as a new detection category
   - Detection logic:
     - Run `bump-version.sh --verify` quietly
     - Check Tier 2 files for old version strings
     - Check `docs/index.md` for stale feature highlights
     - Check `README.md` for stale content
   - Integrate into existing report format
   - When `--headless`: include drift items in auto-fix scope (mechanical only)

2. **Test docs:sync enhancement**
   - Create or extend `tests/test_integration_docs_sync.py` (if exists)
   - Test: clean repo reports no drift
   - Test: stale version triggers drift report
   - Test: stale index.md content flagged

### Commit

```
feat: integrate version drift detection into /craft:docs:sync

docs:sync now detects Tier 1+2 version drift and content staleness
in index.md and README.md alongside existing doc freshness checks.
```

---

## Increment 6: Documentation and Finalization

**Goal:** Update all documentation, CLAUDE.md, CHANGELOG, run full test suite.

### Steps

1. **Update docs**
   - `docs/guide/branch-guard-smart-mode.md`: Add ORCHESTRATE guard section
   - `docs/workflows/git-feature-workflow.md`: Note ORCHESTRATE auto-cleanup
   - `docs/commands/git/clean.md`: Update behavior description
   - `docs/commands/git/worktree.md`: Update finish step description

2. **Update CLAUDE.md**
   - Add `post-release-sweep.sh` to quick commands table
   - Update test count if new tests added

3. **Update CHANGELOG.md**
   - Add [Unreleased] entries for all changes

4. **Run full test suite**

   ```bash
   python3 tests/test_craft_plugin.py
   python3 -m pytest tests/test_plugin_e2e.py -v
   python3 -m pytest tests/test_plugin_dogfood.py -v
   bash tests/test_branch_guard.sh
   bash tests/test_post_release_sweep.sh
   ./scripts/validate-counts.sh
   ./scripts/post-release-sweep.sh  # eat our own dogfood
   ```

5. **Validate counts**
   - Run `./scripts/validate-counts.sh`
   - Ensure all counts are consistent

### Commit

```
docs: update documentation for release hardening v2

Covers branch guard ORCHESTRATE section, release pipeline Step 13.5,
sweep script reference, and updated workflow docs.
```

---

## PR Checklist

- [ ] All increments committed with conventional commit messages
- [ ] Full test suite passes (target: 109+ core tests)
- [ ] `./scripts/validate-counts.sh` passes
- [ ] `./scripts/bump-version.sh --verify` passes
- [ ] `./scripts/post-release-sweep.sh` passes (dogfood!)
- [ ] No ORCHESTRATE files in final branch state (will be removed pre-PR)
- [ ] CHANGELOG updated
- [ ] PR created: `gh pr create --base dev`

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Branch guard false positive | Low | Medium | Regex matches `ORCHESTRATE-*.md` specifically, not substrings |
| Sweep auto-fix corrupts file | Low | High | `--dry-run` default; `--fix` previews before writing |
| docs:sync performance regression | Low | Low | Version checks are fast (grep + bump --verify) |
| Step 13.5 fails during release | Low | Low | Non-blocking — release already published |
