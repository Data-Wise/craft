#!/usr/bin/env python3
"""
Test Hub Integration with Discovery Engine
===========================================
Simulates what happens when /craft:hub is invoked.

Run with: python tests/test_hub_integration.py
"""

import sys
from pathlib import Path

import pytest

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import get_command_stats, load_cached_commands

pytestmark = [pytest.mark.integration, pytest.mark.hub]

def _check_hub_display():
    """Test that hub can generate display with discovery data."""

    print("=" * 70)
    print("🧪 Testing Hub Integration")
    print("=" * 70)
    print()

    # Step 0: Load command data
    print("Step 0: Loading command data from discovery engine...")
    stats = get_command_stats()
    commands = load_cached_commands()

    print(f"  ✓ Loaded {stats['total']} commands")
    print(f"  ✓ Found {len(stats['categories'])} categories")
    print()

    # Step 1: Detect project context (simulated)
    print("Step 1: Detecting project context...")
    project_name = "craft"
    project_type = "Python Plugin"
    git_branch = "feature/hub-v2"
    print(f"  ✓ Project: {project_name} ({project_type}) on {git_branch}")
    print()

    # Step 2: Generate hub display
    print("Step 2: Generating hub display...")
    print()

    # Generate display with real data
    display = f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT - Full Stack Developer Toolkit v1.22.0                         │
│ 📍 {project_name} ({project_type}) on {git_branch}                      │
│ 📊 {stats['total']} Commands | 21 Skills | 8 Agents | 4 Modes           │
├─────────────────────────────────────────────────────────────────────────┤
│ ⚡ SMART COMMANDS (Start Here):                                         │
│    /craft:do <task>     Universal command - AI routes to best workflow │
│    /craft:check         Pre-flight checks for commit/pr/release        │
│    /craft:smart-help    Context-aware help and suggestions             │
├─────────────────────────────────────────────────────────────────────────┤
│ 🎚️ MODES (default|debug|optimize|release):                             │
│    default  < 10s   Quick analysis, minimal output                     │
│    debug    < 120s  Verbose traces, detailed fixes                     │
│    optimize < 180s  Performance focus, parallel execution              │
│    release  < 300s  Comprehensive checks, full audit                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 💻 CODE ({stats['categories'].get('code', 0)})              🧪 TEST                                                     │
│   /craft:code:lint [mode]          /craft:test [mode]                   │
│   /craft:code:coverage             /craft:code:test-gen                 │
│   /craft:code:deps-audit                                                │
│   /craft:ci:local                                                  │
│                                                                         │
│ 📄 DOCS ({stats['categories'].get('docs', 0)})             🏗️ ARCH ({stats['categories'].get('arch', 0)})            │
│   /craft:docs:update               /craft:arch:analyze [mode]           │
│   /craft:docs:changelog            /craft:arch:plan                     │
│   /craft:docs:claude-md:*          /craft:arch:review                   │
│   (site-building moved to folio)   /craft:arch:diagram                  │
│                                                                         │
│ 🔀 GIT ({stats['categories'].get('git', 0)}+4 guides)      📖 SITE ({stats['categories'].get('site', 0)})            │
│   /craft:git:worktree              /craft:site:deploy                   │
│   /craft:git:status                  (rest moved to folio)                │
│   /craft:git:clean                                                      │
│   /craft:git:branch                                                     │
│                                                                         │
│ 📋 PLAN ({stats['categories'].get('plan', 0)})              🎯 MORE CATEGORIES                    │
│   /craft:plan:feature              • CI ({stats['categories'].get('ci', 0)}) • DIST ({stats['categories'].get('dist', 0)}) • WORKFLOW ({stats['categories'].get('workflow', 0)})     │
│   /craft:plan:sprint               • UTILS ({stats['categories'].get('utils', 0)}) • CHECK (1) • DO (1)     │
│   /craft:plan:roadmap              • ORCHESTRATE (1) • SMART-HELP (1)  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ 🎯 Quick Actions:                                                       │
│    /craft:do "fix bug"    /craft:check --for pr    /craft:smart-help   │
│    /craft:test debug      /craft:arch:analyze      /craft:git:status     │
│                                                                         │
│ 💡 TIP: Say "/craft:hub <category>" to see all commands in category    │
│         Example: /craft:hub code                                        │
└─────────────────────────────────────────────────────────────────────────┘
"""

    print(display)

    # Validation
    print()
    print("=" * 70)
    print("✅ Validation")
    print("=" * 70)

    checks = [
        # Floors reflect the folio split (Phase 3, 2026-07-12) + v4 consolidation
        # (Phase 3.5): 24 docs/site-authoring commands moved to `folio`, then the
        # claude-md trio (edit/init/sync) folded into the docs/claude-md skill,
        # leaving docs at 2 (changelog + update, release-plumbing only) and
        # site at 1 (deploy, un-deprecated). Further lowered as T3.5.2 kills the
        # remaining deprecated shims (plan:sprint/roadmap, orch:plan, code:coverage,
        # teaching-residue utils, discovery-usage demoted) — see docs/MIGRATION-v4.md.
        (f"Total commands: {stats['total']}", stats['total'] >= 45),
        (f"CODE category: {stats['categories'].get('code', 0)}", stats['categories'].get('code', 0) >= 12),
        (f"TEST category: {stats['categories'].get('test', 0)}", stats['categories'].get('test', 0) >= 0),
        (f"DOCS category: {stats['categories'].get('docs', 0)}", stats['categories'].get('docs', 0) >= 2),
        # git:worktree folded into a skill reference in the v4 consolidation
        # (Phase 3.5) — see docs/MIGRATION-v4.md — dropping the floor from 8 to 7.
        (f"GIT category: {stats['categories'].get('git', 0)}", stats['categories'].get('git', 0) >= 7),
        (f"SITE category: {stats['categories'].get('site', 0)}", stats['categories'].get('site', 0) >= 1),
        (f"All categories present", len(stats['categories']) >= 9)
    ]

    all_pass = True
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("🎉 All validation checks passed!")
        print()
        print("Hub integration is working correctly.")
        print("The /craft:hub command will display accurate, auto-detected counts.")
        return 0
    else:
        print("⚠️  Some validation checks failed.")
        return 1


def test_hub_display():
    """Test that hub can generate display with discovery data."""
    result = _check_hub_display()
    assert result == 0, f"Hub display validation failed (exit code: {result})"


if __name__ == "__main__":
    exit(_check_hub_display())
