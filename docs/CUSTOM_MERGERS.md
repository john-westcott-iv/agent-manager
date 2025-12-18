# Creating Custom Mergers

This guide shows you how to create custom merger classes for handling new file types or implementing special merge logic.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [AbstractMerger Interface](#abstractmerger-interface)
4. [DictMerger Base Class](#dictmerger-base-class)
5. [Merge Strategies](#merge-strategies)
6. [Self-Documenting Preferences](#self-documenting-preferences)
7. [Testing](#testing)
8. [Real-World Examples](#real-world-examples)

---

## Overview

A **merger** defines how to combine configuration files from multiple hierarchy levels. Agent Manager includes built-in mergers for common types:
- **JsonMerger**: Deep merge JSON objects
- **YamlMerger**: Deep merge YAML objects
- **MarkdownMerger**: Concatenate with AI context markers
- **TextMerger**: Simple concatenation
- **CopyMerger**: Last source wins (fallback)

You can create custom mergers for:
- New file types (TOML, XML, INI, etc.)
- Special merge logic (domain-specific rules)
- Custom formatting preferences

---

## Quick Start

### Example: TOML Merger

Create `agent_manager/plugins/mergers/toml_merger.py`:

```python
"""TOML merger with deep dictionary merging."""

import tomllib  # Python 3.11+
import tomli_w
from typing import Any

from .dict_merger import DictMerger


class TomlMerger(DictMerger):
    """Merger for TOML files with deep dictionary merging."""

    # Files this merger handles
    FILE_EXTENSIONS = [".toml"]

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Parse TOML content.

        Args:
            content: TOML string

        Returns:
            Python dictionary

        Raises:
            tomllib.TOMLDecodeError: If invalid TOML
        """
        return tomllib.loads(content)

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Convert Python object to TOML.

        Args:
            data: Python dictionary
            **settings: Formatting settings

        Returns:
            TOML string
        """
        # Get preferences
        prefs = cls.merge_preferences()
        multiline_strings = settings.get(
            "multiline_strings",
            prefs.get("multiline_strings", {}).get("default", False)
        )

        return tomli_w.dumps(data, multiline_strings=multiline_strings)

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define TOML merger preferences."""
        return {
            "multiline_strings": {
                "type": "bool",
                "default": False,
                "description": "Use multiline strings for long values",
            }
        }
```

That's it! Agent Manager will auto-discover and register this merger for `.toml` files.

---

## AbstractMerger Interface

### Required Class Attributes

```python
class MyMerger(AbstractMerger):
    # File extensions this merger handles
    FILE_EXTENSIONS: list[str] = [".myext"]
```

### Required Methods

#### merge(base, new, source, sources, **settings) -> str

The core merge logic.

```python
@classmethod
def merge(
    cls,
    base: str,
    new: str,
    source: str,
    sources: list[str],
    **settings
) -> str:
    """Merge new content into base content.

    Args:
        base: Existing merged content (empty string if first occurrence)
        new: New content to merge in
        source: Name of the hierarchy level providing new content
        sources: List of all sources that contributed to base so far
        **settings: Merger-specific preferences from config

    Returns:
        Merged content string
    """
    # Your merge logic here
    return merged_content
```

**Flow:**
1. First file: `merge("", content_from_org, "organization", [])`
2. Second file: `merge(org_content, content_from_team, "team", ["organization"])`
3. Third file: `merge(merged_content, content_from_personal, "personal", ["organization", "team"])`

### Optional Methods

#### merge_preferences() -> dict

Define configurable settings for this merger.

```python
@classmethod
def merge_preferences(cls) -> dict:
    """Define configurable preferences.

    Returns:
        Dictionary mapping setting names to their schemas:
        {
            "setting_name": {
                "type": "int|str|bool|float",
                "default": <value>,
                "description": "Help text",
                "min": <optional, for int/float>,
                "max": <optional, for int/float>,
                "choices": <optional, for str>
            }
        }
    """
    return {}  # No preferences
```

This enables:
- Interactive configuration via `agent-manager mergers configure`
- Self-documentation via `agent-manager mergers show`
- Settings stored in `config.yaml` under `mergers.<MergerClassName>`

---

## DictMerger Base Class

For structured data (JSON, YAML, TOML, XML), extend `DictMerger` instead of `AbstractMerger`. It provides:
- Automatic deep merging
- Pluggable merge strategies
- Deserialization/serialization framework

### Interface

```python
from .dict_merger import DictMerger

class MyStructuredMerger(DictMerger):
    FILE_EXTENSIONS = [".myformat"]

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Parse content into Python object."""
        raise NotImplementedError

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Convert Python object to string."""
        raise NotImplementedError

    @classmethod
    def get_merge_strategy(cls) -> type[MergeStrategy]:
        """Override to use custom merge strategy."""
        return MergeStrategy  # Default
```

### Example: XML Merger

```python
"""XML merger with deep dictionary merging."""

import xmltodict
from typing import Any

from .dict_merger import DictMerger


class XmlMerger(DictMerger):
    """Merger for XML files."""

    FILE_EXTENSIONS = [".xml"]

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Parse XML to dictionary."""
        return xmltodict.parse(content)

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Convert dictionary to XML."""
        prefs = cls.merge_preferences()
        pretty = settings.get("pretty", prefs["pretty"]["default"])

        return xmltodict.unparse(
            data,
            pretty=pretty,
            indent="  " if pretty else None
        )

    @classmethod
    def merge_preferences(cls) -> dict:
        return {
            "pretty": {
                "type": "bool",
                "default": True,
                "description": "Pretty-print XML output",
            }
        }
```

---

## Merge Strategies

When using `DictMerger`, you can customize how dictionaries and lists are merged by providing a custom `MergeStrategy`.

### Built-in Strategies

```python
from agent_manager.plugins.mergers import (
    MergeStrategy,        # Deep merge dicts, replace lists
    ExtendListStrategy,   # Deep merge dicts, extend lists
    ReplaceStrategy,      # Replace everything (no deep merge)
)
```

### Using Custom Strategies

```python
class MyJsonMerger(JsonMerger):
    @classmethod
    def get_merge_strategy(cls):
        return ExtendListStrategy  # Lists extend instead of replace
```

### Creating Custom Strategies

```python
from agent_manager.plugins.mergers import MergeStrategy

class SmartListStrategy(MergeStrategy):
    """Merge lists by ID field."""

    @staticmethod
    def merge_list(base: list, new: list, path: str = "") -> list:
        """Merge lists of dicts by 'id' field."""
        if not base:
            return new
        if not new:
            return base

        # If lists contain dicts with 'id', merge by ID
        if isinstance(base[0], dict) and "id" in base[0]:
            merged_dict = {item["id"]: item for item in base}
            for item in new:
                merged_dict[item["id"]] = item
            return list(merged_dict.values())

        # Otherwise, extend
        result = base.copy()
        for item in new:
            if item not in result:
                result.append(item)
        return result
```

See [Merge Strategies](STRATEGIES.md) for detailed documentation.

---

## Self-Documenting Preferences

Make your merger configurable with `merge_preferences()`:

### Preference Schema

```python
@classmethod
def merge_preferences(cls) -> dict:
    return {
        # Integer preference
        "indent": {
            "type": "int",
            "default": 2,
            "description": "Number of spaces for indentation",
            "min": 0,
            "max": 8,
        },

        # Boolean preference
        "sort_keys": {
            "type": "bool",
            "default": False,
            "description": "Sort keys alphabetically",
        },

        # String preference with choices
        "style": {
            "type": "str",
            "default": "compact",
            "description": "Output style",
            "choices": ["compact", "expanded", "minimal"],
        },

        # Float preference
        "threshold": {
            "type": "float",
            "default": 0.5,
            "description": "Merge threshold",
            "min": 0.0,
            "max": 1.0,
        },
    }
```

### Using Preferences

```python
@classmethod
def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
    # Validate settings (warns about unknown settings)
    cls._validate_settings(settings)

    # Get preferences with defaults
    prefs = cls.merge_preferences()
    indent = settings.get("indent", prefs["indent"]["default"])
    sort_keys = settings.get("sort_keys", prefs["sort_keys"]["default"])

    # Use in merge logic
    ...
```

### User Experience

Users can then configure your merger:

```bash
$ agent-manager mergers configure --merger MyMerger

Configuring MyMerger...

indent (int, default=2): Number of spaces for indentation
  Valid range: 0-8
  Enter new value: 4

sort_keys (bool, default=False): Sort keys alphabetically
  Enter new value (true/false): true

✓ Configuration saved!
```

Settings are stored in `~/.agent-manager/config.yaml`:

```yaml
mergers:
  MyMerger:
    indent: 4
    sort_keys: true
```

---

## Complex Example: CSV Merger

```python
"""CSV merger with configurable merge strategies."""

import csv
import io
from typing import Any

from agent_manager import output
from .abstract_merger import AbstractMerger


class CsvMerger(AbstractMerger):
    """Merger for CSV files with various strategies."""

    FILE_EXTENSIONS = [".csv"]

    @classmethod
    def merge(
        cls,
        base: str,
        new: str,
        source: str,
        sources: list[str],
        **settings
    ) -> str:
        """Merge CSV files.

        Strategies:
        - append: Append rows
        - replace: Replace entire file
        - key_merge: Merge by key column
        """
        cls._validate_settings(settings)

        prefs = cls.merge_preferences()
        strategy = settings.get("strategy", prefs["strategy"]["default"])
        key_column = settings.get("key_column", prefs["key_column"]["default"])

        # Parse CSVs
        base_rows = list(csv.DictReader(io.StringIO(base))) if base else []
        new_rows = list(csv.DictReader(io.StringIO(new)))

        if strategy == "append":
            merged_rows = base_rows + new_rows
        elif strategy == "replace":
            merged_rows = new_rows
        elif strategy == "key_merge":
            # Merge by key column
            merged_dict = {row[key_column]: row for row in base_rows}
            for row in new_rows:
                merged_dict[row[key_column]] = row
            merged_rows = list(merged_dict.values())
        else:
            output.warning(f"Unknown strategy '{strategy}', using append")
            merged_rows = base_rows + new_rows

        # Serialize back to CSV
        if not merged_rows:
            return ""

        output_io = io.StringIO()
        fieldnames = merged_rows[0].keys()
        writer = csv.DictWriter(output_io, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

        return output_io.getvalue()

    @classmethod
    def merge_preferences(cls) -> dict:
        return {
            "strategy": {
                "type": "str",
                "default": "append",
                "description": "Merge strategy for CSV rows",
                "choices": ["append", "replace", "key_merge"],
            },
            "key_column": {
                "type": "str",
                "default": "id",
                "description": "Key column for key_merge strategy",
            },
        }
```

---

## Testing

### Unit Tests

```python
import pytest
from my_merger import MyMerger


def test_merge_empty_base():
    """Test merging into empty base."""
    result = MyMerger.merge("", "new content", "source1", [])
    assert result == "new content"


def test_merge_preferences():
    """Test preferences schema."""
    prefs = MyMerger.merge_preferences()

    assert "indent" in prefs
    assert prefs["indent"]["type"] == "int"
    assert prefs["indent"]["default"] == 2


def test_merge_with_settings():
    """Test merge with custom settings."""
    result = MyMerger.merge(
        base="old",
        new="new",
        source="test",
        sources=[],
        indent=4  # Custom setting
    )
    # Assert result uses indent=4
    ...


def test_validate_settings():
    """Test settings validation."""
    # Should not raise for valid settings
    MyMerger.merge("", "", "test", [], indent=2)

    # Should warn for invalid settings
    # (check debug output for warning)
    MyMerger.merge("", "", "test", [], invalid_setting="value")
```

### Integration Tests

```python
def test_merger_in_registry():
    """Test merger is registered correctly."""
    from agent_manager.plugins.mergers import MergerRegistry

    registry = MergerRegistry()
    registry.register_extension(".myext", MyMerger)

    # Should return MyMerger for .myext files
    from pathlib import Path
    merger = registry.get_merger(Path("config.myext"))
    assert merger == MyMerger
```

---

## Real-World Examples

### JsonMerger

See `agent_manager/plugins/mergers/json_merger.py`:
- Extends `DictMerger`
- Uses `json` module for serialization
- Configurable indent and sort_keys

### MarkdownMerger

See `agent_manager/plugins/mergers/markdown_merger.py`:
- Extends `AbstractMerger` directly
- Concatenates with AI context markers
- Configurable separator style

### TextMerger

See `agent_manager/plugins/mergers/text_merger.py`:
- Simplest possible merger
- Just concatenates with source markers

---

## Best Practices

### 1. Extend DictMerger for Structured Data

If your format can be represented as nested dicts/lists, use `DictMerger`:

```python
# Good
class TomlMerger(DictMerger):
    ...

# Not as good (more work)
class TomlMerger(AbstractMerger):
    def merge(self, ...):
        # Have to implement deep merge yourself
        ...
```

### 2. Provide Sensible Defaults

Users should get good behavior without configuration:

```python
@classmethod
def merge_preferences(cls) -> dict:
    return {
        "indent": {
            "default": 2,  # Good default
            ...
        }
    }
```

### 3. Validate Settings

Use `_validate_settings()` to warn about typos:

```python
@classmethod
def merge(cls, ..., **settings):
    cls._validate_settings(settings)  # Warns about unknown settings
    ...
```

### 4. Handle Errors Gracefully

```python
@classmethod
def merge(cls, base: str, new: str, ...) -> str:
    try:
        # Your merge logic
        ...
    except Exception as e:
        output.warning(f"Merge failed: {e}, using copy strategy")
        return new  # Fallback
```

### 5. Document Preferences Well

```python
"indent": {
    "type": "int",
    "default": 2,
    "description": "Number of spaces for indentation (not tabs)",
    "min": 0,
    "max": 8,
}
```

---

## Registration

Mergers are **auto-discovered** if placed in `agent_manager/plugins/mergers/`. You can also manually register them:

### In Agent Plugin

```python
class Agent(AbstractAgent):
    def register_mergers(self):
        from .my_merger import MyMerger

        # By extension
        self.merger_registry.register_extension(".myext", MyMerger)

        # By exact filename
        self.merger_registry.register_filename("special.json", MyMerger)

        # Set default fallback
        self.merger_registry.set_default_merger(MyMerger)
```

### Priority

1. **Exact filename match** (highest priority)
2. **Extension match**
3. **Default fallback** (CopyMerger)

---

## See Also

- [Architecture Overview](ARCHITECTURE.md) - System design
- [Merge Strategies](STRATEGIES.md) - Strategy pattern details
- [Examples](../mergers/) - Built-in merger implementations
- [Custom Agents](CUSTOM_AGENTS.md) - Using custom mergers in agents

