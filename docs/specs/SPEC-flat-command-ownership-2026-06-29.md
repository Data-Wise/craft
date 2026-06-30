# craft: Flat-Command Ownership Spec (Model A **owner**)

**Date:** 2026-06-29
**Status:** Planning
**Branch:** `feature/flat-command-ownership` — creating `contracts/hub.md` is a new file;
branch-guard BLOCKS new files on dev.
**Initiative:** Flat-Command Ownership — distinct from `SPEC-refactor-namespace-2026-06-29.md`

---

## Context

craft **owns** the `hub` behavioral contract under Model A. The contract lives in
`craft/contracts/hub.md`; adopters (savant, scholar) copy the header and implement locally.
opencode-resources hosts the drift check (`check-drift.js` 6th check reads craft's contract).

**craft's flat-command reality (relevant to this initiative):**

| Command | Type | Status |
|---|---|---|
| `hub` | True flat command (`commands/hub.md`) | Own contract + carry header (this spec) |
| `check`, `do`, `grill`, `quota`, etc. | Craft-specific flat commands | No shared contract — domain-specific |
| `git:worktree` (namespace.json key) | Undocumented multi-colon pattern | Flag as risk (Task 3) |

---

## Tasks

### Task 1 — Create `contracts/hub.md`

Create `contracts/hub.md` in the craft repo root. Content:

```markdown
# CONTRACT: hub v1.0

**Governs:** `hub` flat command across CC plugins
**Owner:** craft
**Adopters:** craft, savant, scholar  |  **Opt-outs:** rforge (no hub command)

## Required sections

Every implementing plugin's `hub.md` MUST contain these four sections (any order):

1. **Quick Start** — 2-4 line summary of the plugin's purpose and the 1-2 commands to run first
2. **Command Map** — table or structured list of all commands (name | purpose | when to use)
3. **When to Use Each** — disambiguation guidance; which command for which situation
4. **Recommended Next Step** — single suggested action to take after reading

## Output format

- Table + prose mix
- Max 500 tokens total output
- Lead with Quick Start, end with Recommended Next Step

## Contract header (copy verbatim into implementing files)

Each plugin's `hub.md` opens with this header, version bumped when this contract changes:

    <!-- CONTRACT: hub v1.0 — craft/contracts/hub.md
         Required sections: Quick Start, Command Map, When to Use Each, Recommended Next Step
         Output format: table + prose, max 500 tokens
    -->

## Drift detection

    grep -r "CONTRACT: hub" ~/projects/dev-tools/*/commands/
    grep -r "CONTRACT: hub" ~/projects/dev-tools/*/src/plugin-api/commands/

Any file referencing a version older than v1.0 needs updating.

## Changelog

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-06-29 | Initial contract — 4 required sections, 500-token cap |
```

### Task 2 — Seed the contract header into `commands/hub.md`

File: `commands/hub.md`

Add the following comment header as the **first lines** of the file (before any `#` heading):

```markdown
<!-- CONTRACT: hub v1.0 — craft/contracts/hub.md
     Required sections: Quick Start, Command Map, When to Use Each, Recommended Next Step
     Output format: table + prose, max 500 tokens
-->
```

Then verify the file already contains (or add if missing) the four required sections:

1. Quick Start
2. Command Map
3. When to Use Each
4. Recommended Next Step

### Task 3 — Bundled doc-edit: namespace spec Impl-Note #5

File: `docs/specs/SPEC-refactor-namespace-2026-06-29.md`

Append as **item 5** at the end of the `## Implementation Notes` section (currently ends at item 4
= the "savant/rforge/scholar copy this schema" note):

```markdown

5. **`git:worktree` relies on undocumented multi-colon plugin namespacing — flag as risk.** The
   `"git:worktree"` namespace.json entry implies a `/craft:git:worktree` invocation. Multi-level
   (multi-colon) namespacing is documented for personal/project skills (innermost directory name)
   but **not for plugins** — Claude Code docs (plugins.md, skills.md, checked 2026-06-29) describe
   only single-level `/plugin:command`. Before shipping, verify empirically (install a throwaway
   plugin with a nested `skills/git/worktree/` and observe whether it exposes as `/craft:worktree`
   or `/craft:git:worktree`); if unsupported, fall back to a flat key (`git-worktree`) or a `routes`
   sub-action under a flat `git` command. See `~/.claude/plans/twinkly-inventing-mango.md`.
```

---

## Verification

```bash
# From craft repo root:
# 1. Confirm contract header is present
head -5 commands/hub.md
# Should show the <!-- CONTRACT: hub v1.0 --> header

# 2. Confirm namespace spec Impl-Note #5 is present
grep -n "git:worktree\|multi-colon" docs/specs/SPEC-refactor-namespace-2026-06-29.md

# 3. Spot-check MD031/MD032 (pre-commit hook catches these)
git diff docs/specs/SPEC-refactor-namespace-2026-06-29.md
git diff commands/hub.md
```

---

## Cross-references

- Adopter specs: `savant/docs/specs/SPEC-flat-command-ownership-2026-06-29.md`,
  `scholar/docs/specs/SPEC-flat-command-ownership-2026-06-29.md`
- Drift check host: `opencode-resources/docs/specs/SPEC-flat-command-ownership-2026-06-29.md`
  (check-drift.js 6th check reads `craft/contracts/hub.md`)
- Research audit: `~/.claude/plans/twinkly-inventing-mango.md`
- Namespace refactor (separate initiative): `docs/specs/SPEC-refactor-namespace-2026-06-29.md`
