#!/usr/bin/env python3
"""
Test suite for utils/dry_run_output.py

Tests the dry-run output utility functions, data models, and formatting.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.dry_run_output import (
    render_dry_run_preview,
    render_simple_preview,
    RiskLevel,
    OperationType,
    Severity,
    Operation,
    Warning,
    OperationPlan,
    _wrap_text
)


def test_render_basic_preview():
    """Test basic dry-run preview rendering"""
    preview = render_dry_run_preview(
        command_name="Test Command",
        actions=["Action 1", "Action 2"],
        warnings=None,
        summary=None
    )

    assert "🔍 DRY RUN: Test Command" in preview
    assert "Action 1" in preview
    assert "Action 2" in preview
    assert "Run without --dry-run to execute" in preview

    # Check box structure
    assert preview.startswith("┌")
    assert preview.endswith("┘")
    assert "├" in preview
    assert "│" in preview

    print("✅ test_render_basic_preview passed")


def test_render_with_warnings():
    """Test dry-run preview with warnings"""
    preview = render_dry_run_preview(
        command_name="Test Command",
        actions=["Delete 3 files"],
        warnings=["This is irreversible", "Backup recommended"],
        summary="3 files to delete"
    )

    assert "⚠ Warnings:" in preview
    assert "This is irreversible" in preview
    assert "Backup recommended" in preview
    assert "📊 Summary: 3 files to delete" in preview

    print("✅ test_render_with_warnings passed")


def test_render_with_summary():
    """Test dry-run preview with summary line"""
    preview = render_dry_run_preview(
        command_name="Clean Branches",
        actions=["Delete 5 branches"],
        summary="5 branches to delete, 2 skipped"
    )

    assert "📊 Summary: 5 branches to delete, 2 skipped" in preview

    print("✅ test_render_with_summary passed")


def test_box_width_consistency():
    """Test that all lines have consistent width"""
    preview = render_dry_run_preview(
        command_name="Test",
        actions=["Action"],
        width=65
    )

    lines = preview.split('\n')

    # All lines should be exactly 65 characters
    for line in lines:
        assert len(line) == 65, f"Line length {len(line)} != 65: {repr(line)}"

    print("✅ test_box_width_consistency passed")


def test_text_wrapping():
    """Test that long text is properly wrapped"""
    long_action = "This is a very long action description that should be wrapped to fit within the specified width of the output box"

    preview = render_dry_run_preview(
        command_name="Test",
        actions=[long_action],
        width=65
    )

    # Should not exceed width
    lines = preview.split('\n')
    for line in lines:
        assert len(line) == 65, f"Line length {len(line)} != 65: {repr(line)}"

    # Should contain the text (may be split across lines)
    assert "very long action" in preview
    # Check for parts of the phrase that should be present
    assert "wrapped" in preview or "fit within" in preview

    print("✅ test_text_wrapping passed")


def test_wrap_text_function():
    """Test the _wrap_text helper function"""
    text = "This is a long piece of text that needs to be wrapped"
    wrapped = _wrap_text(text, max_width=20)

    assert isinstance(wrapped, list)
    assert all(len(line) <= 20 for line in wrapped)
    assert ' '.join(wrapped) == text

    # Test short text
    short = "Short"
    wrapped_short = _wrap_text(short, max_width=20)
    assert wrapped_short == ["Short"]

    print("✅ test_wrap_text_function passed")


def test_empty_actions():
    """Test that empty actions list raises error or handles gracefully"""
    try:
        preview = render_dry_run_preview(
            command_name="Test",
            actions=[],
            width=65
        )
        # If it doesn't raise an error, it should at least produce valid output
        assert len(preview) > 0
        print("✅ test_empty_actions passed (handled gracefully)")
    except ValueError:
        print("✅ test_empty_actions passed (raised ValueError as expected)")


def test_long_command_name():
    """Test handling of very long command names"""
    long_name = "This Is A Very Long Command Name That Exceeds Normal Length"

    preview = render_dry_run_preview(
        command_name=long_name,
        actions=["Action"],
        width=65
    )

    # Should still produce valid output
    assert "🔍 DRY RUN:" in preview

    print("✅ test_long_command_name passed")


def test_render_simple_preview():
    """Test simple preview rendering"""
    preview = render_simple_preview(
        command_name="Read Only Command",
        message="This command only reads data. No changes will be made."
    )

    assert "🔍 DRY RUN: Read Only Command" in preview
    assert "only reads data" in preview

    print("✅ test_render_simple_preview passed")


def test_operation_data_model():
    """Test Operation data model"""
    op = Operation(
        type=OperationType.DELETE,
        description="Delete merged branch",
        details=["feature/old-branch", "Last commit: 2 weeks ago"],
        target="feature/old-branch",
        risk_level=RiskLevel.HIGH
    )

    assert op.type == OperationType.DELETE
    assert op.description == "Delete merged branch"
    assert len(op.details) == 2
    assert op.risk_level == RiskLevel.HIGH

    # Test to_dict
    d = op.to_dict()
    assert d['type'] == 'delete'
    assert d['risk_level'] == 'high'
    assert d['target'] == 'feature/old-branch'

    print("✅ test_operation_data_model passed")


def test_warning_data_model():
    """Test Warning data model"""
    warning = Warning(
        message="This operation is irreversible",
        severity=Severity.CRITICAL,
        reason="No undo available"
    )

    assert warning.message == "This operation is irreversible"
    assert warning.severity == Severity.CRITICAL

    # Test to_dict
    d = warning.to_dict()
    assert d['severity'] == 'critical'
    assert d['reason'] == "No undo available"

    print("✅ test_warning_data_model passed")


def test_operation_plan_data_model():
    """Test OperationPlan data model"""
    op1 = Operation(
        type=OperationType.DELETE,
        description="Delete branch",
        details=["feature/old"],
        risk_level=RiskLevel.HIGH
    )

    warn1 = Warning(
        message="Branch has uncommitted changes",
        severity=Severity.WARNING
    )

    plan = OperationPlan(
        operations=[op1],
        warnings=[warn1],
        summary="1 branch to delete",
        risk_level=RiskLevel.HIGH
    )

    assert len(plan.operations) == 1
    assert len(plan.warnings) == 1
    assert plan.summary == "1 branch to delete"

    # Test to_dict
    d = plan.to_dict()
    assert len(d['operations']) == 1
    assert len(d['warnings']) == 1
    assert d['risk_level'] == 'high'

    print("✅ test_operation_plan_data_model passed")


def test_risk_level_enum():
    """Test RiskLevel enum values"""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"

    print("✅ test_risk_level_enum passed")


def test_operation_type_enum():
    """Test OperationType enum values"""
    assert OperationType.CREATE.value == "create"
    assert OperationType.MODIFY.value == "modify"
    assert OperationType.DELETE.value == "delete"
    assert OperationType.EXECUTE.value == "execute"
    assert OperationType.PUBLISH.value == "publish"

    print("✅ test_operation_type_enum passed")


def test_severity_enum():
    """Test Severity enum values"""
    assert Severity.INFO.value == "info"
    assert Severity.WARNING.value == "warning"
    assert Severity.CRITICAL.value == "critical"

    print("✅ test_severity_enum passed")


def test_real_world_example_git_clean():
    """Test realistic git:clean dry-run output"""
    preview = render_dry_run_preview(
        command_name="Clean Merged Branches",
        actions=[
            "✓ Delete 3 local branches (merged to dev):",
            "  - feature/auth-system",
            "  - fix/login-bug",
            "  - refactor/api-cleanup",
            "",
            "⊘ Skip 1 branch:",
            "  - feature/wip (uncommitted changes)"
        ],
        warnings=["Branch feature/wip has uncommitted changes"],
        summary="3 branches to delete, 1 skipped",
        risk_level=RiskLevel.CRITICAL
    )

    assert "Clean Merged Branches" in preview
    assert "3 local branches" in preview
    assert "feature/auth-system" in preview
    assert "⚠ Warnings:" in preview
    assert "📊 Summary:" in preview

    print("✅ test_real_world_example_git_clean passed")


def test_real_world_example_ci_generate():
    """Test realistic ci:generate dry-run output"""
    preview = render_dry_run_preview(
        command_name="Generate CI Workflow",
        actions=[
            "✓ Create .github/workflows/ci.yml (~45 lines)",
            "",
            "Configuration:",
            "  - Project type: Python (uv)",
            "  - Test framework: pytest",
            "  - Python versions: 3.9, 3.10, 3.11"
        ],
        warnings=["No existing workflow file"],
        summary="1 file to create",
        risk_level=RiskLevel.MEDIUM
    )

    assert "Generate CI Workflow" in preview
    assert ".github/workflows/ci.yml" in preview
    assert "Python (uv)" in preview

    print("✅ test_real_world_example_ci_generate passed")


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_render_basic_preview,
        test_render_with_warnings,
        test_render_with_summary,
        test_box_width_consistency,
        test_text_wrapping,
        test_wrap_text_function,
        test_empty_actions,
        test_long_command_name,
        test_render_simple_preview,
        test_operation_data_model,
        test_warning_data_model,
        test_operation_plan_data_model,
        test_risk_level_enum,
        test_operation_type_enum,
        test_severity_enum,
        test_real_world_example_git_clean,
        test_real_world_example_ci_generate,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 65)
    print("🧪 Running Dry-Run Output Tests")
    print("=" * 65 + "\n")

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1

    print("\n" + "=" * 65)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 65 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
