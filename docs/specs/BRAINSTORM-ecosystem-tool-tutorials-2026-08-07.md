# BRAINSTORM: Ecosystem Tool Tutorials

**Date:** 2026-08-07 · **Depth:** default · **Focus:** ops
**Branch:** dev · **Categories:** tech, risks, timeline

## Origin

Follows the `/craft:check --for post-merge` pass on PR #328, which caught
`docs/tutorials/TUTORIAL-opencode-plugins.md` missing from `mkdocs.yml` nav
(fixed in `81b794a85`). That file documents OpenCode's third-party plugin
setup as a cheat-sheet — not a craft feature, but useful tooling knowledge
kept alongside craft's own docs. This brainstorm asks the natural follow-up:
**does codex, or any other installed Claude Code plugin, deserve the same
treatment?**

## Context Scan

- **27 plugins installed** (`~/.claude/plugins/installed_plugins.json`),
  beyond craft itself. Full inventory pulled at brainstorm time.
- **Zero have a dedicated tutorial** in `docs/tutorials/`. A grep pass found
  apparent hits for "remember", "skill-creator", "feature-dev", and
  "explanatory" — all confirmed coincidental word matches (e.g. "remember"
  appearing in `testing-quickstart.md` prose), not real coverage.
- **Data-Wise's own tools are explicitly out of scope** (user decision,
  mid-brainstorm): `craft`, `folio`, `rforge`, `savant`, `scholar`,
  `himalaya-mcp` (all `@local-plugins`) already have their own repos and
  docs — duplicating that here would be the kind of redundant-surface
  problem `doc-update-currency-check.md` warns against.
- **codex@openai-codex** has real setup complexity: it runs a persistent
  broker process (`app-server-broker.mjs`) with a Unix socket per cwd,
  confirmed live in this session's own `ps aux` output (two brokers running
  for `research/product of three` and `dev-tools/savant`). It's also wired
  into craft's own agent list as `codex:codex-rescue` — "use when Claude
  Code is stuck, wants a second implementation pass, or should hand off a
  substantial coding task to Codex."

## Locked Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Scope: which tools | **Evidence-of-use only**, excluding Data-Wise's own plugins. Candidates selected by two signals: visible setup complexity (config, auth, broker/sandbox model) AND actual use this session/repo — not an exhaustive sweep of all 27. |
| 2 | Tutorial format | **Cheat-sheet style**, matching `TUTORIAL-opencode-plugins.md`'s precedent: what it does, config snippet, 1-2 gotchas per tool. Not a full step-by-step walkthrough. |
| 3 | Nav placement | **New top-level mkdocs section** (sibling to "🚀 Getting Started" and "📖 Guides & Tutorials"), not nested inside Specialized Features — signals these are external tooling notes, not craft's own feature docs. |
| 4 | First-pass count | **8 tools** (revised up from 6 mid-brainstorm — user added Dropbox and Agent Skills after seeing the initial candidate table). Depth over breadth for v1; more can be added later following the same template. |
| 5 | Cross-links to own tools | **None.** Fully excluded, no "see also" list — those tools' docs live in their own repos, and a cross-link here would need to be kept in sync from both sides. |

## Candidate Tools (evidence-of-use pass)

| Tool | Plugin ID | Why it's a candidate | Suggested tutorial name |
|---|---|---|---|
| Codex | `codex@openai-codex` | Broker/sandbox process model, live in this session's `ps aux`; wired as `codex:codex-rescue` agent in craft's own ecosystem | `TUTORIAL-codex-plugin.md` |
| Remember | `remember@claude-plugins-official` | `.remember/` rolling-log system, actively injected into this very session's context (`now.md`/`recent.md`/`archive.md`) | `TUTORIAL-remember-plugin.md` |
| i-have-adhd | `i-have-adhd@i-have-adhd` | ADHD-mode ruleset active this entire session via `SessionStart:compact` hook; non-obvious toggle/config (`~/.claude/.i-have-adhd`) | `TUTORIAL-adhd-mode-plugin.md` |
| Token Optimizer | `token-optimizer@token-optimizer` | Large MCP tool surface (60+ `smart_*` tools) referenced this session via a "Consider the smart_read MCP tool" tip on a large-file Read | `TUTORIAL-token-optimizer-plugin.md` |
| Security Guidance | `security-guidance@claude-plugins-official` | Hook actively running (`security_reminder_hook.py`, confirmed live in `ps aux`); non-obvious hook-vs-skill split worth explaining | `TUTORIAL-security-guidance-plugin.md` |
| Claude HUD | `claude-hud@claude-hud` | Status-line/dashboard process running live (`ps aux`); setup likely involves shell/statusline config, a common friction point | `TUTORIAL-claude-hud-plugin.md` |
| Dropbox | `dropbox@claude-plugins-official` | Large live MCP tool surface (browse/search/share-link/file-request/move-copy-delete); OAuth-style account auth is a real setup step | `TUTORIAL-dropbox-plugin.md` |
| Agent Skills | `agent-skills@addy-agent-skills` | Supplies 4 of this session's own available agents (`code-reviewer`, `security-auditor`, `test-engineer`, `web-performance-auditor`) — used this session's own `code-review` skill invocations | `TUTORIAL-agent-skills-plugin.md` |

## Why This Shape (not the alternatives)

- **Not exhaustive-27:** most installed plugins (microsoft-docs,
  frontend-design, preset-cli-skills, storymap-skill, explore,
  chrome-devtools-mcp, playwright, netlify-skills, hookify,
  feature-dev, skill-creator, explanatory/learning-output-style) have no
  observed-use evidence in this session or repo history. Writing tutorials
  for untested tools risks documenting a setup that was never actually
  verified — better to expand the set later, per-tool, once real usage
  exists. (Dropbox and Agent Skills were initially in this "no evidence"
  bucket too, but both have concrete usage evidence — see the candidate
  table — so they moved to the first-pass set on review.)
- **Not nested under Specialized Features:** that group is already ~60
  entries deep (see `docs/skills-agents.md`'s own count-cascade concerns).
  A new top-level section keeps external-tool docs discoverable without
  growing an already-large nav group further.
- **Not a full walkthrough per tool:** `TUTORIAL-opencode-plugins.md`
  proved the cheat-sheet format works for this exact "third-party tool,
  personal setup notes" use case — reuse the proven shape rather than
  inventing a heavier one.

## Risks / Open Questions

- **Staleness risk:** plugin versions/configs change (codex's broker model,
  in particular, is the kind of implementation detail that could shift
  under an upstream update). No dedicated staleness check exists for this
  new section the way `docs-staleness-check.sh` covers craft's own
  command/skill counts — worth a follow-up decision on whether these need
  periodic review, or are accepted as point-in-time snapshots like the
  OpenCode tutorial already is.
- **Section-naming collision:** "Ecosystem" is also used elsewhere in this
  workspace (`~/projects/dev-tools/ECOSYSTEM.md` describes the
  atlas/flow-cli hub-and-spoke architecture) — a different, unrelated
  "ecosystem." Pick the new mkdocs section title carefully to avoid reader
  confusion between the two uses of the word.
- **Eight tools is a first pass, not a ceiling** — feature-dev, hookify,
  playwright/chrome-devtools-mcp, and skill-creator were the next tier
  considered and explicitly deferred, not rejected.

## Test-Plan Scaffold (default-on)

Tier inferred: **docs-only, no new parser/script/command** → `e2e` + `dogfood` tier.

- E2E: after adding the tutorials + nav section, re-run
  `./scripts/docs-staleness-check.sh` — Phase 6 (Nav Completeness) must stay
  GREEN for all new files.
- Dogfood: `python3 -m pytest tests/ -k "docs or staleness or nav"` — no
  existing test should need modification (this doesn't touch counts,
  commands, or skills — pure content addition).
- Non-goal test: confirm none of the 6 new tutorial files reference a
  craft-internal command/skill path that doesn't exist (a stale-ref check,
  same class of bug the nav-gap itself was).

## Documentation Scaffolding (default-on)

Doc-impact score (via `skills/orchestration/references/doc-impact-rubric.md`,
threshold ≥3):

- [x] Guide/tutorial — this BRAINSTORM's entire output IS 8 new tutorial
      files (score ≥3: new user-facing content, no prior art for any of them)
- [x] Nav/REFCARD entry — new top-level mkdocs section needs a name;
      candidates: "🔌 Ecosystem Tools", "🧰 Companion Tools", "🔗 Related
      Plugins" (avoiding "Ecosystem" alone per the naming-collision risk
      above)
- [ ] Demo — N/A, score <3 (cheat-sheet format, not a visually-driven
      feature)
- [ ] Mermaid diagram — N/A, score <3 (no architecture to diagram; each
      tool's cheat-sheet is flat reference content)

## Next Steps

Recommended: this scope is concrete enough (8 named tools, format decided,
nav placement decided) to skip a `/craft:grill` pass and go straight to
writing the 6 tutorial files + the new mkdocs nav section — there's no
unresolved design branch here, just content to produce. If you'd rather
lock the section name and staleness-check question first, `/craft:grill`
on this doc would resolve those two open items before writing starts.
