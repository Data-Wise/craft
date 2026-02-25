# Craft Commands Reference

Complete reference for all 97 Craft commands organized by category. Craft provides intelligent automation across the full development lifecycle.

## Quick Reference

**Smart Commands:** `/craft:do`, `/craft:check`, `/craft:help`, `/craft:hub`
**Dry-Run Support:** 27 of 107 commands support `--dry-run` / `-n` preview mode
**16 Categories:** arch, check, ci, code, dist, do, docs, git, hub, orchestrate, plan, site, smart-help, test, utils, workflow

Use `/craft:hub` to discover all available commands interactively.

!!! tip "Preview Before Executing"
    27 commands now support dry-run mode. Add `--dry-run` or `-n` to preview actions before executing. See [Dry-Run Commands](#dry-run-commands) below.

## Smart Commands

### /craft:do 🔍

Universal command - AI routes to appropriate workflow.

```bash
/craft:do "add user authentication"
/craft:do "optimize database queries"
/craft:do "prepare for release"
/craft:do "add auth" --dry-run           # Preview routing plan
```

**Dry-run:** Preview which commands will be executed and estimated time.

### /craft:orchestrate 🔍

Multi-agent orchestrator with mode-aware execution.

```bash
/craft:orchestrate "add auth" optimize    # Fast parallel
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate status                 # Agent dashboard
/craft:orchestrate "task" --dry-run       # Preview orchestration plan
```

**Modes:** optimize (4 agents), release (comprehensive), debug (verbose)
**Dry-run:** Preview agent allocation, parallelization waves, and execution time.

### /craft:check 🔍

Pre-flight validation for commits, PRs, and releases.

```bash
/craft:check                  # Quick validation
/craft:check --for commit     # Pre-commit checks
/craft:check --for release    # Full release audit
/craft:check --dry-run        # Preview validation plan
```

**Dry-run:** Preview which checks will be performed without executing them.

### /craft:help

Context-aware help and suggestions.

```bash
/craft:help                   # Project-specific suggestions
/craft:help testing           # Deep dive into testing
```

## Architecture Commands (arch/)

### /craft:arch:analyze

Analyze codebase architecture with mode support.

```bash
/craft:arch:analyze
/craft:arch:analyze optimize   # Performance analysis
```

## CI/CD Commands (ci/)

### /craft:ci:detect

Detect project type, build tools, and test frameworks.

```bash
/craft:ci:detect
```

**Detects:** Language, framework, build system, test runner, dependencies

### /craft:ci:generate

Generate GitHub Actions workflow from project detection.

```bash
/craft:ci:generate
/craft:ci:generate --template node-typescript
```

**Generates:** .github/workflows/ci.yml with tests, linting, build steps

### /craft:ci:status

Cross-repo CI status dashboard — see all workflow statuses in one view. Supports `--post-release` mode for downstream verification.

```bash
/craft:ci:status
/craft:ci:status --json
/craft:ci:status --repo craft
/craft:ci:status --post-release
```

**See:** [Command Reference](commands/ci/status.md)

### /craft:ci:validate

Validate existing CI workflow against project configuration.

```bash
/craft:ci:validate
```

## Code Quality Commands (code/)

### /craft:code:lint

Code style and quality checks with mode support.

```bash
/craft:code:lint              # Quick check
/craft:code:lint debug        # Verbose with suggestions
```

## Distribution Commands (dist/)

### /craft:dist:curl-install

Generate curl-based installation scripts for GitHub releases.

```bash
/craft:dist:curl-install
```

**Generates:** install.sh with release detection, platform support

## Documentation Commands (docs/)

### /craft:docs:mermaid

Generate Mermaid diagram templates.

```bash
/craft:docs:mermaid flowchart
/craft:docs:mermaid sequence
/craft:docs:mermaid er
```

### /craft:docs:api-documenter

Create API documentation with OpenAPI support.

```bash
/craft:docs:api-documenter
```

### /craft:docs:tutorial-engineer

Build step-by-step tutorials from code.

```bash
/craft:docs:tutorial-engineer "Getting started guide"
```

### /craft:docs:reference-builder

Generate technical references and API docs.

```bash
/craft:docs:reference-builder
```

## Git Commands (git/)

### /craft:git:worktree

Git worktree management for parallel development.

```bash
/craft:git:worktree list
/craft:git:worktree add feature-branch
/craft:git:worktree remove feature-branch
```

### /craft:git:clean

Clean up merged branches safely.

```bash
/craft:git:clean              # Interactive mode
/craft:git:clean --force      # Auto-delete merged branches
```

### /craft:git:protect

Re-enable branch protection, configure levels, view status.

```bash
/craft:git:protect              # Re-enable protection
/craft:git:protect --show       # Show current level + counters
/craft:git:protect --level smart  # Set protection level
/craft:git:protect --reset      # Reset session counters
```

### /craft:git:unprotect

Session-wide bypass for branch protection with reason logging.

```bash
/craft:git:unprotect                 # Interactive
/craft:git:unprotect merge-conflict  # For merge conflicts
/craft:git:unprotect maintenance     # For bulk maintenance
```

### /craft:git:status

Enhanced git status with branch guard indicator.

```bash
/craft:git:status           # Shows guard level + session info
/craft:git:status --verbose # Additional details
```

## Test Commands (test/)

### /craft:test

Unified test runner with category filtering and modes.

```bash
/craft:test                       # Quick tests (default mode)
/craft:test unit                  # Unit tests only
/craft:test release               # Full suite with coverage
/craft:test --coverage            # Coverage report
/craft:test --watch               # Watch mode
```

### /craft:test:gen

Generate test suites with project-type detection.

```bash
/craft:test:gen                   # Auto-detect and generate
/craft:test:gen plugin            # Force plugin type
/craft:test:gen --tier unit       # Unit tests only
```

### /craft:test:template

Manage Jinja2 templates for test generation.

```bash
/craft:test:template list         # List all templates
/craft:test:template validate     # Validate templates
```

## Mode System

All applicable commands support 4 execution modes:

| Mode | Time | Use Case |
|------|------|----------|
| **default** | <10s | Quick checks |
| **debug** | <120s | Verbose output |
| **optimize** | <180s | Parallel execution |
| **release** | <300s | Comprehensive audit |

**Usage:**

```bash
/craft:code:lint debug
/craft:test release
/craft:arch:analyze optimize
```

## Category Breakdown

- **Smart (4):** do, orchestrate, check, help, hub
- **Architecture (1):** analyze
- **CI/CD (3):** detect, generate, validate
- **Code (1):** lint
- **Distribution (1):** curl-install
- **Documentation (4):** mermaid, api-documenter, tutorial-engineer, reference-builder
- **Git (2):** worktree, clean
- **Test (3):** run, cli-gen, cli-run

## Dry-Run Commands

27 of 107 commands support `--dry-run` / `-n` preview mode. **Target exceeded:** 57% of target commands vs 52% goal.

### Git Commands (6/6) — 100% ✅

- `git:branch` - Preview branch operations
- `git:clean` - Preview merged branch deletion (CRITICAL)
- `git:init` - Preview repository initialization
- `git:recap` - Preview git activity summary
- `git:sync` - Preview sync operations
- `git:worktree` - Preview worktree operations (HIGH)

### CI/CD Commands (3/3) — 100% ✅

- `ci:detect` - Preview project type detection
- `ci:generate` - Preview workflow generation (CRITICAL)
- `ci:status` - CI dashboard (read-only, no dry-run needed)
- `ci:validate` - Preview CI validation

### Site Commands (4/6) — 67%

- `site:build` - Preview site build
- `site:check` - Preview validation checks
- `site:deploy` - Preview GitHub Pages deployment (CRITICAL)
- `site:update` - Preview site content updates

### Documentation Commands (5/10) — 50%

- `docs:changelog` - Preview changelog generation
- `docs:check` - Preview health check
- `docs:claude-md` - Preview CLAUDE.md generation
- `docs:nav-update` - Preview navigation updates
- `docs:sync` - Preview documentation sync

### Code Commands (3/12) — 25%

- `code:ci-local` - Preview local CI checks (6 checks)
- `code:deps-audit` - Preview security vulnerability scanning
- `code:lint` - Preview linting plan (mode-aware)

### Test Commands (1/3) — 33%

- `test` - Preview test execution plan (mode-aware)

### Distribution Commands (1/4) — 25%

- `dist:pypi` - Preview PyPI publishing (CRITICAL - IRREVERSIBLE warnings)

### Smart Routing (3/3) — 100% ✅

- `check` - Preview validation plan
- `do` - Preview routing plan
- `orchestrate` - Preview orchestration plan

**Example usage:**

```bash
/craft:git:clean --dry-run           # Preview branch cleanup
/craft:code:lint release -n          # Preview comprehensive linting
/craft:dist:pypi publish --dry-run   # Preview PyPI publish (CRITICAL)
```

See [DRY-RUN-SUMMARY.md](https://github.com/Data-Wise/craft/blob/dev/DRY-RUN-SUMMARY.md) for complete details.

## See Also

- **[Skills & Agents Guide](skills-agents.md)** - 26 skills, 8 agents
- **[Architecture Guide](architecture.md)** - How Craft works
- **[Orchestrator Guide](orchestrator.md)** - Multi-agent coordination
- **[Mode System](skills-agents.md#mode-aware-behavior)** - Mode system (default/debug/optimize/release)
