#!/usr/bin/env python3
"""Demo script for teaching content validation.

Shows validation output for different course scenarios:
1. Complete valid course
2. Course with missing syllabus sections
3. Course with incomplete schedule
4. Course with missing assignments
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teaching_validation import validate_teaching_content


def create_demo_course(scenario: str) -> Path:
    """Create a temporary course directory for demo."""
    course_dir = Path(tempfile.mkdtemp())

    if scenario == "complete":
        # Complete valid course
        (course_dir / 'syllabus.qmd').write_text("""
# Course Syllabus

## Learning Objectives
Students will master statistical methods and apply them to real-world problems.

## Course Policies
Attendance is required. Late work accepted with 24-hour notice.

## Grading
- Homework: 40%
- Exams: 60%

## Schedule
See the full schedule page for weekly topics and assignments.
        """)

        (course_dir / 'schedule.qmd').write_text("""
# Course Schedule

## Week 1
Introduction to statistics. Read Chapter 1.
Complete HW 1 by Friday.

## Week 2
Descriptive statistics. Read Chapter 2.
Complete HW 2 by Friday.

## Week 3
Probability theory. Read Chapter 3.
Midterm exam on Friday.
        """)

        assignments_dir = course_dir / 'assignments'
        assignments_dir.mkdir()
        (assignments_dir / 'hw-1.qmd').write_text("# Homework 1")
        (assignments_dir / 'hw-2.qmd').write_text("# Homework 2")

    elif scenario == "missing_syllabus":
        # Missing syllabus sections
        (course_dir / 'syllabus.qmd').write_text("""
# Course Syllabus

## Grading
Homework and exams.
        """)

        (course_dir / 'schedule.qmd').write_text("""
## Week 1
Introduction with plenty of content here.
        """)

    elif scenario == "incomplete_schedule":
        # Incomplete schedule
        (course_dir / 'syllabus.qmd').write_text("""
# Syllabus

## Objectives
Learn statistics.

## Policies
Be nice.

## Grading
Homework 50%, Exams 50%.

## Schedule
See schedule page.
        """)

        (course_dir / 'schedule.qmd').write_text("""
## Week 1
Introduction. Lots of content here.

## Week 2

## Week 3
More content here.
        """)

    elif scenario == "missing_assignments":
        # Missing assignment files
        (course_dir / 'syllabus.qmd').write_text("""
# Syllabus

## Objectives
Learn statistics.

## Policies
Be respectful.

## Grading
Homework counts.

## Schedule
Weekly topics.
        """)

        (course_dir / 'schedule.qmd').write_text("""
## Week 1
Introduction. HW 1 due Friday. Good content here.

## Week 2
Descriptive stats. HW 2 due Friday. More content.

## Week 3
Probability. HW 3 due Friday. Even more content.
        """)

        # Only create HW 1, missing HW 2 and HW 3
        assignments_dir = course_dir / 'assignments'
        assignments_dir.mkdir()
        (assignments_dir / 'hw-1.qmd').write_text("# Homework 1")

    return course_dir


def run_demo():
    """Run validation demos for all scenarios."""
    scenarios = [
        ("complete", "✅ Complete Valid Course"),
        ("missing_syllabus", "❌ Missing Syllabus Sections"),
        ("incomplete_schedule", "❌ Incomplete Schedule"),
        ("missing_assignments", "⚠️  Missing Assignments"),
    ]

    for scenario_id, scenario_name in scenarios:
        print(f"\n{'=' * 70}")
        print(f"SCENARIO: {scenario_name}")
        print('=' * 70)

        # Create demo course
        course_dir = create_demo_course(scenario_id)

        # Run validation
        result = validate_teaching_content(str(course_dir))

        # Print report
        print(result.format_report())

        # Cleanup
        import shutil
        shutil.rmtree(course_dir)


if __name__ == '__main__':
    print("Teaching Content Validation Demo")
    print("=" * 70)
    print("This demo shows validation output for different course scenarios.")
    run_demo()
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
