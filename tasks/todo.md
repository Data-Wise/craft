# TODO: Issue #316 — Plugin Skill Identity Hardening

Source:
[`SPEC-plugin-skill-command-identity-hardening-2026-07-27.md`](../docs/specs/SPEC-plugin-skill-command-identity-hardening-2026-07-27.md)

## Slice 1 — Structural Regression Tests

- [x] Add pure skill/command identity inventory helpers to `tests/test_craft_plugin.py`.
  - Acceptance: commands are discovered recursively; skills expose directory and frontmatter
    identity surfaces.
  - Verify: fixture catches nested and frontmatter-only collisions.
- [x] Add exact mismatch and collision debt ledgers with ownership metadata.
  - Acceptance: new debt and stale debt both fail.
  - Verify: fixture tests cover unlisted, moved/duplicated, and stale entries.
- [x] Snapshot `/craft:check`'s public argument contract and normalized whole-file hash.
  - Acceptance: only the canonical replacement path may change.
  - Verify: focused test is red before the move and green after it.

## Slice 2 — Preflight Skill Move

- [x] Move the validator to canonical `skills/preflight-check/`.
  - Acceptance: the skill and `references/gen-validator.md` move together.
- [x] Update runtime, script, test, and live-documentation references.
  - Acceptance: no old runtime/live-doc references remain outside explicit evidence/test
    exclusions.
- [x] Preserve `/craft:check` arguments and representative behavior.
  - Verify: default, thorough, PR, dry-run, and context paths remain valid.

## Slice 3 — Documentation and State

- [x] Add mirrored root/docs changelog entries.
- [x] Update `.STATUS` with #316 implementation state and worktree.
- [x] Pin local and GitHub Actions test runtimes to stable Python 3.14.
- [x] Re-run count, docs-staleness, link, and strict site-build checks.

## Slice 4 — Full Validation and Manual QA

- [x] Run focused structural tests.
- [x] Run the full test suite.
- [x] Validate the plugin and counts.
- [x] Stage the committed artifact in disposable Claude Code and Codex environments.
- [x] Record client versions, resolved paths, commit SHA, and archive hashes.
- [x] Probe `preflight-check`, `brainstorm`, `grill`, and `release` identity behavior.
- [x] Reconcile debt-ledger decisions.
