# Python Conventions

Style patterns used in `utils/` and `tests/`.

## Dataclass-Heavy Style

All structured data uses `@dataclass` with type hints:

```python
@dataclass
class ProjectInfo:
    type: str              # craft-plugin, teaching-site, r-package, ...
    version: Optional[str]
    path: Path
```

Used for: `CheckResult`, `ProjectInfo`, `DetectionResult`, `Issue`, `Section`, `Badge`, `FixResult`, `MetricChange`, `UpdatePlan`, `IgnorePattern`, etc.

## Walrus Operator Detection Chains

The detector uses `:=` for cascading type detection:

```python
if info := self._detect_craft_plugin():
    return info
if info := self._detect_teaching_site():
    return info
if info := self._detect_r_package():
    return info
```

Each `_detect_*` method returns `Optional[ProjectInfo]` — `None` means "not this type, try next."

## Dual Import Pattern

Modules support both package import and direct script execution:

```python
try:
    from .claude_md_detector import CLAUDEMDDetector
except ImportError:
    from claude_md_detector import CLAUDEMDDetector
```

**Why:** Allows `python3 utils/claude_md_auditor.py` (standalone) and `from utils.claude_md_auditor import ...` (package) to both work.

## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Classes (CLAUDE.md domain) | `CLAUDEMD` prefix, PascalCase | `CLAUDEMDDetector`, `CLAUDEMDAuditor` |
| Classes (general) | PascalCase | `BadgeSyncer`, `ComplexityScorer` |
| Private methods | `_` prefix | `_detect_craft_plugin()` |
| Constants | `UPPER_SNAKE` | `EDITOR_CHAIN` |
| Enums | PascalCase class, UPPER members | `Severity.ERROR`, `ChangeType.UPDATE` |

## Type Hints

- All function signatures include type hints
- `Optional[T]` for nullable returns
- `List[T]`, `Set[T]`, `Dict[K, V]` from `typing` (Python 3.8 compat)
- `Path` from `pathlib` for all file paths (never raw strings)
