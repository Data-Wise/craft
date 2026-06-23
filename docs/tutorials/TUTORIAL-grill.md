# Tutorial: Interrogate a Plan with /craft:grill

> Learn when to grill, how the one-at-a-time loop works, and how a grill session feeds the
> planning pipeline.

## When to reach for grill

Use `/craft:grill` when you already have a **position** — a spec, a plan, or even a rough idea —
and you want it stress-tested before you write code. It is the **convergent** counterpart to
`/craft:workflow:brainstorm`:

- **brainstorm** opens the space: "what could we build?"
- **grill** closes it: "where does this plan break?"

If you only have a vague "I want to build X", grill will sketch a quick skeleton first, then
interrogate that — but you'll get sharper results by brainstorming first, then grilling the spec.

## A worked session

```bash
/craft:grill docs/specs/SPEC-auth-2026-06-22.md
```

1. **Codebase-first.** Before asking anything, grill reads your `.STATUS`, recent commits, and the
   spec itself, pre-answering everything it can. You only get asked about genuine unknowns.
2. **One question at a time.** Each question targets a single design-tree branch and carries a
   **Recommended:** answer. You confirm or redirect — no open-ended essays.

   ```text
   Q: The spec stores sessions in memory. Should sessions survive a restart?
      Recommended: Yes — persist to the existing SQLite store (matches auth/db.py).
   > [your answer, or accept the recommendation]
   ```

3. **Milestones.** Every 5 resolved branches, grill pauses: *keep going / wrap up / show ledger so
   far* — so a long interrogation stays manageable.
4. **Halt anytime.** Enter `/done` (or empty-enter) to stop. Pass `--bound 3` to cap the session
   at three branches up front.

## What you get

A durable decision ledger at `docs/specs/GRILL-auth-2026-06-22.md`:

```markdown
## Decision Ledger

| # | Branch | Decision |
|---|--------|----------|
| 1 | Session persistence | Persist to SQLite |
| 2 | Token rotation | Rotate on each refresh |
```

grill never overwrites a brainstorm `SPEC-*` — if one exists for the same topic, grill writes its
own `GRILL-*` file and adds a cross-link both ways.

## Handoff

When you're done, grill offers to hand the locked decisions forward:

```text
/craft:plan  →  ORCHESTRATE-*.md  →  /craft:do
```

grill itself never executes — it interrogates and hands the artifact onward.

## Embedded use

`/craft:orchestrate` reuses grill in its **Step 0.5 Clarify**: on an ambiguous task it runs
`/craft:grill --bound 2 --no-capture` to lock the plan-shaping decisions before building the
orchestration plan — no `GRILL-*` file is written mid-orchestration.

## See also

- [`/craft:grill` reference](../commands/grill.md)
- [`/craft:workflow:brainstorm`](../commands.md) — generate options first
