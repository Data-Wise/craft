# folio Split — Orchestration Plan

> **Branch:** `feature/folio-split` (create when implementation starts — ORCHESTRATE-only for now)
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-folio-split` (not yet created)
> **Second repo:** `~/projects/dev-tools/folio` (NEW — created in Phase 1)
> **Grill:** `docs/specs/GRILL-folio-split-2026-07-09.md` (5 branches B1–B5 LOCKED — the spec input)
> **Status:** ☐ NOT STARTED (2026-07-09). Plan-ready; no code written; no worktree/repo created.

> **This is a NEW initiative.** It supersedes the dropped Phase 3 of
> `ORCHESTRATE-craft-native-first-breakup.md` (which stays CLOSED). Native-first thinning was
> refuted (PR #279); the cross-plugin router wall found there is a *constraint* this plan designs
> around (B2, B3), not a premise.

## Objective

Extract craft's docs-authoring surface (~28 commands + 6 agents + 5 skills) into a standalone,
reusable `folio` plugin; craft keeps workflow-core + release + git. Every move passes one gate:
**a command stays in craft iff a craft-core pipeline invokes it** (caller-based cut, B2). craft
ends at ~64 commands; folio launches at ~28.

## Phase Overview

| Phase | Increment | Repo | Version | Priority | Effort | Status |
|-------|-----------|------|---------|----------|--------|--------|
| 0 | Caller-audit — finalize the exact stays/moves set (read-only) | craft | — | P0 (gates the cut) | Low | ☐ |
| 1 | folio scaffold + docs-standards contract + duplicate count tooling | folio | folio v0.1.0 | P0 | Med | ☐ |
| 2 | History-preserving extraction of the moving-set + folio CI | folio | folio v1.0.0-rc | P0 | High | ☐ |
| 3 | craft amputation — remove moved cmds, collapse site:deploy, drop DOCS from /do+/hub | craft | craft v4.0.0 | P0 | High | ☐ |
| 4 | folio /folio:do + /folio:hub + coordinated two-repo release | both | craft v4.0.0 / folio v1.0.0 | P1 | Med | ☐ |

> **Gating dependency:** Phase 0's staying-set output is the input to Phases 2 & 3. Do NOT extract
> (Phase 2) or amputate (Phase 3) until Phase 0 confirms which `docs:*`/`site:*` commands a
> craft-core pipeline actually calls. B2 confirms `docs:update` + `docs:changelog` stay; Phase 0
> proves the rest.

---

## Phase 0: Caller-Audit (read-only) — resolves Open Question #1

**Scope:** Prove the exact stays/moves partition before anything moves (B2). This is the
"verify the seam before you cut" gate the whole session's method turns on.

- [ ] 0.1 Grep every craft-core invocation of a `docs:*` / `site:*` command across
      `skills/release/`, `skills/distribution/`, `commands/dist/`, `commands/ci/`, `commands/orch/`,
      `commands/git/`, and any hook/script under `scripts/`.
- [ ] 0.2 Classify each hit: **release-plumbing → stays in craft**; **authoring → moves to folio**.
      Seed set (from grill B2): STAY = `docs:update`, `docs:changelog`; `site:deploy` → collapse to
      raw `mkdocs build --strict && mkdocs gh-deploy`. MOVE = `docs:{tutorial, demo, website, guide,
      api, mermaid, lint, check-links, quickstart, nav-update, help, prompt, workflow, check, sync}`
      + 6 docs agents + 4 docs skills + `demonstration-builder` + `site:{build, publish, status,
      progress, check, update}`.
- [ ] 0.3 Resolve any hit NOT in the seed set explicitly (surface it — don't silently bucket it).
- [ ] 0.4 Record the confirmed partition as a recon note appended to the grill's Open Questions.

**Key files:** none modified — output is a recon list.

**Exit:** a concrete stays-set + moves-set. No exit → do not enter Phase 2/3.

---

## Phase 1: folio Scaffold + Contracts (folio v0.1.0)

**Scope:** Stand up an empty-but-valid `folio` plugin repo. No craft changes; no command content
moved yet.

- [ ] 1.1 Create `~/projects/dev-tools/folio` as a git repo (multi-branch: `main` ← `dev` ←
      `feature/*`, matching the ecosystem norm). Add `.claude-plugin/plugin.json` (strict schema),
      `commands/`, `agents/`, `skills/`, `docs/`, `scripts/`, `tests/`, `CLAUDE.md`.
- [ ] 1.2 **folio ↔ docs-standards contract (Open Q #2):** decide how folio's tools reference the
      existing `~/projects/dev-tools/docs-standards` repo (path convention vs. bundled templates vs.
      submodule). Recommended: path convention + a documented fallback — no hard submodule coupling.
      Write the contract into `folio/CLAUDE.md`.
- [ ] 1.3 **Duplicate count tooling (B4):** copy `bump-version.sh`, `validate-counts.sh`,
      `exclusions.txt`, `pre-release-check.sh`, `post-release-sweep.sh` into `folio/scripts/`, tuned
      to folio's (smaller) surface. Wire `validate-counts.sh` to folio's namespaces.
- [ ] 1.4 Add folio to the marketplace/tap generator inputs (entry only — not yet published).

**Key files:** all NEW under `~/projects/dev-tools/folio/`.

**Exit:** `folio` repo exists; `plugin.json` validates; count scripts run green on an empty surface.

---

## Phase 2: History-Preserving Extraction (folio v1.0.0-rc)

**Scope:** Carry the moves-set (Phase 0 output) into folio **with git history** (B5). folio still
does not depend on craft; craft is untouched this phase.

- [ ] 2.1 `git subtree split` (or `git filter-repo`) the moving paths from craft — `commands/docs/`
      (minus stays), `commands/site/` (minus deploy), `agents/docs/`, the 4 `skills/docs/*` +
      `skills/code/demonstration-builder` — preserving authorship/blame.
- [ ] 2.2 Graft the split history into `folio` under the same relative paths. Rewrite internal
      `/craft:*` self-references in the moved files to `/folio:*`.
- [ ] 2.3 Repoint the moved commands' `docs-standards` references per the Phase 1.2 contract.
- [ ] 2.4 Wire folio CI (mirror craft's: unit + e2e + dogfood + Validate Plugin Structure bash
      suites + count-cascade). folio's own `docs/` site builds `--strict`.
- [ ] 2.5 Regenerate folio counts; `validate-counts.sh` green at ~28 cmds / N skills / 6 agents.

**Key files:** `folio/commands/**`, `folio/agents/**`, `folio/skills/**`, `folio/.github/`,
`folio/mkdocs.yml`.

**Exit:** folio full suite green; the moved surface works under `/folio:*`; history intact
(`git log --follow` on a moved command shows its craft-era commits).

---

## Phase 3: craft Amputation (craft v4.0.0 — BREAKING)

**Scope:** Remove the moved surface from craft; keep the release-plumbing subset; sever the router
references. Only enter after Phases 0 & 2 are green.

- [ ] 3.1 Delete the moved commands/agents/skills from craft (the Phase 0 moves-set). Keep the
      stays-set (`docs:update`, `docs:changelog`).
- [ ] 3.2 Collapse `site:deploy` usage in `skills/release/` + `references/pipeline-steps.md` to the
      raw `mkdocs build --strict && mkdocs gh-deploy` shell it already aliased; delete the alias cmd.
- [ ] 3.3 **Drop DOCS/SITE from routing (B3):** remove the DOCS/SITE categories from
      `commands/do.md`'s routing table and the DOCS(22)/SITE(8) grid from `commands/hub.md` (+ the
      docs mirror). `/do` no longer advertises a folio target it can't reach.
- [ ] 3.4 **Confirm craft still builds its OWN site (Open Q #3):** run craft's release doc-sync
      (`docs:update --post-merge`) + `mkdocs build --strict` + `gh-deploy` dry-run WITHOUT the moved
      authoring commands present. Must be fully green — this is the load-bearing proof that the
      caller-based cut was correct.
- [ ] 3.5 Count cascade: `bump-version.sh` + `validate-counts.sh` at craft's new ~64-command total;
      sweep the ~30-file cascade (plugin.json, README, REFCARD, hub, docs/commands, exclusions.txt).
- [ ] 3.6 **`MIGRATION-v4.md` (Open Q #5):** map every moved `/craft:docs:*` / `/craft:site:*` →
      `/folio:*`. Contract-bearing.

**Key files:** `commands/docs/**` + `commands/site/**` (delete subset), `commands/do.md`,
`commands/hub.md`, `skills/release/**`, `plugin.json` + count docs, `MIGRATION-v4.md` (NEW),
`tests/**` (update floors/shim suites — see `test_git_shim_correctness.sh`, hub floors).

**Exit:** craft full suite green (pytest **and** the Validate-Plugin-Structure bash suites — they
diverge, per memory `pytest-doesnt-cover-craft-ci-bash-suites`); craft builds its own site with
zero moved commands; MIGRATION-v4 complete.

---

## Phase 4: folio Router + Coordinated Release (craft v4.0.0 / folio v1.0.0)

**Scope:** Give folio its own entry surface, then ship both repos together.

- [ ] 4.1 **`/folio:do` + `/folio:hub` (Open Q #4):** build folio's own router/index for its
      surface. Recommended: start with a simple `/folio:hub` index (display) + a thin `/folio:do`
      that routes folio's own commands only — no cross-plugin dispatch (the same wall applies in
      reverse). Grow only if needed.
- [ ] 4.2 Coordinated two-repo release: craft **v4.0.0** (breaking — docs commands gone) merges
      `feature/folio-split → dev → main`; folio **v1.0.0** ships from its `dev → main`.
- [ ] 4.3 Homebrew formula + tap manifest + marketplace entries for **both** plugins; verify
      `brew install` / `brew audit` for any moved formula bits.
- [ ] 4.4 CI verify green on `main` for both; docs deploy (auto for push-to-main projects).

**Key files:** `folio/commands/{do,hub}.md`, both `plugin.json`s, tap manifest, marketplace inputs.

**Exit:** two plugins, both suites green, neither depends on the other to ship itself.

---

## Friction Prevention

- **Context first** — verify CWD/branch (`git worktree list`, `git branch --show-current`, `pwd`)
  before any git op; this plan spans two repos, so path/branch confusion is the top risk.
- **No feature code on `dev`** — Phase 1+ requires the `feature/folio-split` worktree first
  (branch-guard blocks new code files on `dev`).
- **The caller-based cut is the whole game** — Phase 0 is non-negotiable; a wrong partition means
  Phase 3.4 (craft can't build its own site) or a broken release. Don't skip to extraction.
- **History-preserving, not copy** (B5) — use `git subtree split`/`filter-repo`; never a plain copy.
- **pytest ≠ CI bash suites** — Phase 2.4 & 3.6 must run the Validate-Plugin-Structure bash suites,
  not just pytest (memory `pytest-doesnt-cover-craft-ci-bash-suites`).
- **Count cascade** — both repos now have their own; run `validate-counts.sh` in EACH after any
  count change (memory `adding-a-command-cascades-30-file-count-bump`).
- **Cross-repo branch name** — use identical `feature/folio-split` in both worktrees if paired.
- **ADR-002 rich-body check** — before deleting any craft command in Phase 3, confirm its logic
  isn't lost (verify the `replaced-by`/moved target carries it); run
  `test_skill_referenced_commands_exist` (memory `deprecated-command-rich-body-trap`).

## Acceptance Criteria

- [ ] Phase 0 partition recorded; every craft-core `docs:*`/`site:*` caller classified.
- [ ] `folio` repo exists, plugin validates, count tooling green.
- [ ] Moving-set extracted **with history**; folio full suite (pytest + bash) green.
- [ ] craft at ~64 commands; craft builds its OWN site with zero moved authoring commands (3.4).
- [ ] `/do` + `/hub` no longer reference DOCS/SITE; no dangling routes.
- [ ] `MIGRATION-v4.md` maps every moved command.
- [ ] Both plugins released, both suites green on `main`, neither depends on the other to ship.

## Commit Strategy

Conventional commits per increment. Phase 3 (craft) = one PR `feature/folio-split → dev`,
squash-merged, then `dev → main` as the v4.0.0 release (merge-commit). folio = its own repo's
`dev → main` v1.0.0. The two releases are coordinated (Phase 4.2) but each repo ships itself.

## Verification

```bash
# craft (in the feature worktree's absolute path)
python3 -m pytest tests/
bash tests/test_git_shim_correctness.sh          # + other Validate-Plugin-Structure bash suites
./scripts/validate-counts.sh
mkdocs build --strict                            # Phase 3.4: craft builds its own site

# folio (in the folio repo)
python3 -m pytest tests/ && ./scripts/validate-counts.sh && mkdocs build --strict
```

## Test Plan (scaffold — default-on)

Tiers inferred (new repo + new scripts + cross-command routing removal + command removal + new
plugin = all tiers):

- **unit** — folio's duplicated count-generator + any extraction/repoint script. *(red-first;
  `# TODO(author): delete if not contract-bearing`)*
- **integration** — craft release doc-sync WITHOUT the moved commands (Phase 3.4 gating proof).
  *(red-first)*
- **dependency** — folio ↔ docs-standards reference behavior when the standards repo is absent
  (fallback path). *(red-first)*
- **count-cascade (dogfood)** — after Phase 3 amputation, craft counts stay consistent at ~64;
  after Phase 2, folio counts consistent at ~28.
- **e2e** — a moved command (e.g. `folio:docs:tutorial`) produces equivalent output post-move.
- **dogfood** — `/craft:do` routes correctly with DOCS/SITE removed; `/folio:do` routes folio's own.

## Documentation (scaffold — default-on)

Spec-time = read-only pre-derive; real edits happen impl/post-merge via
`/craft:docs:update --post-merge` (diff-gated). Auto-docs touches semantic docs only, never
version/count lines.

- [x] `MIGRATION-v4.md` (Phase 3) — every moved `/craft:*` → `/folio:*`. **Contract-bearing.**
- [x] `folio/CLAUDE.md` (Phase 1) — folio conventions + docs-standards contract. **Contract-bearing.**
- [x] CHANGELOG `[Unreleased]` — craft (breaking removal) + folio (initial) per phase.
- [ ] REFCARD / hub / CLAUDE.md count refresh — `N/A at spec-time` (bump-version.sh owns counts).
- [ ] Site consistency (nav, skills-agents.md) in BOTH repos after each phase.

## Session Instructions

**ORCHESTRATE-only** — no worktree, no folio repo created yet. When ready to implement:

```bash
# Phase 0 is read-only — can run from the dev session directly.
# Phases 1+ need the worktree:
git worktree add ~/.git-worktrees/craft/feature-folio-split -b feature/folio-split dev
# move this file to the worktree root, then:
cd ~/.git-worktrees/craft/feature-folio-split && claude
# > "Read ORCHESTRATE-folio-split.md and start Phase 0."
```

**Start with Phase 0 (read-only caller-audit) — it gates every move that follows.**
