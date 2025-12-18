# Agent Manager

> **Hierarchical configuration management for AI agents with pluggable architecture**

A sophisticated framework for managing AI agent configurations across organizational, team, and personal levels with intelligent merging, pluggable repository backends, and type-aware content strategies.

---

## Quick Start

```bash
# Install
pip install -e .

# Initialize configuration
agent-manager config init

# Run agents
agent-manager run --agent claude

# View configuration
agent-manager config show
```

---

## Features

- **Hierarchical Configuration**: Organization → Team → Personal cascading
- **Pluggable Architecture**: Custom repos, agents, and mergers
- **Type-Aware Merging**: JSON, YAML, Markdown, Text with intelligent strategies
- **Hook System**: Pre/post-merge processing
- **Auto-Discovery**: Plugins automatically detected

---

## Documentation

**Comprehensive documentation available in [`docs/`](docs/):**

- **[Getting Started](docs/GETTING_STARTED.md)** - Complete setup guide
- **[Configuration](docs/CONFIGURATION.md)** - Config file reference
- **[CLI Reference](docs/CLI_REFERENCE.md)** - All commands
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Merge Strategies](docs/STRATEGIES.md)** - How merging works

**Extending Agent Manager:**

- **[Custom Agents](docs/CUSTOM_AGENTS.md)** - Create agent plugins
- **[Custom Repos](docs/CUSTOM_REPOS.md)** - Add repository types
- **[Custom Mergers](docs/CUSTOM_MERGERS.md)** - Add merge strategies
- **[Hooks](docs/HOOKS.md)** - Pre/post-merge processing

**Help:**

- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

---

## Development

### Creating Agent Plugins

Create a package named `ai_agent_*`:

```python
# ai_agent_yourplugin/yourplugin.py
from agent_manager.plugins.agents import AbstractAgent
from pathlib import Path

class Agent(AbstractAgent):
    agent_directory = Path.home() / ".yourplugin"

    def register_hooks(self):
        # Optional: Add custom hooks
        pass

    def register_mergers(self):
        # Optional: Add custom mergers
        pass

    def update(self, config: dict):
        self._initialize()
        self.merge_configurations(config)

    def _initialize(self):
        self.agent_directory.mkdir(parents=True, exist_ok=True)
```

Install and it's auto-discovered:

```bash
pip install -e ai_agent_yourplugin/
agent-manager run --agent yourplugin
```

See **[Creating Custom Agents](docs/CUSTOM_AGENTS.md)** for full guide.

---

## Architecture

```
agent-manager (Core)
├── Config Management (YAML hierarchy)
├── Repository Backends (Git, local, extensible)
├── Merge System (Type-aware, pluggable strategies)
└── Agent Plugins (Auto-discovered)

ai_agent_* (Plugins)
└── Tool-specific implementations
```

See **[Architecture Overview](docs/ARCHITECTURE.md)** for details.

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

## Links

- **Documentation**: [docs/](docs/)
- **GitHub**: https://github.com/john-westcott-iv/agent-manager

