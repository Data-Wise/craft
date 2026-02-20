# SPEC: Extend bump-version.sh & Release Skill for Full Doc Coverage

**Status:** draft
**Created:** 2026-02-19
**From Brainstorm:** Inline session analysis during v2.22.2 release
**Scope:** `scripts/bump-version.sh`, release skill (Step 3b)

---

## Overview

During the v2.22.2 release, bump-version.sh handled 9 of 13 files that needed version updates. The remaining 4 files required manual intervention — 2 are mechanical substitutions that belong in the script, and 2 need semantic content (release titles, changelogs) that belongs in the release skill as a new Step 3b.

## Primary User Story

**As a** craft plugin maintainer running a release,
**I want** bump-version.sh and the release skill to cover ALL version references automatically,
**So that** no files are missed and manual version-chasing is eliminated.

### Acceptance Criteria

- [ ] bump-version.sh updates 13 files (up from 9)
- [ ] `--verify` mode detects drift in all 13 files
- [ ] Release skill Step 3b generates CHANGELOG entry with release title
- [ ] Release skill Step 3b generates VERSION-HISTORY section with release title
- [ ] Zero manual version edits needed during a release

## Secondary User Stories

**As a** developer running `bump-version.sh` standalone (outside a release),
**I want** all mechanical version refs updated consistently,
**So that** docs don't drift when I bump versions for testing or hotfixes.

---

## Changes

### Part 1: bump-version.sh — Add 4 Mechanical Files

Add to the "Text files" section of the script:

| File | Pattern | Replacement |
|------|---------|-------------|
| `docs/DEPENDENCY-ARCHITECTURE.md` | `**Version**: X.Y.Z` (footer) | Update version number |
| `docs/reference/configuration.md` | `bump-version.sh X.Y.Z` (example) | Update version in example |
| `docs/REFCARD.md` line ~7 | `Version: X.Y.Z (released YYYY-MM-DD)` | Update version + date |
| `docs/REFCARD.md` line ~11 | `vX.Y.Z: <summary>` | Update version only (leave summary — release skill handles it) |

#### Verify Mode

Add these 4 files to `--verify` checks:

```bash
# docs/DEPENDENCY-ARCHITECTURE.md
if [ -f "docs/DEPENDENCY-ARCHITECTURE.md" ] && grep -q '^\*\*Version\*\*:' docs/DEPENDENCY-ARCHITECTURE.md; then
    FILE_VER=$(grep '^\*\*Version\*\*:' docs/DEPENDENCY-ARCHITECTURE.md | grep -o '[0-9]*\.[0-9]*\.[0-9]*')
    # compare to CURRENT_VERSION
fi

# docs/reference/configuration.md
if [ -f "docs/reference/configuration.md" ] && grep -q 'bump-version.sh [0-9]' docs/reference/configuration.md; then
    FILE_VER=$(grep 'bump-version.sh [0-9]' docs/reference/configuration.md | grep -o '[0-9]*\.[0-9]*\.[0-9]*')
    # compare to CURRENT_VERSION
fi
```

### Part 2: Release Skill — Add Step 3b (Semantic Doc Updates)

After Step 3 (version bump via bump-version.sh), add Step 3b that uses the **release title** (available from Step 1) to:

#### CHANGELOG.md

Insert a new section at the top of the release timeline:

```markdown
## [X.Y.Z] - YYYY-MM-DD: <release-title>

### Added
- <generated from feat: commits>

### Fixed
- <generated from fix: commits>

### Changed
- <generated from refactor:/chore:/docs: commits>
```

Commit analysis approach:

```bash
git log <last-tag>..HEAD --oneline --no-merges | while read hash msg; do
    type=$(echo "$msg" | grep -o '^[a-z]*:' | tr -d ':')
    case "$type" in
        feat) echo "Added: ${msg#*: }" ;;
        fix)  echo "Fixed: ${msg#*: }" ;;
        *)    echo "Changed: ${msg#*: }" ;;
    esac
done
```

#### VERSION-HISTORY.md

Insert a new section after `## Release Timeline`:

```markdown
### vX.Y.Z (YYYY-MM-DD) - <release-title>

**Status:** Released

**Highlights:**
- <top 3 items from commit analysis>
```

#### README.md Release Title

Update the release title line:

```markdown
> **vX.Y.Z - <release-title>** 🚀
```

#### docs/index.md Info Box

Update the latest info box:

```markdown
!!! info "Latest: vX.Y.Z — <release-title>"
```

#### docs/REFCARD.md Summary Line

Update the summary line (~line 11):

```markdown
│  vX.Y.Z: <abbreviated-release-title>                        │
```

### Part 3: Update File Count Documentation

Update the release skill, bump-version.sh header comments, and docs/reference/configuration.md to reflect the new file count (13 instead of 9).

---

## Dependencies

- `scripts/bump-version.sh` (existing)
- `scripts/bump-version-helper.py` (existing, for JSON files)
- Release skill (`skills/release/SKILL.md`)

## Data Models

N/A — No data model changes.

## API Design

N/A — No API changes. CLI interface unchanged except bump-version.sh handles more files.

## UI/UX Specifications

N/A — CLI only. Output format matches existing bump-version.sh style.

## Open Questions

1. **REFCARD summary line** — Should bump-version.sh clear the summary text (leaving just the version), or leave it stale? Current recommendation: update version only, let release skill set the summary text.
2. **VERSION-HISTORY "Total Releases" count** — Should this be auto-incremented? Currently manual (44 → 45 was done by hand).
3. **Date in REFCARD box** — Should bump-version.sh set the date to today, or should only the release skill set dates?

## Review Checklist

- [ ] All 13 files covered by bump-version.sh or release skill
- [ ] `--verify` catches drift in all files
- [ ] `--dry-run` previews all 13 files
- [ ] Release skill Step 3b generates correct CHANGELOG format
- [ ] Release skill Step 3b generates correct VERSION-HISTORY format
- [ ] No duplicate logic between script and skill
- [ ] Backward compatible (old bump-version.sh invocations still work)

## Implementation Notes

- Keep bump-version.sh as pure mechanical substitution — no release context needed
- Release skill has the release title from Step 1, making it the right place for semantic content
- The commit-analysis approach for CHANGELOG should handle merge commits gracefully (skip them)
- Consider making Step 3b idempotent — running it twice shouldn't create duplicate entries

## History

| Date | Change |
|------|--------|
| 2026-02-19 | Initial spec from v2.22.2 release gap analysis |
