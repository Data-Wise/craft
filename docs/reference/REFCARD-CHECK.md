# Quick Reference: /craft:check

**One command for all pre-flight validation** - Smart mode selection, comprehensive checks, ADHD-friendly output.

**Version:** 2.9.0 | **Status:** Production Ready | **NEW:** "Show Steps First" pattern with plan preview

---

## Quick Start

```bash
# Most common usage
/craft:check                    # Smart mode (default or thorough based on context)
/craft:check --mode=default     # Quick checks before commit (<10s)
/craft:check --mode=thorough    # Full validation before PR/release (<300s)

# Preview what would run
/craft:check --dry-run          # Show checklist without executing

# Skip specific checks
/craft:check --skip=tests       # Skip test execution
/craft:check --skip=lint,docs   # Skip multiple checks
```

---

## Decision Tree: Which Mode?

```
┌─ What are you about to do? ────────────────────────────┐
│                                                         │
│  Quick commit?                                          │
│    └─> /craft:check                (default mode)      │
│                                                         │
│  Create PR?                                             │
│    └─> /craft:check --mode=thorough                    │
│                                                         │
│  Prepare release?                                       │
│    └─> /craft:check --mode=thorough                    │
│                                                         │
│  Not sure what it will check?                           │
│    └─> /craft:check --dry-run                          │
│                                                         │
│  Running in CI?                                         │
│    └─> /craft:check:ci                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Mode Comparison

| Mode         | Time  | Checks                                | Use Case                    |
| ------------ | ----- | ------------------------------------- | --------------------------- |
| **default**  | <10s  | Lint, quick tests, basic validation   | Before commit               |
| **thorough** | <300s | Full test suite, coverage, links, docs| Before PR, before release   |

### Default Mode Checks

1. **Code Quality**
   - Basic linting (markdownlint, code linters)
   - Format validation

2. **Quick Tests**
   - Unit tests (fast subset)
   - Smoke tests

3. **Basic Validation**
   - Config file syntax
   - Required files exist

**Estimated time:** 5-10 seconds

### Thorough Mode Checks

1. **Comprehensive Code Quality**
   - All linters with strict rules
   - Code formatting verification
   - Complexity analysis

2. **Full Test Suite**
   - All unit tests
   - Integration tests
   - E2E tests (if applicable)
   - Coverage threshold validation (85%+)

3. **Documentation Validation**
   - Broken link detection
   - Stale documentation detection
   - Navigation structure validation
   - CLAUDE.md sync check

4. **Dependency Checks**
   - Security audit
   - Outdated dependencies
   - License compliance

5. **Build Verification**
   - Clean build from scratch
   - No warnings in build output

**Estimated time:** 2-5 minutes

---

## "Show Steps First" Pattern (NEW v2.9.0)

Before running any checks, `/craft:check` shows you the plan:

```
╭─ Pre-Flight Validation Plan ─────────────────────────╮
│ Mode: default                                         │
│ Estimated time: 5-10 seconds                          │
├───────────────────────────────────────────────────────┤
│                                                       │
│ Steps to run:                                         │
│                                                       │
│ 1. Code Quality (2s)                                  │
│    • markdownlint (24 rules)                          │
│    • python linting (ruff)                            │
│                                                       │
│ 2. Quick Tests (3s)                                   │
│    • Unit tests (fast subset, ~200 tests)             │
│                                                       │
│ 3. Basic Validation (2s)                              │
│    • Config files (pyproject.toml, .markdownlint)     │
│    • Required files (README, LICENSE, CLAUDE.md)      │
│                                                       │
│ Skipping (not in default mode):                       │
│   ⊘ Full test suite                                   │
│   ⊘ Coverage analysis                                 │
│   ⊘ Link validation                                   │
│   ⊘ Dependency audit                                  │
│                                                       │
├───────────────────────────────────────────────────────┤
│ Proceed with these checks? (y/n/switch-mode)          │
╰───────────────────────────────────────────────────────╯
```

**User can:**

- Confirm and run (y)
- Cancel (n)
- Switch to thorough mode
- Add --dry-run to see plan without prompting

---

## Subcommands

### /craft:check:quick

Essential checks only (subset of default mode):

```bash
/craft:check:quick              # Fastest validation (~3s)
```

**Checks:**

- Syntax validation
- Config file format
- Required files exist

### /craft:check:full

All validation steps (superset of thorough mode):

```bash
/craft:check:full               # Most comprehensive (~10min)
```

**Additional checks beyond thorough:**

- Security scanning (SAST)
- Performance benchmarks
- Accessibility validation
- SEO checks (for documentation sites)

### /craft:check:ci

CI-optimized checks (non-interactive, machine-readable output):

```bash
/craft:check:ci                 # For GitHub Actions
```

**Features:**

- No interactive prompts
- Structured output (JSON/JUnit)
- Exit codes for CI systems
- Parallel execution optimized

### /craft:check:deps

Dependency-focused validation:

```bash
/craft:check:deps               # Audit dependencies
/craft:check:deps --fix         # Auto-update safe deps
```

**Checks:**

- Security vulnerabilities
- Outdated packages
- License compatibility
- Dependency graph analysis

### /craft:check:docs

Documentation-focused validation:

```bash
/craft:check:docs               # Validate all docs
/craft:check:docs --fix         # Auto-fix safe issues
```

**Checks:**

- Broken links
- Stale content
- Navigation structure
- CLAUDE.md sync
- Markdown quality (24 rules)

---

## Common Scenarios

### Scenario 1: Before Committing

**Context:** Made changes, ready to commit

**Command:**

```bash
/craft:check                    # Runs default mode
```

**What happens:**

1. Shows plan (5-10s of checks)
2. Asks for confirmation
3. Runs checks
4. Reports results

**If checks pass:**

```
✅ All checks passed

Next steps:
  git add .
  git commit -m "your message"
```

**If checks fail:**

```
❌ 2 checks failed

Failures:
  • markdownlint: 3 violations in docs/guide.md
  • Unit tests: 1 test failed (test_auth_flow)

Fix these issues before committing.

Auto-fix available:
  /craft:check --fix              # Fix markdownlint violations
```

### Scenario 2: Before Creating PR

**Context:** Feature complete, ready for review

**Command:**

```bash
/craft:check --mode=thorough    # Runs thorough mode
```

**What happens:**

1. Shows comprehensive plan (2-5min of checks)
2. Asks for confirmation
3. Runs all validation
4. Generates detailed report

**Report includes:**

- Test coverage percentage
- Code quality metrics
- Documentation status
- Dependency audit results

### Scenario 3: Before Release

**Context:** Preparing production release

**Command:**

```bash
/craft:check --mode=thorough    # Same as PR, but different context
```

**Additional considerations:**

- All tests must pass
- Coverage must meet threshold (85%+)
- No security vulnerabilities
- Documentation up to date
- Changelog updated

### Scenario 4: In CI Pipeline

**Context:** GitHub Actions workflow

**Command:**

```bash
/craft:check:ci                 # Non-interactive
```

**GitHub Actions example:**

```yaml
- name: Run pre-flight checks
  run: |
    /craft:check:ci
  env:
    CI: true
```

---

## Flags Reference

| Flag              | Effect                           | Example                          |
| ----------------- | -------------------------------- | -------------------------------- |
| `--mode=MODE`     | Select mode explicitly           | `--mode=thorough`                |
| `--dry-run`       | Show plan without running        | `--dry-run`                      |
| `--skip=CHECKS`   | Skip specific checks             | `--skip=tests,lint`              |
| `--only=CHECKS`   | Run only specific checks         | `--only=tests`                   |
| `--fix`           | Auto-fix safe issues             | `--fix`                          |
| `--report=FORMAT` | Output format (json/junit/text)  | `--report=json`                  |
| `--verbose`       | Detailed output                  | `--verbose`                      |
| `--quiet`         | Minimal output                   | `--quiet`                        |

---

## Check Categories

### Code Quality

**Checks:**

- Linting (language-specific)
- Format validation
- Complexity analysis
- Code smells detection

**Auto-fixable:**

- Formatting issues
- Import sorting
- Trailing whitespace

**Tools used:**

- Python: ruff, black, isort
- JavaScript/TypeScript: eslint, prettier
- Markdown: markdownlint-cli2 (24 rules)

### Testing

**Checks:**

- Unit test execution
- Integration test execution
- E2E test execution (if applicable)
- Coverage percentage
- Coverage threshold (85%+)

**Outputs:**

- Test results summary
- Coverage report (HTML/text)
- Failed test details

**Tools used:**

- Python: pytest, coverage.py
- JavaScript: jest, vitest
- CLI: Bash test framework

### Documentation

**Checks:**

- Broken links (internal/external)
- Stale content detection
- Navigation structure
- CLAUDE.md sync
- Markdown quality
- Missing documentation

**Auto-fixable:**

- Markdown formatting
- Broken internal links (if target moved)
- Version numbers

**Tools used:**

- markdown-link-check
- markdownlint-cli2
- Custom validators (utils/)

### Dependencies

**Checks:**

- Security vulnerabilities (CVEs)
- Outdated packages
- License compliance
- Dependency conflicts
- Unused dependencies

**Auto-fixable:**

- Safe version updates (patch/minor)

**Tools used:**

- Python: pip-audit, safety
- JavaScript: npm audit
- General: licensee

### Build

**Checks:**

- Clean build succeeds
- No warnings
- Assets generated correctly
- Distribution package valid

**Tools used:**

- Build system (specific to project)
- Package validators

---

## Integration with Other Commands

### Pre-Commit Workflow

```bash
/craft:check                    # Before commit
git add .
git commit -m "message"
```

### Pre-PR Workflow

```bash
/craft:check --mode=thorough    # Full validation
/craft:docs:update              # Update documentation
/craft:check --mode=thorough    # Re-validate
gh pr create --base dev
```

### Pre-Release Workflow

```bash
/craft:check --mode=thorough    # Full validation
/craft:docs:changelog           # Update changelog
/craft:check --mode=thorough    # Re-validate
gh release create v1.0.0
```

### CI Integration

```bash
# In CI pipeline
/craft:check:ci                 # Machine-readable output
```

---

## Troubleshooting

### Check fails with "command not found"

**Solution:**

```bash
# Verify craft is installed
/craft:hub

# Reinstall if needed
brew reinstall craft
```

### Tests timeout in thorough mode

**Solution:**

```bash
# Use default mode for quick feedback
/craft:check

# Or skip tests
/craft:check --mode=thorough --skip=tests
```

### Auto-fix doesn't fix all issues

**Reason:** Some issues require manual intervention (logic errors, missing descriptions, etc.)

**Solution:**

```bash
# Run with --fix to fix safe issues
/craft:check --fix

# Manually fix remaining issues
# Re-run to verify
/craft:check
```

### Want to see what's failing without full output

**Solution:**

```bash
# Quiet mode shows only failures
/craft:check --quiet

# Or just summary
/craft:check --skip=tests --quiet
```

---

## Performance Tips

### Speed up checks

1. **Use default mode for commits:**

   ```bash
   /craft:check                 # Fast (~5-10s)
   ```

2. **Skip heavy checks when unnecessary:**

   ```bash
   /craft:check --skip=tests    # Skip test execution
   ```

3. **Run specific checks:**

   ```bash
   /craft:check:quick           # Minimal checks
   ```

### When to use thorough mode

- Before creating PR
- Before merging to main
- Before release
- After major refactoring
- Weekly validation

### Parallel execution

Thorough mode automatically parallelizes:

- Linting and testing run concurrently
- Documentation checks run in parallel
- Dependency audit runs alongside tests

---

## Exit Codes

| Code | Meaning                | Action                      |
| ---- | ---------------------- | --------------------------- |
| 0    | All checks passed      | Proceed with next step      |
| 1    | Checks failed          | Fix issues and re-run       |
| 2    | Check error            | Report bug or check config  |
| 130  | User cancelled (Ctrl+C)| Re-run when ready           |

---

## Related Commands

| Command                 | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `/craft:code:lint`      | Code quality only                         |
| `/craft:test`       | Testing only                              |
| `/craft:docs:check`     | Documentation only                        |
| `/craft:check:deps`     | Dependencies only                         |
| `/craft:check --fix`    | Auto-fix safe issues                      |

---

## Configuration

### Custom Check Configuration

Create `.craft/check-config.yml`:

```yaml
check:
  default_mode: default
  coverage_threshold: 85
  skip_checks: []
  fail_fast: false
  parallel: true
```

### Per-Project Overrides

In project `.craft-config.json`:

```json
{
  "check": {
    "default_mode": "thorough",
    "coverage_threshold": 90,
    "skip_checks": ["docs"]
  }
}
```

---

## Instruction Health Check (v2.22.0)

New check category validates CLAUDE.md accuracy:

```bash
# Included automatically in all check modes
/craft:check                    # Counts only (default)
/craft:check --mode=thorough    # Full instruction health check
```

**What it validates:**

| Check | default | thorough |
|-------|---------|----------|
| Command/skill/agent/spec counts | ✅ | ✅ |
| Line budget (< 100 lines) | - | ✅ |
| Reference file freshness | - | ✅ |
| CLAUDE.md lint | - | ✅ |

**Auto-fix:** Stale counts are auto-fixed in `--for release` mode.

**Generate reference files:**

```bash
PYTHONPATH=. python3 utils/claude_md_sync.py --generate-reference
```

Creates `.claude/reference/` files (agents.md, test-suite.md, project-structure.md) from filesystem state.

---

## See Also

- [Check Command Mastery Guide](../guide/check-command-mastery.md) - Complete guide with scenarios
- [Interactive Commands Reference](REFCARD-INTERACTIVE-COMMANDS.md) - "Show Steps First" pattern
- [Pre-Commit Workflow](../workflows/pre-commit-workflow.md) - Full pre-commit workflow
- [CI/CD Commands](../commands/ci/generate.md) - Using check in CI/CD

---

**Version:** 2.22.0
**Status:** Production Ready
**Last Updated:** 2026-02-18
