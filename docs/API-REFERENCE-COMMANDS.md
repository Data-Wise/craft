# Craft Command API Reference

This page used to be a hand-maintained, exhaustive per-command reference (Arguments/Examples/Output
for every command). It drifted badly from reality — the last full edit predates the v4 folio split
and still describes commands that either moved to [`folio`](https://github.com/Data-Wise/folio) or
were consolidated into skills. Rather than re-sync a third parallel documentation surface indefinitely,
this page is now a thin index into the two places that stay current:

- **[docs/commands/](commands/overview.md)** — one page per command, gated by
  `scripts/doc-coverage-check.sh` (every live command must have a page or the release-check gate
  fails)
- **[docs/REFCARD.md](REFCARD.md)** — quick-reference tables grouped by category, with copy-paste
  invocation examples

## Full Command List

47 commands across 10 categories. See [docs/commands.md](commands.md) for the complete A-Z table,
or use `/craft:hub` (and `/craft:hub <category>`) to browse interactively from within Claude Code.

| Category | Count | Reference |
|---|---|---|
| Root (do, check, hub, smart-help, brainstorm, brief, done, next, grill, orch, plan, refine, test) | 13 | [docs/commands/overview.md](commands/overview.md) |
| Code | 13 | [docs/commands/code.md](commands/code.md) |
| CI | 8 | [docs/commands/ci/](commands/ci/detect.md) |
| Architecture | 4 | [docs/commands/arch.md](commands/arch.md) |
| Git | 1 (+ `dev/git` skill) | [docs/commands/git.md](commands/git.md) |
| Distribution | 2 | [docs/commands/dist.md](commands/dist.md) |
| Docs | 2 | [docs/commands/docs.md](commands/docs.md) |
| Plan | 2 | [docs/commands/plan.md](commands/plan.md) |
| Site | 1 | [docs/commands/site.md](commands/site.md) |
| Orchestrate | 3 | [docs/commands/orch.md](commands/orch.md) |

## Looking for a command that used to be here?

- **CLAUDE.md management** (`init`/`sync`/`edit`) — folded into the `claude-md-lifecycle` skill
  (2026-07 v4 rider). Ask naturally, e.g. "sync CLAUDE.md".
- **Docs authoring / site building** (`sync`, `lint`, `check`, `nav-update`, `demo`, `mermaid`,
  `guide`, `tutorial`, `api`, `quickstart`, `help`, `prompt`, `site`, `website`, `workflow`) —
  moved to the [`folio`](https://github.com/Data-Wise/folio) plugin. See
  [docs/MIGRATION-v4.md](MIGRATION-v4.md) for the full command migration table.
- **Git worktree/branch/protect/status/clean** — folded into the `dev/git` skill. Ask naturally,
  e.g. "create a worktree for feat/x".
- **Insights, guard audit** — skill-routed (`brainstorm-insights`, `guard-audit`). Ask naturally,
  e.g. "show session insights" or "audit guard config".

## See Also

- [Command Overview](commands/overview.md)
- [REFCARD](REFCARD.md)
- [MIGRATION-v4](MIGRATION-v4.md)
