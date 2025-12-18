# Merge Strategies

This document explains how to use and customize merge strategies for dictionary-based configuration files (JSON, YAML, etc.).

## Overview

The `DictMerger` base class provides pluggable merge strategies that define how different types of values should be merged:
- **Dictionaries**: Deep merge vs. replace
- **Lists**: Extend vs. replace
- **Primitive values**: Always replaced by default

## Built-in Strategies

### 1. MergeStrategy (Default)

The default strategy for JsonMerger and YamlMerger:

```python
from agent_manager.plugins.mergers import MergeStrategy

# Behavior:
# - Dicts: Deep merge (recursively merge nested dicts)
# - Lists: Replace (new list overwrites old)
# - Values: Replace (new value overwrites old)
```

**Example:**
```python
# Base JSON
{"name": "App", "features": ["auth", "api"], "config": {"port": 8080}}

# New JSON
{"version": "2.0", "features": ["ui"], "config": {"host": "localhost"}}

# Result (Deep merge dicts, replace lists):
{
    "name": "App",
    "version": "2.0",
    "features": ["ui"],  # Replaced
    "config": {"port": 8080, "host": "localhost"}  # Deep merged
}
```

---

### 2. ExtendListStrategy

Extends lists instead of replacing them:

```python
from agent_manager.plugins.mergers import ExtendListStrategy

# Behavior:
# - Dicts: Deep merge (same as MergeStrategy)
# - Lists: Extend (append new items, deduplicate)
# - Values: Replace
```

**Example:**
```python
# Base JSON
{"name": "App", "features": ["auth", "api"]}

# New JSON
{"features": ["ui", "auth"]}  # "auth" is duplicate

# Result (Extend and deduplicate):
{
    "name": "App",
    "features": ["auth", "api", "ui"]  # Extended, no duplicate "auth"
}
```

---

### 3. ReplaceStrategy

Replaces everything (no deep merging):

```python
from agent_manager.plugins.mergers import ReplaceStrategy

# Behavior:
# - Dicts: Replace (new dict overwrites old)
# - Lists: Replace
# - Values: Replace
```

**Example:**
```python
# Base JSON
{"name": "App", "features": ["auth"], "config": {"port": 8080}}

# New JSON
{"name": "NewApp", "config": {"host": "localhost"}}

# Result (Complete replacement at root level):
{
    "name": "NewApp",
    "config": {"host": "localhost"}  # "port" is lost
}
```

---

## Using Custom Strategies in Agent Plugins

Agents can override the `get_merge_strategy()` method to customize merge behavior:

### Example: Claude Agent with ExtendListStrategy

```python
from agent_manager.plugins.agents import AbstractAgent
from agent_manager.plugins.mergers import JsonMerger, ExtendListStrategy


class CustomJsonMerger(JsonMerger):
    """Custom JSON merger that extends lists instead of replacing them."""

    @classmethod
    def get_merge_strategy(cls) -> type[MergeStrategy]:
        return ExtendListStrategy


class Agent(AbstractAgent):
    """Claude agent with custom merge behavior."""

    def register_mergers(self) -> None:
        """Register custom mergers."""
        # Use custom JSON merger for all JSON files
        self.merger_registry.register_extension(".json", CustomJsonMerger)
```

**Use case:** Your MCP configuration has plugins defined as a list, and you want to extend the list from org → team → personal instead of replacing it.

---

### Example: Per-File Merge Strategies

You can also use different strategies for different files:

```python
class Agent(AbstractAgent):
    def register_mergers(self) -> None:
        # Use ExtendListStrategy for plugins config
        class PluginsJsonMerger(JsonMerger):
            @classmethod
            def get_merge_strategy(cls):
                return ExtendListStrategy

        # Use ReplaceStrategy for user-specific settings
        class SettingsJsonMerger(JsonMerger):
            @classmethod
            def get_merge_strategy(cls):
                return ReplaceStrategy

        # Register by filename
        self.merger_registry.register_filename("plugins.json", PluginsJsonMerger)
        self.merger_registry.register_filename("settings.json", SettingsJsonMerger)

        # Default JSON merger for all other JSON files
        self.merger_registry.register_extension(".json", JsonMerger)
```

---

## Creating Custom Strategies

You can create your own merge strategies by subclassing `MergeStrategy`:

```python
from agent_manager.plugins.mergers import MergeStrategy


class SmartListStrategy(MergeStrategy):
    """Merge strategy with intelligent list handling."""

    @staticmethod
    def merge_list(base: list, new: list, path: str = "") -> list:
        """Merge lists based on their content type."""
        if not base:
            return new
        if not new:
            return base

        # If lists contain dicts with 'id' fields, merge by ID
        if isinstance(base[0], dict) and "id" in base[0]:
            merged = {item["id"]: item for item in base}
            for item in new:
                merged[item["id"]] = item
            return list(merged.values())

        # Otherwise, extend and deduplicate
        result = base.copy()
        for item in new:
            if item not in result:
                result.append(item)
        return result
```

Then use it in your custom merger:

```python
class SmartJsonMerger(JsonMerger):
    @classmethod
    def get_merge_strategy(cls):
        return SmartListStrategy
```

---

## Summary

| Strategy | Dicts | Lists | Use Case |
|----------|-------|-------|----------|
| `MergeStrategy` | Deep merge | Replace | Default (most configs) |
| `ExtendListStrategy` | Deep merge | Extend + dedupe | Plugin/feature lists |
| `ReplaceStrategy` | Replace | Replace | User-specific overrides |
| Custom | ... | ... | Domain-specific logic |

The pluggable strategy system lets you fine-tune merge behavior per file type, per filename, or per agent!

