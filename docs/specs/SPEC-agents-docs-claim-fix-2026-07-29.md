# SPEC: Fix Stale "Docs-Authoring Agents" Claim in `claude-code-2.1-integration.md` (+ Duplicates)

**Date:** 2026-07-29 · **Status:** DEFERRED — verified, not implemented
**Repo:** `craft`
**Origin:** A now-terminated background session left an uncommitted diff in
`docs/guide/claude-code-2.1-integration.md`, fixing a stale claim about where the
docs-authoring agents (`docs-architect`, `api-documenter`, `tutorial-engineer`) live. That diff
is already applied in the working tree (uncommitted). This SPEC is the adversarial-review +
scoping record for that fix, per the round-4 sweep's "found in passing" flag.

## Problem

`docs/guide/claude-code-2.1-integration.md` previously claimed:

```diff
-The docs-authoring agents that *do* exist (`docs-architect`, `api-documenter`,
-`tutorial-engineer` — under `agents/docs/`) are separate from `/craft:do`'s
-complexity routing; they're invoked directly by the docs commands that need them.
```

This is stale. Craft's `agents/` directory no longer contains an `agents/docs/` subdirectory at
all — it holds only `orchestrator.md` and `orchestrator-v2.md`. The three named agents (plus
`demo-engineer`, `mermaid-expert`, `reference-builder`) moved to the **folio** plugin as part of
the folio split (commit `d76f43f0d`, "wip(folio): Phase 3 T3.1 — remove folio-owned
commands/agents/skills").

## Part 1 — Adversarial Review Verdict: **CONFIRMED**

The already-applied diff's replacement text is factually accurate. Evidence:

1. **`agents/` contents** — `ls agents/` in craft returns only `orchestrator-v2.md` (36.6K) and
   `orchestrator.md` (9.6K). No `agents/docs/` subdirectory exists. Confirms the new text's claim
   ("Craft's own `agents/` directory holds only `orchestrator.md` and `orchestrator-v2.md`; it
   defines no docs-authoring agents").

2. **Folio has the three files** — `~/projects/dev-tools/folio` is a sibling directory (accessible
   from this session) with `agents/docs/` containing `docs-architect.md`, `api-documenter.md`,
   `tutorial-engineer.md` — **plus three more not named in the claim**: `demo-engineer.md`,
   `mermaid-expert.md`, `reference-builder.md`. The claim's list of three is accurate as far as it
   goes (it doesn't claim to be exhaustive), but see the note under "Residual gap" below.

3. **"Moved" vs. "never existed in craft" — genuinely moved, confirmed via git history:**
   - `git log --all --oneline --diff-filter=D -- '*docs-architect*' '*api-documenter*'
     '*tutorial-engineer*'` in craft returns exactly one deletion commit: `d76f43f0d wip(folio):
     Phase 3 T3.1 — remove folio-owned commands/agents/skills`.
   - `git show --stat d76f43f0d` confirms it deleted all six `agents/docs/*.md` files
     (`api-documenter.md`, `demo-engineer.md`, `docs-architect.md`, `mermaid-expert.md`,
     `reference-builder.md`, `tutorial-engineer.md`) from craft.
   - `git show d76f43f0d~1:agents/docs/docs-architect.md` (and the other two) resolve
     successfully, proving all three named files existed in craft immediately before that
     removal commit. This rules out the alternative "never existed in craft" reading — the
     "moved there along with the docs commands during the folio split" characterization in the
     fixed text is accurate, not just plausible-sounding.

4. **Surrounding context (lines ~241–269 of the file) does not contradict the fix.** The section
   is "Medium-Complexity Command Sequencing"; the paragraph immediately above (lines 245–251)
   already establishes that `/craft:do` chains category commands rather than dispatching to
   per-domain agents, and a nearby mermaid diagram (line 267) already references
   `/folio:docs:*` as the current home for doc building/linting. The fixed paragraph is
   consistent with, not contradicted by, this surrounding text.

**Residual gap (minor, not a factual error in the diff, but worth noting for the fix's
completeness):** the fixed text names only 3 of the 6 agents that actually moved to
`folio/agents/docs/` (omits `demo-engineer`, `mermaid-expert`, `reference-builder`). This isn't
wrong — it doesn't claim to be an exhaustive list, and the original stale text also only named
three — but a maximally-accurate fix could say "these and three others" or link to
`docs/skills-agents.md`'s full agent table. Not treated as blocking; noted as an optional
polish item in the fix below.

## Part 1, Step 5 — Duplicate Stale Claims Found Elsewhere (live docs)

A repo-wide grep (`grep -rln "docs-architect\|api-documenter\|tutorial-engineer" --include="*.md"
.`) turned up the same three agent names in many files. Most are historical/archive specs
(`docs/specs/_archive/*`, `docs/plans/ORCHESTRATE-folio-split.md`, GRILL/BRAINSTORM docs) which
are point-in-time records and correctly out of scope for a "fix" — rewriting history would be
wrong. However, **several currently-live reference docs still list these agents as if they are
craft's own**, i.e. carry the same stale-claim bug class as the one already fixed:

| File | What it says (stale) |
|---|---|
| `README.md` (lines ~432–438, ~666–672) | Lists `docs-architect`, `tutorial-engineer`, `api-documenter`, `reference-builder`, `mermaid-expert` in a craft agents table / "5 documentation agents (ported from documentation-generation plugin)" bullet list, with no folio-split note |
| `docs/skills-agents.md` (lines ~151–176) | Full "Agents" table listing all 6 (including `demo-engineer`) with craft-relative paths `agents/docs/api-documenter.md` etc. — these paths no longer exist in craft |
| `docs/REFCARD.md` (lines ~1410–1416) | Agent quick-reference table listing all 5 alongside `orchestrator`/`orchestrator-v2` with no folio note |
| `commands/hub.md` and `docs/commands/hub.md` (lines ~648–655, identical content) | Agent routing table listing all 6 as if craft-native |
| `docs/commands/arch.md` (line ~69) | "Agents: 8 (orchestrator-v2, docs-architect, etc.)" — asserts craft has 8 agents (actually 2) |
| `docs/commands/smart.md` (lines ~216–222) | Example wave-mode output invoking `docs-architect` as a craft agent |
| `docs/ARCHITECTURE-CLAUDE-CODE-2.1.md` (line ~235) | Architecture diagram node `docs-architect agent` under craft's routing map |
| `docs/guide/claude-code-2.1-guide.md` (line ~557) | JSON example with `"type": "docs-architect"` (lower-severity — sample JSON, not an assertion of current file location) |

These are **not part of this SPEC's fix scope** (out of scope per task instructions: only the one
diff, no other file touched), but they represent a materially larger duplicate-claim surface than
the single file already patched — `docs/skills-agents.md` and `commands/hub.md`/`docs/commands/hub.md`
in particular assert specific (now-wrong) craft-relative file paths, which is a stronger form of
the same bug. A future pass should treat these as a batch fix, likely via `/craft:docs:update`
or a manual sweep, updating each to either (a) remove the docs-authoring agents from craft's own
tables entirely, or (b) annotate them as "moved to folio" the same way the already-fixed
paragraph does.

## The Exact Fix (already applied, uncommitted)

No correction needed — the diff as authored by the terminated session is accurate. For the
record, the fix already present in the working tree:

```diff
-The docs-authoring agents that *do* exist (`docs-architect`, `api-documenter`,
-`tutorial-engineer` — under `agents/docs/`) are separate from `/craft:do`'s
-complexity routing; they're invoked directly by the docs commands that need them.
+Docs-authoring agents named `docs-architect`, `api-documenter`, and
+`tutorial-engineer` exist under `agents/docs/` in the **folio** plugin, not
+craft — they moved there along with the docs commands during the folio
+split. Craft's own `agents/` directory holds only `orchestrator.md` and
+`orchestrator-v2.md`; it defines no docs-authoring agents.
```

Optional polish (not required, not blocking): extend the sentence to note 3 more agents also
moved (`demo-engineer`, `mermaid-expert`, `reference-builder`), or point readers to
`docs/skills-agents.md` for the full current list — once that file itself is fixed (see Duplicate
Locations above; right now it would point to stale info).

## Explicitly Deferred

This SPEC performs **no implementation**. Per task instructions:

- `docs/guide/claude-code-2.1-integration.md` is left as-is (already correctly fixed, uncommitted,
  by the prior session — not touched further here).
- No other file (README.md, docs/skills-agents.md, docs/REFCARD.md, commands/hub.md,
  docs/commands/hub.md, docs/commands/arch.md, docs/commands/smart.md,
  docs/ARCHITECTURE-CLAUDE-CODE-2.1.md, docs/guide/claude-code-2.1-guide.md) is modified.
- Nothing is committed. The existing uncommitted diff in `claude-code-2.1-integration.md` remains
  uncommitted; this SPEC file itself is also left uncommitted for review.

## Acceptance Criteria (for a future implementation pass)

- [ ] `docs/guide/claude-code-2.1-integration.md`'s already-applied fix is committed (verify no
      further edits needed — Part 1 found it correct as-is).
- [ ] Each duplicate location in the table above is updated to either remove the docs-authoring
      agents from craft-scoped tables or annotate them as folio-owned, consistent with the fixed
      paragraph's phrasing.
- [ ] `docs/skills-agents.md` and `commands/hub.md`/`docs/commands/hub.md`'s file-path columns no
      longer point at nonexistent `agents/docs/*.md` paths in craft.
- [ ] A follow-up repo-wide grep for `docs-architect\|api-documenter\|tutorial-engineer` in
      `--include="*.md"` shows only folio-annotated or historical/archived references remaining.
- [ ] Any docs-count/link validators (`./scripts/validate-counts.sh`,
      `./scripts/docs-staleness-check.sh`) pass after the batch fix.
