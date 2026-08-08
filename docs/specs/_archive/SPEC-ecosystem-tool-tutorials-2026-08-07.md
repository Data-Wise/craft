# SPEC: Ecosystem Tool Tutorials (Cheat-Sheet Series)

**Date:** 2026-08-07 · **Status:** Ready to implement
**Source:** [`BRAINSTORM-ecosystem-tool-tutorials-2026-08-07.md`](BRAINSTORM-ecosystem-tool-tutorials-2026-08-07.md)
**Repo:** `craft`

## Problem

craft's docs already carry one cheat-sheet-style tutorial for a third-party
tool that isn't a craft feature: `docs/tutorials/TUTORIAL-opencode-plugins.md`
(added 2026-08-01, its `mkdocs.yml` nav entry fixed this session in
`81b794a85`). That precedent raised the obvious question: 27 other Claude
Code plugins are installed alongside craft, and none of them have equivalent
coverage. Several have real, non-obvious setup — broker processes, OAuth
flows, hook wiring — that's currently undocumented anywhere in this repo.

## Scope

### In scope

8 tools, selected by evidence-of-use (session/repo evidence, not a
blind sweep of all 27 installed plugins):

| Tool | Plugin ID | Tutorial file |
|---|---|---|
| Codex | `codex@openai-codex` | `docs/tutorials/TUTORIAL-codex-plugin.md` |
| Remember | `remember@claude-plugins-official` | `docs/tutorials/TUTORIAL-remember-plugin.md` |
| i-have-adhd | `i-have-adhd@i-have-adhd` | `docs/tutorials/TUTORIAL-adhd-mode-plugin.md` |
| Token Optimizer | `token-optimizer@token-optimizer` | `docs/tutorials/TUTORIAL-token-optimizer-plugin.md` |
| Security Guidance | `security-guidance@claude-plugins-official` | `docs/tutorials/TUTORIAL-security-guidance-plugin.md` |
| Claude HUD | `claude-hud@claude-hud` | `docs/tutorials/TUTORIAL-claude-hud-plugin.md` |
| Dropbox | `dropbox@claude-plugins-official` | `docs/tutorials/TUTORIAL-dropbox-plugin.md` |
| Agent Skills | `agent-skills@addy-agent-skills` | `docs/tutorials/TUTORIAL-agent-skills-plugin.md` |

Each tutorial follows `TUTORIAL-opencode-plugins.md`'s cheat-sheet shape:
what the tool does, a config/setup snippet, 1-2 known gotchas — written
**ADHD-friendly** (per `i-have-adhd`'s active ruleset this session): lead
with the setup command/action, numbered steps for multi-step setup, cap
each gotcha list at 5, no preamble/recap prose.

Plus: a new labeled subsection under the existing "📖 Guides & Tutorials"
section (revised from the BRAINSTORM's original "new top-level section"
plan — see Revision below), holding all 8 entries.

**Tooling:** use folio's `nav-sync` skill (`skills/docs/navigation/` in the
folio repo — "new-page scaffolding with auto-nav insertion") to create each
page and insert its nav entry, rather than hand-editing `mkdocs.yml` and
authoring each file's frontmatter/structure manually.

### Revision: nav placement (post-BRAINSTORM correction)

The BRAINSTORM recommended a **new top-level** mkdocs section. Checking
`nav-sync`'s own stated constraint (**≤7 top-level sections, ≤3 nesting
depth** — "ADHD-friendly nav reorganization" is literally in its
description) against craft's current `mkdocs.yml` found **7 real top-level
sections already** (Getting Started, Guides & Tutorials, Teaching, Commands
& Reference, Cookbook & Examples, Reference & Architecture, For
Contributors). Adding an 8th would violate the same ADHD-friendly-nav rule
this SPEC is otherwise trying to satisfy. **Corrected decision:** nest as a
new subsection under "📖 Guides & Tutorials" (sibling to "Specialized
Features," where `TUTORIAL-opencode-plugins.md` itself already landed),
named "Ecosystem Tool Cheat Sheets" — pick a different name only if it
collides with something on read.

### Explicitly out of scope

- **Data-Wise's own plugins** (`craft`, `folio`, `rforge`, `savant`,
  `scholar`, `himalaya-mcp` — all `@local-plugins`). These have their own
  repos and docs; duplicating coverage here is out of scope, and no
  cross-link back to them is added either (BRAINSTORM decision 5).
- **The other ~19 installed plugins** with no observed-use evidence
  (microsoft-docs, frontend-design, preset-cli-skills, storymap-skill,
  explore, chrome-devtools-mcp, playwright, netlify-skills, hookify,
  feature-dev, skill-creator, explanatory/learning-output-style, etc.) —
  deferred to a future pass, not rejected.
- **A staleness/freshness check** for this new section. No mechanism like
  `docs-staleness-check.sh`'s count-cascade applies here (these aren't
  craft's own counts) — these are accepted as point-in-time snapshots, same
  as the OpenCode tutorial already is.

## Open Question (resolved)

**Nav section title/placement.** Superseded by the Revision above: nesting
under "📖 Guides & Tutorials" as "Ecosystem Tool Cheat Sheets" sidesteps the
top-level naming-collision risk entirely (the collision was specifically
with a top-level `ECOSYSTEM.md` concept; a nested subsection heading doesn't
compete with that the same way). No further confirmation needed unless the
name reads badly once the section exists alongside its siblings.

## Acceptance Criteria

- [ ] All 8 files listed in Scope exist under `docs/tutorials/`, each
      containing: a one-paragraph "what it does" (action-first, no
      preamble), a config/setup snippet (real command or config block, not
      a placeholder), and at least one named gotcha (≤5 gotchas per file).
- [ ] `mkdocs.yml` has an "Ecosystem Tool Cheat Sheets" subsection nested
      under "📖 Guides & Tutorials" (sibling to "Specialized Features"),
      listing all 8 new files — created via folio's `nav-sync` skill, not a
      hand-edit.
- [ ] Nesting stays within `nav-sync`'s own ≤3-depth constraint (Guides &
      Tutorials → Ecosystem Tool Cheat Sheets → file = depth 2, within
      budget).
- [ ] After all 8 pages are scaffolded, run `nav-sync` a second time in its
      drift-detection mode ("sync mkdocs navigation" / "fix orphan docs")
      as a final pass — confirms nothing scaffolded outside the skill (or
      edited afterward) left an orphaned page or a stale nav entry.
- [ ] `./scripts/docs-staleness-check.sh` reports Phase 6 (Nav Completeness)
      GREEN after the section is added — every new file is in the nav, no
      orphans.
- [ ] No new file references a craft-internal command/skill path that
      doesn't exist — verified by a stale-ref grep pass across all 8 new
      files (same class of check `docs-staleness-check.sh` Phase 9 runs for
      craft's own docs).
- [ ] `python3 -m pytest tests/ -k "docs or staleness or nav"` passes with
      no existing test needing modification — this is pure content
      addition, not a counts/commands/skills change.

## Test-Plan (from BRAINSTORM, unchanged)

Tier: `e2e` + `dogfood` (docs-only, no new parser/script/command).

- E2E: `./scripts/docs-staleness-check.sh` — Phase 6 GREEN post-change.
- E2E: `nav-sync` drift-detection pass (second run, post-scaffold) — zero
  orphans reported.
- Dogfood: `python3 -m pytest tests/ -k "docs or staleness or nav"`.
- Non-goal test: grep all 8 new files for dead craft-internal references.

## Next Steps

Ready for `/craft:plan docs/specs/SPEC-ecosystem-tool-tutorials-2026-08-07.md`
to generate an ORCHESTRATE breakdown (8 tutorials + 1 nav edit — small
enough to also just write directly without a full orchestrate-dispatch, if
preferred). Resolve the nav-title Open Question first either way.
