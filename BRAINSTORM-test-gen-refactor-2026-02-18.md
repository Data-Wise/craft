# Test Generation Refactor - Brainstorm

**Generated:** 2026-02-18
**Context:** craft plugin, `/craft:test:*` commands
**Depth:** max | **Focus:** feature | **Action:** save

## Overview

Refactor Craft's test generation and execution infrastructure from 7 overlapping commands + 2 skills into a clean 2-command system (`/craft:test` and `/craft:test:gen`) with first-class support for 4 project types: Claude Code plugins, ZSH plugins, Python CLIs, and MCP servers. Add automatic CI-ready tests and interactive QA, with full lifecycle e2e and dogfood testing.

---

## Current State Analysis

### What Exists (7 Commands + 2 Skills)

| Command | Purpose | Overlap |
|---------|---------|---------|
| `test:run` | Unified test runner | Core keeper |
| `test:generate` | Generate dogfood tests | Overlaps with cli-gen |
| `test:cli-gen` | Generate CLI test suites | Overlaps with generate |
| `test:cli-run` | Run CLI test suites | Overlaps with run |
| `test:coverage` | Coverage analysis | Mode of run |
| `test:debug` | Debug failing tests | Mode of run |
| `test:watch` | Watch mode | Mode of run |

**Skills:** `test-generator` (duplicates `test:generate`), `test-strategist` (advisory only)

### Problems

1. **7 commands when 2 would do** — `cli-gen` vs `generate` is confusing; `cli-run`, `coverage`, `debug`, `watch` are modes of `run`
2. **3 test frameworks** — pytest, unittest, custom CheckResult pattern across 70 test files
3. **No pytest config** — can't filter by markers (`-m dogfood`, `-m smoke`)
4. **Generated tests are generic** — same bash scripts regardless of project type
5. **Missing project types** — no ZSH plugin, MCP server, or Quarto support
6. **~31% command coverage** — only 25 of 80 commands have direct tests
7. **No shared test helpers** — each file reimplements path resolution, file reading, subprocess wrappers
8. **No snapshot tests** — formatting output regressions go undetected
9. **No property-based tests** — parsers and validators untested for edge cases

### What Works Well

- Dogfood pattern (`*_dogfood.py`) — tests against real installed state
- E2E bash scripts — thorough, good assertion patterns
- Interactive test concept — valuable for visual QA
- Project type detection in `test:generate` — good foundation

---

## Proposed Architecture

### Command Surface: 2 Commands

```
/craft:test [mode] [filter] [options]    # Run tests
/craft:test:gen [type] [options]         # Generate tests
```

### /craft:test — Unified Runner

Absorbs: `test:run`, `test:cli-run`, `test:coverage`, `test:debug`, `test:watch`

```bash
# Basic usage (auto-detect project, run all)
/craft:test

# By category (pytest markers)
/craft:test smoke              # Critical path only (< 2 min)
/craft:test unit               # Unit tests (< 5 min)
/craft:test integration        # Integration tests (< 15 min)
/craft:test e2e                # End-to-end tests (< 30 min)
/craft:test dogfood            # Self-testing (< 10 min)

# By mode (execution style)
/craft:test --debug            # Verbose traces, pdb on failure
/craft:test --watch            # Re-run on file changes
/craft:test --coverage         # With coverage report
/craft:test --parallel         # Parallel execution

# Combined
/craft:test smoke --watch      # Watch + smoke only
/craft:test e2e --debug        # E2E with verbose output
/craft:test release            # Full suite (smoke+unit+integration+e2e+dogfood)

# Filter
/craft:test --filter="auth"    # Name filter
/craft:test tests/test_foo.py  # Specific file

# CI mode (machine-readable)
/craft:test --ci               # JUnit XML output, no colors
/craft:test --ci --coverage    # CI + coverage thresholds
```

### /craft:test:gen — Unified Generator

Absorbs: `test:generate`, `test:cli-gen`

```bash
# Auto-detect project type
/craft:test:gen                          # Detect + confirm

# Explicit project type
/craft:test:gen plugin                   # Claude Code plugin
/craft:test:gen zsh                      # ZSH plugin/script
/craft:test:gen cli                      # Python/Node CLI
/craft:test:gen mcp                      # MCP server

# Test category
/craft:test:gen plugin smoke             # Smoke tests only
/craft:test:gen plugin dogfood           # Dogfood tests only
/craft:test:gen plugin all               # All categories

# Options
/craft:test:gen --interactive            # Include interactive QA suite
/craft:test:gen --ci                     # Include CI workflow YAML
/craft:test:gen --fixtures               # Generate test fixtures
```

---

## Test Categories (Tiered)

| Tier | Marker | When | Budget | What |
|------|--------|------|--------|------|
| **smoke** | `@pytest.mark.smoke` | Every commit | < 2 min | Exists, loads, version, help |
| **unit** | `@pytest.mark.unit` | Every commit | < 5 min | Function-level, mocked deps |
| **integration** | `@pytest.mark.integration` | Every PR | < 15 min | Real filesystem, subprocess |
| **e2e** | `@pytest.mark.e2e` | Nightly / pre-release | < 30 min | Full pipelines, temp repos |
| **dogfood** | `@pytest.mark.dogfood` | Pre-release | < 10 min | Tool tests itself (real state) |

### CI Pipeline Mapping

```yaml
# PR pipeline (fast gate)
- pytest -m "smoke or unit" --timeout=300

# Nightly pipeline
- pytest -m "not manual" --timeout=1800

# Pre-release pipeline
- pytest  # Everything
```

---

## Project Type Test Templates

### 1. Claude Code Plugin Tests

```
tests/
├── conftest.py                    # Shared fixtures
├── test_plugin_smoke.py           # @smoke: plugin.json, dirs exist
├── test_plugin_structure.py       # @unit: frontmatter, cross-refs
├── test_plugin_commands.py        # @unit: each command file valid
├── test_plugin_skills.py          # @unit: each skill file valid
├── test_plugin_integration.py     # @integration: command routing
├── test_plugin_e2e.py             # @e2e: install, load, invoke
├── test_plugin_dogfood.py         # @dogfood: real plugin state
└── cli/
    ├── automated-tests.sh         # Bash: quick structure check
    └── interactive-tests.sh       # Bash: visual QA
```

**Smoke tests:**

- `plugin.json` exists and is valid JSON
- Required fields present (name, version, description)
- No unrecognized keys (strict schema!)
- `commands/`, `skills/`, `agents/` directories exist
- File counts match declared counts

**Unit tests:**

- Every `.md` file in `commands/` has valid YAML frontmatter
- Required frontmatter fields (`description` at minimum)
- No broken internal cross-references
- Code blocks have language specifiers
- Skill files have `SKILL.md` with valid structure

**Integration tests:**

- Command routing resolves all paths
- Skill trigger phrases work
- Agent definitions valid
- Hook scripts are executable

**E2E tests (full lifecycle):**

- Install plugin to temp Claude config
- Verify plugin loads (parse plugin.json)
- Invoke sample command (via subprocess)
- Verify output format
- Uninstall / cleanup

**Dogfood tests:**

- Test against the REAL installed plugin
- Verify installed version matches source
- Check hook registration in `~/.claude/settings.json`
- Run `/craft:check` against self

### 2. ZSH Plugin Tests

```
tests/
├── conftest.py
├── test_zsh_smoke.py              # @smoke: files source without error
├── test_zsh_functions.py          # @unit: each function outputs expected
├── test_zsh_completions.py        # @unit: completion functions exist
├── test_zsh_integration.py        # @integration: sourcing + PATH
├── test_zsh_e2e.sh                # @e2e: full workflow scripts
└── cli/
    ├── automated-tests.sh
    └── interactive-tests.sh
```

**Smoke tests:**

- All `.zsh` files parse without syntax errors (`zsh -n`)
- Main plugin file sources successfully (`zsh -c "source plugin.zsh"`)
- No missing dependencies

**Unit tests (subprocess-based):**

- Each function returns expected output
- Exit codes correct
- Flag parsing works
- Help text accessible

**Integration tests:**

- Plugin sources in clean ZSH session
- Functions available after sourcing
- No namespace collisions with common tools
- Completions register correctly

**E2E tests:**

- Full workflow: install → source → use → uninstall
- Test with different ZSH versions if available
- Test with/without oh-my-zsh

### 3. Python CLI Tests

```
tests/
├── conftest.py
├── test_cli_smoke.py              # @smoke: installed, --version, --help
├── test_cli_commands.py           # @unit: each subcommand
├── test_cli_args.py               # @unit: argument parsing
├── test_cli_integration.py        # @integration: filesystem ops
├── test_cli_e2e.py                # @e2e: full pipelines
├── test_cli_dogfood.py            # @dogfood: real installed state
├── test_cli_snapshot.py           # @unit: output snapshot comparison
└── cli/
    ├── automated-tests.sh
    └── interactive-tests.sh
```

**Key addition: Snapshot tests**

- Capture `--help` output as golden files
- Capture error messages
- Strip ANSI codes and dynamic content before comparison
- Use `syrupy` or `pytest-snapshot`

### 4. MCP Server Tests

```
tests/
├── conftest.py
├── test_mcp_smoke.py              # @smoke: server starts, responds
├── test_mcp_tools.py              # @unit: each tool registration
├── test_mcp_protocol.py           # @unit: JSON-RPC compliance
├── test_mcp_integration.py        # @integration: tool execution
├── test_mcp_e2e.py                # @e2e: full client-server session
└── cli/
    ├── automated-tests.sh
    └── interactive-tests.sh
```

**Smoke tests:**

- Server binary/script exists
- Starts without errors
- Responds to `initialize` request
- Lists tools correctly

**Unit tests:**

- Each tool has name, description, input schema
- Input validation works
- Error responses formatted correctly

**Integration tests:**

- Tool execution returns expected results
- Concurrent requests handled
- Resource management (no leaks)

**E2E tests:**

- Full session: connect → initialize → list tools → invoke → disconnect
- Test with stdio and SSE transports
- Timeout handling

---

## Shared Test Infrastructure

### New: `tests/helpers.py`

```python
"""Shared test utilities for craft test suites."""
from pathlib import Path
import subprocess, json, re

# Path resolution
def project_root() -> Path: ...
def plugin_json() -> dict: ...
def all_commands() -> list[Path]: ...
def all_skills() -> list[Path]: ...

# File parsing
def read_frontmatter(path: Path) -> dict: ...
def read_markdown_body(path: Path) -> str: ...

# Subprocess execution
def run_command(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess: ...
def run_hook(hook_path: str, payload: dict) -> subprocess.CompletedProcess: ...

# Assertions
def assert_valid_frontmatter(path: Path, required: list[str]): ...
def assert_no_broken_links(content: str, base_dir: Path): ...
def assert_valid_json(path: Path, schema: dict | None = None): ...
```

### New: `conftest.py` (Enriched)

```python
"""Shared pytest fixtures for craft test suites."""
import pytest, tempfile, json
from pathlib import Path

@pytest.fixture
def craft_root() -> Path: ...

@pytest.fixture
def temp_plugin_dir(tmp_path) -> Path:
    """Create a temp directory with valid plugin structure."""
    ...

@pytest.fixture
def temp_git_repo(tmp_path) -> Path:
    """Create a temp git repo for testing."""
    ...

@pytest.fixture
def mock_command_file(tmp_path) -> Path:
    """Create a sample command .md file."""
    ...
```

### New: `pyproject.toml` pytest config

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "smoke: critical path (every commit, < 2 min)",
    "unit: function-level tests (every commit, < 5 min)",
    "integration: filesystem/subprocess tests (every PR, < 15 min)",
    "e2e: full pipeline tests (nightly, < 30 min)",
    "dogfood: self-testing against real state (pre-release, < 10 min)",
    "slow: tests taking > 5s",
    "snapshot: output comparison tests",
]
```

---

## Migration Plan

### Phase 1: Foundation (< 1 day)

1. Add `[tool.pytest.ini_options]` to `pyproject.toml`
2. Create `tests/helpers.py` with shared utilities
3. Enrich `tests/conftest.py` with fixtures
4. Add pytest markers to ALL existing test files
5. Migrate 10 `CheckResult`-pattern files to pytest

### Phase 2: Command Consolidation (< 1 day)

1. Create new `/craft:test` command (absorbs run, cli-run, coverage, debug, watch)
2. Create new `/craft:test:gen` command (absorbs generate, cli-gen)
3. Deprecate old commands (keep as aliases for 1 release)
4. Update `test-generator` skill to call `test:gen`
5. Keep `test-strategist` skill as advisory

### Phase 3: Project Type Templates (< 2 days)

1. Claude Code plugin template
2. ZSH plugin template
3. Python CLI template (enhanced from current)
4. MCP server template

### Phase 4: Advanced Features (< 2 days)

1. Snapshot testing with syrupy
2. Contract tests for plugin.json schema
3. Property-based tests with Hypothesis (frontmatter parser, complexity scorer)
4. Full lifecycle e2e for Claude plugins
5. CI workflow generation

### Phase 5: Cross-Project (future)

1. Shared test library for all `~/projects/dev-tools/` projects
2. Affected-project detection (only test what changed)
3. Cross-project dogfood tests

---

## Quick Wins

1. Add `pyproject.toml` pytest config — enables `pytest -m smoke` immediately
2. Create `tests/helpers.py` — deduplicate code across 70 test files
3. Tag existing dogfood tests with `@pytest.mark.dogfood` — instant filterability
4. Merge `cli-gen` into `generate` — reduce command count by 1
5. Add `--watch` and `--debug` flags to `test:run` — absorb 2 more commands

## Medium Effort

1. Full plugin template with lifecycle e2e
2. ZSH plugin template (new)
3. MCP server template (new)
4. Migrate CheckResult files to pytest
5. Snapshot testing for formatting output

## Long-term

1. Cross-project shared test library
2. Property-based testing for all parsers
3. Performance benchmarks
4. Visual regression testing for terminal output
5. Auto-generated tests from command documentation

---

## Recommended Path

Start with **Phase 1 (Foundation)** because it's highest-ROI with lowest risk:

- pytest config lets you immediately filter and categorize your 1,575 tests
- Shared helpers eliminate duplication across 70 files
- Markers enable tiered CI pipelines

Then **Phase 2 (Consolidation)** to reduce cognitive load:

- 7 → 2 commands is a massive UX improvement
- Users only need to remember `test` and `test:gen`

---

## Research Sources

- [Qodo (CodiumAI)](https://www.qodo.ai/) — AI test generation leader
- [Hypothesis](https://github.com/HypothesisWorks/hypothesis) — Property-based testing for Python
- [ShellSpec](https://shellspec.info/) — Best ZSH test framework (POSIX-native)
- [Schemathesis](https://schemathesis.io/) — API testing from OpenAPI specs
- [Pact](https://docs.pact.io/) — Contract testing for plugins
- [Testkube dogfooding strategy](https://testkube.io/blog/dogfooding-testkube-part1-how-to-test-a-testing-framework)
- [Monorepo testing strategies](https://yrkan.com/blog/monorepo-testing-strategies/)
- [syrupy](https://github.com/toptal/syrupy) — Snapshot testing for pytest
- [bats-core](https://github.com/bats-core/bats-core) — Bash testing framework
