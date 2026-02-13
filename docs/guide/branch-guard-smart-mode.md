# Branch Guard: Smart Mode Guide

> **Teaching-first branch protection with progressive trust**

**Version:** 2.17.0 | **Hook:** `~/.claude/hooks/branch-guard.sh` | **Config:** `.claude/branch-guard.json`

---

## Overview

Smart mode replaces the binary block/allow system with a **3-tier risk classification** that teaches while protecting. Instead of hard-blocking every action on `dev`, the guard classifies each action by risk level and responds proportionally:

| Risk | Behavior | Recovery | Examples |
|------|----------|----------|----------|
| **LOW** | Note on first encounter, then silent | Automatic — action proceeds | Edit existing file, write markdown |
| **MEDIUM** | Teaching box + `[CONFIRM]` prompt | Approve once → one-shot marker | New code file, force push, destructive commands |
| **HIGH** | Hard block (never allowed) | Remove hook temporarily | `rm -rf .git` (repository deletion) |

---

## How It Works

### Protection by Branch

| Branch | Mode | What Happens |
|--------|------|-------------|
| `main` / `master` | `block-all` | Hard block on all writes, edits, commits, pushes |
| `dev` / `develop` | `smart` | 3-tier risk classification (LOW/MEDIUM/HIGH) |
| `feature/*`, `fix/*`, etc. | None | Unrestricted — all operations allowed |

### The Smart Mode Flow

```text
Tool call arrives (Edit, Write, or Bash)
  │
  ├─ Universal catastrophic check (ALL branches)
  │   ├─ rm -rf .git → HIGH (hard block)
  │   └─ git branch -D → MEDIUM (confirm)
  │
  ├─ Check bypass marker (.claude/allow-dev-edit) → allow if present
  ├─ Check one-shot marker (.claude/allow-once) → consume + allow
  │
  └─ Apply risk classification:
      ├─ Critical file? (.env, .pem, .key, guard config) → MEDIUM
      ├─ Markdown file? → LOW (always allowed)
      ├─ Test file? → LOW (always allowed)
      ├─ Existing file? → LOW (allowed)
      ├─ New code file? → MEDIUM (confirm)
      ├─ Force push? → MEDIUM (confirm)
      ├─ Destructive git? (reset --hard, checkout --, clean -f) → MEDIUM
      ├─ Bash write-through? (redirect/tee/cp creating new code) → MEDIUM
      └─ Everything else → allow
```

---

## 3-Tier Risk Classification

### LOW Risk — Note + Allow

The guard prints a brief note on the **first encounter** of each action type, then stays silent for the rest of the session. The action always proceeds.

**What triggers LOW:**

- Editing an existing file on dev
- Writing a markdown file (`.md`)
- Writing extension-less files (`.STATUS`, `Makefile`, `Dockerfile`)
- Writing files in `tests/` directory
- Overwriting an existing file

**What you see (first time only):**

```text
[guard] Editing existing file on dev (allowed)
```

After the first encounter of each type, the guard is completely silent.

### MEDIUM Risk — Teaching + Confirm

The guard shows a teaching box explaining the risk, suggests alternatives, and presents a `[CONFIRM]` prompt. The verbosity of the teaching box decreases over the session (fade-to-brief).

**What triggers MEDIUM:**

- Writing a new code file (`.py`, `.sh`, `.js`, `.ts`, `.json`, `.yml`, etc.)
- Force pushing (`git push --force`, `--force-with-lease`)
- Destructive git commands (`git reset --hard`, `git checkout --`, `git restore`, `git clean -f`)
- Editing/writing critical files (`.env`, `.pem`, `.key`, `.secret`, `branch-guard.json`)
- Force-deleting branches (`git branch -D`)
- Bash write-through creating new code files (redirect, tee, cp)

**What you see (1st encounter — full teaching):**

```text
╔═════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — Medium Risk                                  ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║ Action:  Write new .py file: utils/helper.py                ║
║                                                             ║
║ Why risky:                                                  ║
║   New code files on dev should go in a feature branch       ║
║                                                             ║
║ Safe alternatives:                                          ║
║   → /craft:git:worktree feature/<name>                      ║
║   → Edit an existing file instead (fixups allowed)          ║
║   → /craft:git:unprotect for bulk maintenance               ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
[CONFIRM] New code files on dev should go in a feature branch
Action:    Write new .py file: utils/helper.py
Risk:      New code files on dev should go in a feature branch
Suggest:   /craft:git:worktree feature/<name>
Suggest:   Edit an existing file instead (fixups allowed)
Suggest:   /craft:git:unprotect for bulk maintenance
Branch:    dev (smart mode)
Verbosity: full (1st encounter)
```

**2nd-3rd encounter — brief:**

```text
╔═════════════════════════════════════════════════════════════╗
║ BRANCH GUARD                                                ║
╠═════════════════════════════════════════════════════════════╣
║ Action:  Write new .py file: utils/other.py                 ║
║ Risk:    New code files on dev should go in feature branch   ║
║ Branch:  dev (smart mode)                                   ║
╚═════════════════════════════════════════════════════════════╝
[CONFIRM] Write new .py file: utils/other.py on dev.
```

**4th+ encounter — minimal:**

```text
[CONFIRM] Write new .py file: utils/third.py on dev. Allow?
```

### HIGH Risk — Hard Block

The guard blocks the action completely. No `[CONFIRM]` prompt is offered — the action cannot be approved through the guard.

**What triggers HIGH:**

- `rm -rf .git` (repository deletion) — blocked on ALL branches

**What you see:**

```text
╔═════════════════════════════════════════════════════════════╗
║ BRANCH GUARD — CATASTROPHIC RISK                            ║
╠═════════════════════════════════════════════════════════════╣
║ Cannot run rm -rf .git — destroys entire repository.        ║
║                                                             ║
║ Command: rm -rf .git                                        ║
║ Branch:  dev                                                ║
╠═════════════════════════════════════════════════════════════╣
║ This action is never allowed via the guard.                 ║
║ If intentional, remove the hook temporarily.                ║
╚═════════════════════════════════════════════════════════════╝
```

---

## Fade-to-Brief Learning

The guard tracks how many times each action type has been encountered in the current session using a counter file (`.claude/guard-session-counts`). Teaching verbosity decreases as you demonstrate understanding:

| Encounter | Verbosity | What You See |
|-----------|-----------|--------------|
| 1st | Full | Teaching box with risk explanation + alternatives |
| 2nd-3rd | Brief | Compact box with action + risk + branch |
| 4th+ | Minimal | One-line `[CONFIRM]` prompt |

The session counter automatically resets after **8 hours** of inactivity (the file's mtime is checked).

### How Action Types Are Tracked

Each action type has its own counter. For example, `write_new_code` and `force_push` are tracked independently — getting brief on new code files doesn't affect force push verbosity.

Action types tracked:

| Action Type | Trigger |
|-------------|---------|
| `edit_existing` | Edit any existing file |
| `edit_env` | Edit `.env` files |
| `edit_secret` | Edit `.pem`, `.key`, `.secret` |
| `edit_guard_config` | Edit `branch-guard.json` |
| `write_md` | Write markdown files |
| `write_extensionless` | Write extension-less files |
| `write_test` | Write test files |
| `write_existing` | Overwrite existing files |
| `write_new_code` | Write new code files |
| `write_env` | Write `.env` files |
| `write_secret` | Write secret/key files |
| `write_guard_config` | Write `branch-guard.json` |
| `force_push` | `git push --force` |
| `reset_hard` | `git reset --hard` |
| `checkout_discard` | `git checkout --` |
| `restore_discard` | `git restore` (not `--staged`) |
| `clean_force` | `git clean -f` |
| `bash_write_through` | Bash redirect/tee/cp creating new code |
| `branch_delete` | `git branch -D` |

---

## One-Shot Approval

When Claude shows a `[CONFIRM]` prompt and the user approves, Claude creates a one-shot marker file (`.claude/allow-once`) that the guard consumes on the next tool call. This allows the approved action to proceed without requiring `/craft:git:unprotect`.

### How It Works

1. Guard blocks action with `[CONFIRM]` message (exit 2)
2. User approves in Claude's UI
3. Claude writes `.claude/allow-once` marker
4. Claude retries the tool call
5. Guard sees marker → consumes it (deletes file) → allows action
6. Next tool call has no marker → normal protection resumes

### One-Shot vs Session Bypass

| Mechanism | Scope | Duration | Use Case |
|-----------|-------|----------|----------|
| One-shot (`.claude/allow-once`) | Single action | Consumed immediately | Quick one-off confirm |
| `/craft:git:unprotect` (`.claude/allow-dev-edit`) | All actions | Until `/craft:git:protect` | Bulk maintenance, merge conflicts |

---

## Bash Write-Through Detection

The guard detects when Bash commands create new code files through shell redirection, even though the `Write` tool isn't used directly.

### Detected Patterns

| Pattern | Example | Detection |
|---------|---------|-----------|
| Redirect (`>`, `>>`) | `echo "print(1)" > new.py` | Extracts target after `>` |
| Tee | `echo x \| tee new.py` | Extracts tee argument |
| Copy | `cp template.py new.py` | Extracts destination |

### What Gets Skipped

| Scenario | Why |
|----------|-----|
| Target is markdown (`.md`) | Always allowed on dev |
| Target contains variables (`$VAR`, backticks) | Can't resolve — gracefully skip |
| Target file already exists | Overwrite is LOW risk |
| On feature branch | No protection |

---

## Destructive Command Detection

These git commands are detected and classified as MEDIUM risk on `dev`:

| Command | Risk | Why |
|---------|------|-----|
| `git reset --hard` | MEDIUM | Discards all uncommitted changes permanently |
| `git checkout -- <file>` | MEDIUM | Discards working tree changes for files |
| `git restore <file>` | MEDIUM | Discards working tree changes (excludes `--staged`) |
| `git clean -f` / `-fd` / `-fx` | MEDIUM | Permanently removes untracked files |
| `git push --force` | MEDIUM | Overwrites remote history |
| `git branch -D` | MEDIUM | Force-deletes branch even if not merged |

### Safe Alternatives Suggested

Each destructive command includes teaching suggestions:

- `git reset --hard` → `git stash`, `git reset --soft`, `git diff`
- `git checkout --` → `git stash`, `git diff <file>`
- `git restore` → `git stash`, `git restore --staged` (unstage only)
- `git clean -f` → `git clean -n` (dry run), `git stash -u`
- `git push --force` → regular push, `--force-with-lease`

---

## Critical File Protection

Certain files trigger MEDIUM risk regardless of whether they're new or existing:

| Pattern | Files Matched | Why Protected |
|---------|---------------|---------------|
| `.env`, `.env.*` | `.env`, `.env.local`, `.env.production` | May contain secrets |
| `*.pem`, `*.key`, `*.secret` | `server.pem`, `api.key`, `auth.secret` | Cryptographic material |
| `branch-guard.json` | `.claude/branch-guard.json` | Modifying changes protection rules |

---

## Universal Catastrophic Checks

These checks run on **ALL branches** (including feature branches) before any protection filtering:

| Pattern | Risk | Branch Scope |
|---------|------|-------------|
| `rm -rf .git` | HIGH (hard block) | All branches |
| `git branch -D` | MEDIUM (confirm) | All branches |

---

## Configuration

### Per-Project Config (`.claude/branch-guard.json`)

Override auto-detection with explicit branch → protection mappings:

```json
{
  "main": "block-all",
  "dev": "smart",
  "staging": "smart",
  "production": "block-all"
}
```

**Rules:**

- Only listed branches are protected
- Unlisted branches have no protection
- Valid levels: `block-all`, `smart`, `block-new-code` (alias for smart), `confirm` (alias for smart)

### Code Extensions

The following extensions are classified as "code files" for new-file detection:

```text
py sh js ts jsx tsx json yml yaml toml cfg ini r R zsh
```

Files with other extensions (`.txt`, `.csv`, `.html`, etc.) are allowed without confirmation.

---

## Session Files

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `.claude/allow-dev-edit` | Session bypass marker | Created by `/craft:git:unprotect`, removed by `/craft:git:protect` |
| `.claude/allow-once` | One-shot approval marker | Created by Claude on confirm, consumed on next tool call |
| `.claude/guard-session-counts` | Verbosity fade counter | Auto-created, resets after 8h inactivity |
| `.claude/branch-guard-dryrun` | Dry-run mode marker | Created manually, logs blocks without enforcing |

---

## Relationship to Safety Rails

Smart mode implements the same progressive trust philosophy as the [Safety Rails Guide](../../commands/git/docs/safety-rails.md):

| Safety Rails Concept | Smart Mode Implementation |
|---------------------|--------------------------|
| "Show me everything first" (Week 1) | Full teaching box on 1st encounter |
| "I trust you, but I'm watching" (Week 3) | Brief box on 2nd-3rd encounter |
| "I trust you, tell me if wrong" (Week 4+) | Minimal one-liner on 4th+ encounter |

---

## See Also

- [Branch Guard Quick Reference](../reference/REFCARD-BRANCH-GUARD.md) — At-a-glance reference card
- [Branch Guard Setup Tutorial](../tutorials/TUTORIAL-branch-guard-setup.md) — Step-by-step setup
- [/craft:git:protect](../commands/git/protect.md) — Re-enable protection
- [/craft:git:unprotect](../commands/git/unprotect.md) — Session bypass
- [/craft:git:status](../commands/git/status.md) — Guard indicator
- [Safety Rails Guide](../../commands/git/docs/safety-rails.md) — Progressive trust philosophy
- [Git Feature Workflow](../workflows/git-feature-workflow.md) — How guard fits in the workflow
