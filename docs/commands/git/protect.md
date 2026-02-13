# /craft:git:protect

> **Re-enable branch protection after a temporary bypass**

---

## Synopsis

```bash
/craft:git:protect              # Re-enable protection
/craft:git:protect --show       # Show current level + counters
/craft:git:protect --level smart  # Set protection level
/craft:git:protect --reset      # Reset session counters
```

---

## Description

Removes the bypass marker (`.claude/allow-dev-edit`) and restores branch protection enforcement. The `branch-guard.sh` PreToolUse hook will resume blocking disallowed edits on the next tool call.

Safe to run multiple times --- if no bypass is active, it reports the current protection level and exits.

---

## Behavior

1. Checks if the `branch-guard.sh` hook is installed
2. If no bypass marker exists, reports current protection level and exits
3. Removes `.claude/allow-dev-edit` marker file
4. Detects and displays the restored protection level

---

## Options

| Flag | Description |
|------|-------------|
| `--show` | Display current protection level, session counters, and one-shot marker status |
| `--level <level>` | Set protection level (`block-all`, `smart`, or empty to clear) |
| `--reset` | Reset session counters (verbosity fade restarts from full) |

---

## Protection Levels

| Level | Branches | Behavior |
|-------|----------|----------|
| `block-all` | main, master | Hard block all writes, edits, commits, pushes |
| `smart` | dev, develop | 3-tier risk: LOW (allow) / MEDIUM (confirm) / HIGH (block) |
| `block-new-code` | (alias) | Deprecated alias for `smart` — backward compatible |
| `confirm` | (alias) | Alias for `smart` |

Protection level is determined by `.claude/branch-guard.json` if present, otherwise auto-detected from the branch name.

### Smart Mode Risk Tiers

| Risk | Behavior | Examples |
|------|----------|----------|
| **LOW** | Note on first encounter, then silent | Edit existing file, write markdown, write tests |
| **MEDIUM** | Teaching box + `[CONFIRM]` prompt | New code file, force push, destructive commands |
| **HIGH** | Hard block (never allowed) | `rm -rf .git` (repository deletion) |

---

## Examples

**Re-enable after merge conflict resolution:**

```bash
# After resolving conflicts with protection bypassed
/craft:git:protect
# → Branch protection RE-ENABLED.
# → Branch: dev
# → Protection: smart (3-tier)
```

**Check status when already protected:**

```bash
/craft:git:protect
# → Branch protection is already active. Nothing to do.
# → Current branch: dev
# → Protection level: smart
```

**Show detailed status:**

```bash
/craft:git:protect --show
# → Protection: smart
# → Branch: dev
# → Session confirms: 5
# → One-shot marker: inactive
# → Bypass: inactive
```

**Reset session counters:**

```bash
/craft:git:protect --reset
# → Session counters reset. Teaching boxes will show full verbosity.
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Protection re-enabled or already active |

---

## See Also

- [/craft:git:unprotect](unprotect.md) --- Temporarily bypass branch protection
- [/craft:git:status](status.md) --- Shows protection indicator
- [/craft:check](../check.md) --- Shows branch context section
- [Smart Mode Guide](../../guide/branch-guard-smart-mode.md) --- Full smart mode documentation
- [Branch Guard Quick Reference](../../reference/REFCARD-BRANCH-GUARD.md) --- At-a-glance reference
- [Branch Protection Architecture](../../architecture.md#5-branch-protection-hooks) --- How the hook works
