# Command Namespace Reorganization — Consolidated Decisions

**Status:** Implemented and committed on `dev` (commits `d27698ab`..`daf9305d`), with two decisions reversed during implementation after reading files the original grill didn't (see §5, §8).

**Origin:** Started from a Chat-session proposal covering `/next`, `/refine`, a `prompt-refiner` naming collision, and a proposed new command. Two of that proposal's three "trivial" items rested on false premises (verified against the repo, not assumed) and one new-command idea was dropped as out of scope for craft. That grill expanded into a full root-vs-namespace audit across every command namespace in the plugin.

**Process note:** Every "confirmed" claim below was verified against the actual repo state (file existence, `replaced-by` targets, cross-references) before being used to justify a decision — several premises in the originating proposal turned out to be false (see "Corrected premises").

---

## 1. Root command list (promotions)

Root commands are files directly under `commands/`, invoked as `/craft:<name>` with no namespace segment.

**Before:** `check`, `do`, `grill`, `hub`, `orchestrate`, `plan` (6)

**After (14):** add `next`, `done`, `refine`, `brief`, `brainstorm`

| Command | From | Rationale |
|---|---|---|
| `next` | `workflow:next` | High-frequency; promoted alongside `done` |
| `done` | `workflow:done` | High-frequency; promoted alongside `next` |
| `refine` | `workflow:refine` | Standalone invocation requested; matches existing root-command precedent (check/do/grill/hub/orchestrate/plan already live at root) |
| `brief` | `workflow:brief` | Has real behavior (326 lines, anti-vagueness constraints, `--board`/`--plan` modes), not a shim; invoked as often as check/do |
| `brainstorm` | `workflow:brainstorm` | Symmetry with `grill` (its convergent counterpart), already root; this is the skill running the session that produced this spec |

**Sequencing for `refine`'s move — still open, pick one:**

1. Own small PR now (update ~11 referencing files, including this spec's own repo state)
2. Bundle with `next`/`done` promotion + the `/next`/`/refine` doc-contradiction fixes below
3. Personal shim first (`~/.claude/commands/refine.md`), defer the real move

**Explicitly reverted during the grill:** `worktree` and `sync` were briefly proposed for promotion from `git:`, then reverted — all 10 `git:` shims + `guard` stay nested, no promotions from that namespace.

---

## 2. Corrected premises (from the originating Chat proposal)

1. **`/next` un-deprecation.** Proposal claimed `replaced-by: "skills/workflow/adhd-workflow/"` "doesn't exist anywhere in the repo." **False** — the skill exists (8.5K, `SKILL.md`), fully implements next-task suggestion as its "Next-Task Suggestion" operation, and is the documented producer/consumer partner for `.STATUS`. **Real issue identified instead:** NL-triggering reliability — the skill exists and works via the explicit slash command, but natural-language invocation may not reliably route to it. Fix scope: `skills/workflow/adhd-workflow/SKILL.md` trigger-phrase hardening, not frontmatter deletion.

2. **`/refine` retirement.** Proposal claimed ADR-002 lists `/refine` among "7 shims slated for removal at v3.0.0." **Contradiction found in the repo itself:** ADR-002's own Context section says `/refine` is "a separate consolidation" from the six ADHD-workflow shims (`done`/`recap`/`next`/`focus`/`stuck`/`spec-review`). But `commands/workflow/refine.md`'s own header claims it's "one of seven... commands being consolidated... under the v2.34.0 → v3.0.0 migration (ADR-002)." **Decision:** fix `refine.md`'s self-description to match ADR-002's actual position before deciding anything about retirement — the contradiction, not the retirement, is the real bug.

3. **New `/craft:workflow:context` command** (paste-ready Chat status block). **Dropped entirely** — no demonstrated craft-specific use case; the Chat-priming need belongs to research-repo workflows (`savant`), not craft development.

4. **`prompt-refiner` naming-collision note** (Chat allegedly has a same-named, differently-scoped skill). Unverifiable from this repo — external claim about a different Claude surface. **Decision:** add the clarifying note to `skills/workflow/prompt-refiner/SKILL.md`, but hedge the phrasing ("Chat may have...") rather than asserting it as confirmed fact.

5. **AI-origin commit trailer.** Proposal's format (`Co-authored-by: Claude <noreply@anthropic.com>`) conflicts with every existing commit in this repo's history (`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`, per global CLAUDE.md). **Decision:** use the existing convention; no new format needed.

---

## 3. Deletions

| Command | Reason |
|---|---|
| `code:quota` | Redundant premise was itself wrong (verified: `orchestrate.md` only *references* quota as an external step, has no internal SAFE/TIGHT/DEFER gate) — but decided to delete anyway and **fold the SAFE/TIGHT/DEFER logic directly into `orchestrate.md`** as a first-class pre-flight step. Real feature work porting the estimate logic, not a drive-by deletion. |
| `code:smart-help` | Unused; `hub` already covers command discovery. |
| `~/.claude/commands/hub.md` (personal-level, not part of craft) | **Done** — deleted during this session. Generic, project-agnostic, no craft-specific logic; superseded by `/craft:hub`. |

---

## 4. Moves

| From | To | Notes |
|---|---|---|
| `code:ci-fix`, `code:ci-local` | `ci:fix`, `ci:local` | Full CI-command consolidation — one namespace (`ci:`) for all 8 CI-related commands (6 existing + these 2), since `ci-fix`/`ci-local` are dev-loop pre-push operations but still fundamentally CI concerns. |
| `workflow:adhd-guide` | `skills/workflow/adhd-workflow/references/adhd-guide.md` | Pure reference prose (524 lines, no arguments/behavior) — not a command. Follows the `references/` pattern ADR-002 established for `done.md`'s detail. Drops command count by one. |
| `workflow:task-cancel`, `task-output`, `task-status` | new `task:` namespace | Self-contained trio about background-task lifecycle, distinct from the ADHD-session-workflow group they currently sit beside. **Flagged, not urgent** — unused by the repo owner currently. |

**Correction note:** `test.md` lives at `commands/code/test.md` already (confirmed during the `code:` namespace audit) — it was never a root command, so no "root → code:" move is needed. Ignore any earlier reference in this session's conversation log implying `test` was being moved *from root*; it was already correctly placed. (No action item here.)

---

## 5. Merges / consolidations (real refactor work — each is its own PR, not a rename)

| Merge | Scope |
|---|---|
| `code:release-watch` + `code:desktop-watch` | Near-duplicate purpose (both track upstream Claude release channels for plugin-integration relevance). Merge into one command with `--target=code\|desktop\|both`. |
| `docs:` 9-generator cluster (`api`, `guide`, `help`, `prompt`, `quickstart`, `site`, `tutorial`, `website`, `workflow`) | Consolidate into `/craft:docs:generate <type>`. **Caveat surfaced during the grill and accepted as a known tradeoff:** a sample read of `guide`/`quickstart`/`api` showed genuinely distinct internal logic (orchestration-of-other-commands vs. template-fill vs. OpenAPI-specific sub-actions) — this is a thin-dispatcher consolidation for discoverability, not a code-sharing win like `code:test`'s shared runner. Touches all 9 files plus their mutual "See Also" cross-references. |
| `skills/docs/navigation/` → merge into `skills/docs/site-management/` | One skill instead of two backing the `site:` namespace. **Dependency to preserve:** `docs:nav-update` also points at `skills/docs/navigation/` today — the merge must keep that reference working, not just the two `site:` shims (`add`, `nav`) that prompted the merge. |

---

## 6. Renames (dedicated PR — largest blast radius discussed)

| Rename | Scope | Note |
|---|---|---|
| `orchestrate` → `orch` (namespace **and** root command) | **122 files** reference `craft:orchestrate` — by far the largest change surface of anything in this spec (compare: `/refine`'s move touches ~11). | `--orch` already exists as a flag name in 9 files (e.g. brainstorm's handoff flag) — the short form is already established at the flag level; this rename only affects the slash-command name itself. **Must ship as its own isolated PR**, with a full `validate-counts.sh` + `docs-staleness-check.sh` pass — not bundled with anything else in this spec. |

Sub-namespace `orchestrate:` (`drive`, `plan`, `workflow`) stays nested as-is (under whatever the parent becomes) — no internal changes, only the parent segment renames.

---

## 7. Confirmed no-change (verified, not assumed — listed so this doesn't get re-litigated)

- **All 10 `git:` shims** (`branch`, `clean`, `git-recap`, `init`, `protect-baseline`, `protect`, `status`, `sync`, `unprotect`, `worktree`) + `guard` — single-skill-backed group (`skills/dev/git/`, confirmed exists), stays nested. `worktree`/`sync` promotion was proposed and explicitly reverted.
- **`arch:`** (`analyze`, `diagram`, `plan`, `review`) — 4 distinct, non-deprecated commands, no overlap. `arch:plan`'s coexistence with root `/craft:plan` confirmed as hierarchy (router → specific operation), not a naming collision.
- **`code:` quality/CI cluster** (`ci-fix`\*, `ci-local`\*, `lint`, `docs-check`, `test-gen`, `test`) — \*moving to `ci:`, see Section 4.
- **`code:` audit cluster** (`command-audit`, `deps-audit`, `deps-check`, `skill-standards`, `fewer-prompts`) — kept together, no split into a separate `audit:` namespace.
- **`deps-audit` vs `deps-check`** — read both in full; confirmed genuinely distinct (security/CVE scanning vs. general dependency hygiene), already designed as a cross-referencing companion pair. No consolidation.
- **`code:refactor`, `code:debug`** — straightforward, no overlap, no promotion rationale.
- **`docs:check` vs `docs:check-links`** — read both in full; initially looked like `check-links` was subsumed by `check --links-only`, but `check.md`'s own Phase 1 explicitly defers to `check-links.md` for `.linkcheck-ignore` format details, and `check-links.md` is independently called by `/craft:check`, `/craft:site:check`, and pre-commit hooks. **Shared-library relationship, not redundancy** — same pattern as deps-audit/deps-check. Keep both.
- **`dist:`** (`curl-install`, `homebrew`, `marketplace`, `pypi`, `surfaces`) — 3 confirmed-working shims → `skills/distribution/dist-extras/` (exists) + 2 standalone commands. No changes.
- **`orchestrate:` sub-commands** (`drive`, `plan`, `workflow`) — `plan` confirmed as a working shim → `skills/orchestration/plan-orchestrator/` (exists, shipped 2026-06-30); `drive`/`workflow` are distinct, non-overlapping. Kept together (parent namespace renames per Section 6, internal structure unchanged).
- **`site:`** — all 15 commands confirmed as working shims (13 → `skills/docs/site-management/`, 2 → `skills/docs/navigation/`, both exist) — except the navigation-skill merge in Section 5.
- **`workflow:` remaining shims** (`recap`, `focus`, `stuck`, `spec-review`, `insights`) — all confirmed working (`adhd-workflow`/`brainstorm-insights` skills exist), kept nested as a coherent family.

---

## 8. Investigated and resolved — NOT scope drift (reversing the original flag)

- **`utils:` namespace** (`readme-semester-progress.md`, `readme-teach-config.md`) and **`site:progress`/`site:publish`** were flagged during the interactive grill as apparent teaching/semester-specific scope drift, worth migrating to `scholar`. **Investigation found this was wrong.** README.md has a dedicated "## Teaching Mode" section (with a demo GIF) documenting it as a first-class, intentional craft capability — auto-detection via `.flow/teach-config.yml`, content validation, preview-before-publish workflow, semester tracking, ADHD-friendly dashboards. `semester_progress.py`/`teach_config.py` are actively consumed by `commands/site/publish.md`, `progress.md`, `build.md`, and `git/status.md` — not orphaned. Backed by 2,131 lines across 4 dedicated test files (`test_teaching_mode.py`, `test_teach_config.py`, `test_semester_progress.py`, `test_site_publish.py`). No migration needed; no further action.

---

## Sequencing recommendation

Roughly cheapest/lowest-risk → most expensive/highest-risk:

1. Delete `~/.claude/commands/hub.md` — **done**.
2. Fix `refine.md`'s self-description contradiction with ADR-002 (Section 2, item 2) — pure docs fix.
3. Add hedged `prompt-refiner` collision note (Section 2, item 4) — pure docs fix.
4. Adopt existing commit-trailer convention going forward (Section 2, item 5) — no file change, just stop using the proposal's format.
5. Investigate `/next` NL-triggering reliability (Section 2, item 1) — skill-quality bug, scoped investigation.
6. Root promotions batch: `next`, `done`, `refine`, `brief`, `brainstorm` (Section 1) — mechanical moves + cross-reference updates, moderate file count each.
7. `code:quota` deletion + fold into `orchestrate.md` (Section 3) — real feature work, moderate scope.
8. `ci:` consolidation (Section 4) — small, 2 files.
9. `adhd-guide` → skill reference, `task:` namespace split (Section 4) — small, mechanical.
10. Two merge/consolidation items (Section 5) — **done**, with one reversal: `docs:generate` router added (originals kept, not merged — genuinely distinct logic per file); navigation-skill merge reversed after reading both skills in full (already a correct, deliberate boundary).
11. `orchestrate` → `orch` rename (Section 6) — **done**, own dedicated commits, full validation pass (also caught and fixed a real `bump-version.sh` production bug and pre-existing hub.md count drift).
12. Follow-up investigation: `utils:`/`site:` teaching-content (Section 8) — **done**, resolved as NOT scope drift; no action needed.

**Status: all items implemented and committed** (`d27698ab` through `daf9305d` on `dev`), except the sequencing choice for `refine`'s move (Section 1) which shipped alongside the other root promotions in the same commit.
