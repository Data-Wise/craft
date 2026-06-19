# Tutorial: Guard Suite

A hands-on walkthrough of the two-hook Guard Suite. By the end you will have:

- Installed both guards
- Triggered a YELLOW announcement and a RED confirmation
- Muted a guard for 30 minutes
- Checked guard state
- Applied the `spec` profile for spec-only work
- Run the coverage audit

**Prerequisites:** craft v2.38+ installed, `jq` on your PATH.

---

## Step 1: Install the Guards

The Guard Suite ships as two PreToolUse hooks. The install script registers them in your Claude Code settings and creates the registry file.

```bash
bash scripts/install-guards.sh
```

Expected output:

```
[install-guards] Registering branch-guard.sh as PreToolUse hook... done
[install-guards] Registering no-switch-guard.sh as PreToolUse hook... done
[install-guards] Writing ~/.claude/guards.json... done
[install-guards] jq found at /usr/local/bin/jq
[install-guards] Guard Suite installed. Run /craft:git:guard status to verify.
```

Verify the install:

```
/craft:git:guard status
```

You should see:

```
Guard Suite status:
  🛡️  branch-guard     enabled    (mute_window: 30m)
  🛡️  no-switch-guard  enabled    (mute_window: 30m)
```

Both guards active. You are protected.

---

## Step 2: See the Guards in Action

### Trigger a YELLOW announcement

With a clean working tree, ask Claude to switch to `dev`:

```
switch to dev
```

Claude will run `git switch dev`. Before the switch executes, no-switch-guard fires and emits a YELLOW announcement:

```
[no-switch-guard] Switching to branch 'dev' (clean tree — proceeding)
```

The switch proceeds without confirmation. YELLOW operations are just noted, not blocked. You see the announcement in the model's response and the branch changes normally.

### Trigger a RED confirmation

Now make a small change to any file (so the tree is dirty):

```bash
echo "# temp" >> /tmp/scratch.txt
```

Then ask Claude to switch to `main`:

```
switch to main
```

Claude will attempt `git switch main`. No-switch-guard fires and emits a RED permission prompt:

```
[no-switch-guard] RED: git switch main with dirty working tree.

Reason: switching to a protected branch (main) with uncommitted changes.
This could discard your work or create a confusing stash state.

Allow this operation? (y/N)
```

The switch does not proceed until you answer. Type `N` to cancel. The working tree is unchanged.

---

## Step 3: Mute a Guard

Sometimes you know you'll be switching branches repeatedly and don't want to approve each one. Mute `no-switch-guard` for 30 minutes:

```
/craft:git:guard disable no-switch-guard
```

Wait — "disable" is permanent. For a temporary bypass, use muting via a profile:

```
/craft:git:guard profile yolo
```

This mutes both guards for 30 minutes:

```
[guard] Profile 'yolo' applied: all guards muted for 30m.
  ⚠️  branch-guard     muted 30m
  ⚠️  no-switch-guard  muted 30m
```

Now switch to `main`:

```
switch to main
```

The switch proceeds silently — no announcement, no confirmation. The guard checked the registry, saw `muted_until` is in the future, and returned GREEN immediately.

After your session, the mute expires automatically. No cleanup needed.

---

## Step 4: Check Guard State

At any point, check what is active:

```
/craft:git:guard status
```

Mid-mute output:

```
Guard Suite status:
  ⚠️  branch-guard     muted 22m  (profile: yolo)
  ⚠️  no-switch-guard  muted 22m  (profile: yolo)
```

After expiry:

```
Guard Suite status:
  🛡️  branch-guard     enabled
  🛡️  no-switch-guard  enabled
```

To re-enable guards immediately without waiting for expiry:

```
/craft:git:guard profile focus
```

---

## Step 5: Use Profiles for Spec-Only Work

The `spec` profile is designed for the common pattern of doing spec or doc work on `dev` while needing to freely read branches for context.

Set the spec profile:

```
/craft:git:guard profile spec
```

Output:

```
[guard] Profile 'spec' applied.
  🛡️  branch-guard     enabled
  ⚠️  no-switch-guard  muted 30m
```

`branch-guard` stays active — you are still protected from accidentally committing new code to `dev`. But `no-switch-guard` is muted, so reading `feature/*` branches, checking out old commits, and running `git restore --staged` all proceed without confirmation prompts.

When you are done with spec work, return to full protection:

```
/craft:git:guard profile focus
```

---

## Step 6: Audit Guard Coverage

The `test` action runs a dry-run coverage sweep — it checks that the installed guards correctly handle all known GREEN/YELLOW/RED operations without actually executing them.

```
/craft:git:guard test
```

Expected output:

```
Guard coverage test:
  branch-guard:
    GREEN ops: 5/5 pass
    RED ops: 4/4 pass (block)
  no-switch-guard:
    GREEN ops: 8/8 pass
    YELLOW ops: 3/3 pass
    RED ops: 6/6 pass (4 ask, 2 block)

All guards: 26/26 operations correctly handled.
```

If any operation fails the expected classification, the output shows which command produced an unexpected tier and what the guard emitted. This is useful after upgrading craft or modifying hook scripts.

For a deeper audit that includes guard-suite consistency across the full hook registry, run:

```
/craft:guard-audit
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Check status | `/craft:git:guard status` |
| List all guards | `/craft:git:guard list` |
| Enable all | `/craft:git:guard profile focus` |
| Mute all 30m | `/craft:git:guard profile yolo` |
| Spec mode | `/craft:git:guard profile spec` |
| Re-enable one | `/craft:git:guard enable no-switch-guard` |
| Disable one | `/craft:git:guard disable no-switch-guard` |
| Explain a guard | `/craft:git:guard explain no-switch-guard` |
| Run coverage test | `/craft:git:guard test` |

---

## Troubleshooting

**Guards not firing after install**

Check that the hooks are registered:

```bash
grep -A3 "PreToolUse" ~/.claude/settings.json | grep guard
```

If missing, re-run `bash scripts/install-guards.sh`.

**`jq: command not found` warning**

Install jq:

```bash
brew install jq       # macOS
apt install jq        # Debian/Ubuntu
```

Without jq, the guards fail open (allow all operations). Install jq to get full protection.

**Registry unreadable warning**

Check for JSON syntax errors:

```bash
jq . ~/.claude/guards.json
```

If jq reports an error, the file is corrupt. Reset it:

```bash
bash scripts/install-guards.sh --reset-registry
```

---

## Next Steps

- [Guard Suite Guide](../guide/guard-suite.md) — full reference for all guard behaviors
- [Guard Suite Design](../guide/guard-design.md) — hook internals and architecture
- [Branch Guard Smart Mode](../guide/branch-guard-smart-mode.md) — commit protection on dev/draft
