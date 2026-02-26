# Craft Plugin Testing Summary

**Version:** v2.28.0
**Date:** 2026-02-21
**Branch:** feature/claude-code-integration

---

## Overview

Comprehensive testing for the Craft plugin across three tiers: unit, e2e, and dogfood. All tests run via pytest with marker-based filtering.

---

## Test Suites

### Core Test Suites (62 tests, ~2.5s)

| Suite | File | Tests | Markers | Purpose |
|-------|------|-------|---------|---------|
| Unit | `test_craft_plugin.py` | 13 | `structure` | Plugin structure, counts, links |
| E2E | `test_plugin_e2e.py` | 21 | `e2e, structure` | Cross-component wiring |
| Dogfood | `test_plugin_dogfood.py` | 28 | `e2e, dogfood` | Real scripts against live repo |

### Feature Test Suites

| Suite | File | Tests | Markers | Purpose |
|-------|------|-------|---------|---------|
| Branch Guard | `test_branch_guard_dogfood.py` | ~30 | `e2e, branch_guard` | Hook behavior on real repo |
| Orchestrator | `test_orchestrator_dogfood.py` | ~10 | `e2e, orchestrator` | Orchestrator v2.1 features |
| Release Skill | `test_release_skill_dogfood.py` | ~15 | `e2e, release` | Release pipeline validation |
| Hub Discovery | `test_hub_discovery.py` | 12 | `integration, hub` | Auto-detection engine |
| Hub Layers | `test_hub_layer2.py`, `test_hub_layer3.py` | 15 | `integration, hub` | Category/detail views |
| Command E2E | `test_command_enhancements_e2e.py` | ~20 | `e2e, commands` | Interactive command patterns |

### CLI Test Suites

| Suite | File | Purpose |
|-------|------|---------|
| Automated | `tests/cli/automated-tests.sh` | CI-ready structure validation |
| Interactive | `tests/cli/interactive-tests.sh` | Human-guided QA |
| Marketplace | `tests/cli/marketplace-tests.sh` | Distribution validation |

---

## Quick Commands

```bash
# Core tests (~2.5s)
python3 -m pytest tests/test_craft_plugin.py tests/test_plugin_e2e.py tests/test_plugin_dogfood.py -v

# By tier
python3 -m pytest -m "structure"     # Unit (13 tests)
python3 -m pytest -m "e2e"           # E2E + dogfood (49 tests)
python3 -m pytest -m "dogfood"       # Dogfood only (28 tests)

# By domain
python3 -m pytest -m "branch_guard"  # Branch guard tests
python3 -m pytest -m "hub"           # Hub discovery tests
python3 -m pytest -m "orchestrator"  # Orchestrator tests

# Everything
python3 -m pytest tests/ -v

# CLI tests
bash tests/cli/automated-tests.sh
```

---

## Coverage by Component

| Component | Tests | Coverage |
|-----------|-------|----------|
| Plugin structure (plugin.json, dirs) | 13 unit + 4 dogfood | Full |
| Command frontmatter & discovery | 5 e2e + 2 dogfood | Full |
| Skill registration & triggers | 4 e2e + 1 dogfood | Full |
| Agent wiring | 2 e2e | Structural |
| Version consistency | 5 e2e + 2 dogfood | Full |
| Script syntax (all .sh) | 2 e2e | Full |
| Branch guard hook | 6 dogfood + ~30 dedicated | Full |
| Performance budgets | 2 dogfood | Sampled |
| validate-counts.sh | 2 dogfood | Full |
| pre-release-check.sh | 2 dogfood | Smoke |
| formatting.sh library | 3 dogfood | Full |
| mkdocs.yml | 3 e2e | Structural |
| Hub discovery engine | 12 integration | Full |
| Orchestrator v2.1 | ~10 dedicated | Functional |

---

## CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) auto-discovers all test files:

```yaml
- name: Run test suite
  run: python -m pytest tests/ -v --tb=short
```

CI-sensitive tests auto-detect `CI=true` and:

- Relax performance budgets (3x multiplier)
- Accept detached HEAD (no branch name)
- Skip tests requiring installed hooks

---

## Pytest Markers

Registered in `pyproject.toml`:

| Marker | Description |
|--------|-------------|
| `unit` | Pure function tests, no I/O |
| `integration` | Uses subprocess/filesystem |
| `e2e` | End-to-end against real project |
| `dogfood` | Self-validation with real scripts |
| `structure` | Plugin structure validation |
| `commands` | Command parsing/discovery |
| `skills` | Skill validation |
| `agents` | Agent configuration |
| `branch_guard` | Branch protection hooks |
| `orchestrator` | Orchestrator features |
| `hub` | Hub discovery/display |
| `release` | Release pipeline |

---

## Validation Scripts

| Script | Purpose | Used by |
|--------|---------|---------|
| `scripts/validate-counts.sh` | Command/skill/agent count consistency | Dogfood tests, CI |
| `scripts/pre-release-check.sh` | Version/count/doc alignment | Dogfood tests, release |
| `scripts/branch-guard.sh` | Branch protection hook | Dogfood tests, Claude Code |
| `scripts/formatting.sh` | Shared color/formatting library | All scripts |
| `scripts/health-check.sh` | Tool health validation | Manual |

---

**Last Updated:** 2026-02-20
**Status:** 62 core tests passing
