# TODO — Craft Native-First Breakup, v3.0.0 Increment

Ordered by dependency. `[ ]` open · `[~]` in progress · `[x]` done.
Full detail + acceptance criteria in `tasks/plan.md`.

## Phase 0 — Recon (read-only, on dev, no worktree)

- [x] **T0.1** grep flow-cli / atlas / ~/.claude / tutorials / marketplace for 39 dead names + 3 pilot targets
- [x] **T0.2** wrote `tasks/recon-phase0.md`: **safe-delete=24 · keep-as-alias=15** (sum=39 ✓) — recon caught real flow-cli/tutorial/homebrew breakage. Phase 1a scope revised 39→24.

## ▲ CHECKPOINT A (human) — review recon, then create the worktree

- [ ] create `feature/craft-native-first-breakup` worktree from `dev` *(human-authorized — not auto)*

## Phase 1a — Prune (worktree) ✅ (with in-build correction)

- [x] **T1a.1** `git rm` safe cmds → **deleted 21** (not 24): 3 rich-body commands
  (`git:docs:refcard`, `check:gen-validator`, `workflow:insights`) RESTORED — ADR-002 trap
  caught by `test_skill_referenced_commands_exist`. Count 115 → **94**.
- [x] **T1a.2** removed obsolete `test_git_init_command.py`(+report); fixed brittle count floors in
  `test_hub_integration.py`; repointed 3 true-shim refs in `skills/dev/git/SKILL.md` → `references/`
- [x] **T1a.3** `bump-version.sh --counts-only` synced 14 files → validate-counts GREEN (94/45/8)
- [~] **full suite** running in background to confirm no further breakage
- [ ] **HELD DECISION**: the 3 restored rich-body commands — keep-as-command, or migrate logic into
  their skills then delete? (deferred; they work as-is)

## Phase 1b — Exclude dead docs (worktree, independent of 1a)

- [ ] **T1b.1** sweep inbound links + nav membership into specs/plans/archive; fix them FIRST
- [ ] **T1b.2** extend (not overwrite) `mkdocs.yml` `exclude_docs` with the 3 dirs → `mkdocs build` + link CI green

## Phase 1c — Pilot (worktree; 4-axis gate, the routing proof)

- [ ] **T1c.1** `code:refactor` → `/simplify`: 4-axis transcript → `tasks/pilot-code-refactor.md`
- [ ] **T1c.2** `arch:review` → `/code-review`: 4-axis transcript → `tasks/pilot-arch-review.md`
- [ ] **T1c.3** `ci:generate` → `agent-skills:ci-cd-and-automation`: 4-axis transcript → `tasks/pilot-ci-generate.md`
- [ ] **T1c.4** write `tasks/routing-verdict.md` — can do/hub route cross-plugin? (gates Phase 2)

## ▲ CHECKPOINT B (human) — suite green + routing verdict → decide Phase 2

---

### Next actionable

**T0.1** — read-only, runs now on `dev`, no worktree. Everything past CHECKPOINT A needs the worktree.
