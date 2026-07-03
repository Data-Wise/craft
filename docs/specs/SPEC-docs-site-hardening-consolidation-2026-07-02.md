# SPEC: Docs-Site Staleness Hardening + docs/site Command Consolidation

- **Status:** Draft (proposal — awaiting grill + go-ahead; NOT yet implemented)
- **Created:** 2026-07-02
- **Owner:** dt
- **Source:** `/refine` → live-site check (Chrome extension not connected → fetched live pages)
- **Depth/Focus:** default · arch
- **Grill:** `GRILL-docs-site-hardening-consolidation-2026-07-02.md` (6 branches locked — deploy-model, full-consolidation, merge-safety, guard-scope, H1-gate, sequencing)

## 1. Problem (two independent root causes)

The live docs site (`data-wise.github.io/craft`) "wasn't updated despite running doc
checks + website update." It's **two compounding failures**:

**RC1 — deploy is `main`-gated; work is on `dev`.** `.github/workflows/docs.yml`
triggers only on **push to `main`** (`paths: docs/**`, `mkdocs.yml`) → `mkdocs
gh-deploy --force`. Live site last built **2026-07-01 23:08** (the v2.57.0 release).
Every `docs:*`/`site:*` command this session ran on **`dev`** — none reaches the live
site until a `dev→main` release. The commands report success locally → **false
green**: nothing verifies the live URL actually changed.

**RC2 — deployed site carries stale hardcoded counts.** The live page mixes current
(`2.57.0`, `116 commands`, `44 skills`) with **stale** (`112 commands`, `115
commands`, `39 skills`). Source: hardcoded counts in `docs/` pages —
**`docs/index.md`** (the homepage) + `docs/cookbook/common/find-the-right-command.md`.
This is the Cluster-A drift class, but in `docs/` site pages the count-guards never
scanned (Cluster A's `test_dist_doc_accuracy.py` covers `commands/dist/*` + install.sh,
NOT `docs/`).

> Evidence: `curl data-wise.github.io/craft` (mixed counts + `last-modified 2026-07-01`);
> `docs.yml` (main-only trigger); `grep docs/` (stale counts in index.md + cookbook).

## 2. Harden (both root causes)

### H1 — Verify-live-after-deploy gate

The deploy pipeline (and any "site update" command) must **assert the live URL
reflects the intended state**, not just that a local build succeeded.

- In `docs.yml` (post `mkdocs gh-deploy`): poll `https://data-wise.github.io/craft/`
  until `last-modified` advances, then `curl` it and assert the homepage version ==
  the just-released version (fail the job loudly on mismatch/timeout). Mirrors the
  release skill's existing "Step 13 curl live-site version check" — make it a
  hard gate here too.
- Any `dev`-side `site:update`/`docs:update` command must **print a WARNING** that
  changes won't reach the live site until a `dev→main` release (kills the false green).

### H2 — Extend the dist-doc-accuracy guard to `docs/`

Add `docs/` live-claim pages (`docs/index.md`, `docs/cookbook/**`, `quickstart`) to
the curated set in `tests/test_dist_doc_accuracy.py` (Cluster A / D6) so hardcoded
`N commands`/`N skills` in site pages are gated in CI — same canonical-count check,
same role-scoping (skip changelog/history/spec files). Fixes the RC2 drift at the
source and blocks recurrence.

### H3 — Clarify the dev↔main deploy model (doc, not code)

Document (in the site/docs skill + `docs.yml` header) that **the live site tracks
`main` (releases)**, by design. If a dev-preview is wanted, that's a separate
opt-in (a `workflow_dispatch` preview deploy to a `/dev/` path) — flagged, not built
here.

## 3. Consolidate the docs/site command surface (full audit)

**~35 commands, two overlapping families.** `craft:site:*` is the real site
lifecycle; `craft:docs:*` duplicates chunks of it (`docs:site`, `docs:website`) and
also holds doc-content generators. Proposed merges (thin-shim deprecations, ADR-002):

| Cluster | Current (overlapping) | → Consolidated | Action |
|---|---|---|---|
| **Site lifecycle** | `site:build` `site:deploy` `site:publish` `site:preview` `site:init` `site:create` + `docs:site` `docs:website` | `site:build` · `site:deploy` · `site:preview` · `site:init` | **Deprecate `docs:site` + `docs:website`** (route to `site:*`); fold `publish`→`deploy`, `create`→`init` |
| **Health checks** | `docs:check` `docs:check-links` `site:check` `site:audit` | `docs:check` (umbrella: links + site + count-accuracy) | Merge `check-links` + `site:check` into `docs:check`; keep `site:audit` as content-inventory only |
| **Update / nav** | `docs:update` `docs:sync` `docs:nav-update` `site:update` `site:nav` | `docs:sync` (detect→classify) · `docs:nav-update` | Merge `site:update`→`docs:sync`; `site:nav`→`docs:nav-update` |
| **Status** | `site:status` `site:progress` | `site:status` | Merge `progress`→`status` |
| **Content generators** (keep, distinct) | `docs:api` `docs:changelog` `docs:demo` `docs:guide` `docs:mermaid` `docs:prompt` `docs:quickstart` `docs:tutorial` | (unchanged) | Distinct generators — keep |
| **Misc** | `site:theme` `site:add` `site:consolidate` `docs/frameworks` | (evaluate) | Likely keep; `site:consolidate` may fold into `site:audit` |

**Net:** ~35 → ~24 commands; removes the docs↔site duplication that made "which
command updates the site?" ambiguous (a contributor to RC1's false green). Each
deprecation is a thin shim → canonical command (behavior preserved, ADR-002 pattern).

## 4. Skills touched

`docs/site-management`, `docs/navigation`, `docs/doc-classifier`,
`docs/changelog-automation` — the consolidated commands route into these; the harden
gates (H1/H2) live in `site-management` + the release skill.

## 5. Test plan

| Tier | What |
|---|---|
| e2e | `docs:check` umbrella runs links+site+counts; deprecated `docs:site`/`docs:website` shim to `site:*` |
| dogfood | count-cascade for removed commands (~35→~24); each shim resolves |
| integration | H1 live-URL gate: mock a version mismatch → job fails; H2: stale count in `docs/index.md` → `test_dist_doc_accuracy` fails |
| count-cascade | command-count drop cascades (bump-version, plugin.json, ~doc refs) |

## 6. Risks

- **R1** Command consolidation = a count cascade (~11 removed) → the ~30-file bump. Sequence carefully (memory: `adding-a-command-cascades-30-file-count-bump`).
- **R2** H1 live-URL gate depends on GitHub Pages `last-modified` latency — poll with timeout + retry (don't hard-fail on CDN lag; distinguish "not yet propagated" from "wrong content").
- **R3** Deprecating `docs:site`/`docs:website` — grep ALL callers (do.md/hub routing, tutorials, tests) before shimming (memory: `when-fixing-a-contract-violation-grep-all-callers`).
- **R4** This is a LARGE consolidation — likely its own multi-PR effort, sequenced after the dist-surface release.

## 7. Next (gated)

1. **Grill this spec** (`/craft:grill` — per grill-new-specs rule; no GRILL ledger yet) — esp. the consolidation merge map (R1 cascade, R3 callers) + H1 gate design.
2. Split into workstreams: **Harden** (H1+H2, small, high-value, do first) vs **Consolidate** (large, own effort).
3. Implement post dist-surface `dev→main` release.
