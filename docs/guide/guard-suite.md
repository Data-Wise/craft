# Guard Suite

The Guard Suite is a two-hook safety layer that intercepts destructive git operations before Claude executes them. It replaces the single monolithic `branch-guard.sh` with a purpose-built pair of hooks, a shared registry for enable/disable/muting, and a `/craft:git:guard` command for runtime management.

## Architecture Overview

```
PreToolUse event (Bash tool, git command)
  │
  ├─ branch-guard.sh       ← commit/push protection (exits non-zero)
  │
  └─ no-switch-guard.sh    ← branch-switch / restore protection (emits permissionDecision JSON)
       │
       └─ reads ~/.claude/guards.json   ← registry
```

**Two guards, two jobs:**

| Hook | Protects | Emission mechanism |
|------|----------|--------------------|
| `branch-guard.sh` | Commits to protected branches, force-push, branch deletion | exits non-zero + stderr (`[CONFIRM]` pattern) |
| `no-switch-guard.sh` | `git switch`, `git checkout`, `git restore`, `git worktree add/remove/move` | `permissionDecision` JSON on stdout |

The split matters because the two hook families have different output contracts with the Claude Code runtime. Branch-guard uses the model-mediated confirm pattern (stderr + exit 1); no-switch-guard uses the platform-native permission decision (stdout JSON). Merging them into one script would require picking one contract and losing the other.

---

## Why Two Guards?

`branch-guard.sh` has been the primary safeguard since v2.x. It gates:

- Direct commits to `main` and `dev`
- Force-push and `--delete-branch` operations
- Smart-mode protection (new files on `dev`)

What it did not cleanly own was the _movement_ side: switching branches, checking out, restoring files, and adding/removing worktrees. Those operations were partially handled by duplicate restore/checkout checks inside `branch-guard.sh` that mixed two different emission mechanisms in one file.

The Guard Suite:

1. Removes the duplicate restore/checkout checks from `branch-guard.sh`
2. Moves them to `no-switch-guard.sh`, which uses the correct platform-native emission contract
3. Adds a shared registry so both guards can be muted or disabled independently

---

## The 3-Tier Harm Taxonomy

Every operation the Guard Suite intercepts is classified into one of three tiers. The tier determines what happens next.

### GREEN — Silent Allow

The operation is safe. The guard logs nothing and allows it.

**Examples:**

- `git status`, `git log`, `git diff`, `git show`
- `git fetch`, `git fetch --prune`
- `git restore --staged <file>` (safe unstage — un-stages the file but does not touch working-tree content)
- `git branch -a`, `git remote -v`
- Any non-git command routed through the Bash tool

GREEN operations do not produce any user-visible output from the guard. The session stays quiet.

### YELLOW — Announce

The operation is low-risk but worth noting. The guard announces the action and proceeds.

**Examples:**

- `git switch dev` (clean tree, switching to an existing non-main branch)
- `git checkout feature/my-branch` (clean tree, existing branch)
- `git worktree add <path> feature/new` (creating a worktree for a new feature)

YELLOW announcements look like:

```
[no-switch-guard] Switching to branch 'dev' (clean tree — proceeding)
```

The model sees the announcement and can include it in its response. No confirmation is needed.

### RED — Ask / Block

The operation could cause data loss or irreversible state change. The guard asks for confirmation (or blocks outright when in a protection context).

**Examples:**

- `git switch dev` with uncommitted changes (dirty-tree switch)
- `git checkout -b new-branch` or `git switch -c new-branch` (creating a new branch)
- `git switch main` or `git checkout master` (switching to a protected branch)
- `git worktree remove <path>` or `git worktree move`
- `git restore <file>` without `--staged` (discards working-tree changes — irreversible without stash)

RED triggers a `permissionDecision` prompt (for no-switch-guard) or a `[CONFIRM]` stderr block (for branch-guard). The operation does not proceed until the user explicitly approves.

**Dirty-tree switch example:**

```
[no-switch-guard] RED: git switch main with dirty working tree.
  Uncommitted changes: src/foo.py (+14 / -3)
  Switching to main would discard or stash these changes.
  Allow? (y/N)
```

---

## The Registry (`~/.claude/guards.json`)

Both guards read a shared registry before deciding whether to act.

**Default state (created on first install):**

```json
{
  "guards": {
    "branch-guard": {
      "enabled": true,
      "muted_until": null,
      "mute_window_min": 30
    },
    "no-switch-guard": {
      "enabled": true,
      "muted_until": null,
      "mute_window_min": 30
    }
  }
}
```

### Enabled vs Muted vs Disabled

| State | `enabled` | `muted_until` | Behavior |
|-------|-----------|---------------|----------|
| Active | `true` | `null` | Full protection |
| Muted | `true` | future timestamp | Silently allows everything until expiry |
| Disabled | `false` | any | Permanently off until re-enabled |

**Muting** is a temporary bypass — the guard stays registered and enabled in principle but bypasses all checks until `muted_until` expires. Use muting when you know you'll be making a series of legitimate branch switches and don't want to approve each one.

**Disabling** is a permanent bypass (until you run `/craft:git:guard enable <name>`). Use disabling only when you're doing extended work that genuinely doesn't need protection — not as a lazy alternative to muting.

### Registry Reads and the jq Quirk

Guards read the registry with `jq`. There is a subtle quirk: the `enabled` field is read *without* a `// true` fallback:

```bash
enabled=$(jq -r '.guards["no-switch-guard"].enabled' ~/.claude/guards.json)
```

This is intentional. If the field were missing and the fallback were `true`, a corrupt or partial registry would silently re-enable a guard you intended to disable. Missing fields produce `null`, which is treated as "registry unreadable — fail open" (see Fail-Open Guarantee below).

In jq, `false // true` evaluates to `true` (because `false` is falsy in jq's `//` operator). Do not add a `// true` fallback to the `enabled` read — it would make `"enabled": false` impossible to express.

---

## The `/craft:git:guard` Command

`/craft:git:guard` is the runtime management interface for the Guard Suite. It has 7 actions.

### `list` — Show all guards

```
/craft:git:guard list
```

Prints the current state of every registered guard.

```
Guard Suite status:
  🛡️  branch-guard     enabled    (mute_window: 30m)
  ⚠️  no-switch-guard  muted 18m  (mute_window: 30m)
```

**State icons:**

| Icon | Meaning |
|------|---------|
| 🛡️ | Enabled and active |
| ⚠️ | Muted (shows remaining minutes) |
| ⛔ | Disabled |

### `status` — Summary view

```
/craft:git:guard status
```

Prints a one-line summary per guard, plus the active profile if one is set.

### `explain` — Why a guard fired

```
/craft:git:guard explain no-switch-guard
```

Prints the harm taxonomy for a guard: which operations are GREEN/YELLOW/RED, and why each tier is classified as it is. Useful when you're unsure why a confirmation appeared.

### `test` — Dry-run coverage check

```
/craft:git:guard test
```

Runs a dry-run sweep against known GREEN/YELLOW/RED operations and reports which are correctly handled. Equivalent to `/craft:guard-audit` but scoped to the guard-suite hooks only.

```
Guard coverage test:
  GREEN ops: 8/8 pass
  YELLOW ops: 3/3 pass
  RED ops: 6/6 pass (4 ask, 2 block)
```

### `enable` — Re-enable a disabled guard

```
/craft:git:guard enable no-switch-guard
/craft:git:guard enable branch-guard
/craft:git:guard enable all
```

Sets `enabled: true` and clears `muted_until` in the registry.

### `disable` — Disable a guard (permanent until re-enabled)

```
/craft:git:guard disable no-switch-guard
/craft:git:guard disable branch-guard
/craft:git:guard disable all
```

Sets `enabled: false`. The guard is skipped entirely on every subsequent invocation until you run `enable`.

### `profile` — Apply a named configuration preset

```
/craft:git:guard profile focus
/craft:git:guard profile yolo
/craft:git:guard profile spec
```

Profiles are named registry presets. See the Profiles section below.

---

## Profiles

Profiles let you switch between common guard configurations with a single command instead of enabling/disabling/muting individual guards.

### `focus` — All guards on

```
/craft:git:guard profile focus
```

Sets both guards to `enabled: true, muted_until: null`. Maximum protection. Use when you're in deep implementation work and want every safeguard active.

```
[guard] Profile 'focus' applied: all guards enabled.
  🛡️  branch-guard     enabled
  🛡️  no-switch-guard  enabled
```

### `yolo` — All guards muted for 30 minutes

```
/craft:git:guard profile yolo
```

Mutes both guards for 30 minutes. Use for exploratory sessions where you'll be switching branches, creating branches, and discarding changes frequently and know what you're doing.

```
[guard] Profile 'yolo' applied: all guards muted for 30m.
  ⚠️  branch-guard     muted 30m
  ⚠️  no-switch-guard  muted 30m
```

The mute expires automatically — you don't need to remember to re-enable anything.

### `spec` — branch-guard on, no-switch-guard muted

```
/craft:git:guard profile spec
```

Keeps commit/push protection active but silences the branch-switch guard. Use when doing spec-only work on `dev` where you legitimately need to switch branches to read context but don't want the model asking for approval each time.

```
[guard] Profile 'spec' applied.
  🛡️  branch-guard     enabled
  ⚠️  no-switch-guard  muted 30m
```

**When to use each profile:**

| Profile | Situation |
|---------|-----------|
| `focus` | Deep implementation — maximum protection |
| `yolo` | Exploratory branches, throwaway experiments |
| `spec` | Spec review on dev, need to browse branches freely |

---

## Fail-Open Guarantee

The Guard Suite is designed to never lock you out, even when something goes wrong with the registry or the `jq` binary.

**Fail-open conditions:**

| Condition | Behavior |
|-----------|----------|
| `~/.claude/guards.json` missing | Guard proceeds (allows the operation) |
| `jq` not found on PATH | Guard proceeds |
| Registry is malformed JSON | Guard proceeds |
| `enabled` field is `null` or missing | Guard proceeds |
| `muted_until` field is unparseable | Guard treats it as `null` (not muted) |

Fail-open means a broken registry degrades to "no protection" rather than "locked out." This is intentional: the Guard Suite is a safety aid, not a security boundary. You can always operate normally even if the guards are misbehaving — then fix the registry afterward.

To verify the registry is healthy:

```
/craft:git:guard status
```

If status shows guards as active, the registry is readable. If it shows "registry unreadable," check `~/.claude/guards.json` for syntax errors.

---

## Interaction with Existing Protections

The Guard Suite is additive — it does not replace the session-scoped `/craft:git:unprotect` mechanism.

| Mechanism | Scope | What it gates |
|-----------|-------|---------------|
| `branch-guard.sh` | Per-operation | Commit/push to protected branches |
| `no-switch-guard.sh` | Per-operation | Switch/restore/worktree ops |
| `/craft:git:unprotect` | Session (until reset) | Disables branch-guard for the session |
| `guards.json` mute | Time-boxed (N minutes) | Either or both guards |
| `guards.json` disable | Permanent | Either or both guards |

When `/craft:git:unprotect` is active, branch-guard is bypassed at the hook level. The `guards.json` registry is independent — it affects whether the hook binary runs at all, not what the hook decides when it runs.

---

## Installation

The Guard Suite is installed via:

```bash
bash scripts/install-guards.sh
```

This script:

1. Registers `branch-guard.sh` and `no-switch-guard.sh` as PreToolUse hooks in your Claude Code settings
2. Creates `~/.claude/guards.json` with default values if it doesn't exist
3. Verifies `jq` is available (warns if not, but does not abort)

After installation, run `/craft:git:guard status` to confirm both guards are active.

---

## See Also

- [`/craft:git:unprotect`](../commands/git/unprotect.md) — session-scoped bypass for branch-guard
- [Branch Guard Smart Mode](branch-guard-smart-mode.md) — smart-mode protection for `dev`/`draft` branches
- [`/craft:guard-audit`](../skills/guard-audit/) — audit that guard coverage matches the taxonomy
- [Guard Suite Tutorial](../tutorials/TUTORIAL-guard-suite.md) — hands-on walkthrough
- [Guard Suite Design](guard-design.md) — architecture decisions and hook internals
