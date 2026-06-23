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

def test_check_frontmatter_flags_missing_name_as_error(tmp_path):
    findings = ssa.check_frontmatter({"description": "x"}, tmp_path / "SKILL.md")
    assert any(f.severity == "error" and f.category == "frontmatter" and "name" in f.message for f in findings)

def test_check_frontmatter_flags_non_kebab_name(tmp_path):
    findings = ssa.check_frontmatter({"name": "Demo_Skill", "description": "x"}, tmp_path / "SKILL.md")
    assert any("kebab" in f.message for f in findings)

def test_check_frontmatter_unknown_key_is_warning(tmp_path):
    findings = ssa.check_frontmatter({"name": "demo", "description": "x", "bogus": "y"}, tmp_path / "SKILL.md")
    assert any(f.severity == "warning" and "bogus" in f.message for f in findings)

def test_check_frontmatter_overlong_description_is_warning(tmp_path):
    findings = ssa.check_frontmatter({"name": "demo", "description": "z" * 1600}, tmp_path / "SKILL.md")
    assert any("1536" in f.message for f in findings)

def _mkskill(tmp_path, body_lines, refs=None):
    d = tmp_path / "skills" / "demo"
    (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: demo\ndescription: x\n---\n" + "\n".join(["line"] * body_lines))
    for fname, lines, has_toc in (refs or []):
        toc = "## Table of Contents\n" if has_toc else ""
        (d / "references" / fname).write_text(toc + "\n".join(["x"] * lines))
    return d / "SKILL.md"

def test_check_size_flags_oversized_skill_md(tmp_path):
    sk = _mkskill(tmp_path, body_lines=600)
    assert any("500" in f.message for f in ssa.check_size(sk))

def test_check_size_flags_large_reference_without_toc(tmp_path):
    sk = _mkskill(tmp_path, body_lines=10, refs=[("big.md", 400, False)])
    assert any("big.md" in f.message and "table of contents" in f.message.lower() for f in ssa.check_size(sk))

def test_check_size_passes_large_reference_with_toc(tmp_path):
    sk = _mkskill(tmp_path, body_lines=10, refs=[("big.md", 400, True)])
    assert not any("big.md" in f.message for f in ssa.check_size(sk))

def test_hygiene_flags_version_tags(tmp_path):
    sk = _mkskill(tmp_path, 10, refs=[("r.md", 20, True)])
    (sk.parent / "references" / "r.md").write_text("## Step 1 (NEW in v2.49.0)\nbody\n")
    assert any("version tag" in f.message.lower() for f in ssa.check_reference_hygiene(sk))

def test_hygiene_flags_second_person_framing(tmp_path):
    sk = _mkskill(tmp_path, 10, refs=[("r.md", 20, True)])
    (sk.parent / "references" / "r.md").write_text("You are an assistant. Do the thing.\n")
    assert any(f.severity == "warning" and "second-person" in f.message.lower()
               for f in ssa.check_reference_hygiene(sk))
