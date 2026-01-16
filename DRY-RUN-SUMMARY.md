# Dry-Run Support Summary

**Last Updated:** 2026-01-16
**Status:** 22/90 commands support dry-run (24%)
**Target:** 47/90 commands (52%) for v1.20.0

---

## ✅ Commands WITH Dry-Run Support (22)

### Git Commands (6/6) — 100% COMPLETE ✅
- ✅ `/craft:git:branch` - Branch operations (create, delete, list)
- ✅ `/craft:git:clean` - Delete merged branches (CRITICAL)
- ✅ `/craft:git:git-recap` - Activity summary (7 git commands)
- ✅ `/craft:git:init` - Repository initialization
- ✅ `/craft:git:sync` - Sync with remote
- ✅ `/craft:git:worktree` - Worktree operations (HIGH)

### CI/CD Commands (3/3) — 100% COMPLETE ✅
- ✅ `/craft:ci:detect` - Project type detection (60+ patterns)
- ✅ `/craft:ci:generate` - Workflow generation (CRITICAL)
- ✅ `/craft:ci:validate` - CI validation

### Site Commands (4/6) — 67%
- ✅ `/craft:site:build` - Site build
- ✅ `/craft:site:check` - Validation checks
- ✅ `/craft:site:deploy` - GitHub Pages deploy (CRITICAL)
- ✅ `/craft:site:update` - Site updates

### Docs Commands (5/10) — 50%
- ✅ `/craft:docs:changelog` - Changelog generation
- ✅ `/craft:docs:check` - Health check
- ✅ `/craft:docs:claude-md` - CLAUDE.md generation
- ✅ `/craft:docs:nav-update` - Navigation updates
- ✅ `/craft:docs:sync` - Documentation sync

### Distribution (1/4) — 25%
- ✅ `/craft:dist:pypi` - PyPI automation (CRITICAL)

### Smart Routing (3/4) — 75%
- ✅ `/craft:check` - Universal pre-flight
- ✅ `/craft:do` - Universal routing
- ✅ `/craft:orchestrate` - Multi-agent orchestration

---

## ❌ Commands WITHOUT Dry-Run Support (68)

### Priority for v1.20.0 Target (26 remaining)

#### Code Commands (12 needed)
- `/craft:code:lint` - Linting
- `/craft:code:refactor` - Refactoring suggestions
- `/craft:code:review` - Code review
- `/craft:code:ci-fix` - CI fixes
- `/craft:code:ci-local` - Local CI simulation
- `/craft:code:deps-audit` - Dependency audit
- `/craft:code:format` - Code formatting
- ... and 5 more

#### Architecture Commands (7 needed)
- `/craft:arch:analyze` - Architecture analysis
- `/craft:arch:plan` - Feature planning
- `/craft:arch:diagram` - Architecture diagrams
- `/craft:workflow:brainstorm` - Brainstorming
- `/craft:workflow:spec-review` - Spec review
- ... and 2 more

#### Workflow Commands (2 needed)
- `/craft:workflow:*` - Various workflow commands

#### Other Medium Priority (5 needed)
- Distribution commands (3)
- Documentation commands (2)

### Lower Priority (42 commands)

#### Test Commands (12 total)
- `/craft:test:run` - Test execution
- `/craft:test:coverage` - Coverage analysis
- `/craft:test:debug` - Test debugging
- `/craft:test:cli-run` - CLI test runner
- `/craft:test:cli-gen` - CLI test generation
- ... and 7 more

#### Site Commands (2 remaining)
- `/craft:site:preview` - Local preview
- `/craft:site:frameworks` - Framework detection

#### Docs Commands (5 remaining)
- `/craft:docs:guide` - Guide generation
- `/craft:docs:refcard` - Reference card
- `/craft:docs:update` - Update documentation
- `/craft:docs:validate` - Validation
- `/craft:docs:api` - API documentation

#### Distribution (3 remaining)
- `/craft:dist:homebrew` - Homebrew formula
- `/craft:dist:curl-install` - Curl installer
- `/craft:dist:npm` - NPM publishing

#### Help & Navigation (22 total)
- `/craft:help` - Help system
- `/craft:hub` - Command discovery
- Various category-specific help commands
- Not prioritized for v1.20.0 target

---

## Coverage by Priority

| Priority | With Dry-Run | Total | Percentage |
|----------|--------------|-------|------------|
| **CRITICAL** | 3 | 3 | 100% ✅ |
| **HIGH** | 1 | 1 | 100% ✅ |
| **P0** | 6 | 6 | 100% ✅ |
| **MEDIUM** | 12 | 43 | 28% |
| **LOW** | 0 | 37 | 0% |
| **Total** | **22** | **90** | **24%** |

## Target Progress

```
Current:  22/90 (24% of all commands)
Target:   47/90 (52% of all commands)
Needed:   25 more commands

Breakdown of 25 needed:
- Code/Test: 12 commands
- Architecture: 7 commands
- Workflow: 2 commands
- Other Medium: 4 commands
```

## Completion Milestones

- ✅ **Phase 1:** Infrastructure + Git commands (4)
- ✅ **Phase 2:** CI/Site/Docs commands (9)
- 🔄 **Phase 3:** Smart routing + P0 (5) — PR #8 open
- ⏳ **Phase 4:** Code/Test commands (12)
- ⏳ **Phase 5:** Architecture commands (7)
- ⏳ **Phase 6:** Final medium priority (4)

## Key Achievements

✅ All CRITICAL priority commands: 100%
✅ All HIGH priority commands: 100%
✅ All P0 priority commands: 100%
✅ Git command category: 100%
✅ CI/CD command category: 100%
✅ Smart routing commands: 75%

---

**Next:** Phase 4 targeting code/test commands for broader dry-run coverage
