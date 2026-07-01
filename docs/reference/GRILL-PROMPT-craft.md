# Reusable Grill Prompt (craft-tuned)

A workflow-tuned adversarial grill prompt for stress-testing any craft
proposal / spec / plan before implementation. Swap `<TARGET>` for the file
path or topic. Attack axes 3–6 encode craft-specific traps that have bitten
this repo before (rich-body-trap, phantom-command discovery, unmeasured token
claims, the python-3.9 test gotcha).

## The prompt

```text
Grill <TARGET> (proposal / spec / plan). Convergent: one AskUserQuestion at a
time, and for EVERY question state your explicit recommendation first (which
option + one-line why), Recommended option first. Attack these axes, hardest
first, skipping any that don't apply:

1. Weakest recommendation — the call that looks worst in hindsight; name the
   cheaper/safer alternative.
2. Riskiest assumption — the load-bearing belief that breaks the plan if false.
   Prioritise SILENT failures (behavior lost, not errors thrown).
3. Implementation regret — grounded in this repo's real gotchas: the
   deprecated-command rich-body-trap (ADR-002 — consolidating a command into a
   skill silently drops behavior); craft auto-discovery (ANY .md under commands/
   becomes a command → phantom-command risk); the ~30-file count cascade a
   command add/remove triggers.
4. Token-cost honesty — is any claimed saving measured or just asserted? Flag
   "token-first" framing not backed by /usage data; separate real levers
   (progressive disclosure, thin shims) from wishful ones.
5. Branch / worktree / test discipline — does execution respect dev→feature→main
   + branch-guard, FULL-suite verify (not a sampled subset, and NOT bare python3
   = the 3.9 baseline gotcha), and verify-before-merge?
6. Doc / convention blast radius — does this silently change a craft-wide
   convention or need a doc-drift sweep (~15 files)? Scoped or hidden?
7. Reversibility & scope creep — anything irreversible or ballooning past scope?
   Hold vs. proceed?

Stop when the load-bearing branches are resolved (not exhaustively). Persist each
decision to the GRILL ledger, apply concrete fixes back to the target doc, and
end with what HELD UP under attack vs. what changed. Keep it ADHD-friendly.
```

## Notes

- **Axes 1–2** are the generic adversarial core; **3–7** are craft-workflow-tuned.
- **Axis 3 references:** ADR-002 (deprecated-command-rich-body-trap),
  `commands/_discovery.py` auto-discovery, and the count-cascade class of drift.
- **Axis 5's python gotcha:** default `python3` is Xcode's 3.9 and crashes on
  `dict | None` in `commands/_discovery.py`; run the suite via
  `/opt/homebrew/bin/python3.13 -m pytest tests/ -q` (or `uv run --no-project
  --with pytest --with pyyaml pytest`).
- First proven use: adversarial pass on
  `docs/specs/PROPOSAL-orchestrate-family-simplification-2026-07-01.md`
  (2026-07-01) — caught a phantom-command trap and a rich-body-trap before
  implementation.
