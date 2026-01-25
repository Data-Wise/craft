# Craft Documentation Systems Architecture

## Overview

Craft includes three complementary documentation systems, each with a specific purpose:

### 1. **`/craft:docs:update`** - Code Documentation Sync

**Purpose:** Keep internal documentation aligned with code changes
**Scope:** docs/ directory (internal guides, tutorials, references)
**Detection:** Changes to commands, modules, features, help text
**Output:** Updated markdown files with new documentation

**Detection Categories:**

- Version references (v2.6.0 → v2.7.0)
- Command counts (99 → 101 commands)
- Broken internal links
- Missing help documentation
- Outdated feature status
- Inconsistent terminology
- Missing cross-references
- Stale code examples
- Outdated architecture diagrams

**Example Usage:**

```bash
# Interactive mode with category prompts
/craft:docs:update --interactive

# Auto-approve all updates
/craft:docs:update --auto-yes

# Update only version references
/craft:docs:update -C version_refs
```

**Implementation Status:** ✅ Complete

- Python orchestrator: `utils/docs_update_orchestrator.py`
- Detection engine: `utils/docs_detector.py`
- Validation: `utils/help_file_validator.py`
- All 13 tests passing (706/706)

---

### 2. **`/craft:site:update`** - Website Content Sync

**Purpose:** Keep documentation website in sync with features/commands
**Scope:** Published docs for website (README, REFCARD, feature grids)
**Detection:** New commands, config changes, version bumps
**Output:** Updated website documentation files

**Capabilities:**

- Detects code changes (new commands, features)
- Updates REFCARD.md with new commands
- Updates feature grids and command tables
- Syncs version references
- Validates navigation structure

**Example Usage:**

```bash
# Smart detection and update
/craft:site:update

# Preview without changes
/craft:site:update --dry-run

# Force full update
/craft:site:update full

# Update + validate links
/craft:site:update --validate
```

**Implementation Status:** 📝 Documented

- Command file: `commands/site/update.md` (840 lines)
- Needs: Site update engine implementation
- Integrates with: mkdocs, GitHub Pages

---

### 3. **`/craft:docs:lint`** - Documentation Quality

**Purpose:** Enforce markdown quality standards
**Scope:** All documentation files
**Detection:** Markdown violations (24 rules)
**Output:** Fixed markdown files

**Features:**

- 24 markdownlint rules configured
- Auto-fix for common issues
- Interactive prompts for complex fixes
- Pre-commit hook integration
- Disabled warnings for MD040 (language tags), MD001 (heading increment)

**Example Usage:**

```bash
# Run linting with auto-fix
/craft:docs:lint --fix

# Check without fixing
/craft:docs:lint

# Interactive mode (proposed)
/craft:docs:lint --interactive
```

**Implementation Status:** ✅ Complete

- Config: `.markdownlint.json` (optimized for Craft)
- Command: `commands/docs/lint.md`
- Pre-commit hooks: Active
- All tests passing

---

## Workflow Integration

### Typical Documentation Update Workflow

```
Code Changes
    ↓
1. Run: /craft:docs:lint --fix (ensure quality)
    ↓
2. Run: /craft:docs:update --interactive (update internal docs)
    ↓
3. Review changes: git diff docs/
    ↓
4. Commit & push to dev: git commit -m "docs: ..."
    ↓
5. Create PR: gh pr create --base dev
```

### When to Use Each Command

| Scenario | Use Command | Example |
|----------|------------|---------|
| **After implementing a feature** | `/craft:docs:update` | New `/craft:do` command |
| **Before committing any docs** | `/craft:docs:lint --fix` | Fix markdown errors |
| **Syncing website with code** | `/craft:site:update` | Version bump, new feature |
| **Publishing documentation** | `/craft:site:deploy` | Deploy to GitHub Pages |
| **Checking doc health** | `/craft:docs:check` | Validate all links |

---

## Command Relationships

```
/craft:docs:update (INTERNAL DOCS)
    └── Orchestrates:
        ├── docs_detector.py (9-category detection)
        ├── help_file_validator.py (help validation)
        ├── /craft:docs:lint (quality check)
        └── /craft:docs:check (link validation)

/craft:site:update (WEBSITE DOCS)
    └── Needs:
        ├── Site content engine
        ├── REFCARD.md updater
        ├── Command table generator
        └── Link validator

/craft:docs:lint (QUALITY CHECKS)
    └── Uses:
        ├── markdownlint-cli2 (24 rules)
        ├── .markdownlint.json (config)
        └── Pre-commit hooks
```

---

## File Organization

### Internal Documentation (`docs/`)

- **guides/** - Step-by-step guides
- **reference/** - API references, quick cards
- **tutorials/** - Learning materials
- **specs/** - Implementation specifications
- **architecture/** - System design docs
- **brainstorm/** - Working drafts (gitignored)

### Commands Documentation (`commands/`)

- **docs/** - All documentation update commands
- **site/** - All website management commands
- **check.md** - Pre-flight validation
- **hub.md** - Command discovery

### Supporting Files

- **.markdownlint.json** - Markdown quality rules
- **.linkcheck-ignore** - Expected broken links
- **mkdocs.yml** - Website structure
- **README.md** - Project overview

---

## Current Status Summary

| System | Purpose | Status | Key File | Tests |
|--------|---------|--------|----------|-------|
| **docs:update** | Internal doc sync | ✅ Complete | `utils/docs_update_orchestrator.py` | 13/13 ✅ |
| **docs:lint** | Quality enforcement | ✅ Complete | `.markdownlint.json` | Passing ✅ |
| **docs:check** | Link validation | ✅ Complete | `commands/docs/check.md` | Passing ✅ |
| **site:update** | Website sync | 📝 Documented | `commands/site/update.md` | Ready |
| **site:check** | Site validation | ✅ Complete | `commands/site/check.md` | Passing ✅ |
| **site:deploy** | GitHub Pages deploy | ✅ Complete | `commands/site/deploy.md` | Passing ✅ |

---

## Next Steps (v2.7.0 Planning)

### Phase 1: Claude Code Integration (Current)

- ✅ docs:update orchestrator complete
- ✅ Markdown linting optimized
- 📝 site:update documented (needs engine)

### Phase 2: Interactive Prompts

- Implement category-level questions in docs:update
- Add preview mode with diffs
- Connect to AskUserQuestion tool

### Phase 3: Site Content Engine

- Build site-specific update logic
- Command table generation
- Feature grid updates
- REFCARD updates

### Phase 4: Full Integration

- Multi-command workflows
- Automated release cycles
- Quality gates

---

## Development Notes

### Architecture Decisions

1. **Separate systems** - docs:update (internal) vs site:update (external)
   - Internal docs evolve during development
   - Website docs are published and stable
   - Different update frequencies and audiences

2. **ADHD-friendly design**
   - One command per system
   - Smart detection (no remembering what to update)
   - Visual progress and clear next steps
   - Batch operations for efficiency

3. **Safe by default**
   - Dry-run mode for preview
   - All changes git-reversible
   - Validation before deployment
   - Quality gates via linting

### Testing Strategy

- Unit tests for utilities (docs_detector, validator)
- Integration tests for orchestrator
- E2E tests for full workflows
- Pre-commit hooks for quality gates
- CI/CD validation before merge

### Performance Targets

- Detection: < 2 seconds
- Updates: < 100ms per file
- Linting: < 500ms per 10 files
- Full workflow: < 10 seconds

---

## References

- **Command Docs:** `commands/docs/` and `commands/site/`
- **Utilities:** `utils/`
- **Configuration:** `.markdownlint.json`, `.linkcheck-ignore`
- **Tests:** `tests/test_craft_plugin.py`
- **Specs:** `docs/specs/`

---

**Last Updated:** 2026-01-25
**Version:** 2.7.0 (v2.6.0 infrastructure, v2.7.0 planning)
**Status:** Core systems complete, site:update engine pending
