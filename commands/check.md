---
description: Universal pre-flight check that validates project readiness
arguments:
  - name: mode
    description: Check depth (default|thorough)
    required: false
    default: default
  - name: for
    description: What to check for (commit|pr|release|deploy)
    required: false
  - name: dry-run
    description: Preview checks that will be performed without executing them
    required: false
    default: false
    alias: -n
---

# /craft:check - Universal Pre-flight

Run appropriate checks for your project type and context.

## Usage

```bash
/craft:check                    # Quick validation
/craft:check thorough           # Deep validation
/craft:check --for commit       # Pre-commit checks
/craft:check --for pr           # Pre-PR checks
/craft:check --for release      # Pre-release checks
/craft:check --dry-run          # Preview checks
/craft:check -n                 # Preview checks
```

## Dry-Run Mode

Preview which checks will be performed without actually executing them:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Pre-flight Validation                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Project Detection:                                          │
│   - Type: Python CLI                                          │
│   - Build tool: uv                                            │
│   - Config: pyproject.toml                                    │
│   - Worktree: No (main repo)                                  │
│   - Git status: Clean working tree                            │
│                                                               │
│ ✓ Validation Plan (5 checks):                                 │
│                                                               │
│   1. Linting (ruff)                                           │
│      Command: ruff check .                                    │
│      Scope: All Python files (~450 files)                     │
│      Estimated: ~3 seconds                                    │
│                                                               │
│   2. Type Checking (mypy)                                     │
│      Command: mypy src/                                       │
│      Scope: Source files only                                 │
│      Estimated: ~8 seconds                                    │
│                                                               │
│   3. Testing (pytest)                                         │
│      Command: pytest                                          │
│      Scope: All tests (~135 tests)                            │
│      Estimated: ~15 seconds                                   │
│                                                               │
│   4. Security Audit (pip-audit)                               │
│      Command: uv pip list | pip-audit                         │
│      Scope: All dependencies                                  │
│      Estimated: ~5 seconds                                    │
│                                                               │
│   5. Git Status                                               │
│      Command: git status --porcelain                          │
│      Scope: Working tree                                      │
│      Estimated: < 1 second                                    │
│                                                               │
│ ✓ Mode Configuration:                                         │
│   - Mode: default (quick)                                     │
│   - Context: General validation                               │
│   - Fail fast: Yes                                            │
│   - Exit on first error: Yes                                  │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Total estimated time: ~32 seconds                         │
│   • Use 'thorough' mode for comprehensive checks (~3-5 min)   │
│   • Use '--for commit' for pre-commit specific checks         │
│                                                               │
│ 📊 Summary: 5 checks, ~32 seconds execution time              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Context-Specific Dry-Run

```bash
/craft:check --for pr --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Pre-PR Validation                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Additional PR Checks:                                       │
│   6. Coverage Analysis (pytest-cov)                           │
│      Command: pytest --cov --cov-report=term                  │
│      Threshold: 80% minimum                                   │
│      Estimated: ~20 seconds                                   │
│                                                               │
│   7. Merge Conflict Detection                                 │
│      Command: git merge-tree main HEAD                        │
│      Estimated: ~2 seconds                                    │
│                                                               │
│   8. Branch Status                                            │
│      Command: git rev-list --count origin/main..HEAD          │
│      Check: Branch ahead/behind main                          │
│      Estimated: ~1 second                                     │
│                                                               │
│ 📊 Summary: 8 total checks for PR readiness (~55 seconds)     │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the validation plan based on project type and context. Read-only analysis, no actual checks performed.

## Auto-Detection

Detects project type, git context, and worktree status:

### Worktree Detection

```bash
# Check if running in a worktree
if git rev-parse --is-inside-work-tree &>/dev/null; then
  git_dir=$(git rev-parse --git-dir)
  if [[ "$git_dir" == *".git/worktrees/"* ]]; then
    echo "🌳 Running in worktree"
    echo "   Main repo: $(dirname $(dirname $(dirname $git_dir)))"
    echo "   Branch: $(git branch --show-current)"
  fi
fi
```

**Worktree-aware output:**
```
╭─ /craft:check ──────────────────────────────────────╮
│ Project: scribe (Node.js)                           │
│ 🌳 Worktree: ~/.git-worktrees/scribe/feat-hud       │
│    Main: ~/projects/dev-tools/scribe                │
│    Branch: feat/mission-control-hud                 │
├─────────────────────────────────────────────────────┤
│ ✓ Lint         0 issues                             │
│ ...                                                 │
```

Detects project type and runs appropriate checks:

### Python Projects
```
✓ Detected: Python (pyproject.toml)
Checks:
  ├── ruff check .              (linting)
  ├── mypy .                    (type checking)
  ├── pytest                    (tests)
  ├── pip-audit                 (security)
  └── /craft:docs:check-links   (if docs/ exists and changed)
```

### JavaScript/TypeScript Projects
```
✓ Detected: Node.js (package.json)
Checks:
  ├── eslint .                  (linting)
  ├── tsc --noEmit              (types)
  ├── npm test                  (tests)
  ├── npm audit                 (security)
  └── /craft:docs:check-links   (if docs/ exists and changed)
```

### R Packages
```
✓ Detected: R Package (DESCRIPTION)
Checks:
  ├── lintr::lint_package()     (linting)
  ├── devtools::check()         (R CMD check)
  ├── testthat::test_local()    (tests)
  ├── pkgdown::build_site()     (docs if configured)
  └── spelling::spell_check()   (spelling)
```

### Go Projects
```
✓ Detected: Go (go.mod)
Checks:
  ├── go vet ./...              (static analysis)
  ├── golangci-lint run         (linting)
  ├── go test ./...             (tests)
  └── go mod verify             (dependencies)
```

## Documentation Checks

**Conditional checking** - Runs only when needed:

```bash
# Check if docs/ directory exists
if [ -d "docs/" ]; then
  # Check if any docs were modified
  if git diff --name-only | grep -q "^docs/"; then
    echo "📚 Docs changed, running validation..."

    # Step 1: Markdown linting (fast, critical errors)
    echo "  → Checking markdown quality..."
    claude "/craft:docs:lint default"

    # Step 2: Link validation (internal links)
    echo "  → Checking links..."
    claude "/craft:docs:check-links default"
  else
    echo "📚 Docs unchanged, skipping validation"
  fi
fi
```

**Integration:**
- Automatically runs 2 checks when docs are changed:
  1. `/craft:docs:lint` - Markdown quality (critical errors)
  2. `/craft:docs:check-links` - Internal link validation
- Uses default mode for speed (< 6s total)
- Critical errors cause pre-flight to fail
- Prevents deploying broken documentation

## Check Modes

### Default Mode (Quick)
- Lint check (fast rules only)
- Test run (fail-fast)
- Git status
- Docs quality (if docs/ changed: lint + links)
- ~30 seconds

### Thorough Mode
- Full lint check
- Complete test suite
- Type checking
- Security audit
- Doc validation (lint + links + anchors)
- ~3-5 minutes

## Context-Specific Checks

### Pre-Commit (`--for commit`)
```
╭─ Pre-Commit Checks ─────────────────────────────────╮
│ ✓ Lint: No issues                                  │
│ ✓ Tests: 45/45 passed                              │
│ ✓ Types: No errors                                 │
│ ✓ No secrets detected                              │
├─────────────────────────────────────────────────────┤
│ READY TO COMMIT                                    │
╰─────────────────────────────────────────────────────╯
```

### Pre-PR (`--for pr`)
```
╭─ Pre-PR Checks ─────────────────────────────────────╮
│ ✓ Lint: No issues                                  │
│ ✓ Tests: 156/156 passed                            │
│ ✓ Coverage: 87% (meets 80% threshold)              │
│ ✓ Types: No errors                                 │
│ ✓ No merge conflicts                               │
│ ✓ Branch up to date with main                      │
├─────────────────────────────────────────────────────┤
│ READY FOR PR                                       │
╰─────────────────────────────────────────────────────╯
```

### Pre-Release (`--for release`)
```
╭─ Pre-Release Checks ────────────────────────────────╮
│ ✓ Lint: No issues (strict mode)                    │
│ ✓ Tests: All passing (unit + integration + e2e)    │
│ ✓ Coverage: 87% (meets threshold)                  │
│ ✓ Types: No errors                                 │
│ ✓ Security: No vulnerabilities                     │
│ ✓ Docs: Valid and up-to-date                       │
│ ✓ CHANGELOG: Updated                               │
│ ✓ Version: Bumped correctly                        │
├─────────────────────────────────────────────────────┤
│ READY FOR RELEASE                                  │
╰─────────────────────────────────────────────────────╯
```

## Output Format

### All Passing
```
╭─ /craft:check ──────────────────────────────────────╮
│ Project: aiterm (Python CLI)                       │
│ Time: 12.4s                                        │
├─────────────────────────────────────────────────────┤
│ ✓ Lint         0 issues                            │
│ ✓ Tests        135/135 passed                      │
│ ✓ Types        No errors                           │
│ ✓ Git          Clean working tree                  │
├─────────────────────────────────────────────────────┤
│ STATUS: ALL CHECKS PASSED ✓                        │
╰─────────────────────────────────────────────────────╯
```

### Issues Found
```
╭─ /craft:check ──────────────────────────────────────╮
│ Project: aiterm (Python CLI)                       │
│ Time: 15.2s                                        │
├─────────────────────────────────────────────────────┤
│ ⚠ Lint         3 issues                            │
│   └─ src/main.py:12 - Line too long               │
│   └─ src/utils.py:8 - Unused import               │
│   └─ tests/test_api.py:45 - Missing docstring     │
│                                                     │
│ ✓ Tests        135/135 passed                      │
│ ✓ Types        No errors                           │
│ ⚠ Git          Uncommitted changes                 │
├─────────────────────────────────────────────────────┤
│ STATUS: 2 ISSUES FOUND                             │
│ Fix with: /craft:code:ci-fix                       │
╰─────────────────────────────────────────────────────╯
```

## Integration

Works with:
- `/craft:code:lint` - Detailed code lint results
- `/craft:test:run` - Detailed test results
- `/craft:docs:lint` - Markdown quality validation
- `/craft:docs:check-links` - Documentation link validation
- `/craft:code:ci-fix` - Auto-fix issues
- `/craft:code:ci-local` - Full CI simulation
