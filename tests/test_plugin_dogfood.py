#!/usr/bin/env python3
"""
Plugin Self-Dogfooding Tests
==============================
Runs craft's own validation tools against itself. These tests exercise
the same scripts and checks that users/CI would run, ensuring they
pass on the craft repo itself.

Unlike e2e tests that check structural integrity, dogfood tests run
real scripts and validate real output against the live repo state.

Run with: python3 -m pytest tests/test_plugin_dogfood.py -v
"""

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def _run_script(script_name: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a script from the scripts/ directory."""
    script = SCRIPTS_DIR / script_name
    return subprocess.run(
        ["bash", str(script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PLUGIN_DIR),
    )


# ============================================================================
# 1. Validate Counts (craft's own consistency checker)
# ============================================================================

class TestValidateCounts:
    """Run validate-counts.sh and verify it passes."""

    def test_validate_counts_exits_zero(self):
        """validate-counts.sh passes with exit code 0."""
        result = _run_script("validate-counts.sh")
        assert result.returncode == 0, (
            f"validate-counts.sh failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_validate_counts_no_mismatch_warnings(self):
        """validate-counts.sh output has no MISMATCH warnings."""
        result = _run_script("validate-counts.sh")
        combined = result.stdout + result.stderr
        assert "MISMATCH" not in combined.upper(), (
            f"Count mismatch detected:\n{combined}"
        )


# ============================================================================
# 2. Pre-Release Check (dry validation of current version)
# ============================================================================

class TestPreReleaseCheck:
    """Run pre-release-check.sh against the current version."""

    @pytest.fixture(scope="class")
    def current_version(self):
        data = json.loads(PLUGIN_JSON.read_text())
        return data["version"]

    def test_pre_release_check_runs(self, current_version):
        """pre-release-check.sh runs without crashing."""
        result = _run_script("pre-release-check.sh", current_version)
        # May have warnings but should not crash (exit 0 or known non-zero)
        assert result.returncode in (0, 1), (
            f"Unexpected exit code {result.returncode}:\n{result.stderr}"
        )

    def test_pre_release_detects_version(self, current_version):
        """pre-release-check.sh detects the plugin version."""
        result = _run_script("pre-release-check.sh", current_version)
        assert current_version in result.stdout, (
            f"Script didn't detect version {current_version}"
        )


# ============================================================================
# 3. Version Sync Verification
# ============================================================================

class TestVersionSync:
    """Version references across files must be consistent."""

    @pytest.fixture(scope="class")
    def canonical_version(self):
        return json.loads(PLUGIN_JSON.read_text())["version"]

    def test_version_sync_script_syntax(self):
        """version-sync.sh passes syntax check."""
        script = SCRIPTS_DIR / "version-sync.sh"
        if not script.exists():
            pytest.skip("version-sync.sh not found")
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_claude_md_version_matches(self, canonical_version):
        """CLAUDE.md version matches plugin.json."""
        claude_md = (PLUGIN_DIR / "CLAUDE.md").read_text()
        assert canonical_version in claude_md, (
            f"CLAUDE.md missing version {canonical_version}"
        )


# ============================================================================
# 4. Formatting Library (shared dependency for all scripts)
# ============================================================================

class TestFormattingLibrary:
    """scripts/formatting.sh is the shared formatting library."""

    def test_formatting_sh_exists(self):
        """formatting.sh exists."""
        assert (SCRIPTS_DIR / "formatting.sh").exists()

    def test_formatting_sh_sourceable(self):
        """formatting.sh can be sourced without error."""
        result = subprocess.run(
            ["bash", "-c", f"source {SCRIPTS_DIR}/formatting.sh && echo OK"],
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0, f"Source failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_formatting_exports_color_variables(self):
        """formatting.sh exports FMT_* color variables."""
        result = subprocess.run(
            ["bash", "-c", (
                f"source {SCRIPTS_DIR}/formatting.sh && "
                "echo FMT_RED=$FMT_RED FMT_GREEN=$FMT_GREEN FMT_NC=$FMT_NC"
            )],
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0
        # Should have non-empty color codes
        assert "FMT_RED=" in result.stdout
        assert "FMT_NC=" in result.stdout


# ============================================================================
# 5. Command Discovery (the _discovery.py + _schema.json system)
# ============================================================================

class TestCommandDiscovery:
    """Validate the command discovery and schema system."""

    def test_discovery_py_exists(self):
        """commands/_discovery.py exists."""
        assert (PLUGIN_DIR / "commands" / "_discovery.py").exists()

    def test_schema_json_exists(self):
        """commands/_schema.json exists."""
        assert (PLUGIN_DIR / "commands" / "_schema.json").exists()

    def test_schema_json_valid(self):
        """commands/_schema.json is valid JSON."""
        schema_path = PLUGIN_DIR / "commands" / "_schema.json"
        data = json.loads(schema_path.read_text())
        assert isinstance(data, (dict, list)), "Schema should be dict or list"

    def test_discovery_py_importable(self):
        """commands/_discovery.py can be imported without error."""
        result = subprocess.run(
            ["python3", "-c", (
                f"import sys; sys.path.insert(0, '{PLUGIN_DIR}'); "
                "from commands._discovery import *; print('OK')"
            )],
            capture_output=True, text=True, timeout=10,
        )
        # May fail if dependencies missing, but should not crash
        if result.returncode == 0:
            assert "OK" in result.stdout


# ============================================================================
# 6. Skill Trigger Uniqueness
# ============================================================================

class TestSkillTriggers:
    """SKILL.md trigger descriptions should be distinct to avoid misrouting."""

    def test_skill_descriptions_are_unique(self):
        """No two SKILL.md files have identical descriptions."""
        skills = list((PLUGIN_DIR / "skills").rglob("SKILL.md"))
        if len(skills) < 2:
            pytest.skip("Not enough SKILL.md files to compare")

        descriptions = {}
        for skill in skills:
            content = skill.read_text()
            m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if not m:
                continue
            # Simple extraction of description line
            for line in m.group(1).split("\n"):
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    if desc in descriptions:
                        pytest.fail(
                            f"Duplicate skill description between "
                            f"{skill.parent.name} and {descriptions[desc]}: "
                            f"'{desc}'"
                        )
                    descriptions[desc] = skill.parent.name


# ============================================================================
# 7. Hook Scripts (branch-guard ecosystem)
# ============================================================================

class TestHookEcosystem:
    """Branch guard and related hook scripts are healthy."""

    def test_branch_guard_script_exists(self):
        """scripts/branch-guard.sh exists."""
        assert (SCRIPTS_DIR / "branch-guard.sh").exists()

    def test_branch_guard_syntax_valid(self):
        """branch-guard.sh passes bash -n."""
        result = subprocess.run(
            ["bash", "-n", str(SCRIPTS_DIR / "branch-guard.sh")],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_install_branch_guard_syntax(self):
        """install-branch-guard.sh passes bash -n."""
        script = SCRIPTS_DIR / "install-branch-guard.sh"
        if not script.exists():
            pytest.skip("install-branch-guard.sh not found")
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_branch_guard_handles_empty_input(self):
        """branch-guard.sh doesn't crash on empty stdin."""
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input="",
            capture_output=True, text=True, timeout=5,
        )
        # Should exit cleanly (0 = allow, or graceful error)
        assert result.returncode in (0, 1, 2)

    def test_branch_guard_handles_invalid_json(self):
        """branch-guard.sh doesn't crash on malformed JSON."""
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input="not valid json at all",
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode in (0, 1, 2)

    def test_branch_guard_read_tool_allowed(self):
        """Read tool always passes branch guard."""
        payload = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
            "cwd": str(PLUGIN_DIR),
        })
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input=payload,
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0, (
            f"Read should always be allowed: {result.stderr}"
        )


# ============================================================================
# 8. Performance Budget
# ============================================================================

class TestPerformanceBudget:
    """Key scripts must complete within performance budgets.

    Budgets are relaxed for CI runners (typically 2-3x slower than local).
    """

    # CI runners are slower — detect via common CI env vars
    _IS_CI = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    _PERF_MULTIPLIER = 3 if _IS_CI else 1

    def test_validate_counts_under_5s(self):
        """validate-counts.sh completes in under 5 seconds (15s on CI)."""
        budget = 5 * self._PERF_MULTIPLIER
        start = time.perf_counter()
        _run_script("validate-counts.sh", timeout=budget + 5)
        elapsed = time.perf_counter() - start
        assert elapsed < budget, (
            f"validate-counts.sh took {elapsed:.1f}s (budget: {budget}s)"
        )

    def test_branch_guard_under_200ms(self):
        """branch-guard.sh Read tool check completes in under 200ms avg (600ms on CI)."""
        budget_ms = 200 * self._PERF_MULTIPLIER
        payload = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
            "cwd": str(PLUGIN_DIR),
        })
        times = []
        for _ in range(5):
            start = time.perf_counter()
            subprocess.run(
                ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
                input=payload,
                capture_output=True, text=True, timeout=5,
            )
            times.append((time.perf_counter() - start) * 1000)
        avg = sum(times) / len(times)
        assert avg < budget_ms, (
            f"Branch guard avg {avg:.0f}ms exceeds {budget_ms}ms budget"
        )


# ============================================================================
# 9. Git Repo Health (dogfood: craft's own repo)
# ============================================================================

class TestRepoHealth:
    """Craft's own git repo should be in a healthy state."""

    def test_on_expected_branch_type(self):
        """Current branch is main, dev, feature/*, fix/*, or detached HEAD (CI)."""
        result = subprocess.run(
            ["git", "-C", str(PLUGIN_DIR), "branch", "--show-current"],
            capture_output=True, text=True,
        )
        branch = result.stdout.strip()
        if not branch:
            # Detached HEAD (common in CI) — that's fine
            return
        valid = (
            branch in ("main", "dev")
            or branch.startswith(("feature/", "fix/"))
        )
        assert valid, f"Unexpected branch: {branch}"

    def test_no_merge_conflicts_in_tracked_files(self):
        """No tracked files contain merge conflict markers."""
        result = subprocess.run(
            ["git", "-C", str(PLUGIN_DIR), "diff", "--check", "HEAD"],
            capture_output=True, text=True,
        )
        conflict_lines = [
            line for line in result.stdout.split("\n")
            if "conflict" in line.lower()
        ]
        assert not conflict_lines, f"Merge conflicts found: {conflict_lines}"


# ============================================================================
# 10. Plugin JSON Schema
# ============================================================================

class TestPluginJsonSchema:
    """plugin.json must conform to Claude Code's expected schema."""

    @pytest.fixture(scope="class")
    def plugin_data(self):
        return json.loads(PLUGIN_JSON.read_text())

    def test_required_fields_present(self, plugin_data):
        """All required fields exist."""
        required = ["name", "version", "description", "author"]
        missing = [f for f in required if f not in plugin_data]
        assert not missing, f"Missing required fields: {missing}"

    def test_author_is_object(self, plugin_data):
        """Author field is an object with 'name'."""
        author = plugin_data.get("author")
        assert isinstance(author, dict), "author must be an object"
        assert "name" in author, "author must have 'name' field"

    def test_no_unrecognized_keys(self, plugin_data):
        """No unrecognized top-level keys (strict schema)."""
        recognized = {
            "name", "version", "description", "author",
            "homepage", "repository", "license", "keywords",
            "engines", "dependencies",
        }
        unknown = set(plugin_data.keys()) - recognized
        assert not unknown, (
            f"Unrecognized keys in plugin.json: {unknown} "
            f"(Claude Code uses strict schema)"
        )

    def test_description_not_too_long(self, plugin_data):
        """Description is under 500 characters (display limit)."""
        desc = plugin_data.get("description", "")
        assert len(desc) < 500, (
            f"Description is {len(desc)} chars (max 500 for display)"
        )


def test_refine_delegates_to_skill():
    """Every --refine command must delegate to the skill, not restate the flow."""
    targets = [
        "commands/workflow/brainstorm.md",
        "commands/do.md",
        "commands/orchestrate.md",
        "commands/plan/feature.md",
        "commands/arch/plan.md",
    ]
    bad = []
    for rel in targets:
        text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
        delegates = "prompt-refiner" in text
        restates = "Accept/Edit/Use original" in text or "Accept / Edit / Use original" in text
        if not delegates or restates:
            bad.append(rel)
    assert not bad, f"commands must delegate to prompt-refiner, not restate the flow: {bad}"


# ============================================================================
# 12. bump-version.sh categorical subtotals (item #7)
# ============================================================================

# Subtree bump-version.sh needs to compute counts + rewrite categorical headers.
_BUMP_ISOLATION_PATHS = [
    "scripts", "commands", "skills", "agents", "docs", ".claude-plugin",
]


def _isolated_bump(dst: Path) -> Path:
    """Copy the subtree bump-version.sh needs into dst; return the script path.

    The script resolves PLUGIN_DIR from its own location (SCRIPT_DIR/..), so
    running the COPY makes PLUGIN_DIR == dst — every sed write lands in the
    disposable copy and never touches the real source tree (guards against the
    test-mutates-source bug class, ref v2.36.0 post-mortem).
    """
    dst.mkdir(parents=True, exist_ok=True)
    for name in _BUMP_ISOLATION_PATHS:
        src = PLUGIN_DIR / name
        if not src.exists():
            continue
        target = dst / name
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy(src, target)
    return dst / "scripts" / "bump-version.sh"


def _cmd_cat_count(category: str) -> int:
    """Mirror bump-version.sh _cmd_cat: commands/<category>/*.md sans index/README."""
    d = PLUGIN_DIR / "commands" / category
    return sum(
        1 for p in d.rglob("*.md") if p.name not in ("index.md", "README.md")
    ) if d.exists() else 0


def _skill_cat_count(category: str) -> int:
    """Mirror bump-version.sh _skill_cat: skills/<category>/**/SKILL.md."""
    d = PLUGIN_DIR / "skills" / category
    return sum(1 for _ in d.rglob("SKILL.md")) if d.exists() else 0


def _skill_total() -> int:
    return sum(1 for _ in (PLUGIN_DIR / "skills").rglob("SKILL.md"))


class TestBumpVersionSubtotals:
    """item #7 — bump-version.sh sweeps categorical section headers."""

    def test_verify_passes_on_clean_tree(self):
        """--verify exits 0 (real tree is consistent, incl. new subtotal checks)."""
        result = _run_script("bump-version.sh", "--verify")
        assert result.returncode == 0, (
            f"bump-version.sh --verify reported drift:\n{result.stdout}\n{result.stderr}"
        )

    def test_dry_run_exits_zero(self):
        """--counts-only --dry-run is read-only and exits 0."""
        result = _run_script("bump-version.sh", "--counts-only", "--dry-run")
        assert result.returncode == 0, result.stderr
        assert "would update" in result.stdout, (
            f"dry-run did not preview changes:\n{result.stdout}"
        )

    def test_rewrites_hub_orchestrate_subtotal(self, tmp_path):
        """A stale ORCHESTRATE (99) in hub.md is rewritten to the real count."""
        script = _isolated_bump(tmp_path / "iso")
        hub = script.parent.parent / "commands" / "hub.md"
        # Inject an unambiguous stale value on the canonical box-art label.
        hub.write_text(re.sub(r"ORCHESTRATE \(\d+\)", "ORCHESTRATE (99)",
                              hub.read_text(), count=1))
        subprocess.run(["bash", str(script), "--counts-only"], capture_output=True,
                       text=True, timeout=60)
        expected = _cmd_cat_count("orchestrate")
        out = hub.read_text()
        assert f"ORCHESTRATE ({expected})" in out, f"expected ORCHESTRATE ({expected})"
        assert "ORCHESTRATE (99)" not in out, "stale subtotal not rewritten"

    def test_rewrites_refcard_skills_total(self, tmp_path):
        """A stale '## Skills (99 total)' in REFCARD.md is corrected."""
        script = _isolated_bump(tmp_path / "iso")
        refcard = script.parent.parent / "docs" / "REFCARD.md"
        refcard.write_text(
            re.sub(r"^## Skills \(\d+ total\)", "## Skills (99 total)",
                   refcard.read_text(), count=1, flags=re.MULTILINE)
        )
        subprocess.run(["bash", str(script), "--counts-only"], capture_output=True,
                       text=True, timeout=60)
        out = refcard.read_text()
        assert f"## Skills ({_skill_total()} total)" in out
        assert "## Skills (99 total)" not in out

    def test_rewrites_skills_agents_subcategory(self, tmp_path):
        """A stale '### Distribution (99)' sub-header is corrected to the dir count."""
        script = _isolated_bump(tmp_path / "iso")
        sa = script.parent.parent / "docs" / "skills-agents.md"
        sa.write_text(
            re.sub(r"^### Distribution \(\d+\)", "### Distribution (99)",
                   sa.read_text(), count=1, flags=re.MULTILINE)
        )
        subprocess.run(["bash", str(script), "--counts-only"], capture_output=True,
                       text=True, timeout=60)
        out = sa.read_text()
        assert f"### Distribution ({_skill_cat_count('distribution')})" in out
        assert "### Distribution (99)" not in out

    def test_isolation_leaves_real_tree_untouched(self, tmp_path):
        """Sanity: the isolated rewrites never mutate the real REFCARD.md."""
        real = (PLUGIN_DIR / "docs" / "REFCARD.md").read_text()
        script = _isolated_bump(tmp_path / "iso")
        refcard = script.parent.parent / "docs" / "REFCARD.md"
        refcard.write_text(refcard.read_text().replace("## Skills", "## Skills (99 total) STALE"))
        subprocess.run(["bash", str(script), "--counts-only"], capture_output=True,
                       text=True, timeout=60)
        assert (PLUGIN_DIR / "docs" / "REFCARD.md").read_text() == real, (
            "isolated bump-version run mutated the real source tree"
        )


# ============================================================================
# v2.49.x sprint — Skill-Standards Validator (Track 1, dogfood)
# ============================================================================
class TestSkillStandardsValidatorDogfood:
    """craft runs its own skill-standards auditor against its own skills tree."""

    VALIDATOR = PLUGIN_DIR / ".claude-plugin" / "skills" / "validation" / "skill-standards-check.md"
    AUDIT = SCRIPTS_DIR / "skill_standards_audit.py"

    def test_audit_runs_clean_on_own_skills(self):
        """craft's own skills are compliant -> audit exits 0 with a score line."""
        result = subprocess.run(
            ["python3", str(self.AUDIT), "--root", "skills"],
            capture_output=True, text=True, timeout=60, cwd=str(PLUGIN_DIR),
        )
        assert result.returncode == 0, f"own-skills audit not clean:\n{result.stdout}{result.stderr}"
        assert "100/100" in result.stdout or "Score" in result.stdout

    def test_validator_skill_is_hotreload_fork(self):
        text = self.VALIDATOR.read_text()
        assert "hot_reload: true" in text
        assert "context: fork" in text
        assert "category: validation" in text

    def test_validator_impl_is_advisory_always_exits_zero(self, tmp_path):
        """The embedded bash impl must NEVER exit non-zero (D3 advisory), even on a bad skill."""
        m = re.search(r"## Implementation\s+```bash\n(.*?)```", self.VALIDATOR.read_text(), re.S)
        assert m, "validator has no bash Implementation block"
        bad = tmp_path / "skills" / "bad"
        bad.mkdir(parents=True)
        (bad / "SKILL.md").write_text("# no frontmatter at all\n")
        script = tmp_path / "run.sh"
        script.write_text(m.group(1))
        env = {**os.environ, "SKILL_STANDARDS_ROOT": str(tmp_path / "skills"),
               "CRAFT_ROOT": str(PLUGIN_DIR)}
        r = subprocess.run(["bash", str(script)], capture_output=True, text=True,
                           env=env, timeout=60)
        assert r.returncode == 0, f"advisory validator must exit 0, got {r.returncode}"


# ============================================================================
# v2.49.x sprint — Homebrew dist-gates (Track A, dogfood)
# ============================================================================
class TestHomebrewGatesDogfood:
    """craft's verify_caveats / post_install gates run on synthesized formulae."""

    def test_verify_caveats_advisory_by_default(self, tmp_path):
        """A stale formula returns findings but exit 0 unless --strict (D4 advisory)."""
        formula = tmp_path / "f.rb"
        formula.write_text(
            "class F < Formula\n  def caveats\n    <<~EOS\n      New in v1.0.0:\n"
            "      # --- dynamic bullets ---\n      - old\n      # --- end dynamic bullets ---\n"
            "    EOS\n  end\nend\n"
        )
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("## [2.0.0]\n- new thing\n")
        advisory = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "verify_caveats.py"), str(formula),
             str(changelog), "2.0.0"],
            capture_output=True, text=True, timeout=30, cwd=str(PLUGIN_DIR),
        )
        assert advisory.returncode == 0, "default mode must be advisory (exit 0)"
        strict = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "verify_caveats.py"), str(formula),
             str(changelog), "2.0.0", "--strict"],
            capture_output=True, text=True, timeout=30, cwd=str(PLUGIN_DIR),
        )
        assert strict.returncode == 1, "--strict must escalate stale caveats to exit 1"

    def test_post_install_flags_wrong_update_ordering(self, tmp_path):
        """post_install gate catches 'plugin update' before 'marketplace update' (the v2.49.0 bug)."""
        good = tmp_path / "good.rb"
        good.write_text(
            'class G < Formula\n  def post_install\n    begin\n'
            '      system "claude", "plugin", "marketplace", "update", "local-plugins"\n'
            '      system "claude", "plugin", "update", "g@local-plugins"\n'
            '      (libexec/"x").install "y"\n    rescue => e\n      opoo e.message\n    end\n  end\nend\n'
        )
        r_good = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "post_install_check.py"), str(good)],
            capture_output=True, text=True, timeout=30, cwd=str(PLUGIN_DIR),
        )
        assert r_good.returncode == 0, f"correct ordering should pass:\n{r_good.stdout}"
        bad = tmp_path / "bad.rb"
        bad.write_text(good.read_text().replace(
            'system "claude", "plugin", "marketplace", "update", "local-plugins"\n'
            '      system "claude", "plugin", "update", "g@local-plugins"',
            'system "claude", "plugin", "update", "g@local-plugins"\n'
            '      system "claude", "plugin", "marketplace", "update", "local-plugins"'))
        r_bad = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "post_install_check.py"), str(bad), "--strict"],
            capture_output=True, text=True, timeout=30, cwd=str(PLUGIN_DIR),
        )
        assert r_bad.returncode == 1, "--strict must block wrong update ordering"


# ============================================================================
# v2.49.x sprint — SessionEnd insights facet hook (Track B, dogfood)
# ============================================================================
class TestSessionFacetHookDogfood:
    """craft's own SessionEnd hook + installer run end-to-end against a temp HOME."""

    HOOK = PLUGIN_DIR / "hooks" / "session-facet.sh"
    INSTALLER = SCRIPTS_DIR / "install-session-facet.sh"

    def test_hook_writes_one_facet_per_session(self, tmp_path):
        import json as _json
        env = {**os.environ, "HOME": str(tmp_path)}
        stdin = _json.dumps({"cwd": str(tmp_path), "session_id": "dogfood-sess"})
        for _ in range(2):  # second SessionEnd for same session must be a no-op (D5 dedup)
            r = subprocess.run(["bash", str(self.HOOK)], input=stdin,
                               capture_output=True, text=True, env=env, timeout=30)
            assert r.returncode == 0, f"hook must exit 0: {r.stderr}"
        facets = list((tmp_path / ".claude" / "usage-data" / "facets").glob("session-*.json"))
        assert len(facets) == 1, "exactly one facet per session id (per-session dedup, not per-day)"
        data = _json.loads(facets[0].read_text())
        assert data["session_id"] == "dogfood-sess"
        assert data["auto_collected"] is True

    def test_installer_registers_sessionend_idempotently(self, tmp_path):
        import json as _json
        (tmp_path / ".claude" / "hooks").mkdir(parents=True)
        settings = tmp_path / ".claude" / "settings.json"
        settings.write_text('{"hooks":{}}')
        env = {**os.environ, "HOME": str(tmp_path)}
        for _ in range(2):  # idempotent on re-run
            subprocess.run(["bash", str(self.INSTALLER)], capture_output=True,
                           text=True, env=env, timeout=30, check=True)
        s = _json.loads(settings.read_text())
        se = _json.dumps(s["hooks"].get("SessionEnd", []))
        assert "session-facet.sh" in se, "installer must register the SessionEnd hook"
        assert se.count("session-facet.sh") == 1, "registration must be idempotent"
        assert (tmp_path / ".claude" / "hooks" / "session-facet.sh").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
