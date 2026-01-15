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

```
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
│ 📊 Summary: 3 validation checks on ~450 files                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only command, so dry-run mainly shows what will be checked.

## Checks Performed

### 1. Link Validation

Check for broken links:
- **Internal links** - References to other docs
- **External links** - URLs (if --strict mode)
- **Anchor links** - #sections within pages

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

```
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

- `/craft:site:build` - Build site locally
- `/craft:site:deploy` - Deploy to GitHub Pages
- Template: `templates/dry-run-pattern.md`
