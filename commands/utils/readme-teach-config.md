# Teaching Configuration Parser

Python utility for parsing and validating `.flow/teach-config.yml` files in teaching projects.

## Features

- Automatic config file detection (`.flow/teach-config.yml` or `teach-config.yml`)
- Comprehensive validation (required fields, date formats, logical consistency)
- Break validation (dates, overlaps, semester bounds)
- Default value application for optional fields
- Graceful error handling with clear error messages
- 93% test coverage with 55 unit tests

## Usage

### Basic Usage

```python
from commands.utils.teach_config import load_teach_config

# Load config from current directory
config = load_teach_config()

if config:
    print(f"Course: {config['course']['number']}")
    print(f"Current week: {config['progress']['current_week']}")
else:
    print("No teaching config found")
```

### With Custom Directory

```python
config = load_teach_config("/path/to/teaching/project")
```

### Error Handling

```python
try:
    config = load_teach_config()
except ValueError as e:
    print(f"Validation failed: {e}")
```

## Validation Rules

### Required Fields

- `course.number` (string)
- `course.title` (string)
- `course.semester` (Spring/Fall/Winter/Summer)
- `course.year` (integer, 2000-2100)
- `dates.start` (YYYY-MM-DD)
- `dates.end` (YYYY-MM-DD)

### Optional Fields (with defaults)

- `deployment.production_branch` (default: "production")
- `deployment.draft_branch` (default: "draft")
- `deployment.gh_pages_url` (optional)
- `progress.current_week` (default: "auto")
- `validation.required_sections` (default: ["grading", "policies", "objectives", "schedule"])
- `validation.strict_mode` (default: true)
- `dates.breaks` (default: [])

### Date Validation

- All dates must be in `YYYY-MM-DD` format with zero padding
- Semester end must be after start
- Breaks must fall within semester dates
- Breaks cannot overlap
- Each break must have: `name`, `start`, `end`

## Return Values

- **Success**: Dictionary with config data and defaults applied
- **Not found**: `None` (file doesn't exist, not an error)
- **Malformed YAML**: `None` (with warning to stderr)
- **Validation failure**: Raises `ValueError` with detailed error messages

## Helper Functions

### `get_config_path(cwd: str) -> str | None`

Find config file in directory (priority: `.flow/teach-config.yml`, then `teach-config.yml`).

### `validate_date(date_str: str) -> bool`

Check if date string is valid YYYY-MM-DD format.

### `parse_date(date_str: str) -> datetime | None`

Parse date string to datetime object.

### `validate_breaks(breaks: list, start: str, end: str) -> list[str]`

Validate break periods, return list of errors.

### `apply_defaults(config: dict) -> dict`

Apply default values for optional fields.

### `validate_config(config: dict) -> list[str]`

Validate entire configuration, return list of errors.

## Example Config

See `examples/teach-config-example.yml` for a complete example.

## Testing

```bash
# Run tests
python3 tests/test_teach_config.py -v

# Check coverage
python3 -m coverage run --source=commands/utils tests/test_teach_config.py
python3 -m coverage report --include="commands/utils/teach_config.py"

# Test with example
python3 examples/test_parser.py examples/
```

## Schema Documentation

Full schema reference: `docs/teaching-config-schema.md`

## Error Messages

The parser provides clear, actionable error messages:

```
Configuration validation failed:
  - Missing required field: 'course.number'
  - Invalid start date format: '2026/01/19' (expected YYYY-MM-DD)
  - Break 'Spring Break': ends after semester ends (2026-05-08)
  - Breaks 'Spring Break' and 'Reading Week' overlap
```
