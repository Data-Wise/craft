# GRILL: /usage checkpoint tooling — 2026-06-30

**Target:** design proposal from an in-progress `superpowers:brainstorming` session — fixing the
broken post-PR#232 `/usage` checkpoint tracking (`.STATUS` next-action item D), after the
scheduled-trigger API (`send_later`/`create_trigger`/`list_triggers`) returned 404 across the
board (confirmed as a known platform-wide issue via `anthropics/claude-code` issues #43438, #40460,
and #53581 — not session-specific, retrying wouldn't help).

**Brainstorm SPEC cross-link:** none — no matching `SPEC-usage-checkpoint-tooling-*.md` exists yet;
this grill session precedes and feeds the spec.

**Note on interactivity:** the first `AskUserQuestion` in this grill session went unanswered
(user unavailable mid-session). Per the milestone/auto-mode convention, subsequent branches were
resolved using each question's own **Recommended** option rather than blocking further — every
resolution below is still logged with its reasoning so it can be overridden later.

---

## Decision Ledger

### 1. Where does the measured `/usage` result get recorded?

**Resolved:** addendum to `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` — **not**
`docs/internal/TOKEN-EFFICIENCY-craft.md` (which was this session's original brainstormed
proposal, before the codebase-first sweep caught the conflict).

**Why:** `.STATUS` item D (written earlier this same session) already explicitly commits to this:
*"Record the result as an addendum to that SPEC, not a new doc."* Changing the target file now
would mean editing an already-committed decision without new information forcing the change —
the SPEC is also the correct target on its own merits: it's the document that flagged the
`/usage` hypothesis as unvalidated in the first place, and it already has a matching addendum
pattern (the namespace-refactor token-cost addendum, written the same day). No `.STATUS` wording
fix needed — the SPEC target and the already-committed text agree.

**Consequence of the alternative (rejected):** would have required a follow-up edit to `.STATUS`
item D to keep the two in sync, and split the token-efficiency narrative across two files with no
strong reason.

### 2. Exact tool + package identity

**Resolved and empirically verified** (not guessed):

- `npx ccusage` — no install required, confirmed working live against this machine's real Claude
  Code usage logs. `ccusage daily --since YYYY-MM-DD --until YYYY-MM-DD` is the exact,
  help-verified flag syntax for a date-ranged historical report (also supports `--json` for
  machine-readable output).
- `claude-monitor` — the correct PyPI package name for the "Claude-Code-Usage-Monitor" project
  (earlier research had cited the GitHub repo name, `Claude-Code-Usage-Monitor`, which is **not**
  the installable package name — a real gap the codebase-first sweep caught before it could ship
  into a doc as a broken install command). Install: `uv tool install claude-monitor`. Run:
  `claude-monitor` (aliases `cmonitor`, `ccmonitor`).

**Consequence of not verifying:** the original brainstormed design would have shipped an
unverified `--since` flag guess and a wrong package name (`claude-code-usage-monitor` instead of
`claude-monitor`) into a committed doc — exactly the kind of unverified-claim pattern this whole
session has been correcting elsewhere (PR #232's token-cost overclaims).

### 3. Does the pre-merge baseline already exist, or does something need to capture it first?

**Resolved:** it already exists — no capture step needed. Confirmed live: `ccusage daily --since
2026-06-25` returned real historical rows on this machine covering the period before PR #232
merged (2026-07-01). Claude Code's local usage logs are generated automatically and continuously;
`ccusage`/`claude-monitor` just read them. The `.STATUS` item D checkpoint (~2026-07-14) can query
a date range spanning the merge point directly — no separate "start logging now" action required.

### 4. When does actual tool installation happen — now, or as part of a later implementation step?

**Resolved:** defer `uv tool install claude-monitor` to the implementation-plan execution phase,
not during grill/spec authoring. `ccusage` needs no install (npx runs it on demand) so it has no
equivalent deferred step. This matches grill's own stated boundary — "grill never executes."

### 5. Should this tooling note also live in a personal/global reference doc, since the tools themselves aren't craft-specific?

**Resolved:** no — scope this to the SPEC addendum only. The tools are generic, but the *need*
being solved (validate PR #232's specific token-reduction hypothesis) is craft-specific, and
craft's own `CLAUDE.md` "Available Tooling Notes" pattern is for dispatchers/CLIs the user already
treats as standing personal infrastructure (`himalaya`, `em`, `tok`). This is a one-off
verification tool for one hypothesis, not yet an established personal habit — promoting it to a
global reference doc now would be scope creep ahead of actual use.

---

## Open Questions

None outstanding — all 5 branches resolved. Ready for `/craft:plan` (spec write-up +
implementation plan).
