"""Focused coverage for command and skill discovery helpers."""

import json
import os
from pathlib import Path

from commands import _discovery as discovery


def test_frontmatter_parses_values_arrays_and_nested_objects():
    text = """---
name: check
description: Validate project
tags:
  - one
  - two
arguments:
  - name: mode
    description: (default|debug)
  - name: dry-run
    description: Preview
empty:
---
body
"""
    parsed = discovery.parse_yaml_frontmatter(text)
    assert parsed["name"] == "check"
    assert parsed["tags"] == ["one", "two"]
    assert parsed["arguments"] == [
        {"name": "mode", "description": "(default|debug)"},
        {"name": "dry-run", "description": "Preview"},
    ]
    assert parsed["empty"] == []
    assert discovery.parse_yaml_frontmatter("no frontmatter") == {}


def test_description_and_path_inference_variants():
    assert discovery.extract_first_heading("---\nname: x\n---\n# /craft:code:lint - Lint code\n") == "Lint code"
    assert discovery.extract_first_heading("plain text") is None
    assert discovery.extract_first_paragraph("---\nx: y\n---\n# Heading\n```sh\ncode\n```\nA long description. second sentence") == "A long description."
    assert discovery.extract_first_paragraph("# Heading\n\n```\ncode\n```") is None
    assert discovery.infer_category("hub.md") == "hub"
    assert discovery.infer_category("hub.md") == "hub"
    assert discovery.infer_category("_internal/file.md") == "internal"
    assert discovery.infer_category(r"git\docs\refcard.md") == "git"
    assert discovery.infer_command_name("git/docs/refcard.md", "git") == "git:refcard"
    assert discovery.infer_command_name("git/utils/tool.md", "git") == "git:tool"
    assert discovery.infer_command_name("hub.md", "hub") == "hub"


def test_discover_commands_optional_metadata_and_fallbacks(tmp_path, monkeypatch, capsys):
    commands = tmp_path / "commands"
    (commands / "code").mkdir(parents=True)
    (commands / "code" / "lint.md").write_text("""---
name: code:lint
subcategory: quality
modes: default, release
arguments:
  - name: mode
    description: (default|debug|release)
  - dry-run
---
# Lint
Description.
""")
    (commands / "fallback.md").write_text("# Fallback heading\n\nParagraph.")
    (commands / "_private.md").write_text("# Private")
    (commands / "code" / "bad.md").write_bytes(b"\xff")
    monkeypatch.setattr(discovery, "COMMANDS_DIR", str(commands))
    found = discovery.discover_commands()
    by_name = {item["name"]: item for item in found}
    assert set(by_name) == {"code:lint", "fallback"}
    assert by_name["code:lint"]["modes"] == ["default", "debug", "release"]
    assert by_name["code:lint"]["arguments"][0]["description"] == "(default|debug|release)"
    assert by_name["fallback"]["description"] == "Fallback heading"
    assert "Failed to parse" in capsys.readouterr().out


def test_discover_skills_nested_flat_optional_fields_and_missing_dir(tmp_path, monkeypatch):
    skills = tmp_path / "skills"
    nested = skills / "docs" / "sync" / "SKILL.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("""---
name: docs-sync
description: Sync docs
tags: writing, docs
related_commands:
  - docs-update
---
""")
    flat = skills / "standalone" / "SKILL.md"
    flat.parent.mkdir()
    flat.write_text("# Standalone\n\nHelp text.")
    monkeypatch.setattr(discovery, "SKILLS_DIR", str(skills))
    found = {skill["slug"]: skill for skill in discovery.discover_skills()}
    assert found["sync"]["category"] == "docs"
    assert found["sync"]["tags"] == ["writing", "docs"]
    assert found["sync"]["related_commands"] == ["docs-update"]
    assert found["standalone"]["category"] == "standalone"
    monkeypatch.setattr(discovery, "SKILLS_DIR", str(tmp_path / "absent"))
    assert discovery.discover_skills() == []


def test_cache_fresh_stale_legacy_skills_and_stats(tmp_path, monkeypatch):
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()
    skills_dir = tmp_path / "skills"
    (skills_dir / "topic").mkdir(parents=True)
    skill_path = skills_dir / "topic" / "SKILL.md"
    skill_path.write_text("# Skill")
    cache_file = commands_dir / "_cache.json"
    monkeypatch.setattr(discovery, "COMMANDS_DIR", str(commands_dir))
    monkeypatch.setattr(discovery, "SKILLS_DIR", str(skills_dir))
    rows = [{"name": "code:lint", "category": "code", "modes": ["release"],
             "arguments": [{"name": "dry-run"}]}]
    monkeypatch.setattr(discovery, "discover_commands", lambda: rows)
    monkeypatch.setattr(discovery, "discover_skills", lambda: [{"name": "s", "category": "docs"}])
    assert discovery.load_cached_commands() == rows
    assert discovery.load_cached_skills()[0]["name"] == "s"
    stats = discovery.get_command_stats()
    assert stats["total"] == 1 and stats["with_modes"] == 1 and stats["with_dry_run"] == 1
    assert discovery.get_commands_by_category("code") == rows
    assert discovery.get_category_info("unknown")["icon"] == "📁"
    assert discovery.get_category_info("code")["subcategories"]["general"] == rows

    cache_file.write_text(json.dumps({"commands": rows}))  # Legacy cache lacks skills.
    assert discovery.load_cached_skills()[0]["name"] == "s"
    assert discovery.get_command_detail("lint") == rows[0]
    assert discovery.get_command_detail("missing") is None
    duplicate = rows + [{"name": "test:lint", "category": "test"}]
    monkeypatch.setattr(discovery, "load_cached_commands", lambda: duplicate)
    assert discovery.get_command_detail("lint") is None


def test_cache_counts_string_arguments_and_tutorial_sections(tmp_path, monkeypatch):
    cache_file = tmp_path / "_cache.json"
    monkeypatch.setattr(discovery, "CACHE_FILE", str(cache_file))
    monkeypatch.setattr(discovery, "discover_skills", lambda: [])
    commands = [
        {"name": "one", "category": "code", "arguments": ["--dry-run"]},
        {"name": "two", "category": "test", "arguments": [{"name": "dry-run"}], "modes": ["release"]},
        {"name": "three", "category": "other"},
    ]
    discovery.cache_commands(commands, skills=[{"category": "docs"}, {}])
    cached = json.loads(cache_file.read_text())
    assert cached["stats"] == {"total": 3, "with_modes": 1, "with_dry_run": 2, "skills_total": 2}
    assert cached["skills_categories"] == {"docs": 1, "general": 1}
    tutorial = discovery.generate_command_tutorial({
        "name": "check", "category": "code", "description": "Checks things", "modes": ["default", "custom"],
        "examples": [{"command": "custom invocation", "description": "example"}],
        "common_workflows": [{"name": "Build", "steps": ["one", "two"]}],
        "related_commands": ["known", "unknown"],
    })
    assert "release" not in tutorial and "Standard execution" in tutorial
    assert "COMMON WORKFLOWS" in tutorial and "RELATED COMMANDS" in tutorial
    assert "custom invocation" in tutorial
