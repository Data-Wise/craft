# Quick Reference: Testing

**Unified test runner, generator, and template manager** — 3 commands replacing 7, with tiered execution and project-type detection.

**Version:** 2.22.0 | **Engine:** `utils/test_generator.py`

---

## Quick Decision Tree

```text
What do you need?
│
├─ Run existing tests?
│   └─ /craft:test [category] [mode]
│
├─ Generate tests for a project?
│   ├─ Auto-detect type?
│   │   └─ /craft:test:gen
│   ├─ Know the project type?
│   │   └─ /craft:test:gen plugin|zsh|cli|mcp
│   └─ Just preview?
│       └─ /craft:test:gen --dry-run
│
├─ Manage templates?
│   ├─ See what's available?
│   │   └─ /craft:test:template list
│   ├─ Validate templates?
│   │   └─ /craft:test:template validate
│   └─ Preview rendered output?
│       └─ /craft:test:template render plugin/test_structure
│
└─ Coming from old commands?
    └─ See migration table below
```

---

## Commands at a Glance

| Command | Purpose | Example |
|---------|---------|---------|
| `/craft:test` | Run tests | `/craft:test unit` |
| `/craft:test:gen` | Generate test suite | `/craft:test:gen plugin` |
| `/craft:test:template` | Manage templates | `/craft:test:template list` |

---

## /craft:test — Runner

```bash
/craft:test                          # All tests, default mode
/craft:test unit                     # Unit tier only
/craft:test e2e debug                # E2E with verbose output
/craft:test "unit and hub"           # Combined filter
/craft:test --coverage               # With coverage report
/craft:test --watch                  # Re-run on changes
/craft:test --dry-run                # Preview plan
```

### Tiers

| Tier | Speed | Scope |
|------|-------|-------|
| `smoke` | < 30s | Subset for quick validation |
| `unit` | < 2s each | Pure functions, no I/O |
| `integration` | < 10s each | Subprocess, filesystem |
| `e2e` | < 60s each | Full workflows |

### Modes

| Mode | Flags | Use Case |
|------|-------|----------|
| `default` | `-x -q --tb=short` | Quick check |
| `debug` | `-v --tb=long --capture=no` | Troubleshooting |
| `optimize` | `-n auto --dist loadfile` | Parallel |
| `release` | `--cov -v --maxfail=5` | Pre-release |

### Domain Markers

```text
hub  claude_md  branch_guard  orchestrator  teaching  commands
structure  docs  badge  brainstorm  release  marketplace
formatting  dependency  site  snapshot  property  contract
```

---

## /craft:test:gen — Generator

```bash
/craft:test:gen                      # Auto-detect, generate all
/craft:test:gen plugin               # Force project type
/craft:test:gen --tier unit          # Unit templates only
/craft:test:gen --dry-run            # Preview plan
/craft:test:gen --force              # Overwrite existing
```

### Project Detection

| Indicator | Type | Templates |
|-----------|------|-----------|
| `.claude-plugin/plugin.json` | plugin | 7 test files + conftest |
| `*.plugin.zsh` | zsh | 5 bash test files |
| `pyproject.toml` + `[project.scripts]` | cli | 7 test files + conftest |
| `mcp-server/` | mcp | 5 test files + conftest |

### Template Variables

| Variable | Plugin | ZSH | CLI | MCP |
|----------|--------|-----|-----|-----|
| `project_name` | plugin.json | dir name | manifest | manifest |
| `commands` | glob | - | --help | - |
| `skills` | glob | - | - | - |
| `agents` | glob | - | - | - |
| `functions` | - | grep | - | - |
| `tools` | - | - | - | manifest |
| `resources` | - | - | - | manifest |

---

## /craft:test:template — Manager

| Action | Command | Output |
|--------|---------|--------|
| List | `/craft:test:template list` | All templates by type |
| Show | `/craft:test:template show plugin/test_structure` | Template source |
| Validate | `/craft:test:template validate` | Syntax check all |
| Render | `/craft:test:template render plugin/test_structure` | Rendered output |
| Create | `/craft:test:template create plugin/test_hooks` | New template |
| Edit | `/craft:test:template edit plugin/test_structure` | Modify existing |
| Delete | `/craft:test:template delete plugin/test_hooks` | Remove template |

---

## Migration from Old Commands

| Old | New | Notes |
|-----|-----|-------|
| `/craft:test:run` | `/craft:test` | Same modes |
| `/craft:test:coverage` | `/craft:test --coverage` | Flag instead of command |
| `/craft:test:debug` | `/craft:test debug` | Mode argument |
| `/craft:test:watch` | `/craft:test --watch` | Flag instead of command |
| `/craft:test:cli-gen` | `/craft:test:gen cli` | Type argument |
| `/craft:test:generate` | `/craft:test:gen` | Renamed |
| `/craft:test:cli-run` | `/craft:test` | Consolidated |

---

## Template Directory

```text
templates/
├── _base/                    # Shared partials
│   ├── conftest_shared.py.j2 # sys.path, project_root, temp_dir
│   ├── helpers.py.j2         # read_file, extract_frontmatter
│   └── bash_header.sh.j2     # pass_test, fail_test, summary
├── plugin/  (7 templates)    # Claude Code plugins
├── zsh/     (5 templates)    # ZSH plugins
├── cli/     (7 templates)    # Python/Node CLIs
└── mcp/     (5 templates)    # MCP servers
```

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | 25 pytest markers, addopts |
| `tests/conftest.py` | Shared fixtures |
| `tests/helpers.py` | Shared utilities |
| `templates/registry.json` | Detection rules, variable schemas |
| `utils/test_generator.py` | Rendering engine (865 lines) |

---

## See Also

- [Testing Quickstart](../tutorials/testing-quickstart.md) — Step-by-step tutorial
- [Test Commands Reference](../guide/test-commands.md) — Full options and examples
- [Test Architecture Guide](../guide/test-architecture.md) — How the system works
- [Migration Guide](../guide/test-migration.md) — Old commands to new
