---
name: guard-audit
description: This skill should be used when the user asks to "audit guard", "guard friction", "tune guard", "guard false positives", "fix guard blocking", or mentions branch guard configuration issues. Analyzes branch-guard.sh rules and proposes JSON config changes to reduce false positives.
---

# Guard Audit

Analyze branch guard configuration to find false positives and reduce friction. Proposes changes to `.claude/branch-guard.json` — never modifies the guard script itself.

## When to Use

- User reports branch guard blocking legitimate operations
- User says "audit guard", "tune guard", "guard friction"
- After multiple guard false positives in a session
- User wants to understand guard behavior

## Prerequisites

- `scripts/branch-guard.sh` must exist (the guard script)
- Git repository with branch protection enabled

## Guard Audit Pipeline

Execute these steps in order.

### Step 1: Discovery

Read the branch guard script and extract all protection rules:

```bash
# Extract protection patterns from branch-guard.sh
grep -n "BLOCKED\|blocked\|exit 2\|protection" scripts/branch-guard.sh

# Extract regex patterns used for detection
grep -n "grep.*-E\|=~\|pattern\|regex" scripts/branch-guard.sh

# Read existing config (if any)
cat .claude/branch-guard.json 2>/dev/null || echo "No config file found"
```

Present a summary:

```text
┌───────────────────────────────────────────────────────────────┐
│ GUARD DISCOVERY                                               │
├───────────────────────────────────────────────────────────────┤
│ Script:    scripts/branch-guard.sh (N lines)                  │
│ Config:    .claude/branch-guard.json (found/not found)        │
│ Branches:  main (block-all), dev (smart), feature/* (none)    │
│                                                               │
│ Protection Rules Found:                                       │
│   1. [HIGH] Destructive git commands in PR body               │
│   2. [HIGH] Force push to protected branches                  │
│   3. [MEDIUM] New code files on dev                           │
│   4. [LOW] Config file modifications on dev                   │
│   ... (N total rules)                                         │
└───────────────────────────────────────────────────────────────┘
```

### Step 2: Friction Analysis

For each rule, identify scenarios where it produces false positives:

| Rule | Intended Block | False Positive Scenario |
|------|---------------|------------------------|
| Destructive git in PR body | Actual destructive commands | Documentation mentioning commands |
| Force push detection | Force push to main/dev | Rebased feature branch push |
| New code files on dev | Feature code on dev | Config/build files |
| File extension detection | Source code files | Generated/template files |

### Step 3: Test Harness

Generate test scenarios and report which ones trigger incorrectly:

```bash
# Test 1: PR body with documentation about git commands
# Should NOT trigger — it's documentation, not actual commands
echo "Testing: PR body with 'git reset' in docs context..."

# Test 2: Force push on feature branch
# Should NOT trigger — feature branches allow force push
echo "Testing: Force push on feature/my-feature..."

# Test 3: Config file write on dev
# Should allow — .json/.yaml are config, not code
echo "Testing: Write .claude/branch-guard.json on dev..."

# Test 4: Markdown file on dev
# Should allow — .md files are documentation
echo "Testing: Write docs/guide.md on dev..."
```

### Step 4: Report

Output a friction report with specific recommendations:

```text
┌───────────────────────────────────────────────────────────────┐
│ GUARD FRICTION REPORT                                         │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Rules Analyzed: N                                             │
│ False Positives Found: M                                      │
│                                                               │
│ Recommendation 1: Relax PR body scanning                      │
│   Issue: Guard flags PR bodies containing destructive         │
│          command strings even when used as documentation       │
│   Fix: Add context awareness — only flag if command is in     │
│        a bash/shell code block, not prose                     │
│   Config change:                                              │
│     "pr_body_scan": "code_blocks_only"                        │
│                                                               │
│ Recommendation 2: Allow force-push on feature/*               │
│   Issue: Guard blocks force-push after rebase on feature      │
│          branches                                             │
│   Fix: Only block force-push on main and dev                  │
│   Config change:                                              │
│     "force_push_allow": ["feature/*", "fix/*"]                │
│                                                               │
│ Recommendation 3: Expand allowed file types on dev            │
│   Issue: Guard blocks config files (.json, .yaml) on dev      │
│   Fix: Add config extensions to allowed list                  │
│   Config change:                                              │
│     "dev_allowed_extensions": [".md", ".json", ".yaml",       │
│       ".yml", ".toml", ".txt"]                                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 5: Apply (with user confirmation)

Present proposed JSON config changes:

```json
{
  "version": 2,
  "branches": {
    "main": { "protection": "block-all" },
    "dev": {
      "protection": "smart",
      "allowed_extensions": [".md", ".json", ".yaml", ".yml", ".toml", ".txt"],
      "pr_body_scan": "code_blocks_only"
    },
    "feature/*": {
      "protection": "none",
      "allow_force_push": true
    }
  }
}
```

Ask user to confirm before writing to `.claude/branch-guard.json`.

**IMPORTANT:** Never modify `scripts/branch-guard.sh`. Only propose changes to the JSON config file.

## Output Format

Use craft box-drawing format throughout. Each step shows progress:

```text
[1/5] Discovery ................ DONE (N rules found)
[2/5] Friction analysis ........ DONE (M false positives)
[3/5] Test harness ............. DONE (P/Q tests passed)
[4/5] Report ................... SHOWN
[5/5] Apply .................... WAITING (user confirmation)
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| No guard script found | Report error, suggest installing guard |
| No false positives found | Report clean audit, no changes needed |
| Config write fails | Show JSON for manual copy |
| Tests inconclusive | Show raw test output for review |

## See Also

- `scripts/branch-guard.sh` — The guard script (read-only for this skill)
- `.claude/branch-guard.json` — Per-project config (this skill's output)
- `/craft:git:unprotect` — Session-scoped bypass (temporary)
- `/craft:git:protect` — Re-enable protection
