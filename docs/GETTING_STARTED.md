# Getting Started with Agent Manager

This guide will walk you through installing, configuring, and using Agent Manager to manage your AI agent configurations.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [First Run & Configuration](#first-run--configuration)
4. [Understanding the Hierarchy](#understanding-the-hierarchy)
5. [Basic Operations](#basic-operations)
6. [Next Steps](#next-steps)

---

## Prerequisites

- **Python 3.12+**
- **Git** (for Git repository backends)
- **pip** (Python package installer)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/john-westcott-iv/agent-manager.git
cd agent-manager
```

### Step 2: Install the Core Package

```bash
pip install -e agent_manager/
```

This installs `agent-manager` in editable mode, making the `agent-manager` command available system-wide.

### Step 3: Install Agent Plugins

Install the Claude plugin (or create your own):

```bash
pip install -e ai_agent_claude/
```

To verify installation:

```bash
agent-manager --help
```

You should see the full command list.

---

## First Run & Configuration

On your first run, Agent Manager will guide you through creating your configuration.

### Interactive Setup

```bash
agent-manager run
```

You'll be prompted with:

```
Config file does not exist. Would you like to initialize it now? (yes/no):
```

Type `yes` and press Enter.

### Define Your Hierarchy

You'll be asked to define your configuration hierarchy as a Python list:

```
Please create your hierarchy like a Python list.
The first element has the LOWEST priority, the last element has the HIGHEST priority.
Example: ["organization", "team", "personal"]

Enter hierarchy:
```

**Example:**

```python
["organization", "team", "personal"]
```

This creates a 3-level hierarchy where:
- `organization` is the base (lowest priority)
- `team` overrides organization
- `personal` overrides both (highest priority)

### Provide Repository URLs

For each level, you'll be prompted to provide a Git URL or `file://` path:

```
Enter URL for 'organization' (Git or file://):
```

**Options:**

1. **Git Repository** (public or private):
   ```
   https://github.com/your-org/ai-standards
   ```

2. **Local Directory**:
   ```
   file:///Users/you/my-ai-config
   ```

The system will validate each URL/path:
- For Git URLs: Attempts to clone/fetch
- For file:// paths: Checks if directory exists

If validation fails, you'll be prompted to try again.

### Example Complete Setup

```
Enter hierarchy: ["organization", "team", "personal"]

Enter URL for 'organization' (Git or file://): https://github.com/acme/ai-standards
✓ Successfully validated Git URL

Enter URL for 'team' (Git or file://): https://github.com/acme/backend-team
✓ Successfully validated Git URL

Enter URL for 'personal' (Git or file://): file:///Users/john/my-ai-config
✓ Successfully validated file:// path

✓ Configuration initialized successfully!
Config saved to: /Users/john/.agent-manager/config.yaml
```

---

## Understanding the Hierarchy

The hierarchy defines the **order and priority** of your configuration sources.

### How Merging Works

When you run `agent-manager run`, the system:

1. **Discovers files** in each repository (e.g., `.cursorrules`, `mcp.json`)
2. **Merges them** from lowest to highest priority
3. **Writes the result** to your agent directory (e.g., `~/.claude/`)

**Example:**

```
Organization: .cursorrules
---
Use Python 3.12+
Follow PEP 8

Team: .cursorrules
---
Use FastAPI for APIs
Prefer async/await

Personal: .cursorrules
---
Use 4-space indentation

Result: ~/.claude/.cursorrules
---
**Note to AI Agent:** Given all of the previous information,
the following from 'organization' overrides anything you already know.
---
Use Python 3.12+
Follow PEP 8

---
**Note to AI Agent:** Given all of the previous information,
the following from 'team' overrides anything you already know.
---
Use FastAPI for APIs
Prefer async/await

---
**Note to AI Agent:** Given all of the previous information,
the following from 'personal' overrides anything you already know.
---
Use 4-space indentation
```

For structured files (JSON/YAML), deep merging is used instead.

---

## Basic Operations

### Running Agents

```bash
# Run all configured agents
agent-manager run

# Run a specific agent
agent-manager run --agent claude
```

This will:
1. Update repositories (if needed)
2. Merge configurations
3. Run the specified agent(s)

### Viewing Configuration

```bash
# Show current hierarchy
agent-manager config show

# Show with resolved file:// paths
agent-manager config show --resolve-paths
```

Example output:

```
Current Configuration Hierarchy:

1. organization
   URL: https://github.com/acme/ai-standards
   Type: git
   Status: ✓ Accessible

2. team
   URL: https://github.com/acme/backend-team
   Type: git
   Status: ✓ Accessible

3. personal
   URL: file:///Users/john/my-ai-config
   Type: local
   Path: /Users/john/my-ai-config
   Status: ✓ Accessible
```

### Updating Repositories

```bash
# Update all repositories
agent-manager update

# Force update even if up-to-date
agent-manager update --force
```

This fetches the latest changes from Git repositories.

### Validating Configuration

```bash
# Check if all repositories are accessible
agent-manager config validate
```

---

## Configuration Management

### Adding a New Level

```bash
agent-manager config add <name> <url>

# Example: Add a "client" level at the end (highest priority)
agent-manager config add client https://github.com/client-x/ai-config

# Example: Add at specific position (0-based index)
agent-manager config add client https://github.com/client-x/ai-config --position 2
```

### Removing a Level

```bash
agent-manager config remove <name>

# Example
agent-manager config remove team
```

### Updating a Level

```bash
# Change URL
agent-manager config update team --url https://github.com/acme/new-backend-team

# Rename
agent-manager config update team --rename backend-team

# Both
agent-manager config update team --url <new-url> --rename backend-team
```

### Reordering Levels

```bash
# Move to specific position
agent-manager config move team --position 0

# Move up one position (higher priority)
agent-manager config move team --up

# Move down one position (lower priority)
agent-manager config move team --down
```

---

## Configuring Merge Behavior

Agent Manager uses type-aware mergers for different file types. You can customize their behavior:

```bash
# Interactive configuration
agent-manager mergers configure

# Configure specific merger
agent-manager mergers configure --merger JsonMerger
```

Example session:

```
Configuring JsonMerger...

indent (int, default=2): Number of spaces for JSON indentation
  Current value: 2
  Enter new value (or press Enter to keep current): 4

sort_keys (bool, default=False): Sort JSON keys alphabetically
  Current value: False
  Enter new value (true/false, or press Enter to keep current): true

✓ Configuration saved!
```

### Viewing Merger Info

```bash
# List all available mergers
agent-manager mergers list

# Show preferences for specific merger
agent-manager mergers show JsonMerger
```

---

## Common Workflows

### Scenario 1: Personal Only Setup

If you don't have organization/team repos, just use a local directory:

```python
["personal"]  # Single-level hierarchy
```

```
file:///Users/you/my-ai-config
```

### Scenario 2: Work + Personal

```python
["work", "personal"]
```

- `work`: Company Git repo
- `personal`: Your local overrides

### Scenario 3: Multi-Project

```python
["organization", "project-a", "personal"]
```

Change `project-a` to `project-b` when switching projects:

```bash
agent-manager config update project-a --url https://github.com/org/project-b-ai
```

---

## Next Steps

Now that you have Agent Manager set up:

1. **Explore the CLI**: See [CLI Reference](CLI_REFERENCE.md)
2. **Understand Architecture**: Read [Architecture Overview](ARCHITECTURE.md)
3. **Customize Merging**: Learn about [Merge Strategies](STRATEGIES.md)
4. **Create Custom Agent**: See [Creating Custom Agents](CUSTOM_AGENTS.md)
5. **Troubleshoot**: Check [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `agent-manager run` | Run all agents |
| `agent-manager run --agent <name>` | Run specific agent |
| `agent-manager update` | Update repositories |
| `agent-manager config show` | View configuration |
| `agent-manager config add <name> <url>` | Add hierarchy level |
| `agent-manager config remove <name>` | Remove hierarchy level |
| `agent-manager config validate` | Validate config |
| `agent-manager mergers configure` | Configure merge behavior |
| `agent-manager config init` | Re-initialize config |

---

**Need help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on GitHub.

