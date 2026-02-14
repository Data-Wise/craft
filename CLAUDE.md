# CLAUDE.md - Craft Plugin

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**108 commands** · **23 skills** · **8 agents** · **26 specs** · [Documentation](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

**Current Version:** v2.18.0 | **Latest Release:** v2.18.0 (2026-02-14)
**Documentation Status:** 99% complete | **Tests:** ~1504 passing, 90%+ coverage

## Git Workflow

```text
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Workflow Steps

| Step         | Action                                       | Command                               |
| ------------ | -------------------------------------------- | ------------------------------------- |
| 1. Plan      | Analyze on `dev`, wait for approval          | `git checkout dev`                    |
| 2. Branch    | Create worktree for isolation                | `/craft:git:worktree feature/<name>`  |
| 3. Develop   | Conventional commits (`feat:`, `fix:`, etc.) | Small, atomic commits                 |
| 4. Integrate | Test → rebase → PR to dev                    | `gh pr create --base dev`             |
| 5. Release   | PR from dev to main (or `/release`)          | `gh pr create --base main --head dev` |

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
Config: `.claude/branch-guard.json` (per-project, optional)

## Quick Commands

| Task              | Shell                                      | Craft                            |
| ----------------- | ------------------------------------------ | -------------------------------- |
| Run unit tests    | `python3 tests/test_craft_plugin.py`       | `/craft:test:run`                |
| Integration tests | `python3 tests/test_integration_*.py`      | -------------------------------- |
| Dependency tests  | `bash tests/test_dependency_management.sh` | -------------------------------- |
| Validate          | `./scripts/validate-counts.sh`             | `/craft:check`                   |
| Pre-release check | `./scripts/pre-release-check.sh <version>` | -------------------------------- |
| Build docs        | `mkdocs build`                             | -------------------------------- |
| Lint code         | ------------------------------------------ | `/craft:code:lint`               |
| Lint markdown     | `npx markdownlint-cli2 "**/*.md"`          | `/craft:docs:lint`               |
| Emoji attr check  | `bash scripts/docs-lint-emoji.sh`          | (runs in `/craft:docs:lint`)     |
| Release pipeline  | ------------------------------------------ | `/release` or `/release -n`      |
| Smart routing     | ------------------------------------------ | `/craft:do <task>`               |
| Brainstorm        | ------------------------------------------ | `/craft:workflow:brainstorm`     |
| Orchestrate       | ------------------------------------------ | `/craft:orchestrate`             |
| CLAUDE.md sync    | ------------------------------------------ | `/craft:docs:claude-md:sync`     |

## Execution Modes

| Mode         | Budget | Use Case            | Example                     |
| ------------ | ------ | ------------------- | --------------------------- |
| **default**  | < 10s  | Quick tasks         | `/craft:code:lint`          |
| **debug**    | < 120s | Verbose traces      | `/craft:code:lint debug`    |
| **optimize** | < 180s | Performance         | `/craft:code:lint optimize` |
| **release**  | < 300s | Thorough validation | `/craft:code:lint release`  |

Auto-selection: debug (errors), optimize (performance), release (deploy), else default.

## Agents

| Agent                 | Model  | Use For                                               |
| --------------------- | ------ | ----------------------------------------------------- |
| **orchestrator-v2**   | sonnet | Complex multi-step tasks, parallel execution          |
| **docs-architect**    | sonnet | System documentation, architecture guides             |
| **api-documenter**    | sonnet | OpenAPI specs, API docs, SDKs                         |
| **tutorial-engineer** | sonnet | Step-by-step tutorials, onboarding                    |
| **reference-builder** | haiku  | Parameter listings, config references                 |
| **mermaid-expert**    | haiku  | Flowcharts, sequence diagrams, ERDs                   |
| **demo-engineer**     | ------ | Terminal GIF demos (asciinema workflow)                |

## Project Structure

```text
craft/
├── .claude-plugin/     # Plugin manifest, hooks, validators
├── commands/           # 108 commands (arch, ci, code, docs, git, site, test, workflow)
├── skills/             # 22 specialized skills (including /release)
├── agents/             # 8 agents
├── scripts/            # 30+ utility scripts (dependency management, converters, installers)
├── utils/              # Python utilities (claude-md sync/optimizer, complexity scorer, validators)
├── tests/              # ~1504 tests, 90%+ coverage
├── docs/
│   ├── specs/          # Implementation specs (26 total)
│   ├── guide/          # User guides
│   ├── tutorials/      # Step-by-step guides
│   └── brainstorm/     # Working drafts (gitignored)
└── .STATUS             # Current milestone and progress
```

## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Current milestone, progress, session history |
| `commands/do.md` | Universal smart routing with complexity scoring |
| `commands/check.md` | Pre-flight validation |
| `commands/orchestrate.md` | Multi-agent coordination |
| `skills/release/SKILL.md` | End-to-end release pipeline (`--dry-run` support) |
| `scripts/pre-release-check.sh` | Pre-release validation (version, counts, clean tree) |
| `scripts/formatting.sh` | Unified box-drawing, colors, ANSI-aware padding |
| `scripts/branch-guard.sh` | Branch protection hook (~700 lines) |
| `utils/complexity_scorer.py` | Task complexity scoring (0-10 scale) |
| `utils/claude_md_sync.py` | 4-phase sync pipeline (detect → update → audit → fix) |
| `utils/claude_md_optimizer.py` | Line budget enforcement and section optimization |
| `.claude/branch-guard.json` | Per-project branch protection config (optional) |
| `docs/VERSION-HISTORY.md` | Complete release timeline (v1.0.0 → v2.17.0) |

## Test Suite

Run all tests: `python3 tests/test_craft_plugin.py && python3 tests/test_integration_*.py && bash tests/test_dependency_management.sh && bash tests/test_formatting.sh && bash tests/test_branch_guard.sh && bash tests/test_branch_guard_e2e.sh && bash tests/test_release_skill_e2e.sh`

Key test files: `test_craft_plugin.py` (370), `test_branch_guard.sh` (94), `test_command_enhancements_e2e.py` (93), `test_dependency_management.sh` (79), `test_formatting.sh` (74), `test_branch_guard_e2e.sh` (31), `test_branch_guard_dogfood.py` (52), `test_release_skill_e2e.sh` (27), `test_release_skill_dogfood.py` (28).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Unit tests failing | `python3 tests/test_craft_plugin.py` |
| Integration tests failing | `python3 tests/test_integration_<name>.py` |
| Broken links | `python3 tests/test_craft_plugin.py -k "broken_links"` |
| Outdated counts | `./scripts/validate-counts.sh` |
| Stale worktree | `git worktree remove <path> --force` |
| Plugin not loading | Check `.claude-plugin/plugin.json` has no unrecognized keys (strict schema) |
| Command not found | Verify file in `commands/` with valid frontmatter |

## Version History

See [`docs/VERSION-HISTORY.md`](docs/VERSION-HISTORY.md) for full release timeline. Recent: v2.17.0 (branch guard smart mode + release skill), v2.16.0 (branch protection hooks), v2.15.0 (brainstorm simplification), v2.14.0 (formatting library).

## Links

- [Documentation Site](https://data-wise.github.io/craft/) — Full guides and references
- [Commands Reference](https://data-wise.github.io/craft/commands/) — All 108 commands
- [Architecture Guide](https://data-wise.github.io/craft/architecture/) — How Craft works
- [Version History](docs/VERSION-HISTORY.md) — Complete release timeline
- [GitHub Repository](https://github.com/Data-Wise/craft) — Source code and issues
