---
description: Fix issues found by audit command
arguments:
  - name: scope
    description: "What to fix: errors, warnings, all (default: errors)"
    required: false
    default: errors
  - name: interactive
    description: Confirm each fix before applying
    required: false
    alias: -i
  - name: dry-run
    description: Preview fixes without applying
    required: false
    alias: -n
---

# /craft:docs:claude-md:fix - Auto-Fix CLAUDE.md Issues

Applies automatic fixes for issues found by `/craft:docs:claude-md:audit`.

**Prerequisites:** Run `/craft:docs:claude-md:audit` first to identify issues.

## What It Fixes

| Issue Type | Auto-Fixable | How |
|------------|--------------|-----|
| **Stale commands** | ✅ Yes | Remove from documentation |
| **Dead links** | ✅ Yes | Remove or comment out |
| **Version mismatch** | ✅ Yes | Update from source file |
| **Progress mismatch** | ✅ Yes | Sync from .STATUS |
| **Missing sections** | ❌ Manual | Template suggestion only |
| **Undocumented commands** | ❌ Manual | Needs descriptions |

## Show Steps First Pattern

This command previews fixes before applying, following the craft "Show Steps First" pattern.

### Step 1: Show Fix Plan

```
Fix Plan for CLAUDE.md

Last audit: 2 minutes ago
Issues found:
  🔴 Errors:   2 (auto-fixable)
  ⚠️  Warnings: 3 (2 auto-fixable, 1 manual)
  📝 Info:     3 (manual review)

Auto-Fixes (4):
  1. Remove stale command (Line 45: /craft:deploy:heroku)
  2. Remove dead link (Line 112: src/legacy/deploy.ts)
  3. Update version 2.8.1 → 2.9.0 (Line 8)
  4. Sync progress 95% → 98% (Line 15)

Manual Fixes Needed (2):
  1. Undocumented commands (need descriptions)
  2. Optimization opportunity (verbose section)

Proceed with auto-fixes? [y/n/interactive]
```

### Step 2: Apply Fixes

```bash
python3 utils/claude_md_fixer.py CLAUDE.md --scope errors
```

### Step 3: Show Results

```
Fixes Applied

Applied 4 fixes to CLAUDE.md:
  ✓ Removed stale command reference
  ✓ Removed dead link
  ✓ Updated version: v2.8.1 → v2.9.0
  ✓ Synced progress: 95% → 98%

File: /Users/dt/projects/dev-tools/craft/CLAUDE.md
Changes: -3 lines, +2 lines

Manual items remaining:
  • Add descriptions for 3 undocumented commands
  • Consider condensing Architecture section

Next steps:
  1. Review: git diff CLAUDE.md
  2. Address manual items: /craft:docs:claude-md:edit
  3. Commit: git add CLAUDE.md
```

## Usage

### Fix Errors Only (default)

```bash
/craft:docs:claude-md:fix
/craft:docs:claude-md:fix errors
```

Only fixes 🔴 Error-level issues.

### Fix Errors + Warnings

```bash
/craft:docs:claude-md:fix warnings
```

Fixes 🔴 Errors and ⚠️ Warnings.

### Fix Everything Auto-Fixable

```bash
/craft:docs:claude-md:fix all
```

Fixes all auto-fixable issues regardless of severity.

## Modes

### Interactive Mode

```bash
/craft:docs:claude-md:fix --interactive
/craft:docs:claude-md:fix -i
```

Confirm each fix before applying:

```
Interactive Fix Mode

Fix 1/4: Remove stale command
  Line 45: /craft:deploy:heroku
  Action: Delete line

Apply this fix? [y/n/skip-all/apply-all]
> y

✓ Applied

Fix 2/4: Remove dead link
  Line 112: See src/legacy/deploy.ts
  Action: Delete reference

Apply this fix? [y/n/skip-all/apply-all]
> n

✗ Skipped
...
```

### Dry Run

```bash
/craft:docs:claude-md:fix --dry-run
/craft:docs:claude-md:fix -n
```

Preview what would change without modifying files:

```
Dry Run: /craft:docs:claude-md:fix

Would apply 4 fixes to:
  ~/projects/dev-tools/craft/CLAUDE.md

Changes:
  Line 8:   v2.8.1 → v2.9.0
  Line 15:  Progress: 95% → Progress: 98%
  Line 45:  [DELETE] /craft:deploy:heroku reference
  Line 112: [DELETE] dead link to src/legacy/deploy.ts

Net change: -1 lines

Run without --dry-run to apply
```

## Fix Methods

### Version Update

Updates version string to match source file:

```markdown
Before: **Current Version:** v2.8.1
After:  **Current Version:** v2.9.0
```

**Source priority:** plugin.json > package.json > pyproject.toml > DESCRIPTION

### Stale Command Removal

Removes references to deleted commands:

```markdown
Before:
- /craft:check - Validate project
- /craft:deploy - Deploy (REMOVED)

After:
- /craft:check - Validate project
```

### Broken Link Removal

Removes or comments out broken links:

```markdown
Before: See [architecture](docs/arch.md) for details.
After:  <!-- See [architecture](docs/arch.md) for details. --> (link broken)
```

### Progress Sync

Updates progress to match .STATUS file:

```markdown
Before: progress: 95%
After:  progress: 98%
```

## Safety Features

### Backup Creation

Before applying fixes, creates `.CLAUDE.md.backup`:

```bash
cp CLAUDE.md .CLAUDE.md.backup
```

### Restore from Backup

If fixes break something:

```bash
mv .CLAUDE.md.backup CLAUDE.md
```

### Git Integration

If in a git repository, can review changes:

```bash
git diff CLAUDE.md
```

## Integration Points

### After Audit

```bash
/craft:docs:claude-md:audit
# Issues found...
/craft:docs:claude-md:fix
```

### Before Commit

```bash
/craft:docs:claude-md:audit --strict
/craft:docs:claude-md:fix
git add CLAUDE.md
git commit -m "docs: fix CLAUDE.md issues"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Fixes applied successfully |
| 1 | No fixes needed (no issues found) |
| 2 | Fix operation failed |

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:audit` | Find issues (run first) |
| `/craft:docs:claude-md:update` | Comprehensive sync (more thorough) |
| `/craft:docs:claude-md:edit` | Manual editing for complex fixes |

## Implementation

```bash
#!/usr/bin/env bash
# Location: commands/docs/claude-md/fix.md

set -euo pipefail

# Argument parsing
SCOPE="${1:-errors}"
INTERACTIVE=false
DRY_RUN=false

# Parse flags
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        errors|warnings|all)
            SCOPE="$1"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Check if CLAUDE.md exists
if [[ ! -f CLAUDE.md ]]; then
    echo "Error: CLAUDE.md not found in current directory"
    exit 2
fi

# Show fix plan
echo "Fix Plan for CLAUDE.md"
echo ""

# Run auditor to get issues
python3 utils/claude_md_auditor.py CLAUDE.md > /tmp/audit_output.txt || true

# Count fixable issues
FIXABLE_COUNT=$(grep -c "auto-fixable" /tmp/audit_output.txt || echo "0")

if [[ "$FIXABLE_COUNT" -eq 0 ]]; then
    echo "No auto-fixable issues found"
    exit 1
fi

echo "Auto-Fixes: $FIXABLE_COUNT"
echo ""

# Ask for confirmation (unless dry-run or interactive)
if [[ "$DRY_RUN" == "false" ]] && [[ "$INTERACTIVE" == "false" ]]; then
    read -p "Proceed with auto-fixes? [y/n/interactive] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ii]$ ]]; then
        INTERACTIVE=true
    elif [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Fix cancelled"
        exit 0
    fi
fi

# Build fixer command
FIXER_CMD="python3 utils/claude_md_fixer.py CLAUDE.md --scope $SCOPE"

if [[ "$INTERACTIVE" == "true" ]]; then
    FIXER_CMD="$FIXER_CMD --interactive"
fi

if [[ "$DRY_RUN" == "true" ]]; then
    FIXER_CMD="$FIXER_CMD --dry-run"
fi

# Run fixer
$FIXER_CMD
```
