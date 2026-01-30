---
description: Validate existing CI workflow against project configuration
arguments:
  - name: path
    description: Path to workflow file (defaults to .github/workflows/*.yml)
    required: false
  - name: fix
    description: Auto-fix common issues
    required: false
    default: false
  - name: dry-run
    description: Preview validation checks without analyzing files
    required: false
    default: false
    alias: -n
---

# /craft:ci:validate - Validate CI Configuration

Check that your CI workflow matches your project configuration and follows best practices.

## Quick Start

```bash
/craft:ci:validate                        # Validate all workflows
/craft:ci:validate .github/workflows/ci.yml  # Validate specific file
/craft:ci:validate --fix                  # Auto-fix common issues

# Preview validation plan
/craft:ci:validate --dry-run
/craft:ci:validate -n
```

## Dry-Run Mode

Preview what validation checks will be performed:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Validate CI Configuration                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Workflows to Validate:                                      │
│   - .github/workflows/ci.yml                                  │
│   - .github/workflows/release.yml                             │
│                                                               │
│ ✓ Validation Checks (11 checks per workflow):                 │
│   - Structure: Valid YAML, required keys, triggers            │
│   - Project Alignment: versions, test commands, dependencies  │
│   - Best Practices: caching, fail-fast, timeouts, pinned      │
│                                                               │
│ ✓ Project Detection:                                          │
│   - Type: Python (uv)                                         │
│   - Required Python: >=3.10                                   │
│   - Test framework: pytest                                    │
│   - Linter: ruff, Type checker: mypy                          │
│                                                               │
│ 📊 Summary: Validate 2 workflows with 11 checks each           │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Validation Checks

### Structure Checks

| Check | Description |
|-------|-------------|
| **Valid YAML** | Workflow file is valid YAML |
| **Required Keys** | Has `name`, `on`, `jobs` |
| **Trigger Events** | Uses appropriate triggers (push, pull_request) |
| **Branch Filtering** | Targets correct branches |

### Project Alignment

| Check | Description |
|-------|-------------|
| **Version Match** | Matrix versions match project requirements |
| **Test Command** | Uses correct test command for project type |
| **Dependencies** | Installs dependencies correctly |
| **Build Tool** | Uses correct package manager (uv, npm, etc.) |

### Best Practices

| Check | Description |
|-------|-------------|
| **Caching** | Uses appropriate caching |
| **Fail Fast** | Matrix has fail-fast configured |
| **Timeouts** | Jobs have reasonable timeouts |
| **Actions Versions** | Uses pinned action versions (@v4 not @latest) |
| **Badge URLs** | CI badges point to correct workflows |
| **Badge Branches** | Badge URLs use appropriate branch parameter |

## Output Example

```
╭─ CI Validation Results ─────────────────────────────────╮
│                                                         │
│  📁 .github/workflows/ci.yml                            │
│                                                         │
│  Structure:                                             │
│  ✅ Valid YAML syntax                                   │
│  ✅ Has required keys (name, on, jobs)                  │
│  ✅ Triggers on push and pull_request                   │
│                                                         │
│  Project Alignment:                                     │
│  ✅ Python versions match pyproject.toml               │
│  ✅ Uses uv (matches uv.lock)                          │
│  ⚠️  Missing ruff lint step                            │
│  ⚠️  Missing mypy type check                           │
│                                                         │
│  Best Practices:                                        │
│  ✅ Uses action caching                                 │
│  ✅ Matrix has fail-fast: false                        │
│  ⚠️  No job timeout specified                          │
│  ✅ Actions use pinned versions                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Score: 8/11 (73%)                                      │
│                                                         │
│  Suggested fixes:                                       │
│  1. Add linting step: uv run ruff check .              │
│  2. Add type checking: uv run mypy src/                │
│  3. Add timeout-minutes to jobs                         │
│                                                         │
│  Run with --fix to apply suggestions                   │
╰─────────────────────────────────────────────────────────╯
```

## Common Issues & Fixes

### Issue: Wrong Python versions

```yaml
# Before (doesn't match pyproject.toml requires-python = ">=3.10")
matrix:
  python-version: ['3.8', '3.9', '3.10']

# After
matrix:
  python-version: ['3.10', '3.11', '3.12']
```

### Issue: Missing caching

```yaml
# Before
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}

# After (with caching)
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'pip'
```

### Issue: Using @latest

```yaml
# Before (unpredictable)
- uses: actions/checkout@latest

# After (pinned)
- uses: actions/checkout@v4
```

### Issue: No timeout

```yaml
# Before
jobs:
  test:
    runs-on: ubuntu-latest

# After
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

## Auto-Fix Mode

When run with `--fix`, the command will:

1. **Backup** existing workflow
2. **Apply** safe fixes
3. **Show diff** of changes
4. **Prompt** for confirmation

```bash
/craft:ci:validate --fix
```

```
╭─ CI Auto-Fix ───────────────────────────────────────────╮
│                                                         │
│  Proposed changes to .github/workflows/ci.yml:          │
│                                                         │
│  + timeout-minutes: 30                                  │
│  + Added ruff check step                                │
│  + Added mypy type check step                           │
│                                                         │
│  Apply these changes? [y/N]                             │
╰─────────────────────────────────────────────────────────╯
```

## Badge Validation

`/craft:ci:validate` checks CI badges in README.md and docs/index.md for accuracy:

### Validation Checks

- **Workflow Exists**: Badge points to an actual workflow file in `.github/workflows/`
- **Branch Correct**: Badge URL branch parameter matches current branch
- **URL Format**: Badge URL follows GitHub Actions format

### Example Output

```
╭─ CI Badge Validation ───────────────────────────╮
│                                                  │
│  📁 README.md                                    │
│                                                  │
│    ❌ Line 3: missing_workflow                  │
│       Badge points to non-existent workflow     │
│                                                  │
│    ⚠️  Line 4: wrong_branch                     │
│       Badge uses 'main', expected 'dev'         │
│                                                  │
├──────────────────────────────────────────────────┤
│  Total: 1 error, 1 warning                      │
│  Run with --fix to update badges                │
╰──────────────────────────────────────────────────╯
```

### Execution Logic

```python
from utils.ci_badge_validator import CIBadgeValidator, format_issues_report
import subprocess

validator = CIBadgeValidator(Path.cwd())
current_branch = subprocess.run(
    ['git', 'branch', '--show-current'],
    capture_output=True,
    text=True
).stdout.strip()

badge_issues = validator.validate_badges(branch=current_branch)

if badge_issues:
    print(format_issues_report(badge_issues))

    errors = [i for i in badge_issues if i.severity == 'error']
    if errors and not args.fix:
        print("❌ Badge errors must be fixed")
        exit(1)
```

### Badge Fix Mode

When run with `--fix`, badge issues are automatically corrected:

```bash
/craft:ci:validate --fix
```

```
╭─ Badge Auto-Fix ─────────────────────────────────╮
│                                                  │
│  README.md:                                      │
│    ✓ Updated CI badge branch: main → dev        │
│                                                  │
│  docs/index.md:                                  │
│    ✓ Removed badge for deleted workflow         │
│                                                  │
│  Total: 2 badges fixed                          │
╰──────────────────────────────────────────────────╯
```

## Integration

Works with:

- `/craft:ci:detect` - Detect project configuration
- `/craft:ci:generate` - Generate new workflow
- `/craft:check ci` - Quick validation
- `/craft:code:ci-local` - Run CI checks locally

## See Also

- `/craft:ci:generate` - Generate new CI workflow
- `/craft:ci:detect` - Detect project configuration
- `/craft:check` - Pre-flight validation
- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
