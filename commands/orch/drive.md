---
description: Drive an approved SPEC to completion via the native /goal turn-loop, with a real verify gate; stops at verified green and prints the PR command
category: orchestrate
arguments:
  - name: spec
    description: "Path to SPEC-*.md (default: newest docs/specs/SPEC-*.md or the one referenced by the worktree's ORCHESTRATE-*.md)"
    required: false
  - name: dry-run
    description: Print derived condition + dispatch plan + precondition report; zero side effects
    required: false
    default: false
    alias: -n
  - name: yes
    description: Skip the condition-confirm gate
    required: false
    default: false
    alias: -y
  - name: max-turns
    description: Turn bound folded into the condition's stop clause
    required: false
    default: 25
  - name: no-auto
    description: Do not enable auto mode (approve tools per turn)
    required: false
    default: false
  - name: agents
    description: Max concurrent file-scoped subagents per turn
    required: false
    default: 1
  - name: condition
    description: Override the synthesized /goal condition entirely
    required: false
---

# /craft:orch:drive — Spec-Driven Autonomous Loop

Drives an approved SPEC to completion using Claude Code's built-in `/goal`
as the turn-loop engine. Thin wrapper: it owns condition synthesis,
precondition gating, and the confirm gate — and delegates dispatch + the
real verify gate to the `drive-engine` skill.

> **drive vs `/craft:orch --swarm`:** `drive` is a spec-anchored
> `/goal` turn-loop (iterate until a condition holds, real verify
> arbitrates). `--swarm` is free-form fan-out-and-converge across isolated
> worktrees. Use `drive` when you have an approved spec and want
> autonomous completion; use `--swarm` for parallel independent tasks.

## Execution Behavior (MANDATORY)

Follow these steps in order. Do NOT skip any step.

### Step 1: Locate the spec

Use the `spec` arg; else the newest `docs/specs/SPEC-*.md`; else the spec
referenced by the worktree's `ORCHESTRATE-*.md`. Report which was chosen.

### Step 2: Precondition checks (block with remedy on failure)

| Check | Block reason | Remedy shown |
|-------|--------------|--------------|
| Worktree on `feature/*` | Not isolated | `git worktree add … -b feature/<topic> dev` |
| Hooks not blocking `/goal` (`disableAllHooks` / `allowManagedHooksOnly`) | `/goal` disabled by policy | Adjust hook policy |
| Workspace trust accepted | `/goal` needs trust | Accept workspace trust |
| Auto mode on (unless `--no-auto`) | Loop can't run unattended | Offer to enable in confirm gate |

**Whether the `/goal` engine exists at all (Claude Code CLI vs. any other harness) is NOT
checkable here** — `/goal` is a native slash command, not an introspectable tool, so no prose
instruction at this step can reliably detect its absence ahead of time (see
`GRILL-goal-engine-detection-2026-07-14.md`). That check is empirical and happens at Step 6
instead — do not attempt to predict it in this table.

### Step 3: Synthesize the `/goal` condition

From the spec's **Acceptance Criteria** + **Review Checklist**, build a
condition that is (a) measurable, (b) provable-in-transcript by showing
command output, (c) bounded by `--max-turns`. Honor `--condition` override.
Template:
> `<criteria as end states> — prove each by showing the relevant command
> output in the transcript (e.g. test runner exit, git status). Do not
> change <stated constraints>. Or stop after <max-turns> turns.`

### Step 4: `--dry-run` (zero side effects)

If `--dry-run`, print the derived condition + dispatch plan (from
`drive-engine`) + precondition report, then STOP. Set no goal; change no
auto-mode state.

### Step 5: Confirm gate (defaults to No)

Show the condition. If auto mode is off and `--no-auto` not set, OFFER to
enable it here (never silent). Proceed only on explicit Yes or `--yes`.

### Step 6: Drive the loop

Emit `/goal <condition>`. **This emission IS the `/goal`-availability check** — no separate
probe (a probe would either be redundant in a working session or would itself set a real goal
state, which defeats the point of "harmless"). If there is no observable effect (no goal-status
echo, no state change reported back), STOP immediately and report: "No observable effect after
emitting `/goal` — this harness likely doesn't support the native `/goal` engine. For a
single-scope spec, implement it directly in the worktree (same as any other feature work); use
`/craft:orch --swarm` only if the spec genuinely decomposes into independent parallel scopes."
Do not fall back to `drive-engine`'s dispatch loop without a working `/goal` — that loop's
termination depends on the `/goal` evaluator clearing, which never happens if the engine isn't
there.

Otherwise (goal set successfully), per turn invoke the `drive-engine` skill to dispatch
`--agents N` (default 1) file-scoped subagents.

### Step 7: Real verify gate (authoritative)

When the goal clears, the `drive-engine` skill runs the project's actual
verify command + `git status --short`. Green is required to declare done —
a green-looking transcript alone is NOT sufficient.

### Step 8: Green handoff (no auto-PR)

On verified green, STOP and print the exact command for the user to run,
e.g. `gh pr create --base dev`. Never open the PR yourself.

## Exit paths

- Condition met → real verify → green handoff
- `--max-turns` bound hit → report progress, stop
- User `/goal clear` → stop (drive does not shadow native `/goal`)

## See Also

- `/craft:orch` — free-form multi-agent orchestration (`--swarm`)
- `plan-orchestrator` skill — produce an ORCHESTRATE file from a spec
- `drive-engine` skill — the dispatch + verify body this command calls
