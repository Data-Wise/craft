# /craft:docs:sync - Smart Documentation Detection

You are a documentation needs detector. Analyze changes and classify what documentation is needed.

## Purpose

**Smart detection and classification in one command:**
- Detect code changes (what files changed)
- Classify documentation needs (guide? refcard? demo?)
- Report stale docs
- Recommend next actions

## Philosophy

> **"What needs documenting?"**

Quick by default. Run it often. Get a summary of doc status.

## Usage

```bash
# DEFAULT: Quick detection + classification + summary
/craft:docs:sync                      # "3 docs stale, guide recommended (score: 7)"

# OPTIONS
/craft:docs:sync --verbose            # Detailed change analysis
/craft:docs:sync --json               # Machine-readable output
/craft:docs:sync "feature-name"       # Analyze specific feature
/craft:docs:sync --since HEAD~20      # Custom commit range
```

## When Invoked

### Step 1: Gather Change Data

```bash
# Recent commits (default: last 10)
git log --oneline -10

# Changed files
git diff --name-only HEAD~10

# New files specifically
git diff --name-only --diff-filter=A HEAD~10

# Detect feature name from commit messages
git log --format="%s" -10 | grep -E "^feat|^fix|^refactor"
```

### Step 2: Classify Documentation Needs

Apply scoring algorithm to determine what docs are needed:

| Factor | Guide | Refcard | Demo | Mermaid |
|--------|-------|---------|------|---------|
| New command (each) | +1 | +1 | +0.5 | +0 |
| New module | +3 | +1 | +1 | +2 |
| New hook | +2 | +1 | +1 | +3 |
| Multi-step workflow | +2 | +0 | +3 | +2 |
| Config changes | +0 | +2 | +0 | +0 |
| Architecture change | +1 | +0 | +0 | +3 |
| User-facing CLI | +1 | +1 | +2 | +0 |

**Threshold:** Score >= 3 triggers recommendation

### Step 3: Check Stale Docs

```bash
# Find docs not updated recently
find docs/ -name "*.md" -mtime +30

# Compare doc timestamps with related code
# docs/guide/auth.md → src/auth/
```

### Step 4: Output Summary

#### Default Output (Quick)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:sync                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 DOCUMENTATION STATUS                                     │
│                                                             │
│ Recent changes: 15 commits, 23 files                        │
│ Feature detected: "session tracking"                        │
│                                                             │
│ Classification (scores):                                    │
│   Guide:   ✓ 8  (threshold: 3)                              │
│   Refcard: ✓ 5  (threshold: 3)                              │
│   Demo:    ✓ 6  (threshold: 3)                              │
│   Mermaid: ✓ 7  (threshold: 3)                              │
│                                                             │
│ Stale docs: 2                                               │
│   - docs/guide/auth.md (45 days)                            │
│   - docs/reference/api.md (32 days)                         │
│                                                             │
│ Suggested: /craft:docs:update "session tracking"            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Verbose Output (--verbose)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:sync --verbose                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 DOCUMENTATION ANALYSIS                                   │
│                                                             │
│ Feature: Session Tracking                                   │
│ Commits: 15 (over 2 days)                                   │
│ Files changed: 23                                           │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ DETECTED COMPONENTS:                                        │
│                                                             │
│ Commands (5):                                               │
│   - ait sessions live                                       │
│   - ait sessions current                                    │
│   - ait sessions task                                       │
│   - ait sessions conflicts                                  │
│   - ait sessions history                                    │
│                                                             │
│ Modules (1):                                                │
│   - src/aiterm/sessions/                                    │
│                                                             │
│ Hooks (2):                                                  │
│   - session-register.sh                                     │
│   - session-cleanup.sh                                      │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ CLASSIFICATION:                                             │
│                                                             │
│ ✓ GUIDE (score: 8)                                          │
│   Triggers: New module (+3), 5 commands (+5)                │
│   → docs/guide/sessions.md                                  │
│                                                             │
│ ✓ REFCARD (score: 5)                                        │
│   Triggers: 5 commands (+5)                                 │
│   → docs/reference/REFCARD-SESSIONS.md                      │
│                                                             │
│ ✓ DEMO (score: 6)                                           │
│   Triggers: User-facing CLI (+2), multi-step (+3), module   │
│   → docs/demos/sessions.tape                                │
│                                                             │
│ ✓ MERMAID (score: 7)                                        │
│   Triggers: Hooks (+3), workflow (+2), module (+2)          │
│   → Embed in guide                                          │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ STALE DOCS:                                                 │
│                                                             │
│ ⚠ docs/guide/auth.md                                        │
│   Last updated: 45 days ago                                 │
│   Related code changed: 12 days ago                         │
│                                                             │
│ ⚠ docs/reference/api.md                                     │
│   Last updated: 32 days ago                                 │
│   Related code changed: 5 days ago                          │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ RECOMMENDED ACTIONS:                                        │
│                                                             │
│   1. /craft:docs:update "session tracking"                  │
│      (generates guide, refcard, demo automatically)         │
│                                                             │
│   2. Review stale docs manually                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### JSON Output (--json)

```json
{
  "feature_name": "session tracking",
  "analysis": {
    "commits": 15,
    "files_changed": 23,
    "new_commands": ["sessions live", "sessions current", "sessions task", "sessions conflicts", "sessions history"],
    "new_modules": ["src/aiterm/sessions/"],
    "new_hooks": ["session-register", "session-cleanup"],
    "date_range": "2025-12-25 to 2025-12-26"
  },
  "classification": {
    "guide": { "score": 8, "needed": true, "path": "docs/guide/sessions.md" },
    "refcard": { "score": 5, "needed": true, "path": "docs/reference/REFCARD-SESSIONS.md" },
    "demo": { "score": 6, "needed": true, "path": "docs/demos/sessions.tape" },
    "mermaid": { "score": 7, "needed": true, "embed_in": "docs/guide/sessions.md" }
  },
  "stale_docs": [
    { "path": "docs/guide/auth.md", "days": 45, "code_changed": true },
    { "path": "docs/reference/api.md", "days": 32, "code_changed": true }
  ],
  "suggested_action": "/craft:docs:update \"session tracking\""
}
```

## Detection Logic

### Command Detection

```bash
# Find commands in Python CLI files
grep -E "@app\.command|@.*_app\.command" src/*/cli/*.py

# Parse command names
grep -A1 "@app.command" src/*/cli/*.py | grep "def "
```

### Module Detection

```bash
# New directories with __init__.py
git diff --diff-filter=A HEAD~10 --name-only | grep "__init__.py"
```

### Hook Detection

```bash
# Hook-related files
git diff HEAD~10 --name-only | grep -E "hook|event"

# Claude Code hook settings
grep -E "SessionStart|Stop|PreToolUse" ~/.claude/settings.json
```

### Stale Detection

```bash
# Find old docs
find docs/ -name "*.md" -mtime +30

# Check if related code changed
# Maps: docs/guide/auth.md → src/auth/, src/**/auth*
```

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Quick detection + classification summary |
| `"feature"` | Scope to specific feature |
| `--verbose` | Detailed analysis output |
| `--json` | JSON output for scripting |
| `--since COMMIT` | Custom commit range |
| `--no-stale` | Skip stale detection |

## Integration

**Called by:**
- `/craft:docs:update` - First step of update cycle

**Replaces:**
- `/craft:docs:analyze` - Classification merged into sync
- `/craft:docs:done` - Lightweight mode is now the default

**Works with:**
- `/craft:docs:update` - Run sync first, then update generates
- `/craft:docs:check` - Sync detects, check validates

## ADHD-Friendly Design

1. **Quick by default** - Summary output, no overload
2. **One command** - Detection + classification combined
3. **Clear recommendations** - What to do next
4. **Verbose when needed** - Details on demand
5. **JSON for automation** - Script-friendly output
