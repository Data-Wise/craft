# Developer Guide - Dependency Management System

Complete guide for developers working on the dependency management system.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [Common Tasks](#common-tasks)

---

## Getting Started

### Prerequisites

- Bash 4.0+ (or compatible shell)
- macOS or Linux
- Git
- One of: Homebrew, Cargo, or APT/YUM

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Data-Wise/craft.git
cd craft

# Switch to feature branch
git checkout feature/demo-dependency-management

# Run tests
./tests/test_dependency_management.sh all

# Check dependencies
./scripts/dependency-manager.sh check_dependencies asciinema
```

---

## Development Setup

### Directory Structure

```
craft/
├── commands/docs/demo.md          # Command definition with YAML frontmatter
├── scripts/
│   ├── dependency-manager.sh      # Main orchestrator
│   ├── tool-detector.sh           # Tool detection logic
│   ├── session-cache.sh           # Performance caching
│   ├── dependency-installer.sh    # Installation framework
│   ├── consent-prompt.sh          # User consent UI
│   ├── convert-cast.sh            # Single file conversion
│   ├── batch-convert.sh           # Batch processor
│   ├── health-check.sh            # Health validation
│   ├── version-check.sh           # Version comparison
│   └── repair-tools.sh            # Tool repair system
├── tests/
│   └── test_dependency_management.sh  # Test suite
├── docs/
│   ├── DEPENDENCY-MANAGEMENT.md    # User documentation
│   ├── API-REFERENCE.md            # API documentation
│   ├── DEPENDENCY-ARCHITECTURE.md  # Architecture diagrams
│   └── DEVELOPER-GUIDE.md          # This file
└── .github/workflows/
    └── validate-dependencies.yml   # CI/CD workflow
```

### Environment Setup

```bash
# Enable debug mode
export DEBUG=1

# Disable colors for CI
export NO_COLOR=1

# Custom cache location
export TMPDIR=/custom/cache/path
```

---

## Code Structure

### Script Organization

All scripts follow this structure:

```bash
#!/usr/bin/env bash
#
# Script Name - Brief Description
# Usage: script.sh <args>
#

# Strict mode (no set -e for test scripts)
set -uo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
CACHE_TTL=60
DEFAULT_METHOD="asciinema"

# Functions (alphabetically)
function_a() {
    # Implementation
}

function_b() {
    # Implementation
}

# Main execution (if script is run directly)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
```

### Naming Conventions

- **Variables**: `snake_case` for local, `UPPER_CASE` for constants/globals
- **Functions**: `snake_case_with_underscores`
- **Files**: `kebab-case.sh`
- **Commands**: `parse_frontmatter`, `check_dependencies`

### Error Handling Pattern

```bash
# Function-level error handling
process_data() {
    local input="$1"
    local result

    # Validate input
    if [ -z "$input" ]; then
        echo "ERROR: Input required" >&2
        return 1
    fi

    # Process with error capture
    result=$(risky_operation "$input") || {
        echo "ERROR: Operation failed" >&2
        return 1
    }

    echo "$result"
    return 0
}

# Script-level error handling
main() {
    local status=0

    if ! process_data "$1"; then
        status=1
    fi

    exit $status
}
```

---

## Adding New Features

### Adding a New Tool

**Step 1**: Add tool specification to `commands/docs/demo.md` frontmatter:

```yaml
new_tool:
  required: true
  purpose: "Tool description"
  methods: ["asciinema"]  # or ["vhs"]
  install:
    brew: "new-tool"
    cargo: "new-tool"
    apt: "new-tool"
  version:
    min: "1.0.0"
    check_cmd: "new-tool --version | grep -oE '[0-9.]+' | head -1"
  health:
    check_cmd: "new-tool --help"
    expect_exit: 0
```

**Step 2**: Test detection:

```bash
source scripts/dependency-manager.sh
metadata=$(parse_frontmatter)
echo "$metadata" | jq '.new_tool'
```

**Step 3**: Add tests to `tests/test_dependency_management.sh`:

```bash
# In run_unit_tests()
assert_file_exists "$SCRIPTS_DIR/new-tool-handler.sh" "new-tool handler exists"

# In run_validation_tests()
local tool_status
tool_status=$(detect_tool "new-tool" "which new-tool")
assert_not_empty "$tool_status" "new-tool detection works"
```

---

### Adding a New Installation Strategy

**Step 1**: Create handler in `scripts/dependency-installer.sh`:

```bash
install_via_custom() {
    local tool_name="$1"
    local install_spec="$2"

    # Extract custom install command from spec
    local custom_cmd
    custom_cmd=$(echo "$install_spec" | jq -r '.custom // empty')

    if [ -z "$custom_cmd" ]; then
        return 1  # Strategy not applicable
    fi

    # Execute install
    echo "Installing $tool_name via custom method..."
    eval "$custom_cmd" || return 1

    return 0
}
```

**Step 2**: Add to installation chain in `install_tool`:

```bash
install_tool() {
    local tool_name="$1"
    local install_spec="$2"

    # Try strategies in order
    install_via_brew "$tool_name" "$install_spec" && return 0
    install_via_cargo "$tool_name" "$install_spec" && return 0
    install_via_custom "$tool_name" "$install_spec" && return 0  # New strategy
    install_via_binary "$tool_name" "$install_spec" && return 0

    return 1
}
```

---

### Adding a New Validation Check

**Step 1**: Create check function in appropriate script:

```bash
# In scripts/health-check.sh
run_security_check() {
    local tool_name="$1"
    local tool_path="$2"

    # Perform security validation
    if ! verify_signature "$tool_path"; then
        echo '{"security": "invalid_signature"}'
        return 1
    fi

    echo '{"security": "ok"}'
    return 0
}
```

**Step 2**: Integrate into main check flow:

```bash
# In dependency-manager.sh check_dependencies()
local security_status
security_status=$(run_security_check "$tool_name" "$tool_path")

# Add to output JSON
printf '  "security": %s,\n' "$security_status"
```

---

## Testing

### Running Tests

```bash
# Run all tests
./tests/test_dependency_management.sh all

# Run specific test suite
./tests/test_dependency_management.sh unit
./tests/test_dependency_management.sh validation
./tests/test_dependency_management.sh e2e

# Run with verbose output
DEBUG=1 ./tests/test_dependency_management.sh all
```

### Writing Tests

#### Unit Test Pattern

```bash
run_unit_tests() {
    log_test "Unit" "New feature test"

    # Test 1: File exists
    assert_file_exists "$SCRIPTS_DIR/new-feature.sh" "new-feature script exists"

    # Test 2: Function works
    source "$SCRIPTS_DIR/new-feature.sh"
    local result
    result=$(new_feature_function "test_input")
    assert_equals "expected_output" "$result" "function returns correct value"

    # Test 3: Error handling
    assert_exit_code 1 "new_feature_function ''" "function fails on empty input"
}
```

#### Validation Test Pattern

```bash
run_validation_tests() {
    log_test "Validation" "JSON output test"

    # Generate output
    local json_output
    json_output=$(./scripts/new-feature.sh --json)

    # Validate JSON structure
    assert_json_valid "$json_output" "produces valid JSON"

    # Validate specific fields
    if echo "$json_output" | jq -e '.expected_field' > /dev/null; then
        pass "contains expected_field"
        ((TOTAL_TESTS++))
    else
        fail "contains expected_field" "Field missing"
        ((TOTAL_TESTS++))
    fi
}
```

#### E2E Test Pattern

```bash
run_e2e_tests() {
    log_test "E2E" "Full workflow test"

    # Step 1: Setup
    local temp_dir
    temp_dir=$(mktemp -d)

    # Step 2: Execute workflow
    local workflow_result
    workflow_result=$(./scripts/full-workflow.sh "$temp_dir") || {
        fail "workflow execution" "Workflow failed"
        ((TOTAL_TESTS++))
        return
    }

    # Step 3: Verify results
    assert_file_exists "$temp_dir/output.json" "creates output file"
    assert_contains "$workflow_result" "Success" "reports success"

    # Cleanup
    rm -rf "$temp_dir"
}
```

### Test Assertions

```bash
# File/directory assertions
assert_file_exists <path> <test_name>
assert_executable <path> <test_name>

# String assertions
assert_equals <expected> <actual> <test_name>
assert_contains <haystack> <needle> <test_name>

# Exit code assertions
assert_exit_code <expected_code> <command> <test_name>

# JSON assertions
assert_json_valid <json_string> <test_name>
```

---

## Best Practices

### Bash Scripting

**DO**:
- ✅ Use `set -uo pipefail` for strict mode
- ✅ Quote all variables: `"$var"` not `$var`
- ✅ Use `local` for function variables
- ✅ Check exit codes explicitly
- ✅ Provide meaningful error messages
- ✅ Use `readonly` for constants

**DON'T**:
- ❌ Use `set -e` in test scripts (prevents error collection)
- ❌ Parse `ls` output (use globs or `find`)
- ❌ Use `eval` without validation
- ❌ Ignore error return values
- ❌ Use global variables without `readonly`

### Error Messages

```bash
# Good: Actionable error message
echo "ERROR: File not found: $file_path" >&2
echo "Please check the path and try again" >&2
return 1

# Bad: Vague error
echo "Error" >&2
return 1
```

### JSON Generation

```bash
# Good: Proper JSON escaping
printf '{"name": "%s", "count": %d}\n' "$name" "$count"

# Better: Use jq for complex JSON
jq -n \
    --arg name "$name" \
    --argjson count "$count" \
    '{"name": $name, "count": $count}'
```

### Performance

```bash
# Good: Use session cache
if cached=$(get_cached_status "$method"); then
    echo "$cached"
    return 0
fi

# Compute fresh
fresh=$(compute_status "$method")
store_cache "$method" "$fresh"
echo "$fresh"
```

---

## Common Tasks

### Debugging a Script

```bash
# Enable debug output
DEBUG=1 ./scripts/dependency-manager.sh check_dependencies asciinema

# Trace execution
bash -x ./scripts/dependency-manager.sh check_dependencies asciinema

# Check specific function
bash -c "source scripts/tool-detector.sh && detect_tool 'asciinema' 'which asciinema'"
```

### Testing JSON Output

```bash
# Test JSON structure
./scripts/dependency-manager.sh display_status_json asciinema | jq '.'

# Extract specific field
./scripts/dependency-manager.sh display_status_json asciinema | jq '.status'

# Validate against schema
./scripts/dependency-manager.sh display_status_json asciinema | \
    jq -e '.status and .method and .tools' > /dev/null && echo "Valid"
```

### Profiling Performance

```bash
# Time execution
time ./scripts/dependency-manager.sh check_dependencies asciinema

# Cache effectiveness
DEBUG=1 ./scripts/dependency-manager.sh check_dependencies asciinema 2>&1 | \
    grep -i cache

# Function-level timing
bash -c "
    start=\$SECONDS
    source scripts/dependency-manager.sh
    parse_frontmatter > /dev/null
    duration=\$(( SECONDS - start ))
    echo \"parse_frontmatter took \${duration}s\"
"
```

### Adding Debug Logging

```bash
# Add to script
debug_log() {
    if [ "${DEBUG:-false}" = "true" ] || [ "${DEBUG:-0}" = "1" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# Usage
debug_log "Processing tool: $tool_name"
debug_log "Cache hit for method: $method"
```

### Updating Documentation

```bash
# After code changes, update:
# 1. API Reference
vim docs/API-REFERENCE.md

# 2. User Documentation
vim docs/DEPENDENCY-MANAGEMENT.md

# 3. Architecture diagrams (if structure changed)
vim docs/DEPENDENCY-ARCHITECTURE.md

# 4. This developer guide
vim docs/DEVELOPER-GUIDE.md

# 5. Run docs validation
./scripts/validate-docs.sh
```

---

## Code Review Checklist

Before submitting a PR:

- [ ] All tests pass (`./tests/test_dependency_management.sh all`)
- [ ] Code follows naming conventions
- [ ] Functions have error handling
- [ ] Variables are quoted properly
- [ ] Used `local` for function variables
- [ ] Added tests for new features
- [ ] Updated relevant documentation
- [ ] Checked for shellcheck warnings
- [ ] Tested on both macOS and Linux (if applicable)
- [ ] Added debug logging for complex logic
- [ ] JSON output is valid (if applicable)

---

## Troubleshooting

### Tests Failing

```bash
# Check syntax errors
shellcheck scripts/*.sh

# Verify file permissions
ls -la scripts/*.sh | grep -v '^-rwxr-xr-x'

# Test individual components
bash -c "source scripts/health-check.sh && run_health_check 'asciinema' 'asciinema --help' 0"
```

### Cache Issues

```bash
# Clear cache
rm -f "$TMPDIR"/.craft-demo-cache-*

# Verify cache location
echo "Cache dir: $TMPDIR"

# Check cache contents
cat "$TMPDIR/.craft-demo-cache-$$" 2>/dev/null || echo "No cache"
```

### Installation Failures

```bash
# Test installation manually
source scripts/dependency-installer.sh
install_tool "agg" '{"cargo":"agg"}'

# Check available package managers
command -v brew && echo "Homebrew available"
command -v cargo && echo "Cargo available"
command -v apt && echo "APT available"
```

---

## Release Process

### Version Bump

1. Update version in all documentation files
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag
5. Push to remote

```bash
# Update version references
sed -i '' 's/Version: [0-9.]\+/Version: 1.27.0/g' docs/*.md

# Run tests
./tests/test_dependency_management.sh all

# Commit and tag
git commit -am "chore: bump version to 1.27.0"
git tag v1.27.0
git push origin feature/demo-dependency-management --tags
```

---

## Resources

- [Bash Best Practices](https://bertvv.github.io/cheat-sheets/Bash.html)
- [ShellCheck](https://www.shellcheck.net/)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [Semantic Versioning](https://semver.org/)
- [jq Manual](https://stedolan.github.io/jq/manual/)

---

**Last Updated**: 2026-01-17
**Version**: 1.26.0
**Maintainer**: Data-Wise
