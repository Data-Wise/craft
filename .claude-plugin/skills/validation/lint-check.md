---
name: check:lint
description: Validate code style and quality standards
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# Lint Check Validation

Run project-appropriate linting tools to ensure code quality and consistency.

## Supported Project Types

| Project Type | Linter | Config File |
|--------------|--------|-------------|
| **Python** | ruff, flake8, or pylint | `pyproject.toml`, `.flake8`, `pylintrc` |
| **JavaScript** | eslint | `.eslintrc.js`, `.eslintrc.json` |
| **TypeScript** | eslint + typescript-eslint | `.eslintrc.js` |
| **R** | lintr | `.lintr` |
| **Go** | golangci-lint | `.golangci.yml` |
| **Rust** | clippy | `Cargo.toml` |

## Mode Behavior

| Mode | Severity | Auto-fix | Exit on Error |
|------|----------|----------|---------------|
| **default** | Warnings + Errors | No | Errors only |
| **debug** | All (including info) | No | No (report only) |
| **optimize** | Errors only | Yes | Yes |
| **release** | Errors only | No | Yes |

## Implementation

```bash
#!/bin/bash
set -euo pipefail

# Detect project type
PROJECT_TYPE="unknown"
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    PROJECT_TYPE="python"
elif [ -f "package.json" ]; then
    if grep -q "typescript" package.json; then
        PROJECT_TYPE="typescript"
    else
        PROJECT_TYPE="javascript"
    fi
elif [ -f "DESCRIPTION" ]; then
    PROJECT_TYPE="r"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
fi

# Get mode
MODE="${CRAFT_MODE:-default}"

# Python linting
if [ "$PROJECT_TYPE" == "python" ]; then
    if command -v ruff &> /dev/null; then
        echo "🔍 Running ruff..."

        case "$MODE" in
            debug)
                ruff check . --output-format=text || true
                exit 0
                ;;
            optimize)
                ruff check . --fix
                ;;
            release)
                ruff check . --output-format=text
                ;;
            *)
                ruff check . --output-format=text
                ;;
        esac

        if [ $? -eq 0 ]; then
            echo "✅ PASS: No lint issues found (ruff)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (ruff)"
            exit 1
        fi

    elif command -v flake8 &> /dev/null; then
        echo "🔍 Running flake8..."
        flake8 .

        if [ $? -eq 0 ]; then
            echo "✅ PASS: No lint issues found (flake8)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (flake8)"
            exit 1
        fi
    else
        echo "⚠️  SKIP: No Python linter installed (ruff or flake8)"
        exit 0
    fi

# JavaScript/TypeScript linting
elif [ "$PROJECT_TYPE" == "javascript" ] || [ "$PROJECT_TYPE" == "typescript" ]; then
    if [ -f "node_modules/.bin/eslint" ] || command -v eslint &> /dev/null; then
        echo "🔍 Running eslint..."

        case "$MODE" in
            debug)
                npx eslint . || true
                exit 0
                ;;
            optimize)
                npx eslint . --fix
                ;;
            release)
                npx eslint . --max-warnings 0
                ;;
            *)
                npx eslint .
                ;;
        esac

        if [ $? -eq 0 ]; then
            echo "✅ PASS: No lint issues found (eslint)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (eslint)"
            exit 1
        fi
    else
        echo "⚠️  SKIP: eslint not installed"
        exit 0
    fi

# R linting
elif [ "$PROJECT_TYPE" == "r" ]; then
    if command -v R &> /dev/null; then
        echo "🔍 Running lintr..."
        R -e 'lintr::lint_package()' > lint.Rout 2>&1

        if grep -q "No lints found" lint.Rout; then
            echo "✅ PASS: No lint issues found (lintr)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (lintr)"
            cat lint.Rout
            exit 1
        fi
    else
        echo "⚠️  SKIP: R not installed"
        exit 0
    fi

# Go linting
elif [ "$PROJECT_TYPE" == "go" ]; then
    if command -v golangci-lint &> /dev/null; then
        echo "🔍 Running golangci-lint..."
        golangci-lint run

        if [ $? -eq 0 ]; then
            echo "✅ PASS: No lint issues found (golangci-lint)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (golangci-lint)"
            exit 1
        fi
    else
        echo "🔍 Running go vet..."
        go vet ./...

        if [ $? -eq 0 ]; then
            echo "✅ PASS: No lint issues found (go vet)"
            exit 0
        else
            echo "❌ FAIL: Lint issues detected (go vet)"
            exit 1
        fi
    fi

# Rust linting
elif [ "$PROJECT_TYPE" == "rust" ]; then
    echo "🔍 Running clippy..."
    cargo clippy -- -D warnings

    if [ $? -eq 0 ]; then
        echo "✅ PASS: No lint issues found (clippy)"
        exit 0
    else
        echo "❌ FAIL: Lint issues detected (clippy)"
        exit 1
    fi

else
    echo "⚠️  SKIP: Unknown project type"
    exit 0
fi
```

## Example Output

### Success

```
🔍 Running ruff...
✅ PASS: No lint issues found (ruff)
```

### Failure

```
🔍 Running ruff...
src/main.py:12:5: E501 Line too long (89 > 88 characters)
src/utils.py:45:1: F401 'os' imported but unused
❌ FAIL: Lint issues detected (ruff)
```

### Debug Mode (Non-blocking)

```
🔍 Running ruff...
src/main.py:12:5: E501 Line too long (89 > 88 characters)
src/main.py:25:1: W291 Trailing whitespace
✅ PASS: Lint check completed (debug mode - non-blocking)
```

## Integration with /craft:check

This validator runs automatically:

```bash
/craft:check              # Run with default severity
/craft:check debug        # Show all issues (non-blocking)
/craft:check optimize     # Auto-fix issues
/craft:check release      # Strict mode (exit on any error)
```

## Hot-Reload Behavior

- Auto-detected by `/craft:check` (no restart needed)
- Mode-specific behavior applies immediately
- Can be customized per-project in `.craft/validation-config.yml`:

```yaml
validators:
  lint:
    enabled: true
    modes:
      default:
        severity: warnings
        auto_fix: false
      release:
        severity: errors
        auto_fix: false
        max_warnings: 0
```

## See Also

- `/craft:code:lint` - Detailed linting with mode support
- `/craft:code:ci-fix` - Auto-fix lint issues
- `/craft:check` - Run all validators
