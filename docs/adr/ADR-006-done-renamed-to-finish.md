# ADR-006: `/craft:done` renamed to `/craft:finish`

**Status:** Accepted
**Date:** 2026-07-17
**Supersedes:** ADR-002 on naming only — ADR-002's shim-vs-skill rationale (the
command is a thin routing file, all logic lives in the `adhd-workflow` skill's
`references/done.md`) is unchanged and still governs.

## Context

A user-level root alias (`~/.claude/commands/refine.md`) was created earlier to
give `/craft:refine` a bare, un-namespaced entry point, since Claude Code
requires every plugin command to carry its `<plugin>:` prefix and offers no
platform mechanism for a bare command. The same need came up for
`/craft:done` and `/craft:do`.

A debate (`docs/specs/BRAINSTORM-*-2026-07-17.md` context, captured in chat) on
aliasing both concluded:

- `/craft:do` — too generic a name (high collision risk with other plugins)
  and too much routing logic (branch gating, complexity scoring, `--orch`
  delegation) to alias safely without drift. **Not aliased.**
- `/craft:done` — a thin shim, low risk, but the user already has a zsh-level
  `finish` alias (see `~/.claude/CLAUDE.md`'s Shell Integration section) for
  the same "end session" concept. Rather than alias `/craft:done` under a
  second, different name (`/finish` pointing at `/craft:done`), the decision
  was to rename the canonical command itself so the vocabulary is one name,
  not two, across the shell and Claude Code layers.

## Decision

`commands/done.md` is renamed to `commands/finish.md`. The command is now
`/craft:finish`; `/craft:done` no longer exists (no backward-compatible shim
was kept — this was a rename, not an addition, so the command count is
unaffected). The canonical skill reference file
(`skills/workflow/adhd-workflow/references/done.md`) keeps its filename for
path stability (same precedent as `brainstorm-insights` keeping its directory
name after a similar split) but its prose now refers to `/finish`/`/craft:finish`.

A user-level root alias `~/.claude/commands/finish.md` delegates to
`/craft:finish`, mirroring the existing `~/.claude/commands/refine.md`
pattern (machine-local, can drift silently, breaks silently if craft moves —
same stated trade-offs).

## Consequences

- Any external reference to `/craft:done` (docs, muscle memory, scripts) is
  stale as of this ADR and must use `/craft:finish`.
- Natural-language triggers ("wrap up", "I'm done") in the `adhd-workflow`
  skill are unaffected — they still route to the same reference file.
- Historical docs (specs, plans, CHANGELOG, other ADRs) that mention
  `/craft:done` are left as-is — they are point-in-time records, not live
  documentation, per this repo's own doc-staleness-check exclusion
  convention (`docs/specs/`, `docs/adr/`, `CHANGELOG.md`, `docs/plans/` are
  excluded from staleness scans for this reason).
