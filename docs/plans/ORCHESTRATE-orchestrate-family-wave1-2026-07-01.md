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
| 1 | 1 | Delete/gut `commands/orchestrate/resume.md` (fictional feature) | Low | None | ☐ not started |
| 2 | 2 | Thin-shim `commands/orchestrate/plan.md` → `plan-orchestrator` skill; drop duplicate template | Low-Med | Low | ☐ not started |
| 3 | 3 (T2) | Extract shared verify-gate + engine-comparison prose into one on-demand reference | Low-Med | Low | ☐ not started |

---

## Phase 1 — Remove the fictional `resume.md`

`commands/orchestrate/resume.md` (523 lines) describes an unimplemented "session teleportation"
feature (cloud sync, AES-256, S3, team sharing) with zero code, zero skill delegation, and
references sibling commands (`:sync`, `:archive`, `:share`) that don't exist. It also collides in
name with two *real* resume mechanisms.

- [ ] 1.1 Confirm nothing depends on it: `grep -rn "orchestrate:resume\|orchestrate/resume" commands/ skills/ docs/ tests/` — expect only See-Also links + the guide.
- [ ] 1.2 Decide delete vs. gut-to-stub. **Default: delete the command file.** If discovery/tests expect the file to exist, replace its body with a 5-line stub pointing at the real mechanisms (`workflow --resume <run-id>` for cache-replay; `session-state` skill for local JSON).
- [ ] 1.3 Remove/redirect its See-Also references in `orchestrate.md`, `plan.md`, and both guide docs (`docs/guide/pipeline-orchestrate-guide.md`, `docs/guide/orchestrator.md`).
- [ ] 1.4 Run the count cascade if a command was removed: `./scripts/validate-counts.sh` (command count drops by 1 — update all surfaces it flags).

**Acceptance:** no dangling links to `orchestrate:resume`; `validate-counts.sh` green; the two
*real* resume mechanisms are the only ones a user can find.

---

## Phase 2 — Thin-shim the zombie-deprecated `plan.md`

`commands/orchestrate/plan.md` is frontmatter-marked `deprecated: true` /
`replaced-by: skills/orchestration/plan-orchestrator/` but still carries the full 8-step
spec→ORCHESTRATE→worktree logic verbatim, duplicating `plan-orchestrator/SKILL.md` — including
the ORCHESTRATE template in both files. Same pattern PR #236 fixed for `check.md` + git commands.

- [ ] 2.1 Read `skills/orchestration/plan-orchestrator/SKILL.md` and confirm it fully covers Mode 1 (Spec → ORCHESTRATE) that `plan.md` currently re-implements.
- [ ] 2.2 Replace `plan.md`'s body with a thin shim: keep frontmatter + args surface, delete the inline 8-step logic and the duplicated ORCHESTRATE template, point execution at the skill (the PR #236 shim shape is the reference).
- [ ] 2.3 Verify the ORCHESTRATE template now lives in exactly ONE place (the skill). `grep -rn "ORCHESTRATE Template\|Phase Overview" commands/orchestrate/plan.md` → should be gone.
- [ ] 2.4 Run the deprecated-command auditor: `python3 scripts/audit-deprecated-commands.py --pair commands/orchestrate/plan.md` (body-to-skill ratio should drop below threshold).

**Acceptance:** `plan.md` is a shim (no duplicate logic/template); auditor passes; guide docs
updated to note the skill is canonical (removes the "documented as live, actually deprecated"
mismatch).

---

## Phase 3 — Extract the shared verify-gate + engine-comparison prose (T2)

`orchestrate.md`, `workflow.md`, and `drive.md` each carry their own partial copy of a
"which engine when" comparison table + near-identical "real verify gate" prose. Copied into every
always-loaded command body → drift + token cost. **Token lever: progressive disclosure** (move
shared prose into one on-demand reference).

- [ ] 3.1 Create `commands/orchestrate/references/engines.md` (or a skill reference) holding ONE canonical engine-comparison table + the shared verify-gate description.
- [ ] 3.2 Replace the three copied blocks in `orchestrate.md` / `workflow.md` / `drive.md` with a one-line link to the reference.
- [ ] 3.3 While here, fix the `orchestrate.md` self-contradiction (rank 4 is NOT in this wave, so leave the engine-name/route bug alone unless it's in the same prose block — if it is, note it as a follow-up, don't fix silently).
- [ ] 3.4 Confirm the reference isn't miscounted as a skill/command: `./scripts/validate-counts.sh` + `npx markdownlint-cli2` on the new file.

**Acceptance:** one canonical engine table; three command bodies shrink; counts unaffected;
markdown clean.

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
