# ORCHESTRATE: Claude Code v2.1.49 Integration

**Feature Branch:** `feature/claude-code-integration`
**Created:** 2026-02-20
**Updated:** 2026-02-20 (post-research revision)

---

## Summary

Integrate Claude Code v2.1.49 platform features into craft: plugin `settings.json` for agent defaults, agent enhancements (background, isolation, memory, skills), cleanup of undocumented frontmatter fields, and comprehensive multi-repo coordination documentation.

---

## Research Findings (Pre-Implementation)

### settings.json

- `settings.json` at plugin root is a **Claude Code platform feature** — only supports **agent-level settings**
- It is NOT a general config store — cannot hold custom keys like `claude_md_budget`
- `.claude-plugin/config.json` remains the correct location for craft-specific config
- `plugin.json` has strict schema — no custom keys allowed (confirmed)

### Agent Frontmatter

- All 4 new fields are **officially supported**: `background`, `isolation`, `memory`, `skills`
- Additional supported fields: `maxTurns`, `mcpServers`, `hooks`
- `version` field in current agents is **NOT documented** — should be removed
- Memory scopes: `user` (global), `project` (shared via git), `local` (gitignored)
- Skills are injected into agent context at startup — subagents do NOT inherit parent skills

### Path Corrections

- Optimizer: `utils/claude_md_optimizer.py` (not `scripts/`)
- Sync: `utils/claude_md_sync.py` (not `scripts/`)
- Budget check: `scripts/claude-md-budget-check.sh` (correct)
- Agent definitions: `agents/` directory as `.md` files with YAML frontmatter

---

## Increments

### Increment 1: Plugin settings.json for Agent Defaults (~15 min)

**Goal:** Create `settings.json` with agent-level defaults. Keep `.claude-plugin/config.json` for craft-specific settings (budget, etc.).

**Steps:**

1. Create `settings.json` in plugin root with agent defaults (model routing, permission modes)
2. Document the config resolution chain in a code comment or README section:
   - Agent settings → `settings.json` (platform feature)
   - Craft config → `.claude-plugin/config.json` (custom, not platform)
3. Test: verify plugin loads with settings.json present
4. Run unit tests: `python3 tests/test_craft_plugin.py`

**Files:**

- CREATE: `settings.json`

**No script changes needed** — settings.json is consumed by Claude Code directly for agent settings, not by our Python scripts.

---

### Increment 2: Agent Background, Isolation & Cleanup (~30 min)

**Goal:** Add `background: true` and `isolation: "worktree"` to appropriate agents. Remove undocumented `version` field from all agents.

**Steps:**

1. Remove `version` field from all agent frontmatter (undocumented, may break with strict validation)
2. Add `background: true` to long-running non-blocking agents:
   - `agents/docs/docs-architect.md`
   - `agents/docs/reference-builder.md`
   - `agents/docs/tutorial-engineer.md`
3. Add `isolation: worktree` to code-modifying agents (only if they write files that could conflict):
   - Consider: `orchestrator-v2.md` (coordinates writes via subagents — may not need isolation itself)
4. Test each modified agent with a simple invocation to verify fields are recognized
5. Run unit tests

**Files:**

- MODIFY: `agents/orchestrator-v2.md` (remove version)
- MODIFY: `agents/orchestrator.md` (remove version, if present)
- MODIFY: `agents/docs/docs-architect.md` (remove version, add background)
- MODIFY: `agents/docs/reference-builder.md` (remove version, add background)
- MODIFY: `agents/docs/tutorial-engineer.md` (remove version, add background)
- MODIFY: `agents/docs/api-documenter.md` (remove version)
- MODIFY: `agents/docs/demo-engineer.md` (remove version)
- MODIFY: `agents/docs/mermaid-expert.md` (remove version)

**Decision:** `isolation: worktree` is best for agents that directly modify code files. Docs agents that run in background don't need worktree isolation since they write to separate files. Defer isolation to Increment 3 where we add it selectively.

---

### Increment 3: Agent Memory, Skills & Isolation (~30 min)

**Goal:** Give orchestration agents persistent memory and preloaded skills. Add worktree isolation to code-modifying agents.

**Steps:**

1. Add `memory: project` to orchestrator-v2 (project-specific knowledge, shareable via git)
2. Add `skills` to agents that benefit from preloaded context:
   - Verify each skill name exists in `skills/` directory before adding
   - Only add skills that provide clear value at startup (not all skills)
3. Add `isolation: worktree` to agents that modify code files directly
4. Test memory persistence: invoke orchestrator, check `.claude/agent-memory/orchestrator-v2/` is created
5. Test skills preloading: verify agent has skill context at startup
6. Run unit tests

**Files:**

- MODIFY: `agents/orchestrator-v2.md` (add memory, skills)
- MODIFY: Other agents as determined by skill inventory

**Open question:** Which skills actually exist and are suitable for preloading? Inventory `skills/` directory before deciding.

---

### Increment 4: Multi-Repo Documentation (~1-2 hours)

**Goal:** Create comprehensive multi-repo workflow documentation and fix navigation.

**Steps:**

1. Create `docs/guide/multi-repo-workflow.md` with end-to-end walkthrough:
   - When to use cross-repo coordination
   - Spec syntax that triggers auto-detection (`~/projects/dev-tools/<name>/`)
   - What `orchestrate:plan` does on detection
   - Paired worktrees with bidirectional ORCHESTRATE refs
   - Branch name enforcement
   - `ci:status` cross-repo dashboard
   - Coordinating PRs
2. Add Mermaid sequence diagram to the guide
3. Add cross-repo section to `docs/guide/worktree-advanced-patterns.md` (~50 lines)
4. Update `mkdocs.yml` nav to group multi-repo docs under a visible heading
5. Clarify `ROADMAP.md`: "Cross-repo worktree coordination" = built (v2.15.0+), "Monorepo distribution" = planned
6. Build docs locally: `mkdocs build` to verify no broken links
7. Run broken links test: `python3 tests/test_craft_plugin.py -k "broken_links"`

**Files:**

- CREATE: `docs/guide/multi-repo-workflow.md`
- MODIFY: `docs/guide/worktree-advanced-patterns.md`
- MODIFY: `mkdocs.yml`
- MODIFY: `ROADMAP.md`

---

### Increment 5: Worktree Path Comparison Docs (~20 min)

**Goal:** Document craft's `~/.git-worktrees/` vs Claude's `.claude/worktrees/` clearly.

**Steps:**

1. Add comparison table to `commands/git/worktree.md`
2. Add comparison section to `docs/reference/REFCARD-GIT-WORKTREE.md`
3. Verify both docs recommend craft's approach as primary
4. Build docs to verify rendering

**Files:**

- MODIFY: `commands/git/worktree.md`
- MODIFY: `docs/reference/REFCARD-GIT-WORKTREE.md`

---

## Validation (After All Increments)

- [ ] `python3 tests/test_craft_plugin.py` — 13/13 pass
- [ ] `python3 tests/test_craft_plugin.py -k "broken_links"` — no broken links
- [ ] `mkdocs build` — clean build, no warnings
- [ ] `./scripts/validate-counts.sh` — counts accurate
- [ ] Manual: verify settings.json is picked up by Claude Code
- [ ] Manual: verify agent background/isolation/memory/skills fields work
- [ ] Manual: verify no agents broke after removing `version` field

---

## Commit Strategy

| Increment | Commit Message |
|-----------|---------------|
| 1 | `feat: add plugin settings.json with agent defaults` |
| 2 | `feat: add background field to doc agents, remove undocumented version field` |
| 3 | `feat: add memory, skills, and isolation fields to orchestration agents` |
| 4 | `docs: add multi-repo workflow guide and fix navigation` |
| 5 | `docs: add worktree path comparison (craft vs claude native)` |

---

## Execution Plan (Default Mode — 2 agents max)

### Wave 1 (Parallel)

- **Agent code-1**: Increments 1 + 2 (settings.json + agent cleanup/background)
- **Agent docs-1**: Increment 4 (multi-repo documentation)

### Wave 2 (Parallel)

- **Agent code-1**: Increment 3 (agent memory/skills/isolation)
- **Agent docs-1**: Increment 5 (worktree path comparison)

### Wave 3 (Sequential)

- **Validation**: Full test suite + docs build

---

## Notes

- Increments 1-3 (code) and 4-5 (docs) are independent — can be parallelized
- `settings.json` is for agent defaults ONLY — craft config stays in `.claude-plugin/config.json`
- The multi-repo guide should be the canonical landing page — other docs link to it
- Keep existing `.claude-plugin/config.json` support — no changes to budget resolution chain
- Consider adding `maxTurns` to agents that tend to run too long (future improvement)
