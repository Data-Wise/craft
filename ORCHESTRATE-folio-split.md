# folio Split — Orchestration Plan

> **STATUS: ✅ SHIPPED 2026-07-16 — all 4 phases complete.** craft v4.0.0 + folio v1.0.0 both
> released (see `.STATUS` for the authoritative outcome record). This file is now a historical
> plan-of-record, not a live tracker — the `tasks/todo.md` referenced below was deleted as part
> of the CP-4 post-release cleanup (its content is fully superseded by `.STATUS`).

> **Branch:** `feature/folio-split` (merged and removed — worktree cleaned up post-release)
> **Base:** `dev`
> **Second repo:** `~/projects/dev-tools/folio` (PUBLIC, released as v1.0.0)
> **Grill:** `docs/specs/GRILL-folio-split-2026-07-09.md` (B1–B5 LOCKED)
> **Execution spec:** `docs/specs/SPEC-folio-split-workflow-2026-07-09.md` (W1–W5)
> **Border filter:** `docs/specs/BRAINSTORM-folio-border-filter-2026-07-09.md` (kill/move/merge)
> **v4 rider:** `docs/specs/BRAINSTORM-craft-v4-skills-first-surface-2026-07-09.md` (Phase 3.5)

> **This is a NEW initiative.** Supersedes the dropped Phase 3 of
> `ORCHESTRATE-craft-native-first-breakup.md` (CLOSED). The cross-plugin router wall is a
> designed-around constraint (B2, B3), not a premise.

## Objective

Extract craft's docs-authoring surface into a standalone, reusable, **public** `folio` plugin;
craft keeps workflow-core + release + git. Caller-based cut (B2) + border filter: a command
stays iff craft-core calls it; already-deprecated commands **die at the border** (never pay
extraction cost for something you'd delete in v1.1). craft lands at **69** commands post-split
(→ **~22** after the v4 Phase 3.5 rider); folio launches at **≈15** commands + 6 agents +
6 skills.

## Phase Overview

| Phase | Increment | Repo | Version | Priority | Effort | Status |
|-------|-----------|------|---------|----------|--------|--------|
| 0 | Caller-audit — stays/moves partition (read-only) | craft | — | P0 | Low | ✅ 2026-07-09 |
| 1 | folio scaffold (PUBLIC) + contracts + tooling | folio | folio v0.1.0 | P0 | Med | ☐ |
| 2 | filter-repo extraction + repoint + folio CI + **release choreography** + `/folio:hub` | folio | v1.0.0-rc | P0 | High | ☐ |
| 3 | craft amputation + border kills + **docs-content sweep** + CI-floor edits | craft | (pre-v4) | P0 | High | ☐ |
| 3.5 | **v4 surface rider** — shim-kill (27) + subcommand consolidation → ~22 cmds | craft | — | P1 | High | ✅ CLOSED @46 2026-07-13 (T3.5.1+T3.5.2 only — see `tasks/todo.md`) |
| 3.6 | Router consolidations — organizational, NOT a count target | craft | — | P2 | Med | ✅ CLOSED 2026-07-16 — **1 router of 5 planned**: code:audit shipped (2 cmds, `204822aa`); orch/arch/ci all dropped on full-body reads; ci yielded a metadata fix only (`bbd9c3314`+`63f43ba23`). See `tasks/todo.md` + GRILL D11/D12/D13 |
| 4 | folio `/folio:do` + coordinated release (**folio first, craft tag LAST**) | both | craft v4.0.0 / folio v1.0.0 | P0 | Med | ☐ |

> **Gating:** each phase exits only on its gate (transcripts, adversarial verifier sound=true,
> and a human AskUserQuestion). P2/P3 are NOT parallelizable (P3 deletes what P2 must first
> prove works in folio).

---

## Phase 0: Caller-Audit ✅ COMPLETE (read-only)

Ran 2026-07-09 as dynamic Workflow `wf_bf0549a1` (7 agents: 5 region-audits → synthesize →
adversarial verify). Verdict: **`partition_sound: true`, 0 misclassified, 30/30 coverage.**
Release-path safety proven: `docs:update --post-merge` is INLINE logic (`update.md:379–500`),
not an orchestration of moved subcommands.

### Final partition (Phase 0 + border filter + review fixes B4/B5)

- **STAYS in craft (6):** `docs:update` · `docs:changelog` · `docs:claude-md:{sync, init, edit}`
  (**trio RESOLVED: stays as one unit** — craft-internal CLAUDE.md governance; fixes review B5)
  · `site:deploy` → collapses to raw `mkdocs build --strict && mkdocs gh-deploy` (alias deleted).
- **MOVES to folio (15):** `docs:{api, check, demo, generate, guide, help, lint, mermaid,
  prompt, quickstart, site, sync, tutorial, website, workflow}` — with `docs:check-links`
  **merged into `docs:check`** in transit (16th body, 15 commands land).
- **KILLED at the border (7):** `site:{build, check, progress, publish, status, update}` +
  `docs:nav-update` — all already `deprecated: true`, `replaced-by:` skills that move anyway.
  ADR-002 salvage REQUIRED: `site-management/SKILL.md` is a 284-line router with NO
  `references/` vs ~80KB of bodies — salvage before deletion. `site:progress` = teaching
  residue, pure kill.
- **DEMOTED (1):** `site:docs:frameworks` → folio skill reference (doc, not a command).
- **Agents (6) all MOVE:** api-documenter, demo-engineer, docs-architect, mermaid-expert,
  reference-builder, tutorial-engineer.
- **Skills: 6 MOVE** (doc-classifier, mermaid-linter, navigation, site-management,
  openapi-spec-generation, `skills/code/demonstration-builder`) · **3 STAY** (
  architecture-decision-records, claude-md, changelog-automation — live craft callers verified).
- **Arithmetic (fixes B4):** craft = 94 − 24 leaving − 1 deploy alias = **69**. folio = **15**.
  (The earlier "~64/~28" was unreachable — corrected.)
- **Non-blocking follow-ups → Phase 3 tasks:** do.md docs-category routing (incl. the
  `docs:validate` PHANTOM at do.md:322-324/468/905 — delete it) · ~6 stale `docs:demo` advice
  strings in scripts · `update.md` "Orchestrates these commands" narrative · `site:create`
  phantom in capture-craft-output.sh.

---

## Phase 1: folio Scaffold + Contracts (folio v0.1.0)

- [ ] 1.1 Create `~/projects/dev-tools/folio` — **`gh repo create Data-Wise/folio --public`
      (explicit: gh defaults to private; private folio would bill the zero-CI'd account pool —
      load-bearing)**. Multi-branch `main` ← `dev` ← `feature/*`. Skeleton: strict
      `plugin.json`, `commands/ agents/ skills/ docs/ scripts/ tests/`, `CLAUDE.md`.
- [ ] 1.2 **docs-standards contract** in `folio/CLAUDE.md`: path convention to
      `~/projects/dev-tools/docs-standards` + documented fallback when absent (no submodule).
- [ ] 1.3 **Duplicate count tooling (B4)** — one agent owns the SHARED CATEGORY SCHEMA first
      (the scripts share `formatting.sh` + `bump-version-helper.py` + one label set), then
      adapt: `bump-version.sh`, `validate-counts.sh`, `scripts/config/exclusions.txt`
      (correct path), `pre-release-check.sh`, `post-release-sweep.sh`. Floors tuned to folio's
      ~15/6/6 surface. validate-counts keys on SKILL.md-only.
- [ ] 1.4 Tap/marketplace generator inputs: add `formulas['folio']` to
      `homebrew-tap/generator/manifest.json` + `generate.py` folio support + folio row in the
      aggregator `marketplace.json` (entries only, not yet published).
- [ ] 1.5 **Bare protection only** (fixes bootstrap deadlock): PR-only main, 0 reviews, no
      force-push/deletions — **NO required status contexts yet** (a context that doesn't exist
      blocks every PR forever). Required check added in 2.4 after first green run. `dev` stays
      GitHub-unprotected (local branch-guard).
- [ ] 1.6 Install the Data-Wise GitHub App on folio (`APP_ID`/`APP_PRIVATE_KEY` secrets) —
      prerequisite for 2.4's release workflows.
- [ ] **GATE 1** (ask): repo PUBLIC (verified via `gh repo view --json visibility`) + plugin
      validates + count scripts green on empty surface + App installed.

---

## Phase 2: Extraction + folio CI + Release Choreography (folio v1.0.0-rc)

- [ ] 2.1 **`git filter-repo`** (fixes B1 — `subtree split` takes ONE prefix, no exclusions;
      cannot express this scattered set) with one `--path` per moving root: the 15+1 command
      files, `agents/docs/`, the 6 skill dirs. Exclusions handled by not listing them. Graft
      into folio preserving authorship. Parent-only git (W2).
- [ ] 2.2 wf-p2-repoint: `pipeline(movedFiles)` — rewrite `/craft:`→`/folio:` self-refs +
      docs-standards repoint → per-file adversarial verify. **Checkpoint discipline: parent
      commits after each completed pipeline batch** (fixes dirty-tree recovery —
      `resumeFromRunId` restores agent state, never git state).
- [ ] 2.3 Merge `check-links` body into `docs:check` (flag/section); salvage the 7 killed
      commands' rich bodies → `skills/docs/site-management/references/` +
      `navigation/references/` (ADR-002 line-conservation diff against the 284-line router);
      fold `frameworks.md` into references.
- [ ] 2.4 **folio CI + release choreography** (fixes B3): author `ci.yml` (pytest + structure
      + counts — **floors retuned to ~15/6/6, NOT craft's `-lt 86/-lt 26`**),
      `homebrew-release.yml`, `aggregator-sync.yml` (mirror craft's, folio-parameterized).
      After the first green run on a PR: add the required status context to main protection
      (completes 1.5).
- [ ] 2.5 **`/folio:hub` ships HERE** (fixes UX-F3 — discovery ships with the surface, not in
      Phase 4): index of folio's ~15 commands + skills.
- [ ] 2.6 wf-p2-verify fan-out: counts + structure + spot-E2E (`/folio:docs:tutorial`
      equivalent output) + history proof.
- [ ] **GATE 2** (ask): folio suites green · `git log --follow` shows craft-era history on ≥3
      sampled files · hub present · release workflows actionlint-clean.

---

## Phase 3: craft Amputation (pre-v4, BREAKING — lands only with Phase 3.5 + 4 in the v4.0.0 train)

- [ ] 3.1 Parent (worktree): `git rm` the 24 leaving commands + the deploy alias; collapse
      `site:deploy` refs in `skills/release/` + `references/pipeline-steps.md` to the raw
      shell; delete the 3 STAY-skill references to killed commands.
- [ ] 3.2 Routing (fixes UX-F4/F5): **REBUILD** hub.md's DOCS section to the 6 staying
      commands + one breadcrumb line "docs authoring → folio (see MIGRATION-v4.md)" — NOT a
      blanket drop. do.md: docs category → staying set only; DELETE the `docs:validate`
      phantom (322-324, 468, 905); drop SITE grid.
- [ ] 3.3 **Enumerated test-breakage set** (fixes backend-M6 — the git-shim suite is
      UNAFFECTED): `tests/test_hub_integration.py:119` (`docs >= 19` → new floor) + its
      layer2/3 hardcoded `/craft:site:*`/`docs:sync` displays · `tests/test_site_publish.py`
      → RELOCATES to folio (Phase 2.4), not floor-edited · `tests/test_dist_doc_accuracy.py:29`
      (drop moved `docs/quickstart.md` from scan) · discovery floors · OPT_IN lists.
- [ ] 3.4 **`.github/workflows/ci.yml` floors in the SAME PR** (fixes devops-B2 — the
      required check hard-fails otherwise): `ci.yml:92` `-lt 86` → `-lt 60` (craft@69 passes;
      Phase 3.5 re-baselines to ~18 with the roster) · `ci.yml:101` skills floor OK at 26
      (craft keeps 39).
- [ ] 3.5 **Docs-content sweep** (fixes UX-B6 — the false-green gate): grep-sweep ALL of
      `docs/` for refs to the 24 leaving commands (precedent: 21 commands = 264 refs / 40
      files) → repoint to `/folio:*` or MIGRATION-v4. **Gate = grep-zero on the leaving-set
      names (excluding archives/changelogs), NOT `mkdocs --strict`** (strict can't see prose).
      Includes the Phase 0 follow-ups (stale advice strings, update.md narrative,
      capture-craft-output phantom).
- [ ] 3.6 Counts: parent runs `bump-version.sh --counts-only` + `validate-counts.sh` at 69
      (fixes backend-M5 — agents NEVER touch counts; wf-p3-sweep agents get only disjoint
      non-count files from 3.5's list).
- [ ] 3.7 `MIGRATION-v4.md` (every moved/killed command → its folio home or skill) +
      **breadcrumbs**: link it from README + CHANGELOG (fixes UX-F2).
- [ ] 3.8 Full gates: pytest + ALL Validate-Plugin-Structure bash suites + `mkdocs build
      --strict` + the 3.5 grep-zero + wf-p3-gate (3 adversarial verifiers on the "craft builds
      its own site" evidence).
- [ ] **GATE 3** (ask): all green at 69 → but the PR holds for the 3.5 rider (one breaking
      train).

## Phase 3.5: v4 Surface Rider (26 commands) — ✅ ROSTER GRILLED + LOCKED

Roster locked 2026-07-09: `GRILL-craft-v4-roster-2026-07-09.md` (R1–R4) + full disposition
table `ROSTER-craft-v4-disposition-2026-07-09.md`. **18 keep + 5 micro-shims (next, done,
refine, brainstorm, check) + 3 new routers (ci, arch, code:audit) = 26.**

- [ ] 3.5.1 The **12 salvage diffs** (R2 gate: every dying shim >150L, body-vs-skill →
      unique logic into `references/` first): dist:{pypi, marketplace, curl-install},
      claude-md trio, check (315L→micro-shim), check:gen-validator, git:{docs:refcard,
      worktree}, code:demo, workflow:insights.
- [ ] 3.5.2 Kill 22 shims + 2 teaching utils; demote discovery-usage → docs page.
- [ ] 3.5.3 The 5 consolidations (R3 shape: ~60L router + verbatim bodies →
      `skills/<x>/references/<sub>.md`, ADR-002 line-conservation diff each):
      ci(8), arch(4), code:audit(5) new; orch absorbs drive+workflow; plan absorbs feature.
- [ ] 3.5.4 Cascade: `bump-version.sh --counts-only` at 26 · **hub.md regenerated against the
      26** · `ci.yml:92` re-baselined `-lt 18` · MIGRATION-v4 rows for every killed/
      consolidated name.
- [ ] 3.5.5 Suites (pytest + bash) green at 26; per-skill slash-invocability spot-checks for
      the killed shims' skills (nested skills excepted — keep micro-shim if not invocable).

Same feature-branch family, same MIGRATION-v4.md, same v4.0.0 train. Tolerance ±2 with
ledger-recorded deviations.

---

## Phase 4: `/folio:do` + Coordinated Release (craft v4.0.0 / folio v1.0.0)

> **Re-grounded 2026-07-16** — verified directly against both repos' actual state (not this
> doc's own prior claims) before resuming: folio's `origin/main` is still the single init-scaffold
> commit (Phase 1+2 only ever landed on `origin/dev` via PR #1) — 4.2's "folio v1.0.0 FIRST" is a
> first-ever dev→main for that repo, not routine. `/folio:do` (4.1) doesn't exist as a file yet.
> CP-2's flagged release-readiness gap (zero e2e/dogfood tests, `plugin.json` still `0.1.0`) was
> never turned into a tracked task here — it's due now that Phase 3 is confirmed complete. Full
> re-grounded task breakdown (acceptance + verification per task, corrected dependency order):
> `tasks/todo.md` Phase 4 + `tasks/plan.md`'s P4 dependency graph.
>
> **Adversarially re-checked, same day, second pass:** folio's `main` branch protection has
> `required_status_checks: None` (confirmed via `gh api`, not assumed) — 4.2's "confirmed live"
> release step needs a status-check configured first, since `main` has never had a PR run
> against it. folio's own `tasks/` dir already has leftover cruft (not just craft's) — GATE 4's
> cleanup line covers both repos now. The rollback runbook (4.3) still has no answer for a
> partial rollback (folio ships, craft's release then stalls) — open, unresolved.

- [x] 4.1 Thin `/folio:do` (routes folio's own commands only — no cross-plugin dispatch) — DONE
      2026-07-16: folio PR #2 (`do.md`), #6 (tests), #7 (docs+version), all merged. Corrected
      task numbering + full acceptance/verification: `tasks/todo.md` T4.1/T4.1b/T4.1c.
- [x] 4.2 **Release ORDER (fixes devops-M5): folio v1.0.0 FIRST** — DONE 2026-07-16. folio
      v1.0.0 released first (after a premature-tag mistake was caught by
      `pre-release-check.sh` before any Homebrew damage, deleted, and redone properly with
      the real version bump + CHANGELOG); `brew install`/`brew audit` verified clean. craft
      v4.0.0 tagged LAST (PR #294 dev→main, tag+release, `homebrew-release.yml` 3/3 jobs
      green, `brew audit`/`brew upgrade` verified clean). Every merge/tag/release step asked
      first, per plan.
- [x] 4.3 **Rollback runbook** (written BEFORE 4.2 executes) — DONE 2026-07-16, craft PR
      [#293](https://github.com/Data-Wise/craft/pull/293) MERGED:
      `docs/RUNBOOK-v4-release-rollback.md`. craft revert = revert PR on `main` + restore prior
      `Formula/craft.rb` (url+sha256) + annotate (not delete) the release; folio revert = delete
      release/tag (its first-ever release, no prior version to fall back to) + remove
      `Formula/folio.rb` entirely + unpublish marketplace entry. The partial-rollback question
      (folio ships, craft stalls) is stated explicitly as unresolved — the runbook instructs
      surfacing it, not guessing.
- [x] 4.4 wf-p4-verify — DONE 2026-07-16: both `main`s green (craft 5/5 workflows post-merge;
      folio 2/2 Folio CI runs); `brew audit` clean for both formulas; craft's docs site
      (Deploy Documentation workflow) confirmed green. Folio has no separate docs-site
      workflow of its own. Folio's Aggregator Sync fails BY DESIGN — it's a new plugin never
      added to the shared Data-Wise aggregator's `marketplace.json`, and
      `aggregator-sync.sh` deliberately refuses to silently add unknown plugins (a separate,
      reviewed decision, not part of this release train).
- [x] **GATE 4** — DONE 2026-07-16. Two independent plugins shipped; neither needed the
      other. Outcome recorded in `.STATUS` (milestone entry), ORCHESTRATE (this file), and
      session memory. `tasks/` deleted: craft's (`plan.md`/`todo.md`/`filter-repo-paths.txt`)
      direct-committed to `dev` (unprotected); folio's (`tasks/session-plan-T2.4-CP2.md`) via
      PRs [#15](https://github.com/Data-Wise/folio/pull/15) (dev) and
      [#16](https://github.com/Data-Wise/folio/pull/16) (main) — a direct-branch delete was
      blocked by the permission classifier, so a small reviewable PR was used instead.

**Known follow-up, not part of this train**: `docs/REFCARD.md` has the same staleness
pattern found in `commands/hub.md` during this release's docs sweep (stale per-category
subtotals, 20+ examples for `/craft:git:worktree` which no longer exists as a command) —
flagged during the T4.4 docs pass, not yet fixed.

---

## Friction Prevention

- Verify CWD/branch before any git op; two repos in play — path confusion is the top risk.
- No feature code on `dev`; Phases 1+ require the worktree.
- **Parent-only git; agents get absolute paths + "never run git"; no `isolation:'worktree'`.**
- **Commit-per-completed-batch** during any mutating Workflow (dirty-tree recovery).
- pytest ≠ bash suites — BOTH at every craft gate; **ci.yml floors are part of the change set**.
- Counts: bump-version.sh only, run per repo; agents never touch counts.
- ADR-002 salvage before every deletion (border kills AND 3.5 shim-kills).
- Push dev before PRing off it (squash-folds trap).

## Acceptance Criteria

- [ ] Partition + border filter executed exactly (6 stay / 15 move / 7 kill / 1 demote / 1 merge).
- [ ] folio PUBLIC, protected (bare→check after green), App installed, release choreography live.
- [ ] History preserved (`git log --follow` on ≥3 moved files).
- [ ] craft @ 69 post-P3: pytest + bash + strict build + **grep-zero docs sweep** all green.
- [ ] Phase 3.5 roster grilled + executed → craft @ ~22; `ci.yml` floor re-baselined.
- [ ] MIGRATION-v4.md complete + breadcrumbed from README/CHANGELOG/hub.
- [ ] folio v1.0.0 live FIRST, craft v4.0.0 LAST; rollback runbook written before either.
- [ ] Subagent spend within the W5 envelope (report actuals per phase).

## Verification

```bash
# craft (worktree absolute path)
python3 -m pytest tests/ && bash tests/test_git_shim_correctness.sh   # + other bash suites
./scripts/validate-counts.sh && mkdocs build --strict
grep -rn '<leaving-command-names>' docs/ --include='*.md'              # Phase 3.5 gate: ZERO hits
# folio
python3 -m pytest tests/ && ./scripts/validate-counts.sh && mkdocs build --strict
git log --follow <moved-file>
actionlint .github/workflows/*.yml
```

## Session Instructions

**ORCHESTRATE-only** — no worktree, no folio repo yet. When ready:

```bash
git worktree add ~/.git-worktrees/craft/feature-folio-split -b feature/folio-split dev
# move this file to the worktree root, then start Phase 1 (Phase 0 is done).
```

**Blocked-on before Phase 3.5: the 22-roster grill.** Phases 1–3 can start now.
