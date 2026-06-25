# SPEC: Default-on test-plan + docs scaffolding for spec-producing commands

**Status:** APPROVED (design) · **Date:** 2026-06-25 · **Driver:** user directive (auto test + docs scaffolding by default, disable flags)
**Sibling:** [SPEC-interactive-commands-2026-06-25.md](SPEC-interactive-commands-2026-06-25.md) — same `default-on + --no-* opt-out` family (refine, interaction model). This spec adds the **test** and **docs** dimensions.
**Designed with:** superpowers:brainstorming + experienced-engineer testing-specialist & devops-engineer agent passes (2026-06-25).

---

## 1. Problem

craft's spec/plan-producing commands emit a design but leave **test planning** and **doc
planning** to the author's discipline. Two recurring failures: specs ship without a test plan
(tests bolted on later, ad hoc), and the ~15-file doc cascade is forgotten until the post-release
sweep catches drift. The fix: make both **default-on, auto-derived sections** of every emitted
spec — with `--no-tests` / `--no-docs` opt-outs — generalizing the refine-default-on pattern.

## 2. Locked decisions

| # | Decision | Detail |
|---|----------|--------|
| **D1** | **Two new default-on dimensions** | `--no-tests` (test-plan scaffold) and `--no-docs` (docs scaffold + wired auto-update). Default-on, opt-out, mirroring `--no-refine`. |
| **D2** | **Separate spec** | This is a distinct cross-cutting capability — its own spec, its own implementation plan. (Not folded into the interactive-commands spec.) |
| **D3** | **Command scope** | Default-ON for `brainstorm`, `plan:feature`, `grill` (the true feature-spec producers). `arch:plan` + `spec-review` stay **opt-in** (`--tests`/`--docs`) — their args are often paths, so inference is weak. Matches the §8 refine matrix in the sibling spec. |
| **D4** | **Logic lives in skills, not deprecated command bodies** | `brainstorm.md` + `plan/feature.md` are deprecated → put the generator logic in `skills/workflow/brainstorm-insights/` + `skills/orchestration/plan-orchestrator/` + `commands/orchestrate/plan.md`; command `.md` is a thin pointer. (Deprecated-command rich-body trap — ADR-002.) `grill.md`, `arch:plan.md` are NOT deprecated — logic can live inline or in a shared reference. |
| **D5** | **Flags independent of `--yes`** | `--yes` auto-accepts *prompts* only; it does NOT suppress these sections (they are content, not interaction). `--no-tests`/`--no-docs` are the only switches that remove them. Independent of each other and of `--yes`. |
| **D6** | **Docs lifecycle split** | "Auto-update docs" = (a) spec-time: emit section + pre-derive boxes, **read-only**; (b) impl/post-merge: real edits via existing `/craft:docs:update --post-merge` + `docs-staleness-check.sh --fix`, **diff-confirm gated** (only `--yes`/headless skips). The spec wires (b) as a checklist item; it never edits docs for not-yet-written code at spec-time. |
| **D7** | **Scope guard against count-cascade drift** | Auto-docs owns *semantic* docs only (CHANGELOG `[Unreleased]` ×2 mirror, guide/refcard/tutorial prose). The *mechanical* count cascade (`bump-version.sh` 13 files, `(N craft)` subtotal, badges, version refs) stays release-time. They never write the same lines. |
| **D8** | **No new testing agent** | craft ships no `testing-specialist` agent; use skills only (`test-strategist`, `test-generator`) + superpowers TDD. Avoids the ~30-file count cascade a new agent triggers. |

## 3. Dimension 1 — test-plan scaffold (`--no-tests`)

### 3.1 Tier inference (key on the artifact that changed, not the "feature")

| Change shape | Tiers | Target file convention |
|--------------|-------|------------------------|
| flag / frontmatter / command-prose only | **e2e + dogfood** | `test_<feat>_e2e.py`, `test_<feat>_dogfood.py` |
| + new inline-Python parser or `scripts/*.sh` | **+ unit** | `test_<name>.py` / `.sh` |
| + cross-command data flow (producer→consumer) | **+ integration** | `test_integration_<feat>.py` |
| + dependency detect/install | **+ dependency** | append `test_dependency_management.sh` |
| + new command / skill / agent | **+ count-cascade dogfood** | assert `validate-counts.sh` exits 0 + `plugin.json (N craft)` subtotal |

Unselected tiers render as `N/A — <reason>` lines (reviewed, never trusted blindly) — never empty stubs.

### 3.2 Generated section template (red-first, contract-asserting)

```markdown
## N. Test plan (TDD)
Tier selection (auto): e2e + dogfood. unit N/A — no new parser/script.
integration N/A — single-command. Markers: e2e, dogfood.

### Na. e2e — structural, no execution (tests/test_<feat>_e2e.py)
- [ ] **test_<feat>_scope** (EDIT/NEW): assert the COMPLETE declarer set (any add/remove breaks it).
- [ ] **<contract> declared**: new contract present AND old/inverted contract absent.

### Nb. dogfood — behavioral, real invocation (tests/test_<feat>_dogfood.py)
- [ ] **<behavior> fires**: invoke on a fixture → assert real output/side-effect.
- [ ] **<opt-out> skips**: same invocation with the disable flag → effect absent.

Red-first: write Na/Nb FAILING first; implement to green; run via /craft:test.
```

One checklist item per **contract or behavior**, never per function.

### 3.3 Anti-boilerplate guardrails

- **Keep-rule:** a scaffolded test earns its place only if a plausible future edit would break it.
- Prefer **complete-set scope assertions** (like `test_refine_flag_scope`) over `assert "x" in frontmatter` (tautology — restates the diff, drop it).
- Prefer **behavioral dogfood** (subprocess + asserted output) over source-presence greps.
- Generator marks any item it can't tie to a behavior with `# TODO(author): delete if not contract-bearing` so reviewers prune.

### 3.4 Runnability

- Dogfood tests MUST carry **both** `pytest.mark.e2e` and `pytest.mark.dogfood` (per `test_plugin_dogfood.py:25`) or they misroute under `/craft:test`.
- File names follow the auto-collected convention so `/craft:test <tier>` and full `pytest tests/` pick them up with no config edit.
- Skills: plan-time references `skills/testing/test-strategist`; impl-time uses `skills/testing/test-generator` + `superpowers:test-driven-development`.

## 4. Dimension 2 — docs scaffold + auto-update (`--no-docs`)

### 4.1 Generated "Documentation" section

Canonical template = the existing block at `commands/workflow/brainstorm.md:403-411` — **lift it verbatim** (don't author a competitor), promote to `skills/workflow/brainstorm-insights/references/doc-section-template.md`, reference from each producer. Structure (checklist, N/A-mark unaffected): tutorial · help + command-ref pages · refcard entry · hub/smart-help discovery · website nav + `skills-agents.md` row · CHANGELOG `[Unreleased]` + bumps.

**Deriving WHICH docs:** reuse craft's existing scorer (`commands/docs/sync.md:233` / `update.md:744` — new command +1 refcard, new module +3 guide, new hook +3 mermaid, multi-step +3 tutorial, threshold ≥3). Feed the spec's stated change-shape to the same scorer to pre-check boxes. **No new rubric.**

### 4.2 Lifecycle (D6)

| Phase | Action | Writes files? | Default |
|-------|--------|---------------|---------|
| **Spec-time** (producer runs) | emit section + pre-derive/check boxes via scorer | **No** (read-only) | **on** (`--no-docs` skips) |
| **Impl/post-merge** | real edits via `/craft:docs:update --post-merge` then `docs-staleness-check.sh --fix` | Yes | gated: diff + confirm (only `--yes`/headless skips) |

"Auto-update by default" = section always emitted + pre-derived; the *edits* are the spec's documented impl step, run when code exists.

### 4.3 CHANGELOG + cascade safety (D7)

CHANGELOG writes go to **both** root `CHANGELOG.md` and `docs/CHANGELOG.md` (mirror rule), `[Unreleased]` only. **Exclude** mechanical counts/versions/badges — release-time territory. Enforce via the impl step's category filter (a `--no-changelog`-style guard so counts are never touched pre-release).

### 4.4 Branch/safety

Editing **existing** `.md` is dev-safe (branch table). **Creating new** tutorial/refcard/guide files needs a `feature/*` worktree — and at impl-time the docs ride in the feature worktree alongside code anyway. Spec-time derivation is read-only, safe everywhere. **Never silent auto-commit** of doc edits.

## 5. Test plan (TDD) — for THIS spec's implementation

Two tiers (this is itself a flag + skill-logic change → e2e + dogfood; the doc-scorer reuse adds a unit slice).

### 5a. e2e (structural — `tests/test_scaffold_defaults_e2e.py`)

- [ ] **test_scaffold_flag_scope** (NEW, complete-set): `--no-tests` and `--no-docs` declared in EXACTLY {brainstorm, plan:feature, grill} default-on set; `--tests`/`--docs` opt-in declared in {arch:plan, spec-review}. Any add/remove breaks it.
- [ ] **default-on contract present**: the 3 default-on commands/skills document "test plan + docs emitted by default; `--no-tests`/`--no-docs` to skip".
- [ ] **logic-in-skills**: `brainstorm-insights` + `plan-orchestrator` skills carry the generator/template reference; deprecated `brainstorm.md`/`plan/feature.md` are thin pointers (guards the deprecation trap).
- [ ] **doc-section-template promoted**: `skills/workflow/brainstorm-insights/references/doc-section-template.md` exists and matches the canonical `brainstorm.md:403-411` block.

### 5b. dogfood (behavioral — `tests/test_scaffold_defaults_dogfood.py`)

- [ ] **tier inference**: a flag-only change-shape → emitted section selects e2e+dogfood, marks unit/integration `N/A`.
- [ ] **--no-tests skips**: producer run with `--no-tests` emits NO test-plan section.
- [ ] **--no-docs skips**: producer run with `--no-docs` emits NO Documentation section.
- [ ] **doc-scorer reuse**: change-shape "1 new command" pre-checks the refcard + tutorial + CHANGELOG boxes (assert against the existing scorer's output, not a reimplementation).
- [ ] **--yes does NOT suppress sections**: `--yes` run still emits both sections (content, not prompt).
- [ ] **count-cascade exclusion**: the impl-time docs step never edits a version/count line (assert the category filter blocks it).

### 5c. unit (`tests/test_doc_scorer_changeshape.py`)

- [ ] scorer maps a structured change-shape descriptor → the correct doc-box set (reuses `docs/sync.md` logic; no new rubric).

## 6. Documentation (for THIS spec's implementation)

- [ ] `skills/workflow/brainstorm-insights/SKILL.md` + `skills/orchestration/plan-orchestrator/SKILL.md` — document the two default-on dimensions + flags.
- [ ] `commands/{workflow/brainstorm,plan/feature,grill,arch/plan,workflow/spec-review}.md` — flag tables: `--no-tests`/`--no-docs` (default-on trio) or `--tests`/`--docs` (opt-in pair).
- [ ] `commands/hub.md` / `help:refcard` — note the new defaults.
- [ ] CHANGELOG ×2 mirror — `### Added`: default-on test+docs scaffolding for spec producers.
- [ ] `docs-staleness-check.sh --fix` sweep after edits.
- [ ] Memory: record the "spec producers scaffold tests+docs by default" pattern + the deprecation-trap placement.

## 7. Cascade / non-goals

- **No new commands or agents** → no 30-file count cascade (flag + skill-logic only).
- **Non-goal:** changing what tests/docs are *correct* — only that a *scaffold* is emitted by default.
- **Non-goal v1:** auto-running the impl-time doc edits without confirm (gated always, except headless `--yes`).
- **Non-goal v1:** default-on for `arch:plan`/`spec-review` (opt-in only).

## 8. Open questions (resolve at implementation)

1. Shared reference vs per-command duplication for the test-plan template — lean a single `references/` doc both the skills and the non-deprecated commands (grill, arch:plan) point to.
2. Does `grill` (convergent, often path-arg) emit a *test* scaffold, or only when its target is a topic/feature? Lean: same path-vs-topic rule as its refine (D6 sibling spec) — scaffold for topic, skip for path.
3. Exact name of the impl-time count-exclusion guard (`--no-changelog` exists; may need `--semantic-only`).

---

## Handoff

`/craft:plan` (tier 4) → `ORCHESTRATE-spec-scaffold-defaults.md` → worktree → TDD per §5.
Sequence after / alongside the sibling interactive-commands spec (shared `--yes` + default-on plumbing).
