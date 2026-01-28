# Dry-Run Implementation Pattern

This template shows how to add `--dry-run` / `-n` support to craft commands.

## Overview

The dry-run feature provides users with a preview of what a command will do before executing it. This builds trust in automation and prevents accidental destructive operations.

**Key Principles:**

- High-level summary (not verbose shell commands)
- Consistent bordered box format
- Clear warnings for uncertain operations
- Exit code 0 (standard for preview modes)

## Command Frontmatter

Add the `--dry-run` argument to your command's YAML frontmatter:

```yaml
---
description: [Your command description]
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
  # ... other arguments ...
---
```

## Implementation Pattern

### 1. Import the Utility

```python
from utils.dry_run_output import render_dry_run_preview, RiskLevel
```

### 2. Check for Dry-Run Flag

Early in your command logic, check if `--dry-run` was passed:

```python
# Parse arguments
dry_run = "--dry-run" in arguments or "-n" in arguments

if dry_run:
    # Generate and display preview
    preview = generate_dry_run_preview()
    print(preview)
    return  # Exit without executing
```

### 3. Generate the Preview

Create a function that analyzes what the command would do:

```python
def generate_dry_run_preview():
    """
    Analyze the current state and generate a preview of operations.

    Returns:
        str: Formatted dry-run output
    """
    # 1. Analyze current state (read files, git status, etc.)
    # 2. Determine what operations would be performed
    # 3. Identify any warnings or edge cases

    actions = []
    warnings = []

    # Example: Analyze branches
    merged_branches = get_merged_branches()  # Read-only check

    if merged_branches:
        actions.append(f"✓ Delete {len(merged_branches)} local branches:")
        for branch in merged_branches:
            actions.append(f"  - {branch}")
    else:
        actions.append("⊘ No merged branches found")

    # Check for edge cases
    branches_with_changes = check_uncommitted_changes()
    if branches_with_changes:
        warnings.append(f"{len(branches_with_changes)} branches have uncommitted changes")

    # Generate preview using utility
    return render_dry_run_preview(
        command_name="Your Command Name",
        actions=actions,
        warnings=warnings if warnings else None,
        summary=f"{len(merged_branches)} branches to delete",
        risk_level=RiskLevel.HIGH  # Adjust based on operation
    )
```

### 4. Risk Levels

Choose the appropriate risk level:

- `RiskLevel.LOW` - Read-only or trivial changes
- `RiskLevel.MEDIUM` - Creates/modifies files (reversible)
- `RiskLevel.HIGH` - Modifies git history, updates remote
- `RiskLevel.CRITICAL` - Deletes data, publishes to external services

## Complete Example: Git Clean

```markdown
---
description: Clean up merged branches safely
category: git
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
---

# Git Clean - Remove merged branches

This command safely removes branches that have been merged.

## Implementation

\```python
#!/usr/bin/env python3
import subprocess
import sys
from utils.dry_run_output import render_dry_run_preview, RiskLevel

def get_merged_branches():
    """Get list of merged branches (read-only)"""
    result = subprocess.run(
        ["git", "branch", "--merged"],
        capture_output=True,
        text=True
    )
    branches = [b.strip() for b in result.stdout.split("\n") if b.strip()]
    # Filter out protected branches
    protected = ["main", "master", "dev", "develop"]
    return [b for b in branches if b not in protected and not b.startswith("*")]

def check_uncommitted_changes(branches):
    """Check if branches have uncommitted changes"""
    branches_with_changes = []
    for branch in branches:
        result = subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD", "--"],
            capture_output=True
        )
        if result.returncode != 0:
            branches_with_changes.append(branch)
    return branches_with_changes

def generate_dry_run_preview():
    """Generate preview of branch deletion"""
    merged_branches = get_merged_branches()
    branches_with_changes = check_uncommitted_changes(merged_branches)

    actions = []
    warnings = []

    # Branches to delete
    branches_to_delete = [b for b in merged_branches if b not in branches_with_changes]
    if branches_to_delete:
        actions.append(f"✓ Delete {len(branches_to_delete)} local branches:")
        for branch in branches_to_delete[:5]:  # Show first 5
            actions.append(f"  - {branch}")
        if len(branches_to_delete) > 5:
            actions.append(f"  ... and {len(branches_to_delete) - 5} more")

    # Skipped branches
    if branches_with_changes:
        actions.append("")
        actions.append(f"⊘ Skip {len(branches_with_changes)} branches with uncommitted changes:")
        for branch in branches_with_changes:
            actions.append(f"  - {branch}")
            warnings.append(f"Branch {branch} has uncommitted changes")

    if not merged_branches:
        actions.append("⊘ No merged branches found")

    return render_dry_run_preview(
        command_name="Clean Merged Branches",
        actions=actions,
        warnings=warnings if warnings else None,
        summary=f"{len(branches_to_delete)} branches to delete, {len(branches_with_changes)} skipped",
        risk_level=RiskLevel.CRITICAL
    )

def main():
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        preview = generate_dry_run_preview()
        print(preview)
        return

    # Normal execution
    # ... delete branches ...

if __name__ == "__main__":
    main()
\```
```

## Testing Checklist

After implementing dry-run:

- [ ] Preview shows correct operations
- [ ] No side effects during dry-run (no files changed, no API calls)
- [ ] Warnings appear for edge cases
- [ ] Summary is accurate
- [ ] Exit code is 0
- [ ] `-n` alias works
- [ ] Actual execution matches preview

## Common Patterns

### Pattern 1: File Creation

```python
actions = [
    f"✓ Create {filename} (~{line_count} lines)",
    "",
    "Content:",
    f"  - {section1_description}",
    f"  - {section2_description}"
]
```

### Pattern 2: File Modification

```python
actions = [
    f"✓ Modify {filename}:",
    f"  - Update {field_name} to {new_value}",
    f"  - Add {new_section}",
    f"  - Remove {old_section}"
]
```

### Pattern 3: External Service

```python
actions = [
    f"✓ Publish to {service_name}:",
    f"  - Package: {package_name}",
    f"  - Version: {version}",
    f"  - Target: {target_url}"
]
warnings = [
    "This operation is irreversible",
    "Publishing will make package public"
]
```

### Pattern 4: Read-Only Command

```python
# For commands that don't modify state
from utils.dry_run_output import render_simple_preview

preview = render_simple_preview(
    "Command Name",
    "This command only reads data and displays information. No changes will be made."
)
```

## Best Practices

### DO

✅ Use high-level descriptions (not shell commands)
✅ Show 3-7 key operations
✅ Include warnings for uncertain operations
✅ Use bullet points and indentation
✅ Keep summary concise and informative
✅ Test that dry-run matches actual execution

### DON'T

❌ Show verbose shell output
❌ List every single operation
❌ Make any changes during dry-run
❌ Call external APIs during dry-run
❌ Prompt for user input during dry-run
❌ Exit with non-zero code

## See Also

- Specification: `docs/specs/SPEC-dry-run-feature-2026-01-15.md`
- Utility: `utils/dry_run_output.py`
- Examples: `commands/git/clean.md`, `commands/ci/generate.md`

## Questions?

If you're unsure how to implement dry-run for your command:

1. Check the specification for guidance
2. Look at similar commands for patterns
3. Start with `render_simple_preview()` for read-only commands
4. Use `render_dry_run_preview()` for operations with side effects
