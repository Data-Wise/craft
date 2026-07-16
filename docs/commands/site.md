# Site Management Commands

> **TL;DR** (30 seconds)
>
> - **What:** 15 commands for complete documentation site lifecycle (build, update, deploy, check)
> - **Why:** Zero-to-deployed in minutes with smart automation
> - **How:** `/folio:site:build` to compile, `/folio:site:status` for health check
> - **Next:** Run `/folio:site:update` for content sync or `/craft:site:deploy` to publish

Full documentation site lifecycle management - 15 commands.

## When to Use What

| Scenario | Command | Why |
|----------|---------|-----|
| Already have mkdocs.yml, need to build | `/folio:site:build` | Compiles site without modifying config |
| Push to GitHub Pages | `/craft:site:deploy` | Build + deploy in one step |
| Content changed, update site | `/folio:site:update` | Sync code changes into site content |
| Check site health | `/folio:site:check` | Validate config, links, deploy readiness |

**Common confusion:**

- **build vs deploy** — `build` compiles locally; `deploy` builds AND pushes to GitHub Pages
- **update vs build** — `update` syncs content from code changes; `build` just compiles existing content

---

## Management Commands

### /folio:site:status

Dashboard and health check

### /folio:site:update

Update site content from code changes

### /folio:site:build

Build site

### /craft:site:deploy

Deploy to GitHub Pages

### /folio:site:check

Validate site configuration, broken links, and deployment readiness

```bash
/folio:site:check           # Full validation
/folio:site:check --links   # Links only
```

## Framework Support

### /craft:site:docs/frameworks

Show supported documentation frameworks and their features

```bash
/craft:site:docs/frameworks
```

**Supported:**

- MkDocs Material (default)
- Docusaurus
- VuePress
- Sphinx
