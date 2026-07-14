# GitHub-Attention Triage (issue-premise-check) — Orchestration Plan

> **Branch:** `feature/github-attention-triage`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-github-attention-triage`
> **Spec:** [`docs/specs/GRILL-github-attention-triage-2026-07-14.md`](docs/specs/GRILL-github-attention-triage-2026-07-14.md) (no separate SPEC — brainstorm produced [`BRAINSTORM-github-attention-triage-2026-07-14.md`](BRAINSTORM-github-attention-triage-2026-07-14.md), never captured to SPEC; grill targeted it directly and is the authoritative locked-decision source)

## Objective

Before implementing a fix requested by an open GitHub issue, check whether the
issue's own premise still holds against current code — v1 ships a single new
command that reads an issue + relevant code, emits a structured verdict
(valid / moot / unclear) with cited evidence, and gates `/craft:orch:drive`
when a driven task cites a `#NNN` issue. Advisory only — never auto-blocks,
never auto-closes.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|---|---|---|---|---|
| 1 | Verdict schema + classifier | High | Med | Done |
| 2 | `/craft:git:issue-check` command + docs + tests | High | Med | Done |
| 3 | `orch:drive` pre-filtered gate | Med | Small | Done |
| 4 | `/recap` pointer wording | Low | Small | Done |
| 5 | Dogfood (#199) + non-goal test + count-cascade | High | Small-Med | Done |

## Phase 1: Verdict Schema + Classifier

**Scope:** Lock the structured verdict return type (GRILL Branch 8) before any
command wiring, mirroring `commands/ci/triage.md`'s typed `classify_failure()`
pattern (see `tests/test_ci_triage_unit.py` for how that pattern is tested —
function extracted from the command `.md` file's fenced code block, exec'd
directly, no network calls).

- [x] 1.1 Define the verdict schema: `{status: "valid"|"moot"|"unclear", evidence: [{file, lines, note}], reasoning: str}`.
- [x] 1.2 Implement the classifier logic: given issue title/body (from `gh issue view <N> --json title,body,state,updatedAt`) and a code-search pass over the repo, produce a verdict per GRILL Branch 2 (verdict + cited evidence, never a bare label).
- [x] 1.3 Enforce GRILL Branch 9 (never cache): the classifier always takes freshly-fetched issue JSON as input — no stored/memoized verdict path anywhere in the implementation.

**Key files:** `commands/git/issue-check.md` (NEW — classifier lives in its fenced Python block, per the `ci:triage` precedent).

## Phase 2: `/craft:git:issue-check` Command + Docs + Tests

**Scope:** Wire the classifier into a real, invocable command (GRILL Branch 4 —
new command under `git:` namespace, working name `/craft:git:issue-check`,
confirm final name at this phase).

- [x] 2.1 Write `commands/git/issue-check.md` — frontmatter, argument parsing (`<issue-number>` required), invocation of the Phase 1 classifier, terminal output showing verdict + cited evidence.
- [x] 2.2 Update `skills/dev/git/SKILL.md` — new "When to Use" row + bump the "Consolidates the 10 `commands/git/*.md` commands" count in the intro line to reflect the new command.
- [x] 2.3 Update `docs/API-REFERENCE-COMMANDS.md` — new `### /craft:git:issue-check` section matching existing per-git-command entries.
- [x] 2.4 Update `docs/commands.md` — new entry in the git: command listing.
- [x] 2.5 New tutorial stub under `docs/` + `mkdocs.yml` nav entry, per the Documentation Coverage precedent (`.STATUS` v2.41.1: one stub per new command).
- [x] 2.6 Unit tests: `tests/test_issue_check_unit.py`, mirroring `tests/test_ci_triage_unit.py`'s extraction pattern, asserting against the Phase 1 schema.
- [x] 2.7 E2E test: extend `tests/test_plugin_e2e.py` with a fixture-repo case covering all three verdicts (valid / moot / unclear) — confirms `unclear` is a real third state, not forced into valid/moot.

**Key files:** `commands/git/issue-check.md` (NEW), `skills/dev/git/SKILL.md` (update), `docs/API-REFERENCE-COMMANDS.md` (update), `docs/commands.md` (update), `docs/tutorials/<name>.md` (NEW), `tests/test_issue_check_unit.py` (NEW), `tests/test_plugin_e2e.py` (update).

## Phase 3: `orch:drive` Pre-Filtered Gate

**Scope:** GRILL Branch 3 — gate `/craft:orch:drive` with the Phase 1 classifier,
but ONLY when the driven task/SPEC metadata cites a `#NNN` issue. Never runs
unconditionally (avoids the "unnecessary tax" pattern the token-usage-hooks
backlog was closed to avoid — see GRILL doc for the citation).

- [x] 3.1 Add the `#NNN`-citation pre-filter check to `commands/orch/drive.md` / `skills/orchestration/drive-engine/SKILL.md` — detect an issue reference in the task's SPEC/metadata before invoking the classifier at all.
- [x] 3.2 When a citation is found: run the classifier, surface verdict + evidence, never block (advisory only, GRILL Branch 6/original decision #3) — proceed regardless of verdict, just make it visible.
- [x] 3.3 When no citation is found: skip entirely, zero added cost (confirms the pre-filter actually elides the check, not just skips display).

**Key files:** `commands/orch/drive.md` (update), `skills/orchestration/drive-engine/SKILL.md` (update).

## Phase 4: `/recap` Pointer Wording

**Scope:** GRILL Branch 7 — correct the recap-pointer copy to match the
narrowed v1 scope (issue-premise-check only, not a 5-scan skill that doesn't
exist).

- [x] 4.1 Update `skills/workflow/adhd-workflow/SKILL.md`'s Context Restoration section: when `gh issue list --assignee @me` returns results, the recap output should suggest "run `/craft:git:issue-check <N>` to check if this issue's premise still holds" — not reference a broader GitHub-attention skill.

**Key files:** `skills/workflow/adhd-workflow/SKILL.md` (update).

## Phase 5: Dogfood + Non-Goal Test + Count-Cascade

**Scope:** GRILL Branch 6 (corrected) + Branch 1's narrow-scope discipline —
real-world validation against craft's own issue #199, plus the safety
invariant that this feature never mutates GitHub state.

- [x] 5.1 Dogfood test in `tests/test_plugin_dogfood.py`: run `/craft:git:issue-check 199` against this repo, assert `verdict.status == "valid"`, and assert the evidence cites the specific unmet acceptance criteria (Cowork/Desktop verify command, Step 13.6 WARN→remediate upgrade, recovery docs — none shipped, per the GRILL Branch 6 correction). This is a REAL run, not a mock — assert on actual `gh issue view 199` output shape.
- [x] 5.2 Non-goal test: assert the check never calls `gh issue close`/`gh issue edit`/any mutating `gh` subcommand — mutate-and-revert style test per memory `verify-gate-trigger-wired-not-just-logic`.
- [x] 5.3 Run `bump-version.sh --counts-only` to sync the managed-file list (plugin.json subtotal, command counts across ~14 files).
- [x] 5.4 Run `./scripts/docs-staleness-check.sh --fix` to sweep the ~29 doc refs that mention the git: command count/list.

**Key files:** `tests/test_plugin_dogfood.py` (update), managed count files (bump-version-driven).

## Friction Prevention

- Context first: verify CWD (`~/.git-worktrees/craft/feature-github-attention-triage`) and branch (`feature/github-attention-triage`) before any commit.
- No autonomous starts past a phase boundary without checking the prior phase's tests pass first.
- Test per phase — do not defer all testing to Phase 5; Phase 2 already includes its own unit+e2e tests.
- **Ungrilled-ambiguity backstop:** if a genuine unresolved judgment call surfaces mid-implementation (e.g. the classifier's exact code-search strategy, or the final command name choice deferred at 2.1), leave that checkbox unchecked, add a one-line blocker note directly in this file, and stop — never guess silently.
- Two GRILL open questions were deliberately left unresolved and handed here: final command name (2.1) and whether #199 is a fair calibration case given it's an infra/process issue rather than a code-fix (acknowledge in the Phase 5 test comments, don't silently paper over it).

## Acceptance Criteria

- [x] `/craft:git:issue-check <N>` runs, fetches live issue state, returns a structured verdict with cited evidence — never a bare label.
- [x] Verdict is never cached across invocations (GRILL Branch 9).
- [x] `orch:drive` only invokes the classifier when a task cites `#NNN`; zero cost otherwise.
- [x] `/recap`'s pointer text matches the narrow v1 scope.
- [x] Dogfood test against real issue #199 passes with `verdict.status == "valid"` and cited evidence.
- [x] Non-goal test confirms zero mutating `gh` calls anywhere in the implementation.
- [x] Full test suite passes (unit + e2e + dogfood); count-cascade files synced.

## Commit Strategy

Conventional commits per phase (`feat(git): ...`, `test(git): ...`,
`docs(git): ...`) — one or more commits per phase, never one giant commit for
the whole feature.

## Verification

```bash
python3 -m pytest tests/test_issue_check_unit.py tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -v
python3 -m pytest tests/ # full suite before PR, per pre-pr-testing.md tier table (code change → full suite)
./scripts/validate-counts.sh
./scripts/docs-staleness-check.sh
```

## Session Instructions

```
cd ~/.git-worktrees/craft/feature-github-attention-triage && claude
> "Read ORCHESTRATE-github-attention-triage.md and start Phase 1."
```

## Test-Plan Scaffold (default-on, tier-inferred)

New command + new tests + cross-command data flow (`orch:drive` integration) →
full tier set:

- **unit** — Phase 2.6 (`test_issue_check_unit.py`).
- **e2e** — Phase 2.7 (`test_plugin_e2e.py` extension).
- **integration** — Phase 3 (`orch:drive` pre-filter cross-command data flow).
- **dependency** — N/A — no new external dependency introduced.
- **count-cascade dogfood** — Phase 5.3/5.4 (new command → managed-file sync).

Each stub should be written red-first (failing placeholder) before the
implementation that makes it pass, per this repo's default scaffolding rule.

## Documentation Scaffold (default-on)

Per `commands/docs/sync.md`'s doc-impact rubric (not reproduced here — that
file is the single source of truth for types/thresholds):

- [x] **API reference** — Phase 2.3 (new command entry) — meets threshold (new command).
- [x] **Command/skill reference** — Phase 2.2 (`skills/dev/git/SKILL.md` row) — meets threshold.
- [x] **Tutorial** — Phase 2.5 (new stub) — meets threshold (new command, Documentation Coverage precedent).
- [ ] **Architecture doc** — N/A — score below threshold (single command addition, no architectural shift).
- [ ] **Changelog** — deferred to `/craft:docs:update --post-merge` (impl/post-merge phase per plan-orchestrator's lifecycle split, not spec-time).

### Site Consistency Checklist (impl/post-merge)

- [ ] `docs/API-REFERENCE-COMMANDS.md` git: section count matches actual file count.
- [ ] `mkdocs.yml` nav includes the new tutorial stub.
- [ ] No stale "N commands" claims left across the managed-file cascade (Phase 5.3/5.4 should have already caught this, this is the post-merge re-check).
