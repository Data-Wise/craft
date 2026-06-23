"""Tests for commands/utils/grill_ledger.py (/craft:grill ledger helpers)."""
import os
import tempfile
import time

from commands.utils.grill_ledger import (
    resolve_ledger_path, spec_crosslink, add_backlink, _slug)


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
