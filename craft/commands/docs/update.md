# /craft:docs:update - Universal Documentation Updater

You are an ADHD-friendly documentation updater. Detect what needs updating and handle it with minimal cognitive load.

## Purpose

**The "one command" solution for keeping docs current:**
- Smart mode (default): Detect what changed, update only what's needed
- Full mode: Update ALL documentation types regardless of changes

## Usage

```bash
/craft:docs:update              # Smart: detect what changed, update relevant
/craft:docs:update full         # Update ALL doc types
/craft:docs:update all          # Alias for full
/craft:docs:update --preview    # Show what would be updated (dry run)
```

## When Invoked

### Step 1: Analyze Current State

```bash
# Get recent changes
git diff --name-only HEAD~10
git log --oneline -10

# Check file timestamps
find docs/ -name "*.md" -mtime +7

# Detect project type
ls pyproject.toml package.json DESCRIPTION 2>/dev/null
```

**Determine scope:**
- If arg is `full` or `all` → Update everything
- Otherwise → Smart detection mode

### Step 2: Smart Detection (Default Mode)

Analyze recent changes and map to affected docs:

| Change Type | Files Changed | Docs to Update |
|-------------|---------------|----------------|
| New CLI command | `src/*/cli/*.py` | CLI help epilogs, commands.md, REFCARD |
| Config change | `pyproject.toml`, `package.json` | installation.md, README |
| New feature | Any `src/` | guides, README features, CLAUDE.md |
| API change | `src/*/api/*` | api.md, OpenAPI spec |
| Version bump | Config files | All version references |
| New doc file | `docs/*.md` | mkdocs.yml navigation |

### Step 3: Show Update Plan

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:update                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Analyzing recent changes...                                 │
│                                                             │
│ Detected:                                                   │
│   • 2 new CLI commands (src/aiterm/cli/sessions.py)         │
│   • 1 modified config (pyproject.toml version bump)         │
│   • 3 new doc files (docs/guide/sessions.md, ...)           │
│                                                             │
│ Will update:                                                │
│   ✓ docs/reference/commands.md (new commands)               │
│   ✓ docs/REFCARD.md (new commands)                          │
│   ✓ README.md (feature list)                                │
│   ✓ CLAUDE.md (version, status)                             │
│   ✓ mkdocs.yml (new nav entries)                            │
│   ○ CHANGELOG.md (skipped - use docs:changelog for release) │
│                                                             │
│ Proceed? (y/n/select)                                       │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Full Mode (When `full` or `all` Specified)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:update full                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Full documentation update:                                  │
│                                                             │
│ Phase 1: Code Analysis                                      │
│   • Scanning CLI commands...                                │
│   • Extracting docstrings...                                │
│   • Reading current docs...                                 │
│                                                             │
│ Phase 2: Updates                                            │
│   ✓ CLI Help epilogs (3 commands updated)                   │
│   ✓ docs/reference/commands.md (+45 lines)                  │
│   ✓ docs/REFCARD.md (+12 lines)                             │
│   ✓ docs/reference/REFCARD-*.md (domain refcards)           │
│   ✓ README.md (badges, feature list)                        │
│   ✓ CLAUDE.md (version, quick reference)                    │
│   ✓ mkdocs.yml (navigation updated)                         │
│                                                             │
│ Phase 3: Validation                                         │
│   ✓ All links valid                                         │
│   ✓ Code examples compile                                   │
│                                                             │
│ ✅ 7 files updated, 0 errors                                │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Execute Updates

For each doc type to update:

#### CLI Help Epilogs
```python
# Find CLI commands with missing/outdated epilogs
# Update epilogs with usage examples
```

#### Commands Reference
- Read current `docs/reference/commands.md`
- Compare with actual CLI commands
- Add missing commands, update changed ones

#### REFCARD
- Update `docs/REFCARD.md` quick reference
- Update domain-specific `docs/reference/REFCARD-*.md`

#### README
- Update feature list
- Update badges (version, tests, coverage)
- Update installation instructions if changed

#### CLAUDE.md
- Update version references
- Update "Quick Reference" section
- Update "Project Status" section

#### mkdocs.yml Navigation
- Detect orphan doc files
- Add missing nav entries
- Validate structure

## What Gets Updated (Matrix)

| Doc Type | Smart Mode | Full Mode |
|----------|------------|-----------|
| CLI Help epilogs | If commands changed | Always |
| docs/reference/commands.md | If commands changed | Always |
| docs/REFCARD.md | If commands changed | Always |
| docs/reference/REFCARD-*.md | If relevant area changed | Always |
| README.md | If features/version changed | Always |
| CLAUDE.md | Always (status tracking) | Always |
| mkdocs.yml | If new doc files | Always |
| CHANGELOG.md | Never (use docs:changelog) | Never |

## Output Format

```
✅ DOCUMENTATION UPDATE COMPLETE

Mode: smart (detected 5 updates needed)

Updated:
  • docs/reference/commands.md (+23 lines)
  • docs/REFCARD.md (+8 lines)
  • README.md (badges, features)
  • CLAUDE.md (version sync)
  • mkdocs.yml (2 new nav entries)

Skipped:
  • CHANGELOG.md (use /craft:docs:changelog for releases)
  • docs/api/ (no API changes detected)

What's next?
  → Validate: /craft:docs:validate
  → Commit: git add -A && git commit -m "docs: update documentation"
  → Deploy: /craft:site:deploy
```

## ADHD-Friendly Features

### 1. One Command Does It All
No need to remember which specific command to run. Just `/craft:docs:update` and it figures out what's needed.

### 2. Clear Preview
Always shows what will be updated before doing anything.

### 3. "What's Next" Hints
Every output ends with suggested next steps.

### 4. Full Mode for Peace of Mind
When unsure, `full` mode ensures everything is current.

## Integration

This is a **workflow command** that orchestrates individual commands:

- Calls `/craft:docs:sync` for code-to-doc mapping
- Calls `/craft:docs:claude-md` for CLAUDE.md updates
- Calls `/craft:docs:nav-update` for mkdocs navigation
- Calls `/craft:docs:validate` for final validation (in full mode)

**Related commands:**
- `/craft:docs:feature` - After implementing a feature
- `/craft:docs:done` - End of session updates
- `/craft:docs:changelog` - For release changelogs
