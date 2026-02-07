---
description: Enhanced git status with teaching-specific context
category: git
arguments:
  - name: verbose
    description: Show full git status output
    required: false
    default: false
    alias: -v
  - name: compact
    description: Show compact teaching context only
    required: false
    default: false
    alias: -c
---

# /craft:git:status - Enhanced Git Status

Smart git status with teaching mode awareness and visual context.

## Usage

```bash
# Standard status with teaching context
/craft:git:status

# Verbose mode (include full git status)
/craft:git:status --verbose
/craft:git:status -v

# Compact mode (teaching context only)
/craft:git:status --compact
/craft:git:status -c
```

## Teaching Mode Output

When in a teaching project, shows branch status with critical file highlights:

```
┌─────────────────────────────────────────────────┐
│ 📝 TEACHING MODE: DRAFT BRANCH                  │
├─────────────────────────────────────────────────┤
│ Course: STAT 545 - Data Wrangling              │
│ Branch: draft → production                      │
│                                                 │
│ CRITICAL CHANGES:                               │
│ ⚠️  syllabus/index.qmd        +15  -3          │
│ ⚠️  schedule.qmd              +42  -8          │
│ ✓  lectures/week-01.qmd       +120 -0          │
│ ✓  assignments/hw-01.qmd      +85  -0          │
│                                                 │
│ Summary: 8 files, +247 lines, -18 lines        │
│                                                 │
│ 💡 Run /craft:site:publish to merge to prod    │
└─────────────────────────────────────────────────┘
```

## Standard Mode Output

When not in teaching mode, shows clean git status:

```
┌─────────────────────────────────────────────────┐
│ 🌿 GIT STATUS                                   │
├─────────────────────────────────────────────────┤
│ Branch: feature/new-feature                     │
│ Guard: None (feature branches unrestricted)     │
│ Status: 2 commits ahead of origin               │
│                                                 │
│ Changes:                                        │
│   M  src/main.js                                │
│   M  tests/test_main.py                         │
│   ?? new-file.txt                               │
│                                                 │
│ Summary: 3 files changed                        │
└─────────────────────────────────────────────────┘
```

## Implementation

You are a git status assistant with teaching mode awareness.

## Purpose

Provide clear, actionable git status information:

- Show current branch and tracking status
- Highlight uncommitted changes
- Teaching mode: Show draft vs production diff
- Teaching mode: Highlight critical files (syllabus, schedule, assignments)
- Format in ADHD-friendly boxes with visual hierarchy

## When invoked

### Step 1: Basic Git Status Check

```bash
# Get current branch
git branch --show-current

# Get branch tracking status
git status --branch --short

# Check for uncommitted changes
git status --short
```

### Step 2: Teaching Mode Detection

```python
import sys
import os
sys.path.insert(0, os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'utils'))
from detect_teaching_mode import detect_teaching_mode

is_teaching, method = detect_teaching_mode()
```

**If teaching mode detected:** Proceed to Step 3 (Teaching Context)
**If not teaching mode:** Proceed to Step 4 (Standard Status)

### Step 3: Teaching Context (if teaching mode)

```bash
# Determine current branch type
current_branch=$(git branch --show-current)

# Check if on draft or production branch
if [[ "$current_branch" == "draft" ]]; then
    branch_type="DRAFT"
    compare_to="production"
elif [[ "$current_branch" == "production" ]]; then
    branch_type="PRODUCTION"
    compare_to="draft"
else
    # Non-standard branch, show both
    branch_type="OTHER"
    compare_to="production"
fi
```

**Get diff between branches:**

```bash
# Get stat summary
git diff ${compare_to}..${current_branch} --stat 2>/dev/null || echo "No production branch found"

# Parse for critical files
# Critical patterns:
#   - syllabus/*
#   - syllabus.qmd
#   - schedule.qmd
#   - assignments/*
```

**Format teaching context:**

```
┌─────────────────────────────────────────────────┐
│ 📝 TEACHING MODE: ${branch_type} BRANCH         │
├─────────────────────────────────────────────────┤
│ Course: [From teach-config.yml or detect]       │
│ Branch: ${current_branch} → ${compare_to}       │
│                                                 │
│ CRITICAL CHANGES:                               │
│ [List files with ⚠️ for critical, ✓ for normal] │
│                                                 │
│ Summary: X files, +Y lines, -Z lines            │
│                                                 │
│ 💡 Next: [Suggest action based on branch]       │
└─────────────────────────────────────────────────┘
```

**Critical file detection logic:**

```python
def is_critical_file(filepath):
    """Check if file is critical for teaching."""
    critical_patterns = [
        'syllabus/',
        'syllabus.qmd',
        'schedule.qmd',
        'assignments/',
    ]
    return any(pattern in filepath for pattern in critical_patterns)

def format_file_line(filepath, insertions, deletions):
    """Format file change line with icon."""
    icon = "⚠️ " if is_critical_file(filepath) else "✓ "
    return f"{icon} {filepath:30s} +{insertions:>3}  -{deletions:>3}"
```

**Suggestion logic:**

| Branch Type | Suggestion                                           |
| ----------- | ---------------------------------------------------- |
| DRAFT       | "Run /craft:site:publish to merge to production"     |
| PRODUCTION  | "Switch to draft branch to make changes"             |
| OTHER       | "Teaching branches: draft (work), production (live)" |

### Step 4: Standard Git Status (if not teaching mode)

```bash
# Get clean status output
git status --short

# Count changes
modified=$(git status --short | grep '^ M' | wc -l)
added=$(git status --short | grep '^??' | wc -l)
deleted=$(git status --short | grep '^ D' | wc -l)
```

**Format standard status:**

```
┌─────────────────────────────────────────────────┐
│ 🌿 GIT STATUS                                   │
├─────────────────────────────────────────────────┤
│ Branch: ${current_branch}                       │
│ Status: [ahead/behind/synced with origin]       │
│                                                 │
│ Changes:                                        │
│ [List from git status --short]                  │
│                                                 │
│ Summary: X files changed                        │
└─────────────────────────────────────────────────┘
```

### Step 5: Handle Arguments

**If --verbose:**

- Show teaching context (if applicable)
- Add separator
- Show full `git status` output below

**If --compact:**

- Teaching mode: Only show teaching context box
- Standard mode: Only show summary line

### Step 6: Additional Context

**Check for uncommitted changes:**

```
⚠️ You have uncommitted changes
   Run /craft:git:commit or git add/commit
```

**Check for unpushed commits:**

```bash
# Count unpushed commits
ahead=$(git rev-list @{u}..HEAD 2>/dev/null | wc -l)

if [ $ahead -gt 0 ]; then
    echo "📤 ${ahead} commits ahead of origin (not pushed)"
    echo "   Run git push to sync"
fi
```

**Check for unpulled commits:**

```bash
# Count unpulled commits
behind=$(git rev-list HEAD..@{u} 2>/dev/null | wc -l)

if [ $behind -gt 0 ]; then
    echo "📥 ${behind} commits behind origin (not pulled)"
    echo "   Run git pull to update"
fi
```

## Implementation Example

```bash
#!/usr/bin/env bash
set -euo pipefail

# Get current directory
CWD="${PWD}"

# Import teaching mode detection
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-.}"
export PYTHONPATH="${PLUGIN_ROOT}/utils:${PYTHONPATH:-}"

# Detect teaching mode
TEACHING_MODE=$(python3 -c "
from detect_teaching_mode import detect_teaching_mode
is_teaching, method = detect_teaching_mode('${CWD}')
print('true' if is_teaching else 'false')
")

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Box drawing characters
BOX_TOP="┌─────────────────────────────────────────────────┐"
BOX_MID="├─────────────────────────────────────────────────┤"
BOX_BOT="└─────────────────────────────────────────────────┘"

if [ "${TEACHING_MODE}" = "true" ]; then
    # Teaching mode status
    echo "${BOX_TOP}"

    # Determine branch type
    if [ "${CURRENT_BRANCH}" = "draft" ]; then
        echo "│ 📝 TEACHING MODE: DRAFT BRANCH                  │"
        COMPARE_TO="production"
    elif [ "${CURRENT_BRANCH}" = "production" ]; then
        echo "│ 🚀 TEACHING MODE: PRODUCTION BRANCH             │"
        COMPARE_TO="draft"
    else
        echo "│ 📚 TEACHING MODE: ${CURRENT_BRANCH}             │"
        COMPARE_TO="production"
    fi

    echo "${BOX_MID}"

    # Show diff if comparing branches exist
    if git rev-parse --verify "${COMPARE_TO}" >/dev/null 2>&1; then
        # Get diff stats
        DIFF_STAT=$(git diff "${COMPARE_TO}..${CURRENT_BRANCH}" --stat)

        # Parse critical files
        echo "│ Branch: ${CURRENT_BRANCH} → ${COMPARE_TO}"
        echo "│                                                 │"
        echo "│ CRITICAL CHANGES:                               │"

        # Show file changes (simplified for now)
        echo "${DIFF_STAT}" | grep -E "(syllabus|schedule|assignments)" | head -5 || echo "│ (No critical changes detected)                  │"

        echo "│                                                 │"

        # Summary
        FILES_CHANGED=$(echo "${DIFF_STAT}" | tail -1 | grep -oE '[0-9]+ file' | grep -oE '[0-9]+')
        echo "│ Summary: ${FILES_CHANGED} files changed                        │"
    else
        echo "│ Note: ${COMPARE_TO} branch not found               │"
    fi

    echo "${BOX_BOT}"
else
    # Standard git status
    echo "${BOX_TOP}"
    echo "│ 🌿 GIT STATUS                                   │"
    echo "${BOX_MID}"
    echo "│ Branch: ${CURRENT_BRANCH}                       │"

    # Show branch protection status (NEW in v2.16.0)
    PROJECT_ROOT=$(git rev-parse --show-toplevel)
    if [[ -f "$PROJECT_ROOT/.claude/allow-dev-edit" ]]; then
        REASON=$(jq -r '.reason // "unknown"' "$PROJECT_ROOT/.claude/allow-dev-edit" 2>/dev/null || echo "unknown")
        printf "│ Guard: BYPASSED (reason: %-22s │\n" "${REASON})"
    elif [[ -f "$PROJECT_ROOT/.claude/branch-guard.json" ]]; then
        LEVEL=$(jq -r ".\"${CURRENT_BRANCH}\" // empty" "$PROJECT_ROOT/.claude/branch-guard.json" 2>/dev/null)
        if [[ "$LEVEL" == "block-all" ]]; then
            echo "│ Guard: Active (all edits blocked)               │"
        elif [[ "$LEVEL" == "block-new-code" ]]; then
            echo "│ Guard: Active (new code blocked, fixups OK)     │"
        fi
    fi

    # Show changes
    CHANGES=$(git status --short)
    if [ -n "${CHANGES}" ]; then
        echo "│                                                 │"
        echo "│ Changes:                                        │"
        echo "${CHANGES}" | while read -r line; do
            printf "│   %-45s │\n" "${line}"
        done
    else
        echo "│ Status: Clean working tree                     │"
    fi

    echo "${BOX_BOT}"
fi
```

## Key Behaviors

1. **Teaching-aware** - Detects teaching mode automatically
2. **Visual hierarchy** - Box layout with clear sections
3. **Critical file highlighting** - Warns about syllabus/schedule changes
4. **Actionable suggestions** - Shows next step based on context
5. **Compact mode** - Quick status for scripts
6. **Verbose mode** - Full git status when needed

## Integration

### With /craft:site:publish

```bash
/craft:git:status           # Check changes before publish
/craft:site:publish         # Publish to production
```

### With /craft:git:sync

```bash
/craft:git:status           # See current state
/craft:git:sync             # Sync with remote
```

### With /craft:site:build

```bash
/craft:git:status           # Check for uncommitted changes
/craft:site:build           # Build site
```

## See Also

- `/craft:git:branch` - Branch management
- `/craft:git:sync` - Sync with remote
- `/craft:site:publish` - Publish to production
- Utility: `utils/detect_teaching_mode.py`
