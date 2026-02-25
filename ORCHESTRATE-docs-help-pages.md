# Orchestration: Docs Sub-Command Help Pages

**Branch:** `feature/docs-help-pages`
**Base:** `dev` @ `dbb37ea3`

---

## Overview

Create help pages for 14 missing `/craft:docs:*` sub-commands plus 3 `claude-md` sub-commands. Each help page lives in `docs/commands/docs/` and follows the established pattern from existing pages (check.md, update.md, etc.).

---

## Help Page Template

Every help page follows this structure (derived from existing pages):

```markdown
# /craft:docs:<name>

> **One-line description from command frontmatter**

---

## Synopsis

\`\`\`bash
/craft:docs:<name> [options]
\`\`\`

**Quick examples:**

\`\`\`bash
# 2-3 practical examples
\`\`\`

---

## Description

2-3 paragraphs explaining what the command does, when to use it, and its philosophy.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|

---

## What It Does / How It Works

Key behaviors, phases, or steps.

---

## See Also

- Links to related commands
```

Keep pages concise (40-80 lines). Extract info from the source command file in `commands/docs/`.

---

## Step 1: Simple Commands (6 pages)

Create help pages for the simplest commands first (< 300 lines source):

| File | Command | Source Lines |
|------|---------|-------------|
| `docs/commands/docs/api.md` | `/craft:docs:api` | 246 |
| `docs/commands/docs/help.md` | `/craft:docs:help` | 241 |
| `docs/commands/docs/quickstart.md` | `/craft:docs:quickstart` | 231 |
| `docs/commands/docs/nav-update.md` | `/craft:docs:nav-update` | 253 |
| `docs/commands/docs/prompt.md` | `/craft:docs:prompt` | 333 |
| `docs/commands/docs/site.md` | `/craft:docs:site` | 311 |

For each: read source `commands/docs/<name>.md`, extract description + options + examples, write help page.

**Commit:** `docs: add help pages for api, help, quickstart, nav-update, prompt, site`

---

## Step 2: Medium Commands (5 pages)

| File | Command | Source Lines |
|------|---------|-------------|
| `docs/commands/docs/tutorial.md` | `/craft:docs:tutorial` | 309 |
| `docs/commands/docs/workflow.md` | `/craft:docs:workflow` | 330 |
| `docs/commands/docs/guide.md` | `/craft:docs:guide` | 463 |
| `docs/commands/docs/mermaid.md` | `/craft:docs:mermaid` | 587 |
| `docs/commands/docs/lint.md` | `/craft:docs:lint` | 862 |

**Commit:** `docs: add help pages for tutorial, workflow, guide, mermaid, lint`

---

## Step 3: Complex Commands (3 pages)

| File | Command | Source Lines |
|------|---------|-------------|
| `docs/commands/docs/check-links.md` | `/craft:docs:check-links` | 705 |
| `docs/commands/docs/demo.md` | `/craft:docs:demo` | 1024 |
| `docs/commands/docs/website.md` | `/craft:docs:website` | 786 |

**Commit:** `docs: add help pages for check-links, demo, website`

---

## Step 4: Claude-MD Sub-Commands (3 pages)

Create `docs/commands/docs/claude-md/` directory with:

| File | Command | Source Lines |
|------|---------|-------------|
| `docs/commands/docs/claude-md/edit.md` | `/craft:docs:claude-md:edit` | 634 |
| `docs/commands/docs/claude-md/init.md` | `/craft:docs:claude-md:init` | 319 |
| `docs/commands/docs/claude-md/sync.md` | `/craft:docs:claude-md:sync` | 361 |

Note: `docs/commands/docs/claude-md.md` already exists as the hub page. These are leaf pages.

**Commit:** `docs: add help pages for claude-md edit, init, sync`

---

## Step 5: Update mkdocs.yml Navigation

Add all 17 new pages to the nav under the Docs Commands section.

Structure:

```yaml
- Docs Commands:
  - /craft:docs:update: commands/docs/update.md
  - /craft:docs:claude-md: commands/docs/claude-md.md
  - /craft:docs:claude-md:edit: commands/docs/claude-md/edit.md
  - /craft:docs:claude-md:init: commands/docs/claude-md/init.md
  - /craft:docs:claude-md:sync: commands/docs/claude-md/sync.md
  - /craft:docs:api: commands/docs/api.md
  - /craft:docs:changelog: commands/docs/changelog.md
  - /craft:docs:check: commands/docs/check.md
  - /craft:docs:check-links: commands/docs/check-links.md
  - /craft:docs:demo: commands/docs/demo.md
  - /craft:docs:guide: commands/docs/guide.md
  - /craft:docs:help: commands/docs/help.md
  - /craft:docs:lint: commands/docs/lint.md
  - /craft:docs:mermaid: commands/docs/mermaid.md
  - /craft:docs:nav-update: commands/docs/nav-update.md
  - /craft:docs:prompt: commands/docs/prompt.md
  - /craft:docs:quickstart: commands/docs/quickstart.md
  - /craft:docs:site: commands/docs/site.md
  - /craft:docs:sync: commands/docs/sync.md
  - /craft:docs:tutorial: commands/docs/tutorial.md
  - /craft:docs:website: commands/docs/website.md
  - /craft:docs:workflow: commands/docs/workflow.md
```

**Commit:** `docs: add all docs help pages to mkdocs.yml nav`

---

## Step 6: Update Docs Hub Page

Update `docs/commands/docs.md` (the docs category hub) with a complete table of all sub-commands and their help page links.

**Commit:** `docs: update docs hub page with complete sub-command listing`

---

## Step 7: Validation

1. `mkdocs build --strict` — no warnings
2. Check all new pages render correctly (no broken links)
3. Verify nav structure is correct
4. Run `python3 -m pytest tests/ -v` — all tests pass

**Commit:** (no commit — validation only)

---

## Summary

| Step | What | Files | Commit |
|------|------|-------|--------|
| 1 | Simple commands (6) | 6 new pages | `docs: add help pages for api, help, quickstart...` |
| 2 | Medium commands (5) | 5 new pages | `docs: add help pages for tutorial, workflow...` |
| 3 | Complex commands (3) | 3 new pages | `docs: add help pages for check-links, demo...` |
| 4 | Claude-MD sub-commands (3) | 3 new pages + dir | `docs: add help pages for claude-md...` |
| 5 | Nav update | mkdocs.yml | `docs: add all docs help pages to nav` |
| 6 | Hub page update | docs/commands/docs.md | `docs: update docs hub page` |
| 7 | Validation | — | (no commit) |

**Total:** 17 new help pages, 2 updated files (mkdocs.yml, docs.md)
