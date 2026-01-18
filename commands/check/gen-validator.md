---
description: Generate a new custom validator template for /craft:check
arguments:
  - name: name
    description: Validator name (e.g., security-audit, performance-check)
    required: true
  - name: languages
    description: Comma-separated list of languages (e.g., python,javascript,go)
    required: false
  - name: interactive
    description: Interactive mode with guided prompts
    required: false
    default: false
---

# /craft:check:gen-validator - Validator Template Generator

Generate a custom validator template for the `/craft:check` hot-reload system.

## Usage

```bash
# Generate basic validator template
/craft:check:gen-validator security-audit

# Generate multi-language validator
/craft:check:gen-validator performance-check --languages "python,javascript,go"

# Interactive mode with guided prompts
/craft:check:gen-validator my-validator --interactive
```

## What Gets Generated

Creates a new validator in `.claude-plugin/skills/validation/` with:

1. **Frontmatter** - Properly configured YAML
2. **Auto-detection logic** - Project type detection
3. **Validation implementation** - Tool execution template
4. **Output formatting** - Pass/fail reporting
5. **Mode-aware behavior** - Thresholds per mode

## Generated Template Structure

```markdown
---
name: check:<validator-name>
description: <description>
category: validation
context: fork
hot_reload: true
version: 1.0.0
languages:
  - <lang1>
  - <lang2>
tools:
  - <tool1>
  - <tool2>
---

# <Validator Name> Validator

## Purpose
[What this validator checks]

## Supported Languages
[Which languages/frameworks are supported]

## Auto-Detection
[How to detect if this validator should run]

## Implementation

### <Language 1>
[Validation logic for language 1]

### <Language 2>
[Validation logic for language 2]

## Output Format
[How to report pass/fail]

## Mode-Aware Thresholds
[Different thresholds per mode]
```

## Interactive Mode

When using `--interactive`, you'll be prompted for:

```
╭─ Validator Generator (Interactive Mode) ────────────╮
│                                                      │
│ 1. Validator name: _______                          │
│    (kebab-case, e.g., security-audit)               │
│                                                      │
│ 2. Description: _________________________________    │
│    (One-line description of what it validates)      │
│                                                      │
│ 3. Languages (comma-separated): ___________         │
│    Options: python, javascript, typescript, go,     │
│             rust, r, ruby, java, c, cpp             │
│                                                      │
│ 4. Tools to use: _____________________________      │
│    (Comma-separated, e.g., bandit, semgrep)         │
│                                                      │
│ 5. Mode thresholds:                                 │
│    debug: _______ (default: low)                    │
│    default: _____ (default: medium)                 │
│    optimize: ____ (default: high)                   │
│    release: _____ (default: very-high)              │
│                                                      │
│ 6. Auto-detect logic:                               │
│    ○ File extension (.py, .js, etc.)                │
│    ○ Config file (setup.py, package.json, etc.)     │
│    ○ Directory structure (src/, tests/, etc.)       │
│    ○ Custom logic (write your own)                  │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

## Example: Security Audit Validator

```bash
/craft:check:gen-validator security-audit --languages "python,javascript"
```

Generates:

```markdown
---
name: check:security-audit
description: Security vulnerability scanning for Python and JavaScript
category: validation
context: fork
hot_reload: true
version: 1.0.0
languages:
  - python
  - javascript
tools:
  - bandit
  - semgrep
  - npm-audit
---

# Security Audit Validator

## Purpose
Scans codebase for security vulnerabilities using static analysis tools.

## Supported Languages
- **Python**: bandit, semgrep
- **JavaScript/TypeScript**: npm audit, semgrep

## Auto-Detection

```bash
# Detect Python projects
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    LANG="python"
    TOOLS="bandit semgrep"
fi

# Detect JavaScript/TypeScript projects
if [ -f "package.json" ]; then
    LANG="javascript"
    TOOLS="npm-audit semgrep"
fi
```

## Implementation

### Python (bandit)

```bash
if command -v bandit &> /dev/null; then
    echo "Running bandit security scan..."

    case "$CRAFT_MODE" in
        debug)
            bandit -r . -ll  # Low severity and above
            ;;
        default)
            bandit -r . -l   # Medium severity and above
            ;;
        optimize|release)
            bandit -r . -lll # High severity only
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "✅ PASS: No security issues found (bandit)"
    else
        echo "❌ FAIL: Security vulnerabilities detected"
        exit 1
    fi
fi
```

### JavaScript (npm audit)

```bash
if [ -f "package.json" ]; then
    echo "Running npm audit..."

    case "$CRAFT_MODE" in
        debug)
            npm audit --audit-level=low
            ;;
        default)
            npm audit --audit-level=moderate
            ;;
        optimize|release)
            npm audit --audit-level=high
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "✅ PASS: No vulnerabilities (npm audit)"
    else
        echo "❌ FAIL: Vulnerabilities found"
        exit 1
    fi
fi
```

## Output Format

```
╭─ Security Audit Validator ──────────────────────────╮
│ Language: Python                                     │
│ Tool: bandit                                         │
│ Mode: default (medium severity)                     │
├──────────────────────────────────────────────────────┤
│ ✅ PASS: No security issues found                   │
│ Scanned: 127 files                                   │
│ Issues: 0                                            │
╰──────────────────────────────────────────────────────╯
```

## Mode-Aware Thresholds

| Mode | Severity Level | Fail On |
|------|----------------|---------|
| debug | Low+ | No (report only) |
| default | Medium+ | Yes (medium+) |
| optimize | High | Yes (high only) |
| release | High | Yes (high only) |
```

## Validator Best Practices

When creating custom validators, follow these best practices:

### 1. Graceful Degradation

```bash
# Check if tool is available
if ! command -v mytool &> /dev/null; then
    echo "⚠️  SKIP: mytool not installed"
    exit 0  # Don't fail, just skip
fi
```

### 2. Mode-Aware Behavior

```bash
# Adjust behavior based on mode
case "$CRAFT_MODE" in
    debug)
        # Verbose, all issues, non-blocking
        mytool --all --verbose || true
        ;;
    default)
        # Standard checks
        mytool --warnings
        ;;
    optimize)
        # Fast checks, errors only
        mytool --errors-only --fast
        ;;
    release)
        # Comprehensive, strict
        mytool --strict --comprehensive
        ;;
esac
```

### 3. Clear Output

```bash
# Use consistent output format
echo "✅ PASS: <summary>"
echo "❌ FAIL: <summary>"
echo "⚠️  SKIP: <reason>"
echo "🔄 RUNNING: <description>"
```

### 4. Exit Codes

```bash
# Return appropriate exit codes
exit 0  # Success or skip
exit 1  # Validation failed
exit 2  # Tool error (unexpected)
```

### 5. Performance

```bash
# Use timeouts for slow tools
timeout 60 mytool || {
    echo "⚠️  TIMEOUT: mytool exceeded 60s"
    exit 0  # Don't block on timeout
}
```

## Validator Marketplace

### Discovering Community Validators

Search GitHub for community validators:

```bash
# Search GitHub topics
https://github.com/topics/craft-plugin-validator

# Filter by language
https://github.com/topics/craft-plugin-validator+python
```

### Publishing Your Validator

To share your validator with the community:

1. **Create a GitHub repo**:
   ```
   my-craft-validator/
   ├── README.md
   ├── LICENSE
   └── validator.md  # Your validator file
   ```

2. **Add GitHub topics**:
   - `craft-plugin`
   - `craft-plugin-validator`
   - `validation`
   - Language tags (e.g., `python`, `javascript`)

3. **Document usage**:
   ```markdown
   # My Craft Validator

   ## Installation
   ```bash
   curl -o .claude-plugin/skills/validation/my-validator.md \
     https://raw.githubusercontent.com/user/repo/main/validator.md
   ```

   ## What it validates
   [Description]

   ## Requirements
   - Tool: mytool v2.0+
   - Languages: Python 3.8+
   ```

4. **Tag releases**:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

### Installing Community Validators

```bash
# Direct download
curl -o .claude-plugin/skills/validation/<name>.md \
  https://raw.githubusercontent.com/<user>/<repo>/main/validator.md

# Verify frontmatter
head -20 .claude-plugin/skills/validation/<name>.md

# Test validator
CRAFT_MODE=default bash .claude-plugin/skills/validation/<name>.md

# Use with /craft:check
/craft:check  # Auto-detects new validator
```

## Validator Registry

Community-maintained validators:

| Validator | Languages | Tools | Description |
|-----------|-----------|-------|-------------|
| **test-coverage** | Python, JS, R, Go | pytest-cov, jest, covr | Coverage validation (built-in) |
| **broken-links** | All | test_craft_plugin.py | Internal link validation (built-in) |
| **lint-check** | Python, JS, TS, R, Go, Rust | ruff, eslint, lintr, golangci-lint | Code quality (built-in) |
| **security-audit** | Python, JS | bandit, npm-audit | Security scanning |
| **performance-check** | Python, JS | py-spy, clinic.js | Performance profiling |
| **accessibility** | Web | axe-core, pa11y | Accessibility validation |
| **license-check** | All | licensee, fossa | License compliance |
| **dependency-audit** | Python, JS, Go | safety, snyk, nancy | Dependency vulnerabilities |

**Contributing**: Open a PR to add your validator to the registry!

## Integration with /craft:check

Generated validators are automatically discovered:

```
╭─ /craft:check (with custom validators) ─────────────╮
│ Project: my-app (Python)                            │
│ Mode: default                                        │
├──────────────────────────────────────────────────────┤
│ Built-in Validators:                                 │
│ ✓ test-coverage   87% >= 70%                        │
│ ✓ broken-links    No broken links (342 checked)     │
│ ✓ lint-check      No issues (ruff)                  │
│                                                      │
│ Community Validators:                                │
│ ✓ security-audit  No vulnerabilities (bandit)       │
│ ✓ performance     < 100ms avg (py-spy)              │
├──────────────────────────────────────────────────────┤
│ STATUS: ALL CHECKS PASSED ✓                         │
│ Validators: 5/5 passed (3 built-in, 2 community)    │
╰──────────────────────────────────────────────────────╯
```

## See Also

- `/craft:check` - Run all validators
- `/craft:check --dry-run` - Preview validators
- [Validator Best Practices](https://data-wise.github.io/craft/validators/)
- [GitHub Validator Marketplace](https://github.com/topics/craft-plugin-validator)
