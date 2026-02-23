# BRAINSTORM: Release Pipeline Hardening v2

**Mode:** Feature | **Depth:** Deep | **Duration:** ~8 min
**Date:** 2026-02-23

---

## Problem Statement

The release pipeline (Steps 1-13) handles **Tier 1** version references — the 13 files managed by `bump-version.sh`. But **Tier 2** secondary references silently drift between releases:

| Tier 2 Drift Item | Example | When Caught |
|-------------------|---------|-------------|
| `.STATUS` spec table entries | Stale milestone/session refs | Post-release site sync |
| `CLAUDE.md` duplicate install lines | Leftover from older eras | Manual review |
| Test summary dates/counts | Hardcoded "2026-02-21" in test output | Manual review |
| Docs guide example commands | `homebrew-automation.md` with old v2.26.0 | Post-release grep |
| `docs/index.md` content staleness | Feature highlights not updated | Site deploy check |
| `README.md` content staleness | Tagline/feature list outdated | Manual review |

Additionally:

- **ORCHESTRATE files** can leak to `dev` if user merges PR without using `/craft:git:worktree finish`
- **`/craft:docs:sync`** doesn't detect version drift or flag stale index/README content
- **Site/docs updates** don't touch `index.md` or `README.md` — neither detection nor content

---

## Quick Wins (< 30 min each)

1. **Add ORCHESTRATE guard to `branch-guard.sh`** — Hard block `ORCHESTRATE-*.md` files from being committed on `dev` branch. ~20 lines of bash in the existing guard.

2. **Add `--sweep` flag to `bump-version.sh --verify`** — Extend the existing verify mode to check Tier 2 files too. Report-only, no new script needed.

3. **Update `/craft:git:clean` to auto-remove ORCHESTRATE files** — It already warns about them; make it delete them in its cleanup pass.

---

## Medium Effort (1-2 hours)

4. **Create `scripts/post-release-sweep.sh`** — Standalone script that:
   - Runs `bump-version.sh --verify` (Tier 1 check)
   - Greps for old version strings in Tier 2 files
   - Checks `.STATUS` for stale session entries
   - Checks `CLAUDE.md` for duplicate/stale lines
   - Checks test files for hardcoded dates
   - Checks `docs/index.md` and `README.md` for stale feature descriptions
   - Auto-fixes what it can, reports what needs human judgment
   - Supports `--dry-run` (default) and `--fix` flags

5. **Add Step 13.5 to release skill** — After downstream verification, run `post-release-sweep.sh --fix`. Catches anything the pipeline missed.

6. **Integrate Tier 2 detection into `/craft:docs:sync`** — Add a "version drift" detector category alongside the existing "stale docs" detection. Make it flag `index.md` and `README.md` when content is outdated.

---

## Long-term (Future sessions)

7. **Shared detection library** — Extract common version-checking logic into a reusable module used by `bump-version.sh`, `pre-release-check.sh`, `post-release-sweep.sh`, and `/craft:docs:sync`.

8. **Automated Tier 3 (semantic) suggestions** — Use AI-assisted diff to suggest README tagline updates and VERSION-HISTORY entries based on changelog.

---

## Architecture

### Post-Release Sweep Script

```
scripts/post-release-sweep.sh
├── Phase 1: Run bump-version.sh --verify (Tier 1)
├── Phase 2: Tier 2 file scan
│   ├── .STATUS: version field, milestone, stale sessions
│   ├── CLAUDE.md: duplicate lines, stale install examples
│   ├── Test files: hardcoded dates, counts
│   └── Docs guides: example commands with old versions
├── Phase 3: Content staleness check
│   ├── docs/index.md: feature highlights vs CHANGELOG
│   ├── README.md: tagline, feature list
│   └── mkdocs.yml: description
└── Phase 4: Auto-fix (if --fix) or report
```

### Branch Guard ORCHESTRATE Block

```
branch-guard.sh (existing)
├── Section 9 (or new section): ORCHESTRATE file check
│   ├── On dev branch: check if any staged/written file matches ORCHESTRATE-*.md
│   ├── Hard block with teaching message
│   └── Suggest: use /craft:git:worktree finish
└── Tests: test_branch_guard.sh + test_branch_guard_dogfood.py
```

### docs:sync Enhancement

```
/craft:docs:sync (existing)
├── Current: stale docs detection (content drift)
├── NEW: version drift detection
│   ├── Check Tier 1 via bump-version.sh --verify
│   ├── Check Tier 2 via shared patterns
│   └── Check content staleness (index.md, README.md)
└── Report: unified staleness report
```

---

## Recommended Path

**All in one feature branch** (`feature/release-hardening-v2`):

1. `scripts/post-release-sweep.sh` — the new script (Phase 2-4 logic)
2. `branch-guard.sh` — add ORCHESTRATE block on dev
3. `commands/git/clean.md` — upgrade from warn to auto-remove
4. `skills/release/SKILL.md` — add Step 13.5
5. `commands/docs/sync.md` — integrate Tier 2 drift detection
6. Tests for all of the above
7. Documentation updates

---

## Files Affected

| File | Change |
|------|--------|
| `scripts/post-release-sweep.sh` | **NEW** — Tier 2 sweep + auto-fix |
| `scripts/branch-guard.sh` | Add ORCHESTRATE hard block on dev |
| `commands/git/clean.md` | Upgrade ORCHESTRATE warn → auto-remove |
| `commands/git/worktree.md` | Harden finish Step 2.5 |
| `skills/release/SKILL.md` | Add Step 13.5 |
| `commands/docs/sync.md` | Add version drift detection |
| `tests/test_branch_guard.sh` | Add ORCHESTRATE block tests |
| `tests/test_branch_guard_dogfood.py` | Add ORCHESTRATE dogfood test |
| `tests/test_post_release_sweep.sh` | **NEW** — sweep script tests |
| `CLAUDE.md` | Update test count, add sweep to quick commands |
| `.STATUS` | Update with new session |
| `docs/guide/branch-guard-smart-mode.md` | Document ORCHESTRATE guard |
| `docs/reference/REFCARD-RELEASE.md` | Add Step 13.5 to pipeline |

---

## Acceptance Criteria

- [ ] `post-release-sweep.sh` detects all Tier 1+2 drift items
- [ ] `post-release-sweep.sh --fix` auto-fixes mechanical items
- [ ] `post-release-sweep.sh --dry-run` (default) reports without modifying
- [ ] Branch guard blocks `ORCHESTRATE-*.md` commits on `dev`
- [ ] `/craft:git:clean` auto-removes ORCHESTRATE files post-merge
- [ ] `/craft:git:worktree finish` Step 2.5 is hardened (no silent failures)
- [ ] Release skill Step 13.5 invokes sweep after downstream verification
- [ ] `/craft:docs:sync` detects version drift + content staleness in index/README
- [ ] All existing tests pass
- [ ] New tests cover sweep script, guard rule, and docs:sync enhancement
- [ ] Documentation updated for all changes

---

## Open Questions

1. Should the sweep script maintain its own list of Tier 2 files, or discover them dynamically via grep?
2. Should Step 13.5 auto-commit fixes, or leave them staged for review?
3. How should docs:sync handle the boundary between "version drift" (mechanical) and "content staleness" (requires judgment)?
