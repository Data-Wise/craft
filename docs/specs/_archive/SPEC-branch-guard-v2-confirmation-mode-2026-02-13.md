# SPEC: Branch Guard v2 — Smart Protection with Teaching Suggestions

**Date:** 2026-02-13
**Status:** Draft
**Version:** v2.17.0 target
**Proposal:** `PROPOSAL-branch-guard-improvements.md`
**Brainstorm:** `BRAINSTORM-smart-branch-guard-2026-02-13.md`

## Problem Statement

The current branch guard on dev uses hard-blocking (exit 2) for risky commands like force push and new code file creation. This creates a "wall" experience where the user must:

1. See the block error
2. Run `/craft:git:unprotect` (blanket bypass for everything)
3. Retry the command
4. Remember to run `/craft:git:protect` afterward

This is friction-heavy and the blanket bypass disables ALL protection, not just the specific command. During the 2026-02-13 session, the bypass was left active after maintenance and had to be manually cleaned up.

**User request:** Replace hard-blocking with a **teaching-first protection system** that explains risks, suggests safe alternatives, and gets briefer as the user learns. The guard becomes a coach, not a wall.

## Goals

1. **3-tier risk classification** — LOW (silent note), MEDIUM (teaching box + confirm), HIGH (hard block)
2. **Teaching suggestions** — 4 types: worktree redirect, command rewrite, workflow guidance, risk explanation
3. **Fade-to-brief learning** — full teaching on first encounter, brief after 3x, minimal after 4x (session-scoped, no persistence)
4. **Critical file protection** — .env, secrets, .pem, .key files trigger medium-risk confirm
5. **Bash write-through detection** — catch file creation via shell redirection
6. **One-shot approval** — auto-consumed marker for individual command approval
7. Maintain backward compatibility: `block-all` on main unchanged

## Non-Goals

- Changing main branch behavior (stays `block-all`)
- Interactive prompts inside the hook (hooks can't pause for input)
- Removing `/craft:git:unprotect` (still available as blanket bypass)
- Persistent memory across sessions (fresh every session by design)
- Performance optimization (25ms per call is adequate)

## Design

### Protection Levels

```text
Protection Levels:
  block-all       → HIGH risk tier only, no bypass except /craft:git:unprotect (main)
  smart           → 3-tier system: LOW notes + MEDIUM confirm + HIGH block (dev)
  block-new-code  → DEPRECATED: alias for smart (backward compat)
  confirm         → ALIAS: same as smart
  (empty)         → No protection (feature/*)
```

### 3-Tier Risk Classification

#### Tier 1: LOW Risk — Silent Allow + Brief Note

Actions that are safe but worth noting. Allowed automatically with a one-line note on first encounter per session.

| Action | Note |
|--------|------|
| Edit existing file on dev | `[guard] Editing existing file on dev (allowed)` |
| Write new .md on dev | `[guard] New markdown on dev (always allowed)` |
| Write to tests/ on dev | `[guard] Test files on dev (always allowed)` |
| Write extension-less file | `[guard] Extension-less file (allowed): .STATUS` |
| `git commit` on dev | `[guard] Commit on dev (allowed)` |
| `git push` (normal) on dev | `[guard] Push to dev (allowed)` |
| `git reset --soft` | `[guard] Soft reset (safe — keeps changes staged)` |

**Format:** Single line, `[guard]` prefix, dim color. Shows on first encounter per action type per session, then silent.

#### Tier 2: MEDIUM Risk — Teaching Box + AskUserQuestion

Actions that could cause problems but are sometimes intentional. Block with teaching explanation + ask for approval.

| Action | Risk Category | Teaching Message |
|--------|--------------|-----------------|
| Write new .py/.sh/.js on dev | Unplanned code | "New code files on dev should go in a feature branch" |
| `git push --force` on dev | History rewrite | "Force push overwrites remote history for all collaborators" |
| `git reset --hard` on dev | Work loss | "Hard reset discards ALL uncommitted changes — no undo" |
| `git checkout -- .` on dev | Work loss | "Restores all files to last commit — discards all edits" |
| `git restore .` on dev | Work loss | "Same as checkout -- . — discards uncommitted changes" |
| `git clean -f` on dev | File loss | "Removes ALL untracked files permanently — no recovery" |
| `git branch -D` anywhere | Branch loss | "Force-deletes branch even if not merged — commits may be lost" |
| Overwrite/delete .env, secrets | Security | "Environment file contains sensitive credentials" |
| Delete config files (.pem, .key) | Security | "Removing credentials file may break authentication" |

#### Tier 3: HIGH Risk — Hard Block

Actions never allowed without proper workflow. No confirmation path.

| Action | Branch | Reason |
|--------|--------|--------|
| Any Edit/Write on main | main | All changes via PR |
| `git commit`/`push` on main | main | All changes via PR |
| `rm -rf .git` anywhere | all | Catastrophic — destroys entire repo |
| Delete `.claude/` directory | all | Destroys guard config and bypass state |

### Confirmation Flow (Medium Risk)

```text
Hook invocation (Edit/Write/Bash)
    │
    ├── Check bypass marker (.claude/allow-dev-edit) → ALLOW
    ├── Check one-shot marker (.claude/allow-once) → ALLOW + consume
    │
    ├── Classify action → LOW / MEDIUM / HIGH
    │
    ├── LOW:
    │   ├── Get session counter → first time for this action type?
    │   │   ├── Yes → stderr "[guard] <note>" (dim)
    │   │   └── No → silent
    │   └── Exit 0 (allow)
    │
    ├── MEDIUM:
    │   ├── Get session counter → determine verbosity
    │   │   ├── 1st time → full teaching box + AskUserQuestion (4 options)
    │   │   ├── 2nd-3rd → brief box + AskUserQuestion (3 options)
    │   │   └── 4th+ → one-liner + AskUserQuestion (2 options)
    │   ├── Output [CONFIRM] prefix in stderr
    │   └── Exit 2 (block, awaiting user decision via Claude)
    │
    └── HIGH:
        ├── Full block box with workflow steps
        ├── No [CONFIRM] prefix (not confirmable)
        └── Exit 2 (hard block)
```

### Teaching Box Format (Medium Risk — Full Verbosity)

```text
╔═══════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — Medium Risk                                    ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Action:  git push --force origin dev                          ║
║                                                               ║
║ Why risky:                                                    ║
║   Force push overwrites remote history. If others have        ║
║   pulled from dev, their local copies will diverge.           ║
║                                                               ║
║ Safe alternatives:                                            ║
║   → git push origin dev          (regular push)               ║
║   → git push --force-with-lease  (safer — checks remote)     ║
║   → Create PR instead of pushing directly                     ║
║   → /craft:git:worktree feature/<name>  (isolate changes)    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 4 Suggestion Types

Every medium-risk teaching box includes relevant suggestions from these categories:

| Type | When Used | Example |
|------|-----------|---------|
| **Worktree redirect** | New code on dev | "Create worktree: `/craft:git:worktree feature/<name>`" |
| **Command rewrite** | Risky git command | "`git push origin dev` (without --force)" |
| **Workflow guidance** | Wrong workflow | "`/craft:git:unprotect` for bulk maintenance" |
| **Risk explanation** | Always (first 3 times) | "Force push overwrites remote history for all collaborators" |

### Message Protocol

The `[CONFIRM]` prefix in stderr signals to Claude that this action is confirmable. High-risk blocks have no prefix.

**Full verbosity (1st encounter):**

```text
[CONFIRM] Force push on dev requires approval.
Action:    git push --force origin dev
Risk:      Overwrites remote commit history for all collaborators
Suggest:   git push origin dev (regular push)
Suggest:   git push --force-with-lease (safer)
Suggest:   /craft:git:worktree feature/<name> (isolate changes)
Branch:    dev (smart mode)
Verbosity: full (1st encounter)
```

**Brief verbosity (2nd-3rd encounter):**

```text
[CONFIRM] Force push on dev.
Action:  git push --force origin dev
Risk:    Overwrites remote history
Branch:  dev (smart mode)
```

**Minimal verbosity (4th+):**

```text
[CONFIRM] git push --force on dev. Allow?
```

### Claude's Confirmation Behavior

When Claude sees a `[CONFIRM]` block message, it reads the verbosity level and adapts:

**Full verbosity — 4 options:**

```json
{
  "questions": [{
    "question": "<Risk explanation>. Allow <Action>?",
    "header": "Guard",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes, allow this once",
        "description": "One-shot approval. Guard re-engages on next risky action."
      },
      {
        "label": "Use safe alternative",
        "description": "<First suggestion from Suggest fields>"
      },
      {
        "label": "Cancel",
        "description": "Don't execute. I'll rethink the approach."
      },
      {
        "label": "Bypass all (/craft:git:unprotect)",
        "description": "Disable guard for this session. For heavy maintenance."
      }
    ]
  }]
}
```

**Brief verbosity — 3 options:**

```json
{
  "questions": [{
    "question": "<Action> on <Branch>. Allow?",
    "header": "Guard",
    "multiSelect": false,
    "options": [
      { "label": "Yes, allow once", "description": "One-shot approval." },
      { "label": "Cancel", "description": "Don't execute." },
      { "label": "Bypass all", "description": "/craft:git:unprotect for session." }
    ]
  }]
}
```

**Minimal verbosity — 2 options:**

```json
{
  "questions": [{
    "question": "<Action>. Allow?",
    "header": "Guard",
    "multiSelect": false,
    "options": [
      { "label": "Yes", "description": "Allow this one command." },
      { "label": "No", "description": "Cancel." }
    ]
  }]
}
```

After user decision:

- **Yes/Allow** → create `.claude/allow-once` marker, retry the command
- **Use safe alternative** → Claude executes the suggested command instead
- **Cancel** → Claude explains alternatives in natural language
- **Bypass all** → Claude runs `/craft:git:unprotect`

### One-Shot Marker

**File:** `.claude/allow-once`

```json
{
  "action": "git push --force",
  "approved_at": "2026-02-13T15:00:00Z",
  "session_id": "abc-123-def"
}
```

**Hook logic (checked before `smart` tier rules):**

```bash
ONCE_MARKER="${PROJECT_ROOT}/.claude/allow-once"
if [[ -f "$ONCE_MARKER" ]]; then
  rm -f "$ONCE_MARKER"   # Consume immediately (one-shot)
  exit 0                  # Allow this single command
fi
```

**Properties:**

- Created by Claude after user approval
- Deleted by hook on first use (auto-consumed)
- Contains action description for audit trail
- Session-scoped via session_id (optional validation)
- If session ends without consumption, stale marker is harmless (consumed by next risky command in any session)

### Confirmed Actions Matrix

| Action | On Dev | On Main | On Feature |
|--------|--------|---------|------------|
| Write new code file (.py/.sh/.js etc.) | Confirm | Block | Allow |
| `git push --force` / `--force-with-lease` | Confirm | Block | Allow |
| `git reset --hard` | Confirm | Block | Allow |
| `git checkout -- .` / `git checkout -- <file>` | Confirm | Block | Allow |
| `git restore .` / `git restore <file>` | Confirm | Block | Allow |
| `git clean -f` / `-fd` / `-fx` | Confirm | Block | Allow |
| `git branch -D <branch>` | Confirm | Block | Allow |
| `rm -rf .git` | Confirm | Block | Confirm |
| Edit existing file | Allow | Block | Allow |
| Write new .md file | Allow | Block | Allow |
| Write to tests/ | Allow | Block | Allow |
| `git commit` | Allow | Block | Allow |
| `git push` (normal) | Allow | Block | Allow |

**Note:** `rm -rf .git` is confirmed even on feature branches (catastrophic risk).

### Bash Write-Through Detection

The Bash handler gains file creation pattern detection for `smart` mode:

**Patterns to detect:**

```bash
# Redirect operators creating new code files
cat > path/file.py          # cat with redirect
echo "..." > path/file.py   # echo with redirect
printf "..." > path/file.py # printf with redirect
tee path/file.py            # tee (writes to file)
cp source.py path/new.py    # copy creating new file
mv source.py path/new.py    # move creating new file
```

**Detection regex:**

```bash
# Extract target file from redirect patterns
if echo "$COMMAND" | grep -qoE '(>|tee\s+|cp\s+\S+\s+|mv\s+\S+\s+)(\S+\.(py|sh|js|ts|jsx|tsx|json|yml|yaml|toml|cfg|ini|r|R|zsh))'; then
  TARGET_FILE="..." # extracted from match
  if [[ ! -f "$TARGET_FILE" ]]; then
    # New file via Bash — trigger confirm flow
    confirm "New code file via Bash on dev"
  fi
fi
```

**Limitations (acceptable):**

- Multi-line heredocs: `cat << 'EOF' > file.py` may not be reliably parsed
- Variable expansion: `cat > "$FILE"` won't resolve the variable
- Complex pipes: `curl ... | python3 > output.py` is too ambiguous
- Intentional bypass: someone determined to bypass can always find a way

**Design choice:** Catch the common patterns (80/20 rule), don't try to be exhaustive.

### Coaching Mode (Tool Input Modification — Future Phase)

Since Claude Code v2.0.10, PreToolUse hooks can modify tool inputs by writing JSON to stdout (exit 0). This enables a "coaching" paradigm where the hook corrects actions instead of blocking them.

**Phase 3 scope (spec only, no implementation):**

| Scenario | Current | Coaching Mode |
|----------|---------|---------------|
| Force push on dev | Block | Strip `--force`, continue with regular push |
| New .py on dev | Block | Show warning, suggest worktree path in message |
| `git reset --hard` | Allow (!) | Strip `--hard`, continue with `git reset` (soft) |

**Implementation approach (future):**

```bash
# Instead of:
block "Cannot force push"

# Do:
MODIFIED_COMMAND="$(echo "$COMMAND" | sed 's/--force//; s/--force-with-lease//; s/-f //')"
echo "{\"tool_input\": {\"command\": \"$MODIFIED_COMMAND\"}}"
echo "[COACHING] Stripped --force flag from push command." >&2
exit 0
```

**Open questions for coaching mode:**

1. Should Claude inform the user when a command is silently modified?
2. Should coaching be opt-in (config flag) or default?
3. Which actions should be coached vs. confirmed vs. blocked?
4. Should coaching mode have its own protection level (`coach`)?

These questions will be resolved in a separate coaching mode spec.

## Command Relationships & Integration Approach

### Integration Decision: Hook Handles It

Commands stay simple — the guard hook intercepts at the PreToolUse level independently. Commands don't need to duplicate guard logic. This means:

- `git:branch` (delete with `-D`) → hook catches it, triggers confirm
- `git:sync` (force-push for diverged branches) → hook catches `--force`, triggers confirm
- `git:clean` → uses safe `-d` delete, no guard interaction needed
- `git:git-recap` → read-only, no guard interaction needed
- `git:worktree` → already has main-block awareness, minimal updates

### Command Updates Required

| Command | Change | Priority |
|---------|--------|----------|
| `commands/git/status.md` | Show `smart` level + session counter (e.g., "Guard: smart (3 confirms)") + pending one-shot marker | High |
| `commands/git/protect.md` | Add `--level <level>` flag, `--show` flag, `--reset` flag; change auto-detect `block-new-code` → `smart`; add one-shot marker cleanup on re-protect | High |
| `commands/git/unprotect.md` | Document relationship to one-shot markers (unprotect takes priority over one-shot) | Medium |
| `commands/git/init.md` | Set `smart` as default for dev on new projects; update setup messaging | Medium |
| `commands/git/worktree.md` | Cross-reference guard's worktree redirect suggestion | Low |

### Documentation Updates

| File | Change | Priority |
|------|--------|----------|
| `commands/git/docs/safety-rails.md` | Add cross-reference section: guard's fade-to-brief implements the progressive trust model described in Week 1-4 graduated autonomy | Medium |
| `commands/git/docs/undo-guide.md` | Add note that destructive commands trigger guard confirm on protected branches | Low |

### Explicit Guard Configuration (/craft:git:protect --level)

For existing projects that want to explicitly change protection levels:

```bash
# View current config per branch
/craft:git:protect --show

# Change current branch's protection level
/craft:git:protect --level smart
/craft:git:protect --level block-all

# Set specific branch
/craft:git:protect --branch dev --level smart

# Reset to auto-detect defaults (removes branch-guard.json entry)
/craft:git:protect --reset
```

This writes/updates `.claude/branch-guard.json`. Most users never need this — auto-detect handles the common case.

### Migration Path for Existing Projects

| Scenario | Mechanism | User Action Required |
|----------|-----------|---------------------|
| No `.claude/branch-guard.json` (most projects) | Auto-detect changes `block-new-code` → `smart` | None |
| Has config with `"dev": "block-new-code"` | Alias treats it as `smart` | None |
| Wants to change level explicitly | `/craft:git:protect --level <level>` | Run command |
| Wants old hard-block behavior on dev | `/craft:git:protect --level block-all` | Run command |

## File Changes

### Modified Files

| File | Change |
|------|--------|
| `scripts/branch-guard.sh` | Add `smart` protection level, 3-tier classifier, session counter, one-shot marker check, expanded Bash detection, teaching box output |
| `scripts/install-branch-guard.sh` | Update docs to mention `smart` level |
| `commands/git/status.md` | Show `smart` level + session counter + pending one-shot marker |
| `commands/git/protect.md` | Add `--level`, `--show`, `--reset` flags; change auto-detect to `smart`; one-shot marker cleanup |
| `commands/git/unprotect.md` | Document relationship to one-shot markers |
| `commands/git/init.md` | Set `smart` as default for dev; update setup messaging |
| `commands/git/docs/safety-rails.md` | Add cross-reference to guard's progressive trust model |

### New Files

| File | Purpose |
|------|---------|
| (none — all changes are to existing files) | |

### Test Changes

| File | Change |
|------|--------|
| `tests/test_branch_guard.sh` | Update dev tests: block → smart/confirm message format, add one-shot marker tests, add destructive command tests, add session counter tests |
| `tests/test_branch_guard_e2e.sh` | Add confirm flow e2e tests (block → approve → retry → allowed), teaching box format tests |
| `tests/test_integration_branch_guard.py` | Add confirm flow integration tests, protect --level tests |
| `tests/test_branch_guard_dogfood.py` | Update expectations for smart vs. block-new-code |

### Estimated Test Count Changes

| Test File | Current | Added | New Total |
|-----------|---------|-------|-----------|
| Unit tests | 49 | ~20 (smart + destructive + counter + teaching box) | ~69 |
| E2E tests | 31 | ~12 (confirm flow + protect --level) | ~43 |
| Integration | 6 | ~6 (confirm flow + config migration) | ~12 |
| Dogfooding | 52 | ~5 (smart expectations) | ~57 |
| **Total** | **138** | **~43** | **~181** |

## Backward Compatibility

| Aspect | Behavior |
|--------|----------|
| `block-all` on main | Unchanged — hard block, no [CONFIRM] |
| `block-new-code` in config | Treated as alias for `smart` |
| `confirm` in config | Treated as alias for `smart` |
| Auto-detect (no config) | Dev gets `smart` instead of `block-new-code` |
| `/craft:git:unprotect` | Still works as blanket bypass |
| `.claude/allow-dev-edit` | Still checked first (highest priority) |
| `block-new-code` in test output | Updated to `smart` in messages |
| Feature branches | Unchanged — unrestricted |
| `/craft:git:protect --level` | New flag for explicit config (see Command Relationships section) |

## Migration

### For Users (No Config)

No action required. Auto-detect changes from `block-new-code` to `smart`, which is strictly more capable (teaches + confirms instead of hard block). Applies automatically on next session.

### For Users (With Config)

`block-new-code` in `.claude/branch-guard.json` is treated as alias for `smart`. No action required.

### For Users Wanting Explicit Control

Use `/craft:git:protect --level <level>` to explicitly set/change protection per branch. Use `--show` to view current config. Use `--reset` to return to auto-detect defaults.

## Rollout

### Phase 1: Smart Protection Mode (this spec)

- Add `smart` protection level with 3-tier risk classification
- Session counter + fade-to-brief learning system
- Teaching box format with 4 suggestion types
- One-shot marker mechanism
- Expanded destructive command detection
- Updated test suite (~43 new tests)
- Backward-compatible `block-new-code` → `smart` alias
- `/craft:git:protect --level/--show/--reset` for explicit configuration
- Command updates: status (counter display), protect (--level), init (smart default)
- Documentation cross-references: safety-rails.md → progressive trust

### Phase 2: Bash Write-Through (same feature branch)

- File creation pattern detection in Bash handler
- Integration with confirm flow
- Pattern-specific tests

### Phase 3: Coaching Mode (separate spec, future version)

- Tool input modification design
- Opt-in configuration
- Separate spec document

## Acceptance Criteria

1. On dev, risky commands produce `[CONFIRM]` messages with teaching boxes instead of hard blocks
2. Session counter tracks encounters per action type; verbosity fades: full (1st) → brief (2nd-3rd) → minimal (4th+)
3. One-shot marker is created by Claude after user approval and consumed by hook on next call
4. `block-all` on main is completely unchanged
5. All 6 destructive commands (`checkout --`, `restore`, `clean -f`, `reset --hard`, `branch -D`, `rm -rf .git`) trigger confirmation on dev
6. Bash write-through patterns (>, tee, cp) detected and routed through confirm flow
7. `block-new-code` treated as alias for `smart` (backward compat)
8. Feature branches remain unrestricted
9. All existing tests pass (with updated expectations)
10. ~43 new tests covering confirm flow, teaching boxes, session counter, one-shot markers, destructive commands, protect --level
11. `/craft:git:unprotect` still works as blanket bypass
12. `/craft:git:status` shows guard level + session counter (e.g., "Guard: smart (3 confirms)")
13. `/craft:git:protect --level` allows explicit guard configuration per branch
14. `/craft:git:init` uses `smart` as default for dev on new projects
15. `safety-rails.md` cross-references guard's fade-to-brief as implementation of progressive trust
