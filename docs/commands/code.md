# Code & Testing Commands

Development workflow tools with mode support - 17 commands.

## When to Use What

| Scenario | Command | Why |
|----------|---------|-----|
| Quick style check before commit | `/craft:code:lint` | Fast default mode (< 10s) |
| Full pre-flight validation | `/craft:check` | Runs lint + tests + links together |
| Deep debugging with traces | `/craft:code:lint debug` | Verbose output with fix suggestions |
| Run unit tests | `/craft:test:run` | Auto-detects framework (pytest, jest) |
| Test CLI tool behavior | `/craft:test:cli-run` | Validates stdin/stdout/exit codes |
| Run CI checks locally | `/craft:code:ci-local` | Full CI pipeline without pushing |
| Check for vulnerabilities | `/craft:code:deps-audit` | Security-focused dependency scan |
| Pre-release validation | `/craft:code:lint release` | Comprehensive + types + security |

**Common confusion:**

- **lint vs check** — `lint` checks code style only; `check` validates docs, links, and counts too
- **test:run vs test:cli-run** — `test:run` is for unit/integration tests; `test:cli-run` tests CLI tools via subprocess
- **lint vs ci-local** — `lint` checks one thing fast; `ci-local` runs the full CI pipeline locally

---

## Linting & Code Quality

### /craft:code:lint

```bash
/craft:code:lint                # default mode
/craft:code:lint debug          # Verbose with suggestions
/craft:code:lint optimize       # Fast parallel linting
```

## Testing

### /craft:test:run

```bash
/craft:test:run                 # default mode
/craft:test:run debug           # Verbose test output
/craft:test:run release         # Full suite with coverage
```

## CI/CD Commands

### /craft:code:ci-fix

Auto-fix common CI/CD issues (linting, formatting, missing files).

### /craft:code:ci-local

Run CI checks locally before pushing.

## Dependencies

### /craft:code:deps-audit

Security audit of dependencies with vulnerability reports.

### /craft:code:deps-check

Check for outdated dependencies and breaking changes.

## Documentation Integration

### /craft:code:docs-check

Validate code documentation is up-to-date with implementation.

## Release Management

### /craft:code:release

Complete release checklist (tests, docs, changelog, version bump).

## Advanced Testing

### /craft:test:cli-gen

Generate CLI test suites with comprehensive coverage.

### /craft:test:cli-run

Run CLI-specific tests with output validation.

### /craft:test:watch

Watch mode for continuous testing during development.

## Other Commands

- `/craft:code:debug` - Systematic debugging
- `/craft:code:demo` - Create demonstrations
- `/craft:code:refactor` - Refactoring guidance
- `/craft:code:review` - Code review assistance
- `/craft:test:generate` - Test generation
- `/craft:test:strategy` - Testing strategy
