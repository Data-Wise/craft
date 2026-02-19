# Claude Code Instruction Enforcement Reference

> Research compiled 2026-02-06 after workflow violations in teaching ecosystem session.
> Goal: Understand all mechanisms for making Claude Code follow instructions deterministically.

## Instruction Hierarchy (6 Levels)

| Priority | Source | Behavior | Location |
|----------|--------|----------|----------|
| 1 | System prompt | Immutable, always loaded | Internal to Claude Code |
| 2 | `CLAUDE.md` (project) | Advisory, per-project | `<project>/CLAUDE.md` |
| 3 | `CLAUDE.md` (parent dirs) | Inherited up directory tree | Any parent dir |
| 4 | `~/.claude/CLAUDE.md` | Global user preferences | Home directory |
| 5 | `.claude/rules/*.md` | Scoped rules with path frontmatter | `.claude/rules/` |
| 6 | Hooks (shell scripts) | **Deterministic** — can block actions | `~/.claude/hooks/`, `.claude/hooks/` |

**Key insight:** Levels 1-5 are *advisory* — Claude reads and respects them but can override under momentum/reasoning. Level 6 (hooks) is *deterministic* — exit code 2 physically blocks the action.

## Hook System

### 12 Hook Event Types

| Event | When | Can Block? |
|-------|------|------------|
| `SessionStart` | Session begins | No |
| `UserPromptSubmit` | Before processing user input | Yes (modify) |
| `PreToolUse` | Before any tool executes | **Yes (exit 2)** |
| `PermissionRequest` | When permission needed | Yes |
| `PostToolUse` | After tool executes | No |
| `PostToolUseFailure` | After tool fails | No |
| `Notification` | System notifications | No |
| `SubagentStart` | Subagent launches | No |
| `SubagentStop` | Subagent finishes | No |
| `Stop` | Session ends | No |
| `PreCompact` | Before context compression | No |
| `SessionEnd` | Session cleanup | No |

### PreToolUse — The Key Enforcement Mechanism

**Exit codes:**

- `0` = Allow the tool to proceed
- `2` = **BLOCK** the tool. Stderr message is sent to Claude as feedback.

**JSON control (stdout):**

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "Cannot edit code on dev branch. Create a worktree first."
  }
}
```

**Environment variables available:**

- `CLAUDE_TOOL_NAME` — e.g., `Edit`, `Write`, `Bash`
- `CLAUDE_TOOL_INPUT` — JSON of tool parameters
- `CLAUDE_SESSION_ID`
- `CLAUDE_CWD`

### Guard-Branch Pattern

The specific hook pattern for preventing code edits on protected branches:

```bash
#!/bin/bash
# .claude/hooks/guard-branch.sh
# PreToolUse hook: Block Edit/Write on dev branch

TOOL="$CLAUDE_TOOL_NAME"
BRANCH=$(git branch --show-current 2>/dev/null)

# Only guard Edit and Write tools
if [[ "$TOOL" != "Edit" && "$TOOL" != "Write" ]]; then
  exit 0  # Allow
fi

# Allow on feature branches
if [[ "$BRANCH" == feature/* ]]; then
  exit 0
fi

# Allow spec/doc files on dev
FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null)
if [[ "$FILE" == */docs/* || "$FILE" == */specs/* || "$FILE" == *.md ]]; then
  exit 0
fi

# Block code changes on dev/main
if [[ "$BRANCH" == "dev" || "$BRANCH" == "main" ]]; then
  echo "BLOCKED: Cannot edit code files on '$BRANCH'. Create a worktree: git worktree add ~/.git-worktrees/craft/feature-<name> -b feature/<name> dev" >&2
  exit 2
fi

exit 0
```

**Hook configuration (settings.json or .claude/settings.json):**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": ".claude/hooks/guard-branch.sh"
      }
    ]
  }
}
```

## Rules Directory

**Location:** `.claude/rules/*.md` (project) or `~/.claude/rules/*.md` (global)

**Path-specific frontmatter:**

```yaml
---
paths:
  - "commands/utils/*.py"
  - "tests/*.py"
---
# Rule content here
Only applies when Claude is working with files matching the paths above.
```

**Already configured:**

- `~/.claude/rules/brainstorm-mode.md` — ADHD-friendly brainstorming
- `~/.claude/rules/feature-branch-workflow.md` — No PR suggestions on feature branches

## Memory Systems

| System | Persistence | Scope | Auto-loaded? |
|--------|------------|-------|-------------|
| `MEMORY.md` | Cross-session | Per project | Yes (in system prompt, max 200 lines) |
| Topic files in memory dir | Cross-session | Per project | No (must be read explicitly) |
| `#` shortcut | Cross-session | Per project | Added to MEMORY.md |
| `@import` in CLAUDE.md | Cross-session | Per project | Yes (max 5 hops) |
| Session memory | Current session only | Session | Yes |

**`#` key shortcut:** Press `#` in Claude Code CLI to quickly add a memory note. Appended to MEMORY.md.

**`@import` syntax:** CLAUDE.md files can import other files:

```markdown
@import docs/ARCHITECTURE.md
```

Max 5 import hops to prevent loops.

## Settings Permissions

**Location:** `~/.claude/settings.json` (global) or `.claude/settings.json` (project)

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "deny": [],
    "ask": ["Edit", "Write", "Bash"]
  }
}
```

This controls the permission prompt behavior but is less granular than hooks (can't inspect parameters).

## Enforcement Strategy for This Project

### Problem: Advisory rules get overridden by momentum

The MEMORY.md rules and CLAUDE.md workflow section are advisory. When Claude enters "fix it" mode after exploring code, it overrides soft guidelines. This happened 4 times on 2026-02-06.

### Solution: Layered defense

1. **Layer 1 (Advisory):** MEMORY.md rules + CLAUDE.md workflow section — sets expectations
2. **Layer 2 (Deterministic):** PreToolUse hook — physically blocks code edits on dev/main
3. **Layer 3 (Procedural):** Path-specific rule requiring worktree confirmation before any `.py`/`.sh` edits

### Recommended Implementation

1. Create `.claude/hooks/guard-branch.sh` (PreToolUse hook)
2. Add hook config to `.claude/settings.json`
3. Create `.claude/rules/code-edit-workflow.md` with paths frontmatter
4. Test: Try editing a .py file on dev — should be blocked with helpful message

## References

- Claude Code docs: Hooks system
- Claude Code docs: Rules directory
- Claude Code docs: CLAUDE.md hierarchy
- GitHub: Claude Code settings schema
