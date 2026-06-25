# SPEC: v2.49.x Issues Sprint — #200, #199, #183, #171

**Status:** APPROVED (revised after 14 expert Qs + 2 agents)  
**Date:** 2026-06-23  
**Author:** brainstorm session (max depth, 10 expert Qs, 2 background agents)  
**Target release:** v2.49.x (one coordinated release)
**Grill ledger:** [GRILL-v249-issues-sprint-2026-06-23.md](GRILL-v249-issues-sprint-2026-06-23.md) — 10 sequencing/implementation decisions locked (2026-06-24)

---

## Summary

Four open issues targeted for a coordinated v2.49.x sprint, structured as 2 feature PRs + 1 ADR + quick-win doc fixes directly on `dev`.

| Issue | Title | Status Before This SPEC | Plan |
|-------|-------|------------------------|------|
| #200 | Homebrew gate gaps (verify-caveats + post-install) | Unaddressed | PR A |
| #199 | Cowork/Desktop install overhaul | Unaddressed | PR A |
| #184 | Private plugin + pin-refresh drift | Partial (advisory only) | Deferred post-v2.49.x |
| #183 | Insights facet collection is manual | Unaddressed | PR B |
| #171 | Workflow vs worktree conflict | Unaddressed | ADR on `dev` |

---

## PR A · `feature/homebrew-dist-gates` — Issues #200 + #199

### Problem

`/release` Step 10a auto-bumps `url` + `sha256` in the tap formula but leaves two silent failure modes:

1. **Stale caveats** — `def caveats` block can ship with outdated command lists (obsidian-cli-ops v4.0.0 incident).
2. **Untested post-install** — no gate exercises the `def post_install` block before the formula publishes.
3. **No Cowork/Desktop update story** — `claude plugin update` on Desktop/Cowork fails without the `@local-plugins` qualifier; `/release` has no verification step for this surface.

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Gate ownership | Craft-internal engine + project-level hook contract | Craft ships generic checker; each project adds thin wrapper — mirrors homebrew-release pattern |
| Gate severity | Opt-in strict (`HOMEBREW_GATE_STRICT=1` → exit 1); otherwise advisory | Matches governance graduation path (warn→error soak) |
| Automation level | Fully automated in `/release` pipeline | No manual override needed |

### Files to Create / Modify

```
craft/
  scripts/
    verify_caveats.py         NEW — generic caveats staleness checker
    post_install_check.py     NEW — exercises project's test-post-install.sh
  commands/dist/homebrew.md   MODIFY — add Step 10b (verify-caveats gate)
                                         and Step 10c (Cowork verification)
  docs/
    tutorials/
      TUTORIAL-homebrew-gates.md    NEW
    commands/dist/homebrew.md       MODIFY — mirror command doc updates
  tests/
    test_homebrew_gates.py    NEW

each-formula-project/ (convention, not in craft):
  scripts/
    verify-caveats.sh         NEW (per project) — defines EXPECTED_CAVEATS[]
    test-post-install.sh      NEW (per project) — exercises post_install logic
```

### `verify_caveats.py` — Key Interface (Revised: Multi-Check Gate)

**Scope expanded**: runs 5 checks in order; any failure triggers advisory or block per `HOMEBREW_GATE_STRICT`.

```python
def run_all_gates(formula_path, changelog_path, version, plugin_name=None,
                  strict=False) -> GateReport:
    """
    Runs all 5 gate checks and returns aggregated GateReport.
    Env: HOMEBREW_GATE_STRICT=1 → any finding escalates to exit 1
    """

# Check 1: Version string match
def check_version_string(formula_path: str, version: str) -> CheckResult:
    """Assert 'New in vX.Y.Z:' is present and version matches."""

# Check 2: Bullet content vs CHANGELOG
def check_bullets_vs_changelog(formula_path: str, changelog_path: str,
                                version: str) -> CheckResult:
    """Diff managed-zone bullets against CHANGELOG items for this version."""

# Check 3: post_install structural check
def check_post_install_structure(formula_path: str) -> CheckResult:
    """Assert begin/rescue/end pattern + libexec paths exist (no execution)."""

# Check 4: brew audit --strict (CI/macOS only)
def check_brew_audit(formula_path: str) -> CheckResult:
    """Run brew audit --strict; skip on non-macOS runners."""

# Check 5 (NEW — folded from #184): Plugin cache version match
def check_plugin_version(plugin_name: str, expected_version: str) -> CheckResult:
    """
    Run: claude plugin list | grep plugin_name → extract installed version.
    Assert installed version == expected_version.
    Applicable to Claude Code plugins only (not pure Homebrew CLI tools).
    Skip gracefully if claude CLI not found (CI runners).
    """
```

**Connection to #184**: Check 5 partially addresses #184 (pin-refresh drift) without reopening the full private-plugin scope. If installed version != released version, gate blocks (strict) or warns (advisory), surfacing the drift immediately.

### `/release` Step Updates

```
Step 10a (existing):  auto-bump url + sha256
Step 10b (new):       run verify_caveats.py → advisory or block
Step 10c (new):       run post_install_check.py → advisory or block
Step 10d (new):       print Cowork/Desktop verification instructions:
                        "Run: claude plugin update <name>@local-plugins"
                        "Expected version: $(jq -r .version plugin.json)"
```

### Opt-in Graduation Path

```
Phase 1 (default):   Advisory — warn during /release, print diff, never exit 1
Phase 2 (opt-in):    Project sets HOMEBREW_GATE_STRICT=1
                     → gate blocks Step 10b/10c if staleness detected
Phase 3 (future):    Governance soak integration — auto-promote after 14-day clean
                     (reuse governance/soak.py machinery from R04)
```

### Acceptance Criteria

- [ ] `verify_caveats.py` detects stale caveats in test fixture, exits 0 with warning (advisory mode)
- [ ] `verify_caveats.py` exits 1 when `HOMEBREW_GATE_STRICT=1` and caveats are stale
- [ ] `post_install_check.py` runs `test-post-install.sh` and fails if script exits non-zero
- [ ] `/release` output includes Step 10b/10c gate results and Step 10d Cowork instructions
- [ ] `docs-staleness-check.sh` passes after docs update
- [ ] `validate-counts.sh` passes (no count changes if no new commands)
- [ ] Tests: ≥ 6 new test cases in `test_homebrew_gates.py`
- [ ] Closes GitHub issues #200, #199

### Implementation Risks

1. **Ruby formula parsing is fragile** — `def caveats ... end` may span multiple blocks; use regex with block-depth counting, not naive line-scan
2. **Project-level `verify-caveats.sh` contract drift** — if craft changes the expected output format, existing project scripts break silently; version the contract
3. **`post_install_check.py` needs a dry-run mode** — actually running `post_install` may have side effects; the "check" must simulate, not execute destructively
4. **Cowork verification has no machine-readable signal** — `claude plugin list` output format may change; parse defensively

---

## PR B · `feature/insights-session-hook` — Issue #183

### Problem

`~/.claude/usage-data/` is empty on most machines because facets only write when the user manually runs `/craft:workflow:done`. `commands/workflow/insights.md:62` falsely claims collection is automatic — eroding trust.

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Trigger mechanism | SessionStop hook | Fires on every session end, no /done required |
| Automation depth | Shallow (metadata only) — no LLM | LLM-enriched fields stay in /done; hook writes skeleton |
| Existing pattern | Clone `done-reminder.sh` stdin parsing | Pattern already established; near-total reuse |

### Files to Create / Modify

```
~/.claude/
  hooks/
    session-facet.sh          NEW — SessionStop hook (writes facet skeleton)
  settings.json               MODIFY — add SessionStop hook entry
  usage-data/facets/          EXISTING — hook writes here (already exists)

craft/
  commands/workflow/insights.md   MODIFY — remove false "automatic" claim (line 62)
  tests/
    test_session_stop_hook.py     NEW
```

### `session-facet.sh` — Key Logic

```bash
#!/usr/bin/env bash
# SessionStop hook: write minimal facet when session ends
# Reuses stdin pattern from done-reminder.sh

INPUT=$(cat)
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')

# Don't double-write if /done already ran this session
TODAY=$(date +%Y%m%d)
FACETS="$HOME/.claude/usage-data/facets"
if ls "$FACETS"/session-"$TODAY"-*.json 2>/dev/null | grep -q .; then
  exit 0  # /done already wrote a richer facet today; skip
fi

# Collect shell-only metadata (no LLM needed)
PROJECT=$(basename "$CWD" 2>/dev/null || echo "unknown")
BRANCH=$(git -C "$CWD" branch --show-current 2>/dev/null || echo "")
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Write skeleton facet (same schema as /done, lower fidelity)
cat > "$FACETS/session-$TIMESTAMP.json" <<EOF
{
  "session_id": "$TIMESTAMP",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project": "$PROJECT",
  "branch": "$BRANCH",
  "goal_category": "unknown",
  "outcome": "session-end",
  "friction_events": [],
  "auto_collected": true
}
EOF
```

### Key Distinction: Hook vs `/done`

| Method | Depth | AI analysis | Friction events | Requires user action |
|--------|-------|-------------|-----------------|---------------------|
| SessionStop hook (new) | Shallow (metadata) | No | None | No — automatic |
| `/done` command (existing) | Rich (insights, patterns) | Yes | LLM-extracted | Yes |

The hook fills the zero-baseline problem. `/done` remains the high-signal path for intentional sessions.

### Acceptance Criteria

- [ ] Facet file is written to `~/.claude/usage-data/facets/` when a Claude session ends without `/done`
- [ ] Hook is a no-op if a facet already exists for today (avoids double-write with `/done`)
- [ ] Hook exits 0 on missing git repo, non-existent CWD, or missing `jq`
- [ ] `insights.md:62` no longer contains the false "automatically" claim
- [ ] `docs-staleness-check.sh` passes
- [ ] Tests: ≥ 4 new test cases in `test_session_stop_hook.py`
- [ ] Closes GitHub issue #183

### Implementation Risks

1. **Session ID collision** — if two sessions end within the same second, filenames clash; add PID suffix: `session-$TIMESTAMP-$$.json`
2. **`jq` not available** — check with `command -v jq` and fallback to Python3 parsing (same pattern as other hooks)
3. **`~/.claude/usage-data/facets/` may not exist** — `mkdir -p` before write
4. **Hook double-fire** — if SessionStop fires multiple times (crash-restart), guard against partial writes

---

## ADR · `dev` branch direct — Issue #171

### Context

No worktree needed — this is a `.md` file.

```
craft/
  docs/
    adr/                              NEW directory
      ADR-001-workflow-branch-guard.md    NEW
```

### ADR Outline (decision-only per user choice — no Task vs Workflow table, no migration guide)

**Status:** Accepted

**Context:** Claude Code's `Workflow()` tool spawns in-session agents that inherit the parent session's CWD. When the parent session is on `dev`, branch-guard blocks new code files in all spawned agents. `isolation: 'worktree'` creates ephemeral worktrees (no persistent branch) — incompatible with the craft `feature/*` branch model.

**Decision:** `Workflow()` is safe for READ operations from `dev` sessions (research, audit, analysis). Feature code writes use the ORCHESTRATE protocol (plan on `dev` → create `feature/*` worktree → commit ORCHESTRATE file → new session in worktree). No change to branch-guard or Workflow semantics.

**Alternatives Considered:**

1. `isolation: 'worktree'` on each `agent()` call — rejected: ephemeral, no branch name, state discarded at session end
2. Workflow-aware branch-guard bypass — rejected: safety invariant exists for correctness, not just policy
3. Pre-create worktree then call Workflow from dev — rejected: agents inherit calling session CWD, not worktree path
4. Disable Workflow on dev entirely — rejected: too restrictive for read-only use cases

**Consequences:** Constraint formally documented. No code added. Issue #171 closed with permanent record. Usage guidance stays in TUTORIAL and ORCHESTRATE docs.

---

## Quick Wins (no worktree — direct to `dev`)

These can ship before the PR worktrees are created:

1. **Fix `insights.md:62`** — remove "automatically" claim → `dev` commit ⚡
2. **Write `ADR-001`** — `docs/adr/ADR-001-workflow-branch-guard.md` → `dev` commit ⚡
3. **Add `@local-plugins` qualifier to release runbook** — one-line doc fix → `dev` commit ⚡

---

## PR Structure

```
Quick wins (dev, no worktree):
  chore(docs): fix insights false-auto claim + ADR-001 + release runbook note
  Closes: #171 (ADR written and issue commented)

PR A (feature/homebrew-dist-gates):
  feat(dist): verify-caveats + post-install gates + Cowork verification step
  Closes: #200, #199

PR B (feature/insights-session-hook):
  feat(workflow): SessionStop hook for automatic facet collection
  Closes: #183
```

---

## Not In This Sprint

| Issue | Reason | Next opportunity |
|-------|--------|-----------------|
| #184 (private plugin + pin-refresh) | Partial scope already shipped; remainder needs separate design | v2.50.x or dedicated sprint |
| #130 (PAT→App migration) | External dependency (himalaya-mcp, nexus-cli teams) | After sibling repos configure |
| #138 (Node 20 deprecation) | Hard deadline 2026-09-16; not urgent yet | v2.51.x or earlier if CI starts warning |

---

## Documentation & Discoverability

- [ ] Tutorial: `docs/tutorials/TUTORIAL-homebrew-gates.md` (PR A)
- [ ] Tutorial: Update `docs/tutorials/TUTORIAL-insights-setup.md` with hook note (PR B)
- [ ] Command reference: `docs/commands/dist/homebrew.md` (PR A)
- [ ] Command reference: `docs/commands/workflow/insights.md` — fix false claim (PR B, or quick-win)
- [ ] ADR: `docs/adr/ADR-001-workflow-branch-guard.md` (quick-win on dev)
- [ ] REFCARD: Add gate flags section (PR A); add SessionStop note (PR B)
- [ ] CHANGELOG `[Unreleased]` entries for both PRs
- [ ] `validate-counts.sh` clean after each PR
- [ ] `docs-staleness-check.sh` clean after each PR
- [ ] Close issues: #200, #199 (PR A), #183 (PR B), #171 (ADR + comment)

---

## Agent Findings (incorporated)

### Homebrew Gate Analysis (agent 1)

**Step 10a gap confirmed**: The cask path already has `extract_changelog_items()` / `replace_caveats_bullets()` in `homebrew.md` Step 10b — but these were never wired into the formula path. The verify-caveats gate is the formula-path equivalent.

**Files to create/modify (refined):**

| File | Action | Notes |
|------|--------|-------|
| `scripts/verify_caveats.py` | Create | Generic checker; env overrides for testing |
| `scripts/verify-caveats.sh` | Create | Project-level wrapper; honors `HOMEBREW_GATE_STRICT` |
| `skills/release/SKILL.md` | Modify | Add Step 10a sub-gate (post-url/sha256, pre-tap-push) |
| `scripts/post-release-sweep.sh` | Modify | Add caveats staleness phase to sweep report |

**`verify_caveats.py` key signature:**

```python
def verify_caveats(formula_path, changelog_path, version,
                   strict=False, formula_name=None):
    """Returns (ok: bool, findings: list[str])"""
```

**Staleness detection scope**: Version string `New in vX.Y.Z:` present + managed bullet zone matches CHANGELOG items for this version. Scope is limited to "managed zone only" — no false positives on hand-customized static prose.

**Desktop/Cowork fix (Issue #199)**: Different problem from #200 — no brew caveats apply.

- **BLOCKING**: Enforce aggregator sync (`scripts/aggregator-sync.sh`) exits 0 before release proceeds (exit 1 on failure — prevents stale-version installs; per user decision)
- Fix: `claude plugin update <name>@local-plugins` (not bare name) — already in SKILL.md but not enforced; make it the only documented form
- Add: `--skip-brew` flag so Cowork-only release paths skip formula gates
- Synergy with Check 5: after aggregator sync, verify `claude plugin list` shows updated version

**Critical implementation risks (agent-identified):**

1. **Tap not locally checked out** — mirror `verify-surfaces.sh` absent-leg rule: warn only, never block (CI ubuntu runners have no local tap)
2. **Zone-marker drift** — if no `# --- dynamic bullets` markers exist, fall back to version-string check only; document this explicitly
3. **Empty CHANGELOG section** — `if not items: findings.append("no CHANGELOG entry for vX.Y.Z")` — fail loudly, not vacuously
4. **No count cascade** — `scripts/` is excluded from hub auto-discovery; no count bump needed

### SessionStop Hook Analysis (agent 2)

**Existing infrastructure to reuse:**

- `~/.claude/hooks/done-reminder.sh` — already a Stop hook; provides the exact stdin parsing pattern to clone
- `~/.claude/hooks/session-cleanup.sh` — shows Stop hook response format and `~/.claude/sessions/active/` for start-time
- Facet schema: `session-YYYYMMDD-HHMMSS.json` in `~/.claude/usage-data/facets/` (established, match exactly)

**Double-write guard**: Check `ls "$FACETS"/session-"$TODAY"-*.json` — if /done already ran, skip (same check `done-reminder.sh` uses).

**ADR directory**: `docs/adr/` does not exist — create it. `ADR-001-workflow-branch-guard.md` is the first entry.
