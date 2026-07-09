# SPEC — Branch-Protection Command Consolidation

| | |
|---|---|
| **Status** | done — shipped via PR #272 (squash-merged to `dev` 2026-07-08) |
| **Created** | 2026-07-07 |
| **Owner** | dt |
| **From** | `docs/brainstorm/BRAINSTORM-branch-protection-consolidation-2026-07-07.md` (deep brainstorm, arch focus) |
| **Scope** | Fold `commands/git/guard.md` (registry CLI) and `commands/git/protect.md` (local-hook config) into `skills/dev/git/` as new Operations, matching `unprotect.md`'s already-deprecated pattern. Add a general `explain`/dry-run subcommand. Add a live-tool-call e2e test closing this session's discovered verification gap. Add an audit-then-ask wizard to Operation 8 (protect) and wire it into Operation 1 (init) for new repos. **Also thin the 4 other `commands/git/*.md` files (`status.md`, `clean.md`, `git-recap.md`, `branch.md`) that already claim `replaced-by: skills/dev/git/` but were never actually shimmed** (found during this SPEC's own review sweep — same shim-correctness problem, folded in rather than filed separately). Does **not** touch `branch-guard.sh`/`no-switch-guard.sh`'s emission mechanisms (already rejected in `SPEC-craft-guard-suite-2026-06-19.md`) or fold in `protect-baseline.md` (GitHub-side stays a separate, cross-linked layer). |

---

## 1. Overview

Branch protection in craft is split across 4 command files, 1 skill, 2 enforcement scripts, and 1
flat registry (`~/.claude/guards.json`). One of the four commands (`unprotect.md`) already migrated
to `skills/dev/git/` as Operation 10 — this SPEC completes that migration for the other three
surfaces where it makes sense, and explicitly declines to migrate the one (`protect-baseline.md`)
where the skill's own documentation already argues against collapsing.

**Trigger:** a live session needed to run `/craft:git:guard disable branch-guard` to unblock an
edit to `branch-guard.sh` itself — a command whose name/location has no discoverable relationship
to `protect`/`unprotect`, despite governing the same subsystem.

## 2. Decision record

### ✅ Adopted: fold `guard.md` + `protect.md` into `skills/dev/git/`

Both are CLI surfaces over the **same** local-hook enforcement layer `unprotect.md` already
migrated for. One skill, one place to look for "how do I change what branch-guard does."

### ❌ Rejected: unify `branch-guard.sh`/`no-switch-guard.sh` emission mechanisms

Already litigated and rejected in `SPEC-craft-guard-suite-2026-06-19.md` §2 — `exit 2`+stderr vs.
`permissionDecision` JSON are mutually exclusive channels; unifying would flip ~100-105
safety-critical test assertions for no behavioral gain. **Out of scope here, do not reopen.**

### ❌ Rejected: fold `protect-baseline.md` (GitHub-side) into the same operation set

The skill's "Branch protection layers, weakest to strongest" section already documents GitHub-side
protection as an independent layer from the local hook. Folding it into the same CLI surface as
`guard`/`protect` would imply it's configured the same way (it isn't — it's a `gh api` call against
GitHub, not a `guards.json` mutation). Keep as a separate Operation, cross-linked.

### ⚠️ Needs grill: "registry ownership" (decision #3 from the brainstorm)

The brainstorm's expert-question answer says `guards.json` should "move under skill ownership,"
but `branch-guard.sh`/`no-switch-guard.sh` read it directly and synchronously at hook-invocation
time — there is no skill/LLM in that path, and there structurally can't be (a PreToolUse hook fires
before any model turn). The only meaningful interpretation: **the skill's new Operation 11 becomes
the sole sanctioned way to *mutate* the registry** (already true in practice — `guard.md`'s
implementation already goes through `jq`, never raw `cat >`), formalized as the skill's contract
rather than a command's. The read path is unchanged. **Flag this precisely in the grill session** so
the distinction between "mutation surface" and "read path" doesn't get lost.

## 3. Architecture

```mermaid
flowchart TB
    subgraph "skills/dev/git/ (consolidated)"
      OP8["Op 8: branch-guard config<br/>(absorbs protect.md: level/show/reset/no-hard-deny)"]
      OP9["Op 9: GitHub-side baseline<br/>(cross-link only — protect-baseline.md unchanged)"]
      OP10["Op 10: session bypass<br/>(unprotect.md — already migrated)"]
      OP11["Op 12 (NEW — renumbered from the brainstorm's "Op 11" to avoid collision with the existing Op 11 "Reference Docs"): registry CLI<br/>list/status/enable/disable/profile/explain/test<br/>(absorbs guard.md)"]
    end
    OP11 -->|jq mutate, sole sanctioned writer| REG["~/.claude/guards.json"]
    REG -->|direct read, hook-invocation time,<br/>no LLM in this path| BG["branch-guard.sh"]
    REG -->|direct read, hook-invocation time,<br/>no LLM in this path| NSG["no-switch-guard.sh"]
    OP11 -->|NEW: explain/dry-run,<br/>generalizes no-switch-guard's existing explain| BG
    OP11 -->|explain/dry-run| NSG
```

**Command-surface delta:**

| Before | After |
|---|---|
| `commands/git/guard.md` (446 lines, standalone) | Thin shim → `skills/dev/git/` Op 12, OR deleted if no shim precedent needed (decide in grill) |
| `commands/git/protect.md` (212 lines, standalone) | Thin shim → `skills/dev/git/` Op 8 (extends existing Op 8) |
| `commands/git/unprotect.md` (138 lines, deprecated) | Unchanged — already a thin shim |
| `commands/git/protect-baseline.md` (~157 lines) | Unchanged — cross-linked from the skill, not folded |
| `~/.claude/guards.json` | Unchanged file, but skill Op 12 becomes the documented sole mutator |
| `commands/git/status.md` (453 lines) | Thin shim → Op 3 (§4.7) |
| `commands/git/clean.md` (85 lines) | Thin shim → Op 4 (§4.7) |
| `commands/git/git-recap.md` (508 lines) | Thin shim → Op 7; pedagogical content moves to `skills/dev/git/references/learning-guide.md` (§4.7) |
| `commands/git/branch.md` (483 lines) | Thin shim → Op 4/Op 2 (§4.7) |

## 4. Adversarial-review + refactor-audit requirement (added post-brainstorm)

Before implementation, run two independent review passes — **do not build directly from this
SPEC without them**:

1. **Adversarial review of the consolidated design** — use the **backend-designer** skill/agent to
   stress-test where the consolidated Operations should live (skill vs. script vs. new standalone
   command), whether Op 12's dry-run/`explain` design actually generalizes cleanly across both
   hooks' divergent emission mechanisms (see rejected-unification note above — the CLI can present
   a unified `explain` output even though the hooks emit differently; verify this is genuinely
   true and not hand-waved).
2. **Code-reviewer audit of current state** — use the **code-reviewer** skill/agent to review
   `branch-guard.sh`, `no-switch-guard.sh`, `guard.md`, `protect.md` as they stand today (not the
   proposed design) for bugs, dead code, or inconsistencies that should inform the consolidation
   rather than get carried forward unexamined. Also fold in a broader ask from this session: **audit
   the full `commands/git/*.md` set** (`worktree.md`, `status.md`, `init.md`, `clean.md`,
   `git-recap.md`, `sync.md`, `branch.md`, plus the 4 protection commands) for refactor
   opportunities beyond branch-protection specifically — report separately, don't block this SPEC
   on unrelated findings.

Both passes route through `--orch` (this skill does not spawn agents itself, per its own
no-in-skill-delegation design — see `skills/workflow/brainstorm/SKILL.md` "Going Deeper").

## 4.5. Audit-then-ask wizard (added post-brainstorm, user request)

Two new interactive behaviors, both using `AskUserQuestion` (gap-diff-then-ask, never silent
apply and never silent skip):

1. **Operation 8 (branch-guard config, absorbs `protect.md`) gains an `--audit` flag** (or runs
   this by default when invoked with no args): read the repo's current local-hook config
   (`guards.json` + any per-repo `.claude/branch-guard.json` override) *and* GitHub-side protection
   state (reuse Operation 9 / `protect-baseline.md`'s existing `gh api` check — do not
   re-implement), diff against craft's recommended baseline, and walk the user through each gap
   one `AskUserQuestion` at a time (Recommended-first, one question per gap — matches this
   session's own grilling pattern, not a single dump of every gap at once).
2. **Operation 1 (Repo Init — the full repo/project scaffolding workflow behind
   `commands/git/init.md`, not the bare `git init` shell command) offers to run the same
   audit/wizard immediately after creating a new repo**, via one `AskUserQuestion` ("Set up
   branch protection now?" Recommended-first), instead of leaving a freshly-scaffolded repo
   unprotected until someone remembers to run `protect` later. This is the same wizard from (1),
   invoked at a different trigger point — not a second implementation.

**Explicitly not in scope:** auto-applying any protection change without a per-gap confirm — the
whole point of this addition is asking, not automating past the smart-mode always-confirm
mistake this session already made and reverted once today.

**Cross-reference to §4's `commands/git/*.md` sweep:** that full-repo-commands audit already
covers `worktree.md`/`status.md`/`clean.md`/`git-recap.md`/`sync.md`/`branch.md` alongside the 4
protection commands — the code-reviewer pass should explicitly check whether any of those other
commands have a similar "silently acts where it should ask" gap (the same shape of gap this §4.5
addition fixes for `protect`/`init`), not just look for unrelated refactor opportunities.

## 4.6. Review findings (backend-designer + code-reviewer, 2026-07-07)

Both passes from §4 ran. Findings that change this SPEC, resolved inline; findings that don't
change it, noted for the grill.

### Resolved now (mechanical fixes applied to this SPEC)

- **Op numbering collision** — `skills/dev/git/SKILL.md` already has an Operation 11 ("Reference
  Docs"). Every "Op 11 NEW" reference above is renumbered to **Op 12**. This was a real bug, not a
  style nit — left unfixed it would have corrupted the Integration table and any cross-reference
  by number.
- **"Sole mutator" scope corrected** — confirmed `branch-guard.sh`'s `CONFIG_FILE=".claude/branch-guard.json"`
  (per-repo, protection *level*) is a **separate file** from `~/.claude/guards.json` (global,
  enable/mute *state*). Op 12's "sole sanctioned mutator" claim applies **only** to `guards.json`.
  `.claude/branch-guard.json` is written directly by Op 8 (`protect.md`'s `--level`/`--reset`) and
  stays that way — this is not a gap, but §2's phrasing must say "sole mutator of `guards.json`,"
  not "the registry," to avoid conflating the two files going forward.
- **`guard.md` disposition decided: thin shim, not deletion.** Both scripts hardcode remediation
  strings referencing `/craft:git:guard disable <name>` (`branch-guard.sh` and `no-switch-guard.sh`
  each contain a literal string like this). Deleting `guard.md` outright would require a
  coordinated same-PR update to both enforcement scripts' hardcoded strings — keeping it as a thin
  shim (matching `unprotect.md`'s precedent) avoids that coupling. §3's command-surface delta table
  updated accordingly (no longer "OR deleted").

### Resolved by grill (2026-07-07 — see `GRILL-branch-protection-consolidation-2026-07-07.md`)

1. **Registry-ownership enforcement**: descriptive only, not enforced with a test. Matches
   current practice; revisit only if a second `guards.json` writer actually appears.
2. **Baseline artifact**: build it as part of THIS SPEC, not as a blocking prerequisite. Extract a
   single `baseline.json` (recommended level per branch-role + recommended GitHub settings) from
   `branch-guard.sh`'s existing auto-detect case statement and `protect-baseline.md`'s existing
   payload — both already exist, this is a mechanical extraction, not new design work. Op 8's
   `--audit` flag diffs against this artifact.
3. **`explain`/dry-run ground truth**: build the `--classify` / `GUARD_DRY_RUN=1` mode now (in
   this SPEC's delivery), not later. Each script gains an internal mode that runs its real
   classification logic and prints the tier without blocking, reusing the existing
   `block()`/`ask()` functions. This makes the Test Plan's dogfood tier assert against ground
   truth instead of LLM narration.
4. **`protect.md`'s `$CONFIG`/`$CONFIG_FILE` bug**: fix during the fold into Op 8's actual
   implementation (not a separate pre-fix) — don't copy the drift verbatim.
5. **`guard.md`'s hardcoded registry table**: Op 12 generates this table from `guards.json` at
   render time instead of hardcoding it, so a third registered guard doesn't go stale in the docs.
6. **Stray-code check — CONFIRMED CLEAN.** `git diff 7195d5c9..HEAD -- scripts/branch-guard.sh`
   (pre-session baseline vs. current): 38 lines total, entirely the intentional `GIT_CTX_DIR`
   resolution block. The smart-mode tier logic (`_low_note`/`_confirm` call sites for
   `edit_existing`, `write_md`, `write_extensionless`, `write_test`, `write_existing` ×2) is
   byte-identical to the pre-session state. Today's always-confirm experiment and its revert left
   zero drift.

### Secondary sweep (commands/git/*.md beyond branch-protection) — complete, findings below

Follow-up review of `worktree.md`, `status.md`, `clean.md`, `git-recap.md`, `sync.md`, `branch.md`
(the 6 the first pass didn't reach) found:

- **No silent-action gaps** (confidence ≥80) matching §4.5's pattern. `worktree.md` and `branch.md`
  already gate every destructive action with an explicit confirm; `sync.md`/`status.md`/
  `git-recap.md` are either thin shims or read-only. `clean.md` governs **branch** deletion, not
  the `git clean -f` working-tree operation the hook gates — different operations, no conflict, but
  the doc should add a one-line disambiguation note (naming collision risk for readers, not a
  behavior bug).
- **Stale-shim drift — folded into this SPEC's delivery (2026-07-07).** All 6 files carry
  `deprecated: true, replaced-by: "skills/dev/git/"` frontmatter, but only `worktree.md` and
  `sync.md` are actually thin shims — `status.md` (453 lines), `clean.md` (85 lines),
  `git-recap.md` (508 lines), and `branch.md` (483 lines) still ship full standalone
  implementations despite claiming to have migrated, duplicating logic the skill's
  Cross-Operation Patterns section (or the corresponding Operation) already states once. Originally
  scoped out as unrelated to branch-protection; the user asked to fold it in anyway since it's the
  same shim-correctness problem this SPEC already exists to fix for `guard.md`/`protect.md`, just
  found on 4 more files during the same sweep. Added as §4.7 below.

## 4.7. Stale-shim cleanup (folded in, 2026-07-07)

Four files claim `replaced-by: "skills/dev/git/"` but were never actually thinned. Bring them to
the same standard as `unprotect.md`/`worktree.md`/`sync.md`:

| File | Lines today | Keep in shim | Move / drop |
|---|---|---|---|
| `status.md` | 453 | Flag contract + guard-status display pointer | Teaching-mode box-drawing literals → generate from the skill's existing prose table, don't hardcode twice |
| `clean.md` | 85 | Flag contract | Safety rules (protected-branch exclusion, uncommitted-skip, confirm-before-delete) → collapse to a pointer at Op 4 + Cross-Operation Patterns, don't restate — also add the one-line disambiguation note from §4.6 (this `clean` is branch deletion, not `git clean -f`) |
| `git-recap.md` | 508 | Flag contract + recap-output pointer | "Learning & Practice" pedagogical section → move to `skills/dev/git/references/learning-guide.md` (already the cross-referenced home for this content per Operation 11); do not leave a second copy behind |
| `branch.md` | 483 | Flag contract + action list | Delete-safety checks (merged-check, confirm) → collapse to Op 4/Cross-Operation-Patterns pointer, same pattern as `clean.md`; "Branch Patterns" naming-convention prose → generic reference doc, not per-command |

No behavior change intended — this is doc/shim correctness only (make the frontmatter's claim
true), same risk class as `guard.md`/`protect.md`'s fold. Silent-action posture in all 4 already
checked clean in §4.6 (no new confirm gates needed here, only de-duplication).

## 5. Delivery scope (escalated per brainstorm decision #6)

Full cycle, not a direct PR: `/craft:grill` (**done 2026-07-07** — see
`GRILL-branch-protection-consolidation-2026-07-07.md`) → `superpowers:writing-plans` →
subagent-driven-TDD build. Rationale: this touches enforcement-critical hooks active across every
repo on the machine — same rigor bar as the v2.40.0 Guard Suite build
(`SPEC-craft-guard-suite-2026-06-19.md`).

**Grill decisions on staging/granularity:** §4.7's shim cleanup ships in the **same PR** as the
branch-protection consolidation (one coherent PR, not split) — the same plan also stays **one
combined plan**, not two sequenced ones; subagent-driven-TDD already parallelizes independent
tasks within a single plan, so splitting would only add coordination overhead for work shipping
together anyway.

## 6. Test Plan

Tiers (new command/skill operation + cross-command data flow + external dependency `jq`):

- **Unit** — registry read/write helpers (mute-expiry math already covered by existing
  `test_branch_guard.sh`; new: Op 12's `list`/`status`/`explain` output formatting)
- **Integration** — Op 12 CLI mutation → `guards.json` change → `branch-guard.sh`/
  `no-switch-guard.sh` observe the change on their next invocation
- **E2E (closes this session's gap)** — an actual `Edit`/`Bash` tool call on a protected branch
  visibly surfaces the confirm prompt through the real PreToolUse path, not just
  `echo json | bash script.sh`
- **Dogfood** — run the new `explain`/dry-run subcommand against real commands from this session's
  transcript that should have confirmed and didn't (the cross-repo `cwd` false-negative, the
  post-revert re-test)
- **Count-cascade** — if `guard.md`/`protect.md` become thin shims (not deletions), command count
  is unchanged; if deleted outright, count decreases — run `bump-version.sh --counts-only` either way
- **Shim-correctness (new, §4.7)** — for each of `status.md`/`clean.md`/`git-recap.md`/`branch.md`,
  a dogfood check that the shim's documented behavior still matches what the corresponding skill
  Operation actually does (prevents the exact drift this SPEC found: frontmatter claiming a
  migration that never happened)

## 7. Documentation

- [ ] Rewrite `docs/guide/guard-suite.md` to point at the consolidated skill operations
- [ ] Update `commands/git/docs/refcard.md` for the collapsed command surface
- [ ] No new Mermaid doc needed beyond §3's architecture sketch
- [ ] Move `git-recap.md`'s "Learning & Practice" section into `skills/dev/git/references/learning-guide.md` (§4.7) — verify no duplicate content remains in either place after the move

## 8. Next steps

1. `--orch` → backend-designer (design stress-test) + code-reviewer (current-state audit, both
   scoped and full-`commands/git/*` sweep) — **done 2026-07-07**, findings folded into §4.6/§4.7.
2. `/craft:grill` on this SPEC, foregrounding §2's registry-ownership ambiguity, §4.6's 5 open
   decisions, and §4.7's stale-shim cleanup scope.
3. `superpowers:writing-plans` → subagent-driven-TDD implementation (now covering both the
   branch-protection consolidation and the 4-file shim cleanup in one build).
