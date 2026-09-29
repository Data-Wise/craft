"""Unit coverage for the Mermaid auto-fix and reporting script."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "mermaid-autofix.py"
SPEC = importlib.util.spec_from_file_location("mermaid_autofix_coverage", SCRIPT)
autofix = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(autofix)


def test_safe_fixes_and_report_rules_cover_valid_and_skipped_lines():
    fixed, changes = autofix.fix_leading_slash('A[/path] --> B["/safe"]')
    assert fixed == 'A["/path"] --> B["/safe"]' and len(changes) == 1
    fixed, changes = autofix.fix_lowercase_end("end\n%% comment [end]\nA --> B[ end ]\nC --> D[End]")
    assert "B[ End ]" in fixed and changes == ["[end] -> [End]"]
    fixed, changes = autofix.fix_unquoted_colons("A[State: ok]\nclassDef a: red\nclass A: x\nstyle A: red\nB['x:y']")
    assert 'A["State: ok"]' in fixed and len(changes) == 1
    fixed, changes = autofix.fix_br_tags("A[First<br/>Second]\nB[plain<br>text]")
    assert 'A["First<br/>Second"]' in fixed and len(changes) == 2
    fixed, changes = autofix.fix_deprecated_graph(" graph LR\nflowchart TD\ngraph XX")
    assert fixed.startswith(" flowchart LR") and len(changes) == 1

    assert len(autofix.report_long_text('A[This label is definitely much too long]')) == 1
    assert autofix.report_orphaned_nodes("flowchart TD\nA[alone]\nB --> C")
    assert autofix.report_complex_horizontal("flowchart LR\nA --> B\nB --> C\nC --> D") == []
    assert autofix.report_complex_horizontal("graph LR\nA-->B\nB-->C\nC-->D\nD-->E\nE-->F")


def test_extract_blocks_and_process_dry_run_then_apply(tmp_path):
    path = tmp_path / "diagrams.md"
    original = """Text
```mermaid
graph TD
A[/path] --> B[end]
```
Empty:
```mermaid
   
```
```mermaid
flowchart TD
C --> D
"""
    path.write_text(original)
    blocks = autofix.extract_mermaid_blocks(str(path))
    assert len(blocks) == 1 and blocks[0][0] == 1
    fixes, reports = autofix.process_file(str(path), apply_fixes=False)
    assert {fix.rule for fix in fixes} == {"leading-slash", "lowercase-end", "deprecated-graph"}
    assert path.read_text() == original
    autofix.process_file(str(path), apply_fixes=True)
    updated = path.read_text()
    assert "flowchart TD" in updated and '["/path"]' in updated and "B[End]" in updated

    assert autofix.extract_mermaid_blocks(str(tmp_path / "missing.md")) == []
    invalid = tmp_path / "invalid.md"
    invalid.write_bytes(b"\xff")
    assert autofix.extract_mermaid_blocks(str(invalid)) == []
    empty = tmp_path / "plain.md"
    empty.write_text("no mermaid")
    assert autofix.process_file(str(empty)) == ([], [])


def test_collect_files_self_tests_and_cli_modes(tmp_path, monkeypatch, capsys):
    first = tmp_path / "one.md"
    first.write_text("```mermaid\ngraph TD\nA[/path] --> B[end]\n```")
    nested = tmp_path / "nested"
    nested.mkdir()
    second = nested / "two.md"
    second.write_text("# no diagram")
    text_file = tmp_path / "ignore.txt"
    text_file.write_text("ignore")
    files = autofix.collect_files([str(first), str(nested), str(text_file)])
    assert files == [str(first), str(second)]
    assert autofix.run_tests() is True
    assert "passed" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["mermaid-autofix", "--test"])
    with pytest.raises(SystemExit) as exc:
        autofix.main()
    assert exc.value.code == 0

    monkeypatch.setattr(sys, "argv", ["mermaid-autofix", str(tmp_path), "--fix"])
    with pytest.raises(SystemExit) as exc:
        autofix.main()
    assert exc.value.code == 0 and "APPLIED" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["mermaid-autofix", str(tmp_path / "ignore.txt")])
    with pytest.raises(SystemExit) as exc:
        autofix.main()
    assert exc.value.code == 1

    monkeypatch.setattr(sys, "argv", ["mermaid-autofix"])
    with pytest.raises(SystemExit) as exc:
        autofix.main()
    assert exc.value.code == 2
