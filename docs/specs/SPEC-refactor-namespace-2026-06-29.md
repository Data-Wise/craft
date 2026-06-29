# craft: Namespace Refactoring Spec

**Date:** 2026-06-29
**Status:** Planning
**Source initiative:** opencode-resources `docs/specs/SPEC-plugin-refactoring-2026-06-29.md`
**Sets schema for:** savant, rforge, scholar (use this as the template)

---

## Context

craft has 117 commands organized in directories with a Python `_discovery.py` layer that
dynamically discovers and caches command metadata into `_cache.json`. This dynamic discovery
creates friction: stale caches, Python dependency, runtime filesystem scanning.

The opencode NL Namespace demonstrated that a **static `namespace.json` index** — one JSON file
listing all commands with their descriptions and file paths — eliminates discovery overhead
while making the command surface instantly readable by both AI and humans.

This spec adds `namespace.json` as a static index **alongside** the existing `.md` files.
The `.md` files stay as the authoritative content source; the JSON index is the discovery
and routing layer.

---

## Current Command Inventory (by category)

| Category | Count | Sub-commands |
|----------|-------|-------------|
| `arch` | 4 | analyze, diagram, plan, review |
| `check` | 2 | (top-level) + gen-validator |
| `ci` | 6 | detect, generate, status, triage, validate, watch |
| `code` | 16 | ci-fix, ci-local, command-audit, coverage, debug, demo, deps-audit, deps-check, desktop-watch, docs-check, fewer-prompts, lint, refactor, release, release-watch, skill-standards, test-gen |
| `dist` | 5 | curl-install, homebrew, marketplace, pypi, surfaces |
| `docs` | 17 | api, changelog, check-links, check, demo, guide, help, lint, mermaid, nav-update, prompt, quickstart, site, sync, tutorial, update, website, workflow |
| `git` | 11 | branch, clean, git-recap, guard, init, protect-baseline, protect, status, sync, unprotect, worktree |
| `orchestrate` | 5 | (top-level) + drive, plan, resume, workflow |
| `plan` | 3 | feature, roadmap, sprint |
| `site` | 15 | add, audit, build, check, consolidate, create, deploy, init, nav, preview, progress, publish, status, theme, update |
| `utils` | 2 | readme-semester-progress, readme-teach-config |
| `workflow` | 14 | adhd-guide, brainstorm, brief, done, focus, insights, next, recap, refine, spec-review, stuck, task-cancel, task-output, task-status |
| **Flat** | 8 | check, do, grill, hub, orchestrate, quota, smart-help, test |

**Total:** ~117 commands

---

## Problems Identified

### Structural Bloat

- `docs` has **17 commands** — more than all of opencode combined. Many overlap:
  `check-links` ↔ `check`, `demo` ↔ `guide`, `site` ↔ `website`, `update` ↔ `sync`
- `site` has **15 commands** — overlapping: `create` ↔ `init`, `build` ↔ `deploy`, `check` ↔ `audit`
- Both create sub-action inflation; opencode's `/docs` handles this with `init|sync|check` sub-actions

### Routing Ambiguity

- `check.md` AND `check/gen-validator.md` — flat and directory both named `check`
- `orchestrate.md` AND `orchestrate/` directory — same naming collision
- These create discovery failures when the JSON index can't differentiate

### Misplaced Commands

- `code/release.md` and `code/release-watch.md` live under `code/` but logically belong to
  a `release` category (or the top-level `dist/` category)
- `utils/readme-semester-progress.md` and `utils/readme-teach-config.md` are teaching artifacts
  that belong in scholar, not craft

### Dynamic Discovery Overhead

- `_discovery.py` scans the filesystem on every session, caches to `_cache.json`
- Cache staleness: a renamed file leaves a ghost entry
- Python dependency: not needed for a static listing
- No human-readable index: contributors must run the discovery script to see the full surface

### Cross-repo Duplicates (vs opencode/savant/scholar)

- `workflow/brainstorm` ↔ opencode `/brainstorm` — separate implementations, same purpose
- `workflow/done` ↔ opencode `/done` — separate implementations
- `workflow/next` ↔ opencode `/next` — same pattern, different depth
- `grill.md` ↔ opencode `/grill` — craft version, opencode version — opportunity to align
- `workflow/refine` ↔ opencode `/refine` — duplicated

---

## Proposed Consolidations

### `docs`: 17 → 5 with sub-actions

New structure: `/craft:docs <sub-action>`

| Sub-action | Replaces | Notes |
|------------|---------|-------|
| `init` | `docs/guide.md`, `docs/quickstart.md`, `docs/website.md` | Scaffold docs for a project type |
| `sync` | `docs/update.md`, `docs/sync.md`, `docs/nav-update.md`, `docs/changelog.md` | Pull latest, update nav, changelog |
| `check` | `docs/check.md`, `docs/check-links.md`, `docs/lint.md` | Validation: links, lint, coverage |
| `generate` | `docs/api.md`, `docs/guide.md`, `docs/tutorial.md`, `docs/prompt.md` | Content generation |
| `publish` | `docs/site.md`, `docs/mermaid.md`, `docs/demo.md`, `docs/workflow.md` | Build/deploy/preview |

Archive candidates (rarely used): `docs/help.md` (superseded by `hub.md`),
`docs/desktop-watch` (is this docs or code?), `docs/demo.md` (covered by publish sub-action)

### `site`: 15 → 4 with sub-actions

New structure: `/craft:site <sub-action>`

| Sub-action | Replaces |
|------------|---------|
| `init` | `site/create.md`, `site/init.md`, `site/add.md` |
| `build` | `site/build.md`, `site/deploy.md`, `site/publish.md` |
| `check` | `site/check.md`, `site/audit.md`, `site/status.md` |
| `manage` | `site/nav.md`, `site/theme.md`, `site/consolidate.md`, `site/update.md`, `site/progress.md`, `site/preview.md` |

### `code/release*` → `dist`

Move `code/release.md` and `code/release-watch.md` to `dist/release.md` and `dist/watch.md`.
Rationale: release is a distribution concern, not a code concern.

### `check` disambiguation

Rename `check.md` → `code/check.md` (it's a code quality check).
`check/gen-validator.md` becomes `code/gen-validator.md`.
Eliminates flat/directory collision.

### `orchestrate` disambiguation

`orchestrate.md` becomes the top-level routing entry.
`orchestrate/drive.md`, `orchestrate/plan.md`, etc. become sub-actions routed from
the top-level command. Namespace entry: `"orchestrate:drive"`, `"orchestrate:plan"`, etc.

### `utils` → scholar

`utils/readme-semester-progress.md` and `utils/readme-teach-config.md` → migrate to scholar.
`utils/` directory removed from craft after migration.

---

## Workstream A: Namespace + Routing

### namespace.json schema (craft's authoritative schema)

```json
{
  "do": {
    "description": "Universal NL dispatcher — route any request to the right command",
    "file": "do.md",
    "category": "flat"
  },
  "grill": {
    "description": "Convergent interrogation — stress-test a spec/plan before implementing",
    "file": "grill.md",
    "category": "flat"
  },
  "hub": {
    "description": "Command discovery and prompt engineering — find the right command",
    "file": "hub.md",
    "category": "flat"
  },
  "orchestrate": {
    "description": "Multi-agent orchestration — drive, plan, resume complex workflows",
    "file": "orchestrate.md",
    "category": "flat",
    "routes": {
      "drive": "orchestrate/drive.md",
      "plan": "orchestrate/plan.md",
      "resume": "orchestrate/resume.md",
      "workflow": "orchestrate/workflow.md"
    }
  },
  "git:worktree": {
    "description": "Create, list, finish, or clean git worktrees with .STATUS scaffolding",
    "file": "git/worktree.md",
    "category": "git"
  },
  "docs:init": {
    "description": "Scaffold documentation for a project type",
    "file": "docs/init.md",
    "category": "docs"
  }
}
```

Full namespace.json (all 117 entries) is generated by running:

```bash
node scripts/build-namespace.js > commands/namespace.json
```

`build-namespace.js` replaces `_discovery.py`. It reads the filesystem once (no cache),
outputs a static JSON, and exits. CI validates it via `node scripts/check-drift.js`.

### Routing changes

| Old routing | New routing |
|------------|------------|
| `/craft:check` (ambiguous) | `/craft:code:check` |
| `/craft:orchestrate` | `/craft:orchestrate` (flat) + `/craft:orchestrate:drive` etc. |
| Python `_discovery.py` cache | Static `namespace.json` |

---

## Workstream B: Skill Hardening

### Skills to harden (priority order)

| Skill | Gap | Target pattern |
|-------|-----|---------------|
| `workflow/brainstorm` | Diverges from opencode's depth × focus × action model | Align to opencode `/brainstorm` pattern |
| `workflow/refine` | Duplicate of opencode `/refine` | Extract shared prompt-sharpening logic |
| `workflow/done` | Missing `.STATUS` update step | Add scaffold step (from opencode `/done` template) |
| `workflow/next` | No `.STATUS` write-back | Add task-update step |
| `grill.md` | Matches opencode; consolidate instruction set | Single authoritative grill instruction set |
| `git/worktree` | Already has .STATUS scaffolding | Verify against opencode pattern; no changes needed |

### Cross-repo duplication to eliminate

| craft skill | opencode equivalent | Resolution |
|------------|---------------------|-----------|
| `workflow/brainstorm` | `/brainstorm` | craft calls opencode's template as reference implementation |
| `workflow/refine` | `/refine` | Align wording; opencode's version is more NL-native |
| `grill.md` | `/grill` | craft version is richer (codebase-first sweep); keep; sync opencode to match |

---

## Workstream C: CI Enforcement

### New CI checks (add to `.github/workflows/ci.yml`)

```yaml
- name: Validate namespace.json
  run: node scripts/validate-namespace.js

- name: Check namespace drift
  run: node scripts/check-drift.js

- name: Verify CLAUDE.md exists
  run: test -f CLAUDE.md
```

### `check-drift.js` for craft

Validates that every entry in `namespace.json` has a corresponding `.md` file in `commands/`,
and every command `.md` file has an entry in `namespace.json`. Reports additions and deletions
separately. Returns exit 1 on drift (blocks CI).

### `validate-namespace.js` for craft

Validates `namespace.json` structure: required fields (`description`, `file`, `category`),
valid `file` paths (file exists), description length (≤80 chars), naming format
(`category:command` or flat single-word).

---

## Done Signal

- [ ] `commands/namespace.json` generated and committed
- [ ] `scripts/build-namespace.js` written and working
- [ ] `scripts/check-drift.js` ported from opencode-resources
- [ ] `scripts/validate-namespace.js` written
- [ ] CI: all 3 checks green on main
- [ ] `docs` consolidated: 17 → 5 commands
- [ ] `site` consolidated: 15 → 4 commands
- [ ] `code/release*` moved to `dist/`
- [ ] `check` disambiguation resolved
- [ ] `utils/` teaching commands migrated to scholar
- [ ] GitHub Issue filed and closed

---

## Files to Create / Modify

| Action | File | Notes |
|--------|------|-------|
| Create | `commands/namespace.json` | Full command index, 117 entries |
| Create | `scripts/build-namespace.js` | Generates namespace.json from filesystem |
| Create | `scripts/check-drift.js` | Port from opencode-resources |
| Create | `scripts/validate-namespace.js` | New |
| Create | `docs/specs/SPEC-refactor-namespace-2026-06-29.md` | This file |
| Modify | `.github/workflows/ci.yml` | Add 3-check CI gate |
| Modify | `CLAUDE.md` | Update command count, add namespace.json section |
| Modify | `commands/_discovery.py` | Deprecate; leave as fallback (read-only) or remove |
| Rename | `commands/check.md` → `commands/code/check.md` | Disambiguation |
| Move | `commands/code/release.md` → `commands/dist/release.md` | Re-categorize |
| Move | `commands/code/release-watch.md` → `commands/dist/watch.md` | Re-categorize |
| Delete | `commands/utils/` (migrate to scholar first) | De-scope from craft |

---

## Implementation Notes

1. **Do not run this in the same session as any other craft feature work.** This touches 100+
   commands — file mutations need a dedicated `feature/namespace-refactor` worktree.

2. **Consolidation (Workstream B docs/site) is optional in the first pass.** The CI gate
   (Workstream C) and namespace.json index (Workstream A) are the high-value deliverables.
   Consolidation can be a follow-up spec.

3. **`_discovery.py` stays** until namespace.json is validated in CI for 2+ sprints.
   Then deprecate with a `--legacy` flag and remove after 1 month.

4. **savant/rforge/scholar** copy this spec's schema structure. They differ in command count and
   category names but use the identical JSON schema and the same 3-check CI gate.
