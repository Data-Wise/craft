# SPEC: Two-Level Swarm — `--swarm=2`

**Status:** ready for implementation (spec-only; implementation deferred to a worktree)
**Created:** 2026-06-18
**From:** `RESEARCH-hierarchical-worktrees-2026-06-18.md` (resolved direction)
**Author:** dt + Claude
**Relationship:** extends craft `--swarm` (`commands/orchestrate.md` Swarm Mode). Does **not**
change 1-level behavior or any default.

---

## Goal

Let `/craft:orchestrate` run a **2-level swarm** for a large, cleanly-partitionable feature:
top feature → parallel sub-features → each its own swarm of agents, converged bottom-up into one
PR. **1 level stays the default; 2 levels is explicit opt-in.**

**Non-goals:** depth > 2 (convergence cost grows super-linearly); token savings (worktrees are
isolation only); the Workflow tool (1-level nesting cap — out, per the research note).

---

## Interface — `--swarm` takes an optional level

`--swarm` gains an **optional integer value**, default **1** (backward-compatible):

```bash
/craft:orchestrate <task> --swarm        # 1 level (UNCHANGED default behavior)
/craft:orchestrate <task> --swarm=1      # explicit 1 level (same as above)
/craft:orchestrate <task> --swarm=2      # two levels
/craft:orchestrate <task> --swarm=3      # REJECTED — "max swarm level is 2"
```

- Bare `--swarm` (no value) = `1` — existing scripts/aliases keep working untouched.
- Value `> 2` or non-integer → **reject with a clear message**, do not silently clamp.
- `--swarm=2` requires a 2-level ORCHESTRATE file (below); absent → reject (consistent with
  1-level swarm already requiring an ORCHESTRATE file).
- `--dry-run` previews the full 2-level branch/worktree tree without spawning.

### Frontmatter change (`commands/orchestrate.md`)

The `swarm` argument changes from boolean to **optional-valued** (default `1`). Update the
arguments table, Usage block, and the Swarm Mode section. This is the only command-surface change.

---

## Branch & Worktree Topology (flat siblings, hierarchical branches)

```
dev
 └─ feature/swarm-<task>                  ← TOP convergence branch
     ├─ feature/swarm-<task>-subA         ← sub-convergence branch (off top)
     │   ├─ swarm-<task>-subA-1  (worktree off subA)
     │   └─ swarm-<task>-subA-2  (worktree off subA)
     └─ feature/swarm-<task>-subB         ← sub-convergence branch (off top)
         ├─ swarm-<task>-subB-1  (worktree off subB)
         └─ swarm-<task>-subB-2  (worktree off subB)
```

All worktrees are **physical siblings** in `~/.git-worktrees/<proj>/`; only the **branch
topology** nests. Sub-convergence branches are branched from the top convergence branch so the
final merge is clean.

---

## ORCHESTRATE File — 2-Level Schema

1-level swarm uses one `## Swarm Configuration` table. 2-level adds a **sub-feature grouping**.
Each sub-feature has its own agent table; **file scopes must not overlap across sub-features**
(the eligibility guard).

```markdown
## Swarm Configuration (level 2)

### Sub-feature: subA — "data layer"
| Agent | Worktree | Focus | Files |
|-------|----------|-------|-------|
| model | swarm-subA-model | schema | src/models/ |
| repo  | swarm-subA-repo  | queries | src/repo/ |

### Sub-feature: subB — "api layer"
| Agent | Worktree | Focus | Files |
|-------|----------|-------|-------|
| routes | swarm-subB-routes | endpoints | src/api/ |
| auth   | swarm-subB-auth   | middleware | src/auth/ |
```

**Eligibility guard:** if any file scope appears in two sub-features → **reject** (or, with a
flag, **fall back to flat 1-level swarm**) to avoid cross-sub merge thrash.

---

## Execution Flow

```text
/craft:orchestrate --swarm=2 "build X"

1. Parse ORCHESTRATE 2-level config; validate non-overlapping scopes (else reject/fallback).
2. Create TOP convergence branch feature/swarm-X from dev.
3. For each sub-feature S:
   a. Create sub-convergence branch feature/swarm-X-S from feature/swarm-X.
   b. For each agent in S: git worktree add ~/.git-worktrees/<proj>/swarm-X-S-<agent>
      -b swarm-X-S-<agent> feature/swarm-X-S
   c. Launch S's agents in parallel (each in its worktree).
   d. Wait for S's agents; merge swarm-X-S-* → feature/swarm-X-S; run tests (per-level gate).
      └─ if a sub-feature's test gate fails → STOP that sub-feature, report; do not merge it up.
4. After all sub-features pass: merge each feature/swarm-X-S → feature/swarm-X (wave order).
5. Run full tests on feature/swarm-X (top gate).
6. Create one PR feature/swarm-X → dev.
7. Clean up all swarm-X-S-* worktrees (and sub-branches per policy).
```

Sub-features run in parallel with each other (level-1 parallelism); agents within a sub-feature
run in parallel (level-2 parallelism).

---

## Failure / Rollback

- **Agent fails** → its sub-feature's merge is incomplete; report which agent/worktree, leave the
  worktree for inspection (don't auto-delete a failed agent's work).
- **Sub-feature test gate fails** → that sub-feature is **not merged into the top**; other passing
  sub-features still converge; the run reports a partial result and the failed sub-branch is kept.
- **Top test gate fails** → no PR; top convergence branch kept for manual fix.
- **No partial PRs:** a PR is created only when the top gate passes (configurable: `--allow-partial`
  could PR only the passing sub-features — out of scope for v1).

---

## Default & Compatibility

- **`--swarm` (bare) and `--swarm=1` are byte-for-byte the existing 1-level behavior.** No default
  changes anywhere. Only `--swarm=2` exercises the new path.
- Interacts with the decomposition spec: sub-feature agent counts still obey the mode-scaled soft
  cap (`SPEC-orchestrate-decomposition-2026-06-18.md`) **per sub-feature**.

---

## Tests

- Arg parsing: bare `--swarm`→1; `--swarm=1`→1; `--swarm=2`→2; `--swarm=3`/`--swarm=x`→reject.
- Overlap guard: overlapping scopes → reject (and fallback path when flagged).
- Topology: 2-level branches created off the correct parents; worktrees are siblings on disk.
- Convergence: bottom-up merge order; per-level test gate; sub-failure does not merge up.
- Cleanup: all `swarm-*` worktrees removed on success.
- Dry-run: prints the full tree, spawns nothing.

---

## Branch Routing

- **This spec:** `.md` on `dev` (dev-safe).
- **Implementation:** `commands/orchestrate.md` arg change + orchestrator convergence logic =
  feature behavior → **worktree** (`feature/orchestrate-swarm-2level`). Not started.

---

## Dependencies & Sequencing

1. **Decomposition spec** (`SPEC-orchestrate-decomposition-2026-06-18.md`) — the mode-scaled
   agent soft cap applies **per sub-feature** here. Land decomposition first (or together) so a
   2-level run can't blow past the cap once per sub-feature.
2. **Token-efficiency spec** (`SPEC-orchestrate-token-efficiency-2026-06-17.md`) — orthogonal.
   Worktrees are isolation, not a token lever; 2-level swarm neither helps nor hurts the token
   work. Phase-0 token markers should record `swarm_level` for attribution if both ship.
3. **Research note** (`RESEARCH-hierarchical-worktrees-2026-06-18.md`) — the rationale and the
   rejected alternatives (directory nesting, Workflow-tool path, depth > 2) live there; this
   spec is its resolved-direction realization.
4. **Independent of** the `:workflow` default flip — 2-level swarm is a fan-out-path feature.

---

## Documentation & Discoverability

- Update `commands/orchestrate.md`: arguments table (`swarm` boolean → optional level, default
  `1`), Usage block (`--swarm=2`), Swarm Mode section (2-level topology + ORCHESTRATE schema),
  and the worktree-types table (note the sub-convergence branch).
- `--swarm --help` / dry-run output shows the level and, at `=2`, the full branch/worktree tree.
- CHANGELOG entry on implementation with the backward-compat note (`bare --swarm == --swarm=1`).
- Cross-link the research note and the decomposition spec from the Swarm Mode docs.
