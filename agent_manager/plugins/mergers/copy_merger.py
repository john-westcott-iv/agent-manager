"""Copy merger - last source wins (for binary/unknown file types)."""

from agent_manager.output import MessageType, VerbosityLevel, message

from .abstract_merger import AbstractMerger


class CopyMerger(AbstractMerger):
    """Copy merger that uses the last source's content (last-wins strategy).

    This is the default fallback for file types without a specific merger.
    Useful for binary files, images, archives, or any files that can't be
    intelligently merged.
    """

    @classmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Use last source's content (last-wins strategy).

        Args:
            base: Existing merged content (ignored)
            new: New content to use
            source: Name of source adding new content
            sources: List of all sources

        Returns:
            The new content (last source wins)
        """
        cls._validate_settings(settings)

        # Warn user that we're just copying
        if len(sources) > 0:  # Only warn if there were previous sources
            message(
                f"No merger registered for this file type. Using copy strategy - '{source}' version will be used.",
                MessageType.WARNING,
                VerbosityLevel.ALWAYS,
            )
            message(
                "Consider creating a custom merger if you need intelligent merging for this file type.",
                MessageType.INFO,
                VerbosityLevel.EXTRA_VERBOSE,
            )

        return new  # Last source wins
