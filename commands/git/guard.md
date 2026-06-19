---
description: Manage and inspect craft PreToolUse guards (branch-guard, no-switch-guard)
category: git
arguments:
  - name: action
    description: "Action: list | status | explain | test | enable | disable | profile"
    required: true
  - name: target
    description: "Guard name or number (for enable/disable/explain); profile name (focus|yolo|spec)"
    required: false
  - name: permanent
    description: "Permanent disable (vs 30-min mute)"
    required: false
    default: false
    alias: --permanent
  - name: session
    description: "Session-scoped mute (expires after mute_window_min)"
    required: false
    default: false
    alias: --session
---

# /craft:git:guard - Manage Craft PreToolUse Guards

Inspect, enable, disable, and profile the craft guard suite. Guards live in
`~/.claude/settings.json` as `PreToolUse` hooks; their toggle state is persisted in
`~/.claude/guards.json`.

## Usage

```bash
/craft:git:guard list                          # Numbered table of all guards + state
/craft:git:guard status                        # Like list + metadata + expired-mute sweep
/craft:git:guard explain "git switch main"     # Dry-run a command through both guards
/craft:git:guard test                          # Run guard test suites
/craft:git:guard enable branch-guard           # Re-enable a guard (by name or #)
/craft:git:guard enable 1                      # Same, by number
/craft:git:guard disable no-switch-guard       # 30-min mute (default)
/craft:git:guard disable 2 --permanent         # Permanent disable
/craft:git:guard disable 1 --session           # Session-scoped mute (30 min)
/craft:git:guard profile focus                 # Enable all guards
/craft:git:guard profile yolo                  # Mute all guards 30 min
/craft:git:guard profile spec                  # branch-guard on, no-switch-guard muted
```

## Guard Registry

Guards are numbered alphabetically:

| # | Name | File |
|---|------|------|
| 1 | branch-guard | branch-guard.sh |
| 2 | no-switch-guard | no-switch-guard.sh |

Registry path: `~/.claude/guards.json`

## Execution Behavior (MANDATORY)

### Prerequisite Check

Before any action, verify `jq` is available:

```bash
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required for /craft:git:guard. Install with: brew install jq"
  exit 1
fi

GUARDS_JSON="$HOME/.claude/guards.json"

if [[ ! -f "$GUARDS_JSON" ]]; then
  echo "Error: guards.json not found at $GUARDS_JSON"
  echo "Run install-guards.sh to initialize the registry."
  exit 1
fi
```

### Mute Expiry Check (auto-clear, applies to all actions)

Before displaying state, sweep for expired mutes and clear them:

```bash
now_epoch=$(date -u +%s)

for guard_name in $(jq -r '.guards | keys[]' "$GUARDS_JSON"); do
  muted_until=$(jq -r ".guards[\"$guard_name\"].muted_until // empty" "$GUARDS_JSON")
  if [[ -n "$muted_until" ]]; then
    muted_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$muted_until" +%s 2>/dev/null || \
                  date -d "$muted_until" +%s 2>/dev/null)
    if [[ -n "$muted_epoch" && "$now_epoch" -ge "$muted_epoch" ]]; then
      # Mute expired — clear it
      tmp=$(mktemp)
      jq ".guards[\"$guard_name\"].muted_until = null" "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"
    fi
  fi
done
```

---

## Actions

### `list` — Guard Table

Read `~/.claude/guards.json` and `~/.claude/settings.json` to build a numbered table.
For each guard, derive the matcher from the `hooks` array in settings.json where the hook
script path matches the guard's filename.

**Output:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ Guard Suite                                                         │
├─────────────────────────────────────────────────────────────────────┤
│ #  Name              File               Matcher     State           │
│ ─  ────              ────               ───────     ─────           │
│ 1  branch-guard      branch-guard.sh    Edit|Write  🛡️ enabled      │
│                                         Bash                        │
│ 2  no-switch-guard   no-switch-guard.sh Bash        ⚠️ muted (29m) │
└─────────────────────────────────────────────────────────────────────┘
```

State icons:

- `🛡️ enabled` — guard is active (`enabled: true`, no active mute)
- `⚠️ muted (Nm)` — muted, N minutes remaining until `muted_until`
- `⛔ disabled` — permanently off (`enabled: false`)

**Implementation:**

```python
import json, subprocess, os, re
from datetime import datetime, timezone

guards_path = os.path.expanduser("~/.claude/guards.json")
settings_path = os.path.expanduser("~/.claude/settings.json")

with open(guards_path) as f:
    registry = json.load(f)

# Load matchers from settings.json hooks
matchers = {}
try:
    with open(settings_path) as f:
        settings = json.load(f)
    for hook in settings.get("hooks", {}).get("PreToolUse", []):
        for script in hook.get("hooks", []):
            cmd = script.get("command", "")
            for guard_file in ["branch-guard.sh", "no-switch-guard.sh"]:
                if guard_file in cmd:
                    matchers[guard_file] = hook.get("matcher", "")
except Exception:
    pass

# Guard file mapping (alphabetical = numbered order)
guard_files = {
    "branch-guard": "branch-guard.sh",
    "no-switch-guard": "no-switch-guard.sh",
}

now = datetime.now(timezone.utc)

rows = []
for i, (name, info) in enumerate(sorted(registry["guards"].items()), 1):
    gfile = guard_files.get(name, f"{name}.sh")
    matcher = matchers.get(gfile, "—")
    enabled = info.get("enabled", True)
    muted_until = info.get("muted_until")
    mute_window = info.get("mute_window_min", 30)

    if not enabled:
        state = "⛔ disabled"
    elif muted_until:
        mu = datetime.fromisoformat(muted_until.replace("Z", "+00:00"))
        remaining = int((mu - now).total_seconds() / 60)
        state = f"⚠️  muted ({remaining}m)"
    else:
        state = "🛡️  enabled"

    rows.append((i, name, gfile, matcher, state))
```

---

### `status` — Extended Status

Like `list` but additionally shows:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Guard Suite Status                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ Registry:   ~/.claude/guards.json  (modified: 2026-06-19 14:32 UTC) │
│ Active:     1 of 2 guards enabled                                   │
│ Muted:      1 (no-switch-guard, 29m remaining)                      │
├─────────────────────────────────────────────────────────────────────┤
│ #  Name              File               Matcher     State           │
│ ─  ────              ────               ───────     ─────           │
│ 1  branch-guard      branch-guard.sh    Edit|Write  🛡️ enabled      │
│                                         Bash                        │
│ 2  no-switch-guard   no-switch-guard.sh Bash        ⚠️ muted (29m) │
└─────────────────────────────────────────────────────────────────────┘
```

Auto-clear any expired mutes before computing counts (see Prerequisite Check above).

---

### `explain <cmd>` — Dry-Run

Reason through both guards in sequence against the command text and the current branch.
**Do not actually execute the command or the guard scripts.** Reason about what each guard
would emit based on documented rule logic.

**Guards evaluated in order:**

1. `branch-guard` (Edit|Write|Bash matcher) — checks branch protection, file-edit block, destructive patterns
2. `no-switch-guard` (Bash matcher) — checks switch/worktree/restore patterns, branch destination, tree-dirty state

**Output format:**

```
Dry-run: git switch feature/foo
─────────────────────────────────
branch-guard     [Bash] → ALLOW   (no destructive pattern, not on main)
no-switch-guard  [Bash] → YELLOW  announce (clean-tree switch to existing non-main branch)

Result: ALLOWED with announcement
```

Possible per-guard outcomes:

- `ALLOW` — guard passes silently
- `YELLOW announce` — guard emits a `systemMessage` notification (no block)
- `ASK confirm` — guard emits a `permissionDecision` requiring user confirmation
- `BLOCK` — guard emits exit 2 / stderr (hard deny)
- `SKIP (muted)` — guard is muted or disabled, not evaluated

If a guard is disabled or muted, mark it `SKIP` and note the reason.

**Branch context:** Read `git branch --show-current` and `git status --short` to inform the
dry-run reasoning (dirty tree, on main, etc.).

---

### `test` — Run Guard Test Suites

Run test scripts if they exist, collect pass/fail, show a summary.

```bash
CRAFT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

passed=0
failed=0
missing=0

for script in "tests/test_branch_guard.sh" "tests/test_no_switch_guard.sh"; do
  full="$CRAFT_ROOT/$script"
  if [[ -f "$full" ]]; then
    echo "Running $script..."
    if bash "$full" 2>&1; then
      passed=$((passed + 1))
    else
      failed=$((failed + 1))
    fi
  else
    echo "  (skipped: $script not found)"
    missing=$((missing + 1))
  fi
done

echo ""
echo "Guard tests: ${passed} passed, ${failed} failed, ${missing} missing"
```

**Output:**

```
Running tests/test_branch_guard.sh...
  ✅ 23 assertions passed

Running tests/test_no_switch_guard.sh...
  ✅ 18 assertions passed

Guard tests: 2 passed, 0 failed, 0 missing
```

---

### `enable <name|#>` — Re-Enable a Guard

Resolve name from number if needed (1 = branch-guard, 2 = no-switch-guard, alphabetical).

```bash
# Set enabled: true, clear muted_until
tmp=$(mktemp)
jq ".guards[\"$GUARD_NAME\"].enabled = true | .guards[\"$GUARD_NAME\"].muted_until = null" \
  "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"

echo "✓ $GUARD_NAME enabled"
```

**Output:**

```
✓ branch-guard enabled
```

---

### `disable <name|#> [--permanent] [--session]` — Mute or Disable

**Default (no flags):** 30-min mute. Writes `muted_until = now + mute_window_min`.

```bash
WINDOW=$(jq -r ".guards[\"$GUARD_NAME\"].mute_window_min // 30" "$GUARDS_JSON")

# BSD date (macOS):
UNTIL=$(date -u -v +${WINDOW}M +"%Y-%m-%dT%H:%M:%SZ")
# GNU date (Linux fallback):
# UNTIL=$(date -u -d "+${WINDOW} minutes" +"%Y-%m-%dT%H:%M:%SZ")

tmp=$(mktemp)
jq ".guards[\"$GUARD_NAME\"].muted_until = \"$UNTIL\"" \
  "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"

# Human-readable re-arm time (HH:MM UTC)
REARM=$(date -u -v +${WINDOW}M +"%H:%M")
echo "⚠️  $GUARD_NAME muted for ${WINDOW} min (re-arms at ${REARM} UTC)"
```

**`--permanent`:** Set `enabled: false` instead of writing a mute timestamp.

```bash
tmp=$(mktemp)
jq ".guards[\"$GUARD_NAME\"].enabled = false | .guards[\"$GUARD_NAME\"].muted_until = null" \
  "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"

echo "⛔ $GUARD_NAME permanently disabled (re-enable with: /craft:git:guard enable $GUARD_NAME)"
```

**`--session`:** Same as default mute (30-min window). Label it "session-scoped" in output.

```bash
echo "⚠️  $GUARD_NAME muted for ${WINDOW} min — session-scoped (re-arms at ${REARM} UTC)"
```

---

### `profile <name>` — Apply a Preset

#### `focus` — Enable all guards

```bash
for name in $(jq -r '.guards | keys[]' "$GUARDS_JSON"); do
  tmp=$(mktemp)
  jq ".guards[\"$name\"].enabled = true | .guards[\"$name\"].muted_until = null" \
    "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"
done
echo "🛡️  focus profile applied: all guards enabled"
```

**Output:**

```
🛡️  focus profile applied
  ✓ branch-guard    → enabled
  ✓ no-switch-guard → enabled
```

#### `yolo` — Mute all guards 30 min (NOT permanent)

```bash
for name in $(jq -r '.guards | keys[]' "$GUARDS_JSON"); do
  WINDOW=$(jq -r ".guards[\"$name\"].mute_window_min // 30" "$GUARDS_JSON")
  UNTIL=$(date -u -v +${WINDOW}M +"%Y-%m-%dT%H:%M:%SZ")
  tmp=$(mktemp)
  jq ".guards[\"$name\"].muted_until = \"$UNTIL\"" \
    "$GUARDS_JSON" > "$tmp" && mv "$tmp" "$GUARDS_JSON"
done
```

**Output:**

```
⚠️  yolo profile applied (all guards muted 30 min)
  ⚠️  branch-guard    → muted until 15:02 UTC
  ⚠️  no-switch-guard → muted until 15:02 UTC
```

#### `spec` — Enable branch-guard, mute no-switch-guard 30 min

```bash
# Enable branch-guard
jq '.guards["branch-guard"].enabled = true | .guards["branch-guard"].muted_until = null' ...

# Mute no-switch-guard
UNTIL=$(date -u -v +30M +"%Y-%m-%dT%H:%M:%SZ")
jq ".guards[\"no-switch-guard\"].muted_until = \"$UNTIL\"" ...
```

**Output:**

```
📋 spec profile applied
  ✓ branch-guard    → enabled
  ⚠️  no-switch-guard → muted 30 min (re-arms at 15:02 UTC)
```

---

## Guards.json Schema Reference

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

Fields:

- `enabled` — `false` = permanently disabled; `true` = active (subject to mute check)
- `muted_until` — ISO-8601 UTC timestamp or `null`; if set and in the future, guard is muted
- `mute_window_min` — default mute duration in minutes (used by `disable` and `profile yolo/spec`)

The guards.json file stores **toggle state only**. Guard logic lives in the shell scripts
(`scripts/branch-guard.sh`, `scripts/no-switch-guard.sh`). The scripts read `guards.json` on
each invocation to check whether they are currently enabled/muted.

---

## See Also

- `/craft:git:worktree` — Parallel development with git worktrees
- `/craft:git:protect` — Apply branch protection rules
- `/craft:git:unprotect` — Session-scoped bypass for branch protection
- `docs/guide/guard-suite.md` — Guard suite user guide
