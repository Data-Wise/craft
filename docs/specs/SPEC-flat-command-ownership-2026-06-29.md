# craft: Flat-Command Ownership Spec (Model A adoption)

**Date:** 2026-06-29
**Status:** Planning
**Branch:** `.md` edits to existing files are dev-OK. Recommend batching into
`feature/flat-command-ownership` for coherence with the broader rollout.
**Initiative:** Flat-Command Ownership — distinct from `SPEC-refactor-namespace-2026-06-29.md`
**Owner spec:** `opencode-resources/docs/specs/SPEC-flat-command-ownership-2026-06-29.md`

---

## Context

This spec makes craft an **adopter** of Model A flat-command ownership. The owner spec
(opencode-resources) defines the `hub` behavioral contract; this spec seeds that contract into
craft's `hub.md` and records the multi-colon namespacing risk flagged during the CC audit.

**craft's flat-command reality (relevant to this initiative):**

| Command | Type | Status |
|---|---|---|
| `hub` | True flat command (`commands/hub.md`) | Adopt contract header (this spec) |
| `check`, `do`, `grill`, `quota`, etc. | Craft-specific flat commands | No shared contract — domain-specific |
| `git:worktree` (namespace.json key) | Undocumented multi-colon pattern | Flag as risk (Task 3) |

---

## Tasks

### Task 1 — Adopt the hub contract header

File: `commands/hub.md`

Add the following comment header as the **first lines** of the file (before any `#` heading):

```markdown
<!-- CONTRACT: hub v1.0 — opencode-resources/contracts/hub.md
     Required sections: Quick Start, Command Map, When to Use Each, Recommended Next Step
     Output format: table + prose, max 500 tokens
-->
```

Then verify the file already contains (or add if missing) the four required sections:

1. Quick Start
2. Command Map
3. When to Use Each
4. Recommended Next Step

The content stays craft-specific — the contract governs structure, not content.

### Task 2 — Bundled doc-edit: namespace spec Impl-Note #5

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

- Owner spec: `opencode-resources/docs/specs/SPEC-flat-command-ownership-2026-06-29.md`
- Research audit: `~/.claude/plans/twinkly-inventing-mango.md`
- Namespace refactor (separate initiative): `docs/specs/SPEC-refactor-namespace-2026-06-29.md`
