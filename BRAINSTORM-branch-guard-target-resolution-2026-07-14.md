# BRAINSTORM: Branch-Guard Target-Resolution False Positives

**Date:** 2026-07-14 · **Depth:** default · **Focus:** architecture
**Branch:** dev · **Categories:** tech, risks, existing, scope

## Origin

Four known false-positive patterns are already logged as workarounds in
`~/.claude/CLAUDE.md` and per-project memory, never as a fix:

1. Session on `dev`, command `cd <worktree> && git push` → hook sees `dev`
   from session CWD, blocks a worktree push that's actually fine.
2. Session on `main` (e.g. mid-release), then ANY cross-repo `git push` (tap,
   sibling project) → hook sees `main`, blocks unrelated-repo operations.
3. Compound commands containing the string `main`
   (`git pull origin main && git push origin dev`) → hook substring-matches
   on "main" and blocks the whole line.
4. Compound worktree-cleanup commands
   (`git worktree remove ... && git branch -D ...`) → blocked as a unit even
   when the branch delete is independently safe.

None of these is a bug in the *protection rules* (LOW/MEDIUM/HIGH tiers,
hard_deny) — they're bugs in **how the hook figures out what branch/repo a
command actually targets**. All four share one root cause.

## Context Scan

- `~/.claude/hooks/branch-guard.sh` (955 lines) is the live hook; the
  cached `PROPOSAL-branch-guard-improvements.md` (2026-02-13, v2.16.0) is
  stale — it predates confirm-mode/smart-tier and hard_deny (both shipped).
  Do not reuse its Priority 1 as still-open; it's done.
- Current architecture: hook reads `session.cwd` once, resolves branch via
  `git branch --show-current` in that cwd, then does regex/substring
  matching against the raw `command` string for risk classification. It
  never re-resolves cwd or branch per git-subcommand inside a compound
  command, and never accounts for `-C <path>` or a `cd` prefix changing the
  effective target.
- `REFCARD-BRANCH-GUARD.md` confirms the 3-tier model (LOW auto-allow /
  MEDIUM confirm / HIGH hard-block) plus the hard_deny layer (unconditional,
  classifier-level, no bypass) — the new fix must slot into this tier model,
  not replace it.
- Existing bypass mechanisms (`.claude/allow-once` one-shot,
  `/craft:git:unprotect` session-scoped) already give a "confirm, don't
  block" pattern to reuse rather than invent.

## Locked Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Root-cause fix shape | **Per-subcommand target resolution.** Split compound Bash commands on `&&` / `;` / `\|\|`, then for each `git`-touching clause resolve its *actual* target repo + branch from the clause's own args (`-C <path>`, a leading `cd <path> &&`, remote+refspec in `push`/`pull`) instead of session CWD or whole-string substring match. Classify each clause independently against the tiers. |
| 2 | Cross-repo `main`-session case | **Confirm, not block.** If a Bash command's resolved target repo differs from the session's repo, and that target's branch would otherwise trigger MEDIUM/HIGH, surface a `[CONFIRM]` (not a hard block) — user explicitly rejected a harder gate here ("I do not want hard gate to disrupt"). |
| 3 | Substring match on "main" | **Fixed by decision #1** as a side effect — word-boundary + per-clause resolution means `origin main` inside a `pull` clause targeting a non-protected branch no longer poisons classification of the rest of the line. |
| 4 | Worktree-cleanup compound blocking | **Fixed by decision #1** as a side effect — `git worktree remove <path>` and `git branch -D <branch>` become two independently-classified clauses; the branch-delete clause is checked against actual merge state (existing `git cherry` safe-delete logic referenced in CLAUDE.md), not blocked purely for being compound. |
| 5 | Scope boundary | **Target-resolution only, this pass.** Do not fold in Improvement 3 (tool-input auto-correction/coaching) or Improvement 4 (audit log) from the 2026-02-13 proposal — those are independent, already-deferred improvements; mixing them in enlarges this into a second confirm-mode-sized redesign. |

## Options Considered (not selected)

- **Patch each false positive independently** (targeted regex fixes, ~30–45
  min each) — faster to ship, but leaves the CWD-vs-target root cause open
  for the *next* compound-command pattern nobody's hit yet. Rejected in
  favor of the shared fix.
- **Push resolution entirely into Claude's behavior** (a rule: "always run
  cross-repo/worktree ops as separate Bash calls") — zero hook changes, but
  the CLAUDE.md workaround list already shows this discipline is easy to
  forget under normal work pressure; a rule that's already failing isn't a
  fix.
- **Exempt any command with `-C`/`cd <path>` from protection entirely** —
  simpler than full resolution, but blind whenever the target repo has no
  hook of its own installed (leaves a real gap, not just false positives).

## Risks / Edge Cases

- Per-clause resolution needs a `git -C <resolved-path> branch --show-current`
  call per clause — bounded (compound commands are typically 2–4 clauses),
  but worth confirming stays inside the existing ~25ms/invocation budget
  noted in the (stale) proposal's performance section before shipping.
- `-C` and `cd` are not the only ways a clause can change target (e.g. a
  `git push <remote-url>` where the remote itself points elsewhere) — v1
  should handle the two documented patterns (worktree `cd`, cross-repo
  `-C`/explicit path) and explicitly scope out remote-URL resolution as
  future work rather than silently mis-handling it.
- Confirm-mode for cross-repo `main` needs the `[CONFIRM]` message to name
  *which* repo/branch was resolved (not just "main") — otherwise the user
  can't tell the confirm prompt apart from the existing dev-branch confirm
  flow.

## Test Plan (scaffold, default-on)

Change shape: parser/detection logic inside an existing script + new
cross-clause data flow (clause N's resolved target feeds clause N's own
classification, independent of clause N-1). Tiers:

- **unit** — new clause-splitter + per-clause target-resolver functions;
  cases: single command (no split), 2-clause `&&`, 3-clause mixed
  `&&`/`;`, `-C <path>` override, leading `cd <path> &&`, remote+refspec
  parse for `push`/`pull`.
- **e2e** — full hook invocation (stdin JSON → exit code + stderr) for
  each of the 4 originating false-positive scenarios; assert each now
  passes (or correctly downgrades to `[CONFIRM]` for the cross-repo `main`
  case) instead of hard-blocking.
- **dogfood** — existing 138-ish branch-guard test suite must stay green;
  this is a refactor of classification internals, not new protection
  scope, so no regression in currently-correct blocks is acceptable.
- N/A — integration: no cross-command data flow beyond this hook itself.
- N/A — dependency: no external dependency change.
- N/A — count-cascade: not a new command/skill/agent.

`# TODO(author): delete if not contract-bearing` on each new stub until
confirmed.

## Documentation (scaffold, default-on)

Per the docs/sync scorer (threshold ≥3):

- [x] `docs/adr/ADR-001-workflow-branch-guard.md` — update: record this as
  a follow-on decision (per-clause resolution), don't re-litigate the
  original ADR.
- [x] `docs/reference/REFCARD-BRANCH-GUARD.md` — update the "Quick Decision
  Tree" and "What Triggers Each Tier" tables once clause-level resolution
  changes what counts as "the branch" for a compound command.
- N/A — guide (`docs/guide/branch-guard-smart-mode.md`) — score <3, no
  user-facing mode change, internal resolution fix only.
- N/A — tutorial (`TUTORIAL-branch-guard-setup.md`) — score <3, setup flow
  unaffected.

CHANGELOG `[Unreleased]` entry also expected (fix, not feat — false
positives corrected, no new protection tier).

## Next Command

`/craft:plan:feature "branch-guard target-resolution fix" --spec BRAINSTORM-branch-guard-target-resolution-2026-07-14.md`
— or capture as a SPEC first with `/craft:grill` if the per-clause parser
design (decision #1) needs adversarial stress-testing before implementation
(compound-command splitting is exactly the kind of edge-case-heavy logic
that benefits from a grill pass).
