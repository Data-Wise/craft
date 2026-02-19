# /craft:workflow:insights

Generate insights report from session facets data with friction patterns, goal categories, and CLAUDE.md suggestions.

## Usage

```bash
/craft:workflow:insights                    # Terminal report, last 30 days
/craft:workflow:insights --format html      # HTML report for sharing
/craft:workflow:insights --format json      # JSON output for scripting
/craft:workflow:insights --since 7          # Last 7 days only
/craft:workflow:insights --project craft    # Filter to specific project
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--format` | Output format: `terminal`, `html`, `json` | `terminal` |
| `--since` | Number of days to include | `30` |
| `--project` | Filter to specific project | all projects |

## What It Does

Aggregates session data from `~/.claude/usage-data/facets/` to identify:

1. **Goal categories** — what you worked on (feature dev, bug fixes, docs, etc.)
2. **Friction patterns** — recurring issues by type (wrong approach, context loss, test failures)
3. **Outcome distribution** — success, partial, abandoned rates
4. **CLAUDE.md suggestions** — rules that would prevent observed friction

## Example Output

```text
┌───────────────────────────────────────────────────────────────┐
│ SESSION INSIGHTS — Last 30 days                                │
├───────────────────────────────────────────────────────────────┤
│ Sessions analyzed: 82                                          │
│ Date range: 2026-01-16 → 2026-02-15                           │
│                                                               │
│ Goal Categories:                                               │
│   Feature development  ████████████████░░░░  42 (51%)          │
│   Bug fixes            ██████░░░░░░░░░░░░░░  15 (18%)          │
│   Documentation        █████░░░░░░░░░░░░░░░  12 (15%)          │
│                                                               │
│ Friction Patterns (21 events):                                 │
│   wrong_approach   ████████████  12 (57%)                      │
│   context_loss     ████░░░░░░░░   4 (19%)                      │
│   test_failure     ███░░░░░░░░░   3 (14%)                      │
│                                                               │
│ CLAUDE.md Suggestions (3 found):                               │
│   1. [HIGH] Verify CWD before starting work                    │
│   2. [MEDIUM] Read ORCHESTRATE file on session start           │
│   3. [LOW] Run validate-counts after adding commands           │
├───────────────────────────────────────────────────────────────┤
│ Apply suggestions: /craft:insights-apply                       │
└───────────────────────────────────────────────────────────────┘
```

## Friction Type Mapping

| Friction Type | Guardrail Rule |
|--------------|----------------|
| `wrong_approach` | Verify CWD is the worktree before starting |
| `context_loss` | Read ORCHESTRATE file on session start |
| `tool_misuse` | Use `/craft:do` for routing, not manual commands |
| `test_failure` | Run tests after each phase, not just at the end |
| `dependency_issue` | Check package versions match before implementing |
| `config_drift` | Run validate-counts after structural changes |

## Integration

- **ORCHESTRATE**: Auto-adds friction prevention section when generating plans
- **Brainstorm**: Shows relevant past session patterns when starting
- **`/craft:check --context`**: Appends friction summary to session context

## See Also

- [/craft:check --context](../check.md) — Context-aware phase detection with insights
- [Insights Guide](../../guide/insights-improvements-guide.md) — Full documentation
- [Insights Tutorial](../../tutorials/TUTORIAL-insights-workflow.md) — Step-by-step workflow
