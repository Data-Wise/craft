---
description: Code style and quality checks with mode support
category: code
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

```text
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

```text
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

```text
✓ Lint passed (12 files, 0 issues)
```

### Debug Mode (< 120s)

```bash
# Python: ruff check . --show-fixes --show-source
# JavaScript: eslint . --format=stylish
```

**Output:**

```text
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

```text
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

```text
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

## Markdown File Handling

When the target path contains `.md` files, `/craft:code:lint` automatically delegates markdown linting to `/craft:docs:lint`.

### How It Works

```bash
# 1. Detect file types in path
CODE_FILES=$(find "$path" -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.r" -o -name "*.go" 2>/dev/null)
MD_FILES=$(find "$path" -name "*.md" 2>/dev/null)

# 2. Run code linting on non-markdown files
if [ -n "$CODE_FILES" ]; then
  run_code_linter "$CODE_FILES"
fi

# 3. Delegate markdown files to /craft:docs:lint
if [ -n "$MD_FILES" ]; then
  echo "Delegating ${#MD_FILES[@]} markdown files to /craft:docs:lint..."
  /craft:docs:lint "$mode" "$path"
fi

# 4. Combine exit codes
EXIT_CODE=$((CODE_EXIT || MD_EXIT))
```

### Unified Output

```text
╭─ /craft:code:lint ──────────────────────────────────────────╮
│                                                             │
│ Code Files (12):                                            │
│ ✓ ruff check: 0 issues                                      │
│                                                             │
│ Markdown Files (8):                                         │
│ ✓ markdownlint: 0 issues                                    │
│                                                             │
│ STATUS: ALL CHECKS PASSED ✓                                 │
╰─────────────────────────────────────────────────────────────╯
```

### Example with Issues

```text
╭─ /craft:code:lint ──────────────────────────────────────────╮
│                                                             │
│ Code Files (12):                                            │
│ ✓ ruff check: 0 issues                                      │
│                                                             │
│ Markdown Files (8):                                         │
│ ✗ markdownlint: 3 issues                                    │
│   - docs/guide.md:21 [MD032] Missing blank line             │
│   - docs/api.md:45 [MD040] Missing language tag             │
│   - README.md:8 [MD034] Bare URL                            │
│                                                             │
│ Run /craft:docs:lint --fix to auto-fix markdown issues      │
│                                                             │
│ STATUS: ISSUES FOUND ✗                                      │
╰─────────────────────────────────────────────────────────────╯
```

### Behavior by Mode

| Mode | Code Linting | Markdown Linting |
|------|--------------|------------------|
| **default** | Quick style check | Critical errors only |
| **debug** | All rules + suggestions | + Context + suggestions |
| **optimize** | Performance rules | Parallel processing |
| **release** | Comprehensive + types | + All rules + strict |

## Integration

Works with:

- `/craft:code:ci-local` - Pre-commit checks
- `/craft:code:ci-fix` - Auto-fix lint issues
- `/craft:code:release` - Release validation
- `/craft:docs:lint` - Markdown-specific linting (delegated)

## See Also

- `/craft:code:command-audit` - Validate command frontmatter, find deprecated patterns, report health score
- `/craft:code:coverage` - Test Coverage Report
- `/craft:code:deps-check` - Dependency Check
- `/craft:code:desktop-watch` - Track Claude Desktop releases and identify plugin integration opportunities
