# /craft:docs:site

> **Update all website-related documentation and optionally deploy**

---

## Synopsis

```bash
/craft:docs:site [options]
```

**Quick examples:**

```bash
# Update all website docs
/craft:docs:site

# Update and preview locally
/craft:docs:site --preview

# Validate site structure without making changes
/craft:docs:site --validate
```

---

## Description

Performs a focused update of all documentation website content in a single pass. Detects the documentation framework (MkDocs, Docusaurus, VitePress), analyzes the current state of `docs/`, and updates pages, navigation, and site configuration.

The command handles index pages, quick-start guides, reference cards, getting-started sections, feature guides, and command references. It also detects orphan files not included in navigation and validates internal links.

Use `--preview` to start a local server after updates, or `--deploy` to publish directly to GitHub Pages.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--preview` | Start local preview server after updates | `false` |
| `--deploy` | Build and deploy to GitHub Pages after updates | `false` |
| `--validate` | Only validate site structure, no updates | `false` |

---

## How It Works

1. **Detect framework** — Checks for `mkdocs.yml`, `docusaurus.config.js`, or `.vitepress/config.js`.
2. **Analyze state** — Counts doc files, finds orphans not in nav, checks for broken internal links.
3. **Show update plan** — Displays which files will be updated and prompts for confirmation.
4. **Execute updates** — Updates index, quick-start, reference cards, guides, and navigation.
5. **Validate** — Checks structure, links, and content (titles, empty files, meta descriptions).
6. **Preview/Deploy** — Optionally serves locally or deploys via `mkdocs gh-deploy`.

### What Gets Updated

| Target | When | Notes |
|--------|------|-------|
| `docs/index.md` | Always | Badges, overview |
| `docs/REFCARD.md` | Always | Quick reference |
| `docs/QUICK-START.md` | Always | Installation |
| `docs/getting-started/*` | Always | Setup guides |
| `docs/guide/*` | If changed | Feature guides |
| `docs/reference/*` | If changed | Commands, config |
| `mkdocs.yml` | Always | Navigation |

---

## See Also

- [/craft:docs:nav-update](nav-update.md) — Update navigation from directory structure
- [/craft:docs:check](check.md) — Full documentation health check
- [/craft:docs:update](update.md) — Update all docs including non-website
