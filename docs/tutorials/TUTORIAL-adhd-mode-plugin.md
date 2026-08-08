# ADHD Mode Plugin Cheat Sheet

Run `claude plugin install i-have-adhd@i-have-adhd`, then create
`~/.claude/.i-have-adhd` to turn it on for every session. Say "stop adhd
mode" to turn it off for just the current session.

## What it does

Reshapes every response to be actionable for an ADHD brain: leads with the
next action, numbers multi-step tasks, caps lists at 5 items, restates
progress every turn, and cuts preamble/recap/closing pleasantries.

## Setup

```bash
claude plugin install i-have-adhd@i-have-adhd
touch ~/.claude/.i-have-adhd   # always-on across all sessions
```

Without the marker file, the mode activates per-session only when
explicitly requested or triggered by a hook.

## Gotchas

1. **"stop adhd mode" is session-scoped.** It doesn't delete the marker
   file — the next new session starts with ADHD mode active again if
   `~/.claude/.i-have-adhd` still exists.
2. **It overrides default response shape, not correctness.** Destructive
   actions, real ambiguity, and debug spirals still get full explanations —
   the rule set has explicit exceptions for those, it doesn't force brevity
   everywhere.
3. **Delete the marker file to turn it off for good** — `rm
   ~/.claude/.i-have-adhd` — rather than repeating "stop adhd mode" every
   new session.
