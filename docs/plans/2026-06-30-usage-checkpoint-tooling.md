# /usage Checkpoint Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install and smoke-test the two tools `SPEC-token-efficiency-research-2026-06-30.md` §9
commits to (`claude-monitor`, `ccusage`), closing the last two open Done Signal items now that the
scheduled-trigger dependency has been replaced with direct commands.

**Architecture:** Pure tooling verification — one global CLI install (`uv tool install
claude-monitor`) and two command smoke-tests (`claude-monitor`, `npx ccusage daily`). No repo code
changes; nothing in `craft` itself is modified by this plan.

**Tech Stack:** `uv` (already present: `/opt/homebrew/bin/uv`, v0.11.26), `npx`/`node` (already
present: v26.4.0), Python (via `uv tool`).

## Global Constraints

- Package name is `claude-monitor` on PyPI — **not** `claude-code-usage-monitor` (that's the
  GitHub repo name, verified non-installable during grill).
- `ccusage` requires no install; always invoke via `npx ccusage@latest` or bare `npx ccusage`
  (both resolve the same cached package after first run).
- Pre-merge baseline date range: `--since 2026-06-25 --until 2026-06-30` (verified non-overlapping
  with post-merge range — PR #232 merged 2026-07-01).
- Post-merge date range: `--since 2026-07-01` (open-ended; real comparison data accumulates from
  here through the ~2026-07-14 checkpoint).
- No code, no tests, no commits to `craft` — this plan's only artifacts are local CLI state
  (an installed tool) and terminal verification output.

---

### Task 1: Install `claude-monitor`

**Files:** None — global `uv tool` install, outside the repo.

**Interfaces:** None.

- [ ] **Step 1: Confirm it isn't already installed**

```bash
uv tool list 2>&1 | grep -i claude-monitor || echo "not installed"
```

Expected: `not installed` (first-time install) — if it's already listed, skip to Step 3.

- [ ] **Step 2: Install**

```bash
uv tool install claude-monitor
```

Expected: exits 0, prints an "Installed" confirmation naming `claude-monitor` (and typically the
`cmonitor`/`ccmonitor` aliases) with their install path under `~/.local/bin` (or `uv`'s tool bin
dir).

- [ ] **Step 3: Verify it's on PATH**

```bash
which claude-monitor
claude-monitor --version 2>&1 | head -5
```

Expected: `which` resolves to a path under the `uv tool` bin directory; `--version` (or
equivalent flag — check `claude-monitor --help` if `--version` isn't supported) exits 0 without a
traceback.

---

### Task 2: Smoke-test both tools against real data

**Files:** None.

**Interfaces:**

- Consumes: `claude-monitor` binary on PATH (Task 1's deliverable).

- [ ] **Step 1: Launch `claude-monitor` non-interactively and confirm no crash**

`claude-monitor` is a live dashboard (per SPEC §9, "ongoing live-session awareness") — it doesn't
exit on its own, so run it with a timeout rather than waiting indefinitely:

```bash
timeout 5 claude-monitor 2>&1 | head -20; echo "exit code: $?"
```

Expected: some rendered dashboard/table output (not an immediate traceback or "command not
found"); exit code `124` (timeout fired, meaning it was running fine and had to be killed) or `0`
are both acceptable — anything else (e.g. `1`, `127`) indicates a real failure to investigate.

- [ ] **Step 2: Re-confirm the pre-merge baseline command from SPEC §9**

```bash
npx ccusage daily --since 2026-06-25 --until 2026-06-30
```

Expected: a table of daily usage rows for that date range, matching the format already observed
during grill (columns: Date, Agent, Models, Input, Output, Cache Create, Cache Read, Total Tokens,
Cost). Non-empty — this data already existed as of the grill session.

- [ ] **Step 3: Re-confirm the post-merge command from SPEC §9**

```bash
npx ccusage daily --since 2026-07-01
```

Expected: exits 0 and produces valid table output (headers + at least today's row, since this
session itself generates usage data). Real comparison data will keep accumulating here through
the ~2026-07-14 checkpoint — this step only confirms the command syntax works, not that the full
two-week dataset exists yet.

- [ ] **Step 4: No commit** — this task produces terminal output only; nothing in the repo changes.
If Task 1 or Task 2 surfaces something worth recording (e.g. the install path, or a command that
didn't work as documented), fix `SPEC-token-efficiency-research-2026-06-30.md` §9 or `.STATUS`
item D directly and commit that correction — but the smoke test itself has no artifact to commit.

---

## Done Signal

- [ ] `claude-monitor` installed via `uv tool install claude-monitor` and confirmed on PATH
- [ ] `claude-monitor` launches without crashing (timeout-based smoke test)
- [ ] Both `ccusage` date-range commands from SPEC §9 re-verified working
- [ ] Any discrepancy found between this plan's expectations and actual tool behavior is corrected
      in SPEC §9 / `.STATUS` item D directly, not left undocumented
