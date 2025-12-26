# /site-preview - Preview Documentation Locally

You are a documentation preview assistant. Start a local server to preview the documentation site.

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
quarto preview
```

Default URL: http://localhost:4000 (or similar)

## For pkgdown Sites

```r
pkgdown::preview_site()
```

Or serve the `docs/` directory.

## For MkDocs Sites

```bash
mkdocs serve
```

Default URL: http://127.0.0.1:8000

## Output

```
🌐 PREVIEW SERVER STARTED

Type: [Quarto/pkgdown/MkDocs]
URL: http://localhost:[port]

The server will auto-reload when you edit files.

Press Ctrl+C to stop the server.

💡 Open in browser: open http://localhost:[port]
```

## Quick Reference

| Type | Command | Default Port |
|------|---------|--------------|
| Quarto | `quarto preview` | 4000 |
| pkgdown | `pkgdown::preview_site()` | 8080 |
| MkDocs | `mkdocs serve` | 8000 |
