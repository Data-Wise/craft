# /craft:check

> **Universal pre-flight check that validates project readiness before commits, PRs, or releases.**

---

## Synopsis

```bash
/craft:check [mode] [--for TARGET]
```

**Quick examples:**

```bash
# Most common - quick validation
/craft:check

# Deep validation before release
/craft:check thorough

# Pre-PR validation
/craft:check --for pr
```

---

## Description

Runs appropriate checks for your project type and context. Auto-detects Python, Node.js, R, Go, and Rust projects, then executes the right linting, testing, and validation tools.

**Use cases:**

- Quick sanity check before committing
- Full validation before creating a PR
- Pre-release verification
- CI simulation locally

**What it does:**

- **Shows plan** — previews which checks will run before executing (NEW)
- **Confirms** — asks before running, with skip/dry-run options (NEW)
- Detects project type from marker files (package.json, pyproject.toml, etc.)
- Detects if running in a git worktree
- Runs appropriate lint, test, and security checks
- Reports status with clear pass/fail indicators

---

## Interactive Step Preview (NEW)

Before running any checks, the command shows what it will do and asks for confirmation:

```
/craft:check

Pre-flight Check Plan:
  Project: craft (Claude Plugin)
  Mode: default
  Branch: feature/command-enhancements

  Checks to run:
  1. Git status (clean working tree?)
  2. Unit tests (python3 tests/test_craft_plugin.py)
  3. Markdown lint (30 rules via markdownlint-cli2)

? Run these pre-flight checks?
  › Yes - Run all (Recommended)
    Skip lint (faster)
    Skip external links (faster)
    Dry run (show commands only)
```

After execution, a summary is displayed:

```
  Results: 3/3 checks passed
  Issues: 0 warnings, 0 errors
  Next steps: Ready to commit
```

---

## Options

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `[mode]` | `default` | Check depth: `default` (quick) or `thorough` (full) |

### Flags

| Flag | Description |
|------|-------------|
| `--for commit` | Pre-commit checks (lint, tests, no secrets) |
| `--for pr` | Pre-PR checks (+ coverage, merge conflicts, branch status) |
| `--for release` | Pre-release checks (+ security, docs, changelog, version) |
| `--for deploy` | Pre-deploy checks (full validation + environment) |

---

## Check Modes

### Default Mode

| Check | What it does |
|-------|--------------|
| Lint | Fast rules only |
| Tests | Fail-fast mode |
| Git status | Working tree clean? |

### Thorough Mode

| Check | What it does |
|-------|--------------|
| Lint | All rules |
| Tests | Complete suite |
| Types | Full type checking |
| Security | Vulnerability audit |
| Docs | Validation |

### Mode-Specific Check Depth (NEW)

The check depth varies by mode:

| Check | default | debug | release |
|-------|---------|-------|---------|
| Unit tests | Quick (fail-fast) | Verbose (all output) | Full + coverage report |
| Markdown lint | Changed files only | All files | All files + strict rules |
| Link validation | Skip external | Internal links only | All links (internal + external) |
| Version sync | Basic check | Show all version refs | Full audit with diff |
| Git status | Summary | Detailed | Full diff + ahead/behind |

---

## Examples

### Basic Usage

```bash
# Quick check before commit
/craft:check

# Output:
# ╭─ /craft:check ──────────────────────────────────────╮
# │ Project: craft (Claude Plugin)                      │
# │ Time: 12.4s                                         │
# ├─────────────────────────────────────────────────────┤
# │ ✓ Lint         0 issues                             │
# │ ✓ Tests        13/13 passed                         │
# │ ✓ Git          Clean working tree                   │
# ├─────────────────────────────────────────────────────┤
# │ STATUS: ALL CHECKS PASSED ✓                         │
# ╰─────────────────────────────────────────────────────╯
```

### Thorough Mode

```bash
# Full validation before release
/craft:check thorough

# Runs: lint (all rules), tests (full), types, security, docs
```

### Context-Specific (NEW: detailed check matrix)

```bash
# Before creating a PR
/craft:check --for pr

Pre-flight Check Plan:
  Project: craft (Claude Plugin)
  Mode: default
  Branch: feature/command-enhancements
  Context: pr (pre-PR validation)

  Checks to run (8 for PR context):
  1. Git status (ahead of dev?)
  2. Lint — all files
  3. Unit tests — full suite
  4. Type check
  5. Security advisory
  6. Internal link validation
  7. Merge conflict detection
  8. Coverage threshold (80% minimum)
```

The `--for` flag adjusts which checks run based on context:

| Check | `--for commit` | `--for pr` | `--for release` | `--for deploy` |
|-------|---------------|-----------|----------------|---------------|
| Git status | Clean tree | Ahead of base | Tag exists | Clean + tagged |
| Lint | Changed files | All files | All + strict | All + strict |
| Tests | Fast (fail-fast) | Full suite | Full + coverage | Full + coverage |
| Type check | Skip | Run | Run | Run |
| Security | Skip | Advisory | Full audit | Full audit |
| Links | Skip | Internal | All links | All links |
| Version sync | Skip | Check | Full audit | Full audit |
| Merge conflicts | Skip | Detect | N/A | N/A |
| Coverage threshold | Skip | 80% min | 90% min | 90% min |

### In Worktree

```bash
# Running from a worktree
cd ~/.git-worktrees/craft/feature-x
/craft:check

# Output shows worktree context:
# ╭─ /craft:check ──────────────────────────────────────╮
# │ Project: craft (Claude Plugin)                      │
# │ 🌳 Worktree: ~/.git-worktrees/craft/feature-x      │
# │    Main: ~/projects/dev-tools/craft                │
# │    Branch: feature/docs-improvement                │
# ...
```

---

## Project Type Detection

| Marker File | Project Type | Checks Run |
|-------------|--------------|------------|
| `pyproject.toml` | Python | ruff, mypy, pytest, pip-audit |
| `package.json` | Node.js | eslint, tsc, npm test, npm audit |
| `DESCRIPTION` | R Package | lintr, devtools::check, testthat |
| `go.mod` | Go | go vet, golangci-lint, go test |
| `Cargo.toml` | Rust | cargo clippy, cargo test |
| `.claude-plugin/` | Claude Plugin | Python tests |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No project detected" | Ensure marker file exists (package.json, pyproject.toml, etc.) |
| Lint errors | Run `/craft:code:lint --fix` to auto-fix |
| Test failures | Run `/craft:test:run` for detailed output |
| Security issues | Run `npm audit fix` or `pip-audit --fix` |
| Slow checks | Use `default` mode for quick validation |

---

## See Also

- **Detailed lint:** `/craft:code:lint`
- **Detailed tests:** `/craft:test:run`
- **Auto-fix issues:** `/craft:code:ci-fix`
- **Full CI simulation:** `/craft:code:ci-local`
- **Workflow:** [Git Feature Workflow](../workflows/git-feature-workflow.md)
