# Brainstorm: Docs Staleness Detection System

**Date:** 2026-02-25
**Context:** During post-merge docs health checks, we repeatedly find the same categories of drift: stale counts, missing nav entries, broken cross-references, and undocumented skills/commands. Currently this requires manual agent-driven exploration. The `/craft:docs:check` command and `post-release-sweep.sh` catch some issues but miss many.
**Goal:** Extend `/craft:docs:update` (or a new `/craft:docs:audit`) to systematically detect all categories of documentation staleness.

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

## Proposed Solution: `/craft:docs:audit` Enhancement

### Option A: Extend existing `/craft:docs:check`

Add new phases to the existing 5-phase check pipeline:

```text
Phase 1: Broken links (existing)
Phase 2: Missing images (existing)
Phase 3: Frontmatter validation (existing)
Phase 4: Code block syntax (existing)
Phase 5: Mermaid validation (existing)
Phase 6: Nav completeness     ← NEW
Phase 7: Count consistency    ← NEW
Phase 8: Skill/agent coverage ← NEW
Phase 9: Cross-doc freshness  ← NEW
```

**Pros:** Single command, builds on existing infrastructure
**Cons:** `/craft:docs:check` already takes 10-15s, adding 4 more phases could push to 30s+

### Option B: New dedicated script `scripts/docs-staleness-check.sh`

Standalone script (like `post-release-sweep.sh`) that focuses purely on staleness:

```bash
./scripts/docs-staleness-check.sh           # Dry-run report
./scripts/docs-staleness-check.sh --fix     # Auto-fix mechanical issues
./scripts/docs-staleness-check.sh --json    # Machine-readable output
```

**Pros:** Fast, focused, can run in CI, complements post-release-sweep
**Cons:** Yet another script to maintain, overlaps with docs:check

### Option C: Hybrid — script backend, command frontend

Script does the detection, `/craft:docs:check` calls it as Phase 6+:

```text
/craft:docs:check          → Phases 1-5 (existing) + Phase 6 (staleness summary)
/craft:docs:check --deep   → Phases 1-5 + full staleness audit (Phases 6-9)
./scripts/docs-staleness-check.sh  → Direct script access for CI/automation
```

**Pros:** Best of both worlds, no UX change for casual use, deep mode when needed
**Cons:** Slightly more complex wiring

---

## Detection Modules (Phase 6-9 Detail)

### Phase 6: Nav Completeness

**What it checks:**

- Every `.md` file in `docs/` (excluding `.archive/`, `brainstorm/`, `orch/`, `dev/`, `specs/SPEC-*`) has an entry in `mkdocs.yml` nav
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

**Auto-fix:** No — nav placement requires human judgment about section grouping.

### Phase 7: Count Consistency

**What it checks:**

- Grep all docs for patterns like `\d+ commands`, `\d+ skills`, `\d+ agents`, `\d+ tests`
- Compare against authoritative counts from `validate-counts.sh`
- Flag any mismatch (excluding VERSION-HISTORY.md, CHANGELOG.md, archived specs)

**Exclusions:**

- `docs/VERSION-HISTORY.md` — historical, counts were correct at time of release
- `docs/CHANGELOG.md` — historical log
- `docs/specs/_archive/` — frozen design docs
- Tutorial/example files where counts are illustrative (e.g., "97 commands" in a demo)

**Implementation:**

```bash
EXPECTED_CMDS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Commands:" | awk '{print $2}')
EXPECTED_SKILLS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Skills:" | awk '{print $2}')
EXPECTED_AGENTS=$(./scripts/validate-counts.sh 2>/dev/null | grep "Agents:" | awk '{print $2}')

# Scan active docs (not archive/changelog/version-history)
grep -rn "\b[0-9]+ commands\b" docs/ --include="*.md" \
  | grep -v CHANGELOG | grep -v VERSION-HISTORY | grep -v _archive \
  | while read line; do
      count=$(echo "$line" | grep -oE '[0-9]+ commands' | grep -oE '[0-9]+')
      if [ "$count" != "$EXPECTED_CMDS" ]; then
          echo "STALE: $line (expected $EXPECTED_CMDS)"
      fi
  done
```

**Auto-fix:** Yes (`--fix` mode) — sed replace for exact count mismatches in non-historical files.

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

**Auto-fix:** No — descriptions require human writing. Report only.

### Phase 9: Cross-Doc Freshness

**What it checks:**

- "See Also" sections: referenced counts match current (e.g., "26 skills, 8 agents")
- Architecture docs: key metrics match reality (command counts, category counts)
- REFCARD files: version references match current version
- Tutorial files: version in example commands matches current

**Scope:** Only files that claim to be current (not historical). Detect via:

- Files with `**Version**:` or `**Last Updated**:` headers
- Files referencing specific version numbers in non-historical context

**Auto-fix:** Partial — version string replacement in REFCARDs (like post-release-sweep Tier 2). Count corrections in "See Also" sections.

---

## Integration Points

### With existing tools

| Tool | Integration |
|------|-------------|
| `post-release-sweep.sh` | Delegates Tier 2 version scanning; staleness check handles counts and coverage |
| `validate-counts.sh` | Source of truth for counts; staleness check consumes its output |
| `mkdocs build --strict` | Catches broken links + missing nav; staleness check adds semantic checks |
| `/craft:check --for release` | Should include staleness check as a gate |
| `/craft:docs:update --post-merge` | Should trigger staleness check after updates |

### CI integration

```yaml
# In .github/workflows/ci.yml
- name: Docs staleness check
  run: ./scripts/docs-staleness-check.sh --json
  # Fail CI if critical staleness found (missing nav, wrong counts)
```

### Release pipeline

```text
Step 3:  bump-version.sh          (Tier 1: core files)
Step 13.5: post-release-sweep.sh  (Tier 2: version refs)
Step 13.6: docs-staleness-check.sh (Tier 2+: counts, coverage, nav)  ← NEW
```

---

## Implementation Plan

### Increment 1: Core script (quick win)

**Scope:** Nav completeness + count consistency
**Files:** `scripts/docs-staleness-check.sh`
**Effort:** ~2 hours
**Value:** Catches the two most common drift categories

### Increment 2: Skill/agent coverage

**Scope:** Phase 8 — cross-check filesystem vs docs
**Files:** Extend `scripts/docs-staleness-check.sh`
**Effort:** ~1 hour
**Value:** Prevents undocumented skills/agents

### Increment 3: Cross-doc freshness

**Scope:** Phase 9 — "See Also" counts, architecture metrics, REFCARD versions
**Files:** Extend script + add exclusion config
**Effort:** ~2 hours
**Value:** Catches the long-tail drift in reference docs

### Increment 4: Integration

**Scope:** Wire into `/craft:docs:check --deep`, `/craft:check --for release`, CI
**Files:** `commands/docs/check.md`, `skills/release/SKILL.md`, CI workflow
**Effort:** ~1 hour
**Value:** Makes staleness detection automatic

---

## Recommended Approach

**Option C (Hybrid)** with incremental delivery:

1. Start with `scripts/docs-staleness-check.sh` (Increment 1)
2. Run it manually after merges to validate
3. Wire into `/craft:docs:check --deep` (Increment 4)
4. Add to release pipeline as Step 13.6

This follows the same pattern as `post-release-sweep.sh` — standalone script first, integration later.

---

## Decision Needed

- [ ] Option A (extend docs:check), B (standalone script), or C (hybrid)?
- [ ] Should stale counts in architecture docs (HUB-V2-ARCHITECTURE "97 commands") be flagged or excluded?
- [ ] Should VERSION-HISTORY.md old entries be corrected retroactively or left as historical?
- [ ] CI enforcement: warning only, or fail the build?
