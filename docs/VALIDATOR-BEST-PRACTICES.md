# Validator Best Practices - Craft Plugin

**Audience**: Validator developers, community contributors
**Version**: 1.0.0
**Last Updated**: 2026-01-17

---

## Table of Contents

- [Introduction](#introduction)
- [Validator Anatomy](#validator-anatomy)
- [Best Practices](#best-practices)
- [Anti-Patterns](#anti-patterns)
- [Testing Validators](#testing-validators)
- [Publishing Validators](#publishing-validators)
- [Example Validators](#example-validators)

---

## Introduction

This guide provides best practices for creating custom validators for the Craft plugin's hot-reload validation system.

### What is a Validator?

A validator is a **self-contained validation script** that:

- Runs in forked context (isolated from main conversation)
- Checks code quality, security, performance, or other metrics
- Reports pass/fail status with clear output
- Adapts behavior based on execution mode (debug/default/optimize/release)
- Is automatically discovered by `/craft:check` via `hot_reload: true`

### Why Create Validators?

- **Extensibility**: Add project-specific or domain-specific checks
- **Community sharing**: Package validation logic for others to use
- **Consistency**: Enforce standards across projects
- **Automation**: Integrate with CI/CD pipelines

---

## Validator Anatomy

### Minimal Validator Structure

```markdown
---
name: check:my-validator
description: What this validator checks
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# My Validator

## Auto-Detection
[Detect when to run]

## Implementation
[Validation logic]

## Output
[Report results]
```

### Required Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `name` | ✅ Yes | Unique identifier (prefix: `check:`) | `check:security-audit` |
| `description` | ✅ Yes | One-line purpose | `Security vulnerability scanning` |
| `category` | ✅ Yes | Always `validation` | `validation` |
| `context` | ✅ Yes | Always `fork` (isolation) | `fork` |
| `hot_reload` | ✅ Yes | Always `true` (auto-discovery) | `true` |
| `version` | ✅ Yes | Semantic version | `1.0.0` |

### Optional Frontmatter Fields

| Field | Optional | Purpose | Example |
|-------|----------|---------|---------|
| `languages` | ⭕ Yes | Supported languages | `[python, javascript]` |
| `tools` | ⭕ Yes | Required tools | `[bandit, semgrep]` |
| `min_version` | ⭕ Yes | Minimum Craft version | `1.23.0` |
| `author` | ⭕ Yes | Author info | `John Doe <john@example.com>` |
| `repository` | ⭕ Yes | Source repo | `https://github.com/user/repo` |

---

## Best Practices

### 1. Graceful Tool Detection

**✅ DO**: Check tool availability, skip gracefully if missing

```bash
# Good: Graceful degradation
if ! command -v mytool &> /dev/null; then
    echo "⚠️  SKIP: mytool not installed"
    echo "   Install: pip install mytool"
    exit 0  # Don't fail, just skip
fi
```

**❌ DON'T**: Assume tool is installed

```bash
# Bad: Will crash if tool missing
mytool --check .
```

### 2. Mode-Aware Behavior

**✅ DO**: Adapt behavior to execution mode

```bash
# Good: Mode-aware thresholds
MODE="${CRAFT_MODE:-default}"

case "$MODE" in
    debug)
        # Verbose, all issues, non-blocking
        THRESHOLD="low"
        VERBOSE="--verbose"
        EXIT_ON_FAIL=false
        ;;
    default)
        # Standard checks
        THRESHOLD="medium"
        VERBOSE=""
        EXIT_ON_FAIL=true
        ;;
    optimize)
        # Fast checks, errors only
        THRESHOLD="high"
        VERBOSE="--quiet"
        EXIT_ON_FAIL=true
        ;;
    release)
        # Comprehensive, strict
        THRESHOLD="critical"
        VERBOSE="--strict"
        EXIT_ON_FAIL=true
        ;;
esac

mytool --level "$THRESHOLD" $VERBOSE .
```

**❌ DON'T**: Use same threshold for all modes

```bash
# Bad: No mode awareness
mytool --level high .
```

### 3. Clear, Consistent Output

**✅ DO**: Use standard output format

```bash
# Good: Clear status with summary
echo "╭─ Security Audit ────────────────────────────────────╮"
echo "│ Tool: bandit v1.7.5                                 │"
echo "│ Mode: default (medium severity)                    │"
echo "├─────────────────────────────────────────────────────┤"

if [ "$ISSUES" -eq 0 ]; then
    echo "│ ✅ PASS: No security issues found                  │"
    echo "│ Scanned: $FILES files                              │"
else
    echo "│ ❌ FAIL: $ISSUES security issues found             │"
    echo "│ Severity: $HIGH high, $MED medium, $LOW low        │"
fi

echo "╰─────────────────────────────────────────────────────╯"
```

**❌ DON'T**: Use verbose, unstructured output

```bash
# Bad: Hard to parse
echo "Running security checks..."
mytool --verbose . 2>&1 | tee output.log
echo "Done"
```

### 4. Appropriate Exit Codes

**✅ DO**: Use standard exit codes

```bash
# Good: Clear exit code semantics
if [ "$ISSUES" -eq 0 ]; then
    exit 0  # Success
elif [ "$TOOL_ERROR" = true ]; then
    exit 2  # Tool error (unexpected)
else
    exit 1  # Validation failed (expected)
fi
```

**❌ DON'T**: Use non-standard exit codes

```bash
# Bad: Unclear exit codes
exit $ISSUES  # What does exit 42 mean?
```

### 5. Performance Considerations

**✅ DO**: Use timeouts and caching

```bash
# Good: Timeout for slow tools
CACHE_FILE=".craft/cache/validator-results.json"

# Check cache (< 5 min old)
if [ -f "$CACHE_FILE" ]; then
    AGE=$(($(date +%s) - $(stat -f %m "$CACHE_FILE")))
    if [ $AGE -lt 300 ]; then
        echo "🔄 Using cached results (${AGE}s old)"
        cat "$CACHE_FILE"
        exit 0
    fi
fi

# Run with timeout
timeout 60 mytool --check . | tee "$CACHE_FILE" || {
    echo "⚠️  TIMEOUT: mytool exceeded 60s"
    exit 0  # Don't block on timeout in optimize mode
}
```

**❌ DON'T**: Run slow tools without limits

```bash
# Bad: Can hang indefinitely
mytool --comprehensive-scan .
```

### 6. Error Handling

**✅ DO**: Handle errors gracefully

```bash
# Good: Robust error handling
set -e  # Exit on error
trap 'echo "❌ ERROR: Validator crashed at line $LINENO"' ERR

# Validate inputs
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ ERROR: Target directory not found: $TARGET_DIR"
    exit 2
fi

# Run tool with error capture
if ! OUTPUT=$(mytool --check "$TARGET_DIR" 2>&1); then
    ERROR_CODE=$?
    echo "❌ FAIL: mytool exited with code $ERROR_CODE"
    echo "   Output: $OUTPUT"
    exit 1
fi
```

**❌ DON'T**: Ignore errors

```bash
# Bad: Swallows all errors
mytool --check . || true
```

### 7. Multi-Language Support

**✅ DO**: Auto-detect language, run appropriate tool

```bash
# Good: Language-aware validation
detect_language() {
    if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
        echo "python"
    elif [ -f "package.json" ]; then
        echo "javascript"
    elif [ -f "go.mod" ]; then
        echo "go"
    else
        echo "unknown"
    fi
}

LANG=$(detect_language)

case "$LANG" in
    python)
        run_python_checks
        ;;
    javascript)
        run_javascript_checks
        ;;
    go)
        run_go_checks
        ;;
    unknown)
        echo "⚠️  SKIP: Language not detected"
        exit 0
        ;;
esac
```

**❌ DON'T**: Hardcode language assumptions

```bash
# Bad: Assumes Python project
python -m bandit .
```

### 8. Documentation

**✅ DO**: Document purpose, requirements, and usage

```markdown
# Security Audit Validator

## Purpose
Scans Python codebase for security vulnerabilities using bandit.

## Requirements
- Python 3.8+
- bandit 1.7+: `pip install bandit`

## Supported Languages
- Python

## What it checks
- SQL injection patterns
- Hardcoded passwords
- Insecure crypto usage
- Shell injection vectors

## Mode Behavior
| Mode | Severity | Fail On |
|------|----------|---------|
| debug | All | No (report only) |
| default | Medium+ | Yes |
| optimize | High | Yes |
| release | High | Yes |

## False Positives
- Add `# nosec` comment to suppress specific warnings
- Configure `.bandit` file for project-wide exclusions
```

**❌ DON'T**: Leave validators undocumented

---

## Anti-Patterns

### 1. 🚫 Modifying User Code

**Never modify user code** in a validator. Validators should be **read-only**.

```bash
# ❌ BAD: Modifying code
sed -i 's/foo/bar/g' src/*.py  # NEVER DO THIS

# ✅ GOOD: Report issues only
echo "❌ FAIL: Found deprecated 'foo', use 'bar' instead"
```

### 2. 🚫 Network Requests Without Timeout

```bash
# ❌ BAD: Unbounded network request
curl https://api.example.com/validate

# ✅ GOOD: Timeout and error handling
timeout 10 curl -f https://api.example.com/validate || {
    echo "⚠️  SKIP: API unavailable"
    exit 0
}
```

### 3. 🚫 Writing to Repository

```bash
# ❌ BAD: Creating files in repo
echo "$RESULTS" > validation-report.html

# ✅ GOOD: Use .craft/cache/ for artifacts
mkdir -p .craft/cache
echo "$RESULTS" > .craft/cache/validation-report.html
```

### 4. 🚫 Assuming Dependencies

```bash
# ❌ BAD: Assuming jq is installed
cat data.json | jq '.results'

# ✅ GOOD: Check for dependencies
if command -v jq &> /dev/null; then
    cat data.json | jq '.results'
else
    # Fallback to grep/sed
    cat data.json | grep -o '"results":[^}]*'
fi
```

### 5. 🚫 Hard-Coding Paths

```bash
# ❌ BAD: Hard-coded paths
mytool --config /home/user/.mytoolrc

# ✅ GOOD: Use environment variables
CONFIG="${MYTOOL_CONFIG:-$HOME/.mytoolrc}"
mytool --config "$CONFIG"
```

---

## Testing Validators

### Manual Testing

```bash
# Test in all modes
CRAFT_MODE=debug bash .claude-plugin/skills/validation/my-validator.md
CRAFT_MODE=default bash .claude-plugin/skills/validation/my-validator.md
CRAFT_MODE=optimize bash .claude-plugin/skills/validation/my-validator.md
CRAFT_MODE=release bash .claude-plugin/skills/validation/my-validator.md

# Test with missing tools
mv $(which mytool) $(which mytool).bak
bash .claude-plugin/skills/validation/my-validator.md
mv $(which mytool).bak $(which mytool)

# Test with different project types
cd ~/test-projects/python-project
bash /path/to/my-validator.md

cd ~/test-projects/javascript-project
bash /path/to/my-validator.md
```

### Integration Testing

```bash
# Test with /craft:check
/craft:check --dry-run  # Should discover validator
/craft:check            # Should run validator

# Verify output format
/craft:check 2>&1 | grep "my-validator"
```

### CI Testing

Add validator tests to your CI pipeline:

```yaml
# .github/workflows/test-validator.yml
name: Test Validator

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          pip install bandit
          npm install -g eslint

      - name: Test validator (all modes)
        run: |
          for mode in debug default optimize release; do
            echo "Testing mode: $mode"
            CRAFT_MODE=$mode bash validator.md || exit 1
          done
```

---

## Publishing Validators

### GitHub Repository Structure

```
my-craft-validator/
├── README.md                 # Usage instructions
├── LICENSE                   # MIT/Apache/GPL
├── validator.md              # The validator itself
├── examples/
│   ├── pass/                 # Example passing projects
│   └── fail/                 # Example failing projects
└── .github/
    └── workflows/
        └── test.yml          # CI testing
```

### README Template

```markdown
# My Craft Validator

> Custom validator for [what it validates]

[![CI](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Installation

```bash
curl -o .claude-plugin/skills/validation/my-validator.md \
  https://raw.githubusercontent.com/user/repo/main/validator.md
```

## What it validates

[Description of what the validator checks]

## Requirements

- Tool: `mytool` v2.0+
- Languages: Python 3.8+, Node.js 16+

## Usage

```bash
# Test the validator
CRAFT_MODE=default bash .claude-plugin/skills/validation/my-validator.md

# Use with /craft:check
/craft:check
```

## Configuration

[Optional configuration options]

## Mode Behavior

| Mode | Threshold | Fail On |
|------|-----------|---------|
| debug | Low | No (report only) |
| default | Medium | Yes |
| optimize | High | Yes |
| release | Critical | Yes |

## Examples

See `examples/` directory for sample projects.

## Contributing

Pull requests welcome! Please ensure:

- [ ] Validator passes CI tests
- [ ] Documentation is up-to-date
- [ ] Example projects included

## License

MIT

```

### GitHub Topics

Add these topics to your repository:
- `craft-plugin`
- `craft-plugin-validator`
- `validation`
- Language tags: `python`, `javascript`, `go`, etc.
- Tool tags: `bandit`, `eslint`, etc.

---

## Example Validators

### Example 1: Simple Linter

```markdown
---
name: check:yamllint
description: YAML file linting
category: validation
context: fork
hot_reload: true
version: 1.0.0
languages:
  - yaml
tools:
  - yamllint
---

# YAML Linter Validator

## Auto-Detection

```bash
# Check for YAML files
if ! find . -name "*.yml" -o -name "*.yaml" | grep -q .; then
    echo "⚠️  SKIP: No YAML files found"
    exit 0
fi
```

## Implementation

```bash
if ! command -v yamllint &> /dev/null; then
    echo "⚠️  SKIP: yamllint not installed"
    echo "   Install: pip install yamllint"
    exit 0
fi

MODE="${CRAFT_MODE:-default}"

case "$MODE" in
    debug|default)
        yamllint -f colored .
        ;;
    optimize|release)
        yamllint -f parsable . 2>&1 | grep -v "warning"
        ;;
esac

if [ $? -eq 0 ]; then
    echo "✅ PASS: YAML files valid"
else
    echo "❌ FAIL: YAML linting errors"
    exit 1
fi
```

```

### Example 2: Performance Check

```markdown
---
name: check:load-time
description: Page load time validation
category: validation
context: fork
hot_reload: true
version: 1.0.0
languages:
  - javascript
  - typescript
tools:
  - lighthouse
---

# Load Time Validator

## Auto-Detection

```bash
if [ ! -f "package.json" ]; then
    echo "⚠️  SKIP: Not a Node.js project"
    exit 0
fi
```

## Implementation

```bash
if ! command -v lighthouse &> /dev/null; then
    echo "⚠️  SKIP: lighthouse not installed"
    exit 0
fi

MODE="${CRAFT_MODE:-default}"

case "$MODE" in
    debug)
        THRESHOLD=5000  # 5 seconds
        ;;
    default)
        THRESHOLD=3000  # 3 seconds
        ;;
    optimize|release)
        THRESHOLD=1000  # 1 second
        ;;
esac

LOAD_TIME=$(lighthouse http://localhost:3000 --output=json | jq '.audits["speed-index"].numericValue')

if [ "$LOAD_TIME" -lt "$THRESHOLD" ]; then
    echo "✅ PASS: Load time ${LOAD_TIME}ms < ${THRESHOLD}ms"
else
    echo "❌ FAIL: Load time ${LOAD_TIME}ms >= ${THRESHOLD}ms"
    exit 1
fi
```

```

---

## Resources

- [Craft Plugin Documentation](https://data-wise.github.io/craft/)
- [/craft:check Command](../commands/check.md)
- [Validator Generator](../commands/check/gen-validator.md)
- [GitHub Validator Marketplace](https://github.com/topics/craft-plugin-validator)

---

**Questions?** Open an issue on [GitHub](https://github.com/Data-Wise/craft/issues)
