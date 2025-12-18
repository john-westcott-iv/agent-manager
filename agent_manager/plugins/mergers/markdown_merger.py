"""Markdown merger with AI override markers."""

from .abstract_merger import AbstractMerger


class MarkdownMerger(AbstractMerger):
    """Merger for Markdown files with AI-friendly override markers."""

    FILE_EXTENSIONS = [".md", ".markdown"]

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define Markdown merger preferences."""
        return {
            "separator_style": {
                "type": "str",
                "default": "horizontal_rule",
                "description": "Style of separator between sources",
                "choices": ["horizontal_rule", "heading", "comment"],
            },
        }

    @classmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Merge Markdown with AI override markers.

        Adds clear markers to indicate that content from higher priority sources
        should override earlier content when interpreted by AI agents.

        Args:
            base: Existing markdown content
            new: New markdown content to merge
            source: Name of source adding new content
            sources: List of all sources

        Returns:
            Merged markdown with override markers
        """
        cls._validate_settings(settings)

        # Get preferences with defaults
        prefs = cls.merge_preferences()
        separator_style = settings.get("separator_style", prefs["separator_style"]["default"])

        # Generate separator based on style
        if separator_style == "horizontal_rule":
            separator = "\n\n---\n"
        elif separator_style == "heading":
            separator = f"\n\n## Configuration from: {source}\n\n"
        else:  # comment
            separator = f"\n\n<!-- Configuration from: {source} -->\n\n"

        # Add AI override note
        override_note = (
            f"**Note to AI Agent:** Given all of the previous information, "
            f"the following from '{source}' overrides anything you already know.\n"
            "---\n\n"
        )

        return base + separator + override_note + new
