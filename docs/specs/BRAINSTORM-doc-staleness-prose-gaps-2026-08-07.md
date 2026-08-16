# BRAINSTORM: Doc-Staleness Prose Gaps (closing what count-consistency misses)

**Date:** 2026-08-07 · **Depth:** deep · **Focus:** ops
**Branch:** dev · **Categories:** req, existing, tech, risks, scope, success

## Origin

Seed request (refined via `--refine`): research how doc-staleness detection is handled
elsewhere (other Claude Code plugin/skill projects, adjacent coding-agent ecosystems), then
compare against craft's own tooling to find patterns worth adopting.

Directly triggered by two bugs found and fixed *this session*, both while
`docs-staleness-check.sh` reported GREEN:

- `docs/REFCARD.md`'s quick-reference box had the correct version **number** (4.5.0 —
  `bump-version.sh`'s literal-string target) but a stale release **date** (2026-07-17,
  actually v4.1.0's) and a stale highlight line (still describing v4.1.0's `/craft:restore`,
  not v4.5.0's repo-triage skill).
- `docs/skills-agents.md`'s TL;DR line said "8 specialized agents" two lines above its own
  correct "2 specialized agents" — stale since the v4.0.0 folio split, never caught.

Both are **free prose**, not the structured badges/counts `docs-staleness-check.sh`'s
count-consistency phase (Phase 7) anchors on. The gate did its job on every surface it
watches; these two just weren't watched surfaces.

## Context Scan

- **No existing spec on this topic.** `find`/`grep` across `docs/specs/` for
  `staleness`/`drift`/`doc-track` found nothing prior — genuinely new ground for craft,
  despite already having the most mature doc-tooling stack of the ~25 dev-tools sibling repos.
- **Existing tooling inventory** (all already in craft, none of it is a green-field build):
  - `scripts/docs-staleness-check.sh` (35.7K) — 4-phase gate: nav completeness, count
    consistency, skill/agent/cmd coverage, cross-doc freshness. Anchors on specific
    badge/count patterns (`version-X.Y.Z`, `N commands`, `N skills`), not arbitrary prose.
  - `scripts/doc-coverage-check.sh` — blocks release on missing REFCARD rows / mkdocs nav
    entries for new commands.
  - `utils/claude_md_sync.py` — CLAUDE.md-specific drift detector (documented-command
    existence, error/warning/info tiers); this session's `/craft:done` run caught 1 real
    error (`/craft:done` still referenced, file deleted) via this tool, not the staleness
    gate.
  - `utils/docs_detector.py` / `utils/docs_update_orchestrator.py` — semantic doc-update
    orchestration for `/craft:docs:update`.
  - None of these do free-prose semantic staleness checking today — every one of them
    matches a structured pattern (a badge, a count line, a declared command name).

## External Research (WebSearch, 2026-08-07)

Two search passes: general doc-drift-in-CI practice, and Claude-Code-specific tooling.

**General CI doc-drift practice:**

- **[fiberplane/drift](https://github.com/fiberplane/drift)** — anchors markdown docs to
  source code via tree-sitter + git; on a supported language, hashes a normalized AST
  fingerprint (node kinds + token text) and flags the doc when the anchored code changes.
  Closest match to craft's own `bump-version.sh`-touches-N-files pattern, but source-code-anchored
  rather than count/version-anchored — not directly reusable (craft's staleness is prose-vs-metadata,
  not prose-vs-code).
- **[dosu.dev: doc freshness scoring](https://dosu.dev/blog/score-documentation-freshness-in-ci)** —
  a 0–100 freshness signal from three deterministic checks plus a semantic layer for edge
  cases; the "deterministic checks first, semantic layer only for what's left" shape is the
  most directly transferable idea here.
- **[jbrockSTL/doc-drift](https://github.com/jbrockSTL/doc-drift)** — LLM-in-CI stale-doc
  catcher on every PR via GitHub Actions; cost-controlled via label-gating, cron batching, and
  path filters rather than running on every push.
- **[Vale](https://vale.sh/)** — YAML-rule prose linter (existence/repetition/spelling
  extension points); proves custom prose-pattern rules are a well-trodden, low-tooling-cost
  approach — closer in spirit to extending `docs-staleness-check.sh`'s existing grep-based
  phases than adopting a new dependency.

**Claude Code / coding-agent specific:**

- **[dosu.dev: catching doc drift with Claude Code + GitHub Actions](https://dosu.dev/blog/how-to-catch-documentation-drift-claude-code-github-actions)** —
  triggers Claude Code itself as the drift-detector in CI, reading diffs and flagging
  affected docs semantically.
- **[dev.to: "How Claude Skills Replaced Our Documentation"](https://dev.to/magnusrodseth/how-claude-skills-replaced-our-documentation-emi)** —
  reframes skills as living docs: traditional docs rot because they're write-once/read-rarely,
  but a skill the agent actually executes gets exercised constantly, so drift surfaces
  immediately. Doesn't apply directly to REFCARD/skills-agents.md (reference docs, not
  executable skill bodies) but validates craft's own pattern of thin command-shims pointing
  at canonical skill files (already this repo's convention).

**Takeaway:** nothing found is a drop-in replacement for `docs-staleness-check.sh` — the
external tools solve *code*-anchored drift (source changed, doc didn't) or run a full LLM
pass per PR (cost/latency for a check craft already does deterministically in seconds). The
one directly transferable idea is Vale/dosu's "deterministic pattern checks first, escalate
only what's left" shape — which is exactly what today's bugs argue for: add deterministic
prose-pattern checks for the *specific* phrase shapes that already bit us, not a general
semantic-diff engine.

## Locked Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Trigger for this work | **Both** — the gate missed real bugs today AND external research should inform the fix, not just today's incident. |
| 2 | Integration approach | **Extend `docs-staleness-check.sh`**, not a separate scan — same gate, wider prose-pattern coverage. No new script, no new dependency. |
| 3 | Scope | **Craft only.** Craft already has the most mature doc-tooling of the ~25 dev-tools sibling repos; solve here first, consider porting the pattern later if it proves out. |
| 4 | Rigor level | **Targeted prose-pattern additions**, not general NLP/semantic staleness detection. Low false-positive risk, addresses today's exact bug class (version-box "released DATE" lines, "N specialized agents"/"N skills" free-prose count mentions, stale highlight/callout lines that repeat a phrase from a prior release). |
| 5 | External-tool adoption | **None wholesale.** No new dependency (Vale, drift, LLM-in-CI) — the deterministic-pattern-first shape is worth copying, the tools themselves aren't a fit for craft's count/version-anchored (not code-anchored) staleness problem. |

## New Prose-Pattern Checks (Phase 7 extension)

> **Superseded by adversarial review** (2026-08-07) — the SPEC's "Review Outcome" section
> has the corrected version: check 3 (version-highlight proxy) was dropped as falsified by
> `bump-version.sh`'s own touch pattern, and check 2 was rescoped from free-text search to
> structured line shapes after a false-positive sweep found 90+ non-bug matches. This section
> is left as-is for the historical record of what was first proposed; see the SPEC for what's
> actually being built.

Concrete patterns to add to `docs-staleness-check.sh`'s count-consistency phase, each
regex-anchored the same way existing checks are (compare against the single source of truth —
`plugin.json`'s command/skill/agent counts and the current version):

1. **"released YYYY-MM-DD" / "(released ...)" mentions** — any doc claiming a release date
   for the *current* version must match `.STATUS`'s `release_date:` field. Today's REFCARD.md
   bug is exactly this pattern.
2. **"N specialized agent(s)" / "N agent(s)"** free-prose mentions (excluding files that are
   historical logs by convention — `VERSION-HISTORY.md`, `CHANGELOG.md` entries about past
   versions) — must match the current agent count.
3. **Version "highlight"/"latest"/callout lines** (`docs/index.md`'s `!!! info "Latest: ..."`,
   `docs/REFCARD.md`'s box highlight line) — flag if the line's version token matches current
   but hasn't been touched in the same commit range as the last version bump (a cheap git-log
   proxy for "this prose is stale even though the number is current").

## Test-Plan

| Tier | Coverage |
|---|---|
| `unit` | New regex/pattern-matcher functions for each of the 3 checks above, tested against both a clean fixture and a planted-defect fixture (today's exact REFCARD.md/skills-agents.md bugs, restored as regression fixtures). |
| `dogfood` | `docs-staleness-check.sh` run against the current repo state must stay GREEN; run against a git-stash of today's pre-fix REFCARD.md/skills-agents.md must go RED on the new checks (positive control — proves the fix would have caught this exact incident). |
| `e2e` | Full `/craft:check --for release` pass unaffected in runtime (new checks stay in Phase 7's existing budget, no new phase). |
| `integration` | N/A — no cross-command data flow introduced. |
| `dependency` | N/A — no external dependency added (explicit decision #5). |

## Documentation

| Doc type | Needed? |
|---|---|
| Guide/reference | `[x]` `docs/reference/REFCARD-DOCS-STALENESS.md` — add the 3 new pattern checks to its existing check inventory. |
| REFCARD (main) | N/A — score <3, no new command surface. |
| Demo/GIF | N/A — score <3, no new interactive flow. |
| Mermaid | N/A — score <3, no new architecture shape (extends an existing phase, doesn't add one). |
| CHANGELOG `[Unreleased]` | `[x]` One-line entry once implemented: "docs-staleness-check.sh: 3 new prose-pattern checks (release-date claims, agent-count mentions, stale highlight lines) — closes the REFCARD.md/skills-agents.md gap found 2026-08-07." |

## Next Step

`/craft:plan docs/specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md` to scope implementation
(the 3 pattern checks + fixtures + REFCARD-DOCS-STALENESS.md update) — small enough that grill
is optional (low ambiguity, no unresolved dependency), but available if any pattern's exact
regex/false-positive tradeoff needs interrogation before building.
