<!-- markdownlint-disable MD046 -->
# Testing Quickstart

⏱️ **12 minutes** · 🟢 Beginner · ✓ Complete guide

> **TL;DR** (30 seconds)
>
> - **What:** Unified test commands + 62-test validation suite (unit, e2e, dogfood)
> - **Why:** One command to remember, with category filtering and execution modes
> - **How:** `/craft:test unit` runs unit tests, `pytest -m "e2e"` runs cross-component validation
> - **Next:** Read the [full reference](../guide/test-commands.md) or [architecture guide](../guide/test-architecture.md)

---

## Step 1: Run Your First Test

The simplest invocation runs all tests with default mode:

```bash
/craft:test
```

This executes `pytest tests/ -x -q --tb=short` — fail-fast, quiet output, short tracebacks.

---

## Step 2: Filter by Category

Tests are organized into **tiers** (how thorough) and **domains** (what they test):

```bash
# By tier
/craft:test unit              # Fast, pure function tests (< 2s)
/craft:test integration       # Tests with subprocess/filesystem (< 30s)
/craft:test e2e               # Full end-to-end validation (< 60s)

# By domain
/craft:test hub               # Hub discovery tests
/craft:test branch_guard      # Branch protection tests
/craft:test claude_md         # CLAUDE.md sync tests

# Combined
/craft:test "unit and hub"    # Unit tests for hub only
```

---

## Step 3: Choose an Execution Mode

Four modes optimize for different workflows:

```bash
/craft:test                   # default — quick smoke check (< 30s)
/craft:test debug             # verbose traces, no capture (< 120s)
/craft:test optimize          # parallel execution (< 180s)
/craft:test release           # full suite + coverage (< 300s)
```

Combine category and mode:

```bash
/craft:test unit debug        # Unit tests with verbose output
/craft:test e2e release       # E2E tests with coverage
```

---

## Step 4: Use Flags for Coverage and Watch

```bash
# Coverage report
/craft:test --coverage

# Watch mode (re-run on file changes)
/craft:test unit --watch

# Preview what would run
/craft:test release --dry-run
```

---

## Step 5: Generate Tests for a New Project

Auto-detect project type and generate a full test suite:

```bash
# Auto-detect and generate all tiers
/craft:test:gen

# Generate only unit tests
/craft:test:gen --tier unit

# Preview without writing
/craft:test:gen --dry-run

# Force a specific project type
/craft:test:gen plugin
```

---

## Step 6: Manage Templates

Inspect and customize the Jinja2 templates that power test generation:

```bash
# List all available templates
/craft:test:template list

# Show a specific template
/craft:test:template show plugin/test_structure

# Validate all templates
/craft:test:template validate
```

---

## Step 7: Run the E2E and Dogfood Suites

Beyond `/craft:test`, craft has dedicated test suites that validate the plugin against itself:

```bash
# E2E: validates cross-component wiring (21 tests, ~0.6s)
python3 -m pytest tests/test_plugin_e2e.py -v

# Dogfood: runs craft's own scripts against the live repo (28 tests, ~1.9s)
python3 -m pytest tests/test_plugin_dogfood.py -v

# Both together with the unit suite (74 tests, ~2.5s)
python3 -m pytest tests/test_craft_plugin.py tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -v
```

**What each suite catches:**

| Suite | Catches |
|-------|---------|
| Unit (`test_craft_plugin.py`) | Missing files, broken links, wrong counts |
| E2E (`test_plugin_e2e.py`) | Version drift, stale frontmatter, orphan references |
| Dogfood (`test_plugin_dogfood.py`) | Script regressions, performance budget violations, schema drift |

---

## Step 8: Filter by Pytest Marker

Every test file uses pytest markers for selective execution:

```bash
# By tier
python3 -m pytest -m "structure"     # 13 unit tests
python3 -m pytest -m "e2e"           # 49 e2e + dogfood tests
python3 -m pytest -m "dogfood"       # 28 dogfood-only tests

# By domain
python3 -m pytest -m "branch_guard"  # Branch protection hook tests
python3 -m pytest -m "hub"           # Hub discovery tests
python3 -m pytest -m "orchestrator"  # Orchestrator feature tests

# Combine markers
python3 -m pytest -m "e2e and not dogfood"  # E2E without dogfood
```

Available markers are defined in `pyproject.toml` under `[tool.pytest.ini_options]`.

---

## Migration from Old Commands

| Old Command | New Command |
|-------------|-------------|
| `/craft:test:run` | `/craft:test` |
| `/craft:test:run debug` | `/craft:test debug` |
| `/craft:test:coverage` | `/craft:test --coverage` |
| `/craft:test:debug` | `/craft:test debug` |
| `/craft:test:watch` | `/craft:test --watch` |
| `/craft:test:cli-gen` | `/craft:test:gen cli` |
| `/craft:test:generate` | `/craft:test:gen` |

See the [full migration guide](../guide/test-migration.md) for details.

---

## Next Steps

- [Test Commands Reference](../guide/test-commands.md) — Full argument and flag reference
- [Test Architecture Guide](../guide/test-architecture.md) — Template system and tier design
- [/craft:check](../commands/check.md) — Pre-flight validation (includes test run)
