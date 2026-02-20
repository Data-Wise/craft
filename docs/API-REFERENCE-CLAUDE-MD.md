# API Reference: Claude-MD Utilities

**Version:** v2.10.0-dev
**Module:** `utils/claude_md_*.py`
**Status:** Stable

---

## Table of Contents

1. [Project Detector](#project-detector)
2. [Auditor](#auditor)
3. [Fixer](#fixer)
4. [Template Populator](#template-populator)
5. [Section Editor](#section-editor)
6. [Updaters](#updaters)

---

## Project Detector

**Module:** `utils/claude_md_detector.py`
**Purpose:** Detect project type and extract metadata
**Lines:** 483

### Class: CLAUDEMDDetector

#### Constructor

```python
CLAUDEMDDetector(path: Path = None)
```

**Parameters:**

- `path` (Path, optional): Project directory path. Defaults to current directory.

**Example:**

```python
from utils.claude_md_detector import CLAUDEMDDetector
from pathlib import Path

detector = CLAUDEMDDetector(Path.cwd())
```

#### Methods

##### detect()

```python
def detect(self) -> Optional[ProjectInfo]:
    """Detect project type and gather information.

    Returns:
        ProjectInfo if project type detected, None otherwise
    """
```

**Returns:** `ProjectInfo` dataclass or `None`

**Example:**

```python
detector = CLAUDEMDDetector()
info = detector.detect()

if info:
    print(f"Project: {info.name}")
    print(f"Type: {info.type}")
    print(f"Version: {info.version}")
    print(f"Commands: {len(info.commands)}")
```

**Performance:** < 0.003s for typical projects

##### get_version_from_source()

```python
def get_version_from_source(self, source: str) -> Optional[str]:
    """Extract version from source file.

    Args:
        source: Source type (plugin.json, package.json, etc.)

    Returns:
        Version string or None if not found
    """
```

**Supported Sources:**

- `plugin.json` - Craft plugins
- `package.json` - Node.js projects
- `pyproject.toml` - Python projects
- `DESCRIPTION` - R packages

**Example:**

```python
version = detector.get_version_from_source("plugin.json")
# Returns: "2.10.0"
```

---

### Data Classes

#### ProjectInfo

```python
@dataclass
class ProjectInfo:
    """Detected project information for CLAUDE.md generation."""
    type: str              # craft-plugin, teaching-site, r-package, etc.
    version: str           # Extracted from version source
    version_source: str    # plugin.json, package.json, etc.
    name: str              # Project name
    commands: List[str]    # Discovered commands (for plugins)
    skills: List[str]      # Discovered skills (for plugins)
    agents: List[str]      # Discovered agents (for plugins)
    test_count: int        # Number of tests
    structure: Dict[str, Any]  # Project-specific structure info
```

**Example:**

```python
ProjectInfo(
    type="craft-plugin",
    version="2.10.0-dev",
    version_source="plugin.json",
    name="craft",
    commands=["do.md", "check.md", "hub.md"],
    skills=["backend.md", "frontend.md"],
    agents=["orchestrator.md"],
    test_count=847,
    structure={
        "has_commands": True,
        "has_skills": True,
        "has_agents": True
    }
)
```

---

## Auditor

**Module:** `utils/claude_md_auditor.py`
**Purpose:** Validate CLAUDE.md files
**Lines:** 599

### Class: CLAUDEMDAuditor

#### Constructor

```python
CLAUDEMDAuditor(claude_md_path: Path)
```

**Parameters:**

- `claude_md_path` (Path): Path to CLAUDE.md file

**Example:**

```python
from utils.claude_md_auditor import CLAUDEMDAuditor
from pathlib import Path

auditor = CLAUDEMDAuditor(Path("CLAUDE.md"))
```

#### Methods

##### audit()

```python
def audit(self) -> List[Issue]:
    """Run all validation checks.

    Returns:
        List of issues found
    """
```

**Returns:** `List[Issue]` - All validation issues

**Example:**

```python
auditor = CLAUDEMDAuditor(Path("CLAUDE.md"))
issues = auditor.audit()

for issue in issues:
    print(f"{issue.severity.value}: {issue.message}")
    if issue.fixable:
        print(f"  Fix: {issue.fix_method}")
```

##### check_version_sync()

```python
def check_version_sync(self) -> List[Issue]:
    """Verify version matches source file."""
```

**Returns:** List of version-related issues

**Example:**

```python
version_issues = auditor.check_version_sync()
# Returns: [Issue(severity=WARNING, category="version_mismatch", ...)]
```

##### check_command_coverage()

```python
def check_command_coverage(self) -> List[Issue]:
    """Verify all commands are documented."""
```

**Returns:** List of command coverage issues

**Categories:**

- `missing_command` - Command exists but not documented (INFO)
- `stale_command` - Command documented but file deleted (ERROR)

##### check_broken_links()

```python
def check_broken_links(self) -> List[Issue]:
    """Find broken internal links."""
```

**Returns:** List of broken link issues

**Example:**

```python
link_issues = auditor.check_broken_links()
for issue in link_issues:
    print(f"Line {issue.line_number}: {issue.message}")
```

##### check_required_sections()

```python
def check_required_sections(self) -> List[Issue]:
    """Verify expected sections are present."""
```

**Required Sections:**

- Project header
- Quick Commands
- Git Workflow (for plugins)
- Installation (if applicable)

---

### Data Classes

#### Issue

```python
@dataclass
class Issue:
    """Validation issue found in CLAUDE.md."""
    severity: Severity          # ERROR, WARNING, or INFO
    category: str               # Issue category
    message: str                # Description
    line_number: Optional[int]  # Line number (if applicable)
    fixable: bool               # Can be auto-fixed
    fix_method: Optional[str]   # Fix method name
```

**Example:**

```python
Issue(
    severity=Severity.ERROR,
    category="broken_link",
    message="Link points to non-existent file: docs/missing.md",
    line_number=45,
    fixable=True,
    fix_method="remove_link"
)
```

#### Severity Enum

```python
class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"      # 🔴 Critical - must fix
    WARNING = "warning"  # ⚠️ Should fix
    INFO = "info"        # 📝 Optional
```

---

## Fixer

**Module:** `utils/claude_md_fixer.py`
**Purpose:** Auto-fix CLAUDE.md issues
**Lines:** 442

### Class: CLAUDEMDFixer

#### Constructor

```python
CLAUDEMDFixer(claude_md_path: Path, issues: List[Issue])
```

**Parameters:**

- `claude_md_path` (Path): Path to CLAUDE.md
- `issues` (List[Issue]): Issues to fix from auditor

**Example:**

```python
from utils.claude_md_fixer import CLAUDEMDFixer

auditor = CLAUDEMDAuditor(Path("CLAUDE.md"))
issues = auditor.audit()

fixer = CLAUDEMDFixer(Path("CLAUDE.md"), issues)
```

#### Methods

##### fix_all()

```python
def fix_all(self, dry_run: bool = False) -> Dict[str, Any]:
    """Fix all fixable issues.

    Args:
        dry_run: Preview without applying changes

    Returns:
        Dict with fix results
    """
```

**Returns:**

```python
{
    'fixed_count': 5,
    'skipped_count': 2,
    'errors': [],
    'changes': [
        {'type': 'update_version', 'before': 'v2.9.0', 'after': 'v2.10.0'},
        {'type': 'remove_link', 'link': 'missing.md', 'line': 45}
    ]
}
```

**Example:**

```python
# Dry run - preview
results = fixer.fix_all(dry_run=True)
print(f"Would fix {results['fixed_count']} issues")

# Apply fixes
results = fixer.fix_all(dry_run=False)
print(f"Fixed {results['fixed_count']} issues")
```

##### update_version()

```python
def update_version(self, issue: Issue) -> bool:
    """Update version in CLAUDE.md to match source."""
```

##### remove_stale_command()

```python
def remove_stale_command(self, issue: Issue) -> bool:
    """Remove command that no longer exists."""
```

##### fix_broken_link()

```python
def fix_broken_link(self, issue: Issue) -> bool:
    """Remove or update broken link."""
```

##### add_missing_section()

```python
def add_missing_section(self, issue: Issue) -> bool:
    """Add required section to CLAUDE.md."""
```

---

## Template Populator

**Module:** `utils/claude_md_template_populator.py`
**Purpose:** Generate CLAUDE.md from templates
**Lines:** 485

### Class: CLAUDEMDTemplatePopulator

#### Constructor

```python
CLAUDEMDTemplatePopulator(
    template_path: Path,
    project_info: ProjectInfo
)
```

**Parameters:**

- `template_path` (Path): Path to template file
- `project_info` (ProjectInfo): Detected project information

**Example:**

```python
from utils.claude_md_template_populator import CLAUDEMDTemplatePopulator

detector = CLAUDEMDDetector()
info = detector.detect()

populator = CLAUDEMDTemplatePopulator(
    Path("templates/claude-md/plugin-template.md"),
    info
)
```

#### Methods

##### populate()

```python
def populate(self) -> str:
    """Generate CLAUDE.md content from template.

    Returns:
        Populated CLAUDE.md content
    """
```

**Template Variables:**

- `{project_name}` - Project name
- `{version}` - Current version
- `{command_count}` - Number of commands
- `{skill_count}` - Number of skills
- `{agent_count}` - Number of agents
- `{test_count}` - Number of tests
- `{doc_coverage}` - Documentation percentage
- `{commands_list}` - Markdown list of commands
- `{quick_commands_table}` - Command reference table
- `{git_workflow_diagram}` - Mermaid diagram
- ... +8 more variables

**Example:**

```python
content = populator.populate()

# Write to file
output_path = Path("CLAUDE.md")
output_path.write_text(content)
```

##### get_available_variables()

```python
def get_available_variables(self) -> List[str]:
    """Get list of available template variables."""
```

**Returns:** List of variable names

**Example:**

```python
variables = populator.get_available_variables()
print("Available variables:", ", ".join(variables))
# Output: Available variables: project_name, version, command_count, ...
```

---

## Section Editor

**Module:** `utils/claude_md_section_editor.py`
**Purpose:** Interactive section editing
**Lines:** 299

### Class: CLAUDEMDSectionEditor

#### Constructor

```python
CLAUDEMDSectionEditor(claude_md_path: Path)
```

**Parameters:**

- `claude_md_path` (Path): Path to CLAUDE.md

**Example:**

```python
from utils.claude_md_section_editor import CLAUDEMDSectionEditor

editor = CLAUDEMDSectionEditor(Path("CLAUDE.md"))
```

#### Methods

##### list_sections()

```python
def list_sections(self) -> List[str]:
    """List available sections in CLAUDE.md."""
```

**Returns:** List of section names

**Example:**

```python
sections = editor.list_sections()
for section in sections:
    print(f"- {section}")

# Output:
# - Quick Commands
# - Git Workflow
# - Execution Modes
# - Recent Major Features
```

##### edit_section()

```python
def edit_section(
    self,
    section_name: str,
    new_content: str,
    preview: bool = False
) -> bool:
    """Edit specific section.

    Args:
        section_name: Name of section to edit
        new_content: New section content
        preview: Preview without applying

    Returns:
        True if successful
    """
```

**Example:**

```python
new_content = """
## Quick Commands

| Task | Command |
|------|---------|
| Test | /craft:test |
| Lint | /craft:code:lint |
"""

success = editor.edit_section(
    "Quick Commands",
    new_content,
    preview=False
)

if success:
    print("Section updated successfully")
```

---

## Updaters

### Simple Updater

**Module:** `utils/claude_md_updater_simple.py`
**Purpose:** Simple metric-based updates
**Lines:** 371

#### Class: SimpleCLAUDEMDUpdater

```python
SimpleCLAUDEMDUpdater(
    claude_md_path: Path,
    project_info: ProjectInfo
)
```

**Purpose:** Update simple metrics (version, counts, percentages)

**Methods:**

- `detect_changes()` - Find metric changes
- `apply_changes()` - Apply updates
- `generate_preview()` - Show preview

### Full Updater

**Module:** `utils/claude_md_updater.py`
**Purpose:** Comprehensive updates
**Lines:** 534

#### Class: CLAUDEMDUpdater

```python
CLAUDEMDUpdater(
    claude_md_path: Path,
    project_info: ProjectInfo
)
```

**Purpose:** Full CLAUDE.md synchronization

**Methods:**

- `update_version()` - Sync version
- `update_commands()` - Add/remove commands
- `update_test_counts()` - Update test metrics
- `update_documentation()` - Sync doc status
- `update_all()` - Full update

---

## Usage Examples

### Example 1: Full Workflow

```python
from pathlib import Path
from utils.claude_md_detector import CLAUDEMDDetector
from utils.claude_md_auditor import CLAUDEMDAuditor
from utils.claude_md_fixer import CLAUDEMDFixer

# 1. Detect project
detector = CLAUDEMDDetector(Path.cwd())
info = detector.detect()

if not info:
    print("Could not detect project type")
    exit(1)

print(f"Detected: {info.type} project")
print(f"Version: {info.version}")

# 2. Audit CLAUDE.md
auditor = CLAUDEMDAuditor(Path("CLAUDE.md"))
issues = auditor.audit()

print(f"Found {len(issues)} issues")

# 3. Fix issues
fixable = [i for i in issues if i.fixable]
print(f"{len(fixable)} issues can be auto-fixed")

if fixable:
    fixer = CLAUDEMDFixer(Path("CLAUDE.md"), fixable)
    results = fixer.fix_all(dry_run=False)
    print(f"Fixed {results['fixed_count']} issues")
```

### Example 2: Scaffold New CLAUDE.md

```python
from pathlib import Path
from utils.claude_md_detector import CLAUDEMDDetector
from utils.claude_md_template_populator import CLAUDEMDTemplatePopulator

# Detect project
detector = CLAUDEMDDetector()
info = detector.detect()

# Choose template based on project type
template_map = {
    "craft-plugin": "templates/claude-md/plugin-template.md",
    "teaching-site": "templates/claude-md/teaching-template.md",
    "r-package": "templates/claude-md/r-package-template.md"
}

template_path = Path(template_map.get(info.type, "plugin-template.md"))

# Populate template
populator = CLAUDEMDTemplatePopulator(template_path, info)
content = populator.populate()

# Write CLAUDE.md
output_path = Path("CLAUDE.md")
output_path.write_text(content)

print(f"Created CLAUDE.md from {template_path.name}")
```

### Example 3: Interactive Section Edit

```python
from pathlib import Path
from utils.claude_md_section_editor import CLAUDEMDSectionEditor

editor = CLAUDEMDSectionEditor(Path("CLAUDE.md"))

# List sections
sections = editor.list_sections()
print("Available sections:")
for i, section in enumerate(sections, 1):
    print(f"{i}. {section}")

# Edit section
section_name = input("Which section to edit? ")
new_content = input("New content: ")

success = editor.edit_section(section_name, new_content, preview=True)

if success:
    confirm = input("Apply changes? (y/n): ")
    if confirm.lower() == 'y':
        editor.edit_section(section_name, new_content, preview=False)
```

---

## Error Handling

### Common Exceptions

```python
class CLAUDEMDError(Exception):
    """Base exception for claude-md utilities"""
    pass

class ProjectDetectionError(CLAUDEMDError):
    """Raised when project type cannot be detected"""
    pass

class ValidationError(CLAUDEMDError):
    """Raised when CLAUDE.md validation fails"""
    pass

class FixError(CLAUDEMDError):
    """Raised when auto-fix operation fails"""
    pass
```

### Error Handling Example

```python
from utils.claude_md_detector import CLAUDEMDDetector, ProjectDetectionError

try:
    detector = CLAUDEMDDetector()
    info = detector.detect()

    if not info:
        raise ProjectDetectionError("No project markers found")

except ProjectDetectionError as e:
    print(f"Detection failed: {e}")
    print("Try creating: .claude-plugin/plugin.json or DESCRIPTION")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Considerations

### Optimization Tips

1. **Cache project detection:**

   ```python
   detector = CLAUDEMDDetector()
   info = detector.detect()
   # Reuse 'info' for multiple operations
   ```

2. **Use dry-run for preview:**

   ```python
   # Fast preview without file I/O
   results = fixer.fix_all(dry_run=True)
   ```

3. **Section-specific updates:**

   ```python
   # Update only what changed
   updater.update_version()  # Fast
   # Instead of:
   updater.update_all()      # Slower
   ```

### Memory Usage

- Peak: ~15 MB for large projects
- File operations: Stream-based (constant memory)
- Thread-safe: No shared mutable state

---

## Version Compatibility

| Craft Version | API Version | Changes |
|---------------|-------------|---------|
| **2.10.0-dev** | 1.0 | Initial release |
| **2.10.1** | 1.1 | (planned) Remote templates |
| **2.11.0** | 2.0 | (planned) Multi-file support |

---

## References

- [Command Reference](commands/docs/claude-md.md)
- [Tutorial Guide](tutorials/claude-md-workflows.md)
- [Quick Reference](reference/REFCARD-CLAUDE-MD.md)

---

**API Version:** 1.0
**Last Updated:** 2026-01-30
**Maintained By:** Craft Development Team
