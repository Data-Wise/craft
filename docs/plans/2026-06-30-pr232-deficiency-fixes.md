# PR #232 Deficiency Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 8 confirmed/plausible findings from the PR #232 adversarial review, correct the
token-reduction overclaims found in follow-up review, and close the PR's own admitted validation
gap (no real `/usage` measurement) before merging `feature/token-usage-reduction` to `dev`.

**Architecture:** All changes are documentation/test-fixture edits in the existing
`craft-review` worktree (already on `feature/token-usage-reduction`). No production code paths
change. Each task is independently committable; none depend on Track B
(`2026-06-30-namespace-token-probe.md`), which operates on a separate spec file.

**Tech Stack:** Markdown, YAML frontmatter, pytest, `gh` CLI.

## Global Constraints

- **Working directory for every task:** `/Users/dt/projects/dev-tools/craft-review` (NOT
  `/Users/dt/projects/dev-tools/craft` — that's the `dev` checkout). Verify with
  `git -C /Users/dt/projects/dev-tools/craft-review branch --show-current` before each task; must
  print `feature/token-usage-reduction`.
- Commit messages: Conventional Commits (`fix:`, `docs:`, `test:`).
- Never use `git commit --amend` — always a new commit (per project convention).
- Full verification gate before merge: `python3 -m pytest tests/` (full suite, not a subset —
  this branch's own history shows scoped checks miss regressions), `./scripts/validate-counts.sh`,
  `./scripts/bump-version.sh --verify`.

---

### Task 1: Mechanical count/doc fixes (hub.md ×2, REFCARD.md, skills-agents.md)

**Files:**

- Modify: `commands/hub.md:657`
- Modify: `docs/commands/hub.md:601`
- Modify: `docs/REFCARD.md:8`
- Modify: `docs/skills-agents.md:94`

**Interfaces:** None (pure doc content, no code consumers).

- [ ] **Step 1: Fix the Workflow skill-category row in both hub.md copies**

Current (both files, same text):

```
| Workflow | 7 | **prompt-refiner** (default-on for brainstorm/do/plan/grill; `--no-refine` to skip), adhd-workflow, **brainstorm** (test plan + Documentation section default-on; `--no-tests`/`--no-docs` to skip), **brainstorm-insights** (session friction reports, split from brainstorm) |
```

(docs/commands/hub.md:601 has the shorter variant: `| Workflow | 7 | **prompt-refiner** (NEW — \`--refine\`), adhd-workflow, **brainstorm**, **brainstorm-insights** (split from brainstorm) |`)

In `commands/hub.md:657`, replace with:

```
| Workflow | 5 | **prompt-refiner** (default-on for brainstorm/do/plan/grill; `--no-refine` to skip), adhd-workflow, **brainstorm** (test plan + Documentation section default-on; `--no-tests`/`--no-docs` to skip), **brainstorm-insights** (session friction reports, split from brainstorm), task-management (background task lifecycle) |
```

In `docs/commands/hub.md:601`, replace with:

```
| Workflow | 5 | **prompt-refiner** (NEW — `--refine`), adhd-workflow, **brainstorm**, **brainstorm-insights** (split from brainstorm), task-management |
```

- [ ] **Step 2: Fix REFCARD.md stale Commands count**

`docs/REFCARD.md:8`, current:

```
│  Commands: 112 | Agents: 8 | Skills: 43                     │
```

Replace with:

```
│  Commands: 117 | Agents: 8 | Skills: 43                     │
```

- [ ] **Step 3: Fix skills-agents.md Orchestration header count**

`docs/skills-agents.md:94`, current:

```
### Orchestration (5)
```

Replace with:

```
### Orchestration (6)
```

- [ ] **Step 4: Verify the fixes**

```bash
cd /Users/dt/projects/dev-tools/craft-review
grep -c "task-management" commands/hub.md docs/commands/hub.md
# Expected: 1 each
grep "Commands:" docs/REFCARD.md
# Expected: "Commands: 117 | Agents: 8 | Skills: 43"
grep "### Orchestration" docs/skills-agents.md
# Expected: "### Orchestration (6)" then later "### Orchestration Agents (2)"
./scripts/validate-counts.sh
# Expected: clean exit, no count mismatches reported for these files
```

- [ ] **Step 5: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add commands/hub.md docs/commands/hub.md docs/REFCARD.md docs/skills-agents.md
git commit -m "fix(docs): correct stale counts in hub.md, REFCARD.md, skills-agents.md

Workflow skill-category row said 7 with only 4 named (real count is 5,
task-management was missing from both). REFCARD.md's Commands figure
said 112 while every other doc this branch touches says 117.
skills-agents.md's Orchestration header still said (5) after this
branch added the orchestrator-resilience row, making it 6.

Found in PR #232 adversarial review."
```

---

### Task 2: Fix ADR-002 routing-table contradiction

**Files:**

- Modify: `docs/adr/ADR-002-done-command-skill-consolidation.md:16`

**Interfaces:** None.

**Context:** `commands/workflow/refine.md` cites ADR-002 to justify routing `/refine` to
`skills/workflow/prompt-refiner/`, but ADR-002's own table lists `/refine` under the
`adhd-workflow` consolidation group. `prompt-refiner` is the functionally correct target — it's a
dedicated, substantial skill for prompt optimization (built in PR #215, predates this branch);
`adhd-workflow` covers session-boundary ops (done/recap/next/focus/stuck/spec-review), an unrelated
domain. The fix corrects ADR-002, not the shim.

- [ ] **Step 1: Fix the ADR-002 routing table**

`docs/adr/ADR-002-done-command-skill-consolidation.md:16`, current:

```
/done /recap /next /focus /stuck /spec-review /refine  →  skills/workflow/adhd-workflow/
```

Replace with:

```
/done /recap /next /focus /stuck /spec-review  →  skills/workflow/adhd-workflow/
/refine  →  skills/workflow/prompt-refiner/  (separate consolidation, see SPEC-refine-flag-2026-06-03.md)
```

- [ ] **Step 2: Check for and fix any other reference to the old 7-command grouping**

```bash
cd /Users/dt/projects/dev-tools/craft-review
grep -n "seven\|7 commands" docs/adr/ADR-002-done-command-skill-consolidation.md
```

If a count of "seven" commands appears elsewhere in the same file referring to this group, change
it to "six" (adhd-workflow) and note `/refine` separately. If none found, no further edit needed.

- [ ] **Step 3: Verify**

```bash
grep -n "refine" docs/adr/ADR-002-done-command-skill-consolidation.md
# Expected: /refine now appears on its own line routed to prompt-refiner, not bundled with adhd-workflow
grep -n "ADR-002" commands/workflow/refine.md
# Expected: still cites ADR-002 — now consistent with what ADR-002 actually says
```

- [ ] **Step 4: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add docs/adr/ADR-002-done-command-skill-consolidation.md
git commit -m "fix(docs): correct ADR-002 routing table for /refine

ADR-002 listed /refine under the adhd-workflow consolidation group,
but refine.md routes to (and always routed to) prompt-refiner — a
separate, pre-existing skill for a different domain. A reader
following the ADR-002 citation in refine.md to verify the routing
found the cited source contradicted it.

Found in PR #232 adversarial review."
```

---

### Task 3: Restore dogfood test coverage for brainstorm-insights

**Files:**

- Modify: `tests/test_scaffold_defaults_dogfood.py:6-7`

**Interfaces:**

- Consumes: `skills/workflow/brainstorm-insights/SKILL.md` (must contain the strings the three
  parametrized tests already check for — confirmed present at lines 102-163 per prior review).

- [ ] **Step 1: Write the failing-state check first**

```bash
cd /Users/dt/projects/dev-tools/craft-review
python3 -m pytest tests/test_scaffold_defaults_dogfood.py -v --collect-only | grep brainstorm
```

Expected output before the fix: only `skills/workflow/brainstorm/SKILL.md` and
`skills/orchestration/plan-orchestrator/SKILL.md` appear — `brainstorm-insights` is absent from
the parametrize list.

- [ ] **Step 2: Add brainstorm-insights back to the SKILLS list**

`tests/test_scaffold_defaults_dogfood.py:6-7`, current:

```python
SKILLS = ["skills/workflow/brainstorm/SKILL.md",
          "skills/orchestration/plan-orchestrator/SKILL.md"]
```

Replace with:

```python
SKILLS = ["skills/workflow/brainstorm/SKILL.md",
          "skills/workflow/brainstorm-insights/SKILL.md",
          "skills/orchestration/plan-orchestrator/SKILL.md"]
```

- [ ] **Step 3: Run the full file and confirm all three tests pass for all three skills**

```bash
cd /Users/dt/projects/dev-tools/craft-review
python3 -m pytest tests/test_scaffold_defaults_dogfood.py -v
```

Expected: 9 passed (3 tests × 3 skills), 0 failed. If `brainstorm-insights/SKILL.md` fails any of
the three assertions, that's a real gap to fix in the skill file itself before proceeding — do not
weaken the test.

- [ ] **Step 4: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add tests/test_scaffold_defaults_dogfood.py
git commit -m "test(scaffold-defaults): restore brainstorm-insights dogfood coverage

The brainstorm/brainstorm-insights split swapped brainstorm-insights
out of this parametrize list in favor of the new brainstorm/SKILL.md,
but brainstorm-insights still carries its own full copy of the
scaffold-default contract (tier-inference, --yes non-suppression,
doc-scorer reuse, count-cascade exclusion). A future edit could strip
that language from brainstorm-insights and nothing would catch it.

Found in PR #232 adversarial review."
```

---

### Task 4: Add CHANGELOG `[Unreleased]` entry for this branch's work

**Files:**

- Modify: `docs/CHANGELOG.md` (insert after line 8, before `## [2.55.0]`)
- Modify: `CHANGELOG.md` (insert after line 11, before `## [2.55.0]`, mirroring docs/CHANGELOG.md
  per this project's dual-CHANGELOG convention)

**Interfaces:** None.

- [ ] **Step 1: Insert the Unreleased entry into docs/CHANGELOG.md**

Insert immediately after line 8 (`---`) and before `## [2.55.0] — 2026-06-29`:

```markdown
## [Unreleased]

### Added

- **`skills/code/command-skill-token-efficiency/SKILL.md`** — new skill codifying the
  command-vs-skill content classification, the extract-don't-delete principle, and the
  full-suite-before-calling-it-done lesson from this branch's own regressions. Auto-triggers on
  command/skill/agent authoring. `scripts/audit-deprecated-commands.py` gained a `--pair` mode for
  authoring-time ratio checks (alongside the existing repo-wide `deprecated: true` sweep).
- **`agents/orchestrator-v2.md` model pinning** — explicit `model:` frontmatter on orchestrator
  agents (`orchestrator-v2.md`: sonnet, legacy `orchestrator.md`: haiku) instead of inheriting the
  caller's tier.

### Changed

- **`/refine` reduced to a thin shim** (`commands/workflow/refine.md`, 631→42 lines) — canonical
  behavior now lives entirely in the pre-existing `prompt-refiner` skill.
- **`/brainstorm` split** (`skills/workflow/brainstorm-insights/SKILL.md` →
  `skills/workflow/brainstorm/SKILL.md` + narrowed `brainstorm-insights/SKILL.md`) — cut decision
  points from 4 to 2, removed in-skill agent delegation (now hands off to `orchestrator-v2` via the
  existing `--orch` flag instead of spawning agents directly).
- **`agents/orchestrator-v2.md` BEHAVIOR 5 + 9 extracted** to `skills/orchestrator-resilience/SKILL.md`
  (1473→1212 lines in the agent file) — error-handling/retry reference and the execution-timeline
  template now load on agent failure or `timeline` request, not on every orchestrator-v2 invocation.

### Fixed

- Skill count drift (40→43) across `plugin.json`, `marketplace.json`, `CLAUDE.md`, `README.md`,
  `docs/REFCARD.md`, `mkdocs.yml`, `package.json`, and 8 other doc files.
- Stale `/brainstorm` examples in `commands/hub.md`, `docs/commands/hub.md`,
  `docs/skills-agents.md` describing the pre-redesign max-depth shorthand.
- `agents/orchestrator-v2.md` BEHAVIOR 9 timeline pointer (a literal `EXECUTION TIMELINE` string a
  test asserts on, dropped during the BEHAVIOR 9 extraction, restored).

```

- [ ] **Step 2: Mirror the same entry into root CHANGELOG.md**

Insert the identical block (same heading and content as Step 1) into `CHANGELOG.md` immediately
after its line 11 (`---`) and before `## [2.55.0] — 2026-06-29`.

- [ ] **Step 3: Verify the two files match**

```bash
cd /Users/dt/projects/dev-tools/craft-review
diff <(sed -n '/## \[Unreleased\]/,/## \[2.55.0\]/p' docs/CHANGELOG.md) \
     <(sed -n '/## \[Unreleased\]/,/## \[2.55.0\]/p' CHANGELOG.md)
```

Expected: no output (identical).

- [ ] **Step 4: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add docs/CHANGELOG.md CHANGELOG.md
git commit -m "docs(changelog): add [Unreleased] entry for token-usage-reduction branch

This branch's substantive work (model pinning, /refine shim,
/brainstorm split, orchestrator-resilience extraction, new
command-skill-token-efficiency skill) had no CHANGELOG entry — the
only existing CHANGELOG diff hunks backfilled unrelated historical
v2.39.0/v2.40.0 entries.

Found in PR #232 adversarial review."
```

---

### Task 5: Correct the token-cost overclaim in command-skill-token-efficiency/SKILL.md

**Files:**

- Modify: `skills/code/command-skill-token-efficiency/SKILL.md:8`

**Interfaces:** None.

- [ ] **Step 1: Fix the overclaim**

Current:

```
Grew out of `feature/token-usage-reduction` ([PR #232](https://github.com/Data-Wise/craft/pull/232)), which found and fixed real, measured token cost in `/refine` (630→42 lines), `/brainstorm` (528→112 lines), and `orchestrator-v2.md` (1473→1212 lines) — a 48% reduction in the always-loaded orchestration path. Full research and methodology: `docs/specs/SPEC-token-efficiency-research-2026-06-30.md`.
```

Replace with:

```
Grew out of `feature/token-usage-reduction` ([PR #232](https://github.com/Data-Wise/craft/pull/232)), which measured a 48% reduction in always-loaded *line count* across `/refine` (630→42 lines), `/brainstorm` (528→112 lines), and `orchestrator-v2.md` (1473→1212 lines). Line count and token count correlate but aren't identical — real `/usage` validation of the token-usage hypothesis is a separate, not-yet-completed step (see "Further reading" below). Full research and methodology: `docs/specs/SPEC-token-efficiency-research-2026-06-30.md`.
```

- [ ] **Step 2: Verify the caveat is present**

```bash
cd /Users/dt/projects/dev-tools/craft-review
grep -n "correlate but aren't identical" skills/code/command-skill-token-efficiency/SKILL.md
```

Expected: one match, in the opening paragraph.

- [ ] **Step 3: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add skills/code/command-skill-token-efficiency/SKILL.md
git commit -m "fix(skill): correct token-cost overclaim in command-skill-token-efficiency

The skill's opening paragraph claimed PR #232 'found and fixed real,
measured token cost' — stronger language than its own cited source
(SPEC-token-efficiency-research-2026-06-30.md), which explicitly
states the 48% figure is a line-count diff and that '/usage'
validation has not yet happened. Brought the skill's framing in line
with what's actually been measured.

Found in PR #232 adversarial review."
```

---

### Task 6: Document the depth-count colon-notation removal

**Files:**

- Modify: `skills/workflow/brainstorm/SKILL.md` (insert after line 46, end of "Mandatory
  Interactive Steps" section, before "## Outputs")

**Interfaces:** None.

**Decision:** restoring the old `d:5`/`m:12` custom-count override would directly contradict this
branch's own simplification goal (two fixed decision points, no escape-hatch menus — see "Going
Deeper" section, lines 74-88). The right fix is an explicit removal note, matching the existing
"No max tier — see Going deeper" callout style, not a silent gap.

- [ ] **Step 1: Add the removal note**

Insert a new subsection after line 46 (end of "Mandatory Interactive Steps" paragraph) and before
`## Outputs`:

```markdown
## Removed: Per-Invocation Question-Count Override

The pre-redesign version supported colon notation (`d:5`, `m:12`, `q:0`) to override the
per-depth expert-question count on a single invocation. This is intentionally not carried
forward — the fixed per-depth counts (0/2/6) are part of the same two-decision-point
simplification described above ("Going Deeper"); a per-call override reintroduces the kind of
escape-hatch menu this redesign removed. If a specific topic genuinely needs more than 6
expert questions, run `/brainstorm` at `deep`, then use the "anything else before I generate
this?" follow-up offer (Flow step 5) to add more — don't request a count override.
```

- [ ] **Step 2: Verify**

```bash
cd /Users/dt/projects/dev-tools/craft-review
grep -n "Removed: Per-Invocation" skills/workflow/brainstorm/SKILL.md
```

Expected: one match.

- [ ] **Step 3: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add skills/workflow/brainstorm/SKILL.md
git commit -m "docs(brainstorm): document intentional removal of depth-count colon notation

d:5/m:12-style per-invocation count overrides existed pre-redesign and
were dropped with no migration note. Restoring them would contradict
this branch's own two-decision-point simplification, so the fix is an
explicit removal note (matching the existing 'No max tier' callout
style) rather than restoring the feature.

Found in PR #232 adversarial review."
```

---

### Task 7: Surface the `-C`/`--categories` value table into brainstorm/SKILL.md

**Files:**

- Modify: `skills/workflow/brainstorm/SKILL.md` (insert after line 62, end of Flow step 4, before
  step 5)

**Interfaces:** None.

**Context:** `commands/workflow/brainstorm.md` frontmatter still declares the `categories`
argument with full-word category names (`req,users,scope,tech,timeline,risks,existing,success`).
The only existing value-mapping table lives in the archived
`docs/specs/_archive/SPEC-brainstorm-question-bank.md`, which uses a **different, stale shortcut
convention** (`req,usr,scp,tech,time,risk,exist,ok,all`) that doesn't match the live frontmatter
wording. Surface a corrected table using the frontmatter's actual current convention, in the
skill itself — not a link into an archived, internally-inconsistent doc.

- [ ] **Step 1: Add the category table**

Insert immediately after line 62 (end of Flow step 4's question-bank reference) and before step
5 ("One follow-up offer"):

```markdown

### Category override (`-C` / `--categories`)

Default category selection is focus-driven (see table below). Override with
`-C <list>` / `--categories <list>` (comma-separated, matching `commands/workflow/brainstorm.md`
frontmatter):

| Category | Covers |
|---|---|
| `req` | requirements |
| `users` | target users / audience |
| `scope` | what's in / out of scope |
| `tech` | technical approach, stack |
| `timeline` | sequencing, milestones |
| `risks` | risks, edge cases, failure modes |
| `existing` | existing code/patterns to reuse or replace |
| `success` | success criteria, how to know it's done |
| `all` | every category above (default when `-C` omitted at `deep`) |

Default categories by focus:

| Focus | Default categories |
|---|---|
| `feat` | req, users, scope, success |
| `arch` | tech, risks, existing, scope |
| `api` | tech, req, success |
| `ux` | users, scope, success |
| `ops` | tech, risks, timeline |
| (auto/unset) | req, users, tech, success |

Example: `/brainstorm "caching" -C tech,risks` limits expert questions to the technical and
risk categories regardless of focus.
```

- [ ] **Step 2: Verify**

```bash
cd /Users/dt/projects/dev-tools/craft-review
grep -n "Category override" skills/workflow/brainstorm/SKILL.md
grep -n "categories" commands/workflow/brainstorm.md | head -1
```

Both should reference the same category vocabulary (`req,users,scope,tech,timeline,risks,existing,success`).

- [ ] **Step 3: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git add skills/workflow/brainstorm/SKILL.md
git commit -m "docs(brainstorm): surface -C/--categories value table in the skill

The categories flag was still declared in commands/workflow/brainstorm.md
frontmatter, but its value table was only reachable via a link into an
archived spec that used a different, inconsistent shortcut convention.
Added a corrected table directly in the skill, matching the live
frontmatter's category names.

Found in PR #232 adversarial review."
```

---

### Task 8: Update PR #232 description and schedule the post-merge `/usage` checkpoint

**Files:**

- No repo files modified — this task updates the PR via `gh` and schedules a follow-up reminder.
- Modify: `.STATUS` (add next-action item)

**Interfaces:** None.

- [ ] **Step 1: Confirm the current commit range**

```bash
cd /Users/dt/projects/dev-tools/craft-review
git log --oneline dev..feature/token-usage-reduction
```

Expected: 12 commits (the 6 from the original PR description plus 6 added since:
`d80daa5f`, `8094d6ec`, `ce321be3`, `84e36731`, `6e968161`, `f615f3fb`), plus the 8 fix commits
from Tasks 1-7 of this plan = 20 total once this plan's commits are pushed.

- [ ] **Step 2: Update the PR description**

```bash
gh pr edit 232 --repo Data-Wise/craft --body-file - <<'EOF'
# Token usage reduction: orchestrator model routing, /refine + /brainstorm redesign

**Branch:** `feature/token-usage-reduction` — 20 commits, reviewed via 8-angle adversarial review
+ token-reduction-claim verification. All 8 review findings + the claim-accuracy issues found in
follow-up review are fixed on this branch (see commits tagged `fix:`/`docs:` after the original
redesign work). Full suite, validate-counts, and bump-version --verify all green before merge.

## What this ships

- Explicit `model:` pinning on orchestrator agents (`orchestrator-v2.md`: sonnet,
  legacy `orchestrator.md`: haiku) instead of inheriting the caller's tier.
- `/refine` reduced to a 42-line thin shim over the pre-existing `prompt-refiner` skill
  (was 630 lines, duplicated rather than delegated).
- `/brainstorm` split into `brainstorm` (ideation/spec-capture) and a narrowed
  `brainstorm-insights` (session friction reports) — cut decision points 4→2, removed in-skill
  agent delegation in favor of the existing `orchestrator-v2` handoff.
- `agents/orchestrator-v2.md` BEHAVIOR 5 (error handling) + BEHAVIOR 9 (timeline display)
  extracted to `skills/orchestrator-resilience/SKILL.md` — loads on agent failure or `timeline`
  request, not on every orchestrator-v2 invocation (1473→1212 lines in the always-loaded agent file).
- New `skills/code/command-skill-token-efficiency/SKILL.md` — codifies the command-vs-skill
  content classification and the "verify with the full suite, not a sample" lesson this branch's
  own regressions taught. `scripts/audit-deprecated-commands.py` gained a `--pair` mode.
- `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` +
  `docs/internal/TOKEN-EFFICIENCY-craft.md` — research report and implementation record.
- `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` — repo-wide audit of all 56
  deprecated commands ranked by body-size ratio against their replacement skill.

## What this measures (and what it doesn't)

The 48% figure quoted throughout is a **line-count** reduction (`wc -l`), not a token measurement.
`SPEC-token-efficiency-research-2026-06-30.md` is explicit about this gap. A dated post-merge
`/usage` checkpoint is tracked in `.STATUS` to close it — see Track A, Task 8 of
`docs/plans/2026-06-30-pr232-deficiency-fixes.md`.

## Review history

- 8-angle finder + verifier adversarial review (8 findings, all fixed — see commit history)
- Follow-up adversarial review of the token-reduction claims themselves (3 of 4 mechanisms
  verified REAL with caveats; model-pinning savings UNVERIFIED — sound mechanism, no measurement)
- Remediation plan: `docs/specs/SPEC-pr232-deficiency-fix-and-namespace-gate-2026-06-30.md`
EOF
```

- [ ] **Step 3: Add a `.STATUS` next-action item for the post-merge usage checkpoint**

In `/Users/dt/projects/dev-tools/craft/.STATUS` (the `dev` checkout, not `craft-review` —
`.STATUS` lives on `dev`), add to the `🎯 Next Action` section:

```
D) Check real `/usage` data ~2 weeks after PR #232 merges (target: ~2026-07-14) — compare
   pre-merge vs. post-merge subagent/session token cost against the unvalidated 48% line-count
   hypothesis in SPEC-token-efficiency-research-2026-06-30.md. Record the result as an addendum
   to that SPEC, not a new doc.
```

- [ ] **Step 4: Schedule a reminder for the checkpoint date**

Use `send_later` (or `create_trigger` with `run_once_at`) to schedule a message ~2 weeks out:

```
message: "Checkpoint: PR #232 merged ~2 weeks ago. Check /usage data (subagent/session token
cost) against the pre-merge baseline and record the result as an addendum to
docs/specs/SPEC-token-efficiency-research-2026-06-30.md, per .STATUS next-action item D."
delay: ~14 days from the actual PR #232 merge date (not from this plan's authoring date — set
this when Task 8 actually executes, after Tasks 1-7 are merged).
```

- [ ] **Step 5: Verify and commit the .STATUS change**

```bash
cd /Users/dt/projects/dev-tools/craft
grep -n "Check real \`/usage\` data" .STATUS
git add .STATUS
git commit -m "docs(.status): add post-PR#232 /usage checkpoint next-action item

Closes the validation gap SPEC-token-efficiency-research-2026-06-30.md
itself flags as open — a dated, scheduled follow-up instead of prose
that could quietly evaporate."
```

Note: this commit lands on `dev` (the main `craft` checkout), not `feature/token-usage-reduction`
— `.STATUS` tracks session state for the whole repo, not one branch.

---

## Final verification (before merge)

```bash
cd /Users/dt/projects/dev-tools/craft-review
python3 -m pytest tests/ -v 2>&1 | tail -20
./scripts/validate-counts.sh
./scripts/bump-version.sh --verify
```

All three must be clean. Then merge PR #232 to `dev` per the user's normal release process —
not part of this plan (this plan stops at "ready to merge").
