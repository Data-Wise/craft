#!/usr/bin/env python3
"""SessionStart visibility hook for skill-ecosystem governance.

At session open, audits the live skills tree (``~/.claude/skills``) against the
governance rules and surfaces a COMPACT, RED-ONLY summary into session context
via the SessionStart ``additionalContext`` channel. This is a *visibility* gate:
SessionStart hooks inject context, they cannot block a session — prevention
lives in the pre-commit + CI gates (PR #1).

Quiet by design: silent when clean, silent on any error (a hook must never break
a session), and **mtime-cached** so an unchanged skills tree skips re-audit.

Install (global) — wire into ``~/.claude/settings.json`` (do this deliberately;
it fires in every session):

    "hooks": { "SessionStart": [ { "hooks": [ {
      "type": "command",
      "command": "python3 /ABSOLUTE/PATH/TO/craft/governance/session_hook.py"
    } ] } ] }

Test/override env vars (so dogfood tests stay hermetic):
  GOVERNANCE_ENGINE      path to run_rules.py (default: sibling run_rules.py)
  GOVERNANCE_SKILLS_DIR  default ~/.claude/skills
  GOVERNANCE_INDEX       default <skills>/SKILLS-INDEX.md
  GOVERNANCE_CACHE       default ~/.claude/.cache/governance-session.json
"""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _env(name, default):
    return os.environ.get(name) or default


def audit_summary():
    """Return a compact RED-only summary string, or '' when clean / N/A."""
    engine = _env("GOVERNANCE_ENGINE", os.path.join(HERE, "run_rules.py"))
    skills = os.path.expanduser(_env("GOVERNANCE_SKILLS_DIR", "~/.claude/skills"))
    index = os.path.expanduser(_env("GOVERNANCE_INDEX", os.path.join(skills, "SKILLS-INDEX.md")))
    cache = os.path.expanduser(_env("GOVERNANCE_CACHE", "~/.claude/.cache/governance-session.json"))

    if not os.path.isdir(skills) or not os.path.isfile(engine):
        return ""  # no-op-safe: nothing to audit on this machine

    mtime = int(os.path.getmtime(skills))
    cached = _read_cache(cache)
    if cached is not None and cached.get("mtime") == mtime:
        return cached.get("summary", "")  # unchanged tree → reuse, skip re-audit

    summary = _run_audit(engine, skills, index)
    _write_cache(cache, mtime, summary)
    return summary


def _run_audit(engine, skills, index):
    try:
        p = subprocess.run(
            [sys.executable, engine, "--target", skills, "--index", index, "--json"],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(p.stdout)
    except Exception:
        return ""  # a hook must never break a session
    if not data.get("red"):
        return ""
    offenders = [r["id"] for r in data.get("results", [])
                 if r.get("severity") == "error" and r.get("state") in ("FAIL", "ERROR")]
    return "GOVERNANCE: %d red — %s (run: python3 governance/run_rules.py)" % (
        data["red"], ", ".join(offenders) or "see audit")


def _read_cache(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(path, mtime, summary):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"mtime": mtime, "summary": summary}, f)
    except Exception:
        pass  # cache is best-effort; never fail the hook over it


def main():
    # Consume the SessionStart hook JSON on stdin so we never block the caller.
    try:
        sys.stdin.read()
    except Exception:
        pass
    summary = audit_summary()
    if summary:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": summary}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
