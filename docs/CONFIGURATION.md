# Configuration Reference

This document provides a complete reference for Agent Manager's configuration system.

---

## Table of Contents

1. [Config File Location](#config-file-location)
2. [Config File Structure](#config-file-structure)
3. [Hierarchy Configuration](#hierarchy-configuration)
4. [Merger Configuration](#merger-configuration)
5. [Advanced Configuration](#advanced-configuration)
6. [Environment Variables](#environment-variables)

---

## Config File Location

Agent Manager stores its configuration in:

```
~/.agent-manager/config.yaml
```

On different platforms:
- **macOS/Linux**: `/Users/you/.agent-manager/config.yaml`
- **Windows**: `C:\Users\You\.agent-manager\config.yaml`

To find your config location:

```bash
agent-manager config where
```

---

## Config File Structure

```yaml
# ~/.agent-manager/config.yaml

hierarchy:
  - name: <string>          # Unique identifier
    url: <string>           # Git URL or file:// path
    repo_type: <string>     # "git" or "local"
    repo: <AbstractRepo>    # Repo instance (created at runtime)
  
  # ... more levels ...

mergers:
  <MergerClassName>:
    <setting>: <value>
    # ... more settings ...
  
  # ... more mergers ...
```

---

## Hierarchy Configuration

The `hierarchy` list defines your configuration sources in **priority order** (lowest to highest).

### Hierarchy Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✓ | Unique identifier for this level |
| `url` | string | ✓ | Git URL or `file://` path |
| `repo_type` | string | ✓ | Repository type: `"git"` or `"local"` |
| `repo` | object | ✓ | Repository instance (auto-created) |

### Example

```yaml
hierarchy:
  # Lowest priority (base)
  - name: organization
    url: https://github.com/acme-corp/ai-standards
    repo_type: git
    repo: !python/object:agent_manager.plugins.repos.git_repo.GitRepo {...}
  
  # Medium priority
  - name: team
    url: https://github.com/acme-corp/backend-team
    repo_type: git
    repo: !python/object:agent_manager.plugins.repos.git_repo.GitRepo {...}
  
  # Highest priority (overrides everything)
  - name: personal
    url: file:///Users/john/my-ai-config
    repo_type: local
    repo: !python/object:agent_manager.plugins.repos.local_repo.LocalRepo {...}
```

### Priority Rules

- **First item** = Lowest priority (base configuration)
- **Last item** = Highest priority (overrides everything)
- Files from higher priority sources override lower priority sources

**Example:**

```yaml
hierarchy: ["org", "team", "personal"]

# If all three have .cursorrules:
# 1. org/.cursorrules is loaded first (base)
# 2. team/.cursorrules is merged on top (overrides org)
# 3. personal/.cursorrules is merged on top (final result)
```

---

## Merger Configuration

The `mergers` section lets you customize how different file types are merged.

### Structure

```yaml
mergers:
  JsonMerger:
    indent: 2
    sort_keys: false
  
  YamlMerger:
    indent: 2
    width: 120
  
  MarkdownMerger:
    separator_style: horizontal_rule
```

### Available Mergers

#### JsonMerger

Handles `.json` files with deep dictionary merging.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `indent` | int | `2` | Number of spaces for indentation (0-8) |
| `sort_keys` | bool | `false` | Sort keys alphabetically |

**Example:**

```yaml
mergers:
  JsonMerger:
    indent: 4
    sort_keys: true
```

#### YamlMerger

Handles `.yaml` and `.yml` files with deep dictionary merging.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `indent` | int | `2` | Number of spaces for indentation (2-8) |
| `width` | int | `120` | Maximum line width (60-200) |

**Example:**

```yaml
mergers:
  YamlMerger:
    indent: 4
    width: 100
```

#### MarkdownMerger

Handles `.md` and `.markdown` files with AI-aware concatenation.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `separator_style` | string | `"horizontal_rule"` | Separator between sources |

**Values:**
- `"horizontal_rule"`: Uses `---` separator
- `"heading"`: Uses `## From <source>` headings
- `"comment"`: Uses `<!-- From <source> -->` comments

**Example:**

```yaml
mergers:
  MarkdownMerger:
    separator_style: heading
```

#### TextMerger

Handles `.txt` files with simple concatenation.

No configurable settings.

#### CopyMerger

Fallback for unknown file types. Last source wins (no merging).

No configurable settings.

---

## Advanced Configuration

### Custom Repository Types

If you've added a custom repository type (e.g., S3, HTTP), it will appear in the config:

```yaml
hierarchy:
  - name: s3-config
    url: s3://my-bucket/ai-config/
    repo_type: s3
    repo: !python/object:my_plugin.repos.s3_repo.S3Repo {...}
```

The `repo_type` is determined by the repo class's `REPO_TYPE` attribute.

### Multiple Hierarchies (Future)

Currently not supported, but planned:

```yaml
# Future feature
hierarchies:
  default:
    - name: org
      url: ...
  
  client-x:
    - name: org
      url: ...
    - name: client-x
      url: ...
```

---

## Environment Variables

Agent Manager respects the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_MANAGER_CONFIG_DIR` | Config directory location | `~/.agent-manager` |
| `AGENT_MANAGER_VERBOSITY` | Output verbosity (0-2) | `1` |
| `NO_COLOR` | Disable colored output | (not set) |

### Examples

```bash
# Use custom config directory
export AGENT_MANAGER_CONFIG_DIR="$HOME/.config/agent-manager"
agent-manager run

# Enable debug output
export AGENT_MANAGER_VERBOSITY=2
agent-manager run

# Disable colors
export NO_COLOR=1
agent-manager config show
```

---

## Configuration Best Practices

### 1. Start Simple

Begin with a single-level hierarchy and add complexity as needed:

```yaml
hierarchy:
  - name: personal
    url: file:///Users/you/my-ai-config
    repo_type: local
```

### 2. Use Descriptive Names

Choose clear, descriptive names for hierarchy levels:

```yaml
# Good
["organization", "team", "personal"]
["company", "project-a", "personal"]

# Avoid
["level1", "level2", "level3"]
["a", "b", "c"]
```

### 3. Organize by Priority

Always think in terms of priority when ordering:

```yaml
# Lowest priority first
hierarchy:
  - name: organization  # Company-wide defaults
  - name: team          # Team overrides
  - name: project       # Project-specific
  - name: personal      # Your personal touch
```

### 4. Document Your URLs

Add comments to explain what each repository contains:

```yaml
hierarchy:
  # Company-wide AI coding standards
  - name: organization
    url: https://github.com/acme/ai-standards
    repo_type: git
  
  # Backend team specific configurations
  - name: team
    url: https://github.com/acme/backend-ai
    repo_type: git
  
  # My personal preferences and shortcuts
  - name: personal
    url: file:///Users/john/my-ai-config
    repo_type: local
```

### 5. Keep Personal Local

Use `file://` for personal configs to avoid cluttering Git:

```yaml
hierarchy:
  - name: organization
    url: https://github.com/...  # Git (shared)
  
  - name: personal
    url: file:///Users/you/...   # Local (private)
```

---

## Validation

Agent Manager validates your configuration on startup. Common validation errors:

### Missing Required Fields

```
Configuration error: Hierarchy entry missing required fields: name, url
```

**Fix:** Ensure all entries have `name`, `url`, `repo_type`, and `repo` fields.

### Invalid Repository Type

```
Configuration error: Invalid repo_type 'invalid' for 'organization'
```

**Fix:** Use `"git"` or `"local"` (or a custom type if you've added one).

### Invalid URL

```
Configuration error: Invalid Git URL: https://not-a-real-repo
```

**Fix:** Check that Git URLs are accessible and `file://` paths exist.

### Duplicate Names

```
Configuration error: Duplicate hierarchy name: 'team'
```

**Fix:** Each hierarchy level must have a unique name.

---

## Manual Editing

You can manually edit `~/.agent-manager/config.yaml`, but:

1. **Backup first**: `cp ~/.agent-manager/config.yaml ~/.agent-manager/config.yaml.bak`
2. **Validate after**: `agent-manager config validate`
3. **Use CLI when possible**: Less error-prone

---

## Exporting & Importing

### Export Configuration

```bash
# Export to file
agent-manager config export my-config.yaml

# Export to stdout
agent-manager config export
```

### Import Configuration

```bash
# Import from file
agent-manager config import my-config.yaml
```

**Use cases:**
- Sharing config with teammates
- Backing up before major changes
- Switching between configurations

---

## Example Configurations

### Example 1: Solo Developer

```yaml
hierarchy:
  - name: personal
    url: file:///Users/john/ai-config
    repo_type: local

mergers:
  JsonMerger:
    indent: 2
  MarkdownMerger:
    separator_style: horizontal_rule
```

### Example 2: Corporate Team

```yaml
hierarchy:
  - name: acme-corp
    url: https://github.com/acme/ai-standards
    repo_type: git
  
  - name: backend-team
    url: https://github.com/acme/backend-ai
    repo_type: git
  
  - name: john-westcott
    url: file:///Users/john/my-ai
    repo_type: local

mergers:
  JsonMerger:
    indent: 4
    sort_keys: true
  YamlMerger:
    indent: 2
    width: 100
```

### Example 3: Multi-Client Consultant

```yaml
hierarchy:
  - name: personal-defaults
    url: file:///Users/jane/ai-defaults
    repo_type: local
  
  - name: client-current
    url: https://github.com/clients/client-x-ai
    repo_type: git
  
  - name: overrides
    url: file:///Users/jane/ai-overrides
    repo_type: local

mergers:
  JsonMerger:
    indent: 2
  MarkdownMerger:
    separator_style: heading
```

---

## See Also

- [Getting Started](GETTING_STARTED.md) - Initial setup
- [CLI Reference](CLI_REFERENCE.md) - Command-line usage
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

