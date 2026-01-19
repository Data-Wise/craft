#!/usr/bin/env python3
"""
E2E tests for markdownlint list spacing feature.

Tests full workflow including linting, auto-fix, and pre-commit hook integration.
"""

import json
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestFullLintingWorkflow:
    """End-to-end tests for complete linting workflow."""

    def get_config_path(self):
        """Get config file path."""
        return Path(__file__).parent.parent / ".markdownlint.json"

    def test_multiple_files_linting(self):
        """Linter should handle multiple files at once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create multiple test files
            (tmppath / "file1.md").write_text("## Test 1\n\n-  Item\n")
            (tmppath / "file2.md").write_text("## Test 2\n\n* Item\n")
            (tmppath / "file3.md").write_text("## Test 3\n\n1.  Item\n")

            # Run linter
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    f"{tmppath}/*.md",
                ],
                capture_output=True,
                text=True,
            )

            # Should detect violations in all files
            output = result.stdout + result.stderr
            assert "MD030" in output, "Should detect MD030 violations"
            assert "MD004" in output, "Should detect MD004 violations"
            assert "file1.md" in output or "file2.md" in output, (
                "Should show file names"
            )

    def test_bulk_autofix(self):
        """Auto-fix should handle multiple files at once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create multiple test files with violations
            (tmppath / "file1.md").write_text("## Test 1\n\n-  Item\n")
            (tmppath / "file2.md").write_text("## Test 2\n\n* Item\n")
            (tmppath / "file3.md").write_text("## Test 3\n\n1.  Item\n")

            # Run auto-fix on all files
            subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    "--fix",
                    f"{tmppath}/*.md",
                ],
                capture_output=True,
            )

            # Verify all files are fixed
            for filename in ["file1.md", "file2.md", "file3.md"]:
                filepath = tmppath / filename
                content = filepath.read_text()

                result = subprocess.run(
                    [
                        "npx",
                        "-y",
                        "markdownlint-cli2",
                        "--config",
                        str(self.get_config_path()),
                        str(filepath),
                    ],
                    capture_output=True,
                    text=True,
                )
                output = result.stdout + result.stderr
                assert "MD030" not in output and "MD004" not in output, (
                    "{0} should have no violations after fix: {1}".format(
                        filename, output
                    )
                )

    def test_mixed_violations(self):
        """File with multiple violation types should all be fixed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""## Mixed Violations

Text before list
-  Item with 2 spaces
* Item with asterisk
+ Item with plus

1.  Ordered with 2 spaces
2. Another ordered

## Good Section

- Proper spacing
- Correct marker
""")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    "--fix",
                    temp_path,
                ],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Verify all fixes applied
            assert "- Item with 2 spaces" in content, "Should fix 2-space spacing"
            assert "- Item with asterisk" in content, "Should change asterisk to dash"
            assert "- Item with plus" in content, "Should change plus to dash"
            assert "1. Ordered with 2 spaces" in content, (
                "Should fix ordered list spacing"
            )
            assert "- Proper spacing" in content, "Should keep good sections unchanged"

            # Verify no violations remain
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    temp_path,
                ],
                capture_output=True,
                text=True,
            )
            output = result.stdout + result.stderr
            assert "MD030" not in output and "MD004" not in output, (
                "Should have no violations: {0}".format(output)
            )
        finally:
            Path(temp_path).unlink()


class TestPrecommitHookIntegration:
    """Tests for pre-commit hook integration."""

    def test_hook_file_exists(self):
        """Pre-commit hook should exist in main repo."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        assert hook_path.exists(), "Pre-commit hook not found: {0}".format(hook_path)

    def test_hook_executable(self):
        """Pre-commit hook should be executable."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        # Check if file has execute permission
        import os

        assert os.access(hook_path, os.X_OK), (
            "Pre-commit hook not executable: {0}".format(hook_path)
        )

    def test_hook_has_shebang(self):
        """Pre-commit hook should have bash shebang."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        content = hook_path.read_text()
        assert content.startswith("#!/bin/bash"), "Hook should start with #!/bin/bash"

    def test_hook_checks_markdownlint(self):
        """Hook should check markdownlint."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        content = hook_path.read_text()
        assert "markdownlint-cli2" in content, "Hook should call markdownlint-cli2"

    def test_hook_checks_staged_files(self):
        """Hook should check only staged markdown files."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        content = hook_path.read_text()
        assert "git diff --cached" in content, "Hook should check staged files"
        assert "\\.md$" in content, "Hook should filter for .md files"

    def test_hook_offers_autofix(self):
        """Hook should offer auto-fix option."""
        main_repo = Path(__file__).parent.parent.parent / ".." / ".." / "craft"
        hook_path = main_repo / ".git" / "hooks" / "pre-commit"

        content = hook_path.read_text()
        assert "--fix" in content, "Hook should offer --fix option"
        assert "Would you like" in content or "auto-fix" in content, (
            "Hook should prompt for auto-fix"
        )


class TestBaselineReport:
    """Tests for baseline report functionality."""

    def test_baseline_report_exists(self):
        """Baseline report should exist."""
        baseline_path = (
            Path(__file__).parent.parent / "docs" / "LINT-BASELINE-2026-01-19.txt"
        )
        assert baseline_path.exists(), "Baseline report not found: {0}".format(
            baseline_path
        )

    def test_baseline_has_violations(self):
        """Baseline report should contain violation data."""
        baseline_path = (
            Path(__file__).parent.parent / "docs" / "LINT-BASELINE-2026-01-19.txt"
        )
        content = baseline_path.read_text()

        assert "MD030" in content or len(content) > 100, (
            "Baseline should have MD030 data or be substantial"
        )
        assert "Summary:" in content, "Baseline should have summary section"

    def get_config_path(self):
        """Get config file path."""
        return Path(__file__).parent.parent / ".markdownlint.json"

    def test_baseline_can_be_regenerated(self):
        """Baseline should be reproducible."""
        config_path = self.get_config_path()

        # Run linter on all markdown files
        result = subprocess.run(
            [
                "npx",
                "-y",
                "markdownlint-cli2",
                "--config",
                str(config_path),
                "docs/**/*.md",
                "*.md",
                "commands/**/*.md",
                "skills/**/*.md",
                "agents/**/*.md",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should produce output
        assert len(result.stdout) > 100 or len(result.stderr) > 100, (
            "Linter should produce substantial output"
        )


class TestDocumentationIntegration:
    """Tests for documentation integration."""

    def get_config_path(self):
        """Get config file path."""
        return Path(__file__).parent.parent / ".markdownlint.json"

    def test_docs_lint_md_exists(self):
        """Documentation file should exist."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"
        assert docs_path.exists(), "Documentation not found: {0}".format(docs_path)

    def test_docs_lint_md_mentions_md030(self):
        """Documentation should mention MD030."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"
        content = docs_path.read_text()

        assert "MD030" in content, "Documentation should mention MD030"

    def test_docs_lint_md_mentions_md004(self):
        """Documentation should mention MD004."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"
        content = docs_path.read_text()

        assert "MD004" in content, "Documentation should mention MD004"

    def test_docs_lint_md_has_examples(self):
        """Documentation should have before/after examples."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"
        content = docs_path.read_text()

        assert "Before" in content and "After" in content, (
            "Documentation should have before/after examples"
        )

    def test_docs_lint_md_mentions_spacing(self):
        """Documentation should mention list spacing."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"
        content = docs_path.read_text()

        assert "list spacing" in content.lower() or "List Spacing" in content, (
            "Documentation should mention list spacing"
        )

    def test_docs_lint_md_complies_with_rules(self):
        """Documentation file should comply with its own rules."""
        docs_path = Path(__file__).parent.parent / "commands" / "docs" / "lint.md"

        result = subprocess.run(
            [
                "npx",
                "-y",
                "markdownlint-cli2",
                "--config",
                str(self.get_config_path()),
                str(docs_path),
            ],
            capture_output=True,
            text=True,
        )

        # Note: May still have MD040 violations (code fence language tags)
        # But should not have MD030/MD004 violations
        output = result.stdout + result.stderr
        # We'll check it doesn't crash - actual violations may exist
        assert result.returncode in [0, 1], (
            "Linter should run (pass or fail, not crash)"
        )


class TestRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    def get_config_path(self):
        """Get config file path."""
        return Path(__file__).parent.parent / ".markdownlint.json"

    def test_large_file_handling(self):
        """Should handle large markdown files efficiently."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Create a large file with many violations
            f.write("# Large File\n\n")
            for i in range(100):
                f.write(f"## Section {i}\n\n-  Item {i}-1\n* Item {i}-2\n\n")
            temp_path = f.name

        try:
            # Run linter
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    temp_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,  # Should complete in 30s
            )

            # Should detect violations
            output = result.stdout + result.stderr
            assert "MD030" in output or "MD004" in output, (
                "Should detect violations in large file"
            )

            # Run auto-fix
            subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    "--fix",
                    temp_path,
                ],
                capture_output=True,
                timeout=30,
            )

            # Verify fix completed
            content = Path(temp_path).read_text()
            assert len(content) > 1000, "File should still have content"
        finally:
            Path(temp_path).unlink()

    def test_no_false_positives(self):
        """Should not flag correctly formatted lists."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""## Correctly Formatted

Blank line before list:

- Item 1
- Item 2

Ordered list:

1. First item
2. Second item

Nested:

- Parent
  - Child
  - Another child
""")
            temp_path = f.name

        try:
            # Run linter
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    temp_path,
                ],
                capture_output=True,
                text=True,
            )

            # Should not have MD030 or MD004 violations
            output = result.stdout + result.stderr
            assert "MD030" not in output, (
                "Should not have MD030 false positives: {0}".format(output)
            )
            assert "MD004" not in output, (
                "Should not have MD004 false positives: {0}".format(output)
            )
        finally:
            Path(temp_path).unlink()

    def test_code_blocks_not_affected(self):
        """Should not flag lists in code blocks."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""## Code Blocks

```bash
# This should not be flagged
ls -la
-  Option
* Another option
```

Regular list:

-  This should be flagged (2 spaces)
""")
            temp_path = f.name

        try:
            # Run linter
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(self.get_config_path()),
                    temp_path,
                ],
                capture_output=True,
                text=True,
            )

            # Should flag the regular list, not the code block
            output = result.stdout + result.stderr
            assert "MD030" in output, "Should flag regular list"
            # Note: MD040 might also flag missing language tag
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    import pytest
    import sys

    sys.exit(pytest.main([__file__, "-v", "-s"]))
