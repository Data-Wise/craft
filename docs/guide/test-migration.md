# Test Command Migration Guide

> **Mapping old test commands to the new unified system**

---

## Command Mapping

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `/craft:test:run` | `/craft:test` | Same modes (default, debug, optimize, release) |
| `/craft:test:run debug` | `/craft:test debug` | Identical behavior |
| `/craft:test:run release` | `/craft:test release` | Identical behavior |
| `/craft:test:coverage` | `/craft:test --coverage` | Now a flag instead of separate command |
| `/craft:test:debug` | `/craft:test debug` | Now a mode instead of separate command |
| `/craft:test:watch` | `/craft:test --watch` | Now a flag instead of separate command |
| `/craft:test:cli-gen` | `/craft:test:gen cli` | Merged into unified generator |
| `/craft:test:cli-run` | `/craft:test` | Merged into unified runner |
| `/craft:test:generate` | `/craft:test:gen` | Renamed with project-type detection |

---

## What Changed

### Before (7 commands)

```bash
/craft:test:run                    # Run tests
/craft:test:run debug              # Debug mode
/craft:test:coverage               # Coverage report
/craft:test:debug                  # Debug (duplicate of run debug)
/craft:test:watch                  # Watch mode
/craft:test:cli-gen                # Generate CLI tests
/craft:test:cli-run                # Run CLI tests
/craft:test:generate               # Generate test suite
```

### After (3 commands)

```bash
/craft:test                        # Run tests (modes, categories, flags)
/craft:test:gen                    # Generate tests (project-type aware)
/craft:test:template               # Manage Jinja2 templates (new)
```

---

## New Capabilities

Features that didn't exist in the old commands:

| Feature | Command | Description |
|---------|---------|-------------|
| Category filtering | `/craft:test unit` | Filter by tier (unit/integration/e2e) |
| Domain filtering | `/craft:test hub` | Filter by domain (hub, claude_md, etc.) |
| Combined filters | `/craft:test "unit and hub"` | Two-dimensional filtering |
| Project-type detection | `/craft:test:gen` | Auto-detect plugin/zsh/cli/mcp |
| Template management | `/craft:test:template list` | Inspect and customize templates |
| Template validation | `/craft:test:template validate` | Check Jinja2 syntax and variables |

---

## Infrastructure Changes

### New Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | pytest configuration with 20 marker definitions |
| `tests/helpers.py` | Shared utilities extracted from 9+ test files |
| `templates/registry.json` | Template metadata and detection rules |
| `templates/{_base,plugin,zsh,cli,mcp}/` | Jinja2 template directories |

### Modified Files

| File | Change |
|------|--------|
| `tests/conftest.py` | Added 6 shared fixtures |
| All 66 test files | Added `pytestmark` assignments |
| 9 CheckResult files | Migrated to native pytest assertions (60% line reduction) |

---

## See Also

- [Test Commands Reference](test-commands.md) — Full argument and flag reference
- [Testing Quickstart](../tutorials/testing-quickstart.md) — Step-by-step getting started
- [Test Architecture Guide](test-architecture.md) — Template system and tier design
