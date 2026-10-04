"""check:test-coverage must not pass a release gate when coverage could not be measured.

Regression: with pytest missing, the validator printed "SKIP: pytest not installed" and
exited 0 in every mode, so `CRAFT_MODE=release` (the blocking tier) passed unmeasured.
It also probed `command -v pytest` while running `python3 -m pytest`.
"""
import re
import stat
import subprocess
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parent.parent / ".claude-plugin/skills/validation/test-coverage.md"


def implementation_block():
    blocks = re.findall(r"```bash\n(.*?)```", VALIDATOR.read_text(), re.S)
    impl = [b for b in blocks if "THRESHOLD" in b and b.startswith("#!/bin/bash")]
    assert len(impl) == 1, "expected exactly one implementation block"
    return impl[0]


def run(tmp_path, mode, python_stub_body):
    """Run the implementation block in a throwaway python project with a stub python3."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    (tmp_path / "tests").mkdir()
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir(exist_ok=True)
    stub = stub_dir / "python3"
    stub.write_text("#!/bin/bash\n" + python_stub_body + "\n")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    script = tmp_path / "validator.sh"
    script.write_text(implementation_block())
    env = {"PATH": f"{stub_dir}:/usr/bin:/bin", "CRAFT_MODE": mode, "HOME": str(tmp_path)}
    return subprocess.run(["bash", str(script)], cwd=tmp_path, env=env, capture_output=True, text=True)


NO_PYTEST = 'echo "No module named pytest" >&2; exit 1'


def test_missing_pytest_is_a_skip_outside_release(tmp_path):
    r = run(tmp_path, "default", NO_PYTEST)
    assert r.returncode == 0 and "SKIP" in r.stdout


def test_missing_pytest_fails_the_release_gate(tmp_path):
    r = run(tmp_path, "release", NO_PYTEST)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "FAIL" in r.stdout and "release" in r.stdout


def test_probe_checks_the_python_module_not_a_pytest_binary(tmp_path):
    # a `pytest` binary on PATH must not satisfy the probe when python3 cannot import it
    (tmp_path / "bin").mkdir()
    fake = tmp_path / "bin" / "pytest"
    fake.write_text("#!/bin/bash\nexit 0\n")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    r = run(tmp_path, "release", NO_PYTEST)
    assert r.returncode == 1


def test_working_pytest_still_reaches_the_threshold_check(tmp_path):
    # positive control: importable pytest + passing tests + 95% coverage -> PASS in release mode
    body = ('if [ "$1" = "-c" ]; then exit 0; fi\n'
            'echo \'{"totals": {"percent_covered": 95.0}}\' > coverage.json\nexit 0')
    (tmp_path / "bin").mkdir(exist_ok=True)
    jq = tmp_path / "bin" / "jq"
    jq.write_text('#!/bin/bash\necho 95.0\n')
    jq.chmod(jq.stat().st_mode | stat.S_IEXEC)
    r = run(tmp_path, "release", body)
    assert r.returncode == 0 and "PASS" in r.stdout, r.stdout + r.stderr


def test_lint_validator_uses_an_output_format_modern_ruff_accepts():
    # ruff >= 0.16 rejects --output-format=text (accepted: concise, full, json, ...)
    lint = VALIDATOR.parent / "lint-check.md"
    assert "--output-format=text" not in lint.read_text()
