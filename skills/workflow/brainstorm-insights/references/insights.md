
# brainstorm-insights — Session Insights Report

> **Note (2026-07 v4 consolidation):** this is a skill, not a slash command —
> invoke by asking naturally. The `/craft:insights` command referenced below
> in some historical examples no longer exists.

Aggregate and analyze session data from `~/.claude/usage-data/facets/` to identify friction patterns, recurring goals, and CLAUDE.md improvement suggestions.

## Usage

```bash
# Default: terminal report, last 30 days
ask "generate insights report"

# HTML report for sharing
ask "generate insights report as html"

# JSON output for scripting
ask "generate insights report as json"

# Last 7 days only
ask "generate insights report for the last 7 days"

# Filter to specific project
ask "generate insights report for project craft"
```

## Execution Behavior (MANDATORY)

### Step 1: Locate Facets Data

Check for session data:

```bash
# Primary location
ls ~/.claude/usage-data/facets/*.json 2>/dev/null

# Alternative: report.html from previous /insights runs
ls ~/.claude/usage-data/report.html 2>/dev/null
```

If no data found, show:

```text
No insights data found.

Session facets are written when you run \`/craft:finish\`. Once the SessionEnd facet hook (issue #183) is installed, a lower-fidelity skeleton facet is also written automatically at the end of every session — see the insights setup tutorial.
Check back after a few sessions, or verify data at:
  ~/.claude/usage-data/facets/
```

### Step 2: Aggregate Facets

> **Defensive Parsing Contract (v2.33.0).** Facet files are written by `/craft:finish`, but disk corruption, interrupted writes, or hand-edits can leave malformed entries. Every command that reads facets — including this one, `/craft:hub` Step 1.7, and `/craft:do` Step 1.5 — MUST wrap each per-file read in a `try / except` that catches `(json.JSONDecodeError, KeyError, TypeError, FileNotFoundError, UnicodeDecodeError, OSError)`, log a `warning: skipping malformed facet <path>: <ErrType>: <msg>` line to stderr, and `continue` to the next file. Never abort the whole report on a single bad facet. The regression test lives at `tests/test_facet_parsing_defensive.py` and runs both `commands/hub.md` and `commands/do.md` snippets against deliberately corrupt fixtures.

Read all facet JSON files within the `--since` window. Extract and aggregate:

1. **Session count** — total sessions analyzed
2. **Goal categories** — what users worked on (feature dev, bug fix, docs, etc.)
3. **Friction patterns** — recurring issues categorized by type:
   - `wrong_approach` — started work incorrectly (wrong branch, wrong dir)
   - `context_loss` — lost context mid-session (compression, disconnect)
   - `tool_misuse` — used wrong tool for the task
   - `test_failure` — tests failed unexpectedly
   - `dependency_issue` — package/version problems
   - `config_drift` — configuration out of sync
4. **Outcome distribution** — success, partial, abandoned rates
5. **CLAUDE.md suggestions** — rules that would prevent observed friction

### Step 3: Generate Report

#### Terminal Format (default)

```text
┌───────────────────────────────────────────────────────────────┐
│ SESSION INSIGHTS — Last 30 days                                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Sessions analyzed: 82                                          │
│ Date range: 2026-01-16 → 2026-02-15                           │
│                                                               │
│ Goal Categories:                                               │
│   Feature development  ████████████████░░░░  42 (51%)          │
│   Bug fixes            ██████░░░░░░░░░░░░░░  15 (18%)          │
│   Documentation        █████░░░░░░░░░░░░░░░  12 (15%)          │
│   Refactoring          ███░░░░░░░░░░░░░░░░░   8 (10%)          │
│   Other                ██░░░░░░░░░░░░░░░░░░   5 (6%)           │
│                                                               │
│ Friction Patterns (21 events):                                 │
│   wrong_approach   ████████████  12 (57%)                      │
│   context_loss     ████░░░░░░░░   4 (19%)                      │
│   test_failure     ███░░░░░░░░░   3 (14%)                      │
│   config_drift     ██░░░░░░░░░░   2 (10%)                      │
│                                                               │
│ Top Friction Detail:                                           │
│   1. Wrong CWD (main repo instead of worktree) — 8 times      │
│   2. Forgot to read ORCHESTRATE file — 3 times                 │
│   3. Test count drift after adding commands — 2 times          │
│                                                               │
│ Outcomes:                                                      │
│   Success    ██████████████████  68 (83%)                       │
│   Partial    ████░░░░░░░░░░░░░   9 (11%)                       │
│   Abandoned  ██░░░░░░░░░░░░░░░   5 (6%)                        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ CLAUDE.md Suggestions (3 found):                               │
│                                                               │
│ 1. [HIGH] Verify CWD before starting work                      │
│    Source: 8 wrong_approach events                              │
│    Rule: "Always run `pwd` and `git branch` before editing"    │
│                                                               │
│ 2. [MEDIUM] Read ORCHESTRATE file on session start             │
│    Source: 3 context_loss events                                │
│    Rule: "On session start, read ORCHESTRATE-*.md if present"  │
│                                                               │
│ 3. [LOW] Run validate-counts after adding commands             │
│    Source: 2 config_drift events                                │
│    Rule: "After adding/removing commands, run validate-counts" │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Apply suggestions: ask "apply insights" (insights-apply skill) │
│ Full HTML report: ask "generate insights report as html"       │
└───────────────────────────────────────────────────────────────┘
```

#### HTML Format

Generate `~/.claude/usage-data/report.html` with:

- Interactive charts (session goals, friction patterns)
- Filterable table of all sessions
- CLAUDE.md suggestions with copy buttons
- Timeline of friction events

#### JSON Format

Output structured JSON to stdout:

```json
{
  "period": {"start": "2026-01-16", "end": "2026-02-15", "days": 30},
  "sessions": {"total": 82, "success": 68, "partial": 9, "abandoned": 5},
  "goals": {"feature": 42, "bugfix": 15, "docs": 12, "refactor": 8, "other": 5},
  "friction": {
    "total": 21,
    "by_type": {"wrong_approach": 12, "context_loss": 4, "test_failure": 3, "config_drift": 2},
    "top_details": ["Wrong CWD (8x)", "Forgot ORCHESTRATE (3x)", "Count drift (2x)"]
  },
  "claude_md_additions": [
    {"title": "Verify CWD", "content": "Always run pwd and git branch before editing", "priority": "high", "source": "8 wrong_approach events"}
  ]
}
```

### Step 4: Integration Hooks

After generating the report:

1. **ORCHESTRATE integration**: If generating an ORCHESTRATE file (via `/craft:plan`), check insights for project-specific friction and auto-add a "Friction Prevention" section
2. **Brainstorm integration**: When brainstorm starts, check insights for relevant past session patterns and show a summary if related sessions exist

## Friction Type → Guardrail Mapping

When insights data feeds into ORCHESTRATE generation:

| Friction Type | Guardrail Rule |
|--------------|----------------|
| `wrong_approach` | "Verify CWD is the worktree before starting" |
| `context_loss` | "Read ORCHESTRATE file on session start" |
| `tool_misuse` | "Use /craft:do for routing, not manual commands" |
| `test_failure` | "Run tests after each phase, not just at the end" |
| `dependency_issue` | "Check package versions match before implementing" |
| `config_drift` | "Run validate-counts after structural changes" |

## See Also

- [insights-apply skill](../../../insights-apply/SKILL.md) — Apply suggestions to CLAUDE.md (ask "apply insights")
- [/craft:check --context](../../../../commands/check.md) — Context-aware phase detection
- [Insights Guide](../../../../docs/guide/insights-improvements-guide.md) — Full documentation
