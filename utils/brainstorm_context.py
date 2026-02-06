#!/usr/bin/env python3
"""
Brainstorm Context Scanner — Context-aware smart questions for /workflow:brainstorm.

Scans project state (.STATUS, specs, git log, CLAUDE.md) to pre-fill answers,
skip redundant questions, and add project-type-specific questions.

Version: 1.0.0 (v2.15.0)
Author: Craft Plugin
"""

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any


@dataclass
class ContextScanResult:
    """Result of scanning project context for brainstorm pre-filling."""
    pre_filled_answers: Dict[str, str] = field(default_factory=dict)
    matching_spec: Optional[str] = None
    prior_brainstorm: Optional[str] = None
    project_type: Optional[str] = None
    project_version: Optional[str] = None
    dynamic_questions: List[Dict[str, Any]] = field(default_factory=list)
    status_info: Dict[str, str] = field(default_factory=dict)
    has_failing_tests: bool = False


# Project-type question extensions (2 per type)
PROJECT_TYPE_QUESTIONS = {
    "r-package": [
        {
            "question": "Is CRAN submission planned for this feature?",
            "options": [
                "Yes, targeting CRAN",
                "No, internal/GitHub only",
                "Eventually, not this iteration",
                "Unsure",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
        {
            "question": "Are there R package dependencies to consider?",
            "options": [
                "Tidyverse packages",
                "Base R only",
                "System libraries needed",
                "No new dependencies",
            ],
            "multiSelect": True,
            "category": "project-type",
        },
    ],
    "generic-python": [
        {
            "question": "Is PyPI distribution needed?",
            "options": [
                "Yes, publish to PyPI",
                "No, internal only",
                "GitHub releases only",
                "Unsure",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
        {
            "question": "Are there Python version constraints?",
            "options": [
                "Python 3.9+ minimum",
                "Python 3.11+ (latest features)",
                "Must support 3.8+",
                "No constraints",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
    ],
    "generic-node": [
        {
            "question": "What's the npm publish target?",
            "options": [
                "Public npm registry",
                "Private registry",
                "No npm publish needed",
                "GitHub packages",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
        {
            "question": "Are bundle size concerns relevant?",
            "options": [
                "Yes, client-side bundle",
                "No, server-side only",
                "Moderate concern",
                "Not applicable",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
    ],
    "teaching-site": [
        {
            "question": "Is this student-facing content?",
            "options": [
                "Yes, students will see it",
                "No, instructor-only",
                "Both student and instructor",
                "Administrative tool",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
        {
            "question": "Does this integrate with assessment?",
            "options": [
                "Graded assignment",
                "Practice exercise",
                "No assessment link",
                "Rubric component",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
    ],
    "craft-plugin": [
        {
            "question": "How does this impact command count?",
            "options": [
                "Adds new commands",
                "Modifies existing commands",
                "No command changes",
                "Deprecates commands",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
        {
            "question": "Are there backward compatibility concerns?",
            "options": [
                "Must maintain existing syntax",
                "Breaking changes acceptable",
                "Deprecation period needed",
                "No compatibility issues",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
    ],
    "mcp-server": [
        {
            "question": "What MCP capabilities are affected?",
            "options": [
                "Tools (new or modified)",
                "Resources",
                "Prompts",
                "No MCP changes",
            ],
            "multiSelect": True,
            "category": "project-type",
        },
        {
            "question": "Are there client compatibility concerns?",
            "options": [
                "Must work with Claude Desktop",
                "Claude Code only",
                "Multiple MCP clients",
                "No compatibility issues",
            ],
            "multiSelect": False,
            "category": "project-type",
        },
    ],
}


class BrainstormContext:
    """Scans project context for smart question pre-filling."""

    def __init__(self, project_path: Optional[Path] = None):
        self.path = Path(project_path) if project_path else Path.cwd()

    def scan(self, topic: str) -> ContextScanResult:
        """Run full context scan for a brainstorm topic.

        Args:
            topic: The brainstorm topic string

        Returns:
            ContextScanResult with pre-filled answers and dynamic questions
        """
        result = ContextScanResult()

        # 1. Read .STATUS
        result.status_info = self._read_status()
        if result.status_info.get("version"):
            result.project_version = result.status_info["version"]
            result.pre_filled_answers["technical"] = (
                f"Current version: v{result.project_version}"
            )

        # 2. Find matching specs
        result.matching_spec = self._find_matching_spec(topic)

        # 3. Find prior brainstorms
        result.prior_brainstorm = self._find_prior_brainstorm(topic)

        # 4. Detect project type
        result.project_type = self._detect_project_type()

        # 5. Check for failing tests
        result.has_failing_tests = self._check_failing_tests()

        # 6. Build dynamic questions
        result.dynamic_questions = self._build_dynamic_questions(result)

        return result

    def _read_status(self) -> Dict[str, str]:
        """Read .STATUS file and extract key fields."""
        status_file = self.path / ".STATUS"
        if not status_file.exists():
            return {}

        try:
            content = status_file.read_text()
        except OSError:
            return {}

        info = {}
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("version:"):
                info["version"] = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                info["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("milestone:"):
                info["milestone"] = line.split(":", 1)[1].strip()
            elif line.startswith("progress:"):
                info["progress"] = line.split(":", 1)[1].strip()

        return info

    def _find_matching_spec(self, topic: str) -> Optional[str]:
        """Find a spec file that matches the brainstorm topic.

        Uses keyword matching against spec filenames and first 50 lines.
        """
        specs_dir = self.path / "docs" / "specs"
        if not specs_dir.exists():
            return None

        # Normalize topic to keywords
        keywords = self._extract_keywords(topic)
        if not keywords:
            return None

        best_match = None
        best_score = 0

        for spec_file in specs_dir.glob("SPEC-*.md"):
            score = 0
            name_lower = spec_file.stem.lower()

            # Check filename
            for kw in keywords:
                if kw in name_lower:
                    score += 2

            # Check first 50 lines of content
            if score > 0 or len(keywords) <= 2:
                try:
                    lines = spec_file.read_text().split("\n")[:50]
                    content_lower = "\n".join(lines).lower()
                    for kw in keywords:
                        if kw in content_lower:
                            score += 1
                except OSError:
                    pass

            if score > best_score:
                best_score = score
                best_match = str(spec_file.relative_to(self.path))

        # Require minimum relevance
        if best_score >= 2:
            return best_match
        return None

    def _find_prior_brainstorm(self, topic: str) -> Optional[str]:
        """Find a prior brainstorm file matching the topic."""
        keywords = self._extract_keywords(topic)
        if not keywords:
            return None

        # Search in project root and docs/brainstorm/
        search_dirs = [self.path, self.path / "docs" / "brainstorm"]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for brainstorm_file in search_dir.glob("BRAINSTORM-*.md"):
                name_lower = brainstorm_file.stem.lower()
                if any(kw in name_lower for kw in keywords):
                    return str(brainstorm_file.relative_to(self.path))

        return None

    def _detect_project_type(self) -> Optional[str]:
        """Detect project type using CLAUDEMDDetector if available, else simple checks."""
        try:
            from utils.claude_md_detector import detect_project
            info = detect_project(self.path)
            if info:
                return info.type
        except ImportError:
            pass

        # Fallback: simple file-based detection
        if (self.path / ".claude-plugin" / "plugin.json").exists():
            return "craft-plugin"
        if (self.path / "DESCRIPTION").exists():
            desc = (self.path / "DESCRIPTION").read_text(errors="ignore")
            if "Package:" in desc:
                return "r-package"
        if (self.path / "_quarto.yml").exists():
            if (self.path / "course.yml").exists() or (self.path / "weeks").exists():
                return "teaching-site"
        if (self.path / "pyproject.toml").exists():
            return "generic-python"
        if (self.path / "package.json").exists():
            return "generic-node"

        return None

    def _check_failing_tests(self) -> bool:
        """Check git log for recent test failure indicators."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5", "--format=%s"],
                capture_output=True, text=True, timeout=5,
                cwd=str(self.path)
            )
            if result.returncode != 0:
                return False

            messages = result.stdout.lower()
            failure_indicators = ["fix test", "failing test", "test fix", "broken test"]
            return any(indicator in messages for indicator in failure_indicators)
        except (subprocess.SubprocessError, OSError):
            return False

    def _build_dynamic_questions(self, result: ContextScanResult) -> List[Dict[str, Any]]:
        """Build dynamic questions based on scan results."""
        questions = []

        if result.matching_spec:
            questions.append({
                "question": f"Found {result.matching_spec} — load as context?",
                "options": [
                    "Yes, use spec as context",
                    "No, start fresh",
                    "View spec first",
                ],
                "multiSelect": False,
                "category": "dynamic",
                "type": "matching_spec",
            })

        if result.prior_brainstorm:
            questions.append({
                "question": f"Found prior brainstorm ({result.prior_brainstorm}) — resume or start fresh?",
                "options": [
                    "Resume from prior brainstorm",
                    "Start fresh",
                    "View prior brainstorm first",
                ],
                "multiSelect": False,
                "category": "dynamic",
                "type": "prior_brainstorm",
            })

        if result.has_failing_tests:
            questions.append({
                "question": "Recent commits suggest test failures — address testing first?",
                "options": [
                    "Yes, address tests first",
                    "No, continue with brainstorm",
                    "Include test fixes in scope",
                ],
                "multiSelect": False,
                "category": "dynamic",
                "type": "failing_tests",
            })

        return questions

    def get_project_type_questions(self, project_type: str) -> List[Dict[str, Any]]:
        """Get project-type-specific questions.

        Args:
            project_type: Detected project type string

        Returns:
            List of question dicts for this project type
        """
        return PROJECT_TYPE_QUESTIONS.get(project_type, [])

    def select_smart_questions(
        self,
        base_questions: List[Dict[str, Any]],
        context: ContextScanResult,
        count: int,
    ) -> List[Dict[str, Any]]:
        """Select and order questions based on context.

        Args:
            base_questions: Standard question bank questions (filtered by categories)
            context: Result from scan()
            count: Maximum number of questions to return

        Returns:
            Ordered list of questions with dynamic + project-type + base
        """
        questions = []

        # 1. Dynamic questions first (highest priority)
        questions.extend(context.dynamic_questions)

        # 2. Project-type questions
        if context.project_type:
            pt_questions = self.get_project_type_questions(context.project_type)
            questions.extend(pt_questions)

        # 3. Base questions (mark pre-filled ones as skippable)
        for q in base_questions:
            q_copy = dict(q)
            # Check if we have a pre-filled answer for this question's category
            q_cat = q_copy.get("category", "")
            if q_cat in context.pre_filled_answers:
                q_copy["pre_filled"] = context.pre_filled_answers[q_cat]
                q_copy["skippable"] = True
            questions.append(q_copy)

        # 4. Trim to requested count
        return questions[:count]

    @staticmethod
    def _extract_keywords(topic: str) -> List[str]:
        """Extract searchable keywords from a topic string.

        Normalizes to lowercase, removes common words, splits on spaces/hyphens.
        """
        if not topic:
            return []

        # Normalize
        topic_lower = topic.lower().strip()

        # Split on spaces, hyphens, underscores
        words = re.split(r"[\s\-_]+", topic_lower)

        # Remove common stop words
        stop_words = {
            "a", "an", "the", "is", "for", "to", "in", "on", "of", "and",
            "or", "with", "my", "our", "this", "that", "new", "add", "create",
            "implement", "build", "make", "update", "fix",
        }

        keywords = [w for w in words if w and w not in stop_words and len(w) > 1]
        return keywords


def scan_context(topic: str, project_path: Optional[Path] = None) -> ContextScanResult:
    """Convenience function to scan brainstorm context.

    Args:
        topic: Brainstorm topic
        project_path: Project directory (default: cwd)

    Returns:
        ContextScanResult
    """
    ctx = BrainstormContext(project_path)
    return ctx.scan(topic)


if __name__ == "__main__":
    import sys

    topic_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "test topic"
    result = scan_context(topic_arg)

    print(f"Topic: {topic_arg}")
    print(f"Project type: {result.project_type}")
    print(f"Project version: {result.project_version}")
    print(f"Matching spec: {result.matching_spec}")
    print(f"Prior brainstorm: {result.prior_brainstorm}")
    print(f"Failing tests: {result.has_failing_tests}")
    print(f"Pre-filled answers: {result.pre_filled_answers}")
    print(f"Dynamic questions: {len(result.dynamic_questions)}")
    print(f"Status info: {result.status_info}")
