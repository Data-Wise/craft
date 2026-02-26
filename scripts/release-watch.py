#!/usr/bin/env python3
"""Release Watch — Track Claude Code releases and identify plugin-relevant changes.

Fetches releases from the anthropics/claude-code GitHub repository and scans
release notes for changes that may affect the Craft plugin system. Cross-references
findings against current craft state (agents, hooks, hardcoded models).

Requires: gh CLI (authenticated)
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOX_WIDTH = 63
PLUGIN_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> project root

# Cache configuration
CACHE_DIR = Path.home() / ".claude"
CACHE_FILE = CACHE_DIR / "release-watch-cache.json"
CACHE_TTL = 86400  # 24 hours

KEYWORD_CATEGORIES = {
    "plugin_system": [
        "plugin", "skill", "command", "agent", "hook", "frontmatter",
    ],
    "schema": [
        "schema", "field", "property", "validation",
    ],
    "deprecation": [
        "deprecated", "removed", "breaking", "migration",
    ],
    "new_features": [
        "new", "added", "support", "feature", "capability",
    ],
    "models": [
        "sonnet", "opus", "haiku", "model",
    ],
    "environment": [
        "environment", "variable", "CLAUDE_",
    ],
    "fixed": [
        "fixed", "bug fix", "patch", "resolved",
    ],
}

# Map keyword categories to finding categories
CATEGORY_MAP = {
    "deprecation": "DEPRECATED",
    "new_features": "NEW",
    "plugin_system": "NEW",
    "schema": "BREAKING",
    "models": "NEW",
    "environment": "NEW",
    "fixed": "FIXED",
}

# Known model name patterns to scan for in the codebase
MODEL_PATTERNS = [
    r"claude-3-opus",
    r"claude-3-sonnet",
    r"claude-3-haiku",
    r"claude-3\.5-sonnet",
    r"claude-3\.5-haiku",
    r"claude-opus-4",
    r"claude-sonnet-4",
    r"claude-sonnet-4-5",
    r"claude-sonnet-4-6",
    r"claude-haiku-4-5",
    r"claude-opus-4-6",
    # Future-proofing: catch claude-{family}-{version} patterns
    r"claude-(?:opus|sonnet|haiku)-\d+(?:-\d+)*",
]


# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

def box_top():
    return "╔" + "═" * (BOX_WIDTH - 2) + "╗"


def box_bottom():
    return "╚" + "═" * (BOX_WIDTH - 2) + "╝"


def box_separator():
    return "╠" + "═" * (BOX_WIDTH - 2) + "╣"


def box_line(text=""):
    """Render a box line with text left-aligned inside the box."""
    inner_width = BOX_WIDTH - 4  # 2 for ║ + space on each side
    return "║  " + text.ljust(inner_width) + "║"


def box_blank():
    return box_line("")


# ---------------------------------------------------------------------------
# Cache layer
# ---------------------------------------------------------------------------

def load_cache():
    """Load cache from disk. Returns dict with per-source entries."""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(data):
    """Atomic write cache to disk (tmp + rename). Sets secure permissions."""
    CACHE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=CACHE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.chmod(tmp_path, 0o600)
        os.rename(tmp_path, CACHE_FILE)
    except OSError:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def is_fresh(cache_entry, source):
    """Check if a cache entry is within TTL."""
    if not cache_entry or "timestamp" not in cache_entry:
        return False
    age = time.time() - cache_entry["timestamp"]
    return age < CACHE_TTL


def get_cached(source, cache, refresh=False, no_cache=False):
    """Get data from cache if fresh, or None if stale/missing.

    Args:
        source: Cache key (e.g. "github_releases", "changelog", "releasebot")
        cache: The loaded cache dict
        refresh: If True, treat all entries as stale
        no_cache: If True, skip cache entirely
    Returns:
        Cached data or None
    """
    if no_cache:
        return None
    entry = cache.get(source)
    if entry and not refresh and is_fresh(entry, source):
        return entry.get("data")
    return None


def set_cached(source, data, cache):
    """Update a source entry in the cache dict and save to disk."""
    cache[source] = {
        "timestamp": time.time(),
        "data": data,
    }
    save_cache(cache)


# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------

def check_gh_installed():
    """Verify gh CLI is installed."""
    try:
        subprocess.run(
            ["gh", "--version"],
            capture_output=True, check=True, text=True,
        )
    except FileNotFoundError:
        print("Error: gh CLI is not installed.", file=sys.stderr)
        print("Install it: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: gh CLI returned an error.", file=sys.stderr)
        sys.exit(1)


def check_gh_auth():
    """Verify gh is authenticated."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Error: gh CLI is not authenticated.", file=sys.stderr)
        print("Run: gh auth login", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Fetch releases
# ---------------------------------------------------------------------------

def fetch_releases(count, since=None, cache=None, refresh=False, no_cache=False):
    """Fetch releases from GitHub via gh CLI.

    Uses ?per_page=N to request only the needed releases in a single API call
    instead of --paginate which fetches all pages. Results are cached for 24h.
    """
    if cache is None:
        cache = {}

    # Check cache first
    cached = get_cached("github_releases", cache, refresh=refresh, no_cache=no_cache)
    if cached is not None:
        return _filter_and_sort(cached, count, since)

    # Request more than count when using --since, as we filter afterward
    per_page = min(count * 2, 30) if since else min(count, 30)
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/anthropics/claude-code/releases?per_page={per_page}",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        # Stale fallback: if live fetch fails and stale cache exists, use it
        stale = cache.get("github_releases", {}).get("data")
        if stale and not no_cache:
            print("Warning: Live fetch failed, using stale cache.", file=sys.stderr)
            return _filter_and_sort(stale, count, since)
        print(f"Error: Failed to fetch releases.", file=sys.stderr)
        print(f"Details: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    try:
        releases = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse release data: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(releases, list):
        releases = [releases]

    # Cache the raw releases (before filtering)
    set_cached("github_releases", releases, cache)

    return _filter_and_sort(releases, count, since)


def _filter_and_sort(releases, count, since=None):
    """Sort releases by date descending, apply --since filter, and limit to count."""
    releases.sort(key=lambda r: r.get("published_at", ""), reverse=True)

    if since:
        since_clean = since.lstrip("v")
        filtered = []
        for r in releases:
            tag = r.get("tag_name", "").lstrip("v")
            if _version_gt(tag, since_clean):
                filtered.append(r)
        releases = filtered

    return releases[:count]


def _version_gt(a, b):
    """Simple version comparison: is a > b?"""
    def parts(v):
        return [int(x) for x in re.findall(r"\d+", v)]
    try:
        return parts(a) > parts(b)
    except (ValueError, IndexError):
        return a > b


# ---------------------------------------------------------------------------
# CHANGELOG.md parser
# ---------------------------------------------------------------------------

# Map CHANGELOG item prefixes to finding categories
_CHANGELOG_PREFIX_MAP = {
    "added": "NEW",
    "new": "NEW",
    "improved": "NEW",
    "updated": "NEW",
    "support": "NEW",
    "fixed": "FIXED",
    "fix": "FIXED",
    "deprecated": "DEPRECATED",
    "removed": "BREAKING",
    "breaking": "BREAKING",
}


def fetch_changelog(cache=None, refresh=False, no_cache=False):
    """Fetch raw CHANGELOG.md content from GitHub.

    Returns the text content, or None on failure (graceful degradation).
    """
    if cache is None:
        cache = {}

    cached = get_cached("changelog", cache, refresh=refresh, no_cache=no_cache)
    if cached is not None:
        return cached

    result = subprocess.run(
        ["gh", "api", "repos/anthropics/claude-code/contents/CHANGELOG.md",
         "--jq", ".content"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print("Warning: Failed to fetch CHANGELOG.md, continuing without it.",
              file=sys.stderr)
        return None

    # Decode base64 content
    try:
        content = base64.b64decode(result.stdout.strip()).decode("utf-8")
    except Exception:
        print("Warning: Failed to decode CHANGELOG.md content.", file=sys.stderr)
        return None

    set_cached("changelog", content, cache)
    return content


def parse_changelog(content):
    """Parse CHANGELOG.md into version-keyed sections with categorized items.

    Returns dict: { "2.1.59": [{"text": "...", "category": "NEW"}, ...], ... }
    """
    if not content:
        return {}

    versions = {}
    current_version = None

    for line in content.split("\n"):
        line_stripped = line.strip()

        # Version headers: ## 2.1.59 or ## v2.1.59
        version_match = re.match(r"^##\s+v?(\d+\.\d+\.\d+)", line_stripped)
        if version_match:
            current_version = version_match.group(1)
            versions[current_version] = []
            continue

        # Bullet items under a version
        if current_version and line_stripped.startswith("-"):
            text = line_stripped.lstrip("- ").strip()
            if not text:
                continue

            # Categorize by first word
            first_word = text.split()[0].lower().rstrip(":")
            category = _CHANGELOG_PREFIX_MAP.get(first_word, "NEW")

            versions[current_version].append({
                "text": text,
                "category": category,
            })

    return versions


def merge_changelog_with_releases(releases, changelog_versions):
    """Enrich release findings with CHANGELOG categorization.

    Adds a 'body_changelog' field to each release dict with parsed items.
    CHANGELOG categories take precedence over keyword matching.
    """
    if not changelog_versions:
        return releases

    for release in releases:
        tag = release.get("tag_name", "").lstrip("v")
        items = changelog_versions.get(tag, [])
        release["body_changelog"] = items

    return releases


# ---------------------------------------------------------------------------
# Scan release bodies for keywords
# ---------------------------------------------------------------------------

def scan_releases(releases):
    """Scan release bodies for plugin-relevant keywords.

    When CHANGELOG data is available (body_changelog field), uses those
    categories as the primary source. Falls back to keyword matching.

    Returns a dict of category -> list of finding dicts.
    """
    findings = {"NEW": [], "DEPRECATED": [], "BREAKING": [], "FIXED": []}

    for release in releases:
        tag = release.get("tag_name", "unknown")
        body = release.get("body", "") or ""

        # Build a lookup from CHANGELOG items for category precedence
        changelog_items = release.get("body_changelog", [])
        changelog_categories = {}
        for item in changelog_items:
            # Map CHANGELOG text to its category for line matching
            changelog_categories[item["text"].lower()[:40]] = item["category"]

        lines = body.split("\n")

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                continue

            line_lower = line_stripped.lower()

            # CHANGELOG category takes precedence if available
            cl_key = line_stripped.lstrip("-* ").strip().lower()[:40]
            category = changelog_categories.get(cl_key)

            # Otherwise, check explicit breaking/deprecation signals (word-boundary)
            if category is None:
                if any(re.search(rf'\b{re.escape(kw)}\b', line_lower)
                       for kw in ["breaking", "removed", "migration"]):
                    category = "BREAKING"
                elif any(re.search(rf'\b{re.escape(kw)}\b', line_lower)
                         for kw in ["deprecated"]):
                    category = "DEPRECATED"
                elif any(re.search(rf'\b{re.escape(kw)}\b', line_lower)
                         for kw in ["fix", "fixed", "bug fix", "patch", "resolved"]):
                    category = "FIXED"

            # Check if line contains any plugin-relevant keywords (word-boundary)
            matched_keywords = []
            for cat_name, keywords in KEYWORD_CATEGORIES.items():
                for kw in keywords:
                    if re.search(rf'\b{re.escape(kw.lower())}\b', line_lower):
                        matched_keywords.append(kw)
                        if category is None:
                            category = CATEGORY_MAP.get(cat_name, "NEW")

            if matched_keywords and category:
                # Clean up the line for display
                display = line_stripped.lstrip("-* ").strip()
                if len(display) > 50:
                    display = display[:47] + "..."

                finding = {
                    "version": tag,
                    "category": category,
                    "summary": display,
                    "keywords": list(set(matched_keywords)),
                    "raw_line": line_stripped,
                    "source": "github",
                    "changelog_enriched": cl_key in changelog_categories,
                }
                # Avoid duplicate summaries in the same category
                existing = [f["summary"] for f in findings[category]]
                if display not in existing:
                    findings[category].append(finding)

    return findings


# ---------------------------------------------------------------------------
# Craft state analysis
# ---------------------------------------------------------------------------

def analyze_craft_state():
    """Cross-reference against current craft plugin state."""
    state = {
        "hardcoded_models": [],
        "agent_features": {},
        "hook_events": [],
    }

    # 1. Scan agents for memory, isolation, background fields
    agents_dir = PLUGIN_ROOT / "agents"
    if agents_dir.is_dir():
        for md_file in sorted(agents_dir.rglob("*.md")):
            relative = md_file.relative_to(PLUGIN_ROOT)
            content = md_file.read_text(errors="replace")
            # Parse frontmatter
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm = fm_match.group(1)
                features = {}
                for field in ["memory", "isolation", "background"]:
                    match = re.search(rf"^{field}:\s*(.+)$", fm, re.MULTILINE)
                    if match:
                        features[field] = match.group(1).strip()
                if features:
                    state["agent_features"][str(relative)] = features

    # 2. Check for hardcoded model names across the codebase
    extensions = ["*.md", "*.py", "*.sh", "*.json", "*.yaml", "*.yml"]
    for ext in extensions:
        for filepath in PLUGIN_ROOT.rglob(ext):
            # Skip .git directories and node_modules
            parts = filepath.parts
            if ".git" in parts or "node_modules" in parts or "site" in parts:
                continue
            try:
                text = filepath.read_text(errors="replace")
            except (OSError, PermissionError):
                continue
            for pattern in MODEL_PATTERNS:
                matches = re.findall(pattern, text)
                if matches:
                    relative = filepath.relative_to(PLUGIN_ROOT)
                    for m in matches:
                        entry = {"file": str(relative), "model": m}
                        if entry not in state["hardcoded_models"]:
                            state["hardcoded_models"].append(entry)

    # 3. Look at hook patterns in commands
    commands_dir = PLUGIN_ROOT / "commands"
    hooks_dir = PLUGIN_ROOT / "scripts" / "hooks"
    for search_dir in [commands_dir, hooks_dir]:
        if search_dir and search_dir.is_dir():
            for f in sorted(search_dir.rglob("*.md")):
                content = f.read_text(errors="replace")
                fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm = fm_match.group(1)
                    # Look for hook-related fields: hooks, trigger, event
                    for field in ["hooks", "trigger", "event"]:
                        match = re.search(rf"^{field}:\s*(.+)$", fm, re.MULTILINE)
                        if match:
                            relative = f.relative_to(PLUGIN_ROOT)
                            state["hook_events"].append({
                                "file": str(relative),
                                "field": field,
                                "value": match.group(1).strip(),
                            })

    return state


# ---------------------------------------------------------------------------
# Generate action items
# ---------------------------------------------------------------------------

def generate_action_items(findings, craft_state):
    """Generate actionable items from findings and craft state."""
    items = []

    if findings["BREAKING"]:
        for f in findings["BREAKING"]:
            items.append(f"Review BREAKING change in {f['version']}: {f['summary']}")

    if findings["DEPRECATED"]:
        for f in findings["DEPRECATED"]:
            items.append(f"Check DEPRECATED item in {f['version']}: {f['summary']}")

    if craft_state["hardcoded_models"]:
        models = set(m["model"] for m in craft_state["hardcoded_models"])
        items.append(
            f"Audit {len(craft_state['hardcoded_models'])} hardcoded model "
            f"reference(s): {', '.join(sorted(models))}"
        )

    return items


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_terminal(releases, findings, craft_state, action_items):
    """Render output using box-drawing characters."""
    lines = []

    latest_tag = releases[0]["tag_name"] if releases else "unknown"
    latest_date = ""
    if releases and releases[0].get("published_at"):
        latest_date = releases[0]["published_at"][:10]

    # Header
    lines.append(box_top())
    lines.append(box_line("RELEASE WATCH — Claude Code"))
    lines.append(box_separator())
    lines.append(box_blank())
    date_str = f" ({latest_date})" if latest_date else ""
    lines.append(box_line(f"Latest: {latest_tag}{date_str}"))
    lines.append(box_line(f"Releases checked: {len(releases)}"))
    lines.append(box_blank())

    # Findings
    lines.append(box_separator())
    lines.append(box_line("PLUGIN-RELEVANT CHANGES"))
    lines.append(box_blank())

    has_findings = False
    for category in ["NEW", "DEPRECATED", "BREAKING", "FIXED"]:
        items = findings[category]
        if items:
            has_findings = True
            lines.append(box_line(category))
            for item in items:
                text = f"- {item['version']}: {item['summary']}"
                # Truncate to fit in box
                max_len = BOX_WIDTH - 6
                if len(text) > max_len:
                    text = text[: max_len - 3] + "..."
                lines.append(box_line(text))
            lines.append(box_blank())

    if not has_findings:
        lines.append(box_line("No plugin-relevant changes detected"))
        lines.append(box_blank())

    # Craft state
    lines.append(box_separator())
    lines.append(box_line("CRAFT STATE"))

    if craft_state["hardcoded_models"]:
        models = set(m["model"] for m in craft_state["hardcoded_models"])
        count = len(craft_state["hardcoded_models"])
        lines.append(box_line(f"Hardcoded models: {count} reference(s)"))
        for m in sorted(models):
            lines.append(box_line(f"  - {m}"))
    else:
        lines.append(box_line("No hardcoded model names found"))

    if craft_state["agent_features"]:
        lines.append(box_blank())
        lines.append(box_line(f"Agents with special fields: {len(craft_state['agent_features'])}"))
        for agent, features in craft_state["agent_features"].items():
            feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
            text = f"  - {agent}: {feat_str}"
            max_len = BOX_WIDTH - 6
            if len(text) > max_len:
                text = text[: max_len - 3] + "..."
            lines.append(box_line(text))

    if craft_state["hook_events"]:
        lines.append(box_blank())
        lines.append(box_line(f"Hook/trigger fields: {len(craft_state['hook_events'])}"))
        for h in craft_state["hook_events"]:
            text = f"  - {h['file']}: {h['field']}={h['value']}"
            max_len = BOX_WIDTH - 6
            if len(text) > max_len:
                text = text[: max_len - 3] + "..."
            lines.append(box_line(text))

    lines.append(box_blank())

    # Action items
    lines.append(box_separator())
    if action_items:
        lines.append(box_line(f"Action Items: {len(action_items)} item(s) need attention"))
        for item in action_items:
            max_len = BOX_WIDTH - 8
            text = f"  - {item}"
            if len(text) > max_len:
                text = text[: max_len - 3] + "..."
            lines.append(box_line(text))
    else:
        lines.append(box_line("Action Items: None — you're up to date"))
    lines.append(box_bottom())

    return "\n".join(lines)


def format_json(releases, findings, craft_state, action_items):
    """Render output as JSON."""
    latest_tag = releases[0]["tag_name"] if releases else "unknown"
    output = {
        "releases_checked": len(releases),
        "latest_version": latest_tag,
        "findings": {
            "new": findings["NEW"],
            "deprecated": findings["DEPRECATED"],
            "breaking": findings["BREAKING"],
            "fixed": findings["FIXED"],
        },
        "craft_state": craft_state,
        "action_items": action_items,
    }
    return json.dumps(output, indent=2)


def format_markdown(releases, findings, craft_state, action_items):
    """Render output as Markdown."""
    lines = []
    latest_tag = releases[0]["tag_name"] if releases else "unknown"
    latest_date = ""
    if releases and releases[0].get("published_at"):
        latest_date = releases[0]["published_at"][:10]

    lines.append("# Release Watch -- Claude Code")
    lines.append("")
    date_str = f" ({latest_date})" if latest_date else ""
    lines.append(f"**Latest:** {latest_tag}{date_str}  ")
    lines.append(f"**Releases checked:** {len(releases)}")
    lines.append("")

    lines.append("## Plugin-Relevant Changes")
    lines.append("")

    has_findings = False
    for category in ["NEW", "DEPRECATED", "BREAKING", "FIXED"]:
        items = findings[category]
        if items:
            has_findings = True
            lines.append(f"### {category}")
            lines.append("")
            for item in items:
                lines.append(f"- **{item['version']}**: {item['summary']}")
            lines.append("")

    if not has_findings:
        lines.append("No plugin-relevant changes detected.")
        lines.append("")

    lines.append("## Craft State")
    lines.append("")

    if craft_state["hardcoded_models"]:
        lines.append(f"**Hardcoded models:** {len(craft_state['hardcoded_models'])} reference(s)")
        lines.append("")
        for m in craft_state["hardcoded_models"]:
            lines.append(f"- `{m['file']}`: `{m['model']}`")
        lines.append("")
    else:
        lines.append("No hardcoded model names found.")
        lines.append("")

    if craft_state["agent_features"]:
        lines.append(f"**Agents with special fields:** {len(craft_state['agent_features'])}")
        lines.append("")
        for agent, features in craft_state["agent_features"].items():
            feat_str = ", ".join(f"`{k}={v}`" for k, v in features.items())
            lines.append(f"- `{agent}`: {feat_str}")
        lines.append("")

    if action_items:
        lines.append("## Action Items")
        lines.append("")
        for item in action_items:
            lines.append(f"- [ ] {item}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Track Claude Code releases and identify plugin-relevant changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s                       # Check latest 3 releases (terminal)
  %(prog)s --count 5             # Check latest 5 releases
  %(prog)s --since v1.0.25       # Only releases after v1.0.25
  %(prog)s --format json         # Output as JSON
  %(prog)s --format markdown     # Output as Markdown
""",
    )
    parser.add_argument(
        "--count", "-c", type=int, default=3,
        help="Number of releases to check (default: 3)",
    )
    parser.add_argument(
        "--since", "-s", type=str, default=None,
        help="Only show releases after this version (e.g., v1.0.25)",
    )
    parser.add_argument(
        "--format", "-f", dest="fmt", type=str, default="terminal",
        choices=["terminal", "json", "markdown"],
        help="Output format (default: terminal)",
    )
    parser.add_argument(
        "--refresh", action="store_true",
        help="Force refresh all cached data",
    )
    parser.add_argument(
        "--no-cache", dest="no_cache", action="store_true",
        help="Skip cache entirely (don't read or write)",
    )

    args = parser.parse_args()

    # Prerequisites
    check_gh_installed()
    check_gh_auth()

    # Load cache
    cache = {} if args.no_cache else load_cache()

    # Fetch releases
    releases = fetch_releases(
        args.count, since=args.since,
        cache=cache, refresh=args.refresh, no_cache=args.no_cache,
    )

    if not releases:
        if args.fmt == "json":
            print(json.dumps({"releases_checked": 0, "message": "No releases found"}, indent=2))
        else:
            print("No releases found matching the criteria.")
        sys.exit(0)

    # Fetch and merge CHANGELOG (enriches releases with structured categories)
    changelog_content = fetch_changelog(
        cache=cache, refresh=args.refresh, no_cache=args.no_cache,
    )
    if changelog_content:
        changelog_versions = parse_changelog(changelog_content)
        releases = merge_changelog_with_releases(releases, changelog_versions)

    # Analyze
    findings = scan_releases(releases)
    craft_state = analyze_craft_state()
    action_items = generate_action_items(findings, craft_state)

    # Output
    if args.fmt == "terminal":
        print(format_terminal(releases, findings, craft_state, action_items))
    elif args.fmt == "json":
        print(format_json(releases, findings, craft_state, action_items))
    elif args.fmt == "markdown":
        print(format_markdown(releases, findings, craft_state, action_items))


if __name__ == "__main__":
    main()
