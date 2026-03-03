---
name: sync-features
description: This skill should be used when the user asks to "sync features", "check for new Claude features", "update craft for latest Claude", "what's new in Claude Code", or wants to ensure craft is up-to-date with Claude Code/Desktop capabilities. Chains command-audit and unified release-watch into a prioritized action plan.
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

### Step 2: Unified Release Watch

Fetch Code + Desktop releases using the unified release-watch tool:

```bash
python3 scripts/release-watch.py --format json --count 3
```

This single command now covers both Code and Desktop. Parse the JSON v2 output:

- `findings` — Code findings categorized as NEW / DEPRECATED / BREAKING / FIXED
- `desktop.findings` — Desktop findings (same categories)
- `craft_state` — hardcoded models, agent features, hook events
- `action_items` — items needing attention

Display summary:

```text
┌───────────────────────────────────────────────────────────────┐
│  STEP 2/2: UNIFIED RELEASE WATCH                              │
├───────────────────────────────────────────────────────────────┤
│  Code: 3 releases (latest: v2.1.59)                           │
│  Desktop: 20 entries (latest: February 25, 2026)              │
│                                                               │
│  Code: NEW 4 | BREAKING 0 | DEPRECATED 0 | FIXED 2           │
│  Desktop: NEW 12 | BREAKING 1 | DEPRECATED 0 | FIXED 1       │
│                                                               │
│  Highlights:                                                  │
│  - Cowork plugins and admin controls                          │
│  - 11 hardcoded model references in craft                     │
└───────────────────────────────────────────────────────────────┘
```

### Step 3: Merge and Prioritize

Combine all findings into a single prioritized action list. Assign priorities:

| Priority | Criteria |
|----------|----------|
| P0 (Critical) | BREAKING changes, errors in audit |
| P1 (High) | NEW features craft should adopt, deprecated patterns to remove |
| P2 (Medium) | Warnings from audit, FIXED items to verify |
| P3 (Low) | Desktop integration opportunities, suggestions |

### Step 4: Present Interactive Selection

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

### Step 5: Execute Selected Actions

For each selected item, take appropriate action:

- **Fix frontmatter**: Run `bash scripts/command-audit.sh --fix`
- **Clean hardcoded models**: Search and replace specific model references with generic patterns
- **Adopt new features**: Create a worktree branch if changes are significant, or apply directly if minor
- **Breaking changes**: Investigate affected files and propose fixes

After each action, report what was done and verify the fix.

### Step 6: Summary Report

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
- `/craft:code:release-watch` — Unified Code + Desktop tracking (Step 2)
- `/craft:check` — General pre-flight checks
