# Tasks: v4.0.0 Train — Execution Checklist

> Sized S/M per the breakdown skill; every task has acceptance + verification. Plan of record:
> `ORCHESTRATE-folio-split.md` (repo root — corrected 2026-07-16; the `docs/plans/` path this
> header used to cite doesn't exist). Working artifact — delete from branch before final merge.
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
- [x] **T3.4** ci.yml:92 floor — **DONE 2026-07-16**, resolved as floor=40 (final surface landed
  at 47 commands after Phase 3.6, not the 46 this note assumed when it was last written; 40 was
  picked as a deliberate margin below the actual count, not a mechanical mirror of it). Verified
  on disk: `ci.yml:98` reads `-lt 40`; confirmed passing in PR #290/#291/#292 CI runs. This
  checklist line was stale — corrected during the `/agent-skills:planning-and-task-breakdown`
  pass that also wrote out Phase 4 below.
  - ~~⚠️ STALE A SECOND TIME (2026-07-16).~~ This task targeted 86→60, but Phase 3.5 then cut
    the surface to **46 commands** — so `ci.yml:92`'s current floor of 60 is now *above* the
    actual count and **CI will hard-fail** ("Expected at least 60 commands, found 46"). The
    skills floor (26) is still fine — actual is 40. Picking the new number is a **decision, not
    a mechanical edit**: the floor is a mass-deletion guardrail, so it depends on whether 46 is
    the intended final v4 surface or Phase 4 moves it again. Do not guess it.

## ⛔ BRANCH PARKED (2026-07-16) — read before resuming

This branch is **not PR-ready** and was deliberately parked, not abandoned. Phase 3.6 work is
committed and safe (`204822aa`, `bbd9c3314`, `63f43ba23`, `16d34a0fe`). All Phase 3.6 gates that
*can* pass locally do: pytest **2561 passed / 4 failed** (the 4 are the documented `dev`
baseline — hook-install drift + the `test_v115` trio), `validate-counts.sh` exit 0 (46/40/2),
`mkdocs build --strict` exit 0 / zero warnings, repo-wide `category:` mismatches **0**.

**Scope reality:** `feature/folio-split → dev` is **not** a Workstream B+C PR — it is the entire
v4 train (36 commits, Phases 3 + 3.5 + 3.6), and the branch is **41 commits behind `dev`** off a
merge-base from 2026-07-09. Landing it is the gated operation this plan always intended
("branch holds — 3.5 rides the same train"), not a small follow-up.

**Three CI blockers, three unrelated causes — triaged 2026-07-16. Do NOT treat as one bucket:**

| Blocker | Cause | Fix |
|---|---|---|
| `test_branch_guard.sh` — `test_bash_git_dash_c_commit_on_main_not_caught` (expects 0, gets 2) | **Stale branch, NOT a regression.** A characterization test that encoded a known *limitation*; guard-hardening PRs #287–#289 (on `dev`) closed the gap. `dev` already renamed it `..._now_caught` expecting 2. The suite runs the **installed** hook at `$HOME/.claude/hooks/` (machine-global), not the repo copy — which is why it passes on `dev` and fails here with identical code. | Comes **free with a `dev` merge**. Edit nothing. |
| `ci.yml:92` command floor 60 vs actual 46 | The open **T3.4**, stale a second time (see above). | Needs a **user decision** on the number. |
| `test_git_shim_correctness.sh` — 7 `exists:` failures (21/21 on `dev`) | **The only true branch debt.** T3.5.2 deleted all of `commands/git/` (consolidated into `skills/dev/git/`), but this suite still asserts those 7 shims exist. Its stated purpose — catching "frontmatter claiming a migration that never happened" — is obsolete now that the migration fully happened. **A `dev` merge does NOT fix this** (`dev`'s copy also expects the files). | Update/remove the suite **+ its `ci.yml:180` line**. |

**Why pytest never caught the last one:** these are **bash** suites (`ci.yml:177–180`); pytest
does not run them. T3.5.2's verification cites "full pytest 2575 passed" as its evidence — that
is exactly the blind spot. **Run the bash suites, not just pytest, before calling this branch
green.**

**On merging `dev` in:** not a formality. This branch modified `no-switch-guard.sh`,
`install-guards.sh`, and `version-check.sh` — precisely the files `dev`'s #287–#289 hardening
touched. Expect real conflicts in the guard scripts.

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

## Phase 3.6 — router consolidations ✅ CLOSED (2026-07-16)

> **Outcome: 1 router built out of 5 planned.** Of the five router workstreams this phase
> opened with, three (`plan:feature`, `arch`, `orch`) were dropped before any code, one
> (`code:audit`) shipped shrunk from 5 commands to 2, and one (`ci`) yielded no router at
> all — only a metadata fix. Final state:
>
> | Workstream | Planned | Shipped |
> |---|---|---|
> | A — `orch` router | T3.6.2 | **dropped** (D11) — already delegates to engine skills |
> | `arch` router | T3.6.3 | **dropped** (D6) — no real duplication |
> | `plan:feature` | excluded | unchanged — D2 lock, pre-existing |
> | B — `code:audit` router | 5 commands | **shipped, 2 commands** (D12) — `204822aa` |
> | C — `ci` router | T3.6.5, 8 commands | **no router** (D13) — `bbd9c3314` metadata fix only |
>
> **Root cause of the 3 collapses (D11/D12/D13):** the original grill locked load-bearing
> decisions from line counts and flag names without reading command bodies in full. Every
> family that looked cohesive from surface metrics fell apart on a full read; the one that
> survived (`code:audit`, 2 commands) is the phase's entire real output. Each collapse was
> caught before code was written for the affected scope. **Lesson for future consolidation
> phases: read every candidate body in full before locking a router decision — line counts
> and flag names are not evidence of shared shape.**

> **Superseded 2026-07-15** by `docs/specs/GRILL-phase-3-6-router-consolidation-2026-07-15.md`
> (11 decisions, D1-D11) after the T3.6.0 re-grill this section itself called for. Full
> reasoning lives in that GRILL file — this section states the resulting task breakdown only.
> Net scope change: **2 independent workstreams/PRs, not one bundled CP-3.6 gate**; `plan:feature`
> stays excluded (D2 lock unchanged); `arch` dropped entirely (D6 — 519L/4 commands, no real
> duplication to consolidate); framed as **organizational cleanup, not command-count reduction**
> (D4 — every subcommand keeps direct slash-invocability per D3, so 46→~26 was never reachable
> this way). `orch`/`drive`/`workflow` router **dropped entirely** (D11, correction found at
> implementation start): `drive.md`/`workflow.md` turned out to already be thin command wrappers
> delegating to their own skills (`drive-engine`/`workflow-engine`) — the exact end-state the
> original plan wanted to build — and the 3 commands document genuinely distinct execution
> engines with no real duplication, same verdict as `arch` (D6). `orch.md`/`drive.md`/
> `workflow.md` are left completely untouched.

### Workstream B — code:audit router (own PR) — SHRUNK to 2 commands (D12)

> Corrected 2026-07-16: full read of all 5 bodies showed only `command-audit`+`skill-standards`
> genuinely share shape/flags (both validate craft's own frontmatter). `deps-audit`/`deps-check`/
> `docs-check` are generic cross-project tools with incompatible flag surfaces — left untouched.

- [x] **T3.6.B1** Verify `--format`/`--fix` semantics compatible across command-audit +
  skill-standards — **XS** — DONE in grill (D2): format = output rendering, fix = safe
  mechanical auto-fix, consistent across both.
- [x] **T3.6.B2** Consolidate `command-audit` + `skill-standards` shared vocabulary into
  `skills/code/audit-router/SKILL.md` + shrink both command files to thin shims (frontmatter
  unchanged, body points to the skill) — **S** — DONE `204822aa`. Both commands keep full
  frontmatter (arg surface + slash-invocability intact per D3); bodies now point at the skill.
- [x] **T3.6.B3** Salvage both bodies verbatim into `skills/code/audit-router/references/`
  (ADR-002 line-conservation diff) — **S** — DONE `204822aa`. `references/command-audit.md`
  - `references/skill-standards.md` carry the full bodies verbatim.
- [x] **T3.6.B4** Regen `commands/_cache.json` before final verification — **XS** (D9) — DONE.
- [x] **T3.6.B5** Suites green + slash-invocability spot-check on both entry points — **S** —
  DONE. Skill count cascade 39→40 required `bump-version.sh 2.61.2` **plus a manual sweep of
  10 files outside its tracked list** (README, docs/{index,architecture,commands,
  skills-agents,QUICK-START,MIGRATION-v4}.md, docs/guide/×2, docs/tutorials/×1,
  commands/dist/homebrew.md). Remaining 4 pytest failures verified pre-existing on `dev` via
  `git stash` A/B — 0 regressions.
- [ ] **CP-3.6.B** (ASK): Workstream B all green → PR `feature/folio-split`→`dev` (bundled with
  Workstream C's fixes — both are small and touch disjoint files).

**Explicitly out of scope (D12):** `deps-audit.md`, `deps-check.md`, `docs-check.md` stay
completely untouched.

### Workstream C — ci router ❌ NO ROUTER BUILT (D13, 2026-07-16)

> **Corrected 2026-07-16, same class as D11/D12.** A full read of all 8 `commands/ci/*.md`
> bodies (which the grill had only line-counted) showed the `ci` family is the most
> heterogeneous of the three — there is no shared shape to route:
>
> - `detect.md` (292L) **duplicates `skills/ci/SKILL.md`**, which already holds the real
>   `DETECTORS` list and `detect_project()` algorithm. Routing it would consolidate a copy
>   toward a skill that is already its own source of truth.
> - `triage.md` (176L) contains `classify_failure()` in a ```python block that
>   `tests/test_ci_triage_unit.py` **extracts by regex and `exec()`s** — the markdown file
>   IS the code's source of truth. Body-salvage is structurally blocked without rewriting
>   that test.
> - `generate.md` (730L) is genuinely unique — real YAML CI templates for 15+ project types.
> - `status`/`validate`/`watch` are generic doc-only commands; `fix`/`local` are thin docs.
>
> Only one real defect surfaced, and it was metadata, not structure — see T3.6.C1.

- [x] **T3.6.C1** Fix `category:` metadata mismatches — **XS** — DONE `bbd9c3314` +
  `63f43ba23`. `ci/fix.md` + `ci/local.md` declared `category: code`;
  `orch/drive.md` + `orch/workflow.md` declared `category: orchestrate` against a
  nonexistent `commands/orchestrate/` dir. All four are real defects flagged by
  `utils/help_file_validator._check_category_mismatch` (live-wired via
  `docs_update_orchestrator` → `/craft:docs:update`). A repo-wide validator sweep
  confirms **0 category mismatches remain**. The `orch` pair was pre-existing on `dev`
  and found only because the sweep was run repo-wide rather than against known files.
- [x] **T3.6.C2–C5** — **CANCELLED** (D13). No router, no salvage, no cache regen, no
  8-entry-point spot-check. All 8 `commands/ci/*.md` bodies left untouched.

**Dropped as a premise artifact (D13):** the planned `repo` flag normalization
(`status.md` short-names vs `triage.md`/`watch.md` `OWNER/NAME`). No validator enforces
flag-shape consistency across a family — this was only a "defect" relative to a shared-router
vocabulary that no longer exists. Reclassified as a documentation nit, not a bug.

**Explicitly out of scope:** `arch` router (dropped, D6) — `commands/arch/{analyze,diagram,
plan,review}.md` stay untouched. `orch`/`drive`/`workflow` router (dropped, D11) —
`commands/orch.md`, `commands/orch/{drive,workflow}.md` stay untouched. `plan` absorbing
`plan:feature` — still excluded per the pre-existing D2 lock
(`SPEC-orchestrator-consolidation-2026-07-04.md`), unchanged by this grill. No
`bump-version.sh`/`ci.yml`-floor cascade — command count is not a target of this phase (D4).

**To resume:** the 2 surviving workstreams (B, C) are independently startable — no ordering
dependency between them; C is larger (2117L vs 804L) so do it second if doing both in one
sitting. Full reasoning + all 11 locked decisions:
`docs/specs/GRILL-phase-3-6-router-consolidation-2026-07-15.md`.

Worktree: `~/.git-worktrees/craft/feature-folio-split` (branch `feature/folio-split`).

## Phase 4 — coordinated release

> **Re-grounded 2026-07-16** via `/agent-skills:planning-and-task-breakdown` — the 5-bullet
> skeleton below was written before Phase 3.6 closed and never re-checked against actual repo
> state. Direct inspection (not memory) found real gaps the skeleton didn't capture:
>
> - folio's `origin/main` is **still just the init scaffold commit** — Phase 1+2 (extraction)
>   only ever landed on `origin/dev` via PR #1 (squash, 2026-07-10). "folio v1.0.0: dev→main" is
>   a genuinely first-time operation, not a formality.
> - folio's local checkout (`~/projects/dev-tools/folio`) has a **stale `dev`** (1 behind,
>   3 ahead of `origin/dev` with local-only commits of unclear provenance) and stale `main`.
> - folio has **no `/folio:do`** yet (T4.1 literally doesn't exist as a file) — 16 command files
>   sit un-routed.
> - CP-2's own flagged release-readiness gap (zero e2e/dogfood tests, 3 stub doc pages,
>   `plugin.json` still `0.1.0`) was "deliberately deferred until Phase 3 confirms folio is sole
>   owner" — Phase 3 **is** now confirmed complete (PR #290), so this deferred work is unblocked
>   and due, but it wasn't listed as its own task anywhere.
> - `homebrew-tap`'s `feature/folio-formula` branch exists locally with **PLACEHOLDER**
>   sha256/URL values (T1.5), never pushed or PR'd — correctly sequenced *after* a real tag
>   exists, but not yet tracked as a concrete sub-step of T4.3.
> - craft's `plugin.json` is still `2.61.2` — the v4.0.0 bump (T4.4) genuinely hasn't started.
>
> **Adversarially re-checked 2026-07-16** (second pass, same skill): T4.0's "3 unexplained local
> commits" are resolved — diffed local `dev` against `origin/dev` directly and found local is
> purely *behind* (missing `scripts/aggregator-sync.sh` + a stale `counts.json`), not carrying
> divergent work. Fast-forward/reset is safe, no reconciliation judgment needed. Two more gaps
> surfaced by checking rather than reading: folio's `main` branch protection has
> `required_status_checks: None` (T2.6's "add required context after first green PR" never
> executed — `main` has never had a PR run against it) — folded as an explicit T4.3 sub-step.
> And folio's own `origin/dev` carries a leftover `tasks/session-plan-T2.4-CP2.md` working file —
> CP-4's "delete tasks/ from branch" was singular/craft-only; made explicit for both repos below.
> T4.1b was also over-bundled (tests + version bump + docs under one "M" task, realistically
> 15+ files) — split into T4.1b (tests only) and T4.1c (docs + version bump).
>
> Dependency graph: `T4.0 → T4.1 → T4.1b → T4.1c → T4.3 → T4.4 → T4.5 → CP-4`, with `T4.2`
> (rollback runbook) independent and required to complete **before** T4.3 fires (it's a pre-tag
> gate, not a parallel nice-to-have).
>
> **Open judgment call, not resolved here:** T4.2's rollback runbook doesn't yet address the
> partial-rollback case — folio ships v1.0.0 successfully, craft's v4.0.0 then fails or stalls
> for an extended period. Is that a stable, acceptable state, or does folio need some signal that
> craft hasn't caught up? Needs a human decision before T4.2 is considered complete.
>
> **`/goal`-readiness, 2026-07-16:** the prose Acceptance/Verify bullets below read fine to a
> human but don't match what `/craft:orch:drive` (the `/goal` wrapper) parses — it synthesizes a
> condition from a spec's `## Acceptance Criteria` + `## Review Checklist` H2 sections. Two real
> `docs/specs/SPEC-*.md` files were written in that exact shape, scoped to the tasks that are
> actually autonomous-loop-safe (single repo, no mid-flow human-ask gate):
>
> - **T4.1b + T4.1c** → [`SPEC-folio-phase4-tests-docs-2026-07-16.md`](../docs/specs/SPEC-folio-phase4-tests-docs-2026-07-16.md)
>   — drive from a folio worktree: `/craft:orch:drive --spec docs/specs/SPEC-folio-phase4-tests-docs-2026-07-16.md`
> - **T4.2** → [`SPEC-v4-rollback-runbook-2026-07-16.md`](../docs/specs/SPEC-v4-rollback-runbook-2026-07-16.md)
>   — drive from a craft worktree; the loop is instructed to STOP and surface the partial-rollback
>   question rather than guess an answer.
> - **T4.0** already done (T4.1 above), **T4.3/T4.4 deliberately have no SPEC** — both have
>   multiple explicit mid-flow human asks (PR/merge/tag/release ×4 for T4.3 alone), which
>   `/goal`'s autonomous turn-loop isn't a good fit for; drive those by hand per this file's own
>   Acceptance/Verify bullets, not via `/craft:orch:drive`.

- [ ] **T4.0** Sync local folio checkout to `origin` — **XS**
  - Acceptance: local `dev`/`main` match `origin/dev`/`origin/main` exactly. **Confirmed safe as
    a straight fast-forward/reset** (2026-07-16 re-check): local `dev`'s 3 commits ahead of
    `origin/dev` carry no unique work — diffed directly and found local is only missing
    `scripts/aggregator-sync.sh` (present on `origin/dev`, absent locally) plus a stale
    `counts.json`; nothing to reconcile or rebase
  - Verify: `git -C folio rev-list --left-right --count origin/dev...dev` → `0 0`;
    `git -C folio status` clean
  - Dependencies: None
  - Files: none (git state only)

- [x] **T4.1** Build `/folio:do` — thin universal dispatcher for folio's own 16 commands — **S**
  — DONE 2026-07-16, `folio` PR [#2](https://github.com/Data-Wise/folio/pull/2)
  (`feature/folio-do`, worktree `~/.git-worktrees/folio/feature-folio-do`, not yet merged —
  awaiting review/CI, then an explicit ask before merge)
  - Acceptance: routes all 16 existing `commands/**/*.md` in folio by name/intent; no
    craft-scale multi-tier router logic ported over (folio's surface is ~15 commands — a
    thin dispatcher, per the plan's own "own commands only" scope note); `plugin validate` passes
  - Verify: routing trace for each of the 16 commands (dogfood-style); `npx
    @anthropic-ai/claude-code plugin validate .` in the folio repo — **done**: flat keyword
    table (no complexity scoring/orchestration/branch-awareness ported), routing-trace check
    planted-defect verified (removed a row, check caught it), `plugin validate` shows the same
    pre-existing 1 error/2 warnings before and after (zero new findings), count-cascade bumped
    16→17 via `bump-version.sh --counts-only`, `pytest` 39/39, `validate-counts.sh` clean
  - Dependencies: T4.0
  - Files: `folio/commands/do.md` (new)

- [x] **T4.1b** Close folio's flagged CP-2 test gap — **M** — *(split 2026-07-16 from the
  original T4.1b, which bundled tests + version bump + docs under one M-sized task; realistically
  15+ files across 3 independent concerns — see the skill's own "and" red flag)*
  — DONE 2026-07-16, `folio` PR [#6](https://github.com/Data-Wise/folio/pull/6) MERGED (squash).
  Superseded PR [#3](https://github.com/Data-Wise/folio/pull/3) (closed, not merged): #3's branch
  (`feature/t4.1b-tests`, based on `feature/folio-do`) predated PR #2's merge and carried a
  redundant `do.md` diff once #2 squash-merged (squash breaks straightforward rebase — a fresh
  branch off the real post-merge `origin/dev` was cleaner than fighting it). #6's diff is test
  files only, verified clean.
  - Acceptance: e2e/dogfood test coverage exists for the 16 existing commands + the new `do.md`
    (currently just `tests/test_structure.py` — structural checks only, zero behavioral coverage)
  - Verify: folio's own pytest/test suite run, confirmed nonzero behavioral tests — **done**: 112/112
    pytest passing (up from 38), routing-trace + generic behavioral checks across all 16 commands,
    every check planted-defect verified, CI green on #6. Writing the tests surfaced and fixed 3
    real `do.md` wording gaps (generate row's baked-in aside, missing "what commands" hub
    phrasing, singular-vs-plural keyword mismatches) — landed on PR #2, not #3/#6, since that's
    where do.md's own content belongs. Also surfaced (NOT fixed here, flagged separately):
    `docs/sync.md`'s `--orch` flag cross-plugin-dispatched into `/craft:orch`, against folio's own
    CLAUDE.md — spawned as its own background task, merged independently as folio PR #4 while this
    task was still in review.
  - Dependencies: T4.1 (tests should exercise the real `do.md`, not a stub)
  - Files: `folio/tests/*`

- [x] **T4.1c** Close folio's flagged CP-2 docs + version gap — **S**
  — DONE 2026-07-16, `folio` PR [#7](https://github.com/Data-Wise/folio/pull/7) MERGED (squash).
  Reviewed before merge — review itself caught 2 real bugs, fixed in a follow-up commit before
  merging: `commands/do.md`'s own body still said "16 commands total" (stale by one, same class
  of drift as the `commands.md` header this PR fixed), and `discovery.md` mis-described
  `hub.md`'s sections (claimed 2, it actually has 4). CI re-ran green on the fix commit before merge.
  - Acceptance: `plugin.json` bumped off the placeholder `0.1.0` toward the real `1.0.0` release
    target; doc coverage extends past the 3 stub pages noted at CP-2 (16 commands currently have
    no per-command doc pages beyond the hub listing)
  - Verify: `mkdocs build --strict` if folio ships a docs site; manual page-count check — **done**:
    version bumped to `0.9.0` (pre-release marker, real `1.0.0` tag belongs to T4.3) via
    `bump-version.sh`; 3 new family pages (discovery/generate/validate, per the SPEC's "one page
    per family at minimum" scope, not per-command); `commands.md`'s stale "16" header fixed (had
    silently missed `do.md` entirely); `mkdocs build --strict` clean, pytest 112/112,
    `validate-counts.sh` clean
  - Dependencies: T4.1
  - Files: `folio/docs/*`, `folio/.claude-plugin/plugin.json`

- [x] **T4.2** Rollback runbook (BEFORE any tag) — **S**
  — DONE 2026-07-16, craft PR [#293](https://github.com/Data-Wise/craft/pull/293) MERGED (squash,
  CI green: Docs Staleness/Link Validation/Markdown Linting/Validate Plugin Structure all pass).
  `docs/RUNBOOK-v4-release-rollback.md` on `dev` now.
  - Acceptance: explicit revert maps for BOTH repos — craft: which commit/PR to revert if
    v4.0.0 is bad, how to re-point Homebrew/tap back to `2.61.2`; folio: how to yank a bad
    `v1.0.0` tag/release and unpublish from tap/marketplace. Must also cover the
    cross-repo sequencing risk this phase's own ordering creates: what state craft is left in
    if folio's release fails partway (craft must NOT tag v4.0.0 in that case)
  - ⚠️ **Open judgment call (2026-07-16) — STILL UNRESOLVED, by design:** the runbook's Path C
    states the partial-rollback question explicitly (folio ships v1.0.0, craft's v4.0.0 then
    fails/stalls — stable end-state, or does folio need a signal?) with arguments both ways, and
    instructs whoever hits the scenario to surface the question rather than guess. This satisfies
    the SPEC's acceptance criterion ("stop and report" is an acceptable outcome, not just
    "answered") — but the actual human decision is still pending whenever T4.3/T4.4 sequencing
    is executed for real.
  - Verify: a human can execute either rollback from the runbook alone, no further research —
    **done**: both paths fully commanded out (revert targets, exact `git`/`gh`/`brew` commands,
    confirm-first annotations on every destructive step); Homebrew automation detail (direct push
    to `homebrew-tap` main via GitHub App token, no PR step) confirmed by reading
    `homebrew-release.yml` rather than assumed
  - Dependencies: None — can run in parallel with T4.1/T4.1b/T4.1c
  - Files: new `docs/RUNBOOK-v4-release-rollback.md`

- [ ] **T4.3** folio v1.0.0: dev→main, tag, release; verify brew install + marketplace — **M**
  (ASK before each of: PR creation, merge, tag, GitHub release — four separate asks, not one)
  - Acceptance: **folio's `main` branch protection gets a required status check configured
    BEFORE this PR merges** — confirmed via `gh api repos/Data-Wise/folio/branches/main/
    protection` that `required_status_checks` is currently `None`; T2.6's own acceptance
    criterion ("add required context after first green PR run") was never executed because
    `main` has never had a PR run against it — this would otherwise be the first-ever merge to
    folio's `main` with zero CI gate. Then: `origin/main` merged from `origin/dev` (folio's
    FIRST real release — `main` currently has nothing but the init commit); tag `v1.0.0` on the
    release commit; GH release published; `homebrew-tap`'s `feature/folio-formula` finalized
    with REAL sha256/url (replacing the placeholder from T1.5) and merged; `brew install
    data-wise/tap/folio` succeeds; marketplace entry resolves
  - Verify: `gh api .../branches/main/protection` shows a required context before merging;
    `gh release view v1.0.0 --repo Data-Wise/folio`; `brew install` + `brew audit`;
    marketplace manifest diff
  - Dependencies: T4.1, T4.1b, T4.1c, T4.2
  - Files: `homebrew-tap` generator output, `claude-plugins` marketplace.json

- [ ] **T4.4** craft v4.0.0: dev→main (merge-commit, not squash — preserves Phase 3/3.5/3.6
  history for the tag/changelog), tag LAST; tap/marketplace propagation — **M** (ASK each step)
  - Acceptance: `plugin.json` bumped `2.61.2`→`4.0.0`; `CHANGELOG.md` AND `docs/CHANGELOG.md`
    both backfilled for the full Phase 3/3.5/3.6 arc, not just the latest PR (per this repo's
    own documented drift risk between the two files); `docs/MIGRATION-v4.md` linked from the
    release notes; tag/release only fires AFTER T4.3 confirms folio is live — that ordering is
    this phase's core constraint, not a suggestion
  - Verify: `gh release view v4.0.0`; CI green on `main`; Homebrew formula + tap sync
  - Dependencies: T4.3 (hard ordering constraint — folio must be live first)
  - Files: `.claude-plugin/plugin.json`, `CHANGELOG.md`, `docs/CHANGELOG.md`, `homebrew-tap`

- [ ] **T4.5** wf-p4-verify: both suites on main + brew audit ×2 + sites — **S**
  - Acceptance: craft's full pytest+bash suites green on `main` (not just `dev`); folio's suite
    green on its `main`; `brew audit` clean for both formulas; both docs sites build+deploy
  - Verify: CI transcripts for both repos' `main` branch runs
  - Dependencies: T4.4

- [ ] **CP-4**: record OUTCOME (ORCHESTRATE + .STATUS + memory); delete `tasks/` from **both**
  repos' branches before final merge — confirmed 2026-07-16 that folio's own `origin/dev`
  already carries a leftover `tasks/session-plan-T2.4-CP2.md`, so this isn't craft-only cleanup
  as the original single-line wording implied
  - Dependencies: T4.5

### Checkpoint: Before starting Phase 4

- [ ] T4.0 confirms folio local state actually matches `origin` (currently does NOT)
- [ ] Human has reviewed this breakdown — every ASK-gated step in T4.3/T4.4 still needs its own
  explicit go-ahead when reached; this checkpoint is not blanket authorization

## Standing per-task rules

Leak-scan before every push · ask before push/merge/release/repo-create · parent-only git ·
agents: absolute paths + never-run-git + disjoint files · commit-per-batch · counts parent-only.
