---
description: Update documentation site based on code changes
category: site
arguments:
  - name: mode
    description: Update mode (smart|full)
    required: false
    default: smart
  - name: preview
    description: Preview changes without writing (alias: --dry-run)
    required: false
    default: false
  - name: validate
    description: Validate links after update
    required: false
    default: false
  - name: dry-run
    description: Preview changes without writing (alias for --preview)
    required: false
    default: false
    alias: -n
---

# /craft:site:update - Update Site Content from Code

You are an ADHD-friendly documentation site updater. Detect what changed in the codebase and update the documentation site accordingly.

## Purpose

**Keep your documentation site in sync with code changes:**

- Detects new/changed commands, features, configs
- Updates relevant documentation pages
- Validates links and structure
- Maintains design consistency

## Usage

```bash
/craft:site:update                  # Smart update (detect changes)
/craft:site:update full             # Force full update

# Preview changes without writing
/craft:site:update --preview        # Dry run - show what would change
/craft:site:update --dry-run        # Same as --preview (standardized)
/craft:site:update -n               # Short form

/craft:site:update --validate       # Update + validate links
```

## When Invoked

### Step 1: Analyze Changes

```bash
# Get recent code changes
git diff --name-only HEAD~10 -- "*.py" "*.ts" "*.js" "*.rs"
git log --oneline -10

# Check what's in docs
ls -la docs/

# Get last update timestamp
stat -f "%Sm" docs/REFCARD.md 2>/dev/null || stat -c "%y" docs/REFCARD.md
```

**Display:**

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:site:update                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 ANALYZING CHANGES                                        │
│                                                             │
│ Recent code changes:                                        │
│   • src/cli/sessions.py (+3 commands)                       │
│   • src/config.py (new options)                             │
│   • pyproject.toml (version bump: 0.3.6 → 0.3.7)            │
│                                                             │
│ Docs last updated: 2 days ago                               │
│                                                             │
│ Will update:                                                │
│   ✓ docs/REFCARD.md (new commands)                          │
│   ✓ docs/reference/commands.md (new commands)               │
│   ✓ docs/index.md (version badge)                           │
│   ✓ docs/reference/configuration.md (new options)           │
│   ○ mkdocs.yml (no nav changes needed)                      │
│                                                             │
│ Proceed? (Y/n/preview)                                      │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Update Detection Matrix

| Change Type | Files Changed | Docs to Update |
|-------------|---------------|----------------|
| New CLI command | `src/*/cli/*.py` | REFCARD, commands.md |
| New feature | `src/**/*.py` | index.md features, guide |
| Config change | `pyproject.toml`, `package.json` | installation.md, config.md |
| Version bump | Config files | All version references |
| New doc file | `docs/*.md` | mkdocs.yml navigation |
| API change | `src/*/api/*` | api.md, reference |

### Step 3: Execute Updates

For each file to update:

#### Update REFCARD.md

```markdown
# Quick Reference

## Essential Commands

| Command | Description |
|---------|-------------|
| `ait doctor` | Check installation |
| `ait detect` | Show project context |
| `ait sessions live` | **NEW** Show active sessions |
| `ait sessions conflicts` | **NEW** Detect conflicts |
...
```

#### Update commands.md

- Extract command help from CLI
- Update command tables
- Add new command sections
- Update examples

#### Update index.md

- Update version badge
- Add new features to feature grid
- Update "What's New" section if present

#### Update Configuration Reference

- Extract new config options
- Update defaults table
- Add examples

### Step 3.5: Synchronize Badges

After content updates are complete, synchronize version and CI badges across README.md and docs/index.md:

```python
from utils.badge_syncer import BadgeSyncer

print("\n📛 Syncing badges...")

syncer = BadgeSyncer(project_root=Path.cwd())
mismatches = syncer.sync_badges(
    files=['README.md', 'docs/index.md'],
    auto_confirm=False,  # Always prompt user
    calculate_coverage=True
)

if mismatches:
    print(f"✅ Updated {len(mismatches)} badge{'s' if len(mismatches) != 1 else ''}")
else:
    print("✅ Badges already in sync")
```

#### Display Format

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3.5: SYNCHRONIZING BADGES                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Found 3 badge issues:                                       │
│                                                             │
│   README.md:                                                │
│     • Update version badge: 2.9.1 → 2.10.0-dev              │
│     • Fix CI badge branch: main → dev                       │
│                                                             │
│   docs/index.md:                                            │
│     • Update version badge: 2.9.1 → 2.10.0-dev              │
│                                                             │
│ ✓ Updated 3 badges                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Error Handling

Badge sync is non-blocking - if synchronization fails, site update continues with a warning:

```python
try:
    mismatches = syncer.sync_badges(...)
except Exception as e:
    print(f"⚠️  Badge sync failed: {e}")
    print("Continuing with site update...")
```

#### Badges Synchronized

| Badge Type | Generated From | Files Updated |
|------------|----------------|---------------|
| Version | plugin.json, package.json, pyproject.toml | README.md, docs/index.md |
| CI Status | .github/workflows/*.yml | README.md, docs/index.md |
| Docs Coverage | .STATUS file "Documentation: XX%" | README.md, docs/index.md |

### Step 4: Validate (if --validate)

```bash
# Check for broken links
mkdocs build --strict 2>&1 | grep -E "(WARNING|ERROR)"

# Validate internal links
grep -r "\]\(" docs/ | grep -v "http" | while read link; do
  # Check if target exists
done
```

### Step 5: Show Results

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ SITE UPDATED                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Updated files:                                              │
│   • docs/REFCARD.md (+12 lines)                             │
│   • docs/reference/commands.md (+45 lines)                  │
│   • docs/index.md (version: 0.3.7)                          │
│   • docs/reference/configuration.md (+8 lines)              │
│                                                             │
│ Validation:                                                 │
│   ✓ All links valid                                         │
│   ✓ No broken references                                    │
│   ✓ Navigation intact                                       │
│                                                             │
│ What's next?                                                │
│   → Preview: mkdocs serve                                   │
│   → Deploy: /craft:site:deploy                              │
│   → Status: /craft:site:status                              │
└─────────────────────────────────────────────────────────────┘
```

## Full Mode (`full`)

Updates everything regardless of detected changes:

```bash
/craft:site:update full
```

**Updates:**

- All command references
- All configuration docs
- All version references
- All code examples
- Navigation structure
- Validates everything

## Preview Mode (`--preview`)

Shows what would be updated without making changes:

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:site:update --preview                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔍 PREVIEW MODE (no changes made)                           │
│                                                             │
│ Would update:                                               │
│                                                             │
│ docs/REFCARD.md:                                            │
│   Line 45: + | `ait sessions live` | Show active sessions | │
│   Line 46: + | `ait sessions conflicts` | Detect conflicts |│
│                                                             │
│ docs/reference/commands.md:                                 │
│   + New section: ## Session Commands                        │
│   + 4 new command entries                                   │
│                                                             │
│ docs/index.md:                                              │
│   Line 3: Version badge 0.3.6 → 0.3.7                       │
│                                                             │
│ Run without --preview to apply changes.                     │
└─────────────────────────────────────────────────────────────┘
```

## Integration

**Related commands:**

- `/craft:site:create` - Create new site
- `/craft:site:status` - Check site health
- `/craft:site:deploy` - Deploy to GitHub Pages

**Works with:**

- `/craft:docs:update` - Code documentation (different from site)
- `/craft:docs:feature` - After implementing features

## ADHD-Friendly Features

1. **Smart detection** - Only updates what changed
2. **Preview first** - See changes before applying
3. **Clear output** - Shows exactly what was updated
4. **Next steps** - Always shows what to do next
5. **Validation** - Catches broken links automatically

## Dry-Run Mode

Preview what documentation files will be updated without making changes:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Update Site Content                                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Changes Detected:                                           │
│   - src/cli/sessions.py (+3 commands)                         │
│   - pyproject.toml (version: 0.3.6 → 0.3.7)                   │
│   - docs last updated: 2 days ago                             │
│                                                               │
│ ✓ Files to Update:                                            │
│   - docs/REFCARD.md (add 3 new commands)                      │
│   - docs/reference/commands.md (command documentation)        │
│   - docs/index.md (version badge)                             │
│   - docs/installation.md (version references)                 │
│                                                               │
│ ⊘ No Changes:                                                 │
│   - mkdocs.yml (navigation unchanged)                         │
│                                                               │
│ 📊 Summary: 4 files to update, 1 unchanged                     │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Standardized flags:**

- `--dry-run` / `-n` - Modern standardized dry-run flag
- `--preview` - Legacy flag (still supported, same behavior)

## See Also

- `/craft:site:build` - Build site locally
- `/craft:site:deploy` - Deploy to GitHub Pages  
- `/craft:site:check` - Validate documentation
- Template: `templates/dry-run-pattern.md`
