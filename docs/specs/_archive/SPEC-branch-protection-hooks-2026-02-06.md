# SPEC: Branch Protection Hooks

**Date:** 2026-02-06
**Status:** Draft
**Scope:** Global hook + craft command enhancements
**Trigger:** Workflow violations on 2026-02-06 (4x ignored "stop" instructions, code edits on dev)

---

## Problem Statement

Claude Code's instruction-following is advisory — CLAUDE.md rules and MEMORY.md notes can be overridden when Claude enters "fix it" mode. On 2026-02-06, Claude edited `teach_config.py` and `test_integration_teaching_workflow.py` directly on the `dev` branch despite being told 4 times to "create a spec file only, stop." The existing constraints in CLAUDE.md ("Never write feature code on dev") are documentation, not enforcement.

**Root cause:** No deterministic mechanism prevents code edits on protected branches. Advisory rules fail under reasoning pressure.

---

## Design Decisions (from brainstorm session)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Protection model | Option D: Block new code files, allow fixups | Pragmatic — allows merge conflict fixes on dev |
| Enforcement layer | Both: standalone hook + craft command UX | Hook is deterministic; commands are informational |
| File extension strategy | Smart allowlist | .md, extension-less, tests/ allowed on dev |
| Bypass mechanism | `/craft:git:unprotect` command | Session-scoped, reason-logged, auto-expires |
| Global scope | Auto-detect repos with dev branch | Safe globally — skips repos without dev |
| Per-project config | `.claude/branch-guard.json` | Custom protected branches (teaching projects) |
| Worktree creation | Only from dev, never from main | Strict — no "branch from main anyway" option |
| Ask-before-edit | Advisory only (MEMORY.md) | Hook doesn't add confirmation on feature branches |
| Bash git protection | Block git commit/push on main | Prevents accidental direct commits |
| Rollout | Dry-run first | Logging mode before enforcement |
| Scholar/flow-cli | Hook only, no command changes | Their commands are content generators or run in project context |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  ~/.claude/settings.json (global hook registration) │
│  ┌──────────────────────────────────────────────┐   │
│  │  PreToolUse: Edit|Write|Bash                 │   │
│  │  → ~/.claude/hooks/branch-guard.sh           │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│  branch-guard.sh                                     │
│                                                      │
│  1. Read tool input (stdin JSON)                     │
│  2. Extract file_path and tool_name                  │
│  3. Detect current git branch                        │
│  4. Load .claude/branch-guard.json (if exists)       │
│  5. Auto-detect if no config (check for dev branch)  │
│  6. Check bypass marker (.claude/allow-dev-edit)     │
│  7. Apply protection rules                           │
│  8. Exit 0 (allow) or exit 2 (block + stderr msg)   │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│  Craft commands (informational layer)                │
│                                                      │
│  /craft:check       → Branch Context section         │
│  /craft:do          → Branch-aware routing           │
│  /craft:git:worktree → Only create from dev          │
│  /craft:git:status   → Protection indicator          │
│  /craft:git:unprotect → Bypass with reason           │
│  /craft:git:protect   → Re-enable protection         │
└─────────────────────────────────────────────────────┘
```

---

## Deliverable 1: Standalone Hook Script

**File:** `~/.claude/hooks/branch-guard.sh`

### Input (stdin JSON from Claude Code)

```json
{
  "session_id": "abc123",
  "cwd": "/Users/dt/projects/dev-tools/craft",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/Users/dt/projects/dev-tools/craft/commands/utils/teach_config.py",
    "old_string": "...",
    "new_string": "..."
  }
}
```

### Protection Rules

#### On `main` (or any `block-all` branch)

| Tool | Action | Result |
|------|--------|--------|
| Edit (any file) | BLOCK | "Cannot edit files on main. All changes go through PRs." |
| Write (any file) | BLOCK | "Cannot create files on main." |
| Bash `git commit` | BLOCK | "Cannot commit on main. Use PR workflow." |
| Bash `git push origin main` | BLOCK | "Cannot push to main directly." |
| Read, Glob, Grep | ALLOW | Read-only operations always allowed |

#### On `dev` (or any `block-new-code` branch)

| Tool | File Type | Existing? | Result |
|------|-----------|-----------|--------|
| Edit | `.md` | Any | ALLOW |
| Edit | `.py`, `.sh`, `.js`, etc. | Existing | ALLOW (fixup) |
| Write | `.md` | Any | ALLOW |
| Write | `.py`, `.sh`, `.js`, etc. | New file | BLOCK |
| Write | `.py`, `.sh`, `.js`, etc. | Overwrite existing | ALLOW (fixup) |
| Write | Extension-less (`.STATUS`, `Makefile`) | Any | ALLOW |
| Write | In `tests/` directory | New `.py` | ALLOW (test files) |
| Bash | `git commit` | — | ALLOW (merge commits, doc commits) |
| Bash | `git push` | — | ALLOW |
| Bash | `git push --force` | — | BLOCK |

#### On `feature/*` (or any unlisted branch)

All operations ALLOWED. No restrictions.

### File Extension Classification

```bash
# Code files (blocked when creating NEW on dev)
CODE_EXTENSIONS="py|sh|js|ts|jsx|tsx|json|yml|yaml|toml|cfg|ini|r|R|zsh"

# Always allowed (even new files on dev)
# - .md files
# - Extension-less files (.STATUS, Makefile, Dockerfile, etc.)
# - Files in tests/ directory
```

### Bypass Detection

```bash
# Check for bypass marker
if [[ -f "$PROJECT_DIR/.claude/allow-dev-edit" ]]; then
  exit 0  # Bypass active
fi
```

### Auto-Detect Logic

```bash
# If no .claude/branch-guard.json exists:
# 1. Check if 'dev' branch exists
if git rev-parse --verify dev &>/dev/null; then
  # Apply: main=block-all, dev=block-new-code
else
  # Apply: main=block-all only (if main exists)
fi
```

### Error Messages

**New code file on dev:**

```
BRANCH PROTECTION: Cannot create new Python file on dev.

File: commands/utils/new_module.py
Branch: dev (protected: block-new-code)

Options:
1. Create worktree: git worktree add ~/.git-worktrees/craft/feature-<name> -b feature/<name> dev
2. Edit an EXISTING file instead (fixups are allowed on dev)
3. Bypass: /craft:git:unprotect (session-scoped, auto-expires)
```

**Any edit on main:**

```
BRANCH PROTECTION: Cannot edit files on main.

File: commands/utils/teach_config.py
Branch: main (protected: block-all)

All changes to main go through pull requests from dev.
Switch to dev: git checkout dev
```

**Git commit on main:**

```
BRANCH PROTECTION: Cannot commit on main.

Use the PR workflow:
1. git checkout dev
2. Create worktree for changes
3. PR from feature branch → dev
4. PR from dev → main
```

---

## Deliverable 2: Global Hook Config

**File:** `~/.claude/settings.json` (merge into existing)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/branch-guard.sh",
            "timeout": 5000,
            "statusMessage": "Checking branch protection..."
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/branch-guard.sh",
            "timeout": 5000,
            "statusMessage": "Checking branch protection..."
          }
        ]
      }
    ]
  }
}
```

**Note:** This merges with existing hooks (SessionStart, UserPromptSubmit, Stop, etc.) that are already configured globally.

---

## Deliverable 3: Per-Project Config Schema

**File:** `.claude/branch-guard.json` (optional, per-project)

### Schema

```json
{
  "branches": {
    "<branch-name>": "<protection-level>"
  },
  "fallback": "auto-detect" | "none"
}
```

### Protection Levels

| Level | Meaning |
|-------|---------|
| `block-all` | No edits, no writes, no commits. Read-only. |
| `block-new-code` | Block new code files. Allow fixups, .md, tests/. |

### Examples

**Craft project (standard):**

```json
{
  "branches": {
    "main": "block-all",
    "dev": "block-new-code"
  }
}
```

**Teaching project (stat-545):**

```json
{
  "branches": {
    "production": "block-all",
    "draft": "block-new-code"
  }
}
```

**R package (main-only workflow):**

```json
{
  "branches": {
    "main": "block-all"
  },
  "fallback": "none"
}
```

**No config file:** Falls back to auto-detect (check for dev branch).

---

## Deliverable 4: Craft Command Enhancements

### 4.1 `/craft:check` — Branch Context Section

**File:** `commands/check.md`

**Change:** Add "Branch Context" to Step 0 (Show Check Plan).

```
╔═══════════════════════════════════════════════════════════════╗
║  PRE-FLIGHT CHECK                                            ║
╠═══════════════════════════════════════════════════════════════╣
║  Project: craft                                              ║
║  Branch: dev (protected: new code blocked)                   ║
║  ...existing fields...                                       ║
╚═══════════════════════════════════════════════════════════════╝
```

### 4.2 `/craft:do` — Branch-Aware Smart Routing

**File:** `commands/do.md`

**Change:** When task involves code changes and branch is `dev`, show options before routing:

1. Create worktree (auto-generate branch name from task)
2. Write spec only
3. Analyze only (read code, no edits)

On feature branches, route directly without intervention.

### 4.3 `/craft:git:worktree create` — Only From Dev

**File:** `commands/git/worktree.md`

**Change:** In Step 0, check current branch. If on `main`:

```
Cannot create worktree from main.
Worktrees must branch from dev.

Switch to dev first:
  git checkout dev

Then retry:
  /craft:git:worktree feature/your-feature
```

No options to override. Hard block.

### 4.4 `/craft:git:status` — Protection Indicator

**File:** `commands/git/status.md`

**Change:** Add protection status line:

```
║  Guard: Active (new code blocked, fixups OK)                 ║
```

Or if bypassed:

```
║  Guard: BYPASSED (reason: merge conflict fix)                ║
```

### 4.5 `/craft:git:unprotect` — Bypass Command (NEW)

**File:** `commands/git/unprotect.md` (new)

**Behavior:**

1. Ask reason via AskUserQuestion (merge conflict / CI fix / maintenance)
2. Create `.claude/allow-dev-edit` marker file with JSON content:

   ```json
   {
     "reason": "merge conflict resolution",
     "timestamp": "2026-02-06T18:30:00Z",
     "session_id": "abc123"
   }
   ```

3. Confirm bypass is active
4. Register Stop hook cleanup (auto-remove marker at session end)

### 4.6 `/craft:git:protect` — Re-Enable Protection (NEW)

**File:** `commands/git/protect.md` (new)

**Behavior:**

1. Remove `.claude/allow-dev-edit` marker
2. Confirm protection is re-enabled

---

## Deliverable 5: Tests

### Hook Tests (`tests/test_branch_guard.sh`)

| Test | Input | Expected |
|------|-------|----------|
| Edit .py on main | tool=Edit, branch=main | Exit 2 (BLOCK) |
| Edit .py on dev (existing) | tool=Edit, branch=dev, file exists | Exit 0 (ALLOW) |
| Write new .py on dev | tool=Write, branch=dev, file doesn't exist | Exit 2 (BLOCK) |
| Write new .md on dev | tool=Write, branch=dev, .md file | Exit 0 (ALLOW) |
| Write new .py on feature/* | tool=Write, branch=feature/x | Exit 0 (ALLOW) |
| Edit .md on main | tool=Edit, branch=main | Exit 2 (BLOCK) |
| Write .py in tests/ on dev | tool=Write, branch=dev, tests/ dir | Exit 0 (ALLOW) |
| Write extension-less on dev | tool=Write, branch=dev, no ext | Exit 0 (ALLOW) |
| Bypass marker active | .claude/allow-dev-edit exists | Exit 0 (ALLOW) |
| No git repo | Not in git repo | Exit 0 (ALLOW) |
| No dev branch | Repo without dev | Only protect main |
| Custom branch-guard.json | production=block-all | Block on production |
| Bash git commit on main | tool=Bash, cmd=git commit, main | Exit 2 (BLOCK) |
| Bash git push on main | tool=Bash, cmd=git push, main | Exit 2 (BLOCK) |
| Bash git push --force on dev | tool=Bash, cmd=git push --force, dev | Exit 2 (BLOCK) |
| Bash git merge on dev | tool=Bash, cmd=git merge, dev | Exit 0 (ALLOW) |
| Bash non-git on main | tool=Bash, cmd=ls, main | Exit 0 (ALLOW) |
| Dry-run mode | .claude/branch-guard-dryrun exists | Exit 0 + log |

### Integration Tests (`tests/test_integration_branch_guard.py`)

| Test | Scenario |
|------|----------|
| Full workflow | On dev: try edit .py → blocked → create worktree → edit .py → allowed |
| Bypass flow | On dev: unprotect → edit .py → allowed → protect → edit .py → blocked |
| Config loading | Custom branch-guard.json → correct protection applied |
| Auto-detect | Repo with dev → protected. Repo without dev → only main protected. |

---

## Deliverable 6: Documentation

### CLAUDE.md Update

Add to "Git Workflow" section:

```markdown
### Branch Protection (Enforced by Hook)

| Branch | Code Files | .md Files | Git Operations |
|--------|-----------|-----------|----------------|
| `main` | BLOCKED | BLOCKED | Commit/push BLOCKED |
| `dev` | New: BLOCKED, Existing: allowed | ALLOWED | Commit/push allowed |
| `feature/*` | ALLOWED | ALLOWED | All allowed |

Override: `/craft:git:unprotect` (session-scoped, auto-expires)
```

### Teaching Workflow Guide Update

Add `.claude/branch-guard.json` example for teaching projects.

---

## Implementation Order

1. **Hook script** (`~/.claude/hooks/branch-guard.sh`) — core enforcement
2. **Hook config** (`~/.claude/settings.json`) — register the hook
3. **Dry-run test** — verify hook logs correctly without blocking
4. **Enable enforcement** — remove dry-run flag
5. **Per-project config** (`.claude/branch-guard.json`) — for teaching projects
6. **Craft commands** — UX enhancements (check, do, worktree, status)
7. **New commands** — unprotect/protect
8. **Tests** — hook tests + integration tests
9. **Documentation** — CLAUDE.md + teaching guide updates

Steps 1-4 are the critical path. Steps 5-9 can be done incrementally.

---

## Verification Checklist

- [ ] On craft/dev: try to create new .py file → BLOCKED with helpful message
- [ ] On craft/dev: edit existing .py file → ALLOWED (fixup)
- [ ] On craft/dev: create new .md file → ALLOWED
- [ ] On craft/main: any edit → BLOCKED
- [ ] On craft/main: git commit → BLOCKED
- [ ] On craft/feature/*: everything → ALLOWED
- [ ] On stat-545/production: any edit → BLOCKED (custom config)
- [ ] On stat-545/draft: new code file → BLOCKED (custom config)
- [ ] `/craft:check` shows branch context
- [ ] `/craft:git:worktree` on main → refuses, says switch to dev
- [ ] `/craft:git:unprotect` → bypass works, auto-expires at session end
- [ ] Dry-run mode logs but doesn't block
- [ ] Hook doesn't break non-git directories
- [ ] Hook doesn't slow down operations (< 100ms)
