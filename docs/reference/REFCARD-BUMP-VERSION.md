# Quick Reference: bump-version.sh

**Atomic version + count sync across all project files** — prevents version drift between releases.

**Script:** `scripts/bump-version.sh` | **Helper:** `scripts/bump-version-helper.py`

---

## Quick Decision Tree

```text
Need to update version numbers?
|
+-- Releasing a new version?
|   +-- ./scripts/bump-version.sh 2.23.0
|
+-- Just want to preview changes?
|   +-- ./scripts/bump-version.sh 2.23.0 --dry-run
|
+-- Added new commands/skills/agents?
|   +-- ./scripts/bump-version.sh --counts-only
|
+-- Worried about drift?
|   +-- ./scripts/bump-version.sh --verify
|
+-- Not sure what's wrong?
    +-- ./scripts/bump-version.sh --verify (shows drift)
    +-- ./scripts/bump-version.sh <current-version> (fixes it)
```

---

## Usage

```bash
# Full bump: version + counts across all 9 files
./scripts/bump-version.sh 2.23.0

# Preview without writing
./scripts/bump-version.sh 2.23.0 --dry-run

# Sync counts only (after adding commands/skills/agents)
./scripts/bump-version.sh --counts-only

# Check for drift (CI-friendly: exit 0 = clean, exit 1 = drift)
./scripts/bump-version.sh --verify
```

---

## Files Updated (9)

| Category | File | What Changes |
|----------|------|-------------|
| JSON | `.claude-plugin/plugin.json` | `version`, description counts |
| JSON | `.claude-plugin/marketplace.json` | `metadata.version`, `plugins[0].version`, description counts |
| JSON | `package.json` | `version`, description counts |
| Text | `CLAUDE.md` | `Current Version: vX.Y.Z`, bold counts |
| Text | `README.md` | `version-X.Y.Z` badge, bold counts |
| Text | `docs/index.md` | Version badge, count strings |
| Text | `docs/REFCARD.md` | Header version (first 5 lines only) |
| Text | `mkdocs.yml` | `site_description` version + counts |
| Text | `.STATUS` | `version:` line, count string |

---

## Count Detection

Counts are auto-detected from the filesystem:

| Count | Detection |
|-------|-----------|
| Commands | `find commands -name "*.md"` (excluding index.md, README.md) |
| Skills | `find skills -name "*.md" -o -name "SKILL.md"` |
| Agents | `find agents -name "*.md"` |
| Specs | `find docs/specs -name "SPEC-*.md"` (excluding archive) |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or `--verify` found no drift) |
| 1 | Drift detected (`--verify` mode) |
| 2 | Usage error (bad args, conflicting flags) |

---

## Modes Compared

| Mode | Changes Files | Version | Counts | Use Case |
|------|:---:|:---:|:---:|------|
| `<version>` | Yes | Yes | Yes | Release prep |
| `<version> --dry-run` | No | -- | -- | Preview |
| `--counts-only` | Yes | No | Yes | After adding commands |
| `--verify` | No | -- | -- | CI check, pre-commit |

---

## Verify Mode Checks

`--verify` validates these consistency points:

| Check | Source | Expected |
|-------|--------|----------|
| JSON file versions | plugin.json, marketplace.json, package.json | All match `plugin.json` version |
| Description counts | `plugin.json` description field | Match filesystem counts |
| CLAUDE.md | `v{version}` pattern | Present |
| README.md | `version-{version}` badge | Present |
| mkdocs.yml | `v{version}` pattern | Present |
| .STATUS | `version: {version}` line | Present |

---

## Integration with Release Pipeline

`bump-version.sh` replaces manual file-by-file editing in Step 3 of `/release`:

```text
Step 2: Pre-flight checks pass
    |
Step 3: ./scripts/bump-version.sh <version>   <-- single command
    |
Step 4: git add <changed-files> && git commit
```

The release skill (`skills/release/SKILL.md`) calls this script automatically.

---

## Architecture

```text
bump-version.sh (orchestrator)
    |
    +-- formatting.sh (color output)
    |
    +-- bump-version-helper.py (JSON updates)
    |       Handles: plugin.json, marketplace.json, package.json
    |       Traverses nested keys: version, metadata.version, plugins[0].version
    |       Updates description count strings via regex
    |
    +-- sed (text file updates)
            Handles: CLAUDE.md, README.md, docs/index.md, docs/REFCARD.md,
                     mkdocs.yml, .STATUS
            Uses targeted patterns to avoid rewriting historical references
```

---

## Platform Note

Uses BSD `sed -i ''` (macOS). For GNU/Linux, change to `sed -i` (no empty string argument).

---

## See Also

- [Version Sync Architecture](../architecture/version-sync.md) — Three-layer drift prevention
- [Version Sync Setup Tutorial](../tutorials/TUTORIAL-version-sync-setup.md) — Hook installation
- [Release Pipeline Reference](REFCARD-RELEASE.md) — Full release workflow
- [pre-release-check.sh](../../scripts/pre-release-check.sh) — Release metadata validation
