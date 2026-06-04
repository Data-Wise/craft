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
