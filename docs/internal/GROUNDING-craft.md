# Grounding prompt: craft plugin work

Paste this at the start of a fresh session to re-establish context before diving into craft work.

---

I'm Stat-Wise (Davood Tofighi), a statistics professor at UNM working on causal inference / causal mediation research. This session is about **craft**, my Claude Code plugin at `~/projects/dev-tools/craft` — NOT my research work, NOT the MediationVerse R packages. Keep those separate unless I explicitly connect them.

**What craft is:** a 117-command, 42-skill, 8-agent Claude Code plugin (`.claude-plugin/plugin.json`) for general dev-tools workflow automation — git, docs, site, testing, CI, distribution, release pipeline, plus ADHD-friendly features (brainstorming, task management, spec capture). It is its own git repo with its own conventions, distinct from my research repos.

**Git workflow (read `CLAUDE.md` in the repo root for full detail, this is the critical part):**

```
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← plan here, branch from here
  ↑
feature/* (worktrees) ← all implementation work
```

Always start from `dev`. Never commit directly to `main`. Never write feature code directly on `dev` — branch first. Verify branch with `git branch --show-current` before any edit.

**Status tracking:** `.STATUS` (root) is the live ADHD-format status file — dense, single-line-per-field, append-only session log at the bottom (`✅ Session <date> (...)`). Read it first to know what's in flight. `docs/specs/SPEC-*.md` holds locked-decision design docs (look at a recent one for the exact format before writing a new one — locked-decisions table, dimensioned sections, status/date/driver header line). `docs/adr/ADR-*.md` holds architecture decisions with consequences sections worth reading before touching anything they govern (especially ADR-002, the deprecated-command-rich-body pattern).

**Verification scripts that matter, always run before claiming something is done:**

- `./scripts/validate-counts.sh` — command/skill/agent counts match `plugin.json`
- `./scripts/bump-version.sh --verify` — separately checks `docs/REFCARD.md`'s own count claim
- `./scripts/docs-staleness-check.sh --json` — nav completeness, count consistency, skill/agent doc coverage, cross-doc freshness
- `python3 -m pytest tests/` — full suite is ~2056 tests; if sandboxed with a short tool timeout, chunk by file list and run in parallel (`-n 4` via pytest-xdist) rather than trusting a partial run
- `python3 governance/checks/status_drift.py .` — `.STATUS` claims match git/manifest reality

**Known sandbox quirk (Cowork's bash tool specifically — CONFIRMED sandbox-only, not the repo, not the Mac):** the bash sandbox sometimes can't `unlink()` files under `.git/` (lock files, temp objects, worktree metadata) — `git worktree add`, `git commit`, normal `git update-ref` can all fail with "Operation not permitted." Workaround there: build commits via `git commit-tree` against an alternate `GIT_INDEX_FILE` on the same device, then overwrite the ref file directly with `printf '%s\n' "$HASH" > .git/refs/heads/<branch>` — **never with `2>&1` in the hash-capturing command**, that corrupts the ref by writing warning text into it. Materialize a tree for testing via `git archive <ref> | tar -x` rather than `git checkout`, since archive doesn't touch the index/locks. **Confirmed 2026-06-30:** the exact same stale lock file and dangling worktree that blocked the sandbox were removed instantly via Desktop Commander on the real Mac with plain `rm`/`git worktree remove` — no restriction there. Don't reach for the plumbing workaround if Desktop Commander (or any real-Mac shell) is available; use a normal `git worktree add` instead.

**Two separate execution environments, two separate credential states:** Cowork's sandboxed bash tool (`mcp__workspace__bash` / similar) has no GitHub auth at all — no `gh`, no SSH keys, no `GITHUB_TOKEN`/`GH_TOKEN` env vars. The GitHub MCP connector available in-session has also been unauthenticated every time it's been checked. **Desktop Commander is different**: it runs shell commands directly on the real Mac and inherits whatever's already authenticated there (`gh auth status` → logged in as `Data-Wise`, scopes `gist, read:org, repo, workflow`). When push/PR/issue-filing seems blocked, check Desktop Commander's `gh auth status` before concluding it's actually impossible — don't conflate "this one tool has no token" with "nothing here can authenticate." `git push`, `gh pr create`, `gh issue create` all work fine from there. The sandbox and the Mac's `craft` checkout share the same underlying `.git` object store, so commits built in the sandbox are already visible on the Mac without any bundle/transfer step — just `git branch -f <branch> <sha>` once you know the target SHA, or better, just don't build commits in the sandbox at all if Desktop Commander is available; use a real worktree there instead.

**Before assuming `git push` is safe:** check `git log origin/<branch>..<branch> --oneline` first — `dev` has had local-only unpushed commits sit around before (caused a squash-fold incident in an earlier session, see memory `squash-folds-unpushed-dev-base-commits`). Don't assume the local Mac checkout is in sync with origin.

**My response-format preferences:** ADHD-optimized — TL;DR for anything over 200 words, bullets/bold over prose, time estimates, status icons (🟢🟡🔴) for tool/error outcomes, LaTeX for any math. Expert-level depth assumed, not beginner explanations. I want tools used proactively without asking permission for routine reads/greps/test-runs — ask only when something is genuinely destructive, ambiguous, or needs my judgment call (a design tradeoff, a scope decision, an irreversible action).

**Before doing real work:** check `.STATUS` for in-flight branches and the "Next Action" block at its top, check for any open `docs/specs/SPEC-*.md` relevant to what I'm asking about, and check git branch state before editing anything. Also worth a quick `gh pr list` / `gh issue list` — `.STATUS` can lag actual GitHub state by a session or two.
