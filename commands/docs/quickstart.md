# /craft:docs:quickstart - Quick Start Generator

Generate a 5-minute quickstart guide for any project.

## Purpose

**Get users running in under 5 minutes:**
- Detects project type (Node, Python, R, Go, Rust)
- Extracts setup from README, package files, CI
- Uses `QUICK-START-TEMPLATE.md` for consistent structure
- Generates copy-paste ready commands

## Usage

```bash
# Generate quickstart for current project
/craft:docs:quickstart                # Auto-detect everything

# Specify output
/craft:docs:quickstart --output docs/QUICK-START.md
/craft:docs:quickstart --output README.md --section  # Add to README

# Options
/craft:docs:quickstart --format terminal    # Preview in terminal
/craft:docs:quickstart --dry-run            # Show plan only
/craft:docs:quickstart --verbose            # Detailed output
```

## When Invoked

### Step 1: Detect Project Type

```bash
# Check for project markers
ls package.json pyproject.toml DESCRIPTION go.mod Cargo.toml 2>/dev/null
```

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1/4: DETECTING PROJECT TYPE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Project: craft                                              │
│ Type: Claude Code Plugin                                    │
│                                                             │
│ Detected:                                                   │
│   • .claude-plugin/plugin.json                              │
│   • commands/ (86 files)                                    │
│   • skills/ (21 files)                                      │
│   • agents/ (8 files)                                       │
│   • tests/ (Python)                                         │
│   • docs/ (MkDocs)                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Extract Setup Steps

```
┌─────────────────────────────────────────────────────────────┐
│ Step 2/4: EXTRACTING SETUP                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Sources analyzed:                                           │
│   • README.md (installation section)                        │
│   • CLAUDE.md (quick commands)                              │
│   • package.json / pyproject.toml                           │
│   • .github/workflows/ (CI setup)                           │
│                                                             │
│ Setup steps found:                                          │
│   1. Clone repository                                       │
│   2. (No install step - plugin)                             │
│   3. Verify with tests                                      │
│                                                             │
│ Common tasks found:                                         │
│   • Run tests                                               │
│   • Build docs                                              │
│   • Validate counts                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Generate Quick Start

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3/4: GENERATING QUICK START                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Template: templates/docs/QUICK-START-TEMPLATE.md            │
│                                                             │
│ Sections generated:                                         │
│   ✓ TL;DR (one sentence)                                    │
│   ✓ 30-Second Setup (3 commands)                            │
│   ✓ What This Does (3 bullets)                              │
│   ✓ Common Tasks (5 rows)                                   │
│   ✓ Where Things Are (5 rows)                               │
│   ✓ Current Status                                          │
│   ✓ Need Help? (3 links)                                    │
│                                                             │
│ Output: docs/QUICK-START.md (65 lines)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Validate

```
┌─────────────────────────────────────────────────────────────┐
│ Step 4/4: VALIDATING                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ All commands verified (runnable)                          │
│ ✓ Paths exist                                               │
│ ✓ Links valid                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Output Structure

Generated quickstart follows this structure:

```markdown
# Craft

> **TL;DR:** Claude Code plugin with 86 commands, 21 skills, 8 agents for ADHD-friendly development workflows.

## 30-Second Setup

```bash
# Clone the plugin
git clone https://github.com/Data-Wise/craft.git ~/.claude/plugins/craft

# Verify installation
cd ~/.claude/plugins/craft
python3 tests/test_craft_plugin.py
```

## What This Does

- Smart documentation generation with scoring algorithm
- Git workflow automation with worktrees
- ADHD-friendly brainstorming and task management

## Common Tasks

| I want to... | Run this |
|--------------|----------|
| Run tests | `python3 tests/test_craft_plugin.py` |
| Build docs | `mkdocs build` |
| Validate | `./scripts/validate-counts.sh` |
| Smart routing | `/craft:do <task>` |
| Pre-flight check | `/craft:check` |

## Where Things Are

| Location | Contents |
|----------|----------|
| `commands/` | 86 command definitions |
| `skills/` | 21 specialized skills |
| `agents/` | 8 agents |
| `tests/` | Python test suite |
| `docs/` | MkDocs documentation |

## Current Status

```
version: 1.18.0
status: Production Ready
```

## Need Help?

- **Commands list:** `/help hub`
- **Documentation:** https://data-wise.github.io/craft/
- **Issues:** https://github.com/Data-Wise/craft/issues
```

## Project Type Detection

| Marker | Project Type | Setup Pattern |
|--------|--------------|---------------|
| `package.json` | Node.js | `npm install && npm test` |
| `pyproject.toml` | Python | `pip install -e . && pytest` |
| `DESCRIPTION` | R package | `devtools::load_all()` |
| `go.mod` | Go | `go build && go test ./...` |
| `Cargo.toml` | Rust | `cargo build && cargo test` |
| `.claude-plugin/` | Claude Plugin | Clone and test |
| `mkdocs.yml` | MkDocs site | `mkdocs serve` |

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Generate to docs/QUICK-START.md |
| `--output PATH` | Custom output path |
| `--section` | Insert as section in existing file |
| `--format terminal` | Preview in terminal only |
| `--dry-run` | Show plan without generating |
| `--no-status` | Skip status section |
| `--verbose` | Detailed output |

## Integration

**Uses template:** `templates/docs/QUICK-START-TEMPLATE.md`

**Called by:**
- `/craft:docs:update --with-quickstart`
- `/craft:docs:update` (when score >= 3 for quickstart type)

**Outputs to:**
- `docs/QUICK-START.md` (default)
- `README.md` with `--section`
- Custom path with `--output`

## ADHD-Friendly Design

1. **One command** - No decisions needed
2. **Copy-paste ready** - Commands work as-is
3. **Tables for scanning** - Quick lookup
4. **30-second promise** - Builds confidence
5. **Status included** - Know where project stands
