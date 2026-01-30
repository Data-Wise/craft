---
description: Audit CLAUDE.md for completeness and accuracy
arguments:
  - name: strict
    description: Exit with error code if issues found (for CI)
    required: false
    default: false
---

# /craft:docs:claude-md:audit - Validate CLAUDE.md Quality

Validates CLAUDE.md for version sync, command coverage, broken links, and structural issues.

**This command is read-only.** Use `/craft:docs:claude-md:fix` to apply fixes.

## What It Does

Performs 5 validation checks:

| Check | Description | Severity |
|-------|-------------|----------|
| **Version Sync** | CLAUDE.md version matches source | Warning |
| **Command Coverage** | All commands documented, no stale refs | Error |
| **Broken Links** | Internal file references valid | Error |
| **Required Sections** | Expected sections present | Warning |
| **Status Sync** | .STATUS file alignment | Warning |

## Show Steps First Pattern

This command previews validation checks before executing, following the craft "Show Steps First" pattern.

### Step 1: Show Validation Plan

```
Audit Plan for CLAUDE.md

File: $(pwd)/CLAUDE.md
Size: 329 lines
Last modified: 2 days ago

Validation Checks (5):
  1. Version Sync - Check version matches plugin.json
  2. Command Coverage - Verify all commands documented
  3. Broken Links - Find invalid internal links
  4. Required Sections - Check standard structure
  5. Status Sync - Compare with .STATUS file

Proceed with audit? [y/n]
```

### Step 2: Run Validation

```bash
python3 utils/claude_md_auditor.py CLAUDE.md
```

### Step 3: Show Results

```
Audit Results for CLAUDE.md

🔴 Errors (2) - Must Fix

1. Stale Command Reference
   Line 45: /craft:deploy:heroku
   Status: Command removed in v2.0.0
   Fix: /craft:docs:claude-md:fix

2. Dead Link
   Line 112: See src/legacy/deploy.ts
   Status: File deleted
   Fix: /craft:docs:claude-md:fix

⚠️  Warnings (3) - Should Fix

1. Version Mismatch
   CLAUDE.md: v2.8.1
   Actual: v2.9.0 (from plugin.json)
   Fix: /craft:docs:claude-md:fix

2. Progress Out of Sync
   CLAUDE.md: 95%
   .STATUS: 98%
   Fix: /craft:docs:claude-md:fix

3. Missing Section
   Expected: "Contributing" section
   Fix: Manual edit required

📝 Info (2) - Optional

1. Undocumented Commands (3)
   - /craft:docs:claude-md:audit (new)
   - /craft:docs:claude-md:fix (new)
   - /craft:docs:claude-md:scaffold (new)
   Fix: /craft:docs:claude-md:update

2. Optimization Opportunity
   "Architecture" section is verbose (45 lines)
   Could condense to ~25 lines

Summary:
  🔴 Errors:   2 (auto-fixable)
  ⚠️  Warnings: 3 (2 auto-fixable, 1 manual)
  📝 Info:     2 (optional)

Next: /craft:docs:claude-md:fix
```

## Usage

### Basic Audit

```bash
/craft:docs:claude-md:audit
```

Audits `./CLAUDE.md` with user confirmation.

### Strict Mode (CI)

```bash
/craft:docs:claude-md:audit --strict
```

Returns exit code 1 if errors found. For CI pipelines:

```yaml
# .github/workflows/docs.yml
- name: Validate CLAUDE.md
  run: /craft:docs:claude-md:audit --strict
```

## Integration Points

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
# Validate CLAUDE.md before commit
if git diff --cached --name-only | grep -q "CLAUDE.md"; then
    /craft:docs:claude-md:audit --strict || exit 1
fi
```

### craft:check Integration

The `/craft:check` command automatically runs audit if CLAUDE.md exists.

## Validation Details

### 1. Version Sync Check

Compares version in CLAUDE.md with source files:

- `plugin.json` for craft plugins
- `package.json` for Node.js projects
- `pyproject.toml` for Python projects
- `DESCRIPTION` for R packages

**Severity:** Warning (version drift is common during development)

### 2. Command Coverage Check

Scans `commands/` directory and compares with CLAUDE.md references:

- **Missing commands:** New commands not yet documented (Info)
- **Stale commands:** Documented commands that don't exist (Error)

**Severity:** Error for stale, Info for missing

### 3. Broken Links Check

Validates internal file references in CLAUDE.md:

- Relative paths (`docs/guide/feature.md`)
- Absolute paths from project root (`/commands/check.md`)
- Skips external URLs

**Severity:** Error (broken links cause confusion)

### 4. Required Sections Check

Verifies standard sections exist based on project type:

**Craft Plugin:**

- Quick Commands
- Project Structure
- Testing
- Architecture

**Teaching Site:**

- Course Overview
- Workflow
- Publishing

**R Package:**

- Quick Reference
- Development
- Testing

**Severity:** Warning (structure flexibility needed)

### 5. Status Sync Check

Compares progress/version in CLAUDE.md with `.STATUS` file if present.

**Severity:** Warning (sync issues are minor)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No errors found (warnings OK) |
| 1 | Errors found (strict mode only) |
| 2 | Validation failed to run |

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:fix` | Apply fixes for issues found |
| `/craft:docs:claude-md:update` | Sync with project state |
| `/craft:check` | Pre-flight validation (includes audit) |

## Implementation

```bash
#!/usr/bin/env bash
# Location: commands/docs/claude-md/audit.md

set -euo pipefail

# Argument parsing
STRICT=${1:-false}

# Check if CLAUDE.md exists
if [[ ! -f CLAUDE.md ]]; then
    echo "Error: CLAUDE.md not found in current directory"
    exit 2
fi

# Show validation plan
echo "Audit Plan for CLAUDE.md"
echo ""
echo "File: $(pwd)/CLAUDE.md"
echo "Size: $(wc -l < CLAUDE.md) lines"
echo "Last modified: $(stat -f '%Sm' -t '%Y-%m-%d' CLAUDE.md 2>/dev/null || stat -c '%y' CLAUDE.md 2>/dev/null | cut -d' ' -f1)"
echo ""
echo "Validation Checks (5):"
echo "  1. Version Sync - Check version matches source"
echo "  2. Command Coverage - Verify all commands documented"
echo "  3. Broken Links - Find invalid internal links"
echo "  4. Required Sections - Check standard structure"
echo "  5. Status Sync - Compare with .STATUS file"
echo ""

# Ask for confirmation (unless in strict mode)
if [[ "$STRICT" != "true" ]]; then
    read -p "Proceed with audit? [y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Audit cancelled"
        exit 0
    fi
fi

# Run audit utility
if [[ "$STRICT" == "true" ]]; then
    python3 utils/claude_md_auditor.py CLAUDE.md --strict
else
    python3 utils/claude_md_auditor.py CLAUDE.md
fi
```
