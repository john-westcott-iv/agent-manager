"""File URL utilities for agent-manager."""

from pathlib import Path


def is_file_url(url: str) -> bool:
    """Check if a URL is a file:// URL.

    Args:
        url: The URL to check

    Returns:
        True if it's a file:// URL, False otherwise
    """
    # Reject URLs with leading/trailing whitespace
    if url != url.strip():
        return False
    return url.startswith("file://")


def resolve_file_path(url: str) -> Path:
    """Resolve a file:// URL to an absolute path.

    Args:
        url: The file:// URL to resolve (or plain path)

    Returns:
        Resolved absolute Path
    """
    path_str = url[7:] if url.startswith("file://") else url
    return Path(path_str).expanduser().resolve()
