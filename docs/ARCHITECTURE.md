# Architecture Overview

This document explains the design and architecture of Agent Manager's pluggable system.

---

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Core Components](#core-components)
3. [Pluggable Systems](#pluggable-systems)
4. [Data Flow](#data-flow)
5. [Design Principles](#design-principles)
6. [Extension Points](#extension-points)

---

## High-Level Overview

Agent Manager is built around a **pluggable architecture** where almost every component can be extended or replaced:

```
┌─────────────────────────────────────────────────────────┐
│                     agent-manager                       │
│                     (Core System)                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Config     │  │  Repository  │  │    Merger    │ │
│  │  Management  │  │   Backends   │  │    System    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Agent Plugin System                    │  │
│  │        (Auto-discovers ai_agent_* packages)      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
           │                    │                 │
           ▼                    ▼                 ▼
   ┌──────────────┐    ┌──────────────┐  ┌──────────────┐
   │ ai_agent_    │    │ ai_agent_    │  │ ai_agent_    │
   │   claude     │    │   cursor     │  │   chatgpt    │
   └──────────────┘    └──────────────┘  └──────────────┘
      (Plugin)            (Plugin)          (Plugin)
```

### Key Concepts

1. **Hierarchy**: Ordered list of configuration sources (org → team → personal)
2. **Repositories**: Pluggable backends for storing configs (Git, local, S3, etc.)
3. **Mergers**: Type-aware strategies for combining configs (JSON, YAML, Markdown, etc.)
4. **Agents**: Pluggable AI tool integrations (Claude, Cursor, ChatGPT, etc.)
5. **Hooks**: Pre/post-processing hooks for custom logic

---

## Core Components

### 1. Configuration Management (`agent_manager/config/`)

**Responsibilities:**
- Load/save config from `~/.agent-manager/config.yaml`
- Interactive config initialization
- Validation
- CLI commands for config manipulation

**Key Classes:**
- `Config`: Main configuration manager
- `ConfigError`: Custom exception for validation errors

**Key Data Structures:**

```python
# TypedDict for hierarchy entries
class HierarchyEntry(TypedDict):
    name: str
    url: str
    repo_type: str
    repo: AbstractRepo

# TypedDict for complete config
class ConfigData(TypedDict):
    hierarchy: list[HierarchyEntry]
    mergers: dict[str, dict[str, Any]]
```

### 2. Core Infrastructure (`agent_manager/core/`)

**Responsibilities:**
- Plugin infrastructure management
- Registry systems (MergerRegistry)
- Discovery and factory functions
- System-level operations (update_repositories)

**Key Classes:**
- `MergerRegistry`: Central registry for merger plugins
- Discovery functions: `discover_repo_types()`, `discover_merger_classes()`
- Factory functions: `create_repo()`, `create_default_merger_registry()`
- System operations: `update_repositories()`

### 3. Repository System (`agent_manager/plugins/repos/`)

**Responsibilities:**
- Fetch/update configuration sources
- Abstract away storage backends
- Auto-discovery of repository types

**Architecture:**

```
AbstractRepo (ABC)
├── can_handle_url(url) -> bool
├── validate_url(url) -> tuple[bool, str]
├── get_path() -> Path
├── needs_update() -> bool
├── update() -> None
└── get_display_url() -> str

GitRepo (AbstractRepo)
├── REPO_TYPE = "git"
├── Clones/fetches/pulls from Git
└── Uses GitPython

LocalRepo (AbstractRepo)
├── REPO_TYPE = "local"
└── Resolves file:// paths

[Your Custom Repo] (AbstractRepo)
├── REPO_TYPE = "your_type"
└── Your implementation
```

**Dynamic Discovery:**

```python
# core/repos.py auto-discovers all AbstractRepo subclasses
def discover_repo_types() -> dict[str, type[AbstractRepo]]:
    # Scans agent_manager.plugins.repos for AbstractRepo subclasses
    # Returns map: {"git": GitRepo, "local": LocalRepo, ...}
```

**Factory Pattern:**

```python
# core/repos.py
def create_repo(url: str, repo_type: str) -> AbstractRepo:
    # Returns appropriate repo instance based on type
```

### 4. Merger System (`agent_manager/plugins/mergers/`)

**Responsibilities:**
- Type-aware content merging
- Pluggable merge strategies
- Self-documenting preferences

**Architecture:**

```
AbstractMerger (ABC)
├── FILE_EXTENSIONS: list[str]
├── merge(base, new, source, sources, **settings) -> str
└── merge_preferences() -> dict

DictMerger (AbstractMerger)
├── Abstract base for JSON/YAML
├── Uses pluggable MergeStrategy
├── deserialize(content) -> object
└── serialize(object) -> str

JsonMerger (DictMerger)
├── FILE_EXTENSIONS = [".json"]
├── deserialize() uses json.loads()
└── serialize() uses json.dumps()

YamlMerger (DictMerger)
├── FILE_EXTENSIONS = [".yaml", ".yml"]
├── deserialize() uses yaml.safe_load()
└── serialize() uses yaml.dump()

MarkdownMerger (AbstractMerger)
├── FILE_EXTENSIONS = [".md", ".markdown"]
└── Concatenates with AI context markers

TextMerger (AbstractMerger)
├── FILE_EXTENSIONS = [".txt"]
└── Simple concatenation

CopyMerger (AbstractMerger)
├── FILE_EXTENSIONS = []  (fallback)
└── Last source wins
```

**Merge Strategies:**

```
MergeStrategy
├── merge_dict(base, new) -> dict  (deep merge)
├── merge_list(base, new) -> list  (replace)
└── merge_value(base, new) -> Any  (replace)

ExtendListStrategy (MergeStrategy)
└── merge_list(base, new) -> list  (extend + dedupe)

ReplaceStrategy (MergeStrategy)
├── merge_dict(base, new) -> dict  (replace)
└── No deep merging
```

**Registry System:**

```python
class MergerRegistry:
    def register_filename(filename: str, merger: type[AbstractMerger])
    def register_extension(ext: str, merger: type[AbstractMerger])
    def set_default_merger(merger: type[AbstractMerger])
    def get_merger(file_path: Path) -> type[AbstractMerger]
```

**Priority:**
1. Exact filename match (e.g., `mcp.json`)
2. File extension match (e.g., `.json`)
3. Default fallback (`CopyMerger`)

### 5. Agent System (`agent_manager/plugins/agents/`)

**Responsibilities:**
- Plugin discovery and loading
- Generic file discovery and merging
- Hook system for custom processing

**Architecture:**

```
AbstractAgent (ABC)
├── BASE_EXCLUDE_PATTERNS: list[str]
├── agent_directory: Path
├── __init__():
│   ├── Initializes hook registries
│   ├── Initializes merger registry
│   ├── Calls register_hooks()
│   └── Calls register_mergers()
├── register_hooks() (abstract)
├── register_mergers() (abstract)
├── get_additional_excludes() -> list[str]
├── _discover_files(repo_path) -> list[Path]
├── merge_configurations(config: dict)
└── update(config: dict) (abstract)

Agent (AbstractAgent) - in plugin package
├── agent_directory = Path("~/.claude")
├── register_hooks():
│   ├── Pre-merge: validation, cleanup
│   └── Post-merge: metadata headers
├── register_mergers():
│   └── (optional) Custom mergers
└── update(config):
    ├── Initialize agent environment
    └── Call merge_configurations()
```

**Plugin Discovery:**

```python
# agents/manager.py
class Manager:
    AGENT_PLUGIN_PREFIX = "ai_agent_"
    
    @classmethod
    def discover_agent_plugins() -> dict[str, str]:
        # Scans installed packages for ai_agent_*
        # Returns: {"claude": "ai_agent_claude", ...}
```

### 6. CLI Extensions (`agent_manager/cli_extensions/`)

**Responsibilities:**
- Modular CLI command handlers
- Separate concerns from main entry point
- Easy to extend with new commands

**Key Classes:**
- `AgentCommands`: Handles `run` command and agent plugin discovery
- `MergerCommands`: Handles `mergers` subcommands (list, show, configure)
- `RepoCommands`: Handles `update` command

### 7. Output System (`agent_manager/output/`)

**Responsibilities:**
- Centralized logging with colors and verbosity
- Global singleton accessible everywhere

**Key Functions:**

```python
output.info(message, color=None)      # Normal output
output.debug(message)                  # Debug (verbosity >= 2)
output.success(message)                # Green success
output.warning(message)                # Yellow warning
output.error(message)                  # Red error
```

---

## Directory Structure

Agent Manager's codebase is organized to clearly separate infrastructure, plugins, and extensions:

```
agent_manager/
├── core/                          # Core infrastructure
│   ├── merger_registry.py        # Registry for merger plugins
│   ├── mergers.py                # Merger discovery & factory
│   └── repos.py                  # Repo discovery, factory, & update operations
│
├── plugins/                       # All plugin implementations
│   ├── agents/                   # Agent plugin base classes
│   │   └── agent.py              # AbstractAgent
│   ├── mergers/                  # Merger plugins
│   │   ├── abstract_merger.py   # Base class
│   │   ├── dict_merger.py       # Base for JSON/YAML
│   │   ├── json_merger.py       # JSON merger
│   │   ├── yaml_merger.py       # YAML merger
│   │   ├── markdown_merger.py   # Markdown merger
│   │   ├── text_merger.py       # Text merger
│   │   └── copy_merger.py       # Fallback merger
│   └── repos/                    # Repository plugins
│       ├── abstract_repo.py     # Base class
│       ├── git_repo.py          # Git repository
│       └── local_repo.py        # Local file:// directory
│
├── cli_extensions/                # CLI command handlers
│   ├── agent_commands.py         # AgentCommands (run)
│   ├── merger_commands.py        # MergerCommands (mergers)
│   └── repo_commands.py          # RepoCommands (update)
│
├── config/                        # Configuration management
│   └── config.py                 # Config class
│
├── utils/                         # Pure utility functions
│   └── url.py                    # URL helpers (stateless)
│
├── output/                        # Output system
│   └── output.py                 # Global output manager
│
├── docs/                          # Documentation
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   ├── CONFIGURATION.md
│   └── ...
│
└── tests/                         # Mirrors code structure
    ├── core/
    ├── plugins/
    │   ├── agents/
    │   ├── mergers/
    │   └── repos/
    ├── cli_extensions/
    ├── config/
    └── utils/
```

### Design Philosophy

| Directory | Purpose | Guidelines |
|-----------|---------|------------|
| **`core/`** | Plugin infrastructure & system operations | Registry systems, discovery functions, factories, update operations |
| **`plugins/`** | Plugin implementations | Concrete classes that extend abstract bases (AbstractAgent, AbstractMerger, AbstractRepo) |
| **`cli_extensions/`** | CLI command handlers | Modular command classes with `add_cli_arguments()` and `process_cli_command()` methods |
| **`config/`** | Configuration management | Config file I/O, validation, CLI commands |
| **`utils/`** | Pure utilities | Stateless helper functions (no plugin knowledge) |
| **`output/`** | Output system | Global logging with colors and verbosity |

---

## Pluggable Systems

### Repository Backend Plugins

**To add a new repository type (e.g., S3):**

1. Create `agent_manager/plugins/repos/s3_repo.py`:

```python
from .abstract_repo import AbstractRepo

class S3Repo(AbstractRepo):
    REPO_TYPE = "s3"
    
    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        return url.startswith("s3://")
    
    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        # Validate S3 URL
        ...
    
    def get_path(self) -> Path:
        # Return local cache path
        ...
    
    def needs_update(self) -> bool:
        # Check if S3 has updates
        ...
    
    def update(self) -> None:
        # Download from S3
        ...
```

2. That's it! Auto-discovery handles the rest.

### Merger Plugins

**To add a new merger type (e.g., TOML):**

1. Create `agent_manager/plugins/mergers/toml_merger.py`:

```python
import tomli
import tomli_w
from .dict_merger import DictMerger

class TomlMerger(DictMerger):
    FILE_EXTENSIONS = [".toml"]
    
    @classmethod
    def deserialize(cls, content: str) -> dict:
        return tomli.loads(content)
    
    @classmethod
    def serialize(cls, data: dict, **settings) -> str:
        return tomli_w.dumps(data)
    
    @classmethod
    def merge_preferences(cls) -> dict:
        return {}  # Or define TOML-specific preferences
```

2. That's it! Auto-discovery handles the rest.

### Agent Plugins

**To add a new agent (e.g., ChatGPT):**

1. Create package `ai_agent_chatgpt/`:

```python
# ai_agent_chatgpt/chatgpt.py
from agent_manager.plugins.agents import AbstractAgent

class Agent(AbstractAgent):
    agent_directory = Path.home() / ".chatgpt"
    
    def register_hooks(self):
        # Optional: Add pre/post-merge hooks
        pass
    
    def register_mergers(self):
        # Optional: Register custom mergers
        pass
    
    def update(self, config: dict):
        # Initialize ChatGPT environment
        self._initialize()
        
        # Use generic merge
        self.merge_configurations(config)
```

2. Install: `pip install -e ai_agent_chatgpt/`
3. That's it! Plugin is auto-discovered.

---

## Data Flow

### Startup Flow

```
1. User runs: agent-manager run --agent claude

2. Parse CLI arguments
   ├── Verbosity level
   ├── Agent selection
   └── Command (run, config, update, mergers)

3. Load configuration
   ├── Read ~/.agent-manager/config.yaml
   ├── Validate hierarchy
   ├── Instantiate repo objects
   └── Return ConfigData

4. Discover agent plugins
   ├── Scan for ai_agent_* packages
   └── Return plugin map

5. Execute command
   └── If "run":
       ├── Update repositories (if needed)
       └── Run selected agent(s)
```

### Merge Flow

```
1. Agent.merge_configurations(config)

2. For each hierarchy level (org → team → personal):
   
   a. Discover files in repo
      ├── Respect exclude patterns
      └── Return list of Paths
   
   b. For each file:
      
      i. Read file content
      
      ii. Run pre-merge hook (if registered)
          └── Hook can validate, transform, etc.
      
      iii. Get appropriate merger
           ├── Check filename registry
           ├── Check extension registry
           └── Fallback to CopyMerger
      
      iv. Merge content
          ├── First occurrence: Save as base
          └── Subsequent: Merge with existing
      
      v. Store merged result

3. For each merged file:
   
   a. Run post-merge hook (if registered)
      └── Hook can add metadata, validate, etc.
   
   b. Write to agent directory
```

### Update Flow

```
1. User runs: agent-manager update

2. Load configuration
   └── Returns ConfigData with repo objects

3. For each hierarchy entry:
   
   a. Get repo object
   
   b. Check if update needed
      ├── GitRepo: Check if needs clone/fetch
      └── LocalRepo: Always false
   
   c. If update needed:
      ├── GitRepo: Clone or fetch/pull
      └── LocalRepo: No-op
```

---

## Design Principles

### 1. Pluggable Everything

**Philosophy:** Users should be able to extend any part of the system without modifying core code.

**Implementation:**
- Abstract base classes define interfaces
- Auto-discovery finds implementations
- Factory patterns create instances

### 2. Separation of Concerns

**Philosophy:** Each component has a single, well-defined responsibility.

**Implementation:**
- Config management (config/)
- Repository backends (repos/)
- Merge strategies (mergers/)
- Agent plugins (agents/)
- Output handling (output/)

### 3. Fail-Safe Defaults

**Philosophy:** The system should work with minimal configuration and fail gracefully.

**Implementation:**
- Default merge strategies (deep merge dicts, replace lists)
- Fallback merger (CopyMerger) for unknown types
- Graceful error handling with informative messages

### 4. Self-Documenting

**Philosophy:** The system should be able to describe itself.

**Implementation:**
- `merge_preferences()` defines configurable options
- CLI commands to list/show plugins and settings
- Type hints throughout

### 5. Progressive Enhancement

**Philosophy:** Start simple, add complexity as needed.

**Implementation:**
- Single-level hierarchy works fine
- Default mergers work for most cases
- Hooks/custom mergers are optional

---

## Extension Points

### 1. Custom Repository Type

**When:** You need to fetch configs from a custom source (S3, HTTP, database, etc.)

**How:** Subclass `AbstractRepo` and implement required methods.

**See:** [Creating Custom Repos](CUSTOM_REPOS.md)

### 2. Custom Merger

**When:** You have a file type that needs special merging logic.

**How:** Subclass `AbstractMerger` (or `DictMerger` for structured data).

**See:** [Creating Custom Mergers](CUSTOM_MERGERS.md)

### 3. Custom Agent

**When:** You want to manage configs for a new AI tool.

**How:** Create `ai_agent_*` package with `AbstractAgent` subclass.

**See:** [Creating Custom Agents](CUSTOM_AGENTS.md)

### 4. Custom Merge Strategy

**When:** You need different dict/list merging behavior.

**How:** Subclass `MergeStrategy` and override `merge_dict()` or `merge_list()`.

**See:** [Merge Strategies](STRATEGIES.md)

### 5. Hooks

**When:** You need custom pre/post-processing for specific files.

**How:** Register hooks in your agent's `register_hooks()` method.

**See:** [Hook System](HOOKS.md)

---

## Performance Considerations

### Lazy Loading

- **Repo objects**: Created on-demand during config load
- **Merger classes**: Discovered at startup, instantiated per-use
- **Agent plugins**: Loaded only when selected

### Caching

- **Git repositories**: Cloned once, then fetched/pulled
- **Config file**: Parsed once per command
- **File discovery**: No caching (repos can change)

### Scalability

- **Hierarchy size**: No hard limit, but 3-5 levels is typical
- **File count**: Tested with hundreds of files per repo
- **Repo size**: Git repos are shallow-cloned (depth=1)

---

## Security Considerations

### Git Repository Access

- **Public repos**: No authentication required
- **Private repos**: Uses system Git credentials (SSH keys, credential helpers)
- **HTTPS**: Respects `.netrc` and credential helpers

### Local File Access

- **Paths**: Resolved with `expanduser()` and `resolve()`
- **Symlinks**: Followed (standard Python behavior)
- **Permissions**: Respects filesystem permissions

### Config File

- **Location**: `~/.agent-manager/config.yaml` (user-only)
- **Permissions**: Should be user-readable only (600)
- **Secrets**: Don't store secrets in config (use env vars)

---

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock external dependencies (Git, filesystem)
- Verify error handling

### Integration Tests

- Test end-to-end flows
- Use temporary directories for Git repos
- Verify config file I/O

### Plugin Tests

- Test plugin discovery
- Verify each plugin loads correctly
- Test custom implementations

---

## Future Architecture

### Planned Enhancements

1. **Plugin Marketplace**: Central registry of agent/repo/merger plugins
2. **Remote Merge Server**: Centralized merge service for teams
3. **Web UI**: Browser-based config management
4. **Conflict Resolution**: Interactive merge conflict resolution
5. **Config Versioning**: Track config changes over time

---

## See Also

- [Getting Started](GETTING_STARTED.md) - Setup guide
- [Custom Agents](CUSTOM_AGENTS.md) - Create agent plugins
- [Custom Repos](CUSTOM_REPOS.md) - Add repository types
- [Custom Mergers](CUSTOM_MERGERS.md) - Add merge strategies
- [Merge Strategies](STRATEGIES.md) - How merging works

