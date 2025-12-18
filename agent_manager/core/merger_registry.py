"""Registry for managing content mergers."""

from pathlib import Path

from agent_manager.output import MessageType, VerbosityLevel, message
from agent_manager.plugins.mergers.abstract_merger import AbstractMerger
from agent_manager.plugins.mergers.copy_merger import CopyMerger


class MergerRegistry:
    """Registry for managing content mergers with filename and extension-based lookup."""

    def __init__(self):
        """Initialize the merger registry."""
        self.filename_mergers: dict[str, type[AbstractMerger]] = {}
        self.extension_mergers: dict[str, type[AbstractMerger]] = {}
        self.default_merger: type[AbstractMerger] = CopyMerger

    def register_filename(self, filename: str, merger: type[AbstractMerger]) -> None:
        """Register a merger for a specific filename.

        Args:
            filename: Exact filename to match (e.g., "mcp.json")
            merger: Merger class to use for this filename
        """
        self.filename_mergers[filename] = merger
        message(f"Registered {merger.__name__} for filename: {filename}", MessageType.DEBUG, VerbosityLevel.DEBUG)

    def register_extension(self, extension: str, merger: type[AbstractMerger]) -> None:
        """Register a merger for a file extension.

        Args:
            extension: File extension to match (e.g., ".json", ".md")
            merger: Merger class to use for this extension
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        self.extension_mergers[extension] = merger
        message(f"Registered {merger.__name__} for extension: {extension}", MessageType.DEBUG, VerbosityLevel.DEBUG)

    def set_default_merger(self, merger: type[AbstractMerger]) -> None:
        """Set the default fallback merger.

        Args:
            merger: Merger class to use as default fallback
        """
        self.default_merger = merger
        message(f"Set default merger to: {merger.__name__}", MessageType.DEBUG, VerbosityLevel.DEBUG)

    def get_merger(self, file_path: Path) -> type[AbstractMerger]:
        """Get the appropriate merger for a file.

        Priority:
        1. Exact filename match (e.g., "mcp.json")
        2. File extension match (e.g., ".json")
        3. Default fallback (CopyMerger)

        Args:
            file_path: Path to the file

        Returns:
            Merger class to use
        """
        filename = file_path.name
        extension = file_path.suffix

        # Priority 1: Exact filename match
        if filename in self.filename_mergers:
            merger = self.filename_mergers[filename]
            message(f"Using {merger.__name__} for filename: {filename}", MessageType.DEBUG, VerbosityLevel.DEBUG)
            return merger

        # Priority 2: Extension match
        if extension in self.extension_mergers:
            merger = self.extension_mergers[extension]
            message(f"Using {merger.__name__} for extension: {extension}", MessageType.DEBUG, VerbosityLevel.DEBUG)
            return merger

        # Priority 3: Default fallback
        message(
            f"No specific merger for {filename}, using default: {self.default_merger.__name__}",
            MessageType.DEBUG,
            VerbosityLevel.DEBUG,
        )
        return self.default_merger

    def list_registered_mergers(self) -> dict[str, list[str]]:
        """Get a summary of all registered mergers.

        Returns:
            Dict with 'filenames', 'extensions', and 'default' keys
        """
        return {
            "filenames": list(self.filename_mergers.keys()),
            "extensions": list(self.extension_mergers.keys()),
            "default": self.default_merger.__name__,
        }
