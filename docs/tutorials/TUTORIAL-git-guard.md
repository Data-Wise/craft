# Tutorial: git:guard — Inspect and Manage Craft Guards

By the end of this tutorial you will have:

- Listed all guards and their current state
- Muted a guard temporarily
- Applied a profile for a specific workflow
- Re-enabled a guard after muting

**Prerequisites:** craft v2.38+ installed, `jq` on your PATH.

---

## Step 1: See Guard State

```
/craft:git:guard list
```

Expected output:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Guard Suite                                                         │
├─────────────────────────────────────────────────────────────────────┤
│ #  Name              File               Matcher     State           │
│ 1  branch-guard      branch-guard.sh    Edit|Write  🛡️ enabled      │
│                                         Bash                        │
│ 2  no-switch-guard   no-switch-guard.sh Bash        🛡️ enabled      │
└─────────────────────────────────────────────────────────────────────┘
```

Both guards enabled means full branch protection is active.

---

## Step 2: Check Detailed Status

```
/craft:git:guard status
```

Adds metadata: registry file path, modification time, expired-mute sweep. Any mutes that timed out are auto-cleared before display.

---

## Step 3: Mute a Guard for 30 Minutes

If you need to do exploratory work without the switch guard interrupting:

```
/craft:git:guard disable no-switch-guard
```

Output:

```
⚠️  no-switch-guard muted for 30 min (re-arms at 15:32 UTC)
```

The guard auto-re-enables after 30 minutes — no cleanup needed.

---

## Step 4: Apply a Profile

**Spec mode** (branch-guard on, no-switch-guard muted):

```
/craft:git:guard profile spec
```

**Focus mode** (all guards enabled):

```
/craft:git:guard profile focus
```

**Yolo mode** (all guards muted 30 min — use carefully):

```
/craft:git:guard profile yolo
```

---

## Step 5: Re-Enable a Guard

After manual muting, re-enable immediately:

```
/craft:git:guard enable no-switch-guard
```

Or by number:

```
/craft:git:guard enable 2
```

---

## Step 6: Dry-Run a Command Against the Guards

Check what the guards would do to a specific command without executing it:

```
/craft:git:guard explain "git switch main"
```

Output:

```
Dry-run: git switch main
─────────────────────────────
branch-guard     [Bash] → BLOCK   (switching to protected branch main)
no-switch-guard  [Bash] → BLOCK   (switch to main from non-main branch)

Result: BLOCKED
```

---

## What's Next

- See [TUTORIAL-guard-suite.md](TUTORIAL-guard-suite.md) for the full guard installation walkthrough
- Use `/craft:git:guard test` to run the guard test suites after any hook changes
- See `docs/guide/guard-suite.md` for guard architecture details
