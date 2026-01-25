# Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  CRAFT PLUGIN QUICK REFERENCE                               │
├─────────────────────────────────────────────────────────────┤
│  Version: 2.8.0                                             │
│  Commands: 100 | Agents: 8 | Skills: 21                     │
│  Documentation: 98% complete | Diagrams: 17 Mermaid         │
│  Docs: https://data-wise.github.io/craft/                   │
│  NEW: Markdown linting execution layer with auto-fix        │
└─────────────────────────────────────────────────────────────┘
```

## Essential Commands

| Command | Description |
|---------|-------------|
| `/craft:do <task>` | Universal command - routes to best workflow |
| `/craft:check` | Pre-flight checks (commit/pr/release) |
| `/craft:help` | Context-aware help and suggestions |
| `/craft:hub` | Command discovery hub |

## Smart Documentation (17 commands)

| Command | Description |
|---------|-------------|
| `/craft:docs:lint` | **NEW v2.8.0** Markdown linting with auto-fix support |
| `/craft:docs:update` | **v2.7.0** Interactive: 9 categories, prompts, auto-fix |
| `/craft:docs:update --interactive` | Category-level prompts for precise control |
| `/craft:docs:update --category=NAME` | Update only specific category |
| `/craft:docs:sync` | Detection: Classify changes, report stale docs |
| `/craft:docs:check` | Validation: Links + stale + nav + auto-fix |
| `/craft:docs:website` | ADHD-friendly enhancement with scoring |
| `/craft:docs:guide` | Feature guide + demo + refcard generator |
| `/craft:docs:demo` | VHS tape generator for GIF demos |
| `/craft:docs:mermaid` | Mermaid diagram templates (6 types) |

**Quick examples:**

```bash
/craft:docs:update --interactive          # Interactive mode (9 categories)
/craft:docs:update --category=version_refs # Update only version refs
/craft:docs:update --interactive --dry-run # Preview without changes
/craft:docs:check --report-only           # CI-safe mode
/craft:docs:check-links                   # Validate links
```

**NEW in v2.8.0: Markdown Linting Execution Layer**

- Auto-detect `markdownlint-cli2` globally or use `npx` fallback
- Check markdown: `/craft:docs:lint` (30+ rules configured)
- Auto-fix: `/craft:docs:lint --fix` (apply safe fixes)
- Path targeting: `/craft:docs:lint docs/guide/` (check specific directories)
- Pre-commit integration: Auto-fix on staged markdown
- All 706+ tests passing (100%)
- [Release Notes](../RELEASE-v2.8.0.md) | [Full Docs](../commands/docs/lint.md)

**NEW in v2.7.0: Interactive Documentation Update**

- 9-category detection (version refs, command counts, broken links, etc.)
- Category-level prompts for precise control
- 1,331 real issues detected in craft project
- Production-ready error handling (29/29 tests passing)
- Dry-run preview mode
- [Tutorial](tutorials/interactive-docs-update-tutorial.md) | [Reference](reference/REFCARD-DOCS-UPDATE.md)

## Site Commands (15 commands)

| Command | Description |
|---------|-------------|
| `/craft:site:create` | Full site wizard with 8 ADHD-friendly presets |
| `/craft:site:build` | Build site (teaching-aware) |
| `/craft:site:publish` | **NEW** Preview → Validate → Deploy (teaching mode) |
| `/craft:site:progress` | **NEW** Semester progress dashboard (teaching mode) |
| `/craft:site:nav` | Navigation reorganization (max 7 sections) |
| `/craft:site:audit` | Content inventory & audit |
| `/craft:site:consolidate` | Merge duplicate/overlapping docs |
| `/craft:site:status` | Dashboard and health check |
| `/craft:site:deploy` | Deploy to GitHub Pages |

**Teaching Mode Quick Start:**

```bash
/craft:site:build              # Preview changes
/craft:site:progress           # Check semester status
/craft:site:publish            # Validate & deploy to production
```

**Standard Quick Examples:**

```bash
/craft:site:create --preset data-wise --quick
/craft:site:status
```

## Code & Testing (17 commands)

| Command | Modes | Description |
|---------|-------|-------------|
| `/craft:code:lint` | all | Linting with auto-fix |
| `/craft:test:run` | all | Test runner with watch mode |
| `/craft:code:debug` | - | Systematic debugging |
| `/craft:code:refactor` | - | Refactoring guidance |

**Modes:** `default` (<10s) | `debug` (<120s) | `optimize` (<180s) | `release` (<300s)

**Quick examples:**

```bash
/craft:code:lint optimize       # Parallel, fast
/craft:test:run debug           # Verbose with suggestions
```

## Git Commands (5 commands)

| Command | Description |
|---------|-------------|
| `/craft:git:init` | **NEW** Initialize repository with craft workflow |
| `/craft:git:worktree` | Parallel development with git worktrees |
| `/craft:git:sync` | Smart git sync |
| `/craft:git:clean` | Clean merged branches |
| `/craft:git:recap` | Activity summary |
| `/craft:git:branch` | Branch management |

**Quick examples:**

```bash
/craft:git:init                      # Interactive wizard
/craft:git:init --dry-run            # Preview changes
/craft:git:worktree add feature-auth # Create feature branch
/craft:git:sync                      # Sync with remote
/craft:git:clean                     # Clean merged branches
```

## Orchestrator (Enhanced v2.1, v2.5.0)

```bash
# Traditional method
/craft:orchestrate "add auth" optimize    # Fast parallel (4 agents)
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate status                 # Agent dashboard
/craft:orchestrate timeline               # Execution timeline
/craft:orchestrate continue               # Resume session

# NEW (v2.5.0) - Quick orchestration with --orch flag
/craft:do "add auth" --orch=optimize      # Quick orchestration
/craft:check --orch=release               # Orchestrated validation
/craft:docs:sync --orch=default           # Orchestrated docs sync
/craft:ci:generate --orch=optimize        # Orchestrated CI generation
```

**Features:**

- Mode-aware execution (default/debug/optimize/release)
- Subagent monitoring
- Chat compression
- ADHD-optimized status tracking
- **NEW (v2.5.0)** - --orch flag for quick orchestration

## Workflow Commands (Enhanced v2.4.0)

```bash
# v2.4.0 - Question Control with colon notation
/brainstorm d:5 "auth"              # Deep with exactly 5 questions
/brainstorm m:12 "api"              # Max with 12 questions
/brainstorm q:0 "quick"             # Quick with 0 questions (straight to brainstorming)
/brainstorm d:20 "complex"          # Deep with 20 questions (unlimited mode)

# v2.4.0 - Categories flag to filter question types
/brainstorm d:5 "auth" -C req,tech              # 5 questions from requirements + technical
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
/brainstorm d:8 "feature" -C all                # All 8 categories

# Power user - full control
/brainstorm d:15 f s -C req,tech,success "auth"   # 15 questions, feature, spec, filtered categories
```

**Question Bank (v2.4.0):** 8 categories × 2 questions = 16 total

- requirements, users, scope, technical, timeline, risks, existing, success

**Milestone Prompts:**

- Questions asked in batches of 8
- Continuation options: Done, +4, +8, Keep going
- "Keep going" mode prompts every 4 questions

**Other Workflow Commands:**

```bash
/workflow:focus        # Start focused work session
/workflow:next         # Get next step
/workflow:stuck        # Get unstuck help
/workflow:done         # Complete session
```

## Skills (21 total)

Auto-triggered expertise:

| Skill | Triggers |
|-------|----------|
| `backend-designer` | API, database, auth |
| `frontend-designer` | UI/UX, components |
| `test-strategist` | Test strategy |
| `system-architect` | System design |
| `project-planner` | Feature planning |
| `distribution-strategist` | Homebrew, PyPI, packaging |
| `homebrew-formula-expert` | Homebrew formulas |
| `doc-classifier` | Documentation type detection |
| `mermaid-linter` | Mermaid diagram validation |
| `session-state` | Orchestrator state tracking |
| ...and 11 more | See [Skills & Agents Guide](guide/skills-agents.md) |

## Agents (8 specialized)

| Agent | Specialty |
|-------|-----------|
| `orchestrator-v2` | Mode-aware execution, monitoring |
| `backend-architect` | Scalable APIs, microservices |
| `docs-architect` | Technical documentation |
| `api-documenter` | OpenAPI, developer portals |
| `tutorial-engineer` | Step-by-step tutorials |
| `mermaid-expert` | Diagram creation |
| `reference-builder` | API reference documentation |
| `demo-engineer` | VHS demo creation |

## Configuration

### Mode System

| Mode | Time | Use Case |
|------|------|----------|
| **default** | <10s | Quick checks |
| **debug** | <120s | Verbose output |
| **optimize** | <180s | Parallel, performance |
| **release** | <300s | Comprehensive audit |

### ADHD-Friendly Presets

| Preset | Description |
|--------|-------------|
| `data-wise` | DT's standard (blue/orange) |
| `adhd-focus` | Calm forest green |
| `adhd-calm` | Warm earth tones |
| `adhd-dark` | Dark-first, reduced eye strain |
| `adhd-light` | Warm light, never harsh white |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Verify installation: `/craft:hub` |
| Skill not triggering | Check skill definitions in plugin |
| Build fails | Run `/craft:check` for diagnostics |

## Technical Deep Dives

New comprehensive guides (Phase 3 documentation):

| Guide | Diagrams | Content |
|-------|----------|---------|
| **[Version History](VERSION-HISTORY.md)** | - | Complete timeline v1.0.0 → v2.4.0 with feature evolution |
| **[Claude Code 2.1 Integration](guide/claude-code-2.1-integration.md)** | 9 Mermaid | Hot-reload validators, complexity scoring, orchestration hooks, agent delegation (610 lines) |
| **[Complexity Scoring Algorithm](guide/complexity-scoring-algorithm.md)** | 8 Mermaid | Technical documentation of 0-10 scoring system, decision trees, examples (571 lines) |

**Total:** 17 Mermaid diagrams across all guides

## Links

- **[Full Documentation](guide/getting-started.md)** (95% complete)
- **[GitHub Issues](https://github.com/Data-Wise/craft/issues)**
- **[ROADMAP](https://github.com/Data-Wise/craft/blob/main/ROADMAP.md)**
