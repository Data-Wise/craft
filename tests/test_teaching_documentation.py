#!/usr/bin/env python3
"""
Test suite for teaching workflow documentation.

Validates that all teaching workflow documentation is complete, accurate,
and properly integrated into the documentation site.
"""

import os
import re
from pathlib import Path

# Test configuration
DOCS_DIR = Path(__file__).parent.parent / "docs"
COMMANDS_DIR = Path(__file__).parent.parent / "commands"


class TestTeachingDocumentation:
    """Test teaching workflow documentation completeness"""

    def test_teaching_guide_exists(self):
        """Teaching workflow guide should exist"""
        guide_path = DOCS_DIR / "guide" / "teaching-workflow.md"
        assert guide_path.exists(), "Teaching workflow guide not found"

        content = guide_path.read_text()
        assert len(content) > 1000, "Teaching guide seems incomplete"
        assert "Preview-before-publish" in content, "Missing key workflow description"
        assert "Content validation" in content, "Missing validation section"
        assert "Semester progress" in content, "Missing progress tracking section"

    def test_teaching_refcard_exists(self):
        """Teaching quick reference should exist"""
        refcard_path = DOCS_DIR / "reference" / "REFCARD-TEACHING.md"
        assert refcard_path.exists(), "Teaching refcard not found"

        content = refcard_path.read_text()
        assert "/craft:site:publish" in content, "Missing publish command"
        assert "/craft:site:progress" in content, "Missing progress command"
        assert "/craft:site:build" in content, "Missing build command"

    def test_teaching_demo_exists(self):
        """VHS demo tape should exist"""
        demo_path = DOCS_DIR / "demos" / "teaching-workflow.tape"
        assert demo_path.exists(), "Teaching demo tape not found"

        content = demo_path.read_text()
        assert "Output" in content, "Missing output directive"
        assert "/craft:site:publish" in content, "Demo doesn't show publish workflow"

    def test_teaching_tutorial_exists(self):
        """Teaching mode setup tutorial should exist (from PR)"""
        tutorial_path = DOCS_DIR / "tutorials" / "teaching-mode-setup.md"
        assert tutorial_path.exists(), "Teaching setup tutorial not found"

    def test_teaching_config_schema_exists(self):
        """Teaching config schema should exist (from PR)"""
        schema_path = DOCS_DIR / "teaching-config-schema.md"
        assert schema_path.exists(), "Teaching config schema not found"

    def test_teaching_migration_guide_exists(self):
        """Teaching migration guide should exist (from PR)"""
        migration_path = DOCS_DIR / "teaching-migration.md"
        assert migration_path.exists(), "Teaching migration guide not found"

    def test_teaching_commands_documented(self):
        """All teaching commands should be documented"""
        commands = [
            "site/publish.md",
            "site/progress.md",
            "site/build.md",
            "git/status.md"
        ]

        for cmd in commands:
            cmd_path = COMMANDS_DIR / cmd
            assert cmd_path.exists(), f"Command file {cmd} not found"

    def test_mkdocs_navigation_includes_teaching(self):
        """mkdocs.yml should include teaching documentation"""
        mkdocs_path = Path(__file__).parent.parent / "mkdocs.yml"
        assert mkdocs_path.exists(), "mkdocs.yml not found"

        content = mkdocs_path.read_text()
        assert "teaching-workflow.md" in content, "Teaching guide not in navigation"
        assert "REFCARD-TEACHING.md" in content, "Teaching refcard not in help section"

    def test_refcard_includes_teaching_section(self):
        """Main refcard should include teaching commands"""
        refcard_path = DOCS_DIR / "REFCARD.md"
        assert refcard_path.exists(), "Main REFCARD.md not found"

        content = refcard_path.read_text()
        assert "/craft:site:publish" in content, "Publish command not in main refcard"
        assert "/craft:site:progress" in content, "Progress command not in main refcard"
        assert "Teaching Mode" in content, "Teaching mode section missing"

    def test_changelog_includes_v122(self):
        """CHANGELOG should document v1.22.0 teaching release"""
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
        assert changelog_path.exists(), "CHANGELOG.md not found"

        content = changelog_path.read_text()
        assert "## [1.22.0]" in content, "v1.22.0 release not documented"
        assert "Teaching Workflow System" in content, "Teaching feature not in changelog"
        assert "80% time reduction" in content, "Impact metrics missing"

    def test_teaching_guide_has_complete_sections(self):
        """Teaching guide should have all required sections"""
        guide_path = DOCS_DIR / "guide" / "teaching-workflow.md"
        content = guide_path.read_text()

        required_sections = [
            "## Overview",
            "## Quick Start",
            "## Core Commands",
            "## How It Works",
            "## Configuration",
            "## Common Workflows",
            "## Teaching-Aware Commands",
            "## Troubleshooting",
            "## Migration Guide",
            "## Advanced Features",
            "## Impact"
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_teaching_guide_has_mermaid_diagram(self):
        """Teaching guide should include workflow diagram"""
        guide_path = DOCS_DIR / "guide" / "teaching-workflow.md"
        content = guide_path.read_text()

        assert "```mermaid" in content, "Missing Mermaid diagram"
        assert "graph TD" in content or "graph LR" in content, "Mermaid diagram incomplete"

    def test_teaching_guide_has_code_examples(self):
        """Teaching guide should include practical examples"""
        guide_path = DOCS_DIR / "guide" / "teaching-workflow.md"
        content = guide_path.read_text()

        # Check for YAML examples
        assert "```yaml" in content, "Missing YAML configuration examples"
        assert "teaching:" in content, "Missing teaching config example"

        # Check for shell examples
        assert "```bash" in content, "Missing shell command examples"

    def test_refcard_has_quick_start(self):
        """Refcard should have copy-paste ready quick start"""
        refcard_path = DOCS_DIR / "reference" / "REFCARD-TEACHING.md"
        content = refcard_path.read_text()

        assert "## Quick Start" in content, "Missing quick start section"
        assert "cat >" in content or "teaching:" in content, "Missing quick start config"

    def test_refcard_has_common_workflows(self):
        """Refcard should document common workflows"""
        refcard_path = DOCS_DIR / "reference" / "REFCARD-TEACHING.md"
        content = refcard_path.read_text()

        assert "## Common Workflows" in content, "Missing workflows section"
        assert "Weekly Content Update" in content, "Missing weekly update workflow"

    def test_refcard_has_troubleshooting(self):
        """Refcard should have troubleshooting quick fixes"""
        refcard_path = DOCS_DIR / "reference" / "REFCARD-TEACHING.md"
        content = refcard_path.read_text()

        assert "## Troubleshooting" in content, "Missing troubleshooting section"
        assert "Not Detecting Teaching Mode" in content, "Missing detection troubleshooting"

    def test_demo_tape_is_valid_vhs(self):
        """VHS demo tape should have valid syntax"""
        demo_path = DOCS_DIR / "demos" / "teaching-workflow.tape"
        content = demo_path.read_text()

        # Check VHS directives
        assert "Output" in content, "Missing Output directive"
        assert "Set FontSize" in content, "Missing font size setting"
        assert "Set Width" in content, "Missing width setting"
        assert "Set Height" in content, "Missing height setting"

        # Check demo steps
        assert "Type" in content, "Missing Type commands"
        assert "Sleep" in content, "Missing Sleep commands"
        assert "Enter" in content, "Missing Enter commands"

    def test_teaching_docs_cross_reference(self):
        """Teaching docs should properly cross-reference each other"""
        guide_path = DOCS_DIR / "guide" / "teaching-workflow.md"
        content = guide_path.read_text()

        # Should reference other docs
        assert "teaching-config-schema.md" in content, "Missing schema reference"
        assert "teaching-migration.md" in content, "Missing migration reference"
        assert "teaching-mode-setup.md" in content, "Missing tutorial reference"

    def test_no_broken_internal_links_in_teaching_docs(self):
        """Teaching documentation should not have broken internal links"""
        teaching_docs = [
            DOCS_DIR / "guide" / "teaching-workflow.md",
            DOCS_DIR / "reference" / "REFCARD-TEACHING.md"
        ]

        for doc_path in teaching_docs:
            if not doc_path.exists():
                continue

            content = doc_path.read_text()

            # Find markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)

            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith(('http://', 'https://', '#')):
                    continue

                # Check internal file links
                if link_url.endswith('.md'):
                    # Resolve relative path
                    target = (doc_path.parent / link_url).resolve()
                    assert target.exists(), f"Broken link in {doc_path.name}: {link_url}"

    def test_teaching_utilities_have_readme(self):
        """Teaching utilities should have documentation"""
        utils_dir = Path(__file__).parent.parent / "commands" / "utils"

        readme_files = [
            "readme-teach-config.md",
            "readme-semester-progress.md"
        ]

        for readme in readme_files:
            readme_path = utils_dir / readme
            assert readme_path.exists(), f"Missing utility readme: {readme}"

    def test_teaching_examples_exist(self):
        """Teaching config examples should exist"""
        examples_dir = Path(__file__).parent.parent / "examples"

        example_path = examples_dir / "teach-config-example.yml"
        assert example_path.exists(), "Missing teach-config example"

        content = example_path.read_text()
        # Example uses course: root key instead of teaching:
        assert "course:" in content or "teaching:" in content, "Example missing config structure"
        assert "semester:" in content or "dates:" in content, "Example missing semester info"

    def test_documentation_completeness_score(self):
        """Calculate documentation completeness score"""
        checks = {
            'guide': (DOCS_DIR / "guide" / "teaching-workflow.md").exists(),
            'refcard': (DOCS_DIR / "reference" / "REFCARD-TEACHING.md").exists(),
            'demo': (DOCS_DIR / "demos" / "teaching-workflow.tape").exists(),
            'tutorial': (DOCS_DIR / "tutorials" / "teaching-mode-setup.md").exists(),
            'schema': (DOCS_DIR / "teaching-config-schema.md").exists(),
            'migration': (DOCS_DIR / "teaching-migration.md").exists(),
            'changelog': "## [1.22.0]" in (Path(__file__).parent.parent / "CHANGELOG.md").read_text(),
            'navigation': "teaching-workflow.md" in (Path(__file__).parent.parent / "mkdocs.yml").read_text()
        }

        score = sum(checks.values()) / len(checks) * 100
        print(f"\n📊 Documentation Completeness: {score:.0f}%")

        assert score == 100, f"Documentation incomplete: {score:.0f}%"


def run_tests():
    """Run all documentation tests"""
    import pytest
    import sys

    # Run tests with verbose output
    exit_code = pytest.main([__file__, '-v', '--tb=short'])
    sys.exit(exit_code)


if __name__ == '__main__':
    run_tests()
