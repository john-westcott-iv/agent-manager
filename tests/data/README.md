# Test Data for Agent Manager

This directory contains three sample configuration hierarchies used in integration tests for the agent-manager merging functionality.

## Purpose

These directories (`org/`, `team/`, `personal/`) are used by the `TestAgent` class and integration tests in `test_agent_manager.py` to verify that:
1. Multiple hierarchy levels are correctly merged
2. Different file types use appropriate mergers (JSON, YAML, Markdown, Text)
3. Priority ordering works (personal > team > org)
4. The full agent-manager flow works end-to-end

## Directory Structure

```
agent-manager/
├── org/                    # Organization level (lowest priority)
│   ├── .cursorrules       # Company-wide coding standards
│   ├── mcp.json          # Company-approved MCP servers
│   ├── settings.yaml     # Technical standards
│   └── README.md         # Documentation
│
├── team/                   # Team level (medium priority)
│   ├── .cursorrules       # Team-specific standards
│   ├── mcp.json          # Team tools (PostgreSQL, Redis, AWS)
│   ├── settings.yaml     # Team configuration
│   └── guidelines.md     # Team-specific guidelines
│
└── personal/               # Personal level (highest priority)
    ├── .cursorrules       # Personal preferences
    ├── mcp.json          # Personal development tools
    ├── settings.yaml     # Personal settings
    └── notes.txt         # Personal notes
```

## Merge Priority

When agent-manager merges these configurations:

**Priority**: `personal` > `team` > `org`

- **Organization** configs are overridden by team and personal
- **Team** configs override org, but are overridden by personal
- **Personal** configs have the highest priority

## File Types and Mergers

### JSON Files (`mcp.json`)
- **Merger**: `JsonMerger` (deep merge)
- **Behavior**: Merges nested objects, combines arrays
- **Example**: All MCP servers from org, team, and personal are combined

### YAML Files (`settings.yaml`)
- **Merger**: `YamlMerger` (deep merge)
- **Behavior**: Merges nested dictionaries, later values override earlier
- **Example**: Personal `min_coverage: 90` overrides team's `85` and org's `80`

### Markdown Files (`README.md`, `guidelines.md`)
- **Merger**: `MarkdownMerger` (concatenation)
- **Behavior**: Concatenates content with separators
- **Example**: All markdown files are combined with horizontal rules

### Text Files (`.cursorrules`, `notes.txt`)
- **Merger**: `TextMerger` (concatenation)
- **Behavior**: Concatenates content with blank line separators
- **Example**: All `.cursorrules` from org, team, and personal are combined

## Running the Tests

The integration tests automatically use this test data:

```bash
# Run all integration tests
cd agent_manager
pytest tests/test_agent_manager.py::TestFullIntegration -v

# Run the main merge integration test
pytest tests/test_agent_manager.py::TestFullIntegration::test_full_merge_integration -v
```

## Using as Manual Test Data

You can also use these directories for manual testing:

### Option 1: Using as local file:// repos

Configure agent-manager to use these directories:

```yaml
# ~/.agent-manager/config.yaml
hierarchy:
  - name: organization
    url: file:///path/to/agent_manager/tests/data/org
    repo_type: local
  
  - name: team
    url: file:///path/to/agent_manager/tests/data/team
    repo_type: local
  
  - name: personal
    url: file:///path/to/agent_manager/tests/data/personal
    repo_type: local
```

### Option 2: Convert to Git repositories

```bash
# Initialize each as a git repo
cd org && git init && git add . && git commit -m "Initial org config"
cd ../team && git init && git add . && git commit -m "Initial team config"
cd ../personal && git init && git add . && git commit -m "Initial personal config"
```

Then push to GitHub/GitLab and reference the URLs in your config.

## Expected Merge Results

### mcp.json (Combined)
After merging, you should have all MCP servers:
- `company-docs` (from org)
- `jira` (from org)
- `postgres` (from team)
- `redis` (from team)
- `aws` (from team)
- `filesystem` (from personal)
- `git` (from personal)
- `localhost` (from personal)
- `postgres-local` (from personal)

### settings.yaml (Overrides)
- `min_coverage`: 90 (personal overrides team's 85 and org's 80)
- `log_level`: "DEBUG" (personal overrides team's "INFO")
- Organization settings remain unless overridden

### .cursorrules (Concatenated)
All three files concatenated:
1. Organization standards
2. Team-specific rules
3. Personal preferences

This gives you the full context hierarchy!

## Usage with Agent Manager

```bash
# Initialize configuration
agent-manager config init

# Update repositories
agent-manager update

# Run with an agent (e.g., claude)
agent-manager run --agent claude

# View merged configuration
agent-manager config show
```

## Test Agent

The `TestAgent` class (`agent_manager/plugins/agents/test_agent.py`) is a minimal agent implementation used for testing. It:

- Creates a temporary output directory
- Merges configurations from the hierarchy
- Writes merged files to the temp directory
- Can be cleaned up after testing

Example usage:

```python
from agent_manager.plugins.agents.test_agent import TestAgent

agent = TestAgent()
agent.update(config_data)  # Merge and write configs
output_dir = agent.get_output_directory()
# ... verify merged files ...
agent.cleanup()  # Remove temp directory
```

