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

**Known sandbox quirk (Cowork/this environment specifically, not the repo):** the bash sandbox sometimes can't `unlink()` files under `.git/` (lock files, temp objects, worktree metadata) — `git worktree add`, `git commit`, normal `git update-ref` can all fail with "Operation not permitted." Workaround: build commits via `git commit-tree` against an alternate `GIT_INDEX_FILE` on the same device, then overwrite the ref file directly with `printf '%s\n' "$HASH" > .git/refs/heads/<branch>` — **never with `2>&1` in the hash-capturing command**, that corrupts the ref by writing warning text into it. Materialize a tree for testing via `git archive <ref> | tar -x` rather than `git checkout`, since archive doesn't touch the index/locks. This is very likely sandbox-specific — confirm normal git works fine on the actual Mac before assuming this applies there too.

**My response-format preferences:** ADHD-optimized — TL;DR for anything over 200 words, bullets/bold over prose, time estimates, status icons (🟢🟡🔴) for tool/error outcomes, LaTeX for any math. Expert-level depth assumed, not beginner explanations. I want tools used proactively without asking permission for routine reads/greps/test-runs — ask only when something is genuinely destructive, ambiguous, or needs my judgment call (a design tradeoff, a scope decision, an irreversible action).

**Before doing real work:** check `.STATUS` for in-flight branches and the "Next Action" block at its top, check for any open `docs/specs/SPEC-*.md` relevant to what I'm asking about, and check git branch state before editing anything.
