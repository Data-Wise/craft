# /site-check - Validate Documentation

You are a documentation validation assistant. Check the documentation site for common issues.

## Checks Performed

### 1. Link Validation

Check for broken links:
- Internal links (references to other docs)
- External links (URLs)
- Anchor links (#sections)

### 2. Spelling Check

Common misspellings in technical docs.

### 3. Structure Validation

- All nav items have corresponding files
- No orphaned pages (not in nav)
- Images exist and are referenced

### 4. Build Test

- Can the site build without errors?
- Any warnings?

## For MkDocs Sites

```bash
# Check links (if linkchecker installed)
linkchecker http://localhost:8000

# Or use mkdocs strict mode
mkdocs build --strict
```

## For pkgdown Sites

```r
# Check for issues
pkgdown::check_pkgdown()
```

## For Quarto Sites

```bash
# Build with strict mode
quarto render --strict
```

## Output

```
📋 DOCUMENTATION VALIDATION REPORT

Site Type: [type]

✅ PASSED:
• Build: No errors
• Links: All internal links valid
• Structure: All nav items have files

⚠️ WARNINGS:
• [warning 1]
• [warning 2]

❌ ERRORS:
• Broken link: docs/guide.md → missing.md
• Missing file: docs/api.md (referenced in nav)

SUMMARY: [X] passed, [Y] warnings, [Z] errors

💡 Fix errors before deploying
```

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Broken internal link | Check file path and extension |
| Missing nav file | Create the file or remove from nav |
| Image not found | Check path is relative to docs/ |
| Build warning | Usually safe to ignore, but review |
