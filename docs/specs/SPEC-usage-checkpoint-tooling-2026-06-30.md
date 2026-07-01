# craft: /usage Checkpoint Tooling Spec

**Date:** 2026-06-30
**Status:** Planning
**Grilled:** `docs/specs/GRILL-usage-checkpoint-tooling-2026-06-30.md` (5 branches resolved)
**Fixes:** `.STATUS` next-action item D's tracking mechanism (not its target date or purpose)

---

## Context

PR #232's own `SPEC-token-efficiency-research-2026-06-30.md` flags its headline 48% figure as a
line-count reduction, not a validated token-usage saving — real `/usage` data was left as an
open, dated follow-up (`.STATUS` item D, ~2026-07-14). The original plan was to schedule an
automated reminder via `send_later`/`create_trigger`. All three scheduling calls
(`send_later`, `create_trigger`, `list_triggers`) returned HTTP 404 during that session — confirmed
via web research as a known, currently-open platform issue
(`anthropics/claude-code` [#43438](https://github.com/anthropics/claude-code/issues/43438),
[#40460](https://github.com/anthropics/claude-code/issues/40460),
[#53581](https://github.com/anthropics/claude-code/issues/53581)), not something specific to this
session or account. Retrying the scheduler isn't a fix.

This spec replaces "wait for a trigger to fire" with "run a verified command against data that
already exists" — removing the dependency on the broken scheduling infrastructure entirely.

---

## Decision Summary (from grill)

| # | Question | Resolution |
|---|---|---|
| 1 | Where does the result get recorded? | Addendum to `SPEC-token-efficiency-research-2026-06-30.md` — matches what `.STATUS` item D already committed to; no wording fix needed there. |
| 2 | Exact tool + package identity | `npx ccusage` (no install; verified `--since`/`--until` flags, `YYYY-MM-DD` format) + `claude-monitor` (the actual PyPI package — **not** `claude-code-usage-monitor`, the GitHub repo name). |
| 3 | Does a pre-merge baseline already exist? | Yes — confirmed live: `ccusage daily --since 2026-06-25` returns real historical rows on this machine predating the PR #232 merge. No separate capture step needed. |
| 4 | When does installation happen? | Deferred to the implementation plan's execution phase — grill/spec don't execute. `ccusage` needs no install (npx runs it on demand). |
| 5 | Global reference doc, or scoped to this SPEC? | Scoped to this SPEC's addendum only — the need is specific to validating PR #232's hypothesis, not yet an established personal tooling habit worth promoting to `~/.claude/reference/`. |

Full reasoning for each: `docs/specs/GRILL-usage-checkpoint-tooling-2026-06-30.md`.

---

## What changes

### `.STATUS` item D

Current text references the broken trigger indirectly (via "record the result..." with no
concrete command). Rewrite to reference the exact, verified commands:

```
ccusage daily --since 2026-06-25 --until 2026-06-30   # pre-merge baseline (already exists)
ccusage daily --since 2026-07-01                       # post-merge (PR #232 merged 2026-07-01; run at checkpoint time)
```

Target date (~2026-07-14) and destination (addendum to `SPEC-token-efficiency-research-2026-06-30.md`)
stay unchanged — only the mechanism changes, from "wait for an automated reminder" to "run this
command when you next pick this repo back up."

### New tooling (installed at implementation time, not now)

- `claude-monitor` via `uv tool install claude-monitor` — for ongoing live-session awareness,
  independent of this specific checkpoint (was the "Both" answer to the tool-model question
  earlier in this session's brainstorming — kept as a standing install, not scoped only to this
  one checkpoint).

### No new files beyond the eventual addendum

Consistent with decision 5 — this SPEC and its eventual addendum to
`SPEC-token-efficiency-research-2026-06-30.md` are the only durable artifacts. No new reference
doc, no change to `TOKEN-EFFICIENCY-craft.md`.

---

## Out of scope

- Actually running the ~2026-07-14 checkpoint and writing its addendum — that's future work at
  the target date, not part of this spec's implementation plan.
- Fixing the underlying scheduled-trigger platform bug — external to this repo, tracked upstream
  via the linked GitHub issues.
- Any change to `.STATUS` item E (Validate Plugin Structure CI flake) — unrelated next-action item.

---

## Done Signal

- [ ] `.STATUS` item D rewritten with the exact `ccusage` commands
- [ ] `claude-monitor` installed via `uv tool install`
- [ ] Both tools smoke-tested against real local usage data
- [ ] No new reference docs created beyond this SPEC
