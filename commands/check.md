---
description: Universal pre-flight check that validates project readiness
arguments:
  - name: mode
    description: Check depth (default|thorough)
    required: false
    default: default
  - name: for
    description: What to check for (commit|pr|release|deploy)
    required: false
  - name: dry-run
    description: Preview checks that will be performed without executing them
    required: false
    default: false
    alias: -n
  - name: orch
    description: Enable orchestration mode (NEW in v2.5.0)
    required: false
    default: false
  - name: orch-mode
    description: "Orchestration mode: default|debug|optimize|release (NEW in v2.5.0)"
    required: false
    default: null
  - name: context
    description: Output session context header only (no checks)
    required: false
    default: false
  - name: version
    description: "Run version sync validator only (Tier 1 files: plugin.json + 12 mechanically-synced refs). Use mode=thorough for Tier 2 sweep, mode=release for fatal-on-drift (NEW in v2.33.0)"
    required: false
    default: false
deprecated: true
replaced-by: "skills/check/"
---

# /craft:check - Universal Pre-flight

> **This command is a thin(ner) shim.** The canonical decision logic —
> which validators run for which `--for` context, mode budgets, follow-up
> routing on failure — lives in the `preflight-check` skill
> (`skills/check/SKILL.md`). This file keeps the parts that are
> invocation-specific and can't be deferred to skill-routing: the flag
> contract above, and the exact LLM-executable output format Claude must
> produce when this command runs (kept here per
> `skills/code/command-skill-token-efficiency/SKILL.md`'s rule that
> anything the command always needs — even if skill-routing hasn't fired
> yet — stays in the command file).
>
> **Scope note:** the pre-consolidation version of this command also carried
> full per-language project-detection walls (Python/Node/R/Go check lists),
> an extensive "community validator marketplace" section, and duplicated
> ASCII dry-run mockups for every mode/context combination. That's
> illustrative/aspirational content, not unique behavior — the skill's
> `--for`/mode tables already capture the decision logic, and
> `.claude-plugin/skills/validation/*.md` own the actual per-validator
> implementation. Dropped rather than ported; see the skill for anything
> that looks missing.

## Usage

```bash
/craft:check                    # Quick validation
/craft:check thorough           # Deep validation
/craft:check --for commit       # Pre-commit checks
/craft:check --for pr           # Pre-PR checks
/craft:check --for release      # Pre-release checks
/craft:check --dry-run          # Preview checks
/craft:check -n                 # Preview checks
/craft:check --context              # Output session context only
```

## Execution Behavior (MANDATORY)

When this command runs, Claude MUST follow these steps in order. Do NOT skip
any step or proceed without showing the plan first.

### Step 0: Show Check Plan

Before running ANY checks, display what will be checked:

```text
Pre-flight Check Plan:
  Project: <project-name> (<project-type>)
  Mode: <mode>
  Branch: <current-branch>
  Guard: <protection-status>
  Context: <for-value or "general">

  Checks to run:
  1. <check-name> (<tool>)
  2. <check-name> (<tool>)
  ...
  N. <check-name> (<tool>)
```

### Context-Only Mode (--context)

When `--context` is passed, skip all checks and output only session context:

```text
┌───────────────────────────────────────────────────────────────┐
│ SESSION CONTEXT                                               │
├───────────────────────────────────────────────────────────────┤
│ Project:   <name> (<type>)                                    │
│ Branch:    <current-branch>                                   │
│ Worktree:  <path or "main repo">                              │
│ Base:      <base-branch>                                      │
│ Guard:     <status>                                           │
│ Phase:     <phase> (commits ahead: N)                         │
│ Tests:     <test-command> (N passing)                         │
│ Lint:      <lint-command>                                     │
│ Docs:      <GREEN|YELLOW|RED> (<N> issues)                    │
├───────────────────────────────────────────────────────────────┤
│ TIP: Front-load this context in prompts to reduce wrong-      │
│ approach friction.                                            │
└───────────────────────────────────────────────────────────────┘
```

**Phase detection logic:**

- `implementation`: commits ahead of base, no PR exists
- `testing`: test files modified recently
- `pr-prep`: PR exists for branch, branch is clean
- `release`: on dev branch, features merged

**How to detect:**

```bash
# Phase detection
commits_ahead=$(git rev-list --count dev..HEAD 2>/dev/null || echo 0)
pr_exists=$(gh pr list --head "$(git branch --show-current)" --json number --jq length 2>/dev/null || echo 0)
test_modified=$(git diff --name-only HEAD~3 2>/dev/null | grep -c "test" || echo 0)
tree_clean=$(git status --porcelain | wc -l | tr -d ' ')

if [[ "$(git branch --show-current)" == "dev" ]]; then
    phase="release"
elif [[ "$pr_exists" -gt 0 && "$tree_clean" -eq 0 ]]; then
    phase="pr-prep"
elif [[ "$test_modified" -gt 0 ]]; then
    phase="testing"
else
    phase="implementation"
fi

# Docs staleness one-liner for context header
docs_status=$(./scripts/docs-staleness-check.sh --json 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"status\"]} ({d[\"total_issues\"]} issues)')" 2>/dev/null \
    || echo "N/A")
```

**Insights integration:** if `~/.claude/usage-data/facets/` exists, append a
friction summary (top patterns + `/craft:insights` pointer) to the context
output.

When `--context` is passed, the command exits after displaying this header. No checks are executed.

### Step 0.5: Confirm Before Running

After showing the plan, ask before executing (via `AskUserQuestion`):

```json
{
  "questions": [{
    "question": "Run these pre-flight checks?",
    "header": "Check",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes - Run all (Recommended)",
        "description": "Execute all <N> checks as shown above."
      },
      {
        "label": "Skip lint (faster)",
        "description": "Run all checks except linting."
      },
      {
        "label": "Skip external links (faster)",
        "description": "Run all checks except external link validation."
      },
      {
        "label": "Dry run (show commands only)",
        "description": "Show the exact commands without executing them."
      }
    ]
  }]
}
```

### Steps 1-N: Execute with Progress

Run each check and display results as they complete, then a summary:

```text
  [1/N] <check-name>... ✅ passed (X issues)
  [2/N] <check-name>... ❌ failed (Y errors)
  ...
  Results: X/N checks passed
  Issues: Y warnings, Z errors
  Next steps: [actionable recommendations]
```

## What Runs Where

Which checks run for which `--for` context and mode, and how each is
implemented (lint, tests, version sync, stale refs, hook conflicts, skill
standards, badges, formula desc, CLAUDE.md health, etc.), is decision logic
owned by [`skills/check/SKILL.md`](../skills/check/SKILL.md) — read it for
the full `--for`/mode tables and the validator-routing rules. Do not
reimplement that logic here; if it looks wrong or incomplete, fix the skill.

Two things stay pinned to this command file because they're invocation
mechanics, not decision logic:

### Orchestration Mode (`--orch`)

```bash
/craft:check --orch                 # Orchestrated validation with mode prompt
/craft:check --orch=optimize        # Fast parallel check execution
/craft:check --orch=release --dry-run   # Preview orchestrated validation
```

```python
from utils.orch_flag_handler import handle_orch_flag, show_orchestration_preview, spawn_orchestrator

orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

if orch_flag:
    should_orchestrate, mode = handle_orch_flag(
        "comprehensive project validation",
        orch_flag,
        mode_flag
    )

    if dry_run:
        show_orchestration_preview(
            f"validation workflow with {args.mode} mode",
            mode
        )
        return

    spawn_orchestrator(
        f"run comprehensive checks for {args.for or 'general'} context",
        mode
    )
    return

# Otherwise, continue with normal check flow...
```

### Hot-Reload Validator Discovery + `CRAFT_MODE` Binding (REQUIRED)

`/craft:check` scans `.claude-plugin/skills/validation/*.md` for
`hot_reload: true` validators and executes each in a forked context. Validators
receive their tier **only** through the `CRAFT_MODE` environment variable —
there is no separate `--for` signal inside a validator. Resolve `CRAFT_MODE`
from the active context and **export it on each validator invocation**:

| Active context | Exported `CRAFT_MODE` | Effect on release-gated validators (version-check, skill-standards) |
|----------------|-----------------------|----------------------------------------------------------------------|
| `--for commit`, `--for pr`, default | `default` (or the explicit mode arg) | advisory / warn-only |
| `--for release`, `--for deploy`, `release` mode | `release` | **blocking** — validator propagates its exit code |

Concretely: `/craft:check --for release` MUST invoke each validator as
`CRAFT_MODE=release bash <validator>.md`. Omitting this export silently
downgrades every release-tier gate to advisory.

## Doc Surfaces Warning (non-blocking)

When `--for commit` is active (or mode is default and staged files include
`commands/**/*.md`), print a non-blocking checklist — never fails the check:

```bash
new_cmds=$(git diff --cached --name-only --diff-filter=A -- 'commands/**/*.md' 2>/dev/null || true)
if [[ -n "$new_cmds" ]]; then
    echo ""
    echo "⚠️  New commands detected. Doc surfaces needed:"
    bash scripts/doc-coverage-check.sh --since origin/dev 2>/dev/null || true
    echo ""
    echo "Run /craft:docs:update --post-merge to fill gaps."
fi
```

## Quota Pre-flight (opt-in, never blocking)

After all mandatory checks, surface a quota advisory if a fresh cache file
(`~/.claude/quota-cache.json`, timestamp < 900s old) is present:

```bash
CACHE="$HOME/.claude/quota-cache.json"
NOW=$(date +%s)
if [[ -f "$CACHE" ]]; then
    TS=$(python3 -c "import json; d=json.load(open('$CACHE')); print(d.get('timestamp',0))" 2>/dev/null || echo 0)
    AGE=$(( NOW - TS ))
    if [[ "$AGE" -lt 900 ]]; then
        LEVEL=$(python3 -c "import json; d=json.load(open('$CACHE')); print(d.get('level',''))" 2>/dev/null)
        case "$LEVEL" in
            SAFE)   echo "✅ Quota: SAFE — sufficient tokens for this run" ;;
            TIGHT)  echo "⚠️  Quota: TIGHT — approaching limit; consider batching" ;;
            DEFER)  echo "💡 Quota: DEFER recommended — low tokens; run /craft:quota first" ;;
        esac
    fi
fi
```

Populate the cache with `/craft:quota <run-type>` before `/craft:check`; the
cache auto-expires after 15 minutes.

## Output Format

```
╭─ /craft:check ──────────────────────────────────────╮
│ Project: aiterm (Python CLI)                       │
│ Time: 12.4s                                        │
├─────────────────────────────────────────────────────┤
│ ✓ Lint         0 issues                            │
│ ✓ Tests        135/135 passed                      │
│ ✓ Types        No errors                           │
│ ✓ Git          Clean working tree                  │
├─────────────────────────────────────────────────────┤
│ STATUS: ALL CHECKS PASSED ✓                        │
╰─────────────────────────────────────────────────────╯
```

On issues, use the same box format with per-issue detail lines and a
`STATUS: N ISSUES FOUND` footer plus a fix suggestion (e.g.
`/craft:code:ci-fix`).

## Integration

Works with:

- `/craft:code:lint` - Detailed code lint results
- `/craft:test` - Detailed test results
- `/craft:docs:lint` - Markdown quality validation
- `/craft:docs:check-links` - Documentation link validation
- `/craft:code:ci-fix` - Auto-fix issues
- `/craft:code:ci-local` - Full CI simulation
- `/craft:quota` - Standalone pre-flight quota check
- `/craft:check:gen-validator` - Scaffold a new custom validator (see the skill's "Validator Generation" section for the full flow)
