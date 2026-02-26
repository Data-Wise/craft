# /craft:docs:claude-md:sync

> **Sync CLAUDE.md with project state — update metrics, audit, fix, optimize.**

---

## Synopsis

```bash
/craft:docs:claude-md:sync [options]
```

**Quick examples:**

```bash
# Full sync: detect project state, update metrics, audit
/craft:docs:claude-md:sync

# Sync and auto-fix any issues found
/craft:docs:claude-md:sync --fix

# Enforce line budget and move bloat to detail files
/craft:docs:claude-md:sync --optimize
```

---

## Description

Runs a 4-phase pipeline that keeps CLAUDE.md accurate and lean. Phase 1 detects the project type and version source. Phase 2 updates stale metrics (version, command counts, test counts). Phase 3 audits for issues across 5 validation checks. Phase 4 optionally fixes issues and enforces the line budget.

This command replaces the old `update`, `audit`, and `fix` commands with a single unified pipeline. Audit always runs after metric updates. Fix and optimize are controlled by their respective flags.

The sync command also detects and blocks common anti-patterns such as release notes, diffstats, "what shipped" sections, and completed feature lists from accumulating in CLAUDE.md. These are redirected to detail files like `VERSION-HISTORY.md`.

---

## Options

| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--fix` | | `false` | Auto-fix issues found during audit |
| `--optimize` | `-o` | `false` | Enforce line budget, move bloat to detail files |
| `--dry-run` | `-n` | `false` | Preview changes without applying |
| `--global` | `-g` | `false` | Target `~/.claude/CLAUDE.md` instead of project |
| `--section` | `-s` | `all` | Specific section to update: `status`, `commands`, `testing`, `all` |

---

## How It Works

### 4-Phase Pipeline

**Phase 1: Detect** — Scans the project for current state (type, version source, filesystem counts).

**Phase 2: Update Metrics** — Refreshes stale numbers in CLAUDE.md: version, command/skill/agent counts, test count, documentation percentage.

**Phase 3: Audit** — Validates completeness and accuracy with 5 checks:

| Check | Severity | What It Validates |
|-------|----------|-------------------|
| Version accuracy | Error | Version matches plugin.json or equivalent |
| Command counts | Error | Counts match filesystem |
| Section completeness | Warning | Required sections present |
| Link validity | Warning | Internal links resolve |
| Anti-pattern detection | Info | Common CLAUDE.md bloat patterns |

**Phase 4: Fix / Optimize** (flag-controlled) — `--fix` auto-corrects fixable issues (version mismatches, stale references). `--optimize` enforces the line budget by classifying sections as P0/P1/P2 and moving bloat to detail files, replacing it with pointer lines.

### Budget Enforcement

The line budget defaults to 150 and is resolved from: `.claude-plugin/config.json` (`claude_md_budget`), then `package.json` (`claudeMd.budget`), then the default. Do not place `claude_md_budget` in `plugin.json` — Claude Code's strict schema rejects unrecognized keys.

---

## See Also

- [claude-md command suite](../claude-md.md) — Hub page for all claude-md commands
- [/craft:docs:claude-md:init](init.md) — Create new CLAUDE.md from template
- [/craft:docs:claude-md:edit](edit.md) — Interactive section editing
