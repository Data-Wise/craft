---
name: check:guard-consistency
description: Validate guard suite consistency — no duplicate PreToolUse matchers, no duplicated rule coverage between branch-guard and no-switch-guard
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# Guard Consistency Validation

Validate that the craft guard suite is internally consistent: no duplicate PreToolUse matcher registrations and no duplicated rule coverage between guards.

## Checks

| Check | What it verifies |
|-------|-----------------|
| **A: Duplicate registration** | No (matcher, hook-command) pair appears more than once in `~/.claude/settings.json` — two distinct guards sharing the `Bash` matcher is the intended install, not a duplicate |
| **B: Duplicated rule coverage** | `branch-guard.sh` and `no-switch-guard.sh` do not both handle the same git operations |
| **Guard state** | Surface any disabled or muted guards for situational awareness |

## Implementation

```bash
#!/bin/bash
set -uo pipefail

HOOKS_DIR="$HOME/.claude/hooks"
CHECK_A="SKIP"
CHECK_B="SKIP"

# Auto-detect: skip gracefully if guards not installed
if [[ ! -f "$HOOKS_DIR/branch-guard.sh" ]]; then
  echo "⏭️  SKIP: branch-guard.sh not found in ~/.claude/hooks/ — guard suite not installed"
  exit 0
fi

echo "🔍 Checking guard suite consistency..."
echo ""

# ── Check A: Duplicate PreToolUse matchers in settings.json ─────────────────

SETTINGS="$HOME/.claude/settings.json"
if [[ ! -f "$SETTINGS" ]]; then
  echo "⚠️  WARN: settings.json not found — skipping matcher check"
  CHECK_A="SKIP"
else
  # Duplicate = the SAME hook command registered under the SAME matcher twice.
  # Two DIFFERENT guards sharing the Bash matcher (branch-guard + no-switch-guard)
  # is the intended install, NOT a duplicate — so key on (matcher, command) pairs.
  PAIRS=$(jq -r '.hooks.PreToolUse[]? | .matcher as $m | (.hooks[]?.command // empty) | "\($m)\t\(.)"' "$SETTINGS" 2>/dev/null)
  DUPES=$(echo "$PAIRS" | sort | uniq -d | sed 's/\t/ → /')
  if [[ -n "$DUPES" ]]; then
    echo "❌ FAIL: Same hook registered more than once (matcher → command):"
    echo "$DUPES" | while read -r m; do echo "  - $m"; done
    CHECK_A="FAIL"
  else
    echo "✅ PASS: No duplicate PreToolUse matchers"
    CHECK_A="PASS"
  fi
fi

echo ""

# ── Check B: Duplicated rule coverage between guards ─────────────────────────

BG="scripts/branch-guard.sh"
NSG="scripts/no-switch-guard.sh"

if [[ ! -f "$BG" ]]; then
  echo "⚠️  WARN: scripts/branch-guard.sh not in repo — skipping rule-coverage check"
  CHECK_B="SKIP"
elif [[ ! -f "$NSG" ]]; then
  echo "⚠️  WARN: scripts/no-switch-guard.sh not in repo — skipping rule-coverage check"
  CHECK_B="SKIP"
else
  OVERLAPS=()

  # Check for restore rule in both guards
  if grep -qE '_confirm.*restore|_confirm.*checkout_discard' "$BG" 2>/dev/null && \
     grep -qE 'ask.*restore|restore.*ask' "$NSG" 2>/dev/null; then
    OVERLAPS+=("git restore (discard changes)")
  fi

  # Check for checkout -- (file-restore) in both guards
  if grep -qE '_confirm.*checkout_discard|checkout_discard' "$BG" 2>/dev/null && \
     grep -qE 'checkout[[:space:]]+--' "$NSG" 2>/dev/null; then
    OVERLAPS+=("git checkout -- (file restore)")
  fi

  if [[ ${#OVERLAPS[@]} -gt 0 ]]; then
    echo "❌ FAIL: Duplicated rule coverage found:"
    for overlap in "${OVERLAPS[@]}"; do
      echo "  - '$overlap' handled by BOTH branch-guard and no-switch-guard"
    done
    echo "  → Run Step A2 reconciliation or check scripts manually"
    CHECK_B="FAIL"
  else
    echo "✅ PASS: No duplicated rule coverage"
    CHECK_B="PASS"
  fi
fi

# ── Surface disabled/muted guards ────────────────────────────────────────────

GUARDS_JSON="$HOME/.claude/guards.json"
if [[ -f "$GUARDS_JSON" ]] && command -v jq &>/dev/null; then
  echo ""
  echo "Guard Registry State:"
  jq -r '.guards | to_entries[] |
    if .value.enabled == false then "  ⛔ \(.key): DISABLED (permanent)"
    elif (.value.muted_until != null and .value.muted_until != "") then "  ⚠️  \(.key): MUTED until \(.value.muted_until)"
    else "  🛡️  \(.key): enabled"
    end' "$GUARDS_JSON" 2>/dev/null || echo "  (could not parse guards.json)"
fi

# ── Final result ──────────────────────────────────────────────────────────────

echo ""
if [[ "${CHECK_A:-SKIP}" == "FAIL" || "${CHECK_B:-SKIP}" == "FAIL" ]]; then
  echo "❌ RESULT: FAIL — guard consistency issues found"
  exit 1
else
  echo "✅ RESULT: PASS — guard suite is consistent"
  exit 0
fi
```

## Example Output

### Success

```
🔍 Checking guard suite consistency...

✅ PASS: No duplicate PreToolUse matchers

✅ PASS: No duplicated rule coverage

Guard Registry State:
  🛡️  branch-guard: enabled
  🛡️  no-switch-guard: enabled

✅ RESULT: PASS — guard suite is consistent
```

### Failure (duplicate matcher)

```
🔍 Checking guard suite consistency...

❌ FAIL: Duplicate PreToolUse matchers found:
  - 'Bash' registered more than once

✅ PASS: No duplicated rule coverage

✅ RESULT: FAIL — guard consistency issues found
```

### Failure (duplicated rule coverage)

```
🔍 Checking guard suite consistency...

✅ PASS: No duplicate PreToolUse matchers

❌ FAIL: Duplicated rule coverage found:
  - 'git restore (discard changes)' handled by BOTH branch-guard and no-switch-guard
  → Run Step A2 reconciliation or check scripts manually

❌ RESULT: FAIL — guard consistency issues found
```

### Guards not installed (skip gracefully)

```
⏭️  SKIP: branch-guard.sh not found in ~/.claude/hooks/ — guard suite not installed
```

### With muted guard

```
Guard Registry State:
  🛡️  branch-guard: enabled
  ⚠️  no-switch-guard: MUTED until 2026-06-19T15:30:00Z
```

## Integration with /craft:check

This validator runs automatically when the guard suite is installed:

```bash
/craft:check              # Includes guard-consistency if guards present
/craft:check debug        # Verbose output (non-blocking)
/craft:check release      # Strict mode (exit on any error)
```

The validator silently skips (`exit 0`) when `~/.claude/hooks/branch-guard.sh` is absent, so it is safe on any machine regardless of whether guards are installed.

## See Also

- `/craft:git:guard` — List, enable, or disable individual guards
- `scripts/branch-guard.sh` — Branch protection guard (repo source)
- `scripts/no-switch-guard.sh` — Switch/restore guard (repo source)
- `docs/guide/guard-suite.md` — Guard suite concepts and ownership seam
- `/craft:check` — Run all validators
