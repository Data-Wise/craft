"""Tests for scripts/gen-command-stub-docs.py — the generator for short docs/commands stub pages.

The 15 stubs it replaces all rendered a `[mode]` synopsis for commands that declare no `mode`
argument, and hid their real arguments (e.g. ci:watch's target/repo/bg/json).
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "gen-command-stub-docs.py"

spec = importlib.util.spec_from_file_location("gen_stub_docs", SCRIPT)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def test_stub_pages_are_current():
    """Every generated stub matches its command file — edit frontmatter, then regenerate."""
    r = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_no_mode_synopsis_for_commands_without_a_mode_argument():
    """No docs page advertises `[mode]` for a command whose frontmatter declares no mode arg."""
    bad = []
    for doc in (ROOT / "docs" / "commands").rglob("*.md"):
        text = doc.read_text(encoding="utf-8")
        for name in re.findall(r"^(/craft:\S+) \[mode\]$", text, re.MULTILINE):
            cmd = ROOT / "commands" / (name.removeprefix("/craft:").replace(":", "/") + ".md")
            if not cmd.exists():
                continue
            fm, _ = gen.frontmatter(cmd.read_text(encoding="utf-8"))
            if "mode" not in {a["name"] for a in gen.fm_arguments(fm)} and "[mode]" not in fm:
                bad.append(f"{doc.relative_to(ROOT)}: {name}")
    assert not bad, f"[mode] synopsis for commands with no mode argument: {bad}"


def test_fm_arguments_parses_the_list():
    fm = '''description: x
arguments:
  - name: target
    description: "PR number | run-id"
    required: false
  - name: bg
    required: true
    default: false
tags: ci'''
    args = gen.fm_arguments(fm)
    assert [a["name"] for a in args] == ["target", "bg"]
    assert args[0]["description"] == "PR number | run-id"
    assert args[1]["required"] == "true" and args[1]["default"] == "false"
    assert gen.fm_arguments("description: none") == []


def test_usage_examples_rewrites_short_alias_and_ignores_prose():
    body = "/craft:code:x in prose is ignored\n```bash\n/x --quick   # q\n/craft:code:x\n/other\n```\n"
    assert gen.usage_examples(body, "/craft:code:x") == ["/craft:code:x --quick   # q", "/craft:code:x"]


def test_is_stub_never_claims_a_hand_written_page():
    assert gen.is_stub(gen.MARKER.format(src="commands/a.md") + "\n# /craft:a\n")
    legacy = "# /craft:a\n\n## Synopsis\n\n```bash\n/craft:a [mode]\n```\n- [/craft:hub](../hub.md) — Browse all commands\n"
    assert gen.is_stub(legacy)
    assert not gen.is_stub("# /craft:a\n\nHand-written page, long form.\n" + "line\n" * 40
                           + "/craft:a [mode]\nBrowse all commands\n")
