# CLAUDE.md - Craft Plugin

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**97 commands** · **21 skills** · **8 agents** · **4 specs** · [Documentation](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

## Git Workflow

```
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Workflow Steps

| Step | Action | Command |
|------|--------|---------|
| 1. Plan | Analyze on `dev`, wait for approval | `git checkout dev` |
| 2. Branch | Create worktree for isolation | `/craft:git:worktree feature/<name>` |
| 3. Develop | Conventional commits (`feat:`, `fix:`, etc.) | Small, atomic commits |
| 4. Integrate | Test → rebase → PR to dev | `gh pr create --base dev` |
| 5. Release | PR from dev to main | `gh pr create --base main --head dev` |

### Constraints

- **CRITICAL**: Always start work from `dev` branch (`git checkout dev`)
- **Never** commit directly to `main`
- **Never** write feature code on `dev`
- **Always** verify branch: `git branch --show-current`

## Quick Commands

| Task | Shell | Craft |
|------|-------|-------|
| Run tests | `python3 tests/test_craft_plugin.py` | `/craft:test:run` |
| Validate | `./scripts/validate-counts.sh` | `/craft:check` |
| Build docs | `mkdocs build` | - |
| Lint code | - | `/craft:code:lint` |
| Architecture | - | `/craft:arch:analyze` |
| Git status | `git status` | `/craft:git:status` |
| Worktree | `git worktree add ...` | `/craft:git:worktree <branch>` |
| Clean branches | - | `/craft:git:clean` |
| CI workflow | - | `/craft:ci:generate` |
| Smart routing | - | `/craft:do <task>` |
| Brainstorm | - | `/craft:workflow:brainstorm` |
| Orchestrate | - | `/craft:orchestrate` |

## Execution Modes

| Mode | Budget | Use Case | Example |
|------|--------|----------|---------|
| **default** | < 10s | Quick tasks | `/craft:code:lint` |
| **debug** | < 120s | Verbose traces | `/craft:code:lint debug` |
| **optimize** | < 180s | Performance | `/craft:code:lint optimize` |
| **release** | < 300s | Thorough validation | `/craft:code:lint release` |

Auto-selection: debug (errors), optimize (performance), release (deploy), else default.

## Agents

| Agent | Model | Use For |
|-------|-------|---------|
| **orchestrator-v2** | - | Complex multi-step tasks, parallel execution |
| **orchestrator** | - | Basic workflow automation |
| **docs-architect** | sonnet | System documentation, architecture guides |
| **api-documenter** | sonnet | OpenAPI specs, API docs, SDKs |
| **tutorial-engineer** | sonnet | Step-by-step tutorials, onboarding |
| **reference-builder** | haiku | Parameter listings, config references |
| **mermaid-expert** | haiku | Flowcharts, sequence diagrams, ERDs |
| **demo-engineer** | - | Terminal GIF demos (VHS tapes) |

## Project Structure

```
craft/
├── .claude-plugin/     # Plugin manifest
├── commands/           # 92 commands (arch, ci, code, docs, git, site, test, workflow)
├── skills/             # 21 specialized skills
├── agents/             # 8 agents
├── tests/              # Python test suite
├── docs/
│   ├── specs/          # Implementation specs (4 total)
│   └── brainstorm/     # Working drafts (gitignored)
└── .STATUS             # Current milestone and progress
```

## Active Development

### Just Completed ✅

**Test Coverage Improvements (v1.23.1)** - Comprehensive coverage gap analysis
- ✅ New test suite: `tests/test_coverage_gaps.py` (17 comprehensive tests)
- ✅ Coverage improvements: 75% → 84% overall (+9%)
  - `detect_teaching_mode.py`: 65% → 75% (+10%)
  - `linkcheck_ignore_parser.py`: 71% → 87% (+16%)
  - `dry_run_output.py`: 86% (maintained)
- ✅ Production code coverage: ~91% (excluding demo blocks)
- ✅ Total tests: 353 → 370 (+17 tests)
- ✅ Documentation: `TEST-COVERAGE-REPORT.md` with detailed analysis
- 📍 Status: Merged to `dev`

**Broken Link Validation with .linkcheck-ignore (v1.23.0)** - MERGED ✅
- ✅ Parser utility: `utils/linkcheck_ignore_parser.py` (270 lines)
- ✅ Command integration: `/craft:docs:check-links` (categorized output)
- ✅ Testing: 21/21 tests passing (13 unit + 8 integration)
- ✅ Documentation: Usage instructions, CI templates, implementation guide
- ✅ Impact: 100% reduction in CI false positives (30 → 0)
- 📍 Status: Merged to `dev` (PR #14)

### Current Worktrees
| Branch | Location | Status |
|--------|----------|--------|
| `dev` | `/Users/dt/projects/dev-tools/craft` | Main repo (integration) |
| `feature/website-org-phase2` | `~/.git-worktrees/craft/feature-website-org-phase2` | WIP (Phase 2) |
| `feature/hub-v2` | `~/.git-worktrees/craft/feature-hub-v2` | WIP (Phase 1) |

### Planned Features (v1.21.0+)
| Spec | Priority | Effort | Target |
|------|----------|--------|--------|
| **Teaching Workflow** | High | 6-8h | v1.22.0 |
| Hub v2.0 (Discovery) | High | 30h | v1.21.0+ |
| Help Template System | High | 30h | v1.21.0 |
| Spec Integration | High | 20h | v1.21.0 |

See `docs/specs/` for detailed specifications.

## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Current milestone, progress, next steps |
| `commands/do.md` | Universal smart routing |
| `commands/check.md` | Pre-flight validation |
| `commands/orchestrate.md` | Multi-agent coordination |
| `commands/workflow/brainstorm.md` | ADHD-friendly brainstorming |
| `docs/specs/SPEC-teaching-workflow-2026-01-16.md` | Teaching mode implementation spec |
| `docs/specs/SPEC-broken-link-validation-2026-01-17.md` | .linkcheck-ignore parser spec |
| `.linkcheck-ignore` | Document expected broken links (test files, brainstorm refs) |
| `utils/linkcheck_ignore_parser.py` | Parser for .linkcheck-ignore patterns |
| `tests/test_coverage_gaps.py` | Comprehensive coverage tests (17 tests, 75% → 84%) |
| `TEST-COVERAGE-REPORT.md` | Detailed coverage analysis and recommendations |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tests failing | `python3 tests/test_craft_plugin.py` |
| Broken links | `python3 tests/test_craft_plugin.py -k "broken_links"` |
| Outdated counts | `./scripts/validate-counts.sh` |
| Stale worktree | `git worktree remove <path> --force` |
| Orphaned worktrees | `git worktree prune` |
| Rebase conflicts | `git rebase --abort && git merge origin/dev` |
| Plugin not loading | Check `.claude-plugin/plugin.json` frontmatter |
| Command not found | Verify file in `commands/` with valid frontmatter |
| Agent not triggering | Check triggers list in agent frontmatter |
| GIF showing broken commands | **CRITICAL:** Always test commands in Claude Code FIRST using Bash tool, capture real output, verify no errors, THEN generate GIF. See `templates/docs/GIF-GUIDELINES.md` |

## Links

- [Documentation Site](https://data-wise.github.io/craft/) — Full guides and references
- [Commands Reference](https://data-wise.github.io/craft/commands/) — All 92 commands
- [Architecture Guide](https://data-wise.github.io/craft/architecture/) — How Craft works
- [Specifications](docs/specs/) — Implementation specs (4 total)
- [GitHub Repository](https://github.com/Data-Wise/craft) — Source code and issues
