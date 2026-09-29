"""Coverage for generated CLAUDE.md reference inventories."""

import json
from pathlib import Path

from utils.claude_md_sync import ReferenceFileGenerator


def test_generate_reference_files_from_project_layout(tmp_path):
    (tmp_path / "agents" / "nested").mkdir(parents=True)
    (tmp_path / "agents" / "a-review.md").write_text(
        "model: sonnet\ndescription: " + "x" * 90 + "\n"
    )
    (tmp_path / "agents" / "nested" / "bot.md").write_text("model: opus\n")
    (tmp_path / "tests").mkdir()
    for name in ("test_unit.py", "test_e2e.py", "test_integration.py", "test_dogfood.py"):
        (tmp_path / "tests" / name).write_text("")
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "one.md").write_text("")
    (tmp_path / "skills" / "one").mkdir(parents=True)
    (tmp_path / "skills" / "one" / "SKILL.md").write_text("")
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "SPEC-one.md").write_text("")
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(json.dumps({"version": "4.7.0"}))

    generator = ReferenceFileGenerator(tmp_path)
    written = generator.generate_all()
    assert len(written) == 3
    refs = tmp_path / ".claude" / "reference"
    agents = (refs / "agents.md").read_text()
    assert "2 agents" in agents and "sonnet" in agents and "opus" in agents and "..." in agents
    suite = (refs / "test-suite.md").read_text()
    assert "E2E" in suite and "Integration" in suite and "Dogfood" in suite and "Unit" in suite
    structure = (refs / "project-structure.md").read_text()
    assert "1 commands" in structure and "1 skills" in structure and "1 specs" in structure
    assert "v4.7.0" in structure


def test_reference_generator_handles_missing_directories_and_bad_manifest(tmp_path):
    generator = ReferenceFileGenerator(tmp_path)
    assert generator._generate_agents() is None
    assert generator._generate_test_suite() is None
    written = generator.generate_all()
    assert written == [str(tmp_path / ".claude" / "reference" / "project-structure.md")]
    assert "unknown" in Path(written[0]).read_text()

    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text("{")
    assert "unknown" in generator._generate_project_structure().read_text()
