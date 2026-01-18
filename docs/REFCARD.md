# Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  CRAFT PLUGIN QUICK REFERENCE                               │
├─────────────────────────────────────────────────────────────┤
│  Version: 1.24.0                                            │
│  Commands: 97 | Agents: 8 | Skills: 21                      │
│  Documentation: 95% complete | Diagrams: 17 Mermaid         │
│  Docs: https://data-wise.github.io/craft/                   │
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
| `/craft:docs:update` | Smart-Full: Detect → Generate → Check → Changelog |
| `/craft:docs:sync` | Detection: Classify changes, report stale docs |
| `/craft:docs:check` | Validation: Links + stale + nav + auto-fix |
| `/craft:docs:website` | **NEW** ADHD-friendly enhancement with scoring |
| `/craft:docs:guide` | Feature guide + demo + refcard generator |
| `/craft:docs:demo` | VHS tape generator for GIF demos |
| `/craft:docs:mermaid` | Mermaid diagram templates (6 types) |

**Quick examples:**
```bash
/craft:docs:update                    # Full smart cycle
/craft:docs:website --phase 1         # Quick wins: TL;DR, mermaid fixes
/craft:docs:check --report-only       # CI-safe mode
/craft:docs:check-links               # Validate links (supports .linkcheck-ignore)
```

**NEW in v1.23.0: .linkcheck-ignore Support**
- Document expected broken links (test files, brainstorm refs)
- CI passes with expected links (exit code 0)
- Only fails on critical broken links (exit code 1)
- Create `.linkcheck-ignore` in project root with patterns

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

## Orchestrator (Enhanced v2.1)

```bash
/craft:orchestrate "add auth" optimize    # Fast parallel (4 agents)
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate status                 # Agent dashboard
/craft:orchestrate timeline               # Execution timeline
/craft:orchestrate continue               # Resume session
```

**Features:**
- Mode-aware execution
- Subagent monitoring
- Chat compression
- ADHD-optimized status tracking

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
| **[Claude Code 2.1 Integration](guide/claude-code-2.1-integration.md)** | 9 Mermaid | Hot-reload validators, complexity scoring, orchestration hooks, agent delegation (610 lines) |
| **[Complexity Scoring Algorithm](guide/complexity-scoring-algorithm.md)** | 8 Mermaid | Technical documentation of 0-10 scoring system, decision trees, examples (571 lines) |
| **[Version History](VERSION-HISTORY.md)** | - | Complete timeline v1.0.0 → v1.24.0 with feature evolution (428 lines) |

**Total:** 17 Mermaid diagrams across all guides

## Links

- **[Full Documentation](guide/getting-started.md)** (95% complete)
- **[GitHub Issues](https://github.com/Data-Wise/craft/issues)**
- **[ROADMAP](https://github.com/Data-Wise/craft/blob/main/ROADMAP.md)**
