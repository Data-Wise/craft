# ORCHESTRATE: Orchestrate-Family Simplification — Wave 1

**Source proposal:** [PROPOSAL-orchestrate-family-simplification-2026-07-01.md](../specs/PROPOSAL-orchestrate-family-simplification-2026-07-01.md) (approved)
**Grill (decisions locked):** [GRILL-orchestrate-family-simplification-2026-07-01.md](../specs/GRILL-orchestrate-family-simplification-2026-07-01.md)
**Date:** 2026-07-01
**Scope:** Wave 1 = ranks 1–3 only. Ranks 4–8 (incl. the `do.md` rewrite) are a later wave, gated on the ~2026-07-14 `/usage` checkpoint.
**Base branch:** `dev` · **Feature branch (to create):** `feature/orchestrate-family-wave1`

> **This file is self-contained.** An implementer (a fresh session or a background agent) should
> be able to execute it by reading only this file + the two linked docs. It does not depend on
> the conversation that produced it.

---

## How to start

This is code work → it needs a feature worktree (branch-guard blocks new code files on `dev`):

```bash
git worktree add ~/.git-worktrees/craft/feature-orchestrate-family-wave1 -b feature/orchestrate-family-wave1 dev
cd ~/.git-worktrees/craft/feature-orchestrate-family-wave1
# then: "Read docs/plans/ORCHESTRATE-orchestrate-family-wave1-2026-07-01.md and start Phase 1"
```

**Environment gotcha (known this session):** default `python3` on this Mac is Xcode's 3.9 and
crashes on `dict | None` (PEP 604) inside `commands/_discovery.py`, producing ~20 pre-existing
env-caused test failures. The real baseline via a working interpreter is
`2037 passed / 7 failed / 13 errors` — run the full suite with
`/opt/homebrew/bin/python3.13 -m pytest tests/ -q` (or `uv run --no-project --with pytest --with pyyaml pytest tests/ -q`) so the subprocess gets a 3.10+ interpreter. Do NOT treat the baseline
failures as regressions; compare against that exact count.

---

## Phase Overview

| Phase | Rank | Task | Effort | Risk | Status |
|-------|------|------|--------|------|--------|
| 1 | 1 | Delete/gut `commands/orchestrate/resume.md` (fictional feature) | Low | None | ✅ done |
| 2 | 2 | Thin-shim `commands/orchestrate/plan.md` → `plan-orchestrator` skill; drop duplicate template | Low-Med | Low | ✅ done |
| 3 | 3 (T2) | Extract shared verify-gate + engine-comparison prose into one on-demand reference | Low-Med | Low | ⊘ N/A — premise obsolete (see Phase 3) |

---

## Phase 1 — Remove the fictional `resume.md`

`commands/orchestrate/resume.md` (523 lines) describes an unimplemented "session teleportation"
feature (cloud sync, AES-256, S3, team sharing) with zero code, zero skill delegation, and
references sibling commands (`:sync`, `:archive`, `:share`) that don't exist. It also collides in
name with two *real* resume mechanisms.

- [x] 1.1 Confirm nothing depends on it: `grep -rn "orchestrate:resume\|orchestrate/resume" commands/ skills/ docs/ tests/` — expect only See-Also links + the guide. (Remaining hits are historical spec/plan docs under `docs/specs/` and `docs/specs/_archive/` — out of scope, they document past decisions.)
- [x] 1.2 Decide delete vs. gut-to-stub. **Default: delete the command file.** Deleted `commands/orchestrate/resume.md`, `docs/commands/orchestrate/resume.md`, `docs/tutorials/TUTORIAL-orchestrate-resume.md` (no discovery/test dependency found).
- [x] 1.3 Remove/redirect its See-Also references in `orchestrate.md`, `plan.md`, and both guide docs (`docs/guide/pipeline-orchestrate-guide.md`, `docs/guide/orchestrator.md`) — both guides already had no `orchestrate:resume` references. Also cleaned: `commands/hub.md` + `docs/commands/hub.md` (3 dashboard/reference blocks), `docs/ARCHITECTURE-CLAUDE-CODE-2.1.md` (deleted whole "Session Teleportation" architecture section), `docs/REFCARD.md`, `docs/guide/claude-code-2.1-integration.md` (deleted "Session Teleportation" section + best-practice item + frontmatter/overview mentions), `docs/cookbook/common/use-interactive-orchestration.md`, and `mkdocs.yml` nav (2 entries pointing at deleted files).
- [x] 1.4 Run the count cascade if a command was removed: `./scripts/validate-counts.sh` (command count drops by 1 — update all surfaces it flags). Command count 117→116 (craft subtotal 103→102). Updated `.claude-plugin/plugin.json`, `README.md`, plus ~16 additional doc files carrying the literal "117 commands" claim (`CLAUDE.md`, `docs/QUICK-START.md`, `docs/PLAYGROUND.md`, `docs/ADHD-QUICK-START.md`, `docs/architecture.md`, `docs/commands.md`, `docs/commands/overview.md`, `docs/commands/arch.md`, `docs/getting-started/choose-path.md`, `docs/guide/getting-started.md`, `docs/guide/claude-code-2.1-integration.md`, `docs/guide/homebrew-automation.md`, `docs/guide/homebrew-installation.md`, `docs/tutorials/TUTORIAL-smart-help.md`, `docs/tutorials/TUTORIAL-first-10-minutes.md`). `validate-counts.sh` is green. `docs-staleness-check.sh` Phase 7 residual warnings (`docs/guide/check-command-mastery.md`, `docs/guide/hub-live-dashboard.md`, `docs/tutorials/TUTORIAL-code-skill-standards.md`) are frozen illustrative sample-output blocks (not live count claims) — deliberately left untouched.

**Acceptance:** no dangling links to `orchestrate:resume`; `validate-counts.sh` green; the two
*real* resume mechanisms are the only ones a user can find.

---

## Phase 2 — Thin-shim the zombie-deprecated `plan.md`

`commands/orchestrate/plan.md` is frontmatter-marked `deprecated: true` /
`replaced-by: skills/orchestration/plan-orchestrator/` but still carries the full 8-step
spec→ORCHESTRATE→worktree logic verbatim, duplicating `plan-orchestrator/SKILL.md` — including
the ORCHESTRATE template in both files. Same pattern PR #236 fixed for `check.md` + git commands.

- [x] 2.1 **Diff-and-port gate (do NOT skip — this repo has hit the rich-body-trap before, ADR-002).** Enumerated every distinct behavior in `plan.md`'s body against `skills/orchestration/plan-orchestrator/SKILL.md`. Covered: spec discovery, spec parsing, cross-repo detection, plan confirmation, ORCHESTRATE template (canonical, matches), worktree creation, `.STATUS`/`.gitignore` tracking. **Gap found and ported:** the command's "Rebase Strategy" auto-detection (check `dev`'s last 5 commits for `chore:`/bot commits before suggesting a rebase) was entirely absent from the skill — added a new "Rebase Strategy (Spec → ORCHESTRATE mode)" subsection under the skill's Auto-Detection section before shimming. **Separately found (pre-existing, unrelated, out of scope — flagged as a background task instead of fixed here):** the skill's own "Scaffold templates live in `references/scaffold-templates.md`" pointer (lines ~172, ~190) uses a relative path with no local file — the real shared file is `skills/workflow/brainstorm-insights/references/scaffold-templates.md`. This predates Wave 1 and is orthogonal to the resume/plan consolidation; not touched here.
- [x] 2.2 Replace `plan.md`'s body with a thin shim: keep frontmatter + args surface, delete the inline 8-step logic and the duplicated ORCHESTRATE template, point execution at the skill (the PR #236 / `grill.md` shim shape used as the reference).
- [x] 2.3 Verify the ORCHESTRATE template now lives in exactly ONE place (the skill). `grep -n "ORCHESTRATE Template\|Phase Overview" commands/orchestrate/plan.md` → no matches, confirmed.
- [x] 2.4 Ran the deprecated-command auditor. Note: the ORCHESTRATE file's originally-suggested single-arg invocation (`--pair commands/orchestrate/plan.md`) doesn't match the script's actual signature (`--pair FILE_A FILE_B`); ran `python3 scripts/audit-deprecated-commands.py --pair commands/orchestrate/plan.md skills/orchestration/plan-orchestrator/SKILL.md` instead. Result: ratio 4.3 (flagged, threshold 2.0) — but this is expected/correct for a fully-thinned shim: the reference pattern (`commands/grill.md` vs `skills/workflow/grill/SKILL.md`) also flags at ratio 2.4, and even non-deprecated `commands/check.md` flags at 2.7 against its skill. The script's own docstring confirms exit 1 is "WARN signal, not a hard gate." The repo-wide sweep (`audit-deprecated-commands.py` with no args) does NOT list `plan.md` among its 11 flagged commands, confirming no regression in that direction.

**Acceptance:** `plan.md` is a shim (no duplicate logic/template) — confirmed; auditor ratio is the
expected direction for a thin shim (advisory-only, not a hard gate) — confirmed; guide docs updated
to note the skill is canonical — added a canonical-skill pointer note to
`docs/guide/pipeline-orchestrate-guide.md` (the "documented as live, actually deprecated" mismatch
is resolved).

---

## Phase 3 — Extract the shared verify-gate + engine-comparison prose (T2)

`orchestrate.md`, `workflow.md`, and `drive.md` each carry their own partial copy of a
"which engine when" comparison table + near-identical "real verify gate" prose. Copied into every
always-loaded command body → drift + token cost. **Token lever: progressive disclosure** (move
shared prose into one on-demand reference).

**PHASE 3 IS A NO-OP — premise obsolete, confirmed against the current tree, no extraction performed.**

Verification: `git diff dev -- commands/orchestrate.md commands/orchestrate/workflow.md
commands/orchestrate/drive.md` is **empty** — Phases 1–2 never touched these three files, so this
reflects the state at branch point, not something this wave caused. Re-reading each file directly
(not from the plan's description):

- The "which engine when" comparison table exists in **exactly ONE place already**:
  `commands/orchestrate/workflow.md` lines 33–39 (a `> **Which orchestration mode?**` blockquote
  table). `commands/orchestrate/drive.md` does not carry this table at all. `commands/orchestrate.md`
  does not carry it either (checked `## See Also`, `## Reference`, and the full file — no match).
- The "real verify gate" prose is **not a verbatim copy** across files — `workflow.md` Step 6
  ("A `verify` stage runs the project's real verification command; its exit status is the
  authoritative pass/fail") and `drive.md` Step 7 ("the `drive-engine` skill runs the project's
  actual verify command + `git status --short`... Green is required to declare done") are
  independently-worded, each legitimately describing that command's own step. Neither is a
  copy-paste duplicate of the other, and `orchestrate.md` doesn't carry this prose at all.
- So the acceptance criterion "three command bodies shrink" has no referent — there is nothing to
  extract into a shared reference. Creating one anyway would add indirection for zero drift
  reduction and risk the exact phantom-command failure mode 3.1 itself warns about
  (`commands/_discovery.py:267,287` turning any new `.md` under `commands/` into a discovered
  command).
- **3.3's rank-4 self-contradiction is confirmed present**, exactly as the plan anticipated:
  `commands/orchestrate.md:289` says `"Route to /craft:orchestrate:drive using the detected
  spec/workflow file"` when the engine actually being routed to is `workflow`, not `drive`. Per
  3.3's own instruction ("leave the engine-name/route bug alone... rank 4 is NOT in this wave"),
  this is confirmed but deliberately NOT fixed here.

- [x] 3.1 N/A — no duplicated engine-comparison table to extract (exists in exactly one place).
- [x] 3.2 N/A — no copied blocks exist in the other two command bodies to replace.
- [x] 3.3 Confirmed the `orchestrate.md:289` self-contradiction exists; left it alone (rank 4, out of Wave 1 scope) per the plan's own instruction.
- [x] 3.4 N/A — no new reference file created, so nothing to count/lint. `validate-counts.sh` remains green (verified after Phases 1–2 already).

**Acceptance:** re-scoped to "confirm or refute the premise, act only if real." Premise refuted with
evidence above; no action taken; nothing regressed.

---

## Verification (run before offering merge)

```bash
# Full suite via a working interpreter (NOT bare python3 — see env gotcha)
/opt/homebrew/bin/python3.13 -m pytest tests/ -q
# Compare against baseline: 2037 passed / 7 failed / 13 errors (env-caused, not regressions)

./scripts/validate-counts.sh          # counts consistent after any command removal
npx markdownlint-cli2 $(git diff --name-only dev | grep '\.md$')   # docs clean
```

---

## Commit strategy

Conventional commits, one per phase:

- `refactor(orchestrate): remove unimplemented resume.md session-teleportation`
- `refactor(orchestrate): thin-shim plan.md to plan-orchestrator skill (ADR-002)`
- `refactor(orchestrate): extract shared engine-comparison ref (token: progressive disclosure)`

Then `gh pr create --base dev`. Commit as you go; do **not** push/PR/merge if running as an
unattended agent — leave that to the review gate.

**Review gate (updated 2026-07-01):** under this session's standing authorization (`.STATUS`),
the dispatching session pushes/opens the PR/merges directly once CI is green (or confirmed-benign
per the documented `Validate Plugin Structure` pattern) and the checkboxes + Verification section
have been re-run and confirmed — no separate ask per merge. Post-merge, run the applicable check
(`validate-counts.sh` / `docs-staleness-check.sh` / broken-links).

---

## .STATUS + tracking

- Add an Active Worktrees row for `feature/orchestrate-family-wave1` when the worktree is created.
- Update each Phase Overview status cell (☐ → ⏳ → ✅) as phases complete — this is the durable,
  session-independent progress record (the memory-tool pattern; survives compaction).

## Not in this wave (wave 2, gated on /usage checkpoint ~2026-07-14)

Ranks 5–8: T1 thin-shim `do.md` scorer, T4 plugin-wide concurrency cap, T5 path-scope craft's
own guidance, unify the two complexity scorers. Plus the 2 **[convention]** decisions (doc-types
enforced? PROPOSAL first-class?) — separable, need your explicit confirm first (grill Open
Question).
