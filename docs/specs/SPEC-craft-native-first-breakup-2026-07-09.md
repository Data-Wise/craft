---
title: "SPEC — Craft Native-First Breakup (craft + folio)"
date: 2026-07-09
status: partial — Phase 1 shipped; Phases 2–3 dropped (premise refuted)
type: spec
supersedes: GRILL-craft-refactor-2026-07-09.md (consolidates its 7 branches + 4 new)
source: docs/ideas/craft-refactor-proposal.html (Reviews #1, #2, Proposal v2)
next: /craft:plan tier 4 → ORCHESTRATE-craft-native-first-breakup.md
---

> ## ⏹ OUTCOME (2026-07-09) — native-first thinning REFUTED; ship Phase 1 only
>
> A Stage-2 workflow empirically tested the native-first premise (3 pilots + 4-axis
> gate + cross-plugin routing test). **Result: NO-GO on Phase 2**, two independent blockers:
>
> 1. **The `do`/`hub` router structurally cannot dispatch cross-plugin** — it routes only
>    craft's own commands + own skills (`guard:audit`/`insights:apply`); no path to native
>    (`/simplify`) or third-party (`agent-skills:*`) skills.
> 2. **3/3 pilots = thin-keep, none thin-route** — the "better plugin" replacements aren't
>    ≥ craft on all 4 axes: native reviewers/refactor are weaker or auto-apply; the complete
>    matches are third-party; `ci:generate` fails 4/4 (craft ships 11 language templates, the
>    skill generates nothing). Delegating also loses craft's ADHD UX.
>
> **The "craft reinvents worse wheels" hypothesis was tested and refuted for these commands** —
> craft's dev-ops commands are better-tuned than the generic alternatives. The 4-axis gate did
> its job: it stopped deletion of working, superior functionality.
>
> **SHIPPED (v3.0.0 increment, feature/craft-native-first-breakup):**
>
> - Phase 1a — pruned 21 dead-namespace commands (115→94); 3 rich-body held per ADR-002.
> - Phase 1b — dead docs (specs/plans/archive) excluded from built site.
>
> **DROPPED:** Phase 2 (cascade thinning — premise refuted); Phase 3 folio split (rationale
> was partly native-first; any revisit must stand purely on docs-maintenance merits, grilled fresh).

# SPEC — Craft Native-First Breakup

Consolidates the idea-refine ideation, two adversarial reviews, an advisor pass,
a sibling-repo probe, and **11 grilled decision branches** into one plannable
spec. Convergent output of the grill spine, ready for `/craft:plan`.

## 1. Problem & Intent

Craft has overgrown to **115 commands / 45 skills / 135K doc-lines** — a ~10×
outlier vs typical Claude plugins and 3–6× its own siblings. The author's intent:

- Streamline the workflow using **(1) Claude Code's own ever-evolving
  skills/features FIRST**, and **(2) best-of-breed plugins** for what Claude lacks.
- **Stop maintaining one large, doc-heavy plugin.** Breaking up is acceptable —
  **split by workflow.**

## 2. Locked Decisions (grilled)

### Structure (given by the author)

- **2 plugins**, not 3:
  - **`craft`** — native-first *workflow core*: router (`do`/`hub`/`smart-help`),
    ADHD ergonomics (`brief`/`recap`/`next`/`done`/`stuck`/`focus`),
    `grill`/`brainstorm` planning pair, thin `orch` wrapper, **git + branch
    protection** (branch-guard, no-switch-guard, worktree) folded in, modes.
  - **`folio`** — *everything shipped*: docs/site/website/tutorial/quickstart/
    refcard/mermaid/api/changelog authoring pipeline **+ distribution**
    (homebrew, tap sync, surfaces, marketplace, pypi). See **B1**.
- **Sequence:** thin-first → prune → split. "Split thin, not fat."
- **Through-line gate:** *verify the replacement before deleting the original.*

### From Review #1 (deprecated-command prune)

- **R1-B1** — Drop deprecated in two lanes: **39 dead-namespace commands now**
  (`git/`15 + `workflow/`5 + `task/`3 + `check/`1 + `site/`'s 15 deprecated,
  **keeping site's 1 live**); **17 deprecated-in-live-namespaces** get a
  **verified per-command second pass**. "EFFORT: LOW" badge corrected.
- **R1-B2** — Docs: **exclude `docs/specs`, `docs/plans`, `docs/archive` from the
  built mkdocs site** (`exclude_docs`), keep dirs in-repo as live capture
  targets. **No retention rule** *(dropped by C2)* — excluded dirs cost nothing
  in the build regardless of age; keep everything in git forever.
- **R1-B3** — Success metric = **files-touched-per-release, count cascade (30→1), built-page count**, NOT raw doc line-count.
- **R1-B4** — `docs/commands/` (84 pages): **content-audit before generating**;
  generate only thin mirrors, hand-keep content-rich pages.
- **R1-B5** — *(superseded)* the earlier "cut all splitting" is overridden by the
  author's value-function change (§1); the 2-plugin split is now in scope.
- **R1-B6** — Before `exclude_docs`: **sweep inbound links + per-file nav
  membership**, fix them, then exclude (no red link-validation CI).
- **R1-B7** — Before any command removal: **grep flow-cli, atlas, `~/.claude`,
  shell history, tutorials, marketplace** for the names; anything with a live
  external caller stays a thin alias one more cycle.

### From the native-first grill (this pass)

- **B1 — folio owns docs-publishing** *(refined by C1 below)*. `folio` = docs
  authoring + site publishing + refcard + marketplace curation. Seam: `craft` =
  *how I work* (interactive); `folio` = *what I publish for reading*.
- **B2 — Verification bar = 4-axis head-to-head on ≥1 real task.** Before
  retiring a Tier-A command to a native/plugin route, the replacement must be
  **≥ craft on all four axes**: (a) output quality, (b) switching/re-wiring
  cost, (c) dependency risk (agent-skills is third-party `addy-agent-skills`),
  (d) UX consistency. **Fail any axis → deprecate-in-place (thin-kept), do not
  delete.**
- **B3 — Rollout = pilot 2–3, then cascade.** v3.0.0 thins 2–3 representative
  commands (e.g. `code:refactor`→`/simplify`, `arch:review`→`/code-review`,
  `ci:generate`→`agent-skills:ci-cd-and-automation`), runs the B2 gate, measures
  real doc-shed, and **proves cross-plugin routing (adverse bite #4)** cheaply.
  Cascade the rest in v3.1+.
- **B4 — folio extracted LAST, history-preserving.** After pilot thinning proves
  out, extract via `git subtree`/`filter-repo` (preserve blame on 135K doc lines
  plus publishing scripts). craft takes a major bump when docs-publishing leaves;
  folio starts v1.0.0; migration guide maps moved commands + marketplace entries.

### Second grill pass — open-question resolution (this session)

- **C1 — Distribution split by coupling** *(refines B1)*. Distribution is two
  things: **generic release-ops** (bump, changelog, homebrew formula-gen,
  tap-sync — ships *any* plugin incl. craft itself) → **stays in `craft`**; and
  **docs-publishing** (site deploy, refcard, marketplace curation) → **`folio`**.
  Rationale: a plugin must ship itself without a runtime dependency on a sibling
  (monorepo is dead). "Release-ops = workflow (craft); doc-publishing = artifact
  (folio)."
- **C2 — No retention rule.** Just `exclude_docs` the 3 dirs wholesale; keep
  everything in git. The "prune > N months" idea was over-engineering — excluded
  files already cost nothing in the built site. (Amends R1-B2.)
- **C3 — Name stays `folio`.** With release-ops moved back to craft (C1), folio
  is docs-publishing again — "folio" (a leaf/page, a book format) fits. No
  rename. Dodges `scribe` (existing project) + `commit-*` (existing plugin).

## 3. Design Law — Native-First

Build nothing Claude already has. Every Tier-A command becomes a **thin route**,
subject to the B2 gate:

| craft today | Route to | Verdict |
|---|---|---|
| orchestration (`orch`, orchestrator-v2) | native Workflow + Agent tools | thin-wrap; delete agent |
| planning (`plan`, `arch:plan`) | native Plan mode / agent-skills:plan / feature-dev | route |
| TDD/tests (`test`, `test-gen`) | agent-skills TDD, test-engineer | route |
| code review (`arch:review`) | native `/code-review`,`/review`,`/security-review`; coderabbit | route |
| CI (`ci/*`) | agent-skills:ci-cd-and-automation | route |
| refactor (`code/refactor`) | native `/simplify`; code-simplifier | route |
| debug (`code/debug`) | agent-skills:debugging | route |
| task tracking | native TodoWrite/TaskCreate | drop craft's |
| verify | native `verify` skill | route |
| **ergonomics, grill, router** | — | **craft BUILDS (soul)** |
| **git guards, worktree** | native hooks = mechanism | **craft BUILDS** |
| **docs/site/refcard + distribution** | partial native docs agents | **folio BUILDS** |

**The docs win comes from thinness, not the split.** A router needs few docs.

## 4. Phased Plan

| Phase | Version | Content | Reversible? |
|---|---|---|---|
| **0. External-caller grep** (R1-B7) | pre-work | grep ecosystem for all removed/thinned names; mark keep-as-alias set | read-only |
| **1. Prune + Pilot** | **v3.0.0** | delete 39 dead-namespace cmds; exclude dead docs from built site (after R1-B6 link sweep); pilot-thin 2–3 Tier-A cmds through the B2 gate | mostly |
| **2. Cascade thinning** | v3.1+ | thin remaining Tier-A cmds, each through B2; verify the 17-cmd deprecated tail (R1-B1); fix count cascade 30→1; content-audit `docs/commands` (R1-B4) | per-command |
| **3. Extract folio** | craft v4.0.0 / folio v1.0.0 | history-preserving `git subtree`/`filter-repo` of docs + dist into `folio`; coordinated release; migration guide | one-time |

## 5. Naming

- **`craft`** — kept (equity + it's the interactive soul; also owns generic
  release-ops per C1).
- **`folio`** — docs authoring + site publishing + refcard + marketplace
  curation. **Name LOCKED** (C3). Avoids `scribe` (existing project),
  `commit-*` (existing plugin).

## 6. Test Plan

- **Phase 1:** full `python3 -m pytest tests/` after the 39-command deletion;
  update count/discovery/e2e/dogfood tests that assert dropped commands exist.
  Link-validation CI must stay green after `exclude_docs` (R1-B6).
- **Per thinned command (B2):** a recorded 4-axis head-to-head transcript is the
  test artifact — no transcript, no retirement (e2e-before-PR contract).
- **Phase 3 extraction:** both `craft` and `folio` full suites green post-split;
  `brew install`/`brew audit` for any moved formula; marketplace/tap manifest
  sync verified.

## 7. Documentation

- `MIGRATION-v3.md` (removed/thinned commands → native/plugin replacements).
- Later `MIGRATION-v4.md` / folio README (moved docs+dist commands).
- Update REFCARD, plugin.json counts, CLAUDE.md, hub after each phase.

## 8. Open Questions (for /craft:plan)

*Resolved this session (C1–C3): folio name, retention rule, and
distribution↔release coupling. Remaining are **empirical** — answered by doing,
not deciding:*

1. **Cross-plugin invocation** — can a `craft` command cleanly invoke a `folio`
   or third-party skill? **Pilot (B3) must answer before cascade** — this is the
   single gating unknown for the whole split.
2. **17-command tail effort** — per-command body-vs-skill diff cost (R1-B1);
   produced by the audit, not a decision.

## 9. Handoff

`/craft:plan` tier 4 (plan-orchestrator) → `ORCHESTRATE-craft-native-first-breakup.md`
→ `/craft:do` / `/craft:orch`. This spec is convergent and plan-ready; it does
not execute.
