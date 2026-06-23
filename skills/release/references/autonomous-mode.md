# Autonomous Mode Reference

Full detail for the `--autonomous` / `--auto` flag. Overview table is in `SKILL.md`; this file
covers implementation specifics.

## Table of Contents

- [Autonomous Safety Checks](#autonomous-safety-checks)
- [Autonomous Version Detection](#autonomous-version-detection)
- [Autonomous Admin Override](#autonomous-admin-override)
- [Autonomous Error Recovery](#autonomous-error-recovery)
- [Combining Flags](#combining-flags)

### Autonomous Safety Checks

Before starting, `--autonomous` validates:

- Working tree is clean (no uncommitted changes)
- Current branch is `dev`
- No existing release PR is open

If any check fails, abort with a clear error message. No retries on safety checks.

### Autonomous Version Detection

```bash
# Analyze commits since last release
commits=$(git log $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD --oneline)

# Determine version bump
if echo "$commits" | grep -qi "breaking\|BREAKING"; then
    bump="major"
elif echo "$commits" | grep -q "^.*feat:"; then
    bump="minor"
else
    bump="patch"
fi

# Show decision (but don't ask)
echo "Auto-detected version bump: $bump (from $(echo "$commits" | wc -l | tr -d ' ') commits)"
```

### Autonomous Admin Override

> **WARNING:** This auto-uses `--admin` to bypass branch protection, which skips required status checks. Only use `--autonomous` when CI has already passed on the PR. For safer unattended releases, use `--autonomous --dry-run` first to preview the plan.

When branch protection blocks the merge in Step 7:

1. Log: "**WARNING:** Branch protection blocking merge. Using --admin override."
2. Run: `gh pr merge <number> --merge --admin`
3. Continue pipeline

### Autonomous Error Recovery

On any step failure:

1. Log the error with full output
2. Retry the step once
3. If retry fails, abort with full error report:

```text
┌─────────────────────────────────────────────────────────────┐
│ /release --autonomous ABORTED                                │
├─────────────────────────────────────────────────────────────┤
│ Failed at: Step 7 (Merge Release PR)                        │
│ Error: Branch protection rules not met                      │
│ Retry: Attempted 1 retry, still failing                     │
│ Completed: Steps 1-6                                        │
│ Rollback: PR #71 still open, no release created             │
├─────────────────────────────────────────────────────────────┤
│ Manual fix needed. Resume with: /release (interactive)       │
└─────────────────────────────────────────────────────────────┘
```

### Combining Flags

- `--autonomous --dry-run`: Shows what autonomous mode WOULD do, without executing
- `--autonomous` alone: Full pipeline with no prompts
