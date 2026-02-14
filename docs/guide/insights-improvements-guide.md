# Insights-Driven Improvements Guide (v2.18.0)

> **TL;DR**: 2 new skills, 4 enhanced commands, 1 safety hook — all designed to close the feedback loop between usage patterns and workflow configuration.

## Overview

v2.18.0 adds features that emerged from analyzing real craft usage patterns:

| Feature | Type | Purpose |
|---------|------|---------|
| Guard Audit | New skill | Tune branch guard to reduce false positives |
| Insights Apply | New skill | Apply session learnings to CLAUDE.md |
| PreToolUse Hook | New hook | Warn on writes outside current worktree |
| `--context` flag | Enhanced check | Show session context without running validators |
| `validate` action | Enhanced worktree | Health-check current worktree environment |
| `--autonomous` flag | Enhanced release | Unattended release pipeline |
| `--swarm` flag | Enhanced orchestrate | Isolated worktree per agent |

---

## New Skills

### Guard Audit (`/guard-audit`)

A read-only 5-step pipeline that analyzes your `branch-guard.sh` for false positives — rules that block legitimate work. It discovers all protection rules, tests them against realistic scenarios, generates a friction report, and proposes JSON config changes. It never modifies the guard script itself.

**When to use:** After the guard blocks something it shouldn't, or periodically to tune sensitivity.

**Key principle:** The guard script is the "engine" and `.claude/branch-guard.json` is the "tuning knobs." This skill only adjusts the knobs.

```mermaid
flowchart TD
    Start(["/guard-audit"]) --> D[Step 1: Discovery]
    D --> D1[Read branch-guard.sh]
    D1 --> D2[Extract protection rules]
    D2 --> D3[Read .claude/branch-guard.json]
    D3 --> D4[Present rule summary]

    D4 --> F[Step 2: Friction Analysis]
    F --> F1[Map each rule to false positive scenarios]
    F1 --> F2{False positives found?}
    F2 -->|No| Clean[Report clean audit — no changes needed]
    F2 -->|Yes| T[Step 3: Test Harness]

    T --> T1[Generate test scenarios]
    T1 --> T2[Run tests against guard script]
    T2 --> T3[Identify incorrect triggers]

    T3 --> R[Step 4: Friction Report]
    R --> R1[Show recommendations with config changes]

    R1 --> A[Step 5: Apply]
    A --> A1{User confirms?}
    A1 -->|Yes| A2[Write .claude/branch-guard.json]
    A1 -->|No| Skip[Keep existing config]
    A2 --> Done([Done — guard tuned])
    Skip --> Done
    Clean --> Done

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Clean fill:#27AE60,color:#fff
    style F2 fill:#F39C12,color:#fff
    style A1 fill:#F39C12,color:#fff
```

---

### Insights Apply (`/insights-apply`)

Bridges the gap between `/insights` (which analyzes your usage patterns) and your global `~/.claude/CLAUDE.md`. Parses the insights report, extracts `claude_md_additions` suggestions, presents each for review (apply/skip/edit), applies via the sync pipeline, and enforces the 200-line budget.

**When to use:** After running `/insights` and seeing suggestions you want to persist.

**Key principle:** Targets global CLAUDE.md only — insights are cross-project patterns, not project-specific.

```mermaid
flowchart TD
    Start(["/insights-apply"]) --> P[Step 1: Parse Insights]
    P --> P1{report.html exists?}
    P1 -->|Yes| P3[Extract claude_md_additions]
    P1 -->|No| P2{facets/ exists?}
    P2 -->|Yes| P3
    P2 -->|No| Err[Error: Run /insights first]

    P3 --> S[Step 2: Present Suggestions]
    S --> Loop{Next suggestion?}
    Loop -->|Yes| Show[Show title + content + priority]
    Show --> Ask{User decision?}
    Ask -->|Apply| Approve[Add to approved list]
    Ask -->|Skip| Skip[Add to skipped list]
    Ask -->|Edit first| Edit[User modifies content]
    Edit --> Approve
    Approve --> Loop
    Skip --> Loop

    Loop -->|No more| Apply[Step 3: Apply via Sync Pipeline]
    Apply --> Sync{sync pipeline available?}
    Sync -->|Yes| S1[python3 claude_md_sync.py --add-section]
    Sync -->|No| S2[Direct append to CLAUDE.md]

    S1 --> Budget[Step 4: Budget Check]
    S2 --> Budget
    Budget --> B1{Over 200 lines?}
    B1 -->|No| Report[Step 5: Report]
    B1 -->|Yes| Warn[Show budget warning + options]
    Warn --> Report
    Report --> Done([Done — CLAUDE.md updated])

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Err fill:#E74C3C,color:#fff
    style Ask fill:#F39C12,color:#fff
    style B1 fill:#F39C12,color:#fff
```

---

## New Hook

### PreToolUse Hook (`pretooluse.py`)

A non-blocking safety net that runs on every Write/Edit call. If you're working in a git worktree and a file operation targets a path outside that worktree, it prints a stderr warning. Always exits 0 — it warns but never blocks.

**Key principle:** The fast-path (not in worktree or not Write/Edit) returns immediately with zero overhead. Only calls `git rev-parse` when actually in a worktree.

```mermaid
flowchart TD
    Start([Write/Edit tool call]) --> T1{Tool is Write or Edit?}
    T1 -->|No| Pass1[Exit 0 — skip]
    T1 -->|Yes| T2{CWD contains /.git-worktrees/?}
    T2 -->|No| Pass2[Exit 0 — not in worktree]
    T2 -->|Yes| T3[Parse CLAUDE_TOOL_INPUT JSON]
    T3 --> T4{file_path present?}
    T4 -->|No| Pass3[Exit 0 — no path]
    T4 -->|Yes| T5[Get git toplevel]
    T5 --> T6{git toplevel found?}
    T6 -->|No| Pass4[Exit 0 — can't determine]
    T6 -->|Yes| T7{file_path starts with toplevel?}
    T7 -->|Yes| Pass5[Exit 0 — inside worktree]
    T7 -->|No| Warn["stderr: Writing outside worktree\nExit 0 — non-blocking"]

    style Start fill:#4A90D9,color:#fff
    style Warn fill:#E67E22,color:#fff
    style Pass1 fill:#95A5A6,color:#fff
    style Pass2 fill:#95A5A6,color:#fff
    style Pass3 fill:#95A5A6,color:#fff
    style Pass4 fill:#95A5A6,color:#fff
    style Pass5 fill:#27AE60,color:#fff
```

**Performance:** Fast path ~45ms, worktree path ~60ms.

---

## Enhanced Commands

### `/craft:check --context` — Context-Only Mode

Skips all validators and outputs a session context summary instead. Auto-detects your dev phase (implementation/testing/pr-prep/release) based on commits ahead, PR existence, and test file recency.

**When to use:** At the start of a session to understand where you left off, or to front-load context into prompts.

```mermaid
flowchart TD
    Start(["/craft:check --context"]) --> Detect[Detect project type and branch]
    Detect --> Phase[Phase Detection]

    Phase --> P1{On dev branch?}
    P1 -->|Yes| Release[Phase: release]
    P1 -->|No| P2{PR exists for branch?}
    P2 -->|Yes| PRPrep[Phase: pr-prep]
    P2 -->|No| P3{Test files modified recently?}
    P3 -->|Yes| Testing[Phase: testing]
    P3 -->|No| Impl[Phase: implementation]

    Release --> Display
    PRPrep --> Display
    Testing --> Display
    Impl --> Display

    Display[Display Session Context Box]
    Display --> Info["Project, Branch, Worktree\nBase branch, Guard status\nPhase, Commits ahead\nTest command, Lint command"]
    Info --> Tip["TIP: Front-load this context\nin prompts to reduce friction"]
    Tip --> Done([Exit — no checks run])

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Display fill:#8E44AD,color:#fff
    style P1 fill:#F39C12,color:#fff
    style P2 fill:#F39C12,color:#fff
    style P3 fill:#F39C12,color:#fff
```

---

### `/craft:git:worktree validate` — Worktree Health Check

Verifies your current worktree environment is healthy: you're actually in a worktree, the path matches conventions, the branch name matches the folder name, and no writes are targeting outside the worktree.

**When to use:** After switching to a worktree, or when something feels "off" about the environment.

```mermaid
flowchart TD
    Start(["/craft:git:worktree validate"]) --> C1{CWD inside git worktree?}
    C1 -->|No| Fail1["Not in a worktree\nSuggest: cd to worktree path"]
    C1 -->|Yes| C2[Get branch name + toplevel]

    C2 --> C3{Worktree path matches\n~/.git-worktrees/proj/branch?}
    C3 -->|No| Warn1["Unexpected worktree location"]
    C3 -->|Yes| C4{Branch name matches folder name?}

    C4 -->|No| Warn2["Branch/folder mismatch"]
    C4 -->|Yes| C5{Writes outside worktree detected?}

    C5 -->|Yes| Warn3["External writes detected"]
    C5 -->|No| Pass["All checks passed"]

    Warn1 --> Report
    Warn2 --> Report
    Warn3 --> Report
    Pass --> Report

    Report[Display Validation Report]
    Report --> Done([Done])
    Fail1 --> Done

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Pass fill:#27AE60,color:#fff
    style Fail1 fill:#E74C3C,color:#fff
    style Warn1 fill:#E67E22,color:#fff
    style Warn2 fill:#E67E22,color:#fff
    style Warn3 fill:#E67E22,color:#fff
```

---

### `/release --autonomous` — Unattended Release Pipeline

Runs the full release pipeline with zero user prompts. Pre-validates safety (clean tree, on dev, tests pass, no blockers), then auto-confirms every checkpoint. If any step fails, it aborts and preserves state for recovery.

**When to use:** In CI/CD pipelines, or when you're confident the release is ready and want zero interaction.

**Tip:** Always preview first with `--autonomous --dry-run`.

```mermaid
flowchart TD
    Start(["/release --autonomous"]) --> Safety[Safety Pre-checks]
    Safety --> S1{Working tree clean?}
    S1 -->|No| Abort1["ABORTED: Uncommitted changes"]
    S1 -->|Yes| S2{On dev branch?}
    S2 -->|No| Abort2["ABORTED: Must be on dev"]
    S2 -->|Yes| S3{All tests pass?}
    S3 -->|No| Abort3["ABORTED: Tests failing"]
    S3 -->|Yes| S4{No open blockers?}
    S4 -->|No| Abort4["ABORTED: Open blockers exist"]
    S4 -->|Yes| Pipeline[Begin Pipeline]

    Pipeline --> V[Step 1: Version bump — auto-detect]
    V --> CL[Step 2: Changelog — auto-generate]
    CL --> Commit[Step 3: Commit + tag — auto-confirm]
    Commit --> PR[Step 4: Create PR — auto-fill]
    PR --> Merge{Step 5: Merge PR}
    Merge -->|Success| Pub[Step 6: Publish — Homebrew/PyPI]
    Merge -->|Fail| AbortM["ABORTED at merge\nState preserved for recovery"]
    Pub --> Done([Done — released])

    Abort1 --> Failed([ABORTED])
    Abort2 --> Failed
    Abort3 --> Failed
    Abort4 --> Failed
    AbortM --> Failed

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Failed fill:#E74C3C,color:#fff
    style AbortM fill:#E74C3C,color:#fff
    style Safety fill:#8E44AD,color:#fff
    style Pipeline fill:#2ECC71,color:#fff
```

---

### `/craft:orchestrate --swarm` — Isolated Worktree Agents

Instead of forking agent contexts in the same directory (risking file conflicts), creates a separate git worktree per agent with its own branch. Agents work in parallel with complete isolation, then branches merge into a convergence branch.

**When to use:** Parallel feature implementation where agents would conflict on the same files.

**Requirement:** An ORCHESTRATE file with per-agent file scopes.

```mermaid
flowchart TD
    Start(["/craft:orchestrate --swarm"]) --> Parse[Step 1: Parse ORCHESTRATE file]
    Parse --> Plan[Extract agent assignments + file scopes]
    Plan --> Base["Step 2: Create convergence branch\nfeature/swarm-task"]

    Base --> Agents[Step 3: Create worktrees per agent]
    Agents --> W1["Agent 1: swarm-task-agent1\nFocus: tests/"]
    Agents --> W2["Agent 2: swarm-task-agent2\nFocus: src/"]
    Agents --> W3["Agent 3: swarm-task-agent3\nFocus: docs/"]

    W1 --> Launch[Step 4: Launch agents in parallel]
    W2 --> Launch
    W3 --> Launch

    Launch --> Wait[Step 5: Wait for completion]
    Wait --> Converge[Step 6: Merge all branches]
    Converge --> M1{Merge conflicts?}
    M1 -->|Yes| Conflict["Stop — report conflicts\nAsk user to resolve"]
    M1 -->|No| Test[Step 7: Run tests on merged branch]
    Test --> T1{Tests pass?}
    T1 -->|Yes| PR["Step 8: Create PR to dev"]
    T1 -->|No| Fix["Report failures — user fixes"]
    PR --> Cleanup["Step 9: Remove swarm worktrees\nDelete swarm branches"]
    Cleanup --> Done([Done — single PR created])

    style Start fill:#4A90D9,color:#fff
    style Done fill:#27AE60,color:#fff
    style Conflict fill:#E67E22,color:#fff
    style Fix fill:#E67E22,color:#fff
    style Launch fill:#8E44AD,color:#fff
    style Converge fill:#2ECC71,color:#fff
```

---

## Suggested Workflows

### Workflow 1: New Session Kickoff

Orient yourself at the start of every session.

```bash
/craft:check --context            # See phase + branch + guard status
/craft:git:worktree validate      # Confirm you're in the right place
```

### Workflow 2: Guard Tuning

After the guard blocks something it shouldn't.

```bash
/guard-audit                      # Discover + analyze + propose config
/craft:check                      # Verify nothing broke
```

### Workflow 3: Learning Loop

Periodic — incorporate session learnings into your CLAUDE.md.

```bash
/insights                         # Generate usage report
/insights-apply                   # Extract + review + apply to CLAUDE.md
/craft:docs:claude-md:sync        # Validate CLAUDE.md consistency
```

### Workflow 4: Parallel Feature Implementation

For large features that can be split across isolated agents.

```bash
/craft:orchestrate --swarm "implement feature"  # Isolated agents in worktrees
/craft:orchestrate status                       # Monitor progress
```

### Workflow 5: Unattended Release

When you're confident the release is ready.

```bash
/release --autonomous --dry-run   # Preview the plan
/release --autonomous             # Execute with zero prompts
```

### Workflow 6: Full Pre-Commit Pipeline

Before every commit.

```bash
/craft:git:worktree validate      # Right place?
/craft:check                      # All green?
# commit                          # Ship it
```

---

## See Also

- [Branch Guard Smart Mode Guide](branch-guard-smart-mode.md) — How the guard works
- [Check Command Mastery](check-command-mastery.md) — All check modes and flags
- [Worktree Advanced Patterns](worktree-advanced-patterns.md) — Multi-worktree management
- [Version History](../VERSION-HISTORY.md) — v2.18.0 release notes
- [Quick Reference](../REFCARD.md) — All commands at a glance
