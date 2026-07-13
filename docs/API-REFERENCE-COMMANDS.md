# Craft Command API Reference

Complete OpenAPI-style documentation for all 97 Craft commands organized by category.

**Version**: v1.24.0 | **Last Updated**: 2026-01-17 | **Coverage**: 100% (97/97 commands)

---

## Quick Navigation

### Command Categories

1. **[Root Commands](#root-commands)** (6 commands) - Universal tools
2. **[Architecture Commands](#architecture-commands)** (4 commands) - System design & analysis
3. **[Code Commands](#code-commands)** (12 commands) - Development workflows
4. **[CI/CD Commands](#cicd-commands)** (3 commands) - Continuous integration
5. **[Check Commands](#check-commands)** (1 command) - Pre-flight validation
6. **[Distribution Commands](#distribution-commands)** (4 commands) - Release & packaging
7. **[Documentation Commands](#documentation-commands)** (19 commands) - Docs & tutorials
8. **[Git Commands](#git-commands)** (11 commands) - Version control workflows
9. **[Plan Commands](#plan-commands)** (3 commands) - Project planning
10. **[Site Commands](#site-commands)** (16 commands) - Static site generation
11. **[Test Commands](#test-commands)** (7 commands) - Testing & QA
12. **[Workflow Commands](#workflow-commands)** (12 commands) - Development workflows
13. **[Utility Commands](#utility-commands)** (2 commands) - Helper utilities

---

## Root Commands

Root-level commands that provide universal functionality.

### /craft:do

**Category**: Smart Routing | **Complexity**: Medium | **Time**: < 30s
**Description**: Intelligent command routing with complexity scoring and task decomposition. **NEW (v2.5.0)**: Use `--orch` flag for quick orchestration.

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `task` | string | Yes | - | Task description (natural language) |
| `mode` | enum | No | `default` | Execution mode: `default`, `debug`, `optimize`, `release` |
| `complexity` | enum | No | - | Override complexity: `simple`, `moderate`, `complex` |
| `dry-run` | boolean | No | false | Preview routing decision without executing |
| `-n` | boolean | No | false | Alias for `--dry-run` |
| `orch` | boolean | No | false | **NEW (v2.5.0)** Enable orchestration mode |
| `orch-mode` | enum | No | `default` | **NEW (v2.5.0)** Orchestration mode: `default`, `debug`, `optimize`, `release` |

#### Examples

```bash
# Simple task routing
/craft:do "add authentication"

# With explicit mode
/craft:do "refactor database layer" optimize

# Preview routing
/craft:do "add tests" --dry-run

# Override complexity
/craft:do "quick formatting fix" simple

# NEW (v2.5.0) - Quick orchestration with --orch flag
/craft:do "implement auth" --orch=optimize
/craft:do "debug issue" --orch=debug --dry-run
/craft:do "prepare release" --orch=release
```

#### Output Format

```json
{
  "task": "add authentication",
  "scored_complexity": 7,
  "complexity_level": "moderate",
  "recommended_agent": "orchestrator-v2",
  "suggested_subtasks": [
    "Design authentication flow",
    "Implement OAuth integration",
    "Add unit tests",
    "Update documentation"
  ],
  "estimated_duration": "45 minutes"
}
```

#### Error Scenarios

| Error | Cause | Resolution |
|-------|-------|-----------|
| `Empty task description` | No task provided | Provide a non-empty task description |
| `Invalid mode` | Unknown mode specified | Use: `default`, `debug`, `optimize`, `release` |
| `Complexity override invalid` | Invalid complexity value | Use: `simple`, `moderate`, `complex` |

**File**: `commands/do.md`

---

### /craft:check

**Category**: Validation | **Complexity**: Simple | **Time**: < 30s
**Description**: Pre-flight validation for code quality, tests, and git status

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scope` | enum | No | `all` | What to check: `all`, `code`, `tests`, `git`, `docs` |
| `mode` | enum | No | `default` | Execution mode |
| `fix` | boolean | No | false | Auto-fix fixable issues |
| `--dry-run` | boolean | No | false | Preview fixes without applying |
| `-n` | boolean | No | false | Alias for `--dry-run` |
| `--for` | enum | No | - | Context-specific checks: `pr`, `release`. When `release`, validates badge URLs (main+dev) and Homebrew formula desc consistency |

#### Examples

```bash
/craft:check                 # Check everything
/craft:check code            # Only code quality
/craft:check tests           # Only test coverage
/craft:check code --fix      # Auto-fix code issues
/craft:check --dry-run       # Preview all fixes
/craft:check --for release   # Release checks: badge URLs, formula desc, full CI mirror
```

#### Output Format

```text
✅ CODE QUALITY
  ✓ No linting errors
  ⚠ 2 style warnings

✅ TESTS
  ✓ 94 tests passing
  ✗ 2 tests failing

⚠️ GIT STATUS
  ✓ On dev branch
  ⚠ 3 uncommitted changes
  ✓ Ahead of origin by 1 commit
```

**File**: `commands/check.md`

---

### /craft:hub

**Category**: Discovery | **Complexity**: Simple | **Time**: < 5s
**Description**: Zero-maintenance command discovery with progressive disclosure

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | No | - | Search for commands by keyword |
| `category` | string | No | - | Filter by category |
| `--verbose` | boolean | No | false | Show full help text |
| `-v` | boolean | No | false | Alias for `--verbose` |

#### Examples

```bash
/craft:hub                   # Show main menu
/craft:hub test              # Show test commands
/craft:hub "add tests"       # Search for matching commands
/craft:hub docs --verbose    # Show detailed docs commands
```

#### Output Format

```text
MAIN MENU
├─ Code (12 commands)
│  ├─ /craft:code:lint
│  ├─ /craft:code:test-gen
│  └─ ... more
├─ Tests (7 commands)
├─ Documentation (19 commands)
└─ ... more categories
```

**File**: `commands/hub.md`

---

### /craft:orch

**Category**: Coordination | **Complexity**: Complex | **Time**: Variable
**Description**: Multi-agent task orchestration with background execution
**Tip (v2.5.0)**: For quick orchestration, use the `--orch` flag on supported commands: `/craft:do "task" --orch=optimize`

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `task` | string | Yes | - | Task description for orchestration |
| `mode` | enum | No | `default` | `default`, `debug`, `optimize`, `release` |
| `agents` | number | No | 2 | Number of parallel agents |
| `--background` | boolean | No | true | Run agents in background |
| `-bg` | boolean | No | true | Alias for `--background` |

#### Examples

```bash
/craft:orch "add feature X"
/craft:orch "refactor auth" optimize
/craft:orch "release prep" release
```

#### Output Format

```text
ORCHESTRATOR v2.1 - MODE: OPTIMIZE

Spawning agents:
  [AGENT-1: arch] Analyzing system design...
  [AGENT-2: code] Implementing feature...
  [AGENT-3: test] Creating tests...
  [AGENT-4: docs] Updating documentation...

ETA: ~30 minutes (parallel execution)
Monitor with: /craft:orch status
```

**File**: `commands/orch.md`

---

### /craft:smart-help

**Category**: Help & Discovery | **Complexity**: Simple | **Time**: < 5s
**Description**: Contextual help with examples and related commands

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `command` | string | No | - | Command to get help for |
| `--examples` | boolean | No | false | Show usage examples |
| `-e` | boolean | No | false | Alias for `--examples` |
| `--related` | boolean | No | false | Show related commands |

#### Examples

```bash
/craft:smart-help
/craft:smart-help code:lint
/craft:smart-help code:lint --examples
/craft:smart-help test --related
```

**File**: `commands/smart-help.md`

---

> `discovery-usage` was never a user-invocable slash command (`internal: true`) — demoted to
> a plain docs page in the v4 consolidation (2026-07). See
> [`docs/internal/DISCOVERY-ENGINE-USAGE.md`](internal/DISCOVERY-ENGINE-USAGE.md).

---

## Architecture Commands

Design, analysis, and architectural planning tools.

### /craft:arch:analyze

**Category**: Code Analysis | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Analyze system architecture and identify patterns

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | string | No | `.` | Directory to analyze |
| `mode` | enum | No | `default` | Execution mode |
| `--output` | string | No | stdout | Save output to file |

#### Examples

```bash
/craft:arch:analyze
/craft:arch:analyze src/ optimize
/craft:arch:analyze --output architecture-report.md
```

**File**: `commands/arch/analyze.md`

---

### /craft:arch:diagram

**Category**: Visualization | **Complexity**: Moderate | **Time**: 1-3 min
**Description**: Generate architecture diagrams (Mermaid format)

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | enum | No | `system` | Diagram type: `system`, `dataflow`, `class`, `sequence` |
| `output` | string | No | stdout | Save diagram to file |

#### Examples

```bash
/craft:arch:diagram
/craft:arch:diagram dataflow
/craft:arch:diagram sequence --output workflow.mmd
```

**File**: `commands/arch/diagram.md`

---

### /craft:arch:plan

**Category**: Planning | **Complexity**: Moderate | **Time**: 2-4 hours
**Description**: Plan architectural changes and migrations

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scope` | string | Yes | - | What to plan |
| `timeline` | string | No | `flexible` | Timeline: `urgent`, `normal`, `flexible` |

#### Examples

```bash
/craft:arch:plan "migrate to microservices"
/craft:arch:plan "add caching layer" normal
```

**File**: `commands/arch/plan.md`

---

### /craft:arch:review

**Category**: Code Review | **Complexity**: Moderate | **Time**: 1-2 min
**Description**: Review architectural decisions and patterns

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | string | No | `.` | File or directory to review |
| `--detailed` | boolean | No | false | Show detailed analysis |

#### Examples

```bash
/craft:arch:review
/craft:arch:review src/auth --detailed
```

**File**: `commands/arch/review.md`

---

## Code Commands

Development workflow and code manipulation tools.

### /craft:code:lint

**Category**: Quality | **Complexity**: Simple | **Time**: < 30s
**Description**: Code style and quality checks with mode support

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `mode` | enum | No | `default` | `default`, `debug`, `optimize`, `release` |
| `path` | string | No | `.` | File or directory to lint |
| `--dry-run` | boolean | No | false | Preview without executing |
| `-n` | boolean | No | false | Alias for `--dry-run` |
| `--fix` | boolean | No | false | Auto-fix issues |

#### Modes

| Mode | Time | Focus |
|------|------|-------|
| `default` | < 10s | Quick style check |
| `debug` | < 120s | All rules + suggestions |
| `optimize` | < 180s | Performance rules |
| `release` | < 300s | Comprehensive + strict |

#### Examples

```bash
/craft:code:lint
/craft:code:lint debug
/craft:code:lint release src/
/craft:code:lint --dry-run --fix
```

#### Output

```text
🔍 CODE LINTING

  Style Issues: 3
    ⚠ Line 45: Missing docstring
    ⚠ Line 89: Unused import

  Quality Issues: 1
    ✓ No complexity violations
```

**File**: `commands/code/lint.md`

---

### /craft:code:refactor

**Category**: Development | **Complexity**: Moderate | **Time**: 5-20 min
**Description**: Automated refactoring with safety checks

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `pattern` | string | Yes | - | Refactoring pattern to apply |
| `path` | string | No | `.` | Target directory |
| `--dry-run` | boolean | No | false | Preview changes |
| `--no-test` | boolean | No | false | Skip running tests |

#### Examples

```bash
/craft:code:refactor "rename getCwd to getCurrentWorkingDirectory"
/craft:code:refactor "extract method processData" src/ --dry-run
```

**File**: `commands/code/refactor.md`

---

### /craft:code:test-gen

**Category**: Testing | **Complexity**: Simple | **Time**: 1-5 min
**Description**: Generate test stubs and templates

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | enum | No | `unit` | Test type: `unit`, `integration`, `e2e` |
| `source` | string | No | `.` | Source file to generate tests for |

#### Examples

```bash
/craft:code:test-gen
/craft:code:test-gen unit src/auth.ts
/craft:code:test-gen integration
```

**File**: `commands/code/test-gen.md`

---

### /craft:code:debug

**Category**: Development | **Complexity**: Moderate | **Time**: 5-10 min
**Description**: Debugging tools and trace analysis

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `command` | string | Yes | - | Command to debug |
| `--verbose` | boolean | No | false | Verbose trace output |
| `--breakpoint` | string | No | - | Set breakpoint at line |

#### Examples

```bash
/craft:code:debug "npm start"
/craft:code:debug "python script.py" --verbose
```

**File**: `commands/code/debug.md`

---

### /craft:code:demo

**Category**: Documentation | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Record and generate terminal demos (GIFs/asciinema)

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `script` | string | Yes | - | Demo script file |
| `format` | enum | No | `gif` | Output: `gif`, `asciinema`, `svg` |
| `--speed` | number | No | 1.0 | Playback speed multiplier |

#### Examples

```bash
/craft:code:demo scripts/demo-auth.sh
/craft:code:demo scripts/intro.sh gif --speed 1.5
/craft:code:demo test-run.sh asciinema
```

**File**: `commands/code/demo.md`

---

### /craft:test --coverage

**Category**: Testing | **Complexity**: Simple | **Time**: 1-3 min
**Description**: Analyze and report test coverage

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `mode` | enum | No | `default` | Execution mode |
| `--threshold` | number | No | 80 | Minimum coverage percentage |
| `--report` | enum | No | stdout | Report format: `text`, `html`, `json` |

#### Examples

```bash
/craft:test --coverage
/craft:test --coverage --threshold 85
/craft:test --coverage --report html
```

**File**: `commands/code/coverage.md`

---

### /craft:code:deps-check

**Category**: Maintenance | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Check for outdated and vulnerable dependencies

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--fix` | boolean | No | false | Auto-update fixable issues |
| `--security` | boolean | No | false | Focus on security vulnerabilities |

#### Examples

```bash
/craft:code:deps-check
/craft:code:deps-check --security
/craft:code:deps-check --fix
```

**File**: `commands/code/deps-check.md`

---

### /craft:code:deps-audit

**Category**: Maintenance | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Detailed dependency audit and licensing analysis

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--licenses` | boolean | No | false | Include license analysis |
| `--tree` | boolean | No | false | Show dependency tree |

#### Examples

```bash
/craft:code:deps-audit
/craft:code:deps-audit --licenses --tree
```

**File**: `commands/code/deps-audit.md`

---

### /craft:ci:local

**Category**: CI/CD | **Complexity**: Simple | **Time**: < 60s
**Description**: Run CI checks locally before committing

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--dry-run` | boolean | No | false | Preview without running |

#### Examples

```bash
/craft:ci:local
/craft:ci:local --dry-run
```

**File**: `commands/ci/local.md`

---

### /craft:ci:fix

**Category**: CI/CD | **Complexity**: Simple | **Time**: < 60s
**Description**: Fix common CI failures locally

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `issue` | string | No | - | Specific issue to fix |
| `--apply` | boolean | No | false | Auto-apply fixes |

#### Examples

```bash
/craft:ci:fix
/craft:ci:fix "lint errors" --apply
```

**File**: `commands/ci/fix.md`

---

### /craft:code:docs-check

**Category**: Documentation | **Complexity**: Simple | **Time**: < 30s
**Description**: Validate code documentation completeness

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--strict` | boolean | No | false | Enforce all doc requirements |
| `--fix` | boolean | No | false | Auto-add missing docs |

#### Examples

```bash
/craft:code:docs-check
/craft:code:docs-check --strict
/craft:code:docs-check --fix
```

**File**: `commands/code/docs-check.md`

---

### /craft:code:release

**Category**: Release | **Complexity**: Complex | **Time**: 5-20 min
**Description**: Prepare and execute release workflow

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `version` | string | No | - | Version to release (auto-detect if omitted) |
| `--dry-run` | boolean | No | false | Preview release steps |
| `--skip-tests` | boolean | No | false | Skip test execution |

#### Examples

```bash
/craft:code:release
/craft:code:release 1.0.0
/craft:code:release --dry-run
```

**File**: `commands/code/release.md`

---

## CI/CD Commands

Continuous integration and deployment automation.

### /craft:ci:generate

**Category**: Automation | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Generate CI workflow files for GitHub Actions, GitLab, etc.

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `platform` | enum | No | `github` | CI platform: `github`, `gitlab`, `circle`, `travis` |
| `template` | string | No | `default` | Workflow template |
| `--output` | string | No | auto | Save to specific path |

#### Examples

```bash
/craft:ci:generate
/craft:ci:generate gitlab
/craft:ci:generate github custom-workflow
```

**File**: `commands/ci/generate.md`

---

### /craft:ci:detect

**Category**: Analysis | **Complexity**: Simple | **Time**: < 30s
**Description**: Auto-detect best CI platform for project

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--recommended` | boolean | No | false | Show recommendation with reasoning |

#### Examples

```bash
/craft:ci:detect
/craft:ci:detect --recommended
```

**File**: `commands/ci/detect.md`

---

### /craft:ci:validate

**Category**: Validation | **Complexity**: Simple | **Time**: < 60s
**Description**: Validate CI workflow files for syntax and best practices

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | string | No | auto | Workflow file to validate |
| `--strict` | boolean | No | false | Enforce best practices |

#### Examples

```bash
/craft:ci:validate
/craft:ci:validate .github/workflows/main.yml --strict
```

**File**: `commands/ci/validate.md`

---

## Check Commands

Pre-flight validation and quality gates.

### /craft:check:gen-validator

**Category**: Development | **Complexity**: Moderate | **Time**: 1-3 min
**Description**: Generate custom validators for hot-reload validation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | enum | Yes | - | Validator type: `lint`, `test`, `link` |
| `--output` | string | No | auto | Save validator to file |

#### Examples

```bash
/craft:check:gen-validator lint
/craft:check:gen-validator test --output custom-validator.js
```

**File**: `commands/check/gen-validator.md`

---

## Distribution Commands

Release, packaging, and distribution workflows.

### /craft:dist:pypi

**Category**: Release | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Publish Python packages to PyPI

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `version` | string | No | from manifest | Version to publish |
| `--dry-run` | boolean | No | false | Preview without publishing |
| `--test` | boolean | No | false | Publish to TestPyPI first |

#### Examples

```bash
/craft:dist:pypi
/craft:dist:pypi 1.0.0
/craft:dist:pypi --dry-run
/craft:dist:pypi --test
```

**File**: `commands/dist/pypi.md`

---

### /craft:dist:homebrew

**Category**: Release | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Update Homebrew formula for releases

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `version` | string | No | latest tag | Specific version to use |
| `tap` | string | No | auto-detect | Homebrew tap name |

#### Examples

```bash
/craft:dist:homebrew
/craft:dist:homebrew 1.5.0
/craft:dist:homebrew 2.0.0 --tap data-wise/tap
```

**File**: `commands/dist/homebrew.md`

---

### /craft:dist:curl-install

**Category**: Release | **Complexity**: Moderate | **Time**: 1-3 min
**Description**: Generate curl-based installation script

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--output` | string | No | `install.sh` | Save script to file |
| `--hosting` | string | No | auto | Where script is hosted |

#### Examples

```bash
/craft:dist:curl-install
/craft:dist:curl-install --output setup.sh
```

**File**: `commands/dist/curl-install.md`

---

### /craft:dist:marketplace

Marketplace distribution management — init, validate, test, publish.

```bash
/craft:dist:marketplace              # Validate (default)
/craft:dist:marketplace init         # Generate marketplace.json
/craft:dist:marketplace test         # Local install/uninstall cycle
/craft:dist:marketplace publish      # Push for marketplace availability
```

**Subcommands:** init, validate (default), test, publish
**Integration:** `/release` auto-bumps marketplace.json version

---

## Documentation Commands

Documentation generation, maintenance, and publication.

### /folio:docs:api

**Category**: Reference | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Generate API documentation from code

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `format` | enum | No | `openapi` | Format: `openapi`, `swagger`, `markdown` |
| `--output` | string | No | auto | Save to file |

#### Examples

```bash
/folio:docs:api
/folio:docs:api swagger --output api-spec.yaml
```

**File**: `commands/docs/api.md`

---

### /craft:docs:changelog

**Category**: Release | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Generate changelog from commits

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--from` | string | No | last tag | From commit/tag |
| `--to` | string | No | HEAD | To commit/tag |
| `--format` | enum | No | `markdown` | Output format |

#### Examples

```bash
/craft:docs:changelog
/craft:docs:changelog --from v1.0.0 --to v1.1.0
/craft:docs:changelog --format json
```

**File**: `commands/docs/changelog.md`

---

### /folio:docs:check-links

**Category**: Validation | **Complexity**: Simple | **Time**: 1-3 min
**Description**: Validate all documentation links

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--external` | boolean | No | false | Check external URLs too |
| `--fix` | boolean | No | false | Auto-fix broken links |

#### Examples

```bash
/folio:docs:check-links
/folio:docs:check-links --external
/folio:docs:check-links --fix
```

**File**: `commands/docs/check-links.md`

---

### /folio:docs:check

**Category**: Validation | **Complexity**: Simple | **Time**: < 60s
**Description**: Validate documentation completeness

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--strict` | boolean | No | false | Enforce strict requirements |

#### Examples

```bash
/folio:docs:check
/folio:docs:check --strict
```

**File**: `commands/docs/check.md`

---

### /craft:docs:claude-md

**Category**: Integration | **Complexity**: Simple | **Time**: < 30s
**Description**: Update CLAUDE.md project instructions

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--sync` | boolean | No | true | Sync global + local instructions |

#### Examples

```bash
/craft:docs:claude-md
/craft:docs:claude-md --sync
```

**File**: `commands/docs/claude-md.md`

---

### /folio:docs:demo

**Category**: Content | **Complexity**: Moderate | **Time**: 1-5 min
**Description**: Generate demo documentation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | enum | No | `command` | Demo type: `command`, `feature`, `workflow` |

#### Examples

```bash
/folio:docs:demo
/folio:docs:demo feature
```

**File**: `commands/docs/demo.md`

---

### /folio:docs:guide

**Category**: Content | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Generate step-by-step guides

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Topic for the guide |
| `level` | enum | No | `beginner` | Level: `beginner`, `intermediate`, `advanced` |

#### Examples

```bash
/folio:docs:guide "setting up authentication"
/folio:docs:guide "advanced testing" intermediate
```

**File**: `commands/docs/guide.md`

---

### /folio:docs:help

**Category**: Reference | **Complexity**: Simple | **Time**: < 30s
**Description**: Generate command help documentation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--include-examples` | boolean | No | true | Include usage examples |

#### Examples

```bash
/folio:docs:help
/folio:docs:help --no-examples
```

**File**: `commands/docs/help.md`

---

### /folio:docs:lint

**Category**: Validation | **Complexity**: Simple | **Time**: < 60s
**Description**: Lint documentation for style and consistency

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--fix` | boolean | No | false | Auto-fix style issues |

#### Examples

```bash
/folio:docs:lint
/folio:docs:lint --fix
```

**File**: `commands/docs/lint.md`

---

### /folio:docs:mermaid

**Category**: Visualization | **Complexity**: Moderate | **Time**: 1-3 min
**Description**: Generate Mermaid diagrams for documentation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | enum | Yes | - | Diagram type: `flowchart`, `sequence`, `erd`, `gantt` |
| `--interactive` | boolean | No | false | Generate interactive diagram |

#### Examples

```bash
/folio:docs:mermaid flowchart
/folio:docs:mermaid sequence --interactive
```

**File**: `commands/docs/mermaid.md`

---

### /folio:docs:nav-update

**Category**: Site | **Complexity**: Simple | **Time**: < 30s
**Description**: Update documentation site navigation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--auto` | boolean | No | true | Auto-detect structure |

#### Examples

```bash
/folio:docs:nav-update
/folio:docs:nav-update --manual
```

**File**: `commands/docs/nav-update.md`

---

### /folio:docs:prompt

**Category**: Development | **Complexity**: Simple | **Time**: < 30s
**Description**: Generate system prompts for documentation tasks

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `task` | string | Yes | - | Documentation task |

#### Examples

```bash
/folio:docs:prompt "write API reference for authentication"
/folio:docs:prompt "create getting started guide"
```

**File**: `commands/docs/prompt.md`

---

### /folio:docs:quickstart

**Category**: Content | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Generate quick-start guides

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Quick-start topic |

#### Examples

```bash
/folio:docs:quickstart "setting up a new project"
/folio:docs:quickstart "deploying to production"
```

**File**: `commands/docs/quickstart.md`

---

### /folio:docs:site

**Category**: Site | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Manage documentation website

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | enum | Yes | - | Action: `build`, `deploy`, `preview`, `serve` |

#### Examples

```bash
/folio:docs:site build
/folio:docs:site deploy
/folio:docs:site preview
/folio:docs:site serve
```

**File**: `commands/docs/site.md`

---

### /folio:docs:sync

**Category**: Maintenance | **Complexity**: Simple | **Time**: < 60s
**Description**: Sync documentation with code

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--fix` | boolean | No | false | Auto-fix discrepancies |

#### Examples

```bash
/folio:docs:sync
/folio:docs:sync --fix
```

**File**: `commands/docs/sync.md`

---

### /folio:docs:tutorial

**Category**: Content | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Generate interactive tutorials

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Tutorial topic |
| `interactive` | boolean | No | false | Include interactive elements |

#### Examples

```bash
/folio:docs:tutorial "authentication workflow"
/folio:docs:tutorial "testing best practices" --interactive
```

**File**: `commands/docs/tutorial.md`

---

### /craft:docs:update

**Category**: Maintenance | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Update documentation metadata and headers

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--all` | boolean | No | false | Update all documentation files |
| `--field` | string | No | - | Update specific field |

#### Examples

```bash
/craft:docs:update
/craft:docs:update --all
/craft:docs:update --field version
```

**File**: `commands/docs/update.md`

---

### /folio:docs:workflow

**Category**: Workflow | **Complexity**: Simple | **Time**: < 30s
**Description**: Document development workflows

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `workflow` | string | Yes | - | Workflow name to document |

#### Examples

```bash
/folio:docs:workflow "feature development"
/folio:docs:workflow "release process"
```

**File**: `commands/docs/workflow.md`

---

### /folio:docs:website

**Category**: Site | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Manage overall website structure

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | string | Yes | - | Action: `init`, `add`, `remove`, `restructure` |

#### Examples

```bash
/folio:docs:website init
/folio:docs:website add "new section"
```

**File**: `commands/docs/website.md`

---

## Git Commands

Version control and collaboration workflows.

### /craft:git:status

**Category**: Inspection | **Complexity**: Simple | **Time**: < 5s
**Description**: Show enhanced git status with suggestions

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--detailed` | boolean | No | false | Show detailed information |
| `--suggest` | boolean | No | true | Show suggested next actions |

#### Examples

```bash
/craft:git:status
/craft:git:status --detailed
```

**File**: `commands/git/status.md`

---

### /craft:git:branch

**Category**: Branching | **Complexity**: Simple | **Time**: < 30s
**Description**: Create and manage feature branches

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | enum | Yes | - | Action: `create`, `list`, `delete`, `rename` |
| `name` | string | No | - | Branch name |
| `--type` | enum | No | `feature` | Type: `feature`, `hotfix`, `release` |

#### Examples

```bash
/craft:git:branch create my-feature
/craft:git:branch list
/craft:git:branch delete old-branch
```

**File**: `commands/git/branch.md`

---

### /craft:git:worktree

**Category**: Workflow | **Complexity**: Moderate | **Time**: 1-5 min
**Description**: Git worktree management for parallel development

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | enum | Yes | - | Action: `setup`, `create`, `move`, `list`, `clean`, `install`, `finish` |
| `branch` | string | No | - | Branch name |
| `--dry-run` | boolean | No | false | Preview changes |

#### Examples

```bash
/craft:git:worktree setup
/craft:git:worktree create feature/auth
/craft:git:worktree list
/craft:git:worktree finish
```

**File**: `commands/git/worktree.md`

---

### /craft:git:clean

**Category**: Maintenance | **Complexity**: Simple | **Time**: < 30s
**Description**: Clean up merged branches and stale refs

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--dry-run` | boolean | No | false | Preview cleanup |
| `--remote` | boolean | No | false | Clean remote branches too |

#### Examples

```bash
/craft:git:clean
/craft:git:clean --dry-run
/craft:git:clean --remote
```

**File**: `commands/git/clean.md`

---

### /craft:git:docs:refcard

**Category**: Documentation | **Complexity**: Simple | **Time**: < 5 min
**Description**: Git quick reference card

#### Examples

```bash
/craft:git:docs refcard
```

**File**: `commands/git/docs/refcard.md`

---

## Plan Commands

Project planning and roadmap tools.

### /craft:plan:feature

**Category**: Planning | **Complexity**: Moderate | **Time**: 1-2 hours
**Description**: Plan feature development with breakdown

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `feature` | string | Yes | - | Feature name |
| `--timeline` | string | No | `flexible` | Timeline: `urgent`, `normal`, `flexible` |
| `--scope` | enum | No | `medium` | Scope: `small`, `medium`, `large` |

#### Examples

```bash
/craft:plan:feature "user authentication"
/craft:plan:feature "payment integration" --timeline urgent --scope large
```

**File**: `commands/plan/feature.md`

---

> Sprint planning and roadmap generation (formerly `/craft:plan:sprint` and
> `/craft:plan:roadmap`) were folded into the `plan-orchestrator` skill
> (Modes 3–4) in the v4 command consolidation (2026-07). Invoke `/craft:plan`
> and describe the sprint/roadmap need, or read
> [`skills/orchestration/plan-orchestrator/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/orchestration/plan-orchestrator/SKILL.md).

---

## Site Commands

Static site generation and website management.

### /folio:site:build

**Category**: Build | **Complexity**: Simple | **Time**: 1-3 min
**Description**: Build static site

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--production` | boolean | No | false | Build for production |
| `--minify` | boolean | No | false | Minify assets |

#### Examples

```bash
/folio:site:build
/folio:site:build --production --minify
```

**File**: `commands/site/build.md`

---

### /craft:site:deploy

**Category**: Release | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Deploy site to hosting

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `platform` | enum | No | `github-pages` | Platform: `github-pages`, `netlify`, `vercel`, `s3` |
| `--dry-run` | boolean | No | false | Preview deployment |

#### Examples

```bash
/craft:site:deploy
/craft:site:deploy netlify
/craft:site:deploy s3 --dry-run
```

**File**: `commands/site/deploy.md`

---

### /folio:site:publish

**Category**: Release | **Complexity**: Moderate | **Time**: 2-5 min
**Description**: Publish site (build + deploy)

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--skip-build` | boolean | No | false | Skip build step |

#### Examples

```bash
/folio:site:publish
/folio:site:publish --skip-build
```

**File**: `commands/site/publish.md`

---

### /folio:site:check

**Category**: Validation | **Complexity**: Simple | **Time**: < 60s
**Description**: Validate site configuration and content

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--strict` | boolean | No | false | Strict validation |

#### Examples

```bash
/folio:site:check
/folio:site:check --strict
```

**File**: `commands/site/check.md`

---

### /folio:site:update

**Category**: Maintenance | **Complexity**: Simple | **Time**: 1-2 min
**Description**: Update site configuration and dependencies

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--dry-run` | boolean | No | false | Preview updates |

#### Examples

```bash
/folio:site:update
/folio:site:update --dry-run
```

**File**: `commands/site/update.md`

---

### /folio:site:status

**Category**: Inspection | **Complexity**: Simple | **Time**: < 30s
**Description**: Show site build status

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--details` | boolean | No | false | Show detailed info |

#### Examples

```bash
/folio:site:status
/folio:site:status --details
```

**File**: `commands/site/status.md`

---

### /folio:site:progress

**Category**: Inspection | **Complexity**: Simple | **Time**: < 30s
**Description**: Show site completion progress

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--breakdown` | boolean | No | false | Show breakdown by section |

#### Examples

```bash
/folio:site:progress
/folio:site:progress --breakdown
```

**File**: `commands/site/progress.md`

---

## Test Commands

Testing, quality assurance, and verification tools.

### /craft:test

**Category**: Execution | **Complexity**: Simple | **Time**: < 60s
**Description**: Unified test runner with mode support

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `mode` | enum | No | `default` | `default`, `debug`, `optimize`, `release` |
| `path` | string | No | `.` | Test file or directory |
| `--filter` | string | No | - | Test name filter pattern |
| `--dry-run` | boolean | No | false | Preview test plan |

#### Modes

| Mode | Time | Focus |
|------|------|-------|
| `default` | < 30s | Quick smoke tests |
| `debug` | < 120s | Verbose with traces |
| `optimize` | < 180s | Parallel execution |
| `release` | < 300s | Full test suite |

#### Examples

```bash
/craft:test
/craft:test debug
/craft:test optimize tests/
/craft:test --filter auth
```

**File**: `commands/test.md`

---

### /craft:test:gen

**Category**: Development | **Complexity**: Simple | **Time**: 1-3 min
**Description**: Generate test suites with project-type detection

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `project-type` | enum | No | auto | `plugin`, `zsh`, `cli`, `mcp` |
| `--tier` | enum | No | `all` | `smoke`, `unit`, `integration`, `e2e`, `all` |
| `--output` | string | No | `tests/` | Output directory |
| `--force` | boolean | No | false | Overwrite existing |
| `--dry-run` | boolean | No | false | Preview generation plan |

#### Examples

```bash
/craft:test:gen
/craft:test:gen plugin
/craft:test:gen --tier unit
/craft:test:gen --dry-run
```

**File**: `commands/test/gen.md`

---

### /craft:test:template

**Category**: Development | **Complexity**: Simple | **Time**: < 30s
**Description**: Manage Jinja2 templates for test generation

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `action` | enum | Yes | - | `list`, `show`, `validate`, `render`, `create`, `edit`, `delete` |
| `template` | string | No | - | Template path (e.g., `plugin/test_structure`) |
| `--type` | enum | No | - | `plugin`, `zsh`, `cli`, `mcp`, `_base` |

#### Examples

```bash
/craft:test:template list
/craft:test:template show plugin/test_structure
/craft:test:template validate
```

**File**: `commands/test/template.md`

---

## Workflow Commands

Development workflow and productivity tools.

### /craft:brainstorm

**Category**: Planning | **Complexity**: Moderate | **Time**: 10-30 min
**Description**: ADHD-friendly brainstorming for feature development

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Topic to brainstorm |
| `--duration` | number | No | 20 | Session duration (minutes) |
| `--save` | boolean | No | true | Save to file |

#### Examples

```bash
/craft:brainstorm "new authentication system"
/craft:brainstorm "API redesign" --duration 30 --save
```

**File**: `commands/brainstorm.md`

---

### /craft:next

**Category**: Planning | **Complexity**: Simple | **Time**: < 5 min
**Description**: Get next action suggestion

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--context` | string | No | auto | Current context |

#### Examples

```bash
/craft:next
/craft:next --context "feature-auth"
```

**File**: `commands/next.md`

---

### /craft:done

**Category**: Completion | **Complexity**: Simple | **Time**: 1-3 min
**Description**: Complete task with cleanup and summary

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--message` | string | No | - | Completion message |
| `--commit` | boolean | No | true | Commit changes |

#### Examples

```bash
/craft:done
/craft:done --message "feat: add auth"
/craft:done --no-commit
```

**File**: `commands/done.md`

---

### /craft:refine

**Category**: Planning | **Complexity**: Simple | **Time**: 5-10 min
**Description**: Refine task definition and scope

#### Arguments

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `task` | string | Yes | - | Task to refine |

#### Examples

```bash
/craft:refine "implement caching"
```

**File**: `commands/refine.md`

---

## Utility Commands

Helper utilities and reference tools.

> `readme-teach-config` and `readme-semester-progress` (teaching-residue commands) were
> removed in the v4 command consolidation (2026-07) — no replacement, no longer needed.

---

## Common Patterns

### Error Responses

All commands follow consistent error response patterns:

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "Human readable message",
  "suggestion": "How to fix it",
  "details": {}
}
```

### Mode System

All commands support execution modes:

- **default**: Balanced, quick execution
- **debug**: Verbose output, detailed traces
- **optimize**: Performance optimized
- **release**: Comprehensive validation

### Dry-Run Pattern

Commands that make changes support `--dry-run` or `-n`:

```bash
/craft:code:lint --dry-run        # Preview changes
/craft:git:clean --dry-run        # Preview branch cleanup
/craft:site:deploy --dry-run      # Preview deployment
```

### Output Formats

Commands support multiple output formats:

- `text` - Human readable (default)
- `json` - Machine readable
- `markdown` - Markdown formatted
- `html` - HTML formatted

---

## Command Dependencies

### Related Commands

| If you want to... | Try these commands |
|------|---|
| Create a feature | `/craft:plan:feature` → `/craft:git:worktree` → `/craft:code:test-gen` |
| Release a project | `/craft:code:lint` → `/craft:test release` → `/craft:code:release` |
| Document code | `/folio:docs:api` → `/folio:docs:guide` → `/folio:docs:site publish` |
| Debug issues | `/craft:code:debug` → `/craft:test debug` |

---

## Performance Notes

### Execution Time Estimates

| Complexity | Typical Time | Example |
|-----------|--------------|---------|
| Simple | < 30s | `/craft:git:status`, `/craft:code:lint` |
| Moderate | 1-5 min | `/craft:test`, `/folio:docs:api` |
| Complex | 5-30 min | `/craft:plan:feature`, `/craft:orch` |

### Optimization Tips

1. Use `--dry-run` to preview changes before executing
2. Use appropriate `mode` for your use case
3. Filter tests/files with `--filter` and `path` arguments
4. Run linting/tests frequently to catch issues early
5. Use worktrees for parallel development

---

## Next Steps

1. **Get Started**: See [Quick Start Guide](./QUICK-START.md)
2. **Learn Commands**: Use `/craft:hub` for interactive discovery
3. **Deep Dives**: Check individual command documentation in `commands/` directory
4. **Examples**: See `cookbook/` for real-world usage patterns
5. **Troubleshooting**: See individual command documentation for troubleshooting tips

---

**Last Updated**: January 17, 2026 | **Version**: v1.24.0 | **Status**: Complete (97/97 commands documented)
