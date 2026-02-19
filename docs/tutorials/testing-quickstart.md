<!-- markdownlint-disable MD046 -->
# Testing Quickstart

⏱️ **10 minutes** · 🟢 Beginner · ✓ Complete guide

> **TL;DR** (30 seconds)
>
> - **What:** Three unified test commands replace seven old ones
> - **Why:** One command to remember, with category filtering and execution modes
> - **How:** `/craft:test unit` runs unit tests, `/craft:test:gen` generates test suites
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
