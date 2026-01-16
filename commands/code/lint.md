---
description: Code style and quality checks with mode support
arguments:
  - name: mode
    description: Execution mode (default|debug|optimize|release)
    required: false
    default: default
  - name: path
    description: File or directory to lint
    required: false
  - name: dry-run
    description: Preview linting commands without executing them
    required: false
    default: false
    alias: -n
---

# /craft:code:lint - Code Linting

Run code style and quality checks with configurable depth.

## Modes

| Mode | Time | Focus |
|------|------|-------|
| **default** | < 10s | Quick style check |
| **debug** | < 120s | All rules + fix suggestions |
| **optimize** | < 180s | Performance-focused rules |
| **release** | < 300s | Comprehensive + strict |

## Usage

```bash
/craft:code:lint                    # Quick check (default)
/craft:code:lint debug              # Verbose with suggestions
/craft:code:lint optimize           # Performance rules
/craft:code:lint release            # Full pre-release check
/craft:code:lint debug src/         # Debug mode on specific path
/craft:code:lint --dry-run          # Preview commands
/craft:code:lint release -n         # Preview release mode
```

## Dry-Run Mode

Preview linting commands that will be executed:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Code Linting                                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Project Detection:                                          │
│   - Type: Python                                              │
│   - Linter: ruff (primary), flake8 (fallback)                │
│   - Config: pyproject.toml                                    │
│   - Scope: Current directory (.)                              │
│                                                               │
│ ✓ Mode: default (Quick check)                                 │
│   Time budget: < 10 seconds                                   │
│   Focus: Style violations (E, W, F rules)                     │
│                                                               │
│ ✓ Commands to Execute:                                        │
│   1. ruff check . --select=E,W,F                              │
│      Purpose: Check for errors, warnings, and flake8 rules    │
│      Files: ~450 Python files                                 │
│      Estimated: ~3 seconds                                    │
│                                                               │
│ ✓ Output Format:                                              │
│   - Success: "✓ Lint passed (N files, 0 issues)"             │
│   - Failures: List of violations with file:line:col          │
│   - Exit code: 0 (success) or 1 (issues found)               │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Read-only operation (no auto-fix unless --fix flag)      │
│   • Results cached by ruff for faster subsequent runs         │
│   • Use 'debug' mode for fix suggestions                      │
│                                                               │
│ 📊 Summary: 1 linter, ~450 files, ~3 seconds                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Release Mode Dry-Run

```bash
/craft:code:lint release --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Code Linting (Release Mode)                       │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Mode: release (Comprehensive)                               │
│   Time budget: < 300 seconds                                  │
│   Focus: All rules + security + type checking                 │
│                                                               │
│ ✓ Commands to Execute (3 tools):                              │
│                                                               │
│   1. ruff check . --preview                                   │
│      Purpose: All linting rules (450+ rules enabled)          │
│      Estimated: ~5 seconds                                    │
│                                                               │
│   2. mypy .                                                   │
│      Purpose: Static type checking                            │
│      Config: pyproject.toml [tool.mypy]                       │
│      Estimated: ~45 seconds                                   │
│                                                               │
│   3. bandit -r . -ll                                          │
│      Purpose: Security vulnerability scanning                 │
│      Level: Low and above                                     │
│      Estimated: ~15 seconds                                   │
│                                                               │
│ ✓ Total Estimated Time: ~65 seconds                           │
│                                                               │
│ ⚠ Strict Mode:                                                │
│   • Any tool failure causes overall failure                   │
│   • Zero tolerance for type errors                            │
│   • Security issues block release                             │
│                                                               │
│ 📊 Summary: 3 tools, comprehensive checks                      │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the linting strategy based on detected project type and selected mode. No files are analyzed or modified.

## Project Type Detection

| Project | Linter | Config Files |
|---------|--------|--------------|
| Python | ruff, flake8, pylint | pyproject.toml, .flake8 |
| JavaScript/TypeScript | ESLint, Prettier | .eslintrc.*, prettier.config.* |
| R | lintr | .lintr |
| Go | golint, staticcheck | - |
| Rust | clippy | - |

## Mode Behaviors

### Default Mode (< 10s)
```bash
# Python: ruff check . --select=E,W,F
# JavaScript: eslint . --quiet
# R: Rscript -e "lintr::lint_package()"
```

**Output:**
```
✓ Lint passed (12 files, 0 issues)
```

### Debug Mode (< 120s)
```bash
# Python: ruff check . --show-fixes --show-source
# JavaScript: eslint . --format=stylish
```

**Output:**
```
╭─ Lint Results (Debug Mode) ─────────────────────────╮
│ Files: 12 | Rules: 45 active                        │
├─────────────────────────────────────────────────────┤
│ src/main.py:12:81 - E501 Line too long (85 > 80)   │
│   → Suggestion: Split into multiple lines          │
│ src/utils.py:8:1 - D100 Missing docstring          │
│   → Suggestion: Add module docstring               │
├─────────────────────────────────────────────────────┤
│ Auto-fix available: ruff check --fix               │
╰─────────────────────────────────────────────────────╯
```

### Optimize Mode (< 180s)
```bash
# Python: ruff check . --select=PERF,C4,SIM
# Focus on performance anti-patterns
```

**Output:**
```
╭─ Performance Lint (Optimize Mode) ──────────────────╮
│ Performance Issues: 3                               │
├─────────────────────────────────────────────────────┤
│ src/main.py:30 - PERF401 Use list comprehension    │
│   Estimated speedup: ~15%                          │
│ src/utils.py:15 - SIM118 Use `key in dict`         │
│   Estimated speedup: ~5%                           │
╰─────────────────────────────────────────────────────╯
```

### Release Mode (< 300s)
```bash
# Python: ruff check . && mypy . && bandit -r .
# JavaScript: eslint . && tsc --noEmit
# R: R CMD check --as-cran .
```

**Output:**
```
╭─ Release Lint Check ────────────────────────────────╮
│ Status: ✓ READY FOR RELEASE                        │
├─────────────────────────────────────────────────────┤
│ ✓ Style: 0 issues (45 rules checked)               │
│ ✓ Types: No type errors                            │
│ ✓ Security: No vulnerabilities                     │
│ ✓ Docs: 95% coverage                               │
├─────────────────────────────────────────────────────┤
│ Quality Score: 98/100                              │
╰─────────────────────────────────────────────────────╯
```

## Options

- `--fix` - Auto-fix issues where possible
- `--strict` - Treat warnings as errors
- `--files <pattern>` - Only lint matching files

## Integration

Works with:
- `/craft:code:ci-local` - Pre-commit checks
- `/craft:code:ci-fix` - Auto-fix lint issues
- `/craft:code:release` - Release validation
