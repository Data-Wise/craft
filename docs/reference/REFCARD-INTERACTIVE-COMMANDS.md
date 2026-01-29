# Quick Reference: Interactive Commands

**All 4 commands now show plans before executing and ask before proceeding.**

## The Pattern (All Commands)

```text
Step 0:   Show what the command WILL do
Step 0.5: Ask to proceed (confirm/modify/cancel)
Steps 1-N: Execute with progress
Step N+1: Summary + next steps
```

## /craft:orchestrate

### Quick Start

```bash
# Interactive mode selection
/craft:orchestrate "add auth"

# Skip mode prompt
/craft:orchestrate "add auth" default
/craft:orchestrate "add auth" debug
/craft:orchestrate "add auth" optimize
/craft:orchestrate "add auth" release
```

### Interactive Flow

```text
1. Mode selection     → "Which mode?" (if not specified)
2. Task analysis      → Shows subtask table with waves
3. Confirm            → "Proceed with this plan?"
4. Execute waves      → Agents spawned per wave
5. Wave checkpoint    → "Continue to Wave N?"  (repeats)
6. Summary            → Results + next steps
```

### Mode Comparison

| Behavior | default | debug | optimize | release |
|----------|---------|-------|----------|---------|
| Max agents | 2 | 1 | 4 | 4 |
| Plan display | Summary | Step traces | Parallel map | Full audit |
| Checkpoints | Per wave | Every step | Wave end | Every step |
| Agent output | Summary | Verbose | Summary | Full + diff |

### Confirmation Options

| Option | Effect |
|--------|--------|
| Yes - Start Wave 1 | Proceed as planned |
| Modify steps | Adjust tasks before executing |
| Change mode | Switch execution mode |
| Cancel | Exit without spawning agents |

### Wave Checkpoint Options

| Option | Effect |
|--------|--------|
| Yes - Continue | Proceed to next wave |
| Review results first | Show detailed Wave N output |
| Modify next wave | Change upcoming tasks |
| Stop here | End orchestration, keep completed work |

---

## /craft:check

### Quick Start

```bash
# Default checks
/craft:check

# Context-specific
/craft:check --for commit
/craft:check --for pr
/craft:check --for release
/craft:check --for deploy
```

### Interactive Flow

```text
1. Show check plan    → Lists checks to run
2. Confirm            → "Run these checks?"
3. Execute            → [1/N] check... pass/fail
4. Summary            → X/N passed, issues, next steps
```

### Confirmation Options

| Option | Effect |
|--------|--------|
| Yes - Run all | Execute all checks |
| Skip lint | Faster — skip linting |
| Skip external links | Faster — skip link validation |
| Dry run | Show commands without executing |

### `--for` Flag Check Matrix

| Check | commit | pr | release | deploy |
|-------|--------|-----|---------|--------|
| Git status | Clean | Ahead | Tag exists | Clean + tag |
| Lint | Changed | All | All + strict | All + strict |
| Tests | Fail-fast | Full | Full + coverage | Full + coverage |
| Type check | Skip | Run | Run | Run |
| Security | Skip | Advisory | Full audit | Full audit |
| Links | Skip | Internal | All | All |
| Version sync | Skip | Check | Full audit | Full audit |
| Coverage | Skip | 80% | 90% | 90% |

### Mode-Specific Depth

| Check | default | debug | release |
|-------|---------|-------|---------|
| Tests | Quick | Verbose | Full + coverage |
| Lint | Changed files | All files | All + strict |
| Links | Skip external | Internal only | All links |
| Version sync | Basic | Show all refs | Full audit |

---

## /craft:docs:update

### Quick Start

```bash
# Smart detection
/craft:docs:update

# Post-merge pipeline (NEW)
/craft:docs:update --post-merge

# Preview only
/craft:docs:update --post-merge --dry-run
```

### Interactive Flow (default)

```text
1. Detection          → Scan categories, count updates needed
2. Confirm approach   → "Interactive / Auto-apply / Preview / Cancel?"
3. Execute            → Per-category with progress
4. Summary            → Files changed, validation results
```

### Post-Merge Pipeline Flow

```text
Phase 1: Auto-detect    → Scan 9 categories from PR changes
Phase 2: Auto-fix       → Safe categories (no prompts)
Phase 3: Manual prompt  → Categories needing judgment
Phase 4: Validate       → Lint + links + counts
Phase 5: Summary        → What was fixed/created/skipped
```

### Safe vs Manual Categories

| Category | Auto-fix | Manual |
|----------|:--------:|:------:|
| Version references | **yes** | |
| Command counts | **yes** | |
| Navigation entries | **yes** | |
| Broken links | **yes** | |
| Help files | | **yes** |
| Tutorials | | **yes** |
| Changelog | | **yes** |
| GIF regeneration | | **yes** |
| Feature status | | **yes** |

---

## /craft:git:worktree

### Quick Start

```bash
# Create with auto-setup
/craft:git:worktree create feature/my-feature

# Move current branch
/craft:git:worktree move

# Complete feature
/craft:git:worktree finish
```

### Interactive Flow (create)

```text
1. Show setup plan    → Branch, location, steps
2. Confirm            → "Proceed with this setup?"
3. Execute            → [1/N] step... done
4. Scope detection    → "What workflow files?"
5. Auto-setup         → Create ORCHESTRATE, SPEC, etc.
6. Summary            → Worktree path + next steps
```

### Scope Detection

| Branch Pattern | Scope | Auto-Create |
|----------------|-------|-------------|
| `fix/*` | Small | No files |
| `feature/*` | Medium | ORCHESTRATE |
| `v*` | Release | ORCHESTRATE + SPEC |
| Multi-phase | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |

### Scope Confirmation Options

| Option | Effect |
|--------|--------|
| Auto-detected (Recommended) | Based on branch pattern |
| Multi-phase project | Full file set |
| Minimal (no files) | Skip auto-setup |
| Custom | Choose exactly which files |

---

## Decision Points (Orchestrate Only)

During orchestration, design decisions use structured prompts:

```text
? The auth implementation needs a token strategy.
  > JWT with refresh tokens (Recommended)
    Session cookies
    Hybrid (JWT + sessions)
```

**Rules:**

- Always structured prompts (not passive markdown listings)
- Recommended option listed first
- Trade-off descriptions included
- Blocked agents resume immediately after your choice

---

## Tips

| Tip | Command |
|-----|---------|
| Skip mode prompt | `/craft:orchestrate "task" default` |
| Quick check | `/craft:check` (default is fastest) |
| Preview before applying | `--dry-run` flag |
| Post-merge docs | `/craft:docs:update --post-merge` |
| Auto-create workflow files | `/craft:git:worktree create feature/name` |

---

## See Also

- [Interactive Commands Guide](../guide/interactive-commands.md) — Full explanation with examples
- [Interactive Orchestration Tutorial](../tutorials/interactive-orchestration.md) — Step-by-step walkthrough
- [/craft:orchestrate](../commands/orchestrate.md) — Full command reference
- [/craft:check](../commands/check.md) — Full command reference
- [/craft:docs:update](../commands/docs/update.md) — Full command reference
- [/craft:git:worktree](../commands/git/worktree.md) — Full command reference
