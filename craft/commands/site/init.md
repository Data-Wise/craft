# /site-init - Initialize Documentation Site

You are a documentation site initialization assistant. Set up the appropriate documentation framework based on project type.

## Context Detection

First, detect project type:

```
Detection Rules:
1. DESCRIPTION file → R Package
2. pyproject.toml → Python Package
3. package.json → Node.js Project
4. Otherwise → Generic (use MkDocs)
```

## For R Packages

Offer two options:

```
📦 R PACKAGE DETECTED

Documentation options:

1. Quarto + altdoc (RECOMMENDED)
   • Modern, flexible
   • Supports vignettes as Quarto docs
   • GitHub Pages ready

2. pkgdown (Traditional)
   • Standard R package docs
   • roxygen2 integration
   • Widely used

Which would you like? (1/2)
```

### Option 1: Quarto + altdoc

```r
# Install altdoc if needed
install.packages("altdoc")

# Initialize
altdoc::setup_docs(tool = "quarto_website")
```

Creates:
- `_quarto.yml` - Site configuration
- `docs/` - Documentation directory
- Reference pages from roxygen2

### Option 2: pkgdown

```r
# Install pkgdown if needed
install.packages("pkgdown")

# Initialize
usethis::use_pkgdown()
pkgdown::build_site()
```

Creates:
- `_pkgdown.yml` - Site configuration
- `docs/` - Built site

## For Non-R Projects (Python, Node, Generic)

Use MkDocs with Material theme:

```
📖 MKDOCS SETUP

Creating documentation site with Material theme...
```

### Steps:

1. Create `mkdocs.yml`:
```yaml
site_name: [PROJECT_NAME]
site_description: [from package.json/pyproject.toml or ask]
site_url: https://[username].github.io/[repo]/

repo_name: [username]/[repo]
repo_url: https://github.com/[username]/[repo]

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - search.suggest
    - content.code.copy

plugins:
  - search

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
  - tables

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - Guide:
    - Overview: guide/overview.md
  - Reference:
    - API: reference/api.md
```

2. Create directory structure:
```
docs/
├── index.md
├── getting-started/
│   ├── installation.md
│   └── quickstart.md
├── guide/
│   └── overview.md
└── reference/
    └── api.md
```

3. Create `requirements.txt` (add to existing or create):
```
mkdocs-material>=9.0
```

4. Create `.github/workflows/docs.yml`:
```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
permissions:
  contents: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: 3.x
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

## Output

```
✅ DOCUMENTATION SITE INITIALIZED

Created:
• [config file] - Site configuration
• docs/ - Documentation directory
• [workflow] - GitHub Pages deployment

Next steps:
1. Edit docs/index.md with your content
2. Preview: /site-preview
3. Build: /site-build
4. Deploy: /site-deploy

💡 Run /site-preview to see your site locally
```
