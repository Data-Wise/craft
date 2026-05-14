---
description: Re-enable branch protection after bypass, configure protection level
category: git
tags: [git, branch-protection]
arguments:
  - name: level
    description: Set protection level (smart|block-all|block-new-code)
    required: false
  - name: show
    description: Display current protection config without changes
    required: false
    default: false
  - name: reset
    description: Remove branch from config (revert to auto-detect)
    required: false
    default: false
  - name: no-hard-deny
    description: Skip the hard_deny layer detection step (v2.33.0)
    required: false
    default: false
---

# /craft:git:protect - Branch Protection Management

Re-enable branch protection after bypass, or configure protection levels.

## Usage

```bash
/craft:git:protect                  # Re-enable after bypass + offer hard_deny install
/craft:git:protect --show           # Show current config (incl. hard_deny status)
/craft:git:protect --level smart    # Set protection level for current branch
/craft:git:protect --reset          # Remove branch from config (auto-detect)
/craft:git:protect --no-hard-deny   # Skip hard_deny detection (v2.33.0)
```

## Execution Behavior (MANDATORY)

### Step 1: Check Hook and Current Status

```bash
# Verify hook is installed
if [[ ! -f "$HOME/.claude/hooks/branch-guard.sh" ]]; then
    echo "Branch guard hook is not installed."
    echo "Install with: bash scripts/install-branch-guard.sh"
    exit 0
fi

# Check if bypass is active
if [[ ! -f ".claude/allow-dev-edit" ]]; then
    # Protection is already active — detect level
fi
```

If no bypass is active, detect the actual protection level:

```bash
BRANCH=$(git branch --show-current)
CONFIG=".claude/branch-guard.json"

if [[ -f "$CONFIG" ]]; then
    LEVEL=$(jq -r ".\"${BRANCH}\" // empty" "$CONFIG" 2>/dev/null)
else
    # Auto-detect: main/master = block-all, dev = smart (if dev exists)
    case "$BRANCH" in
        main|master) LEVEL="block-all" ;;
        dev|develop) LEVEL="smart" ;;
        *) LEVEL="" ;;
    esac
fi
```

Output (level detected dynamically):

```
Branch protection is already active. Nothing to do.

Current branch: dev
Protection level: smart (3-tier: low=note, medium=confirm, high=block)
```

### Step 1b: Handle --show Flag

If `--show` is provided, display current config and exit:

```
Branch: dev
Protection: smart (auto-detected)
Session confirms: 3 (minimal verbosity)
One-shot pending: no
Bypass: inactive
```

### Step 1c: Handle --level Flag

If `--level` is provided, write to config:

```bash
mkdir -p .claude
# Read existing config or create new
CONFIG_FILE=".claude/branch-guard.json"
if [[ -f "$CONFIG_FILE" ]]; then
    # Update existing config
    jq --arg branch "$BRANCH" --arg level "$LEVEL" '.[$branch] = $level' "$CONFIG_FILE" > tmp && mv tmp "$CONFIG_FILE"
else
    # Create new config
    echo "{\"$BRANCH\": \"$LEVEL\"}" | jq . > "$CONFIG_FILE"
fi
```

Output:

```
Protection level set for dev: smart
Config: .claude/branch-guard.json
```

### Step 1d: Handle --reset Flag

If `--reset` is provided, remove branch entry from config:

```bash
jq --arg branch "$BRANCH" 'del(.[$branch])' "$CONFIG_FILE" > tmp && mv tmp "$CONFIG_FILE"
```

Output:

```
Removed dev from branch-guard.json (will use auto-detect)
Auto-detect level: smart
```

### Step 2: Remove Bypass Marker

```bash
rm -f .claude/allow-dev-edit
```

### Step 2b: Hard_deny Layer Detection (NEW in v2.33.0)

Skip this step entirely when `--no-hard-deny` was passed.

**Precondition:** if `~/.claude/.craft-hard-deny-declined` exists, the user previously chose "Never offer again". Skip the offer silently and report `Hard_deny: declined` in Step 3. Do not run the check pass below.

```bash
[[ -f "$HOME/.claude/.craft-hard-deny-declined" ]] && skip Step 2b offer
```

The hard_deny layer is a third tier of unconditional protection enforced by the Claude Code auto-mode classifier. It blocks catastrophic operations (force-push to main, recursive deletion of `.git`, GitHub repo deletion, recursive deletion of `~/.claude`) regardless of `.claude/allow-once`, `.claude/allow-dev-edit`, or any user intent. See `scripts/hard-deny-rules.json` for the canonical catalog and rationale per rule.

Run a check pass against `~/.claude/settings.json`:

```bash
bash scripts/install-hard-deny.sh --check --json
```

The script emits a JSON report on stdout (`would_add`, `craft_rules_already_present`, `defaults_present`) plus a human-readable summary on stderr. Interpretation:

- **`would_add == []`** — already installed. Show one line acknowledging it, continue.
- **`would_add` non-empty** — offer to install. Show a preview of each rule that will be added (truncate at ~80 chars per line for readability), then `AskUserQuestion` with three options: "Yes — install", "Skip this time", "Never offer again". The "Never" option writes a marker (`~/.claude/.craft-hard-deny-declined`) that future `/craft:git:protect` invocations honor (see precondition above). To re-enable the offer after declining, delete the marker: `rm ~/.claude/.craft-hard-deny-declined`.

On "Yes":

```bash
bash scripts/install-hard-deny.sh --install
```

The installer atomically writes `~/.claude/settings.json`, prepending `"$defaults"` if absent and merging craft's rules without duplicating entries or overwriting unrelated top-level settings keys.

### Step 3: Confirm

Detect current protection level (same logic as Step 1), then show:

```
Branch protection RE-ENABLED.

Branch: <current-branch>
Protection: <detected-level>
Hard_deny: <installed | declined | not-applicable>
```

For `smart`:

```
  - LOW risk (existing edits, markdown, tests): allowed with note
  - MEDIUM risk (new code, destructive commands, secrets): confirm required
  - HIGH risk (repository deletion): hard block
  - Session counter: fades verbosity (full → brief → minimal)
```

For `block-all`:

```
  - All edits: BLOCKED
  - All writes: BLOCKED
  - Git commit/push: BLOCKED
```

## Key Behaviors

1. **Idempotent** - safe to run multiple times (hard_deny installer is also idempotent — re-running is a no-op once installed)
2. **Informative** - shows current protection level + hard_deny status after re-enabling
3. **Immediate** - takes effect on the next Edit/Write/Bash tool call
4. **Non-destructive to user settings** - the hard_deny installer never overwrites or drops user-added rules; it only appends craft's catalog and ensures `"$defaults"` is the first entry

## See Also

- `/craft:git:protect-baseline` - Apply GitHub-side branch protection (PR required, no force-push, no delete) to any repo. Companion to this command — `/craft:git:protect` manages the local hook, `protect-baseline` manages GitHub-side rules.
- `/craft:git:unprotect` - Bypass branch protection
- `/craft:git:status` - Shows protection indicator
