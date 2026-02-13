# BRAINSTORM: Smart Branch Guard with Teaching Suggestions

**Generated:** 2026-02-13
**Mode:** feature | **Depth:** deep (8 questions)
**Context:** Craft Plugin v2.16.0, branch-guard.sh, builds on SPEC-branch-guard-v2

## Overview

Transform the branch guard from a binary block/allow system into a **teaching-first protection system** that explains risks, suggests safe alternatives, and fades to brief reminders as the user learns the patterns. The guard becomes a coach, not a wall.

---

## Core Design: 3-Tier Risk Classification

### Tier 1: LOW Risk — Silent Allow + Brief Note

Actions that are safe but worth noting. The guard allows them and prints a one-line note on first encounter.

| Action | Note Shown | When |
|--------|-----------|------|
| Edit existing file on dev | `[guard] Editing existing file on dev (allowed)` | First time per session |
| Write new .md on dev | `[guard] New markdown on dev (always allowed)` | First time per session |
| Write to tests/ on dev | `[guard] Test files on dev (always allowed)` | First time per session |
| Write extension-less file | `[guard] Extension-less file (allowed): .STATUS` | First time per session |
| `git commit` on dev | `[guard] Commit on dev (allowed)` | First time per session |
| `git push` (normal) on dev | `[guard] Push to dev (allowed)` | First time per session |
| `git reset --soft` | `[guard] Soft reset (safe — keeps changes staged)` | First time per session |

**Note format:** Single line, no box, `[guard]` prefix, grey/dim color.

**Fade behavior:** Shows note on first encounter per action type per session. Silent on subsequent calls.

---

### Tier 2: MEDIUM Risk — Box Warning + AskUserQuestion

Actions that could cause problems but are sometimes intentional. The guard blocks, shows a teaching box, and asks for explicit approval.

| Action | Risk Category | Teaching Message |
|--------|--------------|-----------------|
| Write new .py/.sh/.js on dev | Unplanned code | "New code files on dev should go in a feature branch" |
| `git push --force` on dev | History rewrite | "Force push overwrites remote history for all collaborators" |
| `git reset --hard` on dev | Work loss | "Hard reset discards ALL uncommitted changes — no undo" |
| `git checkout -- .` on dev | Work loss | "Restores all files to last commit — discards all edits" |
| `git restore .` on dev | Work loss | "Same as checkout -- . — discards uncommitted changes" |
| `git clean -f` on dev | File loss | "Removes ALL untracked files permanently — no recovery" |
| `git branch -D` anywhere | Branch loss | "Force-deletes branch even if not merged — commits may be lost" |
| Overwrite .env / secrets | Security | "Overwriting environment file — contains sensitive credentials" |
| Delete config files | Configuration | "Removing config file may break project setup" |

**Box format (full teaching — first encounter):**

```
╔═══════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — Medium Risk                                    ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Action:  git push --force origin dev                          ║
║                                                               ║
║ Why risky:                                                    ║
║   Force push overwrites remote history. If others have        ║
║   pulled from dev, their local copies will diverge.           ║
║                                                               ║
║ Safe alternatives:                                            ║
║   → git push origin dev          (regular push)               ║
║   → git push --force-with-lease  (safer — checks remote)     ║
║   → Create PR instead of pushing directly                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**AskUserQuestion (follows box):**

```json
{
  "questions": [{
    "question": "Force push on dev — overwrites remote history. Allow?",
    "header": "Guard",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes, allow this once",
        "description": "One-shot approval. Guard re-engages on next risky action."
      },
      {
        "label": "Use safe alternative",
        "description": "Regular push (git push origin dev) — no history overwrite."
      },
      {
        "label": "Cancel",
        "description": "Don't execute. I'll rethink the approach."
      },
      {
        "label": "Bypass all (/craft:git:unprotect)",
        "description": "Disable guard for this session. For heavy maintenance work."
      }
    ]
  }]
}
```

**Fade behavior (medium risk):**

| Encounter | Behavior |
|-----------|----------|
| 1st time | Full teaching box + all 4 suggestion types + AskUserQuestion |
| 2nd-3rd time | Brief box (action + risk only, no alternatives) + AskUserQuestion |
| 4th+ time | One-line: `[guard] Force push on dev. Allow? [Yes/No]` + AskUserQuestion |

---

### Tier 3: HIGH Risk — Hard Block (Main Only)

Actions that are never allowed without going through proper workflow. No confirmation path — must use `/craft:git:unprotect` or switch branches.

| Action | Branch | Why Hard Block |
|--------|--------|----------------|
| Any Edit on main | main | All changes via PR |
| Any Write on main | main | All changes via PR |
| `git commit` on main | main | All changes via PR |
| `git push` on main | main | All changes via PR |
| `rm -rf .git` anywhere | all | Catastrophic — destroys entire repo history |
| Delete `.claude/` directory | all | Destroys guard config and bypass state |

**Box format (hard block):**

```
╔═══════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — Hard Block                                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Cannot edit files on main.                                    ║
║                                                               ║
║ This branch is production-protected. All changes must         ║
║ go through the PR workflow:                                   ║
║                                                               ║
║   1. git checkout dev                                         ║
║   2. /craft:git:worktree feature/<name>                       ║
║   3. Make changes in worktree                                 ║
║   4. gh pr create --base dev                                  ║
║   5. gh pr create --base main --head dev                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**No AskUserQuestion for high risk.** The block message teaches the workflow. User must switch branches.

---

## User Stories

### Primary: Developer on Dev Branch

> As a developer working on the dev branch, I want the branch guard to **explain why** a command is risky and **suggest safe alternatives**, so that I learn the proper workflow instead of just hitting a wall.

**Acceptance criteria:**

1. Medium-risk actions show a teaching box with risk explanation
2. At least one safe alternative is suggested for every blocked action
3. I can approve the action with one click (AskUserQuestion)
4. Teaching messages get briefer after I've seen them 3+ times
5. `/craft:git:unprotect` still works as blanket bypass for heavy tasks

### Secondary: New Team Member

> As a new team member unfamiliar with the branch workflow, I want the guard to teach me the `main → dev → feature` pattern through its suggestions, so I learn without reading documentation.

**Acceptance criteria:**

1. Hard blocks on main include the full workflow steps (1-5)
2. Medium-risk blocks mention worktrees and PRs as alternatives
3. Low-risk notes explain WHY certain actions are safe on dev

### Secondary: Experienced Developer in Maintenance Mode

> As an experienced developer doing maintenance (merge conflicts, CI fixes), I want the guard to be less verbose and let me approve actions quickly, so I'm not slowed down by explanations I already understand.

**Acceptance criteria:**

1. After 3+ encounters, messages fade to brief format
2. After 10+ encounters, messages are one-line
3. `/craft:git:unprotect maintenance` still bypasses everything

---

## 4 Suggestion Types — Templates

### Type 1: Worktree Redirect

**When:** New code file on dev

```
Safe alternative:
  → Create worktree: /craft:git:worktree feature/<name>
    Then write your code in the isolated feature branch.
```

### Type 2: Command Rewrite

**When:** Risky git command has a safer version

```
Safe alternative:
  → git push origin dev              (instead of --force)
  → git push --force-with-lease      (checks remote first)
  → git reset --soft HEAD~1          (instead of --hard)
  → git stash                        (instead of checkout --)
```

### Type 3: Workflow Guidance

**When:** Action suggests the user is in the wrong workflow

```
Workflow suggestion:
  → Run /craft:git:unprotect for bulk maintenance
  → Create a PR: gh pr create --base dev
  → Use /craft:git:worktree to isolate changes
```

### Type 4: Risk Explanation

**When:** Always included for medium risk (first 3 encounters)

```
Why risky:
  Force push overwrites remote history. If others have
  pulled from dev, their local copies will diverge and
  require manual intervention to reconcile.
```

---

## Critical File Protection (Non-Git Scope)

### Protected Files

| Pattern | Risk Level | Why Protected |
|---------|-----------|---------------|
| `.env*` | Medium | Contains credentials, API keys |
| `*.secret*` | Medium | Secrets files |
| `credentials.*` | Medium | Auth credentials |
| `.claude/branch-guard.json` | Medium | Guard config |
| `.claude/settings.json` | Medium | Claude settings |
| `*.pem`, `*.key` | Medium | SSL/SSH keys |
| `.git/` (any operation) | High | Repository internals |

### Detection

```bash
# In Bash handler, check for critical file operations
CRITICAL_PATTERNS="\.env|\.secret|credentials\.|\.pem$|\.key$"

if echo "$COMMAND" | grep -qE "(rm|mv|>)\s.*($CRITICAL_PATTERNS)"; then
  # Trigger medium-risk confirm flow
fi
```

### Suggestion Template for Critical Files

```
╔═══════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — Critical File                                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Action:  rm .env.local                                        ║
║                                                               ║
║ Why risky:                                                    ║
║   .env files contain credentials and API keys.                ║
║   Deletion may break local development setup.                 ║
║                                                               ║
║ Safe alternatives:                                            ║
║   → cp .env.local .env.local.bak   (backup first)            ║
║   → git stash                       (save all changes)       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Fade-to-Brief Learning System

### Session Counter

The guard tracks encounter counts per action type within the current session using a temp file:

```bash
# .claude/guard-session-counts (created fresh each session, not persisted)
force-push:2
new-code-file:1
reset-hard:0
checkout-restore:3
clean:0
branch-delete:0
critical-file:1
```

**No persistent memory** — counter resets when session ends. This means:

- New sessions always start with full teaching
- Frequent users learn fast within a session
- No config file bloat

### Verbosity Levels

| Encounters | Level | What Shows |
|------------|-------|------------|
| 1 | `full` | Teaching box + all 4 suggestion types + AskUserQuestion (4 options) |
| 2-3 | `brief` | Compact box (action + risk only) + AskUserQuestion (3 options: Yes/No/Bypass) |
| 4+ | `minimal` | One-line: `[guard] <action>. Allow? [Y/N]` + simplified AskUserQuestion (2 options: Yes/No) |

### Implementation

```bash
# Get current verbosity for this action type
_verbosity() {
  local action="$1"
  local countfile="${PROJECT_ROOT}/.claude/guard-session-counts"

  # Create if missing
  [[ -f "$countfile" ]] || echo "" > "$countfile"

  # Get count
  local count
  count=$(grep "^${action}:" "$countfile" 2>/dev/null | cut -d: -f2 || echo 0)

  # Increment
  if grep -q "^${action}:" "$countfile" 2>/dev/null; then
    sed -i '' "s/^${action}:.*/${action}:$((count + 1))/" "$countfile"
  else
    echo "${action}:1" >> "$countfile"
  fi

  # Return level
  if (( count == 0 )); then echo "full"
  elif (( count <= 2 )); then echo "brief"
  else echo "minimal"
  fi
}
```

---

## Quick Wins (< 30 min each)

1. **Session counter** — Track encounter counts per action type in temp file (~15 min)
2. **3-tier risk classification** — Map each action to low/medium/high in a lookup table (~15 min)
3. **Low-risk notes** — Add `[guard]` one-liner for allowed-but-notable actions (~15 min)
4. **Critical file patterns** — Add .env/.secret/.pem detection to Bash handler (~20 min)

## Medium Effort (1-2 hours)

5. **Full teaching box** — Redesign block messages with risk explanation + 4 suggestion types (~1 hr)
6. **AskUserQuestion integration** — Replace exit-2 blocks with structured confirm prompts (~1 hr)
7. **Fade-to-brief system** — Implement verbosity levels based on session counter (~45 min)
8. **Command rewrite suggestions** — Build lookup table of risky → safe command pairs (~30 min)

## Long-term (Future sessions)

9. **Coaching mode (tool input modification)** — Auto-correct commands instead of blocking
10. **Per-project risk config** — Let projects customize which actions are low/medium/high
11. **Analytics dashboard** — `/craft:git:guard-stats` showing block/allow patterns

---

## Recommended Path

→ Start with **3-tier risk classification** (Quick Win #2) — it's the foundation everything else builds on. Map each action to low/medium/high risk. Then add **session counter** (#1) and **full teaching box** (#5) together — that gives you the full teaching experience for medium risk. Add **AskUserQuestion integration** (#6) to make it interactive. The fade system (#7) is polish but makes the experience ADHD-friendly for repeat encounters.

## Architecture Summary

```text
Hook invocation (Edit/Write/Bash)
    │
    ├── Check bypass marker (.claude/allow-dev-edit) → ALLOW
    ├── Check one-shot marker (.claude/allow-once) → ALLOW + consume
    │
    ├── Classify action → LOW / MEDIUM / HIGH
    │
    ├── LOW:
    │   ├── Get session counter → first time?
    │   │   ├── Yes: stderr "[guard] <note>" (dim)
    │   │   └── No: silent
    │   └── Exit 0 (allow)
    │
    ├── MEDIUM:
    │   ├── Get session counter → verbosity level
    │   ├── full:    teaching box + AskUserQuestion (4 options)
    │   ├── brief:   compact box + AskUserQuestion (3 options)
    │   ├── minimal: one-liner + AskUserQuestion (2 options)
    │   ├── [CONFIRM] prefix in stderr for Claude parsing
    │   └── Exit 2 (block, awaiting user decision)
    │
    └── HIGH:
        ├── Hard block box with workflow steps
        ├── No AskUserQuestion (must switch branches)
        └── Exit 2 (block)
```

---

## Relationship to Existing Spec

This brainstorm **extends** the existing `SPEC-branch-guard-v2-confirmation-mode-2026-02-13.md`:

| Spec Coverage | This Brainstorm Adds |
|---------------|---------------------|
| `confirm` protection level | 3-tier risk classification (low/medium/high) |
| `[CONFIRM]` message format | Full teaching box with 4 suggestion types |
| One-shot marker | Session counter + fade-to-brief learning |
| Destructive commands list | Critical file protection (.env, secrets) |
| Bash write-through | Command rewrite suggestion templates |
| Backward compat | Low-risk silent notes for allowed actions |

**Recommendation:** Update the spec with this brainstorm's 3-tier classification, teaching box format, and fade-to-brief system before implementation.
