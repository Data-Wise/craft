---
description: Re-enable branch protection after bypass
category: git
tags: [git, branch-protection]
version: 1.0.0
---

# /craft:git:protect - Re-Enable Branch Protection

Remove the bypass marker and restore branch protection enforcement.

## Usage

```bash
/craft:git:protect
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
    # Auto-detect: main/master = block-all, dev = block-new-code (if dev exists)
    case "$BRANCH" in
        main|master) LEVEL="block-all" ;;
        dev|develop) LEVEL="block-new-code" ;;
        *) LEVEL="" ;;
    esac
fi
```

Output (level detected dynamically):

```
Branch protection is already active. Nothing to do.

Current branch: dev
Protection level: block-new-code (new code files blocked, fixups allowed)
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

For `block-new-code`:

```
  - New code files: BLOCKED
  - Existing file edits: allowed
  - Markdown files: allowed
  - Test files: allowed
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
