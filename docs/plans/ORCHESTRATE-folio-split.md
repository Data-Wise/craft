# folio Split — Orchestration Plan

> **Branch:** `feature/folio-split` (create when implementation starts — ORCHESTRATE-only for now)
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-folio-split` (not yet created)
> **Second repo:** `~/projects/dev-tools/folio` (NEW, **PUBLIC** — created in Phase 1)
> **Grill:** `docs/specs/GRILL-folio-split-2026-07-09.md` (B1–B5 LOCKED)
> **Execution spec:** `docs/specs/SPEC-folio-split-workflow-2026-07-09.md` (W1–W5)
> **Border filter:** `docs/specs/BRAINSTORM-folio-border-filter-2026-07-09.md` (kill/move/merge)
> **v4 rider:** `docs/specs/BRAINSTORM-craft-v4-skills-first-surface-2026-07-09.md` (Phase 3.5)
> **Status:** ✅ PHASE 0 COMPLETE + ✅ ADVERSARIALLY REVIEWED + AMENDED (2026-07-09).
> 3-lens review (UX/backend/devops): 6 blockers + 9 majors — ALL folded in below.
> Phases 1–4 NOT STARTED; no code written; no worktree/repo created.

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
| 3.5 | **v4 surface rider** — shim-kill (27) + subcommand consolidation → ~22 cmds | craft | — | P1 | High | ☐ needs roster grill |
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

## Phase 3.5: v4 Surface Rider (~22 commands) — NEEDS ROSTER GRILL FIRST

Per `BRAINSTORM-craft-v4-skills-first-surface-2026-07-09.md`: kill the 27 deprecated shims
(ADR-002 salvage gate — ~12% rich-body base rate; per-skill slash-invocability check, nested
skills excepted) · kill 2 teaching-residue utils · demote discovery-usage · subcommand
consolidation (ci 8→1, arch 4→1, code-audits 5→1, orch 3→1, plan 2→1). Re-baseline
`ci.yml:92` to `-lt 18`. **Blocked on:** the 22-roster grill + salvage list.
Same feature-branch family, same MIGRATION-v4.md, same cascade run.

---

## Phase 4: `/folio:do` + Coordinated Release (craft v4.0.0 / folio v1.0.0)

- [ ] 4.1 Thin `/folio:do` (routes folio's own commands only — no cross-plugin dispatch).
- [ ] 4.2 **Release ORDER (fixes devops-M5): folio v1.0.0 FIRST** — confirmed live +
      `brew install` verified — **then craft v4.0.0 tag LAST**. Both dev→main merge-commit.
      Ask before EACH step.
- [ ] 4.3 **Rollback runbook** (written BEFORE 4.2 executes): craft revert = delete tag +
      restore prior `Formula/craft.rb` + un-bump marketplace pin + revert merge on main;
      folio revert = yank release + tap/marketplace entry removal. Note: `release: published`
      auto-fires irreversible tap/marketplace pushes — the runbook is the undo map.
- [ ] 4.4 wf-p4-verify: both suites on main, brew audit both formulas, site checks.
- [ ] **GATE 4**: two independent plugins; neither needs the other to ship. Record OUTCOME in
      ORCHESTRATE + .STATUS + memory; delete `tasks/` from the branch before final merge.

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
