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
  - name: orch
    description: Enable orchestration mode (NEW in v2.5.0)
    required: false
    default: false
  - name: orch-mode
    description: "Orchestration mode: default|debug|optimize|release (NEW in v2.5.0)"
    required: false
    default: null
  - name: context
    description: Output session context header only (no checks)
    required: false
    default: false
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
/craft:check --context              # Output session context only
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
│   - Guard: Active (block-new-code)                            │
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

## Execution Behavior (MANDATORY)

When this command runs, Claude MUST follow these steps in order. Do NOT skip
any step or proceed without showing the plan first.

### Step 0: Show Check Plan

Before running ANY checks, display what will be checked:

```text
Pre-flight Check Plan:
  Project: <project-name> (<project-type>)
  Mode: <mode>
  Branch: <current-branch>
  Guard: <protection-status>
  Context: <for-value or "general">

  Checks to run:
  1. <check-name> (<tool>)
  2. <check-name> (<tool>)
  ...
  N. <check-name> (<tool>)
```

### Context-Only Mode (--context)

When `--context` is passed, skip all checks and output only session context:

```text
┌───────────────────────────────────────────────────────────────┐
│ SESSION CONTEXT                                               │
├───────────────────────────────────────────────────────────────┤
│ Project:   <name> (<type>)                                    │
│ Branch:    <current-branch>                                   │
│ Worktree:  <path or "main repo">                              │
│ Base:      <base-branch>                                      │
│ Guard:     <status>                                           │
│ Phase:     <phase> (commits ahead: N)                         │
│ Tests:     <test-command> (N passing)                         │
│ Lint:      <lint-command>                                     │
│ Docs:      <GREEN|YELLOW|RED> (<N> issues)                    │
├───────────────────────────────────────────────────────────────┤
│ TIP: Front-load this context in prompts to reduce wrong-      │
│ approach friction.                                            │
└───────────────────────────────────────────────────────────────┘
```

**Phase detection logic:**

- `implementation`: commits ahead of base, no PR exists
- `testing`: test files modified recently
- `pr-prep`: PR exists for branch, branch is clean
- `release`: on dev branch, features merged

**How to detect:**

```bash
# Phase detection
commits_ahead=$(git rev-list --count dev..HEAD 2>/dev/null || echo 0)
pr_exists=$(gh pr list --head "$(git branch --show-current)" --json number --jq length 2>/dev/null || echo 0)
test_modified=$(git diff --name-only HEAD~3 2>/dev/null | grep -c "test" || echo 0)
tree_clean=$(git status --porcelain | wc -l | tr -d ' ')

if [[ "$(git branch --show-current)" == "dev" ]]; then
    phase="release"
elif [[ "$pr_exists" -gt 0 && "$tree_clean" -eq 0 ]]; then
    phase="pr-prep"
elif [[ "$test_modified" -gt 0 ]]; then
    phase="testing"
else
    phase="implementation"
fi

# Docs staleness one-liner for context header
docs_status=$(./scripts/docs-staleness-check.sh --json 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"status\"]} ({d[\"total_issues\"]} issues)')" 2>/dev/null \
    || echo "N/A")
```

**Insights integration (v2.21.0):**

If insights data exists (`~/.claude/usage-data/facets/`), append a friction summary to the context output:

```text
│ Insights: 3 friction patterns in last 30 days               │
│   - Wrong CWD (8x) → verify worktree before editing          │
│   - Forgot ORCHESTRATE (3x) → read on session start          │
│   Run /craft:insights for full report                        │
```

When `--context` is passed, the command exits after displaying this header. No checks are executed.

### Step 0.5: Confirm Before Running

After showing the plan, ask before executing:

```json
{
  "questions": [{
    "question": "Run these pre-flight checks?",
    "header": "Check",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes - Run all (Recommended)",
        "description": "Execute all <N> checks as shown above."
      },
      {
        "label": "Skip lint (faster)",
        "description": "Run all checks except linting."
      },
      {
        "label": "Skip external links (faster)",
        "description": "Run all checks except external link validation."
      },
      {
        "label": "Dry run (show commands only)",
        "description": "Show the exact commands without executing them."
      }
    ]
  }]
}
```

### Steps 1-N: Execute with Progress

Run each check and display results as they complete:

```text
  [1/N] <check-name>... ✅ passed (X issues)
  [2/N] <check-name>... ❌ failed (Y errors)
  ...
```

### Step N+1: Summary

```text
  Results: X/N checks passed
  Issues: Y warnings, Z errors
  Next steps: [actionable recommendations]
```

### Mode-Specific Check Lists

| Check | default | debug | release |
|-------|---------|-------|---------|
| Unit tests | Quick (fail-fast) | Verbose (all output) | Full + coverage report |
| Markdown lint | Changed files only | All files | All files + strict rules |
| Link validation | Skip external | Internal links only | All links (internal + external) |
| Version sync | Basic check | Show all version refs | Full audit with diff |
| Stale refs | Skip | Verbose scan | Full scan |
| Hook conflict | Skip | Verbose audit | Full audit |
| CLAUDE.md health | Line count only | All checks | All checks + fix suggestions |
| Git status | Summary | Detailed | Full diff + ahead/behind |

## Orchestration Mode (NEW in v2.5.0)

Use `--orch` flag to run checks via orchestrator for complex validation scenarios:

```bash
/craft:check --orch                 # Orchestrated validation with mode prompt
/craft:check --orch=optimize        # Fast parallel check execution
/craft:check --orch=release --dry-run   # Preview orchestrated validation
```

### Orchestration Flow

```python
from utils.orch_flag_handler import handle_orch_flag, show_orchestration_preview, spawn_orchestrator

orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

if orch_flag:
    should_orchestrate, mode = handle_orch_flag(
        "comprehensive project validation",
        orch_flag,
        mode_flag
    )

    if dry_run:
        show_orchestration_preview(
            f"validation workflow with {args.mode} mode",
            mode
        )
        return

    spawn_orchestrator(
        f"run comprehensive checks for {args.for or 'general'} context",
        mode
    )
    return

# Otherwise, continue with normal check flow...
```

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
│    Guard: None (feature branches unrestricted)      │
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
  ├── /craft:docs:check-links   (if docs/ exists and changed)
  └── docs-staleness-check.sh   (if scripts/ exists)
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

## Version Consistency Check (NEW in v2.22.0)

Validates that all version references in the project match the source of truth.

**Script:** `scripts/version-sync.sh`

**How it works:**

1. Discovers source of truth (priority: `.claude-plugin/plugin.json` → `package.json` → `pyproject.toml` → `DESCRIPTION` → `Cargo.toml`)
2. Checks all version files (manifests, CLAUDE.md, .STATUS)
3. Scans source code for version constants (`VERSION =`, `__version__`)
4. Reports mismatches with fix suggestions

**When it runs:**

| Context | Behavior |
|---------|----------|
| `--for commit` | Basic check — run `version-sync.sh --quiet` |
| `--for pr` | Full check — show all version references |
| `--for release` | Full audit — show all references + fix suggestions |

**Integration:**

```bash
# Called internally by /craft:check
bash scripts/version-sync.sh           # Full output
bash scripts/version-sync.sh --quiet   # Exit code only (for hooks)
bash scripts/version-sync.sh --fix     # Show fix commands
```

**Belt-and-suspenders protection:**

| Layer | When | Behavior |
|-------|------|----------|
| PreToolUse hook | During editing | Warning (non-blocking) |
| Pre-commit hook | At commit time | Blocking |
| `/craft:check` | On demand | Informational report |

## Stale Reference Scan (NEW in v2.22.0)

Detects file renames that leave stale references in documentation.

**Script:** `scripts/stale-ref-scan.sh`

**How it works:**

1. Runs `git diff --name-status` between base branch and HEAD to find renames
2. Extracts old file names from rename entries (R100, R090, etc.)
3. Greps `docs/`, `README.md`, `CLAUDE.md`, and `tutorials/` for old names
4. Reports files that still reference the old name

**When it runs:** `--for pr` and `--for release`

```bash
bash scripts/stale-ref-scan.sh dev      # Compare against dev
bash scripts/stale-ref-scan.sh --quiet  # Exit code only
```

## Hook Conflict Audit (NEW in v2.22.0)

Audits git hooks for rules that might block Claude Code operations.

**Script:** `scripts/hook-conflict-audit.sh`

**What it checks:**

- `.githooks/`, `.husky/`, `.git/hooks/` for branch protection rules
- Pre-commit hooks with strict linting that may reject auto-generated changes
- Pre-push hooks with test suites that may slow or block pushes
- Commit-msg hooks with conventional commit enforcement
- lint-staged configuration

**When it runs:** `--for pr` and `--for release`

```bash
bash scripts/hook-conflict-audit.sh --for pr       # PR-specific audit
bash scripts/hook-conflict-audit.sh --for release   # Release-specific audit
```

## Badge URL Validation (NEW in v2.27.0)

Validates that CI badge URLs in README.md and docs/index.md include both `?branch=main` and `?branch=dev` variants. Ensures badges are not hardcoded to a single branch.

**When it runs:** `--for release` and `--for deploy`

**What it checks:**

- README.md badge URLs include `?branch=main` variant
- README.md badge URLs include `?branch=dev` variant
- docs/index.md badge URLs include `?branch=main` variant
- docs/index.md badge URLs include `?branch=dev` variant
- All badge URLs resolve (HTTP 200)

**Severity:** error (blocking)

```bash
# Example validation
grep -E 'badge.*\?branch=' README.md docs/index.md
# Expect both ?branch=main and ?branch=dev for each workflow badge
```

## Homebrew Formula Desc Validation (NEW in v2.27.0)

Checks that the Homebrew formula `desc` field command counts match actual counts from the project. Prevents the formula description from drifting out of sync after adding or removing commands.

**When it runs:** `--for release`

**What it checks:**

- Parses `desc` field from the Homebrew formula (`homebrew-tap/Formula/craft.rb`)
- Extracts any numeric counts mentioned (e.g., "107 commands")
- Compares against actual command count from `scripts/validate-counts.sh`
- Reports mismatch if counts differ

**Severity:** warning (not blocking)

```bash
# Example check
formula_desc=$(grep 'desc "' ../homebrew-tap/Formula/craft.rb | sed 's/.*desc "//;s/"//')
actual_count=$(find commands/ -name '*.md' | wc -l | tr -d ' ')
# Compare counts extracted from desc vs actual
```

## CLAUDE.md Health Check (NEW in v2.22.0)

Basic health check for CLAUDE.md files.

**Script:** `scripts/claude-md-health.sh`

**What it checks:**

- Line count (warns if >200, since system prompt truncates)
- Version reference presence
- Staleness (days since last update vs latest commit)
- Count accuracy (e.g., "111 commands" claim vs actual count)

**When it runs:** `--for pr` and `--for release`

```bash
bash scripts/claude-md-health.sh           # Full check
bash scripts/claude-md-health.sh --quiet   # Exit code only
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

## Instruction Health Check (NEW in v2.22.0)

Validates CLAUDE.md accuracy and instruction system health:

```bash
# Run as part of /craft:check (auto-included in all modes)
PYTHONPATH=. python3 utils/claude_md_sync.py --check-only
```

### What Gets Checked

1. **Count accuracy** — Commands, skills, agents, specs, tests match filesystem
2. **Line budget** — Global CLAUDE.md < 100 lines, project CLAUDE.md < 100 lines
3. **Reference file freshness** — `.claude/reference/` files exist and are current
4. **CLAUDE.md lint** — No broken internal links, no stale version references

### Output Format

```
╭─ Instruction Health ────────────────────────────╮
│ CLAUDE.md Counts:                                │
│   Commands: 111 ✅    Skills: 25 ✅               │
│   Agents:   8 ✅      Specs:  30 ✅               │
│   Tests:    ~1575 ✅                              │
│                                                   │
│ Line Budget:                                      │
│   Global CLAUDE.md:  85 lines ✅ (< 100)          │
│   Project CLAUDE.md: 82 lines ✅ (< 100)          │
│                                                   │
│ Reference Files:                                  │
│   .claude/reference/agents.md ✅                  │
│   .claude/reference/test-suite.md ✅              │
│   .claude/reference/project-structure.md ✅       │
│                                                   │
│ CLAUDE.md Lint: No issues ✅                      │
╰─────────────────────────────────────────────────╯
```

### Severity Levels

| Issue | Severity | Action |
|-------|----------|--------|
| Stale count (off by > 5%) | 🔴 ERROR | Auto-fix with `claude_md_sync.py` |
| Line budget exceeded | 🟡 WARNING | Suggest extracting sections to reference/ |
| Missing reference file | 🟡 WARNING | Suggest running `--generate-reference` |
| Stale version reference | 🟡 WARNING | Show current vs documented version |
| Broken CLAUDE.md link | 🔴 ERROR | Show broken path and suggest fix |

### Mode-Specific Behavior

| Check | default | thorough | `--for pr` | `--for release` |
|-------|---------|----------|------------|-----------------|
| Count accuracy | ✅ | ✅ | ✅ | ✅ |
| Line budget | Skip | ✅ | ✅ | ✅ |
| Reference files | Skip | ✅ | ✅ | ✅ |
| CLAUDE.md lint | Skip | ✅ | ✅ | ✅ |
| Auto-fix stale | No | No | No | Yes |

## Check Modes

### Default Mode (Quick)

- Lint check (fast rules only)
- Test run (fail-fast)
- Git status
- Docs quality (if docs/ changed: lint + links)
- Instruction health (count accuracy only)

### Thorough Mode

- Full lint check
- Complete test suite
- Type checking
- Security audit
- Doc validation (lint + links + anchors)
- Instruction health (full check)

### Context-Specific Check Lists (`--for` flag)

The `--for` flag adjusts which checks run based on what you're preparing for:

| Check | `--for commit` | `--for pr` | `--for release` | `--for deploy` |
|-------|---------------|-----------|----------------|---------------|
| Git status | Clean tree | Ahead of base | Tag exists | Clean + tagged |
| Lint | Changed files | All files | All + strict | All + strict |
| Tests | Fast (fail-fast) | Full suite | Full + coverage | Full + coverage |
| Type check | Skip | Run | Run | Run |
| Security | Skip | Advisory | Full audit | Full audit |
| Links | Skip | Internal | All links | All links |
| Version sync | Basic check | Check | Full audit | Full audit |
| Stale refs | Skip | Scan | Scan | Scan |
| Hook conflict | Skip | Audit | Audit | Audit |
| CLAUDE.md health | Skip | Basic | Full | Full |
| Merge conflicts | Skip | Detect | N/A | N/A |
| Coverage threshold | Skip | 80% min | 90% min | 90% min |
| Instruction health | Counts only | Full check | Full check | Full + auto-fix |
| Badge URLs | Skip | Skip | Validate both branches | Validate both branches |
| Formula desc | Skip | Skip | Check counts match | Skip |

When `--for` is specified, the Step 0 preview shows this context:

```text
Pre-flight Check Plan:
  Project: craft (Claude Code Plugin)
  Mode: default
  Branch: feature/command-enhancements
  Context: pr (pre-PR validation)

  Checks to run (8 for PR context):
  1. Git status (ahead of dev?)
  2. Lint — all files (ruff / markdownlint)
  3. Unit tests — full suite (python3 tests/test_craft_plugin.py)
  4. Type check (mypy, if applicable)
  5. Security advisory (pip-audit / npm audit)
  6. Internal link validation
  7. Merge conflict detection (git merge-tree)
  8. Coverage threshold (80% minimum)
```

## Hot-Reload Validator Discovery (NEW in v1.23.0)

**Dynamic validator discovery** - Auto-detects validation skills without restart:

### How It Works

1. **Scan for validators**: `/craft:check` scans `.claude-plugin/skills/validation/*.md`
2. **Parse frontmatter**: Detects validators with `hot_reload: true` flag
3. **Execute in fork**: Runs each validator in isolated context
4. **Aggregate results**: Combines all validator outputs

### Built-in Validators

| Validator | Languages | Tools | Purpose |
|-----------|-----------|-------|---------|
| **test-coverage** | Python, JS, R, Go | pytest-cov, jest, covr, go test | Coverage validation |
| **broken-links** | All | test_craft_plugin.py | Internal link validation |
| **lint-check** | Python, JS, TS, R, Go, Rust | ruff, eslint, lintr, golangci-lint, clippy | Code quality |

### Mode-Aware Behavior

Validators adapt to execution mode:

```
| Mode     | Coverage | Lint Severity | Auto-fix |
|----------|----------|---------------|----------|
| default  | 70%      | Warnings+     | No       |
| debug    | 60%      | All           | No       |
| optimize | 75%      | Errors        | Yes      |
| release  | 90%      | Errors        | No       |
```

### Example Output

```
╭─ /craft:check (with validators) ────────────────────╮
│ Project: craft (Claude Code Plugin)                │
│ Mode: default                                       │
├─────────────────────────────────────────────────────┤
│ Core Checks:                                        │
│ ✓ Git          Clean working tree                  │
│ ✓ Project      Valid plugin manifest               │
│                                                     │
│ Hot-Reload Validators (3 discovered):               │
│ ✓ test-coverage   87% >= 70% (default mode)        │
│ ✓ broken-links    No broken links (342 checked)    │
│ ✓ lint-check      No issues (ruff)                 │
├─────────────────────────────────────────────────────┤
│ STATUS: ALL CHECKS PASSED ✓                        │
│ Validators: 3/3 passed                              │
╰─────────────────────────────────────────────────────╯
```

### Orchestration Examples (v2.5.0)

```
User: /craft:check --orch=optimize

→ ORCHESTRATOR v2.1 — OPTIMIZE MODE
Spawning orchestrator...
   Task: run comprehensive checks for general context
   Mode: optimize

Executing: /craft:orchestrate 'run comprehensive checks for general context' optimize
```

```
User: /craft:check --orch=release --dry-run

+---------------------------------------------------------------------+
| DRY RUN: Orchestration Preview                                      |
+---------------------------------------------------------------------+
| Task: validation workflow with default mode                         |
| Mode: release                                                       |
| Max Agents: 4                                                       |
| Compression: 85%                                                    |
+---------------------------------------------------------------------+
| This would spawn the orchestrator with the above settings.          |
| Remove --dry-run to execute.                                        |
+---------------------------------------------------------------------+
```

```
User: /craft:check --for pr --orch

→ Orchestration Mode Selection
Available modes:
  default   - Quick tasks (2 agents max, 70% compression)
  debug     - Sequential troubleshooting (1 agent, 90% compression)
  optimize  - Fast parallel work (4 agents, 60% compression)
  release   - Pre-release audit (4 agents, 85% compression)

[AskUserQuestion prompt appears]
```

### Adding Custom Validators

Create a new validator in `.claude-plugin/skills/validation/`:

```markdown
---
name: check:my-validator
description: Custom validation logic
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# Custom Validator Implementation

## Auto-Detection
[Detect your project type]

## Validation Logic
[Run your validation tool]

## Output Format
[Report pass/fail with details]
```

**Requirements:**

- Must have `hot_reload: true` in frontmatter
- Must use `context: fork` for isolation
- Must report clear pass/fail status
- Should be mode-aware (check `$CRAFT_MODE`)
- Should gracefully skip if tools unavailable

### Validator Execution Flow

```
1. Scan: .claude-plugin/skills/validation/*.md
2. Filter: Only files with hot_reload: true
3. Execute: In forked context (isolated)
4. Collect: Exit codes and stdout/stderr
5. Report: Aggregated pass/fail summary
```

**Benefits:**

- ✅ **No restart required** - Add validators on the fly
- ✅ **Isolated execution** - Validators don't corrupt context
- ✅ **Community extensible** - Users can add custom validators
- ✅ **Mode-aware** - Behavior adapts to context
- ✅ **Multi-language** - Works across tech stacks

### Community Validator Ecosystem (NEW in v1.23.0)

**Generate custom validators**:

```bash
/craft:check:gen-validator security-audit --languages "python,javascript"
```

**Discover community validators**:

- [GitHub Validator Marketplace](https://github.com/topics/craft-plugin-validator)
- Search by language: `craft-plugin-validator+python`
- 100+ community validators available

**Install validators**:

```bash
# Direct download
curl -o .claude-plugin/skills/validation/security-audit.md \
  https://raw.githubusercontent.com/user/repo/main/validator.md

# Test validator
CRAFT_MODE=default bash .claude-plugin/skills/validation/security-audit.md

# Auto-detected by /craft:check
/craft:check  # Runs all discovered validators
```

**Validator registry** (community-maintained):

| Validator | Languages | Purpose |
|-----------|-----------|---------|
| security-audit | Python, JS | Vulnerability scanning |
| performance-check | Python, JS | Performance profiling |
| accessibility | Web | Accessibility validation |
| license-check | All | License compliance |
| dependency-audit | Python, JS, Go | Dependency vulnerabilities |

**Resources**:

- [Validator Generator](/craft:check:gen-validator)
- [Best Practices Guide](../docs/VALIDATOR-BEST-PRACTICES.md)
- [Example Validators](https://github.com/topics/craft-plugin-validator)

## Context-Specific Checks

### Pre-Commit (`--for commit`)

```
╭─ Pre-Commit Checks ─────────────────────────────────╮
│ ✓ Lint: No issues                                  │
│ ✓ Tests: 45/45 passed                              │
│ ✓ Types: No errors                                 │
│ ✓ No secrets detected                              │
│ ✓ Version sync: All match v2.21.0                  │
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
│ ✓ Version sync: All match v2.21.0                  │
│ ✓ Stale refs: No renames with stale docs           │
│ ✓ Hook audit: No conflicts detected                │
│ ✓ CLAUDE.md: Healthy (161 lines)                   │
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
│ ✓ Version: Bumped correctly (full audit)           │
│ ✓ Stale refs: No renames with stale docs           │
│ ✓ Hook audit: No conflicts for release             │
│ ✓ CLAUDE.md: Healthy (161 lines, counts accurate)  │
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
- `/craft:test` - Detailed test results
- `/craft:docs:lint` - Markdown quality validation
- `/craft:docs:check-links` - Documentation link validation
- `/craft:code:ci-fix` - Auto-fix issues
- `/craft:code:ci-local` - Full CI simulation
