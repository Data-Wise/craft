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
- Detects project type from marker files (package.json, pyproject.toml, etc.)
- Detects if running in a git worktree
- Runs appropriate lint, test, and security checks
- Reports status with clear pass/fail indicators

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

### Default Mode (< 30 seconds)

| Check | What it does |
|-------|--------------|
| Lint | Fast rules only |
| Tests | Fail-fast mode |
| Git status | Working tree clean? |

### Thorough Mode (3-5 minutes)

| Check | What it does |
|-------|--------------|
| Lint | All rules |
| Tests | Complete suite |
| Types | Full type checking |
| Security | Vulnerability audit |
| Docs | Validation |

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

### Context-Specific

```bash
# Before creating a PR
/craft:check --for pr

# Checks: lint, tests, coverage >= 80%, no merge conflicts, branch up to date

# Before release
/craft:check --for release

# Checks: all above + security audit, docs valid, changelog updated, version bumped
```

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
- **Workflow:** [Pre-commit Workflow](../workflows/pre-commit.md)
