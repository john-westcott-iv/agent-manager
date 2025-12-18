"""Abstract base class for content mergers."""

from abc import ABC, abstractmethod

from agent_manager.output import MessageType, VerbosityLevel, message


class AbstractMerger(ABC):
    """Base class for content mergers with self-documenting preferences."""

    # Subclasses should define which file extensions they handle
    FILE_EXTENSIONS: list[str] = []

    @classmethod
    @abstractmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Merge new content into base content.

        Args:
            base: Existing merged content
            new: New content to merge in
            source: Name of source adding new content
            sources: List of all sources that contributed to base
            **settings: Merger-specific settings from config

        Returns:
            Merged content
        """
        pass

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define configurable preferences for this merger.

        Returns:
            Dict mapping preference names to their schema:
            {
                "preference_name": {
                    "type": "int|str|bool|float",
                    "default": <value>,
                    "description": "Help text",
                    "min": <optional min for int/float>,
                    "max": <optional max for int/float>,
                    "choices": <optional list for str>
                }
            }

        Example:
            {
                "indent": {
                    "type": "int",
                    "default": 2,
                    "description": "Number of spaces for indentation",
                    "min": 0,
                    "max": 8
                }
            }
        """
        return {}  # Default: no preferences

    @classmethod
    def _validate_settings(cls, settings: dict) -> None:
        """Validate settings and warn about unknown ones.

        Args:
            settings: Settings dict to validate
        """
        prefs = cls.merge_preferences()

        for key in settings:
            if key not in prefs:
                message(
                    f"{cls.__name__}: Ignoring unknown setting '{key}'. "
                    f"Valid settings: {', '.join(prefs.keys()) if prefs else 'none'}",
                    MessageType.DEBUG,
                    VerbosityLevel.DEBUG,
                )
