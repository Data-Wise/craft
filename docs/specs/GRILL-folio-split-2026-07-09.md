# GRILL — folio split (docs-authoring extraction)

> **Target:** Extract craft's docs-authoring surface into a standalone `folio` plugin;
> craft keeps workflow-core + release + git.
> **Date:** 2026-07-09
> **Context:** Native-first thinning was empirically **refuted** (PR #279, memory
> `native-first-thinning-refuted-for-craft-dev-ops`). This grill revisits the folio
> split on **docs-maintenance merits only** — the one rationale the refutation did not
> touch. The cross-plugin router wall found during that refutation is now a *constraint*
> this split must design around, not a premise.
> **Related:** `docs/specs/SPEC-craft-native-first-breakup-2026-07-09.md` (OUTCOME block),
> `docs/plans/ORCHESTRATE-craft-native-first-breakup.md` (Phase 3, dropped).

## Codebase evidence (pre-grill sweep)

- **Surface to move (~30 cmds + 6 agents + 5 skills):** `commands/docs/` (22),
  `commands/site/` (8), `agents/docs/` (6: api-documenter, demo-engineer, docs-architect,
  mermaid-expert, reference-builder, tutorial-engineer), `skills/docs/` (4: doc-classifier,
  navigation, site-management, mermaid-linter) + `skills/code/demonstration-builder`.
- **SEAM #1 (release coupling) is load-bearing:** craft's `/release` pipeline directly
  invokes `/craft:docs:update --post-merge` (Step 3b, semantic version/count doc-sync) and
  `/craft:site:deploy` (Step 9, an alias over raw `mkdocs build --strict && mkdocs gh-deploy`).
  `docs:changelog` is referenced by `dist/homebrew.md`. The cross-plugin wall means moving
  these to folio breaks craft's release.
- **SEAM #2 (/do + hub routing):** `commands/hub.md` displays a DOCS(22)/SITE(8) grid;
  `/do` routes a "docs" category. Post-split, craft's router cannot dispatch into `/folio:*`.
- **SEAM #3 (count/bump tooling):** `bump-version.sh` / `validate-counts.sh` /
  `exclusions.txt` are craft-internal; folio needs its own.

## Decision Ledger

### B1 — folio scope: tools, or tools + content?  ✅ LOCKED

**Decision:** folio = authoring **TOOLS + a shared docs-standards library**; each project
(including craft) keeps its **own docs content**.

**Why:** Reusable across all ~25 dev-tools projects. Grounds on the *existing* `docs-standards`
sibling repo (Quarto + MkDocs templates) — folio's tools consume/enforce it rather than
re-inventing style. craft's own doc-bloat stays a separate cleanup (exclude_docs + pruning),
not conflated with the split.

**Consequence accepted:** a third moving part (the standards lib) to version alongside folio;
folio and docs-standards must agree on a contract.

### B2 — the release-coupling seam: how to cut docs/?  ✅ LOCKED

**Decision:** **Caller-based classification, not directory-based.** Commands a craft-core
pipeline invokes stay in craft; only pure-authoring commands move to folio.

- **Stay in craft (release-plumbing):** `docs:update` (`--post-merge` = version/count/README/
  REFCARD/mkdocs sync), `docs:changelog`. `site:deploy` collapses back to the raw
  `mkdocs build --strict && mkdocs gh-deploy` shell it already aliases (release keeps the shell,
  drops the alias).
- **Move to folio (authoring):** `docs:{tutorial, demo, website, guide, api, mermaid, lint,
  check-links, quickstart, nav-update, help, prompt, workflow, check, sync}`, the 6 docs agents,
  the 4 docs skills + demonstration-builder. `site:{build, publish, status, progress, check,
  update}` (authoring/preview surface).

**Why:** keeps craft's release self-contained — zero runtime dependency on folio. Rejects the
shell-out option (re-introduces the cross-plugin fragility native-first was refuted for) and the
duplicate-subset option (drift = rich-body-trap one level up).

**Consequence accepted:** `commands/docs/` **splits across two plugins** — a few `/craft:docs:*`
(update, changelog) live alongside most `/folio:docs:*`. Users learn a namespace seam. The exact
staying-set is a SPEC deliverable (audit every craft-core caller before finalizing).

### B3 — /do + /hub routing loss  ✅ LOCKED

**Decision:** craft's `/do` **drops the DOCS/SITE categories** and `/hub` stops displaying them.
Docs authoring becomes deliberate direct invocation (`/folio:docs:*`); **folio ships its own
`/folio:do` / `/folio:hub`** for its surface.

**Why:** honest — the router never advertises a target it structurally can't reach. One clean
mental model per plugin. Rejects the "pointer in /hub" option (advertises unrunnable commands +
craft/folio doc-drift coupling) and the "thin shim" option (dead weight that re-grows craft).

**Consequence accepted:** loses the single-`/do`-entry-point convenience for docs tasks; the user
switches plugins consciously to author docs. Aligns with B1 (docs authoring is a separate mode).

### B4 — count/bump tooling: duplicate or share?  ✅ LOCKED

**Decision:** **Duplicate** the cascade tooling (`bump-version.sh`, `validate-counts.sh`,
`exclusions.txt`, `pre-release-check.sh`, `post-release-sweep.sh`) into folio, tuned to its
surface.

**Why:** the split *shrinks* each plugin's cascade (folio ~30 cmds, craft ~64 vs. today's 94),
so per-repo tooling is lighter than the status quo. A shared lib is over-engineering for two
consumers (a 4th moving part); scriptless-launch re-introduces the count-drift the memory graph
spent months killing.

**Consequence accepted:** two copies drift over time — acceptable since each is small,
independently versioned, and now covers a smaller surface.

### B5 — extraction mechanics + sequencing + versioning  ✅ LOCKED

**Decision:** **History-preserving, staged, `craft v4.0.0` + `folio v1.0.0`.**

- **Mechanics:** `git subtree split` (or `git filter-repo`) to carry `commands/docs/`,
  `commands/site/`, `agents/docs/`, and the docs skills' history into a new `folio` repo.
- **Sequence:** (1) finalize the caller-based staying-set (B2) on a craft feature branch →
  (2) build + wire folio CI as a standalone plugin → (3) craft **v4.0.0** removes the moved
  commands (breaking), folio **v1.0.0** launches → coordinated two-repo release with
  tap/marketplace entries for both.

**Why:** history intact for blame/bisect on ~30 commands + 6 agents. Rejects fresh-copy (loses
authorship on the exact files most likely to need archaeology later).

**Consequence accepted:** two-repo release choreography — done once, then each ships
independently (the whole point of the split).

## Open Questions (resolve at SPEC/plan time, not blocking)

- **Exact caller-based staying-set (B2):** ✅ **RESOLVED 2026-07-09** — Phase 0 caller-audit ran
  via dynamic Workflow (7 agents, adversarial verify: `partition_sound: true`, 0 misclassified,
  30/30 coverage). **STAYS (3):** `docs:update`, `docs:changelog`, `site:deploy`-as-raw-shell.
  **MOVES (26):** all other `docs:*`/`site:*`. Release safety proven: `docs:update --post-merge`
  is inline logic (`update.md:379–500`), not an orchestration of moved subcommands. One judgment
  call left to Phase 1: the `docs:claude-md:*` trio (craft-internal CLAUDE.md governance —
  leaning STAYS as a unit). Full partition + follow-ups: ORCHESTRATE Phase 0 OUTCOME block.
- **folio visibility (NEW, from the zero-CI impact analysis 2026-07-09):** ✅ folio must be
  **PUBLIC** — private-repo Actions bill against the account pool (zero-CI strategy, memory
  `github-actions-zero-ci-strategy-2026-07`); public = CI free; history is public content
  already. Recorded in ORCHESTRATE Phase 1.1 (+ new 1.5 protection-baseline task).
- **folio ↔ docs-standards contract (B1):** how folio's tools reference the existing
  `docs-standards` repo (submodule? path convention? bundled templates?).
- **craft's own docs after split (B1):** craft keeps its content but now authors it with folio —
  confirm craft's release pipeline (which keeps `docs:update`/`mkdocs gh-deploy`) still fully
  builds craft's site without the moved authoring commands.
- **`/folio:do` / `/folio:hub` scope (B3):** does folio need a full router, or a simpler index?
- **Migration doc:** `MIGRATION-v4.md` mapping every moved `/craft:*` → `/folio:*` for users.

## Handoff

Locked ledger is plan-ready. Next: `/craft:plan` tier 4 (plan-orchestrator) →
`ORCHESTRATE-folio-split.md` → `/craft:do` / `/craft:orch`. Grill does not execute.

**This is a NEW initiative** — supersedes the dropped Phase 3 of
`ORCHESTRATE-craft-native-first-breakup.md`; that plan stays CLOSED.
