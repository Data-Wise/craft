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

### Step 1: Check Current Status

```bash
# Check if bypass is active
if [[ ! -f ".claude/allow-dev-edit" ]]; then
    # Protection is already active
fi
```

If no bypass is active:

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

```
Branch protection RE-ENABLED.

Branch: dev
Protection: block-new-code
  - New code files: BLOCKED
  - Existing file edits: allowed
  - Markdown files: allowed
  - Test files: allowed
```

## Key Behaviors

1. **Idempotent** - safe to run multiple times
2. **Informative** - shows current protection level after re-enabling
3. **Immediate** - takes effect on the next Edit/Write/Bash tool call

## See Also

- `/craft:git:unprotect` - Bypass branch protection
- `/craft:git:status` - Shows protection indicator
