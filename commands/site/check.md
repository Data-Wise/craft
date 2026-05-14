---
description: Validate documentation site for broken links and common issues
category: site
arguments:
  - name: dry-run
    description: Preview validation checks without analyzing files
    required: false
    default: false
    alias: -n
---

# /craft:site:check - Validate Documentation

Check documentation sites (MkDocs, Quarto, pkgdown) for common issues before deployment.

## Usage

```bash
# Preview validation plan
/craft:site:check --dry-run
/craft:site:check -n

# Run validation
/craft:site:check
```

## Dry-Run Output

```text
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Validate Documentation                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Type: MkDocs                                              │
│   - Config: mkdocs.yml                                        │
│   - Site directory: docs/                                     │
│                                                               │
│ ✓ Validation Checks:                                          │
│   0. Pre-Build Lint (NEW)                                     │
│      - Markdown formatting via /craft:docs:lint               │
│      - Blocks deployment if issues found                      │
│                                                               │
│   1. Link Validation                                          │
│      - Internal links (~450 files to check)                   │
│      - External links (if --strict)                           │
│      - Anchor links (#sections)                               │
│                                                               │
│   2. Structure Validation                                     │
│      - Nav items have corresponding files                     │
│      - No orphaned pages                                      │
│      - Images exist and are referenced                        │
│                                                               │
│   3. Build Test                                               │
│      - Command: mkdocs build --strict                         │
│      - Check for errors and warnings                          │
│                                                               │
│ 📊 Summary: 4 validation checks on ~450 files                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only command, so dry-run mainly shows what will be checked.

## Checks Performed

### 0. Pre-Build Lint (NEW in v2.7.0)

Before running any build validation, lint all markdown files:

```bash
# Run markdown linting first
/craft:docs:lint "$path"

# If errors found:
#   - Report lint issues
#   - Suggest: /craft:docs:lint --fix
#   - Exit code 1 (block deployment)
```

**Why Lint First:**

- Catches formatting issues before build
- Missing code fence languages cause rendering problems
- Inconsistent list formatting breaks rendered output
- Saves time by failing fast

**Output:**

```text
╭─ /craft:site:check ─────────────────────────────────────────╮
│                                                             │
│ Phase 0: Pre-Build Lint                                     │
│ ✗ 3 markdown issues found                                   │
│   - docs/guide.md:21 [MD032] Missing blank line             │
│   - docs/api.md:45 [MD040] Missing language tag             │
│   - README.md:8 [MD034] Bare URL                            │
│                                                             │
│ Fix with: /craft:docs:lint --fix                            │
│                                                             │
│ BLOCKING: Lint issues must be fixed before deployment       │
╰─────────────────────────────────────────────────────────────╯
```

### 1. Link Validation

Check for broken links using `/craft:docs:check-links`:

- **Internal links** - References to other docs
- **External links** - URLs (if --strict mode)
- **Anchor links** - #sections within pages

**Implementation:**

```bash
# Run internal link validation first (fast)
claude "/craft:docs:check-links default"

# If release mode requested, include comprehensive checks
claude "/craft:docs:check-links release"

# Collect results and integrate into site check report
```

**Integration with site:check:**

- Internal links checked via `/craft:docs:check-links`
- Results merged into overall validation report
- Broken links block deployment (exit code 1)

### 2. Spelling Check

Common misspellings in technical documentation.

### 3. Structure Validation

- All nav items have corresponding files
- No orphaned pages (not in navigation)
- Images exist and are properly referenced

### 4. Build Test

- Can the site build without errors?
- Any warnings to review?

## Implementation by Site Type

### MkDocs

```bash
# Check links (if linkchecker installed)
linkchecker http://localhost:8000

# Or use mkdocs strict mode
mkdocs build --strict
```

### pkgdown

```r
# Check for issues
pkgdown::check_pkgdown()
```

### Quarto

```bash
# Build with strict mode
quarto render --strict
```

## Output Example

```text
📋 DOCUMENTATION VALIDATION REPORT

Site Type: MkDocs

✅ PASSED:
• Build: No errors
• Links: All internal links valid (450 checked)
• Structure: All nav items have files
• Images: All 23 images found

⚠️ WARNINGS:
• Unused file: docs/archive/old-guide.md (not in nav)
• Long page: docs/reference.md (>5000 lines)

❌ ERRORS:
• Broken link: docs/guide.md → missing.md (line 45)
• Missing file: docs/api.md (referenced in mkdocs.yml nav)

SUMMARY: 4 passed, 2 warnings, 2 errors

💡 Fix errors before deploying to GitHub Pages
```

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| **Broken internal link** | Check file path and extension (.md) |
| **Missing nav file** | Create the file or remove from nav |
| **Image not found** | Check path is relative to docs/ |
| **Build warning** | Usually safe to ignore, but review |
| **Orphaned page** | Add to navigation or delete if unused |

## Exit Codes

- `0` - No errors
- `1` - Errors found (broken links, missing files)
- `2` - Build failed

## See Also

- `/craft:docs:check-links` - Internal link validation (integrated)
- `/craft:site:build` - Build site locally
- `/craft:site:deploy` - Deploy to GitHub Pages
- `/craft:site:add` - Add Pages with Navigation Sync
- `/craft:site:audit` - Content Inventory & Audit
- `/craft:site:consolidate` - Merge Duplicate Content
- `/craft:site:create` - Full Documentation Site Wizard
- `/craft:site:nav` - Navigation Reorganization
- `/craft:site:progress` - Display comprehensive semester progress dashboard
- `/craft:site:publish` - Publish teaching site with preview workflow
- `/craft:site:status` - Documentation Site Dashboard
- `/craft:site:theme` - Quick Theme Changes
- Template: `templates/dry-run-pattern.md`
