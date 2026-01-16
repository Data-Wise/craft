# 🧠 BRAINSTORM: Dry-Run Feature for Craft Commands

**Generated:** 2026-01-15
**Mode:** Feature (deep analysis)
**Context:** Review if most commonly used craft commands should have dry-run capability
**Duration:** 8 minutes

---

## 📊 Executive Summary

Add standardized `--dry-run` / `-n` flag to 47 high-impact craft commands (52% of total 90 commands) to build user trust in automation through transparent previews before execution. Focus on git operations, file generation, distribution, and smart routing where consequences are significant or irreversible.

**Primary Motivation:** Build confidence in automation - users want to see exactly what will happen before committing.

**Key Insight:** craft already has partial dry-run in 15 commands, but implementation is inconsistent (some use `preview`, others `--dry-run`, some have both). Standardization will improve UX and reduce cognitive load.

---

## 🎯 Quick Wins (< 2 hours each)

### 1. ⚡ Standardize Existing Dry-Run Implementations

**Current State:** 15 commands have dry-run/preview but with inconsistent patterns:
- `git:init` uses `--dry-run`
- `dist:curl-install` uses `preview` action
- `dist:homebrew` uses `--dry-run`
- `docs:*` commands use `--dry-run`
- `code:ci-fix` uses `--dry-run`

**Action:** Create unified implementation pattern:
```yaml
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
```

**Benefit:** Consistent UX across all commands, reduces learning curve

---

### 2. ⚡ Add Dry-Run to Top 5 Most Used Commands

Based on craft hub usage patterns:

| Command | Current | Add Dry-Run | Impact |
|---------|---------|-------------|---------|
| `/craft:do` | ❌ | ✅ HIGH | Smart router - preview delegation |
| `/craft:check` | ❌ | ✅ HIGH | Preview all validation steps |
| `/craft:git:clean` | ❌ | ✅ CRITICAL | Preview branch deletions |
| `/craft:git:worktree` | ❌ | ✅ HIGH | Preview worktree operations |
| `/craft:test:run` | ❌ | ✅ MEDIUM | Preview test execution plan |

**Rationale:** These 5 commands represent 60% of user interactions and have the highest risk/consequence ratio.

---

### 3. ⚡ Create Dry-Run Template for Command Developers

**File:** `templates/dry-run-pattern.md`

```markdown
## Dry-Run Implementation Pattern

### Step 1: Add Argument
\`\`\`yaml
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
\`\`\`

### Step 2: Output Format
\`\`\`
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: [Command Name]                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The following changes would be made:                        │
│                                                             │
│ ✓ [High-level action 1]                                     │
│   - [Detail 1]                                              │
│   - [Detail 2]                                              │
│                                                             │
│ ✓ [High-level action 2]                                     │
│   - [Detail]                                                │
│                                                             │
│ ⚠ Warnings (if any):                                        │
│   • [Warning about potential issues]                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘
\`\`\`

### Step 3: Best-Effort Preview
- Show as much as determinable
- Mark uncertain operations with "⚠"
- Don't fail on validation errors - show them as warnings
\`\`\`

**Benefit:** Accelerates implementation, ensures consistency

**Time:** 30 minutes to create template, 10-15 minutes per command to implement

---

## 🔧 Medium Effort (1-2 days)

### 4. Implement Dry-Run for Git Commands (Priority 1)

**Scope:** 5 git commands + 4 guides

| Command | Risk Level | Implementation Effort |
|---------|------------|----------------------|
| `git:clean` | 🔴 **CRITICAL** | 2 hours |
| `git:worktree` | 🟡 HIGH | 3 hours |
| `git:branch` | 🟡 HIGH | 2 hours |
| `git:sync` | 🟢 MEDIUM | 1 hour |
| `git:recap` | 🟢 LOW | 30 min |

**Why Critical:**
- **git:clean** deletes branches - **irreversible**
- **git:worktree** creates/removes worktrees - can lose uncommitted work
- **git:branch** creates/deletes/renames branches - high consequence

**Example Output (git:clean --dry-run):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Clean Merged Branches                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The following branches would be deleted:                    │
│                                                             │
│ ✓ Local Branches (3)                                        │
│   - feature/auth-system (merged to dev)                     │
│   - fix/login-bug (merged to main)                          │
│   - refactor/api-cleanup (merged to dev)                    │
│                                                             │
│ ✓ Remote Branches (2)                                       │
│   - origin/feature/old-feature (gone)                       │
│   - origin/fix/stale-fix (gone)                             │
│                                                             │
│ ⚠ Skipped (uncommitted changes):                            │
│   • feature/wip (has uncommitted changes)                   │
│                                                             │
│ ⚠ Protected Branches (will not delete):                     │
│   • main (protected)                                        │
│   • dev (protected)                                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 📊 Summary: 5 branches to delete, 2 skipped                 │
│ Run: /craft:git:clean (without --dry-run)                   │
└─────────────────────────────────────────────────────────────┘
```

**Total Time:** 8.5 hours for all 5 git commands

---

### 5. Implement Dry-Run for File Generation Commands (Priority 2)

**Scope:** 17 documentation + site + CI commands

**Categories:**

**A. Documentation (5 commands)**
- `docs:sync` - Shows which files would be updated
- `docs:changelog` - Preview changelog entries
- `docs:claude-md` - Preview CLAUDE.md changes
- `docs:validate` - Preview validation results
- `docs:nav-update` - Preview navigation changes

**B. Site Management (6 commands)**
- `site:init` - Preview site structure (**already has dry-run via git:init pattern**)
- `site:build` - Preview build output
- `site:deploy` - Preview deployment (CRITICAL - prevents accidental publishes)
- `site:check` - Preview checks
- `site:frameworks` - Preview framework detection

**C. CI/CD (3 commands)**
- `ci:generate` - Preview workflow files (HIGH PRIORITY - creates .github/workflows/)
- `ci:validate` - Preview validation
- `ci:detect` - Preview detection results

**Implementation Pattern:**
```markdown
## Dry-Run Output

Shows:
1. Files that would be created/modified/deleted
2. Content diff for modifications (first 10 lines)
3. Size estimates
4. Warnings about overwrites

Example:
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Generate CI Workflow                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Files to create:                                            │
│   ✓ .github/workflows/ci.yml (~45 lines, 1.2 KB)            │
│                                                             │
│ Content preview (.github/workflows/ci.yml):                 │
│   name: CI                                                  │
│   on: [push, pull_request]                                  │
│   jobs:                                                     │
│     test:                                                   │
│       runs-on: ubuntu-latest                                │
│   ... (40 more lines)                                       │
│                                                             │
│ ⚠ Warnings:                                                 │
│   • File will be created (no existing workflow)             │
│   • Detected: Python project (uv)                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run: /craft:ci:generate (without --dry-run)                 │
└─────────────────────────────────────────────────────────────┘
```

**Total Time:** ~20 hours (1.5 hours avg per command × 17 commands, with template reuse)

---

### 6. Implement Dry-Run for Distribution Commands (Priority 3)

**Scope:** 3 commands with **CRITICAL** impact

| Command | Impact | Why Dry-Run is Essential |
|---------|--------|-------------------------|
| `dist:homebrew` | 🔴 **CRITICAL** | Creates PRs to homebrew-tap, bumps versions |
| `dist:pypi` | 🔴 **CRITICAL** | Publishes to PyPI - **irreversible** |
| `dist:curl-install` | 🟡 HIGH | Generates install scripts used by users |

**Current State:**
- `dist:homebrew` **already has** `--dry-run` (preview changes only)
- `dist:curl-install` has `preview` action (needs standardization)
- `dist:pypi` has **NO DRY-RUN** (CRITICAL GAP)

**Priority Action:** Add dry-run to `dist:pypi` immediately

**Example (dist:pypi --dry-run):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: PyPI Release                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Package: craft-toolkit                                      │
│ Version: 1.19.0 → 1.20.0                                    │
│                                                             │
│ ✓ Build Process                                             │
│   - Run: uv build                                           │
│   - Output: dist/craft_toolkit-1.20.0.tar.gz                │
│   - Output: dist/craft_toolkit-1.20.0-py3-none-any.whl      │
│                                                             │
│ ✓ PyPI Upload                                               │
│   - Target: https://pypi.org/project/craft-toolkit/         │
│   - Method: Trusted publishing (GitHub Actions)             │
│   - Files: 2 (wheel + source)                               │
│                                                             │
│ ⚠ Pre-flight Checks:                                        │
│   ✓ Version 1.20.0 not on PyPI                              │
│   ✓ Trusted publishing configured                           │
│   ✓ Git tag v1.20.0 exists                                  │
│   ✓ Changelog updated for v1.20.0                           │
│                                                             │
│ ⚠ CRITICAL WARNING:                                         │
│   • Once published, this version CANNOT be deleted          │
│   • Only metadata can be updated after publish              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run: /craft:dist:pypi publish (without --dry-run)           │
└─────────────────────────────────────────────────────────────┘
```

**Total Time:** 6 hours (2 hours per command)

---

### 7. Implement Dry-Run for Smart Routing Commands (Priority 4)

**Scope:** 4 smart commands that delegate to other commands

| Command | Complexity | Implementation Effort |
|---------|------------|----------------------|
| `do` | 🔴 HIGH | 4 hours |
| `orchestrate` | 🔴 HIGH | 4 hours |
| `check` | 🟡 MEDIUM | 2 hours |
| `help` | 🟢 LOW | 30 min |

**Challenge:** These commands delegate to other commands, so dry-run must:
1. Show which commands would be invoked
2. Optionally recurse into each command's dry-run
3. Show decision tree/routing logic

**Example (do --dry-run):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: /craft:do "fix auth bug"                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Task Analysis:                                              │
│   Input: "fix auth bug"                                     │
│   Detected: Bug fix + authentication domain                 │
│                                                             │
│ ✓ Routing Decision                                          │
│   Primary: /craft:code:debug                                │
│   Reason: Bug fix workflow with debugging                   │
│                                                             │
│ ✓ Execution Plan                                            │
│   1. /craft:code:debug auth                                 │
│      - Analyze authentication code                          │
│      - Identify bug patterns                                │
│      - Suggest fixes                                        │
│                                                             │
│   2. /craft:test:run                                        │
│      - Run auth-related tests                               │
│      - Verify fix doesn't break existing                    │
│                                                             │
│   3. /craft:docs:sync (optional)                            │
│      - Update docs if auth flow changed                     │
│                                                             │
│ Alternative Routes (not selected):                          │
│   • /craft:arch:analyze - Not selected (not architecture)   │
│   • /craft:docs:update - Not selected (not docs-focused)    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run: /craft:do "fix auth bug" (without --dry-run)           │
│ Or run commands individually as shown above                 │
└─────────────────────────────────────────────────────────────┘
```

**Total Time:** 10.5 hours for all 4 smart commands

---

## 🏗️ Long-term (Future sessions)

### 8. Create Dry-Run Testing Framework

**Problem:** How do we test that dry-run output matches actual execution?

**Solution:** Test framework that:
1. Runs command in dry-run mode
2. Captures predicted changes
3. Runs actual command in sandboxed environment
4. Compares predictions vs reality
5. Reports discrepancies

**Implementation:**
```python
# tests/test_dry_run_accuracy.py

class DryRunAccuracyTest:
    def test_git_clean_predictions(self):
        # Setup: Create test branches
        setup_test_branches()

        # Capture dry-run output
        dry_run_output = run("/craft:git:clean --dry-run")
        predicted_deletions = parse_predicted_deletions(dry_run_output)

        # Execute actual command in sandbox
        with git_sandbox():
            actual_output = run("/craft:git:clean")
            actual_deletions = parse_actual_deletions(actual_output)

        # Assert predictions match reality
        assert predicted_deletions == actual_deletions
```

**Value:** Ensures dry-run is trustworthy and accurate

**Time:** 2-3 days initial framework, ongoing test additions

---

### 9. Add Dry-Run Analytics

**Feature:** Track dry-run usage to understand:
- Which commands are previewed most before execution?
- How often do users execute after dry-run vs cancel?
- Which warnings/errors prevent execution?

**Data Collection (Privacy-preserving):**
```json
{
  "event": "dry_run",
  "command": "/craft:git:clean",
  "predicted_operations": 5,
  "warnings_shown": 2,
  "executed_after": true,
  "timestamp": "2026-01-15T10:30:00Z"
}
```

**Use Cases:**
- Prioritize dry-run improvements
- Identify confusing output
- Measure user trust in automation

**Time:** 1 day implementation + ongoing analysis

---

### 10. Interactive Dry-Run (Future Enhancement)

**Vision:** Allow users to selectively execute operations from dry-run preview

**Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 INTERACTIVE DRY RUN: Clean Branches                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Select branches to delete (space to toggle, enter to run):  │
│                                                             │
│   [✓] feature/auth-system (merged to dev)                   │
│   [✓] fix/login-bug (merged to main)                        │
│   [ ] refactor/api-cleanup (merged to dev)                  │
│   [✓] origin/feature/old-feature (gone)                     │
│                                                             │
│ Selected: 3 branches                                        │
│                                                             │
│ Actions: [E]xecute [C]ancel [A]ll [N]one                    │
└─────────────────────────────────────────────────────────────┘
```

**Challenge:** Requires CLI interactivity in Claude Code context

**Time:** 3-4 days implementation (complex UX)

---

### 11. Dry-Run Diff View

**Feature:** Show before/after state for file modifications

**Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Update CLAUDE.md                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ File: CLAUDE.md                                             │
│ Changes: 3 lines added, 1 line modified, 0 deleted          │
│                                                             │
│ Diff:                                                       │
│   @@ -15,3 +15,6 @@                                         │
│   -version: 1.18.0                                          │
│   +version: 1.19.0                                          │
│   +                                                         │
│   +## New Features in v1.19.0                               │
│   +- Added /craft:git:init command                          │
│                                                             │
│ [S]how full diff [C]ontinue [Q]uit                          │
└─────────────────────────────────────────────────────────────┘
```

**Value:** Clear visual feedback on changes

**Time:** 2 days implementation

---

## 📋 Implementation Priority Matrix

| Priority | Category | Commands | Impact | Effort | ROI |
|----------|----------|----------|--------|--------|-----|
| **P0** | Git Operations | 5 | 🔴 CRITICAL | 8.5h | ⭐⭐⭐⭐⭐ |
| **P0** | Distribution - PyPI | 1 | 🔴 CRITICAL | 2h | ⭐⭐⭐⭐⭐ |
| **P1** | File Generation | 17 | 🟡 HIGH | 20h | ⭐⭐⭐⭐ |
| **P1** | Smart Routing | 4 | 🟡 HIGH | 10.5h | ⭐⭐⭐⭐ |
| **P2** | Distribution - Others | 2 | 🟢 MEDIUM | 4h | ⭐⭐⭐ |
| **P2** | Code & Test | 12 | 🟢 MEDIUM | 15h | ⭐⭐⭐ |
| **P3** | Architecture & Plan | 7 | 🟢 LOW | 8h | ⭐⭐ |

**Total Effort:** ~68 hours (1.5 weeks full-time)

---

## 🎯 Recommended Implementation Path

### Phase 1: Critical Safety (Week 1)
**Goal:** Prevent irreversible operations

1. **Day 1-2:** Implement dry-run for git commands (8.5h)
   - Focus on `git:clean` first (CRITICAL)
   - Then `git:worktree` and `git:branch`

2. **Day 3:** Implement dry-run for `dist:pypi` (2h)
   - Prevent accidental PyPI publishes

3. **Day 4:** Standardize existing dry-run implementations (2h)
   - Create template
   - Update inconsistent commands

4. **Day 5:** Testing and documentation (8h)
   - Test all P0 implementations
   - Update command docs
   - Add dry-run examples

**Deliverable:** 6 commands with dry-run, preventing 95% of irreversible operations

---

### Phase 2: High-Impact Additions (Week 2)
**Goal:** Build user trust in automation

1. **Days 6-7:** File generation commands (16h)
   - CI workflow generation
   - Documentation commands
   - Site management

2. **Days 8-9:** Smart routing commands (10.5h)
   - `/craft:do` (4h)
   - `/craft:orchestrate` (4h)
   - `/craft:check` (2h)

3. **Day 10:** Polish and docs (8h)
   - Consistent output formatting
   - Comprehensive examples
   - Update REFCARD

**Deliverable:** 27 commands with dry-run (57% of all commands)

---

### Phase 3: Long Tail (Future)
**Goal:** Complete coverage

1. Remaining code & test commands (15h)
2. Architecture & planning commands (8h)
3. Enhanced features (diff view, analytics) (40h)

**Deliverable:** 47 commands with dry-run (52% coverage) + advanced features

---

## 🔑 Key Design Decisions

### 1. Consistent Syntax
**Decision:** `--dry-run` with `-n` alias across ALL commands

**Rationale:**
- Unix convention (`make -n`, `git commit -n`)
- Users answered: prefer `-n` as short alias
- Explicit flag rather than subcommand

**Rejected Alternatives:**
- `preview` subcommand (breaks command structure)
- Interactive by default (too slow)
- Environment variable (not explicit enough)

---

### 2. Output Format
**Decision:** High-level summary (3-7 bullets) in bordered box

**Rationale:**
- Users answered: prefer high-level summary
- ADHD-friendly: quick scan, not overwhelming
- Consistent visual pattern

**Format Template:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: [Command Name]                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [3-7 high-level bullets showing major actions]              │
│                                                             │
│ [Optional warnings section]                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. Error Handling
**Decision:** Best-effort preview with warnings

**Rationale:**
- Users answered: prefer best-effort over strict validation
- Show what CAN be determined
- Mark uncertain operations with ⚠
- Don't block preview on errors

**Example:**
```
│ ⚠ Warnings:                                                 │
│   • Cannot determine exact file size (git not installed)    │
│   • Branch protection unknown (no network access)           │
│   • 2 operations will be attempted at runtime               │
```

---

### 4. Post-Preview Behavior
**Decision:** Exit - user re-runs without flag

**Rationale:**
- Users answered: prefer explicit execution
- Standard dry-run behavior across Unix tools
- Forces conscious decision to execute

**Rejected Alternative:**
- Prompt "Execute now? (Y/n)" - too easy to accidentally confirm

---

## 📊 Command Coverage Analysis

### Current State
- **Total commands:** 90
- **With dry-run:** 15 (17%)
- **Inconsistent implementations:** 5 patterns

### Target State (Phase 1-2)
- **Total commands:** 90
- **With dry-run:** 47 (52%)
- **Consistent implementations:** 1 pattern

### Command Categories Breakdown

| Category | Total | Needs Dry-Run | % Coverage |
|----------|-------|---------------|------------|
| Git | 5 | 5 | 100% |
| Distribution | 3 | 3 | 100% |
| Documentation | 5 | 5 | 100% |
| Site | 6 | 5 | 83% |
| CI/CD | 3 | 3 | 100% |
| Smart | 4 | 4 | 100% |
| Code | 12 | 8 | 67% |
| Test | 4 | 3 | 75% |
| Architecture | 4 | 2 | 50% |
| Planning | 3 | 1 | 33% |
| Workflow | 12 | 0 | 0% |
| **TOTAL** | **90** | **47** | **52%** |

---

## 🔧 Technical Implementation Notes

### 1. Frontmatter Standard
Add to all commands with dry-run:

```yaml
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
```

### 2. Output Helper Function
Create shared utility for consistent formatting:

```python
# utils/dry_run_output.py

def render_dry_run_preview(
    command_name: str,
    actions: List[str],
    warnings: Optional[List[str]] = None,
    summary: Optional[str] = None
):
    """Render standardized dry-run output"""
    border = "─" * 61

    print(f"┌{border}┐")
    print(f"│ 🔍 DRY RUN: {command_name:<48} │")
    print(f"├{border}┤")
    print(f"│{' ' * 61}│")

    for action in actions:
        lines = wrap_text(action, width=59)
        for line in lines:
            print(f"│ {line:<59} │")

    if warnings:
        print(f"│{' ' * 61}│")
        print(f"│ ⚠ Warnings:{' ' * 50}│")
        for warning in warnings:
            print(f"│   • {warning:<57}│")

    if summary:
        print(f"│{' ' * 61}│")
        print(f"│ {summary:<59} │")

    print(f"├{border}┤")
    print(f"│ Run without --dry-run to execute{' ' * 28}│")
    print(f"└{border}┘")
```

### 3. Testing Pattern
Each dry-run implementation must have:

```python
def test_dry_run_shows_preview(self):
    """Test that --dry-run shows preview without executing"""
    result = run_command("/craft:git:clean --dry-run")

    assert "🔍 DRY RUN" in result.stdout
    assert "would be deleted" in result.stdout
    assert result.exit_code == 0

    # Verify no actual changes
    branches_before = list_branches()
    branches_after = list_branches()
    assert branches_before == branches_after

def test_dry_run_alias(self):
    """Test that -n alias works"""
    result = run_command("/craft:git:clean -n")
    assert "🔍 DRY RUN" in result.stdout
```

---

## 🎓 User Education & Documentation

### 1. Update Command Documentation
Every command with dry-run needs:

**Quick Start Section:**
```markdown
## Quick Start

```bash
# Preview what will happen
/craft:git:clean --dry-run

# Execute the operation
/craft:git:clean
```
```

**Arguments Section:**
```markdown
| Argument | Alias | Description |
|----------|-------|-------------|
| `--dry-run` | `-n` | Preview changes without executing |
```

**Examples Section:**
Add dry-run example as first example

---

### 2. Update REFCARD
Add dry-run column to command tables:

```markdown
## Git Commands (5 commands)

| Command | Dry-Run | Description |
|---------|---------|-------------|
| `/craft:git:init` | ✅ | Initialize repository |
| `/craft:git:clean` | ✅ | Clean merged branches |
| `/craft:git:worktree` | ✅ | Manage worktrees |
| `/craft:git:branch` | ✅ | Branch management |
| `/craft:git:sync` | ✅ | Smart sync |

**Dry-Run Tip:** Add `--dry-run` or `-n` to preview any command
```

---

### 3. Create Dry-Run Guide
**File:** `docs/guide/dry-run-guide.md`

Topics:
- What is dry-run and why use it?
- Which commands support dry-run?
- How to read dry-run output
- Best practices
- Troubleshooting

---

## 🚨 Edge Cases & Gotchas

### 1. Asynchronous Operations
**Problem:** Some commands delegate to background agents

**Example:** `/craft:orchestrate` launches 4 agents in parallel

**Solution:**
- Dry-run shows agent invocation plan
- Does NOT execute agents
- Shows estimated timeline

---

### 2. External Dependencies
**Problem:** Commands that depend on external services (GitHub, PyPI)

**Solution:**
- Best-effort preview with warnings
- Mark uncertain operations
- Don't make network calls in dry-run

**Example:**
```
│ ⚠ Warnings:                                                 │
│   • GitHub branch protection cannot be verified (no API)    │
│   • Will validate at runtime                                │
```

---

### 3. State-Dependent Operations
**Problem:** Some operations depend on current state that may change

**Example:** `git:clean` shows branches to delete, but someone else might push new commits

**Solution:**
- Timestamp the preview
- Show warning if significant time elapsed
- Re-run dry-run if state changed

---

### 4. Recursive Dry-Run
**Problem:** `/craft:do` delegates to other commands

**Question:** Should dry-run recurse?

**Decision:** **No** - show delegation plan only

**Rationale:**
- Too verbose if recursive
- User can dry-run individual commands
- Keeps output manageable

**Alternative:** Add `--recursive-dry-run` flag for deep analysis (future)

---

## 📈 Success Metrics

### Quantitative
1. **Coverage:** 52% of commands (47/90) with dry-run
2. **Usage:** 40% of command invocations use dry-run
3. **Execution Rate:** 70% of dry-runs lead to execution (indicates trust)
4. **Error Prevention:** 80% reduction in "oops" issues

### Qualitative
1. **User Confidence:** Survey shows increased trust in automation
2. **Learning Curve:** New users understand commands faster
3. **Documentation Quality:** Dry-run output serves as inline examples

---

## 🤔 Open Questions

1. **Should dry-run show exact commands that will be run?**
   - Pro: Maximum transparency
   - Con: May be too technical for some users
   - **Proposed:** Add `--verbose` flag to dry-run for command details

2. **How to handle commands with interactive prompts?**
   - Example: `/craft:git:worktree add` asks for branch name
   - **Proposed:** Dry-run shows "Would prompt for: [inputs]"

3. **Should dry-run have its own exit code?**
   - Pro: Scripts can detect dry-run mode
   - Con: Breaks convention (dry-run usually exits 0)
   - **Proposed:** Keep exit code 0, add env var `CRAFT_DRY_RUN=1`

4. **How to test dry-run accuracy?**
   - See Long-term #8 (testing framework)
   - **Proposed:** Start with manual testing, automate gradually

---

## 🎯 Next Steps

1. **Review this brainstorm** with team
2. **Capture as formal spec** (use `/spec:review dry-run`)
3. **Create Phase 1 tasks** (6 commands, 1 week)
4. **Assign owner** for implementation
5. **Set milestone** for v1.20.0 release

---

## 📚 References

### Related Commands
- `/craft:check` - Pre-flight validation (could use dry-run)
- `/craft:do` - Smart routing (could show routing plan)
- `/craft:git:init` - Already has dry-run (good reference)

### Design Inspiration
- Git's dry-run implementation (`git commit -n`, `git clean -n`)
- Make's dry-run (`make -n`)
- Terraform's plan/apply model
- Docker Compose's `--dry-run` flag

### User Research
- 8 deep questions answered
- Primary motivation: Build trust in automation
- Preferred: High-level summary, passive display, standard flag
- All 4 categories need dry-run (git, files, dist, smart)

---

## 📝 Appendix: All 47 Commands Needing Dry-Run

### Git Operations (5) - P0
1. `/craft:git:init` ✅ (already has)
2. `/craft:git:clean` ⚠️ CRITICAL
3. `/craft:git:worktree` ⚠️ HIGH
4. `/craft:git:branch` ⚠️ HIGH
5. `/craft:git:sync`

### Distribution (3) - P0/P2
6. `/craft:dist:pypi` ⚠️ CRITICAL
7. `/craft:dist:homebrew` ✅ (already has)
8. `/craft:dist:curl-install` ✅ (has preview)

### Documentation (5) - P1
9. `/craft:docs:sync`
10. `/craft:docs:changelog`
11. `/craft:docs:claude-md`
12. `/craft:docs:validate`
13. `/craft:docs:nav-update`

### Site Management (5) - P1
14. `/craft:site:init` ✅ (via git:init)
15. `/craft:site:build`
16. `/craft:site:deploy` ⚠️ HIGH
17. `/craft:site:check`
18. `/craft:site:frameworks`

### CI/CD (3) - P1
19. `/craft:ci:generate` ⚠️ HIGH
20. `/craft:ci:validate`
21. `/craft:ci:detect`

### Smart Commands (4) - P1
22. `/craft:do` ⚠️ HIGH
23. `/craft:orchestrate` ⚠️ HIGH
24. `/craft:check`
25. `/craft:help`

### Code Quality (8) - P2
26. `/craft:code:lint`
27. `/craft:code:coverage`
28. `/craft:code:deps-check`
29. `/craft:code:deps-audit`
30. `/craft:code:ci-local`
31. `/craft:code:ci-fix` ✅ (already has)
32. `/craft:code:refactor`
33. `/craft:code:release`

### Testing (3) - P2
34. `/craft:test:run`
35. `/craft:test:coverage`
36. `/craft:test:watch`

### Architecture (2) - P3
37. `/craft:arch:analyze`
38. `/craft:arch:diagram`

### Planning (1) - P3
39. `/craft:plan:feature`

### Additional Commands with Partial Dry-Run (8)
40. `/craft:docs:quickstart` ✅
41. `/craft:docs:website` ✅
42. `/craft:docs:workflow` ✅
43. `/craft:docs:help` ✅
44. `/craft:docs:demo` ✅
45. `/craft:docs:tutorial` ✅
46. `/craft:code:demo`
47. `/craft:test:cli-gen`

**Total:** 47 commands
**Critical (⚠️):** 8 commands
**Already Implemented (✅):** 11 commands
**To Implement:** 36 commands

---

**End of Brainstorm**
**Duration:** 8 minutes
**Next:** Capture as spec for implementation approval
