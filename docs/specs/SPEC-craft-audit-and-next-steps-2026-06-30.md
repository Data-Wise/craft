# SPEC: Craft audit findings and next-steps roadmap (post token-usage-reduction branch)

**Status:** DRAFT (proposed) · **Date:** 2026-06-30 · **Driver:** Cowork session — token-usage-reduction work surfaced systemic gaps worth tracking as their own program
**Branch:** `feature/token-usage-reduction` (5 commits, unmerged) · **Related:** ADR-002 (done-command-skill-consolidation), governance R04 (`no_drifted_copy.py`)

---

## 1. Problem

The `feature/token-usage-reduction` branch started as a narrow fix (model-pin orchestrator agents, shrink `/refine`, redesign `/brainstorm`) but surfaced three systemic problems that are bigger than that branch's scope:

1. **The deprecated-command-rich-body pattern (ADR-002) is unmonitored.** ADR-002 documented one instance (`/done`) and fixed it, but explicitly deferred "the other six" commands as a known-recurring risk with no follow-up mechanism. This session found and fixed two more instances (`/refine`, `/brainstorm`) by hand, and a full repo scan now shows **56 deprecated commands with no automated check for the pattern at all** — governance has R04 for cross-repo canon drift but nothing for in-repo command-vs-skill drift.
2. **Count-of-record drift is multi-source and silently compounds.** `validate-counts.sh` checks `plugin.json` only. `bump-version.sh --verify` checks `docs/REFCARD.md` separately. Neither checks the 10+ other files (`README.md`, `CLAUDE.md`, `docs/*.md`, `mkdocs.yml`, `package.json`, `marketplace.json`) that also hardcode counts in varying phrasings ("40 skills", "Skills (40 total)", "40 auto-activating skills"). This session found `dev` was already 4 skills over its documented count *before* any of this session's changes — meaning the drift predates and is independent of any single branch.
3. **No CI signal connects "did the full test suite pass" to "is this branch mergeable."** This branch's redesign commit (`039530b5`) shipped with two real test regressions for several hours of session time before anyone ran the full ~2056-test suite against it — only caught because this session was explicitly asked to verify, not because any automated gate would have caught it.

This spec captures what's now known, proposes concrete next steps, and recommends an audit cadence so these don't recur silently.

## 2. What's already fixed (this session, for context)

| Item | Branch commit | Status |
|---|---|---|
| Orchestrator agent model pinning + resilience extraction | `9abdd1b1` | Committed, tested |
| `/refine` → thin shim (631→42 lines) | `0e076e66` | Committed, tested |
| `/brainstorm` fictional subagent_type fix | `c7f9010e` | Committed, tested |
| `/brainstorm` full redesign (split insights, 4→2 decision points, remove in-skill agent spawn) | `039530b5` | Committed, tested |
| Count drift (40→42), hub doc sync, 2 real test regressions found+fixed | `81750e05` | Committed, tested |

Full suite (~2056 tests, chunked due to sandbox limits), `validate-counts.sh`, `bump-version.sh --verify`, `docs-staleness-check.sh` all clean as of `81750e05`. Not yet merged to `dev` — blocked on GitHub auth (no working token in this session's connector) and a human diff review.

## 3. Locked findings (data, not speculation)

### 3.1 Deprecated-command body-size audit (full scan, this session)

56 commands carry `deprecated: true` + a `replaced-by:` skill pointer. Ranked by **lines-in-command ÷ lines-in-target-skill** (a proxy for "how much detail could be silently lost at v3.0.0 cutover," per the ADR-002 failure mode):

| Rank | Command | Lines | Target skill | Skill lines | Ratio |
|---|---|---|---|---|---|
| 1 | `commands/check.md` | 1132 | `skills/check/` | 127 | **8.9** |
| 2 | `commands/workflow/task-cancel.md` | 508 | `skills/workflow/task-management/` | 90 | **5.6** |
| 3 | `commands/workflow/task-output.md` | 467 | `skills/workflow/task-management/` | 90 | **5.2** |
| 4 | `commands/git/worktree.md` | 1010 | `skills/dev/git/` | 250 | **4.0** |
| 5 | `commands/docs/claude-md/edit.md` | 635 | `skills/docs/claude-md/` | 161 | **3.9** |
| 6 | `commands/workflow/task-status.md` | 348 | `skills/workflow/task-management/` | 90 | **3.9** |
| 7 | `commands/check/gen-validator.md` | 447 | `skills/check/` | 127 | **3.5** |
| 8 | `commands/git/docs/safety-rails.md` | 723 | `skills/dev/git/` | 250 | **2.9** |
| 9 | `commands/git/docs/learning-guide.md` | 722 | `skills/dev/git/` | 250 | **2.9** |
| 10 | `commands/site/create.md` | 741 | `skills/docs/site-management/` | 275 | **2.7** |

Full 56-row table reproducible via the script in §5.1 (not yet committed as a script — see next steps).

**Read on this data:** `skills/dev/git/` is the single highest-risk target — it's the `replaced-by:` destination for at least 4 large commands (`worktree.md` 1010, `init.md` 597, `sync.md` 539, `docs/safety-rails.md` 723, `docs/learning-guide.md` 722, `docs/undo-guide.md` 594) totaling **4185 source lines** funneling into one 250-line skill. That's not "thin shim, canonical detail in skill" — that's six commands' worth of detail with nowhere to go. This matches what the earlier in-session subagent audit flagged as "Major" gaps in the git commands, now with a precise number behind it.

`commands/check.md` at ratio 8.9 wasn't flagged by the earlier audit (it focused on git/site) — worth a fresh look since it's actually the single worst ratio in the repo.

### 3.2 Count-of-record sources (now reconciled, but multi-source and fragile)

Confirmed this session: count claims live in at least 16 files across 4 distinct phrasing patterns, checked by 2 different scripts that don't share a source of truth:

- `validate-counts.sh` → reads `.claude-plugin/plugin.json` description string only.
- `bump-version.sh --verify` → reads `docs/REFCARD.md`'s `## Skills (N total)` header only, independently.
- Nothing checks `README.md`, `CLAUDE.md`, `docs/index.md`, `docs/QUICK-START.md`, `docs/architecture.md`, `docs/commands.md`, `docs/guide/*.md`, `mkdocs.yml`, `package.json`, `marketplace.json`, or `docs/tutorials/TUTORIAL-code-skill-standards.md`'s worked example — all of which carry a count claim, all fixed by hand this session.

### 3.3 Test-regression visibility gap

`039530b5` (the brainstorm redesign) shipped 2 commits before anyone ran more than the 9 directly-relevant tests against it. The full suite would have caught both regressions (`test_skill_trigger_phrases_unique`, `test_refine_flag_documented`) immediately. No existing craft mechanism runs the full suite automatically before a commit lands on a feature branch — `/craft:check` and pre-commit hooks exist but weren't invoked mid-session here (this was sandbox-plumbing-built commits, which is itself an unusual path — see §4.3).

## 4. Candidate next steps

### 4.1 Governance rule: command/skill body-ratio check (new, R-series candidate)

Add a governance checker (`governance/checks/no_oversized_deprecated_command.py`, following the existing R03/R04 pattern) that:
- Scans all `commands/**/*.md` with `deprecated: true`.
- For each, resolves `replaced-by:` and compares line counts.
- WARNs (not blocks, per ADR-003's advisory-not-hard-gate precedent) above a configurable ratio threshold (suggest starting at 2.0 — would currently flag ~20 of 56 commands).
- Surfaces in `/craft:check` and the SessionStart visibility hook, same as R01-R04.

This directly generalizes ADR-002's fix into an ongoing signal instead of a one-time manual catch.

### 4.2 Consolidate the count-of-record check

Two options, not mutually exclusive:
- **(a) Minimal:** extend `validate-counts.sh` to also check the ~14 files this session fixed by hand, using the same regex-sweep approach used here (`(?i)40\b.{0,25}skill|skill.{0,25}\b40\b` generalized to the live count). Cheapest, but adds a second hardcoded file list to maintain.
- **(b) Structural:** designate ONE file (likely `plugin.json`) as the single source of truth, and have every other file's count claim either (i) get removed in favor of a link to the live count, or (ii) get regenerated by a `docs-staleness-check.sh --fix` pass rather than hand-maintained prose. More invasive, bigger payoff — closes the class of bug instead of widening the existing patch.

Recommend (b) if there's appetite for the larger change; (a) as a stopgap otherwise.

### 4.3 Investigate why this session's commits required manual git plumbing

Every commit on `feature/token-usage-reduction` was built via `git commit-tree` + manual ref writes because the sandbox couldn't `unlink()` files under `.git/` (lock files, temp objects, worktree metadata). This is almost certainly a property of *this* Cowork sandbox specifically, not a craft repo issue — but it's worth a quick confirmation on your actual Mac that normal `git worktree add` + `git commit` works cleanly there (it should), simply to close the loop and confirm nothing about the repo itself causes this.

### 4.4 Schedule the 49-remaining-command port-before-v3.0.0 decision

Restating the open item from the earlier audit, now with the ratio data attached: before any v3.0.0 cutover that deletes deprecated command bodies, the top ~10 by ratio (§3.1) need either (a) their detail ported into the target skill, or (b) an explicit, documented decision that the detail is intentionally dropped (mirroring what was done for `/refine`'s clipboard/background-task features this session — a real precedent for "drop and document" being an acceptable outcome, not every gap needs porting).

### 4.5 Decide on `skills/dev/git/`'s structure specifically

Given §3.1's finding that 6 commands (4185 lines) all point at one 250-line skill, this single skill is the highest-leverage place to start. Worth its own focused session: read all 6 source commands, decide what's genuinely shared procedure (belongs in the skill) vs. command-specific detail (belongs in `references/`, following the `skills/release/references/` precedent already established in the repo).

## 5. Audit recommendations (cadence and method)

### 5.1 Reusable audit script (committed this session)

The ratio table in §3.1 is reproducible via `scripts/audit-deprecated-commands.py` (committed alongside this spec):

```bash
python3 scripts/audit-deprecated-commands.py --threshold 2.0
python3 scripts/audit-deprecated-commands.py --json --threshold 2.0   # for CI/scripting
```

Exit 0 if nothing exceeds the threshold, exit 1 if anything is flagged (WARN signal — not wired into any gate yet, see §5.3). This is the stopgap; §4.1 proposes promoting it into a proper `governance/checks/` module with the standard FIXTURE+LIVE dual-mode pattern once there's a fixture to selftest against.

### 5.2 Suggested audit cadence

| Audit | Frequency | Mechanism |
|---|---|---|
| Count-of-record consistency | Every release (already happens via `validate-counts.sh` + `bump-version.sh --verify`) | Existing, just needs scope-widening per §4.2 |
| Deprecated-command ratio | Quarterly, or before any v3.0.0-cutover planning session | New, per §4.1 |
| Full test suite against feature branches | Before every merge to `dev`, not just at release | Process discipline — consider a pre-PR hook or `/craft:check --for pr` enforcing this explicitly if it doesn't already |
| Skill/agent doc coverage (`docs/skills-agents.md` completeness) | Per new skill/agent added | `docs-staleness-check.sh`'s `skill_agent_coverage` phase already does this — just needs to be run, which this session confirmed it wasn't for `orchestrator-resilience` until now |

### 5.3 What NOT to do

Don't turn §4.1's new governance rule into a hard release gate immediately. ADR-003 already established the precedent (release-drift is advisory, not hard-blocking) for good reason — a new check needs a soak period to confirm it doesn't false-positive before it can block anything. Land it as WARN-only, same as R05/R06 are advisory today.

## 6. Open questions (not locked — for the next session to decide)

- Does the `skills/dev/git/` consolidation (§4.5) happen as part of the v3.0.0 cutover, or independently and earlier?
- Is the governance rule in §4.1 worth building now, or does it wait until after `feature/token-usage-reduction` merges (avoiding scope creep on an already-large branch)?
- Should `docs/REFCARD.md` and `plugin.json` be merged into one source (§4.2b), or is the duplication acceptable given they serve different audiences (terminal users vs. plugin manifest)?

## 7. Out of scope for this spec

- Actually implementing any of §4's items — this spec is a findings + roadmap document, not an implementation plan. A future `/craft:plan:feature` or `/craft:grill` session should turn whichever item is prioritized into its own spec with locked decisions.
- The GitHub PR for `feature/token-usage-reduction` itself — blocked on auth, tracked separately in the branch's own review doc (`REVIEW-token-usage-reduction.md`, not committed).
