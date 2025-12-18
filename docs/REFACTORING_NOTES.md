# Refactoring Notes: Core Infrastructure

This document describes the architectural refactoring completed on November 21, 2025, which introduced the `core/` directory and reorganized the codebase for better separation of concerns.

---

## Overview

The refactoring focused on separating **plugin infrastructure** from **plugin implementations**, making the codebase more maintainable and easier to understand.

---

## Directory Changes

### New Directory: `core/`

Created `agent_manager/core/` to house core infrastructure:

```
agent_manager/core/
├── __init__.py               # Exports all core components
├── merger_registry.py        # Moved from plugins/mergers/
├── mergers.py                # Moved from utils/
└── repos.py                  # Moved from utils/
```

**Purpose**: Core infrastructure for managing the plugin system, including:
- Registry systems (MergerRegistry)
- Plugin discovery functions
- Factory functions
- System-level operations (update_repositories)

### Renamed Directories

1. **`agents/` → `plugins/agents/`**
   - Pure plugin implementations
   - Contains `AbstractAgent` and related base classes

2. **`mergers/` → `plugins/mergers/`**
   - Pure merger plugin implementations
   - No longer contains `merger_registry.py` (moved to `core/`)

3. **`repos/` → `plugins/repos/`**
   - Pure repository plugin implementations
   - Contains `AbstractRepo`, `GitRepo`, `LocalRepo`

### Updated Directory: `utils/`

**Before**: Mixed utilities and plugin infrastructure
**After**: Pure stateless utility functions only

```
agent_manager/utils/
└── url.py                    # URL helpers (is_file_url, resolve_file_path)
```

### New Directory: `cli_extensions/`

Already existed, but now clearly separated from plugins:

```
agent_manager/cli_extensions/
├── agent_commands.py         # AgentCommands (run command)
├── merger_commands.py        # MergerCommands (mergers subcommands)
└── repo_commands.py          # RepoCommands (update command)
```

---

## File Moves

| Old Location | New Location | Reason |
|--------------|--------------|--------|
| `plugins/mergers/merger_registry.py` | `core/merger_registry.py` | Infrastructure, not a plugin |
| `utils/mergers.py` | `core/mergers.py` | Plugin infrastructure |
| `utils/repos.py` | `core/repos.py` | Plugin infrastructure |

---

## Import Changes

### Core Infrastructure

**Before**:
```python
from agent_manager.utils import create_repo, update_repositories
from agent_manager.plugins.mergers import MergerRegistry
```

**After**:
```python
from agent_manager.core import create_repo, update_repositories
from agent_manager.core import MergerRegistry
```

### Plugin Implementations

**Before**:
```python
from agent_manager.agents import AbstractAgent
from agent_manager.mergers import AbstractMerger
from agent_manager.repos import AbstractRepo
```

**After**:
```python
from agent_manager.plugins.agents import AbstractAgent
from agent_manager.plugins.mergers import AbstractMerger
from agent_manager.plugins.repos import AbstractRepo
```

---

## Files Updated

### Python Code Files

1. **`agent_manager/agent_manager.py`**
   - Updated imports: `core` instead of `utils`

2. **`agent_manager/config/config.py`**
   - Updated imports: `core.repos` instead of `utils`

3. **`agent_manager/cli_extensions/agent_commands.py`**
   - Updated imports: `plugins.agents` instead of `agents`

4. **`agent_manager/cli_extensions/merger_commands.py`**
   - Updated imports: `core.MergerRegistry`

5. **`agent_manager/cli_extensions/repo_commands.py`**
   - Updated imports: `core.update_repositories`

6. **`agent_manager/plugins/agents/agent.py`**
   - Updated imports: `core.MergerRegistry`

7. **All test files**
   - Updated imports to match new structure
   - Moved `test_merger_registry.py` to `tests/core/`

### Documentation Files

All documentation files in `agent_manager/docs/` were updated:

1. **`ARCHITECTURE.md`**
   - Added "Core Infrastructure" section
   - Added "Directory Structure" section with complete tree
   - Updated all path references

2. **`CUSTOM_AGENTS.md`**
   - Updated import paths to `plugins.agents`

3. **`CUSTOM_REPOS.md`**
   - Updated path references to `plugins/repos/`

4. **`CUSTOM_MERGERS.md`**
   - Updated path references to `plugins/mergers/`

5. **`CONFIGURATION.md`**
   - Updated import examples

6. **`HOOKS.md`**
   - Updated import examples

7. **`STRATEGIES.md`**
   - Updated import examples

8. **`TROUBLESHOOTING.md`**
   - Updated file path references

9. **Root `README.md`**
   - Updated project structure diagram
   - Updated all import examples

10. **`agent_manager/README.md`**
    - Updated code examples
    - Updated architecture description

---

## Design Philosophy

The new structure follows these principles:

| Directory | Purpose | Guidelines |
|-----------|---------|------------|
| **`core/`** | Plugin infrastructure & system operations | Registry systems, discovery, factories, system-level operations |
| **`plugins/`** | Plugin implementations | Concrete classes extending abstract bases |
| **`cli_extensions/`** | CLI command handlers | Modular command classes with standard interface |
| **`config/`** | Configuration management | Config file I/O, validation, CLI commands |
| **`utils/`** | Pure utilities | Stateless helper functions (no plugin knowledge) |
| **`output/`** | Output system | Global logging with colors and verbosity |

---

## Benefits

### 1. **Clear Separation of Concerns**
- Infrastructure vs. implementations are now distinct
- No confusion about where code belongs

### 2. **Improved Discoverability**
- Developers immediately know where to look
- `core/` for infrastructure, `plugins/` for implementations

### 3. **Scalability**
- Easy to add more infrastructure (AgentRegistry, ConfigRegistry, etc.)
- Clear place for system-level operations

### 4. **Cleaner Utilities**
- `utils/` is now truly utilities (just URL helpers)
- No mixed concerns

### 5. **Better Testing**
- Test directory mirrors code structure
- Core infrastructure tests separate from plugin tests

---

## Migration Guide

For developers with existing plugins or extensions:

### If you have custom agents:

**Old**:
```python
from agent_manager.agents import AbstractAgent
```

**New**:
```python
from agent_manager.plugins.agents import AbstractAgent
```

### If you have custom repos:

**Old**:
```python
from agent_manager.repos import AbstractRepo
```

**New**:
```python
from agent_manager.plugins.repos import AbstractRepo
```

### If you have custom mergers:

**Old**:
```python
from agent_manager.mergers import AbstractMerger, MergerRegistry
```

**New**:
```python
from agent_manager.plugins.mergers import AbstractMerger
from agent_manager.core import MergerRegistry
```

### If you're using utility functions:

**Old**:
```python
from agent_manager.utils import create_repo, update_repositories
```

**New**:
```python
from agent_manager.core import create_repo, update_repositories
```

---

## Backward Compatibility

This is a **breaking change** for:
- Custom agent plugins that import from `agent_manager.agents`
- Custom repo plugins that import from `agent_manager.repos`
- Custom merger plugins that import from `agent_manager.mergers`
- Any code using `agent_manager.utils.repos` or `agent_manager.utils.mergers`

**Action Required**: Update import statements as shown in the migration guide above.

---

## Future Enhancements

The new `core/` directory makes it easier to add:
- `AgentRegistry` for managing agent plugin lifecycle
- `ConfigRegistry` for managing config validation schemas
- More discovery functions for other plugin types
- System-level monitoring and metrics

---

## Status

- ✅ Code restructuring complete
- ✅ All imports updated
- ✅ Documentation updated
- ✅ Tests restructured
- ✅ Ruff linting passing (2 minor cosmetic warnings)
- ✅ All functionality preserved

---

**Date**: November 21, 2025  
**Author**: AI Assistant (Claude Sonnet 4.5)  
**Approved**: John Westcott IV

