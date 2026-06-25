# tests/test_skill_standards_validator.py
import subprocess, sys, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / ".claude-plugin/skills/validation/skill-standards-check.md"

def _impl_block(md_text):
    # extract the first ```bash fenced block under "## Implementation"
    import re
    m = re.search(r"## Implementation\s+```bash\n(.*?)```", md_text, re.S)
    assert m, "no bash Implementation block found"
    return m.group(1)

def test_validator_skill_exists_with_hotreload_frontmatter():
    text = VALIDATOR.read_text()
    assert "hot_reload: true" in text
    assert "category: validation" in text
    assert "context: fork" in text

def test_validator_is_advisory_never_exits_one(tmp_path):
    # Run the implementation against a skills root that has a deliberately
    # non-compliant SKILL.md; the validator must report but exit 0.
    bad = tmp_path / "skills" / "bad"
    bad.mkdir(parents=True)
    (bad / "SKILL.md").write_text("# no frontmatter at all\n")
    script = tmp_path / "run.sh"
    script.write_text(_impl_block(VALIDATOR.read_text()))
    env = {**os.environ, "SKILL_STANDARDS_ROOT": str(tmp_path / "skills")}
    r = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
    assert r.returncode == 0, f"advisory validator must exit 0, got {r.returncode}: {r.stderr}"
    assert "skill" in (r.stdout + r.stderr).lower()
