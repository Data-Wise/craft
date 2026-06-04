#!/usr/bin/env python3
"""
Craft Plugin Automated Test Suite
==================================
Validates the craft plugin structure, commands, skills, and agents.

Run with: python tests/test_craft_plugin.py
"""

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
    cmd = plugin_dir / "commands" / "orchestrate" / "drive.md"
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
