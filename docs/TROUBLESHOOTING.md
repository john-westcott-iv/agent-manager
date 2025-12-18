# Troubleshooting Guide

Common issues and their solutions for Agent Manager.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Repository Issues](#repository-issues)
4. [Merge Issues](#merge-issues)
5. [Agent Plugin Issues](#agent-plugin-issues)
6. [Performance Issues](#performance-issues)
7. [Getting Help](#getting-help)

---

## Installation Issues

### `agent-manager: command not found`

**Problem:** After running `pip install -e .`, the `agent-manager` command isn't available.

**Solutions:**

1. **Check if installed:**
   ```bash
   pip list | grep agent-manager
   ```

2. **Reinstall in editable mode:**
   ```bash
   cd agent_manager/
   pip install -e .
   ```

3. **Check Python path:**
   ```bash
   which python
   which pip
   # Should be from the same environment
   ```

4. **Activate virtual environment (if using one):**
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate  # Windows
   ```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'agent_manager'`

**Solutions:**

1. **Ensure installation:**
   ```bash
   pip install -e agent_manager/
   ```

2. **Check sys.path:**
   ```python
   python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r agent_manager/requirements.txt
   ```

---

## Configuration Issues

### Config File Not Found

**Problem:**
```
Configuration file not found: ~/.agent-manager/config.yaml
```

**Solutions:**

1. **Initialize configuration:**
   ```bash
   agent-manager config init
   ```

2. **Check config location:**
   ```bash
   agent-manager config where
   ```

3. **Verify file exists:**
   ```bash
   ls -la ~/.agent-manager/
   cat ~/.agent-manager/config.yaml
   ```

### Invalid Configuration

**Problem:**
```
Configuration has 2 errors:
  - Hierarchy entry missing required fields: name, url
  - Invalid repo_type 'invalid' for 'organization'
```

**Solutions:**

1. **Validate configuration:**
   ```bash
   agent-manager config validate
   ```

2. **Re-initialize (backup first):**
   ```bash
   cp ~/.agent-manager/config.yaml ~/.agent-manager/config.yaml.bak
   agent-manager config init
   ```

3. **Manually fix:**
   Edit `~/.agent-manager/config.yaml` and ensure each entry has:
   - `name`: string
   - `url`: valid URL
   - `repo_type`: "git" or "local"
   - `repo`: (auto-generated, don't edit manually)

### Permission Denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied: '~/.agent-manager/config.yaml'
```

**Solutions:**

1. **Fix permissions:**
   ```bash
   chmod 600 ~/.agent-manager/config.yaml
   chmod 700 ~/.agent-manager/
   ```

2. **Check ownership:**
   ```bash
   ls -la ~/.agent-manager/
   # Should be owned by your user
   ```

3. **Remove and recreate:**
   ```bash
   rm -rf ~/.agent-manager/
   agent-manager config init
   ```

---

## Repository Issues

### Git Clone Failed

**Problem:**
```
Failed to update 'organization': fatal: repository 'https://github.com/...' not found
```

**Solutions:**

1. **Verify URL:**
   ```bash
   git ls-remote https://github.com/your-org/repo
   ```

2. **Check authentication (for private repos):**
   ```bash
   # SSH
   ssh -T git@github.com

   # HTTPS
   git credential fill
   # Enter: protocol=https
   #        host=github.com
   ```

3. **Use SSH instead of HTTPS:**
   ```bash
   agent-manager config update organization \
     --url git@github.com:your-org/repo.git
   ```

4. **Check network connection:**
   ```bash
   ping github.com
   curl -I https://github.com
   ```

### Git Authentication Failed

**Problem:**
```
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

**Solutions:**

1. **Use SSH URLs:**
   ```bash
   agent-manager config update <name> --url git@github.com:user/repo.git
   ```

2. **Configure Git credentials:**
   ```bash
   git config --global credential.helper store
   # Or use SSH keys
   ssh-keygen -t ed25519 -C "your@email.com"
   # Add to GitHub: https://github.com/settings/keys
   ```

3. **Use personal access token:**
   ```bash
   # In ~/.netrc
   machine github.com
   login your-username
   password ghp_your_token
   ```

### File:// Path Not Found

**Problem:**
```
Failed to validate file:// path: Directory does not exist: /Users/you/missing
```

**Solutions:**

1. **Create directory:**
   ```bash
   mkdir -p /Users/you/my-ai-config
   ```

2. **Use correct path:**
   ```bash
   agent-manager config update personal \
     --url file:///Users/you/my-ai-config
   ```

3. **Verify path:**
   ```bash
   ls -la /Users/you/my-ai-config
   ```

### Repository Update Stuck

**Problem:** `agent-manager update` hangs indefinitely.

**Solutions:**

1. **Check network:**
   ```bash
   curl -I https://github.com
   ```

2. **Force update:**
   ```bash
   agent-manager update --force
   ```

3. **Clear repo cache:**
   ```bash
   rm -rf ~/.agent-manager/repos/
   agent-manager update
   ```

4. **Enable debug output:**
   ```bash
   agent-manager -vv update
   ```

---

## Merge Issues

### Files Not Being Merged

**Problem:** Config files exist in repos but aren't appearing in agent directory.

**Solutions:**

1. **Check exclude patterns:**
   Files might be excluded. Check `AbstractAgent.BASE_EXCLUDE_PATTERNS`.

2. **Enable debug output:**
   ```bash
   agent-manager -vv run
   # Look for "Discovered X files" messages
   ```

3. **Check file location:**
   Files must be in repo root, not subdirectories (unless agent overrides `_discover_files`).

4. **Verify agent directory:**
   ```bash
   # For Claude
   ls -la ~/.claude/

   # Check where your agent writes
   agent-manager run --agent yourplugin -vv
   ```

### Merge Produces Unexpected Results

**Problem:** Merged file doesn't contain expected content.

**Solutions:**

1. **Check hierarchy order:**
   ```bash
   agent-manager config show
   # Last entry has highest priority
   ```

2. **Check merger type:**
   ```bash
   agent-manager mergers list
   # Verify correct merger for file type
   ```

3. **Test mergers individually:**
   ```python
   from agent_manager.plugins.mergers import JsonMerger

   base = '{"a": 1}'
   new = '{"b": 2}'
   result = JsonMerger.merge(base, new, "test", [])
   print(result)  # Should be {"a": 1, "b": 2}
   ```

4. **Check hooks:**
   Hooks might be modifying content. Disable temporarily:
   ```python
   def register_hooks(self):
       pass  # Temporarily disable
   ```

### JSON/YAML Parse Errors

**Problem:**
```
Invalid JSON from 'team': Expecting property name enclosed in double quotes
```

**Solutions:**

1. **Validate file:**
   ```bash
   # JSON
   python -m json.tool config.json

   # YAML
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Check file in repo:**
   ```bash
   cd ~/.agent-manager/repos/team/
   cat config.json
   ```

3. **Fix syntax:**
   - JSON: Use double quotes, no trailing commas
   - YAML: Check indentation (spaces, not tabs)

### Copy Merger Warning

**Problem:**
```
⚠ No merger registered for this file type. Using copy strategy - 'personal' version will be used.
```

**Solutions:**

This is a **warning**, not an error. The last-seen content is used.

1. **Register custom merger:**
   ```python
   class Agent(AbstractAgent):
       def register_mergers(self):
           from .my_merger import MyMerger
           self.merger_registry.register_extension(".myext", MyMerger)
   ```

2. **Ignore warning:**
   If copy behavior is desired (last source wins), you can ignore this.

---

## Agent Plugin Issues

### Agent Not Discovered

**Problem:** `agent-manager run --agent myplugin` says "Unknown agent".

**Solutions:**

1. **Check package name:**
   Must start with `ai_agent_`:
   ```bash
   ls | grep ai_agent_
   ```

2. **Check installation:**
   ```bash
   pip list | grep ai_agent_myplugin
   ```

3. **Reinstall:**
   ```bash
   pip install -e ai_agent_myplugin/
   ```

4. **Verify Agent class:**
   ```python
   # ai_agent_myplugin/__init__.py
   from .myplugin import Agent
   __all__ = ["Agent"]
   ```

5. **Check for errors:**
   ```bash
   python -c "from ai_agent_myplugin import Agent; print(Agent)"
   ```

### Agent Crashes

**Problem:** `agent-manager run` crashes with exception.

**Solutions:**

1. **Enable debug output:**
   ```bash
   agent-manager -vv run --agent myplugin
   ```

2. **Check agent __init__:**
   ```python
   def __init__(self):
       super().__init__()  # Must call parent __init__
       # Your initialization
   ```

3. **Check hooks:**
   Ensure hooks return content:
   ```python
   def hook(self, content, entry, file_path):
       # ... processing ...
       return content  # Don't forget!
   ```

4. **Test agent independently:**
   ```python
   from ai_agent_myplugin import Agent

   agent = Agent()
   config = {...}  # Mock config
   agent.update(config)
   ```

### Hook Not Running

**Problem:** Registered hook doesn't execute.

**Solutions:**

1. **Check pattern:**
   ```python
   # Pattern must match filename
   self.pre_merge_hooks["*.json"] = hook  # Matches: config.json
   self.pre_merge_hooks["config.json"] = hook  # Matches: config.json only
   ```

2. **Check hook signature:**
   ```python
   # Pre-merge
   def hook(self, content: str, entry: dict, file_path: Path) -> str:
       ...

   # Post-merge
   def hook(self, content: str, entry: dict, file_path: Path, sources: list[str]) -> str:
       ...
   ```

3. **Return content:**
   ```python
   def hook(self, content, entry, file_path):
       modified = content.upper()
       return modified  # Must return!
   ```

4. **Enable debug:**
   ```bash
   agent-manager -vv run
   # Should see "Running pre-merge hook..." messages
   ```

---

## Performance Issues

### Slow Repository Updates

**Problem:** `agent-manager update` takes a long time.

**Solutions:**

1. **Git repos use shallow clone by default** (depth=1), should be fast.

2. **Check network speed:**
   ```bash
   time git clone --depth 1 https://github.com/your-org/repo /tmp/test
   ```

3. **Use local repos for testing:**
   ```bash
   agent-manager config update <name> --url file:///local/path
   ```

4. **Skip update if not needed:**
   ```bash
   # Don't use --force unnecessarily
   agent-manager update  # Only updates if needed
   ```

### Slow Merging

**Problem:** `agent-manager run` is slow during merge phase.

**Solutions:**

1. **Reduce file count:**
   Use exclude patterns to skip unnecessary files.

2. **Optimize hooks:**
   Avoid expensive operations in hooks (API calls, complex parsing).

3. **Profile:**
   ```bash
   python -m cProfile -s cumtime \
     $(which agent-manager) run --agent myplugin
   ```

### High Memory Usage

**Problem:** Agent Manager uses too much memory.

**Solutions:**

1. **Large files:**
   Avoid merging very large files. Add to exclude patterns.

2. **Many files:**
   Merging happens sequentially to keep memory usage low.

3. **Hooks creating state:**
   Ensure hooks don't accumulate large data structures.

---

## Common Error Messages

### `ConfigError: Configuration has X errors`

**See:** [Invalid Configuration](#invalid-configuration)

### `ModuleNotFoundError: No module named ...`

**See:** [Import Errors](#import-errors)

### `PermissionError: [Errno 13]`

**See:** [Permission Denied](#permission-denied)

### `fatal: repository '...' not found`

**See:** [Git Clone Failed](#git-clone-failed)

### `Invalid JSON/YAML from '...': ...`

**See:** [JSON/YAML Parse Errors](#jsonya
ml-parse-errors)

---

## Debug Checklist

When something isn't working:

1. **Enable verbose output:**
   ```bash
   agent-manager -vv <command>
   ```

2. **Validate configuration:**
   ```bash
   agent-manager config validate
   ```

3. **Check config location:**
   ```bash
   agent-manager config where
   ls -la ~/.agent-manager/
   ```

4. **Verify repos are accessible:**
   ```bash
   agent-manager update -vv
   ```

5. **Check agent installation:**
   ```bash
   pip list | grep ai_agent_
   python -c "from ai_agent_<name> import Agent"
   ```

6. **Test merge:**
   ```bash
   agent-manager -vv run --agent <name>
   # Check agent directory for merged files
   ```

7. **Review logs:**
   ```bash
   # If you've set up logging
   tail -f ~/.agent-manager/logs/agent-manager.log
   ```

---

## Getting Help

### Check Documentation

- [Getting Started](GETTING_STARTED.md)
- [Configuration Reference](CONFIGURATION.md)
- [CLI Reference](CLI_REFERENCE.md)
- [Architecture Overview](ARCHITECTURE.md)

### Enable Debug Output

```bash
agent-manager -vv <command>
```

### Check GitHub Issues

Search existing issues: https://github.com/john-westcott-iv/agent-manager/issues

### Create an Issue

Include:
1. **Command you ran:**
   ```bash
   agent-manager -vv run --agent claude
   ```

2. **Full error message:**
   ```
   (Copy complete error output)
   ```

3. **Environment:**
   ```bash
   python --version
   pip list | grep agent-manager
   uname -a  # macOS/Linux
   ```

4. **Configuration (sanitized):**
   ```bash
   agent-manager config show
   # Remove any sensitive URLs
   ```

5. **Steps to reproduce:**
   1. Install agent-manager
   2. Run command X
   3. See error Y

### Community Help

- GitHub Discussions: https://github.com/john-westcott-iv/agent-manager/discussions
- Stack Overflow: Tag questions with `agent-manager`

---

## FAQ

### Q: Can I use Agent Manager without Git?

**A:** Yes! Use `file://` URLs for all hierarchy levels:

```yaml
hierarchy:
  - name: personal
    url: file:///Users/you/my-configs
    repo_type: local
```

### Q: Can I have multiple agents?

**A:** Yes! Install multiple `ai_agent_*` packages:

```bash
pip install -e ai_agent_claude/
pip install -e ai_agent_cursor/
pip install -e ai_agent_chatgpt/

# Run all
agent-manager run

# Run specific one
agent-manager run --agent claude
```

### Q: How do I reset everything?

**A:**

```bash
# Remove all config and cache
rm -rf ~/.agent-manager/

# Remove agent directories (if needed)
rm -rf ~/.claude/
rm -rf ~/.cursor/

# Reinitialize
agent-manager config init
```

### Q: Can I use this in CI/CD?

**A:** Yes! Set config via environment or import:

```bash
# In CI
export AGENT_MANAGER_CONFIG_DIR=/tmp/agent-config
agent-manager config import my-config.yaml
agent-manager run
```

### Q: How do I contribute?

**A:** See [Contributing Guide](../../README.md#-contributing)

---

## Still Having Issues?

If you're still stuck:
1. Enable debug output: `agent-manager -vv <command>`
2. Check all documentation
3. Search GitHub issues
4. Create a new issue with full details

We're here to help! 🚀

