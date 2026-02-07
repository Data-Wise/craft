# /craft:git:protect

> **Re-enable branch protection after a temporary bypass**

---

## Synopsis

```bash
/craft:git:protect
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

## Protection Levels

| Level | Branches | Blocks | Allows |
|-------|----------|--------|--------|
| `block-all` | main, master | All writes, edits, git commits | Read-only operations |
| `block-new-code` | dev, develop | New `.py`, `.sh`, `.js`, `.ts`, `.json`, `.yml` files | Existing file edits, docs, specs, tests |

Protection level is determined by `.claude/branch-guard.json` if present, otherwise auto-detected from the branch name.

---

## Examples

**Re-enable after merge conflict resolution:**

```bash
# After resolving conflicts with protection bypassed
/craft:git:protect
# → Branch protection RE-ENABLED.
# → Branch: dev
# → Protection: block-new-code
```

**Check status when already protected:**

```bash
/craft:git:protect
# → Branch protection is already active. Nothing to do.
# → Current branch: dev
# → Protection level: block-new-code
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
- [Branch Protection Architecture](../../architecture.md#5-branch-protection-hooks) --- How the hook works
