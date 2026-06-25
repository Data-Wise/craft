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

# Task A.2: post_install_check tests
from post_install_check import check_post_install

GOOD_PI = '''class Foo < Formula
  def post_install
    begin
      system "claude", "plugin", "marketplace", "update", "local-plugins"
      system "claude", "plugin", "update", "foo@local-plugins"
      (libexec/"x").install "y"
    rescue => e
      opoo e.message
    end
  end
end
'''
BAD_ORDER_PI = GOOD_PI.replace(
  'system "claude", "plugin", "marketplace", "update", "local-plugins"\n      system "claude", "plugin", "update", "foo@local-plugins"',
  'system "claude", "plugin", "update", "foo@local-plugins"\n      system "claude", "plugin", "marketplace", "update", "local-plugins"')

def test_structural_pass_on_correct_ordering(tmp_path):
    f = tmp_path / "g.rb"; f.write_text(GOOD_PI)
    assert check_post_install(str(f)).ok

def test_structural_flags_update_before_marketplace_refresh(tmp_path):
    f = tmp_path / "b.rb"; f.write_text(BAD_ORDER_PI)
    rep = check_post_install(str(f))
    assert not rep.ok
    assert any("marketplace update" in x for x in rep.findings)

# Task A.3: wiring smoke tests
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def test_release_path_documents_blocking_aggregator_and_advisory_gates():
    hb = (ROOT / "commands/dist/homebrew.md").read_text()
    assert "verify_caveats.py" in hb and "Step 10b" in hb
    assert "post_install_check.py" in hb and "Step 10c" in hb
    assert "aggregator-sync" in hb and ("exit 1" in hb or "BLOCKING" in hb)
    assert "@local-plugins" in hb and "Step 10d" in hb

def test_caveats_gate_is_advisory_by_default_strict_via_env():
    hb = (ROOT / "commands/dist/homebrew.md").read_text()
    assert "HOMEBREW_GATE_STRICT" in hb
