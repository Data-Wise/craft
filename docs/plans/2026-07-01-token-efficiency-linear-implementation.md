# Linear Implementation Plan — Token-Efficiency Follow-on Work

**Spec:** [`docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md`](../specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md)
**Date:** 2026-07-01
**Execution model:** LINEAR / in-line — single session, sequential steps, **no subagent dispatch** (deliberate: this whole work stream is about token frugality; multi-agent orchestration would undercut the point). Each step is self-contained and verifiable before the next begins.

> **No `superpowers:subagent-driven-development` here** — that sub-skill is for parallel/isolated task execution. This plan is intentionally the opposite: one operator, one thread, in order.

---

## Execution order at a glance

| # | Step | Where | Branch policy | Gated on | Status |
|---|---|---|---|---|---|
| 1 | Generalize `scripts/token-probe.py` (Task 2) | craft repo | **new file → feature branch** | `tiktoken` install | 🔧 **worktree ready** — `feature/token-probe-script` @ `~/.git-worktrees/craft/feature-token-probe-script`; `tiktoken` installed 2026-07-01; not yet implemented, needs its own session |
| 2 | Deprecated-command audit batch (Part D #1, issue #233) | craft repo | **feature branch** (large refactor) | Step 1 optional | ⚠️ needs branch — not yet created |
| 3 | Hooks token-cost audit (Part D #2) | craft repo | measurement → `.md` findings, OK on `dev` | — | ✅ **DONE 2026-07-01** — [HOOKS-TOKEN-AUDIT-2026-07-01.md](../internal/HOOKS-TOKEN-AUDIT-2026-07-01.md). Finding: craft's hooks cost 0 tokens/turn on the happy path; real per-turn cost is an external, non-craft `prompt-optimizer.sh` (flagged, out of repo scope) |
| 4 | Automated plugin-audit skill (Part D #3) | craft repo | **feature branch** (new skill) | — | ⚠️ needs branch — not yet created |
| — | Task 1 (external docx) | NOT in repo | n/a | file location | ✅ **DONE 2026-07-01** — found at `~/Downloads/`, corrected via `docx` skill (tracked changes, author Claude), scoped the C1 Superpowers verdict in both §3.3 body and §4 summary table. Output: `~/Downloads/Token-Efficiency-Report-and-Proposal-corrected.docx` |
| — | Task 3 (claude-context pilot) | craft repo | feature branch | **MCP install** + Step 1 done first | ❌ blocked — MCP not installed; also now formally task-graph-blocked on Step 1 (needs `token-probe.py` for its measurement step) |
| — | `/usage` checkpoint | n/a | n/a | ~2026-07-14 date | ⏳ scheduled |

**Branch-guard note:** creating a *new* code file (`scripts/token-probe.py`, a new `skills/**/SKILL.md`) is BLOCKED on `dev` by the branch guard. Steps 2, 4 still need a `feature/*` worktree — not yet created (one-worktree-per-session rule; create when opening each session). Step 1's worktree already exists (see table). Step 3 is done.

**Session task tracker (ephemeral, this session only):** #1 hooks audit (completed) · #2 token-probe.py (pending, worktree ready) · #3 deprecated-cmd audit (pending) · #4 plugin-audit skill (pending) · #5 claude-context pilot (pending, blocked by #2) · #6 `/usage` checkpoint (pending, date-gated). Not persisted outside the session — this table + `.STATUS` are the durable record.

---

## Step 1 — `scripts/token-probe.py` (Task 2)

**Goal:** a reusable `--before <glob> / --after <glob>` token-count comparator, generalized from the disposable namespace probe.

**Prereqs (in order):**

1. `uv tool install tiktoken` **or** `python3 -m pip install tiktoken` — confirmed NOT installed as of 2026-07-01 (`import tiktoken` → ModuleNotFoundError). Needed for Step 1.5's sanity check only; the script can be *written* without it.
2. Feature branch: `feature/token-probe-script` (new file → guard blocks it on `dev`).

**Sub-steps:**

1. Read `docs/plans/2026-06-30-namespace-token-probe.md` in full — recover its comparison logic (synthetic before/after fixture generation, `tiktoken` cl100k_base counting, printed diff).
2. Write `scripts/token-probe.py`:
   - CLI: `--before <glob>`, `--after <glob>`, optional `--encoding` (default `cl100k_base`).
   - Sum token counts across each glob's files; print before, after, delta, and percent.
   - Module docstring MUST carry the caveat: cl100k_base ≠ Claude's real tokenizer — this is a *relative* comparison tool, not an exact Claude token count.
   - Follow the arg-parsing idiom of `scripts/audit-deprecated-commands.py` (sibling script, same dir).
3. `--help` usage example in the docstring/argparse epilog.
4. **Index it:** `audit-deprecated-commands.py` is currently NOT listed in `docs/REFCARD.md` or `docs/reference/*` (verified 2026-07-01) — so there is no existing pattern row to mirror. Add a short entry for BOTH scripts under whatever "scripts" surface exists, or skip indexing and note it — don't invent a table that isn't there.
5. **Sanity check:** run against a real before/after pair and confirm it approximately reproduces the original **68.3%** namespace-refactor figure.

**Done when:** `python3 scripts/token-probe.py --before <glob> --after <glob>` runs standalone, no hardcoded fixtures, and the sanity check lands near 68.3%.

**Verify:** `python3 -m pytest tests/ -q` stays green (new script shouldn't touch existing tests; add a smoke test if a `tests/test_scripts_*.py` convention exists).

---

## Step 2 — Deprecated-command audit batch (Part D #1 / issue #233)

**Goal:** shrink the worst body-to-skill-ratio offenders using Part A's methodology (extract → skill, don't delete; full-suite verify before merge).

**Prereqs:**

1. Feature branch: `feature/deprecated-cmd-audit-batch1`.
2. Re-run the audit to get the current live list (numbers drift): `python3 scripts/audit-deprecated-commands.py --threshold 2.0`.

**Targets (worst first, per the 2026-06-30 audit):**

- `commands/check.md` — 8.9:1 (1132 lines vs. a 127-line skill). Single worst ratio in the repo.
- The 6 commands whose `replaced-by:` is `skills/dev/git/` (250 lines): `worktree.md` (1010), `init.md` (597), `sync.md` (539), plus the three `docs/*.md` git references (`safety-rails` 723, `learning-guide` 722, `undo-guide` 594) — 4185 combined source lines.

**Per-target loop (do ONE target fully before starting the next):**

1. Confirm the `replaced-by:` skill already contains the behavior, or extend the skill to absorb what the command body uniquely holds (extract, don't delete).
2. Reduce the command `.md` to a thin shim (deprecated frontmatter + pointer), matching the ADR-002 pattern already used by other deprecated commands.
3. Run the FULL suite — `python3 -m pytest tests/` — NOT a sampled subset (Part A's single most important lesson: extraction regressions are missing-string / cross-file-consistency / trigger-collision failures that scoped tests miss).
4. Fix any regression before moving to the next target.

**Done when:** each targeted command is a thin shim, its skill carries the moved behavior, and the full suite is green after each.

**Note:** this is the heaviest step — reasonable to make it its own session/PR. It does NOT block Steps 3 or 4.

---

## Step 3 — Hooks token-cost audit (Part D #2)

**Goal:** measure per-turn token cost of craft's always-running hooks — a lever Part A flagged but never measured.

**No new code file → produces `.md` findings → allowed directly on `dev`.**

**Sub-steps:**

1. Inventory the always-on hooks: `branch-guard.sh`, `no-switch-guard`, `session-facet.sh` (and any others in `~/.claude/settings.json` hooks + `hooks/`).
2. For each, measure the context/output it injects per invocation (a hook that prints to stdout on every PreToolUse/SessionStart adds tokens every turn). Use `scripts/token-probe.py` (Step 1) on representative hook output if built; else `wc`-based estimate + note the imprecision.
3. Write findings to `docs/internal/HOOKS-TOKEN-AUDIT-2026-07-01.md` (or an addendum to `docs/internal/TOKEN-EFFICIENCY-craft.md`) — which hooks are cheap, which are candidates for quieter output, which must stay verbose (safety-critical branch-guard messaging).

**Done when:** every always-on hook has a measured (or explicitly-estimated) per-turn cost and a keep/trim recommendation.

---

## Step 4 — Automated plugin-audit skill (Part D #3)

**Goal:** a skill that catches installed-plugin duplicates/collisions automatically (the 2026-06-29 manual sweep missed `workflow@local-plugins`).

**Prereqs:** feature branch `feature/plugin-audit-skill` (new `SKILL.md` → guard blocks on `dev`).

**Sub-steps:**

1. Scaffold `skills/code/plugin-audit/SKILL.md` using an existing craft skill's frontmatter/structure as the template.
2. Logic: diff `~/.claude/settings.json` `enabledPlugins` + `installed_plugins.json` against each plugin's actual command/skill surface; flag name collisions across namespaces (e.g. a bare `workflow:brainstorm` vs. `craft:workflow:brainstorm`).
3. Trigger phrases: "audit my plugins", "check for plugin duplicates", "plugin collision check" — verify no trigger-phrase collision with existing skills (`test_skill_trigger_phrases_unique` — Part A regression #1).
4. Full-suite verify.

**Done when:** the skill exists, detects the `workflow`-vs-`craft:workflow` class of collision on a synthetic fixture, and the suite is green.

---

## Excluded / deferred (do not attempt in the linear pass)

- **Task 3 (claude-context pilot):** blocked until the `claude-context` MCP server is installed and connected (`claude mcp add …`, then verify) — and now also blocked on Step 1 completing first.
- **`/usage` checkpoint (~2026-07-14):** date-gated validation of the 48% hypothesis; commands ready in Part C item 1; record result in `_archive/SPEC-token-efficiency-research-2026-06-30.md` §9.
- **Part D #4 (context-mode output routing):** research-only note, unscheduled — doesn't map onto craft's measured cost driver.

## Documentation & Discoverability (for any step that ships a new surface)

Each of Steps 1/2/4 ships a script or skill — before calling it done, mirror the standard craft surface (tailor to what it touches; mark N/A explicitly):

- [ ] CHANGELOG `[Unreleased]` entry
- [ ] Count bumps (Step 4 adds a skill → `validate-counts.sh` + `bump-version.sh --verify` + `docs-staleness-check.sh` clean)
- [ ] `skills-agents.md` catalog row (Step 4)
- [ ] Scripts index / REFCARD entry (Steps 1) — or a note that no such index exists yet
- [ ] `mkdocs build --strict` clean if any doc/nav touched
