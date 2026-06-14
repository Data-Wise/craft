# Fix: command-audit.sh strips `deprecated`/`replaced-by` frontmatter — Spec

**Generated:** 2026-06-13
**Status:** done — SHIPPED in v2.36.0 (PR #147 → dev `1215e802`, 2026-06-13)
**Severity:** Latent data-loss bug (silently un-deprecates 56 commands in the working tree)
**Branch target:** `fix/command-audit-deprecated-fields` (worktree off `dev`)
**Origin:** Multi-agent hunt 2026-06-13 (15 agents) + manual code verification. Closes `.STATUS` Next-Action item A.

---

## Problem

Running `pytest tests/` (locally or in CI) silently removes the `deprecated: true` and
`replaced-by: "..."` YAML frontmatter lines from all **56 deprecated command files** in the
working tree, while preserving `description`/`category`. CI stays green and counts are
unaffected, so nothing flags it — only a manual `git status` catches the dirty tree.

## Root cause (VERIFIED against live code)

Two independent defects combine:

1. **Allowlist omission** — `scripts/command-audit.sh:20-24` defines `VALID_FIELDS` which lists
   `description`/`category` but **omits `deprecated` and `replaced-by`**. In `--fix` mode,
   `check_invalid_fields()` (`scripts/command-audit.sh:150-232`) treats any key not in the
   allowlist as "invalid" and runs the Python at lines 193-219, which rebuilds the frontmatter
   line-by-line — skipping the offending key and its indented continuations while keeping all
   known keys. This is the exact observed signature.

2. **Test mutates the real source tree** — `tests/test_command_audit.py::test_audit_fix_mode_dry`
   (lines 82-93) calls `_run_audit("--format", "json", "--fix")`, and `_run_audit` runs the
   script with `cwd=PLUGIN_DIR` (the real repo; lines 11, 16-24). The test's own comment admits
   "`--fix` may modify files." So the test itself triggers defect #1 against the real files.

**Why CI-invisible:** in CI the mutation lands in an ephemeral checkout that's never committed
(CI passes); locally it dirties the developer's working tree.

## Fix (both parts required)

### Part 1 — `scripts/command-audit.sh` (whitelist the legitimate fields)

```diff
 VALID_FIELDS=(
     name category subcategory description file modes arguments flags
     tutorial tutorial_level tutorial_file related_commands tags
-    project_types common_workflows time_budgets examples
+    project_types common_workflows time_budgets examples
+    deprecated replaced-by
 )
```

`deprecated`/`replaced-by` are first-class frontmatter keys (used by 56 commands + asserted by
`test_deprecated_commands_have_replacement`). They must never be treated as "invalid".

### Part 2 — `tests/test_command_audit.py` (never run `--fix` against the real tree)

`test_audit_fix_mode_dry` must run `--fix` against a **disposable copy**, not `PLUGIN_DIR`.
Copy a small fixture (or the real `commands/` subset) into `tmp_path`, run the audit there, and
assert the real tree is untouched. Sketch:

```python
def test_audit_fix_mode_does_not_mutate_source(self, tmp_path):
    # Stage a deprecated command in an isolated tree, run --fix there.
    cmd_dir = tmp_path / "commands" / "workflow"
    cmd_dir.mkdir(parents=True)
    sample = cmd_dir / "task-status.md"
    sample.write_text(
        '---\ndescription: x\ncategory: workflow\n'
        'deprecated: true\nreplaced-by: "skills/workflow/task-management/"\n---\n# x\n'
    )
    subprocess.run(["bash", SCRIPT, "--fix"], cwd=tmp_path, timeout=60,
                   capture_output=True, text=True)
    # Regression guard: --fix must NOT strip deprecated/replaced-by
    assert "deprecated: true" in sample.read_text()
    assert "replaced-by:" in sample.read_text()
```

The existing `test_audit_fix_mode_dry` (which runs against `PLUGIN_DIR`) should be retargeted to
`tmp_path` too, so no test ever writes to the source tree.

## TDD order

1. **RED:** add `test_audit_fix_mode_does_not_mutate_source` — fails today (keys stripped).
2. **GREEN (part 1):** add the two fields to `VALID_FIELDS` → regression test passes.
3. **Harden (part 2):** retarget `test_audit_fix_mode_dry` to `tmp_path` so no test mutates source.
4. Run the **full** `pytest tests/` (CI runs ~1700; a subset misses failures) and confirm
   `git status` is clean afterward.

## Acceptance

- [ ] `pytest tests/test_command_audit.py` green; **full `pytest tests/` green**.
- [ ] After a full test run, `git status` shows NO modified command files.
- [ ] `bash scripts/command-audit.sh --fix` on a deprecated command preserves both keys.
- [ ] Drop the stale `stash@{0}` once the fix lands (drift no longer reproducible).

## Documentation & Discoverability

_(Per the spec-creation mandate added 2026-06-13. Bug fix — most surface N/A.)_

- [ ] CHANGELOG `[Unreleased]` under a `### Fixed` header, in **BOTH** `CHANGELOG.md` and `docs/CHANGELOG.md` (they must mirror). Ready-to-paste bullet:
  > `command-audit.sh --fix` no longer strips `deprecated`/`replaced-by` frontmatter — added both to `VALID_FIELDS`, and `test_audit_fix_mode_dry` now runs against a temp tree instead of the real plugin dir, so `pytest tests/` can no longer silently un-deprecate the 56 deprecated commands.
- [ ] Tutorial / help / command pages / REFCARD / hub / website — **N/A** (internal script fix, no user-facing command change).
- [ ] Counts — **N/A** (no command/skill added).

## Residual note

The third agent verdict flagged `commands/_discovery.py` as a culprit; two other verdicts
cleared it with sound reasoning — its `discover_commands()` filter is lossy but **only reads &
caches, never writes back to `.md` files**. Not in scope. If a future tool ever rebuilds command
frontmatter from `discover_commands()` output, revisit it then.
