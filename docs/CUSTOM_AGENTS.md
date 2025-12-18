# Creating Custom Agents

This guide shows you how to create your own agent plugin for Agent Manager.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Agent Structure](#agent-structure)
4. [Implementing AbstractAgent](#implementing-abstractagent)
5. [Hooks System](#hooks-system)
6. [Custom Mergers](#custom-mergers)
7. [Testing Your Agent](#testing-your-agent)
8. [Publishing](#publishing)

---

## Overview

An **agent plugin** is a Python package that:
1. Has a name starting with `ai_agent_`
2. Contains a `Agent` class that inherits from `AbstractAgent`
3. Is installable via `pip`

Agent Manager **automatically discovers** all installed `ai_agent_*` packages.

---

## Quick Start

### Step 1: Create Package Structure

```bash
mkdir ai_agent_myplugin
cd ai_agent_myplugin

# Create package files
touch __init__.py
touch myplugin.py
touch pyproject.toml
touch README.md
```

Your structure:

```
ai_agent_myplugin/
├── __init__.py
├── myplugin.py        # Main agent implementation
├── pyproject.toml     # Package metadata
└── README.md          # Documentation
```

### Step 2: Create `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai_agent_myplugin"
version = "0.0.1"
description = "My custom AI agent plugin for agent-manager"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "agent-manager",
    # Add your dependencies here
]

[project.optional-dependencies]
dev = [
    "ruff",
    "pytest",
]
```

### Step 3: Implement Your Agent

`myplugin.py`:

```python
"""My custom AI agent plugin."""

from pathlib import Path
from agent_manager.plugins.agents import AbstractAgent


class Agent(AbstractAgent):
    """Agent for managing my AI tool configuration."""

    # Set your agent's config directory
    agent_directory: Path = Path.home() / ".myplugin"

    def register_hooks(self) -> None:
        """Register custom hooks for file processing."""
        # Optional: Add pre/post-merge hooks
        pass

    def register_mergers(self) -> None:
        """Register custom mergers."""
        # Optional: Add custom merger classes
        pass

    def update(self, config: dict) -> None:
        """Update configuration from hierarchical repositories.

        Args:
            config: Configuration data with hierarchy and repo objects
        """
        # Initialize your agent environment (if needed)
        self._initialize()

        # Use the generic merge system
        self.merge_configurations(config)

    def _initialize(self) -> None:
        """Initialize agent environment."""
        # Create agent directory if it doesn't exist
        self.agent_directory.mkdir(parents=True, exist_ok=True)

        # Add any additional initialization here
        # E.g., create default files, run setup commands, etc.
```

### Step 4: Export Your Agent

`__init__.py`:

```python
"""My custom AI agent plugin."""

from .myplugin import Agent

__all__ = ["Agent"]
```

### Step 5: Install and Test

```bash
# Install in development mode
pip install -e .

# Verify agent-manager can find it
agent-manager run --agent myplugin
```

---

## Agent Structure

### Required Components

1. **Package name**: Must start with `ai_agent_`
2. **Agent class**: Must be named `Agent` and inherit from `AbstractAgent`
3. **agent_directory**: Class attribute defining where configs are written
4. **update(config)**: Method called by agent-manager to merge configs

### Optional Components

1. **register_hooks()**: Register pre/post-merge hooks
2. **register_mergers()**: Register custom merger classes
3. **get_additional_excludes()**: Add files/dirs to exclude from discovery
4. **_initialize()**: Setup agent environment

---

## Implementing AbstractAgent

### Required Methods

#### update(config: dict)

Main entry point called by agent-manager.

```python
def update(self, config: dict) -> None:
    """Update configuration from hierarchical repositories.

    Args:
        config: Configuration data structure:
            {
                "hierarchy": [
                    {
                        "name": "org",
                        "url": "https://...",
                        "repo_type": "git",
                        "repo": <GitRepo instance>
                    },
                    ...
                ],
                "mergers": {
                    "JsonMerger": {"indent": 2},
                    ...
                }
            }
    """
    # 1. Initialize your environment
    self._initialize()

    # 2. Use generic merge (handles everything for you)
    self.merge_configurations(config)

    # 3. (Optional) Any post-processing
    self._post_process()
```

### Optional Methods

#### register_hooks()

Register functions to run before/after merging specific files.

```python
def register_hooks(self) -> None:
    """Register custom hooks."""
    # Pre-merge: Run before merging
    self.pre_merge_hooks["*.json"] = self._validate_json
    self.pre_merge_hooks["config.yaml"] = self._clean_yaml

    # Post-merge: Run after all sources merged
    self.post_merge_hooks["*"] = self._add_header
```

See [Hooks System](#hooks-system) for details.

#### register_mergers()

Register custom merger classes.

```python
def register_mergers(self) -> None:
    """Register custom mergers."""
    from .my_custom_merger import MyCustomMerger

    # Register for specific filename
    self.merger_registry.register_filename("my_config.json", MyCustomMerger)

    # Or for file extension
    self.merger_registry.register_extension(".myext", MyCustomMerger)
```

See [Custom Mergers](#custom-mergers) for details.

#### get_additional_excludes()

Add files/directories to exclude from discovery.

```python
def get_additional_excludes(self) -> list[str]:
    """Add agent-specific exclude patterns."""
    return [
        "tests/",
        "*.test.json",
        ".myagent_cache",
    ]
```

These are added to `BASE_EXCLUDE_PATTERNS`:

```python
BASE_EXCLUDE_PATTERNS = [
    ".git",
    ".gitignore",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    "README.md",
    "LICENSE",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    ".ruff_cache",
    "*.egg-info",
]
```

---

## Hooks System

Hooks let you run custom logic before/after merging specific files.

### Hook Signature

```python
def hook_function(
    content: str,
    entry: dict,
    file_path: Path,
    **kwargs
) -> str:
    """Hook function.

    Args:
        content: File content (for pre-merge) or merged content (for post-merge)
        entry: Hierarchy entry dict {"name": "...", "url": "...", ...}
        file_path: Path to the file
        **kwargs: Additional context (e.g., "sources" for post-merge)

    Returns:
        Modified content
    """
    # Your processing here
    return content
```

### Pre-Merge Hooks

Run **before** content is merged. Useful for:
- Validation
- Cleanup/normalization
- Transformation

**Example:**

```python
def register_hooks(self) -> None:
    """Register pre-merge hooks."""
    self.pre_merge_hooks["*.json"] = self._validate_json
    self.pre_merge_hooks["config.yaml"] = self._ensure_required_fields

def _validate_json(self, content: str, entry: dict, file_path: Path) -> str:
    """Validate JSON before merging."""
    import json
    try:
        data = json.loads(content)
        # Perform validation
        if "required_field" not in data:
            output.warning(f"Missing required_field in {file_path}")
        return content
    except json.JSONDecodeError as e:
        output.error(f"Invalid JSON in {file_path}: {e}")
        raise

def _ensure_required_fields(self, content: str, entry: dict, file_path: Path) -> str:
    """Add required fields if missing."""
    import yaml
    data = yaml.safe_load(content)
    if "version" not in data:
        data["version"] = "1.0"
    return yaml.dump(data)
```

### Post-Merge Hooks

Run **after** all sources are merged. Useful for:
- Adding metadata/headers
- Final validation
- Side effects (logging, notifications, etc.)

**Example:**

```python
def register_hooks(self) -> None:
    """Register post-merge hooks."""
    self.post_merge_hooks["*"] = self._add_metadata
    self.post_merge_hooks["*.md"] = self._add_toc

def _add_metadata(self, content: str, entry: dict, file_path: Path, sources: list[str]) -> str:
    """Add metadata header to all merged files."""
    header = f"""# Auto-generated by agent-manager
# Sources: {', '.join(sources)}
# Generated: {datetime.now().isoformat()}

"""
    return header + content

def _add_toc(self, content: str, entry: dict, file_path: Path, **kwargs) -> str:
    """Add table of contents to markdown files."""
    # Parse headings and generate TOC
    headings = self._extract_headings(content)
    toc = self._generate_toc(headings)
    return toc + "\n\n" + content
```

### Pattern Matching

Hooks use glob-style patterns:

```python
self.pre_merge_hooks["*"] = hook  # All files
self.pre_merge_hooks["*.json"] = hook  # All JSON files
self.pre_merge_hooks["config.*"] = hook  # config.json, config.yaml, etc.
self.pre_merge_hooks["mcp.json"] = hook  # Exact filename
```

---

## Custom Mergers

If your agent needs special merging logic for certain file types, you can register custom mergers.

### Example: Custom Config Merger

```python
# my_custom_merger.py
from agent_manager.plugins.mergers import AbstractMerger

class MyConfigMerger(AbstractMerger):
    """Custom merger for .myconfig files."""

    FILE_EXTENSIONS = [".myconfig"]

    @classmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Merge .myconfig files with special logic."""
        # Your custom merge logic here
        return merged_content

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define configurable preferences."""
        return {
            "my_setting": {
                "type": "int",
                "default": 10,
                "description": "My custom setting",
            }
        }
```

Register in your agent:

```python
def register_mergers(self) -> None:
    """Register custom mergers."""
    from .my_custom_merger import MyConfigMerger

    self.merger_registry.register_extension(".myconfig", MyConfigMerger)
```

See [Creating Custom Mergers](CUSTOM_MERGERS.md) for full details.

---

## Testing Your Agent

### Unit Tests

```python
# test_agent.py
import pytest
from pathlib import Path
from ai_agent_myplugin import Agent

def test_agent_initialization():
    """Test agent initializes correctly."""
    agent = Agent()
    assert agent.agent_directory == Path.home() / ".myplugin"

def test_agent_merge(tmp_path):
    """Test agent merges configs correctly."""
    agent = Agent()
    agent.agent_directory = tmp_path / ".myplugin"

    config = {
        "hierarchy": [
            # ... mock hierarchy data ...
        ],
        "mergers": {}
    }

    agent.update(config)

    # Assert merged files exist
    assert (agent.agent_directory / "config.json").exists()
```

### Integration Tests

```bash
# Create test repos
mkdir /tmp/test-org
echo '{"key": "org"}' > /tmp/test-org/config.json

mkdir /tmp/test-personal
echo '{"key": "personal"}' > /tmp/test-personal/config.json

# Create test config
cat > /tmp/test-config.yaml << EOF
hierarchy:
  - name: org
    url: file:///tmp/test-org
    repo_type: local
  - name: personal
    url: file:///tmp/test-personal
    repo_type: local
EOF

# Run agent
AGENT_MANAGER_CONFIG_DIR=/tmp agent-manager run --agent myplugin

# Verify results
cat ~/.myplugin/config.json
```

---

## Real-World Example: Claude Agent

See `ai_agent_claude/claude.py` for a complete example:

```python
class Agent(AbstractAgent):
    """Agent for managing Claude/Cursor configuration."""

    agent_directory: Path = Path.home() / ".claude"

    def register_hooks(self) -> None:
        """Register Claude-specific hooks."""
        # Pre-merge validation
        self.pre_merge_hooks["*.md"] = self._clean_markdown
        self.pre_merge_hooks[".cursorrules*"] = self._validate_cursorrules

        # Post-merge metadata
        self.post_merge_hooks["*"] = self._add_metadata_header

    def register_mergers(self) -> None:
        """No custom mergers needed for Claude."""
        pass

    def update(self, config: dict) -> None:
        """Update Claude configuration."""
        self._initialize()
        self.merge_configurations(config)

    def _initialize(self) -> None:
        """Initialize Claude environment."""
        # Try SDK initialization
        try:
            from claude_agent_sdk import query
            query(prompt="/init")
        except Exception:
            # Fallback to manual setup
            self.agent_directory.mkdir(parents=True, exist_ok=True)

    def _clean_markdown(self, content: str, entry: dict, file_path: Path) -> str:
        """Clean up markdown files."""
        # Remove trailing whitespace
        lines = [line.rstrip() for line in content.splitlines()]
        return "\n".join(lines) + "\n"

    def _validate_cursorrules(self, content: str, entry: dict, file_path: Path) -> str:
        """Validate .cursorrules files."""
        if not content.strip():
            output.warning(f"Empty .cursorrules file from '{entry['name']}'")
        return content

    def _add_metadata_header(self, content: str, entry: dict, file_path: Path, sources: list[str]) -> str:
        """Add metadata header to merged files."""
        header = (
            f"# Configuration from: {', '.join(sources)}\n"
            f"# Generated: {datetime.now().isoformat()}\n\n"
        )
        return header + content
```

---

## Publishing

### To PyPI

```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### As Git Repository

```bash
# Users can install directly from Git
pip install git+https://github.com/yourname/ai_agent_myplugin.git
```

---

## Best Practices

### 1. Keep It Simple

Start with the basics:

```python
class Agent(AbstractAgent):
    agent_directory = Path.home() / ".myagent"

    def register_hooks(self):
        pass

    def register_mergers(self):
        pass

    def update(self, config):
        self._initialize()
        self.merge_configurations(config)

    def _initialize(self):
        self.agent_directory.mkdir(parents=True, exist_ok=True)
```

Add complexity only as needed.

### 2. Document Your Agent

Add a comprehensive README explaining:
- What AI tool it's for
- What config files it manages
- Any special setup required
- Examples

### 3. Use Type Hints

```python
def update(self, config: dict) -> None:
    ...
```

### 4. Handle Errors Gracefully

```python
try:
    # Something that might fail
    ...
except Exception as e:
    output.error(f"Failed to initialize: {e}")
    # Fall back to safe default
    self.agent_directory.mkdir(parents=True, exist_ok=True)
```

### 5. Respect BASE_EXCLUDE_PATTERNS

Don't discover files that shouldn't be merged (`.git`, `README.md`, etc.).

### 6. Test Thoroughly

Write tests for:
- Initialization
- Hook behavior
- Custom mergers (if any)
- Error handling

---

## Troubleshooting

### Agent Not Discovered

**Check:**
1. Package name starts with `ai_agent_`
2. Package is installed (`pip list | grep ai_agent`)
3. Has `Agent` class that inherits from `AbstractAgent`

### Import Errors

**Check:**
1. `agent-manager` is installed
2. All dependencies are in `pyproject.toml`
3. No circular imports

### Hooks Not Running

**Check:**
1. Hooks are registered in `register_hooks()`
2. Pattern matches filename (use `*` for all files)
3. Hook function signature is correct

---

## See Also

- [Architecture Overview](ARCHITECTURE.md) - System design
- [Hooks System](HOOKS.md) - Detailed hook documentation
- [Custom Mergers](CUSTOM_MERGERS.md) - Creating custom merge strategies
- [Examples](https://github.com/john-westcott-iv/agent-manager/tree/main/ai_agent_claude) - Claude agent source code

