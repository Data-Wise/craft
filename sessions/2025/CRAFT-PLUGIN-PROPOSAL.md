# Craft Plugin - Comprehensive Proposal

**Generated:** 2025-12-26
**Status:** Ready for Decision
**Current Version:** 1.0.0 (26 commands, 3 skills, 1 agent)

---

## Executive Summary

The **craft** plugin is now fully installed and operational with 26 commands, 3 skills, and 1 agent. All automated tests pass (13/13). This proposal consolidates all planning documents and presents **5 options** for next development phase.

---

## Current State

### What's Working

| Component | Count | Status |
|-----------|-------|--------|
| Commands | 26 | All valid, installed |
| Skills | 3 | backend-designer, frontend-designer, devops-helper |
| Agents | 1 | orchestrator |
| Tests | 13 | 100% passing |
| Categories | 4 | code, docs, git, site |

### Command Breakdown

```
craft/commands/
├── hub.md                    # Discovery hub
├── code/                     # 6 commands
│   ├── debug.md
│   ├── demo.md
│   ├── docs-check.md
│   ├── refactor.md
│   ├── release.md
│   └── test-gen.md
├── docs/                     # 5 commands
│   ├── changelog.md
│   ├── claude-md.md
│   ├── nav-update.md
│   ├── sync.md
│   └── validate.md
├── git/                      # 8 commands
│   ├── branch.md
│   ├── clean.md
│   ├── recap.md
│   ├── refcard.md
│   ├── safety-rails.md
│   ├── sync.md
│   ├── undo-guide.md
│   └── learning-guide.md
└── site/                     # 6 commands
    ├── build.md
    ├── check.md
    ├── deploy.md
    ├── frameworks.md
    ├── init.md
    └── preview.md
```

---

## Planning Documents Found

| Document | Summary |
|----------|---------|
| BRAINSTORM-PLUGIN-NAMES.md | "craft" chosen from 50+ candidates |
| PROPOSAL-DEV-TOOLS-CREATIVE.md | 5 creative plugin designs (P1-P5) |
| PROPOSAL-DEV-TOOLS-PLUGIN-REVISED.md | Plan A/B/C hybrid approaches |
| MODE-SYSTEM-DESIGN.md | 4 modes: default, debug, optimize, release |
| MODE-SYSTEM-DEPLOYMENT-PLAN.md | 4-phase deployment strategy |
| PROJECT-ROADMAP.md | Long-term vision (Track 1-7) |
| NEXT-WEEK-PLAN.md | Week 2 implementation details |

---

## Option A: Production Testing (1 week)

**Philosophy:** Test craft in real daily usage before adding features.

### What You Do
1. Use craft commands for 1 week on real projects
2. Document friction points and missing features
3. Note which commands are most/least useful
4. Identify gaps in coverage

### Daily Testing Protocol
```bash
# Morning
/craft:git:recap              # What did I work on?
/craft:status                 # Project overview

# Development
/craft:code:debug             # Debug issues
/craft:code:test-gen          # Generate tests
/craft:code:refactor          # Refactoring help

# Documentation
/craft:docs:sync              # Keep docs current
/craft:docs:changelog         # Update CHANGELOG

# End of day
/craft:git:sync               # Commit and push
```

### Deliverables
- TESTING-FEEDBACK-CRAFT.md (usage notes)
- Priority list for Phase 2

### Effort: 5-10 hours (spread over 1 week)
### Risk: Low
### Value: Validate before investing more

---

## Option B: Mode System (3-4 days)

**Philosophy:** Add depth to existing commands with modes.

### Mode System Design
```
┌─────────────────────────────────────────────────────────┐
│                    CRAFT MODES                          │
├─────────────┬──────────────┬───────────────────────────┤
│   Mode      │  Time Budget │  Behavior                 │
├─────────────┼──────────────┼───────────────────────────┤
│  default    │   < 10s      │  Quick analysis, minimal  │
│  debug      │   < 120s     │  Detailed traces, verbose │
│  optimize   │   < 180s     │  Performance focus        │
│  release    │   < 300s     │  Full checks, thorough    │
└─────────────┴──────────────┴───────────────────────────┘
```

### Implementation Plan

**Day 1: Core Commands (4-5 hours)**
- Update code/ commands with mode support
- Add mode parameter to frontmatter
- Adjust behavior per mode

**Day 2: Documentation Automation (3-4 hours)**
- Update docs/ commands with modes
- Validate mode + format combinations
- Add mode examples

**Day 3: Testing & Validation (3-4 hours)**
- Create mode tests
- Verify time budgets
- Performance benchmarks

**Day 4: Integration (2-3 hours)**
- End-to-end testing
- Documentation updates
- Release notes

### Example Usage
```bash
/craft:code:debug                 # Quick debug (default mode)
/craft:code:debug debug           # Deep debugging with traces
/craft:code:release release       # Full release checks
/craft:docs:validate optimize     # Performance-focused validation
```

### Effort: 12-16 hours
### Risk: Medium (proven pattern from rforge)
### Value: Deeper, configurable analysis

---

## Option C: Smart Orchestrator (2-3 days)

**Philosophy:** Let AI figure out what to do.

### Concept
Add 4 intelligent entry points that auto-detect needs:

```bash
/craft:do <task>      # Universal command
/craft:plan <feature> # Intelligent planning
/craft:check          # Pre-flight for anything
/craft:help <topic>   # Context-aware help
```

### How It Works

**`/craft:do <task>`** - The Universal Command
```
User: /craft:do add authentication

AI analyzes:
  → Backend task detected
  → Security concern identified
  → Tests needed
  → Documentation required

Executes:
  1. /craft:code:design (architecture)
  2. /craft:code:test-gen (tests)
  3. /craft:docs:sync (documentation)
  4. /craft:git:branch (feature branch)
```

**`/craft:plan <feature>`** - Intelligent Planning
```
User: /craft:plan user dashboard

AI generates:
  - Architecture diagram
  - API endpoints
  - UI components
  - Test plan
  - Implementation steps
```

**`/craft:check`** - Universal Pre-flight
```
Detects project type and runs:
  - R package → R CMD check
  - Python → pytest + type check
  - Node → npm test + lint
  - Docs → link validation
  - Git → status, conflicts
```

### Implementation
1. Create task-analyzer skill
2. Create smart-orchestrator agent
3. Add 4 new commands
4. Test with real projects

### Effort: 10-15 hours
### Risk: Medium-High (less predictable)
### Value: Minimal cognitive load, AI handles routing

---

## Option D: Full Enhancement (1-2 weeks)

**Philosophy:** Everything - modes, orchestrator, new commands.

### Phase 1: Mode System (Days 1-4)
- Add modes to all 26 commands
- Time budget enforcement
- Format options (terminal, json, markdown)

### Phase 2: Smart Orchestrator (Days 5-7)
- 4 intelligent entry points
- Task analyzer skill
- Plugin router skill

### Phase 3: New Commands (Days 8-10)
```
craft/commands/
├── arch/                     # NEW - Architecture (4)
│   ├── analyze.md
│   ├── plan.md
│   ├── review.md
│   └── diagram.md
├── test/                     # NEW - Testing (4)
│   ├── run.md
│   ├── watch.md
│   ├── coverage.md
│   └── debug.md
└── plan/                     # NEW - Planning (3)
    ├── feature.md
    ├── sprint.md
    └── roadmap.md
```

### Phase 4: Polish (Days 11-14)
- Command aliases
- Error message improvements
- Documentation updates
- Real-world validation

### Final Count: 37 commands, 6 skills, 2 agents

### Effort: 30-40 hours
### Risk: High (large scope)
### Value: Comprehensive full-stack toolkit

---

## Option E: Full Stack Dev (Comprehensive)

**Philosophy:** Everything a full-stack developer needs in one plugin.

### Concept
Comprehensive plugin with **all development capabilities**:
- Import workflow skills (backend, frontend, devops)
- Import orchestrator agent
- Add testing, architecture, planning
- Migrate ALL user commands

### Structure
```
craft/
├── commands/
│   ├── hub.md                    # Discovery
│   │
│   ├── code/                     # Development (12)
│   │   ├── debug.md
│   │   ├── demo.md
│   │   ├── docs-check.md
│   │   ├── refactor.md
│   │   ├── release.md
│   │   ├── test-gen.md
│   │   ├── lint.md               # NEW
│   │   ├── coverage.md           # NEW
│   │   ├── deps-check.md         # NEW
│   │   ├── deps-audit.md         # NEW
│   │   ├── ci-local.md           # NEW
│   │   └── ci-fix.md             # NEW
│   │
│   ├── site/                     # Documentation sites (6)
│   │   └── [migrated]
│   │
│   ├── git/                      # Git operations (8)
│   │   └── [migrated]
│   │
│   ├── docs/                     # Docs automation (5)
│   │   ├── sync.md
│   │   ├── changelog.md
│   │   ├── claude-md.md
│   │   ├── validate.md
│   │   └── nav-update.md
│   │
│   ├── test/                     # Testing (4) NEW
│   │   ├── run.md                # Unified test runner
│   │   ├── watch.md              # Watch mode
│   │   ├── coverage.md           # Coverage report
│   │   └── debug.md              # Debug failing tests
│   │
│   ├── arch/                     # Architecture (4) NEW
│   │   ├── analyze.md            # Architecture analysis
│   │   ├── plan.md               # Design planning
│   │   ├── review.md             # Architecture review
│   │   └── diagram.md            # Generate diagrams
│   │
│   └── plan/                     # Planning (3) NEW
│       ├── feature.md            # Feature planning
│       ├── sprint.md             # Sprint planning
│       └── roadmap.md            # Roadmap generation
│
├── skills/
│   ├── design/                   # Import from workflow
│   │   ├── backend-designer.md
│   │   ├── frontend-designer.md
│   │   └── devops-helper.md
│   ├── testing/
│   │   └── test-strategist.md    # NEW
│   ├── architecture/
│   │   └── system-architect.md   # NEW
│   └── planning/
│       └── project-planner.md    # NEW
│
└── agents/
    └── orchestrator.md           # Import from workflow
```

### Commands (42 total)
| Category | Count | Source |
|----------|-------|--------|
| Code | 12 | 6 migrated + 6 new |
| Site | 6 | Migrated |
| Git | 8 | Migrated |
| Docs | 5 | Current |
| Test | 4 | New |
| Arch | 4 | New |
| Plan | 3 | New |

### Skills (6 total)
- **Imported:** backend-designer, frontend-designer, devops-helper
- **New:** test-strategist, system-architect, project-planner

### Effort: 1-2 days
### Risk: Medium
### Pros: Complete, cohesive, self-contained
### Cons: Larger maintenance burden, some overlap with marketplace

---

## Comparison Matrix

| Aspect | Option A | Option B | Option C | Option D | Option E |
|--------|----------|----------|----------|----------|----------|
| **Effort** | 5-10 hrs | 12-16 hrs | 10-15 hrs | 30-40 hrs | 8-16 hrs |
| **Risk** | Low | Medium | Med-High | High | Medium |
| **New Commands** | 0 | 0 | 4 | 11 | 16 |
| **Final Commands** | 26 | 26 | 30 | 37 | 42 |
| **New Skills** | 0 | 0 | 1 | 3 | 3 |
| **Innovation** | None | Moderate | High | Highest | High |
| **ADHD-Friendly** | Yes | Yes | Very | Very | Very |
| **Ship Time** | 1 week | 3-4 days | 2-3 days | 1-2 weeks | 1-2 days |
| **Self-Contained** | Yes | Yes | No | Yes | Yes |
| **Validation** | Thorough | Some | Less | Minimal | Some |

---

## Recommendation

### Best Value: Option E (Full Stack Dev)
**Why:** 42 commands in 1-2 days, complete self-contained toolkit

- Adds 16 new commands (code/6, test/4, arch/4, plan/3)
- 3 new skills (test-strategist, system-architect, project-planner)
- Everything a full-stack developer needs
- Medium risk, high reward

### Alternative: Phased Approach

**Week 1: Option A (Testing)**
- Use craft for real work
- Document feedback
- Identify priorities

**Week 2: Option E (Full Stack Dev)**
- Implement all new commands
- Add skills and structure
- Complete toolkit ready

**Week 3: Option B (Modes) + Option C (Orchestrator)**
- Add mode system for depth
- Add smart entry points
- AI-native experience

---

## Quick Wins (Start Now)

If you have limited time, pick one:

### Quick Win 1: Test Hub Command (5 min)
```bash
/craft:hub
# See all available commands
```

### Quick Win 2: Try Code Commands (10 min)
```bash
/craft:code:debug
/craft:code:test-gen
```

### Quick Win 3: Documentation Sync (10 min)
```bash
/craft:docs:sync
/craft:docs:validate
```

### Quick Win 4: Git Workflow (10 min)
```bash
/craft:git:recap
/craft:git:sync
```

---

## Decision Required

Choose your path:

| Choice | Description | Commands | Time |
|--------|-------------|----------|------|
| **A** | Test first, decide later | 26 | 1 week |
| **B** | Add mode system | 26 | 3-4 days |
| **C** | Add smart orchestrator | 30 | 2-3 days |
| **D** | Full enhancement (phased) | 37 | 1-2 weeks |
| **E** | Full Stack Dev (recommended) | 42 | 1-2 days |
| **A+E** | Test, then Full Stack | 42 | 1.5 weeks |
| **A+E+B** | Test, Full Stack, then Modes | 42 | 2 weeks |

---

## Next Steps by Choice

### If A (Testing):
1. Start using craft commands today
2. Create TESTING-FEEDBACK-CRAFT.md
3. Document for 1 week
4. Review and decide

### If B (Modes):
1. Review MODE-SYSTEM-DESIGN.md
2. Update command frontmatter
3. Add mode parameter handling
4. Test time budgets

### If C (Orchestrator):
1. Create task-analyzer skill
2. Create smart-orchestrator agent
3. Add 4 new commands
4. Test with real projects

### If D (Full Enhancement):
1. Follow Week 2 plan from NEXT-WEEK-PLAN.md
2. Implement in phases
3. Test each phase
4. Document as you go

### If E (Full Stack Dev) - RECOMMENDED:
1. **Day 1 Morning: Code Commands (3-4 hours)**
   - Add 6 new code/ commands: lint, coverage, deps-check, deps-audit, ci-local, ci-fix
   - Test each command

2. **Day 1 Afternoon: New Categories (3-4 hours)**
   - Create test/ directory with 4 commands
   - Create arch/ directory with 4 commands
   - Create plan/ directory with 3 commands

3. **Day 2 Morning: Skills (2-3 hours)**
   - Create testing/test-strategist.md
   - Create architecture/system-architect.md
   - Create planning/project-planner.md

4. **Day 2 Afternoon: Integration (2-3 hours)**
   - Update hub.md with new commands
   - Run automated tests
   - Update documentation

---

## Files for Reference

| Document | Purpose |
|----------|---------|
| craft/README.md | Command overview |
| BRAINSTORM-PLUGIN-NAMES.md | Name decision history |
| PROPOSAL-DEV-TOOLS-CREATIVE.md | 5 design proposals |
| MODE-SYSTEM-DESIGN.md | Mode specification |
| NEXT-WEEK-PLAN.md | Implementation details |
| PROJECT-ROADMAP.md | Long-term vision |

---

**Last Updated:** 2025-12-26
**Status:** Ready for decision
**Recommendation:** Option E (Full Stack Dev) - 42 commands in 1-2 days, complete self-contained toolkit
