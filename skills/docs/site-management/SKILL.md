---
name: site-lifecycle
description: This skill should be used when the user asks to "set up a docs site", "build the site", "preview docs locally", "deploy docs", "publish the site", "audit site content", "change site theme", "check site health", "show site status", or otherwise manages the lifecycle of a documentation site (MkDocs, Quarto, pkgdown). Covers init/create/theme through build/preview/audit through deploy/publish/update.
---

# Site Lifecycle

End-to-end management of a project's documentation site — from initial scaffold through daily build/preview to deploy/publish — across MkDocs, Quarto, and pkgdown.

## When to Use

- Standing up a new docs site (init, full wizard, theme pick)
- Daily authoring: build, preview locally, check for broken links, audit content
- Releasing docs: deploy to GitHub Pages, publish a teaching site (draft → production), update after code changes
- Surveying state: site dashboard, semester progress for teaching projects, content inventory

## Out of Scope (use other skills/commands)

| Task | Where |
|------|-------|
| Add a single page + sync nav | `skills/docs/navigation/` |
| Reorganize `mkdocs.yml` nav tree | `skills/docs/navigation/` |
| Classify what docs a feature needs | `skills/docs/doc-classifier/` |
| Release pipeline (incl. `mkdocs gh-deploy`) | `skills/release/` (calls deploy as Step 9) |
| Changelog generation | `skills/docs/changelog-automation/` |
| CLAUDE.md lifecycle | `skills/docs/claude-md/` |

**Overlap with `release` skill:** `release` invokes `mkdocs gh-deploy` as part of its full pipeline (Step 9). This skill handles deploy/publish **standalone** — when the user wants to ship docs changes without a version bump. If the user says "release v2.X" or "ship it", route to `release` instead.

## Framework Detection

Detect the site framework before any operation:

| Signal | Framework | Build cmd | Preview cmd | Deploy cmd |
|--------|-----------|-----------|-------------|------------|
| `mkdocs.yml` | MkDocs | `mkdocs build` | `mkdocs serve` | `mkdocs gh-deploy` |
| `_quarto.yml` | Quarto | `quarto render` | `quarto preview` | `quarto publish gh-pages` |
| `_pkgdown.yml` / `pkgdown/` | pkgdown (R) | `pkgdown::build_site()` | `pkgdown::preview_site()` | `pkgdown::deploy_to_branch()` |
| Teaching profile (`docs/teach-config.yml`) | MkDocs + teaching mode | adds week/lecture rendering | — | adds draft→production workflow |

For framework comparison / picking one, see reference: `commands/site/docs/frameworks.md` (long-form).

## Lifecycle Phases

```text
Phase 1: SETUP        Phase 2: AUTHOR             Phase 3: SHIP
─────────────         ─────────────               ─────────────
init                  build                       deploy
create  (wizard)      preview                     publish (teaching)
theme                 check   (link/health)       update  (post-code-change)
                      audit   (content inventory)
                      status  (dashboard)
                      progress (semester)
                      consolidate (merge dupes)
```

Pick the phase from the user's intent, then the operation within it.

## Phase 1 — Setup

### init — Initialize site

Idempotent scaffold of a new site. Detects existing config; refuses to overwrite without `--force`.

```bash
# MkDocs default
mkdir -p docs && cat > mkdocs.yml <<EOF
site_name: <project>
theme: { name: material }
nav: [ Home: index.md ]
EOF
mkdocs build  # smoke test
```

For Quarto/pkgdown, use the framework's native init (`quarto create-project`, `usethis::use_pkgdown()`).

### create — Full wizard

Interactive site scaffold with theme choice, nav structure, plugin selection, and CI workflow. Heavier than `init` — use when starting from zero with no preferences yet.

### theme — Quick theme change

Mutate `theme:` block in `mkdocs.yml` (or equivalent) without touching content. Common changes:

| Change | mkdocs.yml mutation |
|--------|---------------------|
| Switch to Material | `theme.name: material` |
| Add dark mode toggle | `theme.palette: [{ scheme: default }, { scheme: slate }]` |
| Custom colors | `theme.palette.primary: <color>` |

Validate with `mkdocs build --strict` after edit.

## Phase 2 — Author

### build — Build site

```bash
# MkDocs
mkdocs build --strict   # --strict fails on warnings (broken links, etc.)

# Quarto
quarto render

# pkgdown
Rscript -e 'pkgdown::build_site()'
```

Teaching mode: also processes week directories and lecture YAML.

**Common failures:** YAML syntax (unquoted `:` in values — see `mkdocs.yml` gotcha), missing nav targets, broken includes.

### preview — Local preview

```bash
mkdocs serve            # http://127.0.0.1:8000, hot-reload
quarto preview          # similar
```

Use when iterating on content. Kill any stale servers first (`lsof -ti:8000 | xargs kill`).

### check — Validation & link health

Runs broken-link detection + common-issue checks without a full build:

- Internal anchor resolution (MkDocs vs markdownlint anchor slug disagreement — replace `&` with `and` in headings)
- External link reachability (sampled)
- Orphaned pages (in `docs/` but absent from nav)
- Image references resolve

Cheaper than `audit`; run before every commit that touches docs.

### audit — Content inventory

Catalogs every page in the site with: word count, last-modified, nav position, outbound link count, headings outline. Used to find:

- Stale pages (not touched in N months)
- Duplicate content (candidates for `consolidate`)
- Orphans (in repo, not in nav)
- Coverage gaps (commands without docs)

Output: a structured table + suggested actions.

### consolidate — Merge duplicate content

When `audit` flags duplicates, this operation merges them: picks a canonical page, redirects others, updates inbound links, removes the redundant files. Always preview the change set; merging is hard to reverse.

### status — Site dashboard

Real-time snapshot:

- Framework + version
- Page count, last build timestamp, last deploy timestamp
- Open broken-link count (from last `check`)
- Live URL + HTTP status
- CI workflow status for docs deploy

### progress — Semester progress (teaching)

Teaching-mode only. Reads `docs/teach-config.yml` and computes:

- Current week / total weeks
- Lectures rendered vs. planned
- Assignment release schedule
- Material due dates

Output `--json` for scripting; default is a visual dashboard.

## Phase 3 — Ship

### deploy — Deploy to GitHub Pages

```bash
mkdocs gh-deploy --force      # pushes site/ to gh-pages branch
quarto publish gh-pages
Rscript -e 'pkgdown::deploy_to_branch()'
```

Pre-flight:

- Build must pass with `--strict`
- gh-pages branch exists, or this is the first deploy
- GitHub Pages enabled in repo settings (`gh api repos/:owner/:repo/pages`)

Post-deploy:

- Wait 30–60s for CDN propagation
- Verify live URL returns 200 and shows new content
- If site has `version` in footer, grep the live HTML for it (see `release` skill's Step 13c pattern)

**When `release` is in flight:** Do NOT run standalone deploy. The release pipeline owns this step.

### publish — Teaching site draft → production

Two-stage workflow for teaching sites:

1. **Draft**: render to a preview branch (`gh-pages-draft`) — instructor reviews
2. **Promote**: merge draft → `gh-pages` (production)

Optional `--skip-validation` flag bypasses teaching content checks (YAML schema, week manifest, lesson plans). Default validates.

Use this instead of plain `deploy` for `scholar`-style course sites.

### update — Post-code-change update

**Dev-branch staleness warning (H3, SPEC-docs-site-hardening-consolidation-2026-07-02):** deploy is `main`-gated (`docs.yml` triggers only on push to `main`). If the current branch is not `main`, warn before making changes:

```text
⚠️  Changes made now won't reach the live site until the next dev→main release.
    Preview locally instead: mkdocs serve
```

This kills the false-green failure mode where `update` reports success locally but the live site never changes.

When code changes and docs may drift, this operation:

1. Detects what changed (git diff vs last deploy tag)
2. Classifies impact (uses `skills/docs/doc-classifier/` if available)
3. Updates affected docs: API refs, command tables, count badges (commands/skills/agents totals), CHANGELOG cross-refs
4. Modes: `smart` (only changed surfaces) or `full` (regenerate everything)

Run after merging a feature PR, before the next release.

## Common Workflows

### "I just merged a feature, prep docs for release"

1. `update --mode smart` — refresh changed surfaces
2. `check` — verify no broken links
3. (commit changes on dev)
4. Defer deploy to `release` skill

### "Docs only fix, ship it"

1. `build --strict` — confirm clean
2. `check` — link health
3. `deploy` — straight to gh-pages (no version bump)
4. Verify live URL

### "Starting a new project"

1. `create` (wizard) or `init` + `theme`
2. Add `gh-pages` branch protection
3. First `deploy` to seed the site

### "Site feels bloated"

1. `audit` — find dupes, orphans, stale
2. `consolidate` — merge dupes
3. Manual: delete orphans, prune stale
4. `check` + `build --strict` to confirm nothing broke

## Inputs

| Input | Type | Notes |
|-------|------|-------|
| `framework` | enum | `mkdocs` \| `quarto` \| `pkgdown` (auto-detect by default) |
| `mode` | enum | For `update`: `smart` \| `full` |
| `dry_run` | bool | Preview without writing (supported by `build`, `check`, `deploy`, `update`, `publish`) |
| `skip_validation` | bool | `publish` only — skip teaching content checks |
| `week` | int | `progress` only — override current week |

## Constraints & Gotchas

- **MkDocs YAML `:` gotcha**: quote any value containing `:` (e.g., `site_description: "Latest: v2.34.0"`). Unquoted, YAML parses it as a nested mapping.
- **Anchor slug disagreement**: markdownlint (MD051) and MkDocs disagree on `&` handling. Replace `&` with `and` in headings; use `&` in display text only.
- **Nested code fences**: outer fences with inner triple-backticks confuse MkDocs. Use 4-backtick outer fences when nesting.
- **Strict mode is the contract**: always build with `--strict` in CI; warnings become errors.
- **gh-deploy is destructive on gh-pages**: never run from a stale local checkout — pull first.
- **Teaching publish has its own branch**: don't deploy a draft directly to `gh-pages`; use `publish` to stage via `gh-pages-draft`.

## Reference

- Framework comparison: `commands/site/docs/frameworks.md`
- Release pipeline integration: `skills/release/SKILL.md` (Step 9, Step 13a)
- Navigation operations: `skills/docs/navigation/SKILL.md`
- Doc impact classification: `skills/docs/doc-classifier/SKILL.md`

## Deprecates

This skill consolidates the following commands (kept functional through one minor release, removed in v3.0.0):

`/craft:site:init`, `/craft:site:create`, `/craft:site:theme`, `/craft:site:build`, `/craft:site:preview`, `/craft:site:check`, `/craft:site:audit`, `/craft:site:consolidate`, `/craft:site:status`, `/craft:site:progress`, `/craft:site:deploy`, `/craft:site:publish`, `/craft:site:update`.

Excluded (own skill): `/craft:site:add`, `/craft:site:nav` → `skills/docs/navigation/`.
