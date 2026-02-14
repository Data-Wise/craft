# Tutorial: Branch Guard Setup

> **Set up teaching-first branch protection in 5 minutes**
> **Difficulty:** Beginner | **Time:** 5 minutes | **Prerequisites:** Git, Claude Code

---

## What You'll Learn

1. Install the branch guard hook
2. Verify it works on each branch type
3. Customize protection with config file
4. Use bypass mechanisms when needed

---

## Step 1: Install the Hook

The branch guard is a Claude Code PreToolUse hook — a shell script that runs before every tool call.

### Option A: Craft Plugin (Automatic)

If you have the Craft plugin installed, the hook is already at:

```text
~/.claude/hooks/branch-guard.sh
```

Verify it exists:

```bash
ls -la ~/.claude/hooks/branch-guard.sh
# Should show the file with execute permissions
```

### Option B: Manual Installation

Copy the hook script to your Claude Code hooks directory:

```bash
# Create hooks directory
mkdir -p ~/.claude/hooks

# Copy from craft plugin (if available)
cp /path/to/craft/scripts/branch-guard.sh ~/.claude/hooks/branch-guard.sh

# Make executable
chmod +x ~/.claude/hooks/branch-guard.sh
```

### Register the Hook

Add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/branch-guard.sh"
          }
        ]
      }
    ]
  }
}
```

The empty `matcher` means the hook runs for **every** tool call (Edit, Write, Bash, etc.).

---

## Step 2: Verify Installation

### Test on Main Branch

```bash
cd your-project
git checkout main

# Try to edit a file — should be BLOCKED
# Claude will see:
#   ╔═══════════════════════════════════════════════════════╗
#   ║ BRANCH PROTECTION                                     ║
#   ╠═══════════════════════════════════════════════════════╣
#   ║ Cannot edit files on main.                            ║
#   ║ → git checkout dev                                    ║
#   ╚═══════════════════════════════════════════════════════╝
```

### Test on Dev Branch

```bash
git checkout dev

# Edit existing file — should be ALLOWED (LOW risk)
# Write new .py file — should show [CONFIRM] (MEDIUM risk)
# Write .md file — should be ALLOWED (LOW risk)
```

### Test on Feature Branch

```bash
git checkout -b feature/test-guard

# Everything should be ALLOWED — no restrictions
# Write new files, edit anything, push freely
```

### Quick Smoke Test

Run this to verify all three branch types:

```bash
# From your project root
echo '{"tool_name":"Write","tool_input":{"file_path":"test.py"},"cwd":"'$(pwd)'"}' | \
  bash ~/.claude/hooks/branch-guard.sh 2>&1; echo "Exit: $?"
```

Expected results by branch:

- `main` → Exit: 2 (blocked)
- `dev` → Exit: 2 with `[CONFIRM]` (new code file)
- `feature/*` → Exit: 0 (allowed)

---

## Step 3: Understand Auto-Detection

By default, the guard auto-detects protection levels:

```text
Repository has 'dev' branch?
├─ Yes → main=block-all, dev=smart
└─ No  → main=block-all only
```

Feature branches (`feature/*`, `fix/*`, `hotfix/*`, `refactor/*`, `chore/*`, `docs/*`, `test/*`) are always unrestricted.

### What "Smart" Means on Dev

| Action | Risk | Result |
|--------|------|--------|
| Edit existing `.py` | LOW | Allowed (note first time) |
| Write new `.py` | MEDIUM | `[CONFIRM]` prompt |
| Write `.md` | LOW | Always allowed |
| Write in `tests/` | LOW | Always allowed |
| `git push --force` | MEDIUM | `[CONFIRM]` prompt |
| `git reset --hard` | MEDIUM | `[CONFIRM]` prompt |

---

## Step 4: Customize (Optional)

### Per-Project Config

Create `.claude/branch-guard.json` in your project root to override auto-detection:

```bash
mkdir -p .claude
cat > .claude/branch-guard.json << 'EOF'
{
  "main": "block-all",
  "dev": "smart",
  "staging": "smart"
}
EOF
```

Only branches listed in the config are protected. Everything else is unrestricted.

### Protection Levels

| Level | Behavior |
|-------|----------|
| `block-all` | Hard block everything (main) |
| `smart` | 3-tier risk classification (recommended for dev) |
| `block-new-code` | Alias for `smart` (backward compatible) |
| `confirm` | Alias for `smart` |

### Add to .gitignore

The session files should not be committed:

```bash
# Add to .gitignore
echo '.claude/allow-dev-edit' >> .gitignore
echo '.claude/allow-once' >> .gitignore
echo '.claude/guard-session-counts' >> .gitignore
echo '.claude/branch-guard-dryrun' >> .gitignore
```

The config file (`.claude/branch-guard.json`) **should** be committed — it's project configuration.

---

## Step 5: Using Bypass Mechanisms

### One-Shot Approval (Most Common)

When the guard shows a `[CONFIRM]` prompt, simply approve it in Claude's UI. The guard creates a one-shot marker that allows the next action, then resumes protection.

```text
Guard: [CONFIRM] Write new .py file on dev. Allow?
You: Yes
→ Action proceeds
→ Next action is protected again
```

### Session Bypass (Bulk Work)

For merge conflicts or maintenance requiring many protected operations:

```bash
# Bypass protection
/craft:git:unprotect merge-conflict

# Do your work — all guards disabled
# Edit files, write new code, etc.

# Re-enable when done
/craft:git:protect
```

### Dry-Run Mode (Testing)

See what the guard would block without actually blocking:

```bash
# Enable dry-run
touch .claude/branch-guard-dryrun

# Guard will log "[DRY-RUN] would block: ..." but allow everything
# Check stderr for what would have been blocked

# Disable dry-run
rm .claude/branch-guard-dryrun
```

---

## Step 6: Check Guard Status

### Via /craft:git:status

The status command shows guard information:

```bash
/craft:git:status
# Output includes:
# │ Guard: smart (3 confirms) · one-shot: inactive  │
```

### Via /craft:git:protect --show

See detailed protection status:

```bash
/craft:git:protect --show
# Shows:
# - Current protection level
# - Session counter (confirms this session)
# - One-shot marker status
# - Bypass status
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Guard not triggering | Check `~/.claude/settings.json` has the hook registered |
| Guard blocking everything | Verify you're on the right branch (`git branch --show-current`) |
| `jq: command not found` | Install jq (`brew install jq`) or the hook falls back to Python |
| Permission denied | `chmod +x ~/.claude/hooks/branch-guard.sh` |
| Config not loading | Verify `.claude/branch-guard.json` is valid JSON (`jq . .claude/branch-guard.json`) |
| Session counter stale | Delete `.claude/guard-session-counts` or use `/craft:git:protect --reset` |
| Need to bypass everything | `/craft:git:unprotect maintenance` |

---

## What's Next?

- Read the [Smart Mode Guide](../guide/branch-guard-smart-mode.md) for detailed risk classification
- Check the [Quick Reference Card](../reference/REFCARD-BRANCH-GUARD.md) for at-a-glance lookup
- Learn the [Git Feature Workflow](../workflows/git-feature-workflow.md) that the guard supports
- Review [Safety Rails](https://github.com/Data-Wise/craft/blob/dev/commands/git/docs/safety-rails.md) for progressive trust philosophy

---

## Summary

```text
1. Install hook → ~/.claude/hooks/branch-guard.sh
2. Register in settings.json (PreToolUse matcher: "")
3. Auto-detects: main=block-all, dev=smart, feature=unrestricted
4. Customize with .claude/branch-guard.json (optional)
5. Approve [CONFIRM] prompts for one-shot access
6. /craft:git:unprotect for bulk bypass
7. /craft:git:protect to re-enable
```
