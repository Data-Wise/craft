# Interactive-Commands Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make grill/orchestrate ask questions via AskUserQuestion (Recommended-first + per-option consequences) with a `--yes` non-interactive escape hatch, and make `brainstorm`/`do`/`plan:feature`/`grill` run prompt-refiner by default (`--no-refine` to opt out).

**Architecture:** craft commands are LLM-prose markdown in `commands/**/*.md` with YAML frontmatter declaring `arguments`. "Implementation" = editing command `.md` contracts + their referenced skills, guarded by pytest **e2e** tests (structural assertions on the markdown) and **dogfood** tests (behavioral assertions). No application code — the markdown IS the program.

**Tech Stack:** Markdown commands + YAML frontmatter, Python 3 stdlib pytest (`tests/`), `commands/utils/*.py` parsers, pre-commit markdownlint.

**Source spec:** [SPEC-interactive-commands-2026-06-25.md](../specs/SPEC-interactive-commands-2026-06-25.md)

## Global Constraints

- **Branch:** all work in a `feature/interactive-commands` worktree off `dev` — feature changes never on `dev`.
- **Refine sanctioned set is bounded by a test:** `tests/test_plugin_e2e.py::test_refine_flag_scope` asserts the COMPLETE declarer set. Today = 6: `brainstorm`, `do`, `orchestrate`, `plan/feature`, `arch/plan`, `orchestrate/workflow`. This plan adds `grill` → 7. The test's `expected` set MUST be edited in lockstep or the suite goes red.
- **`--yes` is prompts-only:** it auto-accepts AskUserQuestion interactions and refine's Accept/Edit; it does NOT delete emitted content. Independent of `--no-refine`.
- **Default-on keeps the flag declared:** a refine-default-on command STILL declares `- name: refine` in frontmatter (the flag is the opt-out's inverse), so `test_refine_flag_scope`'s keying logic is unchanged — only membership grows.
- **No new commands/skills/agents** → no count cascade (`validate-counts.sh` stays green untouched).
- **Test markers:** dogfood tests need BOTH `pytest.mark.e2e` and `pytest.mark.dogfood` (per `tests/test_plugin_dogfood.py:25`) or they misroute under `/craft:test`.
- **Test helpers (reuse, don't reinvent):** `tests/test_plugin_e2e.py` exposes `PLUGIN_DIR` and `_find_all_commands()` (returns `Path` objects). New e2e tests import/extend these.

---

### Task 1: `--yes` / `--non-interactive` flag on grill + orchestrate

**Files:**

- Modify: `commands/grill.md` (frontmatter `arguments:` block)
- Modify: `commands/orchestrate.md` (frontmatter `arguments:` block)
- Test: `tests/test_interactive_commands_e2e.py` (Create)

**Interfaces:**

- Produces: both commands declare `- name: yes` with `description` mentioning "non-interactive / auto-accept Recommended". Later tasks rely on this flag existing.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_interactive_commands_e2e.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR  # reuse existing helper module

pytestmark = pytest.mark.e2e

YES_COMMANDS = ["commands/grill.md", "commands/orchestrate.md"]

@pytest.mark.parametrize("rel", YES_COMMANDS)
def test_yes_flag_declared(rel):
    text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
    assert "- name: yes" in text, f"{rel} must declare the --yes flag"
    assert "non-interactive" in text.lower(), f"{rel} must document non-interactive semantics"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <worktree> && python3 -m pytest tests/test_interactive_commands_e2e.py::test_yes_flag_declared -v`
Expected: FAIL (flag not yet declared).

- [ ] **Step 3: Add the flag to both command frontmatters**

In `commands/grill.md` and `commands/orchestrate.md`, under `arguments:`, add:

```yaml
  - name: yes
    description: "Non-interactive: auto-accept every Recommended answer, emit zero AskUserQuestion prompts (alias --non-interactive)"
    required: false
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_interactive_commands_e2e.py::test_yes_flag_declared -v`
Expected: PASS (2 params).

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md commands/orchestrate.md tests/test_interactive_commands_e2e.py
git commit -m "feat(grill,orchestrate): add --yes non-interactive flag"
```

---

### Task 2: Invert grill's interaction model (free-text → AskUserQuestion + consequences)

**Files:**

- Modify: `commands/grill.md` (Step 3 loop section + the "no batches" directive)
- Test: `tests/test_interactive_commands_e2e.py` (extend)

**Interfaces:**

- Consumes: nothing.
- Produces: grill.md documents AskUserQuestion-per-branch with Recommended-first + per-option consequences; the old "do not fix to batches" string is gone.

- [ ] **Step 1: Write the failing test**

```python
def test_grill_interaction_model_inverted():
    text = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    # old directive removed
    assert 'do not "fix" to batches' not in text, "old free-text directive must be removed"
    # new contract present
    assert "AskUserQuestion" in text, "grill must document AskUserQuestion-per-branch"
    assert "consequence" in text.lower(), "grill must require a per-option consequence"
    assert "Recommended" in text, "grill must keep Recommended-first"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_interactive_commands_e2e.py::test_grill_interaction_model_inverted -v`
Expected: FAIL on the `do not "fix" to batches` assertion (string still present).

- [ ] **Step 3: Rewrite grill.md Step 3**

In `commands/grill.md`, replace the "### Step 3: The grill loop" prose. Remove the paragraph ending `…AskUserQuestion-batch convention; do not "fix" to batches.` Replace with:

```markdown
### Step 3: The grill loop (deliberate, one question at a time)

Ask **one question per AskUserQuestion call** (NOT 4-question batches — one branch at a time
preserves decision-tree fidelity). For EACH question:

- option[0] is the **Recommended** answer, labelled and reasoned;
- EVERY option carries a one-line **consequence** of choosing it;
- the implicit "Other" free-text path stays open for answers off the menu.

Each answer reshapes the next question. **Halt** on `/done` or empty-enter. `--bound N` stops after
N branches. `--yes` / `--non-interactive`: emit ZERO AskUserQuestion calls — auto-pick every
Recommended, log each pick, and proceed straight to capture.
```

(Keep the existing milestone-checkpoint and capture text below it unchanged.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_interactive_commands_e2e.py::test_grill_interaction_model_inverted -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md tests/test_interactive_commands_e2e.py
git commit -m "feat(grill): structured AskUserQuestion model with Recommended+consequences"
```

---

### Task 3: Refine-on-grill (default-on for topic, skip on path) + bump the scope test

**Files:**

- Modify: `commands/grill.md` (frontmatter + Step 2 path-vs-topic note)
- Modify: `tests/test_plugin_e2e.py:153` (`test_refine_flag_scope` expected set 6 → 7)
- Test: `tests/test_interactive_commands_e2e.py` (extend, path rule)

**Interfaces:**

- Consumes: Task 1's frontmatter edits to grill.md.
- Produces: grill.md declares `- name: refine`; documents "default-on for topic, skip on path".

- [ ] **Step 1: Write the failing tests**

```python
def test_grill_declares_refine():
    text = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    assert "- name: refine" in text

def test_grill_refine_path_rule():
    text = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    assert "skip" in text.lower() and "path" in text.lower(), \
        "grill must document: skip refine when arg is a path"
```

And edit the existing scope test in `tests/test_plugin_e2e.py` — add `"commands/grill.md"` to the `expected` set (changing its assertion from 6 to 7 members). Run it FIRST to watch it fail:

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_interactive_commands_e2e.py::test_grill_declares_refine tests/test_plugin_e2e.py::test_refine_flag_scope -v`
Expected: both FAIL (grill not yet a declarer; scope test now expects grill but it's absent).

- [ ] **Step 3: Add refine to grill + the path rule**

In `commands/grill.md` frontmatter `arguments:`, add:

```yaml
  - name: refine
    description: "Refine the topic via prompt-refiner BEFORE grilling. Default-ON for a quoted/bare topic; SKIPPED when the argument is a path (a spec/plan file — nothing to refine). --no-refine to disable."
    required: false
```

In Step 2 (target resolution), add a sentence: *"When the argument is a quoted/bare topic, run prompt-refiner on it first (default-on; `--no-refine` skips). When the argument is a path, skip refine entirely."*

In `tests/test_plugin_e2e.py::test_refine_flag_scope`, add `"commands/grill.md"` to the `expected` literal set.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_interactive_commands_e2e.py -k grill tests/test_plugin_e2e.py::test_refine_flag_scope -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md tests/test_plugin_e2e.py tests/test_interactive_commands_e2e.py
git commit -m "feat(grill): refine default-on for topic (skip on path); scope 6->7"
```

---

### Task 4: Refine default-on for brainstorm / do / plan:feature

**Files:**

- Modify: `commands/workflow/brainstorm.md`, `commands/do.md`, `commands/plan/feature.md` (flip `--refine` doc to default-on; add `--no-refine`)
- Test: `tests/test_interactive_commands_dogfood.py` (Create)

**Interfaces:**

- Consumes: existing `- name: refine` declarations (already present in all 3).
- Produces: each documents "runs by default; `--no-refine` to skip".

- [ ] **Step 1: Write the failing test**

```python
# tests/test_interactive_commands_dogfood.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

DEFAULT_ON = ["commands/workflow/brainstorm.md", "commands/do.md", "commands/plan/feature.md"]

@pytest.mark.parametrize("rel", DEFAULT_ON)
def test_refine_default_on_documented(rel):
    text = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "default" in text and "no-refine" in text, \
        f"{rel} must document refine default-on + --no-refine opt-out"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_refine_default_on_documented -v`
Expected: FAIL (currently documented as opt-in).

- [ ] **Step 3: Flip the docs in all 3 commands**

In each command's `--refine` section, change the description to:

> Runs the prompt-refiner **by default** to pre-process your input. Pass `--no-refine` to skip. Under `--yes`, the refiner auto-accepts (no Accept/Edit prompt).

Also add to each frontmatter `arguments:` a `- name: no-refine` entry documenting the opt-out.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_refine_default_on_documented -v`
Expected: PASS (3 params).

- [ ] **Step 5: Commit**

```bash
git add commands/workflow/brainstorm.md commands/do.md commands/plan/feature.md tests/test_interactive_commands_dogfood.py
git commit -m "feat(brainstorm,do,plan): refine on by default (--no-refine to opt out)"
```

---

### Task 5: `--yes` cascade contract (refine auto-accept + suppressed loop)

**Files:**

- Modify: `commands/grill.md`, `commands/orchestrate.md` (document the cascade)
- Modify: `skills/workflow/prompt-refiner/SKILL.md` (confirm `--yes`/auto auto-accept is documented)
- Test: `tests/test_interactive_commands_dogfood.py` (extend)

**Interfaces:**

- Consumes: Tasks 1–4 flags.
- Produces: documented contract that one `--yes` both auto-accepts refine AND suppresses the interactive loop.

- [ ] **Step 1: Write the failing test**

```python
def test_yes_cascade_documented():
    grill = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8").lower()
    assert "zero askuserquestion" in grill or "auto-pick every recommended" in grill
    refiner = (PLUGIN_DIR / "skills/workflow/prompt-refiner/SKILL.md").read_text(encoding="utf-8").lower()
    assert "auto" in refiner and ("--yes" in refiner or "auto-accept" in refiner), \
        "prompt-refiner must document an auto-accept path for --yes"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_yes_cascade_documented -v`
Expected: FAIL if the refiner's auto path isn't explicit.

- [ ] **Step 3: Document the cascade**

In `commands/grill.md` and `commands/orchestrate.md`, add one line near the `--yes` doc: *"`--yes` cascades: the prompt-refiner auto-accepts AND the interactive loop is suppressed — one flag, fully headless."* Confirm/clarify the auto-accept path in `prompt-refiner/SKILL.md` (it already supports `--yes`/auto per the refine flow; make the phrasing explicit).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_yes_cascade_documented -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md commands/orchestrate.md skills/workflow/prompt-refiner/SKILL.md tests/test_interactive_commands_dogfood.py
git commit -m "feat: document --yes cascade (refine auto-accept + suppressed loop)"
```

---

### Task 6: Orchestrate Step 0.5 clarify adopts the D1 model + honors `--yes`

**Files:**

- Modify: `commands/orchestrate.md` (Step 0.5 clarify section)
- Test: `tests/test_interactive_commands_dogfood.py` (extend)

**Interfaces:**

- Consumes: Task 1's `--yes` on orchestrate; grill's embedded `--no-capture` clarify path.
- Produces: orchestrate clarify documents AskUserQuestion + consequences + `--yes` honoring.

- [ ] **Step 1: Write the failing test**

```python
def test_orchestrate_clarify_model():
    text = (PLUGIN_DIR / "commands/orchestrate.md").read_text(encoding="utf-8")
    assert "Step 0.5" in text
    lo = text.lower()
    assert "askuserquestion" in lo and "consequence" in lo, \
        "orchestrate Step 0.5 must adopt the structured model"
    assert "--yes" in text, "orchestrate clarify must honor --yes"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_orchestrate_clarify_model -v`
Expected: FAIL.

- [ ] **Step 3: Update Step 0.5**

In `commands/orchestrate.md` Step 0.5, document that clarify questions use AskUserQuestion-per-branch with Recommended-first + per-option consequences, and that `--yes` propagates to the embedded grill (`--no-capture`) path so a headless orchestrate run asks nothing.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_interactive_commands_dogfood.py::test_orchestrate_clarify_model -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/orchestrate.md tests/test_interactive_commands_dogfood.py
git commit -m "feat(orchestrate): Step 0.5 clarify uses structured model + honors --yes"
```

---

### Task 7: Docs cascade + memory + full-suite gate

**Files:**

- Modify: `commands/hub.md` (refine "opt-in" → "default-on"; grill row notes `--yes`)
- Modify: root `CHANGELOG.md` AND `docs/CHANGELOG.md` (mirror — `### Changed`)
- Modify/Create: memory entry retiring grill's old "free-text/no-batches" design note
- Run: `scripts/docs-staleness-check.sh --fix`

- [ ] **Step 1: Flip refine references**

Run: `grep -rl "refine" docs/ site/ commands/hub.md` — change opt-in phrasing to default-on for the 4 affected commands.

- [ ] **Step 2: CHANGELOG (both files, mirrored)**

Add under `## [Unreleased]` → `### Changed` in BOTH `CHANGELOG.md` and `docs/CHANGELOG.md`:

```markdown
- grill/orchestrate now ask questions via structured options (Recommended-first + consequences); add `--yes` for non-interactive runs.
- `brainstorm`, `do`, `plan:feature`, `grill` run the prompt-refiner by default (`--no-refine` to opt out).
```

- [ ] **Step 3: Retire the stale grill design memory**

Update any memory file pinning grill's "deliberate free-text, no batches" rationale to reflect the new structured-options model (so future sessions don't re-assert the old design).

- [ ] **Step 4: Staleness sweep + full suite**

Run: `bash scripts/docs-staleness-check.sh --fix` then `python3 -m pytest tests/ -q`
Expected: docs clean; full suite green (incl. the bumped `test_refine_flag_scope`).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs: refine default-on + grill/orchestrate interaction model (changelog, hub, memory)"
```

---

## Self-Review

- **Spec coverage:** D1→Tasks 2/6; D2→Task 1; D3→Task 4; D4→Task 5; D6→Task 3; §4 e2e→Tasks 1-3,6; §4 dogfood→Tasks 4-6; §7 docs→Task 7. ✓ all mapped.
- **Placeholder scan:** none — every step has concrete test code, edit content, and commands.
- **Type consistency:** flag names (`yes`, `no-refine`, `refine`) and the `expected` scope-set membership are consistent across tasks 1, 3, 4, 5.

## Execution Handoff

Implement in a `feature/interactive-commands` worktree (created via superpowers:using-git-worktrees). Then subagent-driven-development (fresh subagent per task, review between).
