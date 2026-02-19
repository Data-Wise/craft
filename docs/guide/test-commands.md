<!-- markdownlint-disable MD046 -->
# Test Commands Reference

> **Complete reference for `/craft:test`, `/craft:test:gen`, and `/craft:test:template`**

---

## /craft:test — Unified Test Runner

### Synopsis

```bash
/craft:test [category] [mode] [--path PATH] [--filter PATTERN]
            [--coverage] [--watch] [--dry-run]
```

### Quick Examples

```bash
/craft:test                         # Run all tests (default mode)
/craft:test unit                    # Unit tests only
/craft:test e2e                     # End-to-end tests only
/craft:test hub                     # Hub domain tests only
/craft:test debug                   # Verbose output with traces
/craft:test unit --filter="auth"    # Unit tests matching "auth"
/craft:test --coverage              # Run with coverage report
/craft:test --watch                 # Re-run on file changes
/craft:test --dry-run               # Preview execution plan
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `category` | Test category filter (see [Category Filtering](#category-filtering)) | All tests |
| `mode` | Execution mode: `default`, `debug`, `optimize`, `release` | `default` |
| `--path PATH` | Test file or directory to run | `tests/` |
| `--filter PATTERN` | Test name filter (`-k` flag) | All tests |
| `--coverage` | Enable coverage reporting | `false` |
| `--watch` | Re-run tests on file changes | `false` |
| `--dry-run`, `-n` | Preview execution plan without running | `false` |

### Category Filtering

Filter by tier (mutually exclusive) or domain (combinable with tiers):

**Tiers:**

| Tier | Marker | Typical Count | Speed |
|------|--------|---------------|-------|
| `unit` | `@pytest.mark.unit` | ~489 | < 2s |
| `integration` | `@pytest.mark.integration` | ~568 | < 30s |
| `e2e` | `@pytest.mark.e2e` | ~333 | < 60s |
| `smoke` | `@pytest.mark.smoke` | subset | < 30s |

**Domains:** `hub`, `claude_md`, `branch_guard`, `orchestrator`, `teaching`, `commands`, `structure`, `docs`, `badge`, `brainstorm`, `release`, `marketplace`, `formatting`, `dependency`, `site`

**Combining filters:**

```bash
/craft:test "unit and hub"              # Unit tests for hub only
/craft:test "integration and not slow"  # Fast integration tests
/craft:test "e2e and branch_guard"      # Branch guard e2e only
```

### Modes

| Mode | Budget | pytest Flags | Use Case |
|------|--------|-------------|----------|
| **default** | < 30s | `-x -q --tb=short` | Quick smoke check |
| **debug** | < 120s | `-v --tb=long --capture=no` | Verbose traces |
| **optimize** | < 180s | `-n auto --dist loadfile` | Parallel execution |
| **release** | < 300s | `--cov --cov-report=term -v --maxfail=5` | Full suite + coverage |

### Replaces

- `/craft:test:run` — Now `/craft:test` (modes work the same)
- `/craft:test:coverage` — Now `/craft:test --coverage`
- `/craft:test:debug` — Now `/craft:test debug`
- `/craft:test:watch` — Now `/craft:test --watch`

---

## /craft:test:gen — Unified Test Generator

### Synopsis

```bash
/craft:test:gen [project-type] [--tier TIER] [--output DIR]
               [--force] [--diff] [--dry-run]
```

### Quick Examples

```bash
/craft:test:gen                     # Auto-detect project type, generate all
/craft:test:gen plugin              # Force plugin type detection
/craft:test:gen --tier unit         # Generate only unit test templates
/craft:test:gen --diff              # Show diff of what would change
/craft:test:gen --dry-run           # Preview generation plan
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `project-type` | Force type: `plugin`, `zsh`, `cli`, `mcp` | Auto-detect |
| `--tier TIER` | Filter templates: `smoke`, `unit`, `integration`, `e2e`, `all` | `all` |
| `--output DIR` | Output directory for generated tests | `tests/` |
| `--force` | Overwrite existing test files | `false` |
| `--diff` | Show diff preview without writing | `false` |
| `--dry-run`, `-n` | Preview generation plan | `false` |

### Project Type Detection

| Type | Detection Rule | Templates Generated |
|------|---------------|-------------------|
| `plugin` | `.claude-plugin/plugin.json` exists | structure, commands, skills, agents, content, lifecycle, conftest |
| `zsh` | `*.plugin.zsh` file exists | sourcing, functions, completions, aliases, e2e |
| `cli` | `pyproject.toml` with `[project.scripts]` | smoke, commands, args, errors, output, e2e, conftest |
| `mcp` | `mcp-server/` directory exists | protocol, tools, resources, errors, conftest |

### Replaces

- `/craft:test:cli-gen` — Now `/craft:test:gen cli`
- `/craft:test:generate` — Now `/craft:test:gen`

---

## /craft:test:template — Template Lifecycle Manager

### Synopsis

```bash
/craft:test:template <action> [template] [--type TYPE] [--output PATH]
```

### Actions

| Action | Description | Example |
|--------|-------------|---------|
| `list` | Show all available templates | `/craft:test:template list` |
| `show` | Display template source | `/craft:test:template show plugin/test_structure` |
| `validate` | Check template integrity | `/craft:test:template validate` |
| `render` | Preview rendered output | `/craft:test:template render plugin/test_structure` |
| `create` | Add a new template | `/craft:test:template create plugin/test_hooks` |
| `edit` | Modify existing template | `/craft:test:template edit plugin/test_structure` |
| `delete` | Remove a template | `/craft:test:template delete plugin/test_hooks` |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `action` | Action to perform (required) | - |
| `template` | Template path (e.g., `plugin/test_structure`) | - |
| `--type TYPE` | Filter by project type: `plugin`, `zsh`, `cli`, `mcp`, `_base` | All |
| `--output PATH` | Output path for `render` action | stdout |

---

## See Also

- [Testing Quickstart Tutorial](../tutorials/testing-quickstart.md) — Step-by-step getting started
- [Test Architecture Guide](test-architecture.md) — Template system, detection, tiers
- [Migration Guide](test-migration.md) — Old commands to new commands
- [/craft:check](../commands/check.md) — Pre-flight validation
