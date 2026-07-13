# Quick Reference: Branch Guard

**Teaching-first branch protection** — 3-tier risk classification with progressive trust, layered with an unconditional hard_deny tier (NEW in v2.33.0) and GitHub-side server protection.

`branch-guard.sh` is now part of the **two-hook Guard Suite**, alongside `no-switch-guard.sh`. Both share a registry (`~/.claude/guards.json`) and support a unified `--classify`/`GUARD_DRY_RUN=1` ground-truth mode. See the [Guard Suite Guide](../guide/guard-suite.md) and [Guard Suite Tutorial](../tutorials/TUTORIAL-guard-suite.md) for the full picture.

**Version:** 2.33.0 | **Hook:** `~/.claude/hooks/branch-guard.sh` | **Catalog:** `scripts/hard-deny-rules.json`

---

## Quick Decision Tree

```text
What do you need to do?
│
├─ Write new code file on dev?
│   └─ MEDIUM: Guard will [CONFIRM] — approve or use worktree
│
├─ Edit existing file on dev?
│   └─ LOW: Always allowed (note on first encounter)
│
├─ Write markdown on dev?
│   └─ LOW: Always allowed
│
├─ Force push on dev?
│   └─ MEDIUM: Guard will [CONFIRM]
│
├─ Do bulk maintenance on dev?
│   └─ ask "unprotect for maintenance" (dev/git skill)
│
├─ Work on feature branch?
│   └─ No restrictions — guard is inactive
│
└─ Anything on main?
    └─ BLOCKED — use PR workflow
```

---

## Risk Tiers at a Glance

| Risk | Icon | Behavior | Can Approve? |
|------|------|----------|-------------|
| **LOW** | `[guard]` | Note once, then silent | Auto-allowed |
| **MEDIUM** | `[CONFIRM]` | Teaching box → confirm | Yes (one-shot) |
| **HIGH** | `CATASTROPHIC` | Hard block | No (remove hook) |

---

## What Triggers Each Tier

### LOW (Auto-Allow)

| Action | Condition |
|--------|-----------|
| Edit file | File exists on disk |
| Write `.md` | Any markdown file |
| Write extensionless | `.STATUS`, `Makefile`, `Dockerfile`, `LICENSE` |
| Write in `tests/` | Any file under tests directory |
| Overwrite file | File already exists |

### MEDIUM (Confirm)

| Action | Trigger |
|--------|---------|
| New code file | `.py`, `.sh`, `.js`, `.ts`, `.json`, `.yml` (and more) via Write |
| Bash write-through | `echo > new.py`, `tee new.py`, `cp x new.py` |
| Force push | `git push --force` or `--force-with-lease` |
| Reset hard | `git reset --hard` |
| Checkout discard | `git checkout -- <file>` |
| Restore | `git restore <file>` (not `--staged`) |
| Clean force | `git clean -f`, `-fd`, `-fx` |
| Branch force-delete | `git branch -D` (all branches) |
| Critical files | `.env*`, `*.pem`, `*.key`, `*.secret`, `branch-guard.json` |

### HIGH (Hard Block)

| Action | Trigger | Scope |
|--------|---------|-------|
| Repository deletion | `rm -rf .git` | All branches |

---

## Hard_deny Layer (NEW in v2.33.0)

A fourth tier sits **above** the LOW/MEDIUM/HIGH classification — `autoMode.hard_deny` in `~/.claude/settings.json`, enforced by the Claude Code auto-mode classifier *before* any tool call runs.

| Property | Value |
|----------|-------|
| Enforcement | Claude Code classifier, before branch-guard.sh runs |
| Scope | All tools (Bash, Write, Edit, MCP), not just Bash |
| Bypass | **None.** Survives `.claude/allow-once`, asking "unprotect" (dev/git skill), and user intent |
| Install | Asking "protect" (dev/git skill) offers it; `bash scripts/install-hard-deny.sh --install` is the direct command |
| Opt out | ask "protect --no-hard-deny" (dev/git skill) |
| Inspect | `bash scripts/install-hard-deny.sh --show` |
| Remove | Edit `~/.claude/settings.json` directly, or `bash scripts/install-hard-deny.sh --uninstall` (removes only craft rules) |

### What craft installs

| Rule ID | Blocks |
|---------|--------|
| `force-push-main` | Force pushes to `main`/`master`/protected primary branch |
| `delete-git-dir` | Recursive deletion of the `.git` directory |
| `delete-github-repo` | `gh repo delete` and GitHub API equivalents |
| `destroy-claude-config` | Recursive deletion of `~/.claude` |

The installer also prepends `"$defaults"` so Claude Code's built-in catastrophic protections are inherited, not replaced.

### What craft deliberately does NOT install in hard_deny

| Pattern | Why left in branch-guard smart-mode |
|---------|-------------------------------------|
| Hard reset to `origin/main` | Legitimate on feature branches (throw-away-and-restart) |
| `find . -delete` | Legitimate with filters; classifier can't see filter args |
| Pipeline-driven removal (`... \| xargs rm`) | Decision depends on upstream pipeline, classifier can't see it |
| Discard uncommitted (`git checkout .`, `git restore .`) | Annoying but recoverable from local stash/reflog |

See `scripts/hard-deny-rules.json` for full rationale per rule.

---

## Bypass Mechanisms

### One-Shot (Single Action)

When Claude shows `[CONFIRM]` and you approve:

```text
Guard blocks → You approve → Claude writes .claude/allow-once
→ Guard consumes marker → Action proceeds → Protection resumes
```

No commands needed — just approve the prompt.

### Session Bypass (Bulk Operations)

```bash
# Enable bypass
ask "unprotect for maintenance" (dev/git skill)

# Do your work (all guards disabled)
# ...

# Re-enable
ask "protect" (dev/git skill)
```

---

## Verbosity Fade

| Encounter | Level | What You See |
|-----------|-------|--------------|
| 1st | Full | Teaching box + risk + alternatives |
| 2nd-3rd | Brief | Compact box: action + risk + branch |
| 4th+ | Minimal | `[CONFIRM] action on branch. Allow?` |

Resets after **8 hours** of inactivity.

---

## Branch Protection Map

| Branch | Protection | Write New Code | Edit Existing | Commit/Push |
|--------|-----------|---------------|--------------|-------------|
| `main` | `block-all` | Blocked | Blocked | Blocked |
| `dev` | `smart` | MEDIUM confirm | LOW allow | Allowed |
| `feature/*` | None | Allowed | Allowed | Allowed |
| `fix/*` | None | Allowed | Allowed | Allowed |

> **Note:** This table covers the **local hook** (`branch-guard.sh`). GitHub-side branch protection is a separate layer — see [GitHub-Side Companion](#github-side-companion) below.

---

## GitHub-Side Companion

The local hook stops accidents on your machine; GitHub-side branch protection stops anything that slips through. Together they form defense-in-depth:

| Layer | Lives at | Manages | Command |
|-------|----------|---------|---------|
| **Local hook** | `~/.claude/hooks/branch-guard.sh` | Edits/writes/bash before they leave your machine | ask "protect" / "unprotect" (dev/git skill) |
| **GitHub-side** | Repo settings → Branches | Pushes/PRs/deletions at the remote | ask "protect-baseline" (dev/git skill) |

Apply both for full coverage:

```bash
# Local hook (per-machine, automatic on craft installs)
ask "protect" (dev/git skill)

# GitHub-side (per-repo, one-time setup)
ask "protect-baseline" (dev/git skill)               # Current repo
ask "protect-baseline --repo OWNER/REPO" (dev/git skill) # Any repo
ask 'protect-baseline --check "test" --strict' (dev/git skill) # With status checks
```

**Important:** Asking "unprotect" (dev/git skill) only bypasses the local hook. GitHub-side protection set by `protect-baseline` is independent and must be removed via `protect-baseline --remove`.

---

## Common Scenarios

### "I need to fix a typo in existing code on dev"

```text
→ Guard: LOW (allowed, brief note first time)
→ No action needed — just edit
```

### "I need to add a new Python file on dev"

```text
→ Guard: MEDIUM [CONFIRM]
→ Options:
  a) Approve the confirm prompt (one-shot)
  b) /craft:git:worktree feature/<name> (recommended)
  c) ask "unprotect for maintenance" (dev/git skill) (bulk bypass)
```

### "I'm resolving merge conflicts on dev"

```bash
ask "unprotect for a merge conflict" (dev/git skill)
# Resolve conflicts freely
ask "protect" (dev/git skill)
```

### "I need to update documentation on dev"

```text
→ Guard: LOW (markdown always allowed)
→ No action needed — just write
```

### "I accidentally force-pushed"

```text
Guard would have shown [CONFIRM] first.
If you approved, use git reflog to recover.
```

---

## Config File (Optional)

`.claude/branch-guard.json` — override auto-detection:

```json
{
  "main": "block-all",
  "dev": "smart",
  "staging": "smart"
}
```

Only listed branches are protected. Unlisted = unrestricted.

---

## Session Files

| File | What It Does |
|------|-------------|
| `.claude/allow-dev-edit` | Session bypass (unprotect) |
| `.claude/allow-once` | One-shot approval marker |
| `.claude/guard-session-counts` | Verbosity fade counter |
| `.claude/branch-guard-dryrun` | Dry-run mode (log only) |
| `--classify` flag / `GUARD_DRY_RUN=1` env var | Ground-truth classification sweep (no-op mode) |

---

## Commands

### Local hook

| Command | Purpose |
|---------|---------|
| ask "protect" (dev/git skill) | Re-enable protection |
| ask "protect --show" (dev/git skill) | Show current level + counters |
| ask "protect --level smart" (dev/git skill) | Set protection level |
| ask "protect --reset" (dev/git skill) | Reset session counters |
| ask "unprotect" (dev/git skill) | Session-wide bypass |
| ask "git status" (dev/git skill) | Shows guard indicator |
| ask "guard status" (dev/git skill) | Guard Suite status (both hooks + registry) |
| ask "guard test" (dev/git skill) | Coverage audit against known operation taxonomy |
| ask "guard explain branch-guard" (dev/git skill) | Classification table for current branch |
| `GUARD_DRY_RUN=1 bash scripts/branch-guard.sh` | Ground-truth classification (no-op sweep) |

### GitHub-side

| Ask (dev/git skill) | Purpose |
|---------|---------|
| "protect-baseline" | Apply baseline protection (PR required, no force, no delete) |
| "protect-baseline --show" | Display current GitHub protection |
| "protect-baseline --check NAME" | Add required status check (repeatable) |
| "protect-baseline --strict" | Require branches to be up-to-date with base |
| "protect-baseline --dry-run" | Preview JSON payload, no API call |
| "protect-baseline --remove" | Remove protection from branch |

---

## Code Extensions (Trigger MEDIUM on New File)

```text
py sh js ts jsx tsx json yml yaml toml cfg ini r R zsh
```

Everything else (`.txt`, `.csv`, `.html`, `.md`) — allowed without confirm.

---

## See Also

- **Guide:** [Smart Mode Guide](../guide/branch-guard-smart-mode.md) — Full documentation
- **Guide:** [Guard Suite Guide](../guide/guard-suite.md) — Two-hook registry, profiles, fail-open
- **Tutorial:** [Guard Suite Tutorial](../tutorials/TUTORIAL-guard-suite.md) — Step-by-step walkthrough
- **Tutorial:** [Branch Guard Setup](../tutorials/TUTORIAL-branch-guard-setup.md) — Original single-hook setup
- **Workflow:** [Git Feature Workflow](../workflows/git-feature-workflow.md) — How guard fits in
- **Skill:** [dev/git](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md) — protect, protect-baseline, unprotect, guard (folded from `/craft:git:*`, 2026-07 v4 consolidation)
- **Refcard:** [REFCARD-PROTECT-BASELINE](REFCARD-PROTECT-BASELINE.md) — GitHub-side companion quick reference
