"""Contract tests for install.sh (the curl-pipe installer).

Pins the D1 fixes from docs/specs/SPEC-dist-surface-hardening-2026-07-01.md:
the installer must fetch CURRENT craft (not the frozen claude-plugins mirror),
must not hardcode drift-prone counts, and must survive `curl | bash` (no
on-disk script file, stdin is the pipe).
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO_ROOT / "install.sh"


@pytest.fixture(scope="module")
def script_text() -> str:
    return INSTALL_SH.read_text(encoding="utf-8")


def test_install_script_exists_and_is_executable():
    assert INSTALL_SH.is_file()
    assert INSTALL_SH.stat().st_mode & 0o111, "install.sh must be executable"


def test_bash_syntax_is_valid():
    bash = shutil.which("bash")
    assert bash, "bash not found on PATH"
    result = subprocess.run(
        [bash, "-n", str(INSTALL_SH)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"bash -n failed: {result.stderr}"


def test_clones_current_craft_repo_not_frozen_mirror(script_text):
    """D1 root cause: the old installer cloned Data-Wise/claude-plugins and
    sparse-checked-out a craft/ subdir permanently frozen at v1.16.0."""
    assert "github.com/Data-Wise/craft.git" in script_text
    assert "claude-plugins.git" not in script_text
    assert "sparse-checkout" not in script_text


def test_installs_by_direct_clone_not_cp(script_text):
    """git writes symlinks as symlinks; `cp -r` follows them and dies on the
    intentionally-broken governance fixtures (macOS BSD cp) — found by live
    curl|bash simulation. Clone straight into PLUGIN_DIR, then strip .git."""
    assert re.search(
        r'git clone --depth 1 "\$\{REPO_URL\}" "\$\{PLUGIN_DIR\}"', script_text
    )
    code_lines = [
        ln for ln in script_text.splitlines() if not ln.lstrip().startswith("#")
    ]
    assert not any(re.search(r"\bcp -[rR]\b", ln) for ln in code_lines), (
        "no recursive cp — broken-symlink fixtures make it fail on macOS"
    )
    assert 'rm -rf "${PLUGIN_DIR}/.git"' in script_text


def test_no_hardcoded_counts_in_banner(script_text):
    """Counts must be computed from the installed tree, never hardcoded
    (drift class: install.sh banner sat at '107 commands | 8 agents |
    36 skills' while actual was 116/8/44)."""
    assert not re.search(r"\d+ commands \|", script_text), (
        "banner must use ${CMD_COUNT}-style variables, not literal counts"
    )
    assert "${CMD_COUNT}" in script_text
    assert "${AGENT_COUNT}" in script_text
    assert "${SKILL_COUNT}" in script_text


def test_skill_count_uses_canonical_marker(script_text):
    """Skills are counted by SKILL.md only — '*.md' over-counts references/
    (recurring bug fixed across 11 utilities; see MEMORY
    validate-counts-skill-breakdown-overcounts)."""
    assert re.search(r"SKILL_COUNT=.*-name\s+\"SKILL\.md\"", script_text)


def test_no_hardcoded_version_in_header_banner(script_text):
    """The pre-clone banner may not claim a version (old script said
    'craft v1.17.0' forever). Version is printed only post-install from
    the cloned plugin.json."""
    assert not re.search(r"Installing: craft v\d", script_text)


def test_formatting_source_has_pipe_fallback(script_text):
    """Under `curl | bash` there is no script dir on disk; an unconditional
    `source scripts/formatting.sh` aborts under set -e. The source must be
    conditional with inline fallbacks."""
    assert re.search(
        r"if \[ -f \"\$\{SCRIPT_DIR\}/scripts/formatting\.sh\" \]", script_text
    ), "formatting.sh source must be guarded by a file-existence check"
    assert "box_header()" in script_text, "inline fallback functions required"


def test_reinstall_prompt_has_tty_guard(script_text):
    """Under `curl | bash` stdin is the script stream — `read` must come from
    /dev/tty or default non-interactively, or set -e kills the installer."""
    assert "/dev/tty" in script_text
    assert re.search(r"\[ -t 0 \]", script_text)


def test_docs_url_points_at_craft_site(script_text):
    assert "data-wise.github.io/craft/" in script_text
    assert "data-wise.github.io/claude-plugins/" not in script_text


def test_advertised_curl_url_matches_readme():
    """README.md advertises the raw URL of THIS file — the header comment
    must agree (the old header pointed at the claude-plugins mirror)."""
    script = INSTALL_SH.read_text(encoding="utf-8")
    assert (
        "raw.githubusercontent.com/Data-Wise/craft/main/install.sh" in script
    )
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"curl -fsSL (\S+install\.sh)", readme)
    assert m, "README must advertise the curl install path"
    assert m.group(1) == (
        "https://raw.githubusercontent.com/Data-Wise/craft/main/install.sh"
    )
