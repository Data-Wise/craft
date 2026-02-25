# ORCHESTRATE: Branch Guard Hook - Fix False Positives

**Branch:** `feature/branch-guard-fix`
**Base:** `dev`
**PR Target:** `dev`
**Repo:** craft

---

## Context

The branch guard hook (`scripts/branch-guard.sh`, ~740 lines) has three false-positive issues discovered during homebrew-tap PR review sessions.

---

## Increments

### Increment 1: Allow writes to non-repo paths

**File:** `scripts/branch-guard.sh` (after line ~82)

The Write/Edit handlers block ALL file writes on protected branches, even for files outside the git repo (e.g., `~/.claude/projects/.../memory/`).

**Fix:** After determining `PROJECT_ROOT` and `BRANCH`, add early exit if target file is outside repo:

```bash
# If path is outside repo root, allow regardless of branch
if [[ -n "$FILE_PATH_ABS" && "$FILE_PATH_ABS" != "$PROJECT_ROOT"* ]]; then
  exit 0
fi
```

### Increment 2: Tighten command text regex

**File:** `scripts/branch-guard.sh` (line 460 and similar)

Current regex matches git subcommands anywhere in the string, catching heredocs and Python strings.

**Current (line 460):**

```bash
if echo "$COMMAND" | grep -qE 'git[[:space:]]+commit|git[[:space:]]+push'; then
```

**Fix:** Require git at the start of a line/statement:

```bash
if echo "$COMMAND" | grep -qE '(^|;|&&|\\|\\|)[[:space:]]*(git[[:space:]]+(commit|push))'; then
```

Apply same pattern to ALL similar regex checks (lines 460, 623-663).

### Increment 3: Test and validate

1. Write to non-repo path on main -> should ALLOW
2. Write to repo path on main -> should BLOCK
3. Bash with direct git operation on main -> should BLOCK
4. Bash with git keywords in heredoc/string -> should ALLOW
5. Dev branch smart-mode still works

---

## Verification Checklist

- [ ] Non-repo file writes allowed on protected branches
- [ ] Repo file writes still blocked on protected branches
- [ ] Direct git commands still blocked on main
- [ ] Git keywords in strings/heredocs no longer trigger blocks
- [ ] Dev branch smart-mode unaffected
