# Insights-Driven Craft Command Updates - Orchestration Plan

> **Branch:** `feature/insights-integration`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-insights-integration`
> **Spec:** `docs/specs/SPEC-insights-integration-2026-02-18.md`

## Objective

Integrate friction-prevention enhancements identified by the Claude Code
Insights report (341 sessions, 613 hours) into existing craft commands.
No new commands — only enhancements to `/craft:check`, `/release`,
`/workflow:done`, and `/craft:docs:sync`, plus new hooks and a global rule.

## Phase Overview

| Phase | Task | Priority | Status |
| ----- | ---- | -------- | ------ |
| 1 | Action-verb execution rule (global) | HIGH | Pending |
| 2 | Version sync (hooks + /craft:check) | HIGH | Pending |
| 3 | /craft:check friction detection enhancements | HIGH | Pending |
| 4 | /release CI monitoring loop | MEDIUM | Pending |
| 5 | Doc sync automation (/workflow:done + headless) | MEDIUM | Pending |
| 6 | Documentation deliverables | LOW | Pending |

---

## Phase 1: Action-Verb Execution Rule (< 15 min)

> **Goal:** Eliminate the #1 friction source (59 "wrong approach" incidents).
> **Why first:** Zero risk, immediate impact, no code changes. Just a
> markdown file that changes Claude's behavior globally.

### Tasks

- [ ] **1.1 Create `~/.claude/rules/action-verb-execution.md`**
  - Action verbs (write, fix, add, create, etc.) = execute immediately
  - Planning verbs (plan, design, investigate, etc.) = plan first
  - Include examples of DO and DON'T patterns
  <!-- COMMENT: This rule addresses the single biggest friction category
       in the insights report. 59 sessions had "wrong approach" friction
       where Claude planned when the user wanted execution. The verb
       distinction is clean and unambiguous. -->

- [ ] **1.2 Test with sample prompts**
  - "Fix the typo in README" → should execute, not plan
  - "Plan the auth system" → should plan, not execute
  - "Add a logout button" → should execute, not plan
  <!-- COMMENT: Quick verification that the rule works as intended.
       Not a formal test suite — just manual confirmation in a
       Claude Code session. -->

### Phase 1 Acceptance Criteria

- [ ] Rule file exists at `~/.claude/rules/action-verb-execution.md`
- [ ] Action verbs trigger immediate execution
- [ ] Planning verbs still trigger planning behavior

---

## Phase 2: Version Sync (1-2 hours)

> **Goal:** Eliminate version drift that causes CI failures (~15 sessions).
> **Why:** Belt-and-suspenders approach — PreToolUse hook warns in-session,
> git pre-commit hook blocks at commit time, /craft:check validates on demand.

### Tasks

- [ ] **2.1 Create `scripts/version-sync.sh`**
  - Convention-based discovery: package.json, plugin.json, pyproject.toml,
    CLAUDE.md, DESCRIPTION, Cargo.toml
  - Source code constants: `VERSION =`, `__version__`
  - Test expectations: `assert.*version`, `expect.*version`
  - Root version is source of truth (monorepo support)
  - Exit 0 (all match) or exit 1 (mismatch with details)
  <!-- COMMENT: This is the core utility that both hooks and /craft:check
       call. Convention-based means it works out of the box for standard
       project types without per-project configuration. The monorepo
       strategy is "root version is source of truth" per user preference. -->

- [ ] **2.2 Create `~/.claude/hooks/version-sync-hook.sh`**
  - PreToolUse hook: triggers before Edit/Write on version-sensitive files
  - WARNING only (does not block) — soft guardrail
  - Register in `~/.claude/settings.json` under PreToolUse
  <!-- COMMENT: This is Layer 1 (in-session). It catches drift before
       it's committed. Warning-only because sometimes you intentionally
       edit version files as part of a bump — blocking would be annoying.
       The pre-commit hook (Layer 2) is the hard block. -->

- [ ] **2.3 Create `scripts/version-sync-precommit.sh`**
  - Git pre-commit hook: runs on staged files
  - BLOCKS commit if versions mismatch
  - Clear error message with fix instructions
  <!-- COMMENT: This is Layer 2 (at commit time). It's the hard block
       that prevents version drift from reaching the repo. Combined with
       the PreToolUse hook, drift is caught twice before it can cause
       CI failures. -->

- [ ] **2.4 Add version consistency check to `/craft:check`**
  - New check for `--for commit`, `--for pr`, `--for release`
  - Calls `scripts/version-sync.sh` and reports results
  - Shows source-of-truth file + all checked files with pass/fail
  <!-- COMMENT: This is the on-demand validation. Users can run it
       explicitly, and it's also called by the release pipeline.
       It provides the nicest output of the three layers. -->

### Phase 2 Acceptance Criteria

- [ ] `scripts/version-sync.sh` discovers version files conventionally
- [ ] PreToolUse hook warns on version drift during edits
- [ ] Pre-commit hook blocks commits with version mismatches
- [ ] `/craft:check --for commit` includes version consistency check

---

## Phase 3: /craft:check Friction Detection (1 hour)

> **Goal:** Add stale reference scanning and hook conflict auditing to
> the existing pre-flight check command.
> **Why:** Stale references after renames caused doc update sessions (40).
> Hook conflicts caused manual intervention in ~35 sessions.

### Tasks

- [ ] **3.1 Add stale reference scan to `--for pr`**
  - Run `git diff --name-status` to detect renames
  - Grep docs/, README, tutorials for old names
  - Report files that need updating
  <!-- COMMENT: This catches the exact pattern from the insights:
       a file is renamed in code, but docs still reference the old name.
       Running this before PR creation means the PR includes doc updates. -->

- [ ] **3.2 Add hook conflict audit to `--for pr` and `--for release`**
  - Parse `.githooks/` and `.husky/` for known conflict patterns
  - Check: will branch guard block our planned push?
  - Check: will pre-commit hooks reject our staged changes?
  <!-- COMMENT: This prevents the "git hooks blocking Claude" friction
       identified in the insights. Rather than disabling hooks, we
       pre-check whether they'll conflict with the operation. -->

- [ ] **3.3 Add CLAUDE.md health check**
  - Reuse logic from claude-md-refactor spec (Phase 4)
  - Check line count, count accuracy, memory staleness
  <!-- COMMENT: This connects to the claude-md-refactor work. When
       both features are merged, /craft:check will have comprehensive
       instruction health validation. Can be a stub if claude-md-refactor
       isn't merged yet. -->

- [ ] **3.4 Update `commands/check.md` with new checks**
  - Add documentation for new check types
  - Update the check table with new entries
  <!-- COMMENT: Command file is the source of truth for what /craft:check
       does. Must be updated alongside the implementation. -->

### Phase 3 Acceptance Criteria

- [ ] `/craft:check --for pr` scans for stale references
- [ ] `/craft:check --for pr` audits hook conflicts
- [ ] CLAUDE.md health check integrated (or stubbed)
- [ ] Command documentation updated

---

## Phase 4: /release CI Monitoring Loop (1-2 hours)

> **Goal:** Make releases fully autonomous by auto-monitoring CI after
> PR creation, diagnosing failures, applying fixes, and retrying.
> **Why:** CI failures during releases required manual back-and-forth
> in ~20 sessions. Full auto means fire-and-forget releases.

### Tasks

- [ ] **4.1 Create `scripts/ci-monitor.sh`**
  - Poll `gh run list` every 30s
  - Parse status: success, failure, in_progress
  - On failure: `gh run view --log-failed` for diagnosis
  - Configurable timeout (default 10 min) via `release-config.json`
  <!-- COMMENT: This is the core polling utility. It's a standalone
       script so it can be tested independently and used outside
       of /release if needed. The configurable timeout is per user
       preference — different projects have different CI durations. -->

- [ ] **4.2 Add Step 6.5 to `/release` SKILL.md**
  - Between PR creation (Step 6) and merge (Step 7)
  - Call `ci-monitor.sh` with PR number
  - On failure: diagnose, apply fix, push, re-poll
  - Max 3 retry cycles
  - Auto-fix: version_mismatch, lint_failure, changelog_format
  - Ask-before-fix: test_failure, security_audit, build_failure
  <!-- COMMENT: The auto-fix vs ask-before-fix distinction is critical.
       Safe fixes (version drift, lint) can be applied automatically.
       Risky fixes (test failures, security issues) need human approval.
       This matches the user's "full auto" preference while maintaining
       safety for non-trivial failures. -->

- [ ] **4.3 Create `.claude/release-config.json` schema**
  - `ci_timeout`, `ci_max_retries`, `ci_poll_interval`
  - `ci_auto_fix_categories`, `ci_ask_before_fix`
  - Document defaults and override behavior
  <!-- COMMENT: Per-project configuration allows different CI timeout
       values for different projects. Craft's CI is fast (~2 min),
       but other projects might have longer pipelines. -->

### Phase 4 Acceptance Criteria

- [ ] CI monitoring polls and reports status correctly
- [ ] Auto-fix works for version mismatch and lint failures
- [ ] Asks before fixing test failures
- [ ] Max 3 retries, then reports to user
- [ ] Configurable timeout via release-config.json

---

## Phase 5: Doc Sync Automation (1 hour)

> **Goal:** Three-layer doc sync: CI catches misses after merge,
> /workflow:done catches in-session, manual for ad-hoc.
> **Why:** 40 documentation-update sessions could be partially automated.

### Tasks

- [ ] **5.1 Add doc drift detection to `/workflow:done`**
  - Compare changed files this session against doc references
  - If drift detected: offer to run `/craft:docs:sync`
  - Show which docs need updating
  <!-- COMMENT: /workflow:done is the natural "end of session" trigger.
       Adding doc drift detection here means every productive session
       ends with up-to-date documentation. This is the same pattern
       as the CLAUDE.md staleness check from the refactor spec. -->

- [ ] **5.2 Add `--headless` flag to `/craft:docs:sync`**
  - Non-interactive mode: auto-approve all changes
  - Standard commit message: "docs: auto-sync documentation"
  - `--headless --dry-run`: show what would change without modifying
  <!-- COMMENT: Headless mode enables CI automation. The existing
       /craft:docs:sync is interactive — it asks for approval before
       each change. Headless skips all prompts. -->

- [ ] **5.3 Create `.github/workflows/docs-sync.yml`**
  - Trigger: push to main
  - Also: workflow_dispatch (manual trigger)
  - Runs: `claude -p "Run /craft:docs:sync --headless"`
  - Requires: ANTHROPIC_API_KEY secret
  <!-- COMMENT: This is the CI layer. It runs after every merge to main,
       catching any documentation that wasn't updated in the feature PR.
       It's a safety net, not the primary mechanism — /workflow:done
       should catch most drift in-session. -->

- [ ] **5.4 Update command documentation**
  - `commands/workflow/done.md` — add doc drift step
  - `commands/docs/sync.md` — add --headless flag docs
  <!-- COMMENT: Keep command files in sync with implementation. -->

### Phase 5 Acceptance Criteria

- [ ] `/workflow:done` detects doc drift and offers sync
- [ ] `/craft:docs:sync --headless` runs non-interactively
- [ ] GitHub Actions workflow triggers on push to main
- [ ] Command documentation updated

---

## Phase 6: Documentation Deliverables (1 hour)

> **Goal:** Complete all 4 documentation deliverables from the spec.
> **Why:** These commands are useless if users don't know about them.

### Tasks

- [ ] **6.1 Update command reference pages**
  - `docs/commands/check.md` — version sync, stale refs, hook audit
  - `docs/commands/workflow/done.md` — doc drift detection
  - `docs/commands/docs/sync.md` — --headless flag
  - `docs/skills/release.md` — CI monitoring loop
  <!-- COMMENT: These are the primary "how to use it" docs. Users
       look here when they want to know what a command does. -->

- [ ] **6.2 Create version sync tutorial**
  - `docs/tutorials/TUTORIAL-version-sync-setup.md`
  - What, why, setup PreToolUse hook, setup pre-commit hook
  - Testing, project type configs, troubleshooting
  <!-- COMMENT: Tutorial format because version sync involves setup
       steps that users need to follow. Not just a reference page. -->

- [ ] **6.3 Update refcard**
  - `docs/REFCARD.md` — add new check behaviors, --headless, CI monitoring
  <!-- COMMENT: Refcard is the quick-reference cheat sheet. One-liner
       descriptions of what's new. -->

- [ ] **6.4 Create CI monitoring architecture doc**
  - `docs/architecture/ci-monitoring.md`
  - Polling loop design, failure diagnosis, retry strategy
  - Sequence diagram, known failure patterns, security considerations
  <!-- COMMENT: Architecture doc for developers who want to understand
       or extend the CI monitoring system. Not for end users. -->

### Phase 6 Acceptance Criteria

- [ ] 4 command reference pages updated
- [ ] Version sync tutorial complete
- [ ] Refcard updated with new entries
- [ ] CI monitoring architecture doc complete

---

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-insights-integration
claude
```

Start with Phase 1 (action-verb rule) — 15 minutes, zero risk, immediate
impact on 59 friction incidents. Each phase can be committed independently.

## Notes

- **Do not implement.** This ORCHESTRATE file is the plan. Implementation
  happens when the user says "start Phase 1" or similar.
- Phase 1 is the fastest win. Phases 2-3 are the core value (version sync).
  Phase 4 is the most complex (CI monitoring). Phases 5-6 are automation
  and documentation layers.
- Phase 3 task 3.3 (CLAUDE.md health) may be a stub if the claude-md-refactor
  feature branch hasn't been merged yet. That's OK — it can be filled in
  later when that work lands.
- The spec has detailed API designs, hook scripts, and CI workflow YAML
  that should be used as implementation references.
