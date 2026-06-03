# /craft:orchestrate:drive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/craft:orchestrate:drive` — a thin command that drives an approved SPEC to completion via Claude Code's native `/goal` turn-loop, with a real verify gate as the authoritative "done" check, stopping at verified-green for a human-opened PR.

**Architecture:** A thin command (`commands/orchestrate/drive.md`) owns only spec→`/goal`-condition synthesis, precondition gating, and the confirm gate. The reusable body — parse-or-derive `ORCHESTRATE-*.md`, file-scoped subagent dispatch, and the real verify pass — lives in a new shared skill `skills/orchestration/drive-engine/`, a sibling of the existing `plan-orchestrator`. Craft commands and skills are Markdown files; "tests" are Python assertions in `tests/test_craft_plugin.py` plus `scripts/validate-counts.sh`.

**Tech Stack:** Markdown command/skill files (YAML frontmatter), Python `unittest`-style tests (`tests/test_craft_plugin.py`), `_discovery.py` auto-discovery, `scripts/validate-counts.sh`, MkDocs site, pre-commit (markdownlint + Mermaid validator).

**Spec:** `docs/specs/SPEC-orchestrate-drive-2026-06-03.md`

---

## File Structure

| File | Create/Modify | Responsibility |
|---|---|---|
| `skills/orchestration/drive-engine/SKILL.md` | Create | Shared body: parse-or-derive ORCHESTRATE, file-scoped dispatch, real verify gate. Auto-activates on "drive a spec to done" phrasing. |
| `commands/orchestrate/drive.md` | Create | Thin command: condition synthesis, precondition gating, confirm gate, dry-run. Delegates body to the skill. |
| `.claude-plugin/plugin.json` | Modify | Bump command count (108→109) and skill count (36→37) in `description`. |
| `CLAUDE.md` | Modify | Active Work counts + one-line capability note. |
| `docs/commands/orchestrate-drive.md` | Create | Human-readable site mirror. |
| `mkdocs.yml` | Modify | Add the site mirror to nav. |
| `docs/commands.md` | Modify | Hand-written category index — add drive under orchestrate. |
| `docs/help/orchestrate-drive.md` | Create | Help page: what/when/how + precondition-failure remedies. |
| `docs/tutorials/TUTORIAL-orchestrate-drive.md` | Create | End-to-end first-timer walkthrough. |
| `docs/cookbook/recipes/drive-a-spec-to-green.md` | Create | Copy-paste recipe. |
| `docs/REFCARD.md` | Modify | One-line orchestrate-section row. |
| `commands/orchestrate.md` | Modify | Cross-link the swarm↔drive distinction. |
| `CHANGELOG.md` + `docs/CHANGELOG.md` | Modify | `[Unreleased]` feature entry (both mirror). |
| `tests/test_craft_plugin.py` | Modify | **Unit** assertions for command + skill existence/shape (Tasks 1–2). |
| `tests/test_plugin_e2e.py` | Modify | **E2E** assertion that drive is wired into nav; suite cross-checks counts (Task 9). |

---

## Task 0: Prerequisite — feature worktree (NOT on dev)

Implementation touches new **code** files (command + skill `.md`). Branch guard blocks new code files on `dev`. Create the worktree first and run all tasks inside it.

- [ ] **Step 1: Create worktree from dev**

```bash
cd ~/projects/dev-tools/craft
git worktree add ~/.git-worktrees/craft/feature-orchestrate-drive -b feature/orchestrate-drive dev
```

- [ ] **Step 2: Start a session in the worktree**

```bash
cd ~/.git-worktrees/craft/feature-orchestrate-drive
git branch --show-current   # expect: feature/orchestrate-drive
```

All paths below are relative to this worktree root.

---

## Task 1: Shared skill — `drive-engine`

**Files:**

- Create: `skills/orchestration/drive-engine/SKILL.md`
- Test: `tests/test_craft_plugin.py` (new `test_drive_engine_skill_exists`)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_craft_plugin.py`:

```python
def test_drive_engine_skill_exists():
    """The shared drive-engine skill must exist with valid frontmatter."""
    skill = PLUGIN_DIR / "skills" / "orchestration" / "drive-engine" / "SKILL.md"
    assert skill.exists(), "skills/orchestration/drive-engine/SKILL.md missing"
    fm = _parse_skill_frontmatter(skill)
    assert fm is not None, "drive-engine SKILL.md has no parseable frontmatter"
    assert "name" in fm and "description" in fm, "drive-engine missing name/description"
    assert fm["name"] == "drive-engine"
```

> Note: `PLUGIN_DIR` and `_parse_skill_frontmatter` already exist in the test file (see `_parse_skill_frontmatter` at line ~220). Reuse them; do not redefine.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_drive_engine_skill_exists -v`
Expected: FAIL with `AssertionError: skills/orchestration/drive-engine/SKILL.md missing`

- [ ] **Step 3: Create the skill file**

Create `skills/orchestration/drive-engine/SKILL.md`:

```markdown
---
name: drive-engine
description: This skill should be used when driving an approved SPEC to completion — "drive this spec to done", "run the orchestrate drive loop", "implement the spec autonomously until tests pass". Owns the reusable body behind /craft:orchestrate:drive — parse-or-derive ORCHESTRATE phases, dispatch file-scoped subagents, and run the authoritative real verify gate.
---

# Drive Engine

The reusable execution body behind `/craft:orchestrate:drive`. The command
owns condition synthesis and gating; this skill owns the work.

## Responsibilities

1. **Resolve phases** — if an `ORCHESTRATE-*.md` exists in the worktree
   root, parse its phases and file-scopes. If not, derive phases directly
   from the SPEC's `## Phase`/`## Increment`/task-list sections. An
   ORCHESTRATE file is preferred when present but never required.
2. **Dispatch** — per turn, launch `--agents N` (default 1) file-scoped
   subagents, one per pending wave item, each scoped to its files only.
   Keep the transcript linear when `N == 1` so the `/goal` evaluator can
   read it.
3. **Real verify gate** — when the `/goal` condition clears, run the
   project's actual verification (auto-detected, see table) and treat its
   exit status as the authoritative "done". A green transcript is NOT
   sufficient; the command must actually run.

## Phase resolution

Look for, in order: worktree `ORCHESTRATE-*.md` → SPEC `## Phase N` /
`## Increment N` headings → top-level numbered task list. Emit a wave list
of `{phase, files[], tasks[]}`.

## Verify-command auto-detection

| Detection | Verify command |
|-----------|----------------|
| `tests/test_craft_plugin.py` | `python3 tests/test_craft_plugin.py` |
| `package.json` test script | `npm test` |
| `pyproject.toml` / `pytest.ini` | `pytest` |
| `Cargo.toml` | `cargo test` |
| `DESCRIPTION` (R) | `R CMD check` |

Always pair with `git status --short` to confirm a clean, committed tree.

## Outputs

A structured verify result: `{ command, exit_code, passed: bool, summary }`.
On `passed: true`, the caller stops at verified-green and prints the
`gh pr create` command — this skill never opens a PR.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_drive_engine_skill_exists -v`
Expected: PASS

- [ ] **Step 5: Run the skill-suite invariants (they must still pass with the new skill)**

Run: `python3 -m pytest tests/test_craft_plugin.py -k "skill" -v`
Expected: PASS — including `test_all_skills_have_valid_frontmatter`, `test_skill_trigger_phrases_unique`, `test_skill_bodies_non_trivial`. If `test_skill_trigger_phrases_unique` fails, reword the `description` trigger phrases to not collide with another skill.

- [ ] **Step 6: Commit**

```bash
git add skills/orchestration/drive-engine/SKILL.md tests/test_craft_plugin.py
git commit -m "feat(orchestrate): add drive-engine shared skill"
```

---

## Task 2: The thin command — `drive.md`

**Files:**

- Create: `commands/orchestrate/drive.md`
- Test: `tests/test_craft_plugin.py` (new `test_drive_command_exists`)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_craft_plugin.py`:

```python
def test_drive_command_exists():
    """The orchestrate:drive command must exist with valid frontmatter."""
    cmd = PLUGIN_DIR / "commands" / "orchestrate" / "drive.md"
    assert cmd.exists(), "commands/orchestrate/drive.md missing"
    text = cmd.read_text(encoding="utf-8")
    assert text.startswith("---"), "drive.md missing frontmatter block"
    assert "description:" in text.split("---")[1], "drive.md frontmatter missing description"
    # Must not silently auto-open a PR (human publish gate).
    assert "gh pr create" in text, "drive.md must print the PR command, not open it"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_drive_command_exists -v`
Expected: FAIL with `AssertionError: commands/orchestrate/drive.md missing`

- [ ] **Step 3: Create the command file**

Create `commands/orchestrate/drive.md`:

```markdown
---
description: Drive an approved SPEC to completion via the native /goal turn-loop, with a real verify gate; stops at verified green and prints the PR command
category: orchestrate
arguments:
  - name: spec
    description: Path to SPEC-*.md (default: newest docs/specs/SPEC-*.md or the one referenced by the worktree's ORCHESTRATE-*.md)
    required: false
  - name: dry-run
    description: Print derived condition + dispatch plan + precondition report; zero side effects
    required: false
    default: false
    alias: -n
  - name: yes
    description: Skip the condition-confirm gate
    required: false
    default: false
    alias: -y
  - name: max-turns
    description: Turn bound folded into the condition's stop clause
    required: false
    default: 25
  - name: no-auto
    description: Do not enable auto mode (approve tools per turn)
    required: false
    default: false
  - name: agents
    description: Max concurrent file-scoped subagents per turn
    required: false
    default: 1
  - name: condition
    description: Override the synthesized /goal condition entirely
    required: false
---

# /craft:orchestrate:drive — Spec-Driven Autonomous Loop

Drives an approved SPEC to completion using Claude Code's built-in `/goal`
as the turn-loop engine. Thin wrapper: it owns condition synthesis,
precondition gating, and the confirm gate — and delegates dispatch + the
real verify gate to the `drive-engine` skill.

> **drive vs `/craft:orchestrate --swarm`:** `drive` is a spec-anchored
> `/goal` turn-loop (iterate until a condition holds, real verify
> arbitrates). `--swarm` is free-form fan-out-and-converge across isolated
> worktrees. Use `drive` when you have an approved spec and want
> autonomous completion; use `--swarm` for parallel independent tasks.

## Execution Behavior (MANDATORY)

Follow these steps in order. Do NOT skip any step.

### Step 1: Locate the spec
Use the `spec` arg; else the newest `docs/specs/SPEC-*.md`; else the spec
referenced by the worktree's `ORCHESTRATE-*.md`. Report which was chosen.

### Step 2: Precondition checks (block with remedy on failure)
| Check | Block reason | Remedy shown |
|-------|--------------|--------------|
| Worktree on `feature/*` | Not isolated | `git worktree add … -b feature/<topic> dev` |
| `/goal` available (Claude Code ≥ v2.1.139) | Engine missing | Upgrade Claude Code |
| Hooks not blocking `/goal` (`disableAllHooks` / `allowManagedHooksOnly`) | `/goal` disabled by policy | Adjust hook policy |
| Workspace trust accepted | `/goal` needs trust | Accept workspace trust |
| Auto mode on (unless `--no-auto`) | Loop can't run unattended | Offer to enable in confirm gate |

### Step 3: Synthesize the `/goal` condition
From the spec's **Acceptance Criteria** + **Review Checklist**, build a
condition that is (a) measurable, (b) provable-in-transcript by showing
command output, (c) bounded by `--max-turns`. Honor `--condition` override.
Template:
> `<criteria as end states> — prove each by showing the relevant command
> output in the transcript (e.g. test runner exit, git status). Do not
> change <stated constraints>. Or stop after <max-turns> turns.`

### Step 4: `--dry-run` (zero side effects)
If `--dry-run`, print the derived condition + dispatch plan (from
`drive-engine`) + precondition report, then STOP. Set no goal; change no
auto-mode state.

### Step 5: Confirm gate (defaults to No)
Show the condition. If auto mode is off and `--no-auto` not set, OFFER to
enable it here (never silent). Proceed only on explicit Yes or `--yes`.

### Step 6: Drive the loop
Emit `/goal <condition>`. Per turn, invoke the `drive-engine` skill to
dispatch `--agents N` (default 1) file-scoped subagents.

### Step 7: Real verify gate (authoritative)
When the goal clears, the `drive-engine` skill runs the project's actual
verify command + `git status --short`. Green is required to declare done —
a green-looking transcript alone is NOT sufficient.

### Step 8: Green handoff (no auto-PR)
On verified green, STOP and print the exact command for the user to run,
e.g. `gh pr create --base dev`. Never open the PR yourself.

## Exit paths
- Condition met → real verify → green handoff
- `--max-turns` bound hit → report progress, stop
- User `/goal clear` → stop (drive does not shadow native `/goal`)

## See Also
- `/craft:orchestrate` — free-form multi-agent orchestration (`--swarm`)
- `plan-orchestrator` skill — produce an ORCHESTRATE file from a spec
- `drive-engine` skill — the dispatch + verify body this command calls
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_drive_command_exists -v`
Expected: PASS

- [ ] **Step 5: Run command-suite invariants**

Run: `python3 -m pytest tests/test_craft_plugin.py -k "command or naming or categor" -v`
Expected: PASS — `test_all_commands_valid`, `test_command_categories`, `test_consistent_naming`. (Note `test_command_count` will fail until Task 3 syncs the count — that is expected and fixed next.)

- [ ] **Step 6: Commit**

```bash
git add commands/orchestrate/drive.md tests/test_craft_plugin.py
git commit -m "feat(orchestrate): add thin drive command"
```

---

## Task 3: Sync counts (command 108→109, skill 36→37)

**Files:**

- Modify: `.claude-plugin/plugin.json` (the `description` string)
- Modify: `CLAUDE.md` (Active Work line)

- [ ] **Step 1: Run the count validator to see the mismatch**

Run: `./scripts/validate-counts.sh`
Expected: reports `Commands` and `Skills` file counts higher than the documented numbers in `plugin.json`.

- [ ] **Step 2: Update plugin.json description**

In `.claude-plugin/plugin.json`, update the `description` numbers to match the new file counts (commands +1, skills +1). Use the exact numbers the validator printed in Step 1 — do not hard-code 109/37 if the validator reports different totals.

- [ ] **Step 3: Update CLAUDE.md Active Work**

In `CLAUDE.md`, update the `**N commands** · **M skills**` line to the validator's numbers and add a one-line note: `orchestrate:drive — spec-driven autonomous /goal loop`.

- [ ] **Step 4: Re-run the validator**

Run: `./scripts/validate-counts.sh`
Expected: `✓ Commands match` and `✓ Skills match`.

- [ ] **Step 5: Run the count test**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_command_count tests/test_craft_plugin.py::test_skills_exist -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/plugin.json CLAUDE.md
git commit -m "chore(orchestrate): sync command/skill counts for drive"
```

---

## Task 4: Website update (index + site mirror + nav)

**Files:**

- Create: `docs/commands/orchestrate-drive.md`
- Modify: `mkdocs.yml`
- Modify: `docs/commands.md` (the hand-written command index)

> craft's site has THREE places a command surfaces: the per-command page
> (`docs/commands/*.md`), the MkDocs nav (`mkdocs.yml`), and the
> hand-written category index (`docs/commands.md`). All three must be
> updated or the e2e/site tests and the index drift. Docs deploy is
> automatic on push to `main` (docs.yml) — no manual deploy step.

- [ ] **Step 1: Create the per-command site page**

Create `docs/commands/orchestrate-drive.md` — a human-readable summary (NOT a copy of the command's MANDATORY steps). Required sections: one-line purpose; the drive-vs-swarm callout (copy the blockquote from the command); the flag table (from the spec's API Design table); the user-journey Mermaid flowchart (copy from `docs/specs/SPEC-orchestrate-drive-2026-06-03.md`, the `flowchart LR` block); a "Stops at verified green" note. Use a quoted label (`["craft:git:worktree …"]`) in the Mermaid node — leading-slash labels fail the Mermaid pre-commit check.

- [ ] **Step 2: Add to the MkDocs nav**

In `mkdocs.yml`, under the Commands → Orchestrate nav grouping, add adjacent to the existing `orchestrate` / `orchestrate:resume` entries:

```yaml
      - drive: commands/orchestrate-drive.md
```

- [ ] **Step 3: Update the hand-written index `docs/commands.md`**

In `docs/commands.md`, in the `### /craft:orchestrate` orchestrate section, add a `### /craft:orchestrate:drive` subsection (one-line purpose + the `--dry-run` example). The category list at the top already includes `orchestrate`, so no category edit is needed — but confirm the orchestrate command count/example block stays consistent.

- [ ] **Step 4: Build the site strict**

Run: `mkdocs build --strict 2>&1 | tail -20`
Expected: build succeeds; no "not found in nav" warning for the new page; no broken-link error.

- [ ] **Step 5: Commit**

```bash
git add docs/commands/orchestrate-drive.md mkdocs.yml docs/commands.md
git commit -m "docs(orchestrate): website update for drive (page, nav, index)"
```

---

## Task 5: Help page (precondition remedies)

**Files:**

- Create: `docs/help/orchestrate-drive.md`

- [ ] **Step 1: Create the help page**

Create `docs/help/orchestrate-drive.md` with these required sections:

1. **What it does** (2 sentences).
2. **When to use** (have an approved spec + want autonomous completion) vs **when not** (free-form work → use `--swarm`).
3. **Quick start**: `… --dry-run` first, then the real run.
4. **Precondition failures + remedies** — a table covering EVERY blocker, copied from the command's Step 2 table (no worktree, `/goal` unavailable by version, `/goal` disabled by hook policy, workspace untrusted, auto mode off). This is the support-question hotspot — it must be exhaustive.
5. **Reading the verify gate** — green = done; red = the loop continues.

- [ ] **Step 2: Verify no broken links**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add docs/help/orchestrate-drive.md
git commit -m "docs(orchestrate): add drive help page"
```

---

## Task 6: Tutorial (end-to-end)

**Files:**

- Create: `docs/tutorials/TUTORIAL-orchestrate-drive.md`

- [ ] **Step 1: Create the tutorial**

Create `docs/tutorials/TUTORIAL-orchestrate-drive.md` walking a first-timer through, on a tiny toy spec:

1. Start: an approved `SPEC-toy.md` in a `feature/*` worktree.
2. **Lead with `--dry-run`** — show the derived `/goal` condition + precondition report; explain reading it.
3. Real run: the confirm gate, the auto-mode offer, the loop.
4. The real verify gate turning green.
5. The green handoff — copy the printed `gh pr create`, open the PR yourself.
6. Embed the user-journey `flowchart LR` from the spec (quoted node labels).

End with "Next: review the PR" — do NOT instruct auto-merging.

- [ ] **Step 2: Verify links + Mermaid**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v && python3 scripts/mermaid-validate.py docs/tutorials/TUTORIAL-orchestrate-drive.md`
Expected: PASS / `0 errors`

- [ ] **Step 3: Commit**

```bash
git add docs/tutorials/TUTORIAL-orchestrate-drive.md
git commit -m "docs(orchestrate): add drive tutorial"
```

---

## Task 7: Cookbook recipe

**Files:**

- Create: `docs/cookbook/recipes/drive-a-spec-to-green.md`

- [ ] **Step 1: Create the recipe**

Create `docs/cookbook/recipes/drive-a-spec-to-green.md` — a terse copy-paste recipe:

```markdown
# Recipe: Drive a spec to green

1. `/craft:orchestrate:drive --dry-run`   # preview the /goal condition
2. Review the condition + preconditions.
3. `/craft:orchestrate:drive`             # confirm gate → enable auto mode → loop
4. Wait for the real verify gate to report green.
5. Copy the printed `gh pr create --base dev` and open the PR yourself.
```

Add the one-line drive-vs-swarm distinction at the bottom.

- [ ] **Step 2: Verify links**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add docs/cookbook/recipes/drive-a-spec-to-green.md
git commit -m "docs(orchestrate): add drive cookbook recipe"
```

---

## Task 8: REFCARD row, CHANGELOG, swarm cross-link

**Files:**

- Modify: `docs/REFCARD.md`
- Modify: `commands/orchestrate.md`
- Modify: `CHANGELOG.md` and `docs/CHANGELOG.md`

- [ ] **Step 1: Add the REFCARD row**

In `docs/REFCARD.md`, in the orchestrate section, add one line beside `orchestrate` / `orchestrate:resume`:
`| /craft:orchestrate:drive | Spec → autonomous /goal loop → verified green |`

- [ ] **Step 2: Cross-link from orchestrate.md**

In `commands/orchestrate.md`, in the `## See Also` section, add:
`- /craft:orchestrate:drive — spec-anchored /goal turn-loop (vs --swarm fan-out)`

- [ ] **Step 3: Add CHANGELOG entries (BOTH files must mirror)**

Under `[Unreleased]` → `### Added` in **both** `CHANGELOG.md` and `docs/CHANGELOG.md`:
`- /craft:orchestrate:drive — spec-driven autonomous implementation loop (native /goal + drive-engine skill + real verify gate).`

> craft maintains root + docs CHANGELOG that must stay identical — update both now to avoid release-time drift.

- [ ] **Step 4: Verify counts + links still pass**

Run: `./scripts/validate-counts.sh && python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v`
Expected: counts match; links PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/REFCARD.md commands/orchestrate.md CHANGELOG.md docs/CHANGELOG.md
git commit -m "docs(orchestrate): refcard, changelog, swarm cross-link for drive"
```

---

## Task 9: E2E coverage

craft's e2e suite (`tests/test_plugin_e2e.py`) already cross-checks
command/skill counts vs `plugin.json`, frontmatter presence, duplicate
names, mkdocs nav, and orphan skill references — so once Tasks 1–4 land,
these exercise `drive` automatically. Add one targeted assertion that the
new page is wired into the site, then run the full e2e + dogfood suites.

**Files:**

- Modify: `tests/test_plugin_e2e.py` (new `test_drive_command_in_nav`)

- [ ] **Step 1: Write the failing e2e assertion**

Add to `tests/test_plugin_e2e.py` (inside the existing MkDocs test class, e.g. near `test_mkdocs_nav_not_empty` ~line 375; reuse the module's `PLUGIN_DIR`):

```python
    def test_drive_command_in_nav(self):
        """The orchestrate:drive site page must be wired into mkdocs nav."""
        nav_text = (PLUGIN_DIR / "mkdocs.yml").read_text(encoding="utf-8")
        assert "commands/orchestrate-drive.md" in nav_text, (
            "orchestrate-drive.md not referenced in mkdocs.yml nav"
        )
```

- [ ] **Step 2: Run it to verify it passes (Task 4 already added the nav entry)**

Run: `python3 -m pytest tests/test_plugin_e2e.py::TestMkDocs::test_drive_command_in_nav -v`
Expected: PASS. (Replace `TestMkDocs` with the actual class name containing the mkdocs tests if different — find it with `grep -n "def test_mkdocs_nav_not_empty" tests/test_plugin_e2e.py` and read the enclosing `class`.)

- [ ] **Step 3: Run the full e2e suite**

Run: `python3 -m pytest tests/test_plugin_e2e.py -v`
Expected: all pass — `test_command_count_matches_description`, `test_skill_count_matches_description`, `test_claude_md_command_count_matches`, `test_no_orphan_skill_references_in_commands`, `test_no_duplicate_command_names`, and the new nav test. Any count mismatch means Task 3's sync was incomplete — fix the count, don't edit the test.

- [ ] **Step 4: Run the dogfood suite (catches cross-doc drift)**

Run: `python3 -m pytest tests/test_plugin_dogfood.py -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_plugin_e2e.py
git commit -m "test(orchestrate): e2e nav assertion for drive"
```

---

## Task 10: Full verification + PR handoff

- [ ] **Step 1: Full unit suite**

Run: `python3 tests/test_craft_plugin.py`
Expected: all pass, including the 2 new unit tests (`test_drive_engine_skill_exists`, `test_drive_command_exists`).

- [ ] **Step 2: E2E + dogfood suites**

Run: `python3 -m pytest tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -q`
Expected: all pass.

- [ ] **Step 3: Counts + site strict build**

Run: `./scripts/validate-counts.sh && mkdocs build --strict 2>&1 | tail -10`
Expected: counts match; strict build clean.

- [ ] **Step 4: Pre-flight check**

Run: `/craft:check` (or `./scripts/pre-release-check.sh` if available)
Expected: green.

- [ ] **Step 5: Push and STOP at the handoff (do not open the PR)**

```bash
git push -u origin feature/orchestrate-drive
```

Then print (do not run) the PR command for the user:
`gh pr create --base dev --title "feat: /craft:orchestrate:drive"`

> Per craft workflow, opening/merging the PR is the user's call. Stop here.

---

## Self-Review

**Spec coverage** — every spec section maps to a task:

- Thin command + shared skill → Tasks 1–2. Two-stage termination (real verify gate) → Task 1 (skill) + command Step 7. Self-sufficient on bare spec → Task 1 phase resolution. Stop at verified green → command Step 8 + Task 10. Require+offer auto mode → command Step 5. Default `--agents 1` → command frontmatter. `--dry-run` zero side effects → command Step 4. Documentation Deliverables table → Tasks 4–8 (command ref=Task 2, site mirror+index+nav=4, help=5, tutorial=6, cookbook=7, REFCARD/CHANGELOG/cross-link=8, both flowcharts embedded in 4 & 6). Counts → Task 3.
- **Tests:** unit (Tasks 1–2, run in Task 10 Step 1) + e2e/dogfood (Task 9, run in Task 10 Step 2). Website update (per-command page + nav + hand-written index) → Task 4, verified by the e2e nav assertion (Task 9) and strict site build (Task 10 Step 3).

**Placeholder scan** — no "TBD/handle edge cases"; command + skill frontmatter given in full; doc tasks specify exact required sections + which spec block to copy.

**Type/name consistency** — skill name `drive-engine` and command path `commands/orchestrate/drive.md` are used identically across Tasks 1, 2, 4–8. Test helpers `PLUGIN_DIR` / `_parse_skill_frontmatter` reuse existing definitions (not redefined). Verify command auto-detection table is identical in the skill and referenced (not restated) by the command.
