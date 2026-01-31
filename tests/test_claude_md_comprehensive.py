"""
Comprehensive test suite for claude-md command suite.

This test file provides both unit and end-to-end tests for:
- Project detection (6 types)
- Template population (18+ variables)
- Version extraction (4 sources)
- Change detection (6 metrics)
- Validation (5 checks)
- Auto-fixing (4 methods)
- Section editing
- Complete workflows

Run with: python3 -m pytest tests/test_claude_md_comprehensive.py -v
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_detector import detect_project, ProjectInfo
from utils.claude_md_template_populator import TemplatePopulator
from utils.claude_md_auditor import CLAUDEMDAuditor, Severity
from utils.claude_md_fixer import CLAUDEMDFixer
from utils.claude_md_section_editor import SectionEditor, SectionParser


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def craft_plugin_project(temp_dir):
    """Create a mock craft plugin project."""
    # Create plugin.json
    plugin_json = {
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "Test plugin"
    }
    (temp_dir / ".claude-plugin").mkdir()
    (temp_dir / ".claude-plugin" / "plugin.json").write_text(json.dumps(plugin_json, indent=2))

    # Create commands
    (temp_dir / "commands").mkdir()
    (temp_dir / "commands" / "test-command.md").write_text("# Test Command")

    # Create skills
    (temp_dir / "skills").mkdir()
    (temp_dir / "skills" / "test-skill.md").write_text("# Test Skill")

    # Create CLAUDE.md
    claude_md = """# CLAUDE.md - test-plugin

**1 commands** · **1 skills** · **0 agents**

**Current Version:** v0.9.0

## Quick Commands

| Task | Command |
|------|---------|
| Test | /test |

## Testing

Run tests with pytest.
"""
    (temp_dir / "CLAUDE.md").write_text(claude_md)

    return temp_dir


@pytest.fixture
def r_package_project(temp_dir):
    """Create a mock R package project."""
    description = """Package: testpkg
Type: Package
Title: Test Package
Version: 0.1.0
Description: A test R package.
"""
    (temp_dir / "DESCRIPTION").write_text(description)

    # Create R/ directory
    (temp_dir / "R").mkdir()
    (temp_dir / "R" / "functions.R").write_text("test_func <- function() {}")

    return temp_dir


@pytest.fixture
def teaching_project(temp_dir):
    """Create a mock teaching project."""
    quarto_yml = """
project:
  type: website
  title: "Test Course"
"""
    (temp_dir / "_quarto.yml").write_text(quarto_yml)

    course_yml = """
course:
  title: "STAT 101"
  semester: "Fall 2026"
"""
    (temp_dir / "course.yml").write_text(course_yml)

    return temp_dir


# ============================================================================
# UNIT TESTS: Project Detection
# ============================================================================

class TestProjectDetection:
    """Test project type detection logic."""

    def test_detect_craft_plugin(self, craft_plugin_project):
        """Verify craft plugin detection."""
        project_info = detect_project(str(craft_plugin_project))

        assert project_info["type"] == "craft-plugin"
        assert project_info["name"] == "test-plugin"
        assert project_info["version"] == "1.0.0"

    def test_detect_r_package(self, r_package_project):
        """Verify R package detection."""
        project_info = detect_project(str(r_package_project))

        assert project_info["type"] == "r-package"
        assert "testpkg" in project_info["name"]
        assert project_info["version"] == "0.1.0"

    def test_detect_teaching_site(self, teaching_project):
        """Verify teaching site detection."""
        project_info = detect_project(str(teaching_project))

        assert project_info["type"] == "teaching-site"

    def test_version_extraction_plugin_json(self, craft_plugin_project):
        """Test version extraction from plugin.json."""
        project_info = detect_project(str(craft_plugin_project))
        assert project_info["version"] == "1.0.0"

    def test_version_extraction_description(self, r_package_project):
        """Test version extraction from DESCRIPTION."""
        project_info = detect_project(str(r_package_project))
        assert project_info["version"] == "0.1.0"

    def test_command_counting(self, craft_plugin_project):
        """Test command discovery and counting."""
        project_info = detect_project(str(craft_plugin_project))
        assert project_info["command_count"] >= 1

    def test_empty_directory_detection(self, temp_dir):
        """Test detection on empty directory."""
        project_info = detect_project(str(temp_dir))
        # Should detect as generic or unknown
        assert "type" in project_info


# ============================================================================
# UNIT TESTS: Template Population
# ============================================================================

class TestTemplatePopulation:
    """Test template variable population."""

    def test_populate_plugin_variables(self, craft_plugin_project):
        """Test variable population for craft plugin."""
        populator = TemplatePopulator(str(craft_plugin_project))
        variables = populator.gather_variables()

        assert variables["plugin_name"] == "test-plugin"
        assert variables["version"] == "1.0.0"
        assert variables["command_count"] >= 1
        assert variables["skill_count"] >= 1

    def test_template_rendering(self, craft_plugin_project, temp_dir):
        """Test template rendering with variables."""
        template_content = """# {plugin_name}
Version: {version}
Commands: {command_count}
"""
        template_file = temp_dir / "test-template.md"
        template_file.write_text(template_content)

        populator = TemplatePopulator(str(craft_plugin_project))
        rendered = populator.render_template(str(template_file))

        assert "test-plugin" in rendered
        assert "1.0.0" in rendered
        assert "Commands:" in rendered

    def test_missing_variable_handling(self, craft_plugin_project):
        """Test handling of missing template variables."""
        populator = TemplatePopulator(str(craft_plugin_project))
        variables = populator.gather_variables()

        # Should have placeholder or None for missing variables
        assert "nonexistent_variable" not in variables or variables.get("nonexistent_variable") is None


# ============================================================================
# UNIT TESTS: Change Detection
# ============================================================================

class TestChangeDetection:
    """Test CLAUDE.md change detection."""

    def test_detect_version_change(self, craft_plugin_project):
        """Test version mismatch detection."""
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.check_version_sync()

        # CLAUDE.md has v0.9.0, plugin.json has 1.0.0
        assert len(issues) == 1
        assert issues[0].category == "version_mismatch"
        assert issues[0].severity == Severity.WARNING

    def test_detect_command_count_change(self, craft_plugin_project):
        """Test command count mismatch detection."""
        # CLAUDE.md says "1 commands", we have 1 command file
        # Should match, no issues
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.check_command_coverage()

        # Should find missing/stale commands if any
        assert isinstance(issues, list)

    def test_no_changes_when_synced(self, craft_plugin_project):
        """Test no issues when CLAUDE.md is up to date."""
        # Update CLAUDE.md to match project
        claude_md = (craft_plugin_project / "CLAUDE.md").read_text()
        claude_md = claude_md.replace("v0.9.0", "v1.0.0")
        (craft_plugin_project / "CLAUDE.md").write_text(claude_md)

        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.check_version_sync()

        assert len(issues) == 0


# ============================================================================
# UNIT TESTS: Validation (Audit)
# ============================================================================

class TestAuditValidation:
    """Test CLAUDE.md audit validation checks."""

    def test_audit_version_sync(self, craft_plugin_project):
        """Test version sync validation."""
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.check_version_sync()

        assert len(issues) > 0  # Version mismatch exists
        assert all(i.severity in [Severity.WARNING, Severity.ERROR] for i in issues)

    def test_audit_required_sections(self, craft_plugin_project):
        """Test required section validation."""
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.check_required_sections()

        # Should check for standard sections
        assert isinstance(issues, list)

    def test_audit_severity_classification(self, craft_plugin_project):
        """Test issue severity classification."""
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        all_issues = auditor.audit()

        # Should have different severity levels
        errors = [i for i in all_issues if i.severity == Severity.ERROR]
        warnings = [i for i in all_issues if i.severity == Severity.WARNING]
        info = [i for i in all_issues if i.severity == Severity.INFO]

        # At least one category should have issues
        assert len(errors) + len(warnings) + len(info) > 0

    def test_fixable_detection(self, craft_plugin_project):
        """Test detection of auto-fixable issues."""
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        all_issues = auditor.audit()

        fixable = [i for i in all_issues if i.fixable]
        # Version mismatch should be fixable
        assert any(i.category == "version_mismatch" for i in fixable)


# ============================================================================
# UNIT TESTS: Auto-Fix
# ============================================================================

class TestAutoFix:
    """Test auto-fix functionality."""

    def test_fix_version_mismatch(self, craft_plugin_project):
        """Test automatic version fix."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"

        # Verify mismatch exists
        content_before = claude_md_path.read_text()
        assert "v0.9.0" in content_before

        # Run fixer
        fixer = CLAUDEMDFixer(str(claude_md_path))
        fixer.fix_all()

        # Verify fix applied
        content_after = claude_md_path.read_text()
        assert "v1.0.0" in content_after
        assert "v0.9.0" not in content_after

    def test_dry_run_no_changes(self, craft_plugin_project):
        """Test dry-run mode doesn't modify file."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"
        content_before = claude_md_path.read_text()

        # Run in dry-run mode
        fixer = CLAUDEMDFixer(str(claude_md_path))
        fixer.fix_all(dry_run=True)

        # Verify no changes
        content_after = claude_md_path.read_text()
        assert content_before == content_after

    def test_backup_creation(self, craft_plugin_project):
        """Test backup file creation before fixing."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"
        backup_path = craft_plugin_project / ".CLAUDE.md.backup"

        # Remove any existing backup
        if backup_path.exists():
            backup_path.unlink()

        # Run fixer (should create backup)
        fixer = CLAUDEMDFixer(str(claude_md_path))
        fixer.fix_all()

        # Verify backup created
        assert backup_path.exists()

    def test_scope_filtering(self, craft_plugin_project):
        """Test fix scope filtering (errors/warnings/all)."""
        fixer = CLAUDEMDFixer(str(craft_plugin_project / "CLAUDE.md"))

        # Test warnings scope
        fixer.fix_all(scope="warnings")

        # Should only fix warning-level issues
        # (Implementation would track which issues were fixed)


# ============================================================================
# UNIT TESTS: Section Editing
# ============================================================================

class TestSectionEditing:
    """Test section parsing and editing."""

    def test_section_parsing(self, craft_plugin_project):
        """Test parsing CLAUDE.md into sections."""
        parser = SectionParser(str(craft_plugin_project / "CLAUDE.md"))
        sections = parser.parse()

        assert len(sections) > 0
        assert any(s["title"] == "Quick Commands" for s in sections)

    def test_section_extraction(self, craft_plugin_project):
        """Test extracting specific section content."""
        parser = SectionParser(str(craft_plugin_project / "CLAUDE.md"))
        content = parser.get_section("Testing")

        assert content is not None
        assert "pytest" in content.lower()

    def test_section_update(self, craft_plugin_project, temp_dir):
        """Test updating section content."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"

        editor = SectionEditor(str(claude_md_path))
        new_content = "## Testing\n\nRun with: python3 -m pytest"

        editor.update_section("Testing", new_content)

        # Verify update
        updated = claude_md_path.read_text()
        assert "python3 -m pytest" in updated


# ============================================================================
# END-TO-END TESTS: Complete Workflows
# ============================================================================

class TestEndToEndWorkflows:
    """Test complete claude-md workflows."""

    def test_scaffold_to_audit_workflow(self, temp_dir):
        """Test: scaffold new CLAUDE.md → audit → should pass."""
        # Create minimal plugin structure
        (temp_dir / ".claude-plugin").mkdir()
        plugin_json = {"name": "new-plugin", "version": "1.0.0"}
        (temp_dir / ".claude-plugin" / "plugin.json").write_text(json.dumps(plugin_json))

        # Scaffold (would use TemplatePopulator in real scenario)
        populator = TemplatePopulator(str(temp_dir))
        variables = populator.gather_variables()

        # Create CLAUDE.md
        claude_md_content = f"""# CLAUDE.md - {variables['plugin_name']}

**Current Version:** v{variables['version']}

## Quick Commands

TBD

## Testing

Run tests.
"""
        (temp_dir / "CLAUDE.md").write_text(claude_md_content)

        # Audit should pass (no version mismatch)
        auditor = CLAUDEMDAuditor(str(temp_dir / "CLAUDE.md"))
        issues = auditor.check_version_sync()

        assert len(issues) == 0  # Should be in sync

    def test_update_audit_fix_workflow(self, craft_plugin_project):
        """Test: update → audit → fix → audit passes."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"

        # 1. Audit (should find version mismatch)
        auditor = CLAUDEMDAuditor(str(claude_md_path))
        issues_before = auditor.check_version_sync()
        assert len(issues_before) > 0

        # 2. Fix
        fixer = CLAUDEMDFixer(str(claude_md_path))
        fixer.fix_all()

        # 3. Audit again (should pass)
        auditor2 = CLAUDEMDAuditor(str(claude_md_path))
        issues_after = auditor2.check_version_sync()
        assert len(issues_after) == 0

    def test_edit_audit_workflow(self, craft_plugin_project):
        """Test: edit section → audit → should still be valid."""
        claude_md_path = craft_plugin_project / "CLAUDE.md"

        # Fix version first
        fixer = CLAUDEMDFixer(str(claude_md_path))
        fixer.fix_all()

        # Edit a section
        editor = SectionEditor(str(claude_md_path))
        new_testing = "## Testing\n\nComprehensive test suite with pytest."
        editor.update_section("Testing", new_testing)

        # Audit should still pass
        auditor = CLAUDEMDAuditor(str(claude_md_path))
        issues = auditor.audit()

        # Should have no critical errors
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_full_maintenance_cycle(self, craft_plugin_project):
        """Test complete maintenance workflow."""
        # Simulate adding a new command
        (craft_plugin_project / "commands" / "new-feature.md").write_text("# New Feature")

        # 1. Update CLAUDE.md (simulated - would use updater)
        # 2. Audit
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        all_issues = auditor.audit()

        # 3. Fix what can be fixed
        fixer = CLAUDEMDFixer(str(craft_plugin_project / "CLAUDE.md"))
        fixer.fix_all()

        # 4. Verify improvement
        auditor2 = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues_after = auditor2.audit()

        # Should have fewer errors after fixing
        errors_before = [i for i in all_issues if i.severity == Severity.ERROR]
        errors_after = [i for i in issues_after if i.severity == Severity.ERROR]
        assert len(errors_after) <= len(errors_before)


# ============================================================================
# END-TO-END TESTS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_claude_md_handling(self, temp_dir):
        """Test handling when CLAUDE.md doesn't exist."""
        # Should gracefully handle missing file
        with pytest.raises((FileNotFoundError, Exception)):
            auditor = CLAUDEMDAuditor(str(temp_dir / "CLAUDE.md"))
            auditor.audit()

    def test_corrupt_json_handling(self, temp_dir):
        """Test handling corrupt plugin.json."""
        (temp_dir / ".claude-plugin").mkdir()
        (temp_dir / ".claude-plugin" / "plugin.json").write_text("{invalid json")

        # Should handle gracefully
        project_info = detect_project(str(temp_dir))
        assert "type" in project_info  # Should still return something

    def test_empty_claude_md_handling(self, temp_dir):
        """Test handling empty CLAUDE.md."""
        (temp_dir / "CLAUDE.md").write_text("")

        auditor = CLAUDEMDAuditor(str(temp_dir / "CLAUDE.md"))
        issues = auditor.audit()

        # Should identify missing sections as issues
        assert len(issues) > 0


# ============================================================================
# END-TO-END TESTS: Integration with Craft
# ============================================================================

class TestCraftIntegration:
    """Test integration with craft workflows."""

    def test_craft_check_integration(self, craft_plugin_project):
        """Test integration with /craft:check workflow."""
        # Simulate /craft:check calling audit
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.audit()

        # Should return structured issues for craft:check
        assert isinstance(issues, list)
        assert all(hasattr(i, "severity") for i in issues)

    def test_git_worktree_scenario(self, craft_plugin_project):
        """Test typical git worktree workflow."""
        # Simulate feature branch workflow
        # 1. Make changes (add command)
        (craft_plugin_project / "commands" / "feature-x.md").write_text("# Feature X")

        # 2. Update CLAUDE.md
        # 3. Audit before commit
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        issues = auditor.audit()

        # Should be able to identify any issues before PR
        assert isinstance(issues, list)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""

    def test_audit_performance(self, craft_plugin_project):
        """Test audit completes in < 3 seconds."""
        import time

        start = time.time()
        auditor = CLAUDEMDAuditor(str(craft_plugin_project / "CLAUDE.md"))
        auditor.audit()
        elapsed = time.time() - start

        assert elapsed < 3.0  # Should be fast

    def test_template_population_performance(self, craft_plugin_project):
        """Test template population completes quickly."""
        import time

        start = time.time()
        populator = TemplatePopulator(str(craft_plugin_project))
        populator.gather_variables()
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should be very fast


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
