# CLAUDE.md - Craft Plugin

## Active Work

**48 commands** · **40 skills** · **2 agents** · [Docs](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

> `orchestrate:drive` — spec-driven autonomous /goal loop · `prompt-refiner` skill + `--refine` flag (7 commands) · `/craft:restore` — combined git+`.STATUS` recap (v4.1.0)

**Current Version:** v4.1.0 | **Tests:** full suite via `python3 -m pytest tests/` · tiers via `/craft:test <unit|e2e|dogfood>`

> For project details, see `plugin.json` description and `scripts/validate-counts.sh`

## Git Workflow

```text
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Constraints

- **CRITICAL**: Always start work from `dev` branch (`git checkout dev`)
- **Never** commit directly to `main`
- **Never** write feature code on `dev`
- **Always** verify branch: `git branch --show-current`

### Branch Protection

| Branch | Code Files | .md Files | Git Operations |
|--------|-----------|-----------|----------------|
| `main` | BLOCKED | BLOCKED | Commit/push BLOCKED |
| `dev` | New: BLOCKED, Existing: allowed | ALLOWED | Commit/push allowed |
| `feature/*` | ALLOWED | ALLOWED | All allowed |

Override local hook: ask "unprotect dev" / "bypass branch guard" (`dev/git` skill, Operation 10 — session-scoped, auto-expires).

## Quick Commands

| Task | Command |
|------|---------|
| Run unit tests | `python3 tests/test_craft_plugin.py` or `/craft:test unit` |
| E2E tests | `python3 -m pytest tests/test_plugin_e2e.py -v` |
| Dogfood tests | `python3 -m pytest tests/test_plugin_dogfood.py -v` |
| Integration tests | `python3 tests/test_integration_*.py` |
| Dependency tests | `bash tests/test_dependency_management.sh` |
| Validate counts | `./scripts/validate-counts.sh` |
| Pre-release check | `./scripts/pre-release-check.sh <version>` |
| Post-release sweep | `./scripts/post-release-sweep.sh` or `--fix` |
| Docs staleness check | `./scripts/docs-staleness-check.sh` or `--fix` |
| Build docs | `mkdocs build` |
| Apply GitHub-side protection | ask "apply GitHub branch protection [--repo OWNER/REPO]" (`dev/git` skill, Operation 9) |
| Smart routing | `/craft:do <task>` |
| Pre-flight check | `/craft:check` |
| Lint code | `/craft:code:lint` |
| Release pipeline | `/release` or `/release -n` |
| Brainstorm | `/craft:brainstorm` |
| Orchestrate | `/craft:orch` |

## Execution Modes

Canonical definitions live in `skills/modes/SKILL.md` (the `mode-controller` skill) —
see it for the full time-budget/use-case/behavior table. Quick reference:
`default` (<10s, quick tasks) · `debug` (<120s, verbose) · `optimize` (<180s,
performance) · `release` (<300s, thorough). Example: `/craft:code:lint debug`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Unit tests failing | `python3 tests/test_craft_plugin.py` |
| Integration tests failing | `python3 tests/test_integration_<name>.py` |
| Broken links | `python3 tests/test_craft_plugin.py -k "broken_links"` |
| Outdated counts | `./scripts/validate-counts.sh` |
| Stale docs | `./scripts/docs-staleness-check.sh` or `--fix` |
| Stale worktree | `git worktree remove <path> --force` |
| Plugin not loading | Check `.claude-plugin/plugin.json` — no unrecognized keys (strict schema) |
| Command not found | Verify file in `commands/` with valid frontmatter |

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `commands/` | 48 commands (auto-discovered, one `.md` per command) |
| `skills/` | 40 skills (`SKILL.md` pattern) |
| `agents/` | 8 agent definitions |
| `tests/` | Unit, e2e, dogfood, and integration test suites |
| `scripts/` | Release, validation, and maintenance scripts |
| `utils/` | Python utilities (`claude_md_sync`, `validate-counts`, etc.) |
| `.claude-plugin/` | Plugin manifest + hot-reload validators |

## Testing

| Tier | Command | Scope |
|------|---------|-------|
| Unit | `python3 -m pytest tests/test_craft_plugin.py` | Core plugin logic |
| E2E | `python3 -m pytest tests/test_plugin_e2e.py` | End-to-end command flows |
| Dogfood | `python3 -m pytest tests/test_plugin_dogfood.py` | Self-usage patterns |
| Full | `python3 -m pytest tests/` | All tiers |
| Tiered | `/craft:test <unit\|e2e\|dogfood>` | Via craft command |
