# GRILL: Docs-Site Hardening + docs/site Consolidation

- **Date:** 2026-07-02
- **Target:** [`SPEC-docs-site-hardening-consolidation-2026-07-02.md`](SPEC-docs-site-hardening-consolidation-2026-07-02.md)
- **Mode:** grill (convergent) — 6 branches resolved
- **Sweep evidence:** `docs.yml` main-only; no dev-preview deploy; `docs:site`/`docs:website` overlap `site:*`; `docs:check` already umbrellas; count-cascade footprint ≈ **40 files**; stale counts in `docs/index.md` + `cookbook/`.

## Locked decisions

| # | Branch | Decision | Why |
|---|--------|----------|-----|
| G-1 | **Deploy model** | Keep **main-gated** (site = released state) + **loud dev-side warning** ("won't reach live until dev→main release; use `mkdocs serve`") + **H1 live-verify gate**. No dev-preview deploy. | Matches craft's release-tracking identity; lowest complexity; kills RC1's false-green on the release path without a 2nd deploy target. |
| G-2 | **Consolidation appetite** | **FULL ~35 → ~24**, bundled WITH the harden in one effort. 40-file cascade accepted. | User chose max scope — remove the docs↔site duplication in one deliberate pass. |
| G-3 | **Merge safety** | **Audit + fold unique logic into the target, THEN thin-shim** each deprecated command. Esp. `docs:website` (30K, ADHD-enhancement) + `docs:site` (12K) — migrate their unique logic into `site:*` before shimming. | Avoids the deprecated-command-rich-body-trap (ADR-002) — no capability silently lost. |
| G-4 | **H2 guard scope** | Scan **ALL `docs/*.md`** but with **smart per-line detection** — flag only plugin-wide count CLAIMS (≥50 threshold, Cluster-A style) + skip historical CONTEXTS (changelog/version-history/dated spec+plan refs). | Full-tree breadth WITHOUT the false-positive firehose (role-scoping lives in the detector, not the file list). Reconciled from an initial "all docs = flag everything" which this session's Cluster A proved noisy. |
| G-5 | **H1 gate (CDN lag)** | **Poll live URL with timeout + retry** (e.g. 30s × ~5min) for last-modified advance AND version match; **FAIL only if never matches** in the window. | Distinguishes "not yet propagated" from "wrong content" — robust against GitHub Pages CDN lag; mirrors `docs.yml`'s existing 3-attempt deploy retry. |
| G-6 | **Sequencing** | **Harden → audit/fold-merge → count-cascade LAST.** H1/H2/H3 land first (no removals, independently valid); then fold+shim merges; then the ~40-file count cascade ONCE against the final ~24-command set (bump-version sweep + validate-counts + full suite). | No broken intermediate commit; the mechanical cascade runs once, not re-done as the command set changes. |

## Open questions (resolve at plan/build)

1. **Final merge map** — exact fate of `site:consolidate` (fold into `site:audit`?), `site:theme`/`site:add`/`docs/frameworks` (keep?), and which of the check/update/status merges are truly safe post-audit (G-3).
2. **Poll window** — H1 exact timeout/interval (5 min / 30s?) tuned to observed Pages propagation.
3. **Caller-grep list** — before shimming `docs:site`/`docs:website`, grep ALL callers: `do.md`/`hub.md` routing, tutorials, tests, skills-agents.md (memory: `when-fixing-a-contract-violation-grep-all-callers`).
4. **Count-cascade files** — the ~40 files bump-version must sweep for the new total; confirm bump-version handles the drop (memory: `adding-a-command-cascades-30-file-count-bump`).

## Handoff

Design decision-locked. Sequenced (G-6) so **Harden (H1/H2/H3) can be the first PR** even though the effort is bundled. Next: `/craft:plan` (tier 4) → `ORCHESTRATE-*.md` for the merge/cascade tracks, or implement Harden directly first. Gated behind the dist-surface `dev→main` release. Task #6 tracks it.
