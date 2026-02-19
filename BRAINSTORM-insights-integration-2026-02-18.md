# Insights-Driven Craft Command Updates - Brainstorm

**Generated:** 2026-02-18
**Context:** Craft Plugin — Claude Code Insights Report Integration
**Mode:** deep | Focus: feature | Action: save

---

## The Problem

The Claude Code Insights report (341 sessions, 613 hours) identified recurring friction patterns that could be eliminated by updating existing craft commands:

| Friction Category | Sessions Affected | Current State |
|-------------------|-------------------|---------------|
| Wrong initial approach (plan vs execute) | 59 | No rule enforcing action-verb behavior |
| Version drift breaking CI | ~15 | Manual grep before commits |
| Stale docs after feature changes | 40 | Manual /craft:docs:sync |
| CI failures requiring back-and-forth | ~20 | Manual CI monitoring in /release |

**Key insight:** These aren't new features — they're **enhancements to existing commands** that close gaps identified by real usage data.

---

## What Changes

### 1. `/craft:check` Enhancement — Friction Detection

**Current:** Validates project structure, counts, tests, links.
**Add:** Version sync, stale reference scan, hook conflict audit.

New checks for `--for commit` and `--for pr`:

| Check | What it does | Trigger |
|-------|-------------|---------|
| Version consistency | Grep all files for version string, flag mismatches | `--for commit`, `--for release` |
| Stale reference scan | After renames, grep for old names in docs | `--for pr` |
| Hook conflict audit | Check git hooks won't block planned operations | `--for pr`, `--for release` |
| CLAUDE.md health | Line count, count accuracy (from claude-md-refactor spec) | All |

### 2. `/release` Enhancement — CI Monitoring Loop

**Current:** Steps 1-10 are sequential, manual CI check between steps 6-7.
**Add:** Auto-poll CI after PR creation, diagnose failures, fix and retry.

```
Step 6: Create PR (existing)
Step 6.5: CI Monitor Loop (NEW)
  → Poll gh run list every 30s
  → If failure: read logs with gh run view --log-failed
  → Diagnose root cause (version drift, lint, test failure)
  → Apply fix, push, re-poll
  → Max 3 retry cycles
  → If still failing after 3: report and ask user
Step 7: Merge PR (existing, only after CI green)
```

### 3. Version Sync Hook — Belt and Suspenders

**Layer 1:** Claude Code PreToolUse hook (in-session)

- Triggers before Edit/Write on version-sensitive files
- Checks version consistency across known locations
- Warns before introducing drift

**Layer 2:** Git pre-commit hook (at commit time)

- Runs version consistency check on staged files
- Blocks commit if versions are out of sync
- Clear error message with fix instructions

### 4. `/workflow:done` Enhancement — Doc Sync

**Current:** Captures session activity, updates .STATUS, suggests commit.
**Add:** Post-session doc staleness check + auto-sync trigger.

New steps after existing done workflow:

| Step | What it does |
|------|-------------|
| Doc drift detection | Compare changed files against doc references |
| Auto-sync trigger | Run /craft:docs:sync if drift detected |
| Report | Show which docs were updated |

### 5. Headless Doc-Sync — CI Automation

**Current:** `/craft:docs:sync` is interactive.
**Add:** `--headless` flag for CI/scripted use.

```bash
# GitHub Actions post-merge job
claude -p "Run /craft:docs:sync --headless" --allowedTools "Read,Edit,Write,Bash,Grep"
```

### 6. Action-Verb Execution Rule

**Location:** Per-project `.claude/rules/action-verb-execution.md`

```markdown
# Action Verb Execution Rule

When the user uses action verbs (write, fix, add, create, update, delete,
run, test, commit, push, deploy), execute the task immediately.

Do NOT:
- Enter plan mode
- Ask clarifying questions (unless genuinely ambiguous)
- Analyze or investigate first

If the user wants planning, they'll say: plan, design, investigate,
analyze, brainstorm, research.
```

---

## Options

### Option A: Sequential Enhancement (Recommended)

Update commands one at a time, each as a commit:

1. Action-verb rule (5 min, zero risk)
2. `/craft:check` version sync (30 min)
3. Version sync hooks (1 hour)
4. `/workflow:done` doc sync (30 min)
5. `/release` CI monitoring (1-2 hours)
6. Headless doc-sync (1 hour)

**Effort:** 1-2 sessions
**Pros:** Each change is independently testable and reversible
**Cons:** Slower than parallel

### Option B: Single Feature Branch

All changes on one `feature/insights-integration` branch with atomic commits.

**Effort:** 1 session
**Pros:** One PR, one review, coherent narrative
**Cons:** Larger blast radius per commit

---

## Quick Wins

1. Create `.claude/rules/action-verb-execution.md` — 5 min, immediate friction reduction
2. Add version consistency check to `/craft:check --for commit` — 30 min
3. Add doc drift step to `/workflow:done` — 30 min

## Medium Effort

- [ ] Version sync hooks (PreToolUse + pre-commit) — 1 hour
- [ ] CI monitoring loop in `/release` — 1-2 hours
- [ ] Headless `/craft:docs:sync --headless` — 1 hour

## Long-term

- [ ] GitHub Actions workflow for post-merge doc sync
- [ ] Self-healing CI patterns beyond release (general use)
- [ ] Friction detection dashboard (track improvements over time)

---

## Recommended Path

Start with Option A (sequential). Quick wins first — the action-verb rule alone addresses 59 friction instances. Then version sync catches the #2 friction source. CI monitoring is the biggest lift but highest ROI for release sessions.
