# CLAUDE.md - Craft Plugin

## Active Work

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**109 commands** · **38 skills** · **8 agents** · [Docs](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

> `orchestrate:drive` — spec-driven autonomous /goal loop · `prompt-refiner` skill + `--refine` flag (5 commands)

**Current Version:** v2.34.0 (v2.35.0 in development on `dev`) | **Tests:** 130 passing (23 unit + 23 e2e + 29 dogfood + 55 homebrew)

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

### Branch Protection (Two Layers)

**Local hook** (`branch-guard.sh`) — enforces table below before edits/writes leave this machine:

| Branch | Code Files | .md Files | Git Operations |
|--------|-----------|-----------|----------------|
| `main` | BLOCKED | BLOCKED | Commit/push BLOCKED |
| `dev` | New: BLOCKED, Existing: allowed | ALLOWED | Commit/push allowed |
| `feature/*` | ALLOWED | ALLOWED | All allowed |

Override local hook: `/craft:git:unprotect` (session-scoped, auto-expires).

**GitHub-side** (`branch protection API`) — applied per-repo via `/craft:git:protect-baseline` (PR required, no force-push, no delete). Independent of local hook; `unprotect` does NOT remove it.

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
| Apply GitHub-side protection | `/craft:git:protect-baseline [--repo OWNER/REPO]` |
| Smart routing | `/craft:do <task>` |
| Pre-flight check | `/craft:check` |
| Lint code | `/craft:code:lint` |
| Lint markdown | `/craft:docs:lint` |
| Release pipeline | `/release` or `/release -n` |
| Brainstorm | `/craft:workflow:brainstorm` |
| Orchestrate | `/craft:orchestrate` |
| CLAUDE.md sync | `/craft:docs:claude-md:sync` |

## Execution Modes

| Mode | Budget | Use Case | Example |
|------|--------|----------|---------|
| **default** | < 10s | Quick tasks | `/craft:code:lint` |
| **debug** | < 120s | Verbose traces | `/craft:code:lint debug` |
| **optimize** | < 180s | Performance | `/craft:code:lint optimize` |
| **release** | < 300s | Thorough validation | `/craft:code:lint release` |

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
