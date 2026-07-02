# NEXT-SESSION Plan — 2026-07-02

Handoff for the next Claude session. Entry points + pending work after the
dist-surface hardening effort (all merged to `dev`, release cut this session).

## State at handoff

- **Dist-surface hardening COMPLETE on `dev`** — D1/A/B/C + esbuild + 4 spawned
  follow-ups (#243–#250, tap #132/#133) all merged. See `.STATUS` `last_completed`.
- **Release:** dist-surface `dev→main` **cut this session** (see `.STATUS` for version/tag).
- **craft-mcp** (`mcp/`): CLI-validated (smoke 20/20 + `mcpb validate`). Desktop
  install unverified — computer-use can't observe Claude Desktop (blocks screen capture).

## Pending work (priority order)

### 1. Docs-site harden + consolidate  — task #6, GRILLED & ready to plan

- Spec: `SPEC-docs-site-hardening-consolidation-2026-07-02.md`
- Grill: `GRILL-docs-site-hardening-consolidation-2026-07-02.md` (6 branches locked)
- **Next step:** `/craft:plan` tier 4 → `ORCHESTRATE`, then implement in G-6 order:
  1. **HARDEN first** (own PR): H1 poll-timeout live-verify gate in `docs.yml` +
     dev-update warning; H2 extend `tests/test_dist_doc_accuracy.py` to ALL
     `docs/*.md` with smart per-line detection (≥50 threshold + skip historical);
     H3 document the main-gated model.
  2. Audit+fold-before-shim the merges (esp. `docs:website` 30K → `site:*` — avoid
     the rich-body trap; caller-grep do/hub/tutorials/tests first).
  3. ~40-file count cascade LAST, against the final ~24-command set.

### 2. Phase-briefing skill — task #5, NOT yet grilled

- Spec: `SPEC-phase-briefing-2026-07-01.md` (detection mechanisms in §3.1).
- **Next step:** grill it first (per the grill-new-specs rule — no GRILL ledger
  yet), then implement (new `skills/workflow/phase-briefing/` + `--phase` on
  `/craft:workflow:brief` + orchestrator emit-point).

### 3. Held / backlog

- **#237** plugin-audit-skill — HELD (jq schema mismatch + false-positive collision heuristic; needs rework).
- craft-mcp Desktop `.mcpb` validation — optional (CLI already proves the server); Apple Note has the steps.
- Teaching-residue audit (craft↔scholar) — unscheduled.

## New rules/memories this session (already saved)

pre-pr-testing · no-auto-archive-live-sessions · ask-question-recommendations trigger ·
grill-new-specs-before-implementation · tar-pipe-copy-for-broken-symlink-trees ·
background-pr-automerge-vigilance · apple-notes-html-formatting.

## Reusable prompts produced (in transcript)

Phase-end briefing protocol · background-agent monitoring w/ leak-scan · MCP-validation
research · npm-hygiene best-practices · live-docs-site staleness check (general form).
