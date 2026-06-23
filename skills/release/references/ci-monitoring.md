# CI Monitoring Reference

Detailed implementation for Step 6.5: CI Monitoring.

## Overview

After creating the PR (Step 5) but before merging (Step 7), monitor CI status and auto-fix safe failures.

**Script:** `scripts/ci-monitor.sh`

```bash
# Poll CI status for the release PR
bash scripts/ci-monitor.sh <pr-number>
```

## Behavior

1. Poll `gh run list` every 30s (configurable via `.claude/release-config.json`)
2. On **success**: proceed to Step 7 (merge)
3. On **failure**: diagnose, categorize, and attempt fix
4. Max 3 retry cycles before reporting to user

## Auto-Fix Categories

**Applied without asking:**

| Category | Fix Strategy |
|----------|-------------|
| `version_mismatch` | Run `scripts/version-sync.sh --fix`, update files, commit + push |
| `lint_failure` | Run linter with `--fix` flag, commit + push |
| `changelog_format` | Reformat CHANGELOG entries, commit + push |

**Ask-before-fix categories (require user approval):**

| Category | Why |
|----------|-----|
| `test_failure` | May indicate real bugs, not just formatting |
| `security_audit` | Vulnerability fixes need careful review |
| `build_failure` | Root cause may be complex |

## Configuration

`.claude/release-config.json`

```json
{
    "ci_timeout": 600,
    "ci_poll_interval": 30,
    "ci_max_retries": 3,
    "ci_auto_fix_categories": ["version_mismatch", "lint_failure", "changelog_format"],
    "ci_ask_before_fix": ["test_failure", "security_audit", "build_failure"]
}
```

## Output Format

```
┌─────────────────────────────────────────────────────────────┐
│ Step 6.5: CI Monitoring                                     │
├─────────────────────────────────────────────────────────────┤
│ Polling CI status for PR #85...                             │
│                                                             │
│ [Poll 1] ⏳ In progress (30s elapsed)                       │
│ [Poll 2] ⏳ In progress (60s elapsed)                       │
│ [Poll 3] ✅ All checks passed (90s elapsed)                  │
│                                                             │
│ Proceeding to Step 7: Merge PR                              │
└─────────────────────────────────────────────────────────────┘
```

## Autonomous Mode

Auto-fixes are applied without prompts. Ask-before-fix categories abort with a report.

## Timeout Behavior

If CI doesn't complete within `ci_timeout` seconds, report to user and ask whether to wait longer or merge with `--admin`.
