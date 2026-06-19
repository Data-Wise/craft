# RESEARCH: Hierarchical Worktrees + Workflow — "worktree → sub-worktrees" / "dev → worktrees"

**Status:** research note — **direction resolved 2026-06-18** (see bottom); no code yet
**Created:** 2026-06-18
**Question:** Can/should we spawn worktrees *from* a worktree (sub-worktrees), or dev → worktrees,
and drive it with the platform `Workflow` tool?

---

## TL;DR

- **"dev → worktrees" already exists** — it is exactly craft `--swarm` (base branch off `dev`,
  N sibling worktrees, parallel agents, converge-merge back, one PR).
- **Physically nested worktrees are a git anti-pattern.** Git worktrees are a **flat set of
  siblings** sharing one `.git`; a worktree inside another worktree confuses git and pollutes
  the outer tree. There is no real "sub-worktree" object.
- **What the idea actually wants is hierarchical *branch topology* over a *flat* set of
  worktrees**, with **multi-level convergence merges**. That IS feasible — it's craft swarm
  extended from 1 level to 2.
- **The platform `Workflow` tool can't express the 2-level orchestration** (workflow nesting is
  capped at **one level** — `workflow()` inside a child throws). It *can* do a **flat** worktree
  swarm in a single workflow. Two levels = two separate workflow runs you sequence yourself.
- **Token note:** worktrees (and sub-worktrees) are **isolation only — 0 token savings**. They
  buy parallelism + conflict-freedom at the cost of setup, disk, and **N×M merge convergence**.

---

## The git reality (verified)

- All worktrees register against **one shared object store**; craft places them as **siblings**
  in `~/.git-worktrees/craft/` (verified: `git worktree list` shows dev + two siblings, none
  nested). git 2.54.
- You *can* `git worktree add` a path physically inside another worktree, but the inner files
  show as untracked noise in the outer worktree and tooling (incl. craft's CWD guard) gets
  confused. **Not recommended.** "Nested worktrees" should mean **branch hierarchy**, not
  **directory nesting**.

## What craft already does — 1-level (`--swarm`)

```
dev
 └─ feature/swarm-<task>            ← convergence branch
     ├─ swarm-<task>-agent1  (worktree, off dev)
     ├─ swarm-<task>-agent2  (worktree, off dev)
     └─ swarm-<task>-agent3  (worktree, off dev)
   → merge all swarm-* → feature/swarm-<task> → test → 1 PR → dev → cleanup
```

Worktrees are short-lived, `swarm-*` branches, scoped to file ranges via the ORCHESTRATE file.

## The proposed extension — 2-level (branch hierarchy, flat worktrees)

A large feature that itself decomposes into parallel sub-features, each parallelizable:

```
dev
 └─ feature/big                         ← top convergence branch
     ├─ feature/big-subA                ← sub-convergence branch
     │   ├─ swarm-subA-1  (worktree off feature/big-subA)
     │   └─ swarm-subA-2  (worktree off feature/big-subA)
     └─ feature/big-subB                ← sub-convergence branch
         ├─ swarm-subB-1  (worktree off feature/big-subB)
         └─ swarm-subB-2  (worktree off feature/big-subB)
   → merge swarm-subA-* → feature/big-subA ; swarm-subB-* → feature/big-subB
   → merge feature/big-sub* → feature/big → test → 1 PR → dev
```

All worktrees are still **physical siblings** in `~/.git-worktrees/craft/`; only the **branch
topology** is hierarchical. Convergence is **bottom-up, level by level**, with a **test gate at
each merge level**.

---

## Options

### A. Extend craft `--swarm` to 2-level branch hierarchy (no Workflow tool)

- Sub-convergence branches + bottom-up merge waves; reuse the existing ORCHESTRATE swarm config,
  nested one level.
- **Pro:** stays in craft's portable Task-tool model; reuses convergence + cleanup machinery.
- **Con:** merge complexity grows (N×M); test-gate at each level; ORCHESTRATE file must express
  the 2-level map. Real risk of merge-conflict thrash if sub-features touch shared files.

### B. Flat worktree swarm via the platform `Workflow` tool (1 level only)

- One workflow, `parallel(agents.map(a => () => agent(a, {isolation:'worktree'})))`; the JS
  layer is free, each agent gets an auto-cleaned worktree.
- **Pro:** deterministic control flow, per-agent model/effort, `budget` cap, schema'd returns.
- **Con:** **only 1 level** (nesting capped); you converge in code, not via craft's PR pipeline.
  Re-implements convergence outside craft.

### C. Hybrid — Workflow per level, sequenced by hand

- Run a parent Workflow for the top split; for each sub-feature, run a **separate** Workflow
  (you sequence them). Each is a flat worktree swarm; you merge each level up.
- **Pro:** gets 2 levels of parallelism with the Workflow tool's levers.
- **Con:** you are the orchestrator across levels; no single artifact ties it together; most
  moving parts.

---

## Honest assessment

- The **directory-nesting** reading is a dead end (git anti-pattern).
- The **branch-hierarchy** reading is feasible but its cost is **convergence**, not spawning —
  and that cost grows super-linearly with levels. **2 levels is likely the practical ceiling.**
- **Worktrees buy isolation, not tokens.** If the goal is token savings, this is the wrong lever
  (see `SPEC-orchestrate-token-efficiency-2026-06-17.md`); if the goal is **conflict-free
  parallel implementation of a big, decomposable feature**, 2-level swarm is the right shape.
- Most tasks **don't need 2 levels.** The decomposition spec
  (`SPEC-orchestrate-decomposition-2026-06-18.md`) already caps agents (~4 default / ~8 release)
  — a flat swarm under that cap usually suffices. 2-level pays off only for genuinely large,
  cleanly-partitionable features.

---

## Open decisions (for the grill)

1. Is the real need **token savings** (then: wrong lever) or **parallel big-feature
   implementation** (then: 2-level swarm)?
2. If pursuing it: **extend craft `--swarm`** (Option A) or treat it as a **flow-level Workflow
   practice** (Option C)?
3. Cap the hierarchy at **2 levels** explicitly, or allow deeper?
4. Spec it now, or park as research until a real big-feature task demands it?

---

## Resolved Direction (2026-06-18)

1. **Goal = parallel big-feature implementation** (not token savings). Worktrees are accepted as
   an isolation lever; the payoff is conflict-free parallel work on a large, cleanly-partitionable
   feature — not cost.
2. **Path = extend craft `--swarm` to 2 levels** (Option A). Stay in craft's portable Task-tool
   model; reuse the existing convergence + cleanup + single-PR pipeline rather than re-implement
   it via the Workflow tool.
3. **Hard cap at 2 levels.** Convergence cost (N×M merges + per-level test gate) grows
   super-linearly; deeper hierarchies are out of scope.
4. **Worktrees stay physically flat siblings** in `~/.git-worktrees/craft/`; only the **branch
   topology** is hierarchical (`feature/big → feature/big-subX → swarm-*`). No directory nesting.
5. **Eligibility guard:** 2-level mode applies only when the ORCHESTRATE file declares sub-feature
   partitions with **non-overlapping file scopes** (overlap → reject or fall back to flat swarm,
   to avoid merge thrash). Most tasks stay flat under the decomposition spec's ~4–8 agent cap.

**Next:** write `SPEC-orchestrate-swarm-2level-2026-06-18.md` (the implementation spec:
ORCHESTRATE 2-level schema, bottom-up merge waves, per-level test gate, cleanup, failure/rollback
when a sub-level fails). Implementation = orchestrator behavior → **worktree**, not `dev`.
