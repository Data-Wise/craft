---
description: Re-enable branch protection after bypass, configure protection level
category: git
tags: [git, branch-protection]
version: 2.0.0
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
---

# /craft:git:protect - Branch Protection Management

Re-enable branch protection after bypass, or configure protection levels.

## Usage

```bash
/craft:git:protect                  # Re-enable after bypass
/craft:git:protect --show           # Show current config
/craft:git:protect --level smart    # Set protection level for current branch
/craft:git:protect --reset          # Remove branch from config (auto-detect)
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

### Step 3: Confirm

Detect current protection level (same logic as Step 1), then show:

```
Branch protection RE-ENABLED.

Branch: <current-branch>
Protection: <detected-level>
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

1. **Idempotent** - safe to run multiple times
2. **Informative** - shows current protection level after re-enabling
3. **Immediate** - takes effect on the next Edit/Write/Bash tool call

## See Also

- `/craft:git:unprotect` - Bypass branch protection
- `/craft:git:status` - Shows protection indicator
