---
name: git-workflow
description: This skill should be used when the user asks to "init a repo", "set up git", "manage branches", "switch branch", "create a worktree", "list worktrees", "clean merged branches", "sync with remote", "git activity", "git recap", "protect main", "apply branch protection", "bypass protection", "undo a commit", "fix a git mistake", or mentions git lifecycle, worktrees, branch protection, GitHub-side baseline protection, safety rails, or learning git workflows. Covers craft's full git lifecycle — repo init, branch and worktree management, remote sync, status/recap, local and GitHub-side branch protection, and the learning/safety reference docs.
---

# Git Workflow

End-to-end git lifecycle for craft users: initialize a repo, manage branches and worktrees, sync with remotes, protect (or temporarily bypass) main/dev, and surface the learning/safety reference material when users ask "how do I undo X?". Consolidates the 10 `commands/git/*.md` commands and 4 `commands/git/docs/*.md` reference docs into one coherent skill.

## When to Use

Activate when the user's prompt matches any of these concerns:

| User intent | Operation |
|-------------|-----------|
| "init repo", "set up git", "bootstrap repository" | Repo init |
| "show branches", "new branch", "switch branch", "delete branch" | Branch management |
| "git status", "what's the state of this repo" | Enhanced status |
| "clean merged branches", "delete merged" | Branch cleanup |
| "create a worktree", "list worktrees", "remove worktree", "finish worktree" | Worktree management |
| "sync with remote", "pull and push", "update from upstream" | Sync |
| "git activity", "git recap", "what did I commit today" | Activity summary |
| "protect main", "enable branch protection", "configure protection level" | Local protection |
| "apply baseline protection", "github-side protection", "PR-required setup" | GitHub-side protection |
| "bypass protection", "unprotect", "let me commit to main once" | Session bypass |
| "how do I undo X?", "fix a git mistake", "I messed up git" | Undo reference |
| "teach me git", "learn git workflow", "git refcard" | Learning material |
| "what are the safety rails?", "is this safe?" | Safety reference |

If the prompt is ambiguous, default to **enhanced status** (cheapest) and offer follow-ups.

## Prerequisites

- Git installed (`git --version`)
- For protection / GitHub-side operations: `gh` CLI authenticated
- For worktrees: shared `~/.git-worktrees/` directory convention (created on first use)
- For learning material: no prerequisites — pure reference

## Operations

### 1. Repo Init

Bootstrap a new git repo with craft's workflow conventions.

**Inputs:** optional remote (`OWNER/REPO` or URL), workflow pattern (`main-dev` | `simple` | `gitflow`), `--dry-run`, `--yes` for non-interactive.

**Steps:**

1. `git init` (idempotent — detect existing `.git/`).
2. Scaffold initial commit if working tree is empty.
3. If `main-dev` workflow (the craft default for multi-branch repos): create `dev` branch off `main`, set `dev` as the integration branch.
4. If `remote` provided: `gh repo create <remote>` (private by default), set origin, push both branches.
5. Apply local branch-guard rules (see Operation 8) and optionally GitHub-side baseline (Operation 9).
6. Write a starter `.gitignore`, `README.md` skeleton, and `CLAUDE.md` template if absent.

**Default workflow:** `main-dev` (craft's recommended pattern). Switch to `simple` only when the user explicitly opts out of the dev integration branch.

### 2. Branch Management

Create, switch, and delete branches safely.

**Sub-actions:** `new <name>`, `switch <name>`, `delete <name>`, `sync` (alias to Operation 6), and a default no-arg overview.

**Safety rules (enforced before any destructive action):**

- Never delete the current branch.
- Never delete protected branches (`main`, `master`, `dev`, `develop`).
- Refuse to switch if working tree has uncommitted changes — suggest `git stash` or commit first.
- For `new`, default base is `dev` if it exists, else `main`.

### 3. Enhanced Status

`git status` with extra context: current branch, ahead/behind, worktree-aware path, teaching-mode hints if a `_teaching/` directory exists.

**Modes:** `--verbose` (full `git status` after the summary), `--compact` (one-line summary only).

Use this as the cheap default when the user's prompt is ambiguous.

### 4. Branch Cleanup

Remove merged feature branches that no longer have work in progress.

**Steps:**

1. Detect merged branches using a two-pass approach:
   - **Pass 1 — `git branch --merged`**: catches normal fast-forward and merge-commit merges.
   - **Pass 2 — `is_squash_merged` (from `lib/git-utils.sh`)**: catches squash-merged branches that `--merged` misses. Uses `git cherry` (exact patch-ID match) with a tree-diff fallback for multi-commit squashes.
2. Skip protected branches and the current branch.
3. Skip branches with uncommitted changes or unpushed commits.
4. **ORCHESTRATE check:** warn if any `ORCHESTRATE-*.md` files remain on `dev` — they're working artifacts and should have been deleted by the `worktree finish` step.
5. Preview deletions in `--dry-run`; badge squash-merged branches as `(squash-merged, safe to delete)` so the user can distinguish them from normal merged branches. Confirm interactively before executing.

**Never** run `git branch -D` without explicit confirmation on branches that `is_squash_merged` returns `NOT_MERGED` or `UNKNOWN`.

### 5. Worktree Management

Parallel development via `git worktree` — each branch in its own folder, no stash juggling.

**Sub-actions:**

| Action | Behavior |
|--------|----------|
| `setup` | One-time: create `~/.git-worktrees/<project>/`, configure conventions |
| `create <branch>` | Add a worktree for a new or existing branch |
| `move <branch>` | Relocate an existing worktree (e.g., into the shared root) |
| `list` | Show all worktrees with branch + path |
| `clean` | Remove stale/merged worktrees safely |
| `finish` | Post-merge cleanup: delete worktree, delete branch, remove `ORCHESTRATE-*.md` |
| `validate` | Check worktree health (orphaned dirs, locked refs, branch drift) |
| `install` | Install the worktree helpers into a new project |

**Convention:** `~/.git-worktrees/<project>/feature-<name>/`, branch named `feature/<name>`, base typically `dev`.

**Critical safety rule:** before any git operation in a worktree, verify CWD and branch with `git worktree list` + `git branch --show-current` — sessions are CWD-pinned and absolute paths may diverge.

**`create` — branch guard:** worktrees must be created from `dev`, never `main` (hard block, no override — if on `main`, tell the user to `git checkout dev` first). After creating, install dependencies by auto-detecting project type (`package.json` → `npm install`; `pyproject.toml` → `uv venv && uv pip install -e .`; `requirements.txt` → `pip install -r requirements.txt`; `Cargo.toml`/`go.mod` → nothing, global cache; `DESCRIPTION`/`renv.lock` → `R -e "renv::restore()"`).

**`create` — scope-based auto-setup:** after creating, detect scope from the branch name and offer (via confirmation) to create workflow files:

| Branch pattern | Scope | Auto-create |
|---|---|---|
| `fix/*` | Small | No workflow files |
| `feature/*` | Medium | `ORCHESTRATE-<name>.md` |
| `v*` (release) | Release | ORCHESTRATE + `SPEC-<name>-<date>.md` |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + update `.STATUS` + update `CLAUDE.md` |
| User selects "custom" | Custom | Ask what to create |

**`move` — bring an in-progress branch into a worktree:** the sequence is stash (`git stash push --include-untracked`) → switch main folder to `main`/`master` → `git worktree add` for the feature branch → `cd` into the new worktree → `git stash pop` → install dependencies (same detection as `create`). Use case: work started in the main folder needs to move to a worktree so the main folder can return to a stable base branch.

**`finish` — complete a feature and open a PR:** (1) run tests auto-detected by project type (`npm test` / `pytest -v` / `R CMD check . --no-manual` / `cargo test` / `go test ./...`); (2) generate a changelog entry, inferring the section from branch prefix (`feat/*` → Added, `fix/*` → Fixed, `docs/*` → Documentation, else → Changed); (3) remove stray `ORCHESTRATE-*.md` working artifacts with a cleanup commit — they're feature-branch scratch files and must not merge to `dev`; (4) `gh pr create` targeting `dev` (or `main` if no `dev` branch exists) with an AI-generated title/body summarizing the commits. Flags: `--skip-tests`, `--draft`, `--target <branch>`.

**`validate` — read-only environment check:** confirm CWD is inside the expected `~/.git-worktrees/<project>/<branch>` path and the branch name matches the folder name; no confirmation needed, no changes made.

**`clean` — remove merged worktrees:** find worktrees for branches merged into `main`, confirm removal per-branch, then `git worktree prune` for stale references.

### 6. Remote Sync

Pull and push with conflict-handling guidance.

**Steps:**

1. Detect divergence: ahead/behind counts against upstream.
2. Fast-forward pull if behind only.
3. If both ahead and behind: prompt for `rebase` vs `merge` (default rebase for feature branches, merge for `dev`/`main`).
4. Push after pull; report any non-fast-forward rejections instead of force-pushing.

**Never** force-push to protected branches (`main`, `dev`). For feature branches, prefer `--force-with-lease` over `--force`.

### 7. Git Activity Recap

Lightweight summary: today's commits, this week's commits, branch ahead/behind, unpushed work, open PRs (`gh pr list --author @me`).

**Modes:** `default` | `detailed` | `summary`. Complements (does not replace) the broader `recap` operation in `adhd-workflow` — that one reads `.STATUS`; this one reads git history.

### 8. Local Branch Protection

Re-enable or configure craft's local `branch-guard.sh` hook (the layer that blocks commits to `main` / new code on `dev` / etc.).

**Sub-actions:** `--show` (display current config), `--level <smart|block-all|block-new-code>`, `--reset` (revert to auto-detect), `--no-hard-deny` (skip the hard_deny installation prompt).

**Three protection levels:**

- `smart` — matches the craft default table (main blocked, dev allows existing-file edits, feature/* allows all).
- `block-all` — paranoid; nothing flows through `main` or `dev` without explicit unprotect.
- `block-new-code` — allows .md and config edits, blocks new code files on `dev`.

This operation manages the **local hook only**. For GitHub-side protection, see Operation 9.

### 9. GitHub-Side Baseline Protection

Apply craft's GitHub-side baseline (PR required with `required_approving_review_count: 0`, no force-push, no deletions) to any repo via `gh api -X PUT repos/OWNER/REPO/branches/<branch>/protection`.

**Arguments:** `--repo OWNER/REPO`, `--branch`, `--check <name>` (repeatable, for required status checks), `--strict` (require up-to-date with base), `--dry-run`, `--remove`, `--show`.

**API quirks to handle:**

- `required_status_checks` and `restrictions` must be explicit `null` when absent — omitting them rejects the PUT.
- Status check names with embedded commas (`test (ubuntu-latest, 3.12)`) need `--check` as a repeatable flag, never comma-separated parsing.
- Route check names through `json.dumps()` / `jq -R -s`; never hand-build the JSON.
- Human-readable headers go to stderr; JSON payload to stdout — preserves pipeability (`... | jq`).

GitHub-side protection is **independent** of the local hook — `unprotect` (Operation 10) does NOT remove it.

### 10. Session Bypass (Unprotect)

Session-scoped bypass of the local branch-guard hook. Persists until `protect` (Operation 8) re-enables, or the session ends.

**Required input:** reason — one of `merge-conflict`, `ci-fix`, `maintenance`, or a freeform string for the audit log. Reason is logged to `.claude/branch-guard.log`.

**Does NOT bypass:** GitHub-side protection, pre-commit hooks, or any other layer. Only the craft local hook.

### 11. Reference Docs (Learning, Refcard, Safety, Undo)

When the user wants to **read** rather than **act**, surface the reference docs instead of running operations:

| User intent | Doc to surface |
|-------------|----------------|
| "teach me git", "how does this workflow work", "learning path" | `skills/dev/git/references/learning-guide.md` |
| "quick reference", "git refcard", "cheat sheet" | `commands/git/docs/refcard.md` |
| "is this safe?", "what are the safety rails?", "won't this break things?" | `skills/dev/git/references/safety-rails.md` |
| "I messed up", "how do I undo X", "git emergency" | `skills/dev/git/references/undo-guide.md` |

(`refcard.md` stays under `commands/git/docs/` — it wasn't flagged by the deprecated-command body-size audit and isn't part of this consolidation batch.)

For undo specifically, prefer the doc over speculating — it has scripted recovery flows for the common "oh no" scenarios (wrong commit message, wrong branch, accidental push, deleted work, merge conflicts).

## Cross-Operation Patterns

### Always verify CWD and branch before destructive ops

Worktrees and CWD-pinned sessions mean a single `git push` can land somewhere unexpected. Before any push, branch delete, or worktree remove:

```bash
git worktree list
git branch --show-current
pwd
```

### Branch architecture per repo

Two patterns coexist in the craft ecosystem:

- **Multi-branch:** `main` (PR only) ← `dev` (integration) ← `feature/*`. Used by **craft only**.
- **Single-integration:** `main` (PR only) ← `feature/*`. All other repos.

Detect with `git branch -a | grep -E 'remotes/origin/(main|dev)$'` before assuming which integration branch applies.

### Defense in depth

Branch protection layers, weakest to strongest:

1. Convention (CLAUDE.md says "don't commit to main").
2. Local pre-commit / branch-guard hook (Operation 8).
3. GitHub-side protection (Operation 9).

Operation 8 is the everyday enforcer; Operation 9 is the backstop. Apply both for solo-dev repos — the GitHub side catches local bypasses or work pushed from another machine.

## Overlap with Other Skills

- **`guard-audit`** — analyzes branch-guard rules to find false positives and proposes JSON config changes. **This skill** toggles the guard on/off and applies the baseline. Trigger phrases are distinct: guard-audit fires on "audit guard" / "guard friction" / "false positives"; this skill fires on "protect main" / "apply baseline" / "bypass protection". If the user reports the guard is blocking legitimate work, prefer `guard-audit` to tune config; if they want to toggle the layer, use this skill.
- **`release`** — runs the release pipeline (version bump, PR, tag, GitHub release). It uses git heavily but doesn't manage the git lifecycle itself. Hand off to `release` when the user says "ship it" or "cut a release"; stay here for branch/worktree/protection concerns.
- **`adhd-workflow`** — its `recap` reads `.STATUS` for session-level context. This skill's Operation 7 (git activity) reads git history. Both can be useful; run this skill's recap when the user explicitly says "git recap" or "git activity", and the other one for general "where did I leave off".

## Integration

This skill replaces the 10 commands and 4 reference docs under `commands/git/` during the v2.34.0 → v3.0.0 migration:

| Command | Operation |
|---------|-----------|
| `/craft:git:init` | 1 (Repo Init) |
| `/craft:git:branch` | 2 (Branch Management) |
| `/craft:git:status` | 3 (Enhanced Status) |
| `/craft:git:clean` | 4 (Branch Cleanup) |
| `/craft:git:worktree` | 5 (Worktree Management) |
| `/craft:git:sync` | 6 (Remote Sync) |
| `/craft:git:git-recap` | 7 (Git Activity Recap) |
| `/craft:git:protect` | 8 (Local Protection) |
| `/craft:git:protect-baseline` | 9 (GitHub-Side Protection) |
| `/craft:git:unprotect` | 10 (Session Bypass) |
| `commands/git/docs/learning-guide.md` (shim → `skills/dev/git/references/learning-guide.md`) | 11 (Reference: learning) |
| `commands/git/docs/refcard.md` | 11 (Reference: refcard) |
| `commands/git/docs/safety-rails.md` (shim → `skills/dev/git/references/safety-rails.md`) | 11 (Reference: safety rails) |
| `commands/git/docs/undo-guide.md` (shim → `skills/dev/git/references/undo-guide.md`) | 11 (Reference: undo) |

Both invocation paths work during the deprecation cycle. The skill auto-fires on natural-language match; explicit `/craft:git:*` paths continue to function until v3.0.0.

## Related Skills

- `release` — when the next action is "ship it" or "cut a release".
- `guard-audit` — when the user wants to tune guard config (false positives), not toggle protection.
- `adhd-workflow` — session-scope recap and next-task; this skill is git-scope.
- `project-planner` — multi-week project breakdowns; this skill handles the git lifecycle that planning eventually flows into.
