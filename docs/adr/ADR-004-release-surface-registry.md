# ADR-004: Release propagates via a surface registry; Cowork is report-only

**Status:** Accepted
**Date:** 2026-06-26
**Deciders:** dt
**Relates to:** craft#218, craft#184, himalaya-mcp#67

---

## Context

Before this ADR, the craft release pipeline propagated to downstream surfaces via ad-hoc scripts
and manual steps. There was no single source of truth for which surfaces existed, what gates they
carried, or whether a release had fully propagated. This led to silent drift (craft#184) and the
aggregator marketplace falling out of sync (himalaya-mcp#67).

Three surfaces require explicit propagation after a release:

1. **Code** — Claude Code CLI (Homebrew + marketplace)
2. **Cowork** — the Cowork platform plugin registry
3. **Desktop** — the Claude Desktop DXT plugin store

---

## Decisions

### D1: Declarative surface registry (JSON + bash driver)

A single `scripts/surfaces/registry.json` file is the source of truth for all surfaces.
Each entry declares: name, detect command, propagate command, verify assertion, and gate level
(BLOCK / WARN / INFO). The `scripts/surfaces.sh` driver reads the registry and routes to
`--verify`, `--report`, `--propagate`, or `--json` operations.

**Rejected alternative:** Hard-coded surface lists in bash scripts. Rejected because additions
require editing multiple scripts; the registry makes surfaces visible and auditable.

### D2: Aggregator propagation via CI action (auto-merged PR)

The aggregator marketplace (`Data-Wise/claude-plugins`) is updated via a `release: published`
GitHub Actions workflow (`aggregator-sync.yml`). The workflow:

- Opens a version-bump PR in the aggregator repo
- Merges with `gh pr merge --admin --squash` (bypasses branch protection)
- Verifies `state == "MERGED"` after merge — exits 1 if not merged (fail-loud)

**Q2 gate decision:** The action fails loud (exit 1) if the PR was opened but not merged.
Rationale: a partially-applied aggregator update leaves users on the wrong version, which is
worse than a failed release. The `--admin` merge is justified because the aggregator repo uses
branch protection that would otherwise block automated PRs; this is a deliberate, documented
bypass for release automation.

**Rejected alternative:** Direct push to aggregator repo. Rejected because it bypasses code
review and audit trail; the PR approach maintains auditability even with auto-merge.

### D3: Cowork surface is WARN-only (report + remind, not auto-update)

The Cowork platform has its own plugin store that cannot be updated via the release pipeline.
The pipeline generates a Cowork report and queues a remind for manual action (WARN; non-blocking).

**Rationale:** Auto-updating a third-party platform store would require API credentials and a
stable API contract. Neither is available today. The WARN-only approach surfaces the drift
without blocking releases.

### D4: Desktop surface is INFO-only

The Claude Desktop DXT plugin store is fully manual. The registry records the surface for
visibility but assigns gate level INFO — no verify, no block.

### D5: Manual App-perm pre-ship gate

Before any release using the aggregator CI action, the GitHub App must have `contents: write`
and `pull-requests: write` permissions on `Data-Wise/claude-plugins`. This is a one-time manual
gate documented in the release skill and downstream-verification reference.

---

## Consequences

**Positive:**

- Single source of truth for surface inventory and gate levels
- Aggregator drift (craft#184) is now a hard block (exit 1) rather than silent
- `/craft:dist:surfaces` provides a read-only audit view at any time
- New surfaces can be added by editing `registry.json` alone

**Negative:**

- The GitHub App setup is a one-time manual prerequisite; missing permissions = CI failure
- Cowork and Desktop remain manual surfaces — they appear in the report but require human follow-up
- `--admin` merge in CI is a bypass of branch protection; if the aggregator repo adds required
  reviews in the future, the action will need to be updated

---

## References

- `scripts/surfaces/registry.json` — surface registry
- `scripts/surfaces.sh` — registry driver
- `.github/workflows/aggregator-sync.yml` — aggregator CI action
- `skills/release/references/downstream-verification.md` — Step 13.6 implementation
- `skills/distribution/dist-extras/SKILL.md` — 3-surface model reference
