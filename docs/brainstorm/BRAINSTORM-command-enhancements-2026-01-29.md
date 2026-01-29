# Command Enhancements Brainstorm

**Generated:** 2026-01-29
**Mode:** max | feat | save
**Context:** Craft Plugin v2.8.1, branch dev
**Commands analyzed:** orchestrate, docs:update, check, git:worktree

---

## Problem Summary

Four most-used commands have behavioral gaps:

1. **Commands skip documented steps** -- orchestrate doesn't ask interactive questions, mode flags don't change behavior visibly
2. **No step preview** -- commands execute without showing what they'll do first
3. **Post-merge docs gap** -- no automation after PR merge for documentation updates
4. **Worktree setup is manual** -- creating a worktree doesn't auto-setup workflow files

---

## Enhancement 1: Orchestrate -- Interactive Step Enforcement

### Current Problems (from agent analysis)

| Problem | Location | Impact |
| ------- | -------- | ------ |
| Mode selection broken | `utils/orch_flag_handler.py:49-106` | `prompt_user_for_mode()` always returns "default" without asking |
| No plan confirmation | `agents/orchestrator-v2.md` BEHAVIOR 1 | Spawns agents immediately, no "proceed?" prompt |
| No wave checkpoints | `agents/orchestrator-v2.md` BEHAVIOR 2 | No pause between waves for review |
| Decision points passive | `agents/orchestrator-v2.md` BEHAVIOR 6 | Lists options but doesn't use AskUserQuestion |

### Proposed: "Show Steps First, Then Ask" Pattern

Every orchestrate invocation should:

**Step 1: Print the plan**

```text
/craft:orchestrate "implement auth"

Orchestration Plan:
  Task: implement auth
  Mode: default (2 agents, 70% compression)
  Complexity: 7/10

  Steps:
  1. Analyze → Design auth flow (arch agent)
  2. Implement → Backend endpoints (code agent)
  3. Test → Unit + integration tests (test agent)
  4. Document → Update docs (doc agent)

  Wave 1 (parallel): Steps 1-2
  Wave 2 (sequential): Steps 3-4
```

**Step 2: Ask to proceed**

```text
AskUserQuestion:
  "Proceed with this plan?"
  - "Yes - Start Wave 1 (Recommended)"
  - "Modify steps"
  - "Change mode (currently: default)"
  - "Cancel"
```

**Step 3: Checkpoint after each wave**

```text
Wave 1 complete:
  - arch-1: Design complete (OAuth 2.0 + PKCE)
  - code-1: Endpoints created (4 routes)

AskUserQuestion:
  "Continue to Wave 2?"
  - "Yes - Continue (Recommended)"
  - "Review Wave 1 results first"
  - "Modify Wave 2 tasks"
  - "Stop here"
```

### Mode Behavior -- Make Flags Visibly Different

| Behavior         | default  | debug       | optimize   | release      |
| ---------------- | -------- | ----------- | ---------- | ------------ |
| Plan display     | Summary  | Step traces | Parallel map | Full audit  |
| Checkpoints      | Per wave | Every step  | Wave end   | Every step   |
| Agent output     | Summary  | Verbose     | Summary    | Full + diff  |
| Auto-proceed     | Ask once | Ask always  | Ask once   | Ask always   |
| Context shown    | Minimal  | Full stack  | Timing     | Everything   |

### Quick Win: Fix `prompt_user_for_mode()`

The Python function in `utils/orch_flag_handler.py` line 101 currently returns `"default"` unconditionally. The command.md should explicitly instruct Claude to use `AskUserQuestion` when no mode is specified, rather than relying on this Python function.

---

## Enhancement 2: docs:update -- Post-Merge Automation

### Current Gap

After merging a PR, there is **zero automation** for documentation updates. The user must manually run `/craft:docs:update` every time. The 9-category detection system exists but isn't triggered automatically.

### Proposed: Post-Merge Documentation Pipeline

**Trigger:** After any PR merge to `dev` (or manually via `/craft:docs:post-merge`)

**Flow:**

```text
PR merged → Auto-detect (9 categories) → Auto-fix safe categories
                                        → Prompt for manual categories
                                        → Lint + validate
                                        → Create new tutorials
                                        → Update existing docs
                                        → Summary
```

**Phase 1: Auto-Detection (no prompts)**

```text
Scanning post-merge changes...

Detected:
  version_refs:    12 files need v2.8.1 → v2.9.0
  command_counts:  4 files (99 → 103 commands)
  navigation:      2 missing mkdocs.yml entries
  broken_links:    1 internal link (renamed file)
  help_files:      3 new commands missing YAML
  tutorial_updates: 1 new module needs tutorial
  changelog:       PR description available
```

**Phase 2: Auto-fix safe categories (no prompts)**

- Version references (find-replace)
- Command counts (recalculate)
- Navigation entries (add to mkdocs.yml)
- Broken links (update paths)

**Phase 3: Interactive for manual categories**

```text
AskUserQuestion:
  "3 new commands need help files. Create from template?"
  - "Yes - Create all 3 (Recommended)"
  - "Select which ones"
  - "Skip for now"

AskUserQuestion:
  "New module detected (sessions/). Create tutorial?"
  - "Yes - Generate tutorial (Recommended)"
  - "No - Manual later"

AskUserQuestion:
  "Draft changelog entry from PR #42 description?"
  - "Yes - Create draft (Recommended)"
  - "No"
```

**Phase 4: Validation pipeline**

```text
Post-update validation:
  /craft:docs:lint --fix
  /craft:docs:check-links

  19 files auto-fixed
  5 files created (3 help + 1 tutorial + 1 changelog)
  0 broken links remaining
```

### Integration Points

| Command | Role in Pipeline | Trigger |
| ------- | --------------- | ------- |
| `docs:update --detect-only` | Phase 1 detection | Auto |
| `docs:update --auto-yes` | Phase 2 safe fixes | Auto |
| `docs:update --interactive` | Phase 3 manual categories | Interactive |
| `docs:lint --fix` | Phase 4 validation | Auto |
| `docs:check-links` | Phase 4 validation | Auto |

### Implementation Options

**Option A: New command `/craft:docs:post-merge`**

- Dedicated command for the post-merge workflow
- Chains existing commands in the right order
- Could be triggered by GitHub Action

**Option B: Enhance `/craft:docs:update` with `--post-merge` flag**

- Adds a mode to the existing command
- Auto-runs detection, applies safe fixes, prompts for manual
- Less surface area (no new command)

**Option C: GitHub Action + Claude Code hook**

- `.github/workflows/docs-post-merge.yml` triggers on PR close
- Runs detection in CI, creates issue with update checklist
- User runs `/craft:docs:update --from-ci` to apply

**Recommendation:** Option B -- extend `docs:update` with `--post-merge` flag. Keeps it in one command, matches the existing `docs:sync` merge plan.

---

## Enhancement 3: check -- Step Preview Before Execution

### Current Behavior

`/craft:check` runs all validation checks immediately without showing what it will do.

### Proposed: Preview-Then-Execute

```text
/craft:check

Pre-flight Check Plan:
  Project: craft (Claude Code Plugin)
  Mode: default
  Branch: feature/v2.9.0

  Checks to run:
  1. Git status (clean working tree?)
  2. Unit tests (python3 tests/test_craft_plugin.py)
  3. Markdown lint (30 rules via markdownlint-cli2)
  4. Link validation (internal + external)
  5. Version sync (plugin.json matches CLAUDE.md)
  6. Count validation (./scripts/validate-counts.sh)

  Estimated: 6 checks

AskUserQuestion:
  "Run all checks?"
  - "Yes - Run all (Recommended)"
  - "Skip lint (faster)"
  - "Skip links (faster)"
  - "Dry run (show commands only)"
```

### Mode Impact on Check

| Check | default | debug | release |
| ----- | ------- | ----- | ------- |
| Git status | Yes | Yes + diff | Yes + full log |
| Unit tests | Quick | Verbose | Full + coverage |
| Markdown lint | Changed files | All files | All + strict |
| Link validation | Skip | Internal only | All links |
| Version sync | Basic | Show all refs | Full audit |
| Count validation | Basic | Show diffs | Full recount |

---

## Enhancement 4: git:worktree -- Auto-Setup Workflow Files

### Current Behavior

`/craft:git:worktree create feature/v2.9.0` creates the worktree but leaves it empty -- user must manually create orchestration plans, specs, and update .STATUS/CLAUDE.md.

### Proposed: Template-Based Auto-Setup

After creating the worktree, automatically:

1. **Create `ORCHESTRATE-<name>.md`** with task plan from context
2. **Create `docs/specs/SPEC-<name>-<date>.md`** if scope warrants it
3. **Update `.STATUS`** in main repo (mark branch as WIP)
4. **Update `CLAUDE.md`** in main repo (add worktree to table)

**Flow:**

```text
/craft:git:worktree create feature/v2.9.0

Step 1: Create worktree
  Branch: feature/v2.9.0 (from dev @ ff5fc2f)
  Path: ~/.git-worktrees/craft/feature-v2.9.0

Step 2: Auto-setup workflow files

AskUserQuestion:
  "What's the scope of this feature branch?"
  - "Small fix (no orchestration file needed)"
  - "Single feature (create ORCHESTRATE file)"
  - "Multi-phase release (create ORCHESTRATE + SPEC)"
  - "Custom setup"

  [User selects: Multi-phase release]

AskUserQuestion:
  "Brief description for the orchestration plan?"
  - [Free text: "v2.9.0 - styled output, execution modes, linting"]

Step 3: Generate files
  Created: ORCHESTRATE-v2.9.0.md (plan template)
  Created: docs/specs/SPEC-v2.9.0-features-2026-01-29.md

Step 4: Update main repo
  Updated: .STATUS (marked feature/v2.9.0 as WIP)
  Updated: CLAUDE.md (added worktree to table)

Step 5: Ready
  cd ~/.git-worktrees/craft/feature-v2.9.0
  claude
```

### Scope Detection

| Signal | Scope | Auto-Setup |
| ------ | ----- | ---------- |
| Branch name `fix/*` | Small | No orchestration file |
| Branch name `feature/*` | Medium | ORCHESTRATE file |
| Branch name matches `v*` | Release | ORCHESTRATE + SPEC |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |
| User selects "custom" | Custom | Ask what to create |

---

## Cross-Cutting Enhancement: "Show Steps First" Pattern

All four commands should adopt the same UX pattern:

```text
1. Print what the command WILL do (numbered steps)
2. Ask to proceed (with options to modify/skip/cancel)
3. Execute steps with progress indicators
4. Show summary with next steps
```

This addresses the core pain point: **commands skip steps because there's no accountability mechanism**. Showing the plan first makes the documented behavior visible and gives the user a chance to catch when something is wrong.

### Implementation

Add a shared behavior to the top of each command's markdown:

```markdown
## Step 0: Plan Display (All Modes)

Before executing any action, ALWAYS:
1. Print a numbered list of steps this command will take
2. Show the mode and any flags that affect behavior
3. Use AskUserQuestion to confirm before proceeding
4. In debug mode, show additional context per step
```

---

## Quick Wins

| Enhancement | Effort | Impact | Command |
| ----------- | ------ | ------ | ------- |
| Fix `prompt_user_for_mode()` | Low | High | orchestrate |
| Add plan confirmation to orchestrator-v2 | Low | High | orchestrate |
| Add `--post-merge` flag to docs:update | Medium | High | docs:update |
| Add step preview to check | Low | Medium | check |
| Add scope detection to worktree create | Medium | High | git:worktree |
| Make modes visibly different (output format) | Medium | High | All 4 commands |

## Recommended Implementation Order

1. **Cross-cutting:** Add "Show Steps First" pattern to orchestrate + check
2. **orchestrate:** Fix mode selection + add wave checkpoints
3. **git:worktree:** Add auto-setup with scope detection
4. **docs:update:** Add `--post-merge` pipeline
5. **All commands:** Make mode flags produce visibly different output

---

## Next Steps

1. Capture as formal spec for implementation
2. Add to v2.9.0 feature branch (`feature/v2.9.0`)
3. Start with orchestrate fixes (highest pain point)
