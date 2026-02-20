# ORCHESTRATE: Claude Code v2.1.49 Integration

**Feature Branch:** `feature/claude-code-integration`
**Spec:** `docs/specs/SPEC-claude-code-integration-2026-02-20.md`
**Brainstorm:** `docs/brainstorm/BRAINSTORM-claude-code-integration-2026-02-20.md`
**Created:** 2026-02-20

---

## Summary

Integrate Claude Code v2.1.49 platform features into craft: plugin `settings.json`, agent enhancements (background, isolation, memory, skills), and comprehensive multi-repo coordination documentation.

---

## Increments

### Increment 1: Plugin settings.json (Quick Win, ~20 min)

**Goal:** Ship default config so new users don't need manual `.claude-plugin/config.json` setup.

**Steps:**

1. Create `settings.json` in plugin root with default budget/mode values
2. Update `scripts/claude_md_optimizer.py` to check settings.json in resolution chain
3. Update `scripts/claude_md_sync.py` to check settings.json in resolution chain
4. Update `scripts/claude-md-budget-check.sh` to check settings.json in resolution chain
5. Test: verify new install uses settings.json defaults, existing config.json overrides still work
6. Run unit tests: `python3 tests/test_craft_plugin.py`

**Files:**

- CREATE: `settings.json`
- MODIFY: `scripts/claude_md_optimizer.py`
- MODIFY: `scripts/claude_md_sync.py`
- MODIFY: `scripts/claude-md-budget-check.sh`

**Open question:** Does Claude Code validate settings.json schema or is it free-form? Test before implementing.

---

### Increment 2: Agent Background and Isolation (~30 min)

**Goal:** Add `background: true` and `isolation: "worktree"` to appropriate agent definitions.

**Steps:**

1. Inventory existing agent definitions (check `.claude/agents/` or agent configs in plugin)
2. Add `background: true` to long-running non-blocking agents (docs-architect, reference-builder)
3. Add `isolation: "worktree"` to code-modifying agents (code-reviewer, feature-dev, backend-architect)
4. Test each modified agent with a simple invocation to verify fields are recognized
5. Run unit tests

**Files:**

- MODIFY: Agent YAML definitions (identify exact paths in worktree session)

**Depends on:** Verify Claude Code >= v2.1.49 supports these fields

---

### Increment 3: Agent Memory and Skills (~30 min)

**Goal:** Give orchestration agents persistent memory and preloaded skills.

**Steps:**

1. Add `memory: project` to orchestrator-v2 and task-analyzer agents
2. Add `skills: [session-state, task-analyzer]` to orchestrator-v2
3. Add `skills: [mode-controller]` to task-analyzer
4. Add `skills: [test-generator]` to feature-dev
5. Add `skills: [system-architect]` to backend-architect
6. Test memory persistence: run orchestrator, check memory survives session restart
7. Test skills preloading: verify agent has skill context at startup
8. Run unit tests

**Files:**

- MODIFY: Same agent YAML definitions from Increment 2

**Open question:** What's the context budget impact of preloading skills? Monitor with `/craft:check --context`

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
2. Add Mermaid sequence diagram (from spec) to the guide
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
- [ ] Manual: verify settings.json is picked up by a fresh plugin install
- [ ] Manual: verify agent background/isolation/memory/skills fields work in v2.1.49

---

## Commit Strategy

| Increment | Commit Message |
|-----------|---------------|
| 1 | `feat: add plugin settings.json for default config` |
| 2 | `feat: add background and isolation fields to agent definitions` |
| 3 | `feat: add memory and skills fields to orchestration agents` |
| 4 | `docs: add multi-repo workflow guide and fix navigation` |
| 5 | `docs: add worktree path comparison (craft vs claude native)` |

---

## Notes

- Increments 1-3 (code) and 4-5 (docs) are independent — can be parallelized
- Test agent fields against Claude Code v2.1.49+ (verify version at session start)
- The multi-repo guide should be the canonical landing page — other docs link to it
- Keep existing `.claude-plugin/config.json` support for backward compatibility
