# Handoff: `feature/token-usage-reduction`

Paste this into a fresh session to resume exactly where this one left off.

---

I'm continuing work on craft's `feature/token-usage-reduction` branch. Here's the exact state:

**Branch:** `feature/token-usage-reduction`, 6 commits ahead of `dev`, clean fast-forward (no rebase needed). NOT merged. NOT pushed to origin.

**Commits, in order:**
1. `9abdd1b1` — pin agent models (`model:` frontmatter) on `agents/orchestrator-v2.md` + `agents/orchestrator.md`; extracted BEHAVIOR 5 (error handling) + BEHAVIOR 9 (timeline) into new `skills/orchestrator-resilience/SKILL.md`
2. `0e076e66` — `/refine` command reduced 631→42 lines (thin shim pointing at `skills/workflow/prompt-refiner/`, ADR-002 pattern)
3. `c7f9010e` — fixed fictional `subagent_type` names (`backend-architect` etc. don't exist) in brainstorm's old max-depth agent delegation
4. `039530b5` — full `/brainstorm` redesign: split `skills/workflow/brainstorm-insights/` into `brainstorm/` (ideation) + `brainstorm-insights/` (session friction reports, kept dir name for path stability); cut decision points 4→2; removed in-skill agent spawning in favor of the existing `--orch` flag
5. `81750e05` — verification pass: ran the FULL pytest suite (~2056 tests) for the first time against the branch, found and fixed 2 real regressions (`test_skill_trigger_phrases_unique`, `test_refine_flag_documented`) plus 1 more (`test_behavior_9_timeline`); fixed skill-count drift (40 documented → 42 actual, across 14+ files); fixed stale `/brainstorm` syntax in `commands/hub.md` + `docs/commands/hub.md` + `docs/skills-agents.md`
6. `1974ffeb` — added `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` (full 56-deprecated-command audit, ranked by body-size ratio vs `replaced-by:` skill) + `scripts/audit-deprecated-commands.py` (reusable, committed, executable) + `.STATUS` session entry

**Verification state (all clean as of commit 6):** full pytest suite, `validate-counts.sh`, `bump-version.sh --verify`, `docs-staleness-check.sh` (1 pre-existing unrelated warning: `commands/workflow/brief.md` missing a tutorial), `governance/checks/status_drift.py`.

**What's BLOCKED and needs you, not me:**
1. **GitHub PR creation / push.** No working `GITHUB_TOKEN`/`GH_TOKEN` was available in the prior session's connector. Run `gh auth status` to check, then either authorize the connector (claude.ai connector settings, or `/mcp` in an interactive Claude Code session) so a future session can push/PR directly, or do it yourself:
   ```bash
   git fetch && git checkout feature/token-usage-reduction
   git push -u origin feature/token-usage-reduction
   gh pr create --base dev --title "Token usage reduction: orchestrator model routing, /refine + /brainstorm redesign"
   ```
2. **Human diff review.** Every commit on this branch was built via manual git plumbing (`git commit-tree` + direct ref writes) because the sandbox couldn't `unlink()` files under `.git/`. The commits are structurally verified (`git cat-file -t`, byte-for-byte content checks against what was tested) but nobody has looked at the actual diff yet. Get a real worktree: `git worktree add ../craft-review feature/token-usage-reduction`.

**Next steps from the SPEC (`docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md`), not yet decided or started:**
- §4.1: new WARN-only governance rule generalizing `scripts/audit-deprecated-commands.py` into `governance/checks/` (R03/R04 FIXTURE+LIVE pattern)
- §4.2: consolidate count-of-record checking — either widen `validate-counts.sh`'s file list (cheap) or designate one source of truth and regenerate the rest (bigger payoff)
- §4.4/§4.5: decide whether to consolidate `skills/dev/git/` (target of 6 commands, 4185 source lines) before any v3.0.0 cutover — highest-leverage single item in the audit
- Open question: does §4.1's governance rule get built now, or after this branch merges (avoid scope creep)?

**Files to read first if context is needed:** `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30-REVIEW.md` (committed — full review with rationale), `token-reduction-plan.md` (committed — original research), `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` (committed — the audit), `docs/internal/GROUNDING-craft.md` (committed — durable project context for future sessions).

Please pick up from here — don't re-research the token-usage problem or re-run the full verification pass, it's already done and documented above. Confirm current branch/auth state, then move on the blocked items or the next-steps list per my direction.
