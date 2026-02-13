# Quick Reference: Branch Guard

**Teaching-first branch protection** — 3-tier risk classification with progressive trust.

**Version:** 2.17.0 | **Hook:** `~/.claude/hooks/branch-guard.sh`

---

## Quick Decision Tree

```text
What do you need to do?
│
├─ Write new code file on dev?
│   └─ MEDIUM: Guard will [CONFIRM] — approve or use worktree
│
├─ Edit existing file on dev?
│   └─ LOW: Always allowed (note on first encounter)
│
├─ Write markdown on dev?
│   └─ LOW: Always allowed
│
├─ Force push on dev?
│   └─ MEDIUM: Guard will [CONFIRM]
│
├─ Do bulk maintenance on dev?
│   └─ /craft:git:unprotect maintenance
│
├─ Work on feature branch?
│   └─ No restrictions — guard is inactive
│
└─ Anything on main?
    └─ BLOCKED — use PR workflow
```

---

## Risk Tiers at a Glance

| Risk | Icon | Behavior | Can Approve? |
|------|------|----------|-------------|
| **LOW** | `[guard]` | Note once, then silent | Auto-allowed |
| **MEDIUM** | `[CONFIRM]` | Teaching box → confirm | Yes (one-shot) |
| **HIGH** | `CATASTROPHIC` | Hard block | No (remove hook) |

---

## What Triggers Each Tier

### LOW (Auto-Allow)

| Action | Condition |
|--------|-----------|
| Edit file | File exists on disk |
| Write `.md` | Any markdown file |
| Write extensionless | `.STATUS`, `Makefile`, `Dockerfile`, `LICENSE` |
| Write in `tests/` | Any file under tests directory |
| Overwrite file | File already exists |

### MEDIUM (Confirm)

| Action | Trigger |
|--------|---------|
| New code file | `.py`, `.sh`, `.js`, `.ts`, `.json`, `.yml` (and more) via Write |
| Bash write-through | `echo > new.py`, `tee new.py`, `cp x new.py` |
| Force push | `git push --force` or `--force-with-lease` |
| Reset hard | `git reset --hard` |
| Checkout discard | `git checkout -- <file>` |
| Restore | `git restore <file>` (not `--staged`) |
| Clean force | `git clean -f`, `-fd`, `-fx` |
| Branch force-delete | `git branch -D` (all branches) |
| Critical files | `.env*`, `*.pem`, `*.key`, `*.secret`, `branch-guard.json` |

### HIGH (Hard Block)

| Action | Trigger | Scope |
|--------|---------|-------|
| Repository deletion | `rm -rf .git` | All branches |

---

## Bypass Mechanisms

### One-Shot (Single Action)

When Claude shows `[CONFIRM]` and you approve:

```text
Guard blocks → You approve → Claude writes .claude/allow-once
→ Guard consumes marker → Action proceeds → Protection resumes
```

No commands needed — just approve the prompt.

### Session Bypass (Bulk Operations)

```bash
# Enable bypass
/craft:git:unprotect maintenance

# Do your work (all guards disabled)
# ...

# Re-enable
/craft:git:protect
```

---

## Verbosity Fade

| Encounter | Level | What You See |
|-----------|-------|--------------|
| 1st | Full | Teaching box + risk + alternatives |
| 2nd-3rd | Brief | Compact box: action + risk + branch |
| 4th+ | Minimal | `[CONFIRM] action on branch. Allow?` |

Resets after **8 hours** of inactivity.

---

## Branch Protection Map

| Branch | Protection | Write New Code | Edit Existing | Commit/Push |
|--------|-----------|---------------|--------------|-------------|
| `main` | `block-all` | Blocked | Blocked | Blocked |
| `dev` | `smart` | MEDIUM confirm | LOW allow | Allowed |
| `feature/*` | None | Allowed | Allowed | Allowed |
| `fix/*` | None | Allowed | Allowed | Allowed |

---

## Common Scenarios

### "I need to fix a typo in existing code on dev"

```text
→ Guard: LOW (allowed, brief note first time)
→ No action needed — just edit
```

### "I need to add a new Python file on dev"

```text
→ Guard: MEDIUM [CONFIRM]
→ Options:
  a) Approve the confirm prompt (one-shot)
  b) /craft:git:worktree feature/<name> (recommended)
  c) /craft:git:unprotect maintenance (bulk bypass)
```

### "I'm resolving merge conflicts on dev"

```bash
/craft:git:unprotect merge-conflict
# Resolve conflicts freely
/craft:git:protect
```

### "I need to update documentation on dev"

```text
→ Guard: LOW (markdown always allowed)
→ No action needed — just write
```

### "I accidentally force-pushed"

```text
Guard would have shown [CONFIRM] first.
If you approved, use git reflog to recover.
```

---

## Config File (Optional)

`.claude/branch-guard.json` — override auto-detection:

```json
{
  "main": "block-all",
  "dev": "smart",
  "staging": "smart"
}
```

Only listed branches are protected. Unlisted = unrestricted.

---

## Session Files

| File | What It Does |
|------|-------------|
| `.claude/allow-dev-edit` | Session bypass (unprotect) |
| `.claude/allow-once` | One-shot approval marker |
| `.claude/guard-session-counts` | Verbosity fade counter |
| `.claude/branch-guard-dryrun` | Dry-run mode (log only) |

---

## Commands

| Command | Purpose |
|---------|---------|
| `/craft:git:protect` | Re-enable protection |
| `/craft:git:protect --show` | Show current level + counters |
| `/craft:git:protect --level smart` | Set protection level |
| `/craft:git:protect --reset` | Reset session counters |
| `/craft:git:unprotect` | Session-wide bypass |
| `/craft:git:status` | Shows guard indicator |

---

## Code Extensions (Trigger MEDIUM on New File)

```text
py sh js ts jsx tsx json yml yaml toml cfg ini r R zsh
```

Everything else (`.txt`, `.csv`, `.html`, `.md`) — allowed without confirm.

---

## See Also

- **Guide:** [Smart Mode Guide](../guide/branch-guard-smart-mode.md) — Full documentation
- **Tutorial:** [Branch Guard Setup](../tutorials/TUTORIAL-branch-guard-setup.md) — Step-by-step
- **Workflow:** [Git Feature Workflow](../workflows/git-feature-workflow.md) — How guard fits in
- **Commands:** [/craft:git:protect](../commands/git/protect.md) | [/craft:git:unprotect](../commands/git/unprotect.md)
