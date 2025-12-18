# CLI Reference

Complete reference for all `agent-manager` command-line options.

---

## Table of Contents

1. [Global Options](#global-options)
2. [Commands Overview](#commands-overview)
3. [run](#run)
4. [update](#update)
5. [config](#config)
6. [mergers](#mergers)

---

## Global Options

These options can be used with any command:

```bash
agent-manager [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Increase output verbosity (can be used multiple times) | `1` |
| `--quiet` | `-q` | Decrease output verbosity | `1` |
| `--no-color` | | Disable colored output | Colors enabled |
| `--help` | `-h` | Show help message | |

### Examples

```bash
# Debug mode (verbosity = 2)
agent-manager -v run

# Very verbose (verbosity = 3)
agent-manager -vv run

# Quiet mode (errors only)
agent-manager -q run

# No colors
agent-manager --no-color config show
```

---

## Commands Overview

| Command | Description |
|---------|-------------|
| `run` | Run agent(s) to merge and apply configurations |
| `update` | Update repositories from their sources |
| `config` | Manage configuration hierarchy |
| `mergers` | Manage merger preferences |

---

## run

Run agent(s) to merge configurations from the hierarchy.

### Usage

```bash
agent-manager run [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--agent` | string | `all` | Agent to run (`all` or specific agent name) |

### Examples

```bash
# Run all configured agents
agent-manager run

# Run specific agent
agent-manager run --agent claude

# Run with verbose output
agent-manager -v run
```

### Behavior

1. **Update repositories** (if they need updating)
2. **Discover agent plugins** (scans for `ai_agent_*` packages)
3. **Run selected agent(s)**:
   - Initialize agent environment
   - Discover files in each hierarchy level
   - Merge files using appropriate strategies
   - Write merged files to agent directory

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (config invalid, repo update failed, merge failed, etc.) |

---

## update

Update repositories from their remote sources.

### Usage

```bash
agent-manager update [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force` | flag | `false` | Force update even if repo appears up-to-date |

### Examples

```bash
# Update all repositories
agent-manager update

# Force update all repos
agent-manager update --force

# Update with verbose output
agent-manager -v update
```

### Behavior

1. Load configuration
2. For each hierarchy entry:
   - Check if update is needed (`needs_update()`)
   - If needed (or `--force`), call `update()`:
     - **GitRepo**: Clone (if needed) or fetch/pull
     - **LocalRepo**: No-op (already up-to-date)

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (all repos updated) |
| `1` | Error (one or more repos failed to update) |

---

## config

Manage configuration hierarchy.

### Usage

```bash
agent-manager config <subcommand> [OPTIONS]
```

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `init` | (Re-)initialize configuration |
| `show` | Display current configuration |
| `validate` | Validate configuration |
| `add` | Add hierarchy level |
| `remove` | Remove hierarchy level |
| `update` | Update hierarchy level |
| `move` | Reorder hierarchy levels |
| `export` | Export configuration to file |
| `import` | Import configuration from file |
| `where` | Show config file location |

---

### config init

Initialize or re-initialize configuration.

#### Usage

```bash
agent-manager config init
```

#### Behavior

1. If config exists, prompt for confirmation
2. Interactively prompt for:
   - Hierarchy definition (Python list syntax)
   - URL for each level (Git or `file://`)
3. Validate each URL
4. Write config to `~/.agent-manager/config.yaml`

#### Example

```bash
$ agent-manager config init
Config already exists. This will overwrite it. Continue? (yes/no): yes

Enter hierarchy: ["organization", "team", "personal"]

Enter URL for 'organization': https://github.com/acme/ai-standards
✓ Valid Git URL

Enter URL for 'team': https://github.com/acme/backend
✓ Valid Git URL

Enter URL for 'personal': file:///Users/john/my-ai
✓ Valid file:// path

✓ Configuration initialized successfully!
```

---

### config show

Display current configuration hierarchy.

#### Usage

```bash
agent-manager config show [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--resolve-paths` | flag | `false` | Show resolved paths for `file://` URLs |

#### Examples

```bash
# Show configuration
agent-manager config show

# Show with resolved paths
agent-manager config show --resolve-paths
```

#### Example Output

```
Current Configuration Hierarchy:

1. organization
   URL: https://github.com/acme/ai-standards
   Type: git
   Status: ✓ Accessible

2. team
   URL: https://github.com/acme/backend
   Type: git
   Status: ✓ Accessible

3. personal
   URL: file:///Users/john/my-ai
   Type: local
   Path: /Users/john/my-ai  (when --resolve-paths)
   Status: ✓ Accessible
```

---

### config validate

Validate configuration.

#### Usage

```bash
agent-manager config validate
```

#### Behavior

1. Load configuration
2. Validate structure (required fields, valid types)
3. Check each repository URL:
   - Git URLs: Attempt to clone/fetch
   - `file://` paths: Check if directory exists
4. Report any errors

#### Example

```bash
$ agent-manager config validate
✓ Configuration structure is valid
✓ All repository URLs are accessible

Configuration is valid!
```

---

### config add

Add a new hierarchy level.

#### Usage

```bash
agent-manager config add <name> <url> [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✓ | Unique name for this level |
| `url` | string | ✓ | Git URL or `file://` path |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--position` | int | end | Position to insert (0-based index) |

#### Examples

```bash
# Add at end (highest priority)
agent-manager config add client https://github.com/client-x/ai

# Add at specific position
agent-manager config add client https://github.com/client-x/ai --position 2
```

#### Behavior

1. Validate URL
2. Detect repository type
3. Insert at specified position (or end)
4. Write updated config

---

### config remove

Remove a hierarchy level.

#### Usage

```bash
agent-manager config remove <name>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✓ | Name of level to remove |

#### Example

```bash
agent-manager config remove team
```

---

### config update

Update an existing hierarchy level.

#### Usage

```bash
agent-manager config update <name> [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✓ | Name of level to update |

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--url` | string | New URL |
| `--rename` | string | New name |

At least one option is required.

#### Examples

```bash
# Change URL
agent-manager config update team --url https://github.com/acme/new-backend

# Rename
agent-manager config update team --rename backend-team

# Both
agent-manager config update team --url <url> --rename backend-team
```

---

### config move

Reorder hierarchy levels (change priority).

#### Usage

```bash
agent-manager config move <name> <direction>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✓ | Name of level to move |

#### Options (mutually exclusive)

| Option | Type | Description |
|--------|------|-------------|
| `--position` | int | Move to specific position (0-based) |
| `--up` | flag | Move up one position (increase priority) |
| `--down` | flag | Move down one position (decrease priority) |

Exactly one option is required.

#### Examples

```bash
# Move to specific position
agent-manager config move team --position 0

# Move up (higher priority)
agent-manager config move team --up

# Move down (lower priority)
agent-manager config move team --down
```

---

### config export

Export configuration to a file or stdout.

#### Usage

```bash
agent-manager config export [file]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `file` | path | | Output file (omit for stdout) |

#### Examples

```bash
# Export to stdout
agent-manager config export

# Export to file
agent-manager config export my-config.yaml

# Export and pipe
agent-manager config export | grep personal
```

---

### config import

Import configuration from a file.

#### Usage

```bash
agent-manager config import <file>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `file` | path | ✓ | Input file |

#### Example

```bash
agent-manager config import my-config.yaml
```

#### Behavior

1. Load and validate imported config
2. Overwrite existing config
3. Confirm success

---

### config where

Show location of config files and directories.

#### Usage

```bash
agent-manager config where
```

#### Example Output

```
Agent Manager Configuration Locations:

Config directory: /Users/john/.agent-manager
Config file: /Users/john/.agent-manager/config.yaml
Repository cache: /Users/john/.agent-manager/repos
```

---

## mergers

Manage merger configurations.

### Usage

```bash
agent-manager mergers <subcommand> [OPTIONS]
```

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List all registered merger types |
| `show` | Show preferences for a specific merger |
| `configure` | Interactively configure merger preferences |

---

### mergers list

List all registered merger types.

#### Usage

```bash
agent-manager mergers list
```

#### Example Output

```
Available Mergers:

1. JsonMerger
   Extensions: .json
   Description: Deep merge JSON objects

2. YamlMerger
   Extensions: .yaml, .yml
   Description: Deep merge YAML objects

3. MarkdownMerger
   Extensions: .md, .markdown
   Description: Concatenate with AI context markers

4. TextMerger
   Extensions: .txt
   Description: Simple concatenation

5. CopyMerger
   Extensions: (fallback for all)
   Description: Last source wins
```

---

### mergers show

Show configurable preferences for a specific merger.

#### Usage

```bash
agent-manager mergers show <merger>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `merger` | string | ✓ | Merger class name (e.g., `JsonMerger`) |

#### Example

```bash
$ agent-manager mergers show JsonMerger

JsonMerger Preferences:

indent (int, default=2)
  Number of spaces for JSON indentation
  Range: 0-8
  Current value: 2

sort_keys (bool, default=False)
  Sort JSON keys alphabetically
  Current value: False
```

---

### mergers configure

Interactively configure merger preferences.

#### Usage

```bash
agent-manager mergers configure [OPTIONS]
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--merger` | string | Configure only a specific merger |

#### Examples

```bash
# Configure all mergers interactively
agent-manager mergers configure

# Configure specific merger
agent-manager mergers configure --merger JsonMerger
```

#### Example Session

```bash
$ agent-manager mergers configure --merger JsonMerger

Configuring JsonMerger...

indent (int, default=2): Number of spaces for JSON indentation
  Current value: 2
  Valid range: 0-8
  Enter new value (or press Enter to keep current): 4

sort_keys (bool, default=False): Sort JSON keys alphabetically
  Current value: False
  Enter new value (true/false, or press Enter to keep current): true

✓ Configuration saved!
```

---

## Exit Codes

All commands use standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (see error message for details) |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_MANAGER_CONFIG_DIR` | Config directory location | `~/.agent-manager` |
| `AGENT_MANAGER_VERBOSITY` | Output verbosity (0-2) | `1` |
| `NO_COLOR` | Disable colored output | (not set) |

---

## Output Verbosity Levels

| Level | Flag | Output |
|-------|------|--------|
| `0` | `-qq` | Errors only |
| `1` | (default) | Info + warnings + errors |
| `2` | `-v` | Debug + info + warnings + errors |
| `3` | `-vv` | Very verbose debug output |

---

## Examples

### Complete Workflow

```bash
# 1. Initialize configuration
agent-manager config init

# 2. View configuration
agent-manager config show

# 3. Add a new level
agent-manager config add project https://github.com/project-x/ai

# 4. Update repositories
agent-manager update

# 5. Configure mergers
agent-manager mergers configure

# 6. Run agents
agent-manager run

# 7. Run specific agent with debug output
agent-manager -v run --agent claude
```

### Team Collaboration

```bash
# Export config for team
agent-manager config export team-config.yaml

# Share with teammate...

# Teammate imports
agent-manager config import team-config.yaml

# Validate it works
agent-manager config validate
```

### Troubleshooting

```bash
# Check config location
agent-manager config where

# Validate config
agent-manager config validate

# Re-initialize if broken
agent-manager config init

# Force update all repos
agent-manager update --force

# Run with full debug output
agent-manager -vv run
```

---

## See Also

- [Getting Started](GETTING_STARTED.md) - Setup guide
- [Configuration](CONFIGURATION.md) - Config file reference
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

