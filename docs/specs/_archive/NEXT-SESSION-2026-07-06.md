# NEXT-SESSION Plan — 2026-07-06

Handoff for the next Claude Code session. Entry point + pending work after
v2.61.0 shipped and the follow-through cleanup that came with it.

## State at handoff

- **v2.61.0 SHIPPED to `main`** — PR #271 (dev→main merge `6c3e2e95`, tag
  v2.61.0). Full detail in `.STATUS` `milestone`. `dev`/`main` in sync; `dev`
  is one commit ahead (`dc6ee28a`, a test-path fix — ships automatically in
  the next release, no action needed).
- **No worktrees active, no PRs open.** Working tree clean on `dev`.
- **Counts unchanged: 115 commands / 45 skills / 8 agents.**

## What happened this session (in order)

1. **PR #270 merged** (`3e736fc8`, 2026-07-06 morning): `do.md`'s dead
   agent-dispatch branch removed + 24-doc sweep, `verify-surfaces.sh
   --report-only`/`--version` + 2 new legs, `docs/runbooks/release-rollback.md`,
   G1 stray-file cleanup. Both `feature/craft-review-followups` and the
   already-stale `feature/mcp-ci-release` worktree/branch entries were closed
   out in `.STATUS`.
2. **Docs audit, pass 1** (`48eb6a74`): synced `docs/commands/dist/surfaces.md`
   (satellite mirror) with the new flags; fixed a docs-staleness false
   positive on `orch.md`'s mode-table "4 agents" via
   `scripts/config/exclusions.txt`.
3. **Docs audit, pass 2** (`5429b7ed`): found 2 dead-agent references PR
   #270's own hyphenated-only grep missed — `docs/index.md`'s feature grid
   listed "Backend architect" (space-separated, capitalized) as one of
   craft's 8 real agents; `skills/orchestrator-resilience/SKILL.md`'s
   fallback-dispatch example routed to the same 4 fictitious names. Both
   fixed.
4. **CHANGELOG/`.STATUS` backfill** (`03a12056`): both `CHANGELOG.md` and
   `docs/CHANGELOG.md` had an empty `[Unreleased]` section — PR #270's work
   and the 2 docs-audit commits had never been recorded. Backfilled. Flagged
   (not fixed — out of scope) a pre-existing, unrelated older-section drift
   between the two CHANGELOG files.
5. **Grilled and closed the orchestrate token-usage-hooks backlog**
   (captured 2026-07-02, `docs/specs/GRILL-orchestrate-token-usage-hooks-2026-07-06.md`):
   2 review passes (backend/architecture + interface/CLI-contract lenses)
   found the live-token-field hook infeasible (no introspection API for a
   prompt-driven session) and the `status`-delta hook structurally
   uncomputable mid-run. The one surviving feasible piece (`--token-report`)
   was rejected anyway — it duplicates the quota-tooling category removed
   earlier this session, and doesn't fix the retroactive-analysis problem
   that motivated the backlog. **No code changes.**
6. **`/craft:release` ran end-to-end**: pre-flight → version bump (2.60.0 →
   2.61.0, MINOR) → docs update (fixed a stale "112 Craft commands" count,
   converted `[Unreleased]`→`[2.61.0]`) → PR #271 → CI monitor → merge
   `--admin` → GitHub release → `dev` sync → downstream verify (docs site,
   tap formula, Homebrew Release/Aggregator Sync/Craft MCP Release workflows
   all confirmed live, not from local cache).
7. **Root-caused and fixed `test_roadmap_orchestrator_enhancements`**
   (`dc6ee28a`, on `dev`, post-release): this test had failed identically on
   every single CI run this session — PR #270, PR #271, and `main` directly
   — always the same `PosixPath('ROADMAP.md').exists()` assertion. The file
   was moved to `docs/archive/ROADMAP.md` back in commit `43f65991`
   ("archive stale ROADMAP.md"), but the test's path was never updated. Pure
   path bug, content assertions were always correct. Fixed; confirmed green
   locally. Not yet on `main` — ships in the next release, should eliminate
   the recurring need for `--admin` merges on this specific failure.
8. **`.STATUS` and this doc updated** to close out the session.

## Held / backlog

- **CHANGELOG drift (pre-existing, unrelated)**: `CHANGELOG.md` and
  `docs/CHANGELOG.md` have older-section content drift (different relative
  link paths, a few sections present in one but not the other) predating
  this session. Flagged twice, not yet fixed — scope it separately if it
  becomes a real problem (e.g. someone reads the wrong file and misses
  content).
- **16 local `feature/*` branches** flagged in `NEXT-SESSION-2026-07-02.md`
  as "not yet audited" — status unchanged since then; still worth a
  `/craft:git:clean` pass eventually, low urgency.
- Nothing else outstanding. This was a clean, fully-closed session.

## New rules/memories this session (already saved)

`code-review-skill-name-collision-with-coderabbit` — `Skill(skill="code-review")`
routes to CodeRabbit's plugin (third-party diff upload), not a native craft
skill; use `/craft:arch:review` + manual review instead when avoiding that.

## Reusable prompts / patterns produced (in transcript)

- Dispatching a backend/architecture review + an interface/CLI-contract
  review as two parallel agents to feed a `/craft:grill`'s codebase-first
  pre-answer sweep, before asking the user anything — used to grill the
  token-usage-hooks backlog, found the fatal design flaw before spending a
  single AskUserQuestion turn on it.
- Robust CI-poll `Monitor` script pattern: avoid `status` as a bash variable
  name (reserved/read-only in zsh — breaks silently with `read-only
  variable: status`), and don't background-poll with an artificial
  `timeout` piped into `tail` (the pipe's exit code masks a killed
  upstream process as success).
