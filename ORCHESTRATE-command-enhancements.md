# Command Enhancements Orchestration Plan

> **Branch:** `feature/command-enhancements`
> **Base:** `dev` (from v2.8.1 release, commit c2ebfa7)
> **Worktree:** `~/.git-worktrees/craft/feature-command-enhancements`
> **Spec:** `docs/specs/SPEC-command-enhancements-2026-01-29.md`
> **Brainstorm:** `BRAINSTORM-command-enhancements-2026-01-29.md`

## Objective

Fix the 4 most-used craft commands so they follow their documented behavior:
show planned steps before execution, ask before proceeding, and enforce
mode-specific differences. Addresses the core pain point: "commands skip
documented steps."

## User-Confirmed Decisions

| Decision | Choice |
| -------- | ------ |
| Primary pain point | Commands skip documented steps |
| Core enhancement | "Show Steps First" pattern across all 4 commands |
| Orchestrate fix | Interactive questions + wave checkpoints |
| docs:update trigger | `--post-merge` flag (Option B) |
| Worktree setup | Auto-create ORCHESTRATE + SPEC + update .STATUS + CLAUDE.md |
| Mode behavior | Make flags produce visibly different output |

## Phase Overview

| Phase | Enhancement | Priority | Depends On | Status |
| ----- | ----------- | -------- | ---------- | ------ |
| 1 | Orchestrate: Fix mode selection + plan confirmation | High | None | ✅ Done |
| 2 | Cross-cutting: "Show Steps First" pattern | High | Phase 1 | ✅ Done |
| 3 | git:worktree: Auto-setup workflow files | Medium | Phase 2 | ✅ Done |
| 4 | docs:update: `--post-merge` pipeline | Medium | Phase 2 | ✅ Done |
| 5 | check: Step preview + mode-specific list | Medium | Phase 2 | ✅ Done |

```text
Phase 1 (Orchestrate fixes) ──► Phase 2 (Show Steps First) ──┬──► Phase 3 (Worktree auto-setup)
                                                               ├──► Phase 4 (docs:update post-merge)
                                                               └──► Phase 5 (check preview)
```

---

## Phase 1: Fix Orchestrate Interactive Behavior (Priority: High)

**Goal:** Make orchestrate ask interactive questions and show plans before execution.

**Root Cause Analysis (from deep analysis):**

| Problem | Location | Impact |
| ------- | -------- | ------ |
| Mode selection broken | `utils/orch_flag_handler.py:49-106` | `prompt_user_for_mode()` always returns "default" |
| No plan confirmation | `agents/orchestrator-v2.md` BEHAVIOR 1 | Spawns agents immediately, no "proceed?" prompt |
| No wave checkpoints | `agents/orchestrator-v2.md` BEHAVIOR 2 | No pause between waves for review |
| Decision points passive | `agents/orchestrator-v2.md` BEHAVIOR 6 | Lists options but doesn't use AskUserQuestion |

**Changes:**

### 1a. Fix `prompt_user_for_mode()` in `utils/orch_flag_handler.py`

The Python function at line 101 currently returns `"default"` unconditionally. The
`commands/orchestrate.md` must explicitly instruct Claude to use `AskUserQuestion`
when no mode is specified, rather than relying on this Python function.

**Approach:** Update `commands/orchestrate.md` to include explicit AskUserQuestion
instructions for mode selection when no mode flag is provided.

### 1b. Add plan confirmation to `agents/orchestrator-v2.md`

After BEHAVIOR 1 (Task Analysis), add a mandatory AskUserQuestion:

```text
AskUserQuestion:
  question: "Proceed with this orchestration plan?"
  header: "Continue"
  options:
    - "Yes - Start Wave 1 (Recommended)"
    - "Modify steps"
    - "Change mode (currently: <mode>)"
    - "Cancel"
```

### 1c. Add wave checkpoints to `agents/orchestrator-v2.md`

After each wave completes, add:

```text
AskUserQuestion:
  question: "Continue to Wave <N>?"
  header: "Progress"
  options:
    - "Yes - Continue (Recommended)"
    - "Review Wave <N-1> results first"
    - "Modify Wave <N> tasks"
    - "Stop here"
```

### 1d. Convert passive decision points to active AskUserQuestion

BEHAVIOR 6 currently lists options and waits. Change to structured prompts.

**Files to modify:**

| File | Change |
| ---- | ------ |
| `commands/orchestrate.md` | Add mode selection AskUserQuestion when no flag |
| `agents/orchestrator-v2.md` | Add plan confirmation, wave checkpoints, active decisions |
| `utils/orch_flag_handler.py` | Update `prompt_user_for_mode()` to indicate Claude should ask |

**Mode behavior matrix (make flags visibly different):**

| Behavior | default | debug | optimize | release |
| -------- | ------- | ----- | -------- | ------- |
| Plan display | Summary | Step traces | Parallel map | Full audit |
| Checkpoints | Per wave | Every step | Wave end | Every step |
| Agent output | Summary | Verbose | Summary | Full + diff |
| Auto-proceed | Ask once | Ask always | Ask once | Ask always |

**Acceptance criteria:**

- [x] `prompt_user_for_mode()` triggers AskUserQuestion when no mode specified
- [x] Orchestrator shows task analysis and asks before spawning agents
- [x] Checkpoints between waves with continue/pause/modify options
- [x] Decision points use AskUserQuestion instead of passive listing
- [x] Each mode produces visibly different output format
- [ ] Tests updated for new interactive behavior (deferred — markdown-only changes)

---

## Phase 2: "Show Steps First" Cross-Cutting Pattern (Priority: High)

**Goal:** Add consistent step preview behavior to all 4 commands.

**Pattern (add to each command's markdown):**

```text
Step 0: Print what the command WILL do (numbered steps)
Step 0.5: AskUserQuestion to confirm/modify/cancel
Steps 1-N: Execute with progress indicators
Step N+1: Summary with next steps
```

**Files to modify:**

| File | Change |
| ---- | ------ |
| `commands/orchestrate.md` | Add Step 0 plan display requirement |
| `commands/check.md` | Add pre-flight check list preview |
| `commands/docs/update.md` | Add detection-first preview |
| `commands/git/worktree.md` | Add setup plan preview |

**Acceptance criteria:**

- [x] All 4 commands show numbered step plan before execution
- [x] AskUserQuestion used for confirmation at key decision points
- [x] Plan displayed as numbered list (screen reader friendly)
- [x] Progress shown with text indicators (not just icons)
- [x] Mode differences documented in help text

---

## Phase 3: git:worktree Auto-Setup (Priority: Medium)

**Goal:** Auto-create workflow files when creating a worktree.

**After creating the worktree, automatically:**

1. Detect scope from branch name (`fix/*`, `feature/*`, `v*`)
2. Ask scope confirmation via AskUserQuestion
3. Create `ORCHESTRATE-<name>.md` with task plan template
4. Create `docs/specs/SPEC-<name>-<date>.md` if scope warrants it
5. Update `.STATUS` in main repo (mark branch as WIP)
6. Update `CLAUDE.md` in main repo (add worktree to table)

**Scope detection:**

| Signal | Scope | Auto-Setup |
| ------ | ----- | ---------- |
| Branch `fix/*` | Small | No orchestration file |
| Branch `feature/*` | Medium | ORCHESTRATE file |
| Branch matches `v*` | Release | ORCHESTRATE + SPEC |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |
| User selects "custom" | Custom | Ask what to create |

**Files to modify:**

| File | Change |
| ---- | ------ |
| `commands/git/worktree.md` | Add auto-setup steps + scope detection |

**Acceptance criteria:**

- [x] Scope detection from branch name pattern
- [x] AskUserQuestion for scope confirmation
- [x] ORCHESTRATE file created with task plan template
- [x] SPEC file created for medium+ scope
- [x] .STATUS updated in main repo
- [x] CLAUDE.md worktree table updated

---

## Phase 4: docs:update `--post-merge` Pipeline (Priority: Medium)

**Goal:** Add post-merge documentation automation to the existing docs:update command.

**Pipeline flow:**

```text
PR merged → Auto-detect (9 categories) → Auto-fix safe categories
                                        → Prompt for manual categories
                                        → Lint + validate
                                        → Summary
```

**Safe (auto-fix, no prompts):**

- Version references (find-replace)
- Command counts (recalculate)
- Navigation entries (add to mkdocs.yml)
- Broken links (update paths)

**Manual (interactive prompts):**

- Help files for new commands
- Tutorial creation for new modules
- Changelog drafting from PR description
- GIF regeneration

**Files to modify:**

| File | Change |
| ---- | ------ |
| `commands/docs/update.md` | Add `--post-merge` flag + 4-phase pipeline |

**Acceptance criteria:**

- [x] `--post-merge` flag triggers the pipeline
- [x] Auto-detection runs first (9 categories from docs_detector.py)
- [x] Safe categories auto-fixed without prompts
- [x] Manual categories prompt via AskUserQuestion
- [x] Validation pipeline runs after updates (lint + check-links)
- [x] Summary shows what was auto-fixed and what was created

---

## Phase 5: check Step Preview (Priority: Medium)

**Goal:** Show check plan before execution with mode-specific check list.

**Preview format:**

```text
Pre-flight Check Plan:
  Project: craft (Claude Code Plugin)
  Mode: default
  Branch: feature/command-enhancements

  Checks to run:
  1. Git status (clean working tree?)
  2. Unit tests (python3 tests/test_craft_plugin.py)
  3. Markdown lint (30 rules via markdownlint-cli2)
  4. Link validation (internal + external)
  5. Version sync (plugin.json matches CLAUDE.md)
  6. Count validation (./scripts/validate-counts.sh)

AskUserQuestion:
  "Run all checks?"
  - "Yes - Run all (Recommended)"
  - "Skip lint (faster)"
  - "Skip links (faster)"
  - "Dry run (show commands only)"
```

**Mode impact:**

| Check | default | debug | release |
| ----- | ------- | ----- | ------- |
| Unit tests | Quick | Verbose | Full + coverage |
| Markdown lint | Changed files | All files | All + strict |
| Link validation | Skip | Internal only | All links |
| Version sync | Basic | Show all refs | Full audit |

**Files to modify:**

| File | Change |
| ---- | ------ |
| `commands/check.md` | Add step preview + mode-specific check list |

**Acceptance criteria:**

- [x] Check plan displayed before execution
- [x] Mode-specific check list shows different depth per mode
- [x] AskUserQuestion for confirm/skip/dry-run
- [x] Skip options available for faster runs

---

## Implementation Order

Phases 1 and 2 are sequential (2 depends on 1). Phases 3, 4, 5 are
independent and can run in parallel after Phase 2.

```text
Wave 1: Phase 1 (orchestrate fixes)
Wave 2: Phase 2 (Show Steps First pattern)
Wave 3: Phases 3 + 4 + 5 (parallel — worktree, docs:update, check)
```

## Commit Convention

```text
feat: fix orchestrate mode selection prompt          (Phase 1)
feat: add plan confirmation to orchestrator-v2       (Phase 1)
feat: add wave checkpoints to orchestrator-v2        (Phase 1)
feat: add "Show Steps First" to orchestrate + check  (Phase 2)
feat: add git:worktree auto-setup                    (Phase 3)
feat: add docs:update --post-merge pipeline          (Phase 4)
feat: add check step preview with mode list          (Phase 5)
test: add orchestrate interactive tests
docs: update command docs for step preview behavior
```

## Testing Strategy

- Validate existing tests still pass: `python3 tests/test_craft_plugin.py`
- Manual testing: invoke each command and verify step preview appears
- Validate counts: `./scripts/validate-counts.sh`
- Validate links: `python3 tests/test_craft_plugin.py -k "broken_links"`

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-command-enhancements
claude

# Start with Phase 1: Fix orchestrate
# Highest pain point — broken mode selection + missing confirmations
```
