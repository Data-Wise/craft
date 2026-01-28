# Craft Plugin Enhancement Proposal

**Generated:** 2025-12-28
**Current Version:** 1.9.0 (64 commands, 16 skills, 7 agents)
**Based on:** Marketplace research + workflow analysis

---

## Executive Summary

The craft plugin is already comprehensive, but marketplace research reveals opportunities to:

1. **Reduce command sprawl** (64 commands may be overwhelming)
2. **Enhance orchestration** (multi-agent workflows)
3. **Add quality gates** (automated validation between steps)
4. **Implement workflow recipes** (pre-configured patterns)

---

## Current State Analysis

### Strengths

| Area | Assessment |
|------|------------|
| **Coverage** | Excellent - covers code, git, site, docs, test, arch, plan, dist |
| **Mode System** | Strong - default/debug/optimize/release modes |
| **ADHD-Friendly** | Excellent - clear hierarchy, quick wins, visual output |
| **Project Detection** | Good - R, Python, Node, Quarto auto-detection |
| **Documentation** | Very good - consistent markdown structure |

### Gaps Identified (vs Marketplace Best Practices)

| Gap | Impact | Priority |
|-----|--------|----------|
| Too many commands (64) | Decision paralysis | HIGH |
| No quality gates | Manual validation needed | MEDIUM |
| Limited workflow recipes | Can't save/replay workflows | MEDIUM |
| No cross-session memory | Context lost between sessions | LOW |
| Skills underutilized | 16 skills but commands dominate | MEDIUM |

---

## Marketplace Insights

### Top Patterns from Research

1. **wshobson/agents (99 agents, 15 orchestrators)**
   - Pre-configured workflow chains (full-stack, security, ML)
   - Quality gates between phases
   - Specialist subagents

2. **Claude Code Best Practices (Anthropic)**
   - "Long lists of complex commands are an anti-pattern"
   - Natural language > magic commands
   - Skills auto-detect context

3. **Superpowers Plugin Pattern**
   - `/brainstorm` → `/write-plan` → `/execute-plan`
   - Three-phase workflow simplification

4. **Claude CodePro Pattern**
   - Spec-driven development
   - TDD enforcement via hooks
   - Cross-session memory

---

## Proposals

### Plan A: Command Consolidation (Conservative) ⭐ RECOMMENDED

**Goal:** Reduce 64 commands to ~25 primary commands via smart routing

**Approach:**

1. Keep top-level commands as primary entry points
2. Route to specific commands via `/craft:do`
3. Convert many commands to skills (auto-invoked)

**Changes:**

| Category | Current | Proposed | Strategy |
|----------|---------|----------|----------|
| **Top-level** | 5 | 5 | Keep (do, check, hub, orchestrate, smart-help) |
| **code** | 12 | 4 | Merge: lint+coverage→quality, ci-local+ci-fix→ci |
| **test** | 7 | 2 | Merge: run+watch+coverage→test, cli-gen+cli-run→cli-test |
| **docs** | 13 | 4 | Merge: generate+api+sync→generate, changelog+claude-md+nav-update→update |
| **site** | 14 | 4 | Merge: create+init→create, build+preview+deploy→publish |
| **git** | 6 | 3 | Merge: sync+clean→sync, branch+worktree→branch |
| **arch** | 4 | 2 | Merge: analyze+plan→analyze, diagram+review→diagram |
| **plan** | 3 | 1 | Merge: feature+sprint+roadmap→plan |
| **dist** | 2 | 1 | Merge: homebrew+curl-install→dist |

**Result:** 64 → 26 commands

**Preserved commands become skills** that `/craft:do` auto-invokes

---

### Plan B: Workflow Recipes (Additive)

**Goal:** Add pre-configured workflow patterns without removing commands

**New Commands:**

```
/craft:recipe list          # Show available recipes
/craft:recipe run <name>    # Execute a recipe
/craft:recipe create        # Save current workflow as recipe
/craft:recipe show <name>   # Preview recipe steps
```

**Built-in Recipes:**

| Recipe | Steps | Use Case |
|--------|-------|----------|
| **full-stack-feature** | arch:plan → code:test-gen → test:run → git:branch | New feature dev |
| **release-prep** | check release → docs:changelog → code:release → dist:homebrew | Release workflow |
| **docs-sprint** | docs:update → site:build → site:preview → site:deploy | Documentation day |
| **code-review** | code:lint optimize → test:coverage → arch:review | PR preparation |
| **quick-fix** | code:debug → test:run → git:sync | Bug fix workflow |
| **r-package** | code:lint → test:run → docs:generate → dist:homebrew | R package release |

**Recipe Format (YAML):**

```yaml
name: full-stack-feature
description: Complete feature development workflow
steps:
  - command: arch:plan
    wait_for_approval: true
  - command: code:test-gen
    mode: default
  - command: test:run
    mode: debug
    gate:
      type: test_pass
      threshold: 100%
  - command: git:branch
    args: "feature/${feature_name}"
```

---

### Plan C: Quality Gates System (Additive)

**Goal:** Add automated validation between workflow steps

**New Concepts:**

1. **Gate Types:**
   - `test_pass` - Tests must pass (configurable threshold)
   - `lint_clean` - No lint errors
   - `coverage_min` - Minimum coverage percentage
   - `docs_current` - Documentation up to date
   - `approval` - Human approval required

2. **Gate Integration:**

```
/craft:gate add <type>      # Add gate to current workflow
/craft:gate check           # Run all gates
/craft:gate status          # Show gate results
```

3. **Orchestrator Enhancement:**

```
/craft:orchestrate "add auth" --gates strict
# Automatically adds gates between phases
```

---

### Plan D: Skills-First Redesign (Transformative)

**Goal:** Convert 75% of commands to auto-invoked skills

**Philosophy:** "Don't make users memorize commands - let Claude figure it out"

**Approach:**

1. Keep only 10 essential commands
2. Convert everything else to skills
3. `/craft:do` becomes the primary interface

**Essential Commands (10):**

```
/craft:do <task>           # Universal entry point
/craft:check [for]         # Pre-flight validation
/craft:hub                 # Discovery
/craft:orchestrate         # Multi-agent mode
/craft:recipe <action>     # Workflow recipes
/craft:site <action>       # Site management
/craft:git <action>        # Git operations
/craft:test <action>       # Testing
/craft:docs <action>       # Documentation
/craft:release             # Release workflow
```

**Everything Else → Skills:**

- `lint`, `coverage`, `refactor` → code-quality skill
- `changelog`, `claude-md`, `nav-update` → docs-automation skill
- `branch`, `worktree`, `sync` → git-workflow skill

**Benefit:** Claude auto-invokes appropriate skill based on context

---

## Recommendation Matrix

| Plan | Effort | Impact | Risk | Best For |
|------|--------|--------|------|----------|
| **A: Consolidation** | Medium | High | Low | Reducing overwhelm |
| **B: Recipes** | Low | Medium | Very Low | Power users |
| **C: Quality Gates** | Medium | Medium | Low | CI/CD workflows |
| **D: Skills-First** | High | Very High | Medium | Long-term vision |

### Recommended Path

```
Phase 1: Plan B (Workflow Recipes)     [2-3 hours]
  └─ Quick win, additive, no breaking changes

Phase 2: Plan C (Quality Gates)        [3-4 hours]
  └─ Enhance orchestrator reliability

Phase 3: Plan A (Consolidation)        [4-6 hours]
  └─ Reduce command count, improve UX

Phase 4: Plan D (Skills-First)         [Future]
  └─ Full transformation (breaking changes)
```

---

## Quick Wins (Implement Now)

### 1. Add `/craft:recipe` Command ⚡

**File:** `commands/recipe.md`
**Effort:** 1 hour
**Impact:** Immediate workflow improvement

### 2. Enhance `/craft:do` Routing

**Current:** Routes to single command
**Enhanced:** Routes to recipe if multi-step task detected

**Example:**

```
User: /craft:do "prepare release"
Claude: Detected multi-step task. Running recipe: release-prep
  Step 1/4: Running check --for release...
  Step 2/4: Running docs:changelog...
  ...
```

### 3. Add Workflow Cheat Sheet

**New skill:** `workflow-patterns`
**Auto-triggers when:** User seems unsure what to do next
**Shows:** Common workflow patterns for current project type

---

## Specific Command Edits

### Commands to Merge

| Merge Into | Absorbs | Rationale |
|------------|---------|-----------|
| `code:quality` | lint, coverage, deps-check | All code health checks |
| `test:run` | watch, debug, coverage | Test execution variations |
| `docs:update` | sync, changelog, claude-md, nav-update | Doc maintenance tasks |
| `site:publish` | build, preview, deploy | Site lifecycle |
| `git:workflow` | sync, clean, branch, worktree | Git operations |

### Commands to Convert to Skills

| Command | → Skill | Trigger |
|---------|---------|---------|
| `code:refactor` | refactoring-advisor | When Claude sees complex code |
| `arch:diagram` | mermaid-generator | When architecture discussed |
| `plan:roadmap` | roadmap-builder | When long-term planning needed |
| `docs:mermaid` | mermaid-expert | When diagrams requested |

### Commands to Keep As-Is

| Command | Reason |
|---------|--------|
| `/craft:do` | Universal entry point |
| `/craft:check` | Pre-flight essential |
| `/craft:hub` | Discovery essential |
| `/craft:orchestrate` | Multi-agent essential |
| `/craft:site:create` | Complex wizard |

---

## New Commands Proposed

### `/craft:recipe`

```yaml
---
description: Manage and run workflow recipes
arguments:
  - name: action
    description: list|run|create|show|edit
    required: true
  - name: name
    description: Recipe name (for run/show/edit)
    required: false
---
```

### `/craft:gate`

```yaml
---
description: Quality gates for workflows
arguments:
  - name: action
    description: check|add|status|clear
    required: true
  - name: type
    description: Gate type (test_pass|lint_clean|coverage_min|docs_current)
    required: false
---
```

### `/craft:workflow`

```yaml
---
description: Workflow management and history
arguments:
  - name: action
    description: history|save|load|replay
    required: true
---
```

---

## Implementation Priority

### Phase 1: Quick Wins (This Week)

- [ ] Create `/craft:recipe` command
- [ ] Add 6 built-in recipes
- [ ] Update hub to show recipes

### Phase 2: Orchestrator Enhancement (Next Week)

- [ ] Add quality gates to orchestrator
- [ ] Implement gate checking between steps
- [ ] Add `--gates` flag to orchestrate

### Phase 3: Command Consolidation (Week 3)

- [ ] Merge code commands (12→4)
- [ ] Merge docs commands (13→4)
- [ ] Convert merged commands to skills
- [ ] Update hub and documentation

### Phase 4: Skills-First (Future)

- [ ] Design skill auto-detection patterns
- [ ] Implement context-based skill triggering
- [ ] Reduce command count to 10

---

## Success Metrics

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Command count | 64 | 25-30 | Count commands/ files |
| Time to common task | ~30s | ~10s | User testing |
| Decision paralysis | High | Low | User feedback |
| Workflow completion | Manual | Automated | Recipe usage |
| Quality gate failures | N/A | Caught early | Gate metrics |

---

## Appendix: Marketplace Research Sources

1. [wshobson/agents](https://github.com/wshobson/agents) - 99 agents, 15 orchestrators
2. [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)
3. [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
4. [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
5. [claude-plugins.dev](https://claude-plugins.dev/skills)
6. [skillsmp.com](https://skillsmp.com/)

---

## Decision Requested

**Recommended:** Start with Plan B (Workflow Recipes) as quick win, then iterate.

**Options:**

- A) Implement Plan B only (recipes) - Low risk, immediate value
- B) Implement Plan B + C (recipes + gates) - Medium effort, high value
- C) Full roadmap (B → C → A) - Comprehensive transformation
- D) Plan D (skills-first) - Major redesign, future consideration

**Your workflow suggests:** Option B (recipes + gates) would provide the most value for your ADHD-friendly, automation-focused development style.
