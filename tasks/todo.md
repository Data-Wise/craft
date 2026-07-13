# Tasks: v4.0.0 Train — Execution Checklist

> Sized S/M per the breakdown skill; every task has acceptance + verification. Plan of record:
> `docs/plans/ORCHESTRATE-folio-split.md`. Working artifact — delete from branch before final merge.
> Paths: WT = `~/.git-worktrees/craft/feature-folio-split` · FO = `~/projects/dev-tools/folio`.

## Phase 1 — folio scaffold ✅ COMPLETE (merged, see .STATUS 2026-07-10)

- [x] **T1.1** Create craft worktree + move ORCHESTRATE there — **XS** (parent git)
  - Acceptance: `feature/folio-split` off dev; ORCHESTRATE at WT root
  - Verify: `git worktree list`; `git -C WT branch --show-current`
- [x] **T1.2** `gh repo create Data-Wise/folio --public` + clone + `main`←`dev` — **S** (ASK first)
  - Acceptance: visibility PUBLIC; dev default working branch
  - Verify: `gh repo view Data-Wise/folio --json visibility`
- [x] **T1.3** folio skeleton: plugin.json (strict), dirs, CLAUDE.md w/ docs-standards contract — **S**
  - Acceptance: `npx @anthropic-ai/claude-code plugin validate .` passes
  - Verify: validate transcript · Files: FO/{.claude-plugin,CLAUDE.md,commands,agents,skills,docs,scripts,tests}
- [x] **T1.4** wf-p1-tooling: schema-owner agent first, then 4 script adapters + 1 verifier — **M**
  - Acceptance: bump-version/validate-counts/exclusions(config/)/pre-release/post-sweep green on empty surface; floors 15/6/6; SKILL.md-only keys
  - Verify: parent runs each script; VERDICT sound=true · Files: FO/scripts/*
- [x] **T1.5** Tap manifest `formulas['folio']` + generate.py support + marketplace row (entries only) — **S**
  - Acceptance: `generate.py folio` emits a valid formula locally (not pushed)
  - Verify: dry-run output · Files: homebrew-tap/generator/*, claude-plugins marketplace.json
  - ⚠️ UNVERIFIED per .STATUS 2026-07-10: fix reworked onto local-only `feature/folio-formula` in homebrew-tap, never pushed/PR'd — re-check before Phase 4.
- [x] **T1.6** Bare protection (NO contexts) + GitHub App install on folio — **S**
  - Acceptance: PR-only/no-force/no-delete; contexts []; APP_ID+APP_PRIVATE_KEY secrets set
  - Verify: `gh api .../branches/main/protection`; secrets list
  - ⚠️ UNVERIFIED per .STATUS 2026-07-10: claimed done, not yet re-confirmed with `gh secret list --repo Data-Wise/folio`.
- [x] **CP-1** (ASK): all above + record outcome in ORCHESTRATE

## Phase 2 — extraction + folio CI + choreography ✅ COMPLETE (merged, folio PR #1, 2026-07-10)

- [x] **T2.1** Build filter-repo path list FROM the disposition table; dry-run — **S** (parent)
  - Acceptance: path list = 16 command files + agents/docs + 6 skill dirs; dry-run file count matches
  - Verify: dry-run manifest vs ROSTER-*.md
- [x] **T2.2** `git filter-repo` split + graft into FO preserving authorship — **M** (parent git)
  - Acceptance: files at same relative paths; craft-era commits present
  - Verify: `git -C FO log --follow` on 3 samples
- [x] **T2.3** wf-p2-repoint pipeline (≈16 files): /craft:→/folio: + docs-standards repoint → per-file verify — **M**
  - Acceptance: zero /craft: self-refs; all VERDICT sound; parent commit per batch
  - Verify: pipeline results + parent spot-grep
- [x] **T2.4** Salvage 7 killed site cmds → site-management/navigation references/ (line-conservation diff vs 284L router); merge check-links→docs:check; demote frameworks.md — **M**
  - Acceptance: Σ-lines conserved per ADR-002; docs:check has links section/flag
  - Verify: diff audit transcript · Files: FO/skills/docs/*/references/*, FO/commands/docs/check.md
- [x] **T2.5** folio ci.yml (pytest+structure+counts, floors ~15/6/6) — **S**
  - Acceptance: actionlint clean; floors match surface
  - Verify: actionlint; first run green — 38/38 pytest, confirmed on real folio GitHub CI
- [x] **T2.6** folio homebrew-release.yml + aggregator-sync.yml (parameterized mirrors); after first green PR run: add required context to main protection — **M**
  - Acceptance: actionlint clean; protection contexts = [folio's check name] (byte-match)
  - Verify: actionlint; `gh api` protection readback
- [x] **T2.7** `/folio:hub` index + minimal folio-built docs site — **M**
  - Acceptance: hub lists ~15 cmds/6 agents/6 skills; `mkdocs build --strict` clean
  - Verify: build transcript · Files: FO/commands/hub.md, FO/mkdocs.yml, FO/docs/*
- [x] **T2.8** wf-p2-verify fan-out: counts + structure + spot-E2E (docs:tutorial equivalence) — **S**
  - Acceptance: all VERDICT sound=true — validate-counts 16/6/6, mkdocs --strict clean, git log --follow history proof
- [x] **CP-2** (ASK): folio suites green + history proof + hub → record outcome
  - ⚠️ RELEASE READINESS GAP per .STATUS 2026-07-10: folio has zero e2e/dogfood tests, only 3 stub doc pages, `plugin.json` still 0.1.0 — deliberately deferred until Phase 3 confirms folio is sole owner.

## Phase 3 — craft amputation (@69, actual landed @70/39/2)

- [x] **T3.1** `git rm` 24 leaving + deploy alias; collapse site:deploy refs in release skill to raw mkdocs shell; fix 3 STAY-skill refs — **M** (parent, WT)
  - Verify: grep clean; `test_skill_referenced_commands_exist` — commit `d76f43f0d`
  - Found + resolved mid-task (not in original plan): plan-orchestrator/brainstorm/
    brainstorm-insights all treated the now-deleted `commands/docs/sync.md` as the
    single source of truth for the doc-impact scoring rubric — inlined into
    `skills/orchestration/references/doc-impact-rubric.md` (commit `<rubric fix>`).
- [x] **T3.2** Rebuild hub DOCS section (6 staying + folio breadcrumb); do.md docs category → staying set; DELETE docs:validate phantom (322-324/468/905); drop SITE grid — **M**
  - Verify: routing dogfood trace; no dangling routes — do.md's Docs-category routing
    and docs:validate phantom fixed. `commands/hub.md`'s own 804-line ASCII catalog
    NOT rebuilt — it's separately stale (pre-dates the 94-cmd baseline) and its full
    diet is explicitly Phase 3.5 scope per ROSTER-craft-v4-disposition's own open
    question. Only the test fixtures asserting hub's *discovery* output (not the
    static markdown) were fixed.
- [x] **T3.3** Enumerated test edits: hub_integration:119 floor + layer2/3 displays; RELOCATE test_site_publish.py→folio; dist_doc_accuracy:29; discovery floors; OPT_IN — **M**
  - Verify: pytest green — full suite 2645 passed / 0 unexplained failed (3 confirmed
    pre-existing on dev, unrelated: test_v115_adhd_enhancements.py's stale workflow
    page content). 21-file stale-count sweep (94→70, 45→39) + README's 4 live claims
    (missed by bump-version.sh's file list) also fixed here.
  - Real regression found + fixed: `commands/code/demo.md`'s deprecated shim pointed
    at `skills/code/demonstration-builder/`, deleted in T3.1 — un-deprecated it
    (same treatment as site/deploy.md); it's real Phase-3.5 salvage-gate territory,
    not now.
  - Flagged, NOT fixed (genuine open question, needs a decision): `scripts/
    dependency-manager.sh` hardcodes `commands/docs/demo.md` (moved to folio) as its
    dependency source. Whole subsystem (dependency-manager.sh, tool-detector.sh,
    health-check.sh, installers/*.sh) may belong in folio now. One test skipped with
    a clear reason rather than guessing at a redesign.
- [ ] **T3.4** ci.yml:92 floor 86→60 (skills floor 26 OK) — **XS**, SAME PR
  - Verify: grep the floor; CI green on PR run

**BACKLOG (2026-07-12, user-decided, not a Phase 3 blocker):** `scripts/dependency-manager.sh`

- `tool-detector.sh` + `health-check.sh` + `installers/` (1,327 lines total) are now orphaned —
they exist only to serve `docs:demo.md`'s asciinema/vhs tooling, which moved to folio in T3.1.
Folio's copy of `demo.md` is otherwise identical, so these scripts would work there unchanged
(just the 2 `/craft:docs:demo` mentions need `/folio:` swap). Explicitly left dormant in craft
per user decision — not deleted, not migrated. `tests/test_integration_dependency_system.py`'s
one live-execution test is skip-guarded with this same reasoning. Revisit as its own dedicated
task if/when this tooling matters again.

- [x] **T3.5** wf-p3-sweep: docs-content grep-sweep for 24 leaving names (repoint→/folio: or MIGRATION) — batched disjoint agents; incl. Phase-0 follow-ups (advice strings, update.md narrative, capture-output phantom) — **M**
  - Acceptance: **grep-zero** on leaving names in docs/ (excl. archives/changelogs) — ✅ verified
  - Verify: 9-agent Workflow dispatch repointed 63 docs files; +11 orphaned mirror/tutorial pages
    deleted (mkdocs.yml nav pruned); Phase-0 follow-ups closed: `capture-craft-output.sh:27`
    phantom `/craft:site:create` fixed → `/folio:site:build`; 4 "advice string" scripts
    (`test-fix-flag.sh`, `consent-prompt.sh`, `version-check.sh`, `test-demo-check.sh`)
    repointed `/craft:docs:demo` → `/folio:docs:demo`; 2 VHS tapes + `ci/local.md`'s phantom
    `docs:validate` fixed. 1 real regression caught+fixed (`test_teaching_demo_exists` expected
    literal `/craft:site:publish`). Full suite: all pass except the 3 pre-existing `dev`-baseline
    failures in `test_v115_adhd_enhancements.py` (confirmed via direct dev-branch run).
    `mkdocs build --strict`: 0 errors.
- [x] **T3.6** Counts: bump-version.sh --counts-only @69 + validate-counts — **XS** (parent only)
  - Verify: `./scripts/validate-counts.sh` — 70/39/2 actual == 70/39/2 documented, all green
    (already satisfied by T3.1's bump-version.sh run; no drift found, no action needed)
- [x] **T3.7** MIGRATION-v4.md (all moved/killed → destinations) + breadcrumbs in README/CHANGELOG — **S**
  - Verify: `docs/MIGRATION-v4.md` created (24 cmds + 6 agents + 6 skills, each destination
    confirmed to exist in folio via direct file check); README.md + CHANGELOG.md breadcrumbs
    added; mkdocs.yml nav entry added; `mkdocs build --strict` clean.
- [x] **T3.8** Full gates: pytest + ALL bash suites + strict build + wf-p3-gate (3 refuters) — **S**
  - Verify: `python3 -m pytest tests/` → 2601 passed / 3 failed / 41 skipped (the 3 failures are
    the pre-existing `dev`-baseline `test_v115_adhd_enhancements.py` trio, confirmed by direct
    dev-branch run — 0 regressions). CI-required bash suites all green: `test_branch_guard.sh`
    (117/117), `test_branch_guard_e2e.sh` (30/30, 1 known-flaky perf test passed on rerun),
    `test_no_switch_guard.sh` (36/36), `test_git_shim_correctness.sh` (21/21),
    `test_bump_version.sh` (45/45), `test_post_release_sweep.sh` (21/21). `mkdocs build --strict`
    clean (0 errors/warnings beyond pre-existing excluded-nav INFO lines).
- [x] **CP-3** (ASK): all green @70; branch holds (no PR yet — 3.5 rides the same train)

## Phase 3.5 — v4 rider (@26)

- [x] **T3.5.1** The 12 salvage diffs (R2): dist×3, claude-md×3, check(→micro), gen-validator, git:{refcard,worktree}, code:demo, insights — unique logic → references/ — **M** (splittable per family)
  - Verify: per-diff line-conservation note in ledger
  - Progress (2026-07-12): **family 1/4 done** — dist×3 (pypi/curl-install/marketplace) salvaged
    verbatim into `skills/distribution/dist-extras/references/`, commands deleted, 2 tests
    repointed, counts synced 70->67, 17-file docs count-sweep, 1 checker exclusion added
    (README's historical "26 commands" crossed the 40%-floor as canonical shrank). Committed
    `840e57d8`. **Plan deviation**: `code:demo` was already un-deprecated in T3.1 (its skill
    moved to folio) — no longer a shim to salvage-and-kill; moved to the keep-as-is set (see
    `docs/MIGRATION-v4.md`). Remaining: claude-md×3, check(→micro)+gen-validator,
    git:{refcard,worktree}, insights.
  - Progress (2026-07-12): **family 2/4 done** — claude-md×3 (edit/sync/init) salvaged
    verbatim into `skills/docs/claude-md/references/`, commands + 4 docs-site mirror pages
    deleted, DOCS category floor 5->2, 9 broken links fixed, 8 advice-string call sites
    repointed, counts synced 67->64. Committed `ee1645d5`. Remaining:
    check(→micro)+gen-validator, git:{refcard,worktree}, insights.
  - Progress (2026-07-12): **family 3/4 done** — gen-validator (447L) salvaged verbatim into
    `skills/check/references/`, command deleted, skill re-pointed. **check.md plan
    deviation**: NOT collapsed to micro-shim — its own header + the token-efficiency
    skill's classification test justify keeping invocation-mandatory content (Step 0,
    confirm gate, --orch, CRAFT_MODE binding) in the command file; recorded in
    MIGRATION-v4.md. Counts synced 64->63. Committed `88efc1ca`. Remaining:
    git:{refcard,worktree}, insights.
  - Progress (2026-07-13): **family 4/4 done — T3.5.1 complete.** git:worktree (229L) +
    git:docs:refcard (350L) salvaged verbatim into `skills/dev/git/references/`;
    workflow:insights (176L) salvaged into `skills/workflow/brainstorm-insights/references/`.
    3 commands + 2 docs-site mirror pages deleted, mkdocs.yml nav trimmed, 12+ cross-tree
    links repointed to absolute GitHub blob URLs (mkdocs docs_dir can't resolve links
    escaping docs/ — see `cross-tree-link-resolution-commands-vs-docs` pattern), 8 test
    files repointed (test_command_enhancements_e2e, test_hub_discovery/integration/layer3,
    test_insights_improvements_dogfood/e2e, test_facet_parsing_defensive,
    test_brief_command_dogfood/e2e — the last two also dropped the now-stale "N workflow"
    plugin.json description breakdown since `commands/workflow/` is empty). Counts synced
    63->60. Committed `318be7d0`. Full pytest: 2575 passed / 4 failed (3 known dev-baseline
    - 1 expected local branch-guard.sh install-drift from this commit's own content change)
    / 43 skipped. `mkdocs build --strict` clean.
- [x] **T3.5.2** Kill 22 shims + 2 utils; demote discovery-usage → docs — **S**
  - Verify: tripwire tests; `ls commands/git/` empty
  - Progress (2026-07-13): **batch 1/2 done** — plan:sprint/roadmap + orch:plan folded into
    `plan-orchestrator` skill (Modes 3-4), code:coverage folded into `test-strategist` skill,
    2 teaching-residue utils (readme-teach-config, readme-semester-progress) deleted (no
    replacement), discovery-usage demoted to `docs/internal/DISCOVERY-ENGINE-USAGE.md`
    (was `internal: true`, never a real slash command). 60->53 commands (counts-only sync +
    2 rounds of `docs-staleness-check.sh --fix`, 57 items auto-fixed). ~35 caller refs
    repointed across docs/guide, docs/reference, docs/tutorials, skills/workflow. 3 test
    floors lowered (test_hub_discovery min_expected, test_hub_integration total>=45,
    test_teaching_documentation utility-readme check removed). Full pytest: 2575 passed /
    4 failed (3 known dev-baseline + 1 install-drift, same as T3.5.1 baseline). `mkdocs
    build --strict` clean.
  - Progress (2026-07-13): **batch 2/2 done — T3.5.2 complete.** git×7 (guard/protect/
    unprotect/status/clean/branch/protect-baseline) deleted — all fully covered by
    `skills/dev/git/SKILL.md` Operations 1/3/6/8/9/10/12 (verified before deletion; all 7
    already carried `deprecated: true`/`replaced-by: skills/dev/git/`). `commands/git/` now
    empty. 53->46 commands. Callers repointed to skill-based phrasing across CLAUDE.md,
    hub.md, docs/. Full pytest: 2575 passed / 4 failed (same known baseline). `mkdocs build
    --strict` clean.
- [x] **Phase 3.5 — CLOSED at T3.5.2** (2026-07-13, user decision). T3.5.1+T3.5.2 are the
  full scope of "salvage-gated kills of already-deprecated shims" — both landed clean at
  46 commands, tests at baseline, `mkdocs build --strict` clean. T3.5.3 (originally
  planned as part of this phase) turned out to be a materially different, riskier class
  of work — see Phase 3.6 below — and is deliberately deferred to its own properly-scoped
  phase/goal rather than rushed. **CP-3.5's original PR-at-@26 gate does not apply**; no
  PR was opened this phase (per design — @26 was never reached, @46 is the real landing
  point). Craft's command count is 46, not the original @26 target — see Phase 3.6.

## Phase 3.6 — router consolidations (deferred, not yet scoped for execution)

> Split out from Phase 3.5 (2026-07-13) after discovering all 5 target families are
> **live, non-deprecated commands** (unlike T3.5.1/T3.5.2's confirmed-redundant shims) —
> checked via `deprecated: true` frontmatter, all 5 came back negative. `orch:drive` is
> called out by name in `CLAUDE.md`'s own TL;DR as active; `plan:feature` carries a
> **locked prior decision** (`SPEC-orchestrator-consolidation-2026-07-04.md` D2,
> enforced by `tests/test_scaffold_defaults_e2e.py::test_logic_lives_in_skills_not_deprecated_commands`)
> that it was deliberately *un-deprecated* — NOT a redirect, genuine independent content.
> This means "consolidate into a router" here means real architecture design (preserve
> full argument surfaces while restructuring), not simple shim deletion. Do not execute
> under time/token pressure — needs its own grill/spec pass before implementation.

- [ ] **T3.6.0** (before any implementation) Re-grill this phase: for EACH of the 5
  families below, confirm against current repo state whether consolidation is still the
  right call (re-check `deprecated:` frontmatter, cross-reference any newer specs/ADRs,
  and specifically re-verify `plan:feature`'s D2 exclusion still holds) — do not assume
  the 2026-07-09 ROSTER's assumptions are current.
- [ ] **T3.6.1** `plan` absorbs `plan:feature` — **XS** — **LIKELY N/A**: superseded by
  the locked D2 decision (see above); `plan/feature.md` was left untouched this session.
  Re-confirm before touching.
- [ ] **T3.6.2** `orch` absorbs `orch:drive` + `orch:workflow` — **S** — drive.md (114L)
  has its own full arg surface (spec/dry-run/yes/max-turns/no-auto/agents/condition) and
  delegates to a separate `drive-engine` skill already; workflow.md (126L) not yet
  inspected. Neither carries `deprecated: true`.
- [ ] **T3.6.3** NEW `arch` router (4→router+refs) — **S** — analyze 147 · diagram 130 ·
  plan 133 · review 109 (Σ519L), none deprecated.
- [ ] **T3.6.4** NEW `code:audit` router (5→router+refs) — **M** — command-audit 131 ·
  deps-audit 170 · deps-check 88 · docs-check 248 · skill-standards 167 (Σ804L), none
  deprecated.
- [ ] **T3.6.5** NEW `ci` router (8→router+refs) — **M** — detect 292 · fix 96 ·
  generate 730 · local 219 · status 166 · triage 176 · validate 303 · watch 135
  (Σ2117L), none deprecated. Largest family — do last.
- [ ] **T3.6.6** Cascade @26 (only if T3.6.1–5 land): bump-version + hub REGEN + ci.yml
  floor→18 + MIGRATION-v4.md rows for every consolidated name — **M** (parent)
- [ ] **T3.6.7** Suites green @26 + slash-invocability spot-checks — **S**
- [ ] **CP-3.6** (ASK): craft@26 all green → ONE PR feature/folio-split→dev (leak-scan,
  evidence in body) → merge on your go. Same PR-approval-only gate as the old CP-3.5.

**To start Phase 3.6 in a future session**, use a freshly-scoped `/goal` — do NOT reuse
the old Phase-3.5 condition (it references CP-3.5/T3.5.x names that no longer map to
open work). Suggested starting point:

```
/goal tasks/todo.md on feature/folio-split shows Phase 3.6 (T3.6.0-T3.6.7) and CP-3.6
all checked off, final pytest run clean (only the 3 known dev-baseline failures),
mkdocs build --strict clean, and no PR opened — CP-3.6 stops at presenting the PR
command for my approval, not executing it
```

Worktree: `~/.git-worktrees/craft/feature-folio-split` (branch `feature/folio-split`).
Start with T3.6.0 (re-grill) before touching any files — do not assume this note's
line counts or deprecation findings are still current by the time you resume.

## Phase 4 — coordinated release

- [ ] **T4.1** Thin `/folio:do` (own commands only) — **S**
- [ ] **T4.2** Rollback runbook (BEFORE any tag): craft revert map + folio yank map — **S**
- [ ] **T4.3** folio v1.0.0: dev→main, tag, release; verify brew install + marketplace — **M** (ASK each step)
- [ ] **T4.4** craft v4.0.0: dev→main (merge-commit), tag LAST; tap/marketplace propagation — **M** (ASK each step)
- [ ] **T4.5** wf-p4-verify: both suites on main + brew audit ×2 + sites — **S**
- [ ] **CP-4**: record OUTCOME (ORCHESTRATE + .STATUS + memory); delete tasks/ from branch

## Standing per-task rules

Leak-scan before every push · ask before push/merge/release/repo-create · parent-only git ·
agents: absolute paths + never-run-git + disjoint files · commit-per-batch · counts parent-only.
