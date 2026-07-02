# SPEC: Distribution-Surface Hardening (Homebrew + Code/Desktop)

- **Status:** Draft (awaiting grill + implementation go-ahead)
- **Created:** 2026-07-01
- **Owner:** dt
- **Depth/Focus:** Default · arch
- **Source:** `/craft:workflow:brainstorm --refine` (3-agent investigation, findings verified against live files)
- **Companion:** `BRAINSTORM-dist-surface-hardening-2026-07-01.md`
- **Grill:** `GRILL-craft-mcp-2026-07-01.md` (Cluster C design — 5 branches locked)
- **Progress:** D1 ✅ (craft #243) · A ✅ (craft #244) · B ✅ (homebrew-tap #132) · C design locked (grill), impl pending

## 1. Summary

Craft ships a large Homebrew-distribution surface (one 1677-line command + 6 distribution
skills) and installs itself into Claude Code via a generated tap formula. A three-agent
audit found (a) **stale/incorrect content** in the source-surface docs, (b) **silent-failure
fragility** in the Code-CLI install path, and (c) a **structural gap**: craft has no path to
Claude Chat Desktop, which uses an incompatible extension format. This spec fixes A + B and
documents C as deferred future work.

## 2. Scope decision (from brainstorm)

| Cluster | Decision | Repo | Branch model |
|---|---|---|---|
| **A** · Source-surface hygiene | **Implement** | `craft` | `.md` only — worktree for a clean PR |
| **B** · Code-CLI install robustness | **Implement** | `homebrew-tap` | code — worktree; formula is GENERATED |
| **C** · Desktop distribution bridge | **IMPLEMENT (net-new MCP/DXT package)** | new pkg | worktree — net-new code |
| **D** · Systemic drift + 🔴 broken curl install | **IMPLEMENT (highest priority)** | `craft` + `claude-plugins` | worktree — code + CI |

> ✅ **Resolved (user, 2026-07-01):** "cover all of them; do not defer desktop; implement all."
> Cluster C is now a full implementation workstream. **Caveat:** this is net-new engineering, not
> a fix — craft has no MCP server today, so C requires authoring one + a DXT/MCPB package. The
> one open fork is *what the server exposes* (§4C) — a product decision, being confirmed before
> C code is written. A/B are unaffected and proceed in parallel.

## 3. Verified findings (evidence)

### Cluster A — Source-surface hygiene (`craft`)

| # | Finding | Evidence (file:line) | Verified |
|---|---|---|---|
| A1 | Stale command count "107" (actual **116**) | `commands/dist/homebrew.md:1061,1063,1589` | ✅ grep + `find commands` = 116 |
| A2 | Auth docs teach PAT as THE mechanism; tap now uses **GitHub App token** (PAT = fallback only) | `skills/distribution/homebrew-workflow-expert/SKILL.md:244-277`, `homebrew-setup-wizard/SKILL.md:229-266` vs `homebrew-tap/.github/workflows/update-formula.yml:100-116` | ✅ |
| A3 | Phantom formula `scribe (v1.0.0)` + dead workflow paths (`batch-update.yml`, `./.github/actions/update-formula`) | `homebrew-multi-formula/SKILL.md:107,161,210,243` — tap has only `scribe-cli`, no batch action | ✅ manifest has no `scribe` |
| A4 | Structurally-wrong manifest example: writes a **flat** `"my-plugin": {…}`; real schema nests under `formulas` | `commands/dist/homebrew.md:1502-1505` vs manifest top-keys `[defaults, formulas]` | ✅ |
| A5 | Hardcoded per-formula count table (`scholar.rb \| 28 commands`, `craft.rb \| 107 commands`) — unverifiable drift-magnets | `commands/dist/homebrew.md:1587-1594` | ✅ |
| A6 | Desktop surface invisible in all 5 Homebrew skills — 3-surface model lives ONLY in `dist-extras` | `dist-extras/SKILL.md:9-11,280-317` | ✅ |
| A7 | (Advisory) command re-inlines all 4 hb skills wholesale → 1677 lines of duplication | `commands/dist/homebrew.md` | ✅ |

**A8 — 6 additional stale-count instances (completeness sweep; the partial-fix trap):** fixing only
`homebrew.md` would have missed these LIVE claims —
`commands/dist/marketplace.md:234` ("108 cmds"), `:253` ("Expected 107 commands"),
`install.sh:83` ("107 commands \| 8 agents \| 36 skills"),
`commands/docs/quickstart.md:133`, `commands/docs/claude-md/init.md:73` & `:118`.
Clean: `curl-install.md`, `pypi.md`, `surfaces.md`. No new phantom `scribe` (other refs are the
`scribe` *project* + `scribe` *cask* namespace — distinct from the `scribe-cli` formula).

**A9 — NEW drift dimension: skills count `36` → actual `44`.** Several A8 files carry a stale
`36 skills` alongside the stale count. Original audit only tracked commands; the fix must sweep
skill counts too (`find skills -name '*.md'` canon).

### Cluster B — Code-CLI install robustness (`homebrew-tap`; formula is GENERATED)

| # | Finding | Evidence | Verified |
|---|---|---|---|
| B1 | `jq` is `:optional` but a **hard dependency** for auto-enable + hook-register + manifest-insert (all silently skip without it) | `Formula/craft.rb:12,66,90,121` | ✅ |
| B2 | `post_install` Step 3 re-copy **silently no-ops** when `claude` not on PATH → runtime keeps stale version | `Formula/craft.rb:223-231` (`if which("claude")`) | ✅ |
| B3 | 4-representation **version drift** (tap manifest / Cellar libexec / `enabledPlugins` / runtime cache copies) — live now: tap 2.57.0, Cellar+cache 2.56.0 | live `brew info`, cache dir | ✅ (reproduced today) |
| B4 | **Cache accretion**: old versions never GC'd in `~/.claude/plugins/cache/local-plugins/craft/` | live dir (2.52…2.56 present) | ✅ |
| B5 | 30s timeout kill + macOS symlink-fallback `exit 0` → **brew reports success while plugin is absent** | `Formula/craft.rb:155-163,204` | ✅ |

### Cluster C — Desktop distribution gap (documented, deferred)

| Aspect | Claude Code (CLI) | Claude Chat Desktop |
|---|---|---|
| Store | `~/.claude/plugins/` + `~/.claude/local-marketplace/` | `~/Library/Application Support/Claude/Claude Extensions/` |
| Registry | `installed_plugins.json`, `marketplace.json` | `extensions-installations.json` |
| Config | `settings.json` → `enabledPlugins` | `claude_desktop_config.json` → `mcpServers` |
| Unit | plugin dir (`commands/`+`skills/`+`agents/`) | DXT/MCPB (`manifest.json` + runnable MCP `entry_point`) |

- **craft reaches Desktop: NO** (`grep craft extensions-installations.json` = 0; install script touches only `~/.claude/`).
- **Root cause:** format incompatibility — craft = prompt assets; Desktop = a runnable MCP server. craft has no server to run, so it **cannot install on Desktop as-is**. Bridging = authoring a **net-new DXT/MCP package**, not a repackage. → Cluster C.

### Cluster D — Systemic drift + broken curl install (completeness sweep; NEW)

| # | Finding | Evidence | Sev |
|---|---|---|---|
| D1 | **🔴 curl install ships craft v1.16.0** (41 versions stale). `README.md:52` advertises `curl … install.sh \| bash`; `install.sh:9,53-55` clones `Data-Wise/claude-plugins` + sparse-checkouts the `craft/` subdir, whose live `plugin.json` = **1.16.0**. `aggregator-sync.yml` only rewrites the aggregator ROOT `marketplace.json`, never the `craft/` subdir the installer copies. Banner also frozen (`install.sh:18,83` "v1.17.0", "107 cmds/36 skills"). | verified live (`gh api` = 1.16.0) | **CRITICAL** |
| D2 | **🟠 Systemic root cause:** no release tool guards any dist artifact except `homebrew.md`. `validate-counts.sh:114` = homebrew.md ONLY; `bump-version.sh:260-262` = plugin.json/marketplace.json/package.json ONLY. So `install.sh`, `marketplace.md`, `quickstart.md`, `init.md` drift every release — this is WHY A1/A8/A9 exist. | verified | HIGH |
| D3 | Local `dist/data-wise-marketplace.json` stale at **v2.38.2** while live aggregator is 2.57.0; `post-release-sweep.sh` feeds this local copy as a BLOCK leg but `RUN_SURFACES` is off by default → block unenforced. | critic (verify at impl) | MED |
| D4 | Cowork surface (`scripts/surfaces/registry.json`) has `propagate: manual`, no write path → drifts silently. Distinct from the Desktop gap (C). | critic (verify at impl) | LOW |
| D5 | `pypi.md` may be dead surface (craft is a plugin, no PyPI package); `curl-install.md` is `deprecated: true`. Confirm before editing. | critic (verify at impl) | LOW |
| D6 | **No test asserts dist-doc accuracy** vs live `plugin.json` counts/version — drift is invisible to CI. | critic | HIGH (prevents recurrence) |

## 4. Proposed fixes

### Cluster A (in `craft`)

- **A1** Scope by ROLE, not blanket `s/107/116/` (edit-safety rule): the **table at `:1587-1594`** is a live reference claim → fix it (or de-hardcode). The three at **`:1061-1063`** are illustrative before/after examples teaching "how to shorten a description" — the count is incidental → judge each individually; prefer placeholder language over a literal bump. (aligns with `hardcoded-counts-in-command-templates-cause-drift`.)
- **A2** Rewrite the two auth sections: **GitHub App token (`app_id`/`app_private_key`) primary**, fine-grained PAT as documented fallback. Update the `secrets:` YAML blocks to show app-token first, matching `update-formula.yml`.
- **A3** Replace `scribe (v1.0.0)` → `scribe-cli` (or drop the illustrative row); remove/annotate the non-existent `batch-update.yml` + `./.github/actions/update-formula` references as "illustrative, not present in tap."
- **A4** Fix the manifest example to nest under `formulas` (`{"formulas": {"my-plugin": {…}}}`) matching the real schema.
- **A5** De-hardcode the per-formula count column (drop counts or mark "see manifest").
- **A6** Add a one-line Desktop/surface cross-reference to each of the 5 Homebrew skills pointing at `dist-extras` / `commands/dist/surfaces.md` (the 3-surface model).
- **A7** (Advisory, likely separate) evaluate slimming `homebrew.md`'s inlined skill content to references — larger refactor, flag don't force.

### Cluster B (in `homebrew-tap`; regen, never hand-edit `.rb`)

> 🔒 **HARD CONSTRAINT (user, 2026-07-01, via /refine): NO SYMLINKS in plugin installation.**
> Installations place REAL directories/files. Replace the two-symlink chain
> (`~/.claude/plugins/<name> → $(brew --prefix)/opt/<name>/libexec`,
> `~/.claude/local-marketplace/<name> → ~/.claude/plugins/<name>`) with real copies in
> `generator/blocks/symlink.sh` (+ `marketplace.sh`) and the post_install emitter — then regen
> all 6 formulas. Implications: (i) `brew upgrade` refresh becomes load-bearing — post_install
> Step 3 (marketplace-update → plugin-update re-copy) must be explicit, not reliant on the `opt/`
> symlink auto-following; (ii) **migration** — installer must detect an existing symlink at
> `~/.claude/plugins/<name>` (current live state) and replace it with a copy; (iii) **B5 is
> superseded** — no symlinks → no symlink-fallback path; rework the macOS-permission failure
> handling for the copy; (iv) **enforcement** — add a tap-side contract test asserting no `ln -s`
> in any generated `*-install` script. The curl installer (D1) is already copy-based (direct
> clone) — keep it that way.

> **Fix-path correction (structural sweep):** the install *bash* logic is NOT inline in
> `generate.py` — it's in per-feature block files under `generator/blocks/*.sh` (loaded via
> `load_block`, `generate.py:31-35`). Only the *Ruby* `post_install` is literal in
> `generate.py:322-378`. Two gotchas: (i) **per-feature gating** — `schema-cleanup.sh`/`branch-guard.sh`
> are craft-only; a universal fix must land in an ALWAYS-emitted spot (`symlink.sh`, or post_install
> Step 2/3); (ii) **two surfaces** — jq + claude-on-PATH are each checked in BOTH the bash blocks
> AND the Ruby post_install; a complete fix touches both.

- **B1 (jq — DECIDED: promote to required dep).** Set `depends_on "jq"` (drop `=> :optional`) in the
  generated formulas — this makes the currently-silent `command -v jq` skips in
  `blocks/{marketplace,claude-detection,branch-guard}.sh` consistent (jq now guaranteed present).
  Cascades to all 6 claude-plugin formulas via `manifest.json` + `generate.py`. (If kept optional
  instead, the skips must become non-silent warnings — but required is cleaner and was chosen.)
- **B2** `post_install` Step 3 `if which("claude")` (`generate.py:370`) → add an `else`/`opoo`
  actionable finish-line (don't silently no-op). Also the bash `command -v claude` sites.
- **B3/B4** Version-drift self-check + cache-GC → add to the post_install Ruby emitter
  (`generate.py:341-376`, ALWAYS-emitted) so they land even when the bash install is skipped.
- **B5** Timeout/symlink-fallback → non-silent warning so `brew` output flags an incomplete install.
- Workflow: edit `generator/blocks/*.sh` and/or `generate.py` → `python3 generator/generate.py` (all
  6) → `generator/check-drift.sh` green → `ruby -c` → Formula Drift Guard CI green. Scope of regen:
  `type=='claude-plugin' AND generated!=false` (`generate.py:447`) = craft, himalaya-mcp, scholar,
  rforge, rforge-orchestrator, workflow. Non-plugin formulas untouched (correct).

### Cluster C — Desktop MCP/DXT bridge (IMPLEMENT, net-new)

Desktop can only load a **runnable MCP server** wrapped as DXT/MCPB. craft has none. So C =
author `craft-mcp` (a new MCP server) + a `manifest.json` DXT package, distributed to
`~/Library/Application Support/Claude/Claude Extensions/`.

- **C1 (OPEN FORK — product decision) — what does the server expose?**
  - **Option A (recommended):** craft's stable **utility scripts as MCP tools** — `validate-counts`,
    governance audit (`run_rules.py`), `pre-release-check`, `docs-staleness-check`, branch-guard
    status. These are real executables with clean I/O → natural tool mapping; immediately useful
    to a Desktop Claude doing repo hygiene.
  - **Option B:** bundle craft's **commands/skills as reference/prompt assets** for Desktop's
    Claude to read. Low effort but low value — Desktop has no slash-command/skill runtime.
  - **Option C:** a **routing proxy** that re-exposes `/craft:do`-style routing over MCP. Highest
    value, highest complexity/fragility (Desktop lacks the Claude Code runtime these assume).
- **C2** Scaffold the MCP server (language TBD by C1 — Node/TS mirrors himalaya-mcp precedent).
- **C3** Author the DXT `manifest.json` (`manifest_version`, `server:{type,entry_point,mcp_config}`,
  `user_config`) + bundle.
- **C4** Distribution: add a `craft-mcp` (or `craft-desktop`) formula/artifact to the tap OR a
  standalone `.mcpb` release asset; add a Desktop install path to the surface model.
- **C5** Update `dist-extras` + the 5 Homebrew skills: Desktop is now SUPPORTED via `craft-mcp`
  (supersedes A6's "not supported" note).

> ✅ **C1 RESOLVED (user, 2026-07-01): Option A — utility scripts as MCP tools.** `craft-mcp`
> exposes `validate-counts`, governance `run_rules.py`, `pre-release-check`, `docs-staleness-check`,
> branch-guard status as MCP tools. C2–C5 now unblocked.

### Cluster D — Systemic drift + broken curl install (highest priority)

- **D1 (🔴 fix FIRST — user-facing).** Repair the curl-install path (open sub-fork): (a) make
  `aggregator-sync.yml` also sync the `claude-plugins` `craft/` subdir on release (proper); (b)
  rewrite `install.sh` to install from current source not the frozen mirror; or (c) deprecate the
  curl path in README, point at Homebrew/marketplace. De-hardcode `install.sh` banner too.
- **D2** Extend drift guards: add `install.sh`, `marketplace.md`, `quickstart.md`, `init.md` to
  `bump-version.sh` targets / `validate-counts.sh` scan. Single source = `plugin.json` counts.
- **D3** Fix stale `dist/data-wise-marketplace.json` (2.38.2→current) + confirm the sweep BLOCK leg runs.
- **D6** Add a **dist-doc accuracy test** (counts/version vs `plugin.json`) — durable fix for the D2 root cause.
- **D4/D5** (advisory) Cowork write-path; `pypi.md` live-vs-dead — likely follow-ups.

## 5. Goals (priority-ordered — 🔴 critical first, then cheapest-first)

```
G0  D1  🔴 fix curl install (ships v1.16.0) + banner     [craft/aggr]   CRITICAL — do first
G1  A1  counts 107→116 (role-scoped) + de-hardcode       [craft, .md]   trivial
G1b A8+A9 sweep the 6 more instances + skills 36→44       [craft, .md]   small — same class as A1
G2  A4  manifest flat→nested example                     [craft, .md]   trivial
G3  A3  scribe→scribe-cli + dead-path annotations        [craft, .md]   small
G4  A5  de-hardcode per-formula count table              [craft, .md]   small
G5  A2  auth: GitHub App primary / PAT fallback (2 skills)[craft, .md]  medium
G6  A6  Desktop/surface cross-ref in 5 hb skills          [craft, .md]  small
Gd2 D2+D6 drift guards + dist-doc accuracy test           [craft]        medium — prevents recurrence
G7  B2  Step-3 non-silent finish message                 [tap, gen]     small
G8  B1  jq required-or-hard-fail                          [tap, gen]     medium
G9  B5  timeout/fallback non-silent warning              [tap, gen]     medium
G10 B3+B4 version-drift self-check + cache GC             [tap, gen]     medium
G12 C2  scaffold craft-mcp server (utility-scripts tools) [new pkg]      LARGE
G13 C3  DXT manifest.json + bundle                        [new pkg]      medium
G14 C4  Desktop distribution artifact (tap/.mcpb)         [tap/new]      medium
G15 C5  flip skills/dist-extras to "Desktop SUPPORTED"    [craft, .md]   small
—   A7  homebrew.md de-inline (advisory)                  [craft]        LARGE → separate
```

**Four workstreams / worktrees:**

- `wt-D-critical` (G0 + Gd2, D-cluster) — **do first**, spans `craft` + `claude-plugins` aggregator.
- `craft-A` (G1-G6, `.md` in craft).
- `tap-B` (G7-G10, generated code in `homebrew-tap`).
- `craft-C` (G12-G15, net-new `craft-mcp` MCP pkg + DXT) — C1 resolved (utility-scripts).

## 6. Test plan (tier-inferred)

Change shapes: prose/frontmatter (A) + install-script logic in a generated template (B).

| Tier | In scope? | What |
|---|---|---|
| `e2e` | ✅ | Assert homebrew.md/skills contain no `107`, no bare `scribe`, no flat-manifest example; auth section names `app_id` |
| `dogfood` | ✅ | `/craft:dist:homebrew` self-usage still routes; count-cascade check |
| `unit` | ✅ (B) | `generate.py` renders jq-hard-fail + drift-check blocks; `ruby -c` on regenerated formulas |
| `integration` | ✅ (B) | Simulated install with `claude` absent → finish-message present; with old cache → GC prunes |
| `dependency` | ⚠️ (B1) | If `jq` promoted to real dep — update dependency tests |
| `count-cascade` | N/A | No new command/skill/agent in A/B/D (C's craft-mcp is a separate pkg, not a plugin unit) |

Emit stubs red-first; `# TODO(author): delete if not contract-bearing`.

## 7. Documentation impact (doc-scorer ≥3)

- **CHANGELOG `[Unreleased]`** — ✅ (behavior + doc-accuracy change).
- **guide/refcard** — N/A (no new user-facing command).
- Cross-repo: `homebrew-tap` changes need a note in its `generator/` reconcile record.

## 8. Risks

- **R1** B changes touch a GENERATED artifact — hand-editing `craft.rb` would be reverted by the next release regen. MUST go through `generate.py` + `blocks/*.sh`. (memory: `manifest-driven-code-generation-vs-hand-editing`.)
- **R2** Promoting `jq` to a required dep changes install semantics for all 6 claude-plugin formulas — regen + drift-guard; jq is tiny/ubiquitous so low blast radius, but it's a real dep flip. (User accepted; flagged.)
- **R3** Cross-repo, FOUR-worktree change across `craft` + `homebrew-tap` + `claude-plugins` (aggregator) + a new `craft-mcp` pkg — sequence independently; don't couple PRs.
- **R4** Auth-doc rewrite (A2) must match the ACTUAL tap contract (app-token primary, PAT fallback) — verify against `update-formula.yml` at implement time, not from memory.
- **R5** D1 curl fix touches the `Data-Wise/claude-plugins` aggregator repo (a *different* repo) — needs its own branch/PR + the release automation may need changing (aggregator-sync must sync the subdir). Confirm approach before coding.
- **R6** C (craft-mcp) is net-new — the effort is a small feature project, not a doc fix. Should likely be its own spec/PR track even within "implement all."

## 9. Next steps (order matters — implementation is gated on worktree permission)

1. ✅ **Completeness sweep** — DONE. Found 6 more stale instances, the skills 36→44 dimension, the
   `blocks/*.sh` fix-path correction, and Cluster D (critical curl bug + systemic root cause).
2. **Recommended sequence:** **D1 (🔴 critical curl fix) FIRST** as a fast standalone PR → then A
   (doc hygiene + D2/D6 guards, one craft PR) → then B (tap generated-code) → then C (net-new craft-mcp).
3. **Get explicit worktree permission** — up to 4 worktrees across 3 repos + a new pkg. (No
   worktree/branch creation without a per-instance "yes" — global rule.)
4. Implement via `/craft:orchestrate:workflow` per workstream; verify (regen + `check-drift.sh` +
   Formula Drift Guard for B; dist-doc accuracy test for A/D; `manifest.json`/DXT validate for C).
