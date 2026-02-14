# SPEC: Insights-Driven Command & Skill Improvements

**Date:** 2026-02-14
**Status:** Approved
**Author:** DT + Claude
**From Brainstorm:** `docs/brainstorm/BRAINSTORM-insights-driven-improvements-2026-02-14.md`

## Overview

Based on the /insights report (97 sessions, 153h, 236 commits over 10 days), update 4 existing commands/skills and create 2 new skills to reduce the top friction patterns: wrong-approach errors (21 events), branch guard false positives (6+ sessions), and repetitive release pipeline interactions (10+ sessions).

## Primary User Story

**As a** craft user running Claude Code sessions daily,
**I want** craft commands that automatically front-load context, self-correct during releases, validate worktree paths, and audit branch guard friction,
**So that** I spend less time course-correcting Claude's wrong approaches and more time on actual development.

### Acceptance Criteria

- [ ] `/craft:check --context` outputs session header (worktree, branch, phase, test command)
- [ ] `/release --autonomous` completes without user prompts (pauses only on fatal errors)
- [ ] `/craft:git:worktree --validate` verifies CWD matches expected worktree
- [ ] PreToolUse hook warns when writes target wrong directory (main repo vs worktree)
- [ ] `/craft:guard:audit` generates friction report + proposed config changes
- [ ] `/craft:insights:apply` extracts CLAUDE.md suggestions from insights report
- [ ] `/craft:orchestrate --swarm` creates isolated worktrees per agent

## Secondary User Stories

**As a** craft user starting a new session in a worktree,
**I want** `/craft:check --context` to output the worktree path, branch, and expected test command,
**So that** Claude has the right context from the start and doesn't write files to the wrong directory.

**As a** craft user releasing a new version,
**I want** `/release --autonomous` to auto-detect the version, run checks, create PRs, and merge without me confirming each step,
**So that** I can kick off a release and only intervene if something actually breaks.

**As a** craft user frustrated by branch guard false positives,
**I want** `/craft:guard:audit` to analyze my guard config and tell me which patterns are too aggressive,
**So that** I can tune the guard without manually reading 740 lines of bash.

## Architecture

### Integration Map

```
Existing Commands/Skills          New Additions
─────────────────────────         ─────────────
/craft:check                      /craft:guard:audit (NEW SKILL)
  └── --context (NEW FLAG)        /craft:insights:apply (NEW SKILL)
  └── --for release (existing)
                                  PreToolUse hook update
/release                            └── worktree path validation
  └── --autonomous (NEW FLAG)
  └── --dry-run (existing)

/craft:git:worktree
  └── --validate (NEW FLAG)
  └── create/finish (existing)

/craft:orchestrate
  └── --swarm (NEW FLAG)
  └── --dry-run (existing)
```

### Change 1: `/craft:check --context`

**Integration point:** `commands/check.md` — add new argument + new behavior section

**Current state:** check.md already detects project type, build tool, worktree status, guard status, git status in Step 0. The `--context` flag would output ONLY this detection info as a session header — no checks executed.

**What to add to check.md:**

1. New argument in frontmatter:

   ```yaml
   - name: context
     description: Output session context header only (no checks)
     required: false
     default: false
   ```

2. New section after "Step 0: Show Check Plan":

   ```
   ### Context-Only Mode (--context)

   When `--context` is passed, skip all checks. Output only:

   ┌───────────────────────────────────────────────────────────────┐
   │ SESSION CONTEXT                                               │
   ├───────────────────────────────────────────────────────────────┤
   │ Project:   craft (Claude Code plugin)                         │
   │ Branch:    feature/my-feature                                 │
   │ Worktree:  ~/.git-worktrees/craft/feature-my-feature          │
   │ Base:      dev                                                │
   │ Guard:     Active (smart mode on dev)                         │
   │ Phase:     implementation (commits ahead of dev: 3)           │
   │ Tests:     python3 tests/test_craft_plugin.py (1504 passing)  │
   │ Lint:      npx markdownlint-cli2 "**/*.md"                    │
   ├───────────────────────────────────────────────────────────────┤
   │ TIP: Front-load this context in prompts to reduce wrong-      │
   │ approach friction.                                            │
   └───────────────────────────────────────────────────────────────┘
   ```

3. Phase detection logic:
   - `implementation`: commits ahead of base, no PR exists
   - `testing`: test files modified recently
   - `pr-prep`: all tests pass, branch is clean
   - `release`: on dev branch, features merged

**Why this integrates cleanly:** Step 0 already gathers all this info. `--context` just outputs it and exits early — zero overlap with existing check behavior.

### Change 2: `/release --autonomous`

**Integration point:** `skills/release/SKILL.md` — add new argument + modify interaction points

**Current interaction points (3):**

1. Step 1, line 92: "Ask the user to confirm the version before proceeding"
2. Step 6, line 179: "use `--admin` only after user confirmation"
3. Error recovery: stop and report

**What `--autonomous` changes:**

| Step | Normal | Autonomous |
|------|--------|------------|
| Step 1 (version) | AskUserQuestion to confirm | Auto-select from commit analysis, show decision |
| Step 2 (pre-flight) | Same | Same (fail = abort, no retry) |
| Step 3-5 (bump, commit, PR) | Same | Same (deterministic) |
| Step 6 (merge) | User confirms --admin if blocked | Auto-use --admin, log the override |
| Step 7-8 (release, deploy) | Same | Same (deterministic) |
| Errors | Stop and report | Retry once (step-level), then abort with report |

**What to add to SKILL.md:**

1. New argument in frontmatter:

   ```yaml
   - name: autonomous
     description: Run without user prompts, auto-resolve where possible
     required: false
     default: false
     alias: --auto
   ```

2. New section "Autonomous Mode":

   ```
   ### Autonomous Mode (--autonomous)

   When --autonomous is passed:
   - Version: Auto-detect from commits (patch/minor/major). Show
     the decision but do NOT ask for confirmation.
   - Branch protection: Auto-use --admin if blocked. Log the override.
   - Errors: Retry the failing step once. If it fails again, abort
     and output a full error report.
   - Still outputs box-drawing progress (not silent).
   - Still respects --dry-run (--autonomous --dry-run shows what
     autonomous mode WOULD do).

   Approval gates that ALWAYS pause (even in autonomous):
   - None. Fully autonomous. User trusts the pipeline.

   Safety: --autonomous refuses to run if working tree is dirty
   or if the current branch is not dev.
   ```

**Why this integrates cleanly:** The 3 interaction points are well-isolated. `--autonomous` just skips the AskUserQuestion calls and uses defaults. The pipeline structure doesn't change.

### Change 3: `/craft:git:worktree --validate`

**Integration point:** `commands/git/worktree.md` — add new action

**Current actions:** setup, create, move, list, clean, install, finish

**What to add:**

1. New argument (action value):

   ```
   /craft:git:worktree validate    # Verify CWD matches expected worktree
   ```

2. Validation checks:
   - Is CWD inside a git worktree? (`git rev-parse --show-toplevel`)
   - Does the worktree path match `~/.git-worktrees/<project>/<branch>`?
   - Is the branch name consistent with the folder name?
   - Are there file writes in this session that went outside the worktree?

3. Output:

   ```
   ┌───────────────────────────────────────────────────────────────┐
   │ WORKTREE VALIDATION                                           │
   ├───────────────────────────────────────────────────────────────┤
   │ CWD:       ~/.git-worktrees/craft/feature-auth                │
   │ Branch:    feature/auth                                       │
   │ Toplevel:  ~/.git-worktrees/craft/feature-auth                │
   │ Main repo: ~/projects/dev-tools/craft                         │
   ├───────────────────────────────────────────────────────────────┤
   │ ✅ CWD is inside expected worktree                             │
   │ ✅ Branch matches folder name                                  │
   │ ✅ No writes detected outside worktree                         │
   └───────────────────────────────────────────────────────────────┘
   ```

**Why this integrates cleanly:** It's a new action (like `list` or `clean`) that doesn't affect existing actions. Read-only, no confirmation needed.

### Change 4: PreToolUse Hook — Worktree Path Validation

**Integration point:** `.claude-plugin/hooks/pretooluse.py` — add worktree check

**Current hook behavior:** The PreToolUse hook in craft runs `pretooluse.py` which currently tracks tool usage for the HUD. Adding worktree validation here means it runs on EVERY Write/Edit call.

**Logic:**

```python
# Only check if we're in a worktree
if os.environ.get('CLAUDE_TOOL_NAME') in ('Write', 'Edit'):
    file_path = json.loads(os.environ.get('CLAUDE_TOOL_INPUT', '{}')).get('file_path', '')
    worktree_root = subprocess.run(
        ['git', 'worktree', 'list', '--porcelain'],
        capture_output=True, text=True
    ).stdout

    # If current dir is a worktree, check file_path is inside it
    cwd = os.getcwd()
    toplevel = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True, text=True
    ).stdout.strip()

    if '/.git-worktrees/' in cwd and file_path and not file_path.startswith(toplevel):
        print(f"WARNING: Writing outside worktree. File: {file_path}", file=sys.stderr)
        print(f"Expected: files inside {toplevel}", file=sys.stderr)
```

**Why this integrates cleanly:** PreToolUse hooks are additive — a new check doesn't break existing checks. The warning is non-blocking (stderr message, not exit code 1).

### Change 5: `/craft:guard:audit` (NEW SKILL)

**Integration point:** `skills/guard-audit/SKILL.md` — new file

**Builds on:**

- `scripts/branch-guard.sh` (740 lines, the guard itself)
- `tests/test_branch_guard.sh` (94 tests, 1256 lines)
- `tests/test_branch_guard_e2e.sh` (31 tests, 663 lines)
- `.claude/branch-guard.json` (per-project config)

**Skill structure:**

```
skills/guard-audit/
└── SKILL.md
```

**What it does:**

1. **Discovery:** Read branch-guard.sh, extract all regex patterns and detection rules
2. **Friction analysis:** For each rule, identify scenarios where it false-positives:
   - PR body text containing command strings as documentation
   - Force-push on rebased feature branches (not dev/main)
   - Write-through detection on variables in paths
   - File extension detection on generated files
3. **Test harness:** Generate 10+ test scenarios and run them:
   - Create PR with "git reset --hard" in description (should NOT trigger)
   - Force-push a rebased feature branch (should NOT trigger on feature/*)
   - Write config file on dev (should allow .json/.yaml)
   - etc.
4. **Report:** Output friction report with proposed config changes
5. **Apply:** If user approves, update `.claude/branch-guard.json`

**Trigger words:** "audit guard", "guard friction", "tune guard", "guard false positives"

### Change 6: `/craft:insights:apply` (NEW SKILL)

**Integration point:** `skills/insights-apply/SKILL.md` — new file

**Builds on:**

- `~/.claude/usage-data/report.html` (insights report)
- `~/.claude/usage-data/facets/` (structured data)
- `utils/claude_md_sync.py` (4-phase CLAUDE.md sync pipeline)
- `utils/claude_md_optimizer.py` (budget enforcement)

**Skill structure:**

```
skills/insights-apply/
└── SKILL.md
```

**What it does:**

1. **Parse:** Read insights report, extract `claude_md_additions` array
2. **Present:** Show each suggestion with context:

   ```
   Suggestion 1/4: Branch Guard & Git Hooks
   Source: 6+ sessions with branch guard friction

   Proposed CLAUDE.md addition:
   ┌─────────────────────────────────────────────────────────────┐
   │ ## Branch Guard & Git Hooks                                  │
   │ - Never include literal destructive git commands in PR        │
   │   bodies — branch guard hooks will flag them.                │
   │ - If a branch guard blocks an operation, don't retry.        │
   │ - Never force-push to protected branches.                    │
   └─────────────────────────────────────────────────────────────┘

   [Apply] [Skip] [Edit first]
   ```

3. **Apply:** Use claude_md_sync.py to insert approved sections
4. **Budget check:** Run claude_md_optimizer.py to ensure budget compliance
5. **Report:** Summary of applied/skipped suggestions

**Trigger words:** "apply insights", "insights to rules", "update rules from insights"

### Change 7: `/craft:orchestrate --swarm`

**Integration point:** `commands/orchestrate.md` — add new argument + new execution mode

**Current state:** Orchestrate reads ORCHESTRATE files and delegates to agents in waves (parallel groups). All agents run in the SAME directory (forked context).

**What `--swarm` changes:**

| Aspect | Normal | Swarm |
|--------|--------|-------|
| Agent isolation | Forked context (same dir) | Separate worktrees |
| File conflicts | Possible (same files) | Impossible (isolated) |
| Convergence | Agents return results to main | Branches merged into feature branch |
| PR | User creates manually | Auto-created from merged branch |
| Use case | Research + small changes | Parallel feature implementation |

**What to add:**

1. New argument:

   ```yaml
   - name: swarm
     description: Run agents in isolated worktrees with branch convergence
     required: false
     default: false
   ```

2. Swarm execution flow:

   ```
   /craft:orchestrate --swarm "implement auth"

   Step 1: Create base worktree branch: feature/swarm-auth
   Step 2: For each agent in ORCHESTRATE file:
     - git worktree add ~/.git-worktrees/<proj>/swarm-<agent> -b swarm-<agent> dev
   Step 3: Launch agents in parallel (each in its worktree)
   Step 4: Wait for all agents to complete
   Step 5: Merge all swarm-* branches into feature/swarm-auth
   Step 6: Run tests in merged branch
   Step 7: Create PR to dev
   ```

3. Swarm ORCHESTRATE format (extended):

   ```markdown
   ## Swarm Configuration

   | Agent | Worktree | Focus | Files |
   |-------|----------|-------|-------|
   | tests | swarm-tests | Write tests | tests/ |
   | impl | swarm-impl | Implementation | src/ |
   | docs | swarm-docs | Documentation | docs/, README.md |
   ```

**Why this needs careful thought:** Swarm mode is fundamentally different from normal orchestration. Agents in worktrees can't see each other's changes. The convergence merge could have conflicts. This is the highest-complexity change and should be implemented last.

### Change 8: Super Command Updates (do.md, smart-help.md, hub.md)

Three "super commands" route users to other commands/skills. They need awareness of the new skills and flags.

#### 8a: `/craft:do` — Routing Table Updates (`commands/do.md`)

**New routing entries** (add to Task Categories table and routing logic):

| Keyword Pattern | Routes To | Score | Context |
|-----------------|-----------|-------|---------|
| "audit guard", "guard friction", "tune guard", "guard false positives" | `/craft:guard:audit` | 2 (skill) | Branch guard frustration detected |
| "apply insights", "insights to rules", "update rules from insights" | `/craft:insights:apply` | 2 (skill) | Insights data exists |
| "release" + "--autonomous" or "auto release" | `/release --autonomous` | 4 (skill) | On dev branch, clean tree |
| "check context", "session context" | `/craft:check --context` | 0 (command) | Session start |
| "validate worktree" | `/craft:git:worktree validate` | 0 (command) | In worktree |
| "swarm", "parallel agents" + orchestrate pattern | `/craft:orchestrate --swarm` | 8 (orchestrator) | ORCHESTRATE file exists |

**Agent selection update** (add to Step 3 in Implementation section):

```python
# New skill-based routing (score 1-3, skill invocation)
if any(word in keywords for word in ["audit", "guard", "tune", "friction"]):
    if "guard" in keywords:
        return "skill:guard-audit"  # Direct skill invocation

if any(word in keywords for word in ["insights", "rules"]):
    if any(word in keywords for word in ["apply", "update"]):
        return "skill:insights-apply"  # Direct skill invocation
```

#### 8b: `/craft:help` — Context-Aware Suggestions (`commands/smart-help.md`)

**New state-based suggestions:**

**Branch guard friction detected** (guard blocked an operation recently):

```
Suggested:
  /craft:guard:audit        Analyze guard config, find false positives
  /craft:git:unprotect      Session-scoped bypass (temporary)
```

**Session start** (new session, no prior context):

```
Suggested:
  /craft:check --context    Front-load session context (branch, worktree, phase)
```

**In a worktree** (CWD is inside `~/.git-worktrees/`):

```
Suggested:
  /craft:git:worktree validate   Verify worktree path is correct
  /craft:check --context         Show session context header
```

**Insights data exists** (`~/.claude/usage-data/report.html` present):

```
Suggested:
  /craft:insights:apply     Apply insights suggestions to CLAUDE.md
```

**Release preparation** (on dev, features merged):

```
Suggested:
  /release                  Interactive release pipeline
  /release --autonomous     Fully automated release (no prompts)
  /release -n               Dry-run preview
```

#### 8c: `/craft:hub` — Discovery Hub Updates (`commands/hub.md`)

**Count updates:**

- Line 73: Change `21 Skills` → `25 Skills` (currently shows 21, already behind at 23, will be 25)
- Update Quick Reference header: `100 COMMANDS` → `108 COMMANDS`

**New entries in Skills section** (currently at line 611):

| Skill | Category | Triggers On |
|-------|----------|-------------|
| `guard-audit` | DevOps | Guard friction, false positives, tune guard |
| `insights-apply` | Workflow | Insights report, CLAUDE.md rules, apply suggestions |
| `release` | Release | Release pipeline, version bump, deploy (with `--autonomous` flag) |

**New entries in Quick Reference:**

```
Insights-Driven:
  /craft:guard:audit              → Audit guard config, find false positives
  /craft:insights:apply           → Apply insights suggestions to CLAUDE.md
  /craft:check --context          → Front-load session context
  /release --autonomous           → Fully automated release pipeline
  /craft:git:worktree validate    → Verify worktree path
  /craft:orchestrate --swarm      → Parallel agents in isolated worktrees
```

**Why these integrate cleanly:** Super commands are discovery/routing layers. Adding new entries doesn't change their behavior for existing routes — it just expands what they know about.

## API Design

N/A — No API changes. These are CLI commands and skills (markdown-driven).

## Data Models

N/A — No new data models. Existing structures (ORCHESTRATE files, branch-guard.json, CLAUDE.md) are reused.

## Dependencies

- `git` (worktree operations)
- `gh` CLI (PR creation in swarm mode)
- `python3` (PreToolUse hook, claude_md_sync.py)
- `~/.claude/usage-data/` (insights:apply reads this)

## UI/UX Specifications

All outputs use existing craft box-drawing format (from `scripts/formatting.sh`). No new visual patterns needed.

### Session Context Output (check --context)

```
┌───────────────────────────────────────────────────────────────┐
│ SESSION CONTEXT                                               │
├───────────────────────────────────────────────────────────────┤
│ Project:   <name> (<type>)                                    │
│ Branch:    <current-branch>                                   │
│ Worktree:  <path or "main repo">                              │
│ Base:      <base-branch>                                      │
│ Guard:     <status>                                           │
│ Phase:     <phase> (commits ahead: N)                         │
│ Tests:     <test-command> (N passing)                         │
│ Lint:      <lint-command>                                     │
└───────────────────────────────────────────────────────────────┘
```

## Open Questions

1. ~~Should `--autonomous` have approval gates?~~ **Resolved:** No gates. Fully autonomous. Safety via dirty-tree/wrong-branch checks.
2. ~~Should `/craft:check --context` run at SessionStart automatically?~~ **Resolved:** Both — auto-run via SessionStart hook AND available manually for refresh.
3. ~~Should swarm mode create PRs per agent or merge silently?~~ **Resolved:** Single convergence PR. Merge all agent branches into one, single PR to dev.
4. ~~Should `/craft:guard:audit` modify branch-guard.sh or only JSON config?~~ **Resolved:** JSON config only. Never touch the script — tune via `.claude/branch-guard.json`.
5. ~~Should insights:apply work cross-project?~~ **Resolved:** Global CLAUDE.md only (insights are cross-project).
6. ~~Implementation scope?~~ **Resolved:** All 5 phases (full implementation including swarm mode).

## Review Checklist

- [ ] All new flags default to `false` (no behavior change for existing users)
- [ ] New skills follow existing SKILL.md format (frontmatter + sections)
- [ ] PreToolUse hook is non-blocking (warning only, not exit 1)
- [ ] Autonomous release still respects `--dry-run`
- [ ] Swarm mode cleans up worktrees after convergence
- [ ] All markdown passes lint
- [ ] Command/skill counts updated in CLAUDE.md, plugin.json, README

## Implementation Notes

### File Changes Summary

| File | Action | Complexity | Description |
|------|--------|------------|-------------|
| `commands/check.md` | UPDATE | Low | Add `--context` arg + session header section |
| `skills/release/SKILL.md` | UPDATE | Medium | Add `--autonomous` flag + auto-resolve logic |
| `commands/git/worktree.md` | UPDATE | Low | Add `validate` action |
| `.claude-plugin/hooks/pretooluse.py` | UPDATE | Medium | Add worktree path validation |
| `skills/guard-audit/SKILL.md` | CREATE | Medium | Branch guard audit + tuning |
| `skills/insights-apply/SKILL.md` | CREATE | Medium | Insights report to CLAUDE.md rules |
| `commands/orchestrate.md` | UPDATE | High | Add `--swarm` flag + worktree-per-agent |
| `commands/do.md` | UPDATE | Low | Add routing for guard:audit, insights:apply, --autonomous |
| `commands/smart-help.md` | UPDATE | Low | Add context-aware suggestions for new skills |
| `commands/hub.md` | UPDATE | Low | Update counts (21 → 25 skills), add new entries |
| `CLAUDE.md` | UPDATE | Low | Version, counts (23 → 25 skills) |
| `.claude-plugin/plugin.json` | UPDATE | Low | Version if releasing |

### Implementation Order

| Phase | Items | Dependencies |
|-------|-------|-------------|
| 1 (parallel) | check --context, worktree --validate, worktree hook | None |
| 2 (parallel) | release --autonomous, guard:audit skill | Phase 1 (context for testing) |
| 3 (sequential) | insights:apply skill | Phase 2 (needs guard:audit to test) |
| 4 (parallel) | Super command updates (do.md, smart-help.md, hub.md) | Phase 1-3 (needs all new skills/flags to exist) |
| 5 (sequential) | orchestrate --swarm | Phase 1-4 (most complex, benefits from others) |

### Count Impact

| Metric | Before | After |
|--------|--------|-------|
| Commands | 108 | 108 (no new commands, just flags) |
| Skills | 23 | 25 (+guard:audit, +insights:apply) |
| Agents | 8 | 8 (no new agents) |

## History

| Date | Change |
|------|--------|
| 2026-02-14 | Initial spec from deep brainstorm (8 questions + 2 agents) |
| 2026-02-14 | Added Change 8: Super command updates (do.md, smart-help.md, hub.md) |
| 2026-02-14 | Resolved all open questions (interactive review). Status → Approved. |
