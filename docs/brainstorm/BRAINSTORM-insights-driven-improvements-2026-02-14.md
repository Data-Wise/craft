# Insights-Driven Improvements - Deep Brainstorm

**Generated:** 2026-02-14
**Context:** Craft plugin, dev branch
**Depth:** Max (8 questions + 2 agents)
**Focus:** Feature
**Source:** /insights report (97 sessions, 10 days, 153h)

## Overview

Analyze the /insights report suggestions and map them to concrete craft command/skill changes. The insights identified 4 CLAUDE.md additions, 3 feature suggestions, and 3 usage pattern improvements across 97 sessions. This brainstorm determines which existing commands need updates, which new skills to create, and the implementation priority.

## Decisions Made (from 8 expert questions)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Priority | All areas equally | No single area dominates friction |
| 2 | Approach | Skills over commands | Skills are more flexible, better for complex workflows |
| 3 | Release autonomy | `/release --autonomous` flag | Extends existing skill, self-corrects on failures |
| 4 | Session context | `/craft:check --context` flag | Injects worktree, branch, phase into session |
| 5 | Branch guard | New `/craft:guard:audit` skill | Analyzes hooks, finds false positives, proposes fixes |
| 6 | Worktree validation | Both hook + command flag | Hook catches mistakes, command provides manual check |
| 7 | Parallel swarm | `/craft:orchestrate --swarm` flag | 3 agents in isolated worktrees, converge to one PR |
| 8 | Insights-to-rules | New `/craft:insights:apply` skill | Parses insights, suggests CLAUDE.md additions |

## Agent Findings

### Agent 1: Command Gap Analysis

**Release skill (`skills/release/SKILL.md`):**

- Currently has 3 user interaction points: version confirmation (Step 1), branch protection override (Step 7), manual intervention on failures
- `--autonomous` would auto-confirm version (use semver from commits), auto-retry CI (up to 2x), auto-resolve simple merge conflicts
- Files: `skills/release/SKILL.md` (update), `scripts/pre-release-check.sh` (no change)

**Branch guard (`scripts/branch-guard.sh`, ~740 lines):**

- False positive sources: regex matches on PR body text containing destructive commands as documentation, write-through detection for variables in paths, force-push detection doesn't distinguish feature branches
- Currently has 94 unit tests + 31 e2e tests — good coverage but no audit/tune capability
- Config at `.claude/branch-guard.json` supports per-project overrides

**Pre-flight (`commands/check.md`):**

- Already detects: project type, build tool, worktree status, guard status, git status
- Missing: session phase (implementation/testing/PR prep), target branch context, test command auto-detection
- `--context` would output a session header block that persists for the conversation

**Orchestrate (`commands/orchestrate.md`):**

- Currently reads ORCHESTRATE files and delegates to agents sequentially or in groups
- No concept of "swarm" (isolated worktrees per agent with convergence)
- Would need: worktree creation per agent, branch naming convention, merge strategy

### Agent 2: New Skill Research

**`/craft:guard:audit` skill:**

- Build on existing test suite (1256 + 663 lines across 2 test files)
- Read `.claude/branch-guard.json` for custom rules
- Generate test harness that simulates 10+ common operations
- Output: friction report + proposed config changes

**`/craft:insights:apply` skill:**

- Insights report at `~/.claude/usage-data/report.html` + `facets/` directory
- Would parse `claude_md_additions` from insights JSON
- Use `utils/claude_md_sync.py` 4-phase pipeline to apply changes
- Interactive: show each suggestion, user approves/rejects

**Swarm mode for orchestrate:**

- Pattern: `ORCHESTRATE-*.md` files already define agent groups
- Swarm adds: auto-create worktrees, agent isolation, convergence PR
- Similar to existing worktree auto-setup in `/craft:git:worktree create`

## Quick Wins (< 30 min each)

1. Add `--context` argument to `/craft:check` frontmatter + output session header
2. Add `--autonomous` argument to `/release` SKILL.md frontmatter
3. Add `--validate` flag to `/craft:git:worktree` frontmatter
4. Create `skills/guard-audit/` directory with SKILL.md skeleton

## Medium Effort (1-2 hours each)

- [ ] Implement `/craft:check --context` session header output
- [ ] Implement `/release --autonomous` self-correction logic
- [ ] Create `/craft:guard:audit` skill (test harness generation)
- [ ] Create `/craft:insights:apply` skill (parse report, suggest rules)
- [ ] Add `--swarm` flag to `/craft:orchestrate` with worktree creation
- [ ] Create PreToolUse hook for worktree path validation

## Long-term (Future sessions)

- [ ] Headless mode integration (claude -p) for pre-flight checks
- [ ] Cross-session learning persistence for branch guard tuning
- [ ] Multi-repo swarm orchestration (across projects)
- [ ] Insights-driven auto-tuning of all craft settings

## Recommended Path

Start with the 3 existing command updates (check, release, worktree) since they extend well-tested code with minimal risk. Then create the 2 new skills (guard:audit, insights:apply). Finally, tackle the orchestrate swarm mode which requires the most new infrastructure.

### Implementation Order

| Phase | Item | Files Changed | Complexity |
|-------|------|---------------|------------|
| 1a | `/craft:check --context` | `commands/check.md` | Low |
| 1b | `/release --autonomous` | `skills/release/SKILL.md` | Medium |
| 1c | `/craft:git:worktree --validate` | `commands/git/worktree.md` | Low |
| 1d | Worktree path validation hook | `.claude-plugin/hooks/pretooluse.py` | Medium |
| 2a | `/craft:guard:audit` skill | `skills/guard-audit/SKILL.md` (new) | Medium |
| 2b | `/craft:insights:apply` skill | `skills/insights-apply/SKILL.md` (new) | Medium |
| 3 | `/craft:orchestrate --swarm` | `commands/orchestrate.md` | High |

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `commands/check.md` | UPDATE | Add `--context` arg, session header output |
| `skills/release/SKILL.md` | UPDATE | Add `--autonomous` flag, self-correction logic |
| `commands/git/worktree.md` | UPDATE | Add `--validate` flag, path verification |
| `commands/orchestrate.md` | UPDATE | Add `--swarm` flag, worktree-per-agent |
| `skills/guard-audit/SKILL.md` | CREATE | Branch guard audit + tuning skill |
| `skills/insights-apply/SKILL.md` | CREATE | Insights report to CLAUDE.md rules |
| `.claude-plugin/hooks/pretooluse.py` | UPDATE | Add worktree path validation |
| `CLAUDE.md` | UPDATE | Version, skill count (23 → 25), any new rules |
| `.claude-plugin/plugin.json` | UPDATE | Version if releasing |
