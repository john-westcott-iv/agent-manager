"""Text merger with simple concatenation and source markers."""

from .abstract_merger import AbstractMerger


class TextMerger(AbstractMerger):
    """Merger for plain text files with source markers."""

    FILE_EXTENSIONS = [".txt"]

    @classmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Simple text concatenation with source markers.

        Args:
            base: Existing text content
            new: New text content to merge
            source: Name of source adding new content
            sources: List of all sources

        Returns:
            Concatenated text with source markers
        """
        cls._validate_settings(settings)

        separator = f"\n\n# --- From: {source} ---\n\n"
        return base + separator + new
