# /craft:docs:site - Website Documentation Focus

You are a documentation site specialist. Update all website-related docs and optionally deploy.

## Purpose

**Focused updates for documentation websites (MkDocs, Docusaurus, etc.):**

- Update all files in docs/ directory
- Ensure navigation is current
- Validate site structure
- Preview and deploy

## Usage

```bash
/craft:docs:site              # Update website docs
/craft:docs:site --preview    # Update + preview locally
/craft:docs:site --deploy     # Update + deploy to GitHub Pages
/craft:docs:site --validate   # Only validate, no updates
```

## When Invoked

### Step 1: Detect Documentation Framework

```bash
# Check for mkdocs
ls mkdocs.yml 2>/dev/null && echo "MkDocs detected"

# Check for docusaurus
ls docusaurus.config.js 2>/dev/null && echo "Docusaurus detected"

# Check for vitepress
ls .vitepress/config.js 2>/dev/null && echo "VitePress detected"

# Check for generic docs/
ls docs/index.md 2>/dev/null && echo "Generic docs/ detected"
```

### Step 2: Analyze Current State

```bash
# Check for orphan files (not in nav)
find docs/ -name "*.md" -type f

# Check nav configuration
cat mkdocs.yml | grep -A 100 "nav:"

# Check for broken internal links
grep -r "\]\(\./" docs/
```

### Step 3: Show Update Plan

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:site                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📚 DOCUMENTATION SITE UPDATE                                │
│                                                             │
│ Framework: MkDocs (Material theme)                          │
│ Docs directory: docs/                                       │
│ Config: mkdocs.yml                                          │
│                                                             │
│ Current state:                                              │
│   • 24 documentation files                                  │
│   • 3 orphan files (not in nav)                             │
│   • 0 broken internal links                                 │
│   • Last build: 3 days ago                                  │
│                                                             │
│ Will update:                                                │
│   ✓ docs/index.md (badges, overview)                        │
│   ✓ docs/REFCARD.md (quick reference)                       │
│   ✓ docs/QUICK-START.md (installation)                      │
│   ✓ docs/getting-started/* (setup guides)                   │
│   ✓ docs/guide/* (feature guides)                           │
│   ✓ docs/reference/* (commands, config, refcards)           │
│   ✓ mkdocs.yml (add 3 orphan files to nav)                  │
│                                                             │
│ Proceed? (y/n)                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Execute Updates

#### 4.1 Index Page (docs/index.md)

Update:

- Version badges
- Feature highlights
- Quick links
- Recent changes summary

#### 4.2 Quick Start (docs/QUICK-START.md)

Update:

- Installation instructions
- First-run examples
- Verification steps

#### 4.3 Reference Card (docs/REFCARD.md)

Update:

- All commands quick reference
- Common workflows
- Troubleshooting shortcuts

#### 4.4 Getting Started Section

Update:

- Installation guides
- Configuration guides
- First steps tutorials

#### 4.5 Guide Section

Update:

- Feature guides
- Workflow documentation
- Best practices

#### 4.6 Reference Section

Update:

- Commands reference
- Configuration reference
- API reference (if applicable)
- Domain-specific REFCARDs

#### 4.7 Navigation (mkdocs.yml)

```yaml
nav:
  - Home: index.md
  - Quick Start: QUICK-START.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Configuration: getting-started/configuration.md
  - Guide:
    - Overview: guide/overview.md
    - Sessions: guide/sessions.md           # NEW
    - Workflows: guide/workflows.md
  - Reference:
    - Commands: reference/commands.md
    - REFCARD: REFCARD.md
    - REFCARD-SESSIONS: reference/REFCARD-SESSIONS.md  # NEW
    - Configuration: reference/configuration.md
  - Troubleshooting: troubleshooting.md
```

### Step 5: Validation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 SITE VALIDATION                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Structure:                                                  │
│   ✓ All files in navigation                                 │
│   ✓ No orphan files                                         │
│   ✓ Consistent structure                                    │
│                                                             │
│ Links:                                                      │
│   ✓ 156 internal links valid                                │
│   ✓ No broken references                                    │
│                                                             │
│ Content:                                                    │
│   ✓ All pages have titles                                   │
│   ✓ No empty files                                          │
│   ⚠️ 2 pages without descriptions (SEO)                     │
│                                                             │
│ Warnings:                                                   │
│   • docs/guide/advanced.md - No meta description            │
│   • docs/reference/api.md - No meta description             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 6: Preview (with --preview)

```bash
# Start local preview server
mkdocs serve --dev-addr localhost:8000
```

```
┌─────────────────────────────────────────────────────────────┐
│ 🌐 SITE PREVIEW                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Preview server running:                                     │
│   → http://localhost:8000                                   │
│                                                             │
│ Press Ctrl+C to stop                                        │
│                                                             │
│ After review:                                               │
│   → Deploy: /craft:docs:site --deploy                       │
│   → Or: mkdocs gh-deploy                                    │
└─────────────────────────────────────────────────────────────┘
```

### Step 7: Deploy (with --deploy)

```bash
# Build and deploy to GitHub Pages
mkdocs gh-deploy --force
```

```
┌─────────────────────────────────────────────────────────────┐
│ 🚀 SITE DEPLOYED                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Deployed to GitHub Pages:                                   │
│   → https://data-wise.github.io/aiterm/                     │
│                                                             │
│ Changes:                                                    │
│   • 8 pages updated                                         │
│   • 2 new pages added                                       │
│   • Navigation restructured                                 │
│                                                             │
│ Deployment commit:                                          │
│   abc1234 (gh-pages branch)                                 │
│                                                             │
│ Live in: ~2-3 minutes                                       │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Updated

| Target | Updated | Notes |
|--------|---------|-------|
| docs/index.md | Always | Badges, overview |
| docs/REFCARD.md | Always | Quick reference |
| docs/QUICK-START.md | Always | Installation |
| docs/getting-started/* | Always | Setup guides |
| docs/guide/* | If changed | Feature guides |
| docs/reference/* | If changed | Commands, config |
| docs/api/* | If API changed | API documentation |
| docs/troubleshooting/* | If issues changed | Known issues |
| mkdocs.yml | Always | Navigation |

## Framework Support

### MkDocs (Primary)

```yaml
# mkdocs.yml
site_name: AITerm
theme:
  name: material
nav:
  - ...
```

### Docusaurus (Future)

```javascript
// docusaurus.config.js
module.exports = {
  title: 'AITerm',
  themeConfig: { ... }
}
```

### VitePress (Future)

```javascript
// .vitepress/config.js
export default {
  title: 'AITerm',
  themeConfig: { ... }
}
```

## ADHD-Friendly Features

1. **Single command** - All website docs in one go
2. **Orphan detection** - Find forgotten files
3. **Validation included** - Catch issues before deploy
4. **Preview option** - See before publishing
5. **Deploy option** - One command to publish

## Integration

This command focuses on **website docs only**. It:

- Calls `/craft:docs:nav-update` for navigation
- Calls `/craft:docs:validate` for link checking
- Calls `/craft:site:deploy` for deployment (if --deploy)

**Related commands:**

- `/craft:docs:update` - All docs including non-website
- `/craft:docs:feature` - After adding features
- `/craft:site:preview` - Just preview, no updates
- `/craft:site:deploy` - Just deploy, no updates
