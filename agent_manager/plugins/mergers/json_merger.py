"""JSON merger with deep dictionary merging."""

import json
from typing import Any

from .dict_merger import DictMerger


class JsonMerger(DictMerger):
    """Merger for JSON files with deep dictionary merging."""

    FILE_EXTENSIONS = [".json"]

    @classmethod
    def merge_preferences(cls) -> dict:
        """Define JSON merger preferences."""
        return {
            "indent": {
                "type": "int",
                "default": 2,
                "description": "Number of spaces for JSON indentation",
                "min": 0,
                "max": 8,
            },
            "sort_keys": {
                "type": "bool",
                "default": False,
                "description": "Sort JSON keys alphabetically",
            },
        }

    @classmethod
    def deserialize(cls, content: str) -> Any:
        """Deserialize JSON content.

        Args:
            content: JSON string

        Returns:
            Python object

        Raises:
            json.JSONDecodeError: If content is invalid JSON
        """
        return json.loads(content)

    @classmethod
    def serialize(cls, data: Any, **settings) -> str:
        """Serialize Python object to JSON.

        Args:
            data: Python object
            **settings: JSON formatting settings (indent, sort_keys)

        Returns:
            JSON string
        """
        # Get preferences with defaults
        prefs = cls.merge_preferences()
        indent = settings.get("indent", prefs["indent"]["default"])
        sort_keys = settings.get("sort_keys", prefs["sort_keys"]["default"])

        return json.dumps(data, indent=indent, sort_keys=sort_keys)
