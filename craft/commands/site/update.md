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
/craft:site:update --preview        # Dry run - show what would change
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
