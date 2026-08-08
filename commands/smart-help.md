---
description: Context-aware help that suggests relevant commands
arguments:
  - name: topic
    description: Topic or question to get help with
    required: false
  - name: refine
    description: Refine the topic via the prompt-refiner skill before acting
    required: false
    default: false
---

# /craft:smart-help - Context-Aware Help

Get intelligent help based on your project and question.

## Usage

```bash
/craft:smart-help                     # Show relevant commands for current project
/craft:smart-help <topic>             # Get help on specific topic
/craft:smart-help "how do I..."       # Answer questions about workflows
```

## --refine (prompt pre-processing)

When `--refine` is set, do NOT act on the raw `topic` argument. First invoke the
`prompt-refiner` skill with the argument and project context. Follow that
skill's canonical flow (before/after box → fenced refined-prompt block →
4-way confirm: Execute now / Copy for elsewhere / Edit first / Skip; `--yes`
or auto mode auto-accepts Execute now). **If the user picks "Copy for
elsewhere," stop here — do not start help lookup.** Otherwise proceed using
the prompt the skill returns. Off by default (`--refine` is opt-in): most
`topic` arguments here are a single keyword or a short question, where the
rewrite round-trip adds little over the skip-gate already handling terse
prompts.

## Context-Aware Suggestions

### Based on Project Type

**Python Project:**

```
╭─ Suggested Commands for Python Project ─────────────╮
│                                                     │
│ Development:                                        │
│   /craft:code:lint         ruff, flake8 checks     │
│   /craft:test          pytest runner           │
│   /craft:test --coverage     coverage report         │
│                                                     │
│ Quality:                                            │
│   /craft:code:deps-audit   pip-audit security      │
│   /craft:ci:local     pre-commit simulation   │
│                                                     │
│ Release:                                            │
│   /craft:code:release      PyPI workflow           │
│   /craft:docs:changelog    update CHANGELOG.md     │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**R Package:**

```
╭─ Suggested Commands for R Package ──────────────────╮
│                                                     │
│ Development:                                        │
│   /craft:test          testthat runner         │
│   /craft:code:lint         lintr checks            │
│   /craft:code:docs-check   roxygen2 validation     │
│                                                     │
│ Quality:                                            │
│   /craft:ci:local     R CMD check simulation  │
│   /craft:arch:analyze      package structure       │
│                                                     │
│ Release:                                            │
│   /craft:code:release      CRAN submission prep    │
│   /craft:site:build        pkgdown site            │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

### Based on Current State

**Uncommitted Changes:**

```
╭─ You have uncommitted changes ──────────────────────╮
│                                                     │
│ Suggested:                                          │
│   /craft:check             Quick validation        │
│   "commit and push"        dev/git skill           │
│   "git recap"              dev/git skill           │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**Failing Tests:**

```
╭─ Tests are failing ─────────────────────────────────╮
│                                                     │
│ Suggested:                                          │
│   /craft:test debug        Debug the failures      │
│   /craft:code:debug        Investigate root cause  │
│   /craft:test --coverage   Check test coverage     │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**Branch guard friction detected** (guard blocked an operation recently):

```
╭─ Guard friction detected ─────────────────────╮
│                                                │
│ Suggested:                                     │
│   ask "audit guard"      Analyze guard config, │
│   (guard-audit skill)    find false positives   │
│   ask "unprotect"        Session-scoped bypass │
│   (dev/git skill)        (temporary)            │
│                                                │
╰────────────────────────────────────────────────╯
```

**Session start** (new session, no prior context):

```
╭─ New session ──────────────────────────────────╮
│                                                │
│ Suggested:                                     │
│   /craft:check --context  Front-load session   │
│                           context (branch,      │
│                           worktree, phase)      │
│                                                │
╰────────────────────────────────────────────────╯
```

**In a worktree** (CWD is inside `~/.git-worktrees/`):

```
╭─ Worktree detected ───────────────────────────╮
│                                                │
│ Suggested:                                     │
│   "check my worktree health"    dev/git skill  │
│   /craft:check --context        Session context│
│                                                │
╰────────────────────────────────────────────────╯
```

**Insights data exists** (`~/.claude/usage-data/report.html` present):

```
╭─ Insights data available ─────────────────────╮
│                                                │
│ Suggested:                                     │
│   ask "apply insights"   Apply insights         │
│   (insights-apply skill) suggestions to          │
│                          CLAUDE.md              │
│                                                │
╰────────────────────────────────────────────────╯
```

**Release preparation** (on dev, features merged):

```
╭─ Ready for release ───────────────────────────╮
│                                                │
│ Suggested:                                     │
│   /release               Interactive release   │
│   /release --autonomous   Fully automated       │
│                           (no prompts)          │
│   /release -n             Dry-run preview       │
│                                                │
╰────────────────────────────────────────────────╯
```

## Topic-Based Help

### Testing

```bash
/craft:smart-help testing

╭─ Testing Commands ──────────────────────────────────╮
│                                                     │
│ /craft:test [mode]     Run tests               │
│   Modes: default, debug, optimize, release         │
│                                                     │
│ /craft:test --watch        Watch mode              │
│   Re-runs tests when files change                  │
│                                                     │
│ /craft:test --coverage     Coverage analysis       │
│   Shows untested code paths                        │
│                                                     │
│ /craft:test debug          Debug failures          │
│   Step through failing tests                       │
│                                                     │
│ Related:                                            │
│   /craft:code:test-gen     Generate test files     │
│   /craft:ci:local     Run full CI checks      │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

### Architecture

```bash
/craft:smart-help architecture

╭─ Architecture Commands ─────────────────────────────╮
│                                                     │
│ /craft:arch:analyze [mode] Analyze structure       │
│   Modes: default, debug, optimize, release         │
│                                                     │
│ /craft:arch:plan           Design features         │
│   Architecture planning assistance                 │
│                                                     │
│ /craft:arch:review         Review changes          │
│   Check architecture consistency                   │
│                                                     │
│ /craft:arch:diagram        Generate diagrams       │
│   Creates Mermaid diagrams                         │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

### Orchestration

```bash
/craft:smart-help orchestration

╭─ Orchestration Modes ───────────────────────────────╮
│                                                     │
│ /craft:orch         Improvised multi-agent  │
│   LLM reasons "what next" each turn (exploratory)  │
│                                                     │
│ /craft:orch:drive   Spec → verified green   │
│   Autonomous /goal loop with a real verify gate    │
│                                                     │
│ /craft:orch:workflow  Coded, fixed program  │
│   parallel/pipeline/verify, schema-gated agents,   │
│   data-driven fan-out, cached/resumable replay     │
│   Best for: decompose → cover → verify → synthesize│
│                                                     │
╰─────────────────────────────────────────────────────╯
```

## Question Answering

```bash
/craft:smart-help "how do I run tests?"
→ Use /craft:test to run your test suite

/craft:smart-help "how do I run a fixed, repeatable multi-agent shape?"
→ Use /craft:orch:workflow for a coded, schema-gated, resumable workflow
→ Preview it first with /craft:orch:workflow --dry-run

/craft:smart-help "how do I prepare a release?"
→ Use /craft:code:release for the full release workflow

/craft:smart-help "how do I check code quality?"
→ Use /craft:check for quick validation
→ Use /craft:ci:local for full CI simulation

/craft:smart-help "what commands are available?"
→ Use /craft:hub to see all 115 commands
```

## Quick Reference

| Category | Commands | For |
|----------|----------|-----|
| **Code** | lint, coverage, deps-check, ci-local | Development |
| **Test** | run, watch, coverage, debug | Testing |
| **Arch** | analyze, plan, review, diagram | Design |
| **Orchestrate** | orchestrate, drive, workflow | Multi-agent execution |
| **Plan** | feature, sprint, roadmap | Planning |
| **Docs** | sync, changelog, validate | Documentation |
| **Site** | init, build, preview, deploy | Doc sites |
| **Git** | branch, sync, clean, recap | Git workflow |

## Integration

For complete command listing:

- `/craft:hub` - Full command discovery
- `/craft:hub <category>` - Category deep dive
