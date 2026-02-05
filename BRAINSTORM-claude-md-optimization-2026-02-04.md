# CLAUDE.md Optimization & Command Reform — Brainstorm

**Generated:** 2026-02-04
**Context:** craft plugin `/craft:docs:claude-md:*` commands
**Depth:** max | **Focus:** architecture + feature

---

## The Problem (Measured)

| File | Lines | ~Bytes | ~Tokens | Loaded |
|------|-------|--------|---------|--------|
| **Craft CLAUDE.md** | 535 | 30,863 | ~8,500 | Every session |
| **Global CLAUDE.md** | 413 | 12,742 | ~3,500 | Every session |
| **Combined** | 948 | 43,605 | ~12,000 | **Every. Single. Session.** |

Anthropic recommends **< 300 lines**. HumanLayer's production file is **< 60 lines**.

### Where the bloat lives (Craft CLAUDE.md)

| Section | Lines | % of File | Useful for Coding? |
|---------|-------|-----------|-------------------|
| **Release history** (v2.4–v2.11) | 174 | 33% | ❌ Never |
| **Recent Releases** (duplicate!) | 32 | 6% | ❌ Never |
| **Phase 3 Docs Enhancements** | 28 | 5% | ❌ Rarely |
| **Feature Status Matrix** | 40 | 7% | ❌ Rarely |
| **Integration Test Categories** | 20 | 4% | ⚠️ Sometimes |
| **Completed Features tables** | 15 | 3% | ❌ Never |
| **Total waste** | **~309** | **~58%** | |

**The rule of thumb:** if Claude needs to `Read` a file to get the detail, it shouldn't be in CLAUDE.md.

Release notes are historical artifacts. They describe what *was built*, not how to *build now*. They consume 39% of the file and help with 0% of coding tasks.

---

## Research: What Anthropic + Community Recommends

### From Anthropic's Official Best Practices

1. **CLAUDE.md goes into every session** — keep it universally applicable
2. **~150–200 instructions** is the reliable ceiling for frontier models
3. **Beginning and end** of prompt get stronger attention (middle gets lost)
4. **Progressive disclosure** — load detail on-demand, not upfront
5. **Use Skills** for specialized workflows (loaded only when invoked)
6. **Use linters** instead of style rules — "never send an LLM to do a linter's job"

### From the Community (54% Context Reduction Gist)

7. **Trigger tables > verbose protocols** — 70% reduction
8. **Merge duplicate content** — 82% reduction
9. **Hard rules only**, no examples/edge cases — 78% reduction
10. **Don't need verbose docs upfront** — need *triggers* to know when to load detail

### The Progressive Disclosure Pattern

```
CLAUDE.md (always loaded)     → Quick reference, pointers, triggers
├── Skills (on-demand)        → Detailed workflows when invoked
├── agent_docs/*.md           → Deep context when needed
└── Read tool                 → Full file contents when required
```

---

## Proposal A: Slim CLAUDE.md (Aggressive — Target < 200 Lines)

### What stays

- TL;DR header (1 line)
- Git Workflow (15 lines — essential for every session)
- Quick Commands table (15 lines — daily use)
- Execution Modes table (8 lines — affects every command)
- Agent table (10 lines — routing reference)
- Project Structure (15 lines — navigation)
- Key Files (20 lines — **pruned to top 15 most-used**)
- Test Suite summary (10 lines — just the run commands, not per-file)
- Troubleshooting (10 lines — critical issues only)
- Active Development status (10 lines — current branch + version only)
- Links (8 lines)

**Estimated: ~140 lines (~3,800 tokens)**

### What gets removed entirely

| Section | Lines Cut | Replacement |
|---------|-----------|-------------|
| Recent Major Features (v2.4–v2.11) | -174 | → `docs/VERSION-HISTORY.md` (already exists!) |
| Recent Releases (duplicate) | -32 | → `docs/VERSION-HISTORY.md` |
| Feature Status Matrix | -40 | → `docs/FEATURE-STATUS.md` (new file) |
| Integration Features (v1.24.0) | -20 | → `docs/guide/integration-testing.md` (exists) |
| Phase 3 Docs section | -28 | → Already in VERSION-HISTORY.md |
| Completed Features tables | -15 | → VERSION-HISTORY.md |
| Per-test-file breakdown table | -25 | → Just keep run command |
| CRAFT-001 detail section | -15 | → Already in docs/specs/ |
| **Total cut** | **~349 lines** | |

### What gets condensed

| Section | Before | After | How |
|---------|--------|-------|-----|
| Key Files table | 40 lines | 20 lines | Top 15 files only |
| Test Suite | 25 lines | 8 lines | Just run commands |
| Active Development | 30 lines | 10 lines | Version + branch only |
| Documentation Guides | 20 lines | 8 lines | Just links |

---

## Proposal B: Command-Level Changes to `/craft:docs:claude-md:*`

### B1: Add `optimize` subcommand (new default behavior)

**Problem:** Current `update --optimize` just "condenses verbose sections." It doesn't enforce token budgets or cut release history.

**New behavior:**

```bash
/craft:docs:claude-md:update --optimize   # or: /craft:docs:claude-md:optimize
```

**What it does:**

| Check | Action |
|-------|--------|
| **Line count > 300** | Flag as bloated, suggest cuts |
| **Release history present** | Move to VERSION-HISTORY.md, replace with 1-line pointer |
| **Duplicate information** | Detect and consolidate |
| **Completed/historical tables** | Move to separate docs, replace with pointer |
| **Per-file test breakdowns** | Collapse to summary + run command |
| **Section-level token budget** | Flag sections > 30 lines |

**Output:**

```
CLAUDE.md Optimization Report

Current:  535 lines (~8,500 tokens)
Target:   < 300 lines (~4,000 tokens)
Savings:  ~4,500 tokens per session

Cuts:
  ✂ Release History (174 lines) → VERSION-HISTORY.md
  ✂ Feature Matrix (40 lines) → FEATURE-STATUS.md
  ✂ Duplicate Releases (32 lines) → removed
  ✂ Phase 3 Detail (28 lines) → VERSION-HISTORY.md
  ✂ Test file breakdown → collapsed to summary

Apply optimizations? [y/n]
```

### B2: Add `--budget` flag to scaffold

```bash
/craft:docs:claude-md:scaffold --budget=200   # Max 200 lines
/craft:docs:claude-md:scaffold --budget=lean   # Alias for 150
/craft:docs:claude-md:scaffold --budget=full   # No limit (current behavior)
```

**How it works:**

- Template populator tracks line count per section
- Sections get trimmed in priority order:
  1. Release history (first to cut)
  2. Detailed tables (collapse to summaries)
  3. Examples (reduce to 1 per section)
  4. Key files (top 10 only)

### B3: Add audit check for bloat

```bash
/craft:docs:claude-md:audit
```

**New check added to existing 5:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Token Budget** | File exceeds 300 lines or ~4,000 tokens | Warning |
| **Release History** | Contains release notes/changelog content | Warning |
| **Duplicate Content** | Same info in multiple sections | Info |

### B4: Update templates to be lean-first

Current `plugin-template.md` is 91 lines — good. But the problem is that **after population**, the file balloons as the `update` command keeps adding sections.

**Fix:** Add a `# --- DO NOT ADD BELOW THIS LINE ---` marker or equivalent convention. Content that grows (release notes, feature matrices) goes in referenced docs, not CLAUDE.md.

### B5: New `prune` subcommand

```bash
/craft:docs:claude-md:prune           # Interactive pruning
/craft:docs:claude-md:prune --auto    # Auto-prune with sensible defaults
```

**What it prunes:**

1. Sections older than 2 releases (move to VERSION-HISTORY.md)
2. Completed feature sections (move to docs)
3. Duplicate information across sections
4. Example blocks beyond 1 per section

---

## Proposal C: Template Architecture Reform

### C1: Two-tier template system

```
templates/claude-md/
├── lean/                     # < 200 lines (new default)
│   ├── plugin-template.md
│   ├── teaching-template.md
│   └── r-package-template.md
├── full/                     # Current templates (opt-in)
│   ├── plugin-template.md
│   ├── teaching-template.md
│   └── r-package-template.md
└── sections/                 # Reusable section snippets
    ├── git-workflow.md
    ├── testing.md
    └── troubleshooting.md
```

### C2: Section priority system

Each template section gets a priority:

```yaml
sections:
  - name: "Git Workflow"
    priority: P0    # Always included
    max_lines: 15
  - name: "Quick Commands"
    priority: P0
    max_lines: 15
  - name: "Project Structure"
    priority: P0
    max_lines: 15
  - name: "Key Files"
    priority: P1    # Included if under budget
    max_lines: 20
  - name: "Test Suite"
    priority: P1
    max_lines: 10
  - name: "Agents"
    priority: P1
    max_lines: 10
  - name: "Recent Changes"
    priority: P2    # Cut first
    max_lines: 5    # Just "see VERSION-HISTORY.md"
  - name: "Feature Matrix"
    priority: P2
    max_lines: 0    # Always in separate file
```

### C3: "Pointer, not content" pattern

For every section that tends to grow unbounded:

```markdown
## Recent Changes

See [VERSION-HISTORY.md](docs/VERSION-HISTORY.md) for full release history.

**Latest:** v2.11.0 (2026-02-03) — Test suite cleanup, CRAFT-001 lint rule
```

2 lines instead of 174. Same information accessible via `Read` when needed.

---

## Proposal D: Global CLAUDE.md Optimization

The global file (413 lines) loads into *every project session* — even projects that don't use half the documented tools.

### D1: What to keep (global)

| Section | Lines | Verdict |
|---------|-------|---------|
| Git Workflow & Standards | 50 | ✅ Keep (universal) |
| Project Structure overview | 15 | ✅ Keep (navigation) |
| Shell workflow commands | 15 | ✅ Keep (daily use) |
| MCP Server table | 15 | ⚠️ Trim to names only |
| Plugin list | 10 | ⚠️ Trim to names only |
| Claude MCP Browser Extension | 15 | ❌ Move to project CLAUDE.md |
| Release Automation | 30 | ❌ Move to homebrew-tap CLAUDE.md |
| @smart Prompt Enhancement | 20 | ⚠️ Trim to 5 lines |
| Thinking Mode | 15 | ⚠️ Trim to 3 lines |
| Detailed worktree examples | 20 | ❌ Already in rules/ |

**Estimated savings: ~150 lines (413 → ~260)**

---

## Recommended Path

### Phase 1: Quick Wins (This Session)

1. **Gut the craft CLAUDE.md**: Remove release history, feature matrix, duplicates → save ~300 lines
2. **Add bloat audit check**: Extend auditor with line-count + release-note detection
3. **Update `optimize` behavior**: Make it actually enforce a budget

### Phase 2: Command Updates (Next Session)

4. **Add `prune` subcommand**: Automated history-to-docs migration
5. **Add `--budget` to scaffold**: Lean-first templates
6. **Two-tier templates**: `lean/` (default) + `full/` (opt-in)

### Phase 3: Systemic Changes (Later)

7. **Section priority system** in templates
8. **Global CLAUDE.md slim-down**
9. **Pointer pattern** enforcement in update command

---

## Anti-Patterns to Encode as Rules

| Anti-Pattern | Why It's Bad | Rule |
|--------------|-------------|------|
| Release notes in CLAUDE.md | Historical detail ≠ coding guidance | Never. Use VERSION-HISTORY.md |
| "Files Changed: 28 (+1,711/-801)" | Meaningless for future sessions | Never include diffstats |
| Duplicate sections | Same content, double the tokens | Deduplicate aggressively |
| Per-test-file breakdowns | Claude can `Read` the test dir | Summary + run command only |
| Feature completion percentages | Stale within days | Move to .STATUS |
| "Phase N" implementation details | Historical planning artifacts | Remove after release |
| Full PR merge details | GitHub has this data | Never in CLAUDE.md |

---

## Decision Points for You

1. **How aggressive?** Proposal A (< 200 lines) vs moderate trim (< 300 lines)?
2. **New command?** Add `/craft:docs:claude-md:prune` or enhance existing `optimize`?
3. **Template reform?** Two-tier system or just update current templates?
4. **Global CLAUDE.md?** Trim it now or focus on project-level first?
5. **Should `update` command prevent adding release notes?** (Hard rule vs warning)

---

## Sources

- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) (redirects to code.claude.com)
- [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [54% Context Reduction Gist](https://gist.github.com/johnlindquist/849b813e76039a908d962b2f0923dc9a)
- [Anthropic: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Claude Code Context Optimization](https://hyperdev.matsuoka.com/p/how-claude-code-got-better-by-protecting)
- [Claude Code Cost Management](https://code.claude.com/docs/en/costs)
- [Claude Skills & CLAUDE.md 2026 Guide](https://www.gend.co/blog/claude-skills-claude-md-guide)
