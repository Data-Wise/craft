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

def test_distinct_sessions_each_get_a_facet_same_day(tmp_path):
    _run({"cwd": str(tmp_path), "session_id": "s1"}, tmp_path)
    _run({"cwd": str(tmp_path), "session_id": "s2"}, tmp_path)
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 2  # per-session, NOT per-day

def test_exits_zero_without_jq_or_git(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # minimal; hook must self-fallback
    r = _run({"cwd": "/nonexistent", "session_id": "x"}, tmp_path)
    assert r.returncode == 0
