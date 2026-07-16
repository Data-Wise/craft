---
name: guard-audit
description: This skill should be used when the user asks to "audit guard", "guard friction", "tune guard", "guard false positives", "fix guard blocking", or mentions branch guard configuration issues. Analyzes branch-guard.sh rules; proposes JSON branch-policy config changes for policy-level false positives, and flags detection-logic bugs (which the flat config schema cannot fix) as needing a code PR instead.
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
│ Config:    .claude/branch-guard.json (found/not found — flat  │
│            branch→level map, e.g. {"main":"block-all"})       │
│ Branches:  main (block-all), dev (smart), feature/* (none)    │
│                                                               │
│ Protection Rules Found:                                       │
│   1. [HIGH] Destructive git commands (reset --hard, clean -f) │
│   2. [HIGH] Force push to protected branches                  │
│   3. [MEDIUM] New code files via Write or shell redirection   │
│   4. [MEDIUM] Guard-bypass marker creation                    │
│   ... (N total rules)                                         │
└───────────────────────────────────────────────────────────────┘
```

### Step 1b: Matcher-Overlap Check

Check `~/.claude/settings.json` for duplicate PreToolUse matcher strings:

```bash
jq -r '.hooks.PreToolUse[]?.matcher // empty' ~/.claude/settings.json | sort | uniq -d
```

If any duplicates appear, flag them — a guard registered twice fires twice for that tool, causing double prompts.

**Progress indicator**: `[1b/5] Matcher-overlap .......... DONE (N duplicates found)`

### Step 1c: Duplicated Rule Coverage + Guard State

**Rule coverage check**: Scan both `scripts/branch-guard.sh` and `scripts/no-switch-guard.sh` for patterns that handle the same git operations. Common overlap site: `git restore` / `git checkout -- <file>` (data-loss detection).

```bash
# Check if both guards handle restore
grep -n 'restore\|checkout.*--' scripts/branch-guard.sh
grep -n 'restore\|checkout.*--' scripts/no-switch-guard.sh
```

Flag any operation handled by BOTH guards (double prompts; ownership should be assigned to one).

**Guard state**: Surface disabled or muted guards so audit context includes current guard state:

```bash
jq -r '.guards | to_entries[] | "\(.key): enabled=\(.value.enabled // true), muted_until=\(.value.muted_until // "null")"' \
  ~/.claude/guards.json 2>/dev/null || echo "(guards.json not found — guards at default state)"
```

**Progress indicator**: `[1c/5] Rule-coverage + state ...... DONE (N overlaps, M muted)`

### Step 2: Friction Analysis

For each rule, identify scenarios where it produces false positives:

| Rule | Intended Block | False Positive Scenario |
|------|---------------|------------------------|
| Force push detection | Force push to main/dev | Rebased feature branch push (already excluded — verify the branch was matched correctly) |
| New code files on dev (shell redirection) | `echo`/`cat`/`tee`/`cp`/`touch` writing code to dev | A `>` character, or the keyword `cp`, `tee`, or `touch` followed by a space, appearing INSIDE a single- or double-quoted argument (an awk/grep/sed program, a search pattern) — text, not real shell syntax |
| New code files on dev (path scoping) | Writes landing inside the repo tree | A target outside `PROJECT_ROOT` entirely (`/tmp/...`, `$HOME/...`) — poses no risk to this repo's branch |
| File extension detection | Source code files | Generated/template files with a non-code extension already in `NONCODE_EXTENSIONS` |

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

**First, classify each false positive by what can actually fix it** — this determines whether
Step 5 applies at all:

| Class | What it looks like | Fixable via config? |
|---|---|---|
| **Branch policy** | The wrong protection *level* for a branch (e.g. a research repo's `draft` branch needs `smart` but has none) | **Yes** — Step 5's flat schema |
| **Detection logic** | The guard misparses a *specific command* regardless of branch — e.g. a `>` inside a quoted `awk`/`grep` program read as a redirect, or an out-of-repo target (`/tmp/...`) flagged as an in-repo write | **No** — this is a bug in `scripts/branch-guard.sh` itself; only a code fix (PR) resolves it |

Output a friction report with specific recommendations:

```text
┌───────────────────────────────────────────────────────────────┐
│ GUARD FRICTION REPORT                                         │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ Rules Analyzed: N                                             │
│ False Positives Found: M (X branch-policy, Y detection-logic) │
│                                                               │
│ Recommendation 1 [branch-policy]: Protect the 'draft' branch  │
│   Issue: research-repo integration branch has no protection   │
│   Config change: {"draft": "smart"}                            │
│                                                               │
│ Recommendation 2 [detection-logic — NOT config-fixable]:      │
│   Issue: `awk 'NR>=203'` flagged as a redirect — the `>` is   │
│          inside a single-quoted awk program, not shell syntax │
│   Fix: requires editing scripts/branch-guard.sh's Pattern 1   │
│        detection to strip quoted spans before scanning (see   │
│        the 2026-07-16 quoted-span-stripping fix for the       │
│        precedent — same class, PR against the script)         │
│   Config change: none exists — the flat schema (Step 5) has   │
│        no such knob                                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 5: Apply (with user confirmation)

**The real config schema is a flat branch-name → protection-level map — nothing else.**
`scripts/branch-guard.sh` reads it with a single lookup, `_json_get ".\"${BRANCH}\""` — there is
no nested `"branches"` object, no `allowed_extensions`, `pr_body_scan`, or `force_push_allow` key.
Those do not exist in the script; proposing them would produce a config file the guard silently
ignores.

Valid protection-level values (from the script's own comment): `"block-all"`, `"smart"`,
`"block-new-code"` (alias for `smart`), `"confirm"` (alias for `smart`), or `""` (no protection).
A branch not listed in the config gets no protection — **a custom config is explicit and
authoritative**; it does not merge with auto-detection.

```json
{
  "main": "block-all",
  "dev": "smart",
  "draft": "smart"
}
```

Only propose **branch-policy** changes this way (see Step 4's classification). Ask the user to
confirm before writing to `.claude/branch-guard.json`.

**IMPORTANT:** Never modify `scripts/branch-guard.sh`. If the false positive is a
detection-logic bug (not fixable via this flat schema), say so plainly and recommend a code fix
as its own PR — do not fabricate a config key to paper over it.

## Output Format

Use craft box-drawing format throughout. Each step shows progress:

```text
[1/5]  Discovery ................. DONE (N rules found)
[1b/5] Matcher-overlap ........... DONE (0 duplicates)
[1c/5] Rule-coverage + state ..... DONE (0 overlaps, 0 muted)
[2/5]  Friction analysis ......... DONE (M false positives)
[3/5]  Test harness .............. DONE (P/Q tests passed)
[4/5]  Report .................... SHOWN
[5/5]  Apply ..................... WAITING (user confirmation)
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
- [`skills/dev/git/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md) — unprotect, protect, and guard management (ask naturally; folded from `/craft:git:unprotect`/`protect`/`guard`, 2026-07 v4 consolidation)
- `docs/guide/guard-suite.md` — Guard suite concepts and usage guide
