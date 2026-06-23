"""Tests for commands/utils/grill_ledger.py (/craft:grill ledger helpers)."""
import os
import tempfile
import time

from commands.utils.grill_ledger import (
    resolve_ledger_path, spec_crosslink, add_backlink, append_decision, _slug)


def test_always_owns_a_grill_file():
    with tempfile.TemporaryDirectory() as d:
        # even when a brainstorm SPEC exists, grill writes its OWN file
        open(os.path.join(d, "SPEC-auth-2026-06-22.md"), "w", encoding="utf-8").write("# spec\n")
        assert resolve_ledger_path("auth", "2026-06-22", d) == \
            os.path.join(d, "GRILL-auth-2026-06-22.md")


def test_slug_sanitizes_path_and_special_chars():
    assert _slug("Auth / OAuth!!") == "auth-oauth"
    assert _slug("../../etc/passwd") == "etc-passwd"          # no traversal
    assert "/" not in os.path.basename(resolve_ledger_path("a/b", "2026-06-22", "/tmp"))
    assert _slug("") == "untitled"                            # never empty


def test_crosslink_finds_latest_across_dates():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "SPEC-auth-2026-06-20.md"), "w", encoding="utf-8").write("x")
        time.sleep(0.01)
        open(os.path.join(d, "SPEC-auth-2026-06-22.md"), "w", encoding="utf-8").write("x")
        assert spec_crosslink("auth", d) == "SPEC-auth-2026-06-22.md"   # latest, not same-date
        assert spec_crosslink("missing", d) is None


def test_backlink_is_idempotent_and_atomic():
    with tempfile.TemporaryDirectory() as d:
        spec = os.path.join(d, "SPEC-auth-2026-06-22.md")
        open(spec, "w", encoding="utf-8").write("# spec\n")
        add_backlink(spec, "GRILL-auth-2026-06-22.md")
        add_backlink(spec, "GRILL-auth-2026-06-22.md")
        # the filename appears twice per backlink line ([text](url)); assert ONE backlink line
        assert open(spec, encoding="utf-8").read().count("> Interrogated by grill") == 1
        assert not os.path.exists(spec + ".tmp")              # atomic write cleaned up


def test_append_decision_creates_section_then_rows():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "GRILL-x-2026-06-22.md")
        open(p, "w", encoding="utf-8").write("# Grill: x\n")
        append_decision(p, "G1", "Form factor", "Standalone command")
        append_decision(p, "G2", "Interaction", "One-at-a-time")
        body = open(p, encoding="utf-8").read()
        assert body.count("## Decision Ledger") == 1
        assert body.count("| # | Branch | Decision |") == 1
        assert "| G1 | Form factor | Standalone command |" in body
        assert "| G2 | Interaction | One-at-a-time |" in body


def test_append_decision_escapes_pipes_and_newlines():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "GRILL-x-2026-06-22.md")
        open(p, "w", encoding="utf-8").write("# x\n")
        append_decision(p, "G1", "Syntax", "use a | b\nform")
        row = [l for l in open(p, encoding="utf-8").read().splitlines() if l.startswith("| G1")][0]
        assert r"use a \| b form" in row                  # pipe escaped, newline flattened
        assert row.count("|") - row.count(r"\|") == 4     # 4 UNescaped delimiters -> table intact
