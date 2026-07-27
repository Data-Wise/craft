#!/usr/bin/env python3
"""
Craft Plugin Automated Test Suite
==================================
Validates the craft plugin structure, commands, skills, and agents.

Run with: python tests/test_craft_plugin.py
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import pytest
import yaml

# Add utils directory to path for linkcheck_ignore_parser
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

pytestmark = [pytest.mark.integration, pytest.mark.structure]

PLUGIN_DIR = Path(__file__).parent.parent


# ─── Plugin Structure Tests ──────────────────────────────────────────────────


def test_plugin_json_exists():
    """Test that plugin.json exists and is valid."""
    plugin_dir = Path(__file__).parent.parent
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"

    assert plugin_json.exists(), f"Missing: {plugin_json}"

    data = json.load(open(plugin_json))

    # Check required fields
    required = ["name", "version", "description", "author"]
    missing = [f for f in required if f not in data]
    assert not missing, f"Missing fields: {missing}"

    # Check author is object
    assert isinstance(data.get("author"), dict), \
        "author must be an object with 'name' field"


def test_directory_structure():
    """Test that required directories exist."""
    plugin_dir = Path(__file__).parent.parent
    required_dirs = ["commands", "skills", "agents", ".claude-plugin"]

    missing = []
    for d in required_dirs:
        if not (plugin_dir / d).is_dir():
            missing.append(d)

    assert not missing, f"Missing directories: {missing}"


def test_all_pytest_marks_are_registered():
    """Every ``pytest.mark.<name>`` used in tests/ must be registered in pyproject.toml.

    Guards against the unregistered-marker class of CI failure: pytest runs
    with --strict-markers, so a mark that exists in a test file but not in
    pyproject's markers list hard-errors at collection time (CI-only flake,
    e.g. the mermaid markers that forced an --admin merge in v2.36.0).
    """
    try:
        import tomllib  # Python 3.11+ stdlib
    except ModuleNotFoundError:  # pragma: no cover - older interpreters only
        import tomli as tomllib

    # Built-in pytest marks are never listed in pyproject's markers list.
    BUILTIN_MARKS = {
        "parametrize", "skipif", "xfail", "skip", "filterwarnings", "usefixtures",
    }

    pyproject = PLUGIN_DIR / "pyproject.toml"
    assert pyproject.exists(), f"Missing: {pyproject}"
    with open(pyproject, "rb") as fh:
        config = tomllib.load(fh)
    raw_markers = config["tool"]["pytest"]["ini_options"]["markers"]
    # Each entry is "name: description"; the canonical name is before the colon.
    registered = {entry.split(":", 1)[0].strip() for entry in raw_markers}

    tests_dir = PLUGIN_DIR / "tests"
    used: dict[str, list[str]] = {}
    for py_file in sorted(tests_dir.glob("*.py")):
        text = py_file.read_text(encoding="utf-8")
        for mark in re.findall(r"pytest\.mark\.(\w+)", text):
            if mark in BUILTIN_MARKS:
                continue
            used.setdefault(mark, []).append(py_file.name)

    unregistered = {m: files for m, files in used.items() if m not in registered}
    if unregistered:
        detail = "\n".join(
            f"  - {mark!r} used in: {', '.join(sorted(set(files)))}"
            for mark, files in sorted(unregistered.items())
        )
        raise AssertionError(
            "Unregistered pytest marks (add to pyproject.toml [tool.pytest.ini_options].markers, "
            "or CI --strict-markers will hard-error at collection):\n" + detail
        )


def test_readme_exists():
    """Test that README.md exists."""
    plugin_dir = Path(__file__).parent.parent
    readme = plugin_dir / "README.md"

    assert readme.exists(), "Missing README.md"


# ─── Command Tests ───────────────────────────────────────────────────────────


def find_all_commands() -> list[Path]:
    """Find all command markdown files."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"
    return list(commands_dir.rglob("*.md"))


def test_command_count():
    """Test that we have expected number of commands."""
    commands = find_all_commands()

    # We expect at least 15 commands based on the structure
    min_expected = 15

    assert len(commands) >= min_expected, \
        f"Found {len(commands)} commands, expected at least {min_expected}"


def validate_command_file(cmd_path: Path) -> tuple[bool, str]:
    """Validate a single command file."""
    try:
        content = cmd_path.read_text()

        # Check it's not empty
        if len(content.strip()) < 10:
            return False, "File is empty or too short"

        # Check for basic markdown structure
        if not content.startswith("#"):
            # Some commands might not start with # but should have content
            if len(content) < 50:
                return False, "Missing header or insufficient content"

        return True, "Valid"

    except Exception as e:
        return False, f"Error reading: {e}"


def test_all_commands_valid():
    """Test that all command files are valid."""
    commands = find_all_commands()
    invalid = []

    for cmd in commands:
        valid, msg = validate_command_file(cmd)
        if not valid:
            relative = cmd.relative_to(Path(__file__).parent.parent)
            invalid.append(f"{relative}: {msg}")

    assert not invalid, \
        f"Invalid commands: {invalid[:3]}{'...' if len(invalid) > 3 else ''}"


def test_command_categories():
    """Test that commands are organized in categories."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"

    # Expected categories
    expected = ["code", "docs", "git", "site"]
    missing = []

    for cat in expected:
        cat_dir = commands_dir / cat
        if not cat_dir.is_dir():
            missing.append(cat)

    assert not missing, f"Missing categories: {missing}"


def test_hub_command_exists():
    """Test that the main hub command exists."""
    plugin_dir = Path(__file__).parent.parent
    hub = plugin_dir / "commands" / "hub.md"

    assert hub.exists(), "Missing commands/hub.md"


# ─── Skills Tests ────────────────────────────────────────────────────────────


def find_all_skills() -> list[Path]:
    """Find all skill markdown files."""
    plugin_dir = Path(__file__).parent.parent
    skills_dir = plugin_dir / "skills"
    return list(skills_dir.rglob("*.md"))


def test_skills_exist():
    """Test that skills are defined."""
    skills = find_all_skills()

    assert len(skills) > 0, "No skills found"


def test_skill_count_predicates_use_canonical_marker():
    """Regression: utilities counting skills must use `find skills -name SKILL.md`.

    The pattern `find skills -name "*.md" -o -name "SKILL.md"` (or just `*.md`)
    over-counts because every SKILL.md matches `*.md` and any non-canonical .md
    in skill subtrees (references, NOTES) leaks in. This bug recurred 11 times
    across utilities. Lock the canonical predicate in.

    Exempts docs-staleness-check.sh:406 which intentionally lists ALL .md files
    in skills/ for coverage analysis (not a count).
    """
    plugin_dir = Path(__file__).parent.parent
    bad_pattern = re.compile(r'SKILL_COUNT=.*find\s+skills\s+-name\s+"\*\.md"')
    offenders: list[str] = []
    for path in [*plugin_dir.glob("scripts/*.sh"), *plugin_dir.rglob("commands/**/*.md")]:
        try:
            for i, line in enumerate(path.read_text().splitlines(), 1):
                if bad_pattern.search(line):
                    offenders.append(f"{path.relative_to(plugin_dir)}:{i}: {line.strip()}")
        except (OSError, UnicodeDecodeError):
            continue
    assert not offenders, (
        "Found utilities counting skills with `*.md` instead of `SKILL.md` "
        "(over-counts non-canonical files):\n  " + "\n  ".join(offenders)
    )


def test_design_skills():
    """Test that design skills are present."""
    plugin_dir = Path(__file__).parent.parent
    design_dir = plugin_dir / "skills" / "design"

    expected = ["backend-designer", "frontend-designer", "devops-helper"]
    missing = []

    for skill in expected:
        if not (design_dir / skill / "SKILL.md").exists():
            missing.append(skill)

    assert not missing, f"Missing: {missing}"


def test_prompt_refiner_skill_exists():
    """The shared prompt-refiner skill must exist with valid frontmatter."""
    skill = PLUGIN_DIR / "skills" / "workflow" / "prompt-refiner" / "SKILL.md"
    assert skill.exists(), "skills/workflow/prompt-refiner/SKILL.md missing"
    fm = _parse_skill_frontmatter(skill)
    assert fm is not None, "prompt-refiner SKILL.md has no parseable frontmatter"
    assert fm.get("name") == "prompt-refiner"
    assert "description" in fm


KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def find_all_skill_md() -> list[Path]:
    """Find all SKILL.md files under skills/ (any depth)."""
    plugin_dir = Path(__file__).parent.parent
    skills_dir = plugin_dir / "skills"
    return list(skills_dir.rglob("SKILL.md"))


def _parse_skill_frontmatter(skill_path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from a SKILL.md file. Returns dict or None."""
    content = skill_path.read_text()
    if not content.startswith("---"):
        return None
    # Split on the closing --- marker
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


IDENTITY_DEBT_FIELDS = {
    "owner",
    "owner_issue",
    "target_release",
    "decision",
    "removal_criterion",
}
TERMINAL_IDENTITY_DECISIONS = {"retain", "rename", "promote"}

KNOWN_SKILL_NAME_MISMATCHES = {
    "skills/architecture/SKILL.md": {
        "frontmatter_name": "system-architect",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/ci/SKILL.md": {
        "frontmatter_name": "project-detector",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/code/SKILL.md": {
        "frontmatter_name": "sync-features",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Move only this file, never the skills/code category tree.",
    },
    "skills/dev/git/SKILL.md": {
        "frontmatter_name": "git-workflow",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/docs/claude-md/SKILL.md": {
        "frontmatter_name": "claude-md-lifecycle",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/modes/SKILL.md": {
        "frontmatter_name": "mode-controller",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/planning/SKILL.md": {
        "frontmatter_name": "project-planner",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
    "skills/workflow/task-management/SKILL.md": {
        "frontmatter_name": "background-task-manager",
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Revisit only in a breaking cross-client identity migration.",
    },
}

KNOWN_COMMAND_SKILL_COLLISIONS = {
    ("commands/brainstorm.md", "skills/workflow/brainstorm/SKILL.md"): {
        "identity_surfaces": {"directory", "frontmatter"},
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Command remains the public shim and must delegate to this skill.",
    },
    ("commands/code/release.md", "skills/release/SKILL.md"): {
        "identity_surfaces": {"directory", "frontmatter"},
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Command remains the project-type shim and must delegate to this skill.",
    },
    ("commands/grill.md", "skills/workflow/grill/SKILL.md"): {
        "identity_surfaces": {"directory", "frontmatter"},
        "owner": "@Data-Wise",
        "owner_issue": "#316",
        "target_release": "v5.0.0",
        "decision": "retain",
        "removal_criterion": "Command remains the public shim and must delegate to this skill.",
    },
}


def _discover_identity_debt(
    plugin_root: Path,
) -> tuple[dict[str, str], dict[tuple[str, str], set[str]]]:
    skills = []
    for skill_path in sorted((plugin_root / "skills").rglob("SKILL.md")):
        frontmatter = _parse_skill_frontmatter(skill_path)
        if frontmatter is None:
            continue
        frontmatter_name = frontmatter.get("name")
        if not isinstance(frontmatter_name, str):
            continue
        skills.append(
            (
                skill_path,
                skill_path.parent.name,
                frontmatter_name,
            )
        )

    mismatches = {
        skill_path.relative_to(plugin_root).as_posix(): frontmatter_name
        for skill_path, directory_name, frontmatter_name in skills
        if directory_name != frontmatter_name
    }

    collisions: dict[tuple[str, str], set[str]] = {}
    for command_path in sorted((plugin_root / "commands").rglob("*.md")):
        command_frontmatter = _parse_skill_frontmatter(command_path)
        if command_frontmatter is None or "description" not in command_frontmatter:
            continue
        command_name = command_path.stem
        for skill_path, directory_name, frontmatter_name in skills:
            surfaces = set()
            if command_name == directory_name:
                surfaces.add("directory")
            if command_name == frontmatter_name:
                surfaces.add("frontmatter")
            if surfaces:
                key = (
                    command_path.relative_to(plugin_root).as_posix(),
                    skill_path.relative_to(plugin_root).as_posix(),
                )
                collisions[key] = surfaces

    return mismatches, collisions


def _assert_identity_debt_matches(
    plugin_root: Path,
    expected_mismatches: dict,
    expected_collisions: dict,
) -> None:
    mismatches, collisions = _discover_identity_debt(plugin_root)
    expected_mismatch_names = {
        path: metadata["frontmatter_name"]
        for path, metadata in expected_mismatches.items()
    }
    expected_collision_surfaces = {
        paths: set(metadata["identity_surfaces"])
        for paths, metadata in expected_collisions.items()
    }

    assert mismatches == expected_mismatch_names
    assert collisions == expected_collision_surfaces

    for ledger in (expected_mismatches, expected_collisions):
        for key, metadata in ledger.items():
            missing = IDENTITY_DEBT_FIELDS - metadata.keys()
            assert not missing, f"{key}: missing identity-debt metadata: {sorted(missing)}"
            for field in IDENTITY_DEBT_FIELDS:
                assert isinstance(metadata[field], str) and metadata[field].strip(), (
                    f"{key}: {field} must be a non-empty string"
                )
            assert metadata["decision"] in TERMINAL_IDENTITY_DECISIONS, (
                f"{key}: identity debt must have a terminal decision"
            )


def _write_test_skill(path: Path, name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: Fixture skill for identity tests.\n---\n\n"
        "# Fixture\n\nFixture body with enough content for discovery.\n"
    )


def _write_test_command(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\ndescription: Fixture command for identity tests.\n---\n\n# Fixture\n"
    )


def test_plugin_identity_debt_matches_owned_ledgers():
    _assert_identity_debt_matches(
        PLUGIN_DIR,
        KNOWN_SKILL_NAME_MISMATCHES,
        KNOWN_COMMAND_SKILL_COLLISIONS,
    )
    for command_path, skill_path in KNOWN_COMMAND_SKILL_COLLISIONS:
        assert skill_path in (PLUGIN_DIR / command_path).read_text()


def test_identity_debt_detects_nested_and_frontmatter_only_collisions(tmp_path):
    _write_test_command(tmp_path / "commands" / "code" / "release.md")
    _write_test_skill(tmp_path / "skills" / "pipeline" / "SKILL.md", "release")

    mismatches, collisions = _discover_identity_debt(tmp_path)

    assert mismatches == {"skills/pipeline/SKILL.md": "release"}
    assert collisions == {
        ("commands/code/release.md", "skills/pipeline/SKILL.md"): {"frontmatter"},
    }


def test_identity_debt_detects_moved_duplicate_and_stale_entries(tmp_path):
    _write_test_command(tmp_path / "commands" / "check.md")
    _write_test_skill(tmp_path / "skills" / "check" / "SKILL.md", "preflight-check")
    expected_mismatches = {
        "skills/check/SKILL.md": {
            "frontmatter_name": "preflight-check",
            "owner": "@Data-Wise",
            "owner_issue": "#316",
            "target_release": "v4.4.2",
            "decision": "rename",
            "removal_criterion": "Move to skills/preflight-check.",
        }
    }
    expected_collisions = {
        ("commands/check.md", "skills/check/SKILL.md"): {
            "identity_surfaces": {"directory"},
            "owner": "@Data-Wise",
            "owner_issue": "#316",
            "target_release": "v4.4.2",
            "decision": "rename",
            "removal_criterion": "Move to skills/preflight-check.",
        }
    }
    _assert_identity_debt_matches(tmp_path, expected_mismatches, expected_collisions)

    moved_skill = tmp_path / "skills" / "moved" / "SKILL.md"
    moved_skill.parent.mkdir(parents=True)
    (tmp_path / "skills" / "check" / "SKILL.md").rename(moved_skill)
    with pytest.raises(AssertionError):
        _assert_identity_debt_matches(tmp_path, expected_mismatches, expected_collisions)

    moved_skill.unlink()
    with pytest.raises(AssertionError):
        _assert_identity_debt_matches(tmp_path, expected_mismatches, expected_collisions)


EXPECTED_CHECK_ARGUMENTS = [
    {"name": "mode", "description": "Check depth (default|thorough)", "required": False, "default": "default"},
    {"name": "for", "description": "What to check for (commit|pr|release|deploy)", "required": False},
    {
        "name": "dry-run",
        "description": "Preview checks that will be performed without executing them",
        "required": False,
        "default": False,
        "alias": "-n",
    },
    {
        "name": "orch",
        "description": "Enable orchestration mode (NEW in v2.5.0)",
        "required": False,
        "default": False,
    },
    {
        "name": "orch-mode",
        "description": "Orchestration mode: default|debug|optimize|release (NEW in v2.5.0)",
        "required": False,
        "default": None,
    },
    {
        "name": "context",
        "description": "Output session context header only (no checks)",
        "required": False,
        "default": False,
    },
    {
        "name": "version",
        "description": (
            "Run version sync validator only (Tier 1 files: plugin.json + 12 mechanically-synced refs). "
            "Use mode=thorough for Tier 2 sweep, mode=release for fatal-on-drift (NEW in v2.33.0)"
        ),
        "required": False,
        "default": False,
    },
]
EXPECTED_NORMALIZED_CHECK_SHA256 = "acee38d9d482bf8a80cf3fbe058efc861bb5467ef90bd48ad4df45b8e4fdc31f"


def test_check_command_contract_only_changes_canonical_skill_path():
    check_path = PLUGIN_DIR / "commands" / "check.md"
    content = check_path.read_text()
    frontmatter = _parse_skill_frontmatter(check_path)

    assert frontmatter is not None
    assert frontmatter["arguments"] == EXPECTED_CHECK_ARGUMENTS
    assert frontmatter["replaced-by"] == "skills/preflight-check/"
    assert "skills/check/" not in content

    normalized = content.replace(
        "skills/preflight-check/",
        "skills/__CHECK_SKILL__/",
    )
    digest = hashlib.sha256(normalized.encode()).hexdigest()
    assert digest == EXPECTED_NORMALIZED_CHECK_SHA256


def test_no_live_legacy_check_skill_references():
    allowed = {
        Path("docs/specs/GRILL-plugin-skill-command-identity-hardening-2026-07-27.md"),
        Path("docs/specs/SPEC-plugin-skill-command-identity-hardening-2026-07-27.md"),
    }
    extensions = {".json", ".md", ".py", ".sh", ".yaml", ".yml"}
    stale_references = []

    for path in PLUGIN_DIR.rglob("*"):
        if (
            not path.is_file()
            or path.suffix not in extensions
            or path.relative_to(PLUGIN_DIR) in allowed
            or "tests" in path.relative_to(PLUGIN_DIR).parts
        ):
            continue
        if "skills/check/" in path.read_text(errors="replace"):
            stale_references.append(str(path.relative_to(PLUGIN_DIR)))

    assert stale_references == []


def test_preflight_check_skill_has_unambiguous_identity():
    canonical = PLUGIN_DIR / "skills" / "preflight-check" / "SKILL.md"
    legacy = PLUGIN_DIR / "skills" / "check"

    assert canonical.exists()
    assert not legacy.exists()
    frontmatter = _parse_skill_frontmatter(canonical)
    assert frontmatter is not None
    assert frontmatter.get("name") == "preflight-check"


def test_all_skills_have_valid_frontmatter():
    """Every SKILL.md must have YAML frontmatter with name + description."""
    plugin_dir = Path(__file__).parent.parent
    skills = find_all_skill_md()
    assert skills, "No SKILL.md files found under skills/"

    errors = []
    for skill_path in skills:
        rel = skill_path.relative_to(plugin_dir)
        fm = _parse_skill_frontmatter(skill_path)
        if fm is None:
            errors.append(f"{rel}: missing or unparseable YAML frontmatter")
            continue

        name = fm.get("name")
        description = fm.get("description")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"{rel}: missing or empty 'name' field")
        elif not KEBAB_CASE_RE.match(name):
            errors.append(f"{rel}: 'name' is not kebab-case: {name!r}")

        if not isinstance(description, str) or not description.strip():
            errors.append(f"{rel}: missing or empty 'description' field")

    assert not errors, "Invalid skill frontmatter:\n  " + "\n  ".join(errors)


def test_skill_trigger_phrases_unique():
    """Quoted trigger phrases in skill descriptions must not collide across skills."""
    plugin_dir = Path(__file__).parent.parent
    skills = find_all_skill_md()
    assert skills, "No SKILL.md files found under skills/"

    # Extract phrases inside single or double quotes
    quote_pattern = re.compile(r'"([^"]+)"|\'([^\']+)\'')

    phrase_to_skills: dict[str, list[str]] = {}
    for skill_path in skills:
        rel = str(skill_path.relative_to(plugin_dir))
        fm = _parse_skill_frontmatter(skill_path)
        if fm is None:
            continue
        description = fm.get("description", "")
        if not isinstance(description, str):
            continue
        for m in quote_pattern.finditer(description):
            phrase = (m.group(1) or m.group(2) or "").strip().lower()
            if not phrase:
                continue
            phrase_to_skills.setdefault(phrase, []).append(rel)

    collisions = {
        phrase: sorted(set(owners))
        for phrase, owners in phrase_to_skills.items()
        if len(set(owners)) >= 2
    }

    if collisions:
        lines = [f"  {phrase!r} claimed by: {owners}" for phrase, owners in collisions.items()]
        raise AssertionError("Duplicate trigger phrases across skills:\n" + "\n".join(lines))


def test_skill_bodies_non_trivial():
    """Every SKILL.md must have a non-trivial body after the frontmatter."""
    plugin_dir = Path(__file__).parent.parent
    skills = find_all_skill_md()
    errors = []
    for skill_path in skills:
        rel = str(skill_path.relative_to(plugin_dir))
        text = skill_path.read_text()
        # Strip frontmatter block
        if text.startswith("---"):
            end = text.find("\n---", 3)
            body = text[end + 4:] if end != -1 else ""
        else:
            body = text
        # Body must have at least 200 non-whitespace chars (heuristic for "real content")
        if len(body.strip()) < 200:
            errors.append(f"{rel}: body too short ({len(body.strip())} chars; need >= 200)")
    assert not errors, "Trivial skill bodies:\n  " + "\n  ".join(errors)


def test_deprecated_commands_have_replacement():
    """Commands with `deprecated: true` must also declare `replaced-by:` pointing to a real skill dir."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"
    if not commands_dir.exists():
        pytest.skip("No commands directory")
    errors = []
    for cmd_path in commands_dir.rglob("*.md"):
        text = cmd_path.read_text()
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        try:
            fm = yaml.safe_load(text[3:end])
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict) or not fm.get("deprecated"):
            continue
        replaced_by = fm.get("replaced-by")
        rel = str(cmd_path.relative_to(plugin_dir))
        if not replaced_by:
            errors.append(f"{rel}: deprecated but missing replaced-by")
            continue
        if not isinstance(replaced_by, str) or not replaced_by.startswith("skills/"):
            errors.append(f"{rel}: replaced-by must point under skills/ (got: {replaced_by!r})")
            continue
        target = plugin_dir / replaced_by.rstrip("/")
        if not target.exists():
            errors.append(f"{rel}: replaced-by target does not exist: {replaced_by}")
    assert not errors, "Deprecated command issues:\n  " + "\n  ".join(errors)


def test_skill_referenced_commands_exist():
    """Commands referenced by SKILL.md as `commands/X.md` paths must exist on disk."""
    plugin_dir = Path(__file__).parent.parent
    skills = find_all_skill_md()
    # Match `commands/<path>.md` references in skill bodies (code or prose).
    # Skip glob patterns (containing `*`) — those are shorthand for sets.
    cmd_ref_pattern = re.compile(r"`(commands/[^`\s]+\.md)`")
    errors = []
    for skill_path in skills:
        rel = str(skill_path.relative_to(plugin_dir))
        text = skill_path.read_text()
        for match in cmd_ref_pattern.finditer(text):
            ref = match.group(1)
            if "*" in ref:
                continue
            target = plugin_dir / ref
            if not target.exists():
                errors.append(f"{rel} references missing: {ref}")
    assert not errors, "Skills reference non-existent commands:\n  " + "\n  ".join(errors)


# ─── Agents Tests ────────────────────────────────────────────────────────────


def find_all_agents() -> list[Path]:
    """Find all agent markdown files."""
    plugin_dir = Path(__file__).parent.parent
    agents_dir = plugin_dir / "agents"
    return list(agents_dir.rglob("*.md"))


def test_agents_exist():
    """Test that agents are defined."""
    agents = find_all_agents()

    assert len(agents) > 0, "No agents found"


def test_orchestrator_agent():
    """Test that the orchestrator agent exists."""
    plugin_dir = Path(__file__).parent.parent
    orchestrator = plugin_dir / "agents" / "orchestrator.md"

    assert orchestrator.exists(), "Missing agents/orchestrator.md"


# ─── Integration Tests ───────────────────────────────────────────────────────


def test_no_broken_links():
    """Test for broken internal links in markdown files.

    NOTE: docs/test-violations.md is intentionally excluded from this test.
    That file contains broken links used to test the .linkcheck-ignore parser
    and link validation system. See .linkcheck-ignore for the list of expected
    broken links.

    Uses .linkcheck-ignore file to filter out documented/expected broken links.
    """
    plugin_dir = Path(__file__).parent.parent

    # Load ignore rules from .linkcheck-ignore
    try:
        from linkcheck_ignore_parser import parse_linkcheck_ignore
        ignore_rules = parse_linkcheck_ignore(str(plugin_dir / ".linkcheck-ignore"))
    except ImportError:
        ignore_rules = None

    all_md = list(plugin_dir.rglob("*.md"))

    broken = []
    ignored = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)

    for md_file in all_md:
        # Skip test files, node_modules, and test-violations.md (intentional broken links)
        if "node_modules" in str(md_file) or "tests" in str(md_file) or "test-violations" in str(md_file):
            continue

        try:
            content = md_file.read_text()

            # Remove code blocks to avoid matching example links
            content_no_code = code_block_pattern.sub('', content)

            matches = link_pattern.findall(content_no_code)

            for text, link in matches:
                # Skip external links
                if link.startswith(("http://", "https://", "#")):
                    continue

                # Skip example/placeholder links (common in docs)
                if any(x in link.lower() for x in ["example", "missing", "path", "page.md", "anchor"]):
                    continue

                # Skip template placeholder links (e.g., {docs_url}, {repo_url})
                if '{' in link and '}' in link:
                    continue

                # Check relative links
                link_path = md_file.parent / link.split("#")[0]
                if not link_path.exists() and not link.startswith("/"):
                    relative = str(md_file.relative_to(plugin_dir))

                    # Check if this link should be ignored (documented in .linkcheck-ignore)
                    if ignore_rules:
                        should_ignore, category = ignore_rules.should_ignore(relative, link)
                        if should_ignore:
                            ignored.append(f"{relative}: {link} ({category})")
                            continue

                    broken.append(f"{relative}: {link}")

        except Exception:
            pass

    assert not broken, \
        f"Broken links: {broken[:3]}{'...' if len(broken) > 3 else ''}"


def test_drive_engine_skill_exists():
    """The shared drive-engine skill must exist with valid frontmatter."""
    plugin_dir = Path(__file__).parent.parent
    skill = plugin_dir / "skills" / "orchestration" / "drive-engine" / "SKILL.md"
    assert skill.exists(), "skills/orchestration/drive-engine/SKILL.md missing"
    fm = _parse_skill_frontmatter(skill)
    assert fm is not None, "drive-engine SKILL.md has no parseable frontmatter"
    assert "name" in fm and "description" in fm, "drive-engine missing name/description"
    assert fm["name"] == "drive-engine"


def test_drive_command_exists():
    """The orchestrate:drive command must exist with valid frontmatter."""
    plugin_dir = Path(__file__).parent.parent
    cmd = plugin_dir / "commands" / "orch" / "drive.md"
    assert cmd.exists(), "commands/orchestrate/drive.md missing"
    text = cmd.read_text(encoding="utf-8")
    assert text.startswith("---"), "drive.md missing frontmatter block"
    assert "description:" in text.split("---")[1], "drive.md frontmatter missing description"
    # Must not silently auto-open a PR (human publish gate).
    assert "gh pr create" in text, "drive.md must print the PR command, not open it"


def test_consistent_naming():
    """Test that files follow naming conventions."""
    plugin_dir = Path(__file__).parent.parent

    # Check for kebab-case in command names
    commands = find_all_commands()
    bad_names = []

    for cmd in commands:
        name = cmd.stem
        # Should be lowercase with hyphens
        if name != name.lower() or "_" in name:
            relative = cmd.relative_to(plugin_dir)
            bad_names.append(str(relative))

    assert not bad_names, f"Non-kebab-case names: {bad_names[:3]}"


def test_refine_flag_documented():
    """The 5 target commands must declare --refine and delegate to the skill."""
    targets = [
        "commands/brainstorm.md",
        "commands/do.md",
        "commands/orch.md",
        "commands/plan/feature.md",
        "commands/arch/plan.md",
    ]
    missing = []
    for rel in targets:
        text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
        if "--refine" not in text or "prompt-refiner" not in text:
            missing.append(rel)
    assert not missing, f"--refine/prompt-refiner missing in: {missing}"


def test_do_score_4_7_no_agent_dispatch():
    """Score 4-7 tasks in /craft:do must route via the category-based
    command-sequencing fallback, never via Task(subagent_type=<dead-agent>).

    The 4 names below (feature-dev, backend-architect, bug-detective,
    code-quality-reviewer) have no backing agent definition anywhere in this
    plugin (only agents/orchestrator.md, agents/orchestrator-v2.md, and the
    6 under agents/docs/* exist). do.md must not dispatch to them.
    """
    dead_agents = [
        "feature-dev",
        "backend-architect",
        "bug-detective",
        "code-quality-reviewer",
    ]
    text = (PLUGIN_DIR / "commands" / "do.md").read_text(encoding="utf-8")

    # No dead agent name may appear as a subagent_type dispatch target.
    dispatched = [
        name for name in dead_agents
        if re.search(rf'subagent_type\s*=\s*"{re.escape(name)}"', text)
    ]
    assert not dispatched, (
        f"do.md still dispatches Task(subagent_type=...) to dead agents with "
        f"no backing definition: {dispatched}"
    )

    # select_agent() (the independent keyword-rescan that picked those dead
    # names) must be gone entirely — Score 4-7 must route through the same
    # category-based fallback Score 0-3 and 8+ already use.
    assert "def select_agent(" not in text, (
        "do.md still defines select_agent() — Score 4-7 must route via the "
        "category-based command-sequencing fallback instead of an "
        "independent agent-selection keyword-rescan"
    )

    # The category-based fallback (route_to_commands / the category if/elif
    # block used by Score 0-3 and available as the Step 6 fallback) must be
    # reachable for Score 4-7, not merely present as an error-path fallback
    # after a Task() dispatch attempt.
    assert 'execute(["/craft:arch:plan"' in text, (
        "do.md must retain the category-based command-sequencing fallback "
        "(feature category → arch:plan/test-gen/git:branch) as the routing "
        "path for medium-complexity tasks"
    )
