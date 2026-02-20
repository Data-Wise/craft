# BRAINSTORM: Claude Code v2.1.49 Integration

**Date:** 2026-02-20
**Focus:** Feature | **Depth:** Default | **Duration:** ~5 min

## Context

Claude Code v2.1.49 introduces several features that craft should integrate:

- Agent `isolation: "worktree"` and `background: true`
- Plugin `settings.json` for default config
- Agent `memory` and `skills` fields
- Native `claude -w` worktree flag

Craft currently has 108 commands, 25 skills, 8 agents. The multi-repo coordination workflow exists but is poorly documented.

---

## Quick Wins (< 30 min each)

1. **Add `settings.json` to plugin** - Ship default config (budget, modes) without requiring `.claude-plugin/config.json` manual setup. This is a single file addition.

2. **Add `background: true` to validation agents** - Craft's doc-build and lint agents could run in background, freeing the main conversation.

3. **Document worktree path differences** - Add a comparison table to `/craft:git:worktree` and the worktree refcard showing craft's `~/.git-worktrees/` vs Claude's `.claude/worktrees/`, recommending craft's approach.

4. **Add `memory: project` to orchestration agents** - Let `orchestrator-v2` and `task-analyzer` accumulate project knowledge across sessions.

## Medium Effort (1-2 hours each)

5. **Add `isolation: "worktree"` to craft agents** - Agents doing code modifications (feature-dev, backend-architect, code-reviewer) should declare worktree isolation for safe parallel execution.

6. **Add `skills` field to agent definitions** - Preload relevant skills into agents at startup (e.g., orchestrator gets `session-state` + `task-analyzer`).

7. **Create multi-repo walkthrough guide** - End-to-end narrative: spec that references another repo -> `/craft:orchestrate:plan` auto-detects -> paired worktrees -> `/craft:ci:status` dashboard -> coordinated PRs.

8. **Add Mermaid architecture diagram for multi-repo** - Visual showing: spec detection regex -> paired worktrees (bidirectional ORCHESTRATE refs) -> branch name enforcement -> ci:status monitoring.

## Long-term (Future sessions)

9. **Transparent worktree style detection** - Detect whether user has `.claude/worktrees/` or `~/.git-worktrees/` style and adapt commands automatically.

10. **Cross-repo agent swarm** - Use `isolation: "worktree"` + Agent Teams to run agents across multiple repos simultaneously.

11. **`claude --from-pr` integration** - Let `/craft:workflow:recap` suggest resuming sessions linked to open PRs.

---

## Multi-Repo Documentation Gaps (Current State)

### What Exists

| Location | Content | Depth |
|----------|---------|-------|
| `commands/orchestrate/plan.md` | Full 8-step cross-repo detection workflow | Comprehensive |
| `commands/orchestrate.md` | Worktree types table, decision tree | Summary |
| `docs/guide/orchestrator.md` | "When to Use What" table | One-liner |
| `docs/guide/pipeline-orchestrate-guide.md` | Worktree types, decision table | Summary |
| `docs/reference/REFCARD-GIT-WORKTREE.md` | Worktree types with prose | 1 paragraph |
| `docs/commands/ci/status.md` | Cross-repo CI dashboard | Complete |

### What's Missing

1. No standalone multi-repo workflow guide page
2. Cross-repo detection logic only in excluded spec file (not user-facing)
3. `worktree-advanced-patterns.md` (948 lines) has zero cross-repo content
4. No nav grouping for multi-repo docs
5. ROADMAP.md lists "monorepo support" as future but cross-repo worktrees already exist

---

## Recommended Path

Start with **Quick Wins 1-4** (plugin settings.json, background agents, worktree docs, agent memory) to get immediate value. Then tackle **Medium Effort 7-8** (multi-repo guide + diagram) to fix the documentation gap. Agent isolation (#5-6) follows as it requires testing each agent definition.

**Priority order:**

1. `settings.json` (removes setup friction immediately)
2. Multi-repo walkthrough guide (fixes the biggest doc gap)
3. Agent `background: true` + `memory` (low-risk, high-value)
4. Agent `isolation: "worktree"` + `skills` (requires more testing)
5. Worktree path comparison docs (quick but less urgent)
