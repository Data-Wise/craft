#!/usr/bin/env python3
"""
End-to-End Plugin Integrity Tests
===================================
Validates that the craft plugin wires together correctly as a whole:
commands ↔ skills ↔ agents, version consistency, frontmatter validity,
cross-references, and documentation alignment.

Unlike unit tests (test_craft_plugin.py) which check individual pieces,
these tests verify the *relationships* between plugin components.

Run with: python3 -m pytest tests/test_plugin_e2e.py -v
"""

import json
import os
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.e2e, pytest.mark.structure]

PLUGIN_DIR = Path(__file__).parent.parent
COMMANDS_DIR = PLUGIN_DIR / "commands"
SKILLS_DIR = PLUGIN_DIR / "skills"
AGENTS_DIR = PLUGIN_DIR / "agents"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
CLAUDE_MD = PLUGIN_DIR / "CLAUDE.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_plugin_json() -> dict[str, Any]:
    return json.loads(PLUGIN_JSON.read_text())


def _extract_frontmatter(path: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from a markdown file."""
    content = path.read_text()
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _find_all_commands() -> list[Path]:
    return [
        p for p in COMMANDS_DIR.rglob("*.md")
        if p.name not in ("index.md", "README.md")
    ]


def _find_all_skill_files() -> list[Path]:
    """Find all skill markdown files (SKILL.md and individual .md skills)."""
    return list(SKILLS_DIR.rglob("*.md"))


def _find_all_agents() -> list[Path]:
    return list(AGENTS_DIR.rglob("*.md"))


# ============================================================================
# 1. Version Consistency Across Files
# ============================================================================

class TestVersionConsistency:
    """Version strings must agree across plugin.json, CLAUDE.md, etc."""

    def test_plugin_json_has_semver(self):
        """plugin.json version is valid semver."""
        data = _load_plugin_json()
        version = data.get("version", "")
        assert re.match(r"^\d+\.\d+\.\d+$", version), (
            f"plugin.json version '{version}' is not valid semver"
        )

    def test_claude_md_references_current_version(self):
        """CLAUDE.md mentions the same version as plugin.json."""
        data = _load_plugin_json()
        expected = data["version"]
        claude_md = CLAUDE_MD.read_text()
        assert expected in claude_md, (
            f"CLAUDE.md should reference current version {expected}"
        )

    def test_readme_references_current_version(self):
        """README.md mentions the same version as plugin.json."""
        readme = PLUGIN_DIR / "README.md"
        if not readme.exists():
            pytest.skip("README.md not found")
        data = _load_plugin_json()
        expected = data["version"]
        content = readme.read_text()
        # README may use v-prefix or bare version
        assert expected in content or f"v{expected}" in content, (
            f"README.md should reference current version {expected}"
        )


# ============================================================================
# 2. Command Frontmatter Validity
# ============================================================================

class TestCommandFrontmatter:
    """Every command must have valid YAML frontmatter with a description."""

    @pytest.fixture(scope="class")
    def all_commands(self):
        return _find_all_commands()

    def test_all_commands_have_frontmatter(self, all_commands):
        """Every command .md has YAML frontmatter."""
        missing = []
        for cmd in all_commands:
            fm = _extract_frontmatter(cmd)
            if not fm:
                missing.append(cmd.relative_to(PLUGIN_DIR))
        assert not missing, f"Commands missing frontmatter: {missing}"

    def test_all_commands_have_description(self, all_commands):
        """Every command frontmatter includes 'description'."""
        missing = []
        for cmd in all_commands:
            fm = _extract_frontmatter(cmd)
            if fm and "description" not in fm:
                missing.append(cmd.relative_to(PLUGIN_DIR))
        assert not missing, f"Commands missing 'description': {missing}"

    def test_no_duplicate_command_names(self, all_commands):
        """No two commands share the same stem within a directory."""
        seen: dict[str, Path] = {}
        dupes = []
        for cmd in all_commands:
            key = f"{cmd.parent.name}/{cmd.stem}"
            if key in seen:
                dupes.append((key, seen[key], cmd))
            seen[key] = cmd
        assert not dupes, f"Duplicate command names: {dupes}"


# ============================================================================
# 3. Skill Registration Integrity
# ============================================================================

class TestSkillIntegrity:
    """Skills must have valid frontmatter and be discoverable."""

    @pytest.fixture(scope="class")
    def all_skills(self):
        return _find_all_skill_files()

    def test_skill_md_files_with_frontmatter_have_description(self, all_skills):
        """Skill files that have frontmatter include 'name' or 'description'."""
        invalid = []
        for skill in all_skills:
            # Skip reference/helper files (not standalone skills)
            if "references" in skill.parts:
                continue
            fm = _extract_frontmatter(skill)
            if fm and not (fm.get("name") or fm.get("description")):
                invalid.append(skill.relative_to(PLUGIN_DIR))
        assert not invalid, f"Skills missing name/description: {invalid}"

    def test_skill_md_files_registered_have_frontmatter(self, all_skills):
        """SKILL.md files (registered skills) must have frontmatter."""
        missing = []
        for skill in all_skills:
            if skill.name != "SKILL.md":
                continue
            fm = _extract_frontmatter(skill)
            if not fm:
                missing.append(skill.relative_to(PLUGIN_DIR))
        assert not missing, f"SKILL.md files missing frontmatter: {missing}"

    def test_skill_directories_have_content(self):
        """Every skill subdirectory has at least one .md file."""
        empty = []
        for d in SKILLS_DIR.iterdir():
            if d.is_dir():
                md_files = list(d.rglob("*.md"))
                if not md_files:
                    empty.append(d.name)
        assert not empty, f"Empty skill directories: {empty}"


# ============================================================================
# 4. Agent Wiring
# ============================================================================

class TestAgentWiring:
    """Agents must be valid and reference real craft commands."""

    @pytest.fixture(scope="class")
    def all_agents(self):
        return _find_all_agents()

    def test_agents_have_content(self, all_agents):
        """Agent files are not empty."""
        empty = [
            a.name for a in all_agents
            if a.stat().st_size < 50
        ]
        assert not empty, f"Near-empty agent files: {empty}"

    def test_orchestrator_v2_references_real_commands(self):
        """orchestrator-v2.md references craft commands that exist."""
        agent_path = AGENTS_DIR / "orchestrator-v2.md"
        if not agent_path.exists():
            pytest.skip("orchestrator-v2.md not found")
        content = agent_path.read_text()

        # Extract /craft:something references
        refs = re.findall(r"/craft:([a-z:_-]+)", content)
        if not refs:
            pytest.skip("No /craft: references found in agent")

        # Build set of valid command stems
        valid_stems = set()
        for cmd in _find_all_commands():
            rel = cmd.relative_to(COMMANDS_DIR)
            # commands/code/lint.md -> "code:lint"
            parts = list(rel.parts[:-1]) + [rel.stem]
            valid_stems.add(":".join(parts))
            # Also add bare stem for top-level commands
            valid_stems.add(rel.stem)

        invalid = [r for r in refs if r not in valid_stems]
        # Allow some known non-command references (skills, etc.)
        invalid = [r for r in invalid if not any(
            r.startswith(prefix) for prefix in ("workflow:", "docs:claude-md:")
        )]
        assert not invalid, (
            f"orchestrator-v2 references non-existent commands: {invalid}"
        )


# ============================================================================
# 5. Plugin.json Description Accuracy
# ============================================================================

class TestPluginJsonAccuracy:
    """plugin.json description counts must match actual file counts."""

    def test_command_count_matches_description(self):
        """Command count in description matches actual file count."""
        data = _load_plugin_json()
        desc = data["description"]

        # Extract "N commands" from description
        m = re.search(r"(\d+)\s+commands", desc)
        if not m:
            pytest.skip("No command count in description")
        documented = int(m.group(1))
        actual = len(_find_all_commands())

        assert documented == actual, (
            f"plugin.json says {documented} commands, found {actual}"
        )

    def test_agent_count_matches_description(self):
        """Agent count in description matches actual file count."""
        data = _load_plugin_json()
        desc = data["description"]

        m = re.search(r"(\d+)\s+agents", desc)
        if not m:
            pytest.skip("No agent count in description")
        documented = int(m.group(1))
        actual = len(_find_all_agents())

        assert documented == actual, (
            f"plugin.json says {documented} agents, found {actual}"
        )

    def test_skill_count_matches_description(self):
        """Skill count in description matches actual file count."""
        data = _load_plugin_json()
        desc = data["description"]

        m = re.search(r"(\d+)\s+skills", desc)
        if not m:
            pytest.skip("No skill count in description")
        documented = int(m.group(1))
        actual = len(_find_all_skill_files())

        assert documented == actual, (
            f"plugin.json says {documented} skills, found {actual}"
        )


# ============================================================================
# 6. Cross-Reference Consistency
# ============================================================================

class TestCrossReferences:
    """Commands, skills, and docs should reference each other consistently."""

    def test_claude_md_command_count_matches(self):
        """CLAUDE.md command count matches plugin.json."""
        data = _load_plugin_json()
        desc = data["description"]
        m = re.search(r"(\d+)\s+commands", desc)
        if not m:
            pytest.skip("No count in plugin.json")
        plugin_count = m.group(1)

        claude_md = CLAUDE_MD.read_text()
        m2 = re.search(r"(\d+)\s+commands", claude_md)
        if not m2:
            pytest.skip("No count in CLAUDE.md")
        claude_count = m2.group(1)

        assert plugin_count == claude_count, (
            f"plugin.json says {plugin_count} commands, "
            f"CLAUDE.md says {claude_count}"
        )

    def test_no_orphan_skill_references_in_commands(self):
        """Commands don't reference skills that don't exist."""
        # Build set of known skill names
        known_skills = set()
        for skill in _find_all_skill_files():
            fm = _extract_frontmatter(skill)
            if fm.get("name"):
                known_skills.add(fm["name"])
            known_skills.add(skill.stem)
            # Add parent dir name for SKILL.md files
            if skill.name == "SKILL.md":
                known_skills.add(skill.parent.name)

        # Scan commands for skill references
        orphans = []
        for cmd in _find_all_commands():
            content = cmd.read_text()
            # Look for explicit skill references like "skill: xyz"
            refs = re.findall(r"skill:\s*[\"']?(\w+)", content)
            for ref in refs:
                if ref not in known_skills:
                    orphans.append((cmd.name, ref))

        assert not orphans, f"Orphan skill references: {orphans}"


# ============================================================================
# 7. Documentation Site Alignment
# ============================================================================

class TestDocsSiteAlignment:
    """mkdocs.yml nav should include all documented commands."""

    def test_mkdocs_yml_exists(self):
        """mkdocs.yml exists at plugin root."""
        assert (PLUGIN_DIR / "mkdocs.yml").exists()

    def test_mkdocs_yml_valid_yaml(self):
        """mkdocs.yml is parseable YAML (may use !!python tags for mkdocs)."""
        mkdocs = PLUGIN_DIR / "mkdocs.yml"
        content = mkdocs.read_text()
        # Strip !!python/name: tags that require mkdocs-material to resolve
        import re
        stripped = re.sub(r'!!python/name:\S+', '""', content)
        try:
            yaml.safe_load(stripped)
        except yaml.YAMLError as e:
            pytest.fail(f"mkdocs.yml is invalid YAML: {e}")

    def test_mkdocs_nav_not_empty(self):
        """mkdocs.yml has a non-empty nav section."""
        mkdocs = PLUGIN_DIR / "mkdocs.yml"
        content = mkdocs.read_text()
        # Check for nav: section with regex since yaml.safe_load can't
        # handle mkdocs !!python/name: tags without material installed
        assert re.search(r"^nav:", content, re.MULTILINE), (
            "mkdocs.yml should have a 'nav:' section"
        )
        # Check nav has at least one entry (a line with "- " after nav:)
        nav_section = content[content.index("nav:"):]
        entry_lines = [
            line for line in nav_section.split("\n")[1:20]
            if line.strip().startswith("- ")
        ]
        assert len(entry_lines) > 0, "nav should have at least one entry"


# ============================================================================
# 8. Script Syntax Validation
# ============================================================================

class TestScriptSyntax:
    """All bash scripts must pass syntax checking."""

    @pytest.fixture(scope="class")
    def all_scripts(self):
        scripts_dir = PLUGIN_DIR / "scripts"
        return [
            p for p in scripts_dir.rglob("*.sh")
            if p.is_file()
        ]

    def test_all_scripts_pass_bash_n(self, all_scripts):
        """Every .sh file passes bash -n syntax check."""
        import subprocess

        failures = []
        for script in all_scripts:
            result = subprocess.run(
                ["bash", "-n", str(script)],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                failures.append(
                    f"{script.relative_to(PLUGIN_DIR)}: {result.stderr.strip()}"
                )
        assert not failures, f"Scripts with syntax errors:\n" + "\n".join(failures)

    def test_all_scripts_have_shebang(self, all_scripts):
        """Every .sh file starts with a shebang line."""
        missing = []
        for script in all_scripts:
            first_line = script.read_text().split("\n", 1)[0]
            if not first_line.startswith("#!"):
                missing.append(script.relative_to(PLUGIN_DIR))
        assert not missing, f"Scripts missing shebang: {missing}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
