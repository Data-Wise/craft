#!/usr/bin/env python3
"""
Test agent hooks in .claude-plugin/hooks/.

Tests the orchestration lifecycle hooks structure and syntax:
- Script exists and is executable
- Valid bash syntax
- Contains required event handlers
- Has correct mode-aware logic
- Creates expected directories and files

Note: Full integration testing of hook execution is done in E2E tests.
Unit tests here verify structure, syntax, and static analysis.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAgentHooks:
    """Tests for orchestration agent hooks."""

    def get_hook_script(self):
        """Get path to hook script."""
        plugin_dir = Path(__file__).parent.parent
        return plugin_dir / ".claude-plugin" / "hooks" / "orchestrate-hooks.sh"

    def get_hook_content(self):
        """Get hook script content."""
        return self.get_hook_script().read_text()

    def test_hook_script_exists(self):
        """Hook script should exist and be executable."""
        hook_script = self.get_hook_script()

        assert hook_script.exists(), \
            f"Hook script not found: {hook_script}"

        assert os.access(hook_script, os.X_OK), \
            f"Hook script not executable: {hook_script}"

    def test_hook_syntax_valid(self):
        """Hook script should have valid bash syntax."""
        hook_script = self.get_hook_script()

        result = subprocess.run(
            ["bash", "-n", str(hook_script)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, \
            f"Bash syntax check failed:\n{result.stderr}"

    def test_hook_has_shebang(self):
        """Hook script should have proper shebang."""
        content = self.get_hook_content()
        lines = content.split('\n')

        assert lines[0].startswith('#!/bin/bash'), \
            f"Expected shebang '#!/bin/bash', got: {lines[0]}"

    def test_hook_handles_pretooluse_event(self):
        """Hook should have PreToolUse event handler."""
        content = self.get_hook_content()

        assert 'PreToolUse)' in content, \
            "Hook should have PreToolUse case handler"

        # Should check resource limits
        assert 'ACTIVE_AGENTS' in content, \
            "PreToolUse handler should check active agents"

        assert 'MAX_AGENTS' in content, \
            "PreToolUse handler should have max agents limit"

        # Should log agent start
        assert 'Starting agent' in content or '🚀' in content, \
            "PreToolUse handler should log agent start"

    def test_hook_handles_posttooluse_event(self):
        """Hook should have PostToolUse event handler."""
        content = self.get_hook_content()

        assert 'PostToolUse)' in content, \
            "Hook should have PostToolUse case handler"

        # Should handle duration
        assert 'DURATION' in content, \
            "PostToolUse handler should handle DURATION"

        # Should log completion
        assert 'Completed agent' in content or '✅' in content, \
            "PostToolUse handler should log completion"

        # Should update cache
        assert '.status' in content, \
            "PostToolUse handler should update status cache"

    def test_hook_handles_stop_event(self):
        """Hook should have Stop event handler."""
        content = self.get_hook_content()

        assert 'Stop)' in content, \
            "Hook should have Stop case handler"

        # Should save session state
        assert 'last-orchestration.json' in content or 'SESSION_FILE' in content, \
            "Stop handler should save session file"

        # Should handle agent count
        assert 'AGENT_COUNT' in content, \
            "Stop handler should handle AGENT_COUNT"

    def test_hook_mode_aware_limits(self):
        """Hook should have mode-specific resource limits."""
        content = self.get_hook_content()

        # Should have mode detection
        assert 'CRAFT_MODE' in content, \
            "Hook should check CRAFT_MODE environment variable"

        # Should have different limits for different modes
        modes = {
            'debug': '1',
            'default': '2',
            'optimize': '4',
            'release': '4'
        }

        for mode, limit in modes.items():
            assert mode in content, \
                f"Hook should handle '{mode}' mode"

            # Check that MAX_AGENTS is set to the correct limit for this mode
            # We look for patterns like "debug)\n    MAX_AGENTS=1"
            mode_section = content[content.find(f'{mode})'):]
            if 'MAX_AGENTS' in mode_section[:200]:  # Check next ~200 chars
                assert f'MAX_AGENTS={limit}' in mode_section[:200], \
                    f"Mode '{mode}' should set MAX_AGENTS={limit}"

    def test_hook_creates_directories(self):
        """Hook should create necessary directories."""
        content = self.get_hook_content()

        # Should create .craft/logs and .craft/cache
        assert 'mkdir -p' in content, \
            "Hook should create directories"

        assert '.craft/logs' in content, \
            "Hook should create .craft/logs directory"

        assert '.craft/cache' in content or 'CACHE_DIR' in content, \
            "Hook should create .craft/cache directory"

    def test_hook_uses_logging(self):
        """Hook should have logging functionality."""
        content = self.get_hook_content()

        # Should have log file
        assert 'LOG_FILE' in content, \
            "Hook should define LOG_FILE variable"

        assert 'orchestration.log' in content, \
            "Hook should use orchestration.log file"

        # Should have log function or logging statements
        assert 'log()' in content or 'echo' in content, \
            "Hook should have logging capability"

        # Should include timestamps
        assert 'timestamp' in content or 'date' in content, \
            "Hook should include timestamps in logs"

    def test_hook_handles_errors_gracefully(self):
        """Hook should handle errors gracefully."""
        content = self.get_hook_content()

        # Should use set -e for error handling
        assert 'set -e' in content, \
            "Hook should use 'set -e' for error handling"

        # Should not use set -u (which causes issues with optional vars)
        assert 'set -euo pipefail' not in content, \
            "Hook should not use 'set -u' (breaks with optional env vars)"

        # Should handle unknown events
        assert '*)' in content, \
            "Hook should have default case for unknown events"

    def test_hook_uses_status_cache(self):
        """Hook should create and update agent status cache."""
        content = self.get_hook_content()

        # Should create status files
        assert 'agent-' in content and '.status' in content, \
            "Hook should create agent status files"

        # Should update status on completion
        assert 'completed' in content or 'success' in content, \
            "Hook should mark agents as completed"

    def test_hook_saves_session_state(self):
        """Hook should save session state on stop."""
        content = self.get_hook_content()

        # Should create JSON session file
        assert '.json' in content, \
            "Hook should create JSON session file"

        # Should collect agent data
        assert 'agents' in content, \
            "Hook should collect agent data in session"

        # Should include timestamp
        assert 'timestamp' in content, \
            "Hook should include timestamp in session"

    def test_hook_archives_old_logs(self):
        """Hook should archive old logs to prevent bloat."""
        content = self.get_hook_content()

        # Should have log retention logic
        # (Looking for archive, cleanup, or keeping last N logs)
        assert 'LOG_COUNT' in content or 'tail -n' in content or '10' in content, \
            "Hook should have log archival logic to prevent bloat"


def run_tests():
    """Run all tests and report results."""
    import time

    test_class = TestAgentHooks()
    test_methods = [
        method for method in dir(test_class)
        if method.startswith('test_')
    ]

    print("=" * 80)
    print("Agent Hooks Unit Tests")
    print("=" * 80)

    passed = 0
    failed = 0
    total_time = 0

    for method_name in test_methods:
        method = getattr(test_class, method_name)
        test_name = method_name.replace('test_', '').replace('_', ' ').title()

        try:
            start = time.time()
            method()
            duration = (time.time() - start) * 1000
            total_time += duration

            print(f"✓ {test_name:60} ({duration:.1f}ms)")
            passed += 1

        except AssertionError as e:
            print(f"✗ {test_name:60} FAILED")
            print(f"  {str(e)}")
            failed += 1

        except Exception as e:
            print(f"✗ {test_name:60} ERROR")
            print(f"  {type(e).__name__}: {str(e)}")
            failed += 1

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed ({total_time:.1f}ms total)")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
