# Branch Guard Improvements — Deep Analysis Proposal

**Generated:** 2026-02-13
**Context:** Craft Plugin v2.16.0, `scripts/branch-guard.sh` (375 lines, 138 tests)
**Sources:** Codebase analysis, session experience (2026-02-13), community best practices

## Executive Summary

The branch guard system is architecturally sound — deterministic PreToolUse enforcement with 3-tier JSON parsing (jq → python3 → grep/sed), 138 tests across 4 test suites, and clean separation of protection levels.

**Key user insight:** Instead of hard-blocking risky commands on dev, the guard should **ask for confirmation** — giving the user explicit control rather than a wall. This proposal redesigns the dev branch experience around a new `confirm` protection mode and adds 7 complementary improvements.

---

## Priority 1: Confirmation Mode for Dev Branch (NEW — User-Requested)

### What It Means

Currently, risky commands on dev are **hard-blocked** (exit 2) — force push, new code files, etc. The user must run `/craft:git:unprotect`, retry, then `/craft:git:protect`. This is friction-heavy for legitimate operations.

The new approach: instead of blocking, the hook **asks for explicit confirmation** through Claude's conversational flow. If the user says "yes", a one-shot bypass allows the single command to proceed.

### New Protection Level: `confirm`

```text
Protection Levels:
  block-all       → Hard block, no bypass except /craft:git:unprotect (main)
  confirm         → Block + ask user, one-shot bypass on approval (dev)  ← NEW
  block-new-code  → Block new code files only (current dev, becomes sub-mode of confirm)
  (empty)         → No protection (feature/*)
```

### How the Confirmation Flow Works

```text
Step 1: Hook detects risky command on dev
        ↓
Step 2: Hook exits 2 with structured message:
        "[CONFIRM] Force push on dev requires approval.
         Action: git push --force origin dev
         Risk: Overwrites remote history
         To allow: create .claude/allow-once"
        ↓
Step 3: Claude reads "[CONFIRM]" prefix and asks user:
        "The branch guard flagged this action:
         git push --force on dev (overwrites remote history)
         Should I proceed? [Yes/No]"
        ↓
Step 4a: User says "yes" → Claude creates one-shot marker:
         .claude/allow-once  (consumed on next hook call)
         Claude retries the command → hook sees marker → allows → deletes marker
        ↓
Step 4b: User says "no" → Claude suggests alternatives
```

### One-Shot Marker (Auto-Consumed)

```json
// .claude/allow-once — deleted after single use
{
  "action": "git push --force",
  "approved_at": "2026-02-13T15:00:00Z",
  "session_id": "abc-123"
}
```

```bash
# In hook: check one-shot marker
ONCE_MARKER="${PROJECT_ROOT}/.claude/allow-once"
if [[ -f "$ONCE_MARKER" ]]; then
  rm "$ONCE_MARKER"    # Consume immediately
  exit 0               # Allow this one command
fi
```

### What Gets Confirmed on Dev (vs. Hard-Blocked vs. Allowed)

| Action | Current | Proposed | Rationale |
|--------|---------|----------|-----------|
| Edit existing file | ✅ Allow | ✅ Allow | Fixups always OK |
| Write new .md | ✅ Allow | ✅ Allow | Docs always OK |
| Write new .py/.sh/.js | 🔴 Block | 🟡 **Confirm** | User decides if intentional |
| Write to tests/ | ✅ Allow | ✅ Allow | Tests always OK |
| `git push` (normal) | ✅ Allow | ✅ Allow | Regular push is safe |
| `git push --force` | 🔴 Block | 🟡 **Confirm** | Ask before overwriting history |
| `git commit` | ✅ Allow | ✅ Allow | Regular commits are fine |
| `git reset --hard` | ✅ Allow | 🟡 **Confirm** | Discards work — ask first |
| `git checkout -- .` | ✅ Allow | 🟡 **Confirm** | Discards changes — ask first |
| `git clean -f` | ✅ Allow | 🟡 **Confirm** | Removes untracked — ask first |
| `git branch -D` | ✅ Allow | 🟡 **Confirm** | Force-deletes branch — ask first |

### Message Format (Structured for Claude Parsing)

```text
[CONFIRM] Cannot force push on dev without approval.
Action:  git push --force origin dev
Risk:    Overwrites remote commit history
Branch:  dev (confirm mode)
Options:
  1. Approve this action (one-shot)
  2. Cancel
  3. Bypass all: /craft:git:unprotect
```

The `[CONFIRM]` prefix is the signal to Claude that this is confirmable (vs. `[BLOCK]` for hard blocks on main).

### Backward Compatibility

- `block-all` on main: unchanged (hard block, no confirmation)
- `block-new-code` on dev: becomes a **sub-behavior** of `confirm` — new code files trigger confirmation, everything else stays the same
- Feature branches: unchanged (unrestricted)
- `/craft:git:unprotect`: still works as blanket bypass

### Implementation in hook

```bash
# New confirm mode (replaces block-new-code section)
if [[ "$PROTECTION" == "confirm" ]]; then
  # Same logic as block-new-code, but use [CONFIRM] prefix
  # instead of hard [BLOCK], and add one-shot marker check
fi
```

### Trade-offs

| Pro | Con |
|-----|-----|
| User stays in control (explicit approval) | Requires Claude to understand [CONFIRM] protocol |
| No more "wall" experience on dev | One-shot marker adds file I/O |
| Legitimate operations proceed smoothly | Need to update 138 tests for new behavior |
| Backward-compatible (block-all unchanged) | Slightly more complex hook logic |

### Effort: 🏗️ Large (~2-3 hours) — this is the centerpiece improvement

---

## Improvement 1: Auto-Expiring Bypass with Optional Timer

### What It Means

Currently, `/craft:git:unprotect` creates a marker file that persists **forever** until you manually run `/craft:git:protect`. During today's session, the bypass was left active after a maintenance task and had to be manually cleaned up. This suggestion adds an optional timeout so the bypass auto-expires.

### Current Behavior

```bash
# Bypass is permanent until removed
.claude/allow-dev-edit  # JSON with reason + timestamp, no expiry
```

### Proposed Change

```bash
# Add optional "expires" field
{
  "reason": "maintenance",
  "timestamp": "2026-02-13T14:30:00Z",
  "branch": "dev",
  "expires": "2026-02-13T15:30:00Z"   # ← NEW: optional 1-hour default
}
```

The hook checks: if `expires` exists and is in the past, treat marker as absent (re-enable protection). The `/craft:git:unprotect` command gets an optional `--duration` flag:

```bash
/craft:git:unprotect maintenance              # Default: 1 hour
/craft:git:unprotect maintenance --duration 2h  # Custom: 2 hours
/craft:git:unprotect maintenance --no-expire    # Explicit: no expiry (current behavior)
```

### Trade-offs

| Pro | Con |
|-----|-----|
| Prevents forgotten bypasses | Adds complexity to the hook |
| Safety net for distracted workflows | May expire mid-task (annoying) |
| ADHD-friendly (set and forget) | Requires date comparison in bash |

### Effort: ⚡ Quick (~30 min)

---

## Improvement 2: Expanded Destructive Command Protection

### What It Means

The current hook blocks `git commit`, `git push`, `git reset --hard`, and `git push --force` on protected branches. Community hooks (Dicklesworthstone, karanb192) block a wider set of destructive commands that can cause data loss. This adds protection against commands that discard uncommitted work or delete branches.

### Current Coverage vs. Proposed

| Command | Currently Blocked? | Risk Level | Proposed |
|---------|-------------------|------------|----------|
| `git commit` | ✅ On main | Critical | Keep |
| `git push` | ✅ On main | Critical | Keep |
| `git push --force` | ✅ On dev | High | Keep |
| `git reset --hard` | ✅ On main | Critical | Keep |
| `git checkout -- .` | ❌ | High | **Add** |
| `git restore .` | ❌ | High | **Add** |
| `git clean -f` / `-fd` | ❌ | High | **Add** |
| `git branch -D` (force delete) | ❌ | Medium | **Add** |
| `git stash drop` / `clear` | ❌ | Medium | **Consider** |
| `rm -rf .git` | ❌ | Critical | **Add** |

### What Each Blocked Command Does

- **`git checkout -- .`** / **`git restore .`** — Discards ALL uncommitted changes in working directory. No undo.
- **`git clean -f`** — Removes all untracked files. `-fd` also removes directories. Gone forever.
- **`git branch -D`** — Force-deletes a branch even if not merged. Can lose commits.
- **`rm -rf .git`** — Destroys the entire git history. Catastrophic.

### Proposed Scope

- On `main`: Block all of the above (already block-all, so they're implicitly blocked for Edit/Write but not for Bash)
- On `dev`: Block `git checkout -- .`, `git restore .`, `git clean -f`, `rm -rf .git`
- On `feature/*`: Block only `rm -rf .git` (safety net)

### Trade-offs

| Pro | Con |
|-----|-----|
| Prevents accidental data loss | More grep patterns = marginally slower |
| Catches common "oops" commands | May block intentional cleanup |
| Community-validated patterns | Slightly more complex Bash parsing |

### Effort: 🔧 Medium (~1 hour)

---

## Improvement 3: Tool Input Modification (Claude Code v2.0.10+)

### What It Means

Since Claude Code v2.0.10, PreToolUse hooks can **modify tool inputs** instead of just blocking them. Instead of showing an error when you try to write a file on the wrong branch, the hook could suggest or auto-redirect the action. This turns blocking into coaching.

### How It Works

```bash
# Current: exit 2 = hard block
exit 2  # "Cannot create new .py file on dev"

# New option: exit 0 with modified JSON on stdout
# Modifies the tool input before execution
echo '{"tool_input": {"file_path": "/suggested/path"}}' | exit 0
```

### Use Cases

1. **Auto-suggest worktree path**: When creating a new `.py` on dev, instead of blocking, suggest: "Would you like me to create this in the worktree instead?"
2. **Redirect force-push to regular push**: When force-pushing on dev, strip the `--force` flag and continue with regular push.
3. **Add warning prefix**: When committing on dev, prepend `[DEV]` to commit message as a visual cue.

### Why This Matters

The current approach is *prohibitive* — it says "no" and requires the user to figure out the alternative. Input modification is *corrective* — it guides toward the right action automatically.

### Trade-offs

| Pro | Con |
|-----|-----|
| Better UX (guidance vs. blocking) | More complex hook logic |
| Reduces friction for common mistakes | Silent modification could confuse |
| Aligns with latest Claude Code capabilities | Requires v2.0.10+ (breaking for older) |

### Effort: 🏗️ Large (~2-3 hours, needs design decisions)

---

## Improvement 4: Audit Log for Block Events

### What It Means

Currently, when the branch guard blocks an action, the error message goes to stderr and disappears after the session. There's no record of *what* was blocked, *when*, or *how often*. An audit log captures every block event and bypass activation for later review.

### Proposed Format

```bash
# .claude/branch-guard.log (append-only)
2026-02-13T14:30:00Z BLOCK main Edit src/main.py "Cannot edit files on main"
2026-02-13T14:31:00Z BLOCK dev Write src/new.py "Cannot create new .py file on dev"
2026-02-13T14:35:00Z BYPASS dev maintenance "User activated bypass"
2026-02-13T15:00:00Z RESTORE dev "Protection re-enabled"
```

### Why This Matters

1. **Pattern detection**: See which branches/files trigger the most blocks
2. **Bypass tracking**: Know when and why protection was disabled
3. **Training data**: Understand how often the guard prevents mistakes
4. **Debugging**: When something slips through, check what the guard saw

### Implementation

Add ~5 lines to the `block()` function:

```bash
_log() {
  local logfile="${PROJECT_ROOT}/.claude/branch-guard.log"
  mkdir -p "$(dirname "$logfile")"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$logfile"
}
```

### Trade-offs

| Pro | Con |
|-----|-----|
| Visibility into guard behavior | Log file grows over time |
| Helps debug false positives | Minor I/O overhead per hook call |
| Useful for `/craft:git:status` | Needs rotation/cleanup eventually |

### Effort: ⚡ Quick (~15 min)

---

## Improvement 5: Bash Write-Through Detection

### What It Means

The branch guard blocks the `Write` tool for new code files on dev, but the `Bash` tool can create files via shell commands like `cat > file.py << EOF` or `echo "code" > file.py`. These bypass the Write tool entirely — the guard only sees a Bash command string.

### Current Gap

```bash
# These bypass Write tool protection on dev:
cat > src/new_feature.py << 'EOF'
print("hello")
EOF

echo 'print("hello")' > src/new_feature.py

cp template.py src/new_feature.py
```

### Proposed Detection

Add patterns to the Bash handler for `block-new-code`:

```bash
# Detect file creation via Bash
if echo "$COMMAND" | grep -qE '(cat|echo|printf|tee|cp|mv)[[:space:]].*>[[:space:]]*[^ ]+\.(py|sh|js|ts|jsx|tsx)'; then
  # Check if target file exists (same logic as Write handler)
  # Block if new file on dev
fi
```

### Why This Matters

During the Feb 6 incident, advisory rules were bypassed through creative approaches. While Bash write-through requires more deliberate action than accidentally using the Write tool, it's still a vector for unplanned code on dev.

### Trade-offs

| Pro | Con |
|-----|-----|
| Closes a real bypass vector | Regex for shell commands is fragile |
| Consistent protection across tools | May false-positive on legitimate commands |
| Harder to accidentally bypass | Complex to get right (many shell patterns) |

### Effort: 🔧 Medium (~1-2 hours, needs careful regex)

---

## Improvement 6: Glob Pattern Matching in Config

### What It Means

The custom config (`.claude/branch-guard.json`) only supports exact branch names. If you want to protect `release/1.0`, `release/2.0`, etc., you need to list each one explicitly. Glob patterns like `release/*` would make config more flexible.

### Current Limitation

```json
{
  "main": "block-all",
  "release/1.0": "block-all",
  "release/2.0": "block-all",
  "release/3.0": "block-all"
}
```

### Proposed Enhancement

```json
{
  "main": "block-all",
  "release/*": "block-all",
  "staging/*": "block-new-code",
  "draft": "block-new-code"
}
```

### Implementation

Replace exact jq lookup with a pattern-matching loop:

```bash
# Try exact match first (fast path)
PROTECTION="$(_json_get ".\"${BRANCH}\"" "$CONFIG_CONTENT")"

# If no exact match, try glob patterns
if [[ -z "$PROTECTION" ]]; then
  for key in $(echo "$CONFIG_CONTENT" | jq -r 'keys[]'); do
    if [[ "$BRANCH" == $key ]]; then  # Bash glob matching
      PROTECTION="$(_json_get ".\"${key}\"" "$CONFIG_CONTENT")"
      break
    fi
  done
fi
```

### Trade-offs

| Pro | Con |
|-----|-----|
| More flexible for multi-branch workflows | Adds iteration (slightly slower) |
| Matches auto-detect pattern behavior | Glob ordering ambiguity |
| Essential for release/* patterns | Need to document precedence rules |

### Effort: ⚡ Quick (~30 min)

---

## Improvement 7: Session-Scoped Bypass (Hook-Level)

### What It Means

Currently, the bypass marker is a file on disk — it persists across sessions, terminal restarts, and even reboots. Community best practices suggest tying bypass to the current Claude Code session. When the session ends, protection auto-restores.

### How It Could Work

The hook receives `session_id` in its JSON input. Instead of checking for a marker file, check if the current session ID matches the bypass session:

```json
{
  "reason": "maintenance",
  "timestamp": "2026-02-13T14:30:00Z",
  "branch": "dev",
  "session_id": "abc-123-def"
}
```

```bash
# In hook: check session match
CURRENT_SESSION="$(_json_get '.session_id' "$INPUT")"
BYPASS_SESSION="$(_json_get '.session_id' "$MARKER_CONTENT")"

if [[ "$CURRENT_SESSION" == "$BYPASS_SESSION" ]]; then
  exit 0  # Same session — bypass active
fi
# Different session — marker is stale, ignore it
```

### Why This Matters

This was a real friction point today: the bypass was left active after maintenance and had to be manually removed. Session-scoped bypass means you never forget to re-enable protection.

### Trade-offs

| Pro | Con |
|-----|-----|
| Auto-restores on session end | Can't carry bypass across sessions |
| Prevents forgotten bypasses | Need to re-bypass in new sessions |
| Matches Claude Code's session model | Requires session_id parsing |

### Effort: 🔧 Medium (~45 min)

---

## Improvement 8: Performance Optimization (Optional)

### What It Means

The hook runs on **every** Edit, Write, and Bash tool call. Each invocation reads stdin JSON, parses it (up to 6 `_json_get` calls), checks git context, reads config file, and applies rules. For a typical session with hundreds of tool calls, this adds up.

### Current Profile (Estimated)

| Step | Time | Calls |
|------|------|-------|
| Read stdin | <1ms | 1 |
| Parse JSON (jq) | ~5ms | 4-6 |
| Git context | ~10ms | 2 (rev-parse, branch) |
| Read config | ~2ms | 1 |
| Apply rules | ~1ms | 1 |
| **Total** | **~25ms** | per tool call |

### Optimization Ideas

1. **Early exit for non-protected tools**: If `TOOL_NAME` is not Edit/Write/Bash, exit immediately (already done via matcher config)
2. **Cache git context**: Write branch name to `.claude/branch-guard-cache` on first call, reuse for 5 seconds
3. **Inline jq queries**: Combine multiple jq calls into one: `jq '{tool: .tool_name, file: .tool_input.file_path}'`

### Trade-offs

| Pro | Con |
|-----|-----|
| Faster tool execution | Caching adds complexity |
| Better UX for rapid edits | Stale cache risk (branch switch) |
| Marginal gain (~15ms/call) | 25ms is already fast enough |

### Effort: 🔧 Medium (~1 hour), but **low priority** — 25ms is well within the 5000ms timeout

---

## User Decisions (2026-02-13)

### Selected Improvements

1. **Confirmation Mode for Dev** (Priority 1) — Centerpiece: replace hard-block with ask-user-first flow
2. **Bash Write-Through Detection** (Improvement 5) — Close the Bash bypass vector
3. **Tool Input Modification / Coaching** (Improvement 3) — Design spec for auto-corrections
4. **Expanded Destructive Commands** (folded into Priority 1) — Confirm before `checkout --`, `clean -f`, `branch -D`, etc.

### Deferred

- Auto-Expiring Bypass (Improvement 1) — Partially addressed by session-scoped one-shot markers
- Audit Log (Improvement 4) — Nice-to-have, not urgent
- Glob Patterns (Improvement 6) — Low priority for current projects
- Session-Scoped Bypass (Improvement 7) — One-shot markers solve the same problem
- Performance (Improvement 8) — Not needed (25ms is fast enough)

## Implementation Order

### Phase 1: Confirmation Mode (~2-3 hours)

1. Add `confirm` protection level to branch-guard.sh
2. Implement one-shot marker (`.claude/allow-once`) — auto-consumed
3. Structured `[CONFIRM]` message format for Claude parsing
4. Move destructive commands (`checkout --`, `clean -f`, `reset --hard`, `branch -D`) into confirm flow
5. Update tests (49 unit + 31 e2e need adjustment)

### Phase 2: Bash Write-Through (~1-2 hours)

6. Add file creation pattern detection to Bash handler
7. Integrate with confirm flow (not hard block)
8. Add tests for common patterns (`cat >`, `echo >`, `tee`, `cp`)

### Phase 3: Coaching Mode Spec (~1 hour design)

9. Design spec for tool input modification (v2.0.10+)
10. Define which actions get auto-corrected vs. confirmed
11. Prototype: strip `--force` from push, redirect new files to worktree suggestion

## Recommended Path

→ Start with **Phase 1: Confirmation Mode** — this is the user's primary request and the highest-impact change. It transforms the dev experience from "wall + manual bypass" to "ask + one-shot approval". Phase 2 (Bash detection) closes the bypass vector within the new confirm paradigm. Phase 3 (coaching spec) is a design document for the next version.

---

## Research Sources

### Community Patterns

- **Dicklesworthstone**: Destructive git command protection pattern — blocks `checkout --`, `clean -f`, `reset --hard`, `branch -D`, `rm -rf`
- **karanb192/claude-code-hooks**: Community hooks collection with safety levels (critical/high/strict)
- **GitHub Copilot**: Uses `copilot/` branch prefix pattern for AI-generated code isolation

### Claude Code Hook Capabilities

- **v2.0.10+**: PreToolUse hooks can now modify tool inputs (stdout JSON), not just block (exit 2)
- **Exit codes**: 0 = allow, 2 = block, other = allow (safety default)
- **Timeout**: 5000ms per hook invocation
- **Matcher**: Regex on tool name (e.g., `Edit|Write`)
