# Brainstorm: Docs Staleness Detection System

**Date:** 2026-02-25
**Context:** During post-merge docs health checks, we repeatedly find the same categories of drift: stale counts, missing nav entries, broken cross-references, and undocumented skills/commands. Currently this requires manual agent-driven exploration. The `/craft:docs:check` command and `post-release-sweep.sh` catch some issues but miss many.
**Goal:** Extend `/craft:docs:update` (or a new `/craft:docs:audit`) to systematically detect all categories of documentation staleness.

---

## Decisions (Resolved)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | **Option C: Hybrid** | Script backend + `/craft:docs:check --deep` frontend |
| Arch docs with old counts | **Flag as warning** | Not errors, but should be visible |
| CI enforcement | **Warn only** | Report in output, don't fail build |
| Scope | **Ship tight, iterate** | 8 discovered categories only |
| Increment 1 scope | **All 4 phases** | Nav + counts + skill coverage + cross-doc freshness |
| Count auto-fix | **Yes, with --fix flag** | sed-replace stale counts in non-historical files |
| Exclusion config location | **`scripts/config/exclusions.txt`** | Next to scripts that consume it |
| Exclusion config format | **Simple file:pattern pairs** | `filepath[:pattern]` with `#` comments |
| Interactive review UX | **Two-pass: auto then interactive** | Pass 1 auto-fixes safe items, Pass 2 presents uncertain items |
| Exclusion reasons | **Auto-generated** | `Excluded YYYY-MM-DD via interactive review` |
| Exclusion maintenance | **Audit subcommand** | `--audit-exclusions` prunes stale entries |
| Skill/agent auto-add | **Yes, with --fix** | Auto-append to correct category table using frontmatter description |
| site_description check | **Yes, in Phase 9** | Compare against latest CHANGELOG headline |
| Release pipeline step | **Step 2d (pre-release)** | Catch staleness before tagging, earlier feedback |

---

## Problem Categories Discovered This Session

| Category | Example | Current Detection | Gap |
|----------|---------|-------------------|-----|
| Missing mkdocs.yml nav entries | New files from PR not in nav | `mkdocs build --strict` warns (pages exist but not in nav) | Not checked by any craft command |
| Stale skill/agent counts | "17 skills, 7 agents" in docs | `validate-counts.sh` checks CLAUDE.md + plugin.json only | Doesn't scan all docs files |
| Undocumented skills | `code/sync-features` missing from skills docs | None | No automated cross-check |
| Undocumented commands | New subcommands not in overview | Hub cache vs docs comparison | Not automated |
| Broken links outside docs/ | `../../commands/dist/homebrew.md` in MkDocs | `mkdocs build --strict` catches | Not in `/craft:docs:check` |
| Stale version refs in secondary docs | Old version in guides/tutorials | `post-release-sweep.sh` (Tier 2) | Only runs post-release |
| Cross-reference accuracy | "See Also" sections with wrong counts | None | Manual review only |
| Architecture docs vs reality | HUB-V2-ARCHITECTURE says "97 commands" | None | Snapshot docs drift silently |

---

## Architecture: Option C (Hybrid)

Script does the detection, `/craft:docs:check` calls it as Phase 6+:

```text
/craft:docs:check          -> Phases 1-5 (existing) + Phase 6 (staleness summary)
/craft:docs:check --deep   -> Phases 1-5 + full staleness audit (Phases 6-9)
./scripts/docs-staleness-check.sh  -> Direct script access for CI/automation
```

### Script Interface

```bash
# Dry-run: two-pass report (auto-fixable items identified, uncertain items listed)
./scripts/docs-staleness-check.sh

# Auto-fix safe items, then interactive review for uncertain items
./scripts/docs-staleness-check.sh --fix

# Non-interactive auto-fix only (CI mode)
./scripts/docs-staleness-check.sh --fix --non-interactive

# JSON output for scripting
./scripts/docs-staleness-check.sh --json

# Audit exclusion list for stale entries
./scripts/docs-staleness-check.sh --audit-exclusions
```

### Output: Traffic Light Status

```text
./scripts/docs-staleness-check.sh

=== Docs Staleness Check ===
Version: 2.27.0 | Commands: 107 | Skills: 26 | Agents: 8

Phase 6: Nav Completeness ............ GREEN (0 issues)
Phase 7: Count Consistency ........... YELLOW (3 warnings)
Phase 8: Skill/Agent Coverage ........ GREEN (0 issues)
Phase 9: Cross-Doc Freshness ......... YELLOW (2 warnings)

Status: YELLOW (5 warnings, 0 errors)
```

---

## Detection Modules (Phases 6-9)

### Phase 6: Nav Completeness

**What it checks:**

- Every `.md` file in `docs/` (excluding paths in exclusions.txt) has an entry in `mkdocs.yml` nav
- Every entry in `mkdocs.yml` nav points to a file that exists on disk
- New files added since last release are flagged if not in nav

**Implementation:**

```bash
# Extract all files referenced in mkdocs.yml nav
grep -oE '[a-zA-Z0-9/_-]+\.md' mkdocs.yml | sort > /tmp/nav-files.txt

# Find all docs files (excluding known exclusions)
find docs -name "*.md" -not -path "docs/.archive/*" ... | sort > /tmp/disk-files.txt

# Diff
comm -23 /tmp/disk-files.txt /tmp/nav-files.txt  # Files on disk but not in nav
comm -13 /tmp/disk-files.txt /tmp/nav-files.txt  # Nav entries with no file
```

**Auto-fix:** No -- nav placement requires human judgment about section grouping.

### Phase 7: Count Consistency

**What it checks:**

- Grep all docs for patterns like `\d+ commands`, `\d+ skills`, `\d+ agents`, `\d+ tests`
- Compare against authoritative counts from `validate-counts.sh`
- Flag any mismatch (consulting exclusions.txt for known exceptions)

**Implementation:**

```bash
EXPECTED_CMDS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Commands:" | awk '{print $2}')
EXPECTED_SKILLS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Skills:" | awk '{print $2}')
EXPECTED_AGENTS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Agents:" | awk '{print $2}')

# Scan active docs, skip exclusions
grep -rn "\b[0-9]+ commands\b" docs/ --include="*.md" \
  | filter_exclusions \
  | while read line; do
      count=$(echo "$line" | grep -oE '[0-9]+ commands' | grep -oE '[0-9]+')
      if [ "$count" != "$EXPECTED_CMDS" ]; then
          echo "STALE: $line (expected $EXPECTED_CMDS)"
      fi
  done
```

**Auto-fix:** Yes (`--fix` mode) -- sed-replace exact count mismatches in non-excluded files.

### Phase 8: Skill/Agent Coverage

**What it checks:**

- Every skill file in `skills/` has a corresponding entry in `docs/skills-agents.md` AND `docs/guide/skills-agents.md`
- Every agent file in `agents/` has a corresponding entry in both skills docs
- Skill/agent counts in TL;DR sections match filesystem

**Implementation:**

```bash
# Get skills from filesystem
SKILLS_ON_DISK=$(find skills -name "*.md" -not -path "*/references/*" | sort)

# Get skills documented
SKILLS_IN_DOCS=$(grep -oE 'skills/[a-z/-]+\.md' docs/skills-agents.md | sort)

# Diff
comm -23 <(echo "$SKILLS_ON_DISK") <(echo "$SKILLS_IN_DOCS")  # Undocumented skills
```

**Auto-fix:** Yes (`--fix` mode) -- auto-append missing skills to the correct category table in both skills-agents.md files, using the skill's frontmatter description.

### Phase 9: Cross-Doc Freshness

**What it checks:**

- "See Also" sections: referenced counts match current (e.g., "26 skills, 8 agents")
- Architecture docs: key metrics flagged as warnings (not errors)
- REFCARD files: version references match current version
- Tutorial files: version in example commands matches current
- `mkdocs.yml` `site_description`: compare against latest CHANGELOG headline feature

**Scope:** Only files that claim to be current (not historical). Detect via:

- Files with `**Version**:` or `**Last Updated**:` headers
- Files referencing specific version numbers in non-historical context

**Auto-fix:** Partial -- version string replacement in REFCARDs. Count corrections in "See Also" sections. site_description is report-only.

---

## Two-Pass Interactive Review (--fix mode)

### Pass 1: Auto-Fix (non-interactive)

Automatically fixes safe, mechanical items:

- Exact count swaps in non-excluded active docs (e.g., `17 skills` -> `26 skills`)
- Missing skills appended to skills-agents.md tables
- Version string replacements in REFCARDs

```text
=== Pass 1: Auto-fix ===
  Fixed: docs/commands.md:362 (17 skills -> 26 skills)
  Fixed: docs/architecture.md:172 (7 agents -> 8 agents)
  Added: docs/skills-agents.md (code/sync-features)
  Added: docs/guide/skills-agents.md (code/sync-features)
  Auto-fixed: 4 items
```

### Pass 2: Interactive Review (uncertain items)

Presents items that need human judgment:

```text
=== Pass 2: Review remaining (4 items) ===

[1/4] docs/architecture/HUB-V2-ARCHITECTURE.md:152
  '97 commands total' -- in mermaid diagram label
  Context: Architecture snapshot document
  [f]ix  [s]kip  [e]xclude permanently: e
  -> Excluded (added to scripts/config/exclusions.txt)

[2/4] docs/tutorials/TUTORIAL-post-merge-pipeline.md:57
  '97 commands' -- illustrative example in tutorial
  [f]ix  [s]kip  [e]xclude permanently: e
  -> Excluded (added to scripts/config/exclusions.txt)

[3/4] docs/guide/desktop-release.md (NOT IN NAV)
  New file, needs mkdocs.yml nav entry
  [s]kip  [e]xclude permanently: s

[4/4] mkdocs.yml:2 site_description
  Headline: 'Mermaid MCP validation' -- CHANGELOG says 'Desktop release pipeline'
  [s]kip: s
```

---

## Exclusion Config

### Location

`scripts/config/exclusions.txt` -- next to scripts that consume it.

### Format

```text
# scripts/config/exclusions.txt
# Format: filepath[:pattern]
# Whole-file exclusions (skip entirely):
docs/VERSION-HISTORY.md
docs/CHANGELOG.md
docs/specs/_archive/

# Pattern exclusions (skip specific matches in specific files):
docs/architecture/HUB-V2-ARCHITECTURE.md:97 commands
docs/tutorials/TUTORIAL-post-merge-pipeline.md:97 commands
docs/demos/hub-v2.tape:97 commands

# Auto-generated exclusions:
# Excluded 2026-02-25 via interactive review
docs/api/DISCOVERY-API.md:97 commands
```

### Shared Between Scripts

Both `post-release-sweep.sh` and `docs-staleness-check.sh` read this file:

```bash
# In both scripts:
EXCLUSIONS_FILE="scripts/config/exclusions.txt"
filter_exclusions() {
    while IFS= read -r line; do
        local file=$(echo "$line" | cut -d: -f1)
        local match=$(echo "$line" | cut -d: -f2-)
        # Check against exclusion list
        if ! is_excluded "$file" "$match"; then
            echo "$line"
        fi
    done
}
```

### Audit Subcommand

```bash
./scripts/docs-staleness-check.sh --audit-exclusions

Exclusion audit:
  OK  docs/VERSION-HISTORY.md -- still exists
  OK  docs/CHANGELOG.md -- still exists
  !!  docs/demos/hub-v2.tape -- FILE DELETED
    Remove exclusion? [y/n]: y
  OK  docs/architecture/HUB-V2-ARCHITECTURE.md:97 commands
    -- pattern still matches (line 152)

Pruned 1 stale exclusion.
```

---

## Integration Points

### With existing tools

| Tool | Integration |
|------|-------------|
| `post-release-sweep.sh` | Shares `scripts/config/exclusions.txt`; handles version refs (Tier 2) |
| `validate-counts.sh` | Source of truth for counts; staleness check consumes its output |
| `mkdocs build --strict` | Catches broken links + missing nav; staleness check adds semantic checks |
| `/craft:check --for release` | Includes staleness check as Step 2d gate |
| `/craft:docs:update --post-merge` | Triggers staleness check after updates |

### CI integration

```yaml
# In .github/workflows/ci.yml
- name: Docs staleness check
  run: ./scripts/docs-staleness-check.sh --non-interactive
  # Warn only -- does not fail the build
  continue-on-error: true
```

### Release pipeline (Step 2d -- pre-release)

```text
Step 2a: bump-version.sh --verify    (Tier 1: core files)
Step 2b: validate-counts.sh          (Authoritative counts)
Step 2c: claude plugin validate .    (Plugin schema)
Step 2d: docs-staleness-check.sh     (Docs freshness)  <-- NEW
Step 3:  bump-version.sh             (Version bump)
...
Step 13.5: post-release-sweep.sh     (Tier 2: version refs post-release)
```

---

## Implementation Plan (Single Increment)

All 4 phases ship together since decisions are resolved:

**Scope:** Phases 6-9, two-pass interactive review, shared exclusion config, audit subcommand

**Files to create:**

- `scripts/docs-staleness-check.sh` -- main script (all 4 phases)
- `scripts/config/exclusions.txt` -- shared exclusion config (seed with known exclusions)

**Files to modify:**

- `skills/release/SKILL.md` -- add Step 2d
- `commands/docs/check.md` -- document `--deep` flag (wires to script)
- `docs/reference/REFCARD-RELEASE.md` -- add Step 2d to pipeline table

**Test coverage:**

- Unit test: `tests/test_docs_staleness.py` or bash-based validation
- Verify against known stale files (HUB-V2-ARCHITECTURE, tutorials)
- Verify exclusion config parsing
- Verify `--fix` mode actually fixes counts
- Verify `--audit-exclusions` prunes deleted files

**Refcard:**

- `docs/reference/REFCARD-DOCS-STALENESS.md` -- usage, phases, exclusion format
