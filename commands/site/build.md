---
description: Build documentation site (Quarto, pkgdown, MkDocs)
category: site
arguments:
  - name: dry-run
    description: Preview build configuration without building
    required: false
    default: false
    alias: -n
---

# /craft:site:build - Build Documentation Site

Build static documentation sites based on detected project type.

## Usage

```bash
# Preview build plan
/craft:site:build --dry-run
/craft:site:build -n

# Build site
/craft:site:build
```

## Dry-Run Output

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Build Documentation Site                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Type: MkDocs                                              │
│   - Config: mkdocs.yml                                        │
│   - Theme: material                                           │
│                                                               │
│ ✓ Build Plan:                                                 │
│   - Command: mkdocs build                                     │
│   - Output directory: site/                                   │
│   - Estimated files: ~450                                     │
│   - Estimated size: ~2.3 MB                                   │
│                                                               │
│ 📊 Summary: Build MkDocs site to site/ directory               │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Context Detection

Automatically detects documentation type:

| File | Type | Build Command |
|------|------|---------------|
| `mkdocs.yml` | MkDocs | `mkdocs build` |
| `_quarto.yml` | Quarto | `quarto render` |
| `_pkgdown.yml` | pkgdown | `pkgdown::build_site()` |

## Build Process

### MkDocs

```bash
mkdocs build
```

**Output**: `site/` directory

### Quarto

```bash
quarto render
```

**Output**: `_site/` or `docs/` (check `_quarto.yml`)

### pkgdown

```r
pkgdown::build_site()
```

**Output**: `docs/` directory

## Output

```
✅ SITE BUILT SUCCESSFULLY

Type: MkDocs
Output: site/
Files: 450 files generated
Size: 2.3 MB

Next steps:
• Preview locally: /craft:site:preview
• Deploy to GitHub Pages: /craft:site:deploy
• Check for issues: /craft:site:check
```

## Error Handling

If build fails:
1. Show the error message
2. Suggest common fixes
3. Offer to help debug

**Common issues:**
- Missing dependencies
- Broken links
- Invalid YAML
- Missing referenced files

## See Also

- `/craft:site:deploy` - Deploy to GitHub Pages
- `/craft:site:check` - Check site for issues
- Template: `templates/dry-run-pattern.md`
