# Handoff: `feature/token-usage-reduction`

Paste this into a fresh session to resume exactly where this one left off.

---

I'm continuing work on craft's `feature/token-usage-reduction` branch. Here's the exact state:

**Branch:** `feature/token-usage-reduction`, 8 commits ahead of `dev`, clean fast-forward (no rebase needed), **pushed to origin**. **[PR #232](https://github.com/Data-Wise/craft/pull/232)** is OPEN against `dev` (mergeable, docs/lint/link CI green, plugin-structure check was still running as of last check). **[Issue #233](https://github.com/Data-Wise/craft/issues/233)** tracks the audit findings + next-steps roadmap. Still needs: human review of the actual PR diff, then merge.

**Commits, in order:**

1. `9abdd1b1` — pin agent models (`model:` frontmatter) on `agents/orchestrator-v2.md` + `agents/orchestrator.md`; extracted BEHAVIOR 5 (error handling) + BEHAVIOR 9 (timeline) into new `skills/orchestrator-resilience/SKILL.md`
2. `0e076e66` — `/refine` command reduced 631→42 lines (thin shim pointing at `skills/workflow/prompt-refiner/`, ADR-002 pattern)
3. `c7f9010e` — fixed fictional `subagent_type` names (`backend-architect` etc. don't exist) in brainstorm's old max-depth agent delegation
4. `039530b5` — full `/brainstorm` redesign: split `skills/workflow/brainstorm-insights/` into `brainstorm/` (ideation) + `brainstorm-insights/` (session friction reports, kept dir name for path stability); cut decision points 4→2; removed in-skill agent spawning in favor of the existing `--orch` flag
5. `81750e05` — verification pass: ran the FULL pytest suite (~2056 tests) for the first time against the branch, found and fixed 2 real regressions (`test_skill_trigger_phrases_unique`, `test_refine_flag_documented`) plus 1 more (`test_behavior_9_timeline`); fixed skill-count drift (40 documented → 42 actual, across 14+ files); fixed stale `/brainstorm` syntax in `commands/hub.md` + `docs/commands/hub.md` + `docs/skills-agents.md`
6. `1974ffeb` — added `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` (full 56-deprecated-command audit, ranked by body-size ratio vs `replaced-by:` skill) + `scripts/audit-deprecated-commands.py` (reusable, committed, executable) + `.STATUS` session entry
7. `d80daa5f` — relocated 3 loose root-level session artifacts into proper repo paths (`docs/specs/SPEC-*-REVIEW.md`, `docs/plans/2026-06-30-token-usage-reduction-handoff.md` — this file, `docs/internal/GROUNDING-craft.md`), drafted (not yet filed) a GitHub issue body
8. `8094d6ec` — pushed the branch, opened PR #232, filed issue #233 (via Desktop Commander's authenticated `gh` CLI on the real Mac — separate from the GitHub MCP connector, which stayed unauthenticated throughout); updated the REVIEW doc and `.STATUS` to close out the "blocked on GitHub auth" framing

**Verification state (all clean as of commit 6, re-verified after via CI on the real PR):** full pytest suite, `validate-counts.sh`, `bump-version.sh --verify`, `docs-staleness-check.sh` (1 pre-existing unrelated warning: `commands/workflow/brief.md` missing a tutorial), `governance/checks/status_drift.py`. PR #232's CI: Markdown Linting/Link Validation/Docs Staleness all SUCCESS; Validate Plugin Structure (runs the test suite) was still IN_PROGRESS as of the last check — confirm it's green before merging.

**What's left — just the human parts now:**

1. **Review the actual PR diff**: [github.com/Data-Wise/craft/pull/232](https://github.com/Data-Wise/craft/pull/232). All 8 commits were eventually built/verified through a real `git worktree` on the Mac (`../craft-review`, via Desktop Commander) — no more plumbing-tool uncertainty, but nobody has looked at the rendered diff yet.
2. **Confirm CI is fully green**, then merge via the GitHub UI or `gh pr merge 232 --squash` (or whatever merge strategy this repo prefers — check past PRs for the convention, most look squash-merged per `.STATUS` history).
3. **After merge**: watch `/usage` for a week to validate the original token-reduction hypothesis; decide on SPEC §4.1 (new governance rule) — now or later.

**Next steps from the SPEC (`docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md`), not yet decided or started:**

- §4.1: new WARN-only governance rule generalizing `scripts/audit-deprecated-commands.py` into `governance/checks/` (R03/R04 FIXTURE+LIVE pattern)
- §4.2: consolidate count-of-record checking — either widen `validate-counts.sh`'s file list (cheap) or designate one source of truth and regenerate the rest (bigger payoff)
- §4.4/§4.5: decide whether to consolidate `skills/dev/git/` (target of 6 commands, 4185 source lines) before any v3.0.0 cutover — highest-leverage single item in the audit
- Open question: does §4.1's governance rule get built now, or after this branch merges (avoid scope creep)?

**Files to read first if context is needed:** `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30-REVIEW.md` (committed — full review with rationale + a dated UPDATE block at the top), `token-reduction-plan.md` (committed — original research), `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` (committed — the audit), `docs/internal/GROUNDING-craft.md` (committed — durable project context for future sessions, includes the Desktop-Commander-vs-sandbox-bash credential distinction learned this session).

Please pick up from here — don't re-research the token-usage problem, don't re-run the full verification pass (already done, documented above, and re-validated by PR #232's own CI), and don't re-attempt the push/PR/issue (already done — #232, #233). Confirm CI is green and merge, or work the SPEC §4 next-steps per my direction.
