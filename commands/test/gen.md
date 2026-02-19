---
description: Auto-detect project type and generate test suite
arguments:
  - name: project_path
    description: "Path to project (default: current directory)"
    required: false
  - name: type
    description: "Project type override: plugin, zsh, cli, mcp"
    required: false
  - name: tier
    description: "Test tier to generate: smoke, unit, integration, e2e, all"
    required: false
    default: all
  - name: dry-run
    description: Preview what would be generated without writing files
    required: false
    default: false
    alias: -n
---

# /craft:test:gen - Unified Test Generator

Auto-detect project type and generate a comprehensive test suite using Jinja2
templates. Replaces the old `test:cli-gen` and `test:generate` commands.

## Quick Start

```bash
/craft:test:gen                     # Auto-detect and generate
/craft:test:gen ~/projects/my-tool  # Generate for specific project
/craft:test:gen --type plugin       # Force project type
/craft:test:gen --tier smoke        # Generate smoke tests only
/craft:test:gen --dry-run           # Preview generation plan
```

## Project Type Detection

The generator auto-detects project type from file indicators:

| Files Present | Detected Type | Template Set |
|--------------|---------------|-------------|
| `.claude-plugin/plugin.json` | **plugin** | `templates/plugin/` |
| `*.plugin.zsh`, `*.zsh` in root | **zsh** | `templates/zsh/` |
| `pyproject.toml` + `[project.scripts]` | **cli** (Python) | `templates/cli/` |
| `package.json` + `bin` | **cli** (Node) | `templates/cli/` |
| `mcp-server/`, MCP manifest | **mcp** | `templates/mcp/` |

Override with `--type <type>` if detection is wrong.

## What Gets Generated

### For Plugin Projects

```
tests/
  conftest.py              # Shared fixtures (craft_root, temp_plugin_dir)
  test_structure.py        # Plugin.json, directories, file counts
  test_commands.py         # Frontmatter parsing, command discovery
  test_skills.py           # Skill file validation
  test_agents.py           # Agent configuration
  test_content.py          # Content validation, broken links
  test_lifecycle_e2e.py    # Full plugin lifecycle (install, load, run)
  helpers.py               # Shared test utilities
```

### For ZSH Plugin Projects

```
tests/
  test_sourcing.sh         # Plugin sources without errors
  test_functions.sh        # All functions defined and callable
  test_completions.sh      # Tab completions work
  test_aliases.sh          # Aliases defined correctly
  test_e2e.sh              # Full workflow tests
```

### For CLI Projects

```
tests/
  conftest.py              # Shared fixtures
  test_smoke.py            # Version, help, basic invocation
  test_commands.py         # Each subcommand works
  test_args.py             # Argument parsing, flags
  test_errors.py           # Invalid input handling, exit codes
  test_output.py           # Output format validation
  test_e2e.py              # End-to-end workflows
  helpers.py               # Shared utilities
```

### For MCP Server Projects

```
tests/
  conftest.py              # Server fixtures, mock transport
  test_protocol.py         # MCP protocol compliance
  test_tools.py            # Each tool executes correctly
  test_resources.py        # Resource listing and reading
  test_errors.py           # Error handling, invalid requests
```

## Test Tiers

Each generated test file is tagged with a pytest marker for tiered execution:

| Tier | Speed | What It Tests |
|------|-------|---------------|
| `smoke` | < 2 min | Basic structure, imports, help flags |
| `unit` | < 5 min | Pure function logic, parsing, validation |
| `integration` | < 15 min | Subprocess calls, file I/O, tool invocation |
| `e2e` | < 30 min | Full workflows, real project dogfooding |

Generate specific tiers:

```bash
/craft:test:gen --tier smoke        # Quick validation tests only
/craft:test:gen --tier unit         # Unit tests only
/craft:test:gen --tier all          # All tiers (default)
```

## Template System

Tests are generated from Jinja2 templates in `templates/`. Each project type
has its own template set. See `/craft:test:template` for managing templates.

### Template Variables

Templates receive these variables during rendering:

| Variable | Source | Example |
|----------|--------|---------|
| `project_name` | Directory name or manifest | `"craft"` |
| `project_type` | Auto-detected or override | `"plugin"` |
| `commands` | Discovered command list | `["test", "check", ...]` |
| `skills` | Discovered skill list | `["release", ...]` |
| `agents` | Discovered agent list | `["orchestrator-v2", ...]` |
| `entry_points` | CLI entry points | `{"craft": "craft.cli:main"}` |
| `test_dir` | Output directory | `"tests/"` |
| `markers` | Available pytest markers | `["unit", "integration", ...]` |

## Dry-Run

Preview what would be generated:

```bash
/craft:test:gen --dry-run
```

```
Test Generation Plan
Project: craft (plugin)
Template: templates/plugin/
Output: tests/

Files to generate:
  [new]    tests/test_structure.py     (12 tests, smoke+unit)
  [new]    tests/test_commands.py      (8 tests, unit)
  [skip]   tests/conftest.py           (already exists)
  [skip]   tests/helpers.py            (already exists)

Estimated: 20 new tests across 2 files
```

## Execution Behavior

When this command runs:

1. **Detect project type** - Scan for indicator files
2. **Analyze structure** - Count commands, find entry points, map features
3. **Select templates** - Load template set from `templates/<type>/`
4. **Gather variables** - Build context dict from project analysis
5. **Render templates** - Apply Jinja2 templates with variables
6. **Write files** - Create test files (skip existing unless `--force`)
7. **Report** - Show generated files and next steps

## Examples

```bash
# Generate tests for current project
/craft:test:gen

# Generate for a different project
/craft:test:gen ~/projects/my-zsh-plugin

# Force MCP type
/craft:test:gen --type mcp

# Preview without writing
/craft:test:gen -n

# Generate only smoke tests
/craft:test:gen --tier smoke

# Dogfood: generate tests for craft itself
/craft:test:gen .
```

## Integration

- `/craft:test` - Run generated tests
- `/craft:test:template` - Manage test templates
- `/craft:check` - Pre-flight validation
