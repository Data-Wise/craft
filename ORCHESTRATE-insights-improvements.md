# Insights-Driven Improvements Orchestration Plan

> **Branch:** `feature/insights-improvements`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-insights-improvements`
> **Spec:** `docs/specs/SPEC-insights-driven-improvements-2026-02-14.md`

## Objective

Reduce top friction patterns from /insights report (97 sessions): wrong-approach errors (21 events), branch guard false positives (6+ sessions), and repetitive release pipeline interactions (10+ sessions). Update 4 existing commands/skills, create 2 new skills, and update 3 super commands.

## Phase Overview

| Phase | Task | Agent | Priority | Status |
| ----- | ---- | ----- | -------- | ------ |
| 1a | `/craft:check --context` flag + session header | Agent 1 | High | Pending |
| 1b | `/craft:git:worktree validate` action | Agent 2 | High | Pending |
| 1c | PreToolUse hook — worktree path validation | Agent 3 | High | Pending |
| 2a | `/release --autonomous` flag + auto-resolve | Agent 4 | High | Pending |
| 2b | `/craft:guard:audit` new skill | Agent 5 | High | Pending |
| 3 | `/craft:insights:apply` new skill | Agent 6 | Medium | Pending |
| 4a | `do.md` routing table updates | Agent 7 | Medium | Pending |
| 4b | `smart-help.md` context-aware suggestions | Agent 8 | Medium | Pending |
| 4c | `hub.md` count + entry updates | Agent 9 | Medium | Pending |
| 5 | `/craft:orchestrate --swarm` mode | Agent 10 | Low | Pending |

## Parallel Execution Groups

### Group 1 (fully parallel — no dependencies)

These three tasks have zero file overlap:

- **Agent 1:** Update `commands/check.md`
  - Read: spec Change 1, current `commands/check.md`
  - Write: `commands/check.md` (add `--context` arg + session header section)
  - Key: phase detection logic (implementation/testing/pr-prep/release)

- **Agent 2:** Update `commands/git/worktree.md`
  - Read: spec Change 3, current `commands/git/worktree.md`
  - Write: `commands/git/worktree.md` (add `validate` action)
  - Key: CWD check, branch-folder consistency, write-outside detection

- **Agent 3:** Update `.claude-plugin/hooks/pretooluse.py`
  - Read: spec Change 4, current `.claude-plugin/hooks/pretooluse.py`
  - Write: `.claude-plugin/hooks/pretooluse.py` (add worktree path check)
  - Key: non-blocking (stderr warning, NOT exit 1), only on Write/Edit

### Group 2 (depends on Group 1 for context)

- **Agent 4:** Update `skills/release/SKILL.md`
  - Read: spec Change 2, current `skills/release/SKILL.md`
  - Write: `skills/release/SKILL.md` (add `--autonomous` flag)
  - Key: skip 3 AskUserQuestion calls, auto-version from commits, auto-admin on blocked merge, retry once on errors
  - **Coordinate:** marketplace spec also modifies this file (Steps 2c, 3, 8.5) — different sections, no conflict

- **Agent 5:** Create `skills/guard-audit/SKILL.md`
  - Read: spec Change 5, `scripts/branch-guard.sh`, `.claude/branch-guard.json`
  - Write: `skills/guard-audit/SKILL.md` (new file)
  - Key: discovery → friction analysis → test harness → report → apply (JSON config only, never touch script)

### Group 3 (depends on Group 2)

- **Agent 6:** Create `skills/insights-apply/SKILL.md`
  - Read: spec Change 6, `utils/claude_md_sync.py`, `utils/claude_md_optimizer.py`
  - Write: `skills/insights-apply/SKILL.md` (new file)
  - Key: parse insights report → present suggestions → apply via sync pipeline → budget check
  - Target: global CLAUDE.md only (insights are cross-project)

### Group 4 (depends on Groups 1-3 — all new skills/flags must exist)

- **Agent 7:** Update `commands/do.md`
  - Read: spec Change 8a, current `commands/do.md`
  - Write: `commands/do.md` (add routing entries for guard:audit, insights:apply, --autonomous, --context, validate, --swarm)

- **Agent 8:** Update `commands/smart-help.md`
  - Read: spec Change 8b, current `commands/smart-help.md`
  - Write: `commands/smart-help.md` (add state-based suggestions for guard friction, session start, worktree, insights data, release prep)

- **Agent 9:** Update `commands/hub.md`
  - Read: spec Change 8c, current `commands/hub.md`
  - Write: `commands/hub.md` (fix stale counts: 21→25 skills, 100→108 commands, add new skill entries)

### Group 5 (depends on all above — most complex)

- **Agent 10:** Update `commands/orchestrate.md`
  - Read: spec Change 7, current `commands/orchestrate.md`
  - Write: `commands/orchestrate.md` (add `--swarm` flag + worktree-per-agent execution)
  - Key: create worktrees per agent, branch naming, convergence merge, single PR to dev
  - This is the highest complexity change — implement last

## Acceptance Criteria

- [ ] `/craft:check --context` outputs session header (worktree, branch, phase, test command)
- [ ] `/release --autonomous` completes without user prompts (pauses only on fatal errors)
- [ ] `/craft:git:worktree validate` verifies CWD matches expected worktree
- [ ] PreToolUse hook warns (stderr) when writes target wrong directory
- [ ] `/craft:guard:audit` generates friction report + proposed JSON config changes
- [ ] `/craft:insights:apply` extracts CLAUDE.md suggestions from insights report
- [ ] `/craft:orchestrate --swarm` creates isolated worktrees per agent
- [ ] `do.md` routes guard:audit, insights:apply, autonomous release keywords
- [ ] `smart-help.md` suggests new skills based on session state
- [ ] `hub.md` shows 25 skills, 108 commands, includes new skill entries
- [ ] All markdown passes lint (`npx markdownlint-cli2`)
- [ ] Skill count updated: 23 → 25 in CLAUDE.md and plugin.json

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-insights-improvements
claude
# Then: /craft:orchestrate (references this file)
# Group 1 runs 3 agents in parallel (check, worktree, hook)
```
