# SPEC: Plugin skill/command identity hardening (#316)

**Status:** GRILLED + ADVERSARIALLY REVIEWED — RE-SCOPED  
**Date:** 2026-07-27  
**Source issue:** [#316](https://github.com/Data-Wise/craft/issues/316)  
**Target:** `skills/**/SKILL.md`, command shims that collide with skill directory names,
skill-path references, and plugin-structure tests

## Final Scope (Post-Review)

| Item | Decision |
|---|---|
| `skills/check/` collision | **FIX NOW** — move to `skills/preflight-check/` |
| Structural recurrence guard | **FIX NOW** — fixture-backed inventory tests over all command depths and all skills |
| `brainstorm`, `grill`, `release` collisions | **BASELINE + PROBE** — exact temporary debt ledger owned by #316; no silent exemption |
| Eight remaining directory/frontmatter mismatches | **DEFER PUBLIC RENAMES** — baseline exactly; require a separate compatibility design after client-provenance probes |
| Original nine-directory normalization | **CUT** — unsafe: it changed public identities and `skills/code/` would have moved unrelated child skills |

The GRILL ledger records all ten review findings and the resulting scope changes:
`GRILL-plugin-skill-command-identity-hardening-2026-07-27.md`.

## Objective

Fix the confirmed `check` command/skill identity collision without changing `/craft:check`,
make every other current inconsistency explicit and mechanically bounded, and add structural
tests that prevent any new collision or directory/frontmatter mismatch.

Success means:

1. The canonical pre-flight skill is exposed as `preflight-check`, while `/craft:check`
   remains the user-facing slash command.
2. The complete current sets of command/skill collisions and directory/frontmatter mismatches
   are captured in exact, stale-detecting debt ledgers.
3. Any new inconsistency, removed inconsistency, or unowned exemption fails CI.
4. The changed worktree artifact, not a globally installed copy, is exercised in Claude Code
   and Codex with provenance evidence.
5. `/craft:check`'s complete frontmatter contract and representative modes remain unchanged.
6. `claude plugin validate .`, craft's plugin-structure tests, and the full test suite pass.

## Evidence Snapshot

Verified against `dev` at `1afdf1d83` (craft v4.4.1):

- `commands/check.md` and `skills/check/SKILL.md` both occupy the plugin identity `check`.
- `skills/check/SKILL.md` declares `name: preflight-check`.
- Current `claude plugin details craft@local-plugins` lists `check` twice but does not list
  `preflight-check`; `claude plugin validate .` passes without a warning.
- The repository contains nine leaf-directory/frontmatter mismatches:

| Current directory | Frontmatter `name:` |
|---|---|
| `skills/check/` | `preflight-check` |
| `skills/modes/` | `mode-controller` |
| `skills/ci/` | `project-detector` |
| `skills/planning/` | `project-planner` |
| `skills/code/` | `sync-features` |
| `skills/docs/claude-md/` | `claude-md-lifecycle` |
| `skills/architecture/` | `system-architect` |
| `skills/workflow/task-management/` | `background-task-manager` |
| `skills/dev/git/` | `git-workflow` |

- The repository contains four command/skill leaf-name collisions:

| Command | Skill directory | Current behavior |
|---|---|---|
| `commands/check.md` | `skills/check/` | Confirmed ambiguous; intended `preflight-check` identity absent |
| `commands/brainstorm.md` | `skills/workflow/brainstorm/` | Thin command shim explicitly loads the skill; direct Skill-tool behavior requires a focused probe |
| `commands/grill.md` | `skills/workflow/grill/` | Thin command shim explicitly loads the skill; direct Skill-tool behavior requires a focused probe |
| `commands/code/release.md` | `skills/release/` | Nested command/skill basename collision; direct Skill-tool behavior requires a focused probe |

- No existing test enforces either directory/frontmatter equality or command/skill namespace
  uniqueness.
- `skills/code/` is both a skill and a category containing three unrelated child skills. Moving
  the directory would change those child paths; only `skills/code/SKILL.md` could be moved
  independently.
- Existing craft docs state that nested skills may not appear in Claude Code's Skill-tool list.
  Directory/frontmatter equality therefore does not prove discovery or invocability.

## Assumptions

1. `/craft:check`, `/craft:brainstorm`, and `/craft:grill` remain stable user-facing slash
   commands.
2. `preflight-check` is the intended semantic identity because it is already the frontmatter
   name and documented skill name.
3. Claude Code and Codex may derive identity, discovery, auto-triggering, and explicit
   invocation from different metadata. Those are separate properties and must be measured,
   not inferred.
4. The eight non-`check` mismatches may represent public identities in one or both clients.
   They are not safe mechanical renames without a compatibility decision.

## Non-Goals

- Changing the behavior, output contract, or flags of `/craft:check`, `/craft:brainstorm`, or
  `/craft:grill`.
- Renaming any skill other than `preflight-check`.
- Resolving the `brainstorm`, `grill`, or `release` public identity in this implementation PR.
- Moving the eight remaining mismatched skills.
- Rewriting the pre-flight validator engine or changing counts.
- Depending on `claude plugin validate` to detect this class; it demonstrably does not today.
- Closing #316 without either resolving the three deferred collisions or creating owner-bound
  follow-up issues with explicit removal criteria.

## Decision Summary

### D1. Fix only the confirmed `check` collision

Rename:

```text
skills/check/ → skills/preflight-check/
```

Keep `commands/check.md` and `/craft:check` unchanged. Update the command shim's `replaced-by`
target and canonical-skill references to `skills/preflight-check/`.

This is the only confirmed user-impacting collision with a ready, already-established distinct
semantic name.

### D2. Replace generic allowlists with exact debt ledgers

Two fixture-tested ledgers capture the current unresolved state after the `check` move. Entries
use full command/skill paths, observed identity surfaces, and closure metadata; basenames alone
are insufficient because a moved or duplicated collision could otherwise pass unchanged.

```python
KNOWN_SKILL_NAME_MISMATCHES = {
    "skills/architecture/SKILL.md": {
        "frontmatter_name": "system-architect",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v4.5.0",
        "decision": "pending",  # must become retain, rename, or promote
        "removal_criterion": "directory/name equality or documented retain decision",
    },
    # Seven more entries with the same ownership schema.
}

KNOWN_COMMAND_SKILL_COLLISIONS = {
    ("commands/brainstorm.md", "skills/workflow/brainstorm/SKILL.md"): {
        "identity_surfaces": {"directory", "frontmatter"},
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v4.5.0",
        "decision": "pending",  # must become retain, rename, or promote
        "removal_criterion": "collision removed or documented retain decision",
    },
    # Equivalent full-path entries for grill and nested commands/code/release.md.
}
```

The tests compare actual state to these exact mappings. They fail on:

- a new mismatch or collision;
- a changed expected semantic name;
- a stale entry after remediation;
- a command hidden below a category directory, such as `commands/code/release.md`.

These mappings are debt ledgers, not claims of safety. Each entry must gain a dedicated issue
number and terminal decision before #316 closes. Fixture assertions enforce the exact schema:
`owner`, `owner_issue`, `target_release`, `decision`, and `removal_criterion`; `decision:
pending` fails the PR-handoff gate.

### D3. Test every command depth and every skill

Command discovery uses `commands/**/*.md` and compares each file's leaf stem. Skill discovery
uses every `skills/**/SKILL.md` and derives both:

- the parent-directory basename;
- the parsed frontmatter `name:`.

A collision record contains the full command path, full skill path, and the set of matching
identity surfaces (`directory`, `frontmatter`, or both). Flat-command-only discovery is
explicitly forbidden because it misses `commands/code/release.md`; directory-only comparison is
also forbidden because it misses future frontmatter-derived collisions.

Extract pure inventory helpers that accept a repository root. Permanent fixture tests exercise:

1. an unlisted mismatch;
2. an unlisted collision;
3. a stale mismatch-ledger entry;
4. a stale collision-ledger entry;
5. a nested command collision;
6. a command matching only a skill's frontmatter identity;
7. a duplicate or moved collision with the same basename but different full paths.

The fixture tests land first and remain in CI; planted defects are not temporary transcript-only
evidence.

### D4. Treat client behavior as a four-property matrix

For each affected identity, record separately:

| Property | Question |
|---|---|
| Identity | Which name does the client assign? |
| Discovery | Does the client list it? |
| Auto-trigger | Can natural language select it? |
| Explicit invocation | Can the Skill tool invoke it by name? |

The implementation probes `preflight-check`, `brainstorm`, `grill`, and `release` in both
clients. It must not infer one property from another or infer nested-skill behavior from a
top-level skill.

The Claude Code probe must answer:

1. Does direct Skill-tool invocation resolve the canonical skill or the command shim?
2. Does auto-triggering from natural language resolve the same artifact?
3. What does `claude plugin details` list for each collision?
4. Does the loaded artifact provenance point to the worktree?

The Codex probe records the same matrix for `craft:preflight-check`, `craft:brainstorm`,
`craft:grill`, and `craft:release`.

### D5. Lock `/craft:check`'s complete contract

Before the move, add a committed snapshot assertion for `commands/check.md`'s public argument
contract, covering all argument names, defaults, required flags, and aliases. The non-public
`replaced-by` field is allowed exactly one change: `skills/check/` to
`skills/preflight-check/`.

Add a normalized whole-file SHA-256 assertion: replace only the two canonical path spellings
with one sentinel before hashing. The normalized hash must remain unchanged, proving the body
diff contains no unrelated edits.

Manual QA exercises:

- default mode;
- `thorough`;
- `--for pr`;
- `--dry-run`;
- `--context`.

This separates behavior preservation from structural identity tests.

## Scope

### Implementation PR — `preflight-check` collision hotfix

#### File move

- `skills/check/` → `skills/preflight-check/`

The entire directory moves, including `references/gen-validator.md`.

#### Reference sweep

Update every tracked reference to `skills/check/`, including:

- `commands/check.md`
- `docs/skills-agents.md`
- `docs/commands.md`
- `docs/MIGRATION-v4.md`
- `CHANGELOG.md` and `docs/CHANGELOG.md`
- active and historical `docs/specs/*` references
- `scripts/deprecate-batch2-commands.py`

Historical prose may retain its historical statement, but its path must point at the current
canonical location. The current SPEC/GRILL pair and fixture tests intentionally retain the old
path as negative evidence. After the move, no runtime or live-documentation reference may
remain:

```bash
git grep -n 'skills/check' -- . \
  ':!docs/specs/SPEC-plugin-skill-command-identity-hardening-2026-07-27.md' \
  ':!docs/specs/GRILL-plugin-skill-command-identity-hardening-2026-07-27.md' \
  ':!tests/test_craft_plugin.py'
```

This command must return no tracked references. The structural fixture test separately asserts
that its intentional old-path example fails as expected.

#### Tests

- Add pure inventory helpers plus permanent fixture-based negative tests.
- Add the exact three-entry collision debt ledger (`brainstorm`, `grill`, `release`).
- Add the exact eight-entry mismatch debt ledger.
- Add positive and negative assertions for `skills/preflight-check/` and `skills/check/`.
- Snapshot the complete `/craft:check` frontmatter contract.
- Update any path-specific tests or fixtures found by the reference sweep.

### Compatibility follow-up — explicitly outside the implementation PR

Do not move the eight remaining mismatched skills in this spec's implementation PR. First
produce the two-client property matrix and decide whether each current directory identity or
frontmatter identity is public.

Important path constraint: `skills/code/` is a mixed category/skill directory. Any future
normalization must move only:

```text
skills/code/SKILL.md → skills/sync-features/SKILL.md
```

and leave `skills/code/audit-router/`, `skills/code/command-skill-token-efficiency/`, and
`skills/code/plugin-audit/` in place.

Before #316 closes:

1. File one or more follow-up issues covering the eight mismatches and the three deferred
   collisions.
2. Give every debt-ledger entry an owner issue and target release.
3. Record a terminal **retain**, **rename**, or **promote** decision for every entry, including
   compatibility/release classification and ledger removal or retention criteria.
4. Replace `owner_issue: "#316"` with the dedicated issue where one is created.

No identity migration may be described as mechanical until the client matrix proves it.

## Implementation Order

1. Record `claude --version`, `codex --version`, current identity listings, resolved plugin
   paths, and hashes as pre-change evidence.
2. Add pure inventory helpers and permanent fixture tests first.
3. Run the production-tree test and record the expected red result for the `check` collision.
4. Snapshot `/craft:check` frontmatter and body-path substitutions.
5. Move `skills/check/` to `skills/preflight-check/` and update tracked references.
6. Run targeted tests, plugin validation, full suite, and provenance-bound client QA.
7. Run the four-property probe for `brainstorm`, `grill`, and `release`.
8. File owner-bound follow-up issues and record terminal decisions for every deferred entry.
9. Replace placeholder debt-ledger ownership values, then open the implementation PR against
   `dev`.
10. Keep #316 open until the implementation PR merges and every deferred entry has a terminal
    retain/rename/promote decision.

## Testing Strategy

### Unit/structural

```bash
python3 -m pytest tests/test_craft_plugin.py -k "skill and (frontmatter or collision or directory)" -v
```

Tests use committed temporary-directory fixtures, not temporary edits to the production tree:

- A fixture with `commands/check.md` plus `skills/check/SKILL.md` fails as an unlisted
  collision.
- A fixture skill whose parent differs from `name:` fails as an unlisted mismatch.
- A fixture with a nested `commands/code/release.md` proves recursive command discovery.
- Removing a fixture inconsistency while retaining its debt-ledger entry fails as stale debt.
- A clean fixture passes with empty ledgers.

### Integration

```bash
claude plugin validate .
./scripts/validate-counts.sh
./scripts/docs-staleness-check.sh
python3 -m pytest tests/ -q
```

Expected counts remain 48 commands, 40 skills, and 2 agents.

### Manual QA

Test the exact worktree artifact, never the globally installed plugin.

Before either client probe:

```bash
test -z "$(git status --porcelain)"
QA_SHA="$(git rev-parse HEAD)"
git archive "$QA_SHA" | shasum -a 256
```

QA runs only on a committed, clean tree. Record `QA_SHA` and the whole-archive hash; a single
`SKILL.md` hash is supplemental, not sufficient provenance.

**Claude Code staging**

```bash
WT=/absolute/path/to/worktree
QA_HOME="$(mktemp -d)"
CLAUDE_CONFIG_DIR="$QA_HOME/claude" claude -p \
  --plugin-dir "$WT" \
  --setting-sources "" \
  "Use the preflight-check skill, report its resolved SKILL.md path, then run /craft:check --context"
```

Record `claude --version`, the resolved `SKILL.md` path, and:

```bash
shasum -a 256 "$WT/skills/preflight-check/SKILL.md"
```

The transcript must resolve under `$WT`, not `~/.claude/plugins/cache/`.

**Codex staging**

Create a disposable local marketplace whose `craft` entry uses `source: "./craft"`, populate
its `craft/` directory from `git archive "$QA_SHA"`, write `QA_SHA` and the archive hash into
the QA record, then:

```bash
CODEX_HOME="$QA_HOME/codex" codex plugin marketplace add "$QA_HOME/marketplace"
CODEX_HOME="$QA_HOME/codex" codex plugin add craft@data-wise-craft
CODEX_HOME="$QA_HOME/codex" codex exec -C "$WT" \
  "Use craft:preflight-check and report the resolved SKILL.md path."
```

Record `codex --version`, the staged plugin path, staged commit SHA, whole-archive hash, and the
staged `SKILL.md` hash. The staged SHA and both hashes must equal the clean worktree record.

**Behavior matrix**

Exercise default, `thorough`, `--for pr`, `--dry-run`, and `--context` through `/craft:check`.
Probe `brainstorm`, `grill`, and `release` separately in both clients; do not infer nested-skill
behavior from `preflight-check`.

## Documentation

Update:

- `docs/skills-agents.md` skill names and canonical paths
- `commands/check.md` delegation path
- `docs/commands.md` migration note
- `docs/MIGRATION-v4.md`
- root and docs changelog `[Unreleased]` sections
- path references found by `git grep`

No count cascade is expected because no skill or command is added or removed.
Do not update documentation for the eight deferred identities as though their rename were
decided.

## Boundaries

### Always

- Preserve the existing frontmatter semantic names.
- Move reference subdirectories atomically with their parent skill.
- Update every tracked old-path reference in the same PR as its directory move.
- Verify the staged worktree artifact in both Claude Code and Codex.
- Keep permanent fixture tests for every negative condition.
- Discover commands recursively under `commands/`.
- Treat identity, discovery, auto-triggering, and explicit invocation separately.

### Ask first

- Renaming the public `brainstorm` or `grill` skill identities.
- Renaming the public `release` skill identity.
- Moving any of the eight deferred mismatched skills.
- Removing either slash-command shim.
- Adding any debt-ledger entry without an owner issue and removal criterion.

### Never

- Change frontmatter names merely to satisfy a directory equality test.
- Add duplicate alias skill directories; that recreates ambiguous discovery and changes the
  skill count.
- Treat `claude plugin validate` passing as proof that routing is correct.
- Rewrite command behavior as part of the path migration.
- Rename the whole `skills/code/` category.
- Inspect the global plugin install and claim it represents the worktree.
- Close #316 before `brainstorm`, `grill`, and `release` have owner-bound terminal decisions.

## Acceptance Criteria

### Implementation PR

- [ ] `skills/preflight-check/SKILL.md` exists with `name: preflight-check`.
- [ ] `skills/check/` no longer exists.
- [ ] No runtime or live-documentation `skills/check` references remain under the explicit
  SPEC/GRILL/test exclusions.
- [ ] `/craft:check`'s public argument snapshot is unchanged; only `replaced-by` changes.
- [ ] The normalized whole-command hash is unchanged, proving no unrelated body edits.
- [ ] Default, `thorough`, `--for pr`, `--dry-run`, and `--context` behavior pass.
- [ ] Claude Code loads `preflight-check` from the staged worktree.
- [ ] Codex loads `craft:preflight-check` from the disposable staged installation whose
  recorded SHA and archive hash match the clean worktree commit.
- [ ] QA runs at a committed, clean `QA_SHA`; staged SHA and whole-archive hashes match.
- [ ] Recursive collision inventory finds `brainstorm`, `grill`, and nested `release`.
- [ ] Collision records contain full command/skill paths and matching identity surfaces.
- [ ] Exact debt ledgers contain eight mismatches and three collisions with owner, target, and
  removal metadata.
- [ ] Fixture tests fail for new inconsistency, nested collision, frontmatter-only collision,
  moved/duplicated collision, and stale debt.
- [ ] Targeted tests, full suite, plugin validation, counts, and docs-staleness checks pass.

### Follow-up ownership

- [ ] `brainstorm`, `grill`, and `release` are probed independently in both clients.
- [ ] Every collision and mismatch has an explicit retain/rename/promote decision matrix.
- [ ] Every deferred item has an issue, owner, target release, and debt-ledger removal
  criterion.
- [ ] #316 remains open until the hotfix merges and every deferred item has a terminal
  retain/rename/promote decision.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Directory move breaks the check shim | Exhaustive `git grep`, command snapshot, behavior matrix |
| Deferred public identities drift further | Exact stale-detecting debt ledgers block new or changed debt |
| Historical docs retain dead paths | Zero-old-path acceptance check across all tracked files |
| Collision ledger becomes permanent debt | Owner issue, target release, removal criterion, stale-entry failure |
| Claude Code behavior changes between versions | Record client version, resolved path, and artifact hash |
| QA uses stale global install | Disposable Claude config and Codex marketplace staging |
| Tests pass vacuously | Permanent fixture negatives for every invariant branch |
| Future work moves unrelated code children | Record `skills/code/SKILL.md` as a file-only move constraint |

## Open Questions

None are load-bearing for the implementation PR. Public identity migrations are deliberately
deferred to owner-bound follow-up issues after the client matrix is recorded.
