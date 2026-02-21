---
description: Session-scoped bypass for branch protection with reason logging
category: git
arguments:
  - name: reason
    description: Reason for bypassing protection (merge-conflict|ci-fix|maintenance)
    required: false
tags: [git, branch-protection, bypass]
---

# /craft:git:unprotect - Bypass Branch Protection

Temporarily disable branch protection. The bypass persists until re-enabled with `/craft:git:protect`.

## Usage

```bash
# Interactive (asks for reason)
/craft:git:unprotect

# With reason
/craft:git:unprotect merge-conflict
/craft:git:unprotect ci-fix
/craft:git:unprotect maintenance
```

## Execution Behavior (MANDATORY)

### Step 1: Check Current Protection Status

```bash
# Get current branch
git branch --show-current

# Check if already bypassed
if [[ -f ".claude/allow-dev-edit" ]]; then
    # Show current bypass info and exit
fi
```

If already bypassed, show status and exit:

```
Branch protection is already bypassed.

Reason: merge conflict resolution
Since: 2026-02-06T18:30:00Z

To re-enable: /craft:git:protect
```

### Step 2: Ask for Reason (if not provided)

If no reason argument was given:

```json
{
  "questions": [{
    "question": "Why do you need to bypass branch protection?",
    "header": "Reason",
    "multiSelect": false,
    "options": [
      {
        "label": "Merge conflict resolution",
        "description": "Need to edit code files to resolve merge conflicts on dev."
      },
      {
        "label": "CI fix",
        "description": "Need to fix CI/CD configuration or test files directly."
      },
      {
        "label": "Maintenance",
        "description": "General maintenance task that requires direct edits."
      }
    ]
  }]
}
```

### Step 3: Create Bypass Marker

```bash
mkdir -p .claude

cat > .claude/allow-dev-edit << 'MARKER'
{
  "reason": "<selected-reason>",
  "timestamp": "<ISO-8601>",
  "branch": "<current-branch>"
}
MARKER
```

### Step 4: Confirm

```
Branch protection BYPASSED.

Branch: dev
Reason: merge conflict resolution
Scope: Until re-enabled via /craft:git:protect

To re-enable manually: /craft:git:protect
```

## Key Behaviors

1. **Marker-based** - bypass marker (`.claude/allow-dev-edit`) is checked by branch-guard.sh hook
2. **Reason-logged** - always records why protection was bypassed
3. **Persists until re-enabled** - run `/craft:git:protect` to remove the marker
4. **Idempotent** - running twice shows current status, doesn't create duplicate

## Relationship to One-Shot Approval

The branch guard supports two bypass mechanisms:

| Mechanism | Scope | Duration | Use Case |
|-----------|-------|----------|----------|
| `/craft:git:unprotect` | All actions | Until `/craft:git:protect` | Bulk maintenance, merge conflicts |
| One-shot marker | Single action | Consumed after one use | Quick one-off confirm from Claude |

- **One-shot** (`.claude/allow-once`): Created by Claude after user confirms a `[CONFIRM]` prompt. Auto-consumed on next tool call. No user action needed.
- **Unprotect** (`.claude/allow-dev-edit`): Session-wide bypass. User must explicitly re-enable with `/craft:git:protect`.

Use `/craft:git:unprotect` when you need to do multiple protected operations (e.g., merge conflict resolution). For single operations, just confirm the `[CONFIRM]` prompt — the one-shot marker handles it automatically.

## See Also

- `/craft:git:protect` - Re-enable branch protection, configure levels
- `/craft:git:status` - Shows protection indicator + session counter
- `/craft:check` - Shows branch context section
