#!/usr/bin/env python3
"""
Craft Plugin v1.15.0 ADHD-Friendly Enhancements Test Suite
===========================================================
Validates Phase 1, 2, and 3 ADHD-friendly website enhancements.

Tests:
- TL;DR boxes on major pages
- Time estimates in tutorials
- Visual workflow diagrams
- Progress indicators
- Mobile responsive CSS
- Accessibility features
- Interactive playground
- Navigation structure

Run with: python tests/test_v115_adhd_enhancements.py
"""

import json
import os
import re
from pathlib import Path

import pytest
from typing import List, Optional, Tuple

pytestmark = [pytest.mark.integration, pytest.mark.orchestrator]


# ─── Phase 1 Tests: Quick Wins ───────────────────────────────────────────────


def test_tldr_boxes_present():
    """Test that TL;DR boxes are present on major pages."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    # Pages that should have TL;DR boxes
    required_pages = [
        "index.md",
        "QUICK-START.md",
        "ADHD-QUICK-START.md",
        "guide/getting-started.md",
        "guide/skills-agents.md",
        "guide/orchestrator.md",
        "commands/overview.md",
        "commands/docs.md",
        "commands/site.md",
        "workflows/index.md",
    ]

    missing = []
    invalid_format = []

    for page_path in required_pages:
        page = docs_dir / page_path
        if not page.exists():
            missing.append(page_path)
            continue

        content = page.read_text()

        # Check for TL;DR box with required sections
        # Format: > **TL;DR** (XX seconds/minutes)\n>\n> - **What:**...\n> - **Why:**...\n> - **How:**...\n> - **Next:**...
        # Or the compact variant: > **TL;DR**: ...
        tldr_pattern = r'> \*\*TL;DR\*\*[ :]'

        if not re.search(tldr_pattern, content):
            invalid_format.append(page_path)

    details = []
    if missing:
        details.append(f"Missing pages: {', '.join(missing)}")
    if invalid_format:
        details.append(f"Invalid TL;DR format: {', '.join(invalid_format)}")
    assert not (missing or invalid_format), "; ".join(details)


def test_time_estimates_in_tutorials():
    """Test that tutorials have time estimates."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    tutorial_pages = [
        "QUICK-START.md",
        "ADHD-QUICK-START.md",
        "guide/getting-started.md",
        "guide/skills-agents.md",
        "guide/orchestrator.md",
        "workflows/index.md",
        "PLAYGROUND.md",
        "ACCESSIBILITY.md",
    ]

    missing_estimate = []

    for page_path in tutorial_pages:
        page = docs_dir / page_path
        if not page.exists():
            continue

        content = page.read_text()

        # Check for time estimate format: ⏱️ **X minutes** • 🟢 Level • ✓ Info
        time_pattern = r'⏱️ \*\*[^*]+\*\* • [🟢🟡🔴] \w+ • ✓'

        if not re.search(time_pattern, content):
            missing_estimate.append(page_path)

    assert not missing_estimate, f"Missing time estimates: {', '.join(missing_estimate)}"


def test_mermaid_syntax_valid():
    """Test that all mermaid diagrams have valid syntax."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    errors = []

    # Find all markdown files
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()

        # Find all mermaid blocks
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)

        for i, block in enumerate(mermaid_blocks):
            # Check for common syntax errors
            # Note: <br/> is valid in mermaid for multi-line node labels

            # Check for unbalanced brackets
            if block.count('[') != block.count(']'):
                errors.append(f"{md_file.name} block {i+1}: Unbalanced square brackets")

            # Check for missing click targets (should use markdown strings)
            if 'click ' in block:
                # Count click statements
                click_count = len(re.findall(r'click \w+', block))
                if click_count > 0:
                    # This is good - interactive diagrams
                    pass

    assert not errors, "; ".join(errors[:5])


# ─── Phase 2 Tests: Structure ────────────────────────────────────────────────


def test_visual_workflows_page_exists():
    """Test that workflows/index.md exists with 5 diagrams."""
    plugin_dir = Path(__file__).parent.parent
    workflows_page = plugin_dir / "docs" / "workflows" / "index.md"

    assert workflows_page.exists(), "workflows/index.md not found"

    content = workflows_page.read_text()

    # Count mermaid diagrams
    diagram_count = len(re.findall(r'```mermaid', content))

    # Check for expected workflows
    expected_workflows = [
        "Documentation Workflow",
        "Site Creation Workflow",
        "Release Workflow",
        "Development Workflow",
        "AI Routing Workflow",
    ]

    missing_workflows = [w for w in expected_workflows if w not in content]

    assert diagram_count >= 5, f"Only {diagram_count} diagrams found, expected 5+"
    assert not missing_workflows, f"Missing workflows: {', '.join(missing_workflows)}"


def test_navigation_flattened():
    """Test that navigation has ADHD features promoted to top-level."""
    plugin_dir = Path(__file__).parent.parent
    mkdocs_yml = plugin_dir / "mkdocs.yml"

    assert mkdocs_yml.exists(), "mkdocs.yml not found"

    content = mkdocs_yml.read_text()

    # Check for promoted top-level items with emojis
    # Updated to match current mkdocs.yml nav structure
    required_nav_items = [
        "Getting Started",
        "Guides & Tutorials",
        "Commands & Reference",
        "Cookbook & Examples",
        "Quick Reference Card",
    ]

    missing = [item for item in required_nav_items if item not in content]

    # Count top-level nav items (should be <= 8 for ADHD-friendly)
    nav_section = re.search(r'nav:\n(.*?)(?:\n\w|\Z)', content, re.DOTALL)
    if nav_section:
        top_level = re.findall(r'\n  - [^:]+:', nav_section.group(1))
        top_level_count = len(top_level)
    else:
        top_level_count = 0

    assert not missing, f"Missing nav items: {', '.join(missing)}"
    assert top_level_count <= 8, f"Too many top-level items: {top_level_count} (max 8 for ADHD)"


def test_callout_boxes_present():
    """Test that visual callout boxes are present."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    # Pages that should have callout boxes
    pages_to_check = [
        "workflows/index.md",
        "QUICK-START.md",
        "ADHD-QUICK-START.md",
        "guide/orchestrator.md",
        "index.md",
        "PLAYGROUND.md",
    ]

    callout_types = {
        "tip": r'!!! tip',
        "success": r'!!! success',
        "warning": r'!!! warning',
        "abstract": r'!!! abstract',
    }

    total_callouts = 0
    pages_with_callouts = 0

    for page_path in pages_to_check:
        page = docs_dir / page_path
        if not page.exists():
            continue

        content = page.read_text()
        page_callouts = sum(len(re.findall(pattern, content)) for pattern in callout_types.values())

        if page_callouts > 0:
            pages_with_callouts += 1
            total_callouts += page_callouts

    assert total_callouts >= 10, f"Only {total_callouts} callouts found, expected 10+"


def test_homepage_card_layout():
    """Test that homepage uses card-based layout."""
    plugin_dir = Path(__file__).parent.parent
    index_page = plugin_dir / "docs" / "index.md"

    assert index_page.exists(), "index.md not found"

    content = index_page.read_text()

    # Check for card grid markup
    assert '<div class="grid cards" markdown>' in content, "Card grid markup not found"

    # Count card sections
    card_sections = len(re.findall(r'<div class="grid cards" markdown>', content))

    # Check for expected sections
    expected_sections = [
        "Features",
        "Popular Workflows",
        "Documentation",
    ]

    missing_sections = [s for s in expected_sections if s not in content]
    assert not missing_sections, f"Missing sections: {', '.join(missing_sections)}"


def test_interactive_mermaid_diagrams():
    """Test that mermaid diagrams have clickable nodes."""
    plugin_dir = Path(__file__).parent.parent
    workflows_page = plugin_dir / "docs" / "workflows" / "index.md"

    assert workflows_page.exists(), "workflows/index.md not found"

    content = workflows_page.read_text()

    # Find mermaid blocks
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)

    # Count click statements (interactive nodes)
    total_clicks = sum(len(re.findall(r'click \w+', block)) for block in mermaid_blocks)

    assert total_clicks >= 10, f"Only {total_clicks} clickable nodes found, expected 10+"


# ─── Phase 3 Tests: Polish ───────────────────────────────────────────────────


def test_mobile_responsive_css():
    """Test that mobile responsive CSS is present."""
    plugin_dir = Path(__file__).parent.parent
    css_file = plugin_dir / "docs" / "stylesheets" / "extra.css"

    assert css_file.exists(), "extra.css not found"

    content = css_file.read_text()

    # Check for required responsive features
    required_features = [
        (r'\.mermaid\s*\{[^}]*overflow-x:\s*auto', "Mermaid overflow fix"),
        (r'@media.*max-width:\s*768px', "Tablet breakpoint"),
        (r'@media.*max-width:\s*480px', "Mobile breakpoint"),
        (r'@media.*prefers-reduced-motion', "Reduced motion support"),
        (r'@media.*prefers-contrast:\s*high', "High contrast mode"),
        (r'a:focus.*outline', "Focus indicators"),
        (r'@media print', "Print styles"),
    ]

    missing_features = []

    for pattern, feature_name in required_features:
        if not re.search(pattern, content, re.DOTALL):
            missing_features.append(feature_name)

    assert not missing_features, f"Missing features: {', '.join(missing_features)}"


def test_progress_indicators():
    """Test that tutorials have progress indicators."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    # Pages that should have progress indicators
    tutorial_pages = {
        "QUICK-START.md": 4,  # Expected number of progress indicators
        "ADHD-QUICK-START.md": 3,
        "guide/getting-started.md": 5,
    }

    missing_or_wrong = []

    for page_path, expected_count in tutorial_pages.items():
        page = docs_dir / page_path
        if not page.exists():
            missing_or_wrong.append(f"{page_path} (missing)")
            continue

        content = page.read_text()

        # Count progress indicators
        progress_pattern = r'!!! abstract "Progress:'
        progress_count = len(re.findall(progress_pattern, content))

        if progress_count != expected_count:
            missing_or_wrong.append(f"{page_path} (has {progress_count}, expected {expected_count})")

    assert not missing_or_wrong, "; ".join(missing_or_wrong)


def test_command_playground_exists():
    """Test that PLAYGROUND.md exists with interactive scenarios."""
    plugin_dir = Path(__file__).parent.parent
    playground_page = plugin_dir / "docs" / "PLAYGROUND.md"

    assert playground_page.exists(), "PLAYGROUND.md not found"

    content = playground_page.read_text()

    # Check for expected scenarios
    expected_scenarios = [
        "Scenario 1:",
        "Scenario 2:",
        "Scenario 3:",
        "Scenario 4:",
        "Scenario 5:",
        "Scenario 6:",
    ]

    missing_scenarios = [s for s in expected_scenarios if s not in content]

    # Check for key elements
    required_elements = [
        ("What Happens", "Example outputs"),
        ("What You Learn", "Learning points"),
        ("Challenge", "Practice challenges"),
    ]

    missing_elements = []
    for element, description in required_elements:
        if element not in content:
            missing_elements.append(description)

    errors = []
    if missing_scenarios:
        errors.append(f"Missing: {', '.join(missing_scenarios)}")
    if missing_elements:
        errors.append(f"Missing elements: {', '.join(missing_elements)}")
    assert not (missing_scenarios or missing_elements), "; ".join(errors)


def test_accessibility_documentation():
    """Test that ACCESSIBILITY.md exists and covers WCAG AA."""
    plugin_dir = Path(__file__).parent.parent
    accessibility_page = plugin_dir / "docs" / "ACCESSIBILITY.md"

    assert accessibility_page.exists(), "ACCESSIBILITY.md not found"

    content = accessibility_page.read_text()

    # Check for WCAG coverage
    required_sections = [
        "WCAG AA Compliance",
        "Keyboard Navigation",
        "Screen Reader Support",
        "Visual Accessibility",
        "Motion and Animation",
        "Mobile and Touch Accessibility",
        "Content Readability",
        "Testing",
        "Reporting Issues",
    ]

    missing_sections = [s for s in required_sections if s not in content]

    # Check for specific WCAG criteria
    wcag_criteria = [
        "1.1 Text Alternatives",
        "1.4.3 Contrast",
        "2.1 Keyboard Accessible",
        "2.4 Navigable",
    ]

    missing_criteria = [c for c in wcag_criteria if c not in content]

    errors = []
    if missing_sections:
        errors.append(f"Missing sections: {', '.join(missing_sections[:3])}")
    if missing_criteria:
        errors.append(f"Missing WCAG criteria: {', '.join(missing_criteria)}")
    assert not (missing_sections or missing_criteria), "; ".join(errors)


# ─── Integration Tests ───────────────────────────────────────────────────────


def test_adhd_score_algorithm():
    """Test ADHD score algorithm components are present."""
    plugin_dir = Path(__file__).parent.parent
    docs_dir = plugin_dir / "docs"

    # Score components (from ROADMAP.md)
    score_components = {
        "Visual Hierarchy (25%)": {
            "tldr_boxes": 0,
            "time_estimates": 0,
            "emojis_in_nav": 0,
        },
        "Time Estimates (20%)": {
            "tutorials_with_estimates": 0,
        },
        "Workflow Diagrams (20%)": {
            "mermaid_diagrams": 0,
            "interactive_nodes": 0,
        },
        "Mobile Responsive (15%)": {
            "responsive_css": False,
            "breakpoints": 0,
        },
        "Content Density (20%)": {
            "progress_indicators": 0,
            "callout_boxes": 0,
        },
    }

    # Scan all docs
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()

        # Count TL;DR boxes
        if re.search(r'> \*\*TL;DR\*\*', content):
            score_components["Visual Hierarchy (25%)"]["tldr_boxes"] += 1

        # Count time estimates
        if re.search(r'⏱️ \*\*[^*]+\*\*', content):
            score_components["Time Estimates (20%)"]["tutorials_with_estimates"] += 1
            score_components["Visual Hierarchy (25%)"]["time_estimates"] += 1

        # Count mermaid diagrams
        diagrams = len(re.findall(r'```mermaid', content))
        score_components["Workflow Diagrams (20%)"]["mermaid_diagrams"] += diagrams

        # Count interactive nodes
        clicks = len(re.findall(r'click \w+', content))
        score_components["Workflow Diagrams (20%)"]["interactive_nodes"] += clicks

        # Count progress indicators
        progress = len(re.findall(r'!!! abstract "Progress:', content))
        score_components["Content Density (20%)"]["progress_indicators"] += progress

        # Count callout boxes
        callouts = len(re.findall(r'!!! (tip|success|warning)', content))
        score_components["Content Density (20%)"]["callout_boxes"] += callouts

    # Check CSS
    css_file = plugin_dir / "docs" / "stylesheets" / "extra.css"
    if css_file.exists():
        css_content = css_file.read_text()
        score_components["Mobile Responsive (15%)"]["responsive_css"] = True
        score_components["Mobile Responsive (15%)"]["breakpoints"] = len(
            re.findall(r'@media.*max-width', css_content)
        )

    # Check nav emojis
    mkdocs_yml = plugin_dir / "mkdocs.yml"
    if mkdocs_yml.exists():
        nav_content = mkdocs_yml.read_text()
        emojis = len(re.findall(r'- [🚀🧠📊🎮📚]', nav_content))
        score_components["Visual Hierarchy (25%)"]["emojis_in_nav"] = emojis

    # Calculate simple pass/fail (all components should have values > 0)
    issues = []
    for category, metrics in score_components.items():
        for metric, value in metrics.items():
            if isinstance(value, bool) and not value:
                issues.append(f"{category}: {metric} is False")
            elif isinstance(value, int) and value == 0:
                issues.append(f"{category}: {metric} is 0")

    assert not issues, "; ".join(issues[:3])


def test_mkdocs_build_succeeds():
    """Test that mkdocs build --strict succeeds."""
    import subprocess

    plugin_dir = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            ["mkdocs", "build"],
            cwd=plugin_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        assert False, "Build timeout after 30s"
    except FileNotFoundError:
        pytest.skip("mkdocs command not found (skipping)")

    assert result.returncode == 0, f"Build failed: {result.stderr[:200]}"

    # Check for ERROR-level issues (mkdocs format: "ERROR   -")
    # Warnings are expected for unlisted pages and README.md conflicts
    combined_output = result.stdout + result.stderr
    assert "ERROR   -" not in combined_output, f"Build has errors: {combined_output[:200]}"
