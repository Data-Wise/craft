# Craft Architecture

Craft is a comprehensive full-stack development toolkit built on intelligent orchestration, mode-aware execution, and multi-agent coordination.

## Architecture Overview

```
User Request
    ↓
Smart Routing (/craft:do)
    ↓
┌─────────────────────────────────────┐
│  Orchestrator v2                     │
│  - Pattern recognition               │
│  - Agent selection                   │
│  - Mode-aware execution              │
└─────────────────────────────────────┘
    ↓
Parallel Agent Execution
    ↓
Result Synthesis
    ↓
User-Friendly Output
```

## Core Components

### 1. Smart Routing System

The `/craft:do` command uses AI to route tasks to appropriate workflows:

```
"add authentication" → backend-architect + security-specialist
"optimize queries" → performance-engineer + database-architect
"prepare release" → orchestrator (release mode, all agents)
```

### 2. Orchestrator v2

Enhanced multi-agent orchestration with:

- **Mode-aware execution** - Adapts behavior based on mode
- **Context tracking** - Monitors token usage and budget
- **Timeline view** - Visualizes agent execution
- **Subagent monitoring** - Tracks agent progress
- **Result synthesis** - Combines agent outputs

### 3. Mode System

Four execution modes control depth and time:

| Mode | Time | Agents | Use Case |
|------|------|--------|----------|
| default | <10s | 1-2 | Quick checks |
| debug | <120s | 2-3 | Verbose diagnostics |
| optimize | <180s | 3-4 | Parallel performance |
| release | <300s | 4+ | Comprehensive audit |

### 4. Agent Coordination

Agents execute in parallel with automatic coordination:

```python
async def orchestrate(task, mode):
    # Pattern recognition
    pattern = recognize_pattern(task)

    # Agent selection
    agents = select_agents(pattern, mode)

    # Parallel execution
    results = await Promise.all([
        agent1.execute(),
        agent2.execute(),
        agent3.execute()
    ])

    # Synthesis
    return synthesize(results)
```

## Command Organization

Commands organized in 13 categories:

```
craft/commands/
├── arch/          # Architecture analysis
├── ci/            # CI/CD automation
├── code/          # Code quality
├── dist/          # Distribution
├── docs/          # Documentation
├── git/           # Git operations
├── plan/          # Planning
├── site/          # Static sites
├── test/          # Testing
├── check.md       # Pre-flight checks
├── do.md          # Smart routing
├── hub.md         # Discovery
└── orchestrate.md # Orchestration
```

## Python Testing Framework

Craft includes comprehensive Python-based testing:

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── performance/       # Performance benchmarks
└── test_craft.py      # Main test suite
```

**Run tests:**

```bash
cd craft
pytest tests/
pytest tests/ --cov=craft
```

## Performance

- **Parallel execution:** 3-4× faster than sequential
- **Smart caching:** Reduces redundant operations
- **Incremental analysis:** Only checks changed code
- **Token-efficient:** Optimized prompts and context

### 5. Branch Protection Hooks

A PreToolUse hook (`scripts/branch-guard.sh`) enforces branch safety:

```
Claude Code tool call (Write, Edit, Bash)
    ↓
PreToolUse hook reads JSON stdin
    ↓
┌──────────────────────────────────┐
│  branch-guard.sh                 │
│  - Reads .claude/branch-guard.json│
│  - Falls back to auto-detect     │
│  - main → block-all              │
│  - dev  → block-new-code         │
│  - feature/* → allow all         │
└──────────────────────────────────┘
    ↓
exit 0 (allow) or exit 2 (block)
```

**Protection levels:**

| Level | Blocks | Allows |
|-------|--------|--------|
| `block-all` | All file writes, edits, git commits | Read-only operations |
| `block-new-code` | New `.py`, `.sh`, `.js`, `.ts` files | Edits to existing files, docs, specs |

**Bypass:** `/craft:git:unprotect` creates a marker file; `/craft:git:protect` removes it.

#### Defense-in-Depth: Three Layers (Hard_deny + Local Hook + GitHub-Side)

> **NEW in v2.33.0.** Added the `hard_deny` tier on top of the existing two-layer model. The hook + GitHub-side layers remain unchanged; the new tier is unconditional and runs *before* either of them.

The branch-guard model has three layers, each catching a different class of failure:

| Tier | Layer | Enforcement point | Catches | Misses | Bypass |
|------|-------|-------------------|---------|--------|--------|
| 1 | **Hard_deny** (`~/.claude/settings.json` `autoMode.hard_deny`) | Claude Code auto-mode classifier, *before* any tool runs | Catastrophic, irreversible operations: force-push to main, recursive deletion of `.git`, `gh repo delete`, recursive deletion of `~/.claude` | Anything not in the catalog; Bash commands that compose patterns at runtime | **None.** Unconditional. Survives `.claude/allow-once`, `/craft:git:unprotect`, and user intent. Only direct edits to `settings.json` can remove. |
| 2 | **Local hook** (`scripts/branch-guard.sh`) | PreToolUse, per-tool-call, on this machine | Accidental edits to protected branches, new code on `dev`, sensitive paths | Pushes from other machines, web UI commits, CI bots, hook bypass via `--no-verify` | `/craft:git:unprotect` (session-scoped, marker-based) or `.claude/allow-once` (one-shot) |
| 3 | **GitHub-side** (`repos/.../branches/.../protection`) | Server-side, on push | Direct pushes from any source, force-pushes, deletions, missing PR | Anything that happens before the push reaches GitHub | Admin override via `--admin` or removing the protection rule |

```
Claude Code tool call (Write, Edit, Bash, MCP, ...)
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: hard_deny classifier (UNCONDITIONAL)               │
│  ~/.claude/settings.json → autoMode.hard_deny prose rules   │
│  Inherits "$defaults" + craft catalog from                  │
│  scripts/hard-deny-rules.json                               │
└─────────────────────────────────────────────────────────────┘
    ↓  (passes hard_deny — proceed)
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: PreToolUse hook (branch-aware, bypassable)         │
│  scripts/branch-guard.sh                                    │
│  Reads .claude/branch-guard.json + auto-detect              │
└─────────────────────────────────────────────────────────────┘
    ↓  (allowed locally — git push)
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: GitHub-side branch protection (push-time)          │
│  Applied via /craft:git:protect-baseline                    │
└─────────────────────────────────────────────────────────────┘
    ↓
operation completes
```

**Why three tiers, not two?** Tier 1 closes the escape hatch where a user creates `.claude/allow-once` (or runs `/craft:git:unprotect`) and then types a catastrophic command — Tier 2 would correctly honor the bypass, but Tier 1 refuses regardless. This matches the spec's safety criterion #5: hard_deny must survive session bypasses.

**Why the catalog is narrow.** Tier 1 is a prose-rule classifier — it cannot evaluate upstream pipelines or context-dependent commands (`xargs rm`, `find . -delete` with filters, `git reset --hard origin/main` on a feature branch). Those remain in Tier 2's smart-mode where the full command string and current branch are visible. The catalog at `scripts/hard-deny-rules.json` documents which patterns were considered and rejected for Tier 1, with rationale per entry.

**Installation.** `/craft:git:protect` runs an idempotent check and offers to merge craft's rules into `~/.claude/settings.json`, prepending `"$defaults"` so Claude Code's built-in catastrophic protections are inherited. The installer (`scripts/install-hard-deny.sh`) preserves any user-added entries and writes atomically. Opt out with `--no-hard-deny`.

`/craft:git:protect-baseline` provides a one-step way to apply the GitHub-side layer (Tier 3) to any repo with craft's standard baseline (PR required with 0 reviews, no force-push, no delete, optional status checks). The three install commands are deliberately separate because:

1. **Different scope** — Tier 1 is global (`~/.claude/`), Tier 2 is per-machine + stateful, Tier 3 is per-repo + persistent
2. **Different invocation** — Tier 1 needs no API, Tier 2 needs no API, Tier 3 requires authenticated `gh` CLI
3. **Different bypass semantics** — `/craft:git:unprotect` only affects Tier 2; Tier 1 is unconditional; Tier 3 requires `protect-baseline --remove`

The three layers are complementary, not redundant: Tier 1 is the unconditional catastrophe-prevention shield, Tier 2 is the fast, opinionated, teaching-oriented branch shield, and Tier 3 is the immutable server-side backstop.

### 6. Documentation Quality Toolchain

Automated detection of documentation drift across 4 phases:

```
scripts/docs-staleness-check.sh
    ↓
Phase 6: Nav Completeness    → mkdocs.yml vs docs/ files
Phase 7: Count Consistency   → "110 commands" refs match reality
Phase 8: Coverage            → skills/agents/commands in docs
Phase 9: Cross-Doc Freshness → stale summary lines
    ↓
Traffic light: GREEN | YELLOW | RED
```

Integrated into `/craft:check`, `pre-release-check.sh`, and CI (`docs-quality.yml`).
Shared exclusion config at `scripts/config/exclusions.txt` for orchestrator mode descriptions and tutorial examples.

## Extensibility

Craft is designed for easy extension:

1. **Add commands:** Create markdown in `commands/category/`
2. **Add skills:** Create skill definitions in `skills/domain/`
3. **Add agents:** Define agents in `agents/`
4. **Add modes:** Extend mode system with custom time budgets

## See Also

- **[Commands Reference](commands.md)** - All commands
- **[Skills & Agents](skills-agents.md)** - 39 skills, 8 agents
- **[Orchestrator Guide](orchestrator.md)** - Coordination details
