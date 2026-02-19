---
description: Unified test runner with category filtering and modes
arguments:
  - name: category
    description: "Test category filter: unit, integration, e2e, smoke, or domain marker (hub, claude_md, etc.)"
    required: false
  - name: mode
    description: Execution mode (default|debug|optimize|release)
    required: false
    default: default
  - name: path
    description: Test file or directory to run
    required: false
  - name: filter
    description: Test name filter pattern (-k flag)
    required: false
  - name: coverage
    description: Enable coverage reporting
    required: false
    default: false
  - name: watch
    description: Re-run tests on file changes
    required: false
    default: false
  - name: dry-run
    description: Preview test execution plan without running
    required: false
    default: false
    alias: -n
---

# /craft:test - Unified Test Runner

Run, debug, measure coverage, and watch tests with a single command. Replaces the
old `test:run`, `test:coverage`, `test:debug`, and `test:watch` commands.

## Quick Start

```bash
/craft:test                         # Run all tests (default mode)
/craft:test unit                    # Run only unit tests
/craft:test e2e                     # Run only e2e tests
/craft:test hub                     # Run only hub domain tests
/craft:test --coverage              # Run with coverage report
/craft:test --watch                 # Watch mode
/craft:test debug                   # Debug mode (verbose traces)
/craft:test unit --filter="auth"    # Unit tests matching "auth"
/craft:test --dry-run               # Preview execution plan
```

## Category Filtering

Filter tests by tier or domain using pytest markers defined in `pyproject.toml`:

### Tiers (mutually exclusive)

| Tier | Marker | Count | Speed |
|------|--------|-------|-------|
| `unit` | `@pytest.mark.unit` | ~489 | < 2s |
| `integration` | `@pytest.mark.integration` | ~568 | < 30s |
| `e2e` | `@pytest.mark.e2e` | ~333 | < 60s |
| `smoke` | `@pytest.mark.smoke` | subset | < 30s |

### Domains (combinable with tiers)

| Domain | Tests For |
|--------|-----------|
| `hub` | Hub discovery, display, layers |
| `claude_md` | CLAUDE.md sync, audit, fix |
| `branch_guard` | Branch protection hooks |
| `orchestrator` | Orchestrator workflows |
| `teaching` | Teaching mode and config |
| `commands` | Command parsing, discovery |
| `structure` | Plugin structure validation |
| `docs` | Documentation link checking |
| `badge` | Badge detection and syncing |
| `brainstorm` | Brainstorm context |
| `release` | Release pipeline |
| `marketplace` | Marketplace distribution |
| `formatting` | Box-drawing, ANSI |
| `dependency` | Dependency management |
| `site` | Site publishing |

### Combining Filters

```bash
/craft:test "unit and hub"          # Unit tests for hub only
/craft:test "integration and not slow"  # Fast integration tests
/craft:test "e2e and branch_guard"  # Branch guard e2e only
```

## Modes

| Mode | Budget | pytest Flags | Use Case |
|------|--------|-------------|----------|
| **default** | < 30s | `-x -q --tb=short` | Quick smoke check |
| **debug** | < 120s | `-v --tb=long --capture=no` | Verbose traces |
| **optimize** | < 180s | `-n auto --dist loadfile` | Parallel execution |
| **release** | < 300s | `--cov --cov-report=term -v --maxfail=5` | Full suite + coverage |

```bash
/craft:test                         # default mode
/craft:test debug                   # verbose with traces
/craft:test optimize                # parallel execution
/craft:test release                 # full suite + coverage
/craft:test unit debug              # unit tests with verbose output
```

## Coverage Mode

```bash
/craft:test --coverage              # Coverage report to terminal
/craft:test --coverage --report html  # HTML report (htmlcov/)
/craft:test unit --coverage         # Coverage for unit tests only
```

Coverage output:

```
Coverage Report
File                     Lines   Branch
tests/test_craft.py       95%     88%
tests/test_hub.py         72%     65%
TOTAL                     87%     82%
```

## Watch Mode

```bash
/craft:test --watch                 # Watch all tests
/craft:test unit --watch            # Watch unit tests only
/craft:test hub --watch             # Watch hub tests only
```

Watch mode re-runs affected tests when source files change. Press `q` to quit.

## Debug Mode

```bash
/craft:test debug                   # Full debug output
/craft:test debug --pdb             # Drop into debugger on failure
/craft:test debug --last            # Re-run last failed tests
```

Debug mode enables:

- Full stack traces with local variables
- No output capture (`--capture=no`)
- Verbose test names with timing

## Dry-Run

```bash
/craft:test --dry-run               # Preview default mode
/craft:test release -n              # Preview release mode
/craft:test unit -n                 # Preview unit tier
```

Shows: project type detection, test discovery count, pytest command to execute,
estimated time, and mode-specific flags.

## Execution Behavior

When this command runs:

1. **Detect project** - Find test framework (pytest for this project)
2. **Build command** - Assemble pytest invocation from mode + category + flags
3. **Show plan** - If `--dry-run`, show plan and stop
4. **Execute** - Run tests with selected configuration
5. **Report** - Show results with mode-appropriate formatting

### pytest Command Construction

```python
# Base command
cmd = ["python3", "-m", "pytest", "tests/"]

# Add mode flags
if mode == "default":
    cmd += ["-x", "-q", "--tb=short"]
elif mode == "debug":
    cmd += ["-v", "--tb=long", "--capture=no"]
elif mode == "optimize":
    cmd += ["-n", "auto", "--dist", "loadfile"]
elif mode == "release":
    cmd += ["--cov", "--cov-report=term", "-v", "--maxfail=5"]

# Add category filter
if category:
    cmd += ["-m", category]

# Add name filter
if filter:
    cmd += ["-k", filter]

# Add coverage
if coverage:
    cmd += ["--cov", "--cov-report=term"]

# Add path
if path:
    cmd[-1] = path  # Replace tests/ with specific path
```

## Examples

```bash
# Quick validation before commit
/craft:test unit

# Debug a specific failing test
/craft:test debug --filter="test_plugin_json"

# Full pre-release validation
/craft:test release

# Domain-specific during development
/craft:test hub
/craft:test claude_md
/craft:test branch_guard

# Combined filter
/craft:test "integration and orchestrator" debug

# Run specific file
/craft:test tests/test_craft_plugin.py

# Run bash tests too (release mode includes them)
/craft:test release  # Runs pytest + bash test scripts
```

## Integration

- `/craft:test:gen` - Generate test suites
- `/craft:test:template` - Manage test templates
- `/craft:check` - Pre-flight validation (includes test run)
- `/craft:code:ci-local` - CI checks
