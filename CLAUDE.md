# CLAUDE.md - Craft Plugin

## Active Work

**Read `ORCHESTRATE-claude-md-refactor.md` in this repo root for the current implementation plan.**

Full spec: `docs/specs/SPEC-claude-md-refactor-2026-02-18.md`

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**107 commands** · **25 skills** · **8 agents** · **30 specs** · [Docs](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

**Current Version:** v2.21.0 | **Tests:** ~1575 passing, 90%+ coverage

> For project details (agents, test suite, structure, key files, version history), see `.claude/reference/`

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

### Branch Protection (Enforced by Hook)

| Branch | Code Files | .md Files | Git Operations |
|--------|-----------|-----------|----------------|
| `main` | BLOCKED | BLOCKED | Commit/push BLOCKED |
| `dev` | New: BLOCKED, Existing: allowed | ALLOWED | Commit/push allowed |
| `feature/*` | ALLOWED | ALLOWED | All allowed |

Override: `/craft:git:unprotect` (session-scoped, auto-expires)

## Quick Commands

| Task | Command |
|------|---------|
| Run unit tests | `python3 tests/test_craft_plugin.py` or `/craft:test unit` |
| Integration tests | `python3 tests/test_integration_*.py` |
| Dependency tests | `bash tests/test_dependency_management.sh` |
| Validate counts | `./scripts/validate-counts.sh` |
| Pre-release check | `./scripts/pre-release-check.sh <version>` |
| Build docs | `mkdocs build` |
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
| Stale worktree | `git worktree remove <path> --force` |
| Plugin not loading | Check `.claude-plugin/plugin.json` — no unrecognized keys (strict schema) |
| Command not found | Verify file in `commands/` with valid frontmatter |
