#!/usr/bin/env python3
"""
Example script demonstrating teach_config.py usage.

Usage:
    python3 examples/test_parser.py [path/to/config/directory]

This will load and validate the teaching config from the specified directory
(or current directory if not specified).
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teach_config import load_teach_config


def main():
    # Get directory from command line or use current directory
    cwd = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"Loading teaching config from: {Path(cwd).resolve()}")
    print("-" * 60)

    try:
        config = load_teach_config(cwd)

        if config is None:
            print("No teaching config found.")
            print("\nSearched for:")
            print("  - .flow/teach-config.yml")
            print("  - teach-config.yml")
            sys.exit(1)

        print("Configuration loaded successfully!\n")

        # Display course info
        course = config["course"]
        print(f"Course: {course['number']} - {course['title']}")
        print(f"Semester: {course['semester']} {course['year']}")

        # Display dates
        dates = config["dates"]
        print(f"\nDates:")
        print(f"  Start: {dates['start']}")
        print(f"  End: {dates['end']}")

        # Display breaks if any
        if dates.get("breaks"):
            print(f"\nBreaks:")
            for i, brk in enumerate(dates["breaks"], 1):
                print(f"  {i}. {brk['name']}: {brk['start']} to {brk['end']}")

        # Display instructor if present
        if "instructor" in config:
            instructor = config["instructor"]
            print(f"\nInstructor:")
            if "name" in instructor:
                print(f"  Name: {instructor['name']}")
            if "email" in instructor:
                print(f"  Email: {instructor['email']}")
            if "office_hours" in instructor:
                print(f"  Office Hours: {instructor['office_hours']}")

        # Display deployment settings
        deployment = config["deployment"]
        print(f"\nDeployment:")
        print(f"  Production Branch: {deployment['production_branch']}")
        print(f"  Draft Branch: {deployment['draft_branch']}")
        if "gh_pages_url" in deployment:
            print(f"  GitHub Pages: {deployment['gh_pages_url']}")

        # Display progress
        progress = config["progress"]
        print(f"\nProgress:")
        print(f"  Current Week: {progress['current_week']}")

        # Display validation settings
        validation = config["validation"]
        print(f"\nValidation:")
        print(f"  Strict Mode: {validation['strict_mode']}")
        print(f"  Required Sections: {', '.join(validation['required_sections'])}")

        # Option to dump full config as JSON
        if "--json" in sys.argv:
            print("\n" + "=" * 60)
            print("Full configuration (JSON):")
            print("=" * 60)
            print(json.dumps(config, indent=2, default=str))

    except ValueError as e:
        print(f"Validation Error:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
