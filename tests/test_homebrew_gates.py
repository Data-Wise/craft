import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from verify_caveats import verify_caveats

FORMULA_STALE = '''class Foo < Formula
  def caveats
    <<~EOS
      New in v2.48.0:
      # --- dynamic bullets ---
      - old feature
      # --- end dynamic bullets ---
    EOS
  end
  def post_install
    begin
      system "x"
    rescue => e
      opoo e.message
    end
  end
end
'''
CHANGELOG = "## [2.49.0]\n- new shiny feature\n- second feature\n"

def test_version_string_mismatch_is_a_finding(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert not rep.ok
    assert any("v2.49.0" in x for x in rep.findings)

def test_advisory_default_returns_findings_not_exception(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0", strict=False)
    assert isinstance(rep.findings, list)

def test_missing_changelog_section_fails_loudly(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE.replace("2.48.0", "2.49.0"))
    c = tmp_path / "CHANGELOG.md"; c.write_text("## [9.9.9]\n- unrelated\n")
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert not rep.ok
    assert any("no changelog entry" in x.lower() for x in rep.findings)

def test_no_dynamic_markers_falls_back_to_version_check_only(tmp_path):
    no_markers = FORMULA_STALE.replace("# --- dynamic bullets ---", "").replace("# --- end dynamic bullets ---", "").replace("2.48.0", "2.49.0")
    f = tmp_path / "foo.rb"; f.write_text(no_markers)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert rep.ok  # version string present, no marker zone to diff
