#!/usr/bin/env python3
"""
Auto-detection engine for Craft Hub v2.0 command discovery system.

Scans commands/ directory recursively for *.md files, parses YAML frontmatter,
infers categories from file paths, and caches results for performance.

Usage:
    from commands._discovery import discover_commands, load_cached_commands

    # Get all commands (uses cache if fresh)
    commands = load_cached_commands()

    # Force regeneration
    commands = discover_commands()
"""

import os
import json
import glob
import re
from datetime import datetime
from typing import Optional

# Get the commands directory (same directory as this script)
COMMANDS_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(COMMANDS_DIR, "_cache.json")


def parse_yaml_frontmatter(content: str) -> dict:
    """
    Extract YAML frontmatter from markdown file.

    Frontmatter is delimited by --- at start and end.

    Supports:
    - Simple key: value pairs
    - Arrays with - items (at any indent level)
    - Nested objects in arrays (for arguments)

    Args:
        content: Full markdown file content

    Returns:
        Dictionary of frontmatter fields (empty dict if no frontmatter)
    """
    # Match frontmatter: starts with ---, content, ends with ---
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}

    frontmatter_text = match.group(1)
    metadata = {}

    # Parse YAML manually
    current_key = None
    current_array = []
    current_obj = {}
    in_array = False
    in_nested_obj = False
    array_item_indent = None  # Track indent level of array items

    for line in frontmatter_text.split('\n'):
        line = line.rstrip()

        # Skip empty lines
        if not line:
            continue

        # Determine indentation level
        indent = len(line) - len(line.lstrip())
        stripped = line.lstrip()

        # Top-level key-value pair (indent=0)
        if indent == 0 and ':' in stripped and not stripped.startswith('-'):
            # Save previous array if exists
            if in_array and current_key:
                # Save last nested object if exists
                if in_nested_obj and current_obj:
                    current_array.append(current_obj)
                    current_obj = {}

                metadata[current_key] = current_array
                current_array = []
                in_array = False
                in_nested_obj = False
                array_item_indent = None

            # Parse new key-value
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value:
                # Simple value
                metadata[key] = value
                current_key = key
            else:
                # Array follows
                current_key = key
                in_array = True
                current_array = []

        # Array item (starts with - at some indent level)
        elif in_array and stripped.startswith('-'):
            # Save previous nested object if exists
            if in_nested_obj and current_obj:
                current_array.append(current_obj)
                current_obj = {}
                in_nested_obj = False

            # Track array item indent level
            if array_item_indent is None:
                array_item_indent = indent

            # Parse array item
            item_content = stripped[1:].strip()  # Remove '-' and whitespace

            if ':' in item_content:
                # Array item with inline key:value (e.g., "- name: mode")
                # Start a new nested object
                in_nested_obj = True
                key, value = item_content.split(':', 1)
                key = key.strip()
                value = value.strip()
                current_obj = {key: value}
            else:
                # Simple array item
                current_array.append(item_content)

        # Nested object field (more indented than array item)
        elif in_array and in_nested_obj and indent > array_item_indent and ':' in stripped:
            # Parse key-value for nested object
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            current_obj[key] = value

    # Save final array if exists
    if in_array and current_key:
        # Save last nested object if exists
        if in_nested_obj and current_obj:
            current_array.append(current_obj)

        metadata[current_key] = current_array

    return metadata


def extract_first_heading(content: str) -> Optional[str]:
    """
    Extract the first markdown heading from content.

    Args:
        content: Markdown content

    Returns:
        First heading text (without #) or None
    """
    # Skip frontmatter
    content_without_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Find first heading (# or ##)
    match = re.search(r'^#{1,2}\s+(.+)$', content_without_frontmatter, re.MULTILINE)
    if match:
        heading = match.group(1).strip()
        # Remove command prefix like "/craft:code:lint - "
        heading = re.sub(r'^/craft:[a-z:]+\s*-\s*', '', heading)
        return heading

    return None


def extract_first_paragraph(content: str) -> Optional[str]:
    """
    Extract the first paragraph after frontmatter and headings.

    Args:
        content: Markdown content

    Returns:
        First paragraph text or None
    """
    # Skip frontmatter
    content_without_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Skip headings and find first paragraph
    lines = content_without_frontmatter.split('\n')
    paragraph = []

    for line in lines:
        line = line.strip()

        # Skip empty lines, headings, and code blocks
        if not line or line.startswith('#') or line.startswith('```'):
            if paragraph:
                break
            continue

        paragraph.append(line)

    if paragraph:
        text = ' '.join(paragraph)
        # Limit to first sentence or 60 chars
        if '.' in text:
            text = text.split('.')[0] + '.'
        if len(text) > 60:
            text = text[:57] + '...'
        return text

    return None


def infer_category(filepath: str) -> str:
    """
    Extract category from file path.

    Examples:
        code/lint.md → "code"
        git/worktree.md → "git"
        git/docs/refcard.md → "git" (docs are part of git category)
        hub.md → "hub" (special case)
        utils/readme-teach-config.md → "utils"

    Args:
        filepath: Relative path from commands/ directory

    Returns:
        Category name
    """
    # Normalize path separators
    filepath = filepath.replace('\\', '/')

    # Split into parts
    parts = filepath.split('/')

    # First part is either a directory (category) or a file (top-level command)
    if len(parts) == 1:
        # Top-level file like hub.md, do.md
        # Use filename (without .md) as category
        return parts[0].replace('.md', '')

    # First part is category directory
    first_part = parts[0]

    # Skip internal files
    if first_part.startswith('_'):
        return 'internal'

    # Directory name is the category
    return first_part


def infer_command_name(filepath: str, category: str) -> str:
    """
    Infer command name from filepath and category.

    Examples:
        code/lint.md → "code:lint"
        git/worktree.md → "git:worktree"
        hub.md → "hub"
        git/docs/refcard.md → "git:refcard"

    Args:
        filepath: Relative path from commands/ directory
        category: Inferred category

    Returns:
        Command name
    """
    # Get filename without extension
    filename = os.path.basename(filepath).replace('.md', '')

    # Normalize path
    filepath = filepath.replace('\\', '/')
    parts = filepath.split('/')

    # Special case: top-level commands like hub.md (only one part)
    if len(parts) == 1:
        return filename

    # Skip "docs" and "utils" directories in path for name inference
    # git/docs/refcard.md → git:refcard (not git:docs:refcard)
    name_parts = []
    for i in range(1, len(parts)):  # Start at 1 to skip category
        part = parts[i].replace('.md', '')
        if part not in ['docs', 'utils']:
            name_parts.append(part)

    if name_parts:
        return f"{category}:{':'.join(name_parts)}"

    # Fallback: category:filename
    return f"{category}:{filename}"


def discover_commands() -> list[dict]:
    """
    Auto-detect all commands from filesystem.

    Scans commands/**/*.md recursively, parses frontmatter, infers metadata.

    Returns:
        List of command metadata dictionaries
    """
    commands = []

    # Find all .md files in commands/ directory
    pattern = os.path.join(COMMANDS_DIR, '**', '*.md')
    md_files = glob.glob(pattern, recursive=True)

    for filepath in md_files:
        # Get relative path from commands directory
        rel_path = os.path.relpath(filepath, COMMANDS_DIR)

        # Skip internal/private files (start with _)
        if os.path.basename(filepath).startswith('_'):
            continue

        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            metadata = parse_yaml_frontmatter(content)

            # Infer category from path
            category = infer_category(rel_path)

            # Skip if internal category
            if category == 'internal':
                continue

            # Get or infer command name
            name = metadata.get('name')
            if not name:
                name = infer_command_name(rel_path, category)

            # Get or infer description
            description = metadata.get('description')
            if not description:
                # Try to extract from first heading
                description = extract_first_heading(content)
                if not description:
                    # Try first paragraph
                    description = extract_first_paragraph(content)
                if not description:
                    description = "No description available"

            # Build command metadata
            command = {
                'name': name,
                'category': category,
                'description': description,
                'file': rel_path
            }

            # Add optional fields if present
            if 'subcategory' in metadata:
                command['subcategory'] = metadata['subcategory']

            if 'modes' in metadata:
                # Parse modes if it's a string
                modes = metadata['modes']
                if isinstance(modes, str):
                    modes = [m.strip() for m in modes.split(',')]
                command['modes'] = modes

            if 'arguments' in metadata:
                command['arguments'] = metadata['arguments']

                # Infer mode support from arguments
                # If there's a 'mode' argument, extract supported modes from description
                for arg in metadata['arguments']:
                    if isinstance(arg, dict) and arg.get('name') == 'mode':
                        desc = arg.get('description', '')
                        # Extract modes from description like "(default|debug|optimize|release)"
                        mode_match = re.search(r'\(([^)]+)\)', desc)
                        if mode_match:
                            modes_str = mode_match.group(1)
                            modes = [m.strip() for m in modes_str.split('|')]
                            command['modes'] = modes
                        break

            if 'tutorial' in metadata:
                tutorial_val = metadata['tutorial']
                command['tutorial'] = tutorial_val == 'true' if isinstance(tutorial_val, str) else bool(tutorial_val)

            if 'tutorial_level' in metadata:
                command['tutorial_level'] = metadata['tutorial_level']

            if 'tutorial_file' in metadata:
                command['tutorial_file'] = metadata['tutorial_file']

            if 'related_commands' in metadata:
                related = metadata['related_commands']
                if isinstance(related, str):
                    related = [r.strip() for r in related.split(',')]
                command['related_commands'] = related

            if 'tags' in metadata:
                tags = metadata['tags']
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',')]
                command['tags'] = tags

            if 'project_types' in metadata:
                project_types = metadata['project_types']
                if isinstance(project_types, str):
                    project_types = [p.strip() for p in project_types.split(',')]
                command['project_types'] = project_types

            commands.append(command)

        except Exception as e:
            # Log error but continue processing
            print(f"Warning: Failed to parse {filepath}: {e}")
            continue

    return commands


def cache_commands(commands: list[dict]) -> None:
    """
    Save commands to cache file for performance.

    Args:
        commands: List of command metadata dictionaries
    """
    # Build category counts
    categories = {}
    for cmd in commands:
        cat = cmd['category']
        categories[cat] = categories.get(cat, 0) + 1

    # Count mode support
    with_modes = sum(1 for cmd in commands if 'modes' in cmd)

    # Count dry-run support (commands with dry-run argument)
    with_dry_run = 0
    for cmd in commands:
        if 'arguments' in cmd:
            args = cmd['arguments']
            if isinstance(args, list):
                for arg in args:
                    # Check if arg is a dict with 'name' field containing 'dry-run'
                    if isinstance(arg, dict) and 'name' in arg:
                        if 'dry-run' in arg['name'].lower():
                            with_dry_run += 1
                            break
                    # Also check string arguments
                    elif isinstance(arg, str) and 'dry-run' in arg.lower():
                        with_dry_run += 1
                        break

    # Build cache object
    cache = {
        'generated': datetime.now().isoformat(),
        'count': len(commands),
        'categories': categories,
        'stats': {
            'total': len(commands),
            'with_modes': with_modes,
            'with_dry_run': with_dry_run
        },
        'commands': commands
    }

    # Write to cache file
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def load_cached_commands() -> list[dict]:
    """
    Load commands from cache if fresh, else regenerate.

    Cache is stale if:
    - _cache.json doesn't exist
    - Any .md file is newer than cache file

    Returns:
        List of command metadata dictionaries
    """
    # Check if cache exists
    if not os.path.exists(CACHE_FILE):
        # Generate new cache
        commands = discover_commands()
        cache_commands(commands)
        return commands

    # Get cache modification time
    cache_mtime = os.path.getmtime(CACHE_FILE)

    # Find all .md files
    pattern = os.path.join(COMMANDS_DIR, '**', '*.md')
    md_files = glob.glob(pattern, recursive=True)

    # Check if any .md file is newer than cache
    for filepath in md_files:
        # Skip internal files
        if os.path.basename(filepath).startswith('_'):
            continue

        if os.path.getmtime(filepath) > cache_mtime:
            # Cache is stale, regenerate
            commands = discover_commands()
            cache_commands(commands)
            return commands

    # Cache is fresh, load it
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache['commands']
    except Exception as e:
        print(f"Warning: Failed to load cache: {e}")
        # Regenerate on error
        commands = discover_commands()
        cache_commands(commands)
        return commands


def get_command_stats() -> dict:
    """
    Get summary statistics about commands.

    Returns:
        Dictionary with stats:
        {
            "total": 97,
            "categories": {"code": 11, "test": 7, ...},
            "with_modes": 29,
            "with_dry_run": 29,
            "generated": "2026-01-17T12:00:00Z"
        }
    """
    # Load cache or generate
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            return {
                'total': cache['count'],
                'categories': cache['categories'],
                'with_modes': cache['stats']['with_modes'],
                'with_dry_run': cache['stats']['with_dry_run'],
                'generated': cache['generated']
            }
        except Exception:
            pass

    # Regenerate
    commands = discover_commands()
    cache_commands(commands)

    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    return {
        'total': cache['count'],
        'categories': cache['categories'],
        'with_modes': cache['stats']['with_modes'],
        'with_dry_run': cache['stats']['with_dry_run'],
        'generated': cache['generated']
    }


def get_commands_by_category(category: str) -> list[dict]:
    """
    Get all commands for a specific category.

    Args:
        category: Category name (e.g., 'code', 'test', 'docs')

    Returns:
        List of command dictionaries for that category
    """
    commands = load_cached_commands()
    return [cmd for cmd in commands if cmd['category'] == category]


def group_commands_by_subcategory(commands: list[dict]) -> dict:
    """
    Group commands by subcategory.

    Args:
        commands: List of command dictionaries

    Returns:
        Dictionary mapping subcategory -> list of commands
        Commands without subcategory go into 'general' group
    """
    grouped = {}

    for cmd in commands:
        subcat = cmd.get('subcategory', 'general')
        if subcat not in grouped:
            grouped[subcat] = []
        grouped[subcat].append(cmd)

    return grouped


def get_category_info(category: str) -> dict:
    """
    Get detailed information about a category.

    Args:
        category: Category name

    Returns:
        Dictionary with:
        - name: Category name
        - count: Number of commands
        - commands: List of commands
        - subcategories: Grouped commands by subcategory
        - icon: Category emoji icon
    """
    commands = get_commands_by_category(category)
    subcategories = group_commands_by_subcategory(commands)

    # Category icons
    icons = {
        'code': '💻',
        'test': '🧪',
        'docs': '📄',
        'git': '🔀',
        'site': '📖',
        'arch': '🏗️',
        'plan': '📋',
        'ci': '🚀',
        'dist': '📦',
        'workflow': '🔄',
        'hub': '🛠️',
        'check': '✅',
        'do': '🎯',
        'orchestrate': '🎯',
        'smart-help': '💡',
        'utils': '🔧'
    }

    return {
        'name': category,
        'count': len(commands),
        'commands': commands,
        'subcategories': subcategories,
        'icon': icons.get(category, '📁')
    }


if __name__ == '__main__':
    """
    CLI usage: python3 commands/_discovery.py

    Regenerates cache and prints statistics.
    """
    import sys

    print("Discovering commands...")
    commands = discover_commands()

    print(f"\nFound {len(commands)} commands")

    # Print category breakdown
    categories = {}
    for cmd in commands:
        cat = cmd['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\nCategories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Cache results
    print(f"\nCaching to {CACHE_FILE}...")
    cache_commands(commands)

    # Print stats
    stats = get_command_stats()
    print(f"\nStatistics:")
    print(f"  Total: {stats['total']}")
    print(f"  With modes: {stats['with_modes']}")
    print(f"  With dry-run: {stats['with_dry_run']}")
    print(f"  Generated: {stats['generated']}")

    print("\n✓ Done!")
