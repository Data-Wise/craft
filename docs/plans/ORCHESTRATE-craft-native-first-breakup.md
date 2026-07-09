# Craft Native-First Breakup — Orchestration Plan

> **Branch:** `feature/craft-native-first-breakup` (create when implementation starts)
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-craft-native-first-breakup` (not yet created — ORCHESTRATE-only)
> **Spec:** `docs/specs/SPEC-craft-native-first-breakup-2026-07-09.md`
> **Grill:** `docs/specs/GRILL-craft-refactor-2026-07-09.md`
> **Status:** PLAN — not started. Exploration/planning only; no code touched.

## Objective

Shrink craft from a 115-command / 135K-doc-line monolith into a **native-first**
system: `craft` (interactive workflow core + release-ops) that routes to Claude's
own features and best-of-breed plugins, and `folio` (docs authoring + publishing),
extracted last. Every deletion passes one gate: **verify the replacement before
deleting the original.**

## Phase Overview

| Phase | Increment | Version | Priority | Effort | Status |
|-------|-----------|---------|----------|--------|--------|
| 0 | External-caller grep (read-only recon) | — | P0 (gates all deletion) | Low | ☐ not started |
| 1 | Prune 39 dead cmds + exclude dead docs + pilot-thin 2–3 | v3.0.0 | P0 | High | ☐ not started |
| 2 | Cascade thinning + verify 17-cmd tail + count cascade + docs/commands audit | v3.1+ | P1 | High | ☐ not started |
| 3 | Extract `folio` (docs+publishing), history-preserving | craft v4.0.0 / folio v1.0.0 | P2 | High | ☐ not started |

> **Gating unknown (resolve in Phase 1 pilot):** can a `craft` command cleanly
> invoke a `folio`/third-party skill? If not, Phase 3 needs rethinking — do NOT
> cascade (Phase 2) or extract (Phase 3) until the pilot answers this.

---

## Phase 0: External-Caller Recon (read-only)

**Scope:** Prove nothing external breaks before any command is removed or thinned (SPEC R1-B7).

- [ ] 0.1 Grep `~/projects/dev-tools/flow-cli`, `~/projects/dev-tools/atlas`, `~/.claude`, shell history, craft's own `docs/tutorials/*`, and the marketplace/tap manifest for all 56 deprecated command names + the 3 pilot targets.
- [ ] 0.2 Produce a **keep-as-alias set**: any name with a live external caller stays a thin alias one more cycle.
- [ ] 0.3 Record the confirmed-safe deletion list (expected: "39 minus external hits").

**Key files:** none modified — output is a recon note appended to the spec's §8 or a scratch list.

**Exit:** a concrete safe-to-delete list. No exit → do not enter Phase 1.

---

## Phase 1: Prune + Pilot (v3.0.0)

**Scope:** The big safe win + the native-first proof-of-method.

### 1a — Prune dead namespaces

- [ ] 1.1 Delete the 39 dead-namespace commands: `git/`(15) + `workflow/`(5) + `task/`(3) + `check/`(1) + `site/`'s 15 deprecated — **keep `site/`'s 1 live command** (SPEC R1-B1).
- [ ] 1.2 Update count/discovery/e2e/dogfood tests that assert the dropped commands exist.
- [ ] 1.3 Regenerate counts once (`bump-version.sh`, `validate-counts.sh`) against the new total.
- [ ] 1.4 Regenerate discovery cache (`commands/_cache.json` is gitignored — force regen).

### 1b — Exclude dead docs from built site

- [ ] 1.5 **First** sweep built pages for inbound links into `docs/specs`/`plans`/`archive` + check per-file nav membership (SPEC R1-B6); fix/redirect them.
- [ ] 1.6 Add `exclude_docs` for the 3 dirs to `mkdocs.yml`; keep dirs in-repo (SPEC R1-B2, **no** retention rule per C2).
- [ ] 1.7 Confirm link-validation CI stays green.

### 1c — Native-first pilot (SPEC B2/B3 — the gate proof)

- [ ] 1.8 Pilot-thin **3 representative commands**, each through the **4-axis gate** (quality · switching cost · dependency risk · UX): `code:refactor`→`/simplify`, `arch:review`→`/code-review`, `ci:generate`→`agent-skills:ci-cd-and-automation`.
- [ ] 1.9 For each: record the head-to-head transcript (no transcript → no retirement). Fail any axis → deprecate-in-place, don't delete.
- [ ] 1.10 **Answer the gating unknown:** does `do`/`hub` route cleanly to the native/plugin target cross-plugin? Document the finding — it gates Phases 2–3.

**Key files:** `commands/{git,workflow,task,check,site}/*` (delete), `mkdocs.yml` (update), `commands/{code/refactor,arch/review,ci/generate}.md` (thin), `plugin.json` + count docs (update), `MIGRATION-v3.md` (NEW), `tests/*` (update).

**Exit:** full suite green; 39 gone; dead docs excluded; 3 pilots thinned-or-thin-kept with transcripts; cross-plugin routing verdict recorded.

---

## Phase 2: Cascade Thinning (v3.1+)

**Scope:** Only if Phase 1's cross-plugin routing verdict is positive.

- [ ] 2.1 Thin remaining Tier-A commands, **each through the 4-axis gate** (batch by category: `ci/*`, `code/*`, `arch/*`, `plan*`, `test`).
- [ ] 2.2 Verify the **17 deprecated-in-live-namespace** commands: diff each body vs its `replaced-by:` skill; delete only when logic is confirmed migrated (SPEC R1-B1).
- [ ] 2.3 Fix the count cascade: one generated counts source-of-truth + build step (30→1 file) (SPEC R1-B3).
- [ ] 2.4 Content-audit `docs/commands/` (84 pages): generate only thin mirrors, hand-keep content-rich pages (SPEC R1-B4).

**Key files:** `commands/{ci,code,arch,plan}/*` (thin/delete), a new counts generator (`scripts/` or `utils/`), `docs/commands/*` (audit/regenerate).

**Exit:** Tier-A surface is thin routes or thin-kept; count cascade dead; metric = files-touched-per-release measurably down.

---

## Phase 3: Extract folio (craft v4.0.0 / folio v1.0.0)

**Scope:** Split the now-thin surface. Split thin, not fat (SPEC B4).

- [ ] 3.1 History-preserving extraction (`git subtree` / `git filter-repo`) of docs + publishing (site deploy, refcard, marketplace curation) into a new `folio` repo. **Release-ops (bump/changelog/formula-gen/tap-sync) STAYS in craft** (SPEC C1).
- [ ] 3.2 craft major bump (v4.0.0) as docs-publishing leaves; folio starts v1.0.0.
- [ ] 3.3 `MIGRATION-v4.md` maps moved commands; update marketplace/tap entries; wire folio's own CI.
- [ ] 3.4 Verify both `craft` and `folio` full suites green post-split; `brew install`/`brew audit` for any moved formula.

**Key files:** new `folio` repo, `craft` docs/ + publishing commands (removed), both `plugin.json`s, marketplace/tap manifests.

**Exit:** two plugins, both green, no cross-plugin dependency for either to ship itself.

---

## Friction Prevention

- **Context first, verify CWD/branch** before any git op (`git worktree list`, `git branch --show-current`, `pwd`).
- **No feature code on `dev`** — Phase 1+ code changes require the `feature/*` worktree first (branch-guard blocks new code files on `dev`).
- **Count cascade** — adding/removing a command touches ~30 files; run `validate-counts.sh` + `bump-version.sh --verify` after every count change (Phase 2.3 exists to kill this).
- **Discovery cache** — `commands/_cache.json` is gitignored; regenerate after command deletions.
- **BSD vs GNU sed** — use flavor-detecting `sedi()`; never bare `sed -i ''` in CI-run scripts.
- **The gate is non-negotiable** — no command is deleted (Phase 1c/2) without a recorded 4-axis transcript. This is the through-line every review converged on.
- **Test in the tree the PR ships from** — run the suite in the worktree's absolute path, not the main checkout.

## Acceptance Criteria

- [ ] 39 dead-namespace commands removed; `site/`'s 1 live command retained.
- [ ] `docs/specs`/`plans`/`archive` excluded from built site; link CI green; all files still in git.
- [ ] 3 pilot commands thinned-or-thin-kept, each with a 4-axis head-to-head transcript.
- [ ] Cross-plugin routing verdict documented (gates Phases 2–3).
- [ ] (Phase 2) count cascade reduced to 1 source file; Tier-A thinned per gate.
- [ ] (Phase 3) `craft` + `folio` split, both suites green, neither depends on the other to release.

## Commit Strategy

Conventional commits per increment (`feat:`, `refactor:`, `docs:`, `test:`, `chore:`).
Phase 1 = one PR (`feature/craft-native-first-breakup → dev`), squash-merged. Phase 3
extraction = its own coordinated two-repo release.

## Verification

```bash
python3 -m pytest tests/                 # full suite (Phase 1 & 2 gates)
./scripts/validate-counts.sh             # after any count change
./scripts/docs-staleness-check.sh        # after doc exclusion
# per thinned command: recorded 4-axis head-to-head transcript (the real gate)
```

## Test Plan (scaffold — default-on)

Tiers inferred from change shape (new scripts + cross-command routing + external dep + command removal → all tiers):

- **unit** — the new counts-generator (Phase 2.3) and any thinning-audit script. *(red-first stub; `# TODO(author): delete if not contract-bearing`)*
- **integration** — `do`/`hub` cross-plugin routing to native/plugin targets (Phase 1.10 gating unknown). *(red-first)*
- **dependency** — depending on `agent-skills` / native skills: pin/fallback behavior when the target is absent. *(red-first)*
- **count-cascade** (dogfood) — after 39-command deletion and after Phase 2 thinning, counts stay consistent across `plugin.json`/marketplace/docs.
- **e2e** — each pilot command's thin route produces equivalent output to its old body (the 4-axis transcript IS this evidence).
- **dogfood** — `/craft:do` still routes correctly with the reduced surface.

## Documentation (scaffold — default-on)

Spec-time = read-only pre-derive; real edits happen impl/post-merge via `/craft:docs:update --post-merge` (diff-gated). Auto-docs touches semantic docs only, never version/count lines.

- [x] `MIGRATION-v3.md` (Phase 1) — removed/thinned commands → native/plugin replacements. **Contract-bearing.**
- [x] CHANGELOG `[Unreleased]` ×2 mirror (root + docs/) per phase.
- [ ] REFCARD / hub / CLAUDE.md count refresh — `N/A at spec-time` (bump-version.sh owns counts).
- [ ] `MIGRATION-v4.md` + folio README (Phase 3) — `N/A until Phase 3`.
- [ ] Site consistency (nav, skills-agents.md) after each phase.

## Session Instructions

This is an **ORCHESTRATE-only** artifact — no worktree was created. When ready to implement:

```bash
git worktree add ~/.git-worktrees/craft/feature-craft-native-first-breakup -b feature/craft-native-first-breakup dev
# move this file to the worktree root, then:
cd ~/.git-worktrees/craft/feature-craft-native-first-breakup && claude
# > "Read ORCHESTRATE-craft-native-first-breakup.md and start Phase 0."
```

**Start with Phase 0 (read-only recon) — it gates every deletion that follows.**
