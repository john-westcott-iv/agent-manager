"""Local directory repository implementation."""

from pathlib import Path

from agent_manager.output import MessageType, VerbosityLevel, message
from agent_manager.plugins.repos.abstract_repo import AbstractRepo
from agent_manager.utils import is_file_url, resolve_file_path


class LocalRepo(AbstractRepo):
    """Manages a local file:// directory."""

    REPO_TYPE = "file"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this is a file:// URL.

        Args:
            url: The URL to check

        Returns:
            True if this is a file:// URL
        """
        return is_file_url(url)

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate that the file path exists and is a directory.

        Args:
            url: The file:// URL to validate

        Returns:
            True if the path exists and is a directory, False otherwise
        """
        try:
            path = resolve_file_path(url)

            if not path.exists():
                message(f"Path does not exist: {path}", MessageType.ERROR, VerbosityLevel.ALWAYS)
                return False

            if not path.is_dir():
                message(f"Path is not a directory: {path}", MessageType.ERROR, VerbosityLevel.ALWAYS)
                return False

            message(f"File URL validated: {url} -> {path}", MessageType.DEBUG, VerbosityLevel.DEBUG)
            return True
        except Exception as e:
            message(f"Invalid file URL: {e}", MessageType.ERROR, VerbosityLevel.ALWAYS)
            return False

    def __init__(self, name: str, url: str, repos_dir: Path):
        """Initialize a local directory repository.

        Args:
            name: Name of the hierarchy level
            url: File URL (file://path/to/dir)
            repos_dir: Base directory (not used for local repos)
        """
        super().__init__(name, url, repos_dir)
        self.local_path = resolve_file_path(url)
        message(f"Using local directory for '{self.name}': {self.local_path}", MessageType.DEBUG, VerbosityLevel.DEBUG)

    def needs_update(self) -> bool:
        """Check if the repository needs to be updated.

        For local directories, updates are never needed.

        Returns:
            Always returns False
        """
        return False

    def update(self) -> None:
        """Update the local repository.

        For local directories, this is a no-op as there's nothing to update.
        """
        message(f"Skipping update for '{self.name}' (local directory)", MessageType.DEBUG, VerbosityLevel.DEBUG)

    def get_display_url(self) -> str:
        """Get the resolved absolute path for display.

        Returns:
            The resolved absolute path as a string
        """
        return str(self.local_path)
