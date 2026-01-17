# /craft:hub

> **Command discovery hub - find the right command for any task.**

---

## Synopsis

```bash
/craft:hub [category]
```

**Quick examples:**
```bash
# Show full hub
/craft:hub

# Show specific category
/craft:hub code
/craft:hub test
/craft:hub git
```

---

## Description

Central command discovery hub that shows all available craft commands organized by category. Automatically detects your project type and shows relevant suggestions.

**Features:**
- **Project detection** - Shows relevant commands for your project type
- **Category browsing** - Deep dive into specific command groups
- **Mode system overview** - Understand execution modes
- **Quick reference** - Common workflows at a glance

---

## Categories

| Category | Commands | Description |
|----------|----------|-------------|
| `code` | 12 | Code quality, linting, debugging |
| `test` | 4 | Testing and coverage |
| `arch` | 4 | Architecture analysis and planning |
| `docs` | 14 | Documentation generation |
| `git` | 8 | Git operations and guides |
| `site` | 12 | Documentation site management |
| `ci` | 3 | CI/CD workflow generation |
| `plan` | 3 | Planning and project management |
| `dist` | 3 | Distribution and packaging |

---

## Output Example

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT - Full Stack Developer Toolkit v1.18.0                         │
│ 📍 craft (Claude Plugin) on dev                                         │
│ 📊 89 Commands | 21 Skills | 8 Agents | 4 Modes                         │
├─────────────────────────────────────────────────────────────────────────┤
│ ⚡ SMART COMMANDS (Start Here):                                         │
│    /craft:do <task>     Universal command - AI routes to best workflow │
│    /craft:check         Pre-flight checks for commit/pr/release        │
│    /craft:help          Context-aware help and suggestions             │
├─────────────────────────────────────────────────────────────────────────┤
│ 🎚️ MODES (default|debug|optimize|release):                             │
│    default  < 10s   Quick analysis, minimal output                     │
│    debug    < 120s  Verbose traces, detailed fixes                     │
│    optimize < 180s  Performance focus, parallel execution              │
│    release  < 300s  Comprehensive checks, full audit                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 💻 CODE (12)                     🧪 TEST (4)                            │
│   /craft:code:lint [mode]          /craft:test:run [mode]               │
│   /craft:code:debug                /craft:test:watch                    │
│   /craft:code:coverage             /craft:test:coverage                 │
│   ...                              /craft:test:debug                    │
│                                                                         │
│ 🏗️ ARCH (4)                       📄 DOCS (14)                          │
│   /craft:arch:analyze [mode]       /craft:docs:update                   │
│   /craft:arch:plan                 /craft:docs:sync                     │
│   /craft:arch:review               /craft:docs:changelog                │
│   /craft:arch:diagram              ...                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Category Deep Dive

### `/craft:hub code`

```
💻 CODE COMMANDS (12)
───────────────────────────────────────────────────────────────────────────
Command                  │ Description                    │ Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:code:lint         │ Code style & quality checks    │ ✓
/craft:code:debug        │ Systematic debugging           │ -
/craft:code:coverage     │ Test coverage report           │ ✓
/craft:code:refactor     │ Refactoring guidance           │ -
/craft:code:deps-audit   │ Security vulnerability scan    │ -
/craft:code:ci-local     │ Run CI checks locally          │ -
───────────────────────────────────────────────────────────────────────────
```

### `/craft:hub git`

```
🔀 GIT COMMANDS (4 commands + 4 guides)
───────────────────────────────────────────────────────────────────────────
Commands:
  /craft:git:worktree   Parallel development with worktrees
  /craft:git:branch     Branch management (create, switch, delete)
  /craft:git:sync       Smart sync with remote (pull, rebase, push)
  /craft:git:clean      Clean up merged branches safely

Guides:
  /craft:git:refcard      Quick reference card
  /craft:git:undo-guide   Emergency undo guide
  /craft:git:safety-rails Safety rails guide
───────────────────────────────────────────────────────────────────────────
```

---

## Mode System

Many commands support execution modes:

| Mode | Time Budget | Use Case |
|------|-------------|----------|
| **default** | < 10-30s | Day-to-day quick checks |
| **debug** | < 120s | Investigating issues, verbose output |
| **optimize** | < 180s | Performance focus, parallel execution |
| **release** | < 300s | Pre-release comprehensive checks |

**Examples:**
```bash
/craft:code:lint                # default mode - quick
/craft:code:lint debug          # verbose with fix suggestions
/craft:code:lint release        # comprehensive with security

/craft:test:run                 # quick smoke tests
/craft:test:run release         # full suite with coverage
```

---

## Project-Aware Suggestions

The hub detects your project type and shows relevant commands:

### Python Project
```
💡 SUGGESTED FOR PYTHON PROJECT:

  /craft:do "run all checks"  Smart workflow
  /craft:code:lint            Run ruff/flake8
  /craft:test:run             Run pytest
  /craft:code:ci-local        Pre-push validation
```

### Node.js Project
```
💡 SUGGESTED FOR NODE PROJECT:

  /craft:do "validate all"    Smart workflow
  /craft:code:lint            Run ESLint/Prettier
  /craft:test:run             Run Jest/Vitest
  /craft:code:deps-audit      Security scan
```

### Claude Plugin
```
💡 SUGGESTED FOR CLAUDE PLUGIN:

  /craft:check                Validate plugin structure
  /craft:test:run             Run Python tests
  /craft:docs:update          Update documentation
```

---

## Quick Reference

```
┌────────────────────────────────────────────────────────────────────────┐
│ CRAFT QUICK REFERENCE                                                   │
├────────────────────────────────────────────────────────────────────────┤
│ Start Here:                                                            │
│   /craft:do <task>   → AI routes to best workflow                     │
│   /craft:check       → Quick validation                               │
│   /craft:help        → Context-aware suggestions                      │
│                                                                        │
│ Development Workflow:                                                  │
│   /craft:code:lint → /craft:test:run → /craft:check → /craft:git:sync │
│                                                                        │
│ Before Release:                                                        │
│   /craft:check --for release                                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## See Also

- **Smart routing:** `/craft:do` - Universal task command
- **Pre-flight:** `/craft:check` - Validation before commit/PR/release
- **Help:** `/craft:help` - Context-aware suggestions
- **Orchestrator:** `/craft:orchestrate` - Multi-agent workflows
