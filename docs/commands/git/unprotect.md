# /craft:git:unprotect

> **Temporarily bypass branch protection for the current session**

---

## Synopsis

```bash
/craft:git:unprotect [reason]
```

**Quick examples:**

```bash
# Interactive (asks for reason)
/craft:git:unprotect

# With reason
/craft:git:unprotect merge-conflict
/craft:git:unprotect ci-fix
/craft:git:unprotect maintenance
```

---

## Description

Creates a bypass marker (`.claude/allow-dev-edit`) that tells the `branch-guard.sh` PreToolUse hook to allow all edits, even on protected branches. The bypass persists until you re-enable protection with `/craft:git:protect`.

Every bypass is logged with a reason, timestamp, and branch name for auditability.

---

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `reason` | Why protection is being bypassed | No (interactive prompt if omitted) |

**Built-in reasons:**

| Reason | When to use |
|--------|-------------|
| `merge-conflict` | Resolving merge conflicts on dev that require code file edits |
| `ci-fix` | Fixing CI/CD configuration or test files directly on dev |
| `maintenance` | General maintenance that requires direct edits on a protected branch |

---

## Behavior

1. Checks if bypass is already active --- if so, shows current status and exits
2. If no reason provided, presents an interactive prompt with standard reasons
3. Creates `.claude/allow-dev-edit` marker with JSON metadata (reason, timestamp, branch)
4. Confirms bypass is active and reminds how to re-enable

---

## Marker Format

The bypass marker at `.claude/allow-dev-edit` contains:

```json
{
  "reason": "merge-conflict",
  "timestamp": "2026-02-07T14:30:00Z",
  "branch": "dev"
}
```

---

## Examples

**Bypass for merge conflict:**

```bash
/craft:git:unprotect merge-conflict
# → Branch protection BYPASSED.
# → Branch: dev
# → Reason: merge conflict resolution
# → Scope: Until re-enabled via /craft:git:protect
```

**Interactive bypass:**

```bash
/craft:git:unprotect
# → Prompts: "Why do you need to bypass branch protection?"
# → Options: Merge conflict, CI fix, Maintenance
```

**Check when already bypassed:**

```bash
/craft:git:unprotect
# → Branch protection is already bypassed.
# → Reason: merge conflict resolution
# → Since: 2026-02-07T14:30:00Z
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Bypass created or already active |

---

## See Also

- [/craft:git:protect](protect.md) --- Re-enable branch protection
- [/craft:git:status](status.md) --- Shows protection indicator
- [/craft:check](../check.md) --- Shows branch context section
- [Branch Protection Architecture](../../architecture.md#5-branch-protection-hooks) --- How the hook works
