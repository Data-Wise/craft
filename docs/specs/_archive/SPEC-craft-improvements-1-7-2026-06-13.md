# SPEC: Craft Improvements — Brainstorm Items 1–7 (post-v2.36.0)

<!-- markdownlint-disable MD033 MD052 -->
<!-- This spec quotes regex (e.g. [0-9]+) and shell placeholders (e.g. <run-id>)
     verbatim from planning-agent output; MD033/MD052 are disabled file-wide. -->

**Status:** done — all 7 items SHIPPED in v2.37.0 (PRs #151/#152/#153/#154/#155 → dev, PR #156 → main `8c21a54d`, 2026-06-13). Post-release sweep ALL CLEAN.
**Created:** 2026-06-13
**From Brainstorm:** `BRAINSTORM-craft-improvements-2026-06-13.md` (post-v2.36.0 workflow-engine release)
**Planned via:** dynamic Workflow (8 agents — 7 `feature-dev:code-architect` planners + 1 synthesis)
**Author:** dt + Claude

---

## Overview

Seven concrete improvements distilled from the friction of the v2.36.0 release
(the manual mermaid `--admin` detour, recurring count-string drift, hand-archiving
shipped specs) plus the new surface the workflow engine makes possible. Each item
below carries a full implementation blueprint (approach, files, steps, tests, risks)
produced by a per-item planning agent reading the real craft code.

**Total effort:** ~12.5h across **6 PRs in 4 phases**. Two strict serial chains:
`#7 → #2` (the drift tripwire must police the subtotal format #7 establishes) and
`#5 → #6` (`ci:watch` forward-references `ci:triage` and shares count/See-Also files).
The three independent items (#1, #3, #4) float — any order, parallel-safe.

---

## Sequenced roadmap

### Phase 1 — Independent quick wins (parallel-safe foundations)

**Items:** 1-strict-markers, 4-recipe-discoverability, 3-auto-archive-specs  ·  **Effort:** ~3h (1: 30min, 4: 30min, 3: 2h)

Three fully-independent items with zero file overlap and no count bumps, so they carry the lowest merge risk and unblock nothing else's critics. Split into TWO PRs by domain affinity: (PR-1a) items 1-strict-markers + 4-recipe-discoverability — both are tiny (30 min each), test-only/frontmatter-only touches that pair naturally as a 'test + discovery hygiene' branch (1 edits test_craft_plugin.py + reads pyproject.toml; 4 edits workflow.md frontmatter + test_hub_e2e_focused.py; disjoint files). (PR-1b) item 3-auto-archive-specs alone — it adds a whole new Phase 5 to post-release-sweep.sh plus a new test file and touches release-checklist/SKILL docs; large enough and release-pipeline-adjacent enough to warrant its own review and its own worktree. Run these first because none depend on anything and they de-risk the test harness before the bigger count-bump work.

### Phase 2 — Version-drift tooling (must precede the tripwire)

**Items:** 7-bump-subtotals  ·  **Effort:** 2h

Solo PR/worktree. 7-bump-subtotals is the hard dependency for 2-drift-tripwire (the tripwire's Phase 7 regex must run against the **N commands** / categorical-subtotal format that 7 establishes and keeps in sync). Landing 7 first means the repo's subtotals are actually correct before the tripwire starts failing CI on them, avoiding a chicken-and-egg where the tripwire fires on drift 7 was meant to eliminate. Sole owner of bump-version.sh; only co-edits test_plugin_dogfood.py. Keep isolated so the ~40 sed sweeps get focused review.

### Phase 3 — CI drift tripwire (consumes Phase 2's format)

**Items:** 2-drift-tripwire  ·  **Effort:** 2h

Solo PR, gated behind 7-bump-subtotals merging to dev. Adds README.md to docs-staleness-check.sh Phase 7, populates exclusions.txt, hardens validate-counts.sh, and adds a new tripwire test file. Must come AFTER 7 so its exclusion list and live-count regions reflect 7's now-synced subtotals; otherwise the tripwire and the bumper disagree about which counts are 'live'. No file overlap with 7 except the shared-spirit of count management, so a clean sequential merge.

### Phase 4 — CI triage + watch (shared count-bump + shared ci command files)

**Items:** 5-ci-triage, 6-ci-watch  ·  **Effort:** 3.5h (5: 2h, 6: 1.5h)

ONE shared worktree, merged as TWO stacked PRs in strict order 5 then 6 (6 explicitly depends on 5). They MUST be coordinated because they collide on three files: plugin.json description and CLAUDE.md header (5 bumps 110→111, 6 bumps 111→112 — uncoordinated separate branches would conflict on the second merge), and commands/ci/status.md See Also (both edit the same section). 6's red-path 'unknown' case forward-references /craft:ci:triage, so shipping 5 first turns that into a live link instead of a dead reference. Branch ci-triage off dev, merge it, then rebase ci-watch on the updated dev so it bumps from the correct 111 baseline. Do them last because they're the only net-new commands (highest count-drift surface) and benefit from Phase 2/3's drift tooling already guarding the tree.

### Recommended first PR

PR-1a = item 1-strict-markers paired with item 4-recipe-discoverability. Rationale: both are 30-minute, dependency-free, disjoint-file changes with no count bumps, so they carry the least merge risk and the fastest path to a green PR. Item 1 (a marker-registration guard test) also strengthens the test harness itself before the heavier count-bump and new-command work in later phases — every subsequent phase adds pytest marks/tests, so locking the strict-markers contract first prevents a rogue unregistered mark from silently slipping in during phases 2-4. Pairing it with item 4 (pure frontmatter + one targeted discovery assertion) keeps the PR tiny while clearing two backlog items at once.

### Cross-item notes & sequencing constraints

OVERLAPS / SEQUENCING CONSTRAINTS:

1) Count-string collision (CRITICAL): items 5, 6, and 7 all mutate plugin.json's description and CLAUDE.md's command-count header. 5 and 6 each increment the command total (+1 each), and 7 sweeps categorical subtotals. Never run 5 and 6 on independent branches off the same base — the second to merge will conflict on the count. Stack them (5→6, rebasing 6 after 5 merges). 7 is on a different file (bump-version.sh) but governs the SAME count strings' format, so it should land before the tripwire (2) that polices them.

2) ci:triage (5) vs ci:watch (6) — deliberate, bounded overlap, NOT duplication. 5 is the deep classifier (parses --log-failed, classifies DIFF-CAUSED/PRE-EXISTING/INFRA-FLAKE/PARTIAL with evidence). 6 is the poller that waits for completion and, on red, does lightweight inline triage for the two clear-cut cases (in-diff → ci-fix; 'Validate Plugin Structure' stuck → --admin) and forwards the 'unknown' case to /craft:ci:triage. Therefore 6 depends on 5 so its forward reference is live. Both also touch commands/ci/status.md's See Also — coordinate in one worktree to avoid edit conflicts.

3) Tripwire (2) depends on bump-subtotals (7): 2's own plan lists 7 as a dependency and notes its Phase 7 regex (\b[0-9]+ TYPE\b) must remain robust to the **N commands** bold format 7 may produce. Land 7 first so the tree's subtotals are synced before the tripwire starts failing CI; otherwise the tripwire fires on the very drift 7 exists to remove.

4) Independent set (1, 3, 4): no count bumps, disjoint files, no inter-dependencies — safe to develop/merge in any order relative to each other and to the rest. 3 touches the release pipeline (post-release-sweep.sh) but not counts, so it's orthogonal to the count-drift cluster (2/7).

5) Test-tree-mutation guard: items 3 (new test_post_release_sweep.py) and 2 (new test_count_drift_tripwire.py) both add scripts that can run with --fix; per the v2.36.0 post-mortem (and the 'No-fix-against-PLUGIN_DIR' guard in test_docs_staleness.py), each new test file MUST include the structural regression guard asserting no test invokes --fix against the real tree, and `git status` must be clean after a full pytest run. Verify this in both PRs.

6) Effort total ≈ 12.5h across 6 PRs in 4 phases. Phases 2→3 are strictly serial (7 then 2). Phase 4 is internally serial (5 then 6). Phase 1's three items can run in parallel with each other and with Phase 2 if reviewer bandwidth allows, since they share no files with the count-drift cluster.

**Total effort:** ~12.5h of implementation across 6 PRs in 4 phases (1: 30min, 4: 30min, 3: 2h, 7: 2h, 2: 2h, 5: 2h, 6: 1.5h). Two strict serial chains: 7→2 (tripwire needs the synced subtotal format) and 5→6 (watch forward-references triage and shares count/See-Also files). The three independent items (1, 4, 3) can overlap with the chains given reviewer bandwidth.

---

## Per-item blueprints

### 1-strict-markers — Strict-markers guard test: assert every pytest.mark.X in tests/ is registered in pyproject.toml

**Effort:** 30 min  ·  **Dependencies:** none

**Approach:** Add a single pure-Python test function to `/Users/dt/projects/dev-tools/craft/tests/test_craft_plugin.py` that (1) parses the registered marker names from `pyproject.toml` using `tomllib` (stdlib in Python 3.11+, else `tomli` fallback), (2) walks every `tests/*.py` and `tests/demo_*.py` file with a regex extracting all `pytest.mark.<name>` tokens, (3) strips the six built-in pytest marks (`parametrize`, `skipif`, `xfail`, `skip`, `filterwarnings`, `usefixtures`), and (4) asserts the used set is a subset of the registered set, reporting every unregistered mark and the file(s) that use it. No new file is needed — `test_craft_plugin.py` already carries the `integration`+`structure` marks and tests plugin meta-contracts at this level.

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/tests/test_craft_plugin.py`

**Key steps:**

1. Read pyproject.toml using `tomllib.loads()` (Python 3.11 stdlib; fall back to `import tomli as tomllib` for older envs). Extract the registered marker short-names by splitting each entry in `tool.pytest.ini_options.markers` on the first `:` and stripping whitespace — this gives the canonical set.
2. Walk `tests/` with `Path(__file__).parent.parent / 'tests'` and collect every `.py` file (including `demo_*.py` — three demo files use marks). Apply `re.findall(r'pytest\.mark\.(\w+)', text)` to each file's content to collect every raw mark token used in that file.
3. Subtract the built-in pytest marks set `{'parametrize', 'skipif', 'xfail', 'skip', 'filterwarnings', 'usefixtures'}` from the collected tokens before comparing. These are built-in and intentionally not listed in pyproject.toml markers.
4. Assert `used_marks - registered_marks == set()`. On failure, build a diagnostic message that maps each unregistered mark name to the list of files that reference it, so the developer sees exactly which files introduced the rogue mark — same style as the `test_skill_count_predicates_use_canonical_marker` diagnostic already in test_craft_plugin.py.
5. Place the test as a top-level function named `test_all_pytest_marks_are_registered` in the existing `# ─── Plugin Structure Tests ─────` section of `test_craft_plugin.py`, immediately after `test_directory_structure`. No new imports needed beyond `tomllib`/`tomli` — `re`, `Path`, and `sys` are already imported in that file.
6. Verify the test passes locally against the current pyproject.toml markers (all marks in use are already registered as of v2.35.0). The test must be self-contained and pass with `python3 -m pytest tests/test_craft_plugin.py::test_all_pytest_marks_are_registered -v`.

**Tests:**

- test_all_pytest_marks_are_registered passes on current tree (all marks registered)
- Manually add a fake `pytest.mark.notregistered` line to a test file, confirm the test fails with a clear diagnostic naming that file and mark
- Remove the fake line, confirm the test passes again — regression guard is live

**Risks:**

- Python version: `tomllib` is stdlib only from 3.11+. The craft CI runner's Python version must be checked (likely 3.11+ given recent pyproject.toml usage, but if 3.10 is in use, add `try: import tomllib except ImportError: import tomli as tomllib` and add `tomli` to `testing` optional deps in pyproject.toml).
- String-only mark references: marks spelled as strings (e.g. `@pytest.mark.custom` via `m.mark` attribute access or `getattr(pytest.mark, name)`) would not be caught by the regex — but audit of the craft test tree shows all marks are used as direct decorator syntax `pytest.mark.<name>`, so this is low risk.
- Demo files (demo_layer2.py, demo_layer3.py, demo_teaching_validation.py) use marks but are not prefixed `test_`. The implementation must glob `tests/*.py` not just `tests/test_*.py` to catch them — confirmed they use `e2e`, `hub`, and `teaching` marks which are all registered, so no false positive today, but the broader glob is the correct contract.

---

### 4-recipe-discoverability — Surface cookbook recipes from /craft:orchestrate:workflow

**Effort:** 30 min  ·  **Dependencies:** none

**Approach:** Add `related_commands`, `tutorial_file`, and `tags` fields to the frontmatter of `commands/orchestrate/workflow.md`, and extend the prose "See Also" section to link both cookbook recipes. No new files, no changes to `_discovery.py` or `_schema.json` — both already fully support these fields. The `tutorial_file` field carries the primary recipe path as structured metadata; the "See Also" prose body exposes both recipes for humans reading the command. The test suite already has `test_workflow_discover_related_commands` in `tests/test_hub_e2e_focused.py` which validates related commands resolve — it will now exercise workflow.md's new frontmatter. One targeted test assertion is added to verify `orchestrate:workflow` specifically has the expected related_commands and tutorial_file set.

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/commands/orchestrate/workflow.md`
- `/Users/dt/projects/dev-tools/craft/tests/test_hub_e2e_focused.py`

**Key steps:**

1. Read the existing frontmatter of commands/orchestrate/workflow.md (already done — confirmed no related_commands, tutorial_file, or tags keys exist)
2. Add to the frontmatter block in commands/orchestrate/workflow.md: `related_commands: [orchestrate, orchestrate:drive]`, `tutorial_file: docs/cookbook/recipes/run-a-coded-workflow.md`, `tags: [workflow, orchestration, parallel, fan-out, yaml]` — insert between the last argument block and the closing `---`
3. Extend the '## See Also' section prose in commands/orchestrate/workflow.md to add two cookbook recipe bullet lines: '- [Run a coded workflow](../../docs/cookbook/recipes/run-a-coded-workflow.md) — cookbook: write a WORKFLOW-*.yaml, dry-run preview, execute, resume' and '- [Fan a workflow across files](../../docs/cookbook/recipes/fan-a-workflow-across-files.md) — cookbook: list → parallel-per-file → gate → summarize pattern'
4. Verify command-audit.sh still passes: both `related_commands` and `tutorial_file` are already in VALID_FIELDS (scripts/command-audit.sh line 22) — no change needed
5. Delete commands/_cache.json (gitignored) to force discovery regeneration on next run, or run `python3 commands/_discovery.py` to verify the new frontmatter parses without warnings
6. Add one targeted test assertion in tests/test_hub_e2e_focused.py (or a new test in tests/test_craft_plugin.py) asserting that `get_command_detail('orchestrate:workflow')` returns a record with `related_commands` containing 'orchestrate' and 'orchestrate:drive', and `tutorial_file` set to the recipe path
7. Run full test suite: `python3 tests/test_craft_plugin.py && python3 -m pytest tests/test_hub_e2e_focused.py -v` to confirm no regressions and the new assertion passes

**Tests:**

- Existing: tests/test_hub_e2e_focused.py::test_workflow_discover_related_commands — already iterates all commands looking for any with related_commands; after this change it will find orchestrate:workflow and validate that 'orchestrate' and 'orchestrate:drive' resolve via get_command_detail()
- New assertion in tests/test_hub_e2e_focused.py (or test_craft_plugin.py): get_command_detail('orchestrate:workflow') is not None; cmd['related_commands'] == ['orchestrate', 'orchestrate:drive']; 'tutorial_file' in cmd and 'run-a-coded-workflow' in cmd['tutorial_file']
- Existing: python3 commands/_discovery.py — run CLI mode to confirm no parse warnings on the updated frontmatter
- Existing: bash scripts/command-audit.sh — confirm no unknown-field errors for tutorial_file or related_commands on orchestrate/workflow.md

**Risks:**

- The `tutorial_file` path stored in frontmatter is metadata-only — _discovery.py stores it but generate_command_tutorial() never renders it. The field is discoverable via the cache/API but will not auto-appear in /craft:hub tutorial boxes until a renderer reads it. This is acceptable: the 'See Also' prose in the command body is the primary human surface.
- Relative markdown links in 'See Also' (../../docs/cookbook/recipes/...) are correct for the MkDocs build (commands/ is at the same level as docs/) but may look odd if someone reads the raw .md file. Alternative: use absolute site paths or skip the relative link in prose and just name the recipes — the frontmatter metadata is the machine-readable surface.
- test_workflow_discover_related_commands in test_hub_e2e_focused.py picks the FIRST command with related_commands and validates its related commands resolve. After this change, orchestrate:workflow will be one candidate; the test only validates the first found, so it may not exercise workflow.md specifically unless the new targeted assertion is also added.

---

### 3-auto-archive-specs — Auto-archive shipped specs at release

**Effort:** 2h  ·  **Dependencies:** none

**Approach:** Add a new Phase 5 to `scripts/post-release-sweep.sh` (inserted before the current Phase 5 Summary block) that scans `docs/specs/SPEC-*.md`, identifies specs whose `**Status:**` line contains the word `done` (case-insensitive), stamps the SHIPPED version into the status line if it is absent, and performs `git mv` to `docs/specs/_archive/`. In dry-run mode it reports candidates without touching files; in `--fix` mode it updates the status line and moves the file. No new script is needed — the pattern exactly mirrors Phase 2 (`FIX_MODE` branching, `add_finding()`, phase-level output) and reuses `$CHECK_VERSION`. A companion Python test in `tests/test_post_release_sweep.py` (new file) validates dry-run and fix-mode behaviour against a temp tree.

**Files to create:**

- `tests/test_post_release_sweep.py`

**Files to edit:**

- `scripts/post-release-sweep.sh`
- `skills/release/references/release-checklist.md`
- `skills/release/SKILL.md`

**Key steps:**

1. Read the spec header detection contract: grep each `docs/specs/SPEC-*.md` for `^\*\*Status:\*\*` (line 1-10 of each file). A spec is archivable when the matched line contains the substring `done` (case-insensitive) — covers `done`, `done ✅`, `done — SHIPPED`, `implemented`, etc. This matches the real archived corpus (SPEC-command-audit, SPEC-workflow-engine, SPEC-craft-hub-v2, SPEC-bump-version-docs, SPEC-claude-md-refactor, SPEC-docs-update-interactive, SPEC-command-enhancements, SPEC-teaching-ecosystem-coordination).
2. Add a SHIPPED_SPECS_ISSUES counter and a SHIPPED_SPECS_FIXED counter to the result-tracking block in post-release-sweep.sh (after line 108 in the current file). These roll into TIER2_ISSUES/TIER2_FIXED so the existing JSON and summary output picks them up without structural changes to the Phase 5 summary.
3. Insert Phase 5 (Spec Archiving) as a new bash block after Phase 4 (line ~331) and before the current Phase 5 Summary block. Structure: (a) ensure `docs/specs/_archive/` exists; (b) iterate `docs/specs/SPEC-*.md`; (c) for each file, extract the Status line with `grep -m1 '^\*\*Status:\*\*' "$file"`; (d) if the line matches `done|implemented` (case-insensitive) and the file is NOT already in _archive; (e) in DRY_RUN mode: call `add_finding` with tier=2, file path, detail='archivable spec (Status: done)', fixable=auto, and print YELLOW ARCHIVE-READY; (f) in FIX_MODE: if status line does not already contain 'SHIPPED in v', prepend 'done — SHIPPED in v${CHECK_VERSION} (archived $(date +%Y-%m-%d))' to the status value using `sed -i ''` (BSD-safe, matching existing Phase 2 sed calls at lines 184-188); then `git mv "$file" "docs/specs/_archive/$(basename $file)"`; increment TIER2_FIXED; add_finding with 'ARCHIVED'; print GREEN ARCHIVED.
4. Update the JSON output block (current Phase 5, lines 340-368) to include a `shipped_specs_archived` field derived from TIER2_FIXED additions. Because TIER2_FIXED is already accumulated, the existing `"tier2_fixed": ${TIER2_FIXED}` field automatically captures it — no JSON schema change required.
5. Add Phase 5 mention to the script's header comment (lines 3-15) and the --help output (lines 52-57): 'Phase 5: Spec archiving — moves docs/specs/SPEC-*.md with Status: done to docs/specs/_archive/'.
6. Create `tests/test_post_release_sweep.py` following the pattern of `tests/test_docs_staleness.py`: a `PLUGIN_DIR` constant, a `_run_script(*args)` helper using `subprocess.run`, and test classes: `TestSpecArchivingDryRun` (verifies ARCHIVE-READY in stdout, no file moves in dry-run), `TestSpecArchivingFixMode` (temp-tree isolation: copy a SPEC-*.md with Status: done into a temp docs/specs/, run --fix, assert the file is now in _archive/ and status line was stamped, and the source is gone), `TestSpecArchivingSkipsNonDone` (spec with Status: draft is not touched), `TestSpecArchivingAlreadyArchived` (a file already in_archive/ is not re-processed), `TestNoFixInvocationTargetsRealTree` (mirror the guard from test_docs_staleness.py: assert test methods never run --fix against PLUGIN_DIR directly).
7. Update `skills/release/references/release-checklist.md` Post-Release section: add a checklist item '[ ] `./scripts/post-release-sweep.sh --fix` archived shipped SPEC-*.md files to docs/specs/_archive/'.
8. Update `scripts/post-release-sweep.sh` --help text and the dry-run display block in `skills/release/SKILL.md` (line ~63: `13.5 Post-release sweep`) to mention spec archiving as part of that step.
9. Run `python3 -m pytest tests/test_post_release_sweep.py -v` (new file) and full `python3 -m pytest tests/ -v` to confirm no regressions, then confirm `git status` is clean after the full test run (guards against the test-mutates-tree class of bugs found in v2.36.0).

**Tests:**

- TestSpecArchivingDryRun::test_done_spec_reported_as_archive_ready — run sweep dry-run on a temp tree with a SPEC-*.md whose Status is 'done'; assert stdout contains 'ARCHIVE-READY' and the file still exists in docs/specs/
- TestSpecArchivingDryRun::test_exit_code_1_when_archivable_specs_found — dry-run exits 1 (drift found) when at least one archivable spec is present, matching existing Tier 2 behaviour
- TestSpecArchivingFixMode::test_file_moved_to_archive — run sweep --fix on isolated temp tree; assert file is gone from docs/specs/ and present in docs/specs/_archive/
- TestSpecArchivingFixMode::test_status_line_stamped_with_version — after --fix, the archived file's Status line contains 'SHIPPED in v' + the current version
- TestSpecArchivingFixMode::test_already_has_shipped_stamp_not_duplicated — if Status already has 'SHIPPED in v2.36.0', running --fix again does not double-stamp the line
- TestSpecArchivingSkipsNonDone::test_draft_spec_untouched — spec with '**Status:** draft' is neither reported nor moved
- TestSpecArchivingSkipsNonDone::test_approved_spec_untouched — spec with '**Status:** approved' is neither reported nor moved
- TestSpecArchivingAlreadyArchived::test_archive_dir_files_not_re_processed — docs/specs/_archive/SPEC-*.md files are excluded from the scan
- TestNoFixInvocationTargetsRealTree::test_no_test_calls_fix_against_plugin_dir — AST or grep scan of this test file itself, asserting no subprocess call combines PLUGIN_DIR with --fix (mirrors guard from test_docs_staleness.py line 46-55)
- TestJsonOutput::test_json_includes_tier2_fixed_count — run sweep --json --fix on temp tree; parse JSON; assert tier2_fixed > 0 and clean == false initially, clean == true after fix

**Risks:**

- Status line heterogeneity — the active specs folder has 'Status: implemented — Batches 1+2+3 complete' (SPEC-commands-to-skills-migration) which contains neither 'done' nor simple 'implemented'. That spec is partially done (v3.0.0 cleanup still pending). The detection pattern must NOT match 'implemented' as a blanket trigger; recommend matching only bare `done` or `done —` prefix, not `implemented` alone. The commands-to-skills spec would then require a manual Status update to `done — SHIPPED` before being auto-archived.
- Sed -i '' BSD vs GNU portability — existing Phase 2 (lines 184-188) already uses `sed -i ''` throughout and the script has a BSD note in bump-version.sh. Phase 5 must follow the same `sed -i ''` idiom. CI runs on GitHub Actions (Ubuntu = GNU sed). Mitigate by using the `-e` form: `sed -i'' -e 's/pattern/replacement/'` which is compatible with both, OR follow the existing script convention since the script already accepts this risk.
- git mv inside a script requires the script to be run from within the git repo root — `cd "$PLUGIN_DIR"` at line 69 already ensures this. However if post-release-sweep is run from a worktree, the git mv will target the worktree's index, not main. Document that spec archiving should only run from the main repo checkout (after Step 11 dev-sync in the release pipeline).
- False positives for superseded/abandoned specs — some specs with 'Status: draft' in _archive were moved manually without updating the status. The new automation only processes the active `docs/specs/SPEC-*.md` directory (not_archive/), so there is no risk of re-archiving. But SPEC files with ambiguous status like 'WIP' (SPEC-test-gen-refactor) will correctly be skipped.
- Test isolation — the v2.36.0 post-mortem found two cases where tests mutated the real source tree (test_command_audit.py and test_docs_staleness.py). The new test_post_release_sweep.py must never pass PLUGIN_DIR to a --fix run. Include the structural regression guard (test_no_fix_invocation_targets_real_tree) as the very first test in the file.

---

### 7-bump-subtotals — Extend bump-version.sh to sweep categorical subtotal headers

**Effort:** 2h  ·  **Dependencies:** none

**Approach:** Add a new "Subtotals" section to /Users/dt/projects/dev-tools/craft/scripts/bump-version.sh that (a) computes per-category command counts by walking commands/ subdirectories (mirroring the breakdown already in validate-counts.sh), (b) computes per-category skill counts by walking skills/ subdirectories, and (c) fires idempotent sed sweeps against every file that contains hardcoded categorical subtotals. Two tiers of subtotals exist: simple total-only headers (README.md "## Skills (17)", REFCARD.md "## Skills (38 total)", docs/skills-agents.md sub-category headers like "### Architecture (1)") and composite strings that interleave a category label and count in ASCII art (hub.md "CODE (15)", "GIT (14 incl. 4 guides)", "ORCHESTRATE (5)"). Simple headers use a sed pattern per category; composite hub.md counts use per-category sed patterns keyed on the label text. A new compute_category_counts() helper function runs the find/wc logic and exports shell variables (CODE_COUNT, DOCS_COUNT, etc.) used by the sed invocations.

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/scripts/bump-version.sh`
- `/Users/dt/projects/dev-tools/craft/tests/test_plugin_dogfood.py`

**Key steps:**

1. Step 1 — Audit and enumerate every categorical subtotal occurrence. Run: grep -n '### .* ([0-9]' README.md; grep -n 'CODE ([0-9]\|DOCS ([0-9]\|GIT ([0-9]\|SITE ([0-9]\|ARCH ([0-9]\|PLAN ([0-9]\|CI ([0-9]\|DIST ([0-9]\|WORKFLOW ([0-9]\|TEST ([0-9]\|ORCHESTRATE ([0-9]' commands/hub.md docs/commands/hub.md. Produce the definitive hit-list before writing a single sed pattern. Confirm the hit-list matches what was found in this blueprint: README.md (18 category headers), commands/hub.md and docs/commands/hub.md (11 ASCII-banner category labels), docs/skills-agents.md (15 sub-category headers like ### Architecture (1)), docs/REFCARD.md '## Skills (38 total)' and '## Agents (8 specialized)', docs/commands/overview.md (7 category headers). README.md's '## Skills (17)' and '## Agents (7)' are already swept by existing sed; verify and skip those duplicates.
2. Step 2 — Add a compute_category_counts() function near the top of /Users/dt/projects/dev-tools/craft/scripts/bump-version.sh (after the existing CMD_COUNT/SKILL_COUNT/AGENT_COUNT block). This function walks commands/ subdirectories with find commands/<subdir> -name '*.md' ! -name 'index.md' ! -name 'README.md' | wc -l for each of: workflow, do (smart), code, test, arch, plan, docs, site, git, ci, dist, orchestrate. It also separately counts skills per subdirectory: find skills/<subdir> -name 'SKILL.md' | wc -l for each of: architecture, check, ci, code, design, dev, distribution, docs, guard-audit, modes, orchestration, planning, release, testing, workflow. Export all as shell variables: CMD_CODE_COUNT, CMD_DOCS_COUNT, CMD_GIT_COUNT, CMD_SITE_COUNT, CMD_WORKFLOW_COUNT, CMD_TEST_COUNT, CMD_ARCH_COUNT, CMD_PLAN_COUNT, CMD_CI_COUNT, CMD_DIST_COUNT, CMD_ORCH_COUNT, SKILL_ARCH_COUNT, SKILL_DIST_COUNT, SKILL_DOCS_COUNT, etc.
3. Step 3 — Add a 'Subtotals section' comment block in bump-version.sh after the existing Text files section. Handle README.md category headers. Use one sed per category label. Pattern for simple 'CommandName Commands (N)' lines: sed -i '' 's|### Code Commands ([0-9][0-9]*)|### Code Commands ('$CMD_CODE_COUNT')|g' README.md (repeat for each of: Workflow, Smart, Code, Test, Architecture, Planning, Documentation, Site, Git, CI, Distribution — 11 sed calls). For '## Commands (110 total)': sed -i '' 's|^## Commands ([0-9][0-9]* total)|## Commands ('$CMD_COUNT' total)|' README.md. For '## Skills (N)' in README.md that are NOT already swept (the ones showing actual count like 17, not bold-starred): sed -i '' 's|^## Skills ([0-9][0-9]*)|## Skills ('$SKILL_COUNT')|' README.md. For '## Agents (N)': same pattern. Note: the existing bold-starred ** patterns already handle **N skills** so only the bare header form needs new sweeps.
4. Step 4 — Handle commands/hub.md and docs/commands/hub.md category labels in ASCII banner. For each of the 11 category labels that appear as LABEL (N) inside the box art, add a pair of sed calls (one per file). Use literal text anchoring to avoid false-positives since these are inside pipe-bordered lines. Example patterns: sed -i '' 's|CODE ([0-9][0-9]*)|CODE ('$CMD_CODE_COUNT')|g' commands/hub.md; sed -i '' 's|DOCS ([0-9][0-9]*)|DOCS ('$CMD_DOCS_COUNT')|g' commands/hub.md. The GIT line is special — it contains 'incl. 4 guides' suffix. Pattern: sed -i '' 's|GIT ([0-9][0-9]* incl\. [0-9]* guides)|GIT ('$CMD_GIT_COUNT' incl. 4 guides)|g'. For ORCHESTRATE: sed -i '' 's|ORCHESTRATE ([0-9][0-9]*)|ORCHESTRATE ('$CMD_ORCH_COUNT')|g'. Apply identical sed calls to docs/commands/hub.md.
5. Step 5 — Handle docs/skills-agents.md sub-category headers. These are '### CategoryName (N)' lines. The top-level '## Skills (N total)' and '## Agents (N total)' are already swept by existing code at line 326-328. Add 15 new sed calls for the sub-category headers, e.g.: sed -i '' 's|^### Architecture ([0-9][0-9]*)|### Architecture ('$SKILL_ARCH_COUNT')|' docs/skills-agents.md. Repeat for Check, CI, Code, Design, Dev, Distribution, Documentation, 'Guard & Insights', Modes, Orchestration, Planning, Release, Testing, Workflow. The 'Guard & Insights' label contains an ampersand — escape it in the sed pattern as 'Guard & Insights' (no escaping needed for &, only for sed's replacement side; use a variable substitution with single-quote boundary to keep & literal in the replacement).
6. Step 6 — Handle docs/REFCARD.md. '## Skills (38 total)' pattern: sed -i '' 's|^## Skills ([0-9][0-9]* total)|## Skills ('$SKILL_COUNT' total)|' docs/REFCARD.md. '## Agents (8 specialized)' pattern: sed -i '' 's|^## Agents ([0-9][0-9]* specialized)|## Agents ('$AGENT_COUNT' specialized)|' docs/REFCARD.md. These are distinct from the existing REFCARD version-badge sweeps at lines 285-289 of bump-version.sh, which target 'version-X.Y.Z' patterns.
7. Step 7 — Handle docs/commands/overview.md category headers. Pattern examples: sed -i '' 's|Smart and Discovery ([0-9][0-9]*)|Smart and Discovery ('$CMD_SMART_COUNT')|g' docs/commands/overview.md. Apply per-category for: Smart and Discovery, Documentation Commands, Site Commands, Code Commands, Testing Commands, Git Commands, CI Commands. Also update the mermaid flowchart labels inside overview.md that show 'Docs (21)', 'Code (15)', etc. if they are hardcoded.
8. Step 8 — Update --verify mode in bump-version.sh to check a sample of the new categorical subtotals. Add checks: grep -q '## Commands ('$CMD_COUNT' total)' README.md or flag as drift; grep -q 'CODE ('$CMD_CODE_COUNT')' commands/hub.md or flag as drift. Keep to ~4-5 spot checks (not all 40+) to avoid bloat. The full CI tripwire (item 2 in BRAINSTORM) is a separate item.
9. Step 9 — Update FILE_COUNT at line 78 (currently 13). Count new files being newly managed — overview.md is new, REFCARD.md subtotals are new. Increment FILE_COUNT to 15 and update the comment, then ensure docs/reference/configuration.md 'across N files' sed sweep picks up the new number automatically (it already does at line 315).
10. Step 10 — Add tests. Add a TestBumpVersionSubtotals class to /Users/dt/projects/dev-tools/craft/tests/test_plugin_dogfood.py (or a new test_bump_version_subtotals.py). Tests: (a) run bump-version.sh --counts-only --dry-run and assert exit 0; (b) run bump-version.sh --verify and assert exit 0 including the new spot checks; (c) in a tempdir, write a stub README.md with a stale '## Commands (99 total)' header, run bump-version.sh --counts-only against it, assert the header was rewritten to the correct count. Mirror pattern from existing dogfood tests in test_plugin_dogfood.py that use_run_script().
11. Step 11 — Run the full test suite (python3 -m pytest tests/ -v) and validate-counts.sh, pre-release-check.sh against the current version before committing.

**Tests:**

- test_bump_version_subtotals_dry_run_exits_zero: run 'bash scripts/bump-version.sh --counts-only --dry-run' from PLUGIN_DIR, assert returncode==0 and 'would update' appears in stdout
- test_bump_version_verify_passes_on_clean_repo: run 'bash scripts/bump-version.sh --verify' from PLUGIN_DIR after running --counts-only to sync, assert returncode==0
- test_bump_version_rewrites_readme_commands_total: copy README.md to tempfile, inject stale '## Commands (99 total)', point bump-version at it, assert corrected to '## Commands (<ACTUAL> total)'
- test_bump_version_rewrites_hub_category_labels: copy commands/hub.md to tempfile, inject stale 'CODE (99)', run bump-version, assert 'CODE (<CMD_CODE_COUNT>)' in output
- test_bump_version_rewrites_skills_agents_subcategory_headers: copy docs/skills-agents.md to tempfile, inject stale '### Distribution (99)', run bump-version --counts-only, assert corrected to '### Distribution (<SKILL_DIST_COUNT>)'
- test_bump_version_rewrites_refcard_skills_agents_headers: copy docs/REFCARD.md to tempfile, inject stale '## Skills (99 total)', run bump-version, assert corrected

**Risks:**

- GIT label in hub.md uses composite format 'GIT (14 incl. 4 guides)' — the 'incl. 4 guides' suffix is a static annotation that does NOT come from file counting. The sed pattern must preserve the suffix while replacing only the numeric prefix. If the suffix ever changes (e.g., more guides are added), the pattern will need updating. Mitigation: use 'GIT ([0-9][0-9]*incl\. [0-9]* guides)' on the match side and reconstruct dynamically by separately computing CMD_GIT_GUIDES_COUNT from find commands/git/docs.
- README.md category sections are intentionally stale — they were written at plugin version v1.x and many counts reflect the old command structure (e.g., '## Skills (17)' reflects a much earlier state). The sed sweep will bring them up to date, which is correct, but any reviewer might question why README category numbers now differ from the narrative prose around them. Mitigation: after applying sweeps, do a manual read-through of the README sections to confirm narrative consistency.
- docs/skills-agents.md sub-category headers reflect actual SKILL.md counts per subdirectory. If a skill subdirectory is renamed or restructured, both the directory-walk in bump-version.sh AND the header in skills-agents.md must be updated atomically. Mitigation: validate-counts.sh already prints the skill breakdown, so drift will surface on the next run.
- docs/commands/overview.md category counts (21 docs commands, 16 site commands, etc.) do NOT simply equal find commands/<subdir>/ counts — they appear to include docs/ mirror copies and may reflect a different counting convention. Before implementing, verify that overview.md counts match validate-counts.sh breakdowns. If they diverge, treat overview.md as Tier 3 (manual update only) and skip the automated sweep for that file.
- The 'Guard & Insights (2)' sub-category header in docs/skills-agents.md contains an ampersand. In BSD sed (macOS), ampersand in the REPLACEMENT string means 'insert matched text'. The pattern must use single-quote shell boundaries so the variable interpolation does not hit this: sed -i '' 's|^### Guard & Insights ([0-9][0-9]*)|### Guard \& Insights ('"$SKILL_GUARD_COUNT"')|'. Test this pattern explicitly before adding to the script.
- hub.md's category labels in the ASCII banner template are display strings that do NOT have to match actual find counts — the live hub command already runs Python discovery (Step 0 in hub.md) to render correct counts at runtime. The static template text with hardcoded numbers is what bumps-version.sh needs to update (to keep the docs/commands/hub.md site copy accurate). Do NOT change the runtime Python interpolation variables like {stats['total']}.

---

### 2-drift-tripwire — CI drift tripwire for count strings in README.md and docs/

**Effort:** 2h  ·  **Dependencies:** 7-bump-subtotals

**Approach:** Extend the existing `docs-staleness-check.sh` Phase 7 grep target to include `README.md` alongside the current `docs/ CLAUDE.md` scan, then add all historical count strings from README.md's embedded changelog section to `scripts/config/exclusions.txt`. This reuses the already-proven exclusion mechanism (file:pattern entries) to suppress legitimate historical numbers while failing CI on any live count string that drifts from discovery. Add a pytest in `tests/test_count_drift_tripwire.py` (marked `integration, docs`) that runs the real script against a temp tree with an intentionally stale README.md count and asserts exit code 1, proving the tripwire fires. No new script or utility is needed — the heavy lifting is already in docs-staleness-check.sh Phase 7.

**Files to create:**

- `/Users/dt/projects/dev-tools/craft/tests/test_count_drift_tripwire.py`

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/scripts/docs-staleness-check.sh`
- `/Users/dt/projects/dev-tools/craft/scripts/config/exclusions.txt`
- `/Users/dt/projects/dev-tools/craft/scripts/validate-counts.sh`

**Key steps:**

1. Step 1 — Audit README.md count strings. Using `grep -nE '[0-9]+ (commands|skills|agents)' README.md`, classify each match as LIVE (must match discovery) or HISTORICAL (changelog/version-history entries that should be excluded). Current LIVE lines: 14, 107, 153, 533, 534. Current HISTORICAL lines: 548 (16→12 commands), 573, 579 (3 commands), 588, 619, 628, 649, 661, 673, 687, 708, 718, 729, 735 (26 commands), 737 (3 skills).
2. Step 2 — Extend the Phase 7 grep target in `scripts/docs-staleness-check.sh`. At line 328, change the grep invocation from `grep -rnE "\b[0-9]+ ${ctype}\b" docs/ CLAUDE.md --include="*.md"` to also include `README.md`: `grep -rnE "\b[0-9]+ ${ctype}\b" docs/ CLAUDE.md README.md --include="*.md" 2>/dev/null`. Note: README.md is not inside docs/, so it must be added explicitly as a positional target. Confirm that `--include="*.md"` applies to all three targets (it does in grep — it filters by filename glob across all positional paths).
3. Step 3 — Add README.md exclusions to `scripts/config/exclusions.txt`. Add a new section after the existing 'Tutorial/example counts' block. Each historical count in README.md's changelog section becomes a `README.md:N TYPE` pattern entry. Required entries (based on the audit in Step 1): README.md:16 commands, README.md:12 commands, README.md:68 commands, README.md:17 skills, README.md:67 commands, README.md:63 commands, README.md:60 commands, README.md:61 commands, README.md:58 commands, README.md:54 commands, README.md:51 commands, README.md:12 skills, README.md:50 commands, README.md:11 skills, README.md:6 agents, README.md:46 commands, README.md:8 skills, README.md:1 agent, README.md:42 commands, README.md:26 commands, README.md:3 skills. Also add the orchestrator-mode prose entry: README.md:4 agents (line 270, 'fast parallel (4 agents)').
4. Step 4 — Verify the 40% threshold still handles edge cases. With the current live count of 110 commands, threshold = 44. This means historical counts of 46+ still need explicit exclusions (which Step 3 provides). Counts below 44 (e.g., '3 skills', '1 agent', '26 commands') fall below threshold naturally and need no exclusion. Double-check by running `./scripts/docs-staleness-check.sh` locally and confirming Phase 7 reports GREEN for README.md after the exclusion entries are added.
5. Step 5 — Add the tripwire pytest `tests/test_count_drift_tripwire.py`. The test uses the `_isolated_plugin()` isolation pattern from `test_docs_staleness.py` (copy the subset of the plugin tree into `tmp_path`, run the copied script). It has three test functions: (a) `test_phase7_catches_stale_readme_command_count` — patches README.md in the isolated tree to have a wrong command count (e.g., replaces '**110 commands**' with '**99 commands**') and asserts exit code 1 and that the finding mentions README.md; (b) `test_phase7_catches_stale_readme_skill_count` — same mutation for skills count; (c) `test_phase7_readme_historical_counts_are_excluded` — runs the script against the real unmodified tree (read-only, no isolation needed) and asserts that the README.md changelog lines do NOT appear in Phase 7 findings (exit 0 or no README.md entries in output).
6. Step 6 — Update `validate-counts.sh` to add a README.md spot-check as a secondary guard. After the existing plugin.json checks, add a bash block that greps README.md for `[0-9]+ commands` patterns above the 40% threshold and compares to CMD_COUNT. This is a simpler, faster tripwire that runs during local pre-flight (`/craft:check`) without requiring the full staleness script. Exit 1 if any live-region count mismatches.
7. Step 7 — Update `scripts/config/exclusions.txt` comment header to document the README.md section, noting that changelog counts in README.md are maintained here (not by bump-version.sh) and must be updated manually when the README changelog section is reorganized.
8. Step 8 — Run the full test suite locally to confirm no regressions: `python3 -m pytest tests/ -v --tb=short`. Then run `./scripts/docs-staleness-check.sh` and `./scripts/validate-counts.sh` to confirm both pass clean.

**Tests:**

- test_phase7_catches_stale_readme_command_count — isolate plugin tree, mutate README.md '**110 commands**' → '**99 commands**', run script, assert exit 1 and stdout contains 'README.md'
- test_phase7_catches_stale_readme_skill_count — isolate plugin tree, mutate '39 skills' → '29 skills', assert exit 1 and stdout mentions README.md
- test_phase7_readme_historical_counts_are_excluded — run script against real tree (read-only), assert Phase 7 finds zero README.md entries in output (exclusions suppress all historical numbers)
- test_validate_counts_catches_readme_drift — run validate-counts.sh on isolated tree with stale README.md count, assert exit 1

**Risks:**

- The --include='*.md' flag in grep applies to all positional targets, but README.md IS a .md file so it will be included — no risk. However, the file path prefix in grep output will be 'README.md:N:...' not 'docs/README.md:N:...' — the is_file_excluded() bash function must match on the raw grep output path. Verify that the pattern exclusion lookup in is_pattern_excluded() uses the path as-is from grep output (it does — the file variable is set from `${match%%:*}`).
- Historical counts in README.md will drift as the embedded changelog grows. Each new release adds a 'Total: N commands, M skills, K agents' line to README.md that needs a new exclusion entry. This is the same O(1)-per-release cost as adding a CHANGELOG exclusion. Document this in the exclusions.txt section header so release engineers know to add it.
- The 40% threshold in Phase 7 (line 314 of docs-staleness-check.sh) uses the current live count dynamically. If the real count ever drops dramatically (e.g., a major restructure removes many commands), previously-safe historical counts could cross the new threshold. The per-entry exclusions in exclusions.txt protect against this, but a threshold change could cause old exclusion entries to become unnecessary (harmless) or previously-unneeded entries to suddenly be needed.
- CI on Ubuntu runs docs-staleness-check.sh as part of `pytest tests/` (via test_docs_staleness.py). Adding README.md to the grep target increases the staleness check's runtime slightly, but README.md is a single file so the impact is negligible.
- Dependency on item 7-bump-subtotals: if bump-version.sh is extended (item 7) to auto-update README.md count strings, the live-count lines may change format. The Phase 7 regex pattern `\b[0-9]+ TYPE\b` is robust to bold markers (`**110 commands**` still matches because `\b` treats `*` as a word boundary), so format changes are low risk.

---

### 5-ci-triage — New command /craft:ci:triage — classify failing CI checks as diff-caused vs pre-existing/infra and recommend action with evidence

**Effort:** 2h  ·  **Dependencies:** none

**Approach:** Create `/Users/dt/projects/dev-tools/craft/commands/ci/triage.md` — a single new command file following the exact frontmatter + numbered-step prose pattern established in `commands/ci/status.md` and `commands/ci/validate.md`. The command fetches the failing run log via `gh run view --log-failed` on the active PR's head SHA, diffs the log's failure sites against `git diff origin/dev...HEAD --name-only` to classify ownership, then emits a verdict box (DIFF-CAUSED / PRE-EXISTING / INFRA-FLAKE) with an explicit recommendation of re-run, fix, or `--admin`. No new Python utility is needed — the classification logic is implemented as inline Python (matching the parser pattern from `commands/ci/status.md` Step 2) and inline bash (matching `commands/git/status.md`). The CLAUDE.md count and `plugin.json` description must be bumped from 110 to 111 commands as part of the feature branch PR.

**Files to create:**

- `/Users/dt/projects/dev-tools/craft/commands/ci/triage.md`

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/.claude-plugin/plugin.json`
- `/Users/dt/projects/dev-tools/craft/CLAUDE.md`
- `/Users/dt/projects/dev-tools/craft/commands/ci/status.md`
- `/Users/dt/projects/dev-tools/craft/commands/code/ci-fix.md`
- `/Users/dt/projects/dev-tools/craft/tests/test_plugin_e2e.py`

**Key steps:**

1. Phase 0 — branch setup: `git worktree add ~/.git-worktrees/craft/feature-ci-triage -b feature/ci-triage dev` (never write code on dev; branch guard enforces this)
2. Phase 1 — write `commands/ci/triage.md` frontmatter: category=ci, three arguments: `pr` (PR number or URL, optional, defaults to current branch's open PR), `repo` (optional, defaults to Data-Wise/craft), `json` (flag, default false). Description: 'Triage a failing CI check: classify as diff-caused vs pre-existing/infra and recommend re-run / --admin / fix with evidence'
3. Phase 2 — implement Step 1 (Identify failing checks): `gh pr checks <PR> --repo <REPO> --json name,state,link` piped through inline python3 to extract only state==FAILURE or state==PENDING entries. Surface run-id from the link field via regex `runs/([0-9]+)`. Emit a list of failing check names + run IDs.
4. Phase 3 — implement Step 2 (Fetch failure log): for each failing run-id: `gh run view <run-id> --repo <REPO> --log-failed 2>&1 | head -200`. Store the log lines. Note: `gh run view --log-failed` exits non-zero if the run is still pending — handle with `|| true`. Also handle exit-code 8 from `gh pr checks` per the documented memory pattern (never use `&&` chain; always capture output separately).
5. Phase 4 — implement Step 3 (Get PR diff file list): `git diff origin/dev...HEAD --name-only 2>/dev/null || gh pr diff <PR> --repo <REPO> --name-only`. This gives the set of files touched by the PR. Store as a Python set.
6. Phase 5 — implement Step 4 (Classification logic as inline Python): parse each log line for a file path pattern `([^\s:]+\.(py|sh|yml|yaml|rb|md|js|ts)):(\d+)`. For each matched filepath, check if it is in the PR diff set. Classification rules:

- If ALL error-site files are in the PR diff → class='DIFF-CAUSED'
- If NO error-site files are in the PR diff → class='PRE-EXISTING' (or 'INFRA-FLAKE' if log contains 'runner', 'npm ERR', 'rate limit', 'timeout', 'HTTP 403', 'HTTP 429', 'connection refused')
- If MIXED → class='PARTIAL' (some diff, some pre-existing)
  Confidence is HIGH when >=1 file path matched; LOW when log has no parseable file references (pure infra error).

7. Phase 6 — implement Step 5 (Render verdict box): use box-drawing characters consistent with `commands/ci/status.md`. Show: check name, class badge (DIFF-CAUSED / PRE-EXISTING / INFRA-FLAKE / PARTIAL), confidence, evidence (up to 3 matched file:line pairs), and recommendation line:

- DIFF-CAUSED → 'Fix the failure in your code, then re-push'
- PRE-EXISTING → '--admin merge is justified; confirm unrelated to diff before proceeding'
- INFRA-FLAKE → 'Re-run failed jobs: gh run rerun <run-id> --failed --repo <REPO>'
- PARTIAL → 'Mixed: fix the diff-owned failures, then re-evaluate the pre-existing ones'

8. Phase 7 — implement Step 6 (JSON output mode): when `--json` flag is set, skip box rendering and output structured JSON: `{checks: [{name, state, run_id, class, confidence, evidence_files, recommendation}], summary: {diff_caused: N, pre_existing: N, infra_flake: N, partial: N}}`
9. Phase 8 — add 'See Also' cross-links at bottom: `/craft:ci:status` (broader dashboard), `/craft:code:ci-fix` (apply fix once cause is known), `/craft:git:unprotect` (needed before --admin on main). Add `/craft:ci:triage` to the 'See Also' of `commands/ci/status.md` (line ~164) and `commands/code/ci-fix.md` (line ~93).
10. Phase 9 — count bump: update `plugin.json` description from '110 commands' to '111 commands'; update `CLAUDE.md` header from '110 commands' to '111 commands'. Run `./scripts/validate-counts.sh` to verify.
11. Phase 10 — add tests (see tests section below), run full suite `python3 -m pytest tests/ -v`, verify 0 regressions before PR.

**Tests:**

- test_plugin_e2e.py — TestCommandFrontmatter already picks up every command in commands/**/*.md via `_find_all_commands()`; adding triage.md means the new file is automatically covered by `test_all_commands_have_frontmatter` and `test_all_commands_have_description`. No new test class needed for structural validity.
- tests/test_ci_triage_unit.py (new file) — class TestClassificationLogic: unit-tests the inline Python classification logic extracted into a helper function `classify_failure(log_lines: list[str], diff_files: set[str]) -> dict`. Test cases: (a) log references file in diff → DIFF-CAUSED; (b) log references file not in diff → PRE-EXISTING; (c) log contains 'rate limit' with no file refs → INFRA-FLAKE; (d) log references both diff-file and non-diff-file → PARTIAL; (e) empty log lines → INFRA-FLAKE with LOW confidence; (f) log references `.github/workflows/ci.yml` (always in repo but rarely in PR diff) → PRE-EXISTING.
- tests/test_ci_triage_unit.py — class TestVerdictFormatting: verify the box renderer produces the four expected class badges (DIFF-CAUSED, PRE-EXISTING, INFRA-FLAKE, PARTIAL) and includes the recommendation string. Use string-contains assertions against the rendered output (no subprocess needed — test the inline Python block directly).
- tests/test_plugin_dogfood.py — TestValidateCounts.test_validate_counts_exits_zero already runs `validate-counts.sh`; after the count bump in plugin.json it will catch any discrepancy if counts.sh still returns the old value. No new dogfood test needed.
- tests/test_plugin_e2e.py — add one targeted assertion in TestCommandFrontmatter: verify that `commands/ci/triage.md` specifically exists (guards against accidental rename/delete during future refactors), using `COMMANDS_DIR / 'ci' / 'triage.md'`.

**Risks:**

- gh CLI log parsing brittleness: `gh run view --log-failed` output format is not a stable API — log lines include ANSI codes and GitHub-specific annotations. The inline Python must strip ANSI before regex-matching file paths, and must degrade gracefully (LOW confidence) when parsing yields nothing.
- No open PR on current branch: the command's default mode assumes an open PR exists for the current branch. If invoked outside a PR context (e.g., directly on dev post-merge), `gh pr checks` returns an error. The implementation must detect this and surface a clear message: 'No open PR found for branch <branch>; pass --pr <number> explicitly'.
- INFRA-FLAKE vs PRE-EXISTING ambiguity for 'Validate Plugin Structure' stuck-pending: the memory note says this check gets stuck at pending (not failure). `gh pr checks --json state` returns 'PENDING' not 'FAILURE' for stuck checks — the command must handle PENDING separately and label it INFRA-STUCK with recommendation to `--admin` after >3 min, not a false DIFF-CAUSED.
- Count drift: adding triage.md increments the command count to 111. `validate-counts.sh` counts `find commands -name '*.md' ! -name index.md ! -name README.md'` — triage.md will be picked up automatically. Only plugin.json description and CLAUDE.md header need manual update. Must run validate-counts.sh on the feature branch before PR.

---

### 6-ci-watch — /craft:ci:watch — Background CI Poller with Completion Notification and Next-Action Routing

**Effort:** 1.5h  ·  **Dependencies:** 5-ci-triage

**Approach:** Add a new command `commands/ci/watch.md` in the existing `ci` category alongside `status.md`, `detect.md`, `generate.md`, and `validate.md`. The command accepts a PR number, SHA, or run ID as its single positional argument and wraps the `gh run watch` / `gh run view --poll` pattern with background-mode awareness. On completion, it classifies the result as green (suggest merge or release next step) or red (surface the triage recommendation from item #5 ci:triage, or inline a condensed triage if that command does not yet exist). The command is a pure `.md` instruction file — no new Python script or shell utility is required, mirroring the thin-command pattern of `ci/status.md` and `code/desktop-watch.md`. A companion published doc `docs/commands/ci/watch.md` mirrors the pattern established by `docs/commands/ci/status.md`. Two mkdocs.yml nav entries and one REFCARD table row complete the doc surface.

**Files to create:**

- `/Users/dt/projects/dev-tools/craft/commands/ci/watch.md`
- `/Users/dt/projects/dev-tools/craft/docs/commands/ci/watch.md`

**Files to edit:**

- `/Users/dt/projects/dev-tools/craft/mkdocs.yml`
- `/Users/dt/projects/dev-tools/craft/docs/REFCARD.md`
- `/Users/dt/projects/dev-tools/craft/docs/skills-agents.md`
- `/Users/dt/projects/dev-tools/craft/.claude-plugin/plugin.json`
- `/Users/dt/projects/dev-tools/craft/CLAUDE.md`
- `/Users/dt/projects/dev-tools/craft/CHANGELOG.md`
- `/Users/dt/projects/dev-tools/craft/docs/CHANGELOG.md`

**Key steps:**

1. Step 1 — Author `commands/ci/watch.md`: Write the command file with YAML frontmatter (description, category: ci, one required argument `target` accepting PR#/SHA/run-id, optional flags --repo, --timeout, --bg, --json). The body defines four execution phases: (1) Resolve the target — distinguish `#NNN` (PR) from a bare SHA from a numeric run-id, then call `gh run list --branch <ref>` or `gh run view <run-id>` to get the canonical run-id and workflow name. (2) Poll loop — use `gh run view <run-id> --json status --jq .status` (NOT `gh pr checks` — that exits 8 on in-progress; see memory note gh-pr-checks-exit-code-8-means-pending-or-failing) in a 15-second poll loop until status == 'completed'. Print a live progress line showing elapsed time and current step count. (3) Classify outcome — call `gh run view <run-id> --json conclusion --jq .conclusion`; 'success' → green path, anything else → red path. (4) Output the completion box and next-action recommendation.
2. Step 2 — Green path output: Display a box-drawing completion block (matching ci/status.md style with box chars `+---+`) showing workflow name, branch, duration, conclusion. Then print the suggested next step: if the target was a PR number and the branch is a feature branch, suggest `gh pr merge --squash`; if main-bound, suggest `/craft:ci:status --post-release`; if on dev, suggest nothing (show it's integration-only).
3. Step 3 — Red path output: Display the same completion block but with failure markers. List all failed job names and their first non-green step via `gh run view <run-id> --log-failed | head -60`. Then classify the failure as (a) 'in my diff' (job name or step matches files changed in the PR), (b) 'pre-existing/infra' (job is in a skip-list like 'Validate Plugin Structure'), or (c) 'unknown'. For each class, recommend: (a) fix → `/craft:code:ci-fix`, (b) --admin merge (show criteria), (c) `/craft:ci:triage` (forward to item #5 when it exists). This is the overlap boundary with #5: watch does lightweight inline triage for the two clear-cut cases; triage does the deep analysis.
4. Step 4 — Implement `--bg` flag (background mode): When `--bg` is passed, the command instructs the user to run the generated shell snippet in a background terminal rather than polling interactively. The snippet is: `until gh run view <run-id> --json status --jq .status | grep -q completed; do sleep 15; done && gh run view <run-id> --json conclusion --jq .conclusion`. This matches the pattern the BRAINSTORM describes ('background-poll-then-notify'). The command itself then exits immediately with the snippet printed.
5. Step 5 — Implement PR-number → run-id resolution: When given `#NNN`, run `gh pr view NNN --json headRefOid,headRefName` to get the SHA and branch, then `gh run list --branch <branch> --limit 5 --json databaseId,name,status --jq 'map(select(.status != "completed")) | first | .databaseId'` to find the most recent in-progress run. If multiple runs exist (push + PR trigger), prefer the one whose workflow name matches a heuristic priority list (CI > all others). Document the resolution logic explicitly so it is deterministic.
6. Step 6 — Write `docs/commands/ci/watch.md`: Mirror the structure of `docs/commands/ci/status.md` — Synopsis section with `bash` examples, 'What It Does' narrative, Output section showing both green and red completion boxes, Arguments table, 'When to Use' table (pre-merge confirmation / release gate / CI debugging / background monitoring), Error Handling table, Prerequisites note (gh CLI + auth), and See Also links to `/craft:ci:status`, `/craft:ci:triage`, `/craft:code:ci-fix`.
7. Step 7 — Update `mkdocs.yml`: Add `/craft:ci:watch: commands/ci/watch.md` in the Help & Examples nav block (at line ~228, after the existing `/craft:ci:status` entry). Also add `- /craft:ci:watch: commands/ci/watch.md` to the docs site nav wherever ci commands are grouped. Both entries must be present (source command doc + published command doc).
8. Step 8 — Update `docs/REFCARD.md`: In the CI Commands table (around line 1089–1104), add one new row: `| /craft:ci:watch <pr|sha> | Poll run to completion; suggest merge or triage |`. Update the section header count from 4 to 5 commands.
9. Step 9 — Update `docs/skills-agents.md` CI section header: Change `### CI (1)` to `### CI (1)` — no new skill is added, so the skill count stays. But the command catalog text near the CI section (the quick-examples block around line 1096–1104) should add the new command example.
10. Step 10 — Update `plugin.json` description string: Increment the total command count (currently 110) to 111 (one new command). Verify with `./scripts/validate-counts.sh` which checks `find commands -name '*.md'` count against the description string.
11. Step 11 — Update `CLAUDE.md`: Increment the 'Current Version' command count in the CLAUDE.md header line (currently '109 commands'). Also add `/craft:ci:watch` to the Quick Commands table if the table lists ci commands.
12. Step 12 — Add to `[Unreleased]` section of `CHANGELOG.md` and `docs/CHANGELOG.md`: `- Added /craft:ci:watch: poll CI run to completion with merge/triage next-action routing.`
13. Step 13 — Write tests in `tests/test_plugin_e2e.py` or a new `tests/test_ci_watch.py`: (a) assert `commands/ci/watch.md` exists and has valid frontmatter with required `target` argument; (b) assert frontmatter `category == 'ci'`; (c) assert the command body references `gh run view` (not `gh pr checks`) for polling, confirming the safe-polling pattern; (d) assert the green and red output blocks both appear in the file; (e) assert the `--bg` flag is described. These are structural/content assertions, consistent with how `test_craft_plugin.py` validates commands without executing them.

**Tests:**

- Structural: commands/ci/watch.md exists, has YAML frontmatter with description + category: ci + required target argument
- Structural: frontmatter does NOT contain 'gh pr checks' in polling logic (guards against the exit-8 anti-pattern documented in memory)
- Structural: command body contains 'gh run view' and '--json status' (confirms safe completion-polling pattern)
- Structural: command body contains both a green-path output block and a red-path output block
- Structural: command body describes the --bg flag with a shell snippet
- Count: validate-counts.sh exits 0 after adding the file (command count in plugin.json description matches find commands -name '*.md' count)
- Nav: mkdocs.yml contains exactly one entry for 'ci/watch.md' (no duplicate, no orphan)
- Nav: docs/commands/ci/watch.md exists (published doc pair is present)
- Integration: pre-release-check.sh passes with the new version string after a bump

**Risks:**

- PR-to-run-id resolution is inherently racy: multiple workflows run on the same push (e.g., CI + docs + validate-deps). The command must clearly document which run it latches onto (heuristic: first non-completed run matching a priority workflow list). If the wrong run is selected, the completion notification is misleading. Mitigation: show the resolved workflow name in the header so the user can see what they're watching.
- Overlap boundary with #5 ci:triage is fuzzy: this command does inline triage for the two clear-cut cases (in-diff failure → fix; Validate Plugin Structure → admin-merge), but the 'unknown' case just forwards to /craft:ci:triage. If #5 is not yet implemented when this ships, the red-path 'unknown' recommendation is a dead forward reference. Mitigation: make the forward reference conditional — 'if you have ci:triage, run it; otherwise see ci:status for run details' — and note in the See Also that triage is a planned companion.
- The --bg flag outputs a shell snippet the user must copy-paste; there is no native 'background task' API in Claude Code commands. This is intentional (matching the craft pattern of instructing rather than executing), but the UX is weaker than a true notification. Mitigate by making the snippet self-contained and immediately copy-paste-able with the resolved run-id substituted in.
- Command count drift: adding one .md file bumps the count that validate-counts.sh checks against plugin.json. If the implementor forgets to update plugin.json description, validate-counts.sh will fail in CI. The test step (count test) is designed to catch this before PR, but it's a recurring source of friction in craft — this is Tier 1 drift class.

---

## Source

- Brainstorm: `BRAINSTORM-craft-improvements-2026-06-13.md`
- Long-term items (#8 engine v2, #9 self-healing release, #10 drift-budget dashboard) and the
  headline (`WORKFLOW-release.yaml` — dogfood the engine on releases) are **out of scope for this spec**;
  track separately.
