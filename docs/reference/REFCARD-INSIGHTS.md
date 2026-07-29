# REFCARD: Insights & Friction Prevention

> **Quick reference** for session insights, friction detection, and version sync features.

**Version:** v2.22.0 | **Last Updated:** 2026-02-19

---

## Commands

> **Note (2026-07 v4 consolidation):** none of `workflow:insights`,
> `insights-apply`, and `guard-audit` are slash commands — all three are
> skills invoked by asking naturally. The table below shows the natural-language
> phrasing that triggers each.

| Ask | Purpose |
|---------|---------|
| "generate insights report" (`brainstorm-insights` skill) | Generate usage pattern reports from session facets |
| `/craft:check --context` | Show session context without running validators |
| "apply insights" (`insights-apply` skill) | Apply session learnings to CLAUDE.md rules |
| "audit guard" (`guard-audit` skill) | Tune branch guard to reduce false positives |

## Insights Report

```bash
# ask "generate insights report" (brainstorm-insights skill) — terminal report (last 30 days)
# ask "generate insights report as html" — HTML report
# ask "generate insights report as json" — machine-readable
# ask "generate insights report for the last 7 days" — last 7 days only
```

**Data source:** `~/.claude/usage-data/facets/`

**Report sections:** Friction patterns (frequency + suggestions), goal categories, CLAUDE.md rule candidates.

## Friction Detection Scripts

Four scripts run as part of `/craft:check`:

| Script | What It Checks |
|--------|----------------|
| `scripts/stale-ref-scan.sh` | `.claude/reference/` files older than the code they document |
| `scripts/hook-conflict-audit.sh` | Conflicting hook rules that cause false positives |
| `scripts/claude-md-health.sh` | CLAUDE.md line budget, count accuracy, reference freshness |
| `scripts/version-check.sh` | Version consistency across project files |

## Version Sync (Three Layers)

| Layer | Tool | When It Runs |
|-------|------|-------------|
| 1. PreToolUse hook | `scripts/version-sync.sh` | Before every tool call |
| 2. Pre-commit hook | `scripts/version-sync-precommit.sh` | At `git commit` |
| 3. `/craft:check` | `scripts/version-check.sh` | On-demand validation |

**Synced files:** `plugin.json`, `CLAUDE.md`, `docs/index.md`, `.STATUS`, `VERSION-HISTORY.md`, `marketplace.json`

## Session Context

```bash
/craft:check --context
```

Shows: project type, branch, worktree path, base branch, guard status, development phase, and recent friction patterns — without running any validators.

**Phase detection:** `implementation` → `testing` → `pr-prep` → `release` (auto-detected from git state).

## Lifecycle Flow

```
Sessions → Facets → brainstorm-insights skill → Friction Report
                                                    ↓
                              insights-apply skill  → CLAUDE.md rules
                              guard-audit skill     → branch-guard.json tuning
                              /craft:check          → friction detection in pre-flight
```

## Related Docs

- **Tutorial:** [Insights-Driven Workflow](../tutorials/TUTORIAL-insights-workflow.md) — Full walkthrough
- **Guide:** [Insights Improvements Guide](../guide/insights-improvements-guide.md) — Detailed feature docs
- **Refcard:** [REFCARD-CHECK](REFCARD-CHECK.md) — Pre-flight check reference
- **Refcard:** [REFCARD-CLAUDE-MD](REFCARD-CLAUDE-MD.md) — CLAUDE.md management
