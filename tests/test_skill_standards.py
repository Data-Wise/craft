"""Tests for skill_standards_audit.py scanner."""
import os, sys, re
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

def test_score_formula_matches_command_audit():
    f = [ssa.Finding("error","c",Path("a"),"m"), ssa.Finding("warning","c",Path("a"),"m")]
    assert ssa.score(f) == 100 - 5 - 2

def test_main_exit_2_on_error(tmp_path, capsys):
    # a skill missing name => error => exit 2
    d = tmp_path / "skills" / "bad"; d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\ndescription: x\n---\n# b\n")
    rc = ssa.main(["--root", str(tmp_path / "skills"), "--json"])
    assert rc == 2
    assert "frontmatter" in capsys.readouterr().out

def test_main_exit_0_when_clean(tmp_path):
    d = tmp_path / "skills" / "good"; d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: good\ndescription: A clean skill.\n---\n# Good\n")
    assert ssa.main(["--root", str(tmp_path / "skills"), "--json"]) == 0

def test_fix_strips_version_tags_only(tmp_path):
    d = tmp_path / "skills" / "demo" / "references"; d.mkdir(parents=True)
    (d.parent / "SKILL.md").write_text("---\nname: demo\ndescription: A skill.\n---\n# Demo\n")
    ref = d / "r.md"
    ref.write_text("## Step 1 (NEW in v2.49.0)\nYou are an assistant.\n")
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    txt = ref.read_text()
    assert "(NEW in v2.49.0)" not in txt          # version tag stripped
    assert "You are an assistant." in txt          # prose NOT auto-rewritten

def test_fix_inserts_toc_stub_in_oversized_reference(tmp_path):
    d = tmp_path / "skills" / "demo"; (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: demo\ndescription: A skill.\n---\n# Demo\n")
    ref = d / "references" / "big.md"
    # 350 lines, no TOC, starts with an H1
    ref.write_text("# Big Reference\n" + "\n".join(["content line"] * 349))
    # Confirm audit sees the finding before fix
    findings = ssa.audit_all(tmp_path / "skills")
    assert any("big.md" in f.message and "table of contents" in f.message.lower() for f in findings)
    # Apply fix
    residual = ssa.apply_safe_fixes(tmp_path / "skills", findings)
    txt = ref.read_text()
    # TOC stub was inserted
    assert re.search(r"(?im)^#{1,3}\s+table of contents", txt), "TOC stub not found in file"
    # Re-audit should produce no size finding for big.md
    assert not any("big.md" in f.message and "table of contents" in f.message.lower() for f in residual)


def test_fix_normalizes_frontmatter_order_and_casing(tmp_path):
    d = tmp_path / "skills" / "demo"; d.mkdir(parents=True)
    # description before name, miscased key "Description:"
    (d / "SKILL.md").write_text(
        "---\nDescription: A skill about things.\nname: demo\n---\n# Demo\n"
    )
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    txt = (d / "SKILL.md").read_text()
    lines = txt.splitlines()
    fm_lines = lines[lines.index("---") + 1: lines.index("---", 1)]
    keys = [l.split(":")[0] for l in fm_lines if ":" in l]
    assert keys[0] == "name", f"name should come first, got {keys}"
    assert keys[1] == "description", f"description should come second, got {keys}"
    # key lowercased
    assert "Description:" not in txt
    assert "description:" in txt


def test_fix_preserves_description_value(tmp_path):
    d = tmp_path / "skills" / "demo"; d.mkdir(parents=True)
    desc_value = "A skill about things."
    (d / "SKILL.md").write_text(
        f"---\nDescription: {desc_value}\nname: demo\n---\n# Demo\n"
    )
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    txt = (d / "SKILL.md").read_text()
    assert desc_value in txt, "description value must be byte-identical after fix"


def test_fix_skips_block_scalar_frontmatter(tmp_path):
    d = tmp_path / "skills" / "demo"; d.mkdir(parents=True)
    original = "---\nname: demo\ndescription: |\n  A multiline\n  description here.\n---\n# Demo\n"
    (d / "SKILL.md").write_text(original)
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    assert (d / "SKILL.md").read_text() == original, "block scalar file must be left byte-identical"


def test_fix_skips_frontmatter_with_comments_or_blanks(tmp_path):
    """Frontmatter with a comment line or blank line must be left byte-identical."""
    d = tmp_path / "skills" / "demo"; d.mkdir(parents=True)
    # has a comment and a blank line inside the frontmatter block
    original = "---\n# This is a comment\nname: demo\n\ndescription: A skill.\n---\n# Demo\n"
    (d / "SKILL.md").write_text(original)
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    assert (d / "SKILL.md").read_text() == original, "file with comment/blank in frontmatter must be byte-identical"


def test_fix_skips_duplicate_frontmatter_keys(tmp_path):
    """Frontmatter with duplicate keys must be left byte-identical (no lines dropped)."""
    d = tmp_path / "skills" / "demo"; d.mkdir(parents=True)
    original = "---\nname: demo\nname: duplicate\ndescription: A skill.\n---\n# Demo\n"
    (d / "SKILL.md").write_text(original)
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    assert (d / "SKILL.md").read_text() == original, "file with duplicate frontmatter keys must be byte-identical"


def test_fix_toc_not_inserted_in_leading_code_fence(tmp_path):
    """TOC stub must not land inside a code fence; it goes above the fence instead."""
    d = tmp_path / "skills" / "demo"; (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: demo\ndescription: A skill.\n---\n# Demo\n")
    ref = d / "references" / "big.md"
    # File starts with a code fence (before any H1), then has an H1 later
    fence_open = "```python\n"
    body_before_h1 = "".join(["# code line\n"] * 10)
    fence_close = "```\n"
    h1_line = "# Big Reference\n"
    body_after = "\n".join(["content line"] * 340) + "\n"
    ref.write_text(fence_open + body_before_h1 + fence_close + h1_line + body_after)
    # Confirm audit sees the finding before fix
    findings = ssa.audit_all(tmp_path / "skills")
    assert any("big.md" in f.message and "table of contents" in f.message.lower() for f in findings)
    # Apply fix
    residual = ssa.apply_safe_fixes(tmp_path / "skills", findings)
    txt = ref.read_text()
    lines = txt.splitlines()
    # TOC heading must exist
    toc_lines = [i for i, l in enumerate(lines) if re.match(r"(?i)^#{1,3}\s+table of contents", l)]
    assert toc_lines, "TOC stub not found after fix"
    # First fence line index
    fence_lines = [i for i, l in enumerate(lines) if l.strip().startswith("```")]
    assert fence_lines, "No fence found"
    first_fence = fence_lines[0]
    toc_pos = toc_lines[0]
    assert toc_pos < first_fence, (
        f"TOC stub (line {toc_pos}) must appear BEFORE the first fence (line {first_fence})"
    )
    # Re-audit should not flag big.md for missing TOC
    assert not any("big.md" in f.message and "table of contents" in f.message.lower() for f in residual)


def test_refresh_standards_updates_provenance(tmp_path, monkeypatch):
    doc = tmp_path / "SKILL-STANDARDS.md"
    doc.write_text("<!-- PROVENANCE\nsynced: 1970-01-01\n-->\n# Standards\nrules…\n")
    monkeypatch.setattr(ssa, "STANDARDS_DOC", doc)
    assert ssa.refresh_standards() == 0
    body = doc.read_text()
    assert "synced: 1970-01-01" not in body      # date bumped
    assert "# Standards" in body                  # prose preserved
    assert "https://code.claude.com" in body      # sources line written
