# --refine Flag Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `--refine` flag to five prompt-driven craft commands that, before the command acts, routes the user's argument through one shared `prompt-refiner` skill, shows a before/after, and proceeds on the approved version.

**Architecture:** A single skill `skills/workflow/prompt-refiner/` owns all refining + the canonical Accept/Edit/Use-original flow. Each of the five commands gains a `--refine` flag in frontmatter and a short section that **delegates to the skill** (never restates the flow) — a dogfood test enforces that delegation so the five can't drift. Commands and skills are Markdown; "tests" are Python assertions in `tests/test_craft_plugin.py`, `tests/test_plugin_e2e.py`, `tests/test_plugin_dogfood.py`, plus `scripts/validate-counts.sh`.

**Tech Stack:** Markdown command/skill files (YAML frontmatter), Python tests, `_discovery.py`, `scripts/validate-counts.sh`, MkDocs, pre-commit (markdownlint + Mermaid validator).

**Spec:** `docs/specs/SPEC-refine-flag-2026-06-03.md`

---

## File Structure

| File | Create/Modify | Responsibility |
|---|---|---|
| `skills/workflow/prompt-refiner/SKILL.md` | Create | The refiner: read context, rewrite prompt, run the Accept/Edit/Use-original confirm. Single source of truth. |
| `commands/workflow/brainstorm.md` | Modify | Add `--refine` flag + delegate-to-skill section. |
| `commands/do.md` | Modify | Same. (Confirm path with `find commands -name do.md`.) |
| `commands/orchestrate.md` | Modify | Same. |
| `commands/plan/feature.md` | Modify | Same. |
| `commands/arch/plan.md` | Modify | Same. |
| `commands/workflow/refine.md` | Modify | Sunset note: deprecated `/refine` → `--refine` flag + `prompt-refiner` skill. |
| `.claude-plugin/plugin.json` | Modify | Skill count +1 in `description`. |
| `CLAUDE.md` | Modify | Skill count + capability note. |
| `docs/help/refine-flag.md` | Create | Help: what/when/how, `--yes` auto-accept caveat. |
| `docs/tutorials/TUTORIAL-refine-flag.md` | Create | Vague→refined→brainstorm walkthrough. |
| `docs/cookbook/recipes/refine-before-running.md` | Create | Copy-paste recipe across the 5 commands. |
| `docs/REFCARD.md` | Modify | One-line `--refine` row. |
| `docs/commands/*.md` (5 mirrors) | Modify | Mention `--refine` on each command's site page. |
| `CHANGELOG.md` + `docs/CHANGELOG.md` | Modify | `[Unreleased]` feature entry (both mirror). |
| `tests/test_craft_plugin.py` | Modify | Unit: skill exists, flag documented. |
| `tests/test_plugin_e2e.py` | Modify | E2E: flag in exactly the 5 commands (scope guard). |
| `tests/test_plugin_dogfood.py` | Modify | Dogfood: commands delegate to skill (no drift). |

---

## Task 0: Prerequisite — feature worktree (NOT on dev)

Implementation adds new **code** files (skill) and edits commands. Branch guard blocks new code files on `dev`. Work in a worktree.

- [ ] **Step 1: Create the worktree from dev**

```bash
cd ~/projects/dev-tools/craft
git worktree add ~/.git-worktrees/craft/feature-refine-flag -b feature/refine-flag dev
```

- [ ] **Step 2: Enter it and confirm**

```bash
cd ~/.git-worktrees/craft/feature-refine-flag
git branch --show-current   # expect: feature/refine-flag
```

All paths below are relative to this worktree root.

- [ ] **Step 3: Confirm the exact paths of the 5 target commands**

```bash
find commands -name brainstorm.md -o -name do.md -o -name orchestrate.md -o -name feature.md -o -name plan.md | sort
```

Expected: `commands/workflow/brainstorm.md`, `commands/do.md`, `commands/orchestrate.md`, `commands/plan/feature.md`, `commands/arch/plan.md`. If any differ, use the real path in later tasks.

---

## Task 1: The `prompt-refiner` skill

**Files:**

- Create: `skills/workflow/prompt-refiner/SKILL.md`
- Test: `tests/test_craft_plugin.py` (new `test_prompt_refiner_skill_exists`)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_craft_plugin.py` (reuse existing `PLUGIN_DIR` + `_parse_skill_frontmatter`):

```python
def test_prompt_refiner_skill_exists():
    """The shared prompt-refiner skill must exist with valid frontmatter."""
    skill = PLUGIN_DIR / "skills" / "workflow" / "prompt-refiner" / "SKILL.md"
    assert skill.exists(), "skills/workflow/prompt-refiner/SKILL.md missing"
    fm = _parse_skill_frontmatter(skill)
    assert fm is not None, "prompt-refiner SKILL.md has no parseable frontmatter"
    assert fm.get("name") == "prompt-refiner"
    assert "description" in fm
```

- [ ] **Step 2: Run it — expect FAIL**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_prompt_refiner_skill_exists -v`
Expected: FAIL with `AssertionError: skills/workflow/prompt-refiner/SKILL.md missing`

- [ ] **Step 3: Create the skill**

Create `skills/workflow/prompt-refiner/SKILL.md`:

```markdown
---
name: prompt-refiner
description: This skill should be used when a command's --refine flag is set, or the user asks to "refine my prompt", "optimize this prompt", "make this request sharper" — rewrites a vague natural-language request into a specific, well-structured prompt using project context, shows before/after, and confirms before the caller proceeds. Replaces the deprecated /craft:workflow:refine command.
---

# Prompt Refiner

Rewrites a raw user request into a sharper prompt, then confirms. Called
by the `--refine` flag on brainstorm / do / orchestrate / plan:feature /
arch:plan, or standalone ("refine and print").

## Inputs

- `prompt` — the raw argument the user typed.
- `context` — project type (DESCRIPTION / package.json / pyproject.toml),
  current git branch, and `.STATUS` current-task if present.

## Procedure (the canonical --refine flow — callers MUST delegate here)

1. **Read context** (read-only): detect project type, branch, `.STATUS`.
2. **Rewrite** the prompt to add scope, specifics, and intent — without
   inventing requirements the user didn't imply.
3. **Show before/after** in a boxed display:

   ```

   ╭─ --refine ─────────────────────────────────────╮
   │ Original:  RAW                                  │
   │ Refined:   REWRITTEN                            │
   │ Changed:   ONE-LINE WHAT CHANGED                │
   ╰─────────────────────────────────────────────────╯

   ```

4. **Confirm** via AskUserQuestion — Accept (Recommended) / Edit /
   Use original. On **Edit**, present the refined text and take the
   user's edited version **inline** (no $EDITOR). With `--yes` or auto
   mode, skip the picker and auto-accept, printing
   `refined (auto-accepted)`.
5. **Return** the chosen prompt string to the caller.

## Constraints

- NEVER execute the prompt or call tools — rewrite text only.
- NEVER write files — context reads are read-only.
- NEVER touch secrets/tokens.

## Standalone use

Invoked with no downstream command, stop after step 3–4 and print the
refined prompt — this preserves the deprecated `/refine` behavior.
```

- [ ] **Step 4: Run it — expect PASS**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_prompt_refiner_skill_exists -v`
Expected: PASS

- [ ] **Step 5: Skill-suite invariants still pass**

Run: `python3 -m pytest tests/test_craft_plugin.py -k "skill" -v`
Expected: PASS — `test_all_skills_have_valid_frontmatter`, `test_skill_trigger_phrases_unique`, `test_skill_bodies_non_trivial`. If trigger phrases collide, reword the `description`.

- [ ] **Step 6: Commit**

```bash
git add skills/workflow/prompt-refiner/SKILL.md tests/test_craft_plugin.py
git commit -m "feat(workflow): add prompt-refiner skill"
```

---

## Task 2: Wire `--refine` into the 5 commands

**Files:**

- Modify: `commands/workflow/brainstorm.md`, `commands/do.md`, `commands/orchestrate.md`, `commands/plan/feature.md`, `commands/arch/plan.md`
- Test: `tests/test_craft_plugin.py` (new `test_refine_flag_documented`)

- [ ] **Step 1: Write the failing unit test**

Add to `tests/test_craft_plugin.py`:

```python
def test_refine_flag_documented():
    """The 5 target commands must declare --refine and delegate to the skill."""
    targets = [
        "commands/workflow/brainstorm.md",
        "commands/do.md",
        "commands/orchestrate.md",
        "commands/plan/feature.md",
        "commands/arch/plan.md",
    ]
    missing = []
    for rel in targets:
        text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
        if "--refine" not in text or "prompt-refiner" not in text:
            missing.append(rel)
    assert not missing, f"--refine/prompt-refiner missing in: {missing}"
```

- [ ] **Step 2: Run it — expect FAIL**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_refine_flag_documented -v`
Expected: FAIL listing all 5 files.

- [ ] **Step 3: Add the flag + delegation block to EACH of the 5 commands**

In each command's YAML frontmatter `arguments:` list, add:

```yaml
  - name: refine
    description: Refine the prompt via the prompt-refiner skill before acting
    required: false
    default: false
```

Then add this identical section to each command's body (after its usage
section). **Use this exact text in all five** — the dogfood test checks
they delegate rather than restate the flow:

```markdown
## --refine (prompt pre-processing)

When `--refine` is set, do NOT act on the raw argument. First invoke the
`prompt-refiner` skill with the argument and project context. Follow that
skill's canonical flow (before/after → Accept/Edit/Use-original; `--yes`
or auto mode auto-accepts). Then proceed using the prompt the skill
returns. On no-argument interactive commands, refine AFTER the topic is
captured.
```

- [ ] **Step 4: Run it — expect PASS**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_refine_flag_documented -v`
Expected: PASS

- [ ] **Step 5: Command-suite invariants**

Run: `python3 -m pytest tests/test_craft_plugin.py -k "command or naming or categor" -v`
Expected: PASS (`test_all_commands_valid`, `test_consistent_naming`).

- [ ] **Step 6: Commit**

```bash
git add commands/workflow/brainstorm.md commands/do.md commands/orchestrate.md commands/plan/feature.md commands/arch/plan.md tests/test_craft_plugin.py
git commit -m "feat(workflow): add --refine flag to 5 commands, delegating to prompt-refiner"
```

---

## Task 3: E2E scope guard (flag in exactly the 5)

**Files:**

- Modify: `tests/test_plugin_e2e.py` (new `test_refine_flag_scope`)

- [ ] **Step 1: Write the failing e2e test**

Add to `tests/test_plugin_e2e.py` (reuse module `PLUGIN_DIR` / `_find_all_commands`):

```python
    def test_refine_flag_scope(self):
        """--refine must appear in exactly the 5 sanctioned commands, no others."""
        allowed = {
            "brainstorm.md", "do.md", "orchestrate.md", "feature.md", "plan.md",
        }
        offenders = []
        for cmd in _find_all_commands():
            if "--refine" in cmd.read_text(encoding="utf-8") and cmd.name not in allowed:
                offenders.append(str(cmd))
        assert not offenders, f"--refine leaked into non-sanctioned commands: {offenders}"
```

> Note: `feature.md` and `plan.md` names are shared by other commands too, but only the sanctioned ones contain `--refine`; the test keys on presence-of-flag, so an accidental flag elsewhere is what it catches.

- [ ] **Step 2: Run it — expect PASS** (Task 2 only added the flag to the 5)

Run: `python3 -m pytest tests/test_plugin_e2e.py -k "test_refine_flag_scope" -v`
Expected: PASS. (Find the enclosing class with `grep -n "def test_mkdocs_nav_not_empty" tests/test_plugin_e2e.py` and place the method in a command-focused test class; if unsure, a module-level `def test_refine_flag_scope():` works too — drop the `self`.)

- [ ] **Step 3: Commit**

```bash
git add tests/test_plugin_e2e.py
git commit -m "test(workflow): e2e scope guard for --refine"
```

---

## Task 4: Dogfood — delegation consistency (anti-drift)

**Files:**

- Modify: `tests/test_plugin_dogfood.py` (new `test_refine_delegates_to_skill`)

- [ ] **Step 1: Write the failing dogfood test**

Add to `tests/test_plugin_dogfood.py` (reuse its `PLUGIN_DIR`; check how that file resolves the plugin root and match it):

```python
def test_refine_delegates_to_skill():
    """Every --refine command must delegate to the skill, not restate the flow."""
    targets = [
        "commands/workflow/brainstorm.md",
        "commands/do.md",
        "commands/orchestrate.md",
        "commands/plan/feature.md",
        "commands/arch/plan.md",
    ]
    bad = []
    for rel in targets:
        text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
        # Must reference the skill by name AND not re-document the picker options.
        delegates = "prompt-refiner" in text
        restates = "Accept/Edit/Use original" in text or "Accept / Edit / Use original" in text
        if not delegates or restates:
            bad.append(rel)
    assert not bad, f"commands must delegate to prompt-refiner, not restate the flow: {bad}"
```

- [ ] **Step 2: Run it — expect PASS** (Task 2's block delegates and does not restate the picker)

Run: `python3 -m pytest tests/test_plugin_dogfood.py -k "test_refine_delegates_to_skill" -v`
Expected: PASS. If FAIL because a command restated the picker options, remove those lines so it only references the skill.

- [ ] **Step 3: Commit**

```bash
git add tests/test_plugin_dogfood.py
git commit -m "test(workflow): dogfood anti-drift for --refine delegation"
```

---

## Task 5: Sync skill count

**Files:**

- Modify: `.claude-plugin/plugin.json`, `CLAUDE.md`

- [ ] **Step 1: See the mismatch**

Run: `./scripts/validate-counts.sh`
Expected: Skills file count is one higher than documented in `plugin.json`.

- [ ] **Step 2: Bump the skill count** in `.claude-plugin/plugin.json` `description` to the number the validator printed (commands unchanged — `--refine` is a flag, not a command).

- [ ] **Step 3: Update `CLAUDE.md`** skill count line + add note: `prompt-refiner skill + --refine flag (5 commands)`.

- [ ] **Step 4: Re-validate**

Run: `./scripts/validate-counts.sh`
Expected: `✓ Skills match`.

- [ ] **Step 5: Run count tests**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_skills_exist tests/test_plugin_e2e.py -k "skill_count" -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/plugin.json CLAUDE.md
git commit -m "chore(workflow): sync skill count for prompt-refiner"
```

---

## Task 6: Docs — help, tutorial, cookbook

**Files:**

- Create: `docs/help/refine-flag.md`, `docs/tutorials/TUTORIAL-refine-flag.md`, `docs/cookbook/recipes/refine-before-running.md`

- [ ] **Step 1: Help page**

Create `docs/help/refine-flag.md` with required sections: (1) What `--refine` does; (2) When to use it (vague prompt on any of the 5 commands); (3) The Accept/Edit/Use-original flow; (4) **`--yes`/auto auto-accepts** — call this out as the one no-confirm path; (5) which 5 commands support it. Lead with one concrete vague→sharp example.

- [ ] **Step 2: Tutorial**

Create `docs/tutorials/TUTORIAL-refine-flag.md`: walk `/brainstorm --refine "add auth"` → before/after box → Accept → brainstorm runs on the refined topic. Embed the Architecture flowchart from `docs/specs/SPEC-refine-flag-2026-06-03.md` (quoted Mermaid node labels — leading-slash labels fail the Mermaid pre-commit check).

- [ ] **Step 3: Cookbook recipe**

Create `docs/cookbook/recipes/refine-before-running.md`:

```markdown
# Recipe: Refine a prompt before running

Add --refine to any of: brainstorm, do, orchestrate, plan:feature, arch:plan.

1. `/craft:do --refine "make the CLI faster"`
2. Review the Original → Refined box.
3. Accept (Recommended) / Edit inline / Use original.
4. The command proceeds on your chosen prompt.

Unattended? `--refine --yes` auto-accepts the refined version.
```

- [ ] **Step 4: Verify links + Mermaid**

Run: `python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v && python3 scripts/mermaid-validate.py docs/tutorials/TUTORIAL-refine-flag.md`
Expected: PASS / `0 errors`.

- [ ] **Step 5: Commit**

```bash
git add docs/help/refine-flag.md docs/tutorials/TUTORIAL-refine-flag.md docs/cookbook/recipes/refine-before-running.md
git commit -m "docs(workflow): help, tutorial, cookbook for --refine"
```

---

## Task 7: Site mirrors, REFCARD, CHANGELOG, /refine sunset

**Files:**

- Modify: `docs/commands/*.md` (5 mirrors), `docs/REFCARD.md`, `CHANGELOG.md`, `docs/CHANGELOG.md`, `commands/workflow/refine.md`

- [ ] **Step 1: Update the 5 site mirrors**

In each of the 5 commands' `docs/commands/*.md` pages, add a one-line `--refine` note linking to `docs/help/refine-flag.md`. Find them with `ls docs/commands/ | grep -E "brainstorm|^do|orchestrate|feature|^plan"`.

- [ ] **Step 2: REFCARD row**

In `docs/REFCARD.md`, add: `| --refine | Refine the prompt before running (brainstorm/do/orchestrate/plan:feature/arch:plan) |`

- [ ] **Step 3: /refine sunset note**

In `commands/workflow/refine.md`, add a line under the deprecation note: `Superseded by the --refine flag (+ prompt-refiner skill). Standalone "refine and print" behavior preserved by the skill.`

- [ ] **Step 4: CHANGELOG (BOTH mirror)**

Under `[Unreleased]` → `### Added` in **both** `CHANGELOG.md` and `docs/CHANGELOG.md`:
`- --refine flag on brainstorm/do/orchestrate/plan:feature/arch:plan — refines the prompt via the new prompt-refiner skill before acting.`

- [ ] **Step 5: Verify counts + links**

Run: `./scripts/validate-counts.sh && python3 -m pytest tests/test_craft_plugin.py::test_no_broken_links -v`
Expected: counts match; links PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/commands/ docs/REFCARD.md CHANGELOG.md docs/CHANGELOG.md commands/workflow/refine.md
git commit -m "docs(workflow): mirrors, refcard, changelog, /refine sunset for --refine"
```

---

## Task 8: Full verification + PR handoff

- [ ] **Step 1: Full unit suite**

Run: `python3 tests/test_craft_plugin.py`
Expected: all pass, incl. `test_prompt_refiner_skill_exists`, `test_refine_flag_documented`.

- [ ] **Step 2: E2E + dogfood**

Run: `python3 -m pytest tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -q`
Expected: all pass, incl. `test_refine_flag_scope`, `test_refine_delegates_to_skill`.

- [ ] **Step 3: Counts + strict site build**

Run: `./scripts/validate-counts.sh && mkdocs build --strict 2>&1 | tail -10`
Expected: counts match; strict build clean.

- [ ] **Step 4: Pre-flight check**

Run: `/craft:check`
Expected: green.

- [ ] **Step 5: Push and STOP (do not open the PR)**

```bash
git push -u origin feature/refine-flag
```

Then print (do not run): `gh pr create --base dev --title "feat: --refine flag + prompt-refiner skill"`

> Opening/merging the PR is the user's call. Stop here.

---

## Self-Review

**Spec coverage** — every spec section maps to a task:

- Shared `prompt-refiner` skill → Task 1. Flag on 5 commands + delegate → Task 2. Before/after + Accept/Edit/Use-original + `--yes` auto-accept → Task 1 skill body. Refine reads context, never executes/writes → Task 1 Constraints. `/refine` sunset → Task 7 Step 3. Skill home = separate skill, inline edit → Task 1 (resolved decisions honored). Counts → Task 5. Docs Deliverables → Tasks 6–7. Testing: unit (Tasks 1–2), e2e scope guard (Task 3), dogfood anti-drift (Task 4), all re-run in Task 8.

**Placeholder scan** — no TBDs; skill frontmatter + body given in full; the exact `--refine` delegation block is provided verbatim for reuse; every test has real code.

**Type/name consistency** — skill name `prompt-refiner` and path `skills/workflow/prompt-refiner/SKILL.md` identical across Tasks 1–8. The five command paths are listed identically in Tasks 2, 4 and the test bodies. The delegation block intentionally does NOT contain the picker option strings, which is exactly what Task 4's dogfood test asserts — consistent by construction.
