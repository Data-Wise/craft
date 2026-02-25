# ORCHESTRATE: Release Pipeline Hardening v2 (Trimmed)

**Branch:** `feature/release-hardening-v2`
**Base:** `dev`
**Spec:** `docs/specs/SPEC-release-hardening-v2-2026-02-23.md`
**Created:** 2026-02-23
**Revised:** 2026-02-24 (trimmed from 6 to 2 increments)

---

## Scope Change

Original plan had 6 increments (~540 lines). Trimmed to 2 increments (~350 lines) covering the core value: automated post-release drift detection.

**Kept:**

- Increment 1: `post-release-sweep.sh` (solves a real recurring problem)
- Increment 2: Step 13.5 in release pipeline (trivial wiring)

**Dropped:**

- ORCHESTRATE branch guard (rare problem, already covered by CLAUDE.md rules)
- `/craft:git:clean` auto-remove upgrade (minor behavioral change)
- `/craft:docs:sync` version drift (overlaps with sweep script)
- Standalone docs increment (folded into Increment 2)

---

## Increment 1: Post-Release Sweep Script (2-3 hours)

**Goal:** Create `scripts/post-release-sweep.sh` with Tier 1+2+3 drift detection and auto-fix.

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

```text
feat: add post-release sweep script for Tier 2+ drift detection

Catches secondary version references, stale dates/counts, and content
staleness that bump-version.sh doesn't cover. Supports --fix for
auto-correction and --dry-run (default) for safe reporting.
```

---

## Increment 2: Release Pipeline Step 13.5 + Docs (1-2 hours)

**Goal:** Wire sweep into release pipeline and update documentation.

### Steps

1. **Edit `skills/release/SKILL.md`**
   - Add Step 13.5 after Step 13 (downstream verification)
   - Normal mode: run `post-release-sweep.sh --fix`, commit if fixes applied
   - Autonomous mode: same behavior (auto-fix is safe)
   - Dry-run mode: run `post-release-sweep.sh` (report only)
   - Update dry-run preview table

2. **Update `docs/reference/REFCARD-RELEASE.md`**
   - Add Step 13.5 to pipeline reference

3. **Update `CLAUDE.md`**
   - Add `post-release-sweep.sh` to quick commands table
   - Update test count

4. **Update `CHANGELOG.md`**
   - Add [Unreleased] entry

5. **Run full test suite**

   ```bash
   python3 tests/test_craft_plugin.py
   python3 -m pytest tests/test_plugin_e2e.py -v
   python3 -m pytest tests/test_plugin_dogfood.py -v
   bash tests/test_post_release_sweep.sh
   ./scripts/validate-counts.sh
   ./scripts/post-release-sweep.sh  # eat our own dogfood
   ```

### Commit

```text
feat: add Step 13.5 post-release sweep to release pipeline
```

---

## PR Checklist

- [ ] All increments committed with conventional commit messages
- [ ] Full test suite passes
- [ ] `./scripts/validate-counts.sh` passes
- [ ] `./scripts/post-release-sweep.sh` passes (dogfood!)
- [ ] No ORCHESTRATE files in final branch state
- [ ] CHANGELOG updated
- [ ] PR created: `gh pr create --base dev`
