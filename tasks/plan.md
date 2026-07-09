# Plan — Craft Native-First Breakup, v3.0.0 Increment (Phase 0 + Phase 1)

**Source:** `docs/specs/SPEC-craft-native-first-breakup-2026-07-09.md` ·
`docs/plans/ORCHESTRATE-craft-native-first-breakup.md`
**Scope:** Phase 0 (recon) + Phase 1 (prune + exclude docs + pilot). NOT Phases 2–3.
**Mode:** plan (read-only). No code changed by writing this plan.

## Dependency graph

```
Phase 0 (read-only) ──┐
                      ▼
              [CHECKPOINT A: review recon → create worktree]
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
   1a prune       1b exclude-docs   1c pilot
   (39 cmds)      (mkdocs)          (3 cmds, gate)
      │               │                ▼
      └───────────────┴──────► [CHECKPOINT B: suite green + routing verdict]
```

- **1a / 1b / 1c are mutually independent** after the worktree exists — different files.
- **1c's cross-plugin routing verdict gates Phases 2–3** (out of this increment's scope), not Phase 1.
- Phase 0 blocks everything (recon must clear names before deletion).

## Hard constraints

- **Phase 0 = read-only** → runs on `dev`, no worktree.
- **Phase 1 = code changes** → branch-guard blocks new/code files on `dev`; requires
  `feature/craft-native-first-breakup` worktree. **CHECKPOINT A is human-gated** (worktree creation).
- **4-axis gate is non-negotiable** (1c): no command retired without a recorded quality ·
  switching-cost · dependency · UX transcript.

---

## Phase 0 — External-Caller Recon (read-only, no worktree)

### T0.1 — Grep the ecosystem for the 39 dead names + 3 pilot targets

- **Do:** grep `~/projects/dev-tools/flow-cli`, `~/projects/dev-tools/atlas`, `~/.claude`,
  shell history, `docs/tutorials/*`, and the marketplace/tap manifest for the 39 dead command
  names and the 3 pilot command names.
- **Acceptance:** a table of name → hit locations (or "no external callers").
- **Verify:** re-run the grep; zero unaudited names remain.

### T0.2 — Produce safe-delete list + keep-as-alias set

- **Do:** any of the 39 with a live external caller → moves to keep-as-alias (thin stub one cycle);
  the rest → confirmed safe-delete.
- **Acceptance:** `safe-delete` count + `keep-as-alias` list written to `tasks/recon-phase0.md`.
- **Verify:** counts reconcile (`safe-delete + keep-as-alias == 39`).

> **CHECKPOINT A (human):** review recon. If clean → authorize the feature worktree.
> Nothing below runs until the worktree exists.

---

## Phase 1a — Prune Dead Namespaces (worktree)

### T1a.1 — Delete the safe-delete command files (vertical: files + retained live)

- **Do:** `git rm` the safe-delete subset of the 39: `git/`(15), `workflow/`(5), `task/`(3),
  `check/`(1), `site/`'s 15 dead — **retain `commands/site/docs/frameworks.md`** (live).
- **Acceptance:** deleted count == safe-delete count; `site/docs/frameworks.md` still present.
- **Verify:** `find commands/{git,workflow,task,check} -name '*.md'` → empty; `site/` shows only live.

### T1a.2 — Update tests asserting the deleted commands exist

- **Do:** grep `tests/` for the deleted names; update count/discovery/e2e/dogfood assertions.
- **Acceptance:** no test references a deleted command.
- **Verify:** `python3 -m pytest tests/` → green (baseline-adjusted).

### T1a.3 — Regenerate counts + discovery cache

- **Do:** `./scripts/validate-counts.sh`, `bump-version.sh --verify`; force-regen `commands/_cache.json`.
- **Acceptance:** counts consistent across `plugin.json`/marketplace/docs; cache current.
- **Verify:** `validate-counts.sh` exits 0; `bump-version.sh --verify` clean.

---

## Phase 1b — Exclude Dead Docs From Built Site (worktree; independent of 1a)

### T1b.1 — Sweep inbound links + nav membership (do FIRST)

- **Do:** grep built pages for links into `docs/specs`/`plans`/`archive`; check each file's nav
  membership (SPEC R1-B6 — the `mkdocs-exclude-docs` memory). Fix/redirect any inbound links.
- **Acceptance:** zero inbound links from built pages into the 3 dirs.
- **Verify:** `python3 tests/test_craft_plugin.py -k broken_links` → green.

### T1b.2 — Extend existing `exclude_docs` (NOT overwrite)

- **Do:** read `mkdocs.yml`'s current `exclude_docs` block (already present, line 9); **append**
  `docs/specs/`, `docs/plans/`, `docs/archive/`. Dirs stay in-repo (no retention rule — C2).
- **Acceptance:** the 3 dirs excluded; prior exclusions preserved.
- **Verify:** `mkdocs build` succeeds; link-validation green; the 3 dirs absent from `site/`.

---

## Phase 1c — Native-First Pilot (worktree; the gate proof)

> Each pilot: run craft's command AND the replacement on ONE real target; score 4 axes; record
> transcript. Fail any axis → **deprecate-in-place (thin-kept), do NOT delete.**

### T1c.1 — `code:refactor` → native `/simplify`

- **Acceptance:** recorded 4-axis transcript; verdict (thin-route | thin-keep) with reason.
- **Verify:** transcript saved to `tasks/pilot-code-refactor.md`; both outputs quoted.

### T1c.2 — `arch:review` → native `/code-review`

- **Acceptance/Verify:** as T1c.1 → `tasks/pilot-arch-review.md`.

### T1c.3 — `ci:generate` → `agent-skills:ci-cd-and-automation`

- **Acceptance/Verify:** as T1c.1 → `tasks/pilot-ci-generate.md`.

### T1c.4 — Answer the cross-plugin routing gating unknown

- **Do:** from the 3 pilots, determine: can `do`/`hub` cleanly invoke a native/other-plugin skill?
- **Acceptance:** a written verdict (YES → cascade viable | NO → split needs rethink) in
  `tasks/routing-verdict.md`.
- **Verify:** verdict cites concrete pilot evidence, not assertion.

> **CHECKPOINT B (human):** full suite green + routing verdict reviewed. This closes the v3.0.0
> increment and decides whether Phase 2 (cascade) proceeds. Out of scope here.

---

## Acceptance (increment-level)

- [ ] Phase 0 recon done; safe-delete list + keep-as-alias set recorded.
- [ ] Safe-delete commands removed; `site/docs/frameworks.md` retained; suite green.
- [ ] 3 dead-doc dirs excluded from built site; link CI green; files still in git.
- [ ] 3 pilots each have a 4-axis transcript; cross-plugin routing verdict documented.

## Verification command

```bash
python3 -m pytest tests/ && ./scripts/validate-counts.sh
```
