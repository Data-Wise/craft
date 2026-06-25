# Spec-Scaffold-Defaults Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `brainstorm`/`plan:feature`/`grill` emit a tier-inferred test-plan section and a doc-scorer-derived Documentation section into every spec by default, with `--no-tests`/`--no-docs` opt-outs; `arch:plan`/`spec-review` get the same as opt-in (`--tests`/`--docs`).

**Architecture:** Logic lives in the SKILLS behind the deprecated commands (`brainstorm-insights`, `plan-orchestrator`) plus `commands/orchestrate/plan.md`, sharing one `references/scaffold-templates.md`. Commands are thin pointers. Both dimensions are content emitted into the spec artifact; doc EDITS are a separate gated impl-time step, never done at spec-write time.

**Tech Stack:** Markdown skills/commands, Python 3 stdlib pytest, the existing doc-scorer in `commands/docs/sync.md` / `update.md`.

**Source spec:** [SPEC-spec-scaffold-defaults-2026-06-25.md](../specs/SPEC-spec-scaffold-defaults-2026-06-25.md)

## Global Constraints

- **DEPENDS ON Plan 1** (`2026-06-25-interactive-commands.md`) being merged to `dev` first — reuses its `--yes` flag + default-on/`--no-*` plumbing + refine-on-grill (D9c).
- **Branch:** `feature/spec-scaffold-defaults` worktree off `dev` (after Plan 1 merges).
- **Deprecation trap (ADR-002):** `brainstorm.md` + `plan/feature.md` are deprecated — generator logic goes in their SKILLS, not the command bodies. A test enforces this.
- **`--yes` does NOT suppress sections** — they're content. Only `--no-tests`/`--no-docs` remove them. Independent flags.
- **Count-cascade exclusion (D7):** auto-docs touches ONLY semantic docs (CHANGELOG `[Unreleased]` ×2 mirror, guide/refcard/tutorial prose) — never version/count lines. Mechanical cascade stays release-time.
- **grill scaffolds on TOPIC, skips on PATH** (D9a) — same rule as its refine.
- **No new commands/agents** → no count cascade. Test markers: dogfood needs both `e2e` + `dogfood` marks.
- **Reuse helpers:** `tests/test_plugin_e2e.py` `PLUGIN_DIR` + `_find_all_commands()`.

---

### Task 1: Shared `scaffold-templates.md` reference (test + doc templates)

**Files:**

- Create: `skills/workflow/brainstorm-insights/references/scaffold-templates.md`
- Test: `tests/test_scaffold_defaults_e2e.py` (Create)

**Interfaces:**

- Produces: a reference doc holding (a) the red-first test-plan template and (b) the doc-section template lifted verbatim from `commands/workflow/brainstorm.md:403-411`. All producers point here (D9b).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scaffold_defaults_e2e.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = pytest.mark.e2e

TEMPLATES = PLUGIN_DIR / "skills/workflow/brainstorm-insights/references/scaffold-templates.md"

def test_scaffold_templates_exist():
    assert TEMPLATES.exists(), "shared scaffold-templates.md must exist"
    body = TEMPLATES.read_text(encoding="utf-8")
    assert "Test plan (TDD)" in body, "must hold the test-plan template"
    assert "Documentation" in body, "must hold the doc-section template"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <worktree> && python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_scaffold_templates_exist -v`
Expected: FAIL (file absent).

- [ ] **Step 3: Create the shared reference**

Create `skills/workflow/brainstorm-insights/references/scaffold-templates.md` containing the two canonical templates: the test-plan block from SPEC §3.2 and the Documentation block lifted verbatim from `commands/workflow/brainstorm.md:403-411`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_scaffold_templates_exist -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/brainstorm-insights/references/scaffold-templates.md tests/test_scaffold_defaults_e2e.py
git commit -m "feat(scaffold): shared scaffold-templates.md (test + doc templates)"
```

---

### Task 2: Flag scope — `--no-tests`/`--no-docs` (default-on trio) + `--tests`/`--docs` (opt-in pair)

**Files:**

- Modify: `commands/workflow/brainstorm.md`, `commands/plan/feature.md`, `commands/grill.md` (declare `no-tests`, `no-docs`)
- Modify: `commands/arch/plan.md`, `commands/workflow/spec-review.md` (declare opt-in `tests`, `docs`)
- Test: `tests/test_scaffold_defaults_e2e.py` (extend — complete-set assertion)

**Interfaces:**

- Produces: the exact flag membership later tasks and `/craft:test` rely on.

- [ ] **Step 1: Write the failing test (complete-set, breaks on any drift)**

```python
DEFAULT_ON = {"commands/workflow/brainstorm.md", "commands/plan/feature.md", "commands/grill.md"}
OPT_IN = {"commands/arch/plan.md", "commands/workflow/spec-review.md"}

def test_scaffold_flag_scope():
    no_tests, no_docs, opt_tests, opt_docs = set(), set(), set(), set()
    for cmd in PLUGIN_DIR.glob("commands/**/*.md"):
        rel = str(cmd.relative_to(PLUGIN_DIR))
        t = cmd.read_text(encoding="utf-8")
        if "- name: no-tests" in t: no_tests.add(rel)
        if "- name: no-docs" in t: no_docs.add(rel)
        if "- name: tests" in t: opt_tests.add(rel)
        if "- name: docs" in t: opt_docs.add(rel)
    assert no_tests == DEFAULT_ON, f"no-tests scope drift: {no_tests ^ DEFAULT_ON}"
    assert no_docs == DEFAULT_ON, f"no-docs scope drift: {no_docs ^ DEFAULT_ON}"
    assert opt_tests == OPT_IN, f"opt-in tests scope drift: {opt_tests ^ OPT_IN}"
    assert opt_docs == OPT_IN, f"opt-in docs scope drift: {opt_docs ^ OPT_IN}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_scaffold_flag_scope -v`
Expected: FAIL (no declarers yet).

- [ ] **Step 3: Declare the flags**

In the 3 default-on commands, add to `arguments:`:

```yaml
  - name: no-tests
    description: "Skip the auto-emitted test-plan section (on by default)"
    required: false
  - name: no-docs
    description: "Skip the auto-emitted Documentation section (on by default)"
    required: false
```

In `arch/plan.md` + `spec-review.md`, add the opt-in inverses:

```yaml
  - name: tests
    description: "Opt in to emitting a test-plan section (off by default here)"
    required: false
  - name: docs
    description: "Opt in to emitting a Documentation section (off by default here)"
    required: false
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_scaffold_flag_scope -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/workflow/brainstorm.md commands/plan/feature.md commands/grill.md commands/arch/plan.md commands/workflow/spec-review.md tests/test_scaffold_defaults_e2e.py
git commit -m "feat(scaffold): --no-tests/--no-docs default-on trio + --tests/--docs opt-in pair"
```

---

### Task 3: Tier-inference + test-plan emission logic (in skills)

**Files:**

- Modify: `skills/workflow/brainstorm-insights/SKILL.md`, `skills/orchestration/plan-orchestrator/SKILL.md` (tier-inference rule + emission, pointing at `scaffold-templates.md`)
- Test: `tests/test_scaffold_defaults_dogfood.py` (Create)

**Interfaces:**

- Consumes: `scaffold-templates.md` (Task 1), flags (Task 2).
- Produces: documented behavior — given a change-shape, emit the right tiers; `--no-tests` suppresses.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scaffold_defaults_dogfood.py
import pytest
from test_plugin_e2e import PLUGIN_DIR
pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

SKILLS = ["skills/workflow/brainstorm-insights/SKILL.md",
          "skills/orchestration/plan-orchestrator/SKILL.md"]

@pytest.mark.parametrize("rel", SKILLS)
def test_tier_inference_documented(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "tier" in t and "dogfood" in t and "scaffold-templates" in t, \
        f"{rel} must document tier inference + reference scaffold-templates.md"
    assert "no-tests" in t, f"{rel} must document the --no-tests opt-out"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_tier_inference_documented -v`
Expected: FAIL.

- [ ] **Step 3: Add the emission logic to both skills**

In each skill, add a "Test-plan scaffolding (default-on)" subsection: the §3.1 tier-inference table (flag-only → e2e+dogfood; +parser/script → unit; +cross-command → integration; +deps → dependency; +new cmd/skill/agent → count-cascade dogfood), the red-first emission referencing `references/scaffold-templates.md`, the `# TODO(author): delete if not contract-bearing` marker rule, and the `--no-tests` opt-out. For grill: emit only on a TOPIC arg.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_tier_inference_documented -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/brainstorm-insights/SKILL.md skills/orchestration/plan-orchestrator/SKILL.md tests/test_scaffold_defaults_dogfood.py
git commit -m "feat(scaffold): tier-inference + test-plan emission in skills"
```

---

### Task 4: Documentation section + doc-scorer reuse

**Files:**

- Modify: same two skills (Documentation-section emission + scorer reuse)
- Test: `tests/test_scaffold_defaults_dogfood.py` (extend) + `tests/test_doc_scorer_changeshape.py` (Create, unit)

**Interfaces:**

- Consumes: the doc-scorer rubric in `commands/docs/sync.md:233`.
- Produces: documented behavior — emit a Documentation section with boxes pre-checked by the existing scorer; `--no-docs` suppresses.

- [ ] **Step 1: Write the failing tests**

```python
# in test_scaffold_defaults_dogfood.py
@pytest.mark.parametrize("rel", SKILLS)
def test_docs_section_documented(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "documentation" in t and "no-docs" in t and "scorer" in t, \
        f"{rel} must document the docs-section emission + scorer reuse + --no-docs"

# tests/test_doc_scorer_changeshape.py (unit)
import pytest
from test_plugin_e2e import PLUGIN_DIR
pytestmark = pytest.mark.unit

def test_scorer_rubric_present():
    # The reused rubric (threshold >=3) must still live in docs/sync.md — not reimplemented.
    body = (PLUGIN_DIR / "commands/docs/sync.md").read_text(encoding="utf-8").lower()
    assert "refcard" in body and "tutorial" in body, "doc-scorer rubric must remain the single source"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_docs_section_documented tests/test_doc_scorer_changeshape.py -v`
Expected: `test_docs_section_documented` FAILs (not yet documented).

- [ ] **Step 3: Add the Documentation-section logic**

In both skills, add a "Documentation scaffolding (default-on)" subsection: emit the doc-section template from `scaffold-templates.md`, derive which boxes via the existing scorer (`commands/docs/sync.md` rubric, threshold ≥3) — pre-check matching boxes, mark the rest `N/A`; state the lifecycle split (spec-time = read-only emit; impl-time = gated `docs:update --post-merge` edits); the count-cascade exclusion (D7); the `--no-docs` opt-out.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_docs_section_documented tests/test_doc_scorer_changeshape.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/brainstorm-insights/SKILL.md skills/orchestration/plan-orchestrator/SKILL.md tests/test_scaffold_defaults_dogfood.py tests/test_doc_scorer_changeshape.py
git commit -m "feat(scaffold): docs-section emission + doc-scorer reuse"
```

---

### Task 5: Deprecation-trap guard — logic in skills, commands are pointers

**Files:**

- Modify: `commands/workflow/brainstorm.md`, `commands/plan/feature.md` (ensure thin pointers to the skills)
- Test: `tests/test_scaffold_defaults_e2e.py` (extend)

**Interfaces:**

- Produces: a regression test that the scaffolding logic is NOT duplicated into the deprecated command bodies.

- [ ] **Step 1: Write the failing test**

```python
def test_logic_lives_in_skills_not_deprecated_commands():
    # the deprecated commands must POINT to the skill, not embed the tier-inference table
    for rel in ["commands/workflow/brainstorm.md", "commands/plan/feature.md"]:
        t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
        assert "brainstorm-insights" in t or "plan-orchestrator" in t, \
            f"{rel} must point to its skill"
        # tier-inference table belongs in the skill, not the deprecated command body
        assert "count-cascade dogfood" not in t, \
            f"{rel} must NOT embed the tier table (deprecation trap)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_logic_lives_in_skills_not_deprecated_commands -v`
Expected: FAIL if a pointer is missing or logic leaked into the command.

- [ ] **Step 3: Make the commands thin pointers**

Ensure each deprecated command's scaffolding mention is a one-line pointer to its skill (`see skills/workflow/brainstorm-insights/` etc.), with no embedded tier table.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold_defaults_e2e.py::test_logic_lives_in_skills_not_deprecated_commands -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/workflow/brainstorm.md commands/plan/feature.md tests/test_scaffold_defaults_e2e.py
git commit -m "feat(scaffold): keep logic in skills, deprecated commands are pointers"
```

---

### Task 6: `--yes` non-suppression + count-cascade exclusion

**Files:**

- Modify: both skills (explicit contracts)
- Test: `tests/test_scaffold_defaults_dogfood.py` (extend)

**Interfaces:**

- Produces: two explicit contracts — `--yes` keeps the sections; the impl-time doc step never edits counts/versions.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.parametrize("rel", SKILLS)
def test_yes_nonsuppression_and_cascade_exclusion(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "yes" in t and "content" in t, \
        f"{rel} must state --yes does NOT suppress sections (they are content)"
    assert "count" in t and ("exclud" in t or "never" in t), \
        f"{rel} must state the count-cascade exclusion"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_yes_nonsuppression_and_cascade_exclusion -v`
Expected: FAIL.

- [ ] **Step 3: Add the two contracts**

In both skills, add: *"`--yes` auto-accepts prompts only; the test-plan and Documentation sections are CONTENT and are still emitted under `--yes`. Only `--no-tests`/`--no-docs` remove them."* And: *"The impl-time doc step edits semantic docs only and NEVER touches version/count lines (the mechanical cascade stays release-time)."*

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold_defaults_dogfood.py::test_yes_nonsuppression_and_cascade_exclusion -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/brainstorm-insights/SKILL.md skills/orchestration/plan-orchestrator/SKILL.md tests/test_scaffold_defaults_dogfood.py
git commit -m "feat(scaffold): --yes non-suppression + count-cascade exclusion contracts"
```

---

### Task 7: Docs cascade + memory + full-suite gate

**Files:**

- Modify: `commands/hub.md` / refcard (note new defaults), root + `docs/CHANGELOG.md` (mirror), memory
- Run: `scripts/docs-staleness-check.sh --fix`, full suite

- [ ] **Step 1: CHANGELOG (both, mirrored)**

Add under `## [Unreleased]` → `### Added` in BOTH files:

```markdown
- `brainstorm`/`plan:feature`/`grill` emit a tier-inferred test plan + a doc-scorer Documentation section by default (`--no-tests`/`--no-docs` to opt out); `arch:plan`/`spec-review` opt-in via `--tests`/`--docs`.
```

- [ ] **Step 2: hub + refcard**

Note the new default-on scaffolding in `commands/hub.md` and `help:refcard`.

- [ ] **Step 3: Memory**

Record the pattern: "craft spec-producers scaffold tests+docs by default; logic in skills (deprecation-trap-safe); docs auto-update is lifecycle-split + count-cascade-excluded."

- [ ] **Step 4: Staleness sweep + full suite**

Run: `bash scripts/docs-staleness-check.sh --fix` then `python3 -m pytest tests/ -q`
Expected: docs clean; full suite green; `validate-counts.sh` exits 0 (no new commands/agents).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(scaffold): changelog, hub/refcard, memory + staleness sweep"
```

---

## Self-Review

- **Spec coverage:** D1→Tasks 2-4; D3 scope→Task 2; D4 deprecation→Task 5; D5 `--yes`→Task 6; D6 lifecycle→Task 4; D7 exclusion→Task 6; D8 no-agent→Global Constraints; D9 (grill topic/path, shared template, sequencing)→Tasks 1-3 + Global. §5 e2e→Tasks 1,2,5; §5 dogfood→Tasks 3,4,6; §5c unit→Task 4; §6 docs→Task 7. ✓
- **Placeholder scan:** none — concrete test code + edit content + commands per step.
- **Type consistency:** flag names (`no-tests`/`no-docs`/`tests`/`docs`) and the `DEFAULT_ON`/`OPT_IN` membership sets are consistent across Tasks 2, 5, 6.

## Execution Handoff

Implement in a `feature/spec-scaffold-defaults` worktree AFTER Plan 1 merges to `dev`. Then subagent-driven-development.
