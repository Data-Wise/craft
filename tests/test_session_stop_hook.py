import subprocess, json, os, pathlib, tempfile

HOOK = pathlib.Path(__file__).resolve().parent.parent / "hooks/session-facet.sh"

def _run(stdin_obj, home):
    env = {**os.environ, "HOME": str(home)}
    return subprocess.run(["bash", str(HOOK)], input=json.dumps(stdin_obj),
                          capture_output=True, text=True, env=env)

def test_writes_facet_on_session_end(tmp_path):
    r = _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    assert r.returncode == 0
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 1
    data = json.loads(facets[0].read_text())
    assert data["session_id"] == "abc123"
    assert data["auto_collected"] is True

def test_no_double_write_for_same_session(tmp_path):
    _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 1  # second SessionEnd for same session is a no-op

def test_no_double_write_when_done_wrote_first(tmp_path):
    # Simulate /done writing a timestamp-named facet (its filename scheme)
    facets_dir = tmp_path / ".claude/usage-data/facets"
    facets_dir.mkdir(parents=True)
    (facets_dir / "session-20260627-143012.json").write_text(
        '{"session_id": "abc123", "outcome": "completed", "auto_collected": false}'
    )
    _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    facets = list(facets_dir.glob("session-*.json"))
    assert len(facets) == 1, "hook must not write a duplicate when /done already wrote a timestamp-named facet"

def test_distinct_sessions_each_get_a_facet_same_day(tmp_path):
    _run({"cwd": str(tmp_path), "session_id": "s1"}, tmp_path)
    _run({"cwd": str(tmp_path), "session_id": "s2"}, tmp_path)
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 2  # per-session, NOT per-day

def test_exits_zero_without_jq_or_git(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # minimal; hook must self-fallback
    r = _run({"cwd": "/nonexistent", "session_id": "x"}, tmp_path)
    assert r.returncode == 0

# --- Task B.2 installer test (appended) ---
import shutil

INSTALLER = pathlib.Path(__file__).resolve().parent.parent / "scripts/install-session-facet.sh"

def test_installer_registers_sessionend_idempotently(tmp_path):
    home = tmp_path; (home / ".claude/hooks").mkdir(parents=True)
    (home / ".claude/settings.json").write_text('{"hooks":{}}')
    env = {**os.environ, "HOME": str(home)}
    for _ in range(2):  # run twice — must stay idempotent
        subprocess.run(["bash", str(INSTALLER)], capture_output=True, text=True, env=env, check=True)
    settings = json.loads((home / ".claude/settings.json").read_text())
    se = json.dumps(settings["hooks"].get("SessionEnd", []))
    assert "session-facet.sh" in se
    assert se.count("session-facet.sh") == 1  # idempotent
    assert (home / ".claude/hooks/session-facet.sh").exists()
