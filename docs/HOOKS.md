# Hook System

This guide explains Agent Manager's hook system for custom pre/post-merge file processing.

---

## Table of Contents

1. [Overview](#overview)
2. [Hook Types](#hook-types)
3. [Hook Signature](#hook-signature)
4. [Registering Hooks](#registering-hooks)
5. [Pattern Matching](#pattern-matching)
6. [Common Use Cases](#common-use-cases)
7. [Best Practices](#best-practices)

---

## Overview

**Hooks** are functions that run before or after file merging, allowing agents to:
- Validate file content
- Transform/normalize data
- Add metadata
- Perform side effects (logging, notifications, etc.)

### Hook Flow

```
For each file in hierarchy:

1. Read file content
   ↓
2. **PRE-MERGE HOOK** (if registered)
   ↓
3. Merge with existing content
   ↓
4. Store merged result

After all files merged:

5. **POST-MERGE HOOK** (if registered)
   ↓
6. Write to agent directory
```

---

## Hook Types

### Pre-Merge Hooks

Run **before** content is merged with existing data.

**When to use:**
- Validate file format
- Clean up/normalize content
- Transform data before merging
- Reject invalid content

**Example:**

```python
def register_hooks(self):
    self.pre_merge_hooks["*.json"] = self._validate_json
```

### Post-Merge Hooks

Run **after** all hierarchy levels are merged.

**When to use:**
- Add metadata headers
- Final validation
- Generate derived files
- Side effects (logging, notifications)

**Example:**

```python
def register_hooks(self):
    self.post_merge_hooks["*"] = self._add_header
```

---

## Hook Signature

### Pre-Merge Hook

```python
def hook_function(
    self,
    content: str,
    entry: dict,
    file_path: Path
) -> str:
    """Pre-merge hook.

    Args:
        content: Raw file content from this hierarchy level
        entry: Hierarchy entry dict:
            {
                "name": "organization",
                "url": "https://...",
                "repo_type": "git",
                "repo": <AbstractRepo instance>
            }
        file_path: Path to the file in the repo

    Returns:
        Modified content (or original if no changes)
    """
    # Your processing here
    return modified_content
```

### Post-Merge Hook

```python
def hook_function(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Post-merge hook.

    Args:
        content: Fully merged content from all hierarchy levels
        entry: Dict with name="merged" (not a real hierarchy entry)
        file_path: Path where file will be written
        sources: List of hierarchy levels that contributed:
            ["organization", "team", "personal"]

    Returns:
        Modified content (or original if no changes)
    """
    # Your processing here
    return modified_content
```

---

## Registering Hooks

Hooks are registered in your agent's `register_hooks()` method:

```python
from agent_manager.plugins.agents import AbstractAgent

class Agent(AbstractAgent):
    def register_hooks(self) -> None:
        """Register custom hooks."""
        # Pre-merge hooks
        self.pre_merge_hooks["*.json"] = self._validate_json
        self.pre_merge_hooks["*.yaml"] = self._clean_yaml
        self.pre_merge_hooks[".cursorrules"] = self._validate_cursorrules

        # Post-merge hooks
        self.post_merge_hooks["*"] = self._add_header
        self.post_merge_hooks["*.md"] = self._add_toc
```

---

## Pattern Matching

Hooks use **glob-style patterns** to match filenames:

| Pattern | Matches | Examples |
|---------|---------|----------|
| `*` | All files | `config.json`, `.cursorrules`, `README.md` |
| `*.json` | All `.json` files | `config.json`, `mcp.json` |
| `*.md` | All markdown files | `README.md`, `NOTES.md` |
| `.cursorrules*` | `.cursorrules` with any suffix | `.cursorrules`, `.cursorrules.bak` |
| `mcp.json` | Exact filename | `mcp.json` only |
| `config.*` | `config` with any extension | `config.json`, `config.yaml`, `config.toml` |

### Specificity

If multiple patterns match, the **most specific** one wins:

```python
self.pre_merge_hooks["*"] = self._generic_hook
self.pre_merge_hooks["*.json"] = self._json_hook
self.pre_merge_hooks["mcp.json"] = self._mcp_specific_hook

# For mcp.json:
#   *.json is more specific than *
#   mcp.json is more specific than *.json
#   → _mcp_specific_hook runs
```

---

## Common Use Cases

### 1. Validation

**Pre-Merge: Validate JSON**

```python
def register_hooks(self):
    self.pre_merge_hooks["*.json"] = self._validate_json

def _validate_json(self, content: str, entry: dict, file_path: Path) -> str:
    """Validate JSON before merging."""
    import json
    from agent_manager import output

    try:
        data = json.loads(content)

        # Check required fields
        if "version" not in data:
            output.warning(f"Missing 'version' in {file_path} from '{entry['name']}'")

        # Check types
        if not isinstance(data.get("settings", {}), dict):
            output.error(f"Invalid 'settings' in {file_path}")
            raise ValueError("settings must be a dict")

        return content
    except json.JSONDecodeError as e:
        output.error(f"Invalid JSON in {file_path} from '{entry['name']}': {e}")
        raise  # Stop merge for this file
```

### 2. Cleanup/Normalization

**Pre-Merge: Normalize Whitespace**

```python
def register_hooks(self):
    self.pre_merge_hooks["*.md"] = self._clean_markdown

def _clean_markdown(self, content: str, entry: dict, file_path: Path) -> str:
    """Clean up markdown files."""
    # Remove trailing whitespace
    lines = [line.rstrip() for line in content.splitlines()]

    # Ensure single newline at EOF
    result = "\n".join(lines)
    if not result.endswith("\n"):
        result += "\n"

    return result
```

### 3. Transformation

**Pre-Merge: Expand Variables**

```python
def register_hooks(self):
    self.pre_merge_hooks["*.yaml"] = self._expand_variables

def _expand_variables(self, content: str, entry: dict, file_path: Path) -> str:
    """Expand environment variables in YAML."""
    import os
    import re

    def replace_var(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    # Replace ${VAR_NAME} with environment variable
    return re.sub(r'\$\{(\w+)\}', replace_var, content)
```

### 4. Adding Metadata

**Post-Merge: Add Header**

```python
from datetime import datetime

def register_hooks(self):
    self.post_merge_hooks["*"] = self._add_header

def _add_header(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Add metadata header to all merged files."""
    header = f"""# Auto-generated by agent-manager
# Sources: {', '.join(sources)}
# Generated: {datetime.now().isoformat()}
#
# DO NOT EDIT THIS FILE MANUALLY
# Changes will be overwritten on next merge

"""
    return header + content
```

### 5. Generate TOC

**Post-Merge: Add Table of Contents to Markdown**

```python
def register_hooks(self):
    self.post_merge_hooks["*.md"] = self._add_toc

def _add_toc(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Add table of contents to markdown files."""
    import re

    # Extract headings
    headings = []
    for line in content.splitlines():
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2)
            anchor = title.lower().replace(' ', '-').replace('[^a-z0-9-]', '')
            headings.append((level, title, anchor))

    if not headings:
        return content

    # Generate TOC
    toc = ["## Table of Contents\n"]
    for level, title, anchor in headings:
        if level == 1:  # Skip H1 (usually title)
            continue
        indent = "  " * (level - 2)
        toc.append(f"{indent}- [{title}](#{anchor})")

    toc_str = "\n".join(toc) + "\n\n"

    # Insert after first H1 or at beginning
    h1_match = re.search(r'^# .+$', content, re.MULTILINE)
    if h1_match:
        insert_pos = h1_match.end() + 1
        return content[:insert_pos] + toc_str + content[insert_pos:]
    else:
        return toc_str + content
```

### 6. Conditional Logic

**Pre-Merge: Skip Files from Specific Sources**

```python
def register_hooks(self):
    self.pre_merge_hooks["secrets.json"] = self._filter_secrets

def _filter_secrets(self, content: str, entry: dict, file_path: Path) -> str:
    """Don't merge secrets from organization level."""
    from agent_manager import output

    if entry["name"] == "organization":
        output.warning(f"Skipping secrets.json from organization level")
        return ""  # Return empty content (effectively skips merge)

    return content
```

### 7. Side Effects

**Post-Merge: Log Merge Activity**

```python
def register_hooks(self):
    self.post_merge_hooks["*"] = self._log_merge

def _log_merge(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Log merge activity."""
    import logging

    logger = logging.getLogger("agent_manager.merges")
    logger.info(
        f"Merged {file_path.name} from {len(sources)} sources: {', '.join(sources)}"
    )

    return content  # No modification
```

### 8. Generate Derived Files

**Post-Merge: Generate Index**

```python
def register_hooks(self):
    self.post_merge_hooks["*"] = self._generate_index

def _generate_index(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Track all merged files for index generation."""
    if not hasattr(self, '_merged_files'):
        self._merged_files = []

    self._merged_files.append({
        "filename": file_path.name,
        "sources": sources,
        "size": len(content)
    })

    # On last file, generate index
    # (You'd need additional logic to detect "last file")

    return content
```

---

## Best Practices

### 1. Return Content (Don't Modify in Place)

```python
# Good
def hook(self, content: str, ...) -> str:
    modified = content.upper()
    return modified

# Bad (doesn't return)
def hook(self, content: str, ...) -> str:
    content = content.upper()  # Modifies local variable only!
    # Missing return!
```

### 2. Use output Module for Feedback

```python
from agent_manager import output

def hook(self, content: str, entry: dict, file_path: Path) -> str:
    output.info(f"Processing {file_path.name}...")
    output.debug(f"Content length: {len(content)}")
    output.warning("Missing required field")
    output.error("Validation failed!")

    return content
```

### 3. Handle Errors Gracefully

```python
def hook(self, content: str, entry: dict, file_path: Path) -> str:
    try:
        # Processing that might fail
        ...
    except Exception as e:
        output.error(f"Hook failed for {file_path}: {e}")
        # Return original content (don't break merge)
        return content
```

### 4. Be Specific with Patterns

```python
# Good
self.pre_merge_hooks["*.json"] = self._validate_json

# Too broad (matches everything)
self.pre_merge_hooks["*"] = self._validate_json
```

### 5. Document Your Hooks

```python
def _validate_json(self, content: str, entry: dict, file_path: Path) -> str:
    """Validate JSON files before merging.

    Checks for:
    - Valid JSON syntax
    - Required 'version' field
    - Proper 'settings' dict structure

    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    ...
```

### 6. Keep Hooks Focused

One hook = one responsibility:

```python
# Good
self.pre_merge_hooks["*.json"] = self._validate_json
self.pre_merge_hooks["*.json"] = self._normalize_json  # Separate concerns

# Bad (doing too much)
def _process_json(self, ...):
    self._validate(...)
    self._normalize(...)
    self._transform(...)
    self._log(...)
```

### 7. Test Hooks

```python
def test_validate_json_hook():
    agent = MyAgent()

    # Valid JSON
    result = agent._validate_json(
        '{"version": "1.0"}',
        {"name": "test"},
        Path("config.json")
    )
    assert result == '{"version": "1.0"}'

    # Invalid JSON
    with pytest.raises(ValueError):
        agent._validate_json(
            '{invalid}',
            {"name": "test"},
            Path("config.json")
        )
```

---

## Advanced Examples

### Conditional Hook (Per-Source)

```python
def _conditional_cleanup(self, content: str, entry: dict, file_path: Path) -> str:
    """Apply different cleanup based on source."""
    source_name = entry["name"]

    if source_name == "organization":
        # Stricter validation for org configs
        if not self._validate_strict(content):
            raise ValueError("Organization config must pass strict validation")

    elif source_name == "personal":
        # More lenient for personal configs
        content = self._apply_defaults(content)

    return content
```

### Chaining Multiple Hooks

```python
def register_hooks(self):
    # Hook 1: Validate
    self.pre_merge_hooks["*.json"] = self._validate_then_normalize

def _validate_then_normalize(self, content: str, entry: dict, file_path: Path) -> str:
    """Validate then normalize (chained processing)."""
    # Step 1: Validate
    content = self._validate_json(content, entry, file_path)

    # Step 2: Normalize
    content = self._normalize_json(content, entry, file_path)

    return content
```

### Hook with State

```python
def __init__(self):
    super().__init__()
    self._merge_stats = {"files": 0, "sources": {}}

def register_hooks(self):
    self.post_merge_hooks["*"] = self._track_stats

def _track_stats(
    self,
    content: str,
    entry: dict,
    file_path: Path,
    sources: list[str]
) -> str:
    """Track merge statistics."""
    self._merge_stats["files"] += 1

    for source in sources:
        self._merge_stats["sources"][source] = \
            self._merge_stats["sources"].get(source, 0) + 1

    return content

def update(self, config: dict):
    super().update(config)

    # Print stats after merge
    output.info(f"Merged {self._merge_stats['files']} files")
    output.info(f"Sources: {self._merge_stats['sources']}")
```

---

## Troubleshooting

### Hook Not Running

**Check:**
1. Pattern matches filename (`*.json` vs `*.js`)
2. Hook is registered in `register_hooks()`
3. Hook function signature is correct
4. Hook returns content (doesn't just modify and forget to return)

### Hook Runs But Has No Effect

**Check:**
1. Hook returns modified content
2. Hook is a method of the agent class (`def hook(self, ...):`)
3. No exception is silently swallowed

### Hook Breaks Merge

**Check:**
1. Hook doesn't raise unhandled exceptions
2. Hook returns valid content for the merger
3. Hook doesn't return empty string unintentionally

---

## See Also

- [Creating Custom Agents](CUSTOM_AGENTS.md) - Using hooks in agents
- [Architecture Overview](ARCHITECTURE.md) - System design
- [Examples](../../ai_agent_claude/claude.py) - Real-world hook usage

