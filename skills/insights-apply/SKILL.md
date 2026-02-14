---
name: insights-apply
description: This skill should be used when the user asks to "apply insights", "insights to rules", "update rules from insights", "apply suggestions", or mentions updating CLAUDE.md from insights data. Extracts suggestions from the /insights report and applies them to the global CLAUDE.md via the sync pipeline.
---

# Insights Apply

Extract CLAUDE.md improvement suggestions from the /insights report and apply them through the sync pipeline. Targets the global CLAUDE.md only (insights are cross-project).

## When to Use

- User says "apply insights", "update rules from insights"
- After running `/insights` and seeing `claude_md_additions` suggestions
- User wants to incorporate session learnings into CLAUDE.md
- Insights data exists at `~/.claude/usage-data/`

## Prerequisites

- Insights report must exist (`~/.claude/usage-data/report.html` or facets data)
- Global CLAUDE.md at `~/.claude/CLAUDE.md`
- Python3 available (for sync pipeline)

## Insights Apply Pipeline

Execute these steps in order.

### Step 1: Parse Insights Report

Locate and parse the insights data:

```bash
# Check for insights data
if [ -f ~/.claude/usage-data/report.html ]; then
    echo "Found insights report"
elif [ -d ~/.claude/usage-data/facets/ ]; then
    echo "Found facets data"
else
    echo "No insights data found. Run /insights first."
    exit 1
fi
```

Extract the `claude_md_additions` array from the report. These are structured suggestions with:

- `title`: Section heading for CLAUDE.md
- `content`: The actual rules/guidance to add
- `source`: Which sessions/patterns generated this suggestion
- `priority`: How impactful the suggestion is (high/medium/low)

### Step 2: Present Suggestions

Show each suggestion with context for user review:

```text
┌───────────────────────────────────────────────────────────────┐
│ INSIGHTS SUGGESTIONS (N found)                                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Suggestion 1/N: <title>                                       │
│ Source: <N sessions with this pattern>                         │
│ Priority: <high|medium|low>                                   │
│                                                               │
│ Proposed CLAUDE.md addition:                                  │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ ## <Title>                                               │   │
│ │ - <rule 1>                                               │   │
│ │ - <rule 2>                                               │   │
│ │ - <rule 3>                                               │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

For each suggestion, ask the user:

```json
{
  "questions": [{
    "question": "Apply this suggestion to global CLAUDE.md?",
    "header": "Apply",
    "multiSelect": false,
    "options": [
      {
        "label": "Apply (Recommended)",
        "description": "Add this section to ~/.claude/CLAUDE.md"
      },
      {
        "label": "Skip",
        "description": "Don't add this suggestion"
      },
      {
        "label": "Edit first",
        "description": "Let me modify the content before applying"
      }
    ]
  }]
}
```

### Step 3: Apply via Sync Pipeline

For each approved suggestion, use the CLAUDE.md sync pipeline:

```bash
# Apply using the sync pipeline
python3 utils/claude_md_sync.py ~/.claude/CLAUDE.md --add-section "<title>" "<content>"
```

If sync pipeline is not available, fall back to direct append:

```bash
# Fallback: Direct append to CLAUDE.md
echo "" >> ~/.claude/CLAUDE.md
echo "## <Title>" >> ~/.claude/CLAUDE.md
echo "" >> ~/.claude/CLAUDE.md
echo "<content>" >> ~/.claude/CLAUDE.md
```

### Step 4: Budget Check

After applying all approved suggestions, verify the CLAUDE.md stays within budget:

```bash
# Run budget enforcer
python3 utils/claude_md_optimizer.py ~/.claude/CLAUDE.md --check

# If over budget, the optimizer will:
# 1. Report which sections exceed limits
# 2. Suggest P2 content to move to detail files
# 3. Offer to auto-optimize
```

If the CLAUDE.md exceeds the line budget after additions:

```text
┌───────────────────────────────────────────────────────────────┐
│ ⚠️  BUDGET WARNING                                            │
├───────────────────────────────────────────────────────────────┤
│ CLAUDE.md is now N lines (budget: 200 lines)                  │
│ Over budget by M lines                                        │
│                                                               │
│ Options:                                                      │
│   1. Run optimizer to trim P2 content                         │
│   2. Keep as-is (will be truncated at 200 lines)              │
│   3. Manually edit to reduce size                             │
└───────────────────────────────────────────────────────────────┘
```

### Step 5: Report

Summarize what was applied:

```text
┌───────────────────────────────────────────────────────────────┐
│ INSIGHTS APPLY REPORT                                         │
├───────────────────────────────────────────────────────────────┤
│ Suggestions found:    N                                       │
│ Applied:              M                                       │
│ Skipped:              P                                       │
│ Edited:               Q                                       │
│                                                               │
│ CLAUDE.md status:     Within budget / Over budget             │
│ File:                 ~/.claude/CLAUDE.md                     │
│                                                               │
│ Applied sections:                                             │
│   ✅ Branch Guard & Git Hooks                                  │
│   ✅ Worktree Best Practices                                   │
│   ⏭️  Release Pipeline (skipped)                               │
│   ✅ Testing Conventions (edited)                              │
└───────────────────────────────────────────────────────────────┘
```

## Output Format

Use craft box-drawing format throughout. Show step progress:

```text
[1/5] Parse insights ........... DONE (N suggestions found)
[2/5] Present suggestions ...... DONE (user reviewed N)
[3/5] Apply approved ........... DONE (M applied)
[4/5] Budget check ............. DONE (within budget)
[5/5] Report ................... SHOWN
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| No insights data | Suggest running `/insights` first |
| CLAUDE.md not found | Suggest running `/craft:docs:claude-md:init` |
| Sync pipeline fails | Fall back to direct append |
| Over budget | Offer optimizer or manual edit |
| Parse error | Show raw data for manual review |

## Scope

**Global CLAUDE.md only.** Insights are cross-project patterns, so they belong in `~/.claude/CLAUDE.md`, not project-specific files.

## See Also

- `/insights` — Generate the insights report
- `/craft:docs:claude-md:sync` — CLAUDE.md sync pipeline
- `utils/claude_md_sync.py` — 4-phase sync pipeline
- `utils/claude_md_optimizer.py` — Budget enforcement
