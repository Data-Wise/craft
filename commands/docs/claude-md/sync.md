---
description: Sync CLAUDE.md with project state - update metrics, audit, fix, optimize
category: docs
arguments:
  - name: fix
    description: Auto-fix issues found during audit
    required: false
    default: false
  - name: optimize
    description: Enforce < 150 line budget, move bloat to detail files
    required: false
    default: false
    alias: -o
  - name: dry-run
    description: Preview changes without applying
    required: false
    default: false
    alias: -n
  - name: global
    description: Target ~/.claude/CLAUDE.md instead of project
    required: false
    default: false
    alias: -g
  - name: section
    description: "Specific section to update: status, commands, testing, all (default: all)"
    required: false
    default: all
    alias: -s
tags: [documentation, claude-md, sync, audit, fix, optimize]
version: 2.0.0
---

# /craft:docs:claude-md:sync - Unified CLAUDE.md Sync

Synchronize CLAUDE.md with project state. Runs a 4-phase pipeline: detect project type → update metrics → audit for issues → optionally fix and optimize.

**This command replaces** `update`, `audit`, and `fix` as separate commands. Audit always runs after updates. Fix and optimize are flag-controlled.

## What It Does

1. **Detect** - Project type, version source, counts
2. **Update Metrics** - Version, command/skill/agent counts, test count, docs%
3. **Audit** - 5 validation checks + anti-pattern detection + budget check
4. **Fix** (with `--fix`) - Auto-fix fixable issues
5. **Optimize** (with `--optimize`) - Enforce < 150 line budget, move bloat to detail files

## Anti-Pattern Blocking

The sync command **refuses** to add these to CLAUDE.md:

| Pattern | Detection | Action |
|---------|-----------|--------|
| Release notes | `^### v\d+\.\d+` or `Released \d{4}` | Block → redirect to VERSION-HISTORY.md |
| Diffstats | `Files Changed:.*+.*/-` | Block → delete |
| "What Shipped" | `What Shipped\|Merged PR` | Block → redirect |
| Completed features | `Status.*Complete\|Released ✅` | Block → redirect |
| Phase details | `^### Phase \d` | Block → redirect |

## --global Flag

When `--global` is passed, targets `~/.claude/CLAUDE.md` instead of the project-local file.

```python
import os
from pathlib import Path

if "--global" in args or "-g" in args:
    target_path = Path.home() / ".claude" / "CLAUDE.md"
else:
    target_path = Path.cwd() / "CLAUDE.md"
```

## Show Steps First Pattern

### Default Flow (no flags)

```
/craft:docs:claude-md:sync

Phase 1: Detect
  Project type: craft-plugin
  Version source: .claude-plugin/plugin.json

Phase 2: Update Metrics
  Version: v2.11.0 → v2.12.0 (changed)
  Commands: 104 (unchanged)
  Tests: 1111 (unchanged)

Phase 3: Audit
  ✅ Version now matches source
  ✅ Commands documented
  ✅ Links valid
  ⚠️ File is 280 lines (budget: 150)
  ⚠️ Contains release history (174 lines)
  ⚠️ 21 anti-patterns detected

2 warnings found. Run with --fix to auto-fix, or --optimize to enforce budget.
```

### With --fix flag

```
/craft:docs:claude-md:sync --fix

[Phase 1-2 same as above]

Phase 3: Audit
  ⚠️ Version mismatch (fixable)
  ⚠️ 2 stale command references (fixable)

Phase 4: Fix
  ✅ Updated version: v2.11.0 → v2.12.0
  ✅ Removed 2 stale command references

Applied 2 fixes. Run audit clean.
```

### With --optimize flag

```
/craft:docs:claude-md:sync --optimize

[Phase 1-2 same as above]

Phase 3: Audit
  ⚠️ File is 280 lines (budget: 150)

Phase 4: Optimize
  CLAUDE.md is 280 lines (budget: 150). Found cuts:

  ✂️ Release History (174 lines)
     → Move to docs/VERSION-HISTORY.md
     → Replace with: "-> Release history: [VERSION-HISTORY.md](...)"

  ✂️ Feature Matrix (40 lines)
     → Move to docs/VERSION-HISTORY.md
     → Replace with: "-> Feature status: [VERSION-HISTORY.md](...)"

  ✂️ Per-test breakdown (25 lines)
     → Collapse to summary (8 lines)

  Result: 280 → 138 lines (-142, -51%)

  Apply optimizations? [y/n]
```

### With --dry-run flag

```
/craft:docs:claude-md:sync --dry-run

Phase 1: Detect
  Project type: craft-plugin

Phase 2: Would update:
  Version: v2.11.0 → v2.12.0

Phase 3: Would report:
  2 warnings, 0 errors

(Dry run - no changes applied)
```

### With --section flag

```
/craft:docs:claude-md:sync --section status

Phase 1: Detect
  Project type: craft-plugin

Phase 2: Update Metrics (section: status)
  Version: v2.11.0 → v2.12.0 (changed)
  Documentation: 98% (unchanged)

(Skipped: commands, testing)
```

## Phased Output

The sync command always shows progress through each phase:

```
Phase 1: Detect ─────────────────────────
  Type: craft-plugin
  Source: .claude-plugin/plugin.json

Phase 2: Update Metrics ─────────────────
  [1/6] Version... v2.11.0 → v2.12.0 ✓
  [2/6] Commands... 104 (unchanged) ✓
  [3/6] Skills... 21 (unchanged) ✓
  [4/6] Agents... 8 (unchanged) ✓
  [5/6] Tests... 1111 (unchanged) ✓
  [6/6] Docs%... 98% (unchanged) ✓

Phase 3: Audit ──────────────────────────
  [✓] Version sync
  [✓] Command coverage
  [✓] Links valid
  [✓] Required sections
  [✓] Status alignment
  [⚠] Budget: 280/150 lines (OVER)
  [⚠] Anti-patterns: 21 detected

Summary: 1 metric updated, 0 errors, 2 warnings
```

## Execution

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.claude_md_sync import CLAUDEMDSync, sync_claude_md

# Determine target path
if "--global" in sys.argv or "-g" in sys.argv:
    target = Path.home() / ".claude" / "CLAUDE.md"
else:
    target = Path.cwd() / "CLAUDE.md"

if not target.exists():
    print("❌ CLAUDE.md not found. Use /craft:docs:claude-md:init to create.")
    sys.exit(1)

# Parse flags
fix = "--fix" in sys.argv
optimize = "--optimize" in sys.argv or "-o" in sys.argv
dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

# Determine section
section = "all"
if "--section" in sys.argv or "-s" in sys.argv:
    flag = "--section" if "--section" in sys.argv else "-s"
    idx = sys.argv.index(flag)
    if idx + 1 < len(sys.argv):
        section = sys.argv[idx + 1]

# Run sync
result, report = sync_claude_md(
    path=target,
    fix=fix,
    optimize=optimize,
    dry_run=dry_run,
    section=section,
)

print(report)

# If --optimize requested, invoke optimizer after sync
if optimize and not dry_run:
    from utils.claude_md_optimizer import CLAUDEMDOptimizer
    optimizer = CLAUDEMDOptimizer(target)
    opt_result = optimizer.optimize(dry_run=dry_run)
    print(optimizer.generate_report(opt_result))

sys.exit(0 if not result.has_errors else 1)
```

## Budget Enforcement

When CLAUDE.md exceeds the 150-line budget, sync reports it as a warning:

```
⚠️ CLAUDE.md is 280 lines (budget: 150)
   Run with --optimize to enforce budget
   Or edit manually: /craft:docs:claude-md:edit
```

The budget is resolved from:

1. `.claude-plugin/plugin.json` → `claude_md_budget`
2. `package.json` → `claude_md_budget`
3. Default: 150 lines

## Section-Specific Updates

```bash
# Update only version/status
/craft:docs:claude-md:sync --section status

# Update only commands
/craft:docs:claude-md:sync --section commands

# Update only testing
/craft:docs:claude-md:sync --section testing
```

## Pointer Architecture

When `--optimize` moves content, it uses pointer lines:

```markdown
-> Release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
-> Architecture: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
-> Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
-> Command reference: [COMMANDS.md](docs/COMMANDS.md)
```

Claude Code naturally follows markdown links when users ask about those topics.

## Integration

### Pre-Commit Workflow

```bash
# Before committing
/craft:docs:claude-md:sync
# Shows any drift

# If issues found
/craft:docs:claude-md:sync --fix
# Auto-fixes what it can

# If over budget
/craft:docs:claude-md:sync --optimize
# Moves bloat to detail files
```

### With /craft:check

The check command calls sync internally as part of its validation pipeline.

## Error Handling

### CLAUDE.md Not Found

```
❌ CLAUDE.md not found.
Use /craft:docs:claude-md:init to create one.
```

### Project Type Unknown

```
⚠️ Could not detect project type.
Sync will check basic structure only (version, links, sections).
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:init` | Create new CLAUDE.md from lean template |
| `/craft:docs:claude-md:edit` | Interactive editing with iA Writer |

## Migration Note

This command replaces three old commands:

- `/craft:docs:claude-md:update` → `/craft:docs:claude-md:sync`
- `/craft:docs:claude-md:audit` → `/craft:docs:claude-md:sync` (audit runs automatically)
- `/craft:docs:claude-md:fix` → `/craft:docs:claude-md:sync --fix`

Old commands still work as deprecation aliases but will be removed in v2.13.0.
