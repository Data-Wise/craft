# /site-build - Build Documentation Site

You are a documentation build assistant. Build the static site based on project type.

## Context Detection

Detect documentation type:

```
Detection Rules:
1. _quarto.yml exists → Quarto site
2. _pkgdown.yml exists → pkgdown site
3. mkdocs.yml exists → MkDocs site
4. No config found → Error
```

## For Quarto Sites

```bash
quarto render
```

Output directory: `_site/` or `docs/` (check `_quarto.yml`)

## For pkgdown Sites

```r
pkgdown::build_site()
```

Output directory: `docs/`

## For MkDocs Sites

```bash
mkdocs build
```

Output directory: `site/`

## Output

```
✅ SITE BUILT SUCCESSFULLY

Type: [Quarto/pkgdown/MkDocs]
Output: [output directory]
Files: [count] files generated

Next steps:
• Preview locally: /site-preview
• Deploy to GitHub Pages: /site-deploy
• Check for issues: /site-check
```

## Error Handling

If build fails:
1. Show the error message
2. Suggest common fixes
3. Offer to help debug

Common issues:
- Missing dependencies
- Broken links
- Invalid YAML
- Missing referenced files
