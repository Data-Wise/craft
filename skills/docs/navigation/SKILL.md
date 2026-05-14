---
name: nav-sync
description: This skill should be used when the user asks to "update nav", "sync mkdocs navigation", "add a doc page", "reorganize navigation", "fix orphan docs", or needs to keep mkdocs.yml in sync with the docs/ directory. Handles directory-driven nav updates, new-page scaffolding with auto-nav insertion, and ADHD-friendly nav reorganization (≤7 top-level sections, ≤3 nesting depth).
---

# nav-sync Skill

Keep mkdocs.yml navigation aligned with the docs/ directory: detect drift, scaffold new pages with auto-nav insertion, and reorganize for clarity.

## Scope and Consolidation Note

This skill consolidates three previously separate commands:

- `/craft:docs:nav-update` — directory-driven sync
- `/craft:site:add` — new page + auto-nav
- `/craft:site:nav` — reorganization (analyze, ADHD, apply, preview)

Historically `docs/*` commands targeted generic docs and `site/*` commands targeted the mkdocs site, but in practice all three operated on mkdocs.yml and `docs/`. Merging them under `skills/docs/navigation/` removes the artificial split and gives one entry point for every navigation concern. Page-content generation (templates) is still part of the "add" path; other doc-type generators (quickstart, tutorial, guide) live in sibling skills.

## When to Use

Trigger when the user wants to:

1. **Sync** — bring mkdocs.yml in line with the actual `docs/*.md` files (find missing entries, dead entries, orphans).
2. **Add** — create a new doc page and have it appear in the nav automatically.
3. **Reorganize** — restructure top-level sections, enforce ADHD-friendly limits, or consolidate clutter.

If the user only wants to *generate* content for an existing page, use a sibling skill (`docs-classifier`, `changelog-automation`, or one of the docs/* commands).

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `mode` | enum | `sync` (default), `add`, `reorganize` |
| `title` | string | Page title (for `add` mode) |
| `section` | string | Target section in nav (for `add` mode); empty = root |
| `type` | enum | Page template: `guide` (default), `reference`, `tutorial`, `concept`, `quick-start`, `refcard` |
| `strategy` | enum | For reorganize: `analyze` (default), `adhd`, `apply`, `preview` |
| `dry_run` | bool | Preview without writing |

## Mode 1 — Sync (Directory-Driven)

Diff `docs/**/*.md` against `mkdocs.yml`'s `nav:` block.

1. Enumerate doc files (`find docs/ -name '*.md' -type f`).
2. Parse current nav entries.
3. Classify each delta:
   - **Add**: file exists, not in nav → propose insertion in section matching parent directory.
   - **Remove**: nav entry, no file → propose deletion.
   - **Orphan**: file exists, not in nav, no obvious section → ask: add / move to `_drafts/` / delete / ignore.
4. Infer title from (in order): H1 in file, frontmatter `title:`, kebab→Title-Case filename.
5. Show the diff plan; require confirmation unless `dry_run`.
6. Write mkdocs.yml.

## Mode 2 — Add (Scaffold + Nav)

1. Resolve filename: lowercase + kebab-case of `title`, suffix `.md`.
2. Determine path: `docs/<section-slug>/<filename>` or `docs/<filename>` if no section.
3. Choose template by `type` (guide, reference, tutorial, concept, quick-start, refcard). Templates live in `templates/site/pages/`.
4. Write the new file.
5. Insert into nav under the section, appended at end (sections sort alphabetically within, unless explicit position requested).
6. If `--new-section` is requested, also create `docs/<section>/index.md` and add a new top-level entry.

Batch form: comma-separated `title` list produces N pages in one section.

## Mode 3 — Reorganize

Apply these ADHD-friendly limits:

| Constraint | Limit |
|------------|-------|
| Top-level sections | ≤ 7 |
| Nesting depth | ≤ 3 |
| Items per section | ≤ 8 |

Strategies:

- `analyze` — produce a proposal, save to `PROPOSAL-NAV-REORGANIZATION.md`.
- `adhd` — same, but fail if proposal still exceeds limits.
- `preview` — show diff only; write nothing.
- `apply` — read existing proposal file, diff against current nav, confirm, write mkdocs.yml, run `mkdocs build --strict` to validate.

Tiered template:

```yaml
nav:
  - Home: index.md
  - Get Started: { Quick Install, First Steps }
  - Reference Card: REFCARD.md
  - Features: ...
  - Integrations: ...
  - Reference: ...
  - Guides: ...
```

## Outputs

```
NAV SYNC RESULT
  + 4 entries added
  - 1 entry removed
  ~ 0 reorganized
File written: mkdocs.yml
Next: mkdocs serve  |  /craft:site:preview
```

Or, for `add`:

```
PAGE CREATED
  docs/getting-started/installation.md (template: guide-page)
  mkdocs.yml nav updated under "Getting Started"
```

## Title Inference & Section Detection

- **Title**: first H1 → frontmatter `title:` → kebab-to-Title-Case filename.
- **Section**: parent directory name, normalized to Title Case. Place alphabetically within section by default; explicit `--after FILE` overrides.

## Integration

**Complements:**

- `doc-classifier` — decides *what* docs are needed; this skill places them in nav.
- `changelog-automation` — detects feature boundaries that often trigger new pages.

**Used by:**

- `/craft:docs:check` — validates nav alignment as part of doc health.
- `/craft:site:build` — should run sync before build to avoid missing-page warnings.
- `/craft:docs:sync` — invokes nav-sync as a post-step after doc generation.

## Validation

After any write to `mkdocs.yml`:

```bash
mkdocs build --strict
```

Catches broken refs, missing files, and YAML parse errors. If validation fails, restore from `mkdocs.yml.bak` (write a backup before any modification).

## Notes / Open Questions

- **Backup strategy**: currently each source command handles this differently. Standardize on `mkdocs.yml.bak` written next to the file before any edit.
- **Section ordering**: should new sections be inserted by tier (Get Started → Features → Reference) or alphabetically? Default is tier-based, falling back to alphabetic for unknown sections.
- **Frontmatter awareness**: this skill currently doesn't write Quarto `_quarto.yml` or pkgdown `_pkgdown.yml`. If multi-framework support is needed, extract per-framework writers.
