"""Tests for skill_standards_audit.py scanner."""
import os, sys
from pathlib import Path
CRAFT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CRAFT / "scripts"))
import skill_standards_audit as ssa

def test_load_frontmatter_reads_name_and_description(tmp_path):
    sk = tmp_path / "SKILL.md"
    sk.write_text("---\nname: demo-skill\ndescription: Does a thing.\n---\n# Body\n")
    fm = ssa.load_frontmatter(sk)
    assert fm["name"] == "demo-skill"
    assert fm["description"] == "Does a thing."

def test_valid_keys_includes_recent_anthropic_additions():
    for k in ("when_to_use", "allowed-tools", "paths", "disable-model-invocation"):
        assert k in ssa.VALID_SKILL_KEYS
