# Migration Guide — craft v3 → v4 (folio split)

> Docs/publishing surface split into a new sibling plugin, `folio`
> ([Data-Wise/folio](https://github.com/Data-Wise/folio)), extracted via
> `git filter-repo` (history-preserving) so no commit history was lost.
> See `docs/plans/ORCHESTRATE-folio-split.md` for the full rationale and plan.

## Install folio

```bash
claude plugin install folio@data-wise-marketplace
```

## Commands moved to folio

53 commands moved. Slash-command syntax unchanged except the plugin prefix
(`/craft:X` → `/folio:X`) — some were consolidated into other folio commands
or demoted to skill references along the way (destination column notes this).

| Old (`/craft:...`) | New location in folio |
|---|---|
| `docs:api` | `/folio:docs:api` |
| `docs:check-links` | Absorbed into `/folio:docs:check` |
| `docs:check` | `/folio:docs:check` |
| `docs:demo` | `/folio:docs:demo` |
| `docs:generate` | `/folio:docs:generate` |
| `docs:guide` | `/folio:docs:guide` |
| `docs:help` | `/folio:docs:help` |
| `docs:lint` | `/folio:docs:lint` |
| `docs:mermaid` | `/folio:docs:mermaid` |
| `docs:nav-update` | Demoted to `skills/docs/navigation/references/nav-update.md` |
| `docs:prompt` | `/folio:docs:prompt` |
| `docs:quickstart` | `/folio:docs:quickstart` |
| `docs:site` | `/folio:docs:site` |
| `docs:sync` | `/folio:docs:sync` |
| `docs:tutorial` | `/folio:docs:tutorial` |
| `docs:website` | `/folio:docs:website` |
| `docs:workflow` | `/folio:docs:workflow` |
| `site:build` | Demoted to `skills/docs/site-management/references/build.md` |
| `site:check` | Demoted to `skills/docs/site-management/references/check.md` |
| `site:docs:frameworks` | Demoted to `skills/docs/site-management/references/frameworks.md` |
| `site:progress` | Consolidated inline in `skills/docs/site-management/SKILL.md` |
| `site:publish` | Demoted to `skills/docs/site-management/references/publish.md` |
| `site:status` | Demoted to `skills/docs/site-management/references/status.md` |
| `site:update` | Demoted to `skills/docs/site-management/references/update.md` |

## Agents moved to folio

| Old craft agent | New location in folio |
|---|---|
| `agents/docs/api-documenter.md` | `agents/docs/api-documenter.md` |
| `agents/docs/demo-engineer.md` | `agents/docs/demo-engineer.md` |
| `agents/docs/docs-architect.md` | `agents/docs/docs-architect.md` |
| `agents/docs/mermaid-expert.md` | `agents/docs/mermaid-expert.md` |
| `agents/docs/reference-builder.md` | `agents/docs/reference-builder.md` |
| `agents/docs/tutorial-engineer.md` | `agents/docs/tutorial-engineer.md` |

## Skills moved to folio

| Old craft skill | New location in folio |
|---|---|
| `skills/code/demonstration-builder/` | `skills/code/demonstration-builder/` |
| `skills/docs/doc-classifier/` | `skills/docs/doc-classifier/` |
| `skills/docs/mermaid-linter/` | `skills/docs/mermaid-linter/` |
| `skills/docs/navigation/` | `skills/docs/navigation/` |
| `skills/docs/openapi-spec-generation/` | `skills/docs/openapi-spec-generation/` |
| `skills/docs/site-management/` | `skills/docs/site-management/` |

## Commands folded into craft skill references (v4 consolidation, Phase 3.5)

These stayed in craft but lost their standalone slash-command form — the content moved into
the `dist-extras` skill (already `deprecated`/`replaced-by` shims pointing there; the salvage
gate extracted their unique content — workflow templates, dry-run examples, check tables —
into skill references before deletion):

| Old command | New location |
|---|---|
| `dist:pypi` | `skills/distribution/dist-extras/references/pypi.md` |
| `dist:curl-install` | `skills/distribution/dist-extras/references/curl-install.md` |
| `dist:marketplace` | `skills/distribution/dist-extras/references/marketplace.md` |
| `docs:claude-md:edit` | `skills/docs/claude-md/references/edit.md` |
| `docs:claude-md:sync` | `skills/docs/claude-md/references/sync.md` |
| `docs:claude-md:init` | `skills/docs/claude-md/references/init.md` |
| `check:gen-validator` | `skills/check/references/gen-validator.md` |
| `git:worktree` | `skills/dev/git/references/worktree.md` |
| `git:docs:refcard` | `skills/dev/git/references/refcard.md` |
| `workflow:insights` | `skills/workflow/brainstorm-insights/references/insights.md` |

## Plan deviations from the original ROSTER (2026-07-09)

- **`check.md` was NOT collapsed to a micro-shim.** The original ROSTER (written before
  this file's own prior salvage pass) called for shrinking `commands/check.md` to a
  ≤5-line shim. Its current header already explains why the Step 0 plan display, confirm
  gate, `--orch` handling, and `CRAFT_MODE` binding are invocation-mandatory, not
  deferrable procedure — `skills/check/SKILL.md` itself defers back to `commands/check.md`
  as "the full check command spec." `skills/code/command-skill-token-efficiency/SKILL.md`'s
  own classification test ("does the command always run, even before skill-routing
  fires?") confirms this content belongs in the command. Left as-is.
- **`code:demo.md`** — see "What stayed in craft" below (T3.1 finding).

## What stayed in craft

Two commands whose scoring/rubric logic had cross-skill dependents were
un-deprecated rather than removed, since their `replaced-by` skills moved
to folio:

- `commands/site/deploy.md` (was pointing at `skills/docs/site-management/`)
- `commands/code/demo.md` (was pointing at `skills/code/demonstration-builder/`)

The doc-impact scoring rubric — previously embedded in `commands/docs/sync.md`
— was extracted into a craft-owned reference,
`skills/orchestration/references/doc-impact-rubric.md`, and re-pointed from
the 3 skills that depend on it (`plan-orchestrator`, `brainstorm`,
`brainstorm-insights`).

## Backlogged (not part of this split)

`scripts/dependency-manager.sh` (+ `tool-detector.sh`, `health-check.sh`,
`installers/*.sh`) — a subsystem that parsed `commands/docs/demo.md`'s prose
for tool names (asciinema, vhs, ffmpeg). Left as a flagged backlog item
(orphaned, not migrated or deleted) per an explicit user decision
2026-07-12 — see `tasks/todo.md` Phase 3 notes.

## Counts

craft: 53 commands · 39 skills · 2 agents (was 94 / 45 / 8 before the split; also was 70 as of
CP-3, before the v4 command-consolidation slices began).
