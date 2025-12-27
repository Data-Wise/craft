# Craft Plugin Roadmap

## Current Version: 1.6.0-dev

---

## v1.5.0 - Distribution Commands ✅ RELEASED

### Distribution Commands (All Complete)

#### `/craft:dist:homebrew` - Homebrew Tap Management ✅
- Detect project type (Python, Node, Go, Rust)
- Generate formula file with dependencies
- Calculate SHA256 for release tarballs
- Update existing formula for new versions
- Push to homebrew-tap repository

#### `/craft:dist:curl-install` - Direct GitHub Installation ✅
- Create `install.sh` for direct GitHub downloads
- Support multiple installation methods (binary, source)
- Include version detection and updates
- Add to README installation section

#### Skills Added ✅
- `distribution-strategist` - Distribution channel recommendations
- `homebrew-formula-expert` - Formula best practices

**Stats:** 53 commands, 13 skills, 7 agents

**Dogfooding:** Tested on aiterm v0.3.5
- Generated and validated Homebrew formula
- Created install.sh with smart auto-detection
- Updated README with curl install instructions

---

## v1.4.0 - Orchestrator v2.1 Enhancement ✅ RELEASED

### Orchestrator v2.1 Features (All Complete)

#### Phase 1: Quick Wins ✅

**1. Real Context Tracking** ✅
- Improved heuristics for context usage estimation
- Watch for Claude Code system warnings about context
- Smarter compression triggers based on exchange count + content size
- Per-agent context budget tracking

**2. Mode Integration** ✅
- Orchestrator respects craft mode system
- `default` mode: 2 agents, 70% compression threshold
- `debug` mode: 1 agent (sequential), verbose output, 90% threshold
- `optimize` mode: 4 agents max, aggressive 60% compression
- `release` mode: 4 agents, full reports, 85% threshold

**Usage:**
```bash
/craft:orchestrate "add auth" optimize    # Fast parallel
/craft:orchestrate "prep release" release # Thorough
```

#### Phase 2: State Persistence ✅

**3. Session State File** ✅
- Persist orchestrator state to `.claude/orchestrator-session.json`
- Enable session recovery after disconnects
- Track completed work, active agents, decisions made

**New Commands:**
```bash
/craft:orchestrate continue      # Resume from saved state
/craft:orchestrate save          # Force state save
/craft:orchestrate history       # Show past sessions
```

#### Phase 3: ADHD Enhancements ✅

**4. Timeline View** ✅
- Visual Gantt-style timeline of agent execution
- ETA countdown with progress bars
- Reduces anxiety about "what's happening"

```
TIME     0    1m    2m    3m    4m
─────────┼─────┼─────┼─────┼─────┤
arch-1   ██████░░░░░░░░░░░░░░░░░░ ✅
code-1        ░░░░████████████░░░ 🟡
─────────┼─────┼─────┼─────┼─────┤
                         NOW ▲
```

### Dogfooding Phase (Manual Testing) ✅ COMPLETE

Live validation tests completed on aiterm project:

- [x] **Live orchestrator test** - Added `ait hello` command via `/craft:orchestrate` default mode
- [x] **Stress test** - 4 parallel agents in `optimize` mode added `ait info` + enhanced `--version`
- [x] **Session persistence test** - Added `ait goodbye` via save/resume workflow

**Results:** All tests passed, features shipped in aiterm v0.3.5

---

## v1.6.0 - Release Automation (Future)

- `/craft:dist:pypi` - PyPI publishing workflow
- `/craft:dist:npm` - npm publishing workflow
- `/craft:dist:cargo` - Cargo publishing workflow
- `/craft:dist:release` - Multi-channel release orchestrator
- Agent pool management (max parallel, priority queue, resource budgets)
- Cost tracking per agent

---

## v1.7.0 - CI/CD Integration (Future)

- `/craft:ci:matrix` - Generate test matrix
- `/craft:ci:workflow` - Create GitHub Actions workflows
- `/craft:ci:badge` - Add/update README badges

---

## Ideas Backlog

- Monorepo support for distribution commands
- Version bumping automation
- Changelog-to-release-notes conversion
- Installation verification tests
- Cross-platform binary building
- Agent result caching (reuse recent analysis)
- Cross-session agent continuity

---

## Contributing

To request features, create an issue or add to this roadmap.
