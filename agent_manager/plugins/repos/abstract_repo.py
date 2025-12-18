"""Abstract base class for repository implementations."""

from abc import ABC, abstractmethod
from pathlib import Path


class AbstractRepo(ABC):
    """Abstract base class for repository management."""

    # Subclasses must define this to identify their type
    REPO_TYPE: str = "unknown"

    def __init__(self, name: str, url: str, repos_dir: Path):
        """Initialize a repository.

        Args:
            name: Name of the hierarchy level
            url: Repository URL
            repos_dir: Base directory where repos are stored
        """
        self.name = name
        self.url = url
        self.repos_dir = repos_dir
        self.local_path: Path

    @classmethod
    @abstractmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this repository type can handle the given URL.

        Args:
            url: The URL to check

        Returns:
            True if this repo type can handle the URL, False otherwise
        """
        pass

    @classmethod
    @abstractmethod
    def validate_url(cls, url: str) -> bool:
        """Validate that the URL is accessible and valid.

        This method should check if the repository URL is not only
        syntactically correct (via can_handle_url), but also accessible.
        For example:
        - Git repos: Check if git ls-remote succeeds
        - File repos: Check if the path exists
        - S3 repos: Check if the bucket is accessible

        Args:
            url: The URL to validate

        Returns:
            True if the URL is valid and accessible, False otherwise
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the repository.

        Should fetch/pull latest changes for remote repositories.
        May be a no-op for local repositories.
        """
        pass

    def get_path(self) -> Path:
        """Get the local path to the repository.

        Returns:
            Path to the local repository
        """
        return self.local_path

    def exists(self) -> bool:
        """Check if the repository exists locally.

        Returns:
            True if the repository exists, False otherwise
        """
        return self.local_path.exists()

    @abstractmethod
    def needs_update(self) -> bool:
        """Check if the repository needs to be updated.

        Returns:
            True if update() should be called, False otherwise
        """
        pass

    def get_display_url(self) -> str:
        """Get a human-friendly display version of the URL.

        This is used for showing resolved paths or formatted URLs
        to users. Default implementation returns the original URL.
        Subclasses can override to provide more meaningful display.

        Returns:
            String representation of the URL for display purposes
        """
        return self.url

    def __str__(self) -> str:
        """String representation of the repository.

        Returns:
            String describing the repository
        """
        repo_type = self.__class__.__name__.replace("Repo", "").lower()
        return f"Repo(name='{self.name}', type={repo_type}, path={self.local_path})"

    def __repr__(self) -> str:
        """Developer representation of the repository.

        Returns:
            String for debugging
        """
        return f"{self.__class__.__name__}(name='{self.name}', url='{self.url}', local_path={self.local_path})"
