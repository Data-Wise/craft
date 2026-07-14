# GRILL: GitHub-Attention Triage (issue-premise-check)

**Date:** 2026-07-14 · **Target:** [BRAINSTORM-github-attention-triage-2026-07-14.md](../../BRAINSTORM-github-attention-triage-2026-07-14.md)
**Branches interrogated:** 5 (deep, attack angles: weakest recommendation, riskiest assumption, implementation regret, blast radius, benefit honesty)

Adversarial review (subagent, post-checkpoint) found decision 5 as originally
locked was factually wrong — see Branch 6 below for the correction. Locked
brainstorm decisions #2, #3, #6 (trigger points wired, advisory-only,
recap-gets-a-pointer) stand as written EXCEPT the pointer wording, corrected
in Branch 7.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | v1 scope | Ship narrow: issue-premise-check only (not the 5-scan broader skill). Overrides brainstorm Locked Decision #4. Rationale: memory adding-a-command-cascades-30-file-count-bump + native-first-thinning-refuted-for-craft-dev-ops — unvalidated breadth ships worse than validated narrow. |
| 2 | verdict format | Every check output MUST include verdict + cited evidence (specific code/test lines checked) — never a bare label, never uncited free-form reasoning. Matches pre-pr-testing.md's 'evidence not assertion' bar. |
| 3 | drive-gate cost control | orch:drive gate integration requires a cheap pre-filter: LLM premise-check only runs when task/SPEC metadata cites a #NNN issue. Never runs unconditionally — avoids repeating the token-usage-hooks-backlog 'unnecessary tax' pattern. |
| 4 | standalone placement | New command under git: namespace (not a /craft:git:status flag, not root-level promotion). Working name: /craft:git:issue-check (final name TBD at implementation). |
| 5 | v1 acceptance target (CORRECTED — see Branch 6) | Originally: dogfood against issue #199, asserting verdict=moot. SUPERSEDED — see Branch 6. |
| 6 | correction to Branch 5 (adversarial review finding) | gh issue view 199 confirms #199 is OPEN with 6 unmet acceptance criteria (Cowork/Desktop verify command, Step 13.6 WARN->remediate upgrade, recovery docs) -- none shipped. The memory cited (post-install-marketplace-refresh-before-update) fixed a DIFFERENT narrower bug (CLI-formula post_install ordering), not #199's scope. FIX: keep #199 as the v1 acceptance target, but flip the asserted verdict to valid, citing the specific unmet acceptance criteria as evidence. Tests the citation-based verdict format (Branch 2) without requiring a second hand-verified issue. |
| 7 | recap-pointer wording (adversarial review finding) | Brainstorm Locked Decision #6's recap-pointer text assumed the broader 5-scan skill; since v1 is narrowed (Branch 1), recap's suggested pointer text must say 'check issue premise', not gesture at a 5-scan skill that does not exist yet. |
| 8 | verdict schema (adversarial review finding) | Lock a structured return type for the verdict (e.g. {status: valid\|moot\|unclear, evidence: [{file, lines, note}], reasoning: str}) before implementation -- prose-only citation guidance (Branch 2) is not machine-checkable by unit tests. Mirrors commands/ci/triage.md's typed-dict classify_failure() pattern. |
| 9 | issue-state staleness (adversarial review finding, OPEN not locked) | No TTL / re-check-before-merge guidance exists yet for issue state changing between premise-check and actual implementation. Flagged as an open question for /craft:plan to resolve, not locked here. |

## Open Questions (not locked, hand to /craft:plan)

- Final command name (`/craft:git:issue-check` is a working name only).
- Issue-state staleness / re-check-before-merge policy (Branch 9).
- Whether #199's own hardness (infra/process bug, not a code-fix) makes it a
  poor calibration case for the verdict format generally, independent of the
  Branch 6 correction -- flagged by review, not resolved.

## Documentation Plan

- `skills/dev/git/SKILL.md` -- new "When to Use" row + update the "Consolidates
  the 10 commands/git/*.md commands" count in the intro line.
- `docs/API-REFERENCE-COMMANDS.md` -- new `### /craft:git:issue-check` section,
  matching the existing per-git-command entries.
- `docs/commands.md` -- new entry in the git: command listing.
- `commands/orch/drive.md` / `skills/orchestration/drive-engine/SKILL.md` --
  note the pre-filter (Branch 3): gate only fires when task metadata cites `#NNN`.
- `skills/workflow/adhd-workflow/SKILL.md` -- recap's pointer-offer text
  (Branch 7 correction).
- New tutorial stub under `docs/` (mkdocs nav entry), per the Documentation
  Coverage precedent (.STATUS v2.41.1: one stub per new command).
- Managed-file cascade: `bump-version.sh --counts-only` + plugin.json subtotal
  - ~29 doc refs, per memory `adding-a-command-cascades-30-file-count-bump`.

## Test Plan

- Unit: `tests/test_issue_check_unit.py`, mirroring `tests/test_ci_triage_unit.py`'s
  pattern (extract the classifier function from the command `.md` fenced block,
  exec directly, no network calls). Assert against the Branch 8 structured schema.
- E2E: extend `tests/test_plugin_e2e.py` with a fixture-repo case covering
  valid / moot / unclear verdicts (brainstorm doc's own E2E scaffold).
- Dogfood: `tests/test_plugin_dogfood.py` -- run against real issue #199,
  assert verdict=valid with evidence citing the specific unmet acceptance
  criteria (Branch 6).
- Non-goal test: assert the check never calls `gh issue close`/`gh issue edit`
  -- advisory-only is a testable invariant (mutate-and-revert style, per
  memory `verify-gate-trigger-wired-not-just-logic`).

## Handoff

Ready for `/craft:plan` (plan-orchestrator tier) -> `ORCHESTRATE-*.md` ->
`/craft:do` / `/craft:orch`. This grill never executed anything -- no code
was written, no command was created.
