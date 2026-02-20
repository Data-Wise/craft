# Craft Plugin Test Quick Reference

**TL;DR:** 62 core tests (13 unit + 21 e2e + 28 dogfood), all passing in ~2.5s

---

## Quick Commands

```bash
# Run all core tests (~2.5s)
python3 -m pytest tests/test_craft_plugin.py tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -v

# By tier
python3 -m pytest -m "structure"   # 13 unit tests (~0.1s)
python3 -m pytest -m "e2e"         # 49 e2e + dogfood tests (~2.5s)
python3 -m pytest -m "dogfood"     # 28 dogfood-only tests (~1.9s)

# Run everything (all test files)
python3 -m pytest tests/ -v

# Integration tests (individual features)
python3 -m pytest tests/test_integration_*.py -v
python3 -m pytest tests/test_branch_guard_dogfood.py -v
```

---

## Test Summary

| Suite | File | Tests | Time | What it validates |
|-------|------|-------|------|-------------------|
| **Unit** | `test_craft_plugin.py` | 13 | ~0.1s | Plugin structure, commands, skills, agents, links |
| **E2E** | `test_plugin_e2e.py` | 21 | ~0.6s | Cross-component wiring, version sync, frontmatter |
| **Dogfood** | `test_plugin_dogfood.py` | 28 | ~1.9s | Real scripts against live repo, performance budgets |
| **Total** | | **62** | **~2.5s** | |

---

## Test Tiers

### Unit Tests (test_craft_plugin.py) — 13 tests

Plugin structure validation:

- plugin.json exists, valid, has required fields
- Directory structure (commands/, skills/, agents/)
- Command count matches, all commands valid
- Command categories present
- Skills and agents exist
- No broken internal links
- Consistent naming conventions

### E2E Tests (test_plugin_e2e.py) — 21 tests

Cross-component integrity:

- **Version consistency**: plugin.json, CLAUDE.md, README all agree
- **Command frontmatter**: all commands have valid YAML with description
- **Skill integrity**: SKILL.md files have frontmatter, directories non-empty
- **Agent wiring**: orchestrator-v2 references real commands
- **Count accuracy**: plugin.json description counts match actual files
- **Cross-references**: no orphan skill references in commands
- **Docs site**: mkdocs.yml exists, valid, has nav entries
- **Script syntax**: all .sh files pass `bash -n`, have shebangs

### Dogfood Tests (test_plugin_dogfood.py) — 28 tests

Self-validation with real scripts:

- **validate-counts.sh**: exits 0, no mismatches
- **pre-release-check.sh**: runs, detects current version
- **Version sync**: version-sync.sh syntax, CLAUDE.md matches
- **formatting.sh**: sourceable, exports FMT_* color variables
- **Command discovery**: _discovery.py importable,_schema.json valid
- **Skill triggers**: no duplicate SKILL.md descriptions
- **Branch guard**: syntax valid, handles empty/invalid/valid JSON payloads
- **Performance**: validate-counts <5s, branch-guard <200ms (3x on CI)
- **Repo health**: valid branch type, no merge conflicts
- **Plugin schema**: required fields, author object, no unrecognized keys

---

## Pytest Markers

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Pure function/class tests | `pytest -m unit` |
| `integration` | Subprocess/filesystem tests | `pytest -m integration` |
| `e2e` | End-to-end against real project | `pytest -m e2e` |
| `dogfood` | Self-dogfooding with real scripts | `pytest -m dogfood` |
| `structure` | Plugin structure validation | `pytest -m structure` |
| `branch_guard` | Branch protection hook tests | `pytest -m branch_guard` |
| `orchestrator` | Orchestrator feature tests | `pytest -m orchestrator` |

---

## CI Integration

The CI workflow (`.github/workflows/ci.yml`) runs `python -m pytest tests/ -v --tb=short` which auto-discovers all test files. CI-sensitive tests auto-detect `CI=true` and relax performance budgets (3x multiplier).

---

## Adding New Tests

1. Create `tests/test_<feature>.py`
2. Add `pytestmark = [pytest.mark.<tier>, pytest.mark.<domain>]`
3. Use fixtures from `conftest.py` (`craft_root`, `temp_git_repo`, etc.)
4. Use helpers from `helpers.py` (`read_file`, `run_hook`, `init_repo`, etc.)
5. Run: `python3 -m pytest tests/test_<feature>.py -v`

---

**Last Updated:** 2026-02-20
