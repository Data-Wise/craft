---
name: git-workflow
description: This skill should be used when the user asks to "init a repo", "set up git", "manage branches", "switch branch", "create a worktree", "list worktrees", "clean merged branches", "sync with remote", "git activity", "git recap", "protect main", "apply branch protection", "bypass protection", "undo a commit", "fix a git mistake", or mentions git lifecycle, worktrees, branch protection, GitHub-side baseline protection, safety rails, or learning git workflows. Covers craft's full git lifecycle — repo init, branch and worktree management, remote sync, status/recap, local and GitHub-side branch protection, and the learning/safety reference docs.
---

# Git Workflow

End-to-end git lifecycle for craft users: initialize a repo, manage branches and worktrees, sync with remotes, protect (or temporarily bypass) main/dev, check whether an open issue's premise still holds, and surface the learning/safety reference material when users ask "how do I undo X?". Consolidates the 9 `commands/git/*.md` commands and 4 `commands/git/docs/*.md` reference docs into one coherent skill.

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
| "list guards", "enable/disable guard", "explain what this command would do", "guard profile" | Guard registry CLI |
| "check if this issue still applies", "is issue #N still valid", "premise check before I fix this" | Issue premise check |

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
7. **Offer the protection audit/wizard immediately after creating the repo** (added by
   SPEC-branch-protection-consolidation-2026-07-07 §4.5): one `AskUserQuestion` — "Set up branch
   protection now?" with "Yes, run the audit (Recommended)" listed first and reasoned ("a
   freshly-scaffolded repo is unprotected until something enables it — cheapest to do now"). On
   yes, run **Operation 8's `--audit` flow exactly as documented there** — do not re-implement or
   re-describe the wizard here, this is the same logic invoked at a second trigger point. On no
   (or non-interactive `--yes` init), skip silently; the repo is left with whatever step 5 already
   applied.

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

`git status` with extra context: current branch, ahead/behind, worktree-aware path, teaching-mode hints if a `_teaching/` directory exists, and a guard-status line (protection level, session-confirm count, one-shot-pending state, or `BYPASSED (reason: ...)` — sourced from Operation 8's config/auto-detect, not re-derived here).

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

Re-enable or configure craft's local `branch-guard.sh` hook (the layer that blocks commits to `main` / new code on `dev` / etc.). Absorbs the former `commands/git/protect.md` (now a thin shim — see Integration table).

**Sub-actions:** `--show` (display current config), `--level <smart|block-all|block-new-code>`, `--reset` (revert to auto-detect), `--no-hard-deny` (skip the hard_deny installation prompt), `--audit` (gap-diff wizard, described below; **default action when invoked with no args and protection is already active** — bare `protect` with an active bypass still re-enables first, per Step 2 below, then offers `--audit`).

**Config file:** `.claude/branch-guard.json` (per-repo, protection *level* — a separate file from the global `~/.claude/guards.json` registry Operation 12 mutates; see that Operation's note on scope). Use one consistent variable name throughout any implementation — `CONFIG_FILE` — never a second alias (`CONFIG`); this fixes a drift bug carried in the pre-consolidation `protect.md`.

**Three protection levels:**

- `smart` — matches the craft default table (main blocked, dev allows existing-file edits, feature/* allows all).
- `block-all` — paranoid; nothing flows through `main` or `dev` without explicit unprotect.
- `block-new-code` — allows .md and config edits, blocks new code files on `dev`.

**Steps (bare invocation, no bypass active):**

1. Detect current branch (`git branch --show-current`) and current level: read `CONFIG_FILE`'s entry for the branch if present, else auto-detect from `docs/specs/baseline.json`'s `local_hook.recommended_level_by_branch_role` (main/master → block-all, dev/develop/draft → smart if that integration branch exists, feature/* and everything else → none).
2. If a bypass marker (`.claude/allow-dev-edit`) is active, remove it (`rm -f .claude/allow-dev-edit`) and report "Branch protection RE-ENABLED."
3. Run the hard_deny detection/install flow (unchanged from the former `protect.md`, skip entirely if `--no-hard-deny` or `~/.claude/.craft-hard-deny-declined` exists): `bash scripts/install-hard-deny.sh --check --json`, offer to install via `AskUserQuestion` (Yes install / Skip this time / Never offer again) if `would_add` is non-empty, run `bash scripts/install-hard-deny.sh --install` on yes.
4. If no bypass was active (protection already on), skip straight to the `--audit` wizard below unless `--show`/`--level`/`--reset` was explicitly passed instead.

**`--show`:** display branch, detected/configured level, session-confirm count, one-shot-pending state, bypass state — no changes made.

**`--level <level>`:** write `CONFIG_FILE`'s entry for the current branch (`jq --arg branch "$BRANCH" --arg level "$LEVEL" '.[$branch] = $level' "$CONFIG_FILE"`, creating the file if absent).

**`--reset`:** remove the current branch's entry from `CONFIG_FILE` (`jq --arg branch "$BRANCH" 'del(.[$branch])' "$CONFIG_FILE"`), reverting to auto-detect.

**`--audit` — gap-diff-then-ask wizard (added by SPEC-branch-protection-consolidation-2026-07-07 §4.5):**

1. Read local state: `CONFIG_FILE` entry (or auto-detect) for the current branch.
2. Read GitHub-side state by reusing Operation 9's existing `gh api` check — **do not re-implement**, call the same lookup Operation 9 already documents.
3. Diff both against `docs/specs/baseline.json` (local `recommended_level_by_branch_role`, GitHub `recommended_settings`).
4. For each gap found, walk it **one `AskUserQuestion` at a time** (never a single dump of every gap) — Recommended-first, with the reason stated (matches this skill's own grilling pattern, not a batch confirm). Example gaps: local level below baseline for this branch role, GitHub PR-required missing, force-push/deletion allowed.
5. Apply only what the user confirms per-gap. Never silently apply, never silently skip — the whole point of this wizard is asking, not automating past a prior always-confirm mistake this project already made and reverted once.
6. If no gaps found: report "Branch protection matches the recommended baseline — nothing to do."

This operation manages the **local hook config** (`.claude/branch-guard.json`) directly, and diffs GitHub-side state (via Operation 9) for the audit — but does not itself mutate GitHub-side settings; that write still goes through Operation 9. For GitHub-side protection application/removal, see Operation 9.

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

### 12. Guard Registry CLI

Inspect, enable, disable, and profile the craft guard suite (`branch-guard.sh` + `no-switch-guard.sh`). Absorbs the former `commands/git/guard.md` (now a thin shim — see Integration table). Guards live in `~/.claude/settings.json` as `PreToolUse` hooks; their toggle state is persisted in `~/.claude/guards.json`.

**This Operation is the sole sanctioned mutator of `~/.claude/guards.json`** (descriptive, not test-enforced — matches current practice, revisit only if a second writer appears). It does **not** own `.claude/branch-guard.json` (per-repo protection level) — that file is written directly by Operation 8's `--level`/`--reset`, a separate mutation surface for a separate file. The read path (`branch-guard.sh`/`no-switch-guard.sh` reading `guards.json` at hook-invocation time) is unchanged and has no LLM in it — a PreToolUse hook fires before any model turn.

**Sub-actions:** `list`, `status`, `explain <cmd>`, `test`, `enable <name|#>`, `disable <name|#> [--permanent|--session]`, `profile <focus|yolo|spec>`.

**Prerequisite:** verify `jq` is on PATH before any action; verify `~/.claude/guards.json` exists (point at `install-guards.sh` if not). Sweep and auto-clear expired mutes (`muted_until` in the past → set back to `null`) before displaying any state, for every sub-action.

**`list` / `status`:** read `~/.claude/guards.json` + `~/.claude/settings.json`, build a numbered table (alphabetical). **Generate this table from `guards.json` at render time — never hardcode it** (a third registered guard would otherwise go stale in the docs; this was a real gap in the former `guard.md`). State icons: `🛡️ enabled`, `⚠️ muted (Nm)`, `⛔ disabled`. `status` additionally shows registry path + mtime, active/muted counts.

**`explain <cmd>` — unified dry-run across both hooks (NEW, generalizes the former `guard.md`'s reasoning-only `explain`):** run the command text through **both scripts' real classification logic**, not LLM narration, via each script's `--classify` / `GUARD_DRY_RUN=1` mode (added to `scripts/branch-guard.sh` and `scripts/no-switch-guard.sh` by this consolidation):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"<cmd>"},"cwd":"<pwd>"}' \
  | GUARD_DRY_RUN=1 bash scripts/branch-guard.sh
echo '{"tool_input":{"command":"<cmd>"}}' \
  | GUARD_DRY_RUN=1 bash scripts/no-switch-guard.sh
```

Each script's classify mode prints a single line — `ALLOW: <reason>` / `ASK: <reason>` / `BLOCK: <reason>` (branch-guard) or `ALLOW:` / `YELLOW:` / `ASK:` (no-switch-guard) / `SKIP: <reason>` (muted/disabled) — reusing the existing `block()`/`ask()`/`announce()`/`_low_note()` call sites, so the printed tier is ground truth, not a re-derivation. **The CLI presents a single unified table from these two independent lines — it does not, and must not, unify the two scripts' actual emission mechanisms** (exit 2+stderr for branch-guard vs. `permissionDecision` JSON for no-switch-guard stay separate; already litigated and rejected in `SPEC-craft-guard-suite-2026-06-19.md` §2). Example combined output:

```
Dry-run: git switch main
─────────────────────────────────
branch-guard     → (not evaluated — Bash/switch is no-switch-guard's concern)
no-switch-guard  → ASK: Switch ONTO 'main' detected. main/master is protected.

Result: would prompt for confirmation
```

**`test`:** run `tests/test_branch_guard.sh` and `tests/test_no_switch_guard.sh` if present, report pass/fail/missing per script.

**`enable <name|#>` / `disable <name|#> [--permanent|--session]` / `profile <focus|yolo|spec>`:** unchanged from the former `guard.md` — `jq`-mutate `guards.json` (`enabled`, `muted_until`), never raw `cat >`. `focus` enables all; `yolo` mutes all 30 min; `spec` enables branch-guard and mutes no-switch-guard 30 min.

**`guards.json` schema:** `{"guards": {"<name>": {"enabled": bool, "muted_until": iso8601|null, "mute_window_min": int}}}`. `enabled: false` = permanently off; `muted_until` in the future = muted; both null/false-mute = active. Guard *logic* lives in the shell scripts — this file stores toggle state only.

### 13. Issue Premise Check

Before implementing a fix an open GitHub issue requests, check whether the
issue's own premise still holds against current code. Absorbs
`commands/git/issue-check.md`.

**Returns:** a structured verdict — `valid` (fix still needed), `moot`
(already resolved or closed), or `unclear` (cannot be mechanically
verified) — always with cited evidence (file path + note), never a bare
label.

**Never caches:** every invocation re-fetches the issue via `gh issue view`
fresh; no verdict is stored or reused across runs or trigger points.

**Never mutates:** read-only — no `gh issue close`/`edit`/`comment`/reopen`
call exists anywhere in the implementation.

**Consumers:** standalone (`/craft:git:issue-check <N>`) and
`/craft:orch:drive`'s pre-filter (only runs when a driven task's SPEC cites
a `#NNN` issue — zero cost otherwise).

See `commands/git/issue-check.md` for the classifier logic
(`classify_issue()`).

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

This skill replaces the 11 commands and 4 reference docs under `commands/git/` during the v2.34.0 → v3.0.0 migration (SPEC-branch-protection-consolidation-2026-07-07 folded `guard.md` in as a new Operation and thinned the 4 stale shims found during its own review sweep):

| Command | Operation |
|---------|-----------|
| `/craft:git:init` | 1 (Repo Init — now also offers the Op 8 audit wizard) |
| `/craft:git:branch` | 2 (Branch Management) |
| `/craft:git:status` | 3 (Enhanced Status) |
| `/craft:git:clean` | 4 (Branch Cleanup) |
| `/craft:git:worktree` | 5 (Worktree Management) |
| `/craft:git:sync` | 6 (Remote Sync) |
| `/craft:git:git-recap` | 7 (Git Activity Recap) |
| `/craft:git:protect` | 8 (Local Protection — now includes the `--audit` gap-diff wizard, absorbed from the standalone `protect.md`) |
| `/craft:git:protect-baseline` | 9 (GitHub-Side Protection — unchanged, stays a separate cross-linked command, not folded) |
| `/craft:git:unprotect` | 10 (Session Bypass — unchanged, already a thin shim) |
| `skills/dev/git/references/learning-guide.md` (command shim removed in v3.0.0 prune; content lives here) | 11 (Reference: learning) |
| `commands/git/docs/refcard.md` | 11 (Reference: refcard) |
| `skills/dev/git/references/safety-rails.md` (command shim removed in v3.0.0 prune; content lives here) | 11 (Reference: safety rails) |
| `skills/dev/git/references/undo-guide.md` (command shim removed in v3.0.0 prune; content lives here) | 11 (Reference: undo) |
| `/craft:git:guard` | 12 (Guard Registry CLI — new, absorbed from the standalone `guard.md`) |
| `/craft:git:issue-check` | 13 (Issue Premise Check — new, standalone command) |

Both invocation paths work during the deprecation cycle. The skill auto-fires on natural-language match; explicit `/craft:git:*` paths continue to function until v3.0.0.

## Related Skills

- `release` — when the next action is "ship it" or "cut a release".
- `guard-audit` — when the user wants to tune guard config (false positives), not toggle protection. Distinct from this skill's Operation 12 registry CLI: `guard-audit` proposes config changes for friction; Operation 12 toggles guards on/off/muted and explains what a command would do.
- `adhd-workflow` — session-scope recap and next-task; this skill is git-scope.
- `project-planner` — multi-week project breakdowns; this skill handles the git lifecycle that planning eventually flows into.
