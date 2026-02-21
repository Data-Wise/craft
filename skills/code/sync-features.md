---
name: sync-features
description: This skill should be used when the user asks to "sync features", "check for new Claude features", "update craft for latest Claude", "what's new in Claude Code", or wants to ensure craft is up-to-date with Claude Code/Desktop capabilities. Chains command-audit, release-watch, and desktop-watch into a prioritized action plan.
---

# Sync Features

Interactive wizard that audits craft's current state, checks for upstream Claude changes, and presents a prioritized list of actions to keep the plugin current.

## When to Use

- User says "sync features", "what's new", "check for updates"
- After a Claude Code release to assess impact on craft
- Periodic maintenance to ensure craft uses latest capabilities
- Before a craft release to verify compatibility

## Prerequisites

- `gh` CLI installed and authenticated (for release-watch)
- Internet access (for desktop-watch web search)

## Sync Pipeline

Execute these steps in order. Show progress between steps.

### Step 1: Command Audit

Run the command audit to assess current craft health:

```bash
bash scripts/command-audit.sh --format json
```

Parse the JSON output and extract:

- `health_score` — overall health
- `errors` — list of frontmatter errors
- `warnings` — list of warnings (deprecated patterns, hardcoded models, orphaned scripts)

Display summary:

```text
┌───────────────────────────────────────────────────────────────┐
│  STEP 1/3: COMMAND AUDIT                                      │
├───────────────────────────────────────────────────────────────┤
│  Health Score: 85/100                                         │
│  Errors: 3 | Warnings: 5 | Files: 106                        │
│                                                               │
│  Top issues:                                                  │
│  - 3 files with invalid frontmatter fields                    │
│  - 2 files with hardcoded model names                         │
│  - 3 orphaned scripts                                         │
└───────────────────────────────────────────────────────────────┘
```

### Step 2: Release Watch

Fetch latest Claude Code releases and identify plugin-relevant changes:

```bash
python3 scripts/release-watch.py --format json --count 3
```

Parse the JSON output and extract:

- `findings` — categorized as NEW / DEPRECATED / BREAKING / FIXED
- `craft_state` — hardcoded models, agent features, hook events
- `action_items` — items needing attention

Display summary:

```text
┌───────────────────────────────────────────────────────────────┐
│  STEP 2/3: RELEASE WATCH                                      │
├───────────────────────────────────────────────────────────────┤
│  Releases checked: 3 (latest: v2.1.50)                        │
│  Plugin-relevant changes: 12                                  │
│                                                               │
│  NEW: 8 | BREAKING: 1 | DEPRECATED: 0 | FIXED: 3             │
│                                                               │
│  Highlights:                                                  │
│  - WorktreeCreate/WorktreeRemove hook events added            │
│  - isolation: worktree support for agents                     │
│  - 9 hardcoded model references in craft                      │
└───────────────────────────────────────────────────────────────┘
```

### Step 3: Desktop Watch (Optional)

Ask the user if they want to include Desktop watch:

```json
{
  "questions": [{
    "question": "Include Claude Desktop release check? (requires web search)",
    "header": "Desktop",
    "multiSelect": false,
    "options": [
      {"label": "Yes", "description": "Search for Claude Desktop updates and integration opportunities"},
      {"label": "Skip", "description": "Only check Claude Code CLI releases"}
    ]
  }]
}
```

If "Yes": Execute the desktop-watch command instructions (WebSearch + WebFetch as defined in the command file). Parse results for integration opportunities.

If "Skip": Move to Step 4.

### Step 4: Merge and Prioritize

Combine all findings into a single prioritized action list. Assign priorities:

| Priority | Criteria |
|----------|----------|
| P0 (Critical) | BREAKING changes, errors in audit |
| P1 (High) | NEW features craft should adopt, deprecated patterns to remove |
| P2 (Medium) | Warnings from audit, FIXED items to verify |
| P3 (Low) | Desktop integration opportunities, suggestions |

### Step 5: Present Interactive Selection

Use AskUserQuestion with multiSelect to let the user choose which items to act on:

```json
{
  "questions": [{
    "question": "Select items to act on now (you can select multiple):",
    "header": "Actions",
    "multiSelect": true,
    "options": [
      {"label": "[P0] Fix breaking change", "description": "v2.1.50 removed X — craft still uses it in Y"},
      {"label": "[P1] Adopt new hook events", "description": "WorktreeCreate/WorktreeRemove now available"},
      {"label": "[P1] Clean hardcoded models", "description": "9 references to specific model names"},
      {"label": "[P2] Fix invalid frontmatter", "description": "3 files with non-schema fields"}
    ]
  }]
}
```

Note: AskUserQuestion supports maximum 4 options. If there are more items, group by priority and present the top 4 most impactful. Mention remaining items in the description of the last option or in a follow-up message.

### Step 6: Execute Selected Actions

For each selected item, take appropriate action:

- **Fix frontmatter**: Run `bash scripts/command-audit.sh --fix`
- **Clean hardcoded models**: Search and replace specific model references with generic patterns
- **Adopt new features**: Create a worktree branch if changes are significant, or apply directly if minor
- **Breaking changes**: Investigate affected files and propose fixes

After each action, report what was done and verify the fix.

### Step 7: Summary Report

Display final summary:

```text
╔═════════════════════════════════════════════════════════════╗
║  SYNC FEATURES — COMPLETE                                   ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║  Actions taken: 3 of 5 selected                             ║
║  Health score: 85 -> 92 (+7)                                ║
║                                                             ║
║  Completed:                                                 ║
║  - Fixed 3 invalid frontmatter fields                       ║
║  - Removed 2 hardcoded model references                     ║
║  - Updated hook event registration                          ║
║                                                             ║
║  Deferred:                                                  ║
║  - Desktop integration (needs separate feature branch)      ║
║  - Breaking change migration (needs testing)                ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
```

## Error Handling

- If `gh` is not available: Skip release-watch, note in output, continue with audit only
- If command-audit fails: Report the error, continue with other steps
- If no action items found: Report "craft is up-to-date" and show health score

## Integration

- `/craft:code:command-audit` — Frontmatter validation (Step 1)
- `/craft:code:release-watch` — Release tracking (Step 2)
- `/craft:code:desktop-watch` — Desktop monitoring (Step 3)
- `/craft:check` — General pre-flight checks
