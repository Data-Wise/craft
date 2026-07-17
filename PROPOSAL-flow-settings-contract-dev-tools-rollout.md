# PROPOSAL: Roll the Project Settings Contract out to dev-tools packages

**Date:** 2026-07-17
**Trigger:** craft's own `.STATUS`/`.flow/` audit (this session) found craft has no `.flow/` folder
at all, and the only real precedent — `.flow/obsidian-sync.yml` — looked research/teaching-specific.
Investigating further found the convention is real, decided, and enforced... just never rolled out
to dev-tools package repos.

**Note on location:** this proposal's natural home is `dev-tools/docs-standards` (the repo that
owns ADR-001 below), but that repo's checkout is currently on `main` (protected, blocks all writes).
Saved here in craft instead rather than switching that repo's branch unprompted — move it over via
a `docs-standards` feature branch if you want it to live there.

## Research findings (the corrected picture)

1. **The convention already exists.** `docs-standards/adr/ADR-001-research-ops-ecosystem-ownership.md`
   (2026-06-25, all decisions locked) defines a **Project Settings Contract**: every project should
   have `.STATUS` + `CLAUDE.md` + a vault-mirror-map file, audited by `atlas doctor`. D5 explicitly
   covers this exact case: *"non-vault projects (packages/dev-tools) use `mirror: none` so the file
   exists but is a no-op."* This isn't something to invent — it's something to **execute**.

2. **The canonical path flip-flopped, but is now settled.** ADR-001 originally decided (D2) to
   relocate the mirror-map from `.flow/obsidian-sync.yml` → `.obs/sync.yml` (obs-owned). That was
   built, then **reverted** by obsidian-cli-ops on 2026-07-12 (`obs link` / `.obs/sync.yml` deleted;
   changelog: *"`.flow/obsidian-sync.yml` is now the sole vault↔repo mirror-map contract"*). atlas's
   own `DoctorUseCase.js` was still pointing at the dead `.obs/sync.yml` path until **today**
   (2026-07-16, atlas PR #88, merged) — a live cross-repo SPEC
   (`atlas/docs/specs/SPEC-cross-repo-research-ops-integration-2026-07-16.md`) caught and fixed it.
   **Bottom line: `.flow/obsidian-sync.yml` is the current, correct, live path.** Don't build
   anything against `.obs/sync.yml` — that path is dead.

3. **Zero dev-tools packages have this file — including the tools that own the convention.**
   Swept `~/projects/dev-tools/*/.flow/`: only `flow-cli` has a `.flow/` folder at all, and it holds
   `teach-config.yml` (a different, flow-cli-specific concern), not `obsidian-sync.yml`. **atlas,
   obsidian-cli-ops, and savant — the three tools that designed and enforce this contract — don't
   have the file for themselves either.** This isn't a dev-tools-specific gap; it's a
   never-rolled-out-anywhere-outside-research-projects gap.

4. **Enforcement already reaches dev-tools; execution doesn't.** `atlas`'s `scanPaths`
   (`~/.atlas/config.json`) already includes `/Users/dt/projects`, which covers every dev-tools repo.
   `atlas doctor` is already auditing all ~25 of them today and reporting the gap (`.flow/obsidian-sync.yml`
   missing, `info` severity, non-blocking) — the enforcement mechanism the ask wants already runs;
   it's just been ignored as low-severity noise because nothing ever populated the file.

5. **The one rollout SPEC in flight doesn't cover dev-tools packages.** The 2026-07-16 SPEC's Item 2
   (scaffolder gap) only wires `savant`'s `research-scaffold --mode repo` to write the file at
   *research-project* birth. It does not touch `atlas init`/dev-tools plugin scaffolding, and no PR
   for Item 2 exists yet (only Items 1 and 4 show merged/open PRs). Dev-tools packages were never in
   scope for that effort — this proposal is the missing piece, not a duplicate of it.

## Quick Wins (< 30 min)

1. ~~Confirm the actual CLI to create the file~~ — **DONE 2026-07-17.** Answer: the installed
   `obs` v4.3.0 (Homebrew) is a **released build that predates the path fix**. `git describe` on
   the source checkout shows `v4.2.0-87-gd42bb0c` — the "`.obs/sync.yml` removed, `.flow/obsidian-sync.yml`
   is sole path" changelog entry is unreleased work sitting in those 87 commits, never cut into a tag.
   Concretely: `obs link` **is** wired in the installed binary and **does** run — but it writes the
   now-dead `.obs/sync.yml` path (`obs_cli.py:1048`, `help='Create the per-project .obs/sync.yml mirror
   map (ADR-001)'`). `obs flow init` (the correct, current path) has no working CLI today — it exists
   only as unreleased source (`core/flow_init.py`) not yet reachable from any installed command.
   **Running `obs link` today would actively create the wrong file.** Don't run it.
2. ~~Hand-author a `mirror: none` stub~~ — **REJECTED 2026-07-17, do not do this.** Checked the
   *current* schema (`schema/obsidian-sync.schema.json`) before writing anything into 3 other repos'
   trees, and it doesn't support a no-op mode at all:

   ```json
   "required": ["vault_root", "pairs"],
   "additionalProperties": false
   ```

   `mirror: none` was a property of the **old, removed** `.obs/sync.yml` interface (confirmed: the
   untracked `obsidian-cli-ops/.obs/sync.yml` stub with that exact content is a leftover from that
   dead path, at the dead path). **ADR-001's D5 promise — "non-vault projects use `mirror: none` so
   the file exists but is a no-op" — did not carry over when the implementation reverted to
   `.flow/obsidian-sync.yml`.** There is currently no schema-valid way to say "this project has no
   vault." Writing a stub now means either an invalid file (fails the schema) or fabricating a fake
   `vault_root`/`pairs` entry — the exact "don't invent config that doesn't apply" trap this whole
   investigation started from. **This is the real blocker, not the CLI.**
3. **Real next step: fix the schema gap, not the CLI gap.** Someone with obsidian-cli-ops context
   needs to decide how a no-vault project should look under the *current* schema — e.g. add back an
   optional `mirror: none` (with `vault_root`/`pairs` conditionally required only when
   `mirror != none`), or an explicit `pairs: []` allowance, or a separate top-level marker. This is a
   schema/ADR decision, not something to route around from a docs-brainstorm session by hand-forging
   a file three other repos would then have to un-fabricate later.
4. Once the schema supports a no-op mode: backfill `.flow/obsidian-sync.yml` for the 3 owner tools
   (atlas, obsidian-cli-ops, savant) first, then re-run `atlas doctor --all` to confirm the gap count
   drops. **Both still pending — nothing written to any of the 3 repos this session.**

## Medium Effort (1-2 hrs)

- [ ] Decide + implement the schema's no-vault representation (item 3 above) in
  `obsidian-cli-ops/schema/obsidian-sync.schema.json` — this blocks everything below it.
- [ ] Once unblocked: backfill `.flow/obsidian-sync.yml` across all ~25 dev-tools repos. A simple
  loop is enough once the schema-valid no-op shape exists — one small file per repo, not a bespoke
  config per project.
- [ ] File (or update) a docs-standards/atlas issue scoping "dev-tools package" as a first-class
  target of the Project Settings Contract rollout, distinct from the research-project scaffolding
  path Item 2 already covers — so this doesn't silently regress the next time someone re-derives
  "who owns what" the way ADR-001 itself had to.
- [ ] Add a `craft:check`-style pre-commit or CI gate in `docs-standards` (or a lightweight shared
  script) that fails a dev-tools repo's CI if `.STATUS`/`CLAUDE.md`/`.flow/obsidian-sync.yml` are
  missing — turning `atlas doctor`'s currently-passive `info` severity into something that actually
  gets fixed instead of accumulating as background noise (57 projects deep already, per the ADR's
  own coverage table).

## Long-term (future sessions)

- [ ] Wire whichever scaffolder creates new dev-tools packages (if one exists / gets built) to call
  the real `obs flow init`-equivalent at birth, mirroring what Item 2 of the 2026-07-16 SPEC does for
  `savant research-scaffold` — so this stops being a backfill problem for every *future* dev-tools
  repo too.
- [ ] Revisit `atlas doctor`'s severity for `.flow/obsidian-sync.yml` on package-kind projects once
  coverage is non-zero — decide whether "info" is still right or whether it should escalate now that
  compliance is achievable in practice, not just in theory.

## Recommended Next Step

→ Decide the schema's no-vault representation (Quick Win #3) in `obsidian-cli-ops` — this is now the
one real blocker. The CLI-availability question (Quick Win #1) turned out to be a red herring once
the schema itself was checked: even with a working `obs flow init`, there's still no schema-valid way
to declare "no vault" for a package like craft or atlas. Fix the schema, and the backfill + rollout
below it is mechanical.
