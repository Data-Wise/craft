---
name: check:test-coverage
description: Validate test coverage meets minimum threshold
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# Test Coverage Validation

Run test suite and check coverage percentage against project-specific thresholds.

## Thresholds

| Mode | Minimum | Target | Release |
|------|---------|--------|---------|
| **default** | 70% | 80% | 90% |
| **debug** | 60% | 70% | 80% |
| **optimize** | 75% | 85% | 95% |
| **release** | 90% | 95% | 98% |

## Project Detection

Auto-detect project type and run appropriate coverage tool:

### Python Projects

```bash
# Run pytest with coverage
python3 -m pytest --cov=. --cov-report=json --cov-report=term tests/

# Parse coverage.json
COVERAGE=$(jq '.totals.percent_covered' coverage.json 2>/dev/null || echo "0")
```

### JavaScript/TypeScript Projects

```bash
# Run jest with coverage
npm test -- --coverage --coverageReporters=json

# Parse coverage-summary.json
COVERAGE=$(jq '.total.lines.pct' coverage/coverage-summary.json 2>/dev/null || echo "0")
```

### R Packages

```bash
# Run devtools::test() with coverage
R -e 'covr::package_coverage()' > coverage.Rout

# Parse coverage percentage
COVERAGE=$(grep -oP '\d+\.\d+(?=%)' coverage.Rout | head -1)
```

### Go Projects

```bash
# Run go test with coverage
go test -cover -coverprofile=coverage.out ./...

# Extract coverage percentage
COVERAGE=$(go tool cover -func=coverage.out | tail -1 | awk '{print $3}' | tr -d '%')
```

## Implementation

```bash
#!/bin/bash
set -euo pipefail

# Detect project type
PROJECT_TYPE="unknown"
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    PROJECT_TYPE="python"
elif [ -f "package.json" ]; then
    PROJECT_TYPE="node"
elif [ -f "DESCRIPTION" ]; then
    PROJECT_TYPE="r"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
fi

# Determine threshold based on mode (default: 70%)
MODE="${CRAFT_MODE:-default}"
case "$MODE" in
    debug)
        THRESHOLD=60
        ;;
    optimize)
        THRESHOLD=75
        ;;
    release)
        THRESHOLD=90
        ;;
    *)
        THRESHOLD=70
        ;;
esac

# Run coverage based on project type
case "$PROJECT_TYPE" in
    python)
        if ! command -v pytest &> /dev/null; then
            echo "⚠️  SKIP: pytest not installed"
            exit 0
        fi

        python3 -m pytest --cov=. --cov-report=json --cov-report=term tests/ || {
            echo "❌ FAIL: Tests failed"
            exit 1
        }

        COVERAGE=$(jq '.totals.percent_covered' coverage.json 2>/dev/null || echo "0")
        ;;

    node)
        if ! npm run test:coverage &> /dev/null; then
            echo "⚠️  SKIP: No test:coverage script"
            exit 0
        fi

        npm test -- --coverage --coverageReporters=json
        COVERAGE=$(jq '.total.lines.pct' coverage/coverage-summary.json 2>/dev/null || echo "0")
        ;;

    r)
        if ! command -v R &> /dev/null; then
            echo "⚠️  SKIP: R not installed"
            exit 0
        fi

        R -e 'covr::package_coverage()' > coverage.Rout 2>&1
        COVERAGE=$(grep -oP '\d+\.\d+(?=%)' coverage.Rout | head -1 || echo "0")
        ;;

    go)
        go test -cover -coverprofile=coverage.out ./... || {
            echo "❌ FAIL: Tests failed"
            exit 1
        }

        COVERAGE=$(go tool cover -func=coverage.out | tail -1 | awk '{print $3}' | tr -d '%')
        ;;

    *)
        echo "⚠️  SKIP: Unknown project type"
        exit 0
        ;;
esac

# Check threshold
COVERAGE_INT=$(printf "%.0f" "$COVERAGE")

if [ "$COVERAGE_INT" -lt "$THRESHOLD" ]; then
    echo "❌ FAIL: Coverage ${COVERAGE}% < ${THRESHOLD}% (${MODE} mode)"
    exit 1
else
    echo "✅ PASS: Coverage ${COVERAGE}% >= ${THRESHOLD}% (${MODE} mode)"
    exit 0
fi
```

## Output Format

```
✅ PASS: Coverage 87% >= 70% (default mode)
```

or

```
❌ FAIL: Coverage 65% < 70% (default mode)
```

## Hot-Reload Behavior

This skill is automatically detected and loaded when `/craft:check` runs:

1. No restart required when this file is added/modified
2. Changes take effect on next `/craft:check` execution
3. Can be overridden with project-specific threshold in `.craft/validation-config.yml`

## See Also

- `/craft:test:run` - Run test suite
- `/craft:test:coverage` - Detailed coverage report
- `/craft:check` - Run all validators
