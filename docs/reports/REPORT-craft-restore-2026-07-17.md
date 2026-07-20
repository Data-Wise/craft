# Report: `/craft:restore` Spec

> Source: [`SPEC-craft-restore-2026-07-17.md`](../specs/SPEC-craft-restore-2026-07-17.md)

**Status:** SHIPPED — implemented as `commands/restore.md`, released in v4.1.0 (2026-07-17) *(source doc status corrected 2026-07-17; it read "DRAFT" from before the command was actually released)*

## tl;dr

| Metric | Value |
|---|---|
| New files this spec produces | 1 (`commands/restore.md`) |
| Output modes | 3 (`default` / `detailed` / `summary`) |
| Locked decisions (grill) | 3 |
| Success criteria | 5 |
| Open questions | 2 |

## What it does

Give craft a single, read-only "restore my context" command combining:

1. **Git-activity recap** (today/week commits, branch ahead/behind, unpushed
   work, open PRs) — currently `skills/dev/git/SKILL.md` Operation 7.
2. **`.STATUS`-based session recap** — currently the `adhd-workflow` skill.

Today these are two separate asks; `/craft:restore` merges them into one
output, mirroring `savant:restore`'s framing.

**Explicitly out of scope:** a cross-plugin `/restore` dispatcher (routing to
`savant:restore` for research projects vs. `craft:restore` for dev-tools
projects). Investigated and confirmed structurally blocked — craft's
`/do`/`/hub` routers cannot dispatch into another plugin's namespace.

**Project structure:** no new directories. Only `commands/restore.md` is new;
`skills/dev/git/SKILL.md` and `skills/workflow/adhd-workflow/` stay unchanged
(canonical logic sources).

## How it's built

- **Code style:** follows the `commands/done.md` thin-shim convention (not
  `commands/next.md`, which predates the shim pattern). No
  `deprecated`/`replaced-by` frontmatter — net-new command name, not a
  migration shim.
- **Modes:** `default` | `detailed` | `summary` apply to the git-activity
  portion only (`dev/git` skill already implements them). `adhd-workflow`'s
  recap has no mode support — verified before writing the spec, not assumed.
  Adding modes there is an open question, not shipped.
- **Overlap handling:** both source skills independently surface recent git
  activity and open PRs — the shim de-dupes into one combined git-activity
  block at presentation time, not two.

## Guardrails

- **Always do:** keep all logic in the two source skills — the command file
  is routing only. Run doc-staleness/count validators before PR.
- **Ask first:** deprecating `dev/git` Operation 7's direct invocation path
  in favor of routing everything through `/craft:restore`; adding a `--sync`
  flag later.
- **Never do:** implement the cross-plugin `/restore` dispatcher as part of
  this work; add write/sync behavior — read-only by design.
- **Testing strategy:** docs-only change — minimum bar is lint +
  count/staleness validators, not the full suite. Also requires manual
  dogfood of all 3 modes with real output (E2E evidence per
  `e2e-before-pr.md`), and a sweep of `commands/hub.md`/`docs/commands/hub.md`
  for stale "git recap" phrasing.

## Success Criteria

- `/craft:restore` (default mode) prints a combined git-activity +
  `.STATUS` summary.
- `detailed`/`summary` modes both work and visibly differ in verbosity.
- No `--sync` or write behavior exists.
- `hub.md`/`docs/commands/hub.md` no longer reference `git-recap`/`recap`.
- `validate-counts.sh` and `docs-staleness-check.sh` both pass clean.

## Locked Decisions (from grill, 2026-07-17)

1. **Scope:** combine BOTH git-activity recap and `.STATUS`-based session
   recap into one command, one combined output.
2. **`--sync` flag:** NOT included — read-only only, unlike `savant:restore`'s
   optional write path.
3. **Output modes:** keep the existing `default`/`detailed`/`summary` shape
   already in `dev/git` Operation 7 — no new modes.

## Open Questions

1. Should a future `--sync` mode (mirroring `savant:restore --sync`) ever be
   added? Deferred — no current use case identified.
2. Should the cross-plugin dispatcher idea get its own spec later? Not this
   spec's call — flagged for a future, separate proposal if wanted.
