# /craft:git:guard

> **Manage the guard suite — view state, enable, disable, mute, and apply profiles**

---

## Synopsis

```bash
/craft:git:guard list                        # Show all guards + state icons
/craft:git:guard status                      # One-line guard health summary
/craft:git:guard enable <guard>              # Re-enable a permanently disabled guard
/craft:git:guard disable <guard>             # Mute guard for default window (30 min)
/craft:git:guard disable <guard> <minutes>   # Mute for N minutes
/craft:git:guard profile <name>              # Apply a preset configuration
/craft:git:guard explain                     # Show harm taxonomy and guard logic
/craft:git:guard test                        # Run guard self-tests
```

---

## Description

`/craft:git:guard` is the control panel for the craft **Guard Suite** — two PreToolUse hooks that protect against accidental destructive git operations:

| Hook | Protects Against |
|------|-----------------|
| `branch-guard` | Commits/pushes to protected branches; new code files on dev |
| `no-switch-guard` | Dirty-tree switches; destructive restore; switch to main |

Both hooks read `~/.claude/guards.json` to determine their enabled/muted state. `disable` sets a `muted_until` timestamp (temporary); `enable`/`disable` without a window permanently toggles the `enabled` flag.

---

## Actions

### `list`

Display all registered guards with their current state:

```
Guard Suite Status
──────────────────────────────────────
🛡️  branch-guard     enabled
🛡️  no-switch-guard  enabled
──────────────────────────────────────
Registry: ~/.claude/guards.json
```

State icons: 🛡️ enabled · ⚠️ muted (Nm remaining) · ⛔ disabled

### `status`

One-line summary suitable for dashboards:

```
Guards: branch-guard 🛡️  no-switch-guard 🛡️
```

### `enable <guard>`

Re-enable a guard that was permanently disabled:

```bash
/craft:git:guard enable no-switch-guard
# → no-switch-guard ENABLED
```

This sets `"enabled": true` in `~/.claude/guards.json`. Does not affect a currently-muted guard (muted guards are already "enabled" — just temporarily silent).

### `disable <guard> [minutes]`

Mute a guard for a time window. Default window: 30 minutes.

```bash
/craft:git:guard disable no-switch-guard        # mute for 30 min
/craft:git:guard disable no-switch-guard 60     # mute for 60 min
/craft:git:guard disable branch-guard           # mute for 30 min
```

Sets `muted_until` to a UTC timestamp. The guard remains "enabled" — it will resume automatically when the window expires. To permanently disable, omit the window argument and use `--permanent`:

```bash
/craft:git:guard disable no-switch-guard --permanent
# → no-switch-guard DISABLED (permanent — use 'enable' to re-activate)
```

### `profile <name>`

Apply a named preset that configures all guards at once:

| Profile | branch-guard | no-switch-guard | Use when |
|---------|-------------|-----------------|----------|
| `focus` | 🛡️ enabled | 🛡️ enabled | Normal dev work |
| `spec` | 🛡️ enabled | ⚠️ muted 30m | Writing specs/docs on dev |
| `yolo` | ⚠️ muted 30m | ⚠️ muted 30m | Rapid iteration (bulk moves) |

```bash
/craft:git:guard profile spec
# → branch-guard: enabled
# → no-switch-guard: muted for 30 min
```

### `explain`

Show the harm taxonomy and what each guard intercepts:

```
Guard Suite Harm Taxonomy
──────────────────────────────────────────────────────
GREEN  Silent allow — read-only ops, git fetch,
       git restore --staged, non-git commands
YELLOW Allow + announce — clean-tree switch to existing
       non-main branch; git worktree add
RED    Ask / block — dirty-tree switch; new-branch
       creation; switch to main/master; git worktree
       remove/move; bare git restore (discards work)
──────────────────────────────────────────────────────
branch-guard handles: commit/push to protected branches,
       new code files on dev, force-push, rm -rf .git
no-switch-guard handles: branch-switch operations,
       destructive restore, worktree lifecycle ops
```

### `test`

Run the guard test suites and report results:

```bash
/craft:git:guard test
# → Running: bash tests/test_no_switch_guard.sh
# → Running: bash tests/test_branch_guard.sh
# → no-switch-guard: 26/26 PASS
# → branch-guard:    99/99 PASS
```

---

## Registry

The guards registry lives at `~/.claude/guards.json`:

```json
{
  "guards": {
    "branch-guard":    { "enabled": true, "muted_until": null, "mute_window_min": 30 },
    "no-switch-guard": { "enabled": true, "muted_until": null, "mute_window_min": 30 }
  }
}
```

**Fail-open guarantee**: if the file is missing, malformed, or `jq` is unavailable, both guards proceed with their default behavior (no lockout).

---

## Examples

**Check guard state before a large refactor:**

```bash
/craft:git:guard status
# Guards: branch-guard 🛡️  no-switch-guard 🛡️
```

**Mute no-switch-guard when doing spec-only work on dev:**

```bash
/craft:git:guard profile spec
# → branch-guard: enabled (commits/pushes still protected)
# → no-switch-guard: muted for 30 min (switch freely)
```

**Restore full protection after the spec work:**

```bash
/craft:git:guard profile focus
# → branch-guard: enabled
# → no-switch-guard: enabled
```

**Temporarily mute branch-guard during a migration (1 hour):**

```bash
/craft:git:guard disable branch-guard 60
# → branch-guard muted until 14:30 UTC (60 min)
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Action completed successfully |
| 1 | Unknown guard name or invalid action |

---

## See Also

- [Guard Suite Guide](../../guide/guard-suite.md) — full user guide
- [Guard Suite Design](../../guide/guard-design.md) — architecture and design decisions
- [Guard Suite Tutorial](../../tutorials/TUTORIAL-guard-suite.md) — hands-on walkthrough
- [/craft:git:unprotect](unprotect.md) — session-scoped branch-guard bypass
- [/craft:git:protect](protect.md) — re-enable branch protection
- [Branch Guard Smart Mode](../../guide/branch-guard-smart-mode.md) — branch-guard deep dive
