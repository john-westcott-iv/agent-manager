# Creating Custom Repository Types

This guide shows you how to add new repository backend types to Agent Manager (e.g., S3, HTTP, database).

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [AbstractRepo Interface](#abstractrepo-interface)
4. [Implementation Guide](#implementation-guide)
5. [Testing](#testing)
6. [Real-World Examples](#real-world-examples)

---

## Overview

A **repository backend** handles fetching and updating configuration sources. Agent Manager includes two built-in types:
- **GitRepo**: Clones/fetches from Git repositories
- **LocalRepo**: Uses local `file://` directories

You can add your own types (S3, HTTP, database, etc.) by implementing the `AbstractRepo` interface.

### Auto-Discovery

Repository types are **automatically discovered** at runtime. Just create a subclass of `AbstractRepo` in the `agent_manager/plugins/repos/` directory (or in a plugin package) and Agent Manager will find it.

---

## Quick Start

### Step 1: Create Your Repo Class

Create `agent_manager/plugins/repos/my_repo.py`:

```python
"""My custom repository backend."""

from pathlib import Path
from agent_manager.plugins.repos import AbstractRepo
from agent_manager import output


class MyRepo(AbstractRepo):
    """Repository backend for my custom storage."""

    # Unique identifier for this repo type
    REPO_TYPE = "my_storage"

    def __init__(self, url: str, name: str, cache_dir: Path):
        """Initialize repository.

        Args:
            url: URL to the repository
            name: Name of this hierarchy level
            cache_dir: Directory for caching downloaded configs
        """
        super().__init__(url, name, cache_dir)
        # Your initialization here

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this repo can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this repo can handle this URL
        """
        return url.startswith("mystorage://")

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        """Validate the URL and return status.

        Args:
            url: URL to validate

        Returns:
            (is_valid, error_message)
        """
        if not url.startswith("mystorage://"):
            return False, "URL must start with 'mystorage://'"

        # Add your validation logic here
        try:
            # Check if resource is accessible
            # ...
            return True, ""
        except Exception as e:
            return False, str(e)

    def get_path(self) -> Path:
        """Get local path to repository contents.

        Returns:
            Path to local directory containing configs
        """
        # Return cache directory path
        return self._cache_path

    def needs_update(self) -> bool:
        """Check if repository needs updating.

        Returns:
            True if update is needed
        """
        # Implement your logic here
        # E.g., check if local cache is stale
        return True

    def update(self) -> None:
        """Update repository from remote source."""
        output.info(f"Downloading from {self.url}...")

        # Your download/sync logic here
        # ...

        output.success(f"Downloaded {self.name}")

    def get_display_url(self, resolve_paths: bool = False) -> str:
        """Get display-friendly URL.

        Args:
            resolve_paths: Whether to resolve paths (not applicable here)

        Returns:
            URL string for display
        """
        return self.url

    @property
    def _cache_path(self) -> Path:
        """Get cache directory for this repo."""
        # Cache in ~/.agent-manager/repos/<name>/
        cache = self.cache_dir / self.name
        cache.mkdir(parents=True, exist_ok=True)
        return cache
```

### Step 2: That's It!

Agent Manager will automatically discover your new repo type. Users can now use it:

```yaml
hierarchy:
  - name: my-configs
    url: mystorage://bucket/configs
    repo_type: my_storage
```

---

## AbstractRepo Interface

### Required Class Attributes

```python
class MyRepo(AbstractRepo):
    # Unique identifier (appears in config file as "repo_type")
    REPO_TYPE: str = "my_storage"
```

### Required Methods

#### can_handle_url(url: str) -> bool

Determine if this repo type can handle the given URL.

```python
@classmethod
def can_handle_url(cls, url: str) -> bool:
    """Check if URL is for this repo type.

    Called during:
    - Config initialization (to detect repo type)
    - URL validation

    Args:
        url: URL to check

    Returns:
        True if this repo can handle this URL
    """
    return url.startswith("mystorage://")
```

**Notes:**
- Multiple repos can claim the same URL (user will be prompted to choose)
- Be specific to avoid false positives

#### validate_url(url: str) -> tuple[bool, str]

Validate that a URL is well-formed and accessible.

```python
@classmethod
def validate_url(cls, url: str) -> tuple[bool, str]:
    """Validate URL format and accessibility.

    Called during:
    - Config initialization
    - Adding new hierarchy levels
    - Config validation

    Args:
        url: URL to validate

    Returns:
        (is_valid, error_message)
        - is_valid: True if URL is valid
        - error_message: Empty string if valid, error description if not
    """
    if not cls.can_handle_url(url):
        return False, "Invalid URL format"

    try:
        # Check if resource exists/is accessible
        # Don't download everything, just check availability
        return True, ""
    except Exception as e:
        return False, f"Cannot access resource: {e}"
```

**Notes:**
- Should be fast (don't download entire repo)
- Should check both format and accessibility

#### get_path() -> Path

Return local filesystem path to repository contents.

```python
def get_path(self) -> Path:
    """Get local path where configs are stored.

    Called by:
    - Agent.merge_configurations() to discover files

    Returns:
        Path to directory containing configuration files
    """
    return self._cache_path
```

**Notes:**
- Must return a Path to an actual directory
- Directory should contain config files ready to be merged

#### needs_update() -> bool

Check if repository needs updating from remote source.

```python
def needs_update(self) -> bool:
    """Check if local cache is stale.

    Called during:
    - agent-manager update
    - agent-manager run (automatic update check)

    Returns:
        True if update() should be called
    """
    if not self.get_path().exists():
        return True  # Need initial download

    # Check if remote has changes
    # E.g., compare timestamps, check ETag, etc.
    return self._is_cache_stale()
```

**Notes:**
- Should be fast (don't download everything)
- Return `True` if unsure (update() will handle it)

#### update() -> None

Update local cache from remote source.

```python
def update(self) -> None:
    """Download/sync from remote source.

    Called during:
    - agent-manager update
    - agent-manager run (if needs_update() returns True)

    Raises:
        Exception: If update fails
    """
    output.info(f"Updating {self.name} from {self.url}...")

    try:
        # Download/sync logic here
        # ...

        output.success(f"Updated {self.name}")
    except Exception as e:
        output.error(f"Failed to update {self.name}: {e}")
        raise
```

**Notes:**
- Should be idempotent (can be called multiple times)
- Use `output.*` for user feedback

#### get_display_url(resolve_paths: bool = False) -> str

Return URL for display in CLI output.

```python
def get_display_url(self, resolve_paths: bool = False) -> str:
    """Get user-friendly display URL.

    Called by:
    - agent-manager config show

    Args:
        resolve_paths: If True, resolve/expand paths
                       (mainly for LocalRepo)

    Returns:
        URL string suitable for display
    """
    return self.url
```

---

## Implementation Guide

### Example: S3 Repository

```python
"""Amazon S3 repository backend."""

import boto3
from pathlib import Path
from agent_manager.plugins.repos import AbstractRepo
from agent_manager import output


class S3Repo(AbstractRepo):
    """Repository backend for Amazon S3."""

    REPO_TYPE = "s3"

    def __init__(self, url: str, name: str, cache_dir: Path):
        super().__init__(url, name, cache_dir)

        # Parse S3 URL: s3://bucket/prefix/
        self.bucket, self.prefix = self._parse_s3_url(url)

        # Initialize S3 client
        self.s3 = boto3.client("s3")

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        return url.startswith("s3://")

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        if not url.startswith("s3://"):
            return False, "URL must start with 's3://'"

        try:
            bucket, prefix = cls._parse_s3_url(url)

            # Check if bucket exists and is accessible
            s3 = boto3.client("s3")
            s3.head_bucket(Bucket=bucket)

            return True, ""
        except Exception as e:
            return False, f"Cannot access S3 bucket: {e}"

    def get_path(self) -> Path:
        return self._cache_path

    def needs_update(self) -> bool:
        cache = self._cache_path

        if not cache.exists():
            return True  # Need initial download

        # Check if S3 has newer files
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )

            if "Contents" not in response:
                return False

            # Compare timestamps
            for obj in response["Contents"]:
                key = obj["Key"]
                local_file = cache / key.removeprefix(self.prefix)

                if not local_file.exists():
                    return True

                local_mtime = local_file.stat().st_mtime
                s3_mtime = obj["LastModified"].timestamp()

                if s3_mtime > local_mtime:
                    return True

            return False
        except Exception:
            return True  # If check fails, assume update needed

    def update(self) -> None:
        output.info(f"Downloading from S3: {self.bucket}/{self.prefix}")

        cache = self._cache_path
        cache.mkdir(parents=True, exist_ok=True)

        try:
            # List all objects with prefix
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )

            if "Contents" not in response:
                output.warning("No files found in S3 prefix")
                return

            # Download each file
            for obj in response["Contents"]:
                key = obj["Key"]
                relative_path = key.removeprefix(self.prefix)
                local_file = cache / relative_path

                # Create parent directories
                local_file.parent.mkdir(parents=True, exist_ok=True)

                # Download file
                output.debug(f"Downloading {key}...")
                self.s3.download_file(self.bucket, key, str(local_file))

            output.success(f"Downloaded {len(response['Contents'])} files")
        except Exception as e:
            output.error(f"Failed to download from S3: {e}")
            raise

    def get_display_url(self, resolve_paths: bool = False) -> str:
        return self.url

    @property
    def _cache_path(self) -> Path:
        cache = self.cache_dir / self.name
        cache.mkdir(parents=True, exist_ok=True)
        return cache

    @staticmethod
    def _parse_s3_url(url: str) -> tuple[str, str]:
        """Parse S3 URL into bucket and prefix.

        Args:
            url: S3 URL (e.g., s3://bucket/prefix/)

        Returns:
            (bucket, prefix)
        """
        parts = url.removeprefix("s3://").split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        return bucket, prefix
```

### Example: HTTP Repository

```python
"""HTTP/HTTPS repository backend."""

import requests
from pathlib import Path
from agent_manager.plugins.repos import AbstractRepo
from agent_manager import output


class HttpRepo(AbstractRepo):
    """Repository backend for HTTP/HTTPS endpoints."""

    REPO_TYPE = "http"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        try:
            response = requests.head(url, timeout=5)
            response.raise_for_status()
            return True, ""
        except Exception as e:
            return False, str(e)

    def get_path(self) -> Path:
        return self._cache_path

    def needs_update(self) -> bool:
        cache_file = self._cache_path / "config.json"

        if not cache_file.exists():
            return True

        # Check ETag or Last-Modified headers
        try:
            response = requests.head(self.url, timeout=5)
            etag = response.headers.get("ETag")

            # Compare with cached ETag
            etag_file = self._cache_path / ".etag"
            if etag_file.exists():
                cached_etag = etag_file.read_text()
                return etag != cached_etag

            return True
        except Exception:
            return True

    def update(self) -> None:
        output.info(f"Downloading from {self.url}...")

        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()

            cache = self._cache_path
            cache.mkdir(parents=True, exist_ok=True)

            # Save content
            config_file = cache / "config.json"
            config_file.write_bytes(response.content)

            # Save ETag for future checks
            if "ETag" in response.headers:
                etag_file = cache / ".etag"
                etag_file.write_text(response.headers["ETag"])

            output.success(f"Downloaded {len(response.content)} bytes")
        except Exception as e:
            output.error(f"Failed to download: {e}")
            raise

    @property
    def _cache_path(self) -> Path:
        cache = self.cache_dir / self.name
        cache.mkdir(parents=True, exist_ok=True)
        return cache
```

---

## Testing

### Unit Tests

```python
import pytest
from pathlib import Path
from my_repo import MyRepo


def test_can_handle_url():
    assert MyRepo.can_handle_url("mystorage://bucket/path")
    assert not MyRepo.can_handle_url("https://example.com")


def test_validate_url():
    is_valid, error = MyRepo.validate_url("mystorage://bucket/path")
    assert is_valid
    assert error == ""


def test_repo_initialization(tmp_path):
    repo = MyRepo(
        url="mystorage://bucket/path",
        name="test",
        cache_dir=tmp_path
    )
    assert repo.url == "mystorage://bucket/path"
    assert repo.name == "test"
    assert repo.get_path().exists()


def test_needs_update(tmp_path):
    repo = MyRepo("mystorage://bucket", "test", tmp_path)

    # Initially needs update
    assert repo.needs_update()

    # After update, may not need it
    repo.update()
    # ... (depends on your logic)
```

### Integration Tests

```bash
# Create test repo
python -c "
from my_repo import MyRepo
from pathlib import Path

repo = MyRepo('mystorage://test', 'test', Path('/tmp'))
repo.update()

print(repo.get_path())
print(list(repo.get_path().glob('*')))
"
```

---

## Real-World Examples

### GitRepo (Built-in)

See `agent_manager/plugins/repos/git_repo.py`:
- Uses GitPython library
- Implements shallow cloning
- Handles fetch/pull logic

### LocalRepo (Built-in)

See `agent_manager/plugins/repos/local_repo.py`:
- Simplest possible implementation
- Just resolves `file://` paths
- `needs_update()` always returns False

---

## Best Practices

### 1. Cache Aggressively

Don't re-download on every run:

```python
def needs_update(self) -> bool:
    # Check timestamps, ETags, etc.
    # Only return True if remote has changes
    pass
```

### 2. Handle Errors Gracefully

```python
def validate_url(cls, url: str) -> tuple[bool, str]:
    try:
        # Validation logic
        return True, ""
    except Exception as e:
        return False, f"Validation failed: {e}"
```

### 3. Provide Feedback

Use the `output` module:

```python
from agent_manager import output

output.info("Starting download...")
output.debug("Downloading file...")
output.success("Download complete!")
output.warning("File not found")
output.error("Download failed")
```

### 4. Use `_cache_path` Helper

```python
@property
def _cache_path(self) -> Path:
    cache = self.cache_dir / self.name
    cache.mkdir(parents=True, exist_ok=True)
    return cache
```

### 5. Be Specific with `can_handle_url`

Avoid false positives:

```python
# Good
def can_handle_url(cls, url: str) -> bool:
    return url.startswith("s3://")

# Bad (too broad)
def can_handle_url(cls, url: str) -> bool:
    return "/" in url  # Matches almost everything!
```

---

## See Also

- [Architecture Overview](ARCHITECTURE.md) - System design
- [Examples](../repos/) - Built-in repo implementations
- [Configuration](CONFIGURATION.md) - How repos are used

