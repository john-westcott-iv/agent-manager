"""Base dictionary merger with pluggable merge strategies."""

from typing import Any

from agent_manager.output import MessageType, VerbosityLevel, message

from .abstract_merger import AbstractMerger


class MergeStrategy:
    """Defines how to merge different types of values."""

    @staticmethod
    def merge_dict(base: dict, new: dict, path: str = "") -> dict:
        """Strategy for merging dictionaries.

        Default: Deep merge (recursively merge nested dicts).

        Args:
            base: Base dictionary
            new: New dictionary (takes precedence)
            path: Current path in the nested structure (for debugging)

        Returns:
            Merged dictionary
        """
        merged = base.copy()
        for key, value in new.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = MergeStrategy.merge_dict(merged[key], value, f"{path}.{key}" if path else key)
            else:
                # New value overwrites
                merged[key] = value
        return merged

    @staticmethod
    def merge_list(base: list, new: list, path: str = "") -> list:
        """Strategy for merging lists.

        Default: Replace (new list overwrites base list).

        Args:
            base: Base list
            new: New list
            path: Current path in the nested structure (for debugging)

        Returns:
            Merged list
        """
        # Default: Replace strategy
        return new

    @staticmethod
    def merge_value(base: Any, new: Any, path: str = "") -> Any:
        """Strategy for merging primitive values.

        Default: Replace (new value overwrites base value).

        Args:
            base: Base value
            new: New value
            path: Current path in the nested structure (for debugging)

        Returns:
            Merged value
        """
        # Default: New value wins
        return new


class ExtendListStrategy(MergeStrategy):
    """Merge strategy that extends lists instead of replacing them."""

    @staticmethod
    def merge_list(base: list, new: list, path: str = "") -> list:
        """Extend base list with new items (removing duplicates).

        Args:
            base: Base list
            new: New list
            path: Current path in the nested structure

        Returns:
            Extended list with unique items
        """
        # Extend and deduplicate (preserving order)
        result = base.copy()
        for item in new:
            if item not in result:
                result.append(item)
        return result


class ReplaceStrategy(MergeStrategy):
    """Merge strategy that replaces everything (no deep merging)."""

    @staticmethod
    def merge_dict(base: dict, new: dict, path: str = "") -> dict:
        """Replace base dict entirely with new dict.

        Args:
            base: Base dictionary (ignored)
            new: New dictionary
            path: Current path in the nested structure

        Returns:
            New dictionary (base is discarded)
        """
        return new


class DictMerger(AbstractMerger):
    """Base merger for dictionary-based formats (JSON, YAML, etc.) with pluggable strategies.

    Subclasses should:
    1. Define FILE_EXTENSIONS
    2. Implement serialize() and deserialize() methods
    3. Optionally override get_merge_strategy() to customize merge behavior
    """

    @classmethod
    def get_merge_strategy(cls) -> type[MergeStrategy]:
        """Get the merge strategy for this merger.

        Override this method to provide a custom merge strategy.

        Returns:
            Merge strategy class to use
        """
        return MergeStrategy  # Default strategy

    @classmethod
    def merge(cls, base: str, new: str, source: str, sources: list[str], **settings) -> str:
        """Merge dictionary-based content with pluggable strategies.

        Args:
            base: Existing content (serialized)
            new: New content to merge (serialized)
            source: Name of source adding new content
            sources: List of all sources
            **settings: Merger-specific settings

        Returns:
            Merged content (serialized)
        """
        cls._validate_settings(settings)

        try:
            # Deserialize content
            base_data = cls.deserialize(base)
            new_data = cls.deserialize(new)

            # Check if both are dictionaries
            if isinstance(base_data, dict) and isinstance(new_data, dict):
                # Get merge strategy
                strategy = cls.get_merge_strategy()

                # Merge using strategy
                merged = strategy.merge_dict(base_data, new_data)

                # Serialize and return
                return cls.serialize(merged, **settings)
            else:
                # Can't deep merge non-dicts, replace
                message(
                    f"Content from '{source}' is not a dict, replacing instead of merging",
                    MessageType.WARNING,
                    VerbosityLevel.ALWAYS,
                )
                return cls.serialize(new_data, **settings)

        except Exception as e:
            message(
                f"Failed to merge content from '{source}': {e}, using copy strategy",
                MessageType.WARNING,
                VerbosityLevel.ALWAYS,
            )
            return new  # Fallback to copy strategy

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Deserialize content into Python objects.

        Must be implemented by subclasses.

        Args:
            content: Serialized content

        Returns:
            Deserialized Python object

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"{cls.__name__} must implement deserialize()")

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Serialize Python objects into content.

        Must be implemented by subclasses.

        Args:
            data: Python object to serialize
            **settings: Merger-specific settings

        Returns:
            Serialized content

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"{cls.__name__} must implement serialize()")
